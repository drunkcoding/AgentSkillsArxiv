from __future__ import annotations

import hashlib
import logging
import os
import re
import threading
import time
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class PlanCandidate:
    text: str
    message_id: str
    confidence: float
    detected_at: float


class PlanGate:
    _NUMBERED_PLAN_RE = re.compile(
        r"(?ms)^\s*1\.\s+.+?^\s*2\.\s+.+?^\s*3\.\s+",
    )
    _PLAN_HEADING_RE = re.compile(r"(?im)^\s*##\s*plan\b")
    _STEP_RE = re.compile(r"(?im)\bstep\s*1\s*:")
    _PHRASE_WEIGHTS: tuple[tuple[str, float], ...] = (
        ("here's my plan", 0.35),
        ("proposed approach", 0.35),
        ("implementation plan", 0.35),
        ("i'll", 0.15),
        ("i will", 0.15),
    )

    def __init__(self, approval_timeout: int = 1800) -> None:
        raw = os.environ.get("DISPATCH_PLAN_GATE_TIMEOUT", str(approval_timeout))
        try:
            parsed = int(raw)
        except ValueError:
            log.warning("Invalid DISPATCH_PLAN_GATE_TIMEOUT=%r; using %s", raw, approval_timeout)
            parsed = approval_timeout

        self.approval_timeout = max(1, parsed)
        self._pending: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def detect_plan(self, text: str) -> PlanCandidate | None:
        normalized = text.strip()
        if not normalized:
            return None

        lowered = normalized.lower()
        score = 0.0

        if self._NUMBERED_PLAN_RE.search(normalized):
            score += 0.45
        if self._PLAN_HEADING_RE.search(normalized):
            score += 0.35
        if self._STEP_RE.search(normalized):
            score += 0.35

        for phrase, weight in self._PHRASE_WEIGHTS:
            if phrase in lowered:
                score += weight

        if score < 0.35:
            return None

        now = time.time()
        digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:10]
        message_id = f"msg_{int(now * 1000)}_{digest}"
        return PlanCandidate(
            text=normalized,
            message_id=message_id,
            confidence=min(1.0, score),
            detected_at=now,
        )

    def request_approval(self, candidate: PlanCandidate, notifier: Any, job: Any) -> None:
        task_id = str(getattr(job, "task_id", "")).strip()
        if not task_id:
            raise ValueError("job.task_id is required for plan approval")

        with self._lock:
            self._pending[task_id] = {
                "candidate": candidate,
                "status": "pending",
                "requested_at": time.time(),
            }

        excerpt = candidate.text
        if len(excerpt) > 1200:
            excerpt = excerpt[:1199].rstrip() + "…"

        message = (
            "Agent proposed an implementation plan and is waiting for approval.\n\n"
            f"Confidence: {candidate.confidence:.2f}\n"
            f"Message ID: {candidate.message_id}\n\n"
            f"{excerpt}\n\n"
            "Reply with APPROVE to continue or REJECT to stop."
        )

        if notifier is None:
            log.info("Plan approval requested for %s, but notifier is missing", task_id)
            return

        try:
            notifier.plan_approval(
                str(getattr(job, "host", "dispatcher")),
                str(getattr(job, "folder", "")),
                str(getattr(job, "title", "Plan approval")),
                excerpt,
                task_id,
            )
        except Exception:  # noqa: BLE001
            log.exception("Failed sending plan approval request for %s", task_id)

    def check_approval(self, task_id: str) -> str:
        with self._lock:
            record = self._pending.get(task_id)
            if record is None:
                return "approved"

            status = str(record.get("status", "pending"))
            if status != "pending":
                return status

            requested_at = float(record.get("requested_at", 0.0))
            if (time.time() - requested_at) >= float(self.approval_timeout):
                record["status"] = "timeout"
                log.info("Plan approval timed out for %s (auto-approved)", task_id)
                return "timeout"

            return "pending"

    def register_approval(self, task_id: str, approved: bool) -> None:
        with self._lock:
            record = self._pending.get(task_id)
            if record is None:
                placeholder = PlanCandidate(
                    text="",
                    message_id=f"manual_{task_id}",
                    confidence=0.0,
                    detected_at=time.time(),
                )
                record = {
                    "candidate": placeholder,
                    "status": "pending",
                    "requested_at": time.time(),
                }
                self._pending[task_id] = record

            record["status"] = "approved" if approved else "rejected"


class _TestNotifier:
    def question(self, host: str, folder: str, title: str, question: str) -> None:
        print(f"[QUESTION] {host} {folder} :: {title}\n{question}\n")


@dataclass
class _TestJob:
    task_id: str
    host: str
    folder: str
    title: str


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    gate = PlanGate(approval_timeout=2)
    samples = [
        "I'll fix the race condition.",
        "## Plan\n1. Reproduce\n2. Add lock\n3. Add tests",
        "Quick question: what does this function do?",
        "Here's my plan: Step 1: inspect state transitions.",
    ]

    test_job = _TestJob(
        task_id="task_123",
        host="devbox",
        folder="/srv/project",
        title="Fix monitor reconnect flake",
    )
    notifier = _TestNotifier()

    for sample in samples:
        candidate = gate.detect_plan(sample)
        print("detect_plan ->", bool(candidate), candidate.confidence if candidate else "-")

    candidate = gate.detect_plan(samples[1])
    if candidate:
        gate.request_approval(candidate, notifier, test_job)
        print("status[0s] ->", gate.check_approval(test_job.task_id))
        time.sleep(2.2)
        print("status[2.2s] ->", gate.check_approval(test_job.task_id))

    gate.register_approval(test_job.task_id, approved=False)
    print("status[manual reject] ->", gate.check_approval(test_job.task_id))
