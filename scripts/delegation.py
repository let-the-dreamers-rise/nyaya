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
from bench.replay import f1_of, score_step  # noqa: E402

DEFAULT_METHODS = ("copy-forward", "last-effect", "nyaya-templates", "dsl-synthesis-rel")


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
            "noops": noops, "perfect_f1": perfect_f1}


def run(corpus_path, names):
    episodes = corpus_mod.load(corpus_path)
    out = {}
    for name in names:
        total = {"n": 0, "commits": 0, "exact": 0, "delegable": 0, "noops": 0, "perfect_f1": 0}
        for chain in episodes.values():
            counts = measure(methods.build(name), chain)
            for key in total:
                total[key] += counts[key]
        out[name] = total
    return out


def table(results, title):
    lines = [title, "",
             f"{'method':<20}{'actions':>9}{'commits':>9}{'commit ok':>11}{'delegable':>11}{'no-ops':>8}{'cells ok':>10}",
             "-" * 78]
    for name, t in results.items():
        n = t["n"] or 1
        commit_ok = t["delegable"] / t["commits"] if t["commits"] else 0.0
        lines.append(
            f"{name:<20}{t['n']:>9}{t['commits'] / n:>9.1%}{commit_ok:>11.1%}"
            f"{t['delegable'] / n:>11.1%}{t['noops'] / n:>8.1%}{t['perfect_f1'] / n:>10.1%}"
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
    args = parser.parse_args(argv)
    path = Path(args.corpus) if args.corpus else corpus_mod.CORPUS
    results = run(path, args.methods)
    print(table(results, f"corpus: {path.name}"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
