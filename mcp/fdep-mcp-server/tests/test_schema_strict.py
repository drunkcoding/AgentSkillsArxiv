"""Schema strictness tests for fdep-mcp-server.

Validates the strict-reject policy from mcp-compliance/baseline-policy.json:

  unknown_fields.policy:  "strict-reject"
  invalid_params.policy:  "strict-reject"

The fdep server uses a custom dispatcher (FdepMcpServer) with explicit
_validate_no_unknown_keys calls at every level:

  - Top-level envelope keys
  - Per-method params (initialize, tools/list, tools/call)
  - Per-tool arguments (fdep_graph, fdep_callers, analyze_function_deps)

Unlike the MCP TypeScript SDK (which wraps validation errors as tool-level
results), the fdep dispatcher emits protocol-level errors (-32602) for
invalid/unknown params fields — including tool arguments.

Also verifies that tools/list descriptors include inputSchema with
additionalProperties: false, making the strict policy machine-readable.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Import FdepMcpServer
# ---------------------------------------------------------------------------
_SRC_DIR = Path(__file__).resolve().parents[1]
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from fdep_mcp.tools import (  # noqa: E402
    FdepMcpServer,
    INVALID_PARAMS,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

INVALID_PARAMS_CODE: int = INVALID_PARAMS  # -32602


def _make_server(initialized: bool = True) -> FdepMcpServer:
    """Return a fresh FdepMcpServer, optionally pre-initialized."""
    srv = FdepMcpServer()
    if initialized:
        srv.state.initialized = True
    return srv


def _send(server: FdepMcpServer, req: dict[str, Any]) -> dict[str, Any]:
    """Send a wire line and return the parsed response dict."""
    line = json.dumps(req) + "\n"
    resp_line = server.handle_wire_line(line)
    assert resp_line is not None, "Expected a response, got None (notification path?)"
    return json.loads(resp_line)


def _call_tool(
    server: FdepMcpServer,
    *,
    name: str,
    arguments: dict[str, Any],
    req_id: int = 1,
) -> dict[str, Any]:
    """Helper to send a tools/call request."""
    return _send(server, {
        "jsonrpc": "2.0",
        "id": req_id,
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
    })


def _tools_list(server: FdepMcpServer, req_id: int = 9) -> list[dict[str, Any]]:
    """Return the tools array from a tools/list response."""
    resp = _send(server, {"jsonrpc": "2.0", "id": req_id, "method": "tools/list", "params": {}})
    assert "error" not in resp, f"tools/list returned error: {resp}"
    return resp["result"]["tools"]


def _require_protocol_error(resp: dict[str, Any], expected_code: int) -> None:
    """Assert the response is a protocol-level error with the given code."""
    assert "error" in resp, f"Expected protocol error, got: {resp}"
    assert "result" not in resp, f"result must be absent in protocol error: {resp}"
    assert resp["error"]["code"] == expected_code, (
        f"Expected code {expected_code}, got {resp['error']['code']}"
    )


# ===========================================================================
# 1. tools/list: inputSchema descriptors reflect strict policy
# ===========================================================================


class TestToolsListInputSchema:
    """tools/list must expose inputSchema with additionalProperties: false."""

    def test_all_tools_have_input_schema(self) -> None:
        srv = _make_server()
        tools = _tools_list(srv)
        assert len(tools) > 0
        for tool in tools:
            assert "inputSchema" in tool, f"Tool {tool['name']} is missing inputSchema"

    def test_all_tool_schemas_have_additional_properties_false(self) -> None:
        srv = _make_server()
        tools = _tools_list(srv)
        for tool in tools:
            schema = tool["inputSchema"]
            assert schema.get("additionalProperties") is False, (
                f"Tool {tool['name']} inputSchema must have additionalProperties: false "
                f"(strict-reject policy); got {schema.get('additionalProperties')!r}"
            )

    def test_fdep_graph_required_fields(self) -> None:
        srv = _make_server()
        tools = _tools_list(srv)
        tool = next(t for t in tools if t["name"] == "fdep_graph")
        schema = tool["inputSchema"]
        assert schema["required"] == ["paths"]

    def test_fdep_callers_required_fields(self) -> None:
        srv = _make_server()
        tools = _tools_list(srv)
        tool = next(t for t in tools if t["name"] == "fdep_callers")
        schema = tool["inputSchema"]
        assert set(schema["required"]) == {"function", "paths"}

    def test_analyze_function_deps_required_fields(self) -> None:
        srv = _make_server()
        tools = _tools_list(srv)
        tool = next(t for t in tools if t["name"] == "analyze_function_deps")
        schema = tool["inputSchema"]
        assert schema["required"] == ["file"]

    def test_input_schema_type_is_object(self) -> None:
        srv = _make_server()
        tools = _tools_list(srv)
        for tool in tools:
            assert tool["inputSchema"]["type"] == "object", (
                f"Tool {tool['name']} inputSchema.type must be 'object'"
            )


# ===========================================================================
# 2. fdep_graph: strict argument validation
# ===========================================================================


class TestFdepGraphStrictness:
    """fdep_graph rejects unknown/missing argument fields with -32602."""

    def test_accepts_valid_arguments(self) -> None:
        srv = _make_server()
        # Use a real existing path so no tool-level error fires.
        import tempfile  # noqa: E401
        with tempfile.TemporaryDirectory() as td:
            resp = _call_tool(srv, name="fdep_graph", arguments={"paths": [td]})
        assert "error" not in resp
        assert resp["result"].get("isError") is not True

    def test_rejects_unknown_argument_field(self) -> None:
        srv = _make_server()
        resp = _call_tool(
            srv,
            name="fdep_graph",
            arguments={"paths": ["."], "UNKNOWN": "value"},
        )
        _require_protocol_error(resp, INVALID_PARAMS_CODE)

    def test_rejects_missing_required_paths(self) -> None:
        srv = _make_server()
        resp = _call_tool(srv, name="fdep_graph", arguments={})
        _require_protocol_error(resp, INVALID_PARAMS_CODE)

    def test_rejects_paths_wrong_type(self) -> None:
        srv = _make_server()
        resp = _call_tool(srv, name="fdep_graph", arguments={"paths": "not-a-list"})
        _require_protocol_error(resp, INVALID_PARAMS_CODE)

    def test_id_is_preserved_in_error(self) -> None:
        srv = _make_server()
        resp = _call_tool(
            srv,
            name="fdep_graph",
            arguments={"paths": ["."], "extra": "x"},
            req_id=42,
        )
        _require_protocol_error(resp, INVALID_PARAMS_CODE)
        assert resp["id"] == 42


# ===========================================================================
# 3. fdep_callers: strict argument validation
# ===========================================================================


class TestFdepCallersStrictness:
    """fdep_callers rejects unknown/missing argument fields with -32602."""

    def test_rejects_unknown_argument_field(self) -> None:
        srv = _make_server()
        resp = _call_tool(
            srv,
            name="fdep_callers",
            arguments={"function": "foo", "paths": ["."], "bogus": True},
        )
        _require_protocol_error(resp, INVALID_PARAMS_CODE)

    def test_rejects_missing_required_function(self) -> None:
        srv = _make_server()
        resp = _call_tool(
            srv,
            name="fdep_callers",
            arguments={"paths": ["."]},
        )
        _require_protocol_error(resp, INVALID_PARAMS_CODE)

    def test_rejects_missing_required_paths(self) -> None:
        srv = _make_server()
        resp = _call_tool(
            srv,
            name="fdep_callers",
            arguments={"function": "foo"},
        )
        _require_protocol_error(resp, INVALID_PARAMS_CODE)

    def test_rejects_empty_function_string(self) -> None:
        srv = _make_server()
        resp = _call_tool(
            srv,
            name="fdep_callers",
            arguments={"function": "", "paths": ["."]},
        )
        _require_protocol_error(resp, INVALID_PARAMS_CODE)


# ===========================================================================
# 4. analyze_function_deps: strict argument validation
# ===========================================================================


class TestAnalyzeFunctionDepsStrictness:
    """analyze_function_deps rejects unknown/missing argument fields with -32602."""

    def test_rejects_unknown_argument_field(self) -> None:
        srv = _make_server()
        resp = _call_tool(
            srv,
            name="analyze_function_deps",
            arguments={"file": "x.py", "verbose": True},
        )
        _require_protocol_error(resp, INVALID_PARAMS_CODE)

    def test_rejects_missing_required_file(self) -> None:
        srv = _make_server()
        resp = _call_tool(srv, name="analyze_function_deps", arguments={})
        _require_protocol_error(resp, INVALID_PARAMS_CODE)

    def test_rejects_empty_file_string(self) -> None:
        srv = _make_server()
        resp = _call_tool(srv, name="analyze_function_deps", arguments={"file": ""})
        _require_protocol_error(resp, INVALID_PARAMS_CODE)

    def test_id_is_preserved_in_error(self) -> None:
        srv = _make_server()
        resp = _call_tool(
            srv,
            name="analyze_function_deps",
            arguments={"file": "x.py", "extra": "y"},
            req_id=77,
        )
        _require_protocol_error(resp, INVALID_PARAMS_CODE)
        assert resp["id"] == 77


# ===========================================================================
# 5. tools/call params-level strictness (unknown fields in params itself)
# ===========================================================================


class TestToolsCallParamsStrictness:
    """tools/call params must not contain unknown fields (only name/arguments)."""

    def test_rejects_unknown_field_in_tools_call_params(self) -> None:
        srv = _make_server()
        resp = _send(srv, {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "fdep_graph",
                "arguments": {"paths": ["."]},
                "unexpected": "field",
            },
        })
        _require_protocol_error(resp, INVALID_PARAMS_CODE)

    def test_accepts_valid_tools_call_params(self) -> None:
        """tools/call with only name + arguments must not produce a param error."""
        import tempfile  # noqa: E401
        srv = _make_server()
        with tempfile.TemporaryDirectory() as td:
            resp = _send(srv, {
                "jsonrpc": "2.0",
                "id": 6,
                "method": "tools/call",
                "params": {"name": "fdep_graph", "arguments": {"paths": [td]}},
            })
        # No protocol error; might be tool success or tool error but not param error
        assert "error" not in resp or resp["error"]["code"] != INVALID_PARAMS_CODE


# ===========================================================================
# 6. Behavioral difference: fdep emits protocol errors, not tool errors
# ===========================================================================


class TestFdepProtocolErrorShape:
    """
    Unlike ast-grep (SDK) which wraps validation errors as result.isError=true,
    fdep emits top-level protocol errors for invalid tool arguments.
    Both are strict-reject, but the error-shape layer differs.
    """

    def test_invalid_tool_args_produce_protocol_error_not_tool_error(self) -> None:
        """Invalid fdep tool args must use error.code, NOT result.isError=true."""
        srv = _make_server()
        resp = _call_tool(
            srv,
            name="fdep_graph",
            arguments={"paths": ["."], "extra": "forbidden"},
        )
        # Must have top-level error (protocol error shape)
        assert "error" in resp, "fdep must emit protocol-level error for invalid args"
        # Must NOT use the tool-error result shape
        assert "result" not in resp, "result must be absent in a protocol error"
        assert resp["error"]["code"] == INVALID_PARAMS_CODE

    def test_valid_tool_args_do_not_produce_protocol_error(self) -> None:
        """Valid fdep tool args must not produce a protocol error."""
        import tempfile  # noqa: E401
        srv = _make_server()
        with tempfile.TemporaryDirectory() as td:
            resp = _call_tool(srv, name="fdep_graph", arguments={"paths": [td]})
        assert "error" not in resp, f"Valid call must not produce protocol error: {resp}"
