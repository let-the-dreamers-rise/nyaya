"""Policies the analyzer delegates to, so actions stop costing tokens.

THE BLOCKER THIS EXISTS TO REMOVE

Measured across the runs in this repo: about 441 tokens of reasoning per
environment action, against roughly 65,000 tokens per run (195 tok/s aggregate,
divided by concurrency, times the wall clock). Perfect play costs 208 actions on
ft09 and 1,070 on sk48, so 92k and 472k tokens. Both exceed the budget, which
means winning is arithmetically impossible for any intelligence under
one-action-per-turn. Every run in this competition history ends gave_up at
about 66k tokens.

The sandbox already permits the fix. action(...) may be called repeatedly
inside a single python tool call, and the runtime rebinds current_frame,
previous_frame and valid_actions after each one. So a single tool call, one
round trip of tokens, can buy hundreds of actions. These functions are that
lever: the model names a policy, not a move.

CONSTRAINTS THIS FILE OBEYS, WHICH ARE SANDBOX RULES AND NOT PREFERENCES

No imports, because the importer allows only a short stdlib whitelist and this
source is injected verbatim. No globals, exec or object either, since the
restricted builtins omit them, so runtime state is reached by plain global
reference. That reference resolves against the sandbox namespace at call time
and therefore sees every refresh, which is also why nothing is cached across an
action(...) call. No time module exists, so each loop is bounded by step count
alone, well inside the 30 second tool ceiling.

Returns are compact dicts. A policy that printed boards would spend the tokens
it was written to save.

These build on helpers injected into the same namespace by sandbox_helpers:
grid_from_ascii, moved_object, route and hud_cells. This file carries no
``from __future__`` line of its own, because the two sources are concatenated
for injection and such an import is only legal at the top of the result.
"""

# action, current_frame, previous_frame and valid_actions come from the sandbox
# runtime, not from this module. They are referenced as globals so that every
# lookup sees the value left by the most recent action.

MOVE_NAMES = ("UP", "DOWN", "LEFT", "RIGHT")
# SPACE is probed too. It rarely moves a body, so it contributes no delta, but
# whether it changes the board at all is a fact about the game that costs one
# action to learn and cannot be read off a frame.
PROBE_NAMES = MOVE_NAMES + ("SPACE",)
# Geometry is one of the priors this benchmark tests, so a control whose
# opposite is known is better guessed than written off as inert.
OPPOSITE = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
MAX_STEPS_PER_CALL = 400


def _ex_ascii():
    """The current board, or an empty string when the runtime has no frame."""
    frame = current_frame  # noqa: F821 - sandbox global
    return getattr(frame, "ascii", "") or ""


def _ex_level():
    frame = current_frame  # noqa: F821 - sandbox global
    return int(getattr(frame, "level", 0) or 0)


def _ex_valid():
    try:
        return [str(name) for name in valid_actions]  # noqa: F821 - sandbox global
    except Exception:
        return []


def _ex_do(spec):
    """Run one environment action and report what the engine said about it.

    action(...) hands back the host's compact result, which answers directly
    what an ascii diff can only guess at: whether the board moved, whether the
    level cleared, whether the game ended. It is used when present and the diff
    is the fallback, so this still works against a harness shaped differently.

    The refusal case matters as much as the rest. Once any action in a snippet
    reports a terminal state the host stops executing and returns
    ``executed: False`` for everything after it, leaving the frame untouched.
    A policy that missed that would keep issuing moves into a finished game --
    the GAME_OVER loop the graft authors call the dominant score loss.
    """
    before = _ex_ascii()
    before_level = _ex_level()
    result = action([spec])  # noqa: F821 - sandbox global
    after = _ex_ascii()
    said = result if isinstance(result, dict) else {}

    changed = said.get("board_changed")
    if changed is None:
        changed = after != before
    refused = said.get("executed") is False
    return {
        "changed": bool(changed),
        "level_up": bool(said.get("level_completed")) or _ex_level() > before_level,
        "over": bool(
            said.get("game_over") or said.get("run_complete") or said.get("done")
        )
        or refused,
        "before": before,
        "after": after,
    }


def _ex_stop(result):
    """The reason to stop after one action, or None to carry on.

    A cleared level is checked first: an action can be both the last of a level
    and terminal, and the useful reading is that the level was won.
    """
    if result["level_up"]:
        return "level up"
    if result["over"]:
        return "game over"
    return None


def _ex_position():
    """Where the controlled body ended up, from the last real transition."""
    if previous_frame is None:  # noqa: F821 - sandbox global
        return None
    mover = moved_object(previous_frame.ascii, _ex_ascii())  # noqa: F821
    return mover["to"] if mover is not None else None


def _axis(step):
    """Which way a displacement mostly points: 0 for rows, 1 for columns."""
    return 0 if abs(step[0]) >= abs(step[1]) else 1


def _consistency(deltas):
    """How much a mover behaves like the thing the controls drive.

    Only relational structure is scored, never absolute direction. A game is
    free to map UP to downward motion, or to swap the axes outright, and this
    benchmark deliberately tests mappings that are not the obvious ones. What
    no game does is answer two opposite controls with the same displacement --
    so that, and its converse, carry the weight.
    """
    score = len(deltas)
    for name, mate in OPPOSITE.items():
        step = deltas.get(name)
        other = deltas.get(mate)
        if step is None or other is None:
            continue
        if step == other:
            score -= 4
        elif step[0] == -other[0] and step[1] == -other[1]:
            score += 4

    vertical = [deltas[n] for n in ("UP", "DOWN") if n in deltas]
    horizontal = [deltas[n] for n in ("LEFT", "RIGHT") if n in deltas]
    if vertical and horizontal:
        rows = set(_axis(step) for step in vertical)
        cols = set(_axis(step) for step in horizontal)
        if len(rows) == 1 and len(cols) == 1 and rows != cols:
            score += 3
    return score


def _pick_body(seen):
    """Choose which mover is the body, and return its deltas.

    ``seen`` maps a control name to ``{identity: delta}``. Scenery that shifts
    the same way on every action -- a timer, a scrolling background, an
    animation running on its own clock -- scores badly here however short its
    hop was, which is exactly what a shortest-hop rule cannot tell apart. The
    run that produced this function reported five controls all moving the body
    by (0, 6), and the model rightly refused to route on it.
    """
    identities = set()
    for by_identity in seen.values():
        identities.update(by_identity)

    best = None
    for identity in sorted(identities):
        deltas = {}
        for name in seen:
            if identity in seen[name]:
                deltas[name] = seen[name][identity]
        score = _consistency(deltas)
        if best is None or score > best[0]:
            best = (score, identity, deltas)
    if best is None:
        return None, {}, 0
    return best[1], best[2], best[0]


def learn_controls(names=None, repeats=1, retry_unknown=True):
    """Probe each control and report what it does.

    Costs one action per probe and returns the movement model the routing
    policies need. Two repeats by default, because a single sighting can be
    something else on the board moving at the same moment.

    ``deltas`` holds only controls that move a body. ``effective`` holds every
    control that changed the board at all, which is the wider and often more
    useful set: a control with no delta but a real effect is the game's verb.

    Two things stop a body wedged against a wall from reporting its controls as
    inert, which is what a single pass from a corner would conclude. Unknown
    controls get one more look after the first pass, by which point the body
    has usually moved off the wall; and anything still unknown whose opposite
    is known is filled in by reflection and listed under ``inferred``, so the
    model can see which entries are guesses. A wrong guess costs one action,
    because auto_route abandons a plan the board contradicts on the first step.
    """
    live = set(_ex_valid())
    names = [n for n in (names or PROBE_NAMES) if not live or n in live]
    votes = {}
    where = {}
    effective = []
    spent = 0
    stopped = None

    def probe(name, times):
        nonlocal spent, stopped
        for _ in range(max(1, int(times))):
            result = _ex_do(name)
            spent += 1
            # A cleared level replaces the board, so the displacement across
            # that step describes nothing; stop before reading it.
            stopped = _ex_stop(result)
            if stopped:
                return
            if not result["changed"]:
                continue
            if name not in effective:
                effective.append(name)
            for move in moved_objects(result["before"], result["after"]):  # noqa: F821
                identity = (move["char"], move["size"])
                counts = votes.setdefault(name, {}).setdefault(identity, {})
                counts[move["delta"]] = counts.get(move["delta"], 0) + 1
                where[identity] = move["to"]

    for name in names:
        if stopped:
            break
        probe(name, repeats)

    if retry_unknown:
        for name in names:
            if stopped:
                break
            if name not in votes:
                probe(name, 1)

    seen = {}
    for name in votes:
        picked = {}
        for identity, counts in votes[name].items():
            best = None
            for delta in counts:
                if best is None or counts[delta] > counts[best]:
                    best = delta
            if best is not None:
                picked[identity] = best
        seen[name] = picked

    body, deltas, score = _pick_body(seen)
    position = where.get(body)

    inferred = []
    observed = dict(deltas)
    for name in names:
        mate = OPPOSITE.get(name)
        if name in observed or mate is None or mate not in observed:
            continue
        step = observed[mate]
        deltas[name] = (-step[0], -step[1])
        inferred.append(name)

    return {
        "deltas": deltas,
        "body": body,
        "agreement": score,
        "effective": effective,
        "inferred": inferred,
        "position": position,
        "actions_spent": spent,
        "stopped": stopped,
        "level": _ex_level(),
    }


def auto_route(
    target_row, target_col, deltas, blocked_chars=None, max_steps=200, start=None
):
    """Walk to a target and report what happened.

    Plans once, then executes, and stops the moment the board stops responding
    as predicted. A wrong plan is worth abandoning immediately rather than
    spending the rest of the budget proving it wrong.
    """
    max_steps = min(int(max_steps), MAX_STEPS_PER_CALL)
    if not deltas:
        return {"acted": 0, "stopped": "no controls known"}

    grid = grid_from_ascii(_ex_ascii())  # noqa: F821
    walls = set(blocked_chars or ())
    height = len(grid)
    width = len(grid[0]) if height else 0

    def passable(point):
        r, c = point
        if not (0 <= r < height and 0 <= c < width):
            return False
        return grid[r][c] not in walls

    # The caller usually knows where the body is, from learn_controls or from
    # reading the board; falling back to the last transition only covers the
    # case where it does not, and that inference fails after a blocked move.
    if start is None:
        start = _ex_position()
    if start is None:
        return {"acted": 0, "stopped": "position unknown; move once first"}

    path = route(start, (int(target_row), int(target_col)), deltas, passable)  # noqa: F821
    if path is None:
        # Naming the controls in hand matters: the usual cause is a movement
        # model missing an axis, because the body was against a wall when it
        # was probed. That is fixed by moving and probing again, and the model
        # can only see to do it if the report says which controls were used.
        return {"acted": 0, "stopped": "unreachable", "known": sorted(deltas)}

    plan = path[:max_steps]
    acted = 0
    for name in plan:
        result = _ex_do(name)
        acted += 1
        stop = _ex_stop(result)
        if stop:
            return {"acted": acted, "stopped": stop, "level": _ex_level()}
        if not result["changed"]:
            return {"acted": acted, "stopped": "blocked; replan"}
    arrived = len(plan) == len(path)
    return {
        "acted": acted,
        "stopped": "arrived" if arrived else "step cap; call again",
        "remaining": len(path) - len(plan),
        "level": _ex_level(),
    }


def auto_repeat(name, times, stop_when_still=True):
    """Repeat one control, stopping as soon as it stops doing anything."""
    times = min(int(times), MAX_STEPS_PER_CALL)
    acted = 0
    for _ in range(times):
        result = _ex_do(name)
        acted += 1
        stop = _ex_stop(result)
        if stop:
            return {"acted": acted, "stopped": stop, "level": _ex_level()}
        if stop_when_still and not result["changed"]:
            return {"acted": acted, "stopped": "no effect"}
    return {"acted": acted, "stopped": "done", "level": _ex_level()}


def _ex_hud_block():
    """HUD cells, widened to the whole strip each flagged cell belongs to.

    hud_cells reports only what changed, but a timer sheds one segment at a
    time and the segments still standing look exactly like pieces worth
    clicking. Seeing any part of a run shift on a step where the interior held
    still condemns the entire run, so each flagged cell is flood-filled in the
    previous board, where it still had its colour.
    """
    if previous_frame is None:  # noqa: F821 - sandbox global
        return set()
    before = previous_frame.ascii  # noqa: F821 - sandbox global
    flagged = hud_cells(before, _ex_ascii())  # noqa: F821
    if not flagged:
        return set()

    grid = grid_from_ascii(before)  # noqa: F821
    block = set()
    for cell in flagged:
        if cell in block:
            continue
        row, col = cell
        if not (0 <= row < len(grid) and 0 <= col < len(grid[row])):
            continue
        char = grid[row][col]
        block.add(cell)
        stack = [cell]
        while stack:
            cr, cc = stack.pop()
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = cr + dr, cc + dc
                if (nr, nc) in block:
                    continue
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[nr]):
                    if grid[nr][nc] == char:
                        block.add((nr, nc))
                        stack.append((nr, nc))
    return block


def auto_click_all(char, limit=60, skip_hud=True):
    """Click every cell of one colour, re-reading the board each time.

    The board is re-read after every click because clicking one cell often
    removes others. HUD cells are skipped by default: a timer strip looks
    exactly like a row of clickable pieces, and working through a clock one
    segment at a time is a documented way to lose an entire budget.
    """
    limit = min(int(limit), MAX_STEPS_PER_CALL)
    acted = 0
    hud = _ex_hud_block() if skip_hud else set()

    for _ in range(limit):
        grid = grid_from_ascii(_ex_ascii())  # noqa: F821
        target = None
        for r in range(len(grid)):
            for c in range(len(grid[r])):
                if grid[r][c] == char and (r, c) not in hud:
                    target = (r, c)
                    break
            if target is not None:
                break
        if target is None:
            return {"acted": acted, "stopped": "none left", "level": _ex_level()}
        result = _ex_do({"action": "MOUSE", "row": target[0], "col": target[1]})
        acted += 1
        stop = _ex_stop(result)
        if stop:
            return {"acted": acted, "stopped": stop, "level": _ex_level()}
        if not result["changed"]:
            hud.add(target)
    return {"acted": acted, "stopped": "limit", "level": _ex_level()}


def auto_sweep(budget=40, names=None):
    """Rotate through the controls, dropping ones that stop having an effect.

    The fallback when nothing is understood yet: systematic coverage for one
    tool call instead of one call per action.

    The budget is deliberately small. A level scores (baseline / actions) ** 2,
    so against a 48-action baseline a 400-action sweep that clears the level
    still scores about 0.01 -- better than the zero for not clearing it, and
    far worse than routing. Blind cycling is the last resort, not the workhorse.
    """
    budget = min(int(budget), MAX_STEPS_PER_CALL)
    live = set(_ex_valid())
    names = list(names or [n for n in MOVE_NAMES if n in live] or MOVE_NAMES)
    started = _ex_level()
    dead = set()
    acted = 0
    while acted < budget:
        usable = [n for n in names if n not in dead]
        if not usable:
            return {"acted": acted, "stopped": "all controls inert", "level": _ex_level()}
        for name in usable:
            if acted >= budget:
                break
            result = _ex_do(name)
            acted += 1
            stop = _ex_stop(result)
            if stop:
                return {"acted": acted, "stopped": stop, "level": _ex_level()}
            if not result["changed"]:
                dead.add(name)
    return {
        "acted": acted,
        "stopped": "budget",
        "level": _ex_level(),
        "levels_gained": _ex_level() - started,
    }
