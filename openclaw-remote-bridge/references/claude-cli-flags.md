# Claude Code CLI Flags for Non-Interactive Use

## Core Flags Used by the Bridge

```bash
claude -p "prompt"                    # Non-interactive: send prompt, get response, exit
claude --output-format json           # JSON output: {"result": "...", "session_id": "...", ...}
claude --session-id <uuid>            # Resume an existing conversation session
```

Combined (what bridge.py runs):
```bash
claude -p "message" --output-format json --session-id <uuid>
```

## Additional Useful Flags

```bash
claude --max-turns <n>                # Limit agentic turns (default: unlimited in -p mode)
claude --allowedTools "tool1,tool2"   # Restrict which tools Claude can use
claude --model <model-id>            # Override model (e.g. claude-sonnet-4-6)
claude --verbose                      # Show detailed execution info
```

## Output Format

With `--output-format json`, Claude returns:

```json
{
  "result": "The response text...",
  "session_id": "uuid-of-session",
  "cost_usd": 0.042,
  "duration_ms": 3200,
  "num_turns": 1
}
```

The bridge extracts `result` for the reply. If JSON parsing fails, raw stdout is used.

## Session Behavior

- `--session-id` resumes a prior conversation with full context
- Sessions persist in `~/.claude/` managed by Claude Code itself
- The bridge's `session_manager.py` maps (channel, sender) → session UUID
- Sessions are separate from OpenClaw sessions — one is Claude's, the other is OpenClaw's

## Error Exit Codes

| Code | Meaning                 |
|------|-------------------------|
| 0    | Success                 |
| 1    | General error           |
| 2    | Invalid arguments       |
| 124  | Timeout (via `timeout` wrapper) |
