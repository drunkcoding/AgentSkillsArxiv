# AGENTS.md - Learnings & Architecture

This document records architectural decisions, operational knowledge, and integration lessons learned during development and testing of the openclaw-remote-dispatch plugin.

## Architecture Decisions

### Content-based Phase Tracking (not API items)
The TickTick Open API v1 only supports `items` (checklist sub-tasks) on tasks created with `kind: "CHECKLIST"`. Since dispatch tasks are created by users as regular `TASK` kind, the plugin uses markdown-formatted phase progress in the `content` field instead. The 8 phases use ✅/⏳/⬜ markers with per-phase metadata.

### update_task Requires projectId
All TickTick `update_task` calls must include `projectId` in the request body. Without it, the API returns empty `{}` and silently ignores the update. This was discovered during integration testing when both status lines and checklist items failed to persist.

### LLM Fallback Chain for Session Matching
The session matcher uses a 3-stage funnel: hard filter (host+folder match) -> fuzzy scoring (rapidfuzz token_sort_ratio) -> LLM tie-breaker. The LLM chain is `claude-haiku-4-5 -> gpt-5.1 -> gpt-4o` with per-provider circuit breakers (3 failures -> 10min cooldown). API key auth takes priority over subscription.

### Event-Driven Monitoring via SSE
The dispatcher monitors agent progress through OpenCode Serve's SSE `/global/event` endpoint. Events are normalized into `TextEvent` and `ToolEvent` types for stuck detection and plan detection. The `assistant.message.completed` event signals job completion.

### Stale Job Resume with TickTick Validation
On daemon restart, stale jobs (running/pending with a local_port) are validated against TickTick before reattachment:
- Task deleted -> mark failed, cleanup runtime
- Task completed -> mark done, cleanup runtime
- Task still open -> attempt reattach to running opencode serve

### TypeScript Gateway Plugin Structure
External OpenClaw plugins require:
1. `package.json` with `"openclaw": { "extensions": ["./index.ts"] }` — this is what `openclaw plugins install` validates
2. `openclaw.plugin.json` with plugin `id`, `name`, `description`, and optional `configSchema`
3. **CRITICAL**: The `name` in `package.json` (unscoped) must match the `id` in `openclaw.plugin.json`. The installer derives the plugin ID from `package.json` name, but the registry uses the `id` from `openclaw.plugin.json`. Mismatch causes `plugin not found` during config validation.
4. Plugins are installed to `~/.openclaw/extensions/<pluginId>/` and auto-enabled in `openclaw.json`
5. The gateway's TypeScript loader handles `.ts` files directly — no build step needed

### Plugin Script Resolution
When a plugin is installed to `~/.openclaw/extensions/`, its `__dirname` is that directory. If the plugin references companion scripts (like Python files), the path must be resolved carefully:
- Self-contained: include scripts in the plugin dir or use `path.resolve(__dirname, "scripts/")`
- Skill bridge: resolve from `~/.openclaw/workspace/skills/<skill-name>/scripts/`
- Use a search path array and `accessSync()` to find the first valid location at import time

## Operational Knowledge

### Testing Dispatch
1. Create tasks in `🤖 CodeDispatch` project on TickTick
2. Use `Local: ~/path` or `Remote: hostname -> ~/path` in content
3. Run: `python3 dispatcher.py --daemon --notify '+E164PHONE' --interval 10 --max-concurrent 1`
4. Use `PYTHONUNBUFFERED=1` for live log output in daemon mode

### Credential Locations
- TickTick OAuth2: `~/.clawdbot/credentials/ticktick-cli/config.json`
- OpenClaw config: `~/.openclaw/openclaw.json`
- API keys (OpenAI): `~/.openclaw/.env`
- SSH config: `~/.ssh/config`

### State Files
- Dispatch state: `~/.openclaw/remote-dispatch-state.json`
- Session registry: `~/.openclaw/session-registry.json`
- Session graph: `~/.openclaw/session-graph.json`

### Common Failure Modes
1. **Silent update failure**: TickTick returns `{}` when `projectId` missing from update body
2. **Notification failure**: Using contact name instead of E.164 phone number
3. **Port exhaustion**: Multiple stale jobs consuming dispatch slots
4. **JSON decode on shutdown**: OpenCode `/global/shutdown` returns non-JSON
5. **Plugin ID mismatch**: `package.json` name vs `openclaw.plugin.json` id must match (unscoped) or install fails with `plugin not found`
6. **Script path ENOENT**: Plugin installed to `~/.openclaw/extensions/` cannot find companion scripts at `../scripts/` — use multi-path resolution

### Daemon Management
```bash
# Start daemon (background)
nohup python3 -u dispatcher.py --daemon --notify '+447XXXXXXXXX' > /tmp/dispatch.log 2>&1 &

# Check logs
tail -f /tmp/dispatch.log

# Check state
python3 dispatcher.py --status

# Clean old jobs
python3 dispatcher.py --cleanup

# Kill daemon
kill $(pgrep -f "dispatcher.py --daemon")
```

## Integration Test Checklist

Before deploying changes:

1. [ ] `python3 -c "import dispatcher; import notifier; import config; print('OK')"` - modules compile
2. [ ] Create test task on TickTick, verify parsing
3. [ ] Run `--dry-run` to validate hosts
4. [ ] Run daemon with `--max-concurrent 1 --interval 10` 
5. [ ] Verify Phase Progress appears in TickTick task content
6. [ ] Verify status lines appear (`🔄 Dispatched`, `✅ Done`)
7. [ ] Verify stale job resume handles deleted/completed tasks
8. [ ] Check notification delivery (E.164 format)
9. [ ] `bash setup.sh` to reinstall skill
10. [ ] Copy plugin files: `cp plugin/* ~/.openclaw/extensions/remote-dispatch/`
11. [ ] `openclaw gateway restart` to reload
12. [ ] Verify plugin in `openclaw plugins list` (status: loaded)

## File Map

| File | Purpose | Lines |
|------|---------|-------|
| `dispatcher.py` | Main orchestrator, lifecycle management | ~1600 |
| `ticktick_client.py` | TickTick Open API v1 client | ~450 |
| `ticktick_cli.py` | General-purpose TickTick CLI | ~580 |
| `opencode_client.py` | OpenCode Serve HTTP client | ~200 |
| `ssh_tunnel.py` | SSH tunnel + local/remote opencode lifecycle | ~350 |
| `notifier.py` | WhatsApp notifications via openclaw CLI | ~200 |
| `config.py` | Configuration with env var overrides | ~106 |
| `state.py` | Persistent job state (JSON + file lock) | ~165 |
| `task_parser.py` | Task content parsing | ~120 |
| `llm_client.py` | Multi-provider LLM with circuit breaker | ~200 |
| `intent_router.py` | Keyword-based agent selection | ~60 |
| `event_normalizer.py` | SSE event normalization | ~80 |
| `stuck_detector.py` | 4-pattern loop detection | ~120 |
| `plan_gate.py` | Plan detection + approval flow | ~100 |
| `session_registry.py` | Persistent session store | ~100 |
| `session_matcher.py` | 3-stage relevance funnel | ~120 |
| `session_graph.py` | DAG with cycle detection | ~100 |
