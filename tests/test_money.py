"""The money witness: parsing Indian bank SMS, learning from them, serving
the result to the phone's own browser, and never anywhere else."""

import json
import threading
import urllib.request
from datetime import datetime

import pytest

from nyaya.money import parse, serve, sources
from nyaya.money import cli as money_cli
from nyaya.money.witness import (
    amount_band, beliefs, examples_payee, rupees, to_skill, witness,
)
from nyaya import synthesis

T = datetime(2026, 9, 7, 19, 30)


# --- parsing ---------------------------------------------------------------


def test_hdfc_upi_payment_with_vpa():
    t = parse.parse_message(T, "VM-HDFCBK",
        "Sent Rs.450.00 From HDFC Bank A/C *4521 To zomato@ybl On 07/09/26 Ref 526 Not You? Call 18002586161")
    assert t.direction == "out" and t.amount == 450.0
    assert t.party == "zomato@ybl" and t.channel == "upi" and t.account == "4521"


def test_hdfc_neft_credit_names_the_payer():
    t = parse.parse_message(T, "VM-HDFCBK",
        "Rs.62000.00 credited to a/c XX4521 on 01-09-26 by NEFT ACME PAYROLL. Avl bal Rs.84210.55")
    assert t.direction == "in" and t.amount == 62000.0
    assert t.party == "Acme Payroll" and t.channel == "transfer"


def test_icici_semicolon_format():
    t = parse.parse_message(T, "JD-ICICIB",
        "ICICI Bank Acct XX3210 debited for Rs 1,299.00 on 14-Aug-26; JIO PREPAID credited. UPI:5212. Call 18002662 for dispute")
    assert t.direction == "out" and t.amount == 1299.0
    assert t.party == "Jio Prepaid" and t.account == "3210" and t.channel == "upi"


def test_card_spend_at_merchant():
    t = parse.parse_message(T, "VM-HDFCBK",
        "Rs.2,150.00 spent on HDFC Bank Card x9012 at AMAZON on 03-09-26. Avl limit Rs.1,20,000")
    assert t.party == "Amazon" and t.channel == "card" and t.amount == 2150.0


def test_lakh_comma_style_amount():
    assert parse.amount_of("Rs 1,20,000.50 debited") == 120000.5


def test_otp_and_balance_and_promo_are_not_transactions():
    assert parse.parse_message(T, "VM-HDFCBK", "OTP is 482913 for txn of Rs 450.00 at ZOMATO. Do not share.") is None
    assert parse.parse_message(T, "VM-HDFCBK", "Avl bal in HDFC Bank A/C *4521 is Rs.41,230.55") is None
    assert parse.parse_message(T, "AD-MYNTRA", "Flat 50% off. Rs.499 only. Ends tonight!") is None


def test_phishing_from_a_phone_number_never_enters_the_ledger():
    body = "Rs.12000.00 debited from your SBI a/c. Call 9811234567 if not you"
    assert parse.is_bank_sender("+919811234567", body) is False
    assert parse.parse_message(T, "+919811234567", body) is None


# --- sources ---------------------------------------------------------------


def test_text_export_round_trips(tmp_path):
    msgs = sources.demo_messages(days=10)
    path = tmp_path / "sms.txt"
    sources.write_text(msgs, path)
    back = sources.read_text(path)
    assert [m["body"] for m in back] == [m["body"] for m in msgs]
    assert back[0]["when"] == msgs[0]["when"].replace(microsecond=0)


def test_xml_backup_reads_inbox_only(tmp_path):
    path = tmp_path / "sms.xml"
    path.write_text(
        '<?xml version="1.0"?><smses count="2">'
        '<sms address="VM-HDFCBK" date="1788800000000" type="1" body="Sent Rs.30.00 From HDFC Bank A/C *4521 To chaiwala@ybl On 07/09/26 Ref 1" />'
        '<sms address="+919876543210" date="1788800001000" type="2" body="sent it" />'
        "</smses>", encoding="utf-8")
    msgs = sources.read_xml(path)
    assert len(msgs) == 1 and msgs[0]["sender"] == "VM-HDFCBK"


def test_malformed_xml_is_a_value_error(tmp_path):
    path = tmp_path / "bad.xml"
    path.write_text('<smses><sms address="x" date="1" body="unclosed', encoding="utf-8")
    with pytest.raises(ValueError) as err:
        sources.read_xml(path)
    assert "SMS Backup" in str(err.value)


def test_termux_missing_says_what_to_do(monkeypatch):
    monkeypatch.setattr(sources.shutil, "which", lambda name: None)
    with pytest.raises(FileNotFoundError) as err:
        sources.read_termux()
    assert "F-Droid" in str(err.value)


def test_termux_reader_uses_the_injected_runner():
    raw = json.dumps([{"threadid": 1, "type": "inbox", "read": True, "number": "VM-HDFCBK",
                       "received": "2026-09-07 08:05:11", "body": "hello"}])
    calls = []
    msgs = sources.read_termux(limit=5, runner=lambda args: calls.append(args) or raw)
    assert calls[0][:3] == ["termux-sms-list", "-l", "5"]
    assert msgs[0]["sender"] == "VM-HDFCBK" and msgs[0]["when"].hour == 8


def test_demo_is_deterministic_and_rich():
    a, b = sources.demo_messages(), sources.demo_messages()
    assert [m["body"] for m in a] == [m["body"] for m in b]
    txns = sources.transactions(a)
    assert len(txns) > 150
    assert all(t.party for t in txns), "every demo transaction names a party"


# --- the witness -----------------------------------------------------------


@pytest.fixture(scope="module")
def demo():
    msgs = sources.demo_messages()
    return msgs, witness(msgs)


def test_bands_and_rupees():
    assert amount_band(45) == "under Rs 100" and amount_band(18000) == "Rs 10,000 to 50,000"
    assert rupees(1234567) == "Rs 12,34,567" and rupees(999) == "Rs 999"


def test_the_scam_is_the_only_alert(demo):
    _, r = demo
    alerts = [s for s in r["sentences"] if s["kind"] == "alert"]
    assert len(alerts) == 1
    assert "kyc.update9@ybl" in alerts[0]["text"] and "9 minutes" in alerts[0]["text"]
    assert "'kyc'" in alerts[0]["text"]


def test_rent_is_a_monthly_fact_not_a_stranger(demo):
    _, r = demo
    texts = [s["text"] for s in r["sentences"]]
    assert any(t.startswith("Every month around the 2nd, Rs 18,000 to sunil.rent@okaxis") for t in texts)
    assert not any("sunil.rent@okaxis" in t and "never paid before" in t for t in texts)


def test_chai_belief_carries_all_its_evidence(demo):
    _, r = demo
    chai = [s for s in r["sentences"] if s["kind"] == "belief" and "chaiwala@ybl" in s["text"]]
    assert chai and chai[0]["evidence"]["fired on"] == 72
    assert "Right 72 of 72 times" in chai[0]["text"]


def test_one_habit_is_one_sentence(demo):
    """'A payment of under Rs 100 goes to chai' and 'Chai is under Rs 100' are
    the same belief found by two passes; a reader should see it once."""
    _, r = demo
    chai = [s for s in r["sentences"] if s["kind"] == "belief" and "chaiwala" in s["text"].lower()]
    assert len(chai) == 1, [s["text"] for s in chai]


def test_beliefs_are_scored_against_everything(demo):
    msgs, _ = demo
    txns = sources.transactions(msgs)
    examples = examples_payee(txns)
    for s in beliefs(txns, {}):
        ev = s["evidence"]
        assert ev["right"] / ev["fired on"] >= 0.9
    # and the payee pass pins to a constant so one habit is one rule
    assert all(obs["self"] == "money" for obs, _ in examples)


def test_muting_and_nicknames_change_what_is_said(demo):
    msgs, r = demo
    target = next(s for s in r["sentences"] if s["kind"] == "belief")
    again = witness(msgs, {"muted": [target["id"]], "nicknames": {"sunil.rent@okaxis": "Rent"}})
    assert target["id"] not in [s["id"] for s in again["sentences"]]
    assert again["muted"] == 1
    assert any("to Rent." in s["text"] for s in again["sentences"])


def test_skill_renders_as_editable_python(demo):
    _, r = demo
    text = to_skill(r).render()
    assert "RULES = [" in text and "money" in text
    namespace = {}
    exec(compile(text, "money_skill.py", "exec"), namespace)
    assert len(namespace["RULES"]) == len(r["sentences"])


def test_no_messages_is_not_an_error():
    assert witness([])["count"] == 0


# --- the page --------------------------------------------------------------


@pytest.fixture
def server(tmp_path):
    ledger = serve.Ledger("demo", home=tmp_path)
    httpd = serve.make_server(ledger, port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield "http://127.0.0.1:{0}".format(httpd.server_port), ledger
    httpd.shutdown()
    httpd.server_close()


def _get(url):
    with urllib.request.urlopen(url, timeout=5) as resp:
        return resp.status, resp.read().decode("utf-8")


def _post(url, payload):
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def test_server_binds_loopback_only(server):
    base, ledger = server
    httpd = serve.make_server(ledger, port=0)
    assert httpd.server_address[0] == "127.0.0.1"
    httpd.server_close()


def test_page_loads_nothing_from_outside(server):
    base, _ = server
    status, html = _get(base + "/")
    assert status == 200 and "Nothing leaves this phone" in html
    assert "http://" not in html.replace("http://127.0.0.1", "") and "https://" not in html
    assert "<link" not in html and 'src="' not in html


def test_witness_endpoint_and_mute_persist(server, tmp_path):
    base, ledger = server
    status, body = _get(base + "/api/witness")
    data = json.loads(body)
    assert status == 200 and data["count"] > 150
    first = data["sentences"][0]["id"]
    _post(base + "/api/prefs", {"muted": [first], "nicknames": {}})
    _, body = _get(base + "/api/witness")
    assert first not in [s["id"] for s in json.loads(body)["sentences"]]
    assert json.loads((tmp_path / "prefs.json").read_text())["muted"] == [first]


def test_unknown_path_is_404(server):
    base, _ = server
    with pytest.raises(urllib.error.HTTPError) as err:
        _get(base + "/nope")
    assert err.value.code == 404


# --- the command -----------------------------------------------------------


class _Out:
    def __init__(self):
        self.text = ""

    def write(self, s):
        self.text += s


def test_report_prints_the_three_kinds(tmp_path):
    out = _Out()
    assert money_cli.main(["--home", str(tmp_path), "report", "demo"], out) == 0
    assert "Look at this" in out.text and "Learned" in out.text and "shape of a scam" in out.text


def test_skill_command_writes_a_file(tmp_path):
    out = _Out()
    target = tmp_path / "mine.py"
    assert money_cli.main(["--home", str(tmp_path), "skill", "demo", "-o", str(target)], out) == 0
    assert "RULES" in target.read_text(encoding="utf-8")


def test_missing_file_is_a_clean_error(tmp_path, capsys):
    assert money_cli.main(["--home", str(tmp_path), "report", str(tmp_path / "none.xml")], _Out()) == 1
    assert "no such file" in capsys.readouterr().err


def test_synthesis_score_is_the_one_the_witness_reuses():
    assert callable(synthesis._score)
