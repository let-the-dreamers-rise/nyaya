"""What the CLI does when the user makes the mistakes users actually make.

A typo'd filename is the single most common failure of a command-line tool,
and until these tests existed it produced a Python traceback printing an
absolute path from the maintainer's disk. These lock in the friendlier
behaviour so it cannot quietly regress.
"""

from __future__ import annotations

import pytest

from nyaya import cli


def run(argv, capsys):
    code = cli.main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


# --- missing and malformed inputs ---------------------------------------


def test_a_missing_data_file_is_a_sentence_not_a_traceback(capsys):
    code, _, err = run(["learn", "nope.tsv"], capsys)
    assert code == 1
    assert "no data file at nope.tsv" in err
    assert "data/sms.tsv" in err  # tells them what a good one looks like
    assert "Traceback" not in err


def test_a_missing_skill_file_suggests_the_command_that_makes_one(capsys):
    code, _, err = run(["classify", "missing_skill.py", "hello"], capsys)
    assert code == 1
    assert "no skill file at missing_skill.py" in err
    assert "nyaya learn" in err


def test_an_empty_corpus_says_what_a_row_should_look_like(tmp_path, capsys):
    empty = tmp_path / "empty.tsv"
    empty.write_text("", encoding="utf-8")
    code, _, err = run(["learn", str(empty)], capsys)
    assert code == 1
    assert "no usable rows" in err
    assert "tab" in err


def test_a_corpus_with_one_class_is_refused_with_the_reason(tmp_path, capsys):
    one = tmp_path / "one.tsv"
    one.write_text("\n".join(["ham\thello there"] * 12), encoding="utf-8")
    code, _, err = run(["learn", str(one)], capsys)
    assert code == 1
    assert "both classes" in err


def test_too_few_rows_names_the_count(tmp_path, capsys):
    tiny = tmp_path / "tiny.tsv"
    tiny.write_text("spam\twin cash\nham\thi there\n", encoding="utf-8")
    code, _, err = run(["learn", str(tiny)], capsys)
    assert code == 1
    assert "2 rows is too few" in err


def test_a_python_file_that_is_not_a_skill_is_named_as_such(tmp_path, capsys):
    notskill = tmp_path / "notskill.py"
    notskill.write_text("X = 1\n", encoding="utf-8")
    code, _, err = run(["classify", str(notskill), "hello"], capsys)
    assert code == 1
    assert "not a nyaya skill" in err


def test_a_directory_where_a_file_belongs_is_explained(tmp_path, capsys):
    code, _, err = run(["learn", str(tmp_path)], capsys)
    assert code == 1
    assert "directory" in err or "no data file" in err


# --- the bare invocation -------------------------------------------------


def test_running_with_no_arguments_shows_help_and_succeeds(capsys):
    code, out, _ = run([], capsys)
    assert code == 0
    assert "learn" in out and "explain" in out


# --- the happy path still works -----------------------------------------


def test_learn_then_explain_round_trips(tmp_path, capsys):
    data = tmp_path / "d.tsv"
    rows = ["spam\twin a free prize now claim cash"] * 8 + [
        "ham\tsee you at home tonight sorry"
    ] * 8
    data.write_text("\n".join(rows), encoding="utf-8")
    skill = tmp_path / "s.py"

    code, out, _ = run(["learn", str(data), "-o", str(skill)], capsys)
    assert code == 0 and skill.exists()
    assert "held-out" in out

    code, out, _ = run(["explain", str(skill), "win a free prize"], capsys)
    assert code == 0
    assert "verdict" in out


@pytest.mark.parametrize("command", ["learn", "eval", "classify", "explain"])
def test_every_subcommand_has_help(command, capsys):
    with pytest.raises(SystemExit) as exit_info:
        cli.main([command, "--help"])
    assert exit_info.value.code == 0
