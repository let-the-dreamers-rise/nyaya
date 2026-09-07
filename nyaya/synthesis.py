"""Programs synthesised from an agent's own mistakes, with no model in the loop.

The template learner in `world_model.py` fits parameters inside a fixed
hypothesis class: which colour is the body, what displacement each control
produces, which colours block. When the true mechanism lies outside that class,
more data cannot help -- and measurement says that is where we are, because a
one-line heuristic (`last-effect` in the benchmark) beats it on the development
corpus.

So this module does not fit parameters. It *searches for programs*.

A program here is a **local update rule**: a conjunction of predicates over a
cell's neighbourhood and the action taken, implying what that cell becomes.

    if self='.' and left='@' and action=RIGHT  ->  '@'

That is a small hypothesis space per rule and an enormous one in combination,
and it can express mechanisms templates structurally cannot: conditional
movement, blocking that depends on what is behind the blocker, spreading,
contact effects, position-independent physics. Crucially it is *position
independent*, which is exactly where `last-effect` fails -- that baseline
replays the same absolute cells forever.

**Nothing here knows what a grid is.** The engine takes observations, actions
and a registered primitive set. Grid knowledge lives entirely in the
primitives, so swapping them points the same search at UI traces, tool-use
logs, or anything else shaped like (state, action, state').

Standard library only. No model is called at any point.
"""

from __future__ import annotations

from itertools import combinations

# --- primitives ------------------------------------------------------------

PRIMITIVE_SETS: dict = {}


def register_primitives(name):
    """A primitive set is the only domain knowledge the searcher ever sees."""

    def wrap(factory):
        PRIMITIVE_SETS[name] = factory
        return factory

    return wrap


@register_primitives("grid")
def grid_primitives():
    """What a cell can notice about itself, its neighbours and the action.

    Deliberately small. A large primitive set makes the search space explode
    long before it makes the theories better, and the point of stage one is to
    find out whether search helps at all.
    """

    def at(grid, r, c):
        if 0 <= r < len(grid) and 0 <= c < len(grid[r]):
            return grid[r][c]
        return None  # off-board is a real, distinguishable observation

    def make(name, fn):
        fn.__name__ = name
        return (name, fn)

    return [
        make("self", lambda g, r, c, a: at(g, r, c)),
        make("up", lambda g, r, c, a: at(g, r - 1, c)),
        make("down", lambda g, r, c, a: at(g, r + 1, c)),
        make("left", lambda g, r, c, a: at(g, r, c - 1)),
        make("right", lambda g, r, c, a: at(g, r, c + 1)),
        make("up2", lambda g, r, c, a: at(g, r - 2, c)),
        make("down2", lambda g, r, c, a: at(g, r + 2, c)),
        make("left2", lambda g, r, c, a: at(g, r, c - 2)),
        make("right2", lambda g, r, c, a: at(g, r, c + 2)),
        make("action", lambda g, r, c, a: a),
        # Diagonals were tried and measurably hurt: with a greedy refiner they
        # gave the search more ways to over-specialise, and held-out F1 on the
        # probe episode fell from 0.153 to 0.121. Kept out on evidence.
        # make("upleft", ...), make("upright", ...), ...
    ]


def features(primitives, grid, r, c, action):
    """The observation vector for one cell: (primitive name, value) pairs."""
    return tuple((name, fn(grid, r, c, action)) for name, fn in primitives)


# --- programs --------------------------------------------------------------


class Rule:
    """One synthesised program: a conjunction of tests, implying an outcome.

    `support` is how many logged transitions it explained and `precision` how
    often it was right when it fired -- carried on the rule itself, because a
    program without its evidence is an assertion.
    """

    __slots__ = ("conditions", "outcome", "support", "precision")

    def __init__(self, conditions, outcome, support=0, precision=0.0):
        self.conditions = tuple(sorted(conditions))
        self.outcome = outcome
        self.support = support
        self.precision = precision

    def __repr__(self):
        return "Rule({0} -> {1!r})".format(self.sentence(), self.outcome)

    def __eq__(self, other):
        return (
            isinstance(other, Rule)
            and self.conditions == other.conditions
            and self.outcome == other.outcome
        )

    def __hash__(self):
        return hash((self.conditions, self.outcome))

    def matches(self, observed):
        """observed is a dict of primitive name -> value for one cell."""
        for name, value in self.conditions:
            if observed.get(name) != value:
                return False
        return True

    def sentence(self):
        """The rule as something a person can read and disagree with."""
        parts = [
            "{0} is {1}".format(name, "off-board" if value is None else repr(value))
            for name, value in self.conditions
        ]
        return "when " + " and ".join(parts) + ", it becomes {0!r}".format(self.outcome)

    def as_evidence(self):
        return {"fired on": self.support, "right": round(self.precision, 3)}


# --- the search ------------------------------------------------------------


def _score(examples, conditions, outcome):
    """(support, precision) of one candidate conjunction over the examples."""
    fired = right = 0
    for observed, actual in examples:
        ok = True
        for name, value in conditions:
            if observed.get(name) != value:
                ok = False
                break
        if ok:
            fired += 1
            if actual == outcome:
                right += 1
    return fired, (right / fired if fired else 0.0)


def synthesise(
    examples,
    max_conditions=3,
    min_support=4,
    min_precision=0.90,
    max_rules=200,
):
    """Search for local update rules that explain the observed changes.

    Separate-and-conquer with counterexample-guided refinement: take the
    outcome we have most evidence for, find the shortest conjunction that
    predicts it precisely, and when a candidate is impure, add the condition
    that best separates the cases it currently gets wrong -- the mispredictions
    are the specification for the next conjunct. Explained examples are then
    removed and the search repeats on what is left.

    `examples` is a list of (observed, outcome) where observed maps primitive
    name to value. The searcher never learns what any primitive means.
    """
    remaining = list(examples)
    rules = []

    while remaining and len(rules) < max_rules:
        # Candidate outcomes, most evidence first. A rule that predicts no
        # change is a rule that does nothing, so those are never searched for.
        outcomes = {}
        for observed, actual in remaining:
            if actual != observed.get("self"):
                outcomes[actual] = outcomes.get(actual, 0) + 1
        if not outcomes:
            break

        # Try every outcome we have real evidence for, not just the top few.
        # An earlier version stopped at six and broke out of the whole search
        # the moment those six failed, so one hard mechanism ended the run and
        # recall collapsed to 8% while precision stayed at 86%.
        best = None
        for outcome in sorted(outcomes, key=lambda o: -outcomes[o]):
            if outcomes[outcome] < min_support:
                break
            found = _grow_rule(
                remaining, outcome, max_conditions, min_support, min_precision
            )
            if found is None:
                continue
            if best is None or _rank(found) > _rank(best):
                best = found

        if best is None:
            break

        rules.append(best)
        before = len(remaining)
        remaining = [
            (observed, actual)
            for observed, actual in remaining
            if not (best.matches(observed) and actual == best.outcome)
        ]
        if len(remaining) == before:  # made no progress; stop rather than spin
            break

    return rules


def _rank(rule):
    return (rule.precision, rule.support, -len(rule.conditions))


def _grow_rule(examples, outcome, max_conditions, min_support, min_precision):
    """Grow one conjunction for `outcome`, refining on what it gets wrong."""
    # Only cells that actually *changed* into this outcome are positives. The
    # first version omitted this and cheerfully learned "when self is 'b', it
    # becomes 'b'" with support 4,755 -- a rule that predicts nothing, wins the
    # separate-and-conquer round on sheer support, and starves the search of
    # the budget it needed for real mechanisms.
    positives = [
        obs
        for obs, actual in examples
        if actual == outcome and actual != obs.get("self")
    ]
    if len(positives) < min_support:
        return None

    # Every rule is pinned to what the cell currently is. It keeps prediction
    # cheap (one index lookup per cell instead of a scan over all rules) and it
    # rules out the degenerate hypotheses that ignore the cell entirely.
    selves = {}
    for observed in positives:
        key = observed.get("self")
        selves[key] = selves.get(key, 0) + 1
    pinned = max(sorted(selves, key=repr), key=lambda k: selves[k])
    if pinned == outcome:
        return None  # a rule that changes nothing is not a rule
    conditions = [("self", pinned)]
    used = {"self"}
    positives = [o for o in positives if o.get("self") == pinned]
    if len(positives) < min_support:
        return None

    for _ in range(max_conditions - 1):
        support, precision = (
            _score(examples, conditions, outcome) if conditions else (0, 0.0)
        )
        if conditions and precision >= min_precision and support >= min_support:
            return Rule(conditions, outcome, support, precision)

        # Which single further test best explains the cases we get wrong?
        tally = {}
        for observed in positives:
            if conditions and not all(
                observed.get(n) == v for n, v in conditions
            ):
                continue
            for name, value in observed.items():
                if name in used:
                    continue
                tally[(name, value)] = tally.get((name, value), 0) + 1
        if not tally:
            return None

        candidates = sorted(tally, key=lambda k: -tally[k])[:8]
        scored = []
        for candidate in candidates:
            trial = conditions + [candidate]
            s, p = _score(examples, trial, outcome)
            if s >= min_support:
                scored.append((p, s, candidate))
        if not scored:
            return None

        scored.sort(reverse=True)
        _, _, chosen = scored[0]
        conditions.append(chosen)
        used.add(chosen[0])

    support, precision = _score(examples, conditions, outcome)
    if support >= min_support and precision >= min_precision:
        return Rule(conditions, outcome, support, precision)
    return None


# --- the learner -----------------------------------------------------------


class SynthesisLearner:
    """Observes transitions, searches for programs, predicts with them.

    Re-synthesis happens on a doubling schedule rather than every step: the
    search is the expensive part and running it 3,000 times to watch it change
    slightly is a waste. It never sees a transition before predicting it.
    """

    def __init__(self, primitive_set="grid", max_conditions=3, min_support=4,
                 min_precision=0.90, negatives_per_positive=3):
        self.primitives = PRIMITIVE_SETS[primitive_set]()
        self.max_conditions = max_conditions
        self.min_support = min_support
        self.min_precision = min_precision
        self.negatives_per_positive = negatives_per_positive

        self.examples: list = []
        self.rules: list = []
        self.by_self: dict = {}
        self.wildcard: list = []
        self.seen = 0
        self.next_fit = 8
        self.tokens = 0  # no model is called, ever

    # -- learning --

    def _observed(self, grid, r, c, action):
        return dict(features(self.primitives, grid, r, c, action))

    def observe(self, before, action, after):
        changed = []
        for r in range(min(len(before), len(after))):
            row_b, row_a = before[r], after[r]
            if row_b == row_a:
                continue
            for c in range(min(len(row_b), len(row_a))):
                if row_b[c] != row_a[c]:
                    changed.append((r, c))

        for r, c in changed:
            self.examples.append((self._observed(before, r, c, action), after[r][c]))

        # Negatives matter more than positives here, and *where* they are
        # sampled decides whether the search works at all.
        #
        # The first version of this sampled only cells adjacent to a change.
        # Rules then looked precise on that neighbourhood while firing in a
        # thousand places nobody had shown the searcher, and prediction got
        # worse than doing nothing (F1 0.058 against a 0.313 baseline). A rule
        # is applied to the whole board, so it has to be scored against the
        # whole board: a uniform stride across every row, plus the hard cases
        # next to real changes.
        changed_set = set(changed)
        rows = len(before)
        stride = max(1, (rows * max(1, len(before[0]))) // 240)
        flat = 0
        for r in range(rows):
            row_b, row_a = before[r], after[r] if r < len(after) else before[r]
            for c in range(len(row_b)):
                flat += 1
                if flat % stride:
                    continue
                if (r, c) in changed_set or c >= len(row_a) or row_b[c] != row_a[c]:
                    continue
                self.examples.append(
                    (self._observed(before, r, c, action), row_b[c])
                )

        wanted = self.negatives_per_positive * max(1, len(changed))
        taken = 0
        for r, c in changed:
            for dr in (-2, -1, 0, 1, 2):
                for dc in (-2, -1, 0, 1, 2):
                    if taken >= wanted:
                        break
                    rr, cc = r + dr, c + dc
                    if not (0 <= rr < len(before) and 0 <= cc < len(before[rr])):
                        continue
                    if (rr, cc) in changed_set or before[rr][cc] != after[rr][cc]:
                        continue
                    self.examples.append(
                        (self._observed(before, rr, cc, action), before[rr][cc])
                    )
                    taken += 1

        self.seen += 1
        if self.seen >= self.next_fit:
            self._fit()
            self.next_fit = self.seen * 2

    def _fit(self):
        # Bound the window so late episodes stay affordable; recent evidence is
        # also the evidence most likely to still be true.
        window = self.examples[-6000:]
        self.rules = synthesise(
            window,
            max_conditions=self.max_conditions,
            min_support=self.min_support,
            min_precision=self.min_precision,
        )
        self._index()

    def _index(self):
        """Group by the `self` test so prediction touches few rules per cell."""
        self.by_self, self.wildcard = {}, []
        for rule in sorted(self.rules, key=_rank, reverse=True):
            pinned = dict(rule.conditions).get("self", _MISSING)
            if pinned is _MISSING:
                self.wildcard.append(rule)
            else:
                self.by_self.setdefault(pinned, []).append(rule)

    # -- predicting --

    def predict(self, board, action):
        if not self.rules:
            return list(board)

        grid = None
        for r in range(len(board)):
            row = board[r]
            for c in range(len(row)):
                candidates = self.by_self.get(row[c])
                if candidates is None and not self.wildcard:
                    continue
                observed = None
                for rule in (candidates or []) + self.wildcard:
                    if rule.outcome == row[c]:
                        continue  # predicts no change; nothing to apply
                    if observed is None:
                        observed = self._observed(board, r, c, action)
                    if rule.matches(observed):
                        if grid is None:
                            grid = [list(x) for x in board]
                        grid[r][c] = rule.outcome
                        break
        if grid is None:
            return list(board)
        return ["".join(row) for row in grid]

    # -- the artefact --

    def to_skill(self, name="learned physics"):
        """The synthesised theory as the same readable object every other
        learner in this repository returns."""
        from . import skill as sk

        rules = [
            sk.Rule(r.sentence(), 1, "transition", r.as_evidence())
            for r in sorted(self.rules, key=_rank, reverse=True)
        ]
        return sk.Skill(
            name,
            "grid world",
            rules,
            {"transitions observed": self.seen, "examples": len(self.examples)},
        )


class _Missing:
    pass


_MISSING = _Missing()
