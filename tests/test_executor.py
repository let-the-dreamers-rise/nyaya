"""Tests for the policies the analyzer delegates to.

These exec the same concatenated source that deployment injects into the
sandbox, against a fake runtime that rebinds current_frame after every action
the way the real one does. A pass here is a statement about what the model will
actually run, not about an import of this package.
"""
from __future__ import annotations

import ast
import inspect
import re

import pytest

from nyaya import executor as ex
from nyaya import sandbox_helpers as sh

NL = chr(10)
MOVES = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}


def injected_source():
    """Exactly what gets prepended to the model's code."""
    return inspect.getsource(sh) + NL + NL + inspect.getsource(ex)


class Frame:
    def __init__(self, ascii_text, level):
        self.ascii = ascii_text
        self.level = level


class World:
    """A grid the fake action() drives, standing in for the environment.

    ``@`` is the body, ``#`` blocks it, clicking a ``*`` clears it, stepping
    onto ``goal`` advances the level, and stepping onto ``trap`` ends the game.
    """

    def __init__(self, rows, goal=None, trap=None, valid=None, ticker=None):
        self.rows = [list(row) for row in rows]
        self.goal = goal
        self.trap = trap
        self.valid = list(valid or MOVES)
        self.ticker = ticker
        self.level = 0
        self.over = False
        self.log = []

    @property
    def ascii(self):
        return NL.join("".join(row) for row in self.rows)

    def at(self):
        for r, row in enumerate(self.rows):
            for c, char in enumerate(row):
                if char == "@":
                    return (r, c)
        return None

    def tick(self):
        """Advance the scenery: a mark that slides the same way every action.

        This is what broke the Kaggle run. A timer, a scrolling background or
        an animation on its own clock shifts on every step regardless of which
        control was pressed, and it can shift by less than the body does.
        """
        if self.ticker is None:
            return
        row, col, step = self.ticker
        width = len(self.rows[0])
        self.rows[row][col] = "."
        col = (col - 1) % width if (col + step) % width == 0 else (col + step) % width
        if self.rows[row][col] == ".":
            self.rows[row][col] = "T"
            self.ticker = (row, col, step)

    def step(self, spec):
        self.log.append(spec)
        self.tick()
        if isinstance(spec, dict):
            row, col = spec["row"], spec["col"]
            if self.rows[row][col] == "*":
                self.rows[row][col] = "."
            return
        delta = MOVES.get(spec)
        here = self.at()
        if delta is None or here is None:
            return
        nxt = (here[0] + delta[0], here[1] + delta[1])
        if not (0 <= nxt[0] < len(self.rows) and 0 <= nxt[1] < len(self.rows[0])):
            return
        if self.rows[nxt[0]][nxt[1]] == "#":
            return
        self.rows[here[0]][here[1]] = "."
        self.rows[nxt[0]][nxt[1]] = "@"
        if self.goal is not None and nxt == self.goal:
            self.level += 1
        if self.trap is not None and nxt == self.trap:
            self.over = True

    def sandbox(self):
        """A namespace holding the injected source over a live fake runtime.

        action() returns the host's compact payload and, once any action has
        reported a terminal state, refuses every later one with
        ``executed: False`` and an unchanged frame -- which is what the real
        host does for the rest of a snippet.
        """
        ns = {}
        exec(compile(injected_source(), "<sandbox>", "exec"), ns)
        terminal = []

        def action(specs):
            ns["previous_frame"] = ns["current_frame"]
            if terminal:
                return {"executed": False, "board_changed": False, "stopped_early": True}
            before, level = self.ascii, self.level
            for spec in specs:
                self.step(spec)
            ns["current_frame"] = Frame(self.ascii, self.level)
            ns["valid_actions"] = list(self.valid)
            payload = {
                "executed": True,
                "board_changed": self.ascii != before,
                "level_completed": self.level > level,
                "game_over": self.over,
                "level": self.level,
            }
            if payload["level_completed"] or payload["game_over"]:
                terminal.append(payload)
            return payload

        ns["action"] = action
        ns["current_frame"] = Frame(self.ascii, self.level)
        ns["previous_frame"] = None
        ns["valid_actions"] = list(self.valid)
        return ns


def open_room(size=7):
    rows = ["#" * size]
    for _ in range(size - 2):
        rows.append("#" + "." * (size - 2) + "#")
    rows.append("#" * size)
    mid = size // 2
    rows[mid] = rows[mid][:mid] + "@" + rows[mid][mid + 1 :]
    return rows


@pytest.fixture
def room():
    return World(open_room())


# --- what the sandbox will accept ------------------------------------------


def test_injected_source_compiles():
    # Concatenation is the deployment path, and a stray __future__ line in the
    # second file would make the whole blob a syntax error.
    compile(injected_source(), "<sandbox>", "exec")


def test_executor_uses_no_imports():
    # The sandbox importer allows only a short stdlib whitelist, so an import
    # here would raise the moment the model called the policy.
    tree = ast.parse(inspect.getsource(ex))
    assert [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))] == []


def test_executor_avoids_builtins_the_sandbox_withholds():
    # The restricted builtins omit these, and there is no time module at all.
    source = inspect.getsource(ex)
    for name in ("globals", "exec", "eval", "object", "__import__", "open", "time"):
        assert re.search(r"\b" + name + r"\s*\(", source) is None, name


# --- learning the controls -------------------------------------------------


def test_learn_controls_recovers_the_movement_model(room):
    ns = room.sandbox()
    report = ns["learn_controls"](names=MOVES, repeats=2)
    assert report["deltas"] == MOVES
    assert report["inferred"] == []
    assert report["actions_spent"] == 8
    assert report["position"] == room.at()


def test_learn_controls_retries_what_a_wall_hid():
    # Wedged in a corner, three of four controls do nothing on the first pass.
    # After RIGHT moves the body, LEFT is worth another look.
    world = World(["#####", "#@..#", "#####"])
    ns = world.sandbox()
    report = ns["learn_controls"](names=MOVES, repeats=1)
    assert report["deltas"]["RIGHT"] == (0, 1)
    assert report["deltas"]["LEFT"] == (0, -1)
    assert "LEFT" not in report["inferred"]


def test_learn_controls_ignores_scenery_that_moves_on_every_action():
    # The failure that cost the first Kaggle run: five controls all reported
    # the same delta, because the shortest hop belonged to a ticking strip
    # rather than to the body. Opposite controls answering identically is the
    # tell, and it is the one thing no real body does.
    rows = ["#" * 14] + ["#" + "." * 12 + "#" for _ in range(9)] + ["#" * 14]
    rows[5] = rows[5][:6] + "@" + rows[5][7:]
    world = World(rows, ticker=(1, 1, 1))
    ns = world.sandbox()

    report = ns["learn_controls"](names=MOVES, repeats=2)
    assert report["deltas"] == MOVES, report["deltas"]
    assert report["body"] == ("@", 1)


def test_consistency_rejects_one_answer_to_opposite_questions():
    ns = World(open_room()).sandbox()
    same = {"UP": (0, 6), "DOWN": (0, 6), "LEFT": (0, 6), "RIGHT": (0, 6)}
    real = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
    assert ns["_consistency"](real) > ns["_consistency"](same)
    assert ns["_consistency"](same) < 0


def test_consistency_accepts_an_inverted_mapping():
    # A game may map UP to downward motion, or swap the axes. Only relational
    # structure is scored, so an inverted body still reads as a body.
    ns = World(open_room()).sandbox()
    inverted = {"UP": (1, 0), "DOWN": (-1, 0), "LEFT": (0, 1), "RIGHT": (0, -1)}
    swapped = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}
    for deltas in (inverted, swapped):
        assert ns["_consistency"](deltas) >= ns["_consistency"](
            {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
        )


def test_pick_body_prefers_the_mover_that_answers_the_controls():
    ns = World(open_room()).sandbox()
    seen = {
        "UP": {("@", 1): (-1, 0), ("T", 1): (0, 1)},
        "DOWN": {("@", 1): (1, 0), ("T", 1): (0, 1)},
        "LEFT": {("@", 1): (0, -1), ("T", 1): (0, 1)},
        "RIGHT": {("@", 1): (0, 1), ("T", 1): (0, 1)},
    }
    body, deltas, score = ns["_pick_body"](seen)
    assert body == ("@", 1)
    assert deltas == MOVES
    assert score > 0


def test_pick_body_reports_nothing_when_nothing_moved():
    ns = World(open_room()).sandbox()
    assert ns["_pick_body"]({}) == (None, {}, 0)


def test_learn_controls_reflects_a_control_it_could_not_observe():
    # A one-way corridor never lets LEFT be seen, but its opposite is known and
    # geometry is one of the priors this benchmark tests.
    world = World(["#####", "#@..#", "#####"], valid=["RIGHT", "LEFT"])
    ns = world.sandbox()
    ns["learn_controls"] = ns["learn_controls"]
    report = ns["learn_controls"](names=["RIGHT"], repeats=1)
    assert report["deltas"] == {"RIGHT": (0, 1)}

    report = ns["learn_controls"](names=["RIGHT", "UP"], repeats=1)
    assert "UP" not in report["deltas"], "nothing vertical was ever seen"


def test_learn_controls_infers_the_opposite_of_what_it_saw():
    world = World(["#######", "#@....#", "#######"])
    ns = world.sandbox()
    # Only RIGHT is offered, so LEFT is never probed and never observed.
    report = ns["learn_controls"](names=["RIGHT", "LEFT"], repeats=1)
    assert report["deltas"]["RIGHT"] == (0, 1)
    assert report["deltas"]["LEFT"] == (0, -1)


def test_learn_controls_probes_space_by_default():
    # SPACE moves no body, so it earns no delta -- but whether it does anything
    # at all is a fact about the game worth one action.
    world = World(open_room(), valid=list(MOVES) + ["SPACE"])
    ns = world.sandbox()
    report = ns["learn_controls"](repeats=1)
    # Five probes, plus one retry for SPACE, which the first pass could not
    # tell apart from a control blocked by whatever the body was standing on.
    assert report["actions_spent"] == 6
    assert "SPACE" not in report["deltas"]
    assert "SPACE" not in report["effective"]
    assert set(report["effective"]) == set(MOVES)


def test_learn_controls_probes_only_what_the_runtime_offers():
    world = World(open_room(), valid=["UP", "DOWN"])
    ns = world.sandbox()
    report = ns["learn_controls"](repeats=1)
    assert set(report["deltas"]) == {"UP", "DOWN"}
    assert report["actions_spent"] == 2


def test_learn_controls_reports_nothing_for_an_inert_control():
    # Wedged against the top wall, UP costs an action and teaches nothing --
    # which the report must say rather than inventing a delta.
    world = World(["#####", "#@..#", "#...#", "#####"])
    ns = world.sandbox()
    report = ns["learn_controls"](names=["UP"], repeats=2, retry_unknown=False)
    assert report["deltas"] == {}
    assert report["effective"] == []
    assert report["inferred"] == []
    assert report["actions_spent"] == 2


# --- routing ---------------------------------------------------------------


def test_auto_route_detours_around_a_wall():
    world = World(["#######", "#@....#", "#####.#", "#.....#", "#######"])
    ns = world.sandbox()
    report = ns["auto_route"](3, 1, MOVES, blocked_chars="#", start=(1, 1))
    assert report["stopped"] == "arrived"
    assert world.at() == (3, 1)
    assert report["acted"] == 10


def test_auto_route_spends_nothing_when_the_target_is_unreachable(room):
    ns = room.sandbox()
    report = ns["auto_route"](0, 0, MOVES, blocked_chars="#", start=(3, 3))
    assert report["acted"] == 0
    assert report["stopped"] == "unreachable"
    assert world_actions(room) == 0


def test_auto_route_names_the_controls_it_had():
    # The usual cause of unreachable is a movement model missing an axis, so
    # the report has to show what it was working with.
    world = World(open_room())
    ns = world.sandbox()
    report = ns["auto_route"](5, 3, {"LEFT": (0, -1), "RIGHT": (0, 1)}, start=(3, 3))
    assert report["known"] == ["LEFT", "RIGHT"]


def test_auto_route_abandons_a_plan_the_board_contradicts():
    # The deltas are wrong: UP is claimed to move right. The first step proves
    # it, and the policy must stop there rather than spend the plan out.
    world = World(["#####", "#@..#", "#...#", "#####"])
    ns = world.sandbox()
    report = ns["auto_route"](1, 3, {"UP": (0, 1)}, blocked_chars="#", start=(1, 1))
    assert report == {"acted": 1, "stopped": "blocked; replan"}


def test_auto_route_stops_the_moment_the_level_clears():
    world = World(["#######", "#@...G#", "#######"], goal=(1, 5))
    ns = world.sandbox()
    report = ns["auto_route"](1, 5, MOVES, blocked_chars="#", start=(1, 1))
    assert report["stopped"] == "level up"
    assert report["level"] == 1
    assert report["acted"] == 4


def test_auto_route_admits_when_it_ran_out_of_steps():
    world = World(["#######", "#@....#", "#######"])
    ns = world.sandbox()
    report = ns["auto_route"](1, 5, MOVES, blocked_chars="#", start=(1, 1), max_steps=2)
    assert report["stopped"] == "step cap; call again"
    assert report["acted"] == 2
    assert report["remaining"] == 2


def test_auto_route_needs_a_position(room):
    ns = room.sandbox()
    report = ns["auto_route"](1, 1, MOVES, blocked_chars="#")
    assert report["acted"] == 0
    assert "position unknown" in report["stopped"]


def test_auto_route_without_controls_spends_nothing(room):
    ns = room.sandbox()
    assert ns["auto_route"](1, 1, {}, start=(3, 3))["acted"] == 0


# --- repeating -------------------------------------------------------------


def test_auto_repeat_stops_when_the_move_stops_working():
    world = World(["#######", "#@....#", "#######"])
    ns = world.sandbox()
    report = ns["auto_repeat"]("RIGHT", 50)
    assert report == {"acted": 5, "stopped": "no effect"}
    assert world.at() == (1, 5)


def test_auto_repeat_is_capped_at_the_call_ceiling():
    world = World(["#####", "#..@#", "#####"])
    ns = world.sandbox()
    report = ns["auto_repeat"]("RIGHT", 5000, stop_when_still=False)
    assert report["acted"] == ex.MAX_STEPS_PER_CALL


# --- clicking --------------------------------------------------------------


def test_auto_click_all_clears_every_target():
    world = World(["#######", "#*.*..#", "#..*..#", "#######"])
    ns = world.sandbox()
    report = ns["auto_click_all"]("*", skip_hud=False)
    assert report["acted"] == 3
    assert report["stopped"] == "none left"
    assert "*" not in world.ascii


def test_auto_click_all_leaves_a_hud_strip_alone():
    # The strip shed a segment while the interior held still, which is what
    # marks it as scenery -- and the segments left standing must be spared
    # too, or a whole budget goes into a clock.
    rows = ["." * 12 for _ in range(12)]
    rows[0] = ".**........."
    rows[5] = ".....*......"
    rows[6] = "......*....."
    world = World(rows)
    ns = world.sandbox()
    ns["previous_frame"] = Frame(world.ascii.replace(".**...", ".***..", 1), 0)

    report = ns["auto_click_all"]("*")
    assert report["acted"] == 2
    assert world.rows[0][1] == "*" and world.rows[0][2] == "*"
    assert world.rows[5][5] == "." and world.rows[6][6] == "."


def test_auto_click_all_gives_up_on_cells_that_do_nothing():
    # Nothing here is clickable, so every click is wasted; the policy must
    # learn that from the board rather than burn the whole limit.
    world = World(["#######", "#*.*..#", "#######"])
    world.step = lambda spec: world.log.append(spec)
    ns = world.sandbox()
    report = ns["auto_click_all"]("*", limit=20, skip_hud=False)
    assert report["acted"] == 2
    assert report["stopped"] == "none left"


# --- sweeping --------------------------------------------------------------


def test_auto_sweep_drops_controls_that_go_inert():
    world = World(["#######", "#@....#", "#######"])
    ns = world.sandbox()
    report = ns["auto_sweep"](budget=50)
    assert report["stopped"] == "all controls inert"
    assert world.at() == (1, 5)
    assert report["acted"] < 50


def test_auto_sweep_stops_on_a_level_up():
    world = World(["#######", "#@...G#", "#######"], goal=(1, 5))
    ns = world.sandbox()
    report = ns["auto_sweep"](budget=50)
    assert report["stopped"] == "level up"
    assert report["level"] == 1


def test_auto_sweep_respects_its_budget(room):
    ns = room.sandbox()
    report = ns["auto_sweep"](budget=5)
    assert report == {
        "acted": 5,
        "stopped": "budget",
        "level": 0,
        "levels_gained": 0,
    }


# --- ending the game -------------------------------------------------------


def test_auto_repeat_stops_when_the_game_ends():
    world = World(["#####", "#@X.#", "#####"], trap=(1, 2))
    ns = world.sandbox()
    report = ns["auto_repeat"]("RIGHT", 50)
    assert report["stopped"] == "game over"
    assert report["acted"] == 1
    assert len(world.log) == 1


def test_auto_sweep_stops_when_the_game_ends():
    world = World(["#####", "#@X.#", "#####"], trap=(1, 2))
    ns = world.sandbox()
    report = ns["auto_sweep"](budget=50)
    assert report["stopped"] == "game over"
    # UP, DOWN and LEFT are all walls here, so only the fourth ends it.
    assert report["acted"] == 4


def test_auto_route_stops_when_the_game_ends():
    world = World(["#####", "#@X.#", "#####"], trap=(1, 2))
    ns = world.sandbox()
    report = ns["auto_route"](1, 3, MOVES, blocked_chars="#", start=(1, 1))
    assert report["stopped"] == "game over"
    assert report["acted"] == 1


def test_learn_controls_stops_probing_once_the_game_ends():
    # The host refuses every action after a terminal one, so continuing would
    # spend the rest of the probe learning nothing.
    world = World(["#####", "#@X.#", "#####"], trap=(1, 2))
    ns = world.sandbox()
    report = ns["learn_controls"](names=["RIGHT", "UP", "DOWN"], repeats=2)
    assert report["stopped"] == "game over"
    assert report["actions_spent"] == 1


def test_learn_controls_does_not_read_a_step_that_cleared_a_level():
    # The board is replaced at a level change, so the displacement across that
    # step describes nothing and must not enter the movement model.
    world = World(["#######", "#@G...#", "#######"], goal=(1, 2))
    ns = world.sandbox()
    report = ns["learn_controls"](names=["RIGHT"], repeats=2)
    assert report["stopped"] == "level up"
    assert report["deltas"] == {}


def test_the_engine_verdict_beats_the_ascii_diff():
    # A ticking HUD makes every frame differ, so a diff always says "changed".
    # The host's own board_changed is the answer that matters.
    ns = {}
    exec(compile(injected_source(), "<sandbox>", "exec"), ns)
    ticks = [0]

    def action(specs):
        ticks[0] += 1
        ns["previous_frame"] = ns["current_frame"]
        ns["current_frame"] = Frame("@" + "." * ticks[0], 0)
        return {"executed": True, "board_changed": False}

    ns["action"] = action
    ns["current_frame"] = Frame("@", 0)
    ns["previous_frame"] = None
    ns["valid_actions"] = list(MOVES)

    report = ns["auto_repeat"]("RIGHT", 50)
    assert report == {"acted": 1, "stopped": "no effect"}


def test_a_diff_still_answers_when_the_host_says_nothing():
    # Against a harness that returns no payload the policies fall back to the
    # board, so they keep working rather than reading silence as "no effect".
    world = World(["#######", "#@....#", "#######"])
    ns = world.sandbox()
    stepped = ns["action"]
    ns["action"] = lambda specs: stepped(specs) and None
    report = ns["auto_repeat"]("RIGHT", 50)
    assert report == {"acted": 5, "stopped": "no effect"}
    assert world.at() == (1, 5)


# --- the point of the whole file -------------------------------------------


def test_one_call_buys_hundreds_of_actions():
    # The blocker this module exists to remove: ~441 tokens per action against
    # a ~65k-token run. Here 400 actions cost one round trip.
    world = World(open_room(21))
    ns = world.sandbox()
    report = ns["auto_sweep"](budget=400)
    assert report["acted"] == 400
    assert world_actions(world) == 400


def test_reports_stay_small_enough_to_be_worth_sending():
    # A policy that echoed the board would spend the tokens it was written to
    # save, so no field may carry anything board-sized.
    world = World(open_room(21))
    ns = world.sandbox()
    reports = [
        ns["learn_controls"](repeats=1),
        ns["auto_repeat"]("RIGHT", 3),
        ns["auto_sweep"](budget=8),
        ns["auto_click_all"]("*", limit=2),
    ]
    # Roughly 70 tokens at the widest, against ~1600 for a 40x40 board.
    for report in reports:
        assert len(repr(report)) < 280


def world_actions(world):
    return len(world.log)
