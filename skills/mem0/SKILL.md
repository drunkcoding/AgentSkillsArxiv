---
name: mem0
description: >
  Per-agent persistent memory for oh-my-open-code. Stores and retrieves knowledge
  across sessions using agent_id scoping — each agent (oracle, librarian, explore,
  sisyphus, deep, etc.) maintains its own memory namespace while allowing cross-agent
  search. Primary use case: persisting deep research findings, architecture decisions,
  library patterns, and codebase knowledge. Triggers on: "remember", "store this",
  "what do we know about", "recall", "search memory", "persist findings", or any
  need to retain knowledge across sessions.
---

# mem0 — Per-Agent Persistent Memory for oh-my-open-code

Local-first, session-persistent memory layer. Each agent stores knowledge under its own `agent_id`. All agents can search across namespaces.

**Storage**: `~/.local/share/opencode/mem0/` (configurable via `MEM0_LOCAL_STORE_PATH`).

## Agent Memory Namespaces

| `agent_id` | What to Store | Examples |
|------------|--------------|---------|
| `oracle` | Architecture decisions, debugging breakthroughs, complex tradeoff analyses | "JWT refresh tokens stored in httpOnly cookies, not localStorage — XSS risk" |
| `librarian` | Library API patterns, version-specific gotchas, documentation findings | "fastapi 0.115+ requires `lifespan` instead of `on_event` for startup/shutdown" |
| `explore` | Codebase structural patterns, module relationships, convention discoveries | "All API routes in src/api/ use dependency injection via `Depends(get_db)`" |
| `deep` | Deep research conclusions, multi-source synthesis, investigation outcomes | "Qdrant outperforms Chroma at >1M vectors; switch threshold identified at 500K" |
| `sisyphus` | Project-level decisions, user preferences, recurring task patterns | "User prefers minimal PRs — one concern per PR, no drive-by refactors" |
| `metis` | Requirement ambiguities found, scope clarifications, pre-planning insights | "Auth module: user said 'simple login' but codebase has RBAC — clarify scope" |
| `momus` | Review findings, quality gaps identified, recurring plan weaknesses | "Plans often miss error handling — always check for catch blocks in delegation" |

## When to Store

**STORE when:**
- Research yields a non-obvious finding that took effort to discover
- A debugging session reveals root cause that wasn't apparent
- An architecture decision is made with specific reasoning
- A library has version-specific behavior or gotchas
- A codebase convention is discovered that isn't documented
- User states a preference or working style

**DO NOT store:**
- Trivial facts easily found via grep (file paths, function names)
- Temporary debugging state (use `run_id` scoping for that)
- Anything already in the codebase's own documentation
- Raw tool output — distill first, then store the insight

## Core Operations

### Store a Finding

```
mem0_add(
    data="<concise insight — what was learned and why it matters>",
    agent_id="<your-agent-name>",
    metadata={"source": "<where-found>", "topic": "<domain>", "project": "<project-name>"}
)
```

**Good memory content** (distilled, actionable):
```
"The payments module uses eventual consistency — OrderCreated events are processed
async by PaymentService. Direct DB queries after order creation will miss payment
status for ~200ms. Use the event bus callback instead."
```

**Bad memory content** (raw, undistilled):
```
"Found some stuff in payments/service.py about async processing"
```

### Search for Knowledge

```
# Search own agent's memories
mem0_search(query="authentication patterns", agent_id="oracle")

# Cross-agent search — find what librarian discovered about a library
mem0_search(query="fastapi lifespan migration", agent_id="librarian")

# Broad search — omit agent_id to search across all agents
mem0_search(query="database connection pooling")

# Narrow with limit
mem0_search(query="JWT security best practices", agent_id="oracle", limit=3)
```

### Retrieve All Agent Memories

```
# All memories for a specific agent
mem0_list(agent_id="explore")

# Combined scope — agent memories for a specific user context
mem0_list(agent_id="librarian", user_id="project-acme")
```

### Update / Delete

```
# Correct outdated information
mem0_update(memory_id="<uuid>", data="Updated: fastapi 0.116 reverted lifespan change")

# Remove stale memories
mem0_delete(memory_id="<uuid>")

# Nuclear option — clear all memories for an agent
mem0_delete_all(agent_id="deep", confirm=true)
```

### Check Health

```
mem0_health()
```

## Deep Research Memory Pattern

When a research-intensive task completes, the agent should persist key findings:

```
# After deep investigation, store the synthesis (not raw findings)
mem0_add(
    data="React Server Components: Cannot use useState/useEffect. For interactive
    elements, mark with 'use client'. Server components can async/await directly.
    fetch() in server components auto-dedupes. Mixing: server components can import
    client components but NOT vice versa.",
    agent_id="deep",
    metadata={
        "topic": "react-server-components",
        "source": "next.js docs + vercel blog + react RFC",
        "confidence": "high",
        "project": "frontend-migration"
    }
)
```

### Before Starting Research — Check Memory First

```
# Before launching explore/librarian agents, check if we already know this
mem0_search(query="react server components patterns", agent_id="deep")
mem0_search(query="react server components", agent_id="librarian")
```

If relevant memories exist with high confidence, skip redundant research.

## Metadata Conventions

Use consistent metadata keys for queryable context:

| Key | Purpose | Examples |
|-----|---------|---------|
| `topic` | Knowledge domain | `"auth"`, `"database"`, `"react-hooks"` |
| `source` | Where the knowledge came from | `"codebase-analysis"`, `"official-docs"`, `"debugging-session"` |
| `project` | Which project this applies to | `"acme-api"`, `"frontend-app"` |
| `confidence` | How reliable the finding is | `"high"`, `"medium"`, `"speculative"` |

## Cross-Project Memory (Knowledge Merge)

Cross-project memory lets you reuse what you learned in one coding session inside later pseudocode, planning, or workflow sessions. Instead of re-discovering conventions for every repository, you store reusable patterns once and then pull them into any project that shares the same problems.

### Metadata shape for cross-project patterns

Use metadata to say where a pattern came from and how broad it is.

Recommended conventions:

- `app_id`: stable identifier for the project or app that produced the pattern, for example `"mem0-mcp-server"` or `"research-notebooks"`.
- `scope`: either `"global"` for patterns that should apply across many projects, or `"project"` for patterns that are specific to a single codebase.
- `abstraction_type`: what kind of pattern this is, for example `"testing_pattern"`, `"client_setup"`, `"workflow"`, `"prompting"`.
- Optional extras, reused from earlier sections: `topic`, `source`, `confidence`.

Store cross-project patterns under a dedicated agent namespace:

- `agent_id="patterns"` for reusable abstractions that you want to merge across projects.

### Writing patterns

Global pattern written from a coding session:

```python
mem0_add(
    data=(
        "mem0 MCP tools should forward filters and limit directly to the "
        "underlying client without reshaping the dictionary."
    ),
    agent_id="patterns",
    metadata={
        "app_id": "mem0-cross-project-memory",
        "scope": "global",
        "abstraction_type": "api_contract",
        "topic": "mem0",
        "source": "coding_session",
    },
)
```

Project-scoped variant linked to a specific app:

```python
mem0_add(
    data=(
        "mem0 MCP server tests use MagicMock for MemoryClient and assert "
        "filters and limit passthrough on search and get_all."
    ),
    agent_id="patterns",
    metadata={
        "app_id": "mem0-mcp-server",
        "scope": "project",
        "abstraction_type": "testing_pattern",
        "topic": "mem0",
        "source": "tests",
    },
)
```

Both examples share the same `agent_id="patterns"` namespace so you can search across apps while still filtering by `app_id` and `scope`.

### Reading patterns

Load global patterns for a new project:

```python
global_patterns = mem0_search(
    query="mem0 integration pattern",
    agent_id="patterns",
    filters={"scope": "global"},
)
```

Load patterns that belong to a single app:

```python
project_patterns = mem0_search(
    query="testing pattern",
    agent_id="patterns",
    filters={"app_id": "mem0-mcp-server"},
)
```

You can also pull every pattern for a scope with `mem0_list`:

```python
all_global = mem0_list(
    agent_id="patterns",
    filters={"scope": "global"},
)

mem0_mcp_patterns = mem0_list(
    agent_id="patterns",
    filters={"app_id": "mem0-mcp-server"},
)
```

### Filter syntax by profile

Filters are passed straight through to the mem0 backend, so you need to match what your profile supports.

Local profile (for example Qdrant, SQLite, simple vector stores):

- Use flat key value dictionaries such as `filters={"app_id": "mem0-mcp-server", "scope": "global"}`.
- Keys are combined with implicit AND semantics.
- Complex logical trees or range operators might not work, even if you see them in hosted mem0 examples.

Hosted or platform profile (mem0 cloud, platform vector stores):

- Might support advanced filters such as:

```python
filters={
    "AND": [
        {"scope": "global"},
        {"abstraction_type": {"in": ["workflow", "api_contract"]}},
    ]
}
```

- Treat this shape as hosted only. Do not rely on it for local first tools unless the backend explicitly documents support.

### Recommended workflow

At the end of a coding session:

1. Scan the work you just finished.
2. Distill reusable ideas into short, technology neutral sentences.
3. Store them with `mem0_add`, `agent_id="patterns"`, and metadata such as:

   - `app_id` for the current project
   - `scope="global"` for broadly useful ideas, or `scope="project"` for codebase specific patterns
   - `abstraction_type` to describe what kind of pattern you are saving

At the start of a new session:

1. Load global patterns with `mem0_search(..., agent_id="patterns", filters={"scope": "global"})`.
2. Optionally load project specific history with `filters={"app_id": "<current-app-id>"}`.
3. Use the retrieved patterns to guide new designs, pseudocode, and workflow planning before you touch the code.

This keeps cross-project knowledge in a form that survives repo changes and lets planning sessions benefit from past coding work.

### Anti-patterns

Avoid these failure modes:

- Do not dump raw code into the `patterns` namespace. Store the idea, not the entire function body.
- Do not use project specific variable names in global patterns. Prefer neutral descriptions that make sense in any repo.
- Do not save patterns without metadata. Always include at least `app_id`, `scope`, and `abstraction_type` so you can filter later.
- Do not rely on hosted only filter syntax when you are running against a local Qdrant profile.

## Session-Scoped Memory (`run_id`)

For temporary context within a single work session (discardable after):

```
mem0_add(
    data="Current debugging: the 500 error traces to middleware ordering — cors must come before auth",
    agent_id="oracle",
    run_id="debug-session-2024-01-15"
)
```

Use `run_id` for ephemeral notes. Use `agent_id` alone for permanent knowledge.

## Configuration

All configuration via environment variables in `opencode.json`:

| Variable | Default | Purpose |
|----------|---------|---------|
| `MEM0_PROFILE` | `local` | Storage profile (`local`, `hosted`, `custom`) |
| `MEM0_LOCAL_STORE_PATH` | `~/.local/share/opencode/mem0/` | Where qdrant stores vector data |
| `MEM0_DEFAULT_USER_ID` | *(none)* | Fallback user_id when none specified |
| `MEM0_API_KEY` | *(none)* | Only for `hosted` profile |
| `MEM0_CONFIG_PATH` | *(none)* | JSON config file for `custom` profile |

**Local storage is persistent across sessions and reboots.** Data lives at the configured path until explicitly deleted.
