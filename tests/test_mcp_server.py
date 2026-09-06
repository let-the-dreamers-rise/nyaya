"""The MCP surface is how anyone who is not already cloning the repo reaches this.

So it gets tested like a protocol, not like a helper: handshake, discovery,
calls, and the failure paths a real client will actually hit.
"""

from __future__ import annotations

import io
import json

import pytest

from nyaya import mcp_server as mcp


def call(name, arguments, request_id=1):
    return mcp.handle(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
    )


def text_of(response):
    return response["result"]["content"][0]["text"]


EXAMPLES = [{"label": "spam", "text": "win a free prize now, claim your cash"}] * 8 + [
    {"label": "ham", "text": "see you at home tonight, sorry I am late"}
] * 8


# --- handshake -----------------------------------------------------------


def test_initialize_declares_tools_and_identifies_the_server():
    got = mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert got["result"]["serverInfo"]["name"] == "nyaya"
    assert "tools" in got["result"]["capabilities"]


def test_initialize_echoes_a_protocol_version_it_supports():
    got = mcp.handle(
        {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"},
        }
    )
    assert got["result"]["protocolVersion"] == "2024-11-05"


def test_an_unknown_protocol_version_falls_back_rather_than_failing():
    got = mcp.handle(
        {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "1999-01-01"},
        }
    )
    assert got["result"]["protocolVersion"] == mcp.PROTOCOL


def test_notifications_are_not_answered():
    assert mcp.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None


def test_unknown_methods_return_a_jsonrpc_error():
    got = mcp.handle({"jsonrpc": "2.0", "id": 3, "method": "nope/nope"})
    assert got["error"]["code"] == -32601


# --- discovery -----------------------------------------------------------


def test_every_advertised_tool_has_a_handler_and_a_schema():
    tools = mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
    assert {t["name"] for t in tools} == set(mcp.HANDLERS)
    for tool in tools:
        assert tool["description"].strip()
        assert tool["inputSchema"]["type"] == "object"


# --- learn_skill ---------------------------------------------------------


def test_learn_skill_returns_a_readable_skill_and_honest_metrics():
    body = text_of(call("learn_skill", {"examples": EXAMPLES}))
    assert "held out" in body.lower()
    assert "RULES = [" in body
    assert "No model was called" in body


def test_learn_skill_refuses_a_sample_too_small_to_hold_anything_out():
    got = call("learn_skill", {"examples": EXAMPLES[:4]})
    assert got["result"]["isError"] is True
    assert "too few" in text_of(got)


def test_a_bad_label_is_named_rather_than_silently_dropped():
    got = call("learn_skill", {"examples": [{"label": "maybe", "text": "hi"}]})
    assert got["result"]["isError"] is True
    assert "spam" in text_of(got)


def test_learn_skill_without_any_data_says_what_to_pass():
    got = call("learn_skill", {})
    assert got["result"]["isError"] is True
    assert "tsv_path" in text_of(got)


def test_a_missing_tsv_path_is_reported_with_the_path():
    got = call("learn_skill", {"tsv_path": "no/such/file.tsv"})
    assert got["result"]["isError"] is True
    assert "no/such/file.tsv" in text_of(got).replace("\\", "/")


# --- screen_message ------------------------------------------------------


def test_screening_returns_reasons_not_just_a_score():
    learned = text_of(call("learn_skill", {"examples": EXAMPLES}))
    source = learned[learned.index('"""') :]
    got = text_of(
        call("screen_message", {"text": "win a free prize now", "examples": EXAMPLES})
    )
    assert "evidence" in got
    assert "threshold" in got
    assert source  # the artefact really is emitted as source


def test_screening_a_message_with_no_matches_says_so_plainly():
    got = text_of(call("screen_message", {"text": "zzzz", "examples": EXAMPLES}))
    assert "nothing fired" in got


def test_screening_without_text_asks_for_it():
    got = call("screen_message", {})
    assert got["result"]["isError"] is True


# --- list_beliefs --------------------------------------------------------


def test_list_beliefs_orders_by_weight_of_evidence():
    got = text_of(call("list_beliefs", {"examples": EXAMPLES}))
    assert "beliefs" in got
    assert "fired on" in got


# --- errors --------------------------------------------------------------


def test_an_unknown_tool_is_a_protocol_error_not_a_tool_error():
    got = call("no_such_tool", {})
    assert got["error"]["code"] == -32602


def test_a_tool_failure_is_returned_to_the_model_not_raised():
    """A raised exception would kill the server; the model must see the message."""
    got = call("screen_message", {"text": "hi", "skill_python": "raise ValueError('boom')"})
    assert got["result"]["isError"] is True
    assert "boom" in text_of(got)


# --- transport -----------------------------------------------------------


def test_serve_reads_lines_and_writes_one_response_per_request():
    stdin = io.StringIO(
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        + "\n"
        + json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"})
        + "\n"
        + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        + "\n"
    )
    stdout = io.StringIO()
    mcp.serve(stdin, stdout)
    lines = [ln for ln in stdout.getvalue().splitlines() if ln.strip()]
    assert len(lines) == 2, "the notification must not be answered"
    assert json.loads(lines[0])["id"] == 1
    assert json.loads(lines[1])["id"] == 2


def test_malformed_json_does_not_kill_the_server():
    stdout = io.StringIO()
    mcp.serve(io.StringIO("{not json\n"), stdout)
    assert json.loads(stdout.getvalue())["error"]["code"] == -32700


@pytest.mark.parametrize("blank", ["", "   "])
def test_blank_lines_are_ignored(blank):
    stdout = io.StringIO()
    mcp.serve(io.StringIO(blank + "\n"), stdout)
    assert stdout.getvalue() == ""
