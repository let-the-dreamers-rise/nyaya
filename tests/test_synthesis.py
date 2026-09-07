"""The searcher has to find real mechanisms and refuse to invent fake ones.

These tests encode what went wrong on the way here: it learned no-op rules,
it over-fired because negatives were sampled only near changes, and it stopped
searching the moment one outcome proved hard. Each has a test now.
"""

from __future__ import annotations

from nyaya import synthesis as syn


# --- primitives ----------------------------------------------------------


def test_the_engine_knows_nothing_about_grids_until_given_primitives():
    assert "grid" in syn.PRIMITIVE_SETS
    names = [name for name, _ in syn.PRIMITIVE_SETS["grid"]()]
    assert "self" in names and "action" in names


def test_off_board_is_an_observation_not_a_crash():
    prims = syn.PRIMITIVE_SETS["grid"]()
    observed = dict(syn.features(prims, ["ab"], 0, 0, "UP"))
    assert observed["self"] == "a"
    assert observed["left"] is None
    assert observed["up"] is None


def test_relative_primitives_describe_a_cell_by_where_the_action_points():
    prims = syn.PRIMITIVE_SETS["grid-relative"]()
    grid = ["abc", "def", "ghi"]
    right = dict(syn.features(prims, grid, 1, 1, "RIGHT"))
    down = dict(syn.features(prims, grid, 1, 1, "DOWN"))
    assert right["self"] == down["self"] == "e"
    assert right["ahead"] == "f" and right["behind"] == "d"
    assert down["ahead"] == "h" and down["behind"] == "b"


def test_the_same_mechanism_looks_identical_in_every_direction():
    """The whole reason this primitive set exists: one rule, not four."""
    prims = syn.PRIMITIVE_SETS["grid-relative"]()
    moving_right = dict(syn.features(prims, ["...", ".@.", "..."], 1, 2, "RIGHT"))
    moving_down = dict(syn.features(prims, ["...", ".@.", "..."], 2, 1, "DOWN"))
    assert moving_right["behind"] == moving_down["behind"] == "@"


def test_a_non_directional_action_is_flagged_rather_than_special_cased():
    prims = syn.PRIMITIVE_SETS["grid-relative"]()
    click = dict(syn.features(prims, ["abc"], 0, 1, ("MOUSE", 3, 4)))
    assert click["directional"] is False
    assert click["ahead"] == click["self"]  # zero displacement, no crash


def test_relative_primitives_handle_the_board_edge():
    prims = syn.PRIMITIVE_SETS["grid-relative"]()
    edge = dict(syn.features(prims, ["ab"], 0, 0, "LEFT"))
    assert edge["ahead"] is None


def test_a_registered_primitive_set_is_the_only_domain_knowledge():
    @syn.register_primitives("unit-test-set")
    def _tiny():
        return [("self", lambda g, r, c, a: g[r][c])]

    try:
        assert "unit-test-set" in syn.PRIMITIVE_SETS
    finally:
        syn.PRIMITIVE_SETS.pop("unit-test-set", None)


# --- rules ---------------------------------------------------------------


def test_a_rule_reads_as_a_sentence_a_person_can_disagree_with():
    rule = syn.Rule([("self", "."), ("action", "UP")], "@", 12, 0.95)
    text = rule.sentence()
    assert "self is '.'" in text and "action is 'UP'" in text
    assert "becomes '@'" in text


def test_off_board_conditions_read_as_words_not_as_none():
    assert "off-board" in syn.Rule([("up", None)], "x").sentence()


def test_a_rule_carries_the_evidence_that_earned_it():
    assert syn.Rule([("self", "a")], "b", 9, 0.912).as_evidence() == {
        "fired on": 9,
        "right": 0.912,
    }


# --- the search ----------------------------------------------------------


def _examples(pairs):
    return [(dict(obs), out) for obs, out in pairs]


def test_it_finds_a_mechanism_that_is_actually_there():
    ex = _examples(
        [({"self": ".", "left": "@", "action": "R"}, "@")] * 10
        + [({"self": ".", "left": ".", "action": "R"}, ".")] * 30
    )
    rules = syn.synthesise(ex, min_support=3)
    assert rules, "a clean deterministic mechanism must be found"
    assert rules[0].outcome == "@"
    assert ("left", "@") in rules[0].conditions


def test_it_never_learns_a_rule_that_changes_nothing():
    """It once learned \"when self is 'b', it becomes 'b'\" with support 4,755."""
    ex = _examples([({"self": "b", "left": "b"}, "b")] * 200)
    for rule in syn.synthesise(ex, min_support=2):
        assert rule.outcome != dict(rule.conditions).get("self")


def test_noise_alone_yields_no_rules():
    ex = _examples(
        [({"self": ".", "left": "@"}, "@")] * 5
        + [({"self": ".", "left": "@"}, ".")] * 50
    )
    assert syn.synthesise(ex, min_support=3, min_precision=0.9) == []


def test_one_hard_outcome_does_not_end_the_whole_search():
    """The bug that dropped recall to 8% while precision stayed at 86%."""
    hard = [({"self": "x", "left": str(i % 7)}, "H") for i in range(40)]
    easy = [({"self": "y", "left": "k", "action": "A"}, "E")] * 20
    filler = [({"self": "y", "left": "z", "action": "A"}, "y")] * 40
    rules = syn.synthesise(_examples(hard + easy + filler), min_support=4)
    assert any(r.outcome == "E" for r in rules), (
        "the learnable mechanism must survive an unlearnable one being tried first"
    )


def test_every_rule_is_pinned_to_what_the_cell_currently_is():
    ex = _examples(
        [({"self": ".", "left": "@", "action": "R"}, "@")] * 10
        + [({"self": ".", "left": ".", "action": "R"}, ".")] * 30
    )
    for rule in syn.synthesise(ex, min_support=3):
        assert "self" in dict(rule.conditions)


# --- the learner ---------------------------------------------------------


def _slide(n):
    """A dot that moves one cell right each time RIGHT is taken."""
    chain = []
    for i in range(n):
        before = ["." * 12, "." * i + "@" + "." * (11 - i), "." * 12]
        after = ["." * 12, "." * (i + 1) + "@" + "." * (10 - i), "." * 12]
        chain.append((before, "RIGHT", after))
    return chain


def test_the_learner_predicts_before_it_has_learned_anything():
    learner = syn.SynthesisLearner()
    board = ["ab", "cd"]
    assert learner.predict(board, "UP") == list(board)


def test_it_learns_a_moving_object_from_its_own_observations():
    learner = syn.SynthesisLearner(min_support=3)
    chain = _slide(9)
    for before, action, after in chain:
        learner.observe(before, action, after)
    learner._fit()
    assert learner.rules, "a sliding object is a mechanism it must be able to state"


def test_it_reports_zero_tokens_because_no_model_is_called():
    assert syn.SynthesisLearner().tokens == 0


def test_the_theory_it_learns_is_the_same_readable_artefact_as_every_other():
    import ast

    learner = syn.SynthesisLearner(min_support=3)
    for before, action, after in _slide(9):
        learner.observe(before, action, after)
    learner._fit()

    artefact = learner.to_skill()
    assert artefact.domain == "grid world"
    ast.parse(artefact.render())
    assert artefact.provenance["transitions observed"] == 9


def test_both_hypothesis_classes_are_registered_so_the_benchmark_decides():
    from bench import methods

    for name in ("dsl-synthesis", "dsl-synthesis-rel"):
        built = methods.build(name)
        assert built.tokens == 0
        assert built.predict(["ab"], "UP") == ["ab"]


def test_the_relative_learner_learns_a_slide_it_has_seen_in_one_direction():
    learner = syn.SynthesisLearner(primitive_set="grid-relative", min_support=3)
    for before, action, after in _slide(9):
        learner.observe(before, action, after)
    learner._fit()
    assert learner.rules
