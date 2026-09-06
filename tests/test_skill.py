"""The shared type is the claim: two learners, one readable artefact.

If these tests pass, 'agents that compile experience into rules' is a fact
about the code. If they are deleted, it goes back to being a slogan.
"""

from __future__ import annotations

import pytest

from nyaya import skill as sk
from nyaya import sms_rules as sr
from nyaya import world_model as wm


# --- the type ------------------------------------------------------------


def test_a_rule_carries_its_sentence_weight_and_evidence():
    rule = sk.Rule("asks for a fee to claim a prize", 3, "accuses", {"support": 12})
    assert rule.text.startswith("asks for a fee")
    assert rule.weight == 3
    assert "support=12" in rule.evidence_line()


def test_a_rule_without_evidence_says_so_rather_than_pretending():
    assert sk.Rule("a bare assertion").evidence_line() == ""


def test_unsupported_rules_are_findable_because_a_reviewer_looks_there_first():
    s = sk.Skill(
        "x",
        "text messages",
        [sk.Rule("backed", evidence={"support": 4}), sk.Rule("bare")],
    )
    assert [r.text for r in s.unsupported()] == ["bare"]


def test_a_skill_round_trips_through_json_unchanged():
    original = sk.Skill(
        "scam screening",
        "text messages",
        [sk.Rule("claims a prize", 2, "accuses", {"precision": 0.91})],
        {"source": "data/sms.tsv", "examples": 4459},
    )
    restored = sk.Skill.from_json(original.to_json())
    assert restored.as_dict() == original.as_dict()
    assert restored.rules == original.rules


def test_an_unknown_schema_is_refused_rather_than_guessed_at():
    with pytest.raises(ValueError):
        sk.Skill.from_dict({"schema": 999, "name": "x", "domain": "y"})


# --- the artefact --------------------------------------------------------


def test_the_rendered_file_is_valid_python():
    import ast

    s = sk.Skill("demo", "text messages", [sk.Rule("claims a prize", 2, "accuses")])
    ast.parse(s.render())


def test_the_rendered_file_leads_with_sentences_not_machinery():
    s = sk.Skill(
        "demo",
        "text messages",
        [sk.Rule("asks for a fee to claim a prize", 3, "accuses", {"support": 9})],
    )
    text = s.render()
    assert "asks for a fee to claim a prize" in text
    assert "support=9" in text  # the evidence rides along as a comment
    assert "import" not in text  # nothing to read but the beliefs


def test_provenance_travels_with_the_skill_so_it_can_be_interrogated():
    s = sk.Skill("demo", "text messages", [], {"source": "data/sms.tsv"})
    assert "data/sms.tsv" in s.render()


def test_deleting_a_rule_deletes_the_belief_from_the_artefact():
    rules = [sk.Rule("first belief"), sk.Rule("second belief")]
    full = sk.Skill("demo", "text messages", rules).render()
    trimmed = sk.Skill("demo", "text messages", rules[:1]).render()
    assert "second belief" in full
    assert "second belief" not in trimmed


# --- adapter one: text ---------------------------------------------------


def test_the_text_learner_produces_a_skill():
    examples = [("spam", "win a free prize now")] * 6 + [
        ("ham", "see you at home tonight")
    ] * 6
    learned = sr.learn(examples, min_support=2)
    s = sk.from_text_rules(learned, provenance={"source": "unit test"})

    assert isinstance(s, sk.Skill)
    assert s.domain == "text messages"
    assert len(s) == len(learned["rules"])
    assert s.provenance["threshold"] == learned["threshold"]


def test_text_rules_are_labelled_as_accusing_or_vouching():
    examples = [("spam", "win a free prize now")] * 6 + [
        ("ham", "see you at home tonight")
    ] * 6
    s = sk.from_text_rules(sr.learn(examples, min_support=2))
    assert set(r.kind for r in s.rules) <= {"accuses", "vouches"}


# --- adapter two: interaction --------------------------------------------


def _walked_model():
    """A body at (1,1) that moves up when told to, over enough steps to settle."""
    model = wm.wm_new()
    boards = [
        [".....", ".@...", "....."],
        ["..@..", ".....", "....."],
    ]
    before = [".....", ".@...", "....."]
    after = [".@...", ".....", "....."]
    for _ in range(8):
        wm.wm_observe(model, before, "UP", after)
        wm.wm_observe(model, after, "DOWN", before)
    assert boards  # the walk above is the same shape
    return model


def test_the_world_model_produces_a_skill_of_the_same_type():
    s = sk.from_world_model(wm.wm_summary(_walked_model()))
    assert isinstance(s, sk.Skill)
    assert s.domain == "grid world"


def test_learned_physics_renders_as_sentences_a_person_can_read():
    s = sk.from_world_model(wm.wm_summary(_walked_model()))
    text = " ".join(s.sentences())
    assert "the thing I control" in text
    assert "moves it by" in text


def test_physics_skills_and_text_skills_are_the_same_class():
    """The whole point: one artefact type across two unrelated domains."""
    physics = sk.from_world_model(wm.wm_summary(_walked_model()))
    examples = [("spam", "win a free prize now")] * 6 + [
        ("ham", "see you at home tonight")
    ] * 6
    text = sk.from_text_rules(sr.learn(examples, min_support=2))

    assert type(physics) is type(text) is sk.Skill
    for one in (physics, text):
        assert sk.Skill.from_json(one.to_json()).as_dict() == one.as_dict()
        import ast

        ast.parse(one.render())


def test_an_empty_theory_yields_an_empty_but_valid_skill():
    s = sk.from_world_model(wm.wm_summary(wm.wm_new()))
    assert len(s) == 0
    import ast

    ast.parse(s.render())
