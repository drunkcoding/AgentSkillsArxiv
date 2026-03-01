from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class ToolEvent:
    tool_name: str
    tool_input: str
    call_id: str
    status: str
    error_text: str
    timestamp: float


@dataclass
class TextEvent:
    text: str
    block_type: str
    message_id: str
    timestamp: float


@dataclass
class StatusEvent:
    event_type: str
    payload: dict
    timestamp: float


def _to_text(value: Any) -> str:
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(value)


def _timestamp(node: dict[str, Any]) -> float:
    for key in ("timestamp", "ts", "time", "createdAt", "created_at"):
        value = node.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                pass
    return time.time()


def _tool_event_from_part(part: dict[str, Any], fallback_ts: float) -> ToolEvent | None:
    part_type = _to_text(part.get("type", "")).lower()
    hinted = any(
        key in part for key in ("tool", "tool_name", "toolName", "tool_call_id", "toolCallId", "call_id", "callId")
    )
    if "tool" not in part_type and "function" not in part_type and not hinted:
        return None

    tool_name = ""
    for key in ("tool_name", "toolName", "name"):
        value = part.get(key)
        if isinstance(value, str) and value.strip():
            tool_name = value.strip()
            break
    if not tool_name and isinstance(part.get("tool"), dict):
        tool_meta = part["tool"]
        for key in ("tool_name", "toolName", "name"):
            value = tool_meta.get(key)
            if isinstance(value, str) and value.strip():
                tool_name = value.strip()
                break
    if not tool_name:
        return None

    tool_input = ""
    for key in ("input", "tool_input", "toolInput", "arguments", "args", "params"):
        if key in part:
            tool_input = _to_text(part[key])
            break
    if not tool_input and isinstance(part.get("tool"), dict):
        for key in ("input", "arguments", "args", "params"):
            if key in part["tool"]:
                tool_input = _to_text(part["tool"][key])
                break

    call_id = ""
    for key in ("call_id", "callId", "tool_call_id", "toolCallId", "id"):
        value = part.get(key)
        if isinstance(value, str) and value.strip():
            call_id = value.strip()
            break

    error_text = ""
    for key in ("error_text", "errorText", "error", "message"):
        value = part.get(key)
        if isinstance(value, str) and value.strip():
            error_text = value.strip()
            break

    raw_status = _to_text(part.get("status", part.get("state", "pending"))).lower()
    if error_text or any(token in raw_status for token in ("error", "failed", "fail")):
        status = "error"
    elif any(token in raw_status for token in ("completed", "complete", "done", "success")):
        status = "completed"
    elif any(token in raw_status for token in ("running", "active", "progress", "execut")):
        status = "running"
    else:
        status = "pending"

    return ToolEvent(tool_name, tool_input, call_id, status, error_text, _timestamp(part) if part else fallback_ts)


def _text_event_from_payload(payload: dict[str, Any], fallback_ts: float) -> TextEvent | None:
    message_id = ""
    for key in ("message_id", "messageId", "id"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            message_id = value.strip()
            break

    for node in (payload.get("delta"), payload.get("part"), payload):
        if not isinstance(node, dict):
            continue
        type_raw = _to_text(node.get("block_type", node.get("type", "text"))).lower()
        block_type = "thinking" if "thinking" in type_raw else "reasoning" if "reason" in type_raw else "text"

        text = node.get("text")
        if isinstance(text, str) and text.strip():
            return TextEvent(text.strip(), block_type, message_id, _timestamp(node))

        content = node.get("content")
        if isinstance(content, str) and content.strip():
            return TextEvent(content.strip(), block_type, message_id, _timestamp(node) if node else fallback_ts)
        if isinstance(content, list):
            pieces = [item.get("text", "").strip() for item in content if isinstance(item, dict)]
            merged = "\n".join(piece for piece in pieces if piece)
            if merged:
                return TextEvent(merged, block_type, message_id, _timestamp(node) if node else fallback_ts)

    return None


def extract_tool_from_parts(parts: list[dict]) -> list[ToolEvent]:
    ts = time.time()
    events: list[ToolEvent] = []
    for part in parts:
        if isinstance(part, dict):
            event = _tool_event_from_part(part, ts)
            if event is not None:
                events.append(event)
    return events


def normalize(raw_event: dict) -> ToolEvent | TextEvent | StatusEvent | None:
    if not isinstance(raw_event, dict):
        return None

    event_name = _to_text(raw_event.get("event", "")).strip()
    payload_any = raw_event.get("data", {})
    payload = payload_any if isinstance(payload_any, dict) else {"raw": payload_any}
    ts = _timestamp(payload)

    if event_name == "assistant.message.completed":
        return StatusEvent("completed", payload, ts)
    if event_name == "session.idle":
        return StatusEvent("idle", payload, ts)
    if event_name == "question.asked":
        return StatusEvent("question", payload, ts)

    if event_name == "message.part.updated":
        parts = payload.get("parts")
        if not isinstance(parts, list) and isinstance(payload.get("message"), dict):
            parts = payload["message"].get("parts")
        if isinstance(parts, list):
            events = extract_tool_from_parts([part for part in parts if isinstance(part, dict)])
            return events[-1] if events else None
        return None

    if event_name == "message.part.delta":
        for candidate in (payload.get("part"), payload.get("delta"), payload):
            if isinstance(candidate, dict):
                tool_event = _tool_event_from_part(candidate, ts)
                if tool_event is not None:
                    return tool_event
        return _text_event_from_payload(payload, ts)

    if "error" in event_name.lower():
        return StatusEvent("error", payload, ts)

    log.debug("Ignoring event: %s", event_name)
    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    samples = [
        {
            "event": "message.part.delta",
            "data": {"part": {"type": "tool_call", "toolName": "bash", "toolCallId": "c1", "input": {"command": "ls"}, "status": "running"}},
        },
        {"event": "message.part.delta", "data": {"part": {"type": "text", "text": "Let me check.", "messageId": "m1"}}},
        {
            "event": "message.part.updated",
            "data": {"parts": [{"type": "tool_result", "tool_name": "grep", "call_id": "c2", "input": {"pattern": "err"}, "status": "completed"}]},
        },
        {"event": "assistant.message.completed", "data": {"id": "m-final"}},
        {"event": "session.idle", "data": {"session": "ses_1"}},
        {"event": "question.asked", "data": {"question": "Proceed?"}},
    ]
    for sample in samples:
        print(sample["event"], "->", normalize(sample))
