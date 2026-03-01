# Task Format for Code Dispatch

Create tasks in the **🤖 CodeDispatch** TickTick project. The dispatcher picks them up automatically.

## Format

**Title** = Your coding prompt. This is sent directly to the OpenCode agent.

**Content** = Dispatch metadata (first lines before `---`):

```
Remote: <ssh_host> → <folder_path>
Clone: <git_url>                        (optional)
Agent: build|plan                       (optional, default: build)
```

### Fields

| Field | Required | Description |
|---|---|---|
| `Remote:` | Yes | SSH config host name → project folder on that machine |
| `Clone:` | No | Git clone URL — used if the folder doesn't exist on the remote |
| `Agent:` | No | OpenCode agent to use: `build` (default) or `plan` |

### Available SSH Hosts

Check your `~/.ssh/config` for available host aliases. The dispatcher validates the host before dispatching.

## Examples

### Simple task

**Title:** Fix the type error in src/auth/middleware.ts

**Content:**
```
Remote: fuji3 → ~/projects/my-api
```

### Task with clone URL

**Title:** Set up the initial project structure with Express + TypeScript

**Content:**
```
Remote: gala1 → ~/projects/new-service
Clone: git@github.com:user/new-service.git
```

### Task using plan agent

**Title:** Analyze the codebase and propose a refactoring plan for the auth module

**Content:**
```
Remote: fuji3 → ~/projects/my-api
Agent: plan
```

## Checklist Items

The dispatcher creates and ticks off checklist items as stages complete:

1. ☐ Validate remote host & folder
2. ☐ Launch opencode serve via SSH
3. ☐ Send prompt to agent
4. ☐ Monitor progress
5. ☐ Collect results & diff

## Status Log

The dispatcher appends status lines below `---` in the task content:

```
Remote: fuji3 → ~/projects/my-api
---
🔄 2026-03-01 00:12 — Dispatched
🔄 2026-03-01 00:14 — Reconnected after SSH drop
✅ 2026-03-01 00:18 — Done. 3 files changed
```

Status emojis:
- 🔄 In progress / dispatched
- ✅ Completed successfully
- ❌ Failed
- ⚠️ Blocked (e.g., folder not found, invalid host)

## WhatsApp Notifications

When `--notify` is set, the dispatcher sends tagged messages:

- `[🔄 fuji3/my-api]` — Progress updates (throttled to every 30s)
- `[❓ fuji3/my-api]` — Agent questions (reply to answer)
- `[✅ fuji3/my-api]` — Completion with diff summary
- `[❌ fuji3/my-api]` — Failure with reason
- `[⚠️ fuji3/my-api]` — Blocked (action needed)

## Tips

1. **Keep titles concise but specific** — they're the actual prompt sent to the coding agent
2. **One task per coding action** — don't batch multiple unrelated changes
3. **Use the plan agent** for analysis/review tasks that shouldn't modify files
4. **Add Clone: URL** for new repos — the dispatcher will git clone automatically
5. **Check `--status`** to see active dispatch jobs: `python dispatcher.py --status`
