#!/usr/bin/env python3
"""Maps (channel, sender_id) → Claude Code session UUID.

Storage: ~/.openclaw/claude-sessions.json
Supports: get, list, reset, reset-all subcommands
TTL-based expiry (default 24 h). File locking for concurrency safety.
"""

import argparse
import fcntl
import json
import os
import sys
import time
import uuid

DEFAULT_STORE = os.path.expanduser("~/.openclaw/claude-sessions.json")
DEFAULT_TTL = 86400  # 24 hours


def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def _load(path: str) -> dict:
    """Load session store, returning empty dict if missing/corrupt."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(path: str, data: dict) -> None:
    _ensure_dir(path)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def _key(channel: str, sender: str) -> str:
    return f"{channel}:{sender}"


def _with_lock(path: str, fn):
    """Execute fn while holding an advisory file lock."""
    lock_path = path + ".lock"
    _ensure_dir(lock_path)
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        return fn()
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def get_session(channel: str, sender: str, *, ttl: int = DEFAULT_TTL,
                store: str = DEFAULT_STORE) -> str:
    """Return existing session UUID or create a new one. Expired sessions are replaced."""
    def _inner():
        data = _load(store)
        k = _key(channel, sender)
        now = time.time()
        entry = data.get(k)
        if entry and (now - entry["created"]) < ttl:
            entry["last_used"] = now
            _save(store, data)
            return entry["session_id"]
        # Create new session
        sid = str(uuid.uuid4())
        data[k] = {"session_id": sid, "created": now, "last_used": now}
        _save(store, data)
        return sid
    return _with_lock(store, _inner)


def list_sessions(*, store: str = DEFAULT_STORE) -> list[dict]:
    """Return all sessions with metadata."""
    data = _load(store)
    result = []
    for k, v in data.items():
        channel, sender = k.split(":", 1)
        result.append({
            "channel": channel, "sender": sender,
            "session_id": v["session_id"],
            "created": v["created"], "last_used": v["last_used"],
        })
    return result


def reset_session(channel: str, sender: str, *, store: str = DEFAULT_STORE) -> bool:
    """Remove a single session. Returns True if it existed."""
    def _inner():
        data = _load(store)
        k = _key(channel, sender)
        if k in data:
            del data[k]
            _save(store, data)
            return True
        return False
    return _with_lock(store, _inner)


def reset_all(*, store: str = DEFAULT_STORE) -> int:
    """Remove all sessions. Returns count removed."""
    def _inner():
        data = _load(store)
        count = len(data)
        _save(store, {})
        return count
    return _with_lock(store, _inner)


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Claude Code sessions for OpenClaw")
    sub = parser.add_subparsers(dest="command", required=True)

    p_get = sub.add_parser("get", help="Get or create session for (channel, sender)")
    p_get.add_argument("--channel", required=True)
    p_get.add_argument("--sender", required=True)
    p_get.add_argument("--ttl", type=int, default=DEFAULT_TTL)
    p_get.add_argument("--store", default=DEFAULT_STORE)

    p_list = sub.add_parser("list", help="List all sessions")
    p_list.add_argument("--store", default=DEFAULT_STORE)

    p_reset = sub.add_parser("reset", help="Reset session for (channel, sender)")
    p_reset.add_argument("--channel", required=True)
    p_reset.add_argument("--sender", required=True)
    p_reset.add_argument("--store", default=DEFAULT_STORE)

    p_all = sub.add_parser("reset-all", help="Reset all sessions")
    p_all.add_argument("--store", default=DEFAULT_STORE)

    args = parser.parse_args()

    if args.command == "get":
        sid = get_session(args.channel, args.sender, ttl=args.ttl, store=args.store)
        print(sid)
    elif args.command == "list":
        sessions = list_sessions(store=args.store)
        print(json.dumps(sessions, indent=2))
    elif args.command == "reset":
        ok = reset_session(args.channel, args.sender, store=args.store)
        print("removed" if ok else "not found")
        sys.exit(0 if ok else 1)
    elif args.command == "reset-all":
        count = reset_all(store=args.store)
        print(f"removed {count} session(s)")


if __name__ == "__main__":
    main()
