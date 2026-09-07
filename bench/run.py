"""Run the head-to-head and print the table.

    python -m bench.run                      # every registered method
    python -m bench.run --methods nyaya-templates --per-episode

Adding a method is the point: register it in methods.py, run this, and the
comparison is apples to apples because every method sees the same corpus under
the same protocol. Numbers produced any other way are not comparable and
should not be reported as if they were.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import corpus, methods, replay


def _fmt_threshold(value) -> str:
    return str(value) if value is not None else "--"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--methods", nargs="*", default=sorted(methods.REGISTRY))
    parser.add_argument("--corpus", default=None)
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--per-episode", action="store_true")
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="first N episodes only -- a two-second look before the full run",
    )
    parser.add_argument("--json", default=None, help="also write results here")
    args = parser.parse_args(argv)

    data = corpus.load(Path(args.corpus) if args.corpus else None)
    data = {name: chain for name, chain in data.items() if chain}
    if args.limit:
        data = dict(sorted(data.items())[: args.limit])
    if not data:
        print("no corpus found -- run `python -m bench.pack <raw_dir>` first")
        return 2

    total = sum(len(c) for c in data.values())
    print(f"corpus: {len(data)} episodes, {total} transitions")
    print(f"protocol: predict before learning; threshold F1 >= {args.threshold}\n")

    results = {}
    for name in args.methods:
        rows = []
        # Replaying 25 episodes takes long enough that silence reads as a hang.
        # One dot per episode costs nothing and says the machine is working.
        print(f"running {name:<18}", end="", flush=True)
        for episode, chain in sorted(data.items()):
            row = replay.replay(methods.build(name), chain, threshold=args.threshold)
            row["episode"] = episode
            rows.append(row)
            print(".", end="", flush=True)
        print(" done", flush=True)
        results[name] = {"per_episode": rows, "total": replay.aggregate(rows)}

        if args.per_episode:
            print(f"--- {name} ---")
            print(f"{'episode':<10}{'trans':>7}{'exact':>8}{'F1':>8}{'to_thr':>8}")
            for row in rows:
                print(
                    f"{row['episode']:<10}{row['transitions']:>7}"
                    f"{row['exact']:>7.0%}{row['f1']:>8.3f}"
                    f"{_fmt_threshold(row['to_threshold']):>8}"
                )
            print()

    print()
    print(
        f"{'method':<20}{'exact':>8}{'F1':>8}{'95% CI':>16}{'tokens':>9}"
        f"{'ms/step':>9}{'reached':>9}"
    )
    print("-" * 80)
    for name, result in results.items():
        t = result["total"]
        interval = (
            f"{t['f1_lo']:.3f}-{t['f1_hi']:.3f}"
            if t["f1_lo"] is not None
            else "--"
        )
        print(
            f"{name:<20}{t['exact']:>7.0%}{t['f1']:>8.3f}{interval:>16}"
            f"{t['tokens']:>9}{t['ms_per_step']:>9.2f}"
            f"{str(t['reached_threshold']) + '/' + str(t['episodes']):>9}"
        )
    print(
        "\nF1 is over changed cells only -- copy-forward scores 0 there by "
        "construction.\nThe interval is a 95% bootstrap over episodes, so two "
        "methods whose intervals\noverlap have not been shown to differ. "
        "'reached' counts episodes whose\ntrailing F1 crossed the threshold."
    )
    if "memorise" in results:
        print(
            "\nRead `memorise` first: it is a lookup table, so whatever it scores is "
            "the\nshare of this corpus that is repetition rather than generalisation."
        )

    if args.json:
        Path(args.json).write_text(json.dumps(results, indent=1), encoding="utf-8")
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
