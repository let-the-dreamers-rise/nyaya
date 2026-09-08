"""Bank and UPI SMS -> Transaction. Indian formats, standard library only.

The messages are not standardised, but they are highly regular: an amount
with a currency mark, a direction word, a counterparty introduced by 'to',
'from' or 'at', and an account tail. Each bank has its own template and the
templates change every year, so this parser is written as a set of small
independent extractors rather than one regex per bank. A message that yields
an amount and a direction is a transaction; the rest is best effort and
reported as such.

Nothing personal is stored beyond what the message itself already says.
"""

from __future__ import annotations

import re
from datetime import datetime

_AMOUNT = re.compile(
    r"(?:rs\.?|inr|₹)\s*:?\s*([0-9][0-9,]*(?:\.[0-9]{1,2})?)", re.I
)
_VPA = re.compile(r"\b([a-z0-9][a-z0-9._-]{1,60}@[a-z][a-z0-9]{1,20})\b", re.I)
_ACCOUNT = re.compile(
    r"(?:a/c|acct|account|ac)\.?\s*(?:no\.?\s*)?[*x]*([0-9]{3,6})\b", re.I
)
_CARD = re.compile(r"card\s*(?:ending|no\.?|xx)?\s*[*x]*([0-9]{4})\b", re.I)

_OUT = ("debited", "debit", "sent", "paid", "spent", "withdrawn", "purchase",
        "transferred", "payment of")
_IN = ("credited", "credit", "received", "deposited", "refund", "cashback")

# Words that introduce the other party, in the order they are tried. The VPA
# extractor runs first because a VPA is unambiguous; these handle merchants
# and names written in capitals by the bank template.
_PARTY = [
    re.compile(r"\bto\s+(?:vpa\s+)?([A-Z][A-Z0-9 .&'\-]{2,40}?)(?=\s+(?:on|via|ref|upi|at|dt)\b|[.,;(]|$)", re.I),
    re.compile(r"\bat\s+([A-Z][A-Z0-9 .&'\-]{2,40}?)(?=\s+(?:on|via|ref|upi|dt)\b|[.,;(]|$)", re.I),
    re.compile(r"\bfrom\s+(?:vpa\s+)?([A-Z][A-Z0-9 .&'\-]{2,40}?)(?=\s+(?:on|via|ref|upi|at|dt|to)\b|[.,;(]|$)", re.I),
    re.compile(r"\bby\s+(?:neft|imps|rtgs|upi)[\s:-]+([A-Z][A-Z0-9 .&'\-]{2,40}?)(?=[.,;(]|\s+(?:on|ref|avl)\b|$)", re.I),
    re.compile(r";\s*([A-Z][A-Z0-9 .&'\-]{2,40}?)\s+credited", re.I),
    re.compile(r"\binfo:?\s*([A-Z][A-Z0-9 .&'\-]{2,40}?)(?=[.,;(]|$)", re.I),
]
_NOISE_PARTY = {"your", "you", "a/c", "ac", "account", "upi", "bank", "the", "acct"}

_BANK_SENDER = re.compile(r"^(?:[A-Z]{2}-)?[A-Z]{2}-?[A-Z0-9]{5,7}(?:-[A-Z])?$")
_BANK_WORDS = ("bank", "hdfc", "sbi", "icici", "axis", "kotak", "pnb", "bob",
               "idfc", "yes", "indus", "canara", "union", "paytm", "phonepe",
               "gpay", "upi", "a/c", "acct", "card")

_CHANNELS = (
    ("upi", ("upi", "vpa", "@")),
    ("card", ("card", "pos", "ecom")),
    ("atm", ("atm", "cash withdrawal")),
    ("transfer", ("neft", "imps", "rtgs")),
)


class Transaction:
    """One movement of money, as far as the message lets us know it."""

    __slots__ = ("when", "amount", "direction", "party", "channel",
                 "account", "sender", "body")

    def __init__(self, when, amount, direction, party="", channel="other",
                 account="", sender="", body=""):
        self.when = when
        self.amount = float(amount)
        self.direction = direction  # 'out' or 'in'
        self.party = party
        self.channel = channel
        self.account = account
        self.sender = sender
        self.body = body

    def __repr__(self):
        return "Transaction({0} {1} {2:.2f} {3!r})".format(
            self.when.strftime("%Y-%m-%d %H:%M"), self.direction, self.amount, self.party
        )

    def as_dict(self):
        return {
            "when": self.when.strftime("%Y-%m-%d %H:%M"),
            "amount": self.amount,
            "direction": self.direction,
            "party": self.party,
            "channel": self.channel,
            "account": self.account,
        }


def amount_of(body):
    """The first currency amount in the text, or None."""
    m = _AMOUNT.search(body)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def direction_of(body):
    """'out', 'in', or None. The earliest direction word wins, because bank
    templates say 'debited ... credited to X' for a payment and the reverse
    for a receipt: the first verb describes *your* account."""
    low = body.lower()
    best = None
    for word, kind in [(w, "out") for w in _OUT] + [(w, "in") for w in _IN]:
        pos = low.find(word)
        if pos >= 0 and (best is None or pos < best[0]):
            best = (pos, kind)
    return best[1] if best else None


def channel_of(body):
    low = body.lower()
    for name, marks in _CHANNELS:
        if any(mark in low for mark in marks):
            return name
    return "other"


def party_of(body):
    """The counterparty: a VPA if there is one, else the name after to/at/from."""
    m = _VPA.search(body)
    if m:
        return m.group(1).lower()
    for pattern in _PARTY:
        m = pattern.search(body)
        if not m:
            continue
        name = " ".join(m.group(1).split()).strip(" .-")
        if name.lower() in _NOISE_PARTY or len(name) < 3:
            continue
        if _AMOUNT.match(name):
            continue
        return name.title() if name.isupper() else name
    return ""


def account_of(body):
    m = _ACCOUNT.search(body) or _CARD.search(body)
    return m.group(1) if m else ""


def is_bank_sender(sender, body=""):
    """Does this look like a bank or payment app rather than a person?

    Indian transactional SMS arrive from six-character sender IDs with a
    two-letter route prefix (VM-HDFCBK, AD-SBIINB, JD-ICICIB). A phone number
    with a bank-shaped body is treated as not-a-bank on purpose: that is the
    exact shape of a phishing message and it must not enter the ledger.
    """
    sid = (sender or "").strip().upper()
    if not sid or sid.lstrip("+").replace("-", "").isdigit():
        return False
    if not _BANK_SENDER.match(sid):
        return False
    low = (sid + " " + body).lower()
    return any(word in low for word in _BANK_WORDS)


def parse_message(when, sender, body):
    """A Transaction if this message records one, else None.

    A message counts when it comes from a bank-shaped sender and carries both
    an amount and a direction. OTPs, balance alerts and offers fail one of
    those tests and are dropped.
    """
    if not isinstance(when, datetime):
        raise TypeError("when must be a datetime")
    if not is_bank_sender(sender, body):
        return None
    low = body.lower()
    if "otp" in low and "debited" not in low and "credited" not in low:
        return None
    amount = amount_of(body)
    direction = direction_of(body)
    if amount is None or direction is None or amount <= 0:
        return None
    return Transaction(
        when, amount, direction, party_of(body), channel_of(body),
        account_of(body), sender, body,
    )
