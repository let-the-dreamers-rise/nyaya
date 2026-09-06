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


def build(name: str):
    if name not in REGISTRY:
        raise KeyError(f"unknown method {name!r}; known: {sorted(REGISTRY)}")
    return REGISTRY[name]()
