"""Put the policies inside the model's sandbox, and in front of the model.

executor.py is inert until two things happen: the source has to reach the
sandbox namespace, and the model has to know the functions are there. This is
both halves.

WHY THE SOURCE IS PREPENDED RATHER THAN INJECTED

The sandbox subprocess builds runtime_globals as a fresh dict holding only the
restricted builtins plus the state it refreshes; it does not inherit the
bootstrap module's namespace, which is why the model can reach segmentation
only through frame.segmentation and never as a function. So there is no host
side hook that adds a name. The single channel is the code string, exactly as
the bootstrap itself does with the segmentation source.

WHAT THAT COSTS, AND THE REPAIR

Prepending shifts every line number in the model's own snippet, and the sandbox
reports tracebacks as File "<python_tool>", line N. Left alone the model would
be told its error is hundreds of lines past the end of what it wrote. The
wrapper therefore subtracts the prelude length on the way back out. Failures
inside the prelude itself land at a non-positive line and are reported as
unknown, which still leaves the function name, and that is the useful half.

WHY THE TIMEOUT GOES UP

The stock 30 seconds is sized for a snippet that takes one action. A policy
takes hundreds, each one a round trip to the host, so the same ceiling would
kill the call mid-run. The actions already taken still count -- they were
executed host-side and recorded -- but the report is lost, and the model learns
nothing from a turn it paid for. Raising the ceiling trades a rarer, longer
stall for turns that finish.
"""
from __future__ import annotations

import inspect
import re
from typing import Any, Optional

from . import executor, sandbox_helpers

_FUTURE = re.compile(r"^from\s+__future__\s+import\s+.*$", re.MULTILINE)
_TRACEBACK = re.compile(r'(File "<python_tool>", line )(\d+)')

HEADER = "# --- policies available to this snippet ---"
DEFAULT_TIMEOUT_SECONDS = 180

# Set by the notebook builder. On Kaggle these modules are inlined as plain
# top-level source, so there is no module object for inspect.getsource to read
# and the prelude has to be handed over as text instead.
PRELUDE_OVERRIDE: Optional[str] = None

POLICY_BRIEF = (
    " IMPORTANT: prebuilt policies are already defined in this snippet's namespace, "
    "and each one runs MANY environment actions in a single call. Taking one action "
    "per snippet cannot finish a level inside the budget, so prefer these over "
    "calling action(...) step by step. "
    "learn_controls() probes each control once and returns "
    "{'deltas': {name: (drow, dcol)}, 'effective': [names that changed the "
    "board at all], 'position': (row, col)}. "
    "auto_route(row, col, deltas, blocked_chars, start=(row, col)) walks to a cell "
    "and stops early if the board contradicts the plan. "
    "auto_repeat(name, times) repeats one control until it stops changing anything. "
    "auto_click_all(char, limit) clicks every cell of that character, skipping HUD "
    "strips. auto_sweep(budget) cycles the controls and drops the ones that go inert; "
    "it is the last resort when nothing is understood yet, so keep its budget small. "
    "A level scores (human baseline / your actions) squared, so route deliberately "
    "rather than sweeping. "
    "Each returns a small dict with 'acted', 'stopped' and 'level' -- read 'stopped' "
    "and call again. Also defined: grid_from_ascii(ascii), "
    "moved_object(before_ascii, after_ascii), route(start, goal, deltas, passable) "
    "and hud_cells(before_ascii, after_ascii)."
)


POLICY_NAMES = (
    "learn_controls",
    "auto_route",
    "auto_repeat",
    "auto_click_all",
    "auto_sweep",
)

STATS = {
    "snippets": 0,
    "actions": 0,
    "policy_snippets": 0,
    "most_in_one_call": 0,
    "calls": {},
}


def reset_stats() -> None:
    STATS.update(
        snippets=0, actions=0, policy_snippets=0, most_in_one_call=0, calls={}
    )


def note(code: str, result: Any) -> None:
    """Record one snippet, so the run can be read afterwards.

    Without this a finished run cannot answer the only question that matters
    about the change: did the model actually delegate, or did it keep taking
    one action per turn. ``code`` must be the model's own snippet, before the
    prelude is prepended, or every snippet would look like it called every
    policy.
    """
    STATS["snippets"] += 1
    taken = 0
    if isinstance(result, dict):
        taken = len(result.get("action_results") or [])
    STATS["actions"] += taken
    if taken > STATS["most_in_one_call"]:
        STATS["most_in_one_call"] = taken

    used = [name for name in POLICY_NAMES if name + "(" in code]
    if used:
        STATS["policy_snippets"] += 1
    for name in used:
        STATS["calls"][name] = STATS["calls"].get(name, 0) + 1


def stats_line() -> str:
    share = 0
    if STATS["snippets"]:
        share = int(round(100.0 * STATS["policy_snippets"] / STATS["snippets"]))
    return (
        "[exec] snippets=%d actions=%d most_in_one_call=%d delegated=%d%% %s"
        % (
            STATS["snippets"],
            STATS["actions"],
            STATS["most_in_one_call"],
            share,
            STATS["calls"],
        )
    )


def prompt_edits(seconds: int) -> tuple:
    """Exact substitutions on the system prompt, as (constant, old, new).

    Three lines in the stock prompt work against a model that delegates.

    The first is simply false once the timeout is raised, and a model told it
    has 30 seconds will size its loops to fit 30 seconds.

    The second tells it to hand-write a BFS whenever the game is about
    navigating to a target. That is the right algorithm and the wrong advice:
    it is already written, tested and injected, and rewriting it every turn
    spends the tokens the policies exist to save.

    The third frames a turn around "the next best action or short sequence",
    which is the habit that costs the run. Nothing here loosens the pressure to
    use few in-game actions -- the score is (baseline / actions) squared and
    that stays the target. What changes is how many actions one turn may carry.

    No replacement may contain a brace: one of these constants is passed
    through str.format and a stray brace would raise there.
    """
    return (
        (
            "COMPACT_TOOL_SESSION_ADDENDUM",
            "- Each `python` tool call has a hard time limit of 30 seconds.\n",
            "- Each `python` tool call has a hard time limit of "
            + str(int(seconds))
            + " seconds, which is room for one call to run hundreds of "
            "environment actions.\n",
        ),
        (
            "PYTHON_ADDENDUM",
            "- IMPORTANT: Especially when the game is about making an agent navigate "
            "to a target, it is usually safer to write an explicit search algorithm "
            "such as BFS.",
            "- IMPORTANT: when the game is about making an agent navigate to a "
            "target, do not rewrite the search. Call auto_route, which runs a "
            "breadth-first search and then walks the whole path in one call, or "
            "route for the path alone.",
        ),
        (
            "GAME_OVERVIEW_ADDENDUM",
            "choose the next best action or short sequence against the goal as "
            "currently understood, execute it,",
            "choose the next best policy or action sequence against the goal as "
            "currently understood and execute it in one call -- a policy may run "
            "for hundreds of actions, and a turn spent on a single action is a "
            "turn wasted --",
        ),
    )


def apply_prompt_edits(tool_agent: Any, seconds: int) -> list:
    """Rewrite the prompt constants in place, reporting which ones took.

    A miss means the upstream prompt moved, which is worth seeing in the log
    rather than silently running with advice that contradicts the policies.
    """
    applied = []
    for name, old, new in prompt_edits(seconds):
        text = getattr(tool_agent, name, None)
        if not isinstance(text, str):
            continue
        if new in text:
            applied.append(name)
            continue
        if old not in text:
            continue
        setattr(tool_agent, name, text.replace(old, new, 1))
        applied.append(name)
    return applied


def prelude_source() -> str:
    """The source prepended to every snippet the model runs.

    Both __future__ lines are dropped: they are legal only at the top of the
    combined text, and a model that opens its own snippet with one would then
    be writing an illegal statement in the middle of a file.
    """
    if PRELUDE_OVERRIDE:
        return PRELUDE_OVERRIDE
    parts = [HEADER]
    for module in (sandbox_helpers, executor):
        parts.append(_FUTURE.sub("", inspect.getsource(module)).strip("\n"))
    return "\n".join(parts) + "\n"


def prelude_lines(source: Optional[str] = None) -> int:
    return (source if source is not None else prelude_source()).count("\n")


def remap_traceback(text: str, offset: int) -> str:
    """Shift reported line numbers back into the model's own snippet."""

    def shift(match: re.Match) -> str:
        line = int(match.group(2)) - offset
        return match.group(1) + (str(line) if line > 0 else "?")

    return _TRACEBACK.sub(shift, text)


def install(
    tool_agent: Any,
    *,
    timeout_seconds: Optional[int] = DEFAULT_TIMEOUT_SECONDS,
    describe: bool = True,
    report_every: int = 25,
) -> dict:
    """Patch a live tool_agent module so every snippet carries the policies.

    Returns what was actually changed rather than raising, because a failure
    here should cost the policies, not the run.
    """
    report = {"sandbox": False, "described": False, "prelude_lines": 0, "prompt": []}

    original = getattr(tool_agent, "run_sandboxed_python", None)
    if original is not None and getattr(original, "_delegation", False):
        report["sandbox"] = True
        report["prelude_lines"] = int(getattr(original, "_prelude_lines", 0))
    elif callable(original):
        prelude = prelude_source()
        offset = prelude_lines(prelude)

        def wrapped(**kwargs: Any) -> Any:
            written = str(kwargs.get("code", ""))
            kwargs["code"] = prelude + written
            if timeout_seconds:
                given = int(kwargs.get("timeout_seconds") or 0)
                kwargs["timeout_seconds"] = max(given, int(timeout_seconds))
            result = original(**kwargs)
            try:
                note(written, result)
                if report_every and STATS["snippets"] % int(report_every) == 0:
                    print(stats_line())
            except Exception:  # noqa: BLE001 - diagnostics never cost a run
                pass
            if not isinstance(result, dict):
                return result
            shifted = {}
            for key in ("error", "stdout"):
                value = result.get(key)
                if isinstance(value, str) and value:
                    shifted[key] = remap_traceback(value, offset)
            return {**result, **shifted} if shifted else result

        wrapped._delegation = True
        wrapped._prelude_lines = offset
        tool_agent.run_sandboxed_python = wrapped
        report["sandbox"] = True
        report["prelude_lines"] = offset

    description = getattr(tool_agent, "_PYTHON_TOOL_DESCRIPTION", "")
    if describe and isinstance(description, str) and description:
        if POLICY_BRIEF not in description:
            tool_agent._PYTHON_TOOL_DESCRIPTION = description + POLICY_BRIEF
        report["described"] = True
        report["prompt"] = apply_prompt_edits(
            tool_agent, timeout_seconds or DEFAULT_TIMEOUT_SECONDS
        )

    return report
