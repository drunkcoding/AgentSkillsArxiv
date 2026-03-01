from __future__ import annotations

import argparse
import logging
import threading
import time
from datetime import datetime
from typing import Any

from config import (
    DEFAULT_CHANNEL,
    DISPATCH_CHECKLIST,
    MAX_CONCURRENT,
    POLL_INTERVAL,
    TICKTICK_PROJECT,
)
from notifier import Notifier
from opencode_client import OpenCodeClient, OpenCodeError
from ssh_hosts import validate_host
from ssh_tunnel import FolderNotFoundError, RemoteOpenCode, SSHTunnelError
from state import Job, StateStore
from task_parser import DispatchTask, ParseError, append_status, parse_task
from ticktick_client import AuthError, TickTickClient, TickTickError

log = logging.getLogger(__name__)


def _format_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _format_diff_summary(diff_data: dict[str, Any]) -> str:
    if not isinstance(diff_data, dict):
        return "0 files changed"

    int_keys = (
        "files_changed",
        "filesChanged",
        "changed_files",
        "changedFiles",
        "num_files",
        "numFiles",
        "count",
    )
    for key in int_keys:
        value = diff_data.get(key)
        if isinstance(value, int):
            count = max(0, value)
            return "1 file changed" if count == 1 else f"{count} files changed"

    list_keys = ("files", "changes", "diffs", "items")
    for key in list_keys:
        value = diff_data.get(key)
        if isinstance(value, list):
            count = len(value)
            return "1 file changed" if count == 1 else f"{count} files changed"

    paths: set[str] = set()

    def _collect_paths(node: Any) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                k_lower = k.lower()
                if k_lower in {"path", "file", "filename", "newpath", "oldpath"}:
                    if isinstance(v, str) and v.strip():
                        paths.add(v.strip())
                _collect_paths(v)
            return

        if isinstance(node, list):
            for item in node:
                _collect_paths(item)
            return

    _collect_paths(diff_data)
    if paths:
        count = len(paths)
        return "1 file changed" if count == 1 else f"{count} files changed"

    raw_text_keys = ("diff", "patch", "raw")
    for key in raw_text_keys:
        value = diff_data.get(key)
        if isinstance(value, str):
            marker_count = value.count("diff --git ")
            if marker_count > 0:
                return "1 file changed" if marker_count == 1 else f"{marker_count} files changed"

    return "0 files changed"


class Dispatcher:
    """Orchestrates TickTick tasks into remote OpenCode coding sessions."""

    def __init__(
        self,
        notify_to: str | None,
        channel: str,
        project_name: str,
        poll_interval: int,
        max_concurrent: int,
        dry_run: bool,
    ) -> None:
        """Initialize TickTick client, state store, notifier, and runtime controls."""
        self.notify_to = (notify_to or "").strip()
        self.channel = channel
        self.project_name = project_name
        self.poll_interval = max(1, int(poll_interval))
        self.max_concurrent = max(1, int(max_concurrent))
        self.dry_run = dry_run

        self.ticktick = TickTickClient()
        self.state = StateStore()
        self.notifier: Notifier | None = (
            Notifier(self.notify_to, self.channel) if self.notify_to else None
        )

        self._shutdown = threading.Event()
        self._runtime_lock = threading.Lock()
        self._monitor_threads: dict[str, threading.Thread] = {}
        self._active_remotes: dict[str, RemoteOpenCode] = {}

    def run_once(self) -> int:
        """Execute one poll cycle and start new dispatches up to available capacity."""
        project = self.ticktick.ensure_project(self.project_name)
        project_id = str(project.get("id", "")).strip()
        if not project_id:
            raise TickTickError(
                f"Project '{self.project_name}' did not return a valid project ID"
            )

        project_data = self.ticktick.get_project_data(project_id)
        tasks_raw = project_data.get("tasks", [])
        tasks: list[dict[str, Any]] = (
            [t for t in tasks_raw if isinstance(t, dict)]
            if isinstance(tasks_raw, list)
            else []
        )

        state_data = self.state.load()
        tracked_ids = set(state_data.jobs.keys())
        active_count = sum(
            1
            for job in state_data.jobs.values()
            if job.status in ("pending", "running")
        )
        capacity = max(0, self.max_concurrent - active_count)
        if capacity <= 0:
            log.debug(
                "No dispatch capacity available (active=%d max=%d)",
                active_count,
                self.max_concurrent,
            )
            return 0

        dispatches_started = 0
        for task in tasks:
            if dispatches_started >= capacity:
                break

            task_id = str(task.get("id", "")).strip()
            if not task_id or task_id in tracked_ids:
                continue

            if not self._is_open_task(task):
                continue

            parsed = parse_task(task)
            if isinstance(parsed, ParseError):
                log.warning("Task %s parse error: %s", task_id, parsed.reason)
                self._append_task_status(
                    project_id=parsed.project_id,
                    task_id=parsed.task_id,
                    status_line=f"⚠️ {_format_timestamp()} — Parse error: {parsed.reason}",
                    dedupe_token=f"Parse error: {parsed.reason}",
                )
                continue

            host_error = validate_host(parsed.host)
            if host_error:
                log.warning("Task %s host validation failed: %s", parsed.task_id, host_error)
                appended = self._append_task_status(
                    project_id=parsed.project_id,
                    task_id=parsed.task_id,
                    status_line=f"⚠️ {_format_timestamp()} — {host_error}",
                    dedupe_token=host_error,
                )
                if appended:
                    self._notify_blocked(
                        parsed.host,
                        parsed.folder,
                        parsed.title,
                        host_error,
                    )
                continue

            if self.dry_run:
                log.info(
                    "[dry-run] validated task=%s host=%s folder=%s agent=%s",
                    parsed.task_id,
                    parsed.host,
                    parsed.folder,
                    parsed.agent,
                )
                continue

            try:
                self.dispatch_task(parsed)
                dispatches_started += 1
                tracked_ids.add(parsed.task_id)
            except Exception as exc:  # noqa: BLE001
                log.exception("Unhandled dispatch error for task %s: %s", parsed.task_id, exc)

        return dispatches_started

    def run_daemon(self) -> None:
        """Run dispatcher continuously until interrupted."""
        log.info(
            "Dispatcher daemon started (project=%s interval=%ss max=%d)",
            self.project_name,
            self.poll_interval,
            self.max_concurrent,
        )

        try:
            while not self._shutdown.is_set():
                try:
                    started = self.run_once()
                    if started > 0:
                        log.info("Started %d new dispatch job(s)", started)
                except (TickTickError, AuthError) as exc:
                    log.exception("TickTick poll failure: %s", exc)
                    self._notify_dispatcher_error(f"TickTick poll failed: {exc}")
                except Exception as exc:  # noqa: BLE001
                    log.exception("Unexpected poll failure: %s", exc)

                self._shutdown.wait(self.poll_interval)
        except KeyboardInterrupt:
            log.info("Keyboard interrupt received, stopping dispatcher")
        finally:
            self._shutdown.set()
            self._shutdown_all_remotes()
            log.info("Dispatcher stopped")

    def dispatch_task(self, dt: DispatchTask) -> None:
        """Dispatch one parsed TickTick task onto a remote OpenCode serve session."""
        now = time.time()
        job = Job(
            task_id=dt.task_id,
            project_id=dt.project_id,
            host=dt.host,
            folder=dt.folder,
            title=dt.title,
            status="pending",
            started_at=now,
            last_event_at=now,
            notify_to=self.notify_to,
            channel=self.channel,
            error="",
        )
        self.state.add_job(job)

        self._append_task_status(
            project_id=dt.project_id,
            task_id=dt.task_id,
            status_line=f"🔄 {_format_timestamp()} — Dispatched",
            dedupe_token="— Dispatched",
        )
        self._tick_checklist(dt, 0)

        remote = RemoteOpenCode(dt.host, dt.folder, dt.clone)
        try:
            client = remote.start()
        except FolderNotFoundError as exc:
            reason = str(exc)
            self.state.update_job(
                dt.task_id,
                status="blocked",
                error=reason,
                last_event_at=time.time(),
            )
            self._append_task_status(
                project_id=dt.project_id,
                task_id=dt.task_id,
                status_line=f"⚠️ {_format_timestamp()} — Blocked: {reason}",
                dedupe_token=f"Blocked: {reason}",
            )
            self._notify_blocked(dt.host, dt.folder, dt.title, reason)
            return
        except SSHTunnelError as exc:
            self._fail_job(job, remote, f"SSH launch failed: {exc}")
            return

        self.state.update_job(
            dt.task_id,
            status="running",
            ssh_port=remote.remote_port,
            local_port=remote.local_port,
            password=remote.password,
            last_event_at=time.time(),
            error="",
        )
        self._tick_checklist(dt, 1)

        try:
            session_id = client.create_session(dt.title[:50])
            client.prompt_async(session_id, dt.title, agent=dt.agent)
        except OpenCodeError as exc:
            self._fail_job(job, remote, f"OpenCode dispatch failed: {exc}")
            return

        self.state.update_job(
            dt.task_id,
            opencode_session_id=session_id,
            last_event_at=time.time(),
        )

        self._tick_checklist(dt, 2)
        self._notify_progress(
            dt.host,
            dt.folder,
            dt.title,
            f"Dispatched to {dt.host}, agent working...",
        )

        monitor_job = self._load_job(dt.task_id) or job
        monitor_thread = threading.Thread(
            target=self._monitor_events,
            args=(monitor_job, remote, session_id),
            name=f"dispatch-monitor-{dt.task_id[:8]}",
            daemon=True,
        )
        with self._runtime_lock:
            self._active_remotes[dt.task_id] = remote
            self._monitor_threads[dt.task_id] = monitor_thread

        try:
            monitor_thread.start()
        except RuntimeError as exc:
            self._fail_job(job, remote, f"Failed to start monitor thread: {exc}")

    def handle_reply(self, task_id: str, reply_text: str) -> None:
        """Route user reply text to the active OpenCode session for task_id."""
        reply = reply_text.strip()
        if not reply:
            log.warning("Empty reply ignored for task %s", task_id)
            return

        job = self._load_job(task_id)
        if job is None:
            log.error("No job found for task_id=%s", task_id)
            return

        if job.status not in ("pending", "running"):
            log.error(
                "Task %s is not active (status=%s); reply not forwarded",
                task_id,
                job.status,
            )
            return

        if job.local_port <= 0 or not job.password or not job.opencode_session_id:
            log.error(
                "Task %s missing session connection metadata; reply not forwarded",
                task_id,
            )
            return

        client = OpenCodeClient(f"http://127.0.0.1:{job.local_port}", job.password)
        agent = self._resolve_agent(job.project_id, job.task_id)

        try:
            client.prompt_async(job.opencode_session_id, reply, agent=agent)
            self.state.update_job(task_id, last_event_at=time.time(), error="")
            log.info("Forwarded reply to task %s session %s", task_id, job.opencode_session_id)
        except OpenCodeError as exc:
            reason = f"Reply forwarding failed: {exc}"
            log.error("%s", reason)
            self._notify_failed(job.host, job.folder, job.title, reason)

    def _tick_checklist(self, task: DispatchTask, index: int) -> None:
        if index < 0:
            return

        try:
            task_data = self._fetch_task(task.project_id, task.task_id)
        except (TickTickError, AuthError) as exc:
            log.warning(
                "Unable to fetch task %s for checklist update: %s",
                task.task_id,
                exc,
            )
            return

        if task_data is None:
            log.warning("Checklist update skipped; task %s not found", task.task_id)
            return

        existing_items = task_data.get("items", [])
        items: list[dict[str, Any]] = []
        if isinstance(existing_items, list):
            for idx, item in enumerate(existing_items):
                if not isinstance(item, dict):
                    continue
                merged = dict(item)
                if "title" not in merged and idx < len(DISPATCH_CHECKLIST):
                    merged["title"] = DISPATCH_CHECKLIST[idx]
                raw_status = merged.get("status", 0)
                try:
                    merged["status"] = 1 if int(raw_status) == 1 else 0
                except (TypeError, ValueError):
                    merged["status"] = 0
                items.append(merged)

        while len(items) < len(DISPATCH_CHECKLIST):
            items.append({"title": DISPATCH_CHECKLIST[len(items)], "status": 0})

        while len(items) <= index:
            items.append({"title": f"Step {len(items) + 1}", "status": 0})

        items[index]["status"] = 1
        try:
            self.ticktick.update_task(task.task_id, {"items": items})
        except (TickTickError, AuthError) as exc:
            log.warning(
                "Checklist update failed for task %s item %d: %s",
                task.task_id,
                index,
                exc,
            )

    def _monitor_events(
        self,
        job: Job,
        remote: RemoteOpenCode,
        session_id: str,
    ) -> None:
        current_session_id = session_id
        last_event_time = max(job.last_event_at, time.time())
        last_progress_notice = 0.0
        last_question_text = ""

        while not self._shutdown.is_set():
            client = remote.client
            if client is None:
                self._fail_job(job, remote, "OpenCode client unavailable while monitoring")
                return

            try:
                saw_matching_event = False
                for event in client.stream_events(timeout=30):
                    if self._shutdown.is_set():
                        return

                    event_type = str(event.get("event", "")).strip()
                    payload = event.get("data", {})
                    if not self._event_matches_session(payload, current_session_id):
                        continue

                    now = time.time()
                    saw_matching_event = True
                    last_event_time = now
                    self.state.update_job(
                        job.task_id,
                        status="running",
                        last_event_at=now,
                        opencode_session_id=current_session_id,
                    )

                    if event_type == "assistant.message.completed":
                        self._finalize_done(job, remote, current_session_id)
                        return

                    if self._is_question_event(event_type, payload):
                        question = self._extract_question_text(payload)
                        if question and question != last_question_text:
                            self._notify_question(
                                job.host,
                                job.folder,
                                job.title,
                                question,
                            )
                            last_question_text = question
                        continue

                    if event_type == "message.part.delta":
                        if now - last_progress_notice >= 30:
                            delta = self._extract_delta_text(payload)
                            if delta:
                                self._notify_progress(
                                    job.host,
                                    job.folder,
                                    job.title,
                                    f"Agent update: {self._truncate(delta, 260)}",
                                )
                                last_progress_notice = now
                        continue

                now = time.time()
                if now - last_event_time >= 60:
                    log.info(
                        "Task %s idle for 60s after prompt; marking done",
                        job.task_id,
                    )
                    self._finalize_done(job, remote, current_session_id)
                    return

                if not remote.is_alive():
                    resumed_session = self._restart_and_resume(job, remote)
                    if resumed_session is None:
                        return
                    current_session_id = resumed_session
                    last_event_time = time.time()
                    last_progress_notice = 0.0
                    continue

                if not saw_matching_event:
                    time.sleep(1)
            except OpenCodeError as exc:
                log.warning("SSE stream error for task %s: %s", job.task_id, exc)

                if self._shutdown.is_set():
                    return

                if remote.is_alive():
                    time.sleep(2)
                    continue

                resumed_session = self._restart_and_resume(job, remote)
                if resumed_session is None:
                    return

                current_session_id = resumed_session
                last_event_time = time.time()
                last_progress_notice = 0.0
            except Exception as exc:  # noqa: BLE001
                self._fail_job(job, remote, f"Monitor crashed: {exc}")
                return

    def _restart_and_resume(self, job: Job, remote: RemoteOpenCode) -> str | None:
        self._notify_progress(
            job.host,
            job.folder,
            job.title,
            "Connection lost, attempting SSH reconnect...",
        )

        try:
            client = remote.restart()
        except SSHTunnelError as exc:
            self._fail_job(job, remote, f"SSH reconnect failed: {exc}")
            return None

        agent = self._resolve_agent(job.project_id, job.task_id)
        try:
            resumed_session = client.create_session(job.title[:50])
            client.prompt_async(resumed_session, job.title, agent=agent)
        except OpenCodeError as exc:
            self._fail_job(job, remote, f"Resume after reconnect failed: {exc}")
            return None

        current = self._load_job(job.task_id)
        retries = (current.retries if current else job.retries) + 1
        self.state.update_job(
            job.task_id,
            status="running",
            retries=retries,
            ssh_port=remote.remote_port,
            local_port=remote.local_port,
            password=remote.password,
            opencode_session_id=resumed_session,
            last_event_at=time.time(),
            error="",
        )
        self._append_task_status(
            project_id=job.project_id,
            task_id=job.task_id,
            status_line=f"🔄 {_format_timestamp()} — Reconnected after SSH drop",
            dedupe_token="Reconnected after SSH drop",
        )
        self._notify_progress(
            job.host,
            job.folder,
            job.title,
            "SSH tunnel reconnected, monitoring resumed.",
        )
        return resumed_session

    def _finalize_done(self, job: Job, remote: RemoteOpenCode, session_id: str) -> None:
        diff_summary = "0 files changed"
        client = remote.client
        if client is not None:
            try:
                diff_data = client.get_diff(session_id)
                if isinstance(diff_data, dict):
                    diff_summary = _format_diff_summary(diff_data)
            except OpenCodeError as exc:
                log.warning("Diff retrieval failed for task %s: %s", job.task_id, exc)

        task = DispatchTask(
            task_id=job.task_id,
            project_id=job.project_id,
            title=job.title,
            host=job.host,
            folder=job.folder,
            clone=None,
            agent="build",
        )
        self._tick_checklist(task, 3)
        self._tick_checklist(task, 4)

        self._notify_done(job.host, job.folder, job.title, diff_summary)
        self._append_task_status(
            project_id=job.project_id,
            task_id=job.task_id,
            status_line=f"✅ {_format_timestamp()} — Done. {diff_summary}",
            dedupe_token="— Done.",
        )

        try:
            self.ticktick.complete_task(job.project_id, job.task_id)
        except (TickTickError, AuthError) as exc:
            log.warning("Failed to complete TickTick task %s: %s", job.task_id, exc)
            self._notify_dispatcher_error(
                f"Could not complete TickTick task '{job.title}': {exc}"
            )

        self.state.update_job(
            job.task_id,
            status="done",
            error="",
            opencode_session_id=session_id,
            last_event_at=time.time(),
        )

        try:
            remote.kill()
        finally:
            self._release_runtime(job.task_id)

    def _is_open_task(self, task: dict[str, Any]) -> bool:
        status = task.get("status", 0)
        try:
            return int(status) == 0
        except (TypeError, ValueError):
            return False

    def _fetch_task(self, project_id: str, task_id: str) -> dict[str, Any] | None:
        project_data = self.ticktick.get_project_data(project_id)
        tasks_raw = project_data.get("tasks", [])
        if not isinstance(tasks_raw, list):
            return None

        for task in tasks_raw:
            if isinstance(task, dict) and str(task.get("id", "")) == task_id:
                return task
        return None

    def _append_task_status(
        self,
        project_id: str,
        task_id: str,
        status_line: str,
        dedupe_token: str | None = None,
    ) -> bool:
        if not project_id or not task_id:
            return False

        try:
            task = self._fetch_task(project_id, task_id)
        except (TickTickError, AuthError) as exc:
            log.warning("Failed fetching task %s for status update: %s", task_id, exc)
            return False

        if task is None:
            log.warning("Task %s not found for status update", task_id)
            return False

        content = str(task.get("content", "") or "")
        if dedupe_token and dedupe_token in content:
            return False

        updated_content = append_status(content, status_line)
        try:
            self.ticktick.update_task(task_id, {"content": updated_content})
            return True
        except (TickTickError, AuthError) as exc:
            log.warning("Failed updating task %s content: %s", task_id, exc)
            return False

    def _load_job(self, task_id: str) -> Job | None:
        state = self.state.load()
        return state.jobs.get(task_id)

    def _resolve_agent(self, project_id: str, task_id: str) -> str:
        try:
            task = self._fetch_task(project_id, task_id)
        except (TickTickError, AuthError):
            return "build"

        if task is None:
            return "build"

        parsed = parse_task(task)
        if isinstance(parsed, DispatchTask):
            return parsed.agent
        return "build"

    def _fail_job(
        self,
        job: Job,
        remote: RemoteOpenCode | None,
        reason: str,
    ) -> None:
        log.error("Task %s failed: %s", job.task_id, reason)
        self.state.update_job(
            job.task_id,
            status="failed",
            error=reason,
            last_event_at=time.time(),
        )
        self._append_task_status(
            project_id=job.project_id,
            task_id=job.task_id,
            status_line=f"❌ {_format_timestamp()} — Failed: {reason}",
        )
        self._notify_failed(job.host, job.folder, job.title, reason)

        if remote is not None:
            try:
                remote.kill()
            except Exception:  # noqa: BLE001
                log.exception("Error while killing remote for task %s", job.task_id)

        self._release_runtime(job.task_id)

    def _release_runtime(self, task_id: str) -> None:
        with self._runtime_lock:
            self._active_remotes.pop(task_id, None)
            self._monitor_threads.pop(task_id, None)

    def _shutdown_all_remotes(self) -> None:
        with self._runtime_lock:
            remotes = list(self._active_remotes.items())
            self._active_remotes.clear()
            self._monitor_threads.clear()

        for task_id, remote in remotes:
            try:
                remote.kill()
            except Exception:  # noqa: BLE001
                log.exception("Error shutting down remote for task %s", task_id)

    def _notify_progress(self, host: str, folder: str, title: str, msg: str) -> None:
        if not self.notifier:
            return
        try:
            self.notifier.progress(host, folder, title, msg)
        except Exception:  # noqa: BLE001
            log.exception("Progress notification failed")

    def _notify_question(self, host: str, folder: str, title: str, question: str) -> None:
        if not self.notifier:
            return
        try:
            self.notifier.question(host, folder, title, question)
        except Exception:  # noqa: BLE001
            log.exception("Question notification failed")

    def _notify_done(self, host: str, folder: str, title: str, diff_summary: str) -> None:
        if not self.notifier:
            return
        try:
            self.notifier.done(host, folder, title, diff_summary)
        except Exception:  # noqa: BLE001
            log.exception("Done notification failed")

    def _notify_failed(self, host: str, folder: str, title: str, reason: str) -> None:
        if not self.notifier:
            return
        try:
            self.notifier.failed(host, folder, title, reason)
        except Exception:  # noqa: BLE001
            log.exception("Failure notification failed")

    def _notify_blocked(self, host: str, folder: str, title: str, reason: str) -> None:
        if not self.notifier:
            return
        try:
            self.notifier.blocked(host, folder, title, reason)
        except Exception:  # noqa: BLE001
            log.exception("Blocked notification failed")

    def _notify_dispatcher_error(self, reason: str) -> None:
        self._notify_failed(
            host="dispatcher",
            folder="ticktick",
            title="CodeDispatch daemon",
            reason=reason,
        )

    def _event_matches_session(self, payload: Any, session_id: str) -> bool:
        session_ids: set[str] = set()

        def _walk(node: Any) -> None:
            if isinstance(node, dict):
                for key, value in node.items():
                    key_l = key.lower()
                    if key_l in {"sessionid", "session_id", "session"}:
                        if isinstance(value, str):
                            session_ids.add(value)
                    if key_l == "id" and isinstance(value, str) and value.startswith("ses_"):
                        session_ids.add(value)
                    _walk(value)
                return

            if isinstance(node, list):
                for item in node:
                    _walk(item)

        _walk(payload)
        if not session_ids:
            return True
        return session_id in session_ids

    def _is_question_event(self, event_type: str, payload: Any) -> bool:
        lowered = event_type.lower()
        if lowered == "tool.requires_input":
            return True
        if "question" in lowered:
            return True

        if isinstance(payload, dict):
            keys = {key.lower() for key in payload.keys()}
            return "question" in keys or "requires_input" in keys
        return False

    def _extract_delta_text(self, payload: Any) -> str:
        text = self._extract_text(payload, preferred_keys=("delta", "text", "content"))
        return self._truncate(text, 400)

    def _extract_question_text(self, payload: Any) -> str:
        text = self._extract_text(
            payload,
            preferred_keys=("question", "prompt", "text", "content", "input", "raw"),
        )
        if not text:
            return "Agent requires input to continue."
        return self._truncate(text, 1500)

    def _extract_text(self, payload: Any, preferred_keys: tuple[str, ...]) -> str:
        queue: list[Any] = [payload]
        fallback = ""
        preferred = {key.lower() for key in preferred_keys}

        while queue:
            node = queue.pop(0)

            if isinstance(node, str):
                stripped = node.strip()
                if stripped and not fallback:
                    fallback = stripped
                continue

            if isinstance(node, dict):
                for key, value in node.items():
                    if key.lower() in preferred and isinstance(value, str):
                        stripped = value.strip()
                        if stripped:
                            return stripped
                queue.extend(node.values())
                continue

            if isinstance(node, list):
                queue.extend(node)

        return fallback

    def _truncate(self, text: str, max_len: int) -> str:
        if len(text) <= max_len:
            return text
        if max_len <= 1:
            return text[:max_len]
        return text[: max_len - 1].rstrip() + "…"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="TickTick → Remote OpenCode dispatch daemon",
    )
    parser.add_argument(
        "--notify",
        metavar="TO",
        help="Notification destination/contact (required for --daemon)",
    )
    parser.add_argument(
        "--channel",
        default=DEFAULT_CHANNEL,
        help=f"Notification channel (default: {DEFAULT_CHANNEL})",
    )
    parser.add_argument(
        "--project",
        default=TICKTICK_PROJECT,
        help=f"TickTick project name (default: {TICKTICK_PROJECT})",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=POLL_INTERVAL,
        help=f"Polling interval seconds (default: {POLL_INTERVAL})",
    )
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=MAX_CONCURRENT,
        help=f"Max simultaneous dispatches (default: {MAX_CONCURRENT})",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run continuously instead of one-shot poll",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate parse/hosts but do not dispatch",
    )
    parser.add_argument(
        "--reply",
        nargs=2,
        metavar=("TASK_ID", "TEXT"),
        help="Forward user reply text to active OpenCode session",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean old finished jobs from state",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show active jobs from state",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.daemon and not args.notify:
        parser.error("--notify is required when using --daemon")

    dispatcher = Dispatcher(
        notify_to=args.notify,
        channel=args.channel,
        project_name=args.project,
        poll_interval=args.interval,
        max_concurrent=args.max_concurrent,
        dry_run=args.dry_run,
    )

    if args.reply:
        task_id, text = args.reply
        dispatcher.handle_reply(task_id, text)
        return 0

    admin_action_ran = False
    if args.cleanup:
        removed = dispatcher.state.cleanup_finished()
        log.info("Removed %d old finished job(s)", removed)
        admin_action_ran = True

    if args.status:
        active = dispatcher.state.get_active_jobs()
        if not active:
            log.info("No active jobs")
        else:
            for task_id, job in active.items():
                log.info(
                    "task=%s status=%s host=%s folder=%s session=%s retries=%d",
                    task_id,
                    job.status,
                    job.host,
                    job.folder,
                    job.opencode_session_id,
                    job.retries,
                )
        admin_action_ran = True

    if admin_action_ran and not args.daemon:
        return 0

    if args.daemon:
        dispatcher.run_daemon()
        return 0

    try:
        started = dispatcher.run_once()
        if args.dry_run:
            log.info("Dry-run complete")
        else:
            log.info("Started %d new dispatch job(s)", started)
        return 0
    except (TickTickError, AuthError) as exc:
        log.exception("TickTick one-shot run failed: %s", exc)
        dispatcher._notify_dispatcher_error(f"TickTick one-shot run failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
