#!/usr/bin/env python3
"""Phase-0 gate: validate local mem0 + qdrant metadata filter roundtrip.

This script seeds local mem0 memory with a temporary qdrant store, then runs
explicit metadata filter checks with PASS/FAIL output and exit-code gating.
"""

from __future__ import annotations

import os
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any


QUERY_TOKEN = "mem0-filter-roundtrip-token"
SEED_MEMORIES: list[tuple[str, dict[str, str]]] = [
    (
        f"{QUERY_TOKEN} entry 1 for projA appA scope global",
        {"project": "projA", "app_id": "appA", "scope": "global"},
    ),
    (
        f"{QUERY_TOKEN} entry 2 for projB appB scope project",
        {"project": "projB", "app_id": "appB", "scope": "project"},
    ),
    (
        f"{QUERY_TOKEN} entry 3 for projA appA scope project",
        {"project": "projA", "app_id": "appA", "scope": "project"},
    ),
]


def _extract_results(payload: Any) -> list[Any]:
    if isinstance(payload, dict):
        results = payload.get("results")
        if isinstance(results, list):
            return results
        return [payload]
    if isinstance(payload, list):
        return payload
    if payload is None:
        return []
    return [payload]


def _count(payload: Any) -> int:
    return len(_extract_results(payload))


def _print_check(ok: bool, label: str, expected: int, actual: int) -> None:
    status = "PASS" if ok else "FAIL"
    print(f"{status}: {label} -> expected={expected}, actual={actual}")


def _validate_openai_key() -> bool:
    if os.getenv("OPENAI_API_KEY"):
        return True

    print(
        "ERROR: OPENAI_API_KEY is missing. This gate validates local mem0 + "
        "qdrant with the default OpenAI embedder.",
        file=sys.stderr,
    )
    print(
        "ACTION: Export OPENAI_API_KEY and rerun, e.g. "
        "OPENAI_API_KEY=sk-... python mcp/mem0-mcp-server/scripts/validate_filters.py",
        file=sys.stderr,
    )
    return False


def _create_memory(qdrant_path: Path) -> Any | None:
    try:
        from mem0 import Memory
    except ImportError:
        print(
            "ERROR: mem0ai is not installed in this Python environment. "
            "Install project dependencies before running this gate.",
            file=sys.stderr,
        )
        return None

    config = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": f"validate_filters_{uuid.uuid4().hex[:12]}",
                "path": str(qdrant_path),
            },
        }
    }

    try:
        return Memory.from_config(config)
    except Exception as exc:
        print(
            "ERROR: Failed to initialize local mem0 Memory.from_config with qdrant.",
            file=sys.stderr,
        )
        print(f"DETAIL: {exc}", file=sys.stderr)
        return None


def main() -> int:
    if not _validate_openai_key():
        return 1

    with tempfile.TemporaryDirectory(prefix="mem0-validate-filters-") as temp_dir:
        qdrant_path = Path(temp_dir) / "qdrant"
        qdrant_path.mkdir(parents=True, exist_ok=True)

        memory = _create_memory(qdrant_path)
        if memory is None:
            return 1

        user_id = f"validate-filters-{uuid.uuid4().hex[:10]}"
        print(f"INFO: temp_qdrant_path={qdrant_path}")
        print(f"INFO: user_id={user_id}")

        for idx, (text, metadata) in enumerate(SEED_MEMORIES, start=1):
            try:
                memory.add(text, user_id=user_id, metadata=metadata, infer=False)
            except TypeError:
                memory.add(text, user_id=user_id, metadata=metadata)
            except Exception as exc:
                print(f"FAIL: seed add #{idx} failed for metadata={metadata}: {exc}")
                return 1

        try:
            all_entries_count = _count(memory.get_all(user_id=user_id, limit=100))

            case1_count = _count(
                memory.search(
                    QUERY_TOKEN,
                    user_id=user_id,
                    filters={"project": "projA"},
                    limit=100,
                )
            )
            case2_count = _count(
                memory.search(
                    QUERY_TOKEN,
                    user_id=user_id,
                    filters={"project": "projA", "scope": "global"},
                    limit=100,
                )
            )
            case3_count = _count(
                memory.get_all(
                    user_id=user_id,
                    filters={"app_id": "appA"},
                    limit=100,
                )
            )
            case4_count = _count(
                memory.search(
                    QUERY_TOKEN,
                    user_id=user_id,
                    filters={},
                    limit=100,
                )
            )
            case5_count = _count(
                memory.search(
                    QUERY_TOKEN,
                    user_id=user_id,
                    filters={"project": "nonexistent"},
                    limit=100,
                )
            )
        except TypeError as exc:
            print(
                "FAIL: Installed mem0 version does not support expected search/get_all "
                "metadata filter parameters.",
                file=sys.stderr,
            )
            print(f"DETAIL: {exc}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"FAIL: runtime error during filter checks: {exc}", file=sys.stderr)
            return 1

        checks = [
            ("filters={'project':'projA'}", 2, case1_count),
            ("filters={'project':'projA','scope':'global'}", 1, case2_count),
            ("get_all(filters={'app_id':'appA'})", 2, case3_count),
            ("filters={}", all_entries_count, case4_count),
            ("filters={'project':'nonexistent'}", 0, case5_count),
        ]

        all_passed = True
        for label, expected, actual in checks:
            ok = expected == actual
            _print_check(ok, label, expected, actual)
            all_passed = all_passed and ok

        if all_passed:
            print("RESULT: PASS - metadata filter roundtrip gate succeeded.")
            return 0

        print("RESULT: FAIL - one or more metadata filter checks failed.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
