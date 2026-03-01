from __future__ import annotations

import json
import logging
import os
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class SessionNode:
    session_id: str
    task_id: str
    host: str
    folder: str
    title: str
    agent: str
    summary_text: str = ""
    summary_message_id: str = ""
    resume_message_id: str = ""
    todo_items: list[str] = field(default_factory=list)
    diff_stats: dict[str, int] = field(default_factory=dict)
    completed_at: float = 0.0
    parent_session_id: str = ""
    children: list[str] = field(default_factory=list)
    related_sessions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class SessionRegistry:
    def __init__(self, path: str | None = None) -> None:
        default_path = os.environ.get(
            "DISPATCH_SESSION_REGISTRY_PATH",
            "~/.openclaw/session-registry.json",
        )
        self._path = Path(path or default_path).expanduser()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def add(self, node: SessionNode) -> None:
        with self._lock:
            data = self._load()
            data[node.session_id] = node
            self._save(data)

    def get(self, session_id: str) -> SessionNode | None:
        with self._lock:
            return self._load().get(session_id)

    def update(self, session_id: str, **fields: Any) -> None:
        with self._lock:
            data = self._load()
            node = data.get(session_id)
            if node is None:
                log.warning("Session %s not found in registry", session_id)
                return

            valid = SessionNode.__dataclass_fields__
            for key, value in fields.items():
                if key not in valid:
                    log.warning("Skipping unknown SessionNode field: %s", key)
                    continue
                setattr(node, key, value)

            data[session_id] = node
            self._save(data)

    def list_by_host_folder(self, host: str, folder: str) -> list[SessionNode]:
        with self._lock:
            data = self._load()

        result = [
            node
            for node in data.values()
            if node.host == host and node.folder == folder
        ]
        result.sort(key=lambda item: item.completed_at, reverse=True)
        return result

    def list_recent(self, limit: int = 20) -> list[SessionNode]:
        with self._lock:
            nodes = list(self._load().values())

        nodes.sort(key=lambda item: item.completed_at, reverse=True)
        return nodes[: max(0, limit)]

    def search(self, query: str) -> list[SessionNode]:
        normalized = query.strip().lower()
        if not normalized:
            return []

        with self._lock:
            nodes = list(self._load().values())

        result = [
            node
            for node in nodes
            if normalized in node.title.lower()
            or normalized in node.summary_text.lower()
        ]
        result.sort(key=lambda item: item.completed_at, reverse=True)
        return result

    def remove(self, session_id: str) -> None:
        with self._lock:
            data = self._load()
            removed = data.pop(session_id, None)
            if removed is None:
                return

            for node in data.values():
                if node.parent_session_id == session_id:
                    node.parent_session_id = ""
                if session_id in node.children:
                    node.children = [child for child in node.children if child != session_id]
                if session_id in node.related_sessions:
                    node.related_sessions = [
                        related for related in node.related_sessions if related != session_id
                    ]

            self._save(data)

    def _load(self) -> dict[str, SessionNode]:
        if not self._path.exists():
            return {}

        try:
            raw = json.loads(self._path.read_text())
        except (OSError, json.JSONDecodeError):
            log.warning("Failed to read session registry, returning empty state")
            return {}

        if not isinstance(raw, dict):
            return {}

        parsed: dict[str, SessionNode] = {}
        valid = SessionNode.__dataclass_fields__
        required_defaults = {
            "task_id": "",
            "host": "",
            "folder": "",
            "title": "",
            "agent": "",
        }

        for session_id, item in raw.items():
            if not isinstance(item, dict):
                continue

            clean = {k: v for k, v in item.items() if k in valid}
            clean["session_id"] = str(clean.get("session_id") or session_id)
            for key, default_value in required_defaults.items():
                clean[key] = str(clean.get(key, default_value) or default_value)

            if not isinstance(clean.get("todo_items"), list):
                clean["todo_items"] = []
            else:
                clean["todo_items"] = [str(value) for value in clean["todo_items"]]

            if not isinstance(clean.get("children"), list):
                clean["children"] = []
            else:
                clean["children"] = [str(value) for value in clean["children"]]

            if not isinstance(clean.get("related_sessions"), list):
                clean["related_sessions"] = []
            else:
                clean["related_sessions"] = [str(value) for value in clean["related_sessions"]]

            if not isinstance(clean.get("diff_stats"), dict):
                clean["diff_stats"] = {}
            else:
                clean["diff_stats"] = {
                    str(k): int(v)
                    for k, v in clean["diff_stats"].items()
                    if isinstance(v, int)
                }

            if not isinstance(clean.get("metadata"), dict):
                clean["metadata"] = {}

            completed_at = clean.get("completed_at", 0.0)
            try:
                clean["completed_at"] = float(completed_at)
            except (TypeError, ValueError):
                clean["completed_at"] = 0.0

            try:
                parsed[clean["session_id"]] = SessionNode(**clean)
            except TypeError:
                log.warning("Skipping invalid SessionNode entry %s", session_id)

        return parsed

    def _save(self, data: dict[str, SessionNode]) -> None:
        payload = {session_id: asdict(node) for session_id, node in data.items()}
        tmp_path = self._path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str))
        tmp_path.replace(self._path)


if __name__ == "__main__":
    import tempfile

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    demo_path = Path(tempfile.gettempdir()) / f"session-registry-demo-{int(time.time())}.json"
    registry = SessionRegistry(str(demo_path))

    node1 = SessionNode(
        session_id="ses_001",
        task_id="task_001",
        host="devbox",
        folder="/srv/app",
        title="Fix reconnect flake",
        agent="build",
        summary_text="Added reconnect retry guard",
        completed_at=time.time(),
    )
    node2 = SessionNode(
        session_id="ses_002",
        task_id="task_002",
        host="devbox",
        folder="/srv/app",
        title="Add timeout plan gate",
        agent="plan",
        summary_text="Proposed timeout + fallback strategy",
        completed_at=time.time() - 100,
    )

    registry.add(node1)
    registry.add(node2)
    registry.update("ses_001", resume_message_id="msg_resume_123", todo_items=["test", "ship"])

    print("get(ses_001) ->", registry.get("ses_001"))
    print("list_by_host_folder ->", [n.session_id for n in registry.list_by_host_folder("devbox", "/srv/app")])
    print("list_recent ->", [n.session_id for n in registry.list_recent(5)])
    print("search('timeout') ->", [n.session_id for n in registry.search("timeout")])

    registry.remove("ses_002")
    print("after remove ->", [n.session_id for n in registry.list_recent(5)])

    try:
        demo_path.unlink(missing_ok=True)
    except OSError:
        pass
