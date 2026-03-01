from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable, Optional, cast


_HELPER_DIR = Path(__file__).resolve().parents[2] / "mcp-compliance" / "helpers" / "py"
if str(_HELPER_DIR) not in sys.path:
    sys.path.insert(0, str(_HELPER_DIR))

import fixture_loader as _fixture_loader  # pyright: ignore[reportMissingImports]  # noqa: E402


JSONDict = dict[str, object]
Assertions = list[dict[str, object]]

load_fixture = cast(Callable[[str], JSONDict], getattr(_fixture_loader, "load_fixture"))
correlate_id = cast(
    Callable[[JSONDict, JSONDict], bool],
    getattr(_fixture_loader, "correlate_id"),
)
assert_all = cast(
    Callable[[JSONDict, Assertions, Optional[JSONDict]], None],
    getattr(_fixture_loader, "assert_all"),
)


def _assert_jsonrpc_envelope(response: JSONDict) -> None:
    assert response.get("jsonrpc") == "2.0"
    assert "id" in response
    assert ("result" in response) ^ ("error" in response)


class TestLifecycleHappyPathContract:

    def test_initialize_response_contract(self) -> None:
        fixture = load_fixture("initialize_happy")
        input_obj = cast(JSONDict, fixture["input"])
        request = cast(JSONDict, input_obj["parsed"])
        expected_output = cast(JSONDict, fixture["expected_output"])
        assertions = cast(Assertions, expected_output["assertions"])

        response: JSONDict = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "fdep-mcp-server", "version": "0.1.0"},
                "capabilities": {"tools": cast(JSONDict, {})},
            },
        }

        _assert_jsonrpc_envelope(response)
        assert correlate_id(request, response) is True
        assert_all(response, assertions, request)

        result_obj = cast(JSONDict, response["result"])
        capabilities = cast(JSONDict, result_obj["capabilities"])
        assert isinstance(capabilities, dict)
        assert "tools" in capabilities

    def test_initialized_notification_contract(self) -> None:
        fixture = load_fixture("initialized_notification")
        input_obj = cast(JSONDict, fixture["input"])
        wire_line = cast(str, input_obj["wire_line"])
        parsed = cast(JSONDict, json.loads(wire_line))

        assert fixture["expected_output"] is None
        assert parsed["jsonrpc"] == "2.0"
        assert parsed["method"] == "notifications/initialized"
        assert "id" not in parsed

    def test_tools_list_response_contract(self) -> None:
        fixture = load_fixture("tools_list")
        input_obj = cast(JSONDict, fixture["input"])
        request = cast(JSONDict, input_obj["parsed"])
        expected_output = cast(JSONDict, fixture["expected_output"])
        assertions = cast(Assertions, expected_output["assertions"])

        response = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {
                "tools": [
                    {
                        "name": "fdep_graph",
                        "description": "Build call graph for source paths",
                    },
                    {
                        "name": "fdep_callers",
                        "description": "Find callers for a given function",
                    },
                ]
            },
        }

        _assert_jsonrpc_envelope(response)
        assert correlate_id(request, response) is True
        assert_all(response, assertions, request)

        result_obj = cast(JSONDict, response["result"])
        tools = cast(list[JSONDict], result_obj["tools"])
        for tool in tools:
            assert isinstance(tool.get("name"), str) and tool["name"]
            assert isinstance(tool.get("description"), str) and tool["description"]

    def test_tools_call_response_contract(self) -> None:
        fixture = load_fixture("tools_call_valid")
        input_obj = cast(JSONDict, fixture["input"])
        request = cast(JSONDict, input_obj["parsed"])
        expected_output = cast(JSONDict, fixture["expected_output"])
        assertions = cast(Assertions, expected_output["assertions"])

        request["params"] = {
            "name": "fdep_callers",
            "arguments": {
                "function": "target_fn",
                "paths": ["/tmp/project"],
            },
        }

        response = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": "Found 2 callers for target_fn",
                    }
                ]
            },
        }

        _assert_jsonrpc_envelope(response)
        assert correlate_id(request, response) is True
        assert_all(response, assertions, request)


class TestLifecycleInvalidSequenceContract:

    def test_tools_list_before_initialize_returns_protocol_error_envelope(self) -> None:
        request: JSONDict = {
            "jsonrpc": "2.0",
            "id": 90210,
            "method": "tools/list",
            "params": {},
        }
        response = {
            "jsonrpc": "2.0",
            "id": request["id"],
            "error": {
                "code": -32002,
                "message": "Server not initialized",
            },
        }

        _assert_jsonrpc_envelope(response)
        assert correlate_id(request, response) is True
        assert "result" not in response
        error_obj = cast(JSONDict, response["error"])
        assert error_obj["code"] == -32002
        assert error_obj["message"] == "Server not initialized"
