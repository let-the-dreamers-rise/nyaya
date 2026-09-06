"""The substrate has to be trustworthy before any number on it means anything.

These tests guard the four properties a reviewer would want to check by hand:
the packing is lossless, the replay is causal, the headline metric cannot be
gamed by predicting nothing, and pooling is not averaging.
"""

from __future__ import annotations

import pytest

from bench import corpus, methods, pack, replay


# --- packing -------------------------------------------------------------


def test_diff_then_apply_restores_the_frame_exactly():
    before = ["abc", "def"]
    after = ["abX", "dYf"]
    assert pack.apply_diff(before, pack.diff(before, after)) == after


def test_diff_of_identical_frames_is_empty():
    board = ["aaa", "bbb"]
    assert pack.diff(board, board) == []


def test_diff_records_only_changed_cells():
    cells = pack.diff(["aaa", "bbb"], ["aXa", "bbb"])
    assert cells == [[0, 1, "X"]]


def test_engine_actions_are_named_not_numbered():
    # A learner keyed on 'ACTION1' would silently mean nothing to a reader.
    assert pack.ENGINE["ACTION1"] == "UP"
    assert pack.ENGINE["ACTION4"] == "RIGHT"


def test_read_action_normalises_a_click_to_its_coordinates():
    action = pack.read_action(
        {"action_name": "ACTION6", "action_display": "click row=3, col=5"}
    )
    assert action == ["MOUSE", 3, 5]


def test_read_action_without_coordinates_stays_a_bare_name():
    assert pack.read_action({"action_name": "ACTION6"}) == "MOUSE"


def test_unknown_action_names_survive_rather_than_vanish():
    assert pack.read_action({"action_name": "RESET"}) == "RESET"
    assert pack.read_action({}) is None


# --- the metric ----------------------------------------------------------


def test_changed_cell_scoring_ignores_unchanged_scenery():
    before = ["aaaa"]
    after = ["aaXa"]
    exact, tp, fp, fn = replay.score_step(after, before, after)
    assert exact and tp == 1 and fp == 0 and fn == 0


def test_predicting_nothing_scores_zero_not_high():
    """The whole reason changed-cell F1 is the headline."""
    before = ["aaaa"]
    after = ["aaXa"]
    _, tp, fp, fn = replay.score_step(before, before, after)
    assert tp == 0 and fn == 1
    assert replay.f1_of(tp, fp, fn) == 0.0


def test_a_wrong_guess_costs_both_a_miss_and_a_false_alarm():
    before = ["aaaa"]
    after = ["aaXa"]
    _, tp, fp, fn = replay.score_step(["aYaa"], before, after)
    assert tp == 0 and fp == 1 and fn == 1


def test_f1_of_is_zero_when_nothing_was_predicted_or_missed():
    assert replay.f1_of(0, 0, 0) == 0.0


# --- the protocol --------------------------------------------------------


class Peeker:
    """A method that would score perfectly if the harness let it cheat."""

    def __init__(self):
        self.seen: list = []
        self.order: list = []

    def predict(self, board, action):
        self.order.append("predict")
        # Only knowledge from *previous* transitions is available.
        for before, act, after in self.seen:
            if before == board and act == action:
                return after
        return list(board)

    def observe(self, before, action, after):
        self.order.append("observe")
        self.seen.append((before, action, after))


def _chain():
    a = ["aa", "aa"]
    b = ["Xa", "aa"]
    c = ["XX", "aa"]
    return [(a, "UP", b), (b, "UP", c)]


def test_predict_is_always_called_before_observe():
    peeker = Peeker()
    replay.replay(peeker, _chain())
    assert peeker.order[:2] == ["predict", "observe"]
    assert peeker.order == ["predict", "observe", "predict", "observe"]


def test_a_method_cannot_score_the_transition_it_is_currently_predicting():
    """Both transitions here are novel, so perfect recall must still score 0."""
    result = replay.replay(Peeker(), _chain())
    assert result["tp"] == 0


def test_replay_reports_cost_alongside_quality():
    result = replay.replay(methods.build("nyaya-templates"), _chain())
    assert "tokens" in result and "ms_per_step" in result
    assert result["tokens"] == 0


# --- aggregation ---------------------------------------------------------


def test_cells_are_pooled_not_averaged_over_episodes():
    """A 1-transition episode must not outweigh a 100-transition one."""
    def row(tp, fp, fn, transitions, exact):
        return {
            "tp": tp, "fp": fp, "fn": fn, "transitions": transitions,
            "exact": exact, "tokens": 0, "seconds": 0.0, "to_threshold": None,
        }

    tiny = row(tp=1, fp=0, fn=0, transitions=1, exact=1.0)
    large = row(tp=0, fp=100, fn=100, transitions=100, exact=0.0)
    pooled = replay.aggregate([tiny, large])

    # Averaging per-episode F1 would give (1.0 + 0.0) / 2 = 0.5.
    assert pooled["f1"] < 0.02
    assert pooled["transitions"] == 101
    # Exact-frame rate is weighted by episode length for the same reason.
    assert pooled["exact"] == pytest.approx(1 / 101)


# --- the registry --------------------------------------------------------


def test_the_null_baseline_is_registered_and_predicts_no_change():
    null = methods.build("copy-forward")
    board = ["ab", "cd"]
    assert null.predict(board, "UP") == list(board)


def test_unknown_method_names_fail_loudly_with_the_known_list():
    with pytest.raises(KeyError) as raised:
        methods.build("no-such-method")
    assert "copy-forward" in str(raised.value)


def test_registering_a_method_makes_it_runnable():
    @methods.register("test-only-echo")
    class Echo:
        def predict(self, board, action):
            return list(board)

        def observe(self, before, action, after):
            pass

    try:
        assert isinstance(methods.build("test-only-echo"), Echo)
    finally:
        methods.REGISTRY.pop("test-only-echo", None)


# --- the shipped corpora -------------------------------------------------


@pytest.mark.parametrize("name", ["bench/corpus", "bench/corpus-heldout"])
def test_both_corpora_ship_with_the_repository(name):
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    found = corpus.episodes(root / name)
    assert len(found) == 25, f"{name} should hold 25 episodes, found {len(found)}"


def test_a_packed_episode_replays_into_usable_transitions():
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    chain = corpus.transitions(corpus.episodes(root / "bench/corpus")[0])
    assert chain, "the first episode should yield transitions"
    before, action, after = chain[0]
    assert before and after and action
    assert len(before) == len(after), "a transition must not change the grid size"
