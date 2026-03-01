"""
Smoke tests: shared stdio fixture consumption (Python side).

Verifies that:
  1. All fixture scenario files in mcp-compliance/fixtures/ can be loaded.
  2. Each scenario conforms to the expected dict shape.
  3. The stdio framing helpers (build_stdio_line, parse_stdio_line,
     read_chunked_lines) round-trip correctly.
  4. The ID correlation helper works for matched and mismatched ids.
  5. The assertion evaluator correctly judges all supported operators.

These tests do NOT start a live server — they prove shared-fixture
readability and Python helper correctness only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Helper import — add mcp-compliance/helpers/py to sys.path
# ---------------------------------------------------------------------------
# parents[0] = fdep-mcp-server/tests
# parents[1] = fdep-mcp-server
# parents[2] = repo root
_HELPER_DIR = Path(__file__).resolve().parents[2] / "mcp-compliance" / "helpers" / "py"
if str(_HELPER_DIR) not in sys.path:
    sys.path.insert(0, str(_HELPER_DIR))

from fixture_loader import (  # pyright: ignore[reportMissingImports]  # noqa: E402
    load_fixture,
    load_fixture_index,
    load_all_fixtures,
    build_stdio_line,
    parse_stdio_line,
    read_chunked_lines,
    correlate_id,
    evaluate_assertions,
    assert_all,
    FIXTURES_DIR,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EXPECTED_SCENARIO_IDS = [
    "initialize_happy",
    "initialized_notification",
    "tools_list",
    "tools_call_valid",
    "malformed_json",
    "invalid_envelope",
    "unknown_method",
]


# ---------------------------------------------------------------------------
# 1. Index loading
# ---------------------------------------------------------------------------


class TestFixtureIndex:
    def test_index_file_exists(self) -> None:
        assert (FIXTURES_DIR / "index.json").is_file()

    def test_index_loads_and_has_version(self) -> None:
        index = load_fixture_index()
        assert index["version"] == "1.0.0"

    def test_index_scenario_count(self) -> None:
        index = load_fixture_index()
        assert len(index["scenarios"]) == 7

    def test_index_entries_have_required_fields(self) -> None:
        index = load_fixture_index()
        for entry in index["scenarios"]:
            assert isinstance(entry["id"], str)
            assert isinstance(entry["file"], str)
            assert isinstance(entry["scenario_type"], str)


# ---------------------------------------------------------------------------
# 2. Individual fixture loading
# ---------------------------------------------------------------------------


class TestIndividualFixtureLoading:
    @pytest.mark.parametrize("fixture_id", EXPECTED_SCENARIO_IDS)
    def test_loads_without_error(self, fixture_id: str) -> None:
        scenario = load_fixture(fixture_id)
        assert scenario["id"] == fixture_id
        assert scenario["transport"] == "stdio"
        assert scenario["framing"] == "newline_delimited_json"
        assert isinstance(scenario["description"], str)
        assert len(scenario["description"]) > 0

    def test_load_all_fixtures_returns_all_scenarios(self) -> None:
        all_fixtures = load_all_fixtures()
        assert len(all_fixtures) == 7
        ids = [f["id"] for f in all_fixtures]
        for expected_id in EXPECTED_SCENARIO_IDS:
            assert expected_id in ids


# ---------------------------------------------------------------------------
# 3. Scenario structure — request_response
# ---------------------------------------------------------------------------


class TestRequestResponseFixtureStructure:
    def test_initialize_happy_input_structure(self) -> None:
        f = load_fixture("initialize_happy")
        assert f["scenario_type"] == "request_response"
        assert isinstance(f["input"]["wire_line"], str)
        assert len(f["input"]["wire_line"]) > 0
        assert f["input"]["parsed"] is not None
        assert f["input"]["parsed"]["method"] == "initialize"

    def test_initialize_happy_expected_output_not_null(self) -> None:
        f = load_fixture("initialize_happy")
        assert f["expected_output"] is not None
        assert isinstance(f["expected_output"]["assertions"], list)
        assert len(f["expected_output"]["assertions"]) > 0

    def test_tools_list_has_length_gte_assertion(self) -> None:
        f = load_fixture("tools_list")
        assertions = f["expected_output"]["assertions"]
        lgt = next(
            (a for a in assertions if a["op"] == "length_gte" and a["path"] == "result.tools"),
            None,
        )
        assert lgt is not None
        assert isinstance(lgt["value"], int)

    def test_unknown_method_requires_error_code_32601(self) -> None:
        f = load_fixture("unknown_method")
        code_assert = next(
            (a for a in f["expected_output"]["assertions"] if a["op"] == "eq" and a["path"] == "error.code"),
            None,
        )
        assert code_assert is not None
        assert code_assert["value"] == -32601


# ---------------------------------------------------------------------------
# 4. Scenario structure — notification
# ---------------------------------------------------------------------------


class TestNotificationFixtureStructure:
    def test_initialized_notification_has_null_expected_output(self) -> None:
        f = load_fixture("initialized_notification")
        assert f["scenario_type"] == "notification"
        assert f["expected_output"] is None

    def test_notification_wire_line_has_no_id(self) -> None:
        f = load_fixture("initialized_notification")
        parsed = json.loads(f["input"]["wire_line"])
        assert "id" not in parsed


# ---------------------------------------------------------------------------
# 5. Scenario structure — error fixtures
# ---------------------------------------------------------------------------


class TestErrorFixtureStructure:
    def test_malformed_json_has_null_parsed(self) -> None:
        f = load_fixture("malformed_json")
        assert f["scenario_type"] == "request_error"
        assert f["input"]["parsed"] is None

    def test_malformed_json_has_error_code_32700(self) -> None:
        f = load_fixture("malformed_json")
        code_assert = next(
            (a for a in f["expected_output"]["assertions"] if a["op"] == "eq" and a["path"] == "error.code"),
            None,
        )
        assert code_assert is not None
        assert code_assert["value"] == -32700

    def test_invalid_envelope_has_error_code_32600(self) -> None:
        f = load_fixture("invalid_envelope")
        code_assert = next(
            (a for a in f["expected_output"]["assertions"] if a["op"] == "eq" and a["path"] == "error.code"),
            None,
        )
        assert code_assert is not None
        assert code_assert["value"] == -32600

    def test_parse_and_invalid_errors_may_be_null_id(self) -> None:
        for name in ("malformed_json", "invalid_envelope"):
            f = load_fixture(name)
            assert f["expected_output"]["id_correlation"] == "may_be_null"

    def test_unknown_method_must_match_input_id(self) -> None:
        f = load_fixture("unknown_method")
        assert f["expected_output"]["id_correlation"] == "must_match_input_id"


# ---------------------------------------------------------------------------
# 6. Stdio framing utilities
# ---------------------------------------------------------------------------


class TestStdioFraming:
    def test_build_stdio_line_appends_newline(self) -> None:
        obj = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
        line = build_stdio_line(obj)
        assert line.endswith("\n")

    def test_round_trip_simple_object(self) -> None:
        obj = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        line = build_stdio_line(obj)
        parsed = parse_stdio_line(line)
        assert parsed["jsonrpc"] == "2.0"
        assert parsed["id"] == 1
        assert parsed["method"] == "initialize"

    def test_parse_stdio_line_strips_whitespace(self) -> None:
        obj = {"jsonrpc": "2.0", "id": 2}
        padded = "  " + json.dumps(obj) + "  \n"
        parsed = parse_stdio_line(padded)
        assert parsed["id"] == 2

    def test_parse_stdio_line_raises_on_invalid_json(self) -> None:
        with pytest.raises(json.JSONDecodeError):
            parse_stdio_line("not json at all")

    def test_fixture_wire_line_round_trips(self) -> None:
        f = load_fixture("initialize_happy")
        parsed = parse_stdio_line(f["input"]["wire_line"])
        assert parsed["jsonrpc"] == "2.0"
        assert parsed["method"] == "initialize"


class TestReadChunkedLines:
    def test_splits_multi_line_buffer(self) -> None:
        buf = '{"jsonrpc":"2.0","id":1,"result":{}}\n{"jsonrpc":"2.0","id":2,"result":{}}\n'
        lines = read_chunked_lines(buf)
        assert len(lines) == 2
        assert '"id":1' in lines[0]
        assert '"id":2' in lines[1]

    def test_discards_trailing_partial_line(self) -> None:
        buf = '{"jsonrpc":"2.0","id":1,"result":{}}\n{"partial":true'
        lines = read_chunked_lines(buf)
        assert len(lines) == 1
        assert '"id":1' in lines[0]

    def test_single_line_buffer(self) -> None:
        buf = '{"jsonrpc":"2.0","id":3,"result":{}}\n'
        lines = read_chunked_lines(buf)
        assert len(lines) == 1

    def test_empty_buffer(self) -> None:
        assert read_chunked_lines("") == []
        assert read_chunked_lines("\n") == []


# ---------------------------------------------------------------------------
# 7. ID correlation
# ---------------------------------------------------------------------------


class TestCorrelateId:
    def test_returns_true_for_matching_ids(self) -> None:
        assert correlate_id({"jsonrpc": "2.0", "id": 1}, {"jsonrpc": "2.0", "id": 1}) is True

    def test_returns_false_for_different_ids(self) -> None:
        assert correlate_id({"jsonrpc": "2.0", "id": 1}, {"jsonrpc": "2.0", "id": 2}) is False

    def test_returns_false_when_request_has_no_id(self) -> None:
        assert correlate_id({"jsonrpc": "2.0"}, {"jsonrpc": "2.0", "id": 1}) is False

    def test_returns_false_when_response_has_no_id(self) -> None:
        assert correlate_id({"jsonrpc": "2.0", "id": 1}, {"jsonrpc": "2.0"}) is False


# ---------------------------------------------------------------------------
# 8. Assertion evaluation
# ---------------------------------------------------------------------------


_SUCCESS_RESPONSE: dict[str, Any] = {
    "jsonrpc": "2.0",
    "id": 42,
    "result": {
        "protocolVersion": "2024-11-05",
        "serverInfo": {"name": "test-server", "version": "1.0.0"},
        "capabilities": {"tools": {}},
        "tools": ["a", "b", "c"],
    },
}


class TestEvaluateAssertions:
    def test_op_eq_passes(self) -> None:
        results = evaluate_assertions(
            _SUCCESS_RESPONSE, [{"path": "jsonrpc", "op": "eq", "value": "2.0"}]
        )
        assert results[0]["passed"] is True

    def test_op_eq_fails(self) -> None:
        results = evaluate_assertions(
            _SUCCESS_RESPONSE, [{"path": "jsonrpc", "op": "eq", "value": "1.0"}]
        )
        assert results[0]["passed"] is False
        assert results[0]["reason"]

    def test_op_eq_input_id_passes(self) -> None:
        results = evaluate_assertions(
            _SUCCESS_RESPONSE,
            [{"path": "id", "op": "eq_input_id"}],
            input_request={"jsonrpc": "2.0", "id": 42},
        )
        assert results[0]["passed"] is True

    def test_op_eq_input_id_fails(self) -> None:
        results = evaluate_assertions(
            _SUCCESS_RESPONSE,
            [{"path": "id", "op": "eq_input_id"}],
            input_request={"jsonrpc": "2.0", "id": 99},
        )
        assert results[0]["passed"] is False

    def test_op_exists_passes(self) -> None:
        results = evaluate_assertions(
            _SUCCESS_RESPONSE, [{"path": "result.serverInfo", "op": "exists"}]
        )
        assert results[0]["passed"] is True

    def test_op_exists_fails(self) -> None:
        results = evaluate_assertions(
            _SUCCESS_RESPONSE, [{"path": "result.missing_key", "op": "exists"}]
        )
        assert results[0]["passed"] is False

    def test_op_not_exists_passes(self) -> None:
        results = evaluate_assertions(
            _SUCCESS_RESPONSE, [{"path": "error", "op": "not_exists"}]
        )
        assert results[0]["passed"] is True

    def test_op_not_exists_fails(self) -> None:
        results = evaluate_assertions(
            _SUCCESS_RESPONSE, [{"path": "result", "op": "not_exists"}]
        )
        assert results[0]["passed"] is False

    def test_op_typeof_array_passes(self) -> None:
        results = evaluate_assertions(
            _SUCCESS_RESPONSE,
            [{"path": "result.tools", "op": "typeof", "value": "array"}],
        )
        assert results[0]["passed"] is True

    def test_op_typeof_string_passes(self) -> None:
        results = evaluate_assertions(
            _SUCCESS_RESPONSE,
            [{"path": "jsonrpc", "op": "typeof", "value": "string"}],
        )
        assert results[0]["passed"] is True

    def test_op_length_gte_passes(self) -> None:
        results = evaluate_assertions(
            _SUCCESS_RESPONSE,
            [{"path": "result.tools", "op": "length_gte", "value": 3}],
        )
        assert results[0]["passed"] is True

    def test_op_length_gte_fails(self) -> None:
        results = evaluate_assertions(
            _SUCCESS_RESPONSE,
            [{"path": "result.tools", "op": "length_gte", "value": 10}],
        )
        assert results[0]["passed"] is False

    def test_multiple_assertions_all_evaluated(self) -> None:
        results = evaluate_assertions(
            _SUCCESS_RESPONSE,
            [
                {"path": "jsonrpc", "op": "eq", "value": "2.0"},
                {"path": "error", "op": "not_exists"},
                {"path": "result.serverInfo.name", "op": "exists"},
                {"path": "result.tools", "op": "length_gte", "value": 1},
            ],
        )
        assert len(results) == 4
        assert all(r["passed"] for r in results)


class TestAssertAll:
    def test_does_not_raise_when_all_pass(self) -> None:
        assert_all(
            {"jsonrpc": "2.0", "id": 1, "result": {"protocolVersion": "2024-11-05"}},
            [
                {"path": "jsonrpc", "op": "eq", "value": "2.0"},
                {"path": "result.protocolVersion", "op": "exists"},
            ],
        )

    def test_raises_with_failure_details(self) -> None:
        with pytest.raises(AssertionError, match="1 assertion"):
            assert_all(
                {"jsonrpc": "1.0"},
                [{"path": "jsonrpc", "op": "eq", "value": "2.0"}],
            )


# ---------------------------------------------------------------------------
# 9. End-to-end: fixture assertions against synthetic response
# ---------------------------------------------------------------------------


class TestEndToEnd:
    def test_initialize_happy_assertions_pass_against_well_formed_response(
        self,
    ) -> None:
        fixture = load_fixture("initialize_happy")
        input_parsed = fixture["input"]["parsed"]
        synthetic = {
            "jsonrpc": "2.0",
            "id": input_parsed["id"],
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "fdep-server", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        }
        assert_all(
            synthetic,
            fixture["expected_output"]["assertions"],
            input_request=input_parsed,
        )

    def test_initialize_happy_assertions_fail_on_incomplete_response(self) -> None:
        fixture = load_fixture("initialize_happy")
        incomplete = {"jsonrpc": "2.0", "id": 1}
        results = evaluate_assertions(
            incomplete,
            fixture["expected_output"]["assertions"],
            input_request=fixture["input"]["parsed"],
        )
        failed = [r for r in results if not r["passed"]]
        # At minimum: result.protocolVersion, result.serverInfo, result.capabilities missing
        assert len(failed) >= 3

    def test_malformed_json_error_assertions_pass(self) -> None:
        fixture = load_fixture("malformed_json")
        synthetic_error = {
            "jsonrpc": "2.0",
            "id": None,
            "error": {"code": -32700, "message": "Parse error"},
        }
        assert_all(synthetic_error, fixture["expected_output"]["assertions"])

    def test_unknown_method_assertions_pass_against_synthetic_error(self) -> None:
        fixture = load_fixture("unknown_method")
        input_parsed = fixture["input"]["parsed"]
        synthetic_error = {
            "jsonrpc": "2.0",
            "id": input_parsed["id"],
            "error": {"code": -32601, "message": "Method not found"},
        }
        assert_all(
            synthetic_error,
            fixture["expected_output"]["assertions"],
            input_request=input_parsed,
        )
