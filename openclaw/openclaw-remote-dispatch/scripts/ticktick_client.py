"""Self-contained TickTick Open API V1 client. Python stdlib only."""

from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Any

from config import (
    TICKTICK_API_BASES,
    TICKTICK_CRED_PATH,
    TICKTICK_OAUTH_BASES,
    TICKTICK_REGION,
)

# ---------------------------------------------------------------------------
# Retry configuration
# ---------------------------------------------------------------------------
_RETRY_DELAYS = [5, 15, 30, 60]  # seconds
_MAX_RETRIES = len(_RETRY_DELAYS)

# Priority mapping (matching TickTick's integer values)
PRIORITY_MAP: dict[str, int] = {
    "none": 0,
    "low": 1,
    "medium": 3,
    "high": 5,
}

PRIORITY_REVERSE: dict[int, str] = {
    0: "none",
    1: "low",
    3: "medium",
    5: "high",
}


class TickTickError(Exception):
    """Base error for TickTick API failures."""


class AuthError(TickTickError):
    """Authentication / token errors."""


class RateLimitError(TickTickError):
    """API rate-limit exceeded after retries."""


class TickTickClient:
    """Minimal TickTick Open API V1 client (stdlib only).

    Reads OAuth2 tokens from the shared credential file written by the
    existing OpenClaw ticktick skill.  Handles token refresh automatically.
    """

    def __init__(
        self,
        cred_path: str | None = None,
        region: str | None = None,
    ) -> None:
        self._cred_path = Path(cred_path or TICKTICK_CRED_PATH)
        region = region or TICKTICK_REGION
        self._api_base = TICKTICK_API_BASES[region]
        self._oauth_base = TICKTICK_OAUTH_BASES[region]
        self._config: dict[str, Any] | None = None

    # ------------------------------------------------------------------
    # Credential management
    # ------------------------------------------------------------------

    def _load_config(self) -> dict[str, Any]:
        if self._config is not None:
            return self._config
        if not self._cred_path.exists():
            raise AuthError(
                f"Credential file not found: {self._cred_path}\n"
                "Run 'bun run ticktick.ts auth' in the ticktick skill, "
                "or set TICKTICK_CRED_PATH to an existing credential file."
            )
        raw = json.loads(self._cred_path.read_text())
        self._config = raw if isinstance(raw, dict) else {}
        return self._config

    def _save_config(self, config: dict[str, Any]) -> None:
        self._cred_path.parent.mkdir(parents=True, exist_ok=True)
        self._cred_path.write_text(json.dumps(config, indent=2))
        self._cred_path.chmod(0o600)
        self._config = config

    def _get_token(self) -> str:
        """Return a valid access token, refreshing if needed."""
        config = self._load_config()
        token = config.get("accessToken")
        if not token:
            raise AuthError(
                "No access token. Run 'bun run ticktick.ts auth' to authenticate."
            )

        # Refresh if expired (5-min buffer)
        expiry = config.get("tokenExpiry", 0)
        if expiry and time.time() * 1000 > expiry - 300_000:
            refresh = config.get("refreshToken")
            if not refresh:
                raise AuthError("Token expired and no refresh token available.")
            token = self._refresh_token(config)

        return token

    def _refresh_token(self, config: dict[str, Any]) -> str:
        creds = base64.b64encode(
            f"{config['clientId']}:{config['clientSecret']}".encode()
        ).decode()

        data = urllib.parse.urlencode(
            {
                "grant_type": "refresh_token",
                "refresh_token": config["refreshToken"],
            }
        ).encode()

        req = urllib.request.Request(
            f"{self._oauth_base}/token",
            data=data,
            headers={
                "Authorization": f"Basic {creds}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            raise AuthError(f"Token refresh failed: {e.code} {e.read().decode()}")

        config["accessToken"] = body["access_token"]
        if "refresh_token" in body:
            config["refreshToken"] = body["refresh_token"]
        config["tokenExpiry"] = int(time.time() * 1000) + body["expires_in"] * 1000
        self._save_config(config)
        return config["accessToken"]

    # ------------------------------------------------------------------
    # HTTP transport
    # ------------------------------------------------------------------

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        retry: int = 0,
    ) -> Any:
        token = self._get_token()
        url = f"{self._api_base}{path}"

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=payload, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                text = resp.read().decode()
                return json.loads(text) if text else {}
        except urllib.error.HTTPError as e:
            status = e.code
            err_text = e.read().decode()

            # Rate limit (429 or 500 with exceed_query_limit)
            is_rate_limit = status == 429 or (
                status == 500 and "exceed_query_limit" in err_text
            )
            if is_rate_limit and retry < _MAX_RETRIES:
                wait = _RETRY_DELAYS[retry]
                time.sleep(wait)
                return self._request(method, path, body, retry + 1)

            if is_rate_limit:
                raise RateLimitError(
                    "Rate limit exceeded after maximum retries. Wait a few minutes."
                )

            if status == 401:
                raise AuthError("Authentication expired. Re-authenticate.")
            if status == 404:
                raise TickTickError(f"Not found: {path}")

            raise TickTickError(f"API error {status}: {err_text}")

    # ------------------------------------------------------------------
    # Project endpoints
    # ------------------------------------------------------------------

    def list_projects(self) -> list[dict[str, Any]]:
        """GET /project — list all projects."""
        return self._request("GET", "/project")

    def get_project(self, project_id: str) -> dict[str, Any]:
        """GET /project/{id}."""
        return self._request("GET", f"/project/{project_id}")

    def get_project_data(self, project_id: str) -> dict[str, Any]:
        """GET /project/{id}/data — project + tasks + columns."""
        return self._request("GET", f"/project/{project_id}/data")

    def create_project(self, name: str, **kwargs: Any) -> dict[str, Any]:
        """POST /project — create a new project."""
        payload: dict[str, Any] = {"name": name, "kind": "TASK", **kwargs}
        return self._request("POST", "/project", payload)

    def find_project_by_name(self, name: str) -> dict[str, Any] | None:
        """Find project by name (case-insensitive)."""
        lower = name.lower()
        for p in self.list_projects():
            if p.get("name", "").lower() == lower:
                return p
        return None

    def ensure_project(self, name: str) -> dict[str, Any]:
        """Find or create a project by name."""
        project = self.find_project_by_name(name)
        if project is None:
            project = self.create_project(name)
        return project

    # ------------------------------------------------------------------
    # Task endpoints
    # ------------------------------------------------------------------

    def create_task(
        self,
        project_id: str,
        title: str,
        content: str = "",
        desc: str = "",
        priority: int = 0,
        items: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """POST /task — create a task."""
        payload: dict[str, Any] = {
            "projectId": project_id,
            "title": title,
            "content": content,
            "desc": desc,
            "priority": priority,
            **kwargs,
        }
        if items:
            payload["items"] = items
        return self._request("POST", "/task", payload)

    def update_task(self, task_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        """POST /task/{id} — partial update."""
        return self._request("POST", f"/task/{task_id}", fields)

    def complete_task(self, project_id: str, task_id: str) -> None:
        """POST /project/{pid}/task/{tid}/complete."""
        self._request("POST", f"/project/{project_id}/task/{task_id}/complete")

    def delete_task(self, project_id: str, task_id: str) -> None:
        """DELETE /project/{pid}/task/{tid}."""
        self._request("DELETE", f"/project/{project_id}/task/{task_id}")

    def get_task(self, project_id: str, task_id: str) -> dict[str, Any]:
        """GET /project/{pid}/task/{tid}."""
        return self._request("GET", f"/project/{project_id}/task/{task_id}")

    def update_project(self, project_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        """POST /project/{id} — partial update (name/color/etc.)."""
        return self._request("POST", f"/project/{project_id}", fields)

    def get_inbox_data(self) -> dict[str, Any]:
        """Get Inbox project data via project lookup or inbox endpoint."""
        projects = self.list_projects()
        inbox: dict[str, Any] | None = None

        for project in projects:
            name = str(project.get("name", "")).lower()
            kind = str(project.get("kind", ""))
            if name == "inbox" or kind == "INBOX":
                inbox = project
                break

        if inbox is None:
            return self._request("GET", "/project/inbox/data")

        inbox_id = str(inbox.get("id", "")).strip()
        if not inbox_id:
            return self._request("GET", "/project/inbox/data")

        return self.get_project_data(inbox_id)

    def find_task_by_id(self, task_id: str) -> dict[str, Any] | None:
        """Find a task by ID across all accessible projects."""
        projects = self.list_projects()

        for project in projects:
            project_id = str(project.get("id", "")).strip()
            if not project_id:
                continue

            try:
                data = self.get_project_data(project_id)
                tasks = data.get("tasks", [])
                if not isinstance(tasks, list):
                    continue

                for task in tasks:
                    if isinstance(task, dict) and str(task.get("id", "")) == task_id:
                        return {"task": task, "projectId": project_id}
            except TickTickError:
                continue

        return None

    def find_task_by_title(
        self,
        title: str,
        project_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Find task by exact title (case-insensitive) or ID."""
        projects = self.list_projects()
        if project_id:
            project_id_lower = project_id.lower()
            search_projects = [
                project
                for project in projects
                if str(project.get("id", "")) == project_id
                or str(project.get("name", "")).lower() == project_id_lower
            ]
        else:
            search_projects = projects

        lower_title = title.lower()
        is_id_search = len(title) == 24 and all(
            ch in "0123456789abcdefABCDEF" for ch in title
        )
        matches: list[dict[str, Any]] = []

        for project in search_projects:
            pid = str(project.get("id", "")).strip()
            if not pid:
                continue

            try:
                data = self.get_project_data(pid)
                tasks = data.get("tasks", [])
                if not isinstance(tasks, list):
                    continue

                for task in tasks:
                    if not isinstance(task, dict):
                        continue

                    task_title = str(task.get("title", "")).lower()
                    task_id = str(task.get("id", ""))
                    if task_title == lower_title or task_id == title:
                        matches.append(
                            {
                                "task": task,
                                "projectId": pid,
                                "projectName": str(project.get("name", "")),
                            }
                        )
            except TickTickError:
                continue

        if not matches:
            return None

        if is_id_search or len(matches) == 1:
            return {
                "task": matches[0]["task"],
                "projectId": matches[0]["projectId"],
            }

        match_list = "\n".join(
            f'  [{str(m["task"].get("id", ""))[:8]}] "{m["task"].get("title", "")}" '
            f'in project "{m["projectName"]}"'
            for m in matches
        )
        raise TickTickError(
            f'Multiple tasks found with name "{title}":\n{match_list}\n\n'
            "Please use the task ID instead of the name to specify which task."
        )

    def get_all_tasks(self, project_id: str | None = None) -> list[dict[str, Any]]:
        """Get all tasks across projects, optionally filtered by project."""
        projects = self.list_projects()
        if project_id:
            project_id_lower = project_id.lower()
            search_projects = [
                project
                for project in projects
                if str(project.get("id", "")) == project_id
                or str(project.get("name", "")).lower() == project_id_lower
            ]
        else:
            search_projects = projects

        all_tasks: list[dict[str, Any]] = []
        for project in search_projects:
            pid = str(project.get("id", "")).strip()
            if not pid:
                continue

            try:
                data = self.get_project_data(pid)
                tasks = data.get("tasks", [])
                if not isinstance(tasks, list):
                    continue

                for task in tasks:
                    if isinstance(task, dict):
                        all_tasks.append(task)
            except TickTickError:
                continue

        return all_tasks

    def abandon_task(self, project_id: str, task_id: str) -> dict[str, Any]:
        """Mark a task as abandoned (status -1 / won't do)."""
        return self.update_task(
            task_id,
            {
                "id": task_id,
                "projectId": project_id,
                "status": -1,
            },
        )

    def batch_tasks(self, batch: dict[str, Any]) -> dict[str, Any]:
        """POST /batch/task — add/update/delete task operations."""
        return self._request("POST", "/batch/task", batch)
