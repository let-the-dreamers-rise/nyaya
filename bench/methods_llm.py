"""A language model in the loop, the way EvoSkill does it, on the same corpus.

EvoSkill's loop is propose, generate, evaluate: a model reads failed
trajectories, writes a skill as code, and the skill is kept if it survives
evaluation. This is that loop reduced to the benchmark's interface so it can
sit in the same table as the $0 methods:

- propose: the last few transitions of an action, as the cells that changed
- generate: the model writes `def predict(board, action)`
- evaluate: the program is kept only if it reproduces every example it was
  shown, exactly, in a subprocess with a timeout

The model is any Ollama model (default `granite3.2:8b`, an open 8B model that
runs on a laptop), so the row costs $0 in API fees and is priced instead in
tokens and seconds, which are reported. Every prompt and response is cached
under `bench/llm-cache/` and committed, so the row replays without a model
and anyone can read what the model wrote.

This is the floor for LLM-in-the-loop, not the ceiling: one prompt, no
retries on evaluator feedback, no frontier model. A stronger prompt or model
is welcome in the registry; the protocol does not change.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

from . import methods

CACHE = Path(__file__).parent / "llm-cache"
DEFAULT_MODEL = os.environ.get("NYAYA_LLM_MODEL", "granite3.2:8b")
DEFAULT_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MAX_EXAMPLES = 4
MAX_CELLS = 48
MAX_CALLS_PER_ACTION = 3
VERIFY_TIMEOUT_S = 30

_RUNNER = """
import json, sys
payload = json.load(sys.stdin)
ns = {}
exec(payload["code"], ns)
fn = ns["predict"]
ok = True
for before, action, after in payload["examples"]:
    action = tuple(action) if isinstance(action, list) else action
    out = fn(list(before), action)
    out = ["".join(str(c) for c in row) for row in out]
    if out != after:
        ok = False
        break
print(json.dumps(ok))
"""


class OllamaClient:
    """One blocking completion; returns (text, tokens billed)."""

    def __init__(self, model=DEFAULT_MODEL, host=DEFAULT_HOST, num_predict=700):
        self.model = model
        self.host = host.rstrip("/")
        self.num_predict = num_predict

    def complete(self, prompt):
        body = {"model": self.model, "stream": False, "prompt": prompt,
                "options": {"temperature": 0, "num_predict": self.num_predict}}
        request = urllib.request.Request(
            self.host + "/api/generate", data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=1800) as response:
            data = json.loads(response.read().decode("utf-8"))
        tokens = int(data.get("prompt_eval_count", 0)) + int(data.get("eval_count", 0))
        return data.get("response", ""), tokens


def changed_cells(before, after, limit=MAX_CELLS):
    """(row, col, old, new) for every cell that changed, capped."""
    out = []
    for r in range(min(len(before), len(after))):
        if before[r] == after[r]:
            continue
        for c in range(min(len(before[r]), len(after[r]))):
            if before[r][c] != after[r][c]:
                out.append((r, c, before[r][c], after[r][c]))
                if len(out) >= limit:
                    return out, True
    return out, False


def prompt_for(action, examples):
    """The propose step: the action's recent history as changed cells."""
    height = len(examples[0][0])
    width = len(examples[0][0][0]) if height else 0
    lines = [
        "You are writing the transition rule of an unknown grid game.",
        f"The board is a list of {height} strings of {width} characters, one character per cell.",
        f"The action is {action!r}. When the action is a tuple, the numbers are a row and a column.",
        "Below are recent transitions caused by this action. Only the cells that changed are",
        "listed as (row, col): old->new; every other cell stayed the same.",
        "",
    ]
    for i, (before, after) in enumerate(examples, 1):
        cells, truncated = changed_cells(before, after)
        body = ", ".join(f"({r},{c}): {o}->{n}" for r, c, o, n in cells) or "nothing changed"
        more = " ..." if truncated else ""
        lines.append(f"example {i}: {body}{more}")
    lines += [
        "",
        "Write one Python function `def predict(board, action)` that returns the next board",
        "as a list of strings and reproduces every example above exactly. Prefer a rule that",
        "depends on what is on the board (find things by their character and move or recolour",
        "them) over fixed coordinates, so the rule keeps working when things have moved.",
        "Return only the code, no explanation, no markdown fences.",
    ]
    return "\n".join(lines)


def extract_code(text):
    """Strip markdown fences if the model added them anyway."""
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        inner = parts[1] if len(parts) > 1 else parts[0]
        if inner.startswith("python"):
            inner = inner[len("python"):]
        text = inner.strip()
    return text


def normalise(result, shape):
    """A program may return lists of characters; the protocol wants strings of the right shape."""
    try:
        rows = ["".join(str(c) for c in row) for row in result]
    except TypeError:
        return None
    if len(rows) != shape[0] or any(len(row) != shape[1] for row in rows):
        return None
    return rows


def verify(code, examples, timeout=VERIFY_TIMEOUT_S):
    """The evaluate step, in a subprocess so a runaway program cannot take the run with it."""
    payload = json.dumps({"code": code, "examples": [[b, a, af] for b, a, af in examples]})
    try:
        done = subprocess.run([sys.executable, "-c", _RUNNER], input=payload,
                              capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False
    return done.returncode == 0 and done.stdout.strip() == "true"


def compile_predict(code):
    namespace: dict = {}
    exec(code, namespace)  # noqa: S102 -- verified in a subprocess first
    return namespace["predict"]


@methods.register("llm-skill")
class LlmSkill:
    """Skills written by a model, kept only when they explain the evidence."""

    def __init__(self, client=None, cache_dir=CACHE, max_calls=MAX_CALLS_PER_ACTION):
        self.client = client or OllamaClient()
        self.cache_dir = Path(cache_dir) / getattr(self.client, "model", "fake").replace(":", "-")
        self.max_calls = max_calls
        self.examples: dict = {}
        self.programs: dict = {}
        self.calls: dict = {}
        self.tokens = 0
        self.accepted = 0

    def _complete(self, prompt):
        key = hashlib.sha256((getattr(self.client, "model", "") + "\n" + prompt).encode("utf-8")).hexdigest()
        path = self.cache_dir / f"{key}.json"
        if path.exists():
            hit = json.loads(path.read_text(encoding="utf-8"))
            return hit["response"], int(hit["tokens"])
        text, tokens = self.client.complete(prompt)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"prompt": prompt, "response": text, "tokens": tokens}, indent=1),
                        encoding="utf-8")
        return text, tokens

    def _run(self, key, board, action):
        program = self.programs.get(key)
        if program is None:
            return None
        try:
            return normalise(program(list(board), action), (len(board), len(board[0]) if board else 0))
        except Exception:  # noqa: BLE001 -- a wrong program is a miss, not a crash
            return None

    def predict(self, board, action):
        out = self._run(repr(action), board, action)
        return out if out is not None else list(board)

    def observe(self, before, action, after):
        key = repr(action)
        history = self.examples.setdefault(key, [])
        history.append((before, after))
        explained = self._run(key, before, action) == after
        if explained or len(history) < 2 or self.calls.get(key, 0) >= self.max_calls:
            return
        self.calls[key] = self.calls.get(key, 0) + 1
        recent = history[-MAX_EXAMPLES:]
        text, tokens = self._complete(prompt_for(action, recent))
        self.tokens += tokens
        code = extract_code(text)
        if not code or not verify(code, [(b, action, a) for b, a in recent]):
            self.programs.pop(key, None)
            return
        try:
            self.programs[key] = compile_predict(code)
            self.accepted += 1
        except Exception:  # noqa: BLE001
            self.programs.pop(key, None)

    def summary(self):
        return {"programs": len(self.programs), "accepted": self.accepted,
                "calls": sum(self.calls.values()), "tokens": self.tokens}
