---
name: function-dep-search
description: AST-accurate function dependency analysis using Tree-sitter. Use when tracing function call chains, finding callers/callees, analyzing blast radius of changes, detecting unused functions, or finding circular dependencies. Replaces grep-based code exploration with precise, structural matching. Supports Python, JavaScript, TypeScript, Go, Rust, C, C++, Java. Triggers on questions like "what calls X?", "what does X call?", "find unused functions", "show me the call graph", "what's the impact of changing X?", or any function dependency/relationship query.
---

# Function Dependency Search

AST-based function dependency analysis via Tree-sitter. More precise and faster than grep for understanding function relationships in code.

## Quick Start

```bash
# Install dependencies (auto-installs per-language grammars)
python3 scripts/fdep.py --install defs <path>

# Or install manually
pip install tree-sitter tree-sitter-python tree-sitter-javascript
```

## Commands

| Command | Usage | Purpose |
|---------|-------|---------|
| `defs` | `fdep.py defs <paths>` | List all function definitions |
| `calls` | `fdep.py calls <paths>` | Show call graph (caller -> callees) |
| `callees` | `fdep.py callees <func> <paths>` | What does `<func>` call? |
| `callers` | `fdep.py callers <func> <paths>` | What calls `<func>`? |
| `deps` | `fdep.py deps <func> <paths>` | Transitive dependencies (downstream) |
| `rdeps` | `fdep.py rdeps <func> <paths>` | Reverse transitive deps (upstream impact) |
| `unused` | `fdep.py unused <paths>` | Functions never called |
| `circular` | `fdep.py circular <paths>` | Circular dependency detection |
| `graph` | `fdep.py graph <paths>` | Full call graph |

### Output Formats

- `--json` — Structured JSON (best for programmatic use)
- `--dot` — Graphviz DOT (for `graph`, `deps`, `rdeps`)
- Default — Human-readable text with `file:line` locations

### Options

- `--depth N` — Max transitive depth (default: 10)
- `--lang LANG` — Force language instead of auto-detect from extension
- `--install` — Auto-install missing tree-sitter packages

## When to Use Which Command

**Understanding a function:** `callees` to see what it does, `callers` to see who uses it.

**Change impact analysis:** `rdeps` to find all upstream callers transitively — shows blast radius.

**Refactoring safety:** `unused` to find dead code. `circular` to find tangled dependencies.

**Codebase overview:** `graph` for full call graph. `defs` for function inventory.

**Debugging a chain:** `deps` to trace the full downstream call chain from an entry point.

## Supported Languages

Auto-detected from file extensions. Use `--lang` to override.

| Language | Extensions | Package |
|----------|-----------|---------|
| Python | .py, .pyi | tree-sitter-python |
| JavaScript | .js, .jsx, .mjs, .cjs | tree-sitter-javascript |
| TypeScript | .ts, .tsx | tree-sitter-typescript |
| Go | .go | tree-sitter-go |
| Rust | .rs | tree-sitter-rust |
| C | .c, .h | tree-sitter-c |
| C++ | .cpp, .cc, .hpp, etc. | tree-sitter-cpp |
| Java | .java | tree-sitter-java |

## Extending Queries

See [references/queries.md](references/queries.md) for per-language tree-sitter query patterns and instructions for adding new languages.
