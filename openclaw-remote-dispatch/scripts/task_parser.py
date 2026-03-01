"""Parse TickTick task content into dispatch metadata.

Task content format (first lines before '---' separator):

    Remote: <ssh_host> → <folder_path>
    Clone: <git_url>           (optional)
    Agent: build|plan          (optional, default: build)

Everything after '---' is status/progress log appended by the dispatcher.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class DispatchTask:
    """Parsed dispatch task ready for execution."""

    task_id: str
    project_id: str
    title: str  # the coding prompt
    host: str  # SSH config host name
    folder: str  # remote project path
    clone: str | None  # git clone URL (optional)
    agent: str  # "build" or "plan"


@dataclass
class ParseError:
    """Human-readable parse failure."""

    task_id: str
    project_id: str
    title: str
    reason: str


def parse_task(task: dict) -> DispatchTask | ParseError:
    """Parse a TickTick task dict into a DispatchTask.

    Returns ParseError with a human-readable reason on failure.
    """
    task_id = task.get("id", "")
    project_id = task.get("projectId", "")
    title = task.get("title", "").strip()
    content = task.get("content", "") or ""

    # Extract header (everything before first '---' line)
    header = content.split("---")[0] if "---" in content else content

    # Parse Remote: host → folder
    remote_match = re.search(
        r"Remote:\s*(\S+)\s*[→>]\s*(.+)", header, re.IGNORECASE
    )
    if not remote_match:
        return ParseError(
            task_id=task_id,
            project_id=project_id,
            title=title,
            reason=(
                "Missing 'Remote:' line in task content. "
                "Expected format: Remote: <ssh_host> → <folder_path>"
            ),
        )

    host = remote_match.group(1).strip()
    folder = remote_match.group(2).strip()

    # Parse optional Clone: url
    clone_match = re.search(r"Clone:\s*(\S+)", header, re.IGNORECASE)
    clone = clone_match.group(1).strip() if clone_match else None

    # Parse optional Agent: build|plan
    agent_match = re.search(r"Agent:\s*(\S+)", header, re.IGNORECASE)
    agent = agent_match.group(1).strip().lower() if agent_match else "build"

    if agent not in ("build", "plan"):
        agent = "build"

    if not title:
        return ParseError(
            task_id=task_id,
            project_id=project_id,
            title=title,
            reason="Task has no title (the title is the coding prompt).",
        )

    return DispatchTask(
        task_id=task_id,
        project_id=project_id,
        title=title,
        host=host,
        folder=folder,
        clone=clone,
        agent=agent,
    )


def build_task_content(
    host: str,
    folder: str,
    clone: str | None = None,
    agent: str = "build",
) -> str:
    """Build the content string for a new dispatch task."""
    lines = [f"Remote: {host} → {folder}"]
    if clone:
        lines.append(f"Clone: {clone}")
    if agent != "build":
        lines.append(f"Agent: {agent}")
    return "\n".join(lines)


def append_status(existing_content: str, status_line: str) -> str:
    """Append a timestamped status line below the '---' separator."""
    if "---" not in existing_content:
        existing_content = existing_content.rstrip() + "\n---"
    return existing_content.rstrip() + "\n" + status_line
