"""Negative-path protocol/error-shape tests for fdep-mcp-server.

This suite encodes the expected error-shape policy explicitly, drawn from
mcp-compliance/baseline-policy.json.  All tests use synthetic (constructed)
JSON-RPC responses verified through the shared assertion helpers — no live
server is required.

Categories covered
------------------
1. Malformed JSON          -> Parse Error      (code -32700)
2. Invalid envelope        -> Invalid Request  (code -32600)
3. Unknown method          -> Method Not Found (code -32601)
4. Invalid params/schema   -> Invalid Params   (code -32602)
5. Tool failure branch     -> isError=true in result (NOT a protocol error)

Key invariants
--------------
* Protocol errors  -> top-level "error" key with JSON-RPC error code; no "result" key.
* Tool errors      -> top-level "result" key with isError=true; no "error" key.
* These two shapes are MUTUALLY EXCLUSIVE and must never be confused.

Source references
-----------------
* mcp-compliance/baseline-policy.json -> error_boundary (protocol vs tool errors)
* mcp-compliance/baseline-policy.json -> strictness_matrix (invalid_params, tool_errors)
* mcp-compliance/fixtures/scenarios/malformed_json.json    (code -32700)
* mcp-compliance/fixtures/scenarios/invalid_envelope.json  (code -32600)
* mcp-compliance/fixtures/scenarios/unknown_method.json    (code -32601)
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Shared fixture-loader import
# ---------------------------------------------------------------------------

_HELPER_DIR = (
    Path(__file__).resolve().parents[2] / "mcp-compliance" / "helpers" / "py"
)
if str(_HELPER_DIR) not in sys.path:
    sys.path.insert(0, str(_HELPER_DIR))

from fixture_loader import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    load_fixture,
    build_stdio_line,
    parse_stdio_line,
    evaluate_assertions,
    assert_all,
)

# ---------------------------------------------------------------------------
# Baseline-derived error-code constants
# (Source: JSON-RPC 2.0 spec §5.1; referenced in baseline-policy.json)
# ---------------------------------------------------------------------------

PARSE_ERROR: int = -32700       # Input is not valid JSON at all
INVALID_REQUEST: int = -32600   # Valid JSON but not a valid JSON-RPC 2.0 Request
METHOD_NOT_FOUND: int = -32601  # Method does not exist / not available
INVALID_PARAMS: int = -32602    # Invalid method params (missing required, wrong type)

# ---------------------------------------------------------------------------
# Inline assertion lists for categories without a shared fixture
# (same declarative format used by the fixture JSON files)
# ---------------------------------------------------------------------------

#: Policy assertions for an Invalid Params (-32602) error where request ID is known.
_INVALID_PARAMS_ASSERTIONS: list[dict[str, Any]] = [
    {"path": "jsonrpc", "op": "eq", "value": "2.0"},
    {"path": "id", "op": "eq_input_id"},
    {"path": "error", "op": "exists"},
    {"path": "error.code", "op": "eq", "value": INVALID_PARAMS},
    {"path": "error.message", "op": "exists"},
    {"path": "result", "op": "not_exists"},
]

#: Policy assertions for a tool-failure result (isError=true).
#: Critically, the top-level "error" key must be ABSENT — tool errors are
#: not protocol errors (baseline-policy.json: error_boundary.tool_errors).
_TOOL_FAILURE_ASSERTIONS: list[dict[str, Any]] = [
    {"path": "jsonrpc", "op": "eq", "value": "2.0"},
    {"path": "id", "op": "eq_input_id"},
    {"path": "result", "op": "exists"},
    {"path": "result.isError", "op": "eq", "value": True},
    {"path": "result.content", "op": "exists"},
    {"path": "result.content", "op": "typeof", "value": "array"},
    {"path": "error", "op": "not_exists"},   # MUST be absent: not a protocol error
]


# ===========================================================================
# 1. Malformed JSON  ->  Parse Error (-32700)
# ===========================================================================


class TestMalformedJsonErrorShape:
    """Protocol policy: unparseable wire lines must yield a -32700 Parse Error."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _conforming(self, id_value: Any = None) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": id_value,
            "error": {"code": PARSE_ERROR, "message": "Parse error"},
        }

    # ------------------------------------------------------------------
    # Conforming responses — must pass fixture assertions
    # ------------------------------------------------------------------

    def test_conforming_parse_error_passes_fixture_assertions(self) -> None:
        """Well-formed -32700 response satisfies every fixture assertion."""
        fixture = load_fixture("malformed_json")
        assert_all(self._conforming(), fixture["expected_output"]["assertions"])

    def test_parse_error_code_is_minus_32700(self) -> None:
        results = evaluate_assertions(
            self._conforming(),
            [{"path": "error.code", "op": "eq", "value": PARSE_ERROR}],
        )
        assert results[0]["passed"] is True

    def test_parse_error_response_has_no_result_key(self) -> None:
        results = evaluate_assertions(
            self._conforming(),
            [{"path": "result", "op": "not_exists"}],
        )
        assert results[0]["passed"] is True

    def test_parse_error_has_message_field(self) -> None:
        results = evaluate_assertions(
            self._conforming(),
            [{"path": "error.message", "op": "exists"}],
        )
        assert results[0]["passed"] is True

    def test_parse_error_id_may_be_null(self) -> None:
        """id_correlation=may_be_null: null response id is acceptable."""
        fixture = load_fixture("malformed_json")
        assert fixture["expected_output"]["id_correlation"] == "may_be_null"
        # null id must still satisfy all fixture assertions
        assert_all(self._conforming(id_value=None), fixture["expected_output"]["assertions"])

    # ------------------------------------------------------------------
    # Non-conforming responses — must FAIL specific assertions
    # ------------------------------------------------------------------

    def test_wrong_error_code_fails_error_code_assertion(self) -> None:
        """Using -32600 instead of -32700 must fail the error.code assertion."""
        fixture = load_fixture("malformed_json")
        wrong = {"jsonrpc": "2.0", "id": None, "error": {"code": INVALID_REQUEST, "message": "x"}}
        results = evaluate_assertions(wrong, fixture["expected_output"]["assertions"])
        failed_paths = {r["assertion"]["path"] for r in results if not r["passed"]}
        assert "error.code" in failed_paths, (
            "error.code assertion must fail when the code is not -32700"
        )

    def test_result_key_present_violates_not_exists_assertion(self) -> None:
        fixture = load_fixture("malformed_json")
        wrong = {
            "jsonrpc": "2.0",
            "id": None,
            "result": {},
            "error": {"code": PARSE_ERROR, "message": "Parse error"},
        }
        results = evaluate_assertions(wrong, fixture["expected_output"]["assertions"])
        failed = [
            r for r in results
            if not r["passed"]
            and r["assertion"]["path"] == "result"
            and r["assertion"]["op"] == "not_exists"
        ]
        assert len(failed) == 1, "result not_exists assertion must fail when 'result' key is present"

    def test_missing_error_key_fails_exists_assertion(self) -> None:
        fixture = load_fixture("malformed_json")
        wrong = {"jsonrpc": "2.0", "id": None}   # no "error" key
        results = evaluate_assertions(wrong, fixture["expected_output"]["assertions"])
        failed_paths = {r["assertion"]["path"] for r in results if not r["passed"]}
        assert "error" in failed_paths


# ===========================================================================
# 2. Invalid JSON-RPC Envelope  ->  Invalid Request (-32600)
# ===========================================================================


class TestInvalidEnvelopeErrorShape:
    """Protocol policy: valid JSON but missing jsonrpc/id fields -> -32600."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _conforming(self, id_value: Any = None) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": id_value,
            "error": {"code": INVALID_REQUEST, "message": "Invalid Request"},
        }

    # ------------------------------------------------------------------
    # Conforming responses — must pass fixture assertions
    # ------------------------------------------------------------------

    def test_conforming_invalid_request_passes_fixture_assertions(self) -> None:
        fixture = load_fixture("invalid_envelope")
        assert_all(self._conforming(), fixture["expected_output"]["assertions"])

    def test_invalid_request_code_is_minus_32600(self) -> None:
        results = evaluate_assertions(
            self._conforming(),
            [{"path": "error.code", "op": "eq", "value": INVALID_REQUEST}],
        )
        assert results[0]["passed"] is True

    def test_invalid_request_response_has_no_result_key(self) -> None:
        results = evaluate_assertions(
            self._conforming(),
            [{"path": "result", "op": "not_exists"}],
        )
        assert results[0]["passed"] is True

    def test_invalid_request_has_message_field(self) -> None:
        results = evaluate_assertions(
            self._conforming(),
            [{"path": "error.message", "op": "exists"}],
        )
        assert results[0]["passed"] is True

    def test_invalid_envelope_id_may_be_null(self) -> None:
        """id_correlation=may_be_null: null response id is acceptable."""
        fixture = load_fixture("invalid_envelope")
        assert fixture["expected_output"]["id_correlation"] == "may_be_null"

    # ------------------------------------------------------------------
    # Non-conforming responses — must FAIL specific assertions
    # ------------------------------------------------------------------

    def test_wrong_error_code_fails_assertion(self) -> None:
        fixture = load_fixture("invalid_envelope")
        wrong = {"jsonrpc": "2.0", "id": None, "error": {"code": PARSE_ERROR, "message": "x"}}
        results = evaluate_assertions(wrong, fixture["expected_output"]["assertions"])
        failed_paths = {r["assertion"]["path"] for r in results if not r["passed"]}
        assert "error.code" in failed_paths

    def test_missing_error_key_fails_assertion(self) -> None:
        fixture = load_fixture("invalid_envelope")
        wrong = {"jsonrpc": "2.0", "id": None, "result": {}}
        results = evaluate_assertions(wrong, fixture["expected_output"]["assertions"])
        failed_paths = {r["assertion"]["path"] for r in results if not r["passed"]}
        assert "error" in failed_paths

    def test_result_key_present_fails_assertion(self) -> None:
        fixture = load_fixture("invalid_envelope")
        wrong = {
            "jsonrpc": "2.0",
            "id": None,
            "result": {},
            "error": {"code": INVALID_REQUEST, "message": "x"},
        }
        results = evaluate_assertions(wrong, fixture["expected_output"]["assertions"])
        failed_paths = {r["assertion"]["path"] for r in results if not r["passed"]}
        assert "result" in failed_paths


# ===========================================================================
# 3. Unknown Method  ->  Method Not Found (-32601)
# ===========================================================================


class TestUnknownMethodErrorShape:
    """Protocol policy: unregistered method in valid envelope -> -32601."""

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _input_request(self, req_id: int = 5) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "nonexistent/method",
            "params": {},
        }

    def _conforming(self, req_id: int = 5) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": METHOD_NOT_FOUND, "message": "Method not found"},
        }

    # ------------------------------------------------------------------
    # Conforming responses — must pass fixture assertions
    # ------------------------------------------------------------------

    def test_conforming_method_not_found_passes_fixture_assertions(self) -> None:
        fixture = load_fixture("unknown_method")
        input_parsed = fixture["input"]["parsed"]
        resp = self._conforming(req_id=input_parsed["id"])
        assert_all(
            resp,
            fixture["expected_output"]["assertions"],
            input_request=input_parsed,
        )

    def test_method_not_found_code_is_minus_32601(self) -> None:
        results = evaluate_assertions(
            self._conforming(),
            [{"path": "error.code", "op": "eq", "value": METHOD_NOT_FOUND}],
        )
        assert results[0]["passed"] is True

    def test_method_not_found_has_no_result_key(self) -> None:
        results = evaluate_assertions(
            self._conforming(),
            [{"path": "result", "op": "not_exists"}],
        )
        assert results[0]["passed"] is True

    def test_method_not_found_has_message_field(self) -> None:
        results = evaluate_assertions(
            self._conforming(),
            [{"path": "error.message", "op": "exists"}],
        )
        assert results[0]["passed"] is True

    def test_unknown_method_id_correlation_must_match_input(self) -> None:
        """id_correlation=must_match_input_id: response id echoes request id."""
        fixture = load_fixture("unknown_method")
        assert fixture["expected_output"]["id_correlation"] == "must_match_input_id"

    def test_id_correlation_passes_when_ids_match(self) -> None:
        req = self._input_request(req_id=99)
        resp = self._conforming(req_id=99)
        results = evaluate_assertions(
            resp,
            [{"path": "id", "op": "eq_input_id"}],
            input_request=req,
        )
        assert results[0]["passed"] is True

    def test_id_correlation_fails_when_ids_mismatch(self) -> None:
        req = self._input_request(req_id=99)
        resp = self._conforming(req_id=42)   # deliberately wrong id
        results = evaluate_assertions(
            resp,
            [{"path": "id", "op": "eq_input_id"}],
            input_request=req,
        )
        assert results[0]["passed"] is False

    # ------------------------------------------------------------------
    # Non-conforming responses — must FAIL specific assertions
    # ------------------------------------------------------------------

    def test_wrong_error_code_fails_assertion(self) -> None:
        fixture = load_fixture("unknown_method")
        input_parsed = fixture["input"]["parsed"]
        wrong = {
            "jsonrpc": "2.0",
            "id": input_parsed["id"],
            "error": {"code": INVALID_REQUEST, "message": "wrong code"},
        }
        results = evaluate_assertions(
            wrong,
            fixture["expected_output"]["assertions"],
            input_request=input_parsed,
        )
        failed_paths = {r["assertion"]["path"] for r in results if not r["passed"]}
        assert "error.code" in failed_paths

    def test_mismatched_id_fails_eq_input_id_assertion(self) -> None:
        fixture = load_fixture("unknown_method")
        input_parsed = fixture["input"]["parsed"]
        wrong_id = input_parsed["id"] + 100
        resp = self._conforming(req_id=wrong_id)
        results = evaluate_assertions(
            resp,
            fixture["expected_output"]["assertions"],
            input_request=input_parsed,
        )
        failed_paths = {r["assertion"]["path"] for r in results if not r["passed"]}
        assert "id" in failed_paths


# ===========================================================================
# 4. Invalid Params/Schema  ->  Invalid Params (-32602)
# ===========================================================================


class TestInvalidParamsErrorShape:
    """Protocol policy: invalid/missing required params -> -32602.

    There is no shared fixture file for this code; assertions are defined
    inline from the baseline policy (strictness_matrix.invalid_params).
    """

    _INPUT_REQUEST: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": 8,
        "method": "tools/call",
        "params": {},   # missing required 'name' field
    }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _conforming(self) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": 8,
            "error": {
                "code": INVALID_PARAMS,
                "message": "Invalid params: missing required field 'name'",
            },
        }

    # ------------------------------------------------------------------
    # Conforming responses — must pass inline policy assertions
    # ------------------------------------------------------------------

    def test_conforming_invalid_params_passes_all_assertions(self) -> None:
        assert_all(
            self._conforming(),
            _INVALID_PARAMS_ASSERTIONS,
            input_request=self._INPUT_REQUEST,
        )

    def test_invalid_params_code_is_minus_32602(self) -> None:
        results = evaluate_assertions(
            self._conforming(),
            [{"path": "error.code", "op": "eq", "value": INVALID_PARAMS}],
        )
        assert results[0]["passed"] is True

    def test_invalid_params_has_message_field(self) -> None:
        results = evaluate_assertions(
            self._conforming(),
            [{"path": "error.message", "op": "exists"}],
        )
        assert results[0]["passed"] is True

    def test_invalid_params_response_has_no_result_key(self) -> None:
        results = evaluate_assertions(
            self._conforming(),
            [{"path": "result", "op": "not_exists"}],
        )
        assert results[0]["passed"] is True

    def test_invalid_params_id_echoes_request_id(self) -> None:
        results = evaluate_assertions(
            self._conforming(),
            [{"path": "id", "op": "eq_input_id"}],
            input_request=self._INPUT_REQUEST,
        )
        assert results[0]["passed"] is True

    # ------------------------------------------------------------------
    # Non-conforming responses — must FAIL specific assertions
    # ------------------------------------------------------------------

    def test_wrong_error_code_fails_assertion(self) -> None:
        wrong = {
            "jsonrpc": "2.0",
            "id": 8,
            "error": {"code": METHOD_NOT_FOUND, "message": "wrong"},
        }
        results = evaluate_assertions(
            wrong,
            _INVALID_PARAMS_ASSERTIONS,
            input_request=self._INPUT_REQUEST,
        )
        failed_paths = {r["assertion"]["path"] for r in results if not r["passed"]}
        assert "error.code" in failed_paths

    def test_result_key_present_fails_assertion(self) -> None:
        wrong = {
            "jsonrpc": "2.0",
            "id": 8,
            "result": {},
            "error": {"code": INVALID_PARAMS, "message": "..."},
        }
        results = evaluate_assertions(
            wrong,
            _INVALID_PARAMS_ASSERTIONS,
            input_request=self._INPUT_REQUEST,
        )
        failed_paths = {r["assertion"]["path"] for r in results if not r["passed"]}
        assert "result" in failed_paths

    def test_wrong_id_in_response_fails_assertion(self) -> None:
        wrong = {
            "jsonrpc": "2.0",
            "id": 999,   # does not match input id=8
            "error": {"code": INVALID_PARAMS, "message": "..."},
        }
        results = evaluate_assertions(
            wrong,
            _INVALID_PARAMS_ASSERTIONS,
            input_request=self._INPUT_REQUEST,
        )
        failed_paths = {r["assertion"]["path"] for r in results if not r["passed"]}
        assert "id" in failed_paths


# ===========================================================================
# 5. Tool Failure Branch  ->  isError=true in result (NOT a protocol error)
# ===========================================================================


class TestToolFailureErrorShape:
    """Policy (baseline error_boundary.tool_errors):

    Tool runtime errors must be reported via result.isError=true, NOT as a
    top-level JSON-RPC protocol error.  The "must_not_be_reported_as_protocol_error"
    flag in baseline-policy.json is the source for this invariant.
    """

    _INPUT_REQUEST: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": 9,
        "method": "tools/call",
        "params": {
            "name": "analyze_function_deps",
            "arguments": {"file": "/nonexistent/path.py"},
        },
    }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _conforming_tool_failure(self) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "id": 9,
            "result": {
                "isError": True,
                "content": [
                    {"type": "text", "text": "Error: file '/nonexistent/path.py' not found"}
                ],
            },
        }

    def _tool_failure_as_protocol_error(self) -> dict[str, Any]:
        """Incorrectly shapes a tool failure as a top-level protocol error."""
        return {
            "jsonrpc": "2.0",
            "id": 9,
            "error": {
                "code": -32000,   # implementation-defined server error
                "message": "Tool execution failed",
            },
        }

    # ------------------------------------------------------------------
    # Conforming tool-failure responses — must pass tool-shape assertions
    # ------------------------------------------------------------------

    def test_conforming_tool_failure_passes_all_assertions(self) -> None:
        assert_all(
            self._conforming_tool_failure(),
            _TOOL_FAILURE_ASSERTIONS,
            input_request=self._INPUT_REQUEST,
        )

    def test_tool_failure_has_is_error_true(self) -> None:
        results = evaluate_assertions(
            self._conforming_tool_failure(),
            [{"path": "result.isError", "op": "eq", "value": True}],
        )
        assert results[0]["passed"] is True

    def test_tool_failure_content_is_array(self) -> None:
        results = evaluate_assertions(
            self._conforming_tool_failure(),
            [
                {"path": "result.content", "op": "exists"},
                {"path": "result.content", "op": "typeof", "value": "array"},
            ],
        )
        assert all(r["passed"] for r in results)

    def test_tool_failure_has_no_top_level_error_key(self) -> None:
        """Core invariant: tool errors must NOT use protocol-level error shape.

        Source: baseline-policy.json -> error_boundary.tool_errors.must_not_be_reported_as_protocol_error
        """
        results = evaluate_assertions(
            self._conforming_tool_failure(),
            [{"path": "error", "op": "not_exists"}],
        )
        assert results[0]["passed"] is True, (
            "A tool failure must not set a top-level 'error' key; "
            "that shape is reserved exclusively for protocol errors."
        )

    def test_tool_failure_preserves_valid_protocol_framing(self) -> None:
        """Protocol envelope (jsonrpc version + id correlation) must remain valid."""
        assert_all(
            self._conforming_tool_failure(),
            [
                {"path": "jsonrpc", "op": "eq", "value": "2.0"},
                {"path": "id", "op": "eq_input_id"},
            ],
            input_request=self._INPUT_REQUEST,
        )

    # ------------------------------------------------------------------
    # Non-conforming: tool failure reported as protocol error — must FAIL
    # ------------------------------------------------------------------

    def test_tool_error_as_protocol_error_fails_multiple_tool_assertions(self) -> None:
        """A tool failure misreported via top-level 'error' violates the tool-shape policy."""
        results = evaluate_assertions(
            self._tool_failure_as_protocol_error(),
            _TOOL_FAILURE_ASSERTIONS,
            input_request=self._INPUT_REQUEST,
        )
        failed = [r for r in results if not r["passed"]]
        # Must fail: result (exists), result.isError (eq True), result.content (exists),
        #            result.content (typeof array), error (not_exists)
        assert len(failed) >= 2, (
            "Reporting a tool failure via protocol-level 'error' must violate "
            "at least two tool-shape policy assertions."
        )
        failed_paths = {r["assertion"]["path"] for r in failed}
        assert "result" in failed_paths, "result exists assertion must fail"
        assert "error" in failed_paths, "error not_exists assertion must fail"

    def test_is_error_false_does_not_satisfy_tool_failure_assertions(self) -> None:
        """isError=False indicates a successful call, not a tool failure."""
        resp = {
            "jsonrpc": "2.0",
            "id": 9,
            "result": {
                "isError": False,
                "content": [{"type": "text", "text": "ok"}],
            },
        }
        results = evaluate_assertions(
            resp,
            [{"path": "result.isError", "op": "eq", "value": True}],
        )
        assert results[0]["passed"] is False

    def test_result_without_is_error_field_fails_assertion(self) -> None:
        resp = {
            "jsonrpc": "2.0",
            "id": 9,
            "result": {"content": [{"type": "text", "text": "ok"}]},
        }
        results = evaluate_assertions(
            resp,
            [{"path": "result.isError", "op": "eq", "value": True}],
        )
        assert results[0]["passed"] is False


# ===========================================================================
# 6. Protocol Error vs Tool Error — Explicit Mutual Exclusivity
# ===========================================================================


class TestProtocolVsToolErrorDifferentiation:
    """Explicitly encode the mutual exclusivity of protocol errors and tool errors.

    Source: mcp-compliance/baseline-policy.json -> error_boundary:
      protocol_errors.shape = JSON-RPC error object (code/message)
      tool_errors.shape     = MCP tool error result (isError=true with content)
      tool_errors.must_not_be_reported_as_protocol_error = true
    """

    # ------------------------------------------------------------------
    # Representative sample responses
    # ------------------------------------------------------------------

    _PROTOCOL_ERROR: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": None,
        "error": {"code": PARSE_ERROR, "message": "Parse error"},
    }

    _TOOL_FAILURE: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": 10,
        "result": {
            "isError": True,
            "content": [{"type": "text", "text": "Error: execution failed"}],
        },
    }

    # Minimal shape signatures (path-based)
    _PROTOCOL_ERROR_SHAPE: list[dict[str, Any]] = [
        {"path": "error", "op": "exists"},
        {"path": "result", "op": "not_exists"},
    ]

    _TOOL_FAILURE_SHAPE: list[dict[str, Any]] = [
        {"path": "result", "op": "exists"},
        {"path": "result.isError", "op": "eq", "value": True},
        {"path": "error", "op": "not_exists"},
    ]

    # ------------------------------------------------------------------
    # Each shape satisfies its own signature
    # ------------------------------------------------------------------

    def test_protocol_error_satisfies_protocol_error_shape(self) -> None:
        assert_all(self._PROTOCOL_ERROR, self._PROTOCOL_ERROR_SHAPE)

    def test_tool_failure_satisfies_tool_failure_shape(self) -> None:
        assert_all(self._TOOL_FAILURE, self._TOOL_FAILURE_SHAPE)

    # ------------------------------------------------------------------
    # Cross-shape failures — must fail at least one assertion of the other shape
    # ------------------------------------------------------------------

    def test_protocol_error_fails_tool_failure_shape_check(self) -> None:
        results = evaluate_assertions(self._PROTOCOL_ERROR, self._TOOL_FAILURE_SHAPE)
        failed = [r for r in results if not r["passed"]]
        assert len(failed) >= 1, (
            "A protocol-error response must fail at least one tool-failure shape assertion"
        )

    def test_tool_failure_fails_protocol_error_shape_check(self) -> None:
        results = evaluate_assertions(self._TOOL_FAILURE, self._PROTOCOL_ERROR_SHAPE)
        failed = [r for r in results if not r["passed"]]
        assert len(failed) >= 1, (
            "A tool-failure response must fail at least one protocol-error shape assertion"
        )

    # ------------------------------------------------------------------
    # Comprehensive mutual-exclusivity matrix
    # ------------------------------------------------------------------

    def test_shapes_are_mutually_exclusive(self) -> None:
        """Four-quadrant check: each response type satisfies only its own shape."""
        # Protocol error against both shape signatures
        proto_vs_proto = evaluate_assertions(self._PROTOCOL_ERROR, self._PROTOCOL_ERROR_SHAPE)
        proto_vs_tool = evaluate_assertions(self._PROTOCOL_ERROR, self._TOOL_FAILURE_SHAPE)
        # Tool failure against both shape signatures
        tool_vs_tool = evaluate_assertions(self._TOOL_FAILURE, self._TOOL_FAILURE_SHAPE)
        tool_vs_proto = evaluate_assertions(self._TOOL_FAILURE, self._PROTOCOL_ERROR_SHAPE)

        assert all(r["passed"] for r in proto_vs_proto), (
            "Protocol error must pass ALL protocol-error shape assertions"
        )
        assert any(not r["passed"] for r in proto_vs_tool), (
            "Protocol error must fail AT LEAST ONE tool-failure shape assertion"
        )
        assert all(r["passed"] for r in tool_vs_tool), (
            "Tool failure must pass ALL tool-failure shape assertions"
        )
        assert any(not r["passed"] for r in tool_vs_proto), (
            "Tool failure must fail AT LEAST ONE protocol-error shape assertion"
        )

    # ------------------------------------------------------------------
    # All four standard protocol error codes follow protocol-error shape
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        "code,message",
        [
            (PARSE_ERROR, "Parse error"),
            (INVALID_REQUEST, "Invalid Request"),
            (METHOD_NOT_FOUND, "Method not found"),
            (INVALID_PARAMS, "Invalid params"),
        ],
    )
    def test_all_standard_protocol_error_codes_use_protocol_shape(
        self, code: int, message: str
    ) -> None:
        resp: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": code, "message": message},
        }
        assert_all(resp, self._PROTOCOL_ERROR_SHAPE)

    # ------------------------------------------------------------------
    # IO framing round-trips for both shapes
    # ------------------------------------------------------------------

    def test_io_framing_round_trip_for_protocol_error(self) -> None:
        line = build_stdio_line(self._PROTOCOL_ERROR)
        assert line.endswith("\n")
        parsed = parse_stdio_line(line)
        assert parsed["error"]["code"] == PARSE_ERROR
        assert "result" not in parsed

    def test_io_framing_round_trip_for_tool_failure(self) -> None:
        line = build_stdio_line(self._TOOL_FAILURE)
        assert line.endswith("\n")
        parsed = parse_stdio_line(line)
        assert parsed["result"]["isError"] is True
        assert "error" not in parsed
