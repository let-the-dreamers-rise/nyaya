"""Tests for the scam-skill learner -- the bridge artefact's honesty."""
from __future__ import annotations

from pathlib import Path

import pytest

from nyaya import sms_rules as sr

DATA = Path(__file__).resolve().parents[1] / "data"

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


def tiny_corpus():
    return [("spam", t) for t in SCAMS] * 3 + [("ham", t) for t in NORMALS] * 3


def tiny_learn(examples=None):
    # Laplace smoothing makes the default precision bar unreachable on a
    # thirty-message corpus -- correctly so. Tiny tests loosen the bar; the
    # real-corpus test below keeps the strict defaults the pitch quotes.
    return sr.learn(examples or tiny_corpus(), min_support=2, min_precision=0.8)


def test_learner_finds_the_obvious_signals():
    skill = tiny_learn()
    descs = [r[0] for r in skill["rules"] if r[3] > 0]
    assert any("prize or lottery" in d for d in descs)
    assert any("web link" in d for d in descs)


def test_learner_convicts_no_hand_tuned_rule_without_evidence():
    # A ham-only corpus must produce no accusing rules at all: the named
    # signals are candidates, and candidates need evidence.
    skill = sr.learn([("ham", t) for t in NORMALS] * 4, min_support=2, min_precision=0.8)
    assert all(r[3] < 0 for r in skill["rules"])


def test_classification_separates_the_tiny_corpus():
    skill = tiny_learn()
    stats = sr.evaluate(skill, tiny_corpus())
    assert stats["f1"] == 1.0


def test_score_reports_which_rules_fired():
    skill = tiny_learn()
    total, fired = sr.score(skill, SCAMS[0])
    assert total >= skill["threshold"]
    assert fired and all(isinstance(d, str) for d, _ in fired)


def test_rendered_skill_is_valid_python_and_round_trips():
    skill = tiny_learn()
    source = sr.render_skill(skill, "test provenance")
    namespace: dict = {}
    exec(compile(source, "<skill>", "exec"), namespace)
    loaded = sr.load_skill(namespace)
    for _, text in tiny_corpus():
        assert sr.classify(loaded, text) == sr.classify(skill, text)


def test_editing_the_skill_changes_the_verdict():
    # Ownership means deletion works: remove the rules that fired and the
    # guardian genuinely changes its mind.
    skill = tiny_learn()
    text = SCAMS[1]
    _, fired = sr.score(skill, text)
    fired_descs = {d for d, _ in fired}
    owned = {
        "rules": [r for r in skill["rules"] if r[0] not in fired_descs],
        "threshold": skill["threshold"],
    }
    assert sr.classify(skill, text) and not sr.classify(owned, text)


@pytest.mark.skipif(not (DATA / "sms.tsv").is_file(), reason="corpus not downloaded")
def test_real_corpus_held_out_quality():
    import random

    uci = sr.read_tsv(DATA / "sms.tsv")
    assert len(uci) > 5000
    random.Random(7).shuffle(uci)
    cut = int(0.8 * len(uci))
    skill = sr.learn(uci[:cut])
    stats = sr.evaluate(skill, uci[cut:])
    # The honesty bar the pitch quotes: readable rules, real data, held out.
    assert stats["precision"] >= 0.85, stats
    assert stats["recall"] >= 0.70, stats


@pytest.mark.skipif(not (DATA / "india_seed.tsv").is_file(), reason="seed missing")
def test_adaptation_with_few_local_examples_beats_zero_shot():
    import random

    uci = sr.read_tsv(DATA / "sms.tsv") if (DATA / "sms.tsv").is_file() else tiny_corpus()
    india = sr.read_tsv(DATA / "india_seed.tsv")
    random.Random(7).shuffle(uci)
    train = uci[: int(0.8 * len(uci))]
    zero = sr.evaluate(sr.learn(train), india[1::2])
    adapted = sr.evaluate(sr.learn(train + india[0::2]), india[1::2])
    assert adapted["f1"] >= zero["f1"]
