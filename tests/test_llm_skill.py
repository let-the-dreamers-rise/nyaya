"""The model-in-the-loop baseline keeps only programs that explain the evidence."""

from bench import methods
from bench.methods_llm import LlmSkill, extract_code, normalise, prompt_for

RULE = "def predict(board, action):\n    return [row.replace('3', '5') for row in board]\n"
WRONG = "def predict(board, action):\n    return [row.replace('3', '9') for row in board]\n"
BROKEN = "def predict(board, action):\n    return 1 / 0\n"


class Fake:
    model = "fake"

    def __init__(self, replies):
        self.replies = list(replies)
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        return self.replies.pop(0), 100


def transitions():
    a = (["0300", "0000"], ["0500", "0000"])
    b = (["0030", "0000"], ["0050", "0000"])
    return [a, b]


def test_registered():
    assert "llm-skill" in methods.REGISTRY


def test_keeps_a_program_that_explains_the_examples(tmp_path):
    client = Fake(["```python\n" + RULE + "```"])
    skill = LlmSkill(client=client, cache_dir=tmp_path)
    for before, after in transitions():
        assert skill.predict(before, "ACTION1") == before
        skill.observe(before, "ACTION1", after)
    assert skill.predict(["3333", "0000"], "ACTION1") == ["5555", "0000"]
    assert skill.tokens == 100
    assert skill.summary()["accepted"] == 1
    assert "(0,1): 3->5" in client.prompts[0]


def test_drops_a_program_that_fails_verification(tmp_path):
    skill = LlmSkill(client=Fake([WRONG, BROKEN, WRONG]), cache_dir=tmp_path)
    for before, after in transitions():
        skill.observe(before, "ACTION1", after)
    assert skill.predict(["3333", "0000"], "ACTION1") == ["3333", "0000"]
    assert skill.summary()["programs"] == 0


def test_caps_calls_per_action(tmp_path):
    client = Fake([WRONG] * 10)
    skill = LlmSkill(client=client, cache_dir=tmp_path, max_calls=2)
    for _ in range(5):
        for before, after in transitions():
            skill.observe(before, "ACTION1", after)
    assert len(client.prompts) == 2


def test_cache_replays_without_the_model(tmp_path):
    first = LlmSkill(client=Fake([RULE]), cache_dir=tmp_path)
    for before, after in transitions():
        first.observe(before, "ACTION1", after)
    silent = Fake([])
    second = LlmSkill(client=silent, cache_dir=tmp_path)
    for before, after in transitions():
        second.observe(before, "ACTION1", after)
    assert silent.prompts == [] and second.tokens == 100
    assert second.predict(["3333", "0000"], "ACTION1") == ["5555", "0000"]


def test_feedback_round_carries_the_evaluators_verdict(tmp_path):
    client = Fake([WRONG, RULE])
    skill = LlmSkill(client=client, cache_dir=tmp_path, rounds=2)
    for before, after in transitions():
        skill.observe(before, "ACTION1", after)
    assert len(client.prompts) == 2
    assert "Your previous program" in client.prompts[1]
    assert "you said 9, it was 5" in client.prompts[1]
    assert skill.predict(["3333", "0000"], "ACTION1") == ["5555", "0000"]
    assert skill.summary()["accepted"] == 1


def test_feedback_rounds_share_the_call_budget(tmp_path):
    client = Fake([WRONG] * 10)
    skill = LlmSkill(client=client, cache_dir=tmp_path, max_calls=3, rounds=2)
    for _ in range(4):
        for before, after in transitions():
            skill.observe(before, "ACTION1", after)
    assert len(client.prompts) == 3
    assert "llm-skill-feedback" in methods.REGISTRY


def test_extract_and_normalise():
    assert extract_code("```python\nx = 1\n```") == "x = 1"
    assert normalise([["a", "b"], ["c", "d"]], (2, 2)) == ["ab", "cd"]
    assert normalise(["ab"], (2, 2)) is None
    assert normalise(7, (1, 1)) is None


def test_prompt_names_the_action_and_the_shape():
    text = prompt_for(("ACTION6", 3, 4), transitions())
    assert "('ACTION6', 3, 4)" in text and "2 strings of 4 characters" in text
