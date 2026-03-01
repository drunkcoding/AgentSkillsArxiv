from __future__ import annotations

import argparse
import logging
import threading
import time
from datetime import datetime
from typing import Any

from config import (
    DEFAULT_AGENT,
    DEFAULT_CHANNEL,
    DISPATCH_PHASES,
    MAX_CONCURRENT,
    NOTIFY_TARGET,
    PLAN_GATE_ENABLED,
    PLAN_GATE_TIMEOUT,
    POLL_INTERVAL,
    SESSION_FORK_THRESHOLD,
    SESSION_NEW_THRESHOLD,
    SESSION_REGISTRY_PATH,
    STUCK_JITTER_SIMILARITY,
    STUCK_REPEAT_THRESHOLD,
    STUCK_WINDOW_SIZE,
    TICKTICK_PROJECT,
)
from event_normalizer import TextEvent, ToolEvent, normalize
import intent_router
import llm_client
from notifier import Notifier
from opencode_client import OpenCodeClient, OpenCodeError
from plan_gate import PlanGate
from session_graph import SessionGraph
from session_matcher import MatchResult, SessionMatcher
from session_registry import SessionNode, SessionRegistry
from ssh_hosts import validate_host
from ssh_tunnel import FolderNotFoundError, LocalOpenCode, RemoteOpenCode, SSHTunnelError
from state import Job, StateStore
from stuck_detector import StuckDetector
from task_parser import DispatchTask, ParseError, append_status, is_local, parse_task
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
        self._active_remotes: dict[str, RemoteOpenCode | LocalOpenCode] = {}

        self._plan_gate = PlanGate(PLAN_GATE_TIMEOUT) if PLAN_GATE_ENABLED else None
        self._session_registry = SessionRegistry(SESSION_REGISTRY_PATH)
        self._session_matcher = SessionMatcher(
            self._session_registry,
            llm_classify=llm_client.classify,
            fork_threshold=SESSION_FORK_THRESHOLD,
            new_threshold=SESSION_NEW_THRESHOLD,
        )
        self._session_graph = SessionGraph(self._session_registry)

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
        tracked_ids = {
            task_id
            for task_id, job in state_data.jobs.items()
            if not (
                job.status == "failed"
                and str(job.error).startswith("Daemon restart: could not reconnect")
            )
        }
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

        self._resume_stale_jobs()

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

                self._check_plan_timeouts()
                self._shutdown.wait(self.poll_interval)
        except KeyboardInterrupt:
            log.info("Keyboard interrupt received, stopping dispatcher")
        finally:
            self._shutdown.set()
            self._shutdown_all_remotes()
            log.info("Dispatcher stopped")

    def dispatch_task(self, dt: DispatchTask) -> None:
        """Dispatch one parsed TickTick task onto a remote OpenCode serve session."""
        resolved_agent = intent_router.route_agent(dt.title, dt.agent)
        explicit_agent = (dt.agent or "").strip().lower()
        if explicit_agent and explicit_agent in {"build", "plan", "deep"} and resolved_agent == explicit_agent:
            agent_source = "explicit"
        elif resolved_agent == DEFAULT_AGENT:
            agent_source = "default"
        else:
            agent_source = "keyword"

        try:
            match_result = self._session_matcher.match(dt.host, dt.folder, dt.title)
        except Exception as exc:  # noqa: BLE001
            log.warning("Session matching failed for task %s: %s", dt.task_id, exc)
            match_result = MatchResult(
                decision="new_root",
                matched_session_id="",
                score=0.0,
                reason=f"matcher error: {exc}",
            )

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
            agent=resolved_agent,
            agent_source=agent_source,
            session_decision=match_result.decision,
            origin_session_id=match_result.matched_session_id,
            relevance_score=match_result.score,
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

        if is_local(dt.host):
            remote: RemoteOpenCode | LocalOpenCode = LocalOpenCode(dt.folder, dt.clone)
        else:
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
        self._tick_checklist(dt, 1, f"port:{remote.local_port}")

        try:
            if match_result.decision == "fork" and match_result.matched_session_id:
                session_id = client.fork_session(match_result.matched_session_id)
                if not session_id:
                    session_id = client.create_session(dt.title[:50])
            elif match_result.decision == "continue" and match_result.matched_session_id:
                session_id = match_result.matched_session_id
            else:
                session_id = client.create_session(dt.title[:50])

            self._tick_checklist(dt, 2, f"sid:{session_id[:12]}")
            client.prompt_async(session_id, dt.title, agent=resolved_agent)
            self._tick_checklist(dt, 3, f"agent:{resolved_agent}")
        except OpenCodeError as exc:
            self._fail_job(job, remote, f"OpenCode dispatch failed: {exc}")
            return

        self.state.update_job(
            dt.task_id,
            opencode_session_id=session_id,
            last_event_at=time.time(),
        )
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
            self._tick_checklist(dt, 4)
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

        reply_lower = reply.lower()
        if reply_lower.startswith("approve") and self._plan_gate:
            self._plan_gate.register_approval(task_id, approved=True)
            if job.pending_plan_text:
                plan_section = (
                    f"\n\n--- Approved Plan ({_format_timestamp()}) ---\n"
                    f"{job.pending_plan_text}"
                )
                self._append_task_status(
                    project_id=job.project_id,
                    task_id=job.task_id,
                    status_line=plan_section,
                    dedupe_token="--- Approved Plan",
                )
            self.state.update_job(
                task_id,
                approval_state="approved",
                pause_kind="",
                pause_reason="",
                confirmed_plan=job.pending_plan_text or job.confirmed_plan,
                pending_plan_text="",
                pending_plan_message_id="",
                approval_requested_at=0.0,
                last_event_at=time.time(),
                error="",
            )
            self._resume_paused_job(task_id)
            return

        if reply_lower.startswith("reject") and self._plan_gate:
            self._plan_gate.register_approval(task_id, approved=False)
            self.state.update_job(task_id, approval_state="rejected")
            self._fail_job(job, self._get_active_remote(task_id), "Plan rejected by user")
            return

        if reply_lower.startswith("continue"):
            self.state.update_job(
                task_id,
                pause_kind="",
                pause_reason="",
                last_event_at=time.time(),
                error="",
            )
            self._resume_paused_job(task_id)
            return

        if reply_lower.startswith("abort"):
            self._fail_job(job, self._get_active_remote(task_id), "Aborted by user after stuck detection")
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

    def _get_active_remote(self, task_id: str) -> RemoteOpenCode | LocalOpenCode | None:
        with self._runtime_lock:
            return self._active_remotes.get(task_id)

    def _resume_paused_job(self, task_id: str) -> None:
        job = self._load_job(task_id)
        if job is None:
            log.error("Cannot resume; no job found for task_id=%s", task_id)
            return

        if job.local_port <= 0 or not job.password or not job.opencode_session_id:
            self._fail_job(job, self._get_active_remote(task_id), "Resume failed: missing session metadata")
            return

        remote = self._get_active_remote(task_id)
        if remote is None:
            self._fail_job(job, None, "Resume failed: active runtime not found")
            return

        client = remote.client
        if client is None:
            self._fail_job(job, remote, "Resume failed: OpenCode client unavailable")
            return

        agent = job.agent or self._resolve_agent(job.project_id, job.task_id)
        try:
            client.prompt_async(job.opencode_session_id, job.title, agent=agent)
        except OpenCodeError as exc:
            self._fail_job(job, remote, f"Resume failed: {exc}")
            return

        self.state.update_job(
            task_id,
            status="running",
            pause_kind="",
            pause_reason="",
            error="",
            last_event_at=time.time(),
        )

        with self._runtime_lock:
            existing_thread = self._monitor_threads.get(task_id)
            if existing_thread and existing_thread.is_alive():
                return

        monitor_job = self._load_job(task_id) or job
        monitor_thread = threading.Thread(
            target=self._monitor_events,
            args=(monitor_job, remote, job.opencode_session_id),
            name=f"dispatch-monitor-{task_id[:8]}",
            daemon=True,
        )
        with self._runtime_lock:
            self._active_remotes[task_id] = remote
            self._monitor_threads[task_id] = monitor_thread

        try:
            monitor_thread.start()
        except RuntimeError as exc:
            self._fail_job(monitor_job, remote, f"Failed to restart monitor thread: {exc}")

    def _resume_stale_jobs(self) -> None:
        state_data = self.state.load()
        stale_jobs = {
            task_id: job
            for task_id, job in state_data.jobs.items()
            if job.status in ("running", "pending") and job.local_port > 0
        }
        if not stale_jobs:
            return

        def _stop_stale_runtime(stale_job: Job) -> None:
            if stale_job.local_port <= 0:
                return

            client: OpenCodeClient | None = None
            client_is_healthy = False
            try:
                client = OpenCodeClient(
                    f"http://127.0.0.1:{stale_job.local_port}",
                    stale_job.password,
                )
                client_is_healthy = client.health()
            except (OpenCodeError, OSError):
                client = None

            if client and client_is_healthy:
                try:
                    client._request("POST", "/global/shutdown")
                except (OpenCodeError, OSError, ValueError):
                    pass

            try:
                runtime: RemoteOpenCode | LocalOpenCode
                if is_local(stale_job.host):
                    runtime = LocalOpenCode(stale_job.folder)
                    runtime._port = stale_job.local_port
                else:
                    runtime = RemoteOpenCode(stale_job.host, stale_job.folder)
                    runtime._remote_port = stale_job.ssh_port
                    runtime._local_port = stale_job.local_port
                runtime._password = stale_job.password
                if client and client_is_healthy:
                    runtime._client = client
                runtime.kill()
            except Exception as exc:  # noqa: BLE001
                log.warning(
                    "Best-effort stale runtime cleanup failed for task %s (port %d): %s",
                    stale_job.task_id,
                    stale_job.local_port,
                    exc,
                )

        for task_id, job in stale_jobs.items():
            log.info(
                "Attempting to resume stale job %s (host=%s, phase=%d)",
                task_id,
                job.host,
                job.phase_index,
            )

            try:
                ticktick_task = self._fetch_task(job.project_id, job.task_id)
                if ticktick_task is None:
                    log.info(
                        "Stale job %s task deleted in TickTick; marking failed and skipping reattach",
                        task_id,
                    )
                    _stop_stale_runtime(job)
                    self._release_runtime(task_id)
                    self.state.update_job(
                        task_id,
                        status="failed",
                        error="TickTick task deleted before stale resume",
                        last_event_at=time.time(),
                    )
                    continue

                if not self._is_open_task(ticktick_task):
                    log.info(
                        "Stale job %s already closed in TickTick (status=%s); marking done",
                        task_id,
                        ticktick_task.get("status"),
                    )
                    _stop_stale_runtime(job)
                    self._release_runtime(task_id)
                    self.state.update_job(
                        task_id,
                        status="done",
                        error="",
                        last_event_at=time.time(),
                    )
                    continue
            except (TickTickError, AuthError) as exc:
                log.warning(
                    "Could not verify TickTick status for stale job %s: %s; proceeding with reattach",
                    task_id,
                    exc,
                )

            try:
                client = OpenCodeClient(f"http://127.0.0.1:{job.local_port}", job.password)
                if client.health():
                    log.info(
                        "Reattached to running opencode on port %d for task %s",
                        job.local_port,
                        task_id,
                    )

                    remote: RemoteOpenCode | LocalOpenCode
                    if is_local(job.host):
                        remote = LocalOpenCode(job.folder)
                        remote._client = client
                        remote._port = job.local_port
                    else:
                        remote = RemoteOpenCode(job.host, job.folder)
                        remote._client = client
                        remote._remote_port = job.ssh_port
                        remote._local_port = job.local_port
                    remote._password = job.password

                    session_id = job.opencode_session_id
                    if not session_id:
                        sessions = client.list_sessions()
                        if sessions:
                            session_id = str(sessions[-1].get("id", "")).strip()

                    if session_id:
                        self.state.update_job(
                            task_id,
                            status="running",
                            opencode_session_id=session_id,
                            last_event_at=time.time(),
                            error="",
                        )
                        monitor_job = self._load_job(task_id) or job
                        monitor_thread = threading.Thread(
                            target=self._monitor_events,
                            args=(monitor_job, remote, session_id),
                            name=f"dispatch-monitor-{task_id[:8]}",
                            daemon=True,
                        )
                        with self._runtime_lock:
                            self._active_remotes[task_id] = remote
                            self._monitor_threads[task_id] = monitor_thread

                        try:
                            monitor_thread.start()
                            self._tick_checklist(monitor_job, 4)
                            continue
                        except RuntimeError:
                            with self._runtime_lock:
                                self._active_remotes.pop(task_id, None)
                                self._monitor_threads.pop(task_id, None)
                            raise
            except (OpenCodeError, OSError, RuntimeError):
                pass

            log.warning(
                "Could not reattach to task %s, marking as failed for re-dispatch",
                task_id,
            )
            self.state.update_job(
                task_id,
                status="failed",
                error=f"Daemon restart: could not reconnect (port {job.local_port})",
                last_event_at=time.time(),
            )
            self._append_task_status(
                project_id=job.project_id,
                task_id=job.task_id,
                status_line=f"⚠️ {_format_timestamp()} — Daemon restarted, could not resume",
                dedupe_token="Daemon restarted",
            )

    def _check_plan_timeouts(self) -> None:
        """Check for plan-gated jobs whose approval timeout has expired and auto-resume them."""
        if not self._plan_gate:
            return

        state_data = self.state.load()
        for task_id in state_data.jobs:
            current_job = self._load_job(task_id)
            if current_job is None:
                continue

            if current_job.pause_kind != "plan_review" or current_job.approval_state != "pending":
                continue

            status = self._plan_gate.check_approval(task_id)
            if status in ("timeout", "approved"):
                log.info("Plan auto-approved (%s) for task %s", status, task_id)
                if current_job.pending_plan_text:
                    section_title = "--- Auto-Approved Plan" if status == "timeout" else "--- Approved Plan"
                    plan_section = (
                        f"\n\n{section_title} ({_format_timestamp()}) ---\n"
                        f"{current_job.pending_plan_text}"
                    )
                    self._append_task_status(
                        project_id=current_job.project_id,
                        task_id=current_job.task_id,
                        status_line=plan_section,
                        dedupe_token=section_title,
                    )
                self.state.update_job(
                    task_id,
                    approval_state="auto_approved" if status == "timeout" else "approved",
                    pause_kind="",
                    pause_reason="",
                    confirmed_plan=current_job.pending_plan_text or current_job.confirmed_plan,
                    pending_plan_text="",
                    pending_plan_message_id="",
                    approval_requested_at=0.0,
                    last_event_at=time.time(),
                    error="",
                )
                self._resume_paused_job(task_id)

    def _tick_checklist(self, task: DispatchTask | Job, index: int, metadata: str = "") -> None:
        if index < 0:
            return

        self.state.update_job(task.task_id, phase_index=index)

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

        content = str(task_data.get("content", "") or "")
        section_header = "--- Phase Progress ---"

        lines = content.splitlines()
        section_start = -1
        section_end = -1
        existing_titles: list[str] = []

        for idx, line in enumerate(lines):
            if line.strip() == section_header:
                section_start = idx
                section_end = idx + 1
                while section_end < len(lines):
                    stripped = lines[section_end].strip()
                    if not stripped:
                        section_end += 1
                        continue
                    if stripped.startswith(("✅", "⏳", "⬜")):
                        existing_titles.append(stripped[1:].strip())
                        section_end += 1
                        continue
                    break
                break

        total_phases = max(len(DISPATCH_PHASES), index + 1, len(existing_titles))
        phase_titles: list[str] = []
        for idx in range(total_phases):
            if idx < len(DISPATCH_PHASES):
                phase_titles.append(DISPATCH_PHASES[idx])
            else:
                phase_titles.append(f"Step {idx + 1}")

        for idx, existing_title in enumerate(existing_titles):
            if existing_title.strip() and idx < len(phase_titles):
                phase_titles[idx] = existing_title.strip()

        if metadata.strip():
            base_title = DISPATCH_PHASES[index] if index < len(DISPATCH_PHASES) else f"Step {index + 1}"
            phase_titles[index] = f"{base_title} ({metadata.strip()})"

        progress_lines = [section_header]
        final_index = len(phase_titles) - 1
        for idx, phase_title in enumerate(phase_titles):
            marker = "⬜"
            if idx < index:
                marker = "✅"
            elif idx == index:
                marker = "✅" if idx == final_index else "⏳"
            progress_lines.append(f"{marker} {phase_title}")

        if section_start >= 0 and section_end >= section_start:
            updated_lines = lines[:section_start] + progress_lines + lines[section_end:]
            updated_content = "\n".join(updated_lines)
        else:
            progress_section = "\n".join(progress_lines)
            updated_content = f"{content.rstrip()}\n\n{progress_section}" if content.strip() else progress_section

        try:
            self.ticktick.update_task(task.task_id, {"content": updated_content}, project_id=task.project_id)
        except (TickTickError, AuthError) as exc:
            log.warning(
                "Checklist update failed for task %s phase %d: %s",
                task.task_id,
                index,
                exc,
            )

    def _monitor_events(
        self,
        job: Job,
        remote: RemoteOpenCode | LocalOpenCode,
        session_id: str,
    ) -> None:
        current_session_id = session_id
        last_event_time = max(job.last_event_at, time.time())
        last_progress_notice = 0.0
        last_question_text = ""
        stuck = StuckDetector(
            STUCK_WINDOW_SIZE,
            STUCK_REPEAT_THRESHOLD,
            STUCK_JITTER_SIMILARITY,
        )

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

                    norm = normalize(event)

                    if isinstance(norm, (ToolEvent, TextEvent)):
                        signal = stuck.feed(norm)
                        if signal:
                            try:
                                client.abort(current_session_id)
                            except OpenCodeError as exc:
                                log.warning(
                                    "Failed aborting stuck session %s for task %s: %s",
                                    current_session_id,
                                    job.task_id,
                                    exc,
                                )

                            current_job = self._load_job(job.task_id)
                            loop_count = (
                                (current_job.loop_count if current_job else job.loop_count) + 1
                            )
                            self.state.update_job(
                                job.task_id,
                                pause_kind="stuck",
                                pause_reason=signal.description,
                                loop_count=loop_count,
                                last_event_at=time.time(),
                            )

                            if self.notifier:
                                try:
                                    self.notifier.stuck_alert(
                                        job.host,
                                        job.folder,
                                        job.title,
                                        signal.description,
                                        job.task_id,
                                    )
                                except Exception:  # noqa: BLE001
                                    log.exception("Stuck notification failed")
                            return

                    if self._plan_gate and isinstance(norm, TextEvent):
                        candidate = self._plan_gate.detect_plan(norm.text)
                        if candidate:
                            try:
                                client.abort(current_session_id)
                            except OpenCodeError as exc:
                                log.warning(
                                    "Failed aborting plan-gated session %s for task %s: %s",
                                    current_session_id,
                                    job.task_id,
                                    exc,
                                )

                            self.state.update_job(
                                job.task_id,
                                pause_kind="plan_review",
                                pending_plan_text=candidate.text[:2000],
                                pending_plan_message_id=candidate.message_id,
                                approval_state="pending",
                                approval_requested_at=time.time(),
                                last_event_at=time.time(),
                            )
                            self._plan_gate.request_approval(candidate, self.notifier, job)
                            return

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

    def _restart_and_resume(self, job: Job, remote: RemoteOpenCode | LocalOpenCode) -> str | None:
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

    def _finalize_done(self, job: Job, remote: RemoteOpenCode | LocalOpenCode, session_id: str) -> None:
        diff_summary = "0 files changed"
        summary_bullets: list[str] = []
        client = remote.client
        if client is not None:
            try:
                diff_data = client.get_diff(session_id)
                if isinstance(diff_data, dict):
                    diff_summary = _format_diff_summary(diff_data)
            except OpenCodeError as exc:
                log.warning("Diff retrieval failed for task %s: %s", job.task_id, exc)

            try:
                todos = client.get_todo(session_id)
                if isinstance(todos, list):
                    summary_bullets = [
                        str(todo.get("content", todo.get("title", ""))).strip()
                        for todo in todos[:10]
                        if isinstance(todo, dict)
                        and str(todo.get("content", todo.get("title", ""))).strip()
                    ]
            except OpenCodeError:
                pass

        self._tick_checklist(job, 5)
        validation_ok = self._validate_completion(job, diff_summary, summary_bullets)
        self._tick_checklist(job, 6)

        if validation_ok:
            if self.notifier and summary_bullets:
                try:
                    self.notifier.done_with_summary(
                        job.host,
                        job.folder,
                        job.title,
                        diff_summary,
                        summary_bullets,
                        session_id,
                    )
                except Exception:  # noqa: BLE001
                    log.exception("Enhanced done notification failed")
                    self._notify_done(job.host, job.folder, job.title, diff_summary)
            else:
                self._notify_done(job.host, job.folder, job.title, diff_summary)

            self._append_task_status(
                project_id=job.project_id,
                task_id=job.task_id,
                status_line=f"✅ {_format_timestamp()} — Done. {diff_summary}",
                dedupe_token="— Done.",
            )

            try:
                self.ticktick.complete_task(job.project_id, job.task_id)
                self._tick_checklist(job, 7)
            except (TickTickError, AuthError) as exc:
                log.warning("Failed to complete TickTick task %s: %s", job.task_id, exc)
                self._notify_dispatcher_error(
                    f"Could not complete TickTick task '{job.title}': {exc}"
                )
        else:
            self._append_task_status(
                project_id=job.project_id,
                task_id=job.task_id,
                status_line=(
                    f"⚠️ {_format_timestamp()} — Completed but no changes detected. Needs review."
                ),
                dedupe_token="Needs review.",
            )
            if self.notifier:
                try:
                    self.notifier.question(
                        job.host,
                        job.folder,
                        job.title,
                        "Completed but no changes detected. Please verify before marking done.",
                    )
                except Exception:  # noqa: BLE001
                    log.exception("Validation review notification failed")

        completed_at = time.time()
        summary_text = (job.summary_text or "\n".join(summary_bullets[:5])).strip()
        diff_count = 0
        first_token = diff_summary.split(" ", 1)[0].strip()
        if first_token.isdigit():
            diff_count = int(first_token)
        self.state.update_job(
            job.task_id,
            status="done",
            error="" if validation_ok else "validation_pending",
            opencode_session_id=session_id,
            summary_text=summary_text,
            last_event_at=completed_at,
        )

        try:
            node = SessionNode(
                session_id=session_id,
                task_id=job.task_id,
                host=job.host,
                folder=job.folder,
                title=job.title,
                agent=job.agent or DEFAULT_AGENT,
                summary_text=summary_text,
                todo_items=summary_bullets[:10],
                diff_stats={"files_changed": diff_count},
                completed_at=completed_at,
                parent_session_id=job.origin_session_id,
            )
            self._session_registry.add(node)

            if job.origin_session_id and job.origin_session_id != session_id:
                self._session_graph.add_edge(job.origin_session_id, session_id)
        except Exception as exc:  # noqa: BLE001
            log.warning("Session registry update failed for task %s: %s", job.task_id, exc)

        try:
            remote.kill()
        finally:
            self._release_runtime(job.task_id)

    def _validate_completion(self, job: Job, diff_summary: str, summary_bullets: list[str]) -> bool:
        has_changes = not diff_summary.startswith("0 files")
        has_todos = bool(summary_bullets)
        has_plan = bool(job.confirmed_plan or job.pending_plan_text)

        if not has_plan:
            return True
        if has_changes or has_todos:
            return True

        log.warning(
            "Task %s has plan but no changes/todos — validation failed",
            job.task_id,
        )
        return False

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
            self.ticktick.update_task(task_id, {"content": updated_content}, project_id=project_id)
            return True
        except (TickTickError, AuthError) as exc:
            log.warning("Failed updating task %s content: %s", task_id, exc)
            return False

    def _load_job(self, task_id: str) -> Job | None:
        state = self.state.load()
        return state.jobs.get(task_id)

    def _resolve_agent(self, project_id: str, task_id: str) -> str:
        current = self._load_job(task_id)
        if current and current.agent:
            return current.agent

        try:
            task = self._fetch_task(project_id, task_id)
        except (TickTickError, AuthError):
            return DEFAULT_AGENT

        if task is None:
            return DEFAULT_AGENT

        parsed = parse_task(task)
        if isinstance(parsed, DispatchTask):
            return parsed.agent
        return DEFAULT_AGENT

    def _fail_job(
        self,
        job: Job,
        remote: RemoteOpenCode | LocalOpenCode | None,
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
        default=NOTIFY_TARGET,
        help="Notification target (E.164 phone for WhatsApp, e.g. +447123456789)",
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
