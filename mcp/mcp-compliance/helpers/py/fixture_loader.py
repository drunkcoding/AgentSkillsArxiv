"""
Shared stdio fixture loader and assertion helpers for MCP compliance testing.

Consumed by fdep-mcp-server (pytest) and usable by any Python test suite that
adds the parent directory to sys.path.  Mirrors the TypeScript counterpart at
mcp-compliance/helpers/ts/fixtureLoader.ts — keep the two in sync when adding
new assertion operators.

Path anchor: this file lives at mcp-compliance/helpers/py/fixture_loader.py.
FIXTURES_DIR is resolved relative to __file__ at import time.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

# parents[0] = mcp-compliance/helpers/py
# parents[1] = mcp-compliance/helpers
# parents[2] = mcp-compliance
FIXTURES_DIR: Path = Path(__file__).resolve().parents[2] / "fixtures"

# ---------------------------------------------------------------------------
# Sentinel for missing dict paths (distinct from None)
# ---------------------------------------------------------------------------


class _Missing:
    """Singleton sentinel returned by _get_at_path when a key is absent."""

    _instance: "_Missing | None" = None

    def __new__(cls) -> "_Missing":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "<MISSING>"


_MISSING = _Missing()

# ---------------------------------------------------------------------------
# Fixture loading
# ---------------------------------------------------------------------------


def load_fixture(name: str) -> dict[str, Any]:
    """Load a named scenario from mcp-compliance/fixtures/scenarios/<name>.json."""
    path = FIXTURES_DIR / "scenarios" / f"{name}.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_fixture_index() -> dict[str, Any]:
    """Load the fixture manifest (mcp-compliance/fixtures/index.json)."""
    return json.loads((FIXTURES_DIR / "index.json").read_text(encoding="utf-8"))


def load_all_fixtures() -> list[dict[str, Any]]:
    """Load all scenarios listed in the index, in order."""
    index = load_fixture_index()
    return [load_fixture(entry["id"]) for entry in index["scenarios"]]


# ---------------------------------------------------------------------------
# Stdio framing utilities
# ---------------------------------------------------------------------------


def build_stdio_line(obj: dict[str, Any]) -> str:
    """
    Serialize obj to a newline-terminated stdio wire line.

    This is the correct framing unit for MCP stdio transport.
    Uses compact separators to match canonical JSON-RPC serialisation.
    """
    return json.dumps(obj, separators=(",", ":")) + "\n"


def parse_stdio_line(line: str) -> dict[str, Any]:
    """
    Parse a single stdio line into a dict.

    Raises json.JSONDecodeError when the line is not valid JSON.
    """
    return json.loads(line.strip())


def read_chunked_lines(data: str) -> list[str]:
    """
    Split a (potentially chunked) buffer received from stdout into complete
    JSON-RPC lines.

    Trailing partial lines (no terminating newline) and blank lines are
    discarded so callers always receive only complete frames.
    """
    parts = data.split("\n")
    # Drop the trailing element: it is either "" (after a terminating newline)
    # or a partial, unterminated line fragment — both must be discarded so
    # callers only receive complete frames.  Mirrors the TS implementation:
    # parts.slice(0, parts.length - 1).filter(l => l.trim().length > 0)
    return [part for part in parts[:-1] if part.strip()]


# ---------------------------------------------------------------------------
# ID correlation
# ---------------------------------------------------------------------------


def correlate_id(request: dict[str, Any], response: dict[str, Any]) -> bool:
    """Return True when response['id'] equals request['id']."""
    req_id = request.get("id")
    return req_id is not None and req_id == response.get("id")


# ---------------------------------------------------------------------------
# Assertion evaluation
# ---------------------------------------------------------------------------


def _get_at_path(obj: Any, dot_path: str) -> Any:
    """Navigate a dot-separated path; returns _MISSING if any segment is absent."""
    current: Any = obj
    for seg in dot_path.split("."):
        if not isinstance(current, dict):
            return _MISSING
        current = current.get(seg, _MISSING)
        if current is _MISSING:
            return _MISSING
    return current


def evaluate_assertions(
    response: dict[str, Any],
    assertions: list[dict[str, Any]],
    input_request: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Evaluate all assertions from a fixture's expected_output against a server
    response.

    Returns a list of result dicts, each containing:
      - passed (bool)
      - assertion (the original assertion dict)
      - actual (the value found at the path, or None if missing)
      - reason (str | None) — human-readable failure explanation

    When any assertion uses op "eq_input_id", pass input_request so the helper
    can read the expected id value.
    """
    results: list[dict[str, Any]] = []

    for a in assertions:
        actual = _get_at_path(response, a["path"])
        op: str = a["op"]

        if op == "eq":
            passed = actual == a["value"]
            reason = (
                None if passed else f"Expected {a['value']!r}, got {actual!r}"
            )

        elif op == "eq_input_id":
            input_id = input_request.get("id") if input_request else None
            passed = actual is not _MISSING and actual == input_id
            reason = (
                None if passed
                else f"Expected id={input_id!r}, got {actual!r}"
            )

        elif op == "exists":
            passed = actual is not _MISSING
            reason = (
                None if passed
                else f"Expected path '{a['path']}' to exist in response"
            )

        elif op == "not_exists":
            passed = actual is _MISSING
            reason = (
                None if passed
                else f"Expected path '{a['path']}' to be absent; got {actual!r}"
            )

        elif op == "typeof":
            type_map: dict[str, type | tuple[type, ...]] = {
                "string": str,
                "number": (int, float),
                "boolean": bool,
                "object": dict,
                "array": list,
            }
            if a["value"] == "array":
                passed = isinstance(actual, list)
                reason = (
                    None if passed
                    else f"Expected list at '{a['path']}', got {type(actual).__name__}"
                )
            else:
                expected_type = type_map.get(a["value"])
                passed = expected_type is not None and isinstance(
                    actual, expected_type
                )
                reason = (
                    None if passed
                    else f"Expected typeof {a['value']!r} at '{a['path']}', got {type(actual).__name__}"
                )

        elif op == "length_gte":
            if isinstance(actual, list):
                passed = len(actual) >= a["value"]
                reason = (
                    None if passed
                    else f"Expected length >= {a['value']}, got {len(actual)}"
                )
            else:
                passed = False
                reason = f"length_gte requires a list; got {type(actual).__name__}"

        else:
            passed = False
            reason = f"Unknown assertion op: {op!r}"

        results.append(
            {
                "passed": passed,
                "assertion": a,
                "actual": None if actual is _MISSING else actual,
                "reason": reason,
            }
        )

    return results


def assert_all(
    response: dict[str, Any],
    assertions: list[dict[str, Any]],
    input_request: dict[str, Any] | None = None,
) -> None:
    """
    Run evaluate_assertions and raise AssertionError if any assertion fails.

    Convenience wrapper for use directly inside pytest test functions.
    """
    results = evaluate_assertions(response, assertions, input_request)
    failures = [r for r in results if not r["passed"]]
    if failures:
        lines = [
            f"  [{f['assertion']['op']}] {f['assertion']['path']}: {f['reason']}"
            for f in failures
        ]
        raise AssertionError(
            f"{len(failures)} assertion(s) failed:\n" + "\n".join(lines)
        )
