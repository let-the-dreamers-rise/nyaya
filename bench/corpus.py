"""Load the packed corpus and reconstruct transitions exactly.

The corpus ships delta-encoded (see pack.py). This module turns it back into
the only thing a learner sees: a stream of (before, action, after) triples,
with the transitions that teach nothing about dynamics removed.

Which transitions are excluded, and why it matters: a reset or a level change
replaces the board wholesale, so predicting across one measures scene loading
rather than physics. Including them would let a method that has learned
nothing score well by predicting "everything changes", which is exactly the
kind of accidental win a shared protocol exists to prevent.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

from .pack import apply_diff

CORPUS = Path(__file__).parent / "corpus"


def as_action(raw):
    """JSON gives lists; the learners expect a name or a (name, row, col)."""
    if isinstance(raw, list):
        return tuple([raw[0]] + [int(v) for v in raw[1:]])
    return raw


def episodes(path: Path | None = None) -> list:
    directory = Path(path) if path else CORPUS
    return sorted(directory.glob("*.json.gz"))


def transitions(path: Path) -> list:
    """(before, action, after) for one episode, resets and level changes cut."""
    with gzip.open(path, "rb") as handle:
        packed = json.loads(handle.read().decode("utf-8"))

    board = list(packed["initial"])
    level = packed["steps"][0]["lvl"] if packed["steps"] else 0
    out = []
    for step in packed["steps"]:
        before, after = board, apply_diff(board, step["d"])
        board = after
        action = as_action(step["a"])
        crossed = step["up"] or step["lvl"] != level
        level = step["lvl"]
        if not action or action == "RESET" or crossed:
            continue
        if len(before) != len(after):
            continue
        out.append((before, action, after))
    return out


def load(path: Path | None = None) -> dict:
    """Every episode, keyed by name."""
    return {p.name.split(".")[0]: transitions(p) for p in episodes(path)}
