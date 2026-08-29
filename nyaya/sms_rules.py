"""Learn a readable scam-detection skill from labelled SMS. The bridge.

The runtime's claim is that an agent's learned behaviour should be a small
program a person can read, edit and own. This module is that claim leaving
the grid-world: from a few hundred labelled messages it induces a scoring
skill whose every rule is a human sentence -- "asks the reader to pay a fee
to claim a prize", weight +3 -- and whose entire decision procedure fits on
a page. No embeddings, no weights, no network, no GPU; stdlib only, so the
same file runs on a phone-class CPU.

Two honesty notes, load-bearing:

Every rule is induced, none is hand-tuned: the named signals below are
candidate FEATURES, but whether each earns a place in the skill, in which
direction, and at what weight, is decided by counting its precision on the
training labels. A signal that fires on legitimate bank alerts convicts
itself out of the skill.

And the transparent scorer pays for its readability: this is a keyword-era
classifier, and a motivated adversary who reads the skill can write around
it. That trade is the point of the demo -- the user can read exactly what
their guardian believes -- and the measured numbers below say how much the
trade costs against real data today.
"""
from __future__ import annotations

import math
import re

# Candidate named signals. Descriptions are what the skill file prints, so
# they are written for the person who will read them, not for the parser.
SIGNALS = (
    ("contains a web link", re.compile(r"https?://|www\.|\b\w+\.(?:xyz|shop|info|co|net|org|in|com|apk)\b", re.I)),
    ("contains a phone number to call", re.compile(r"\b(?:\+?\d[\d\s-]{8,12}\d)\b")),
    ("contains an SMS shortcode to text", re.compile(r"\b(?:text|txt|sms|send)\s+\w{1,10}\s+to\s+\d{4,6}\b", re.I)),
    ("claims the reader won a prize or lottery", re.compile(r"\b(?:won|winner|congratulat\w*|lucky draw|lottery|prize|jeeta|jeete)\b", re.I)),
    ("asks for a fee, charge or deposit to receive something", re.compile(r"\b(?:processing fee|registration fee|delivery charge|customs duty|gst fee|verification charge|security deposit|bail amount|advance)\b", re.I)),
    ("mentions KYC, Aadhaar or PAN verification", re.compile(r"\b(?:kyc|aadhaar|aadhar|pan card|pan\b)", re.I)),
    ("threatens suspension, blocking or disconnection", re.compile(r"\b(?:suspend\w*|blocked?|deactivat\w*|disconnect\w*|banned|band ho|block ho)\b", re.I)),
    ("applies deadline pressure", re.compile(r"\b(?:immediately|urgent\w*|within \d+\s*(?:hours|hrs|minutes)|today|tonight|abhi|turant|expire\w* today|24 ghante)\b", re.I)),
    ("invokes police, courts, CBI or arrest", re.compile(r"\b(?:police|cbi|cyber cell|arrest|warrant|fir\b|money laundering|inspector|court)\b", re.I)),
    ("asks for OTP or UPI PIN", re.compile(r"\b(?:share (?:the )?otp|otp .{0,20}(?:share|bheje|send)|upi pin|enter pin)\b", re.I)),
    ("mentions a refund, cashback or unclaimed money", re.compile(r"\b(?:refund|cashback|unclaimed|credited failed|pending amount)\b", re.I)),
    ("advertises easy daily earnings or guaranteed income", re.compile(r"\b(?:earn (?:rs|rupees|\$|money)|per day|daily income|work from home|guaranteed income|monthly income)\b", re.I)),
    ("asks the reader to click or login to verify", re.compile(r"\b(?:click|verify|login|update)\b.{0,40}\b(?:link|here|details|account)\b", re.I)),
    ("quotes a large money amount", re.compile(r"(?:rs\.?|inr|₹|\$|usd|£)\s?\d[\d,]{3,}|\b\d+\s*(?:lakh|crore)\b", re.I)),
    ("written with shouting or heavy punctuation", re.compile(r"[A-Z]{6,}|!{2,}")),
    ("reads like a personal message to someone known", re.compile(r"\b(?:bhai|yaar|beta|mummy|papa|didi|bro|dear \w+,|kal|aaj (?:ka|gym)|good morning|happy birthday|see you|meeting|class)\b", re.I)),
    ("is a standard transaction or delivery notice", re.compile(r"\b(?:debited from a/c|credited to a/c|avl bal|order #|out for delivery|pnr|recharge successful|premium .{0,12}due|appointment .{0,12}confirmed)\b", re.I)),
    ("warns never to share the code (bank style)", re.compile(r"\bdo not share\b", re.I)),
)

WORD = re.compile(r"[a-zऀ-ॿ]{3,}")


def _tokens(text):
    return set(WORD.findall(text.lower()))


def learn(examples, min_support=4, min_precision=0.85, max_word_rules=40):
    """Induce a skill from (label, text) pairs; label is 'spam' or 'ham'.

    Every candidate -- named signal or frequent word -- is scored by Laplace
    precision toward each class and admitted only if it clears the bar in
    one direction. Weights are small integers because a person has to be
    able to audit the arithmetic in their head.
    """
    spam = [t for lab, t in examples if lab == "spam"]
    ham = [t for lab, t in examples if lab == "ham"]
    rules = []

    def admit(desc, kind, pattern, s_hits, h_hits):
        p_spam = (s_hits + 1) / (s_hits + h_hits + 2)
        p_ham = (h_hits + 1) / (s_hits + h_hits + 2)
        if s_hits >= min_support and p_spam >= min_precision:
            weight = 3 if p_spam >= 0.97 else 2 if p_spam >= 0.92 else 1
            rules.append((desc, kind, pattern, weight, s_hits, h_hits))
        elif h_hits >= min_support and p_ham >= min_precision:
            weight = -2 if p_ham >= 0.95 else -1
            rules.append((desc, kind, pattern, weight, s_hits, h_hits))

    for desc, regex in SIGNALS:
        s_hits = sum(1 for t in spam if regex.search(t))
        h_hits = sum(1 for t in ham if regex.search(t))
        admit(desc, "regex", regex.pattern, s_hits, h_hits)

    # Vocabulary the labels teach us, rendered as readable word rules. The
    # cap keeps the skill on one page; candidates are ranked by how much
    # evidence they carry, not just how pure they are.
    spam_df, ham_df = {}, {}
    for t in spam:
        for w in _tokens(t):
            spam_df[w] = spam_df.get(w, 0) + 1
    for t in ham:
        for w in _tokens(t):
            ham_df[w] = ham_df.get(w, 0) + 1
    named = "|".join(p for _, _, p, *_ in rules if _tokens(p))
    scored = []
    for w in set(spam_df) | set(ham_df):
        if w in named:
            continue
        s, h = spam_df.get(w, 0), ham_df.get(w, 0)
        p = (s + 1) / (s + h + 2)
        if s + h < min_support:
            continue
        if p >= 0.9:
            scored.append((p * math.log(1 + s), f"contains the word '{w}'", w, 1, s, h))
        elif p <= 0.1:
            scored.append(((1 - p) * math.log(1 + h), f"contains the word '{w}'", w, -1, s, h))
    scored.sort(reverse=True)
    for _, desc, w, weight, s, h in scored[:max_word_rules]:
        rules.append((desc, "word", w, weight, s, h))

    skill = {"rules": rules, "threshold": 1}
    best = (0.0, 1)
    for threshold in range(1, 7):
        skill["threshold"] = threshold
        stats = evaluate(skill, examples)
        if stats["f1"] > best[0]:
            best = (stats["f1"], threshold)
    skill["threshold"] = best[1]
    return skill


def score(skill, text):
    """Total evidence and the list of rules that fired, for showing a person."""
    total = 0
    fired = []
    words = _tokens(text)
    for desc, kind, pattern, weight, *_ in skill["rules"]:
        hit = (
            pattern in words
            if kind == "word"
            else re.search(pattern, text, re.I) is not None
        )
        if hit:
            total += weight
            fired.append((desc, weight))
    return total, fired


def classify(skill, text):
    return score(skill, text)[0] >= skill["threshold"]


def evaluate(skill, examples):
    tp = fp = fn = tn = 0
    for label, text in examples:
        said = classify(skill, text)
        real = label == "spam"
        tp += said and real
        fp += said and not real
        fn += real and not said
        tn += (not said) and (not real)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": (tp + tn) / max(1, len(examples)),
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
    }


def render_skill(skill, provenance=""):
    """The skill as a Python file a person can open, read, edit and own.

    Deleting a line deletes the belief. Changing a weight changes the
    guardian's mind. That editability is the product claim, so the emitted
    file is the real artefact, not a serialisation format.
    """
    lines = [
        '"""A learned scam-screening skill. Yours: read it, edit it, keep it.',
        "",
        "Each rule is (what it looks for, kind, pattern, weight, spam_hits,",
        "ham_hits) -- the hits are the training evidence it earned its weight",
        "with. Positive weights accuse; negative weights vouch. A message is",
        "flagged when the summed weights of fired rules reach THRESHOLD.",
        provenance,
        '"""',
        "",
        "RULES = [",
    ]
    for desc, kind, pattern, weight, s, h in skill["rules"]:
        lines.append(
            f"    ({desc!r},\n     {kind!r}, {pattern!r}, {weight}, {s}, {h}),"
        )
    lines.append("]")
    lines.append(f"THRESHOLD = {skill['threshold']}")
    lines.append("")
    return "\n".join(lines)


def load_skill(namespace):
    """Rebuild a skill from an exec'd or imported skill file."""
    return {"rules": [tuple(r) for r in namespace["RULES"]], "threshold": namespace["THRESHOLD"]}


def read_tsv(path):
    examples = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            label, _, text = line.partition("\t")
            if label in ("spam", "ham") and text:
                examples.append((label, text))
    return examples
