"""A symbolic world model learned online from transitions.

This is the seed of the EMPA-shaped answer in docs/AGI.md: a factored,
program-like theory of a game's dynamics, learned from the transitions the
agent has already paid for, cheap enough to fold in after every action and to
predict a frame in microseconds. Planning searches inside it, so real actions
are spent only on walking and on splitting hypotheses, never on search.

Written under sandbox law -- no imports, no withheld builtins, plain data --
because its final home is injection next to the executor. Locally the same
source is imported by the offline evaluation harness and measured against
recorded games (experiment E1); nothing here may assume numpy exists.

The model is deliberately factored so each part can be wrong alone:

  body      which cells the controls drive, and each control's displacement
  blocking  which colours refuse the body (learned from failed moves)
  movers    non-body cells that change on their own clock (timers, animation)
  effects   what happens at contact: nothing yet -- the residual E1 exposes

Prediction composes the parts over a copy-forward base. Copy-forward is the
null theory and it is strong: most of a frame is scenery.
"""

WM_OPPOSITE = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}


def wm_new():
    """A fresh theory: nothing believed yet."""
    return {
        "deltas": {},      # action -> (dr, dc) it moves the body
        "delta_votes": {}, # action -> {(dr, dc): count}
        "body_char": None, # colour of the controlled cells
        "body_votes": {},  # char -> count of control-consistent moves
        "blockers": {},    # char -> {"hit": n, "through": n}
        "clicks": {},      # clicked colour -> {outcome: count}
        "auto": {},        # colour -> {(dr, dc): count} action-independent drift
        "shrink": {},      # colour -> {"max": n, "min": n, "other": n}
        "still": {},       # colour -> transitions it sat unchanged through
        "steps": 0,
    }


def _wm_key(action):
    """Split an action into (name, click) -- clicks travel as tuples."""
    if isinstance(action, tuple):
        name = str(action[0])
        click = (int(action[1]), int(action[2])) if len(action) == 3 else None
        return name, click
    return str(action), None


def wm_observe(model, before, action, after):
    """Fold one transition into the theory. Boards are lists of row strings.

    Learning is by voting rather than replacement, so one animation frame
    cannot overturn what twenty clean steps established.
    """
    model["steps"] += 1
    name, click = _wm_key(action)
    if name == "MOUSE" and click is not None:
        _wm_learn_click(model, before, click, after)
    if before == after:
        _wm_learn_block(model, before, name)
        return model

    moves = _wm_movers(before, after)
    # A known move that failed to move the body is a blocked move even when
    # the rest of the board changed -- a ticking timer must not be allowed to
    # hide every wall in the game behind "something changed".
    body = model["body_char"]
    if body is not None and name in model["deltas"]:
        # The body is judged by centroid displacement, not rigid shape: a
        # body that just ate something changes its cell count, vanishes from
        # the rigid-mover list, and would read as a failed move -- charging
        # the background as a wall on exactly the steps that make progress.
        shift = _wm_centroid_shift(before, after, body)
        if shift == (0, 0):
            _wm_learn_block(model, before, name)
        elif shift is not None:
            # The move went through: everything swept is thereby exonerated.
            for ch in _wm_swept(before, body, model["deltas"][name]):
                seen = model["blockers"].setdefault(ch, {"hit": 0, "through": 0})
                seen["through"] += 1
    for char, delta, cells in moves:
        # Drift votes are per colour and action-blind: what marks scenery is
        # that the action does not matter to it.
        drift = model["auto"].setdefault(char, {})
        drift[delta] = drift.get(delta, 0) + 1
        if name == "MOUSE":
            continue
        votes = model["delta_votes"].setdefault(name, {})
        votes[delta] = votes.get(delta, 0) + 1
        # A mover that answers opposite controls oppositely is body-like.
        mate = WM_OPPOSITE.get(name)
        if mate and mate in model["delta_votes"]:
            for other, count in model["delta_votes"][mate].items():
                if other[0] == -delta[0] and other[1] == -delta[1] and count:
                    model["body_votes"][char] = model["body_votes"].get(char, 0) + 1

    _wm_learn_shrink(model, before, after)
    _wm_track_still(model, before, after, set(m[0] for m in moves))
    _wm_settle(model)
    return model


def _wm_track_still(model, before, after, moved_chars):
    """Count the steps each colour sat through unchanged.

    Drift and decay are claims about EVERY step -- a timer loses a segment
    each tick, a patroller slides each tick. A colour that moved three times
    and held still ninety-seven is scenery that got bumped, and without this
    denominator the model predicts the bump forever, which is exactly how six
    games' exact-match went to zero.
    """
    counts_b = {}
    counts_a = {}
    for row in before:
        for ch in row:
            counts_b[ch] = counts_b.get(ch, 0) + 1
    for row in after:
        for ch in row:
            counts_a[ch] = counts_a.get(ch, 0) + 1
    for char, n in counts_b.items():
        if char in moved_chars or n > 200:
            continue
        if counts_a.get(char, 0) == n:
            model["still"][char] = model["still"].get(char, 0) + 1


def wm_predict(model, board, action):
    """The theory's next frame: clicks, body motion, drift and decay composed
    over a copy-forward base."""
    name, click = _wm_key(action)
    grid = [list(row) for row in board]

    if name == "MOUSE" and click is not None:
        _wm_apply_click(model, grid, click)
    else:
        _wm_apply_move(model, grid, name)
    _wm_apply_auto(model, grid)
    _wm_apply_shrink(model, grid)
    return ["".join(row) for row in grid]


def _wm_apply_move(model, grid, name):
    delta = model["deltas"].get(name)
    body = model["body_char"]
    if delta is None or body is None:
        return
    height = len(grid)
    width = len(grid[0]) if height else 0
    cells = [(r, c) for r in range(height) for c in range(width) if grid[r][c] == body]
    if not cells or len(cells) > 200:
        return

    # The move happens only if every target cell is free or vacated.
    source = set(cells)
    fill = _wm_background(grid)
    for r, c in cells:
        nr, nc = r + delta[0], c + delta[1]
        if not (0 <= nr < height and 0 <= nc < width):
            return
        ch = grid[nr][nc]
        if (nr, nc) not in source and _wm_blocks(model, ch):
            return

    for r, c in cells:
        grid[r][c] = fill
    for r, c in cells:
        grid[r + delta[0]][c + delta[1]] = body


def _wm_apply_click(model, grid, click):
    r, c = click
    if not (0 <= r < len(grid) and 0 <= c < len(grid[r])):
        return
    src = grid[r][c]
    votes = model["clicks"].get(src)
    if not votes:
        return
    outcome = max(sorted(votes), key=lambda k: votes[k])
    if votes[outcome] < 2:
        return
    if outcome[0] == "cell":
        grid[r][c] = outcome[1]
    elif outcome[0] == "component":
        for rr, cc in _wm_component(grid, r, c):
            grid[rr][cc] = outcome[1]


def _wm_apply_auto(model, grid):
    """Translate colours that drift the same way whatever the action was."""
    body = model["body_char"]
    height = len(grid)
    width = len(grid[0]) if height else 0
    for char in sorted(model["auto"]):
        if char == body:
            continue
        votes = model["auto"][char]
        best = max(sorted(votes), key=lambda d: votes[d])
        total = sum(votes.values()) + model["still"].get(char, 0)
        if votes[best] < 3 or votes[best] < 0.8 * total:
            continue
        cells = [(r, c) for r in range(height) for c in range(width) if grid[r][c] == char]
        if not cells or len(cells) > 200:
            continue
        source = set(cells)
        fill = _wm_background(grid)
        ok = True
        for r, c in cells:
            nr, nc = r + best[0], c + best[1]
            if not (0 <= nr < height and 0 <= nc < width):
                ok = False
                break
            if (nr, nc) not in source and grid[nr][nc] != fill:
                ok = False
                break
        if not ok:
            continue
        for r, c in cells:
            grid[r][c] = fill
        for r, c in cells:
            grid[r + best[0]][c + best[1]] = char


def _wm_apply_shrink(model, grid):
    """Remove one end cell of colours that decay one cell per step (timers)."""
    fill = _wm_background(grid)
    for char in sorted(model["shrink"]):
        votes = model["shrink"][char]
        end = max(sorted(votes), key=lambda k: votes[k])
        total = sum(votes.values()) + model["still"].get(char, 0)
        if end == "other" or votes[end] < 3 or votes[end] < 0.8 * total:
            continue
        cells = _wm_cells(grid, char)
        if not cells or len(cells) > 200:
            continue
        r, c = max(cells) if end == "max" else min(cells)
        grid[r][c] = fill


def wm_summary(model):
    """The ~40-token line the LLM reads instead of re-deriving physics."""
    blockers = sorted(
        ch
        for ch, seen in model["blockers"].items()
        if seen["hit"] >= 2 and seen["hit"] > 2 * seen["through"]
    )
    clicks = {}
    for char, votes in model["clicks"].items():
        outcome = max(sorted(votes), key=lambda k: votes[k])
        if votes[outcome] >= 2 and outcome[0] != "none":
            clicks[char] = outcome[0] if len(outcome) == 1 else f"{outcome[0]}->{outcome[1]}"
    return {
        "body": model["body_char"],
        "deltas": dict(model["deltas"]),
        "blockers": "".join(blockers),
        "clicks": clicks,
        "steps": model["steps"],
    }


# --- internals -------------------------------------------------------------


def _wm_settle(model):
    """Promote the strongest votes to beliefs."""
    if model["body_votes"]:
        model["body_char"] = max(
            sorted(model["body_votes"]), key=lambda ch: model["body_votes"][ch]
        )
    for action, votes in model["delta_votes"].items():
        best = max(sorted(votes), key=lambda d: votes[d])
        if votes[best] >= 2 or len(votes) == 1:
            model["deltas"][action] = best


def _wm_learn_block(model, board, action):
    """A move that failed teaches: something in the swept path refused it.

    Every colour on the path is charged, because a multi-cell stride hides
    which cell did the blocking. The innocent majority -- usually the
    background -- is exonerated by the through counter as successful moves
    sweep it, so only colours that block and are never crossed stay guilty.
    """
    delta = model["deltas"].get(action)
    body = model["body_char"]
    if delta is None or body is None:
        return
    for ch in _wm_swept(board, body, delta):
        seen = model["blockers"].setdefault(ch, {"hit": 0, "through": 0})
        seen["hit"] += 1


def _wm_centroid_shift(before, after, char):
    """How far a colour's centroid moved, in whole cells; None if absent."""
    cells_b = _wm_cells(before, char)
    cells_a = _wm_cells(after, char)
    if not cells_b or not cells_a:
        return None
    rb = sum(r for r, _ in cells_b) / len(cells_b)
    cb = sum(c for _, c in cells_b) / len(cells_b)
    ra = sum(r for r, _ in cells_a) / len(cells_a)
    ca = sum(c for _, c in cells_a) / len(cells_a)
    return (int(round(ra - rb)), int(round(ca - cb)))


def _wm_swept(board, body, delta):
    """Colours in the region a body stride passes over, body cells excluded."""
    height = len(board)
    width = len(board[0]) if height else 0
    steps = max(abs(delta[0]), abs(delta[1]))
    if not steps:
        return set()
    unit = (
        (delta[0] > 0) - (delta[0] < 0),
        (delta[1] > 0) - (delta[1] < 0),
    )
    swept = set()
    for r in range(height):
        for c in range(width):
            if board[r][c] != body:
                continue
            for k in range(1, steps + 1):
                nr, nc = r + unit[0] * k, c + unit[1] * k
                if 0 <= nr < height and 0 <= nc < width:
                    ch = board[nr][nc]
                    if ch != body:
                        swept.add(ch)
    return swept


def _wm_learn_click(model, before, click, after):
    """What clicking a colour does: nothing, recolour the cell, or recolour
    its whole connected component. Anything wider is left unlearned rather
    than guessed."""
    r, c = click
    if not (0 <= r < len(before) and 0 <= c < len(before[r])):
        return
    src = before[r][c]
    changed = []
    for rr in range(min(len(before), len(after))):
        row_b, row_a = before[rr], after[rr]
        if row_b == row_a:
            continue
        for cc in range(min(len(row_b), len(row_a))):
            if row_b[cc] != row_a[cc]:
                changed.append((rr, cc))
                if len(changed) > 500:
                    return
    if not changed:
        outcome = ("none",)
    else:
        grid = [list(row) for row in before]
        component = _wm_component(grid, r, c)
        after_colours = set(after[rr][cc] for rr, cc in changed)
        if len(after_colours) == 1 and set(changed) == component:
            outcome = ("component", after_colours.pop())
        elif changed == [(r, c)]:
            outcome = ("cell", after[r][c])
        else:
            outcome = ("complex",)
    votes = model["clicks"].setdefault(src, {})
    votes[outcome] = votes.get(outcome, 0) + 1


def _wm_learn_shrink(model, before, after):
    """A colour that lost exactly one cell and gained none is decaying."""
    counts_b = {}
    counts_a = {}
    for row in before:
        for ch in row:
            counts_b[ch] = counts_b.get(ch, 0) + 1
    for row in after:
        for ch in row:
            counts_a[ch] = counts_a.get(ch, 0) + 1
    for char, n_before in counts_b.items():
        if counts_a.get(char, 0) != n_before - 1 or n_before > 200:
            continue
        cells_b = set(_wm_cells(before, char))
        cells_a = set(_wm_cells(after, char))
        lost = cells_b - cells_a
        if len(lost) != 1 or cells_a - cells_b:
            continue
        cell = lost.pop()
        if cell == max(cells_b):
            end = "max"
        elif cell == min(cells_b):
            end = "min"
        else:
            end = "other"
        votes = model["shrink"].setdefault(char, {"max": 0, "min": 0, "other": 0})
        votes[end] += 1


def _wm_component(grid, r, c):
    """Four-connected same-colour cells reachable from (r, c), as a set."""
    char = grid[r][c]
    seen = {(r, c)}
    stack = [(r, c)]
    while stack:
        cr, cc = stack.pop()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = cr + dr, cc + dc
            if (
                0 <= nr < len(grid)
                and 0 <= nc < len(grid[nr])
                and (nr, nc) not in seen
                and grid[nr][nc] == char
            ):
                seen.add((nr, nc))
                stack.append((nr, nc))
                if len(seen) > 500:
                    return seen
    return seen


def _wm_blocks(model, char):
    seen = model["blockers"].get(char)
    return bool(seen) and seen["hit"] >= 2 and seen["hit"] > 2 * seen["through"]


def _wm_background(grid):
    counts = {}
    for row in grid:
        for ch in row:
            counts[ch] = counts.get(ch, 0) + 1
    return max(sorted(counts), key=lambda ch: counts[ch]) if counts else " "


def _wm_movers(before, after, limit=6):
    """Colours whose full cell set rigidly translated between two boards.

    The whole set is compared, not just the changed cells. Diffing only the
    changed cells of a solid body yields its trailing and leading strips, and
    their offset is the body's WIDTH, not its step -- the exact degenerate
    (0, 6) readings the first Kaggle run kept reporting.
    """
    touched = set()
    height = min(len(before), len(after))
    for r in range(height):
        row_b, row_a = before[r], after[r]
        if row_b == row_a:
            continue
        for c in range(min(len(row_b), len(row_a))):
            if row_b[c] != row_a[c]:
                touched.add(row_b[c])
                touched.add(row_a[c])

    moves = []
    for ch in sorted(touched):
        cells_b = _wm_cells(before, ch)
        if not cells_b or len(cells_b) > 400:
            continue
        cells_a = _wm_cells(after, ch)
        if len(cells_a) != len(cells_b):
            continue
        dr = cells_a[0][0] - cells_b[0][0]
        dc = cells_a[0][1] - cells_b[0][1]
        if (dr or dc) and all(
            (r + dr, c + dc) == a for (r, c), a in zip(cells_b, cells_a)
        ):
            moves.append((ch, (dr, dc), len(cells_b)))
        if len(moves) >= limit:
            break
    return moves


def _wm_cells(board, char, cap=401):
    """Sorted positions of a colour, capped so scenery never gets scanned."""
    cells = []
    for r, row in enumerate(board):
        for c, ch in enumerate(row):
            if ch == char:
                cells.append((r, c))
                if len(cells) >= cap:
                    return cells
    return cells
