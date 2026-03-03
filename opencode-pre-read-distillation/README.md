# opencode-pre-read-distillation

Standalone OpenCode plugin that intercepts large `read` outputs in `tool.execute.after` and applies policy-based pre-read distillation.

It is designed to coexist with DCP:

- **This plugin**: pre-read interception (`read` output shaping before context growth)
- **DCP**: post-hoc message pruning/deduplication after tool history accumulates

---

## Installation

Add the plugin to your OpenCode config:

```jsonc
{
  "plugin": [
    "@tarquinen/opencode-dcp@latest",
    "opencode-pre-read-distillation@latest"
  ]
}
```

Or use as a local plugin during development:

```bash
bun install
bun run build
```

Then point OpenCode at the built plugin package from your local registry/workspace.

---

## Configuration

Global config path:

- `~/.config/opencode/prd.jsonc` (or `prd.json`)

Supported precedence:

1. defaults
2. global (`~/.config/opencode/prd.jsonc`)
3. `$OPENCODE_CONFIG_DIR/prd.jsonc`
4. project (`.opencode/prd.jsonc`)

Example `prd.jsonc`:

```jsonc
{
  "$schema": "https://raw.githubusercontent.com/your-org/opencode-pre-read-distillation/main/prd.schema.json",
  "enabled": true,
  "llm": {
    "provider": "openai-compatible",
    "model": "gpt-4o-mini",
    "apiKeyEnv": "OPENAI_API_KEY",
    "baseURL": "https://api.openai.com/v1",
    "timeoutMs": 20000,
    "temperature": 0,
    "maxOutputTokens": 1200
  },
  "policy": {
    "passThroughMaxTokens": 1500,
    "distillMinTokens": 1500,
    "metadataOnlyMinTokens": 12000,
    "maxDistillInputChars": 120000
  },
  "cache": {
    "enabled": true,
    "ttlSec": 86400,
    "maxEntries": 2000,
    "maxBytes": 300000000
  },
  "customTools": {
    "distilledRead": true,
    "rawRead": true,
    "fileOutline": true
  }
}
```

---

## How it works

### Hook lifecycle

```text
read tool executes
   ↓
tool.execute.after (this plugin)
   ↓
decision engine (pass_through | distill | metadata_only)
   ↓
if distill:
  cache lookup (sha256 + model + policyVersion)
   ├─ hit → return cached distilled payload
   └─ miss → call cheap model → validate JSON → cache result
   ↓
output rewritten before LLM sees it
```

### Hooks used

- `tool.execute.after` → intercept built-in `read`
- `tool.definition` → append read-description note about auto-distillation
- `experimental.chat.system.transform` → teach agent when to escalate to `raw_read`
- `chat.message` → capture per-session intent hints for policy decisions
- `tool` → register `distilled_read`, `raw_read`, `file_outline`

---

## Custom tools

- `distilled_read`
  - explicit distill-first read
  - mode overrides: `auto | force_distill | force_metadata | force_raw`
- `raw_read`
  - exact file content (line-numbered, no distillation)
- `file_outline`
  - lightweight symbol outline for TS/JS/Python/Go/Rust

---

## Telemetry and cache storage

- Cache: `~/.local/share/opencode/storage/plugin/prd/cache/`
- Telemetry: `~/.local/share/opencode/storage/plugin/prd/{sessionID}.json`

Tracked metrics:

- `raw_tokens_avoided`
- `distill_tokens_spent`
- `cache_hits`
- `cache_misses`
- `escalation_rate`
- `fallback_rate`

---

## Comparison with DCP

| Concern | DCP | pre-read distillation plugin |
|---|---|---|
| Stage | Post-hoc message transform/pruning | Pre-read tool output interception |
| Trigger | Chat/messages transform + prune tools | `tool.execute.after` on `read` |
| Primary effect | Removes old/noisy context | Prevents oversized context from entering |
| Subagent behavior | Often disabled in DCP setups | Independently configurable here |

Run both together for additive effect.

---

## Tests

```bash
bun run typecheck
bun test
bun run build
```

Test coverage includes:

- policy decisions
- cache behavior and eviction
- distiller model integration with mocked responses
- hook integration (`tool.execute.after`, `tool.definition`)

---

## Implementation order (recommended)

1. `src/types.ts` (data contracts)
2. `src/config.ts` (+ config loading + defaults)
3. `src/policy.ts` (decision engine)
4. `src/distiller.ts` (LLM integration + JSON validation)
5. `src/cache.ts` (hash-keyed cache)
6. `src/telemetry.ts` (session stats)
7. `src/tools.ts` (custom tools)
8. `src/index.ts` (hook wiring)
9. tests (`tests/*.test.ts`)
10. rollout in shadow mode, then progressive activation
