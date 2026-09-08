"""What the phone noticed about your money, as sentences with evidence.

Three kinds of sentence come out of here and they are labelled so a reader
knows which is which:

  fact     -- counted, not learned. "Zomato 14 times in 30 days, Rs 6,240."
  belief   -- found by the program synthesiser in `nyaya.synthesis`, the same
              search that learns grid physics. "On Sundays in the evening a
              payment of Rs 500 to 2,000 goes to Zomato. Right 9 of 10 times."
  alert    -- a shape worth a second look. "Rs 12,000 to a first-time
              recipient nine minutes after a message that said KYC."

Every sentence carries an id so the person can mute it, and a muted sentence
stays muted across re-reads. No sentence is ever sent anywhere.
"""

from __future__ import annotations

import hashlib
from datetime import timedelta

from .. import skill as sk
from .. import synthesis
from .sources import transactions as _transactions

SCAM_WORDS = ("kyc", "blocked", "block", "suspend", "arrest", "police", "cbi",
              "customs", "lottery", "prize", "winner", "urgent", "immediately",
              "expire", "verify", "share otp", "link", "courier", "parcel")
SALARY_FLOOR = 20000.0

_AMOUNT_BANDS = ((100, "under Rs 100"), (500, "Rs 100 to 500"), (2000, "Rs 500 to 2,000"),
                 (10000, "Rs 2,000 to 10,000"), (50000, "Rs 10,000 to 50,000"))
_DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def amount_band(amount):
    for ceiling, label in _AMOUNT_BANDS:
        if amount < ceiling:
            return label
    return "over Rs 50,000"


def time_band(when):
    h = when.hour
    if 5 <= h < 11:
        return "morning"
    if 11 <= h < 16:
        return "midday"
    if 16 <= h < 21:
        return "evening"
    return "night"


def day_band(when):
    d = when.day
    if d <= 3:
        return "1st and 3rd"
    if d <= 10:
        return "4th and 10th"
    if d <= 20:
        return "11th and 20th"
    return "21st and month end"


def pay_band(days):
    if days is None:
        return "no pay seen"
    if days <= 3:
        return "0 to 3 days after pay"
    if days <= 10:
        return "4 to 10 days after pay"
    if days <= 20:
        return "11 to 20 days after pay"
    return "over 20 days after pay"


def rupees(amount):
    whole = int(round(amount))
    s = str(whole)
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts) + "," + tail
    return "Rs " + s


def _sid(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]


def _sentence(text, kind, evidence=None):
    return {"id": _sid(text), "text": text, "kind": kind, "evidence": dict(evidence or {})}


# --- examples for the synthesiser ------------------------------------------


def _contexts(txns):
    """Each outgoing transaction with what was true just before it."""
    seen = set()
    last_pay = None
    rows = []
    for t in txns:
        if t.direction == "in" and t.amount >= SALARY_FLOOR:
            last_pay = t.when
        if t.direction != "out":
            continue
        since = (t.when - last_pay).days if last_pay else None
        rows.append((t, {
            "weekday": _DAYS[t.when.weekday()],
            "time": time_band(t.when),
            "day": day_band(t.when),
            "amount": amount_band(t.amount),
            "channel": t.channel,
            "first time": t.party not in seen,
            "pay": pay_band(since),
        }))
        seen.add(t.party)
    return rows


def examples_payee(txns):
    """Predict who is paid from when and how much.

    The synthesiser pins every rule to `self`. The first version pinned it to
    the day of the month and got the pathology the grid work already
    documented: one habit (chai every morning) became four rules with a
    quarter of the evidence each. So `self` is a constant here and the
    calendar is an ordinary condition the search may add when it helps.
    """
    out = []
    for t, ctx in _contexts(txns):
        if not t.party:
            continue
        obs = dict(ctx)
        obs["self"] = "money"
        out.append((obs, t.party))
    return out


def examples_amount(txns):
    """Predict how much from who and when. `self` is the party."""
    out = []
    for t, ctx in _contexts(txns):
        if not t.party:
            continue
        obs = {k: v for k, v in ctx.items() if k not in ("amount", "first time")}
        obs["self"] = t.party
        out.append((obs, ctx["amount"]))
    return out


# --- rendering ---------------------------------------------------------------


def _phrase(name, value, names):
    if name == "self":
        return None  # handled by the caller, it means different things per pass
    if name == "day":
        return "between the {0}".format(value)
    if name == "channel" and value == "other":
        return None
    if name == "weekday":
        return "on {0}s".format(value)
    if name == "time":
        return "in the {0}".format(value) if value != "night" else "at night"
    if name == "amount":
        return "a payment of {0}".format(value)
    if name == "channel":
        return "by {0}".format(value.upper() if value in ("upi", "atm") else value)
    if name == "first time":
        return "to someone new" if value else "to someone you have paid before"
    if name == "pay":
        return value
    return "{0} is {1}".format(name, value)


def _evidence(rule):
    right = int(round(rule.precision * rule.support))
    return {"fired on": rule.support, "right": right}


_ORDER = ("day", "weekday", "time", "pay", "first time", "channel", "amount")


def _phrases(rule, names):
    conds = dict(rule.conditions)
    out = []
    for name in _ORDER:
        if name in conds:
            p = _phrase(name, conds[name], names)
            if p:
                out.append(p)
    return out


def _render_payee(rule, names):
    conds = dict(rule.conditions)
    subject = "a payment of {0}".format(conds["amount"]) if "amount" in conds else "money"
    parts = [p for p in _phrases(rule, names) if not p.startswith("a payment of")]
    ev = _evidence(rule)
    when = (", ".join(parts) + ", ") if parts else ""
    text = "{0}{1} goes to {2}. Right {3} of {4} times.".format(
        when, subject, names.get(rule.outcome, rule.outcome), ev["right"], ev["fired on"])
    return _sentence(text[0].upper() + text[1:], "belief", ev)


def _render_amount(rule, names):
    conds = dict(rule.conditions)
    party = names.get(conds["self"], conds["self"])
    parts = _phrases(rule, names)
    ev = _evidence(rule)
    when = (", ".join(parts) + ", ") if parts else ""
    text = "{0}{1} is {2}. Right {3} of {4} times.".format(
        when, party, rule.outcome, ev["right"], ev["fired on"])
    return _sentence(text[0].upper() + text[1:], "belief", ev)


def beliefs(txns, names, min_support=4, min_precision=0.9):
    """The learned part. Two passes of the same synthesiser."""
    out = []
    said = set()  # (party, amount band) pairs already stated by the payee pass
    for examples, render in ((examples_payee(txns), _render_payee),
                             (examples_amount(txns), _render_amount)):
        for rule in synthesis.synthesise(examples, 3, min_support, min_precision):
            # Separate-and-conquer scores each rule on what earlier rules left
            # behind, so 'in the evening -> Zomato' can read 14 of 14 after the
            # Swiggy evenings were explained away. A person reads the sentence
            # alone, so the evidence shown is against everything.
            support, precision = synthesis._score(examples, rule.conditions, rule.outcome)
            if precision < min_precision or support < min_support:
                continue
            conds = dict(rule.conditions)
            if render is _render_payee and set(conds) == {"self", "amount"}:
                said.add((rule.outcome, conds["amount"]))
            # The amount pass restates 'under Rs 100 -> chai' as 'chai is under
            # Rs 100'. Same belief, two passes; the reader sees it once.
            if render is _render_amount and set(conds) == {"self"} \
                    and (conds["self"], rule.outcome) in said:
                continue
            rule.support, rule.precision = support, precision
            out.append(render(rule, names))
    return sorted(out, key=lambda s: -s["evidence"]["fired on"])


# --- facts -------------------------------------------------------------------


def _window(txns, end, days):
    lo = end - timedelta(days=days)
    return [t for t in txns if lo < t.when <= end]


def facts(txns, names, end):
    out = []
    this = _window(txns, end, 30)
    prev = _window(txns, end - timedelta(days=30), 30)
    out_this = sum(t.amount for t in this if t.direction == "out")
    out_prev = sum(t.amount for t in prev if t.direction == "out")
    in_this = sum(t.amount for t in this if t.direction == "in")
    if this:
        text = "In the last 30 days {0} left and {1} came in.".format(rupees(out_this), rupees(in_this))
        if out_prev:
            change = (out_this - out_prev) / out_prev * 100
            text += " Spending is {0}{1:.0f}% against the 30 days before.".format(
                "+" if change >= 0 else "", change)
        out.append(_sentence(text, "fact", {"transactions": len(this)}))
    by = {}
    for t in this:
        if t.direction == "out" and t.party:
            n, s = by.get(t.party, (0, 0.0))
            by[t.party] = (n + 1, s + t.amount)
    for party, (n, s) in sorted(by.items(), key=lambda kv: -kv[1][1])[:5]:
        share = s / out_this * 100 if out_this else 0
        times = "once" if n == 1 else "{0} times".format(n)
        out.append(_sentence(
            "{0}: {1} in 30 days, {2}. That is {3:.0f}% of what left.".format(
                names.get(party, party), times, rupees(s), share), "fact", {"count": n}))
    return out


def recurring(txns, names):
    """Same party, roughly monthly, roughly the same amount, three or more times."""
    by = {}
    for t in txns:
        if t.direction == "out" and t.party:
            by.setdefault(t.party, []).append(t)
    out = []
    for party, rows in by.items():
        if len(rows) < 3:
            continue
        gaps = [(b.when - a.when).days for a, b in zip(rows, rows[1:])]
        amounts = [t.amount for t in rows]
        mid = sorted(amounts)[len(amounts) // 2]
        steady = all(abs(a - mid) <= 0.2 * mid for a in amounts)
        monthly = all(25 <= g <= 35 for g in gaps)
        if steady and monthly:
            days = sorted(t.when.day for t in rows)
            out.append(_sentence(
                "Every month around the {0}, {1} to {2}. Seen {3} times.".format(
                    _ordinal(days[len(days) // 2]), rupees(mid), names.get(party, party), len(rows)),
                "fact", {"count": len(rows)}))
    return out


def _ordinal(d):
    suffix = "th" if 11 <= d % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    return "{0}{1}".format(d, suffix)


# --- alerts ------------------------------------------------------------------


def _scam_hits(body, words):
    low = body.lower()
    hits = [w for w in words if w in low]
    # 'block' inside 'blocked' is one hit, not two.
    return [h for h in hits if not any(h != o and h in o for o in hits)]


def alerts(txns, messages, names, words=SCAM_WORDS, window_minutes=30, recent_days=30):
    """Recent payments to a stranger that look like a scam or a shock.

    A stranger is a party paid exactly once in the whole ledger. The rent on
    its first month is not a stranger, because it recurs; the ledger knows
    that by the time anyone reads it. Only the last `recent_days` are
    alerted on, because an alert about June is a history lesson.
    """
    out = []
    outgoing = [t for t in txns if t.direction == "out"]
    if not outgoing:
        return out
    amounts = sorted(t.amount for t in outgoing)
    median = amounts[len(amounts) // 2]
    counts = {}
    for t in outgoing:
        counts[t.party] = counts.get(t.party, 0) + 1
    cutoff = outgoing[-1].when - timedelta(days=recent_days)
    strangers = [m for m in messages
                 if m["sender"].lstrip("+").replace("-", "").isdigit() or not m["sender"]]
    for t in outgoing:
        if t.when < cutoff or counts.get(t.party, 0) != 1 or t.channel == "atm":
            continue
        lo = t.when - timedelta(minutes=window_minutes)
        for m in strangers:
            if not (lo <= m["when"] <= t.when):
                continue
            hits = _scam_hits(m["body"], words)
            if not hits:
                continue
            mins = int((t.when - m["when"]).total_seconds() // 60)
            out.append(_sentence(
                "{0} went to {1}, a first-time recipient, {2} minutes after a message from {3} that said {4}. That is the shape of a scam.".format(
                    rupees(t.amount), names.get(t.party, t.party), mins, m["sender"],
                    " and ".join("'{0}'".format(h) for h in hits[:3])),
                "alert", {"minutes": mins}))
            break
        else:
            if median and t.amount >= 5 * median and t.amount >= 2000:
                out.append(_sentence(
                    "{0} went to {1}, someone you had never paid before. That is {2:.0f} times your usual payment.".format(
                        rupees(t.amount), names.get(t.party, t.party), t.amount / median),
                    "alert", {"usual": median}))
    return out


# --- the whole thing ---------------------------------------------------------


def witness(messages, prefs=None):
    """Everything the phone can say about this person's money, as sentences."""
    prefs = dict(prefs or {})
    names = dict(prefs.get("nicknames") or {})
    muted = set(prefs.get("muted") or ())
    words = tuple(prefs.get("scam_words") or SCAM_WORDS)
    txns = _transactions(messages)
    if not txns:
        return {"count": 0, "sentences": [], "span": ""}
    end = txns[-1].when
    sentences = alerts(txns, messages, names, words) + facts(txns, names, end) \
        + recurring(txns, names) + beliefs(txns, names)
    kept = [s for s in sentences if s["id"] not in muted]
    return {
        "count": len(txns),
        "span": "{0} to {1}".format(txns[0].when.strftime("%d %b %Y"), end.strftime("%d %b %Y")),
        "sentences": kept,
        "muted": len(sentences) - len(kept),
        "transactions": [t.as_dict() for t in txns[-50:]],
    }


def to_skill(result, name="what my phone knows about my money"):
    rules = [sk.Rule(s["text"], 1, s["kind"], s["evidence"]) for s in result.get("sentences", ())]
    return sk.Skill(name, "money", rules, {"transactions": result.get("count", 0), "span": result.get("span", "")})
