"""How much of an agent's routine work could a $0 world model take today?

The delegation architecture says: a frontier model proposes goals and reads
anomalies; a world model that costs nothing per call handles the steps it
has already learned. Before anyone funds that, the honest first question is
how many steps the free end can take *right now*, on games it has never
seen, scored post hoc against what actually happened.

Per transition, under the causal-replay protocol (predict before observe):

  commits    the model predicted a change, i.e. it claimed to know
  exact      the whole predicted frame matched reality
  delegable  committed and exact: an action the agent could have taken
             without a model call and without being wrong
  no-op      nothing changed and the model said so; free by construction

This is an upper bound on delegation, because it assumes the agent could
tell which commits to trust. It is published because the number is small
and the curve has to start somewhere honest.

    python scripts/delegation.py
    python scripts/delegation.py --corpus bench/corpus-heldout --methods dsl-synthesis-rel
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bench import corpus as corpus_mod  # noqa: E402
from bench import methods  # noqa: E402
from bench import methods_llm  # noqa: E402,F401  registers llm-skill
from bench.replay import f1_of, score_step  # noqa: E402

DEFAULT_METHODS = ("copy-forward", "last-effect", "nyaya-templates", "dsl-synthesis-rel")
CALIBRATED = ("last-effect-stable", "dsl-cal-8", "dsl-cal-32", "dsl-cal-64")
COMPLETE = ("complete-1:last-effect", "complete-2:last-effect",
            "complete-1:nyaya-templates", "complete-2:nyaya-templates",
            "complete-1:dsl-synthesis-rel", "complete-2:dsl-synthesis-rel",
            "complete-3:dsl-synthesis-rel",
            "union:complete-2:last-effect|complete-1:nyaya-templates|complete-1:dsl-synthesis-rel")


class StableEffect:
    """last-effect, but it only commits when an action has done the same
    thing the last `k` times. The cheapest possible calibration."""

    def __init__(self, k=2):
        self.inner = methods.build("last-effect")
        self.history: dict = {}
        self.k = k

    def predict(self, board, action):
        past = self.history.get(repr(action), [])
        if len(past) >= self.k and all(p == past[-1] for p in past[-self.k:]):
            return self.inner.predict(board, action)
        return list(board)

    def observe(self, before, action, after):
        self.inner.observe(before, action, after)
        key = repr(action)
        self.history.setdefault(key, []).append(repr(self.inner.effect.get(key)))


class CalibratedSynthesis:
    """dsl-synthesis-rel, committing only on rules with enough evidence.

    The rules carry support and precision already; this just refuses to act
    on the thin ones. Whether that trades commits for correctness is exactly
    the question.
    """

    def __init__(self, min_support, min_precision=0.98):
        from nyaya.synthesis import SynthesisLearner

        self.learner = SynthesisLearner(primitive_set="grid-relative")
        self.min_support = min_support
        self.min_precision = min_precision

    def predict(self, board, action):
        full = self.learner.rules
        self.learner.rules = [r for r in full
                              if r.support >= self.min_support and r.precision >= self.min_precision]
        self.learner._index()
        try:
            return self.learner.predict(board, action)
        finally:
            self.learner.rules = full
            self.learner._index()

    def observe(self, before, action, after):
        self.learner.observe(before, action, after)


class Complete:
    """Any method, committing only when its current theory explains the
    last `k` times this action was taken, completely.

    The first calibration round showed that per-rule evidence does not
    predict whole-frame correctness, and that whole-effect consistency does.
    This is the general form of that: before committing, replay the action's
    recent history through the method as it stands now and ask whether every
    frame comes back exact. Costs k extra predictions per step.
    """

    def __init__(self, inner, k=2):
        self.inner = inner
        self.k = k
        self.history: dict = {}

    def predict(self, board, action):
        past = self.history.get(repr(action), [])
        if len(past) < self.k:
            return list(board)
        for before, after in past[-self.k:]:
            if self.inner.predict(before, action) != after:
                return list(board)
        return self.inner.predict(board, action)

    def observe(self, before, action, after):
        self.inner.observe(before, action, after)
        self.history.setdefault(repr(action), []).append((before, after))


class Union:
    """Several gated methods; the first that commits, speaks.

    Each completeness-gated learner covers about one percent of actions.
    If they cover different actions, the union covers more at the same
    precision; if they cover the same ones, it does not. Measured, not
    assumed.
    """

    def __init__(self, inners):
        self.inners = list(inners)

    def predict(self, board, action):
        for inner in self.inners:
            out = inner.predict(board, action)
            if out != board:
                return out
        return list(board)

    def observe(self, before, action, after):
        for inner in self.inners:
            inner.observe(before, action, after)


def build(name):
    if name.startswith("union:"):
        return Union(build(part) for part in name[len("union:"):].split("|"))
    if name == "last-effect-stable":
        return StableEffect()
    if name.startswith("dsl-cal-"):
        return CalibratedSynthesis(min_support=int(name.rsplit("-", 1)[1]))
    if name.startswith("complete-"):
        # complete-2:dsl-synthesis-rel
        k, inner = name[len("complete-"):].split(":", 1)
        return Complete(build(inner), k=int(k))
    return methods.build(name)


def measure(method, chain):
    """Delegation counts for one episode, causally."""
    n = commits = exact = delegable = noops = perfect_f1 = 0
    for before, action, after in chain:
        predicted = method.predict(before, action)
        committed = predicted != before
        hit, tp, fp, fn = score_step(predicted, before, after)
        n += 1
        commits += committed
        exact += hit
        delegable += committed and hit
        noops += (not committed) and hit
        perfect_f1 += (tp + fp + fn) > 0 and f1_of(tp, fp, fn) == 1.0
        method.observe(before, action, after)
    return {"n": n, "commits": commits, "exact": exact, "delegable": delegable,
            "noops": noops, "perfect_f1": perfect_f1, "tokens": int(getattr(method, "tokens", 0))}


def run(corpus_path, names, limit=0):
    episodes = corpus_mod.load(corpus_path)
    if limit:
        episodes = dict(sorted(episodes.items())[:limit])
    out = {}
    for name in names:
        total = {"n": 0, "commits": 0, "exact": 0, "delegable": 0, "noops": 0, "perfect_f1": 0, "tokens": 0}
        for chain in episodes.values():
            counts = measure(build(name), chain)
            for key in total:
                total[key] += counts[key]
        out[name] = total
    return out


def table(results, title):
    lines = [title, "",
             f"{'method':<20}{'actions':>9}{'commits':>9}{'commit ok':>11}{'delegable':>11}{'no-ops':>8}{'cells ok':>10}{'tokens':>9}",
             "-" * 87]
    for name, t in results.items():
        n = t["n"] or 1
        commit_ok = t["delegable"] / t["commits"] if t["commits"] else 0.0
        lines.append(
            f"{name:<20}{t['n']:>9}{t['commits'] / n:>9.1%}{commit_ok:>11.1%}"
            f"{t['delegable'] / n:>11.1%}{t['noops'] / n:>8.1%}{t['perfect_f1'] / n:>10.1%}{t.get('tokens', 0):>9}"
        )
    lines.append("")
    lines.append("commits: claimed to know the outcome.  commit ok: of those, whole frame right.")
    lines.append("delegable: actions the agent could have taken free and right.  no-ops: nothing")
    lines.append("changed and the model said so.  cells ok: every changed cell right (F1 = 1).")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--corpus", default=None, help="episode directory (default: bench/corpus)")
    parser.add_argument("--methods", nargs="*", default=list(DEFAULT_METHODS))
    parser.add_argument("--calibrated", action="store_true",
                        help="add the variants that only commit on earned evidence")
    parser.add_argument("--complete", action="store_true",
                        help="add the variants that commit only when the theory explains the action's recent history completely")
    parser.add_argument("--limit", type=int, default=0, help="first N episodes only")
    args = parser.parse_args(argv)
    if args.calibrated:
        args.methods = list(args.methods) + list(CALIBRATED)
    if args.complete:
        args.methods = list(args.methods) + list(COMPLETE)
    path = Path(args.corpus) if args.corpus else corpus_mod.CORPUS
    results = run(path, args.methods, limit=args.limit)
    title = f"corpus: {path.name}" + (f" (first {args.limit} episodes)" if args.limit else "")
    print(table(results, title))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
