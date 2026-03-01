"""Parse ~/.ssh/config for known host aliases."""

from __future__ import annotations

import re
from pathlib import Path


def parse_ssh_hosts(config_path: str | None = None) -> list[str]:
    """Return list of Host aliases from SSH config, excluding wildcards."""
    path = Path(config_path or Path.home() / ".ssh" / "config")
    if not path.exists():
        return []

    hosts: list[str] = []
    for match in re.finditer(
        r"^\s*Host\s+(.+)$", path.read_text(), re.MULTILINE
    ):
        for name in match.group(1).split():
            name = name.strip()
            if name and "*" not in name and "?" not in name:
                hosts.append(name)
    return hosts


def validate_host(host: str, config_path: str | None = None) -> str | None:
    """Return None if host is valid, or an error message with suggestions.

    'local' and 'localhost' are always valid (local dispatch, no SSH needed).
    """
    if host.lower() in ("local", "localhost"):
        return None
    known = parse_ssh_hosts(config_path)
    if host in known:
        return None
    if not known:
        return (
            f"Unknown host '{host}' (no ~/.ssh/config found or it's empty)."
        )
    return (
        f"Unknown host '{host}'. "
        f"Available: local, {', '.join(sorted(known))}"
    )
