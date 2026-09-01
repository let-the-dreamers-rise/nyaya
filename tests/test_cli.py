"""Tests for the CLI -- the MVP surface a stranger actually touches."""
from __future__ import annotations

from pathlib import Path

import pytest

from nyaya.cli import main

SCAMS = [
    "You won Rs 500000 lottery! Pay processing fee to claim http://win.xyz",
    "KYC expired, account will be blocked. Verify immediately http://kyc.co",
    "Congratulations winner! Claim prize now, pay registration fee 5000",
    "Your parcel held at customs, pay duty at http://fedx.info immediately",
    "Earn Rs 4000 per day work from home, join now limited seats",
]
NORMALS = [
    "Meeting moved to 3pm, bring the numbers",
    "Your order is out for delivery, arriving by 8pm",
    "Happy birthday! Party kab de raha hai",
    "Recharge successful, plan valid 28 days",
    "Doctor appointment confirmed for Saturday 11:30am",
]


@pytest.fixture
def data(tmp_path: Path) -> Path:
    rows = [f"spam\t{t}" for t in SCAMS] * 3 + [f"ham\t{t}" for t in NORMALS] * 3
    path = tmp_path / "data.tsv"
    path.write_text("\n".join(rows), encoding="utf-8")
    return path


def test_learn_writes_a_skill_and_reports_held_out(data, tmp_path, capsys):
    out = tmp_path / "skill.py"
    code = main(["learn", str(data), "-o", str(out), "--min-support", "2",
                 "--min-precision", "0.8"])
    printed = capsys.readouterr().out
    assert code == 0
    assert out.is_file()
    assert "held-out" in printed and "precision" in printed
    assert "page of Python" in printed
    assert "RULES = [" in out.read_text(encoding="utf-8")


def test_learn_refuses_a_tiny_file(tmp_path, capsys):
    path = tmp_path / "tiny.tsv"
    path.write_text("spam\thello", encoding="utf-8")
    assert main(["learn", str(path)]) == 2
    assert "at least 10" in capsys.readouterr().out


def test_eval_scores_a_written_skill(data, tmp_path, capsys):
    out = tmp_path / "skill.py"
    main(["learn", str(data), "-o", str(out), "--min-support", "2",
          "--min-precision", "0.8"])
    capsys.readouterr()
    assert main(["eval", str(out), str(data)]) == 0
    printed = capsys.readouterr().out
    assert "F1" in printed and "true-positive" in printed


def test_classify_flags_a_scam_and_passes_a_normal(data, tmp_path, capsys):
    out = tmp_path / "skill.py"
    main(["learn", str(data), "-o", str(out), "--min-support", "2",
          "--min-precision", "0.8"])
    capsys.readouterr()
    code = main(["classify", str(out), SCAMS[0], NORMALS[0]])
    printed = capsys.readouterr().out
    assert code == 0
    assert "FLAG" in printed and "ok" in printed
    assert "1 flagged" in printed


def test_explain_names_the_beliefs_that_fired(data, tmp_path, capsys):
    out = tmp_path / "skill.py"
    main(["learn", str(data), "-o", str(out), "--min-support", "2",
          "--min-precision", "0.8"])
    capsys.readouterr()
    assert main(["explain", str(out), SCAMS[0]]) == 0
    printed = capsys.readouterr().out
    assert "verdict: FLAG" in printed
    assert "accuses" in printed
    assert "owning a skill" in printed
