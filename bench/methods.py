"""The registry every method enters, and the baselines it must beat.

A method is anything with `observe(before, action, after)` and
`predict(board, action) -> board`. That interface is deliberately tiny so a
third party can wrap an existing system in a few lines rather than
reimplementing it -- and so nobody has to trust our reimplementation of their
work, which is the failure mode that makes most published comparisons
arguable.

Methods that call a model may report cost by incrementing `self.tokens`; it
is reported alongside quality because cost per hypothesis revision is the
axis the literature does not publish and the one where approaches differ by
orders of magnitude.
"""
from __future__ import annotations

from nyaya import world_model as wm

REGISTRY: dict = {}


def register(name: str):
    def wrap(factory):
        REGISTRY[name] = factory
        return factory

    return wrap


@register("copy-forward")
class CopyForward:
    """The null theory: nothing ever changes.

    Scores zero changed-cell F1 by construction, which is the point -- it
    isolates dynamics from scenery. A method that cannot beat this has
    learned nothing, and on a board that is mostly background its
    exact-frame rate can still look respectable, which is why exact-frame
    alone is a misleading headline.
    """

    tokens = 0

    def observe(self, before, action, after):
        return None

    def predict(self, board, action):
        return list(board)


@register("nyaya-templates")
class NyayaTemplates:
    """The factored symbolic theory: body, deltas, blocking, clicks, decay.

    Learns by voting within a fixed hypothesis class, on CPU, with no model
    in the loop -- so its token cost is zero by construction.
    """

    def __init__(self):
        self.model = wm.wm_new()
        self.tokens = 0

    def observe(self, before, action, after):
        wm.wm_observe(self.model, before, action, after)

    def predict(self, board, action):
        return wm.wm_predict(self.model, board, action)

    def summary(self):
        return wm.wm_summary(self.model)


@register("memorise")
class Memorise:
    """Has this exact board been seen with this exact action before?

    Not a serious learner -- a diagnostic, and the most important one in the
    registry. If a lookup table scores well, the corpus is repetitive and every
    other number here is measuring recall rather than generalisation. A
    benchmark without this baseline cannot tell you which of the two it is.

    Keyed on a hash so memory stays flat regardless of grid size.
    """

    def __init__(self):
        self.seen: dict = {}
        self.tokens = 0

    @staticmethod
    def _key(board, action):
        return (hash(tuple(board)), repr(action))

    def observe(self, before, action, after):
        self.seen[self._key(before, action)] = list(after)

    def predict(self, board, action):
        return self.seen.get(self._key(board, action), list(board))


@register("last-effect")
class LastEffect:
    """Replay the cell changes this action caused the last time it was taken.

    The cheapest theory that is not the null: an action does whatever it did
    before, in the same places. It separates 'the environment responds
    consistently' from 'the response depends on where things are', which is the
    first real question about any dynamics.
    """

    def __init__(self):
        self.effect: dict = {}
        self.tokens = 0

    def observe(self, before, action, after):
        changes = []
        for r in range(min(len(before), len(after))):
            row_b, row_a = before[r], after[r]
            if row_b == row_a:
                continue
            for c in range(min(len(row_b), len(row_a))):
                if row_b[c] != row_a[c]:
                    changes.append((r, c, row_a[c]))
        self.effect[repr(action)] = changes

    def predict(self, board, action):
        changes = self.effect.get(repr(action))
        if not changes:
            return list(board)
        grid = [list(row) for row in board]
        for r, c, ch in changes:
            if 0 <= r < len(grid) and 0 <= c < len(grid[r]):
                grid[r][c] = ch
        return ["".join(row) for row in grid]


def build(name: str):
    if name not in REGISTRY:
        raise KeyError(f"unknown method {name!r}; known: {sorted(REGISTRY)}")
    return REGISTRY[name]()
