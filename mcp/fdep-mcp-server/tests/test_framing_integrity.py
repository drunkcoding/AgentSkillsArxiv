"""
Framing integrity tests for fdep-mcp-server.

Verifies:
  1. Stdout carries exclusively parseable JSON-RPC frames (contamination detection).
  2. Newline-delimited framing helpers are robust against partial frames and edge cases.
  3. Multi-message framing handles chunked output in insertion order.
  4. build_stdio_line / parse_stdio_line always produce valid, round-trippable frames.
  5. A live subprocess echoing JSON-RPC frames produces only parseable stdout.

Sections:
  A. Contamination detection — synthetic buffers (negative-path)
  B. Newline-delimited framing robustness — unit tests
  C. Stdio frame contract — build / parse round-trips
  D. Live subprocess — stdout purity (positive test with inline echo server)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from textwrap import dedent
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
    build_stdio_line,
    parse_stdio_line,
    read_chunked_lines,
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _is_valid_json(line: str) -> bool:
    """Return True if `line` is parseable JSON."""
    try:
        json.loads(line)
        return True
    except json.JSONDecodeError:
        return False


def _parse_failures(buffer: str) -> list[str]:
    """Return all complete lines from `buffer` that fail JSON.parse."""
    return [l for l in read_chunked_lines(buffer) if not _is_valid_json(l)]


# ---------------------------------------------------------------------------
# A. Contamination detection — synthetic buffers
# ---------------------------------------------------------------------------


class TestStdoutContaminationDetection:
    """Negative-path tests: verify non-JSON stdout lines are detectable."""

    def test_single_non_json_line_in_multi_frame_buffer_is_detected(self) -> None:
        contaminated = (
            '{"jsonrpc":"2.0","id":1,"result":{}}\n'
            "WARNING: leaked debug output\n"
            '{"jsonrpc":"2.0","id":2,"result":{}}\n'
        )
        failures = _parse_failures(contaminated)
        assert len(failures) == 1
        assert "WARNING" in failures[0]

    def test_clean_buffer_produces_zero_failures(self) -> None:
        clean = (
            '{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05"}}\n'
            '{"jsonrpc":"2.0","id":2,"result":{"tools":[]}}\n'
        )
        assert _parse_failures(clean) == []

    def test_buffer_of_only_non_json_text_all_lines_fail(self) -> None:
        all_bad = "Server starting...\nInitializing tools...\n"
        lines = read_chunked_lines(all_bad)
        failures = _parse_failures(all_bad)
        assert len(lines) > 0
        assert len(failures) == len(lines)  # 100 % contamination

    def test_single_contamination_in_10_frame_buffer_detected(self) -> None:
        frames = [f'{{"jsonrpc":"2.0","id":{i},"result":{{}}}}\n' for i in range(10)]
        frames.insert(5, "DEBUG: connection established\n")
        buffer = "".join(frames)
        failures = _parse_failures(buffer)
        assert len(failures) == 1
        assert "DEBUG" in failures[0]

    def test_parse_stdio_line_raises_json_decode_error_on_non_json(self) -> None:
        with pytest.raises(json.JSONDecodeError):
            parse_stdio_line("WARNING: debug output")

    def test_parse_stdio_line_succeeds_on_valid_json_rpc(self) -> None:
        obj: dict[str, Any] = {"jsonrpc": "2.0", "id": 1, "result": {}}
        line = build_stdio_line(obj)
        parsed = parse_stdio_line(line)
        assert parsed["jsonrpc"] == "2.0"
        assert parsed["id"] == 1

    def test_error_response_envelope_is_valid_json(self) -> None:
        error_frame = (
            '{"jsonrpc":"2.0","id":42,'
            '"error":{"code":-32601,"message":"Method not found"}}\n'
        )
        lines = read_chunked_lines(error_frame)
        assert len(lines) == 1
        assert _is_valid_json(lines[0])

    def test_stderr_leak_to_stdout_is_detectable(self) -> None:
        # Models the scenario where a server incorrectly emits log lines to stdout.
        stderr_leak = "[INFO] Server started\n"
        protocol_frame = '{"jsonrpc":"2.0","id":1,"result":{}}\n'
        mixed = protocol_frame + stderr_leak

        failures = _parse_failures(mixed)
        assert len(failures) == 1
        assert "[INFO]" in failures[0]


# ---------------------------------------------------------------------------
# B. Newline-delimited framing robustness — unit tests
# ---------------------------------------------------------------------------


class TestNewlineDelimitedFramingRobustness:
    def test_two_frames_in_single_chunk_yields_two_lines_in_order(self) -> None:
        chunk = '{"jsonrpc":"2.0","id":10}\n{"jsonrpc":"2.0","id":11}\n'
        lines = read_chunked_lines(chunk)
        assert len(lines) == 2
        assert json.loads(lines[0])["id"] == 10
        assert json.loads(lines[1])["id"] == 11

    def test_partial_trailing_frame_is_discarded(self) -> None:
        partial = '{"jsonrpc":"2.0","id":20}\n{"incomplete":true'
        lines = read_chunked_lines(partial)
        assert len(lines) == 1
        assert json.loads(lines[0])["id"] == 20

    def test_three_frames_in_chunk_in_insertion_order(self) -> None:
        chunk = (
            '{"jsonrpc":"2.0","id":30}\n'
            '{"jsonrpc":"2.0","id":31}\n'
            '{"jsonrpc":"2.0","id":32}\n'
        )
        lines = read_chunked_lines(chunk)
        assert len(lines) == 3
        assert [json.loads(l)["id"] for l in lines] == [30, 31, 32]

    def test_empty_buffer_yields_no_frames(self) -> None:
        assert read_chunked_lines("") == []

    def test_newline_only_buffer_yields_no_frames(self) -> None:
        assert read_chunked_lines("\n") == []

    def test_consecutive_newlines_between_frames_produce_no_spurious_frames(
        self,
    ) -> None:
        buf = '{"jsonrpc":"2.0","id":40}\n\n{"jsonrpc":"2.0","id":41}\n'
        lines = read_chunked_lines(buf)
        assert len(lines) == 2
        assert all(l.strip() for l in lines)  # no blank lines leaked through

    def test_compact_json_frame_parses_correctly(self) -> None:
        compact = '{"jsonrpc":"2.0","id":50,"result":{"nested":{"a":1,"b":true}}}\n'
        lines = read_chunked_lines(compact)
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["jsonrpc"] == "2.0"
        assert parsed["id"] == 50

    def test_frame_without_newline_is_treated_as_incomplete_and_discarded(
        self,
    ) -> None:
        no_terminator = '{"jsonrpc":"2.0","id":70}'
        assert read_chunked_lines(no_terminator) == []

    def test_large_batch_of_20_frames_all_parse_and_preserve_order(self) -> None:
        n = 20
        buffer = "".join(
            f'{{"jsonrpc":"2.0","id":{1000 + i}}}\n' for i in range(n)
        )
        lines = read_chunked_lines(buffer)
        assert len(lines) == n
        ids = [json.loads(l)["id"] for l in lines]
        assert ids == list(range(1000, 1000 + n))


# ---------------------------------------------------------------------------
# C. Stdio frame contract — build / parse round-trips
# ---------------------------------------------------------------------------


class TestStdioFrameContract:
    def test_build_stdio_line_always_ends_with_newline(self) -> None:
        objs: list[dict[str, Any]] = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize"},
            {"jsonrpc": "2.0", "id": 2, "result": {"tools": []}},
            {
                "jsonrpc": "2.0",
                "error": {"code": -32600, "message": "Invalid Request"},
            },
        ]
        for obj in objs:
            line = build_stdio_line(obj)
            assert line.endswith("\n"), f"Expected trailing newline, got: {line!r}"

    def test_build_stdio_line_contains_exactly_one_newline(self) -> None:
        obj: dict[str, Any] = {"jsonrpc": "2.0", "id": 1}
        line = build_stdio_line(obj)
        assert line.count("\n") == 1

    def test_round_trip_preserves_all_fields(self) -> None:
        original: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": 42,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "fdep-server", "version": "0.1.0"},
                "capabilities": {"tools": {}},
            },
        }
        line = build_stdio_line(original)
        parsed = parse_stdio_line(line)
        assert parsed == original

    def test_multiple_round_trips_preserve_order(self) -> None:
        msgs: list[dict[str, Any]] = [
            {"jsonrpc": "2.0", "id": i, "result": {}} for i in range(5)
        ]
        lines = [build_stdio_line(m) for m in msgs]
        parsed = [parse_stdio_line(l) for l in lines]
        for i, p in enumerate(parsed):
            assert p["id"] == i

    def test_result_xor_error_envelope_structure(self) -> None:
        # A valid response has result OR error, never both, never neither
        success: dict[str, Any] = {"jsonrpc": "2.0", "id": 1, "result": {}}
        error: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": 2,
            "error": {"code": -32601, "message": "Method not found"},
        }
        for envelope in (success, error):
            parsed = parse_stdio_line(build_stdio_line(envelope))
            has_result = "result" in parsed
            has_error = "error" in parsed
            assert has_result or has_error
            assert not (has_result and has_error)

    def test_parse_stdio_line_strips_surrounding_whitespace(self) -> None:
        obj: dict[str, Any] = {"jsonrpc": "2.0", "id": 9}
        padded = "   " + json.dumps(obj) + "   \n"
        parsed = parse_stdio_line(padded)
        assert parsed["id"] == 9


# ---------------------------------------------------------------------------
# D. Live subprocess — stdout purity (positive test)
# ---------------------------------------------------------------------------

# Minimal JSON-RPC echo server used as a stand-in for the real fdep server.
# Reads newline-delimited JSON from stdin, writes newline-delimited JSON to
# stdout, and sends any non-protocol messages exclusively to stderr.
_ECHO_SERVER_SCRIPT = dedent("""\
    import sys, json

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            # Non-protocol input: send error to stderr only, not stdout
            print("parse error", file=sys.stderr, flush=True)
            continue

        resp = {
            "jsonrpc": "2.0",
            "id": req.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": "echo-server", "version": "0.0.1"},
                "capabilities": {},
            },
        }
        sys.stdout.write(json.dumps(resp) + "\\n")
        sys.stdout.flush()
""")


class TestLiveSubprocessStdoutPurity:
    """Positive tests: spawn a subprocess and verify stdout contains only JSON-RPC."""

    def _spawn_echo_server(self) -> subprocess.Popen[bytes]:
        return subprocess.Popen(
            [sys.executable, "-c", _ECHO_SERVER_SCRIPT],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def _exchange(
        self,
        proc: subprocess.Popen[bytes],
        request: dict[str, Any],
    ) -> str:
        """Write one JSON-RPC request and read the raw response line from stdout."""
        assert proc.stdin is not None
        assert proc.stdout is not None
        proc.stdin.write(json.dumps(request).encode() + b"\n")
        proc.stdin.flush()
        return proc.stdout.readline().decode()

    def test_subprocess_stdout_is_valid_json_for_initialize(self) -> None:
        proc = self._spawn_echo_server()
        try:
            request: dict[str, Any] = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0.0.0"},
                },
            }
            raw = self._exchange(proc, request)
            # Must be valid JSON
            parsed = json.loads(raw)
            assert parsed["jsonrpc"] == "2.0"
            assert parsed["id"] == 1
        finally:
            proc.kill()
            proc.wait()

    def test_subprocess_stdout_id_correlates_with_request_id(self) -> None:
        proc = self._spawn_echo_server()
        try:
            for req_id in (10, 20, 30):
                request: dict[str, Any] = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test", "version": "0.0.0"},
                    },
                }
                raw = self._exchange(proc, request)
                parsed = json.loads(raw)
                assert parsed["id"] == req_id, (
                    f"Expected id={req_id}, got id={parsed.get('id')}"
                )
        finally:
            proc.kill()
            proc.wait()

    def test_subprocess_stdout_produces_no_parse_failures_across_multiple_exchanges(
        self,
    ) -> None:
        proc = self._spawn_echo_server()
        try:
            raw_lines: list[str] = []
            assert proc.stdout is not None
            assert proc.stdin is not None
            for i in range(5):
                request: dict[str, Any] = {
                    "jsonrpc": "2.0",
                    "id": 100 + i,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test", "version": "0.0.0"},
                    },
                }
                proc.stdin.write(json.dumps(request).encode() + b"\n")
                proc.stdin.flush()
                raw_lines.append(proc.stdout.readline().decode())

            failures = [l for l in raw_lines if not _is_valid_json(l.strip())]
            assert failures == [], (
                f"Unexpected non-JSON stdout lines: {failures}"
            )
        finally:
            proc.kill()
            proc.wait()

    def test_subprocess_stderr_does_not_contaminate_stdout(self) -> None:
        """Any diagnostics from the server must go to stderr, not stdout."""
        proc = self._spawn_echo_server()
        try:
            assert proc.stdin is not None
            assert proc.stdout is not None

            # Send a valid request; the server may log to stderr
            request: dict[str, Any] = {
                "jsonrpc": "2.0",
                "id": 200,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "0.0.0"},
                },
            }
            proc.stdin.write(json.dumps(request).encode() + b"\n")
            proc.stdin.flush()
            raw = proc.stdout.readline().decode()

            # stdout line must be parseable JSON regardless of stderr content
            assert _is_valid_json(raw.strip()), (
                f"stdout contained non-JSON: {raw!r}"
            )
        finally:
            proc.kill()
            proc.wait()
