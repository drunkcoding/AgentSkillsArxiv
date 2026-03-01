from __future__ import annotations

import json
import logging
import os
import re
import time
import urllib.error
import urllib.request
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from opencode_client import OpenCodeClient

log = logging.getLogger(__name__)

_DEFAULT_PROVIDERS = "anthropic:claude-haiku-4-5,openai:gpt-5.1,openai:gpt-4o"
_FAIL_THRESHOLD = 3
_COOLDOWN_SECONDS = 600
_STATE: dict[str, dict[str, float | int]] = {}


def _provider_chain() -> list[tuple[str, str]]:
    raw = os.environ.get("DISPATCH_LLM_PROVIDERS", _DEFAULT_PROVIDERS)
    chain: list[tuple[str, str]] = []
    for item in raw.split(","):
        token = item.strip()
        if not token or ":" not in token:
            continue
        provider, model = token.split(":", 1)
        provider = provider.strip().lower()
        model = model.strip()
        if provider and model:
            chain.append((provider, model))
    return chain


def _timeout_seconds() -> float:
    raw = os.environ.get("DISPATCH_LLM_TIMEOUT", "5")
    try:
        return max(1.0, float(raw))
    except ValueError:
        return 5.0


def _state_for(provider_key: str) -> dict[str, float | int]:
    state = _STATE.get(provider_key)
    if state is None:
        state = {"fails": 0, "open_until": 0.0}
        _STATE[provider_key] = state
    return state


def _provider_open(provider_key: str) -> bool:
    state = _state_for(provider_key)
    return time.time() < float(state.get("open_until", 0.0))


def _record_success(provider_key: str) -> None:
    state = _state_for(provider_key)
    state["fails"] = 0
    state["open_until"] = 0.0


def _record_failure(provider_key: str) -> None:
    state = _state_for(provider_key)
    fails = int(state.get("fails", 0)) + 1
    state["fails"] = fails
    if fails >= _FAIL_THRESHOLD:
        state["open_until"] = time.time() + _COOLDOWN_SECONDS
        state["fails"] = 0


def _http_post_json(
    url: str,
    headers: dict[str, str],
    body: dict[str, Any],
    timeout: float,
) -> dict[str, Any]:
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {details}") from exc
    except (urllib.error.URLError, OSError) as exc:
        raise RuntimeError(f"HTTP request failed: {exc}") from exc


def _extract_anthropic_text(data: dict[str, Any]) -> str:
    chunks: list[str] = []
    for part in data.get("content", []) if isinstance(data.get("content"), list) else []:
        if isinstance(part, dict) and isinstance(part.get("text"), str):
            chunks.append(part["text"])
    return "\n".join(chunks).strip()


def _extract_openai_text(data: dict[str, Any]) -> str:
    choices = data.get("choices", [])
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0] if isinstance(choices[0], dict) else {}
    message = first.get("message", {}) if isinstance(first, dict) else {}
    content = message.get("content") if isinstance(message, dict) else ""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        text_parts = [
            str(item.get("text", "")).strip()
            for item in content
            if isinstance(item, dict) and isinstance(item.get("text"), str)
        ]
        return "\n".join(part for part in text_parts if part)
    return ""


def _extract_text_from_obj(node: Any) -> str:
    if isinstance(node, str):
        return node.strip()
    if isinstance(node, list):
        for item in node:
            text = _extract_text_from_obj(item)
            if text:
                return text
        return ""
    if isinstance(node, dict):
        if isinstance(node.get("text"), str):
            return node["text"].strip()
        for key in ("content", "message", "delta", "output", "raw", "data", "result"):
            if key in node:
                text = _extract_text_from_obj(node[key])
                if text:
                    return text
        for value in node.values():
            text = _extract_text_from_obj(value)
            if text:
                return text
    return ""


def _extract_json_dict(text: str) -> dict[str, Any] | None:
    candidates: list[str] = [text.strip()]

    fenced = re.findall(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.IGNORECASE | re.DOTALL)
    candidates.extend(chunk.strip() for chunk in fenced if chunk.strip())

    brace_matches = re.findall(r"\{.*?\}", text, flags=re.DOTALL)
    candidates.extend(chunk.strip() for chunk in brace_matches if chunk.strip())

    for candidate in candidates:
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _call_anthropic(model: str, system_prompt: str, user_prompt: str, timeout: float) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return ""
    data = _http_post_json(
        "https://api.anthropic.com/v1/messages",
        {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        {
            "model": model,
            "max_tokens": 256,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        },
        timeout,
    )
    return _extract_anthropic_text(data)


def _call_openai(model: str, system_prompt: str, user_prompt: str, timeout: float) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return ""
    data = _http_post_json(
        "https://api.openai.com/v1/chat/completions",
        {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        {
            "model": model,
            "max_tokens": 256,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        },
        timeout,
    )
    return _extract_openai_text(data)


def _call_subscription(
    provider: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    opencode_client: OpenCodeClient | None,
    timeout: float,
) -> str:
    if opencode_client is None:
        return ""

    session_id = ""
    try:
        session_id = opencode_client.create_session(f"dispatch-{provider}-{model}")
        prompt = (
            "Follow the system instruction and return JSON only.\n\n"
            f"System:\n{system_prompt}\n\n"
            f"User:\n{user_prompt}"
        )
        result = opencode_client.prompt_sync(
            session_id,
            prompt,
            agent="build",
            timeout=max(5, int(timeout)),
        )
        return _extract_text_from_obj(result)
    finally:
        if session_id:
            try:
                opencode_client.delete_session(session_id)
            except Exception:  # noqa: BLE001
                log.warning("Failed deleting temporary session %s", session_id)


def classify(
    system_prompt: str,
    user_prompt: str,
    opencode_client: OpenCodeClient | None = None,
) -> dict[str, Any] | None:
    timeout = _timeout_seconds()
    for provider, model in _provider_chain():
        provider_key = f"{provider}:{model}"
        if _provider_open(provider_key):
            log.debug("Skipping provider %s due to open circuit", provider_key)
            continue

        try:
            if provider == "anthropic":
                text = _call_anthropic(model, system_prompt, user_prompt, timeout)
                if not text:
                    text = _call_subscription(
                        provider,
                        model,
                        system_prompt,
                        user_prompt,
                        opencode_client,
                        timeout,
                    )
            elif provider == "openai":
                text = _call_openai(model, system_prompt, user_prompt, timeout)
                if not text:
                    text = _call_subscription(
                        provider,
                        model,
                        system_prompt,
                        user_prompt,
                        opencode_client,
                        timeout,
                    )
            else:
                log.warning("Unknown provider '%s' in chain", provider)
                _record_failure(provider_key)
                continue

            parsed = _extract_json_dict(text)
            if parsed is None:
                raise RuntimeError("provider returned non-JSON output")

            _record_success(provider_key)
            return parsed
        except Exception as exc:  # noqa: BLE001
            _record_failure(provider_key)
            log.warning("LLM provider %s failed: %s", provider_key, exc)

    return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    test_system = "Return strict JSON with keys: intent and confidence."
    test_user = "Task title: Fix flaky reconnect logic in dispatcher monitor"
    result = classify(test_system, test_user)
    print("classify() ->", result)
