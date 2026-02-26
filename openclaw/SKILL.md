---
name: openclaw
description: >
  Bridge OpenClaw messaging channels (WhatsApp, Discord, Telegram, Slack, etc.) to Claude Code CLI.
  Use when the user wants to set up remote access to Claude Code through messaging apps,
  configure the OpenClaw-to-Claude bridge, manage cross-channel sessions, debug message routing,
  or format Claude responses for channel-specific limits.
---

# OpenClaw Bridge for Claude Code

Connects OpenClaw's 22+ messaging channels to Claude Code, letting users interact with Claude through WhatsApp, Discord, Telegram, and other platforms.

## Architecture

```
User (WhatsApp/Discord/...)
  → OpenClaw Gateway
    → bridge.py --sender <id> --channel <ch> --message "text"
      → session_manager.py → claude -p --session-id <uuid>
      → format_response.py → split for channel limits
    → openclaw message send → User receives reply
```

## Quick Start

1. **Verify gateway is running:**
   ```bash
   openclaw gateway status
   ```

2. **Install the bridge skill into OpenClaw:**
   ```bash
   bash scripts/setup_openclaw_skill.sh
   ```

3. **Pair a channel and test:**
   ```bash
   openclaw channels pair whatsapp
   # Send a message through WhatsApp → should get a Claude response
   ```

## Core Scripts

| Script | Purpose |
|--------|---------|
| `scripts/bridge.py` | Main orchestrator — receives messages, invokes Claude, sends replies |
| `scripts/session_manager.py` | Maps (channel, sender) to Claude session UUIDs with 24h TTL |
| `scripts/format_response.py` | Splits responses for per-channel character limits |
| `scripts/channel_check.sh` | Probes OpenClaw channel connectivity |
| `scripts/setup_openclaw_skill.sh` | Installs bridge skill into OpenClaw workspace |

## Interactive Commands

Users can send these through any channel:

| Command | Action |
|---------|--------|
| `/status` | Show channel connectivity and session info |
| `/reset` | Clear session, start a fresh Claude conversation |
| `/help` | List available commands |

All other messages are forwarded to Claude Code.

## Session Management

Sessions map each (channel, sender) pair to a Claude Code session UUID. Managed by `session_manager.py`:

```bash
# Get or create session
python3 scripts/session_manager.py get --channel whatsapp --sender "+1234567890"

# List all sessions
python3 scripts/session_manager.py list

# Reset a specific session
python3 scripts/session_manager.py reset --channel discord --sender "user#1234"

# Reset all sessions
python3 scripts/session_manager.py reset-all
```

Sessions expire after 24 hours by default (configurable via `--ttl`).

## Reference Files

- `references/openclaw-commands.md` — OpenClaw CLI commands (gateway, channels, messages, skills)
- `references/claude-cli-flags.md` — Claude Code non-interactive flags (`-p`, `--output-format json`, `--session-id`)
- `references/channel-formatting.md` — Per-channel character limits, markdown support matrix, code block handling
