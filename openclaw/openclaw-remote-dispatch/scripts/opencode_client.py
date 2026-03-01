"""Self-contained OpenCode Serve HTTP client. Python stdlib only."""

from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from typing import Any, Generator


class OpenCodeError(Exception):
    """Error communicating with OpenCode Serve."""


class OpenCodeClient:
    """HTTP client for a running opencode serve instance.

    Connects via a local-forwarded SSH tunnel port.
    Auth uses HTTP Basic (username='opencode', password=<one-time>).
    """

    def __init__(self, base_url: str, password: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._auth = base64.b64encode(
            f"opencode:{password}".encode()
        ).decode()

    # ------------------------------------------------------------------
    # HTTP transport
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        timeout: int = 30,
    ) -> Any:
        url = f"{self._base_url}{path}"
        headers = {
            "Authorization": f"Basic {self._auth}",
            "Content-Type": "application/json",
        }
        payload = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=payload, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                text = resp.read().decode()
                return json.loads(text) if text else {}
        except urllib.error.HTTPError as e:
            raise OpenCodeError(
                f"OpenCode API error {e.code}: {e.read().decode()}"
            )
        except (urllib.error.URLError, OSError) as e:
            raise OpenCodeError(f"Connection failed: {e}")

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health(self) -> bool:
        """GET /global/health — returns True if server is reachable."""
        try:
            self._request("GET", "/global/health", timeout=5)
            return True
        except OpenCodeError:
            return False

    def wait_healthy(self, timeout: int = 30) -> bool:
        """Poll health until ready or timeout."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.health():
                return True
            time.sleep(1)
        return False

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def create_session(self, title: str = "") -> str:
        """POST /session — create session, return session ID."""
        body: dict[str, Any] = {}
        if title:
            body["title"] = title
        result = self._request("POST", "/session", body)
        # Response shape: { "id": "ses_...", ... }
        return result.get("id", result.get("sessionID", ""))

    def list_sessions(self) -> list[dict[str, Any]]:
        """GET /session — list all sessions."""
        return self._request("GET", "/session")

    def delete_session(self, session_id: str) -> None:
        """DELETE /session/{id}."""
        self._request("DELETE", f"/session/{session_id}")

    # ------------------------------------------------------------------
    # Prompting
    # ------------------------------------------------------------------

    def prompt_sync(
        self,
        session_id: str,
        text: str,
        agent: str = "build",
        timeout: int = 600,
    ) -> dict[str, Any]:
        """POST /session/{id}/message — synchronous prompt (blocks until done)."""
        body: dict[str, Any] = {"parts": [{"type": "text", "text": text}]}
        if agent:
            body["agent"] = agent
        return self._request(
            "POST", f"/session/{session_id}/message", body, timeout=timeout
        )

    def prompt_async(
        self,
        session_id: str,
        text: str,
        agent: str = "build",
    ) -> dict[str, Any]:
        """POST /session/{id}/prompt_async — non-blocking prompt, returns 204."""
        body: dict[str, Any] = {"parts": [{"type": "text", "text": text}]}
        if agent:
            body["agent"] = agent
        return self._request("POST", f"/session/{session_id}/prompt_async", body)

    # ------------------------------------------------------------------
    # Monitoring
    # ------------------------------------------------------------------

    def get_status(self) -> dict[str, Any]:
        """GET /session/status — all sessions status."""
        return self._request("GET", "/session/status")

    def get_session_status(self, session_id: str) -> dict[str, Any]:
        """GET /session/{id} — single session details."""
        return self._request("GET", f"/session/{session_id}")

    def get_messages(self, session_id: str) -> list[dict[str, Any]]:
        """GET /session/{id}/message — list messages in session."""
        return self._request("GET", f"/session/{session_id}/message")

    def get_diff(self, session_id: str) -> dict[str, Any]:
        """GET /session/{id}/diff — file changes in session."""
        return self._request("GET", f"/session/{session_id}/diff")

    def abort(self, session_id: str) -> None:
        """POST /session/{id}/abort — stop a running session."""
        self._request("POST", f"/session/{session_id}/abort")

    # ------------------------------------------------------------------
    # SSE event stream
    # ------------------------------------------------------------------

    def stream_events(
        self, timeout: int = 300
    ) -> Generator[dict[str, Any], None, None]:
        """GET /global/event — yields parsed SSE events.

        Each yielded dict has keys: 'event' (type) and 'data' (parsed JSON).
        Events include: message.part.delta, question.asked, session.updated, etc.
        """
        url = f"{self._base_url}/global/event"
        headers = {"Authorization": f"Basic {self._auth}"}
        req = urllib.request.Request(url, headers=headers)

        try:
            resp = urllib.request.urlopen(req, timeout=timeout)
        except (urllib.error.URLError, OSError) as e:
            raise OpenCodeError(f"SSE connection failed: {e}")

        event_type = ""
        data_lines: list[str] = []

        try:
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace").rstrip("\n\r")

                if line.startswith("event:"):
                    event_type = line[6:].strip()
                elif line.startswith("data:"):
                    data_lines.append(line[5:].strip())
                elif line == "":
                    # End of event
                    if event_type and data_lines:
                        raw_data = "\n".join(data_lines)
                        try:
                            parsed = json.loads(raw_data)
                        except json.JSONDecodeError:
                            parsed = {"raw": raw_data}
                        yield {"event": event_type, "data": parsed}
                    event_type = ""
                    data_lines = []
        except (OSError, StopIteration):
            pass
        finally:
            resp.close()
