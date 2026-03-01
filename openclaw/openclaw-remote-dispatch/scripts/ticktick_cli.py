#!/usr/bin/env python3
"""General-purpose TickTick CLI — Python equivalent of the existing bun/ts ticktick skill.

Provides the same commands: tasks, task, complete, abandon, batch-abandon, lists, list, auth.
Uses the shared OAuth2 credentials from ~/.clawdbot/credentials/ticktick-cli/config.json.

Usage:
    python ticktick_cli.py tasks [--list NAME] [--status pending|completed] [--json]
    python ticktick_cli.py task TITLE --list NAME [--content TEXT] [--priority LEVEL] [--due DATE] [--tag TAG ...] [--json]
    python ticktick_cli.py task TITLE --update [--list NAME] [--content TEXT] [--priority LEVEL] [--due DATE] [--tag TAG ...] [--json]
    python ticktick_cli.py complete TASK [--list NAME] [--json]
    python ticktick_cli.py abandon TASK [--list NAME] [--json]
    python ticktick_cli.py batch-abandon TASKID [TASKID ...] [--json]
    python ticktick_cli.py lists [--json]
    python ticktick_cli.py list NAME [--color HEX] [--json]
    python ticktick_cli.py list NAME --update [--name NEWNAME] [--color HEX] [--json]
    python ticktick_cli.py auth --status
    python ticktick_cli.py auth --logout
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any

from ticktick_client import AuthError, TickTickClient, TickTickError
from ticktick_utils import (
    PRIORITY_MAP,
    format_due_date,
    format_task,
    is_task_id,
    parse_due_date,
    parse_priority,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Command implementations
# ---------------------------------------------------------------------------


def cmd_tasks(client: TickTickClient, args: argparse.Namespace) -> int:
    """List tasks — optionally filtered by project and/or status."""
    projects = client.list_projects()
    project_map: dict[str, str] = {p["id"]: p.get("name", p["id"]) for p in projects}

    if args.list:
        project = client.find_project_by_name(args.list)
        if project is None:
            _error(f"Project not found: {args.list}")
            return 1
        search_projects = [project]
    else:
        search_projects = projects

    tasks_with_project: list[dict[str, Any]] = []
    for proj in search_projects:
        try:
            data = client.get_project_data(proj["id"])
            for task in data.get("tasks", []):
                if isinstance(task, dict):
                    task["projectName"] = project_map.get(
                        task.get("projectId", ""), proj.get("name", "")
                    )
                    tasks_with_project.append(task)
        except TickTickError:
            continue

    # Filter by status
    if args.status == "pending":
        tasks_with_project = [t for t in tasks_with_project if t.get("status", 0) != 2]
    elif args.status == "completed":
        tasks_with_project = [t for t in tasks_with_project if t.get("status", 0) == 2]

    if args.json:
        print(json.dumps(tasks_with_project, indent=2))
        return 0

    if not tasks_with_project:
        print("No tasks found.")
        return 0

    print(f"\nTasks ({len(tasks_with_project)}):\n")
    for task in tasks_with_project:
        print(format_task(task, show_project=not args.list))
    return 0


def cmd_task_create(client: TickTickClient, args: argparse.Namespace) -> int:
    """Create a new task."""
    if not args.list:
        _error("--list is required when creating a task")
        return 1

    project = client.find_project_by_name(args.list)
    if project is None:
        _error(f"Project not found: {args.list}")
        return 1

    payload: dict[str, Any] = {
        "title": args.title,
        "projectId": project["id"],
    }

    if args.content:
        payload["content"] = args.content

    if args.priority:
        pri = parse_priority(args.priority)
        if pri is None:
            _error(f"Invalid priority: {args.priority}. Use none, low, medium, or high.")
            return 1
        payload["priority"] = pri

    if args.due:
        try:
            payload["dueDate"] = parse_due_date(args.due)
        except ValueError as e:
            _error(str(e))
            return 1

    if args.tag:
        payload["tags"] = args.tag

    task = client.create_task(
        project_id=project["id"],
        title=args.title,
        content=payload.get("content", ""),
        priority=payload.get("priority", 0),
        **{k: v for k, v in payload.items() if k not in ("title", "projectId", "content", "priority")},
    )

    if args.json:
        print(json.dumps(task, indent=2))
        return 0

    print(f'✓ Task created: "{task.get("title", args.title)}"')
    print(f'  ID: {task.get("id", "unknown")}')
    print(f'  Project: {project.get("name", "")}')
    due = task.get("dueDate")
    if due:
        print(f"  Due: {format_due_date(due)}")
    return 0


def cmd_task_update(client: TickTickClient, args: argparse.Namespace) -> int:
    """Update an existing task."""
    found = _find_task(client, args.title, args.list)
    if found is None:
        return 1

    task_data, project_id = found["task"], found["projectId"]

    fields: dict[str, Any] = {
        "id": task_data["id"],
        "projectId": project_id,
    }

    if args.content is not None:
        fields["content"] = args.content

    if args.priority:
        pri = parse_priority(args.priority)
        if pri is None:
            _error(f"Invalid priority: {args.priority}. Use none, low, medium, or high.")
            return 1
        fields["priority"] = pri

    if args.due:
        try:
            fields["dueDate"] = parse_due_date(args.due)
        except ValueError as e:
            _error(str(e))
            return 1

    if args.tag:
        fields["tags"] = args.tag

    updated = client.update_task(task_data["id"], fields)

    if args.json:
        print(json.dumps(updated, indent=2))
        return 0

    print(f'✓ Task updated: "{updated.get("title", task_data.get("title", ""))}"')
    print(f'  ID: {updated.get("id", task_data["id"])}')
    return 0


def cmd_complete(client: TickTickClient, args: argparse.Namespace) -> int:
    """Mark a task as complete."""
    found = _find_task(client, args.task, getattr(args, "list", None))
    if found is None:
        return 1

    task_data, project_id = found["task"], found["projectId"]
    client.complete_task(project_id, task_data["id"])

    if args.json:
        print(json.dumps({
            "success": True,
            "task": {
                "id": task_data["id"],
                "title": task_data.get("title", ""),
                "projectId": project_id,
                "status": "completed",
            },
        }, indent=2))
        return 0

    print(f'✓ Completed: "{task_data.get("title", "")}"')
    return 0


def cmd_abandon(client: TickTickClient, args: argparse.Namespace) -> int:
    """Mark a task as won't do (status -1)."""
    found = _find_task(client, args.task, getattr(args, "list", None))
    if found is None:
        return 1

    task_data, project_id = found["task"], found["projectId"]

    result = client.update_task(task_data["id"], {
        "id": task_data["id"],
        "projectId": project_id,
        "status": -1,
    })

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(f'✓ Abandoned: "{task_data.get("title", "")}"')
    return 0


def cmd_batch_abandon(client: TickTickClient, args: argparse.Namespace) -> int:
    """Abandon multiple tasks by ID in a single batch API call."""
    task_ids: list[str] = args.task_ids
    if not task_ids:
        _error("At least one task ID is required")
        return 1

    invalid = [tid for tid in task_ids if not is_task_id(tid)]
    if invalid:
        _error(
            f"Invalid task ID format: {', '.join(invalid)}\n"
            "Task IDs must be 24-character hex strings."
        )
        return 1

    updates: list[dict[str, Any]] = []
    not_found: list[str] = []

    for tid in task_ids:
        found = client.find_task_by_id(tid)
        if found:
            updates.append({
                "id": found["task"]["id"],
                "projectId": found["projectId"],
                "status": -1,
            })
        else:
            not_found.append(tid)

    if not_found:
        print(f"Warning: Tasks not found: {', '.join(not_found)}", file=sys.stderr)

    if not updates:
        _error("No valid tasks to abandon")
        return 1

    result = client.batch_tasks({"update": updates})

    if args.json:
        print(json.dumps({
            "abandoned": [u["id"] for u in updates],
            "notFound": not_found,
            "response": result,
        }, indent=2))
        return 0

    id2error = result.get("id2error", {}) or {}
    success_count = len(updates) - len(id2error)
    print(f"✓ Abandoned {success_count} task(s)")

    if id2error:
        print("Errors:", file=sys.stderr)
        for tid, err in id2error.items():
            print(f"  {tid}: {err}", file=sys.stderr)

    if not_found:
        print(f"Skipped {len(not_found)} task(s) not found")
    return 0


def cmd_lists(client: TickTickClient, args: argparse.Namespace) -> int:
    """List all projects."""
    projects = client.list_projects()

    if args.json:
        print(json.dumps(projects, indent=2))
        return 0

    if not projects:
        print("No projects found.")
        return 0

    print(f"\nProjects ({len(projects)}):\n")
    for proj in projects:
        color = f' ({proj["color"]})' if proj.get("color") else ""
        closed = " [closed]" if proj.get("closed") else ""
        print(f'• {proj.get("name", "unnamed")}{color}{closed}')
        print(f'  id: {proj.get("id", "unknown")}')
        print()
    return 0


def cmd_list_create(client: TickTickClient, args: argparse.Namespace) -> int:
    """Create a new project."""
    kwargs: dict[str, Any] = {}
    if args.color:
        kwargs["color"] = _normalize_color(args.color)

    project = client.create_project(args.name, **kwargs)

    if args.json:
        print(json.dumps(project, indent=2))
        return 0

    print(f'✓ Project created: "{project.get("name", args.name)}"')
    print(f'  ID: {project.get("id", "unknown")}')
    if project.get("color"):
        print(f'  Color: {project["color"]}')
    return 0


def cmd_list_update(client: TickTickClient, args: argparse.Namespace) -> int:
    """Update an existing project."""
    project = client.find_project_by_name(args.name)
    if project is None:
        _error(f"Project not found: {args.name}")
        return 1

    fields: dict[str, Any] = {"id": project["id"]}

    if args.new_name:
        fields["name"] = args.new_name
    if args.color:
        fields["color"] = _normalize_color(args.color)

    updated = client.update_project(project["id"], fields)

    if args.json:
        print(json.dumps(updated, indent=2))
        return 0

    print(f'✓ Project updated: "{updated.get("name", project.get("name", ""))}"')
    print(f'  ID: {updated.get("id", project["id"])}')
    if updated.get("color"):
        print(f'  Color: {updated["color"]}')
    return 0


def cmd_auth(client: TickTickClient, args: argparse.Namespace) -> int:
    """Check auth status or logout."""
    if args.auth_status:
        try:
            # Try loading and using a token
            client._get_token()
            print("✓ Authenticated with TickTick")
        except AuthError:
            print("✗ Not authenticated. Run 'bun run ticktick.ts auth' to set up.")
        return 0

    if args.logout:
        import json as json_mod
        from pathlib import Path

        from config import TICKTICK_CRED_PATH

        cred_path = Path(TICKTICK_CRED_PATH)
        if cred_path.exists():
            try:
                config = json_mod.loads(cred_path.read_text())
                config.pop("accessToken", None)
                config.pop("refreshToken", None)
                config.pop("tokenExpiry", None)
                cred_path.write_text(json_mod.dumps(config, indent=2))
                cred_path.chmod(0o600)
                print("Logged out successfully. Credentials preserved.")
            except (json_mod.JSONDecodeError, OSError) as e:
                _error(f"Failed to update credential file: {e}")
                return 1
        else:
            print("No configuration found.")
        return 0

    print("Use --status to check auth or --logout to clear tokens.")
    print("For initial auth setup, use the existing bun skill:")
    print("  bun run scripts/ticktick.ts auth --client-id ID --client-secret SECRET")
    return 0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_task(
    client: TickTickClient,
    name_or_id: str,
    project_filter: str | None = None,
) -> dict[str, Any] | None:
    """Find a task by name or ID. Returns {"task": dict, "projectId": str} or None."""
    if is_task_id(name_or_id) and not project_filter:
        found = client.find_task_by_id(name_or_id)
    else:
        found = client.find_task_by_title(name_or_id, project_filter)

    if found is None:
        _error(f"Task not found: {name_or_id}")
        return None
    return found


def _normalize_color(color: str) -> str:
    """Ensure color has # prefix."""
    return color if color.startswith("#") else f"#{color}"


def _error(msg: str) -> None:
    """Print error to stderr."""
    print(f"Error: {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ticktick",
        description="CLI for TickTick task and project management (Python)",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # --- tasks ---
    p_tasks = sub.add_parser("tasks", help="List tasks")
    p_tasks.add_argument("-l", "--list", metavar="NAME", help="Filter by project name or ID")
    p_tasks.add_argument(
        "-s", "--status", choices=["pending", "completed"], help="Filter by status"
    )
    p_tasks.add_argument("--json", action="store_true", help="Output as JSON")

    # --- task (create / update) ---
    p_task = sub.add_parser("task", help="Create or update a task")
    p_task.add_argument("title", help="Task title (or ID for update)")
    p_task.add_argument("-l", "--list", metavar="NAME", help="Project name or ID")
    p_task.add_argument("-c", "--content", metavar="TEXT", help="Task description/content")
    p_task.add_argument(
        "-p", "--priority", choices=list(PRIORITY_MAP.keys()), help="Priority level"
    )
    p_task.add_argument(
        "-d", "--due", metavar="DATE",
        help="Due date: today, tomorrow, 'in N days', or ISO date",
    )
    p_task.add_argument("-t", "--tag", nargs="+", metavar="TAG", help="Tags for the task")
    p_task.add_argument("-u", "--update", action="store_true", help="Update existing task")
    p_task.add_argument("--json", action="store_true", help="Output as JSON")

    # --- complete ---
    p_complete = sub.add_parser("complete", help="Mark a task as complete")
    p_complete.add_argument("task", help="Task name or ID")
    p_complete.add_argument("-l", "--list", metavar="NAME", help="Project name or ID")
    p_complete.add_argument("--json", action="store_true", help="Output as JSON")

    # --- abandon ---
    p_abandon = sub.add_parser("abandon", help="Mark a task as won't do")
    p_abandon.add_argument("task", help="Task name or ID")
    p_abandon.add_argument("-l", "--list", metavar="NAME", help="Project name or ID")
    p_abandon.add_argument("--json", action="store_true", help="Output as JSON")

    # --- batch-abandon ---
    p_batch = sub.add_parser("batch-abandon", help="Abandon multiple tasks by ID")
    p_batch.add_argument("task_ids", nargs="+", metavar="TASKID", help="Task IDs (24-char hex)")
    p_batch.add_argument("--json", action="store_true", help="Output as JSON")

    # --- lists ---
    p_lists = sub.add_parser("lists", help="List all projects")
    p_lists.add_argument("--json", action="store_true", help="Output as JSON")

    # --- list (create / update) ---
    p_list = sub.add_parser("list", help="Create or update a project")
    p_list.add_argument("name", help="Project name (or name/ID for update)")
    p_list.add_argument("-c", "--color", metavar="HEX", help="Project color in hex format")
    p_list.add_argument("-u", "--update", action="store_true", help="Update existing project")
    p_list.add_argument("-n", "--new-name", metavar="NAME", help="New name (for update)")
    p_list.add_argument("--json", action="store_true", help="Output as JSON")

    # --- auth ---
    p_auth = sub.add_parser("auth", help="Check or manage authentication")
    p_auth.add_argument(
        "--status", dest="auth_status", action="store_true", help="Check auth status"
    )
    p_auth.add_argument("--logout", action="store_true", help="Clear tokens (keep credentials)")

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    client = TickTickClient()

    try:
        if args.command == "tasks":
            return cmd_tasks(client, args)

        if args.command == "task":
            if args.update:
                return cmd_task_update(client, args)
            return cmd_task_create(client, args)

        if args.command == "complete":
            return cmd_complete(client, args)

        if args.command == "abandon":
            return cmd_abandon(client, args)

        if args.command == "batch-abandon":
            return cmd_batch_abandon(client, args)

        if args.command == "lists":
            return cmd_lists(client, args)

        if args.command == "list":
            if args.update:
                return cmd_list_update(client, args)
            return cmd_list_create(client, args)

        if args.command == "auth":
            return cmd_auth(client, args)

        parser.print_help()
        return 0

    except AuthError as e:
        _error(str(e))
        return 1
    except TickTickError as e:
        _error(str(e))
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
