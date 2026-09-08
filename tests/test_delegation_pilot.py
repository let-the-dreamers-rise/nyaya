"""The delegation pilot counts what it says it counts."""

import importlib.util
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "delegation_script", Path(__file__).resolve().parents[1] / "scripts" / "delegation.py")
delegation = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(delegation)


class Oracle:
    """Knows the next frame; commits only when something will change."""

    def __init__(self, chain):
        self.answers = [after for _, _, after in chain]
        self.i = 0

    def predict(self, board, action):
        out = self.answers[self.i]
        self.i += 1
        return out

    def observe(self, before, action, after):
        pass


class Wrong:
    def predict(self, board, action):
        return ["X" * len(row) for row in board]

    def observe(self, *args):
        pass


class Silent:
    def predict(self, board, action):
        return list(board)

    def observe(self, *args):
        pass


CHAIN = [
    (["..", ".."], "UP", ["a.", ".."]),   # a change
    (["a.", ".."], "UP", ["a.", ".."]),   # a no-op
    (["a.", ".."], "UP", [".a", ".."]),   # a change
]


def test_oracle_delegates_every_change_and_names_the_noop():
    counts = delegation.measure(Oracle(CHAIN), CHAIN)
    assert counts == {"n": 3, "commits": 2, "exact": 3, "delegable": 2, "noops": 1, "perfect_f1": 2}


def test_wrong_commits_everywhere_and_delegates_nothing():
    counts = delegation.measure(Wrong(), CHAIN)
    assert counts["commits"] == 3 and counts["delegable"] == 0 and counts["exact"] == 0


def test_silent_gets_only_the_noop():
    counts = delegation.measure(Silent(), CHAIN)
    assert counts["commits"] == 0 and counts["noops"] == 1 and counts["delegable"] == 0


def test_stable_effect_waits_for_two_identical_effects():
    m = delegation.StableEffect(k=2)
    a, b = ["..", ".."], ["a.", ".."]
    assert m.predict(a, "UP") == a            # never seen
    m.observe(a, "UP", b)
    assert m.predict(a, "UP") == a            # seen once, still silent
    m.observe(a, "UP", b)
    assert m.predict(a, "UP") == b            # same effect twice, commits
    m.observe(a, "UP", [".a", ".."])          # a different effect breaks the streak
    assert m.predict(a, "UP") == a


def test_calibrated_synthesis_restores_its_rules_after_predicting():
    m = delegation.CalibratedSynthesis(min_support=1000)
    for _ in range(12):
        m.observe(["a..", "..."], "RIGHT", [".a.", "..."])
    before = list(m.learner.rules)
    m.predict(["a..", "..."], "RIGHT")
    assert m.learner.rules == before


def test_build_knows_the_calibrated_names():
    assert isinstance(delegation.build("last-effect-stable"), delegation.StableEffect)
    assert delegation.build("dsl-cal-16").min_support == 16


def test_table_renders_percentages():
    text = delegation.table({"m": {"n": 4, "commits": 2, "exact": 1, "delegable": 1, "noops": 0, "perfect_f1": 1}}, "t")
    assert "50.0%" in text and "25.0%" in text and "delegable" in text
