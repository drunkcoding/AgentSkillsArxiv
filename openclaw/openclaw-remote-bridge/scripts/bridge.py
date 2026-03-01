#!/usr/bin/env python3
"""Core orchestrator: receive a message from OpenClaw, invoke Claude Code, reply.

Called by OpenClaw's exec tool:
    python3 bridge.py --sender <id> --channel <ch> --message "text"

Flow:
    1. Check channel connectivity
    2. Get or create Claude Code session for (channel, sender)
    3. Invoke: claude -p "message" --output-format json --session-id <uuid>
    4. Parse JSON response, extract result text
    5. Format/split for channel limits
    6. Send each chunk via: openclaw message send --to <id> --channel <ch> --message "chunk"
"""

import argparse
import json
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLAUDE_TIMEOUT = 300  # seconds


def check_channel(channel: str) -> bool:
    result = subprocess.run(
        [os.path.join(SCRIPT_DIR, "channel_check.sh"), channel],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def get_session(channel: str, sender: str) -> str:
    result = subprocess.run(
        [sys.executable, os.path.join(SCRIPT_DIR, "session_manager.py"),
         "get", "--channel", channel, "--sender", sender],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def invoke_claude(message: str, session_id: str) -> str:
    """Invoke claude CLI in non-interactive mode and return the result text."""
    cmd = [
        "claude", "-p", message,
        "--output-format", "json",
        "--session-id", session_id,
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=CLAUDE_TIMEOUT,
        )
    except FileNotFoundError:
        raise RuntimeError("claude CLI not found — is Claude Code installed?")
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Claude timed out after {CLAUDE_TIMEOUT}s")

    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(f"claude exited {result.returncode}: {stderr}")

    # Parse JSON output
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        # Fall back to raw text if JSON parsing fails
        return result.stdout.strip()

    # Extract result text — claude --output-format json returns {"result": "...", ...}
    if isinstance(data, dict):
        return data.get("result", data.get("text", json.dumps(data)))
    return str(data)


def format_response(text: str, channel: str) -> list[str]:
    result = subprocess.run(
        [sys.executable, os.path.join(SCRIPT_DIR, "format_response.py"),
         "--channel", channel, "--text", text],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def send_message(to: str, channel: str, message: str) -> None:
    subprocess.run(
        ["openclaw", "message", "send",
         "--to", to, "--channel", channel, "--message", message],
        check=True, capture_output=True, text=True,
    )


def handle_special_commands(message: str, channel: str, sender: str) -> str | None:
    """Handle bridge-local special commands. Returns response text or None."""
    cmd = message.strip().lower()

    if cmd == "/status":
        connected = check_channel(channel)
        session_id = get_session(channel, sender)
        status = "connected" if connected else "disconnected"
        return f"Channel: {channel} ({status})\nSession: {session_id[:8]}..."

    if cmd == "/reset":
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, "session_manager.py"),
             "reset", "--channel", channel, "--sender", sender],
            capture_output=True, text=True,
        )
        return "Session reset. Next message starts a fresh conversation."

    if cmd == "/help":
        return (
            "Claude Code Bridge Commands:\n"
            "  /status  — Show channel and session info\n"
            "  /reset   — Start a fresh Claude conversation\n"
            "  /help    — Show this message\n\n"
            "Everything else is forwarded to Claude Code."
        )

    return None


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenClaw → Claude Code bridge")
    parser.add_argument("--sender", required=True, help="Sender identifier")
    parser.add_argument("--channel", required=True, help="Messaging channel (whatsapp, discord, ...)")
    parser.add_argument("--message", required=True, help="Message text")
    args = parser.parse_args()

    try:
        # Handle special commands locally
        special = handle_special_commands(args.message, args.channel, args.sender)
        if special is not None:
            chunks = format_response(special, args.channel)
            for chunk in chunks:
                send_message(args.sender, args.channel, chunk)
            return

        # Check channel
        if not check_channel(args.channel):
            send_message(args.sender, args.channel,
                         f"Channel '{args.channel}' is not connected. Check OpenClaw gateway.")
            return

        # Get session
        session_id = get_session(args.channel, args.sender)

        # Invoke Claude
        response = invoke_claude(args.message, session_id)

        # Format and send
        chunks = format_response(response, args.channel)
        for chunk in chunks:
            send_message(args.sender, args.channel, chunk)

    except Exception as e:
        error_msg = f"Bridge error: {e}"
        print(error_msg, file=sys.stderr)
        try:
            send_message(args.sender, args.channel, error_msg)
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
