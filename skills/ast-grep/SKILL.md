---
name: ast-grep
description: AST-aware structural code search, rewriting, and linting via ast-grep. Use for structural search (find function calls, match patterns with meta-variables), code rewriting (rename functions, migrate APIs, convert patterns), custom lint rules (detect anti-patterns, enforce conventions), and any task where text-based grep is too imprecise for code structure.
---

# ast-grep: Structural Code Search & Rewriting

AST-aware search, replace, and lint. Matches code structure, not text patterns.

## Installation

Before first use, ensure ast-grep is installed:

```bash
bash /home/xly/AgentSkillsArxiv/ast-grep/scripts/ensure_installed.sh
```

## When to Use ast-grep vs ripgrep

| Need | Tool | Why |
|------|------|-----|
| Find `print(...)` calls | **ast-grep** | Matches function call structure, ignores `# print(...)` in comments |
| Find the string "TODO" | **ripgrep** | Text search across all file types |
| Replace `foo(a, b)` with `bar(b, a)` | **ast-grep** | Captures and reorders arguments structurally |
| Find files containing "error" | **ripgrep** | Simple text matching |
| Detect `except:` without exception type | **ast-grep** | AST node kind matching |
| Search in non-code files (logs, configs) | **ripgrep** | ast-grep only parses code |
| Enforce coding conventions via rules | **ast-grep** | YAML rule engine with fix suggestions |
| Count occurrences of a string | **ripgrep** | Faster for simple counting |

**Rule of thumb:** If you care about code *structure* (calls, assignments, blocks), use ast-grep. If you care about *text content*, use ripgrep.

## Core Commands

### Search — find matching code
```bash
ast-grep run -p 'PATTERN' -l LANG PATH
```
Examples:
```bash
ast-grep run -p 'print($$$)' -l python .
ast-grep run -p 'console.log($$$)' -l javascript src/
ast-grep run -p '$ERR.unwrap()' -l rust .
```

### Rewrite — search and replace structurally
```bash
# Preview (dry run, no changes)
ast-grep run -p 'PATTERN' -r 'REPLACEMENT' -l LANG PATH

# Apply changes
ast-grep run -p 'PATTERN' -r 'REPLACEMENT' -l LANG --update-all PATH
```
Examples:
```bash
# Preview: print → logger.info
ast-grep run -p 'print($MSG)' -r 'logger.info($MSG)' -l python .

# Apply: require → import
ast-grep run -p 'const $N = require($P)' -r 'import $N from $P' -l javascript --update-all .
```

### Scan — run YAML lint rules
```bash
# Single rule file
ast-grep scan -r rule.yml

# Project rules (reads sgconfig.yml)
ast-grep scan

# Apply auto-fixes from rules
ast-grep scan --update-all
```

## Pattern Quick Reference

| Meta-variable | Matches | Example |
|---------------|---------|---------|
| `$VAR` | One AST node | `print($MSG)` matches `print("hi")` |
| `$$$` | Zero or more nodes | `func($$$)` matches `func()` and `func(a, b)` |
| `$_` | Any single node (no capture) | `$_ + $_` matches any addition |
| `$$NAME` | Zero or more (named capture) | `[$$$ITEMS]` captures list contents |

Same-name meta-variables must match identical content: `$A == $A` matches `x == x` but NOT `x == y`.

## Language IDs

Use with `-l` flag:

| Language | ID | Language | ID |
|----------|----|----------|----|
| Python | `python` | TypeScript | `typescript` |
| JavaScript | `javascript` | TSX | `tsx` |
| Go | `go` | Rust | `rust` |
| C | `c` | C++ | `cpp` |
| Java | `java` | C# | `csharp` |
| Ruby | `ruby` | Kotlin | `kotlin` |
| Swift | `swift` | Lua | `lua` |
| HTML | `html` | CSS | `css` |
| Bash | `bash` | YAML | `yaml` |
| JSON | `json` | TOML | `toml` |

Full list: `ast-grep list-languages`

## Common Pitfalls

1. **Use `ast-grep`, not `sg`** — On Linux, `sg` is the `setgroups` command. Always use the full `ast-grep` binary name.

2. **Never use `-i` (interactive mode)** — Interactive mode requires terminal input and will hang. Always use `--update-all` (or `-U`) to apply changes non-interactively:
   ```bash
   # WRONG: hangs waiting for input
   ast-grep run -p 'old($$$)' -r 'new($$$)' -i -l python .

   # CORRECT: applies all changes
   ast-grep run -p 'old($$$)' -r 'new($$$)' --update-all -l python .
   ```

3. **Patterns must be valid syntax** — `$FUNC(` is not valid code and will fail. Patterns must parse as real code with meta-variables substituted.

4. **Strictness for ambiguous patterns** — If a simple pattern matches too broadly, use `--strictness` to control matching:
   ```bash
   ast-grep run -p '$EXPR' --strictness relaxed -l python .   # more matches
   ast-grep run -p '$EXPR' --strictness strict -l python .    # fewer matches
   ```

5. **Path argument comes last** — The search path must be the final argument:
   ```bash
   # CORRECT
   ast-grep run -p 'pattern' -l python ./src

   # WRONG
   ast-grep run ./src -p 'pattern' -l python
   ```

6. **No output = no matches** — ast-grep only prints matches. Empty output means the pattern didn't match anything (check the pattern and language flag).

## When to Load References

Load **[pattern-examples.md](./references/pattern-examples.md)** when:
- You need language-specific pattern templates
- You're unsure how to express a structural pattern
- You want ready-made find/replace recipes for a specific language
- You need the full meta-variable reference with edge cases

Load **[yaml-rules-guide.md](./references/yaml-rules-guide.md)** when:
- You need to write a YAML lint/scan rule
- You need relational rules (inside, has, follows, precedes)
- You need composite rules (all, any, not)
- You need constraints or transforms
- You need sgconfig.yml setup for project-wide scanning
