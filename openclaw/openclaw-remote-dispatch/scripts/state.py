"""Persistent job state store (JSON + file locking)."""

from __future__ import annotations

import fcntl
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from config import STATE_PATH

log = logging.getLogger(__name__)


@dataclass
class Job:
    """State of a single dispatch job."""

    task_id: str
    project_id: str
    host: str
    folder: str
    title: str
    ssh_port: int = 0
    local_port: int = 0
    password: str = ""
    opencode_session_id: str = ""
    status: str = "pending"  # pending | running | blocked | done | failed
    retries: int = 0
    started_at: float = 0.0
    last_event_at: float = 0.0
    notify_to: str = ""
    channel: str = "whatsapp"
    error: str = ""


@dataclass
class StateData:
    """Top-level state file structure."""

    jobs: dict[str, Job] = field(default_factory=dict)
    daemon_pid: int = 0
    last_poll: float = 0.0


class StateStore:
    """Thread-safe JSON state with file locking."""

    def __init__(self, path: str | None = None) -> None:
        self._path = Path(path or STATE_PATH)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _read_raw(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        return json.loads(self._path.read_text())

    def _write_raw(self, data: dict[str, Any]) -> None:
        tmp = self._path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, default=str))
        tmp.replace(self._path)

    def load(self) -> StateData:
        """Load state from disk with file lock."""
        try:
            raw = self._read_raw()
        except (json.JSONDecodeError, OSError):
            log.warning("Corrupt state file, starting fresh")
            return StateData()

        state = StateData(
            daemon_pid=raw.get("daemon_pid", 0),
            last_poll=raw.get("last_poll", 0.0),
        )

        for task_id, job_data in raw.get("jobs", {}).items():
            state.jobs[task_id] = Job(**{
                k: v
                for k, v in job_data.items()
                if k in Job.__dataclass_fields__
            })

        return state

    def save(self, state: StateData) -> None:
        """Persist state to disk with atomic write."""
        raw: dict[str, Any] = {
            "daemon_pid": state.daemon_pid,
            "last_poll": state.last_poll,
            "jobs": {
                tid: asdict(job) for tid, job in state.jobs.items()
            },
        }
        self._write_raw(raw)

    def update_job(self, task_id: str, **fields: Any) -> None:
        """Load, update a single job, save."""
        state = self.load()
        job = state.jobs.get(task_id)
        if job is None:
            log.warning("Job %s not found in state", task_id)
            return
        for k, v in fields.items():
            if hasattr(job, k):
                setattr(job, k, v)
        state.jobs[task_id] = job
        self.save(state)

    def add_job(self, job: Job) -> None:
        """Add a new job to state."""
        state = self.load()
        state.jobs[job.task_id] = job
        self.save(state)

    def remove_job(self, task_id: str) -> None:
        """Remove a job from state."""
        state = self.load()
        state.jobs.pop(task_id, None)
        self.save(state)

    def get_active_jobs(self) -> dict[str, Job]:
        """Return jobs with status in (pending, running)."""
        state = self.load()
        return {
            tid: job
            for tid, job in state.jobs.items()
            if job.status in ("pending", "running")
        }

    def cleanup_finished(self, max_age: float = 86400 * 7) -> int:
        """Remove done/failed jobs older than max_age seconds. Returns count removed."""
        state = self.load()
        now = time.time()
        to_remove = [
            tid
            for tid, job in state.jobs.items()
            if job.status in ("done", "failed")
            and job.last_event_at > 0
            and (now - job.last_event_at) > max_age
        ]
        for tid in to_remove:
            del state.jobs[tid]
        if to_remove:
            self.save(state)
        return len(to_remove)
