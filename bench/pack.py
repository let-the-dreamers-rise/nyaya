"""Pack raw episode logs into the compact corpus format the benchmark uses.

Raw logs store a full 64x64 board per step, which is ~185 MB for 50 episodes
and cannot live in a repository. Almost every step changes a handful of cells,
so the corpus ships as one initial frame per episode plus a per-step list of
changed cells. Reconstruction is exact -- this is a delta encoding, not a
lossy summary -- and the packed form is small enough to distribute, which is
the whole point: a benchmark nobody can download is not a benchmark.

    python -m bench.pack <raw_dir> -o bench/corpus

Input is one JSON-lines file per episode with, per line: `board_ascii`, and
optionally `action_name`, `action_display`, `level`, `level_completed`.
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
from pathlib import Path

# Engine action ids as they appear in raw logs, mapped to the names a policy
# speaks. Clicks carry coordinates in the display string.
ENGINE = {
    "ACTION1": "UP",
    "ACTION2": "DOWN",
    "ACTION3": "LEFT",
    "ACTION4": "RIGHT",
    "ACTION5": "SPACE",
    "ACTION6": "MOUSE",
}
_CLICK = re.compile(r"row=(\d+),\s*col=(\d+)")


def read_action(event: dict):
    """Normalise one event's action to a name, or ('MOUSE', row, col)."""
    name = str(event.get("action_name") or "").strip().upper()
    action = ENGINE.get(name, name)
    if action == "MOUSE":
        hit = _CLICK.search(str(event.get("action_display") or ""))
        if hit:
            return ["MOUSE", int(hit.group(1)), int(hit.group(2))]
    return action or None


def diff(before: list, after: list) -> list:
    """Changed cells as [row, col, char]; exact and order-independent."""
    out = []
    for r in range(min(len(before), len(after))):
        row_b, row_a = before[r], after[r]
        if row_b == row_a:
            continue
        for c in range(min(len(row_b), len(row_a))):
            if row_b[c] != row_a[c]:
                out.append([r, c, row_a[c]])
    return out


def apply_diff(board: list, cells: list) -> list:
    grid = [list(row) for row in board]
    for r, c, ch in cells:
        if 0 <= r < len(grid) and 0 <= c < len(grid[r]):
            grid[r][c] = ch
    return ["".join(row) for row in grid]


def pack_episode(path: Path) -> dict | None:
    frames, meta = [], []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            board = event.get("board_ascii")
            if not board:
                continue
            frames.append(board.splitlines())
            meta.append(event)
    if len(frames) < 2:
        return None

    steps = []
    for i in range(1, len(frames)):
        event = meta[i]
        steps.append(
            {
                "a": read_action(event),
                "d": diff(frames[i - 1], frames[i]),
                "lvl": int(event.get("level") or 0),
                "up": bool(event.get("level_completed")),
            }
        )
    return {
        "episode": path.name.split("_")[0],
        "shape": [len(frames[0]), len(frames[0][0]) if frames[0] else 0],
        "initial": frames[0],
        "steps": steps,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw_dir", help="directory of *_events.jsonl files")
    parser.add_argument("-o", "--out", default="bench/corpus")
    parser.add_argument("--limit", type=int, default=0, help="first N episodes only")
    args = parser.parse_args(argv)

    raw = sorted(Path(args.raw_dir).rglob("*_events.jsonl"))
    if args.limit:
        raw = raw[: args.limit]
    if not raw:
        print(f"no *_events.jsonl under {args.raw_dir}")
        return 2

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    total_in = total_out = kept = steps = 0
    for path in raw:
        packed = pack_episode(path)
        if packed is None:
            continue
        target = out_dir / f"{packed['episode']}.json.gz"
        blob = json.dumps(packed, separators=(",", ":")).encode("utf-8")
        with gzip.open(target, "wb", compresslevel=9) as handle:
            handle.write(blob)
        total_in += path.stat().st_size
        total_out += target.stat().st_size
        steps += len(packed["steps"])
        kept += 1

    print(
        f"packed {kept} episodes, {steps} transitions: "
        f"{total_in / 1e6:.1f} MB -> {total_out / 1e6:.2f} MB "
        f"({total_in / max(1, total_out):.0f}x smaller)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
