"""The nyaya command line: learn, evaluate, and use readable skills.

This is the MVP surface. The demos prove the mechanism on our data; the CLI
lets a stranger run it on theirs in three commands:

    nyaya learn their_data.tsv -o skill.py
    nyaya eval skill.py their_data.tsv
    nyaya explain skill.py "some message to judge"

Data format: TSV, one example per line, label<TAB>text, labels 'spam'/'ham'
(read as positive/negative -- the engine does not care what the classes mean).
The emitted skill is a page of Python the user owns and can edit; `explain`
shows exactly which beliefs fired, which is the whole point.
"""
from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path

from . import sms_rules as sr


def _load_skill_file(path: Path) -> dict:
    namespace: dict = {}
    source = path.read_text(encoding="utf-8")
    exec(compile(source, str(path), "exec"), namespace)  # noqa: S102 - user's own file
    if "RULES" not in namespace:
        raise ValueError(
            "{0} has no RULES list, so it is not a nyaya skill".format(path)
        )
    return sr.load_skill(namespace)


def _require_examples(rows, path):
    """Refuse to pretend an unreadable file was a small one."""
    if not rows:
        raise ValueError(
            "{0} has no usable rows -- each line must be 'spam' or 'ham', a tab, "
            "then the text".format(path)
        )
    if len(rows) < 8:
        raise ValueError(
            "{0} rows is too few to hold any out; give at least 8".format(len(rows))
        )
    labels = set(label for label, _ in rows)
    unknown = labels - {"spam", "ham"}
    if unknown:
        raise ValueError(
            "unexpected label(s) {0} -- nyaya expects 'spam' or 'ham'".format(
                ", ".join(sorted(repr(u) for u in unknown))[:80]
            )
        )
    if len(labels) < 2:
        raise ValueError(
            "every row is labelled {0!r}; learning needs both classes".format(
                labels.pop()
            )
        )
    return rows


def _pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def _print_eval(stats: dict, n: int, label: str) -> None:
    print(
        f"{label}: precision {_pct(stats['precision'])}  "
        f"recall {_pct(stats['recall'])}  F1 {stats['f1']:.3f}  "
        f"accuracy {_pct(stats['accuracy'])}  (n={n})"
    )
    print(
        f"  true-positive {stats['tp']}  false-positive {stats['fp']}  "
        f"false-negative {stats['fn']}  true-negative {stats['tn']}"
    )


def cmd_learn(args: argparse.Namespace) -> int:
    examples = _require_examples(sr.read_tsv(args.data), args.data)

    # Honest numbers first: hold out a fifth, report, then train the final
    # skill on everything. The held-out line is what the user may quote; the
    # skill they ship gets all the evidence.
    shuffled = list(examples)
    random.Random(args.seed).shuffle(shuffled)
    cut = int(0.8 * len(shuffled))
    started = time.perf_counter()
    probe = sr.learn(
        shuffled[:cut], min_support=args.min_support, min_precision=args.min_precision
    )
    elapsed = time.perf_counter() - started
    _print_eval(sr.evaluate(probe, shuffled[cut:]), len(shuffled) - cut, "held-out")

    skill = sr.learn(
        examples, min_support=args.min_support, min_precision=args.min_precision
    )
    accusing = sum(1 for r in skill["rules"] if r[3] > 0)
    vouching = len(skill["rules"]) - accusing
    print(
        f"learned {len(skill['rules'])} rules ({accusing} accusing, {vouching} "
        f"vouching) from {len(examples)} examples in {elapsed:.2f}s on CPU"
    )

    provenance = (
        f"\nLearned {time.strftime('%Y-%m-%d')} from {len(examples)} examples in "
        f"{Path(args.data).name} by `nyaya learn`. Held-out check above threshold "
        "was printed at learn time; re-run `nyaya eval` any time."
    )
    out = Path(args.out)
    out.write_text(sr.render_skill(skill, provenance), encoding="utf-8")
    print(f"skill written to {out} -- open it; it is a page of Python you own")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    skill = _load_skill_file(Path(args.skill))
    examples = sr.read_tsv(args.data)
    if not examples:
        print(f"no usable examples in {args.data}")
        return 2
    _print_eval(sr.evaluate(skill, examples), len(examples), Path(args.data).name)
    return 0


def cmd_classify(args: argparse.Namespace) -> int:
    skill = _load_skill_file(Path(args.skill))
    texts = args.text or [line.rstrip("\n") for line in sys.stdin]
    flagged = 0
    for text in texts:
        if not text.strip():
            continue
        verdict = sr.classify(skill, text)
        flagged += verdict
        print(f"{'FLAG' if verdict else 'ok  '}  {text}")
    print(f"-- {flagged} flagged")
    return 0


def cmd_explain(args: argparse.Namespace) -> int:
    skill = _load_skill_file(Path(args.skill))
    text = " ".join(args.text)
    total, fired = sr.score(skill, text)
    verdict = total >= skill["threshold"]
    print(f"verdict: {'FLAG' if verdict else 'ok'} (score {total}, threshold {skill['threshold']})")
    if not fired:
        print("  no rules fired")
    for desc, weight in fired:
        side = "accuses" if weight > 0 else "vouches"
        print(f"  {weight:+d}  {desc}  ({side})")
    print(
        "every line above is a belief in the skill file; delete the line and "
        "the verdict changes. That is what owning a skill means."
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nyaya",
        description="Learn, evaluate and use readable classification skills.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("learn", help="induce a skill from a labelled TSV")
    p.add_argument("data", help="TSV file: label<TAB>text, labels spam/ham")
    p.add_argument("-o", "--out", default="skill.py", help="where to write the skill")
    p.add_argument("--min-support", type=int, default=4)
    p.add_argument("--min-precision", type=float, default=0.85)
    p.add_argument("--seed", type=int, default=7)
    p.set_defaults(func=cmd_learn)

    p = sub.add_parser("eval", help="measure a skill against a labelled TSV")
    p.description = "Score an existing skill on labelled data it may never have seen."
    p.add_argument("skill")
    p.add_argument("data")
    p.set_defaults(func=cmd_eval)

    p = sub.add_parser("classify", help="classify lines of text (args or stdin)")
    p.add_argument("skill")
    p.add_argument("text", nargs="*")
    p.set_defaults(func=cmd_classify)

    p = sub.add_parser("explain", help="show exactly which beliefs fired and why")
    p.add_argument("skill")
    p.add_argument("text", nargs="+")
    p.set_defaults(func=cmd_explain)

    return parser


def _complain(problem, remedy):
    """One line for what went wrong, one for what to do about it.

    A stack trace tells the reader where our code is on our disk. It does not
    tell them they typed a filename wrong, which is what actually happened
    almost every time.
    """
    print("nyaya: {0}".format(problem), file=sys.stderr)
    print("       {0}".format(remedy), file=sys.stderr)
    return 1


def main(argv=None) -> int:
    parser = build_parser()
    given = sys.argv[1:] if argv is None else list(argv)
    if not given:
        # Someone typing the bare name is asking what this does, not making a
        # mistake. Answer the question instead of scolding them.
        parser.print_help()
        return 0
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FileNotFoundError as missing:
        name = getattr(missing, "filename", None) or "that file"
        if str(name).endswith(".py"):
            return _complain(
                "no skill file at {0}".format(name),
                "make one first:  python -m nyaya learn data/sms.tsv -o {0}".format(name),
            )
        return _complain(
            "no data file at {0}".format(name),
            "expected a TSV of 'label<TAB>text' rows; the bundled one is data/sms.tsv",
        )
    except IsADirectoryError as wrong:
        return _complain(
            "{0} is a directory, not a file".format(getattr(wrong, "filename", "that path")),
            "point at the .tsv itself, e.g. data/sms.tsv",
        )
    except PermissionError as denied:
        return _complain(
            "not allowed to open {0}".format(getattr(denied, "filename", "that file")),
            "check the file's permissions, or copy it somewhere you own",
        )
    except UnicodeDecodeError:
        return _complain(
            "that file is not UTF-8 text",
            "nyaya reads plain TSV; re-save it as UTF-8 and try again",
        )
    except ValueError as bad:
        return _complain(str(bad), "see  python -m nyaya <command> --help")
    except KeyboardInterrupt:
        print(file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
