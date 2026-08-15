"""Tests for the sandbox-injectable helpers.

These exercise the same source that gets injected into the analyzer's python
sandbox, so a pass here is a statement about what the model will execute.
"""
from __future__ import annotations

import ast
import inspect

from nyaya import sandbox_helpers as sh

NL = chr(10)


def board(rows):
    return NL.join(rows)


def blank(n=10):
    return ["." * n for _ in range(n)]


def test_helpers_use_no_imports():
    # The sandbox allows only a short stdlib whitelist, so an import inside an
    # injected helper would raise the moment the model ran it.
    tree = ast.parse(inspect.getsource(sh))
    bad = [
        n
        for n in ast.walk(tree)
        if isinstance(n, (ast.Import, ast.ImportFrom))
        and not (isinstance(n, ast.ImportFrom) and n.module == "__future__")
    ]
    assert bad == []


def test_grid_from_ascii_drops_blank_lines():
    assert sh.grid_from_ascii("ab" + NL + NL + "cd") == [["a", "b"], ["c", "d"]]


def test_hud_flags_an_edge_strip_moving_alone():
    a = blank(); a[0] = "XX........"
    b = blank(); b[0] = "X........."
    assert (0, 1) in sh.hud_cells(board(a), board(b), margin=2)


def test_hud_is_empty_when_the_interior_also_moved():
    a = blank(); a[0] = "XX........"; a[5] = "....o....."
    b = blank(); b[0] = "X........."; b[5] = ".....o...."
    assert sh.hud_cells(board(a), board(b), margin=2) == []


def test_hud_ignores_a_purely_interior_change():
    a = blank(); a[5] = "....o....."
    b = blank(); b[5] = ".....o...."
    assert sh.hud_cells(board(a), board(b), margin=2) == []


def test_hud_handles_mismatched_boards():
    assert sh.hud_cells("ab", "abc" + NL + "def") == []


def test_moved_object_reports_a_single_step():
    a = blank(); a[4] = "...o......"
    b = blank(); b[4] = "....o....."
    move = sh.moved_object(board(a), board(b))
    assert move is not None
    assert move["delta"] == (0, 1)
    assert move["char"] == "o"


def test_moved_object_is_none_when_nothing_moves():
    a = blank(); a[4] = "...o......"
    assert sh.moved_object(board(a), board(a)) is None


def test_moved_object_tracks_a_multi_cell_body():
    a = blank(); a[3] = "..oo......"
    b = blank(); b[5] = "..oo......"
    move = sh.moved_object(board(a), board(b))
    assert move is not None and move["delta"] == (2, 0) and move["size"] == 2


def test_moved_object_prefers_the_shortest_hop():
    a = blank(); a[0] = "x........."; a[4] = "...o......"
    b = blank(); b[9] = "x........."; b[4] = "....o....."
    move = sh.moved_object(board(a), board(b))
    assert move is not None and move["char"] == "o"


def test_route_finds_the_shortest_path():
    deltas = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
    path = sh.route((0, 0), (0, 3), deltas, lambda p: 0 <= p[0] < 8 and 0 <= p[1] < 8)
    assert path == ["RIGHT", "RIGHT", "RIGHT"]


def test_route_is_empty_when_already_there():
    assert sh.route((2, 2), (2, 2), {"UP": (-1, 0)}, lambda p: True) == []


def test_route_detours_around_a_wall():
    deltas = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}

    def passable(p):
        return 0 <= p[0] < 5 and 0 <= p[1] < 5 and p != (0, 1)

    path = sh.route((0, 0), (0, 2), deltas, passable)
    assert path is not None and len(path) == 4


def test_route_returns_none_when_walled_off():
    deltas = {"RIGHT": (0, 1)}
    path = sh.route((0, 0), (0, 4), deltas, lambda p: p[1] < 2)
    assert path is None


def test_route_without_deltas_is_none():
    assert sh.route((0, 0), (1, 1), {}, lambda p: True) is None


def test_route_respects_the_node_cap():
    deltas = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}
    path = sh.route(
        (0, 0), (7, 7), deltas, lambda p: 0 <= p[0] < 8 and 0 <= p[1] < 8, max_nodes=3
    )
    assert path is None
