#!/usr/bin/env python3
"""Export OpenCode session context into mem0 per-agent memory.

Reads sessions from the global OpenCode SQLite database, extracts meaningful
assistant-generated content, and stores it in mem0 with agent_id scoping so
each agent (oracle, librarian, explore, deep, etc.) retains its own namespace.

Usage:
    # Export all sessions from a specific project
    python export_sessions.py --project-path /home/xly/AgentSkillsArxiv

    # Export from multiple projects
    python export_sessions.py --project-path /home/xly/project1 --project-path /home/xly/project2

    # Export all projects
    python export_sessions.py --all

    # Dry run (print what would be stored, don't write)
    python export_sessions.py --project-path /path --dry-run

    # Custom store path
    python export_sessions.py --all --store-path /custom/mem0/path

    # Custom opencode DB path
    python export_sessions.py --all --db-path /path/to/opencode.db

    # Filter by date
    python export_sessions.py --all --since 2025-01-01

    # Limit messages per session
    python export_sessions.py --all --max-messages 50
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OPENCODE_DB_DEFAULT = Path.home() / ".local" / "share" / "opencode" / "opencode.db"
MEM0_STORE_DEFAULT = Path.home() / ".local" / "share" / "opencode" / "mem0"

# Map OpenCode agent display names → mem0 agent_id
AGENT_ID_MAP: dict[str, str] = {
    "sisyphus": "sisyphus",
    "ultraworker": "sisyphus",
    "hephaestus": "hephaestus",
    "oracle": "oracle",
    "librarian": "librarian",
    "explore": "explore",
    "metis": "metis",
    "momus": "momus",
    "atlas": "atlas",
    "prometheus": "prometheus",
    "deep": "deep",
    "multimodal": "multimodal-looker",
}

# Patterns to strip from exported text (injected instructions, not real content)
STRIP_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"<skill-instruction>.*?</skill-instruction>", re.DOTALL),
    re.compile(r"<system-reminder>.*?</system-reminder>", re.DOTALL),
    re.compile(r"<prunable-tools>.*?</prunable-tools>", re.DOTALL),
    re.compile(r"<env>.*?</env>", re.DOTALL),
    re.compile(r"<directories>.*?</directories>", re.DOTALL),
    re.compile(r"\[analyze-mode\].*?---\s*\n", re.DOTALL),
]

MIN_CONTENT_LENGTH = 80  # Skip trivial content
MAX_CHUNK_CHARS = 2000  # mem0 memory chunk ceiling

log = logging.getLogger("export_sessions")

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------


def _connect(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f"OpenCode database not found at {db_path}")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def list_projects(db_path: Path) -> list[dict[str, Any]]:
    """Return all projects in the database."""
    conn = _connect(db_path)
    rows = conn.execute("SELECT id, worktree, name FROM project").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def find_projects(db_path: Path, worktrees: list[str]) -> list[dict[str, Any]]:
    """Find projects matching the given worktree paths."""
    conn = _connect(db_path)
    placeholders = ",".join("?" * len(worktrees))
    rows = conn.execute(
        f"SELECT id, worktree, name FROM project WHERE worktree IN ({placeholders})",
        worktrees,
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_sessions(
    db_path: Path,
    project_id: str,
    since_ts: int | None = None,
) -> list[dict[str, Any]]:
    """Get sessions for a project, optionally filtered by creation time."""
    conn = _connect(db_path)
    query = "SELECT id, title, directory, time_created FROM session WHERE project_id = ?"
    params: list[Any] = [project_id]
    if since_ts is not None:
        query += " AND time_created >= ?"
        params.append(since_ts)
    query += " ORDER BY time_created ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_messages(
    db_path: Path,
    session_id: str,
    max_messages: int | None = None,
) -> list[dict[str, Any]]:
    """Get messages for a session with their text parts assembled."""
    conn = _connect(db_path)
    query = "SELECT id, data FROM message WHERE session_id = ? ORDER BY time_created ASC"
    if max_messages:
        query += f" LIMIT {max_messages}"
    msg_rows = conn.execute(query, (session_id,)).fetchall()

    results: list[dict[str, Any]] = []
    for msg_row in msg_rows:
        msg_data = json.loads(msg_row["data"])

        # Collect text parts for this message
        part_rows = conn.execute(
            "SELECT data FROM part WHERE message_id = ? ORDER BY time_created ASC",
            (msg_row["id"],),
        ).fetchall()

        text_parts: list[str] = []
        for part_row in part_rows:
            part_data = json.loads(part_row["data"])
            if part_data.get("type") == "text" and part_data.get("text"):
                text_parts.append(part_data["text"])

        if not text_parts:
            continue

        full_text = "\n".join(text_parts)
        results.append(
            {
                "role": msg_data.get("role", "unknown"),
                "agent": msg_data.get("agent", ""),
                "model": msg_data.get("model", {}),
                "text": full_text,
                "time_created": msg_data.get("time", {}).get("created"),
            }
        )

    conn.close()
    return results


# ---------------------------------------------------------------------------
# Content processing
# ---------------------------------------------------------------------------


def resolve_agent_id(agent_display_name: str) -> str:
    """Map an OpenCode agent display name to a mem0 agent_id."""
    lower = agent_display_name.lower()
    for key, agent_id in AGENT_ID_MAP.items():
        if key in lower:
            return agent_id
    return "sisyphus"  # fallback for main orchestrator


def clean_text(text: str) -> str:
    """Remove injected instructions and noise from message text."""
    cleaned = text
    for pattern in STRIP_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    # Collapse excessive whitespace from stripping
    cleaned = re.sub(r"\n{4,}", "\n\n\n", cleaned)
    return cleaned.strip()


def is_meaningful(text: str, role: str) -> bool:
    """Determine whether a message contains exportable content."""
    if len(text) < MIN_CONTENT_LENGTH:
        return False
    # Assistant messages: always interesting if long enough
    if role == "assistant":
        return True
    # User messages: only if they contain substantial requirements/decisions
    if role == "user" and len(text) > 200:
        return True
    return False


def chunk_text(text: str, max_chars: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split text into chunks at paragraph boundaries."""
    if len(text) <= max_chars:
        return [text]

    paragraphs = text.split("\n\n")
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) > max_chars:
            if current:
                chunks.append(current.strip())
            # If a single paragraph exceeds max, hard-split it
            if len(para) > max_chars:
                for i in range(0, len(para), max_chars):
                    chunks.append(para[i : i + max_chars].strip())
                current = ""
            else:
                current = para
        else:
            current = candidate

    if current.strip():
        chunks.append(current.strip())

    return chunks if chunks else [text[:max_chars]]


# ---------------------------------------------------------------------------
# mem0 integration
# ---------------------------------------------------------------------------


def create_mem0_client(store_path: Path) -> Any:
    """Create a mem0 Memory client with local qdrant storage."""
    try:
        from mem0 import Memory
    except ImportError:
        print(
            "Error: mem0ai is not installed. Run: pip install mem0ai",
            file=sys.stderr,
        )
        sys.exit(1)

    store_path.mkdir(parents=True, exist_ok=True)
    qdrant_path = str(store_path / "qdrant")

    config = {
        "custom_prompt": (
            "You are a Technical Knowledge Extractor for a software engineering AI agent system. "
            "Extract actionable technical facts from conversations between engineers and AI agents. "
            "Focus on: architecture decisions and rationale, library/API patterns and gotchas, "
            "debugging root causes that weren't obvious, codebase conventions, performance "
            "characteristics, configuration requirements, security considerations, and user "
            "preferences for code style or workflow. DO NOT extract trivial file paths, generic "
            "programming knowledge, temporary debugging state, or raw code without context. "
            "Return facts as concise, actionable statements useful to an engineer encountering "
            "the same codebase/library/problem in the future.\n\nInput:\n{user_input}\n\n"
            "Extracted facts (return as JSON list of strings):"
        ),
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "opencode_mem0",
                "path": qdrant_path,
            },
        },
    }
    return Memory.from_config(config)


def export_message_to_mem0(
    memory: Any,
    text: str,
    agent_id: str,
    project_name: str,
    app_id: str,
    session_title: str,
    role: str,
    original_agent: str,
) -> int:
    """Chunk and store a message in mem0. Returns number of memories added."""
    chunks = chunk_text(text)
    added = 0
    for chunk in chunks:
        metadata = {
            "source": "session-export",
            "project": project_name,
            "app_id": app_id,
            "session": session_title,
            "role": role,
            "original_agent": original_agent,
        }
        try:
            memory.add(chunk, agent_id=agent_id, metadata=metadata)
            added += 1
        except Exception:
            log.exception("Failed to add memory chunk (agent=%s, project=%s)", agent_id, project_name)
    return added


def _prepare_export_items(
    db_path: Path,
    project: dict[str, Any],
    *,
    app_id_override: str | None = None,
    since_ts: int | None = None,
    max_messages: int | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    """Collect all exportable messages across sessions for a project."""
    project_name = project.get("name") or Path(project["worktree"]).name
    app_id = app_id_override or Path(project["worktree"]).name
    project_id = project["id"]

    sessions = get_sessions(db_path, project_id, since_ts=since_ts)
    log.info("  Found %d sessions for project '%s'", len(sessions), project_name)

    items: list[dict[str, Any]] = []
    for session in sessions:
        session_id = session["id"]
        session_title = session.get("title") or session_id
        messages = get_messages(db_path, session_id, max_messages=max_messages)

        for msg in messages:
            cleaned = clean_text(msg["text"])
            if not is_meaningful(cleaned, msg["role"]):
                continue
            items.append({
                "text": cleaned,
                "agent_id": resolve_agent_id(msg["agent"]),
                "project_name": project_name,
                "app_id": app_id,
                "session_title": session_title,
                "role": msg["role"],
                "original_agent": msg["agent"],
            })

    return project_name, items


def export_project(
    db_path: Path,
    project: dict[str, Any],
    memory: Any | None,
    *,
    app_id_override: str | None = None,
    dry_run: bool = False,
    since_ts: int | None = None,
    max_messages: int | None = None,
    concurrency: int = 8,
) -> dict[str, int]:
    """Export all sessions for a project. Returns stats."""
    project_name, items = _prepare_export_items(
        db_path,
        project,
        app_id_override=app_id_override,
        since_ts=since_ts,
        max_messages=max_messages,
    )

    sessions_count = len(
        get_sessions(db_path, project["id"], since_ts=since_ts)
    )
    total_messages = sessions_count  # approx, re-counted from DB
    stats = {"sessions": sessions_count, "messages_scanned": len(items), "memories_added": 0, "skipped": 0}

    if dry_run:
        for item in items:
            preview = item["text"][:120].replace("\n", " ")
            print(
                f"  [DRY RUN] agent_id={item['agent_id']:<12} role={item['role']:<10} "
                f"len={len(item['text']):>5}  {preview}..."
            )
            stats["memories_added"] += len(chunk_text(item["text"]))
        return stats

    if not memory:
        return stats

    # --- Concurrent export ---
    lock = threading.Lock()
    added_total = 0
    failed_total = 0

    def _process_item(item: dict[str, Any]) -> int:
        return export_message_to_mem0(
            memory,
            item["text"],
            agent_id=item["agent_id"],
            project_name=item["project_name"],
            app_id=item["app_id"],
            session_title=item["session_title"],
            role=item["role"],
            original_agent=item["original_agent"],
        )

    log.info("  Processing %d messages with %d workers...", len(items), concurrency)
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = {executor.submit(_process_item, item): item for item in items}
        for future in as_completed(futures):
            try:
                count = future.result()
                with lock:
                    added_total += count
            except Exception:
                item = futures[future]
                log.exception(
                    "Failed to export message (agent=%s, project=%s)",
                    item["agent_id"],
                    item["project_name"],
                )
                with lock:
                    failed_total += 1

    stats["memories_added"] = added_total
    stats["skipped"] = failed_total
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export OpenCode session context into mem0 per-agent memory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--project-path",
        action="append",
        dest="project_paths",
        help="Worktree path(s) to export. Can be specified multiple times.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="export_all",
        help="Export sessions from ALL projects in the database.",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=Path(os.environ.get("OPENCODE_DB_PATH", str(OPENCODE_DB_DEFAULT))),
        help=f"Path to OpenCode SQLite database (default: {OPENCODE_DB_DEFAULT})",
    )
    parser.add_argument(
        "--store-path",
        type=Path,
        default=Path(
            os.environ.get("MEM0_LOCAL_STORE_PATH", str(MEM0_STORE_DEFAULT))
        ),
        help=f"mem0 local store path (default: {MEM0_STORE_DEFAULT})",
    )
    parser.add_argument(
        "--app-id",
        type=str,
        default=None,
        help=(
            "Override app_id metadata for all exported chunks. "
            "By default app_id is derived from project name/worktree basename."
        ),
    )
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Only export sessions created after this date (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--max-messages",
        type=int,
        default=None,
        help="Max messages to read per session.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be exported without writing to mem0.",
    )
    parser.add_argument(
        "--list-projects",
        action="store_true",
        help="List available projects and exit.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=8,
        help="Number of parallel workers for mem0 API calls (default: 8).",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    db_path: Path = args.db_path.expanduser().resolve()
    store_path: Path = args.store_path.expanduser().resolve()

    # ---- List projects mode ----
    if args.list_projects:
        projects = list_projects(db_path)
        if not projects:
            print("No projects found in database.")
            return
        print(f"Projects in {db_path}:\n")
        for p in projects:
            print(f"  {p['name'] or '(unnamed)':30s}  {p['worktree']}")
        return

    # ---- Validate args ----
    if not args.project_paths and not args.export_all:
        parser.error("Specify --project-path or --all to select projects.")

    # ---- Resolve since timestamp ----
    since_ts: int | None = None
    if args.since:
        try:
            dt = datetime.strptime(args.since, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            since_ts = int(dt.timestamp() * 1000)  # OpenCode uses millisecond timestamps
        except ValueError:
            parser.error(f"Invalid date format: {args.since}. Use YYYY-MM-DD.")

    # ---- Find projects ----
    if args.export_all:
        projects = list_projects(db_path)
    else:
        # Resolve paths to absolute
        resolved = [str(Path(p).expanduser().resolve()) for p in args.project_paths]
        projects = find_projects(db_path, resolved)
        if not projects:
            log.error(
                "No matching projects found for paths: %s",
                ", ".join(args.project_paths),
            )
            log.info("Available projects:")
            for p in list_projects(db_path):
                log.info("  %s  %s", p["name"] or "(unnamed)", p["worktree"])
            sys.exit(1)

    # ---- Create mem0 client ----
    memory = None
    if not args.dry_run:
        log.info("Initializing mem0 at %s", store_path)
        memory = create_mem0_client(store_path)

    # ---- Export ----
    total_stats = {"sessions": 0, "messages_scanned": 0, "memories_added": 0, "skipped": 0}

    for project in projects:
        project_name = project.get("name") or Path(project["worktree"]).name
        log.info("Exporting project: %s (%s)", project_name, project["worktree"])

        stats = export_project(
            db_path,
            project,
            memory,
            app_id_override=args.app_id,
            dry_run=args.dry_run,
            since_ts=since_ts,
            max_messages=args.max_messages,
            concurrency=args.concurrency,
        )

        for k in total_stats:
            total_stats[k] += stats[k]

        log.info(
            "  → %d sessions, %d messages scanned, %d memories added, %d skipped",
            stats["sessions"],
            stats["messages_scanned"],
            stats["memories_added"],
            stats["skipped"],
        )

    # ---- Summary ----
    print(f"\n{'=' * 60}")
    print("Export Summary")
    print(f"{'=' * 60}")
    print(f"  Projects:         {len(projects)}")
    print(f"  Sessions:         {total_stats['sessions']}")
    print(f"  Messages scanned: {total_stats['messages_scanned']}")
    print(f"  Memories added:   {total_stats['memories_added']}")
    print(f"  Skipped:          {total_stats['skipped']}")
    if args.dry_run:
        print("  Mode:             DRY RUN (nothing written)")
    else:
        print(f"  Store path:       {store_path}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
