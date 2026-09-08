"""Where the messages come from: the phone, an export, a file, or the demo.

Every reader returns the same thing, a list of dicts with `when` (datetime),
`sender` (str) and `body` (str), oldest first. The phone reader shells out
to Termux:API, which is the only way a plain Python process can read SMS on
Android without being the default SMS app. The XML reader takes the file
that the SMS Backup & Restore app writes, for phones without Termux.
"""

from __future__ import annotations

import json
import random
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree

from .parse import parse_message

_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S")


def _when(value):
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    if text.isdigit():
        return datetime.fromtimestamp(int(text) / 1000.0)
    for fmt in _FORMATS:
        try:
            return datetime.strptime(text[: len(fmt) + 2], fmt)
        except ValueError:
            continue
    raise ValueError("cannot read a time from {0!r}".format(text))


def _message(when, sender, body):
    return {"when": _when(when), "sender": str(sender or ""), "body": str(body or "")}


def read_termux(limit=3000, runner=None):
    """Inbox via `termux-sms-list`. `runner` is injectable for tests."""
    run = runner or (lambda args: subprocess.run(
        args, capture_output=True, text=True, check=True).stdout)
    raw = run(["termux-sms-list", "-l", str(limit), "-t", "inbox"])
    return _from_termux_json(raw)


def _from_termux_json(raw):
    out = []
    for row in json.loads(raw or "[]"):
        sender = row.get("sender") or row.get("number") or ""
        out.append(_message(row.get("received") or row.get("date"), sender, row.get("body")))
    return sorted(out, key=lambda m: m["when"])


def read_xml(path):
    """SMS Backup & Restore export: <sms address= date= type= body= />."""
    out = []
    for _, el in ElementTree.iterparse(str(path)):
        if el.tag != "sms" or el.get("type") not in (None, "1"):
            continue
        out.append(_message(el.get("date"), el.get("address"), el.get("body")))
        el.clear()
    return sorted(out, key=lambda m: m["when"])


def read_text(path):
    """One message per line: time<TAB>sender<TAB>body. '#' lines ignored."""
    out = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t", 2)
        if len(parts) != 3:
            raise ValueError("expected time<TAB>sender<TAB>body, got {0!r}".format(line[:60]))
        out.append(_message(*parts))
    return sorted(out, key=lambda m: m["when"])


def read_json(path):
    raw = Path(path).read_text(encoding="utf-8")
    rows = json.loads(raw)
    if rows and ("received" in rows[0] or "number" in rows[0]):
        return _from_termux_json(raw)
    return sorted(
        (_message(r["when"], r.get("sender"), r.get("body")) for r in rows),
        key=lambda m: m["when"],
    )


def load(source):
    """'termux', 'demo', or a path ending .xml / .json / .txt / .tsv."""
    if source == "termux":
        return read_termux()
    if source == "demo":
        return demo_messages()
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError("no such file: {0}".format(path))
    ext = path.suffix.lower()
    if ext == ".xml":
        return read_xml(path)
    if ext == ".json":
        return read_json(path)
    return read_text(path)


def write_text(messages, path):
    lines = ["# time\tsender\tbody"]
    for m in messages:
        body = m["body"].replace("\t", " ").replace("\n", " ")
        lines.append("{0}\t{1}\t{2}".format(
            m["when"].strftime("%Y-%m-%d %H:%M:%S"), m["sender"], body))
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def transactions(messages):
    """Every message that records money moving, oldest first."""
    out = []
    for m in messages:
        t = parse_message(m["when"], m["sender"], m["body"])
        if t is not None:
            out.append(t)
    return out


# --- the demo person -------------------------------------------------------

_HDFC = "VM-HDFCBK"
_ICICI = "JD-ICICIB"


def _hdfc_out(amount, party, when, ref):
    return "Sent Rs.{0:.2f} From HDFC Bank A/C *4521 To {1} On {2} Ref {3} Not You? Call 18002586161/SMS BLOCK UPI to 7308080808".format(
        amount, party, when.strftime("%d/%m/%y"), ref)


def _hdfc_in(amount, party, when, bal):
    return "Rs.{0:.2f} credited to a/c XX4521 on {1} by NEFT {2}. Avl bal Rs.{3:.2f}".format(
        amount, when.strftime("%d-%m-%y"), party, bal)


def _hdfc_upi_in(amount, vpa, when):
    return "Rs.{0:.2f} credited to a/c XX4521 on {1} by UPI {2} Ref 5{3:08d}".format(
        amount, when.strftime("%d-%m-%y"), vpa, int(amount * 7) % 10 ** 8)


def _hdfc_card(amount, merchant, when):
    return "Rs.{0:.2f} spent on HDFC Bank Card x9012 at {1} on {2}. Avl limit Rs.1,20,000".format(
        amount, merchant, when.strftime("%d-%m-%y"))


def _hdfc_atm(amount, when):
    return "Rs.{0:.2f} withdrawn from HDFC Bank A/C *4521 at ATM MG ROAD on {1}. Avl bal Rs.30,412.10".format(
        amount, when.strftime("%d/%m/%y"))


def _icici_out(amount, party, when, ref):
    return "ICICI Bank Acct XX3210 debited for Rs {0:,.2f} on {1}; {2} credited. UPI:{3}. Call 18002662 for dispute".format(
        amount, when.strftime("%d-%b-%y"), party, ref)


def demo_messages(days=100, end=None, seed=7):
    """A hundred days of one fictional person's phone: Meera, salaried,
    Bangalore, two bank accounts, one bad afternoon in late August.

    Deterministic for a given seed so the demo reads the same every time.
    Nothing in it is a real person, account or number.
    """
    rng = random.Random(seed)
    end = end or datetime(2026, 9, 8, 12, 0)
    start = (end - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0)
    out = []
    ref = 100000

    def add(when, sender, body):
        out.append(_message(when, sender, body))

    day = start
    while day <= end:
        d, wd = day.day, day.weekday()  # Mon=0
        if d == 1:
            add(day.replace(hour=10, minute=2), _HDFC, _hdfc_in(62000, "ACME PAYROLL", day, 84210.55))
        if d == 2:
            ref += 1
            add(day.replace(hour=8, minute=30), _HDFC, _hdfc_out(18000, "sunil.rent@okaxis", day, ref))
        if d == 5:
            ref += 1
            add(day.replace(hour=9, minute=0), _ICICI, _icici_out(5000, "GROWW MF SIP", day, ref))
        if (day - start).days % 28 == 2:
            ref += 1
            add(day.replace(hour=7, minute=45), _ICICI, _icici_out(299, "JIO PREPAID", day, ref))
        if d == 15:
            add(day.replace(hour=13, minute=10), _HDFC, _hdfc_atm(10000, day))
        if wd < 5:
            ref += 1
            add(day.replace(hour=8, minute=rng.randint(0, 20)), _HDFC,
                _hdfc_out(rng.choice((20, 30, 40)), "chaiwala@ybl", day, ref))
            if rng.random() < 0.6:
                ref += 1
                add(day.replace(hour=8, minute=rng.randint(30, 59)), _HDFC,
                    _hdfc_out(rng.randint(120, 260), "UBER INDIA", day, ref))
        if wd in (4, 6):
            ref += 1
            add(day.replace(hour=19 + rng.randint(0, 1), minute=rng.randint(0, 59)), _HDFC,
                _hdfc_out(rng.randint(380, 720), "ZOMATO", day, ref))
        if wd == 2:
            ref += 1
            add(day.replace(hour=20, minute=rng.randint(0, 40)), _HDFC,
                _hdfc_out(rng.randint(250, 450), "SWIGGY", day, ref))
        if wd == 5:
            add(day.replace(hour=10 + rng.randint(0, 1), minute=rng.randint(0, 59)), _HDFC,
                _hdfc_card(rng.randint(1400, 2600), "BIGBASKET", day))
        if (day - start).days % 9 == 4:
            add(day.replace(hour=22, minute=rng.randint(0, 30)), _HDFC,
                _hdfc_card(rng.randint(600, 3500), "AMAZON", day))
        if (day - start).days % 19 == 7:
            add(day.replace(hour=15, minute=rng.randint(0, 59)), _HDFC,
                _hdfc_upi_in(1200, "priya.s@okicici", day))
        if (day - start).days % 11 == 3:
            add(day.replace(hour=12, minute=5), _HDFC,
                "OTP is {0} for txn of Rs 450.00 at ZOMATO. Do not share OTP with anyone.".format(rng.randint(100000, 999999)))
        if (day - start).days % 13 == 6:
            add(day.replace(hour=11, minute=0), "AD-MYNTRA", "Flat 50% off on your favourite brands. Hurry, ends tonight!")
        if (day - start).days % 17 == 9:
            add(day.replace(hour=21, minute=15), "+919876543210", "bro send 500 for the cab")
        day += timedelta(days=1)

    scam_day = end - timedelta(days=12)
    add(scam_day.replace(hour=14, minute=12), "+919811234567",
        "Dear customer your SBI account will be BLOCKED today. Update KYC immediately at http://sbi-kyc-update.in or call 9811234567")
    ref += 1
    add(scam_day.replace(hour=14, minute=21), _HDFC, _hdfc_out(12000, "kyc.update9@ybl", scam_day, ref))
    return sorted(out, key=lambda m: m["when"])
