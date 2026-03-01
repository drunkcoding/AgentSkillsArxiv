from __future__ import annotations

import hashlib
import importlib
import json
import logging
import re
import time
from collections import deque
from dataclasses import dataclass

try:
    fuzz = importlib.import_module("rapidfuzz.fuzz")
except ImportError:
    fuzz = None

from event_normalizer import ToolEvent, TextEvent

log = logging.getLogger(__name__)

_STALL_RE = re.compile(r"(?:i apologize|let me try again|i['’]?m still working|let me check)", re.IGNORECASE)


@dataclass
class StuckSignal:
    kind: str
    description: str
    evidence: list[str]
    confidence: float


class StuckDetector:
    def __init__(self, window_size: int = 20, repeat_threshold: int = 3, jitter_similarity: float = 0.85) -> None:
        self.window_size = max(2, int(window_size))
        self.repeat_threshold = max(2, int(repeat_threshold))
        self.jitter_similarity = max(0.0, min(1.0, float(jitter_similarity)))
        self._events: deque[ToolEvent | TextEvent] = deque(maxlen=self.window_size)
        self._last_error_tool = ""
        self._error_streak = 0

    def feed(self, event: ToolEvent | TextEvent) -> StuckSignal | None:
        self._events.append(event)
        if isinstance(event, ToolEvent):
            return self._detect_error_streak(event) or self._detect_exact_repeat(event) or self._detect_arg_jitter(event)
        return self._detect_stall_text()

    def _normalize_input(self, value: str) -> str:
        text = value.strip()
        if not text:
            return ""
        try:
            text = json.dumps(json.loads(text), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        except (json.JSONDecodeError, TypeError, ValueError):
            pass
        return re.sub(r"\s+", " ", text).strip().lower()

    def _hash_key(self, event: ToolEvent) -> str:
        raw = f"{event.tool_name.lower()}|{self._normalize_input(event.tool_input)}"
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()

    def _detect_exact_repeat(self, event: ToolEvent) -> StuckSignal | None:
        key = self._hash_key(event)
        tool_events = [item for item in self._events if isinstance(item, ToolEvent)]
        matches = [item for item in tool_events if self._hash_key(item) == key]
        if len(matches) < self.repeat_threshold:
            return None
        evidence = [
            f"{item.tool_name} call={item.call_id or '-'} input={self._normalize_input(item.tool_input)[:120]}"
            for item in matches[-self.repeat_threshold :]
        ]
        confidence = min(1.0, 0.75 + 0.05 * (len(matches) - self.repeat_threshold))
        return StuckSignal(
            kind="exact_repeat",
            description=f"Tool '{event.tool_name}' repeated exact input {len(matches)} times",
            evidence=evidence,
            confidence=confidence,
        )

    def _detect_arg_jitter(self, event: ToolEvent) -> StuckSignal | None:
        if fuzz is None:
            return None
        current = self._normalize_input(event.tool_input)
        if not current:
            return None

        threshold_pct = self.jitter_similarity * 100.0
        candidates = [
            item for item in self._events if isinstance(item, ToolEvent) and item.tool_name == event.tool_name
        ]

        similar = 1
        evidence = [f"seed={current[:120]}"]
        for prior in candidates[:-1]:
            prior_text = self._normalize_input(prior.tool_input)
            if not prior_text:
                continue
            score = float(fuzz.token_sort_ratio(current, prior_text))
            if score >= threshold_pct:
                similar += 1
                evidence.append(f"score={score:.1f} prior={prior_text[:120]}")

        if similar < self.repeat_threshold:
            return None

        confidence = min(1.0, 0.65 + 0.08 * (similar - self.repeat_threshold))
        return StuckSignal(
            kind="arg_jitter",
            description=f"Tool '{event.tool_name}' called with jittered but similar args {similar} times",
            evidence=evidence[-self.repeat_threshold :],
            confidence=confidence,
        )

    def _detect_error_streak(self, event: ToolEvent) -> StuckSignal | None:
        if event.status.lower() == "error":
            if event.tool_name == self._last_error_tool:
                self._error_streak += 1
            else:
                self._last_error_tool = event.tool_name
                self._error_streak = 1
        else:
            self._last_error_tool = ""
            self._error_streak = 0
            return None

        if self._error_streak < self.repeat_threshold:
            return None

        evidence = [
            f"call={item.call_id or '-'} error={item.error_text or '<empty>'}"
            for item in self._events
            if isinstance(item, ToolEvent)
            and item.tool_name == event.tool_name
            and item.status.lower() == "error"
        ]
        confidence = min(1.0, 0.8 + 0.04 * (self._error_streak - self.repeat_threshold))
        return StuckSignal(
            kind="error_streak",
            description=f"Tool '{event.tool_name}' failed {self._error_streak} consecutive times",
            evidence=evidence[-self.repeat_threshold :],
            confidence=confidence,
        )

    def _detect_stall_text(self) -> StuckSignal | None:
        matches = [
            item for item in self._events if isinstance(item, TextEvent) and _STALL_RE.search(item.text)
        ]
        if len(matches) < self.repeat_threshold:
            return None
        evidence = [item.text.strip()[:160] for item in matches[-self.repeat_threshold :]]
        confidence = min(1.0, 0.6 + 0.07 * (len(matches) - self.repeat_threshold))
        return StuckSignal(
            kind="stall_text",
            description=f"Stall-like assistant text repeated {len(matches)} times",
            evidence=evidence,
            confidence=confidence,
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    now = time.time()

    exact_detector = StuckDetector(window_size=10, repeat_threshold=3)
    exact = None
    for i in range(3):
        exact = exact_detector.feed(ToolEvent("bash", '{"command":"ls -la"}', f"ex-{i}", "running", "", now + i))
    print("exact_repeat ->", exact)

    jitter_detector = StuckDetector(window_size=10, repeat_threshold=3, jitter_similarity=0.8)
    jitter = None
    for i, text in enumerate(["grep -R error src/", "grep src/ -R error", "grep  -R  error   src"]):
        jitter = jitter_detector.feed(ToolEvent("bash", text, f"jit-{i}", "running", "", now + 10 + i))
    print("arg_jitter ->", jitter if fuzz is not None else "rapidfuzz unavailable")

    error_detector = StuckDetector(window_size=10, repeat_threshold=3)
    streak = None
    for i in range(3):
        streak = error_detector.feed(
            ToolEvent("read", f'{{"filePath":"/missing-{i}.txt"}}', f"err-{i}", "error", "File not found", now + 20 + i)
        )
    print("error_streak ->", streak)

    stall_detector = StuckDetector(window_size=10, repeat_threshold=3)
    stall = None
    for i, text in enumerate(
        [
            "I apologize, let me try again.",
            "I'm still working, let me check one more thing.",
            "I apologize, let me check and retry.",
        ]
    ):
        stall = stall_detector.feed(TextEvent(text, "text", f"m-{i}", now + 30 + i))
    print("stall_text ->", stall)
