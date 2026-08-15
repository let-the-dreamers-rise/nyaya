"""Pure-Python helpers for injection into the analyzer's python sandbox.

The sandbox is a subprocess started with ``-I -S`` whose importer allows only a
short stdlib whitelist -- numpy is not on it -- and host-side globals injection
is impossible. The only channel is the code string itself, so helpers must be
self-contained source that is prepended to the model's code, in the manner the
vendored sandbox already uses for its segmentation module.

Everything here therefore obeys three rules: no imports, no builtins outside
the sandbox's restricted set, and no state between calls. Each function takes
plain lists and strings and returns plain data.

These are the three things our own agent does that the harness's model does
not. Its authors' forensics name two of them directly: hypothesis lock-in on a
HUD bar (one action repeated 71 times against a timer strip) and a prompt that
tells the model to "write an explicit search algorithm such as BFS" every game
rather than handing it one.
"""
from __future__ import annotations


def grid_from_ascii(ascii_text):
    """Split a newline-delimited board into a list of rows of characters."""
    return [list(line) for line in str(ascii_text).splitlines() if line]


def hud_cells(before_ascii, after_ascii, margin=4):
    """Border cells that changed while the interior of the board did not.

    A timer or remaining-steps bar sits flush against an edge and shifts on
    almost every step regardless of what the move did. It also looks exactly
    like what a click ranking prefers -- many small blocks in an uncommon
    colour -- so an agent can spend a whole budget clicking through a clock one
    segment at a time.

    The discriminating test is not position but independence: a strip that
    moves on a step when nothing in the interior moved is scenery. Returns
    ``[]`` when the interior did change, because such a step says nothing.
    """
    before = grid_from_ascii(before_ascii)
    after = grid_from_ascii(after_ascii)
    if not before or not after or len(before) != len(after):
        return []
    height = len(before)
    width = min(len(before[0]), len(after[0]))

    changed = []
    interior_moved = False
    for r in range(height):
        for c in range(width):
            if before[r][c] == after[r][c]:
                continue
            edge = (
                r < margin
                or c < margin
                or r >= height - margin
                or c >= width - margin
            )
            if edge:
                changed.append((r, c))
            else:
                interior_moved = True
    return [] if interior_moved else changed


def moved_objects(before_ascii, after_ascii, background=None, limit=8):
    """Every same-shaped run that shifted between two boards, shortest first.

    Each entry is ``{'char', 'from', 'to', 'delta', 'size'}``. Matching is by
    cell pattern rather than position, so a body keeps its identity as it moves.

    Returning the whole field rather than one guess is the point. Which mover
    is the body cannot be decided from a single step -- a timer, a scrolling
    background and an animation all shift too, sometimes by less. It can be
    decided across several steps, by seeing which one answers opposite controls
    in opposite directions, and that needs all the candidates.
    """
    before = grid_from_ascii(before_ascii)
    after = grid_from_ascii(after_ascii)
    if not before or not after:
        return []
    skip = set(background or _background_chars(before))

    groups_before = _runs_by_shape(before, skip)
    groups_after = _runs_by_shape(after, skip)

    found = []
    for shape, origins in groups_before.items():
        targets = groups_after.get(shape)
        if not targets or len(targets) != len(origins):
            continue
        best = None
        for origin in origins:
            for target in targets:
                dr = target[0] - origin[0]
                dc = target[1] - origin[1]
                if dr == 0 and dc == 0:
                    continue
                distance = abs(dr) + abs(dc)
                if best is None or distance < best[0]:
                    best = (
                        distance,
                        {
                            "char": shape[0],
                            "from": origin,
                            "to": target,
                            "delta": (dr, dc),
                            "size": len(shape[1]),
                        },
                    )
        if best is not None:
            found.append(best)
    found.sort(key=lambda item: item[0])
    return [item[1] for item in found[:limit]]


def moved_object(before_ascii, after_ascii, background=None):
    """The shortest displacement between two boards, or ``None``.

    Kept for the single-step case. It cannot tell a body from scenery -- see
    moved_objects, and prefer that wherever several steps are available.
    """
    found = moved_objects(before_ascii, after_ascii, background, limit=1)
    return found[0] if found else None


def route(start, goal, deltas, passable, max_nodes=20000):
    """Shortest sequence of deltas from ``start`` to ``goal``.

    ``deltas`` maps an action name to a ``(dr, dc)`` step; ``passable`` is
    called with ``(row, col)``. Returns the list of action names, ``[]`` when
    already there, or ``None`` when unreachable within the node budget.

    Breadth-first, so the first route found is the shortest -- which is what
    the scoring wants, since a level is scored on ``(baseline/actions)**2``.
    """
    if tuple(start) == tuple(goal):
        return []
    if not deltas:
        return None

    ordered = sorted(deltas.items())
    frontier = [(tuple(start), [])]
    seen = {tuple(start)}
    expanded = 0
    head = 0
    while head < len(frontier) and expanded < max_nodes:
        position, path = frontier[head]
        head += 1
        expanded += 1
        for name, step in ordered:
            nxt = (position[0] + step[0], position[1] + step[1])
            if nxt in seen or not passable(nxt):
                continue
            extended = path + [name]
            if nxt == tuple(goal):
                return extended
            seen.add(nxt)
            frontier.append((nxt, extended))
    return None


def _background_chars(grid, threshold=0.25):
    """Characters covering at least ``threshold`` of the board."""
    counts = {}
    total = 0
    for row in grid:
        for ch in row:
            counts[ch] = counts.get(ch, 0) + 1
            total += 1
    if not total:
        return set()
    return {ch for ch, n in counts.items() if n >= threshold * total}


def _runs_by_shape(grid, skip):
    """Group four-connected same-character runs by (char, normalised cells)."""
    height = len(grid)
    seen = set()
    groups = {}
    for r in range(height):
        for c in range(len(grid[r])):
            if (r, c) in seen or grid[r][c] in skip:
                continue
            ch = grid[r][c]
            cells = []
            stack = [(r, c)]
            seen.add((r, c))
            while stack:
                cr, cc = stack.pop()
                cells.append((cr, cc))
                for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nr, nc = cr + dr, cc + dc
                    if (
                        0 <= nr < height
                        and 0 <= nc < len(grid[nr])
                        and (nr, nc) not in seen
                        and grid[nr][nc] == ch
                    ):
                        seen.add((nr, nc))
                        stack.append((nr, nc))
            top = min(x for x, _ in cells)
            left = min(y for _, y in cells)
            shape = (ch, tuple(sorted((x - top, y - left) for x, y in cells)))
            groups.setdefault(shape, []).append((top, left))
    return groups
