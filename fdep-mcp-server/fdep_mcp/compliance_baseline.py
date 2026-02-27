from __future__ import annotations

import json
from pathlib import Path
from typing import cast


SHARED_COMPLIANCE_BASELINE_PATH = (
    Path(__file__).resolve().parents[2] / "mcp-compliance" / "baseline-policy.json"
)


def read_shared_compliance_baseline() -> dict[str, object]:
    return cast(
        dict[str, object],
        json.loads(SHARED_COMPLIANCE_BASELINE_PATH.read_text(encoding="utf-8")),
    )
