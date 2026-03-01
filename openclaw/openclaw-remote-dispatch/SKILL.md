---
name: openclaw-remote-dispatch
description: Poll TickTick for coding tasks and dispatch them to remote machines via SSH + OpenCode Serve. Includes full TickTick CLI (tasks, projects, create, complete, abandon, batch operations) with OAuth2 auth, rate limit handling, and WhatsApp progress notifications.
---

# Remote Code Dispatch Plugin

Poll a dedicated TickTick project (`🤖 CodeDispatch`) for coding tasks, SSH into remote machines, launch OpenCode Serve, dispatch prompts, monitor progress, and notify via WhatsApp. Also includes a full general-purpose TickTick CLI.

## Setup

### 1. Prerequisites

- Python 3.10+
- SSH access to remote machines (configured in `~/.ssh/config`)
- OpenCode CLI installed on remote machines (`opencode serve` available)
- TickTick OAuth2 credentials (shared with existing ticktick skill)
- OpenClaw CLI (optional — for WhatsApp notifications)

### 2. TickTick Authentication

This plugin reuses credentials from the existing ticktick skill at `~/.clawdbot/credentials/ticktick-cli/config.json`.

If not already authenticated:

```bash
# Using the existing bun/ts skill
bun run ~/.openclaw/skills/ticktick/scripts/ticktick.ts auth --client-id YOUR_ID --client-secret YOUR_SECRET

# Or check status via this plugin
python scripts/ticktick_cli.py auth --status
```

### 3. Install

```bash
# From the plugin directory
bash setup.sh
```

This symlinks the skill into `~/.openclaw/workspace/skills/openclaw-remote-dispatch`.

## Dispatcher Commands

### One-shot poll

```bash
# Poll once, dispatch any new tasks
python scripts/dispatcher.py --notify "+1234567890"

# Dry-run: validate parsing + hosts without dispatching
python scripts/dispatcher.py --dry-run

# Custom project and interval
python scripts/dispatcher.py --notify "+1234567890" --project "🤖 CodeDispatch" --interval 30
```

### Daemon mode

```bash
# Run continuously, polling every 60s
python scripts/dispatcher.py --daemon --notify "+1234567890"

# With custom settings
python scripts/dispatcher.py --daemon --notify "+1234567890" --channel whatsapp --max-concurrent 3
```

### Reply routing

```bash
# Forward a WhatsApp reply to an active coding session
python scripts/dispatcher.py --reply TASK_ID "Yes, use the async version"
```

### Status & cleanup

```bash
# Show active dispatch jobs
python scripts/dispatcher.py --status

# Remove old finished jobs from state
python scripts/dispatcher.py --cleanup
```

## TickTick CLI Commands

Full general-purpose TickTick management, equivalent to the bun/ts skill:

### List Tasks

```bash
# List all tasks
python scripts/ticktick_cli.py tasks

# Filter by project
python scripts/ticktick_cli.py tasks --list "Work"

# Filter by status
python scripts/ticktick_cli.py tasks --status pending
python scripts/ticktick_cli.py tasks --status completed

# JSON output
python scripts/ticktick_cli.py tasks --json
```

### Create Task

```bash
# Basic task
python scripts/ticktick_cli.py task "Buy groceries" --list "Personal"

# With description and priority
python scripts/ticktick_cli.py task "Review PR" --list "Work" --content "Check auth changes" --priority high

# With due date
python scripts/ticktick_cli.py task "Submit report" --list "Work" --due tomorrow
python scripts/ticktick_cli.py task "Plan vacation" --list "Personal" --due "in 7 days"

# With tags
python scripts/ticktick_cli.py task "Research" --list "Work" --tag research important
```

### Update Task

```bash
# Update by task name or ID
python scripts/ticktick_cli.py task "Buy groceries" --update --priority medium
python scripts/ticktick_cli.py task "abc123def456..." --update --due tomorrow --content "Updated notes"

# Limit search to specific project
python scripts/ticktick_cli.py task "Review PR" --update --list "Work" --priority low
```

### Complete Task

```bash
python scripts/ticktick_cli.py complete "Buy groceries"
python scripts/ticktick_cli.py complete "Review PR" --list "Work"
```

### Abandon Task (Won't Do)

```bash
python scripts/ticktick_cli.py abandon "Old task"
python scripts/ticktick_cli.py abandon "Obsolete item" --list "Do"
```

### Batch Abandon

```bash
# Abandon multiple tasks in a single API call (requires task IDs)
python scripts/ticktick_cli.py batch-abandon abc123... def456... --json
```

### List Projects

```bash
python scripts/ticktick_cli.py lists
python scripts/ticktick_cli.py lists --json
```

### Create / Update Project

```bash
# Create
python scripts/ticktick_cli.py list "New Project"
python scripts/ticktick_cli.py list "Work Tasks" --color "#FF5733"

# Update
python scripts/ticktick_cli.py list "Old Name" --update --new-name "New Name"
python scripts/ticktick_cli.py list "Work" --update --color "#00FF00"
```

## Task Format for Dispatch

Create tasks in the `🤖 CodeDispatch` project with this format:

**Title** = the coding prompt (what you want the agent to do)

**Content** = dispatch metadata:

Remote (via SSH):
```
Remote: fuji3 → ~/projects/my-app
Clone: git@github.com:user/repo.git    (optional)
Agent: build                             (optional, default: build)
```

Local (same machine, no SSH):
```
Local: ~/projects/my-app
Clone: git@github.com:user/repo.git    (optional)
Agent: build                             (optional, default: build)
```

The dispatcher automatically appends a status log below `---`:

```
Local: ~/projects/my-app
---
🔄 2026-03-01 00:12 — Dispatched
✅ 2026-03-01 00:18 — Done. 3 files changed
```

See `references/task-format.md` for full format documentation.

## Options Reference

### Priority Levels
- `none` — No priority (default)
- `low` — Low priority
- `medium` — Medium priority
- `high` — High priority

### Due Date Formats
- `today` — Due today
- `tomorrow` — Due tomorrow
- `in N days` — Due in N days (e.g., "in 3 days")
- `next monday` — Next occurrence of weekday
- ISO date — `YYYY-MM-DD` or full ISO format

### Global Options
- `--json` — Output results in JSON format
- `--help` — Show help for any command

## Agent Usage Tips

When using this skill as an AI agent:

1. **Always use `--json` flag** for machine-readable output
2. **List projects first** with `lists --json` to get valid project IDs
3. **Use project IDs** rather than names when possible for reliability
4. **Check task status** before completing to avoid errors
5. For dispatch tasks, ensure the remote host is in `~/.ssh/config`

## Configuration

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DISPATCH_PROJECT` | `🤖 CodeDispatch` | TickTick project for dispatch tasks |
| `DISPATCH_POLL_INTERVAL` | `60` | Polling interval (seconds) |
| `DISPATCH_MAX_CONCURRENT` | `3` | Max simultaneous dispatch jobs |
| `DISPATCH_SSH_RETRY_MAX` | `3` | SSH reconnect attempts |
| `DISPATCH_SSH_RETRY_DELAY` | `5` | Delay between SSH retries (seconds) |
| `DISPATCH_HEALTH_TIMEOUT` | `30` | OpenCode health check timeout (seconds) |
| `DISPATCH_STATE_PATH` | `~/.openclaw/remote-dispatch-state.json` | State file location |
| `DISPATCH_CHANNEL` | `whatsapp` | Notification channel |
| `TICKTICK_REGION` | `intl` | `intl` or `cn` (dida365.com) |
| `TICKTICK_CRED_PATH` | `~/.clawdbot/credentials/ticktick-cli/config.json` | OAuth2 credential file |

### Credential File

Tokens stored in `~/.clawdbot/credentials/ticktick-cli/config.json`:

```json
{
  "clientId": "YOUR_CLIENT_ID",
  "clientSecret": "YOUR_CLIENT_SECRET",
  "accessToken": "...",
  "refreshToken": "...",
  "tokenExpiry": 1234567890000,
  "redirectUri": "http://localhost:8080"
}
```

Credentials are stored in plaintext with 600 permissions. Treat as sensitive.

## API Notes

Uses the [TickTick Open API v1](https://developer.dida365.com/api).

### Rate Limits
- **100 requests per minute**
- **300 requests per 5 minutes**

The CLI has built-in retry with exponential backoff (5s, 15s, 30s, 60s).

### Batch Endpoint
```
POST /batch/task
{"add": [...], "update": [...], "delete": [...]}
```

### Limitations
- Maximum 500 tasks per project
- No webhook support (polling only)
- Tags not readable via V1 API (write-only)
- Some advanced features (focus time, habits) not supported

## Troubleshooting

### "Not authenticated" error
Check credentials: `python scripts/ticktick_cli.py auth --status`

### "Project not found" error
Use `python scripts/ticktick_cli.py lists` to see available projects and IDs.

### "Task not found" error
- Check the task title matches exactly (case-insensitive)
- Try using the task ID instead
- Use `--list` to narrow search to a specific project

### SSH connection failures
- Verify host is in `~/.ssh/config`: check with `ssh -G hostname`
- Ensure `opencode` CLI is installed on the remote machine
- Check SSH key authentication is working

### Token expired errors
The CLI auto-refreshes tokens. If issues persist, re-authenticate via the bun/ts skill.

## Verified Test Results (2026-03-01)

Both local and remote dispatch tested end-to-end against live TickTick API and OpenCode Serve.

### Local Dispatch

**Task:** "Add a hello world function to hello.py that prints current date and time"
**Content:** `Local: ~/dispatch-test-local`

```
$ python3 scripts/dispatcher.py --dry-run
[dry-run] validated task=69a41c6e... host=local folder=~/dispatch-test-local agent=build

$ python3 scripts/dispatcher.py
Local opencode ready on port 25151 in ~/dispatch-test-local
Started 2 new dispatch job(s)

$ cat ~/dispatch-test-local/hello.py
from datetime import datetime

def hello():
    now = datetime.now()
    print(f"Hello, world! Current date and time: {now}")

if __name__ == "__main__":
    hello()

$ python3 ~/dispatch-test-local/hello.py
Hello, world! Current date and time: 2026-03-01 11:07:35.593636
```

### Remote Dispatch (gala1)

**Task:** "Add a hello world function to hello.py that prints hostname and current time"
**Content:** `Remote: gala1 → ~/dispatch-test-remote`

```
$ python3 scripts/dispatcher.py
Remote opencode ready: gala1:59896 → localhost:28059
Started 2 new dispatch job(s)

$ ssh gala1 'cat ~/dispatch-test-remote/hello.py'
from datetime import datetime
import socket

def hello_world() -> None:
    hostname = socket.gethostname()
    current_time = datetime.now().isoformat(timespec="seconds")
    print(f"Hello world from {hostname} at {current_time}")

if __name__ == "__main__":
    hello_world()

$ ssh gala1 'python3 ~/dispatch-test-remote/hello.py'
Hello world from gala1-G482-Z54-00 at 2026-03-01T11:07:36
```
