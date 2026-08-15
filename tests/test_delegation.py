"""Tests for getting the policies into the sandbox and into the prompt.

The patch target is a stand-in module shaped like inference.agent.tool_agent:
the real one cannot be imported here, and what matters is the contract between
them -- a keyword-only run_sandboxed_python and a module-level tool description.
"""
from __future__ import annotations

import ast
import types

from nyaya import delegation

STOCK_DESCRIPTION = "Run one ephemeral Python snippet against preloaded ASCII game state."


def fake_tool_agent(result=None):
    """A module shaped like the one that calls into the sandbox."""
    module = types.ModuleType("fake_tool_agent")
    calls = []

    def run_sandboxed_python(**kwargs):
        calls.append(kwargs)
        return dict(result) if result is not None else {"stdout": "", "error": ""}

    module.run_sandboxed_python = run_sandboxed_python
    module._PYTHON_TOOL_DESCRIPTION = STOCK_DESCRIPTION
    for name, old, _ in delegation.prompt_edits(180):
        setattr(module, name, "before. " + old + " after.")
    module.calls = calls
    return module


def call(module, code="print(1)", **extra):
    kwargs = {
        "code": code,
        "timeout_seconds": 30,
        "initial_state": {},
        "action_handler": lambda actions: {},
    }
    kwargs.update(extra)
    return module.run_sandboxed_python(**kwargs)


# --- the prelude -----------------------------------------------------------


def test_prelude_compiles_as_the_head_of_a_snippet():
    source = delegation.prelude_source() + "result = auto_sweep\n"
    compile(source, "<python_tool>", "exec")


def test_prelude_carries_no_imports_at_all():
    # A __future__ line is legal only at the top of a file, so it would break
    # the moment a model opened its own snippet with one; anything else would
    # hit the sandbox's short import whitelist.
    tree = ast.parse(delegation.prelude_source())
    assert [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))] == []


def test_prelude_defines_every_advertised_name():
    namespace = {}
    exec(compile(delegation.prelude_source(), "<python_tool>", "exec"), namespace)
    for name in (
        "learn_controls",
        "auto_route",
        "auto_repeat",
        "auto_click_all",
        "auto_sweep",
        "grid_from_ascii",
        "moved_object",
        "route",
        "hud_cells",
    ):
        assert name in namespace, name
        assert name in delegation.POLICY_BRIEF, name


# --- line numbers ----------------------------------------------------------


def test_remap_shifts_a_traceback_back_into_the_snippet():
    text = 'File "<python_tool>", line 412, in <module>'
    assert delegation.remap_traceback(text, 400) == (
        'File "<python_tool>", line 12, in <module>'
    )


def test_remap_marks_a_failure_inside_the_prelude():
    text = 'File "<python_tool>", line 30, in auto_route'
    out = delegation.remap_traceback(text, 400)
    assert 'line ?, in auto_route' in out


def test_remap_leaves_other_text_alone():
    assert delegation.remap_traceback("ValueError: line 9 is bad", 400) == (
        "ValueError: line 9 is bad"
    )


# --- installing ------------------------------------------------------------


def test_install_prepends_the_prelude_to_every_snippet():
    module = fake_tool_agent()
    delegation.install(module)
    call(module, code="result = auto_sweep(budget=50)")
    sent = module.calls[0]["code"]
    assert sent.startswith(delegation.HEADER)
    assert sent.endswith("result = auto_sweep(budget=50)")
    assert "def auto_sweep(" in sent


def test_install_reports_the_prelude_length():
    module = fake_tool_agent()
    report = delegation.install(module)
    assert report["sandbox"] is True
    assert report["prelude_lines"] == delegation.prelude_lines()
    assert report["prelude_lines"] > 100


def test_install_raises_the_timeout_for_batched_calls():
    module = fake_tool_agent()
    delegation.install(module, timeout_seconds=180)
    call(module)
    assert module.calls[0]["timeout_seconds"] == 180


def test_install_never_lowers_a_timeout_the_caller_chose():
    module = fake_tool_agent()
    delegation.install(module, timeout_seconds=180)
    call(module, timeout_seconds=600)
    assert module.calls[0]["timeout_seconds"] == 600


def test_install_can_leave_the_timeout_alone():
    module = fake_tool_agent()
    delegation.install(module, timeout_seconds=None)
    call(module)
    assert module.calls[0]["timeout_seconds"] == 30


def test_install_shifts_the_line_numbers_coming_back():
    offset = delegation.prelude_lines()
    reported = f'Traceback:{chr(10)}  File "<python_tool>", line {offset + 7}, in <module>'
    module = fake_tool_agent({"error": reported, "stdout": ""})
    delegation.install(module)
    assert 'line 7, in <module>' in call(module)["error"]


def test_install_does_not_mutate_the_sandbox_result():
    original = {"error": 'File "<python_tool>", line 999, in <module>', "stdout": ""}
    module = fake_tool_agent(original)
    delegation.install(module)
    call(module)
    assert original["error"] == 'File "<python_tool>", line 999, in <module>'


def test_install_passes_a_non_dict_result_through():
    module = fake_tool_agent()
    module.run_sandboxed_python = lambda **kwargs: "unexpected"
    delegation.install(module)
    assert call(module) == "unexpected"


def test_install_is_idempotent():
    module = fake_tool_agent()
    first = delegation.install(module)
    second = delegation.install(module)
    call(module)
    assert second == first
    assert module.calls[0]["code"].count(delegation.HEADER) == 1
    assert module._PYTHON_TOOL_DESCRIPTION.count(delegation.POLICY_BRIEF) == 1


def test_install_tells_the_model_the_policies_exist():
    module = fake_tool_agent()
    delegation.install(module)
    assert module._PYTHON_TOOL_DESCRIPTION.startswith(STOCK_DESCRIPTION)
    assert "auto_route" in module._PYTHON_TOOL_DESCRIPTION


def test_install_can_skip_the_description():
    module = fake_tool_agent()
    report = delegation.install(module, describe=False)
    assert report["described"] is False
    assert module._PYTHON_TOOL_DESCRIPTION == STOCK_DESCRIPTION


# --- the system prompt -----------------------------------------------------


def test_install_corrects_the_stale_timeout_claim():
    # A model told it has 30 seconds sizes its loops to fit 30 seconds, which
    # cancels the whole lever.
    module = fake_tool_agent()
    delegation.install(module, timeout_seconds=180)
    assert "30 seconds" not in module.COMPACT_TOOL_SESSION_ADDENDUM
    assert "180 seconds" in module.COMPACT_TOOL_SESSION_ADDENDUM


def test_install_points_the_search_advice_at_the_provided_one():
    module = fake_tool_agent()
    delegation.install(module)
    assert "auto_route" in module.PYTHON_ADDENDUM
    assert "write an explicit search algorithm" not in module.PYTHON_ADDENDUM


def test_install_lets_a_turn_carry_more_than_one_action():
    module = fake_tool_agent()
    delegation.install(module)
    assert "a turn spent on a single action is a turn wasted" in (
        module.GAME_OVERVIEW_ADDENDUM
    )


def test_install_reports_which_prompt_edits_took():
    module = fake_tool_agent()
    report = delegation.install(module)
    assert set(report["prompt"]) == {
        "COMPACT_TOOL_SESSION_ADDENDUM",
        "PYTHON_ADDENDUM",
        "GAME_OVERVIEW_ADDENDUM",
    }


def test_prompt_edits_survive_a_prompt_that_moved_on():
    # A miss must be reported, not raised: the run still works with the stock
    # advice, it just works less well.
    module = fake_tool_agent()
    module.PYTHON_ADDENDUM = "upstream rewrote this line"
    report = delegation.install(module)
    assert "PYTHON_ADDENDUM" not in report["prompt"]
    assert module.PYTHON_ADDENDUM == "upstream rewrote this line"


def test_prompt_edits_are_idempotent():
    module = fake_tool_agent()
    delegation.install(module)
    once = module.COMPACT_TOOL_SESSION_ADDENDUM
    delegation.apply_prompt_edits(module, 180)
    assert module.COMPACT_TOOL_SESSION_ADDENDUM == once


def test_prompt_replacements_carry_no_braces():
    # COMPACT_TOOL_SESSION_ADDENDUM is passed through str.format, so a stray
    # brace in a replacement would raise where the prompt is built.
    for _, _, new in delegation.prompt_edits(180):
        assert "{" not in new and "}" not in new


def test_edited_prompt_still_formats():
    module = fake_tool_agent()
    module.COMPACT_TOOL_SESSION_ADDENDUM = (
        "- Each `python` tool call has a hard time limit of 30 seconds.\n"
        "- Tool responses are capped to about {tool_output_tokens} tokens.\n"
    )
    delegation.install(module)
    formatted = module.COMPACT_TOOL_SESSION_ADDENDUM.format(tool_output_tokens=4096)
    assert "4096 tokens" in formatted
    assert "180 seconds" in formatted


# --- reading the run afterwards --------------------------------------------


def test_stats_count_actions_and_delegation():
    delegation.reset_stats()
    module = fake_tool_agent({"action_results": [{}] * 40, "stdout": "", "error": ""})
    delegation.install(module, report_every=0)
    call(module, code="result = auto_route(3, 4, deltas, start=(1, 1))")
    call(module, code="print(current_frame.ascii[:20])")
    assert delegation.STATS["snippets"] == 2
    assert delegation.STATS["actions"] == 80
    assert delegation.STATS["most_in_one_call"] == 40
    assert delegation.STATS["policy_snippets"] == 1
    assert delegation.STATS["calls"] == {"auto_route": 1}


def test_stats_do_not_credit_the_prelude_with_calling_policies():
    # The prelude defines every policy, so counting the prepended text would
    # make a single-action snippet look like full delegation.
    delegation.reset_stats()
    module = fake_tool_agent()
    delegation.install(module, report_every=0)
    call(module, code="action(['LEFT'])")
    assert delegation.STATS["policy_snippets"] == 0
    assert delegation.STATS["calls"] == {}


def test_stats_line_reports_the_delegated_share():
    delegation.reset_stats()
    module = fake_tool_agent()
    delegation.install(module, report_every=0)
    call(module, code="auto_sweep(budget=20)")
    call(module, code="action(['LEFT'])")
    line = delegation.stats_line()
    assert "snippets=2" in line
    assert "delegated=50%" in line


def test_broken_diagnostics_never_cost_a_run():
    delegation.reset_stats()
    module = fake_tool_agent()
    delegation.install(module, report_every=0)
    delegation.STATS.pop("snippets")
    assert call(module) == {"stdout": "", "error": ""}
    delegation.reset_stats()


def test_install_survives_a_module_without_the_hooks():
    # A harness that moved these names should cost the policies, not the run.
    report = delegation.install(types.ModuleType("bare"))
    assert report == {
        "sandbox": False,
        "described": False,
        "prelude_lines": 0,
        "prompt": [],
    }


def test_installed_snippet_runs_end_to_end():
    # The whole contract in one test: prelude plus the model's own code, run
    # under a fake action() the way the sandbox would.
    module = fake_tool_agent()
    delegation.install(module)
    call(module, code="result = auto_repeat('RIGHT', 3)")

    from test_executor import Frame, World, open_room

    world = World(open_room())
    namespace = world.sandbox()
    exec(compile(module.calls[0]["code"], "<python_tool>", "exec"), namespace)
    assert namespace["result"]["acted"] == 3
    assert len(world.log) == 3
