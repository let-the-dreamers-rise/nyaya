"""nyaya-money: your money, witnessed on your own phone.

    nyaya-money report            # sentences in the terminal
    nyaya-money serve             # the page, at http://127.0.0.1:8765/
    nyaya-money skill -o mine.py  # the beliefs as an editable file
    nyaya-money export-demo demo.txt

The source defaults to the phone (Termux:API) when `termux-sms-list` is on
the PATH, otherwise to the built-in demo person. Pass a path to an SMS
Backup & Restore .xml, or a .txt of time<TAB>sender<TAB>body, to use your
own export on a laptop.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from . import serve as srv
from . import sources
from .witness import to_skill, witness


def default_source():
    return "termux" if shutil.which("termux-sms-list") else "demo"


def _parser():
    p = argparse.ArgumentParser(prog="nyaya-money", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--home", help="where preferences live (default ~/.nyaya-money)")
    sub = p.add_subparsers(dest="cmd")

    r = sub.add_parser("report", help="print the sentences")
    r.add_argument("source", nargs="?", default=None)
    r.add_argument("--json", action="store_true")

    s = sub.add_parser("serve", help="serve the page on this device only")
    s.add_argument("source", nargs="?", default=None)
    s.add_argument("--port", type=int, default=srv.DEFAULT_PORT)

    k = sub.add_parser("skill", help="write the beliefs as an editable Python file")
    k.add_argument("source", nargs="?", default=None)
    k.add_argument("-o", "--out", required=True)

    e = sub.add_parser("export-demo", help="write the demo person's messages to a file")
    e.add_argument("out")
    return p


def _report(result, as_json, out):
    if as_json:
        out.write(json.dumps(result, indent=2) + "\n")
        return
    if not result["count"]:
        out.write("No bank messages found.\n")
        return
    out.write("{0} transactions, {1}. Nothing left this device.\n\n".format(
        result["count"], result["span"]))
    for kind, title in (("alert", "Look at this"), ("fact", "Counted"), ("belief", "Learned")):
        rows = [s for s in result["sentences"] if s["kind"] == kind]
        if not rows:
            continue
        out.write(title + "\n")
        for s in rows:
            out.write("  - " + s["text"] + "\n")
        out.write("\n")


def main(argv=None, out=None):
    out = out or sys.stdout
    args = _parser().parse_args(argv)
    if not args.cmd:
        _parser().print_help(out)
        return 0
    try:
        if args.cmd == "export-demo":
            sources.write_text(sources.demo_messages(), args.out)
            out.write("wrote {0}\n".format(args.out))
            return 0
        source = args.source or default_source()
        if args.cmd == "serve":
            srv.serve(source, args.port, args.home, announce=lambda m: out.write(m + "\n"))
            return 0
        ledger = srv.Ledger(source, args.home)
        result = ledger.result()
        if args.cmd == "report":
            _report(result, args.json, out)
        elif args.cmd == "skill":
            Path(args.out).write_text(to_skill(result).render(), encoding="utf-8")
            out.write("wrote {0} ({1} beliefs)\n".format(args.out, len(result["sentences"])))
        return 0
    except FileNotFoundError as exc:
        sys.stderr.write("nyaya-money: {0}\n".format(exc))
        return 1
    except ValueError as exc:
        sys.stderr.write("nyaya-money: could not read that: {0}\n".format(exc))
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
