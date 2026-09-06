"""Nyaya as an MCP server: any agent can learn a skill and then own it.

The point of this repository is that what an agent learns should be a file its
user can read, edit and keep. An MCP server is the natural delivery: an agent
calls `learn_skill`, gets back a page of Python with the evidence for every
belief, and can hand that file to a person. Nothing is uploaded, no model is
called, and the learning happens on the CPU of whoever ran the server.

Speaks MCP over stdio -- newline-delimited JSON-RPC 2.0 -- implemented against
the standard library alone, because a runtime that claims to need no
dependencies should not acquire one to be reachable.

    python -m nyaya.mcp_server

Register it with any MCP client, e.g. Claude Code:

    claude mcp add nyaya -- python -m nyaya.mcp_server
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

from . import skill as sk
from . import sms_rules as sr

PROTOCOL = "2025-06-18"
SUPPORTED = ("2025-06-18", "2025-03-26", "2024-11-05")
DATA = Path(__file__).resolve().parent.parent / "data" / "sms.tsv"

_DEFAULT = {}


def default_skill():
    """The bundled scam-screening skill, learned once and kept.

    Learning costs about two seconds, which is cheap enough to do on demand and
    wasteful enough to do twice.
    """
    if "skill" not in _DEFAULT and DATA.exists():
        examples = sr.read_tsv(DATA)
        started = time.perf_counter()
        _DEFAULT["skill"] = sr.learn(examples)
        _DEFAULT["seconds"] = round(time.perf_counter() - started, 2)
        _DEFAULT["examples"] = len(examples)
    return _DEFAULT.get("skill")


def _examples_from(args):
    """Accept inline examples or a TSV path; say plainly when neither works."""
    rows = args.get("examples")
    if rows:
        out = []
        for row in rows:
            label = str(row.get("label", "")).strip().lower()
            if label not in ("spam", "ham"):
                raise ValueError(
                    "each example needs label 'spam' or 'ham'; got {0!r}".format(label)
                )
            out.append((label, str(row.get("text", ""))))
        return out
    path = args.get("tsv_path")
    if path:
        target = Path(path)
        if not target.exists():
            raise ValueError("no file at {0}".format(target))
        return sr.read_tsv(target)
    raise ValueError("pass either `examples` or `tsv_path`")


def _load(args):
    """The skill named by the arguments, or the bundled one."""
    source = args.get("skill_python")
    if source:
        namespace = {}
        exec(compile(source, "<skill>", "exec"), namespace)  # noqa: S102
        return sr.load_skill(namespace)
    if args.get("tsv_path") or args.get("examples"):
        return sr.learn(_examples_from(args))
    learned = default_skill()
    if learned is None:
        raise ValueError(
            "no skill given and the bundled corpus is missing; pass `skill_python`"
        )
    return learned


# --- the tools -------------------------------------------------------------


def tool_learn_skill(args):
    examples = _examples_from(args)
    if len(examples) < 8:
        raise ValueError(
            "{0} examples is too few to hold anything out; give at least 8".format(
                len(examples)
            )
        )

    shuffled = list(examples)
    random.Random(int(args.get("seed", 7))).shuffle(shuffled)
    cut = int(0.8 * len(shuffled))

    started = time.perf_counter()
    probe = sr.learn(shuffled[:cut])
    seconds = round(time.perf_counter() - started, 2)
    held = sr.evaluate(probe, shuffled[cut:])

    final = sr.learn(examples)
    artefact = sk.from_text_rules(
        final,
        name=args.get("name", "scam screening"),
        provenance={
            "examples": len(examples),
            "learned in": "{0}s on CPU".format(seconds),
            "held out": "{0} examples".format(len(shuffled) - cut),
        },
    )

    lines = [
        "Learned {0} beliefs from {1} examples in {2}s on CPU. No model was called.".format(
            len(final["rules"]), len(examples), seconds
        ),
        "",
        "Held out on {0} examples it never saw:".format(len(shuffled) - cut),
        "  precision {0:.1%}  recall {1:.1%}  F1 {2:.3f}  accuracy {3:.1%}".format(
            held["precision"], held["recall"], held["f1"], held["accuracy"]
        ),
        "",
        "The skill below is the artefact. It is a page of Python: every belief is a",
        "sentence with the evidence that earned it. Save it, read it, delete a line",
        "you disagree with -- the verdict changes and nothing needs retraining.",
        "",
        artefact.render(),
    ]
    return "\n".join(lines)


def tool_screen_message(args):
    text = args.get("text")
    if not text:
        raise ValueError("pass the message to screen as `text`")
    learned = _load(args)
    total, fired = sr.score(learned, text)
    flagged = total >= learned["threshold"]

    lines = [
        "{0} (evidence {1}, threshold {2})".format(
            "FLAG" if flagged else "LOOKS ORDINARY", total, learned["threshold"]
        ),
        "",
    ]
    if not fired:
        lines.append("  nothing fired -- no belief in this skill matches the message")
    for desc, weight in fired:
        lines.append("  {0:>3}  {1}".format(("+" if weight > 0 else "") + str(weight), desc))
    lines += [
        "",
        "Every line above is a reason, not a score. If one of them is wrong, it is",
        "one line to delete.",
    ]
    return "\n".join(lines)


def tool_list_beliefs(args):
    learned = _load(args)
    artefact = sk.from_text_rules(learned)
    lines = ["{0} beliefs, strongest evidence first:".format(len(artefact))]
    ordered = sorted(artefact.rules, key=lambda r: -r.evidence.get("fired on", 0))
    for rule in ordered:
        lines.append(
            "  {0:>3}  {1:<52} {2}".format(
                ("+" if rule.weight > 0 else "") + str(rule.weight),
                rule.text,
                rule.evidence_line(),
            )
        )
    return "\n".join(lines)


TOOLS = [
    {
        "name": "learn_skill",
        "description": (
            "Learn a readable text-classification skill from labelled examples, on "
            "CPU, with no model call. Returns a page of Python where every belief is "
            "a sentence carrying the evidence that earned it, plus honest held-out "
            "metrics. Use when someone wants a filter they can inspect and edit "
            "rather than a black box."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "examples": {
                    "type": "array",
                    "description": "Labelled examples. Each item is {label, text} where label is 'spam' or 'ham'.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string", "enum": ["spam", "ham"]},
                            "text": {"type": "string"},
                        },
                        "required": ["label", "text"],
                    },
                },
                "tsv_path": {
                    "type": "string",
                    "description": "Alternative to `examples`: path to a TSV of label<TAB>text rows.",
                },
                "name": {"type": "string", "description": "What to call the skill."},
                "seed": {"type": "integer", "description": "Split seed. Default 7."},
            },
        },
    },
    {
        "name": "screen_message",
        "description": (
            "Screen one message and return the verdict together with every rule that "
            "fired and its weight, so the answer is a list of reasons rather than a "
            "score. Uses the bundled scam skill (learned from 5,574 real messages) "
            "unless you pass your own."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The message to screen."},
                "skill_python": {
                    "type": "string",
                    "description": "Optional: the source of a skill produced by learn_skill.",
                },
                "tsv_path": {
                    "type": "string",
                    "description": "Optional: learn from this TSV instead of using the bundled skill.",
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "list_beliefs",
        "description": (
            "List everything a skill believes, ordered by how much evidence stands "
            "behind each belief. Use to audit a filter before trusting it -- it will "
            "show you the dataset's biases as plain sentences."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "skill_python": {"type": "string", "description": "Optional skill source."},
                "tsv_path": {"type": "string", "description": "Optional corpus to learn from."},
            },
        },
    },
]

HANDLERS = {
    "learn_skill": tool_learn_skill,
    "screen_message": tool_screen_message,
    "list_beliefs": tool_list_beliefs,
}


# --- JSON-RPC --------------------------------------------------------------


def _result(request_id, payload):
    return {"jsonrpc": "2.0", "id": request_id, "result": payload}


def _error(request_id, code, message):
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle(message):
    """One JSON-RPC message in, one response out -- or None for a notification.

    Kept as a pure function so the whole protocol surface is testable without
    spawning a process or speaking to a real client.
    """
    method = message.get("method")
    request_id = message.get("id")
    params = message.get("params") or {}

    if request_id is None:
        return None  # a notification; nothing is owed

    if method == "initialize":
        asked = params.get("protocolVersion")
        return _result(
            request_id,
            {
                "protocolVersion": asked if asked in SUPPORTED else PROTOCOL,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "nyaya", "version": "0.1.0"},
                "instructions": (
                    "Learns readable classification skills on CPU with no model in "
                    "the loop. Every skill it returns is a page of Python the user "
                    "can read, edit and keep -- hand it to them rather than "
                    "summarising it away."
                ),
            },
        )

    if method == "ping":
        return _result(request_id, {})

    if method == "tools/list":
        return _result(request_id, {"tools": TOOLS})

    if method == "tools/call":
        name = params.get("name")
        handler = HANDLERS.get(name)
        if handler is None:
            return _error(request_id, -32602, "unknown tool {0!r}".format(name))
        try:
            text = handler(params.get("arguments") or {})
        except Exception as failure:  # surfaced to the model, not swallowed
            return _result(
                request_id,
                {
                    "content": [{"type": "text", "text": "{0}".format(failure)}],
                    "isError": True,
                },
            )
        return _result(request_id, {"content": [{"type": "text", "text": text}]})

    return _error(request_id, -32601, "unknown method {0!r}".format(method))


def serve(stdin=None, stdout=None):
    """Read newline-delimited JSON-RPC from stdin, write responses to stdout."""
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except ValueError:
            stdout.write(json.dumps(_error(None, -32700, "invalid JSON")) + "\n")
            stdout.flush()
            continue
        response = handle(message)
        if response is not None:
            stdout.write(json.dumps(response) + "\n")
            stdout.flush()
    return 0


def main(argv=None):
    return serve()


if __name__ == "__main__":
    raise SystemExit(main())
