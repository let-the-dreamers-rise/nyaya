"""A skill: what both learners in this repository actually produce.

The world-model learner watches an agent act and works out what moves, what
blocks, what a click does. The text learner reads labelled messages and works
out which patterns accuse and which vouch. Those look like different projects
until you ask what each one *returns*, and the answer is the same object in
both cases:

    a set of beliefs, each a human sentence carrying the evidence that
    earned it, plus a record of where the whole thing came from.

That object is a Skill. It is deliberately not a model, a checkpoint or a
serialisation format -- it is source code a person can open, disagree with and
edit, and the edit changes what the agent does. Provenance travels with it so
a skill inherited from someone else can be interrogated rather than trusted.

Standard library only, like everything else here, because a skill that needs a
runtime to read is not readable.
"""

from __future__ import annotations

import json
import re

SCHEMA = 1

_SAFE = re.compile(r"[^0-9A-Za-z_]+")


def _slug(text):
    return _SAFE.sub("_", str(text)).strip("_").lower() or "skill"


class Rule:
    """One belief. The sentence is the point; the weight is how much it counts.

    `evidence` is whatever the learner can show for it -- support counts,
    held-out precision, the number of transitions that voted. A rule with no
    evidence is allowed, and reads as exactly that: an assertion.
    """

    __slots__ = ("text", "weight", "kind", "evidence")

    def __init__(self, text, weight=1, kind="", evidence=None):
        self.text = str(text)
        self.weight = weight
        self.kind = str(kind)
        self.evidence = dict(evidence or {})

    def __repr__(self):
        return "Rule({0!r}, weight={1!r})".format(self.text, self.weight)

    def __eq__(self, other):
        return isinstance(other, Rule) and self.as_dict() == other.as_dict()

    def as_dict(self):
        return {
            "text": self.text,
            "weight": self.weight,
            "kind": self.kind,
            "evidence": dict(self.evidence),
        }

    @classmethod
    def from_dict(cls, raw):
        return cls(
            raw["text"],
            raw.get("weight", 1),
            raw.get("kind", ""),
            raw.get("evidence"),
        )

    def evidence_line(self):
        """The evidence as a short human clause, or '' if there is none."""
        if not self.evidence:
            return ""
        parts = []
        for key in sorted(self.evidence):
            value = self.evidence[key]
            if isinstance(value, float):
                value = round(value, 3)
            parts.append("{0}={1}".format(key, value))
        return ", ".join(parts)


class Skill:
    """Beliefs plus provenance, renderable as Python a person can edit.

    `domain` names what the beliefs are about ('sms', 'grid-world'), so a
    library of skills can be filtered without executing any of them.
    """

    def __init__(self, name, domain, rules=(), provenance=None):
        self.name = str(name)
        self.domain = str(domain)
        self.rules = list(rules)
        self.provenance = dict(provenance or {})

    def __len__(self):
        return len(self.rules)

    def __repr__(self):
        return "Skill({0!r}, domain={1!r}, rules={2})".format(
            self.name, self.domain, len(self.rules)
        )

    # --- reading -------------------------------------------------------

    def sentences(self):
        """Every belief as a plain line -- the whole skill, readable aloud."""
        return [r.text for r in self.rules]

    def unsupported(self):
        """Rules carrying no evidence. A reviewer should look here first."""
        return [r for r in self.rules if not r.evidence]

    # --- portability ---------------------------------------------------

    def as_dict(self):
        return {
            "schema": SCHEMA,
            "name": self.name,
            "domain": self.domain,
            "provenance": dict(self.provenance),
            "rules": [r.as_dict() for r in self.rules],
        }

    @classmethod
    def from_dict(cls, raw):
        if raw.get("schema") != SCHEMA:
            raise ValueError(
                "skill schema {0!r} is not {1}".format(raw.get("schema"), SCHEMA)
            )
        return cls(
            raw["name"],
            raw["domain"],
            [Rule.from_dict(r) for r in raw.get("rules", ())],
            raw.get("provenance"),
        )

    def to_json(self, indent=2):
        return json.dumps(self.as_dict(), indent=indent, sort_keys=True)

    @classmethod
    def from_json(cls, text):
        return cls.from_dict(json.loads(text))

    # --- the artefact --------------------------------------------------

    def render(self):
        """The skill as a Python file: beliefs first, machinery nowhere.

        Deliberately not a serialisation. Someone who has never seen this
        library should be able to open the file, disagree with line 12, delete
        it, and have the agent's verdict change.
        """
        out = [
            '"""{0}\n'.format(self.name),
            "Learned beliefs about: {0}".format(self.domain),
            "",
        ]
        if self.provenance:
            out.append("Where this came from:")
            for key in sorted(self.provenance):
                out.append("  {0}: {1}".format(key, self.provenance[key]))
            out.append("")
        out.append("Each rule below is one belief. Delete a line to delete the")
        out.append('belief; the agent stops acting on it.\n"""')
        out.append("")
        out.append("SKILL = {0!r}".format(self.name))
        out.append("DOMAIN = {0!r}".format(self.domain))
        out.append("")
        out.append("RULES = [")
        for rule in self.rules:
            evidence = rule.evidence_line()
            if evidence:
                out.append("    # {0}".format(evidence))
            out.append(
                "    ({0!r}, {1!r}, {2!r}),".format(rule.text, rule.weight, rule.kind)
            )
        out.append("]")
        out.append("")
        return "\n".join(out)

    def filename(self):
        return "{0}_skill.py".format(_slug(self.name))


# --- adapters: the two learners, one type ------------------------------------


def from_text_rules(skill_dict, name="scam screening", provenance=None):
    """Wrap `sms_rules.learn()` output as a Skill.

    The text learner already stores each rule as a human sentence with its
    weight, so this is a translation rather than a summary: nothing is lost
    and nothing is invented.
    """
    rules = []
    for row in skill_dict.get("rules", ()):
        text, weight = row[0], row[3]
        accuses = weight > 0
        # Rows carry (spam_hits, ham_hits); turn them into the two numbers a
        # person actually wants: how often it fired, and how often it was right.
        evidence = {}
        if len(row) > 5:
            for_class, against = (row[4], row[5]) if accuses else (row[5], row[4])
            support = for_class + against
            if support:
                evidence = {
                    "fired on": support,
                    "right": round(for_class / support, 3),
                }
        rules.append(Rule(text, weight, "accuses" if accuses else "vouches", evidence))
    prov = dict(provenance or {})
    prov.setdefault("threshold", skill_dict.get("threshold"))
    return Skill(name, "text messages", rules, prov)


def from_world_model(summary, name="environment physics", provenance=None):
    """Turn `world_model.wm_summary()` into the same readable object.

    A learned physics is a set of beliefs exactly like a learned scam filter
    is: 'UP moves the body up one row' is the same kind of statement as
    'asking for a fee to claim a prize accuses'. Rendering them through one
    type is what makes the claim in this repository's README a fact about the
    code rather than a metaphor.
    """
    rules = []
    steps = summary.get("steps", 0)
    seen = {"transitions": steps} if steps else {}

    body = summary.get("body")
    if body:
        rules.append(
            Rule("the thing I control is drawn as {0!r}".format(body), 1, "body", seen)
        )

    for action in sorted(summary.get("deltas") or {}):
        dr, dc = summary["deltas"][action]
        rules.append(
            Rule(
                "{0} moves it by {1} rows and {2} columns".format(action, dr, dc),
                1,
                "movement",
                seen,
            )
        )

    for char in summary.get("blockers") or "":
        rules.append(Rule("{0!r} blocks it".format(char), 1, "blocking", seen))

    for char in sorted(summary.get("clicks") or {}):
        rules.append(
            Rule(
                "clicking {0!r} causes {1}".format(char, summary["clicks"][char]),
                1,
                "click",
                seen,
            )
        )

    prov = dict(provenance or {})
    prov.setdefault("transitions observed", steps)
    return Skill(name, "grid world", rules, prov)
