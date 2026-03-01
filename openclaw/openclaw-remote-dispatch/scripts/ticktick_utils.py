"""Standalone TickTick utility helpers.

This module centralizes priority mapping, due-date parsing/formatting,
and human-readable task formatting used by TickTick-related scripts.
"""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Any

PRIORITY_MAP: dict[str, int] = {"none": 0, "low": 1, "medium": 3, "high": 5}
PRIORITY_REVERSE: dict[int, str] = {0: "none", 1: "low", 3: "medium", 5: "high"}

_IN_DAYS_RE = re.compile(r"^in (\d+) days?$", re.IGNORECASE)
_NEXT_DAY_RE = re.compile(
    r"^next (monday|tuesday|wednesday|thursday|friday|saturday|sunday)$",
    re.IGNORECASE,
)
_TASK_ID_RE = re.compile(r"^[a-f0-9]{24}$", re.IGNORECASE)
_WEEKDAY_INDEX: dict[str, int] = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def parse_priority(level: str) -> int | None:
    """Parse a human priority level into TickTick numeric priority.

    Accepts: ``none``, ``low``, ``medium``, ``high`` (case-insensitive).
    Returns ``None`` for invalid input.
    """
    return PRIORITY_MAP.get(level.lower())


def format_priority(priority: int) -> str:
    """Format TickTick numeric priority into a human priority label.

    Unknown values default to ``"none"``.
    """
    return PRIORITY_REVERSE.get(priority, "none")


def _to_ticktick_iso(dt: datetime) -> str:
    utc_dt = dt.astimezone(timezone.utc)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.000+0000")


def _end_of_day_local(base: datetime) -> datetime:
    local_tz = datetime.now().astimezone().tzinfo
    if local_tz is None:
        local_tz = timezone.utc
    return datetime.combine(base.date(), time(23, 59, 59), tzinfo=local_tz)


def _parse_iso_like(value: str) -> datetime:
    text = value.strip()
    if not text:
        raise ValueError("empty date")

    normalized = text.replace("Z", "+00:00")
    if re.search(r"[+-]\d{4}$", normalized):
        normalized = f"{normalized[:-5]}{normalized[-5:-2]}:{normalized[-2:]}"

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        parsed_date = date.fromisoformat(text)
        return datetime.combine(parsed_date, time(0, 0, 0), tzinfo=timezone.utc)

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def parse_due_date(due_str: str) -> str:
    """Parse due-date input to TickTick datetime format.

    Supported inputs:
    - ``today``
    - ``tomorrow``
    - ``in N day`` / ``in N days``
    - ``next monday`` ... ``next sunday``
    - ISO-like date/datetime strings

    Returns TickTick datetime format: ``YYYY-MM-DDTHH:MM:SS.000+0000``.
    """
    now = datetime.now().astimezone()
    lower_due = due_str.lower().strip()

    if lower_due == "today":
        return _to_ticktick_iso(_end_of_day_local(now))

    if lower_due == "tomorrow":
        return _to_ticktick_iso(_end_of_day_local(now + timedelta(days=1)))

    in_days_match = _IN_DAYS_RE.match(lower_due)
    if in_days_match:
        days = int(in_days_match.group(1))
        return _to_ticktick_iso(_end_of_day_local(now + timedelta(days=days)))

    next_day_match = _NEXT_DAY_RE.match(lower_due)
    if next_day_match:
        target_name = next_day_match.group(1).lower()
        target_day = _WEEKDAY_INDEX[target_name]
        current_day = now.weekday()
        days_until = target_day - current_day
        if days_until <= 0:
            days_until += 7
        return _to_ticktick_iso(_end_of_day_local(now + timedelta(days=days_until)))

    try:
        parsed = _parse_iso_like(due_str)
    except ValueError as exc:
        raise ValueError(
            f"Invalid date format: {due_str}. Try 'today', 'tomorrow', 'in 3 days', or ISO date."
        ) from exc

    return _to_ticktick_iso(parsed)


def format_due_date(date_str: str) -> str:
    """Format due date into a compact human label.

    Returns:
    - ``today`` if date is today
    - ``tomorrow`` if date is tomorrow
    - otherwise ``Mon D`` style (e.g. ``Jan 7``)
    """
    dt = _parse_iso_like(date_str).astimezone()
    task_day = dt.date()
    today = datetime.now().astimezone().date()
    tomorrow = today + timedelta(days=1)

    if task_day == today:
        return "today"
    if task_day == tomorrow:
        return "tomorrow"

    month = calendar.month_abbr[task_day.month]
    return f"{month} {task_day.day}"


def format_task(task: dict[str, Any], show_project: bool = False) -> str:
    """Format a TickTick task dictionary into a one-line display string."""
    status = "✓" if task.get("status") == 2 else "○"
    priority = task.get("priority")
    priority_indicator = "!!!" if priority == 5 else "!!" if priority == 3 else "!" if priority == 1 else ""
    due_str = f" - due {format_due_date(str(task['dueDate']))}" if task.get("dueDate") else ""
    project_str = f" ({task['projectName']})" if show_project and task.get("projectName") else ""
    short_id = str(task.get("id", ""))[:8]
    title = str(task.get("title", ""))
    return f"{status} [{short_id}] {priority_indicator}{title}{project_str}{due_str}"


def is_task_id(s: str) -> bool:
    """Return True if the string is a 24-character hexadecimal task ID."""
    return _TASK_ID_RE.fullmatch(s) is not None
