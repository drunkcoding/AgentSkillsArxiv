---
name: better-grep
description: Performs fast text search with one-shot patterns that minimize iterations by getting files, lines, and context in a single call. Use this skill when searching for text patterns, finding specific code locations, or getting context around matches
---

# ripgrep: Powerful, one-shot text search

**Always invoke ripgrep skill for text search - do not execute bash commands directly.**

## Default Strategy

**Invoke ripgrep skill** for fast text search with one-shot patterns. Use `-e 'pattern' -n -C 2` to get files, line numbers, and context in a single call.

This minimizes iterations and context usage. Always prefer getting line numbers and surrounding context over multiple search attempts.

Common workflow: ripgrep skill → other skills (fzf, bat, sd, analyzing-code-structure) for interactive selection, preview, or modification.

## Tool Selection

**Grep tool** (built on ripgrep) - Use for structured searches:
- Basic pattern matching with structured output
- File type filtering with `type` parameter
- When special flags like `-F`, `-v`, `-w`, or pipe composition are not needed
- Handles 95% of search needs

**Bash(rg)** - Use for one-shot searches needing special flags or composition:
- Fixed string search (`-F`)
- Invert line match (`-v`)
- Word boundaries (`-w`)
- Files without matches (`--files-without-match`)
- Multiline patterns (`-U`)
- PCRE2 lookahead/lookbehind (`-P`)
- Replace preview (`-r`)
- Search hidden/ignored files (`--hidden`, `--no-ignore`)
- Pipe composition (`| head`, `| wc -l`, `| sort`)
- Use when Grep tool lacks the needed flag

**Glob tool** - Use for file name/path matching only (not content search)

## When to Load Detailed Reference

Load [ripgrep guide](./reference/ripgrep-guide.md) when needing:
- One-shot search pattern templates
- Effective flag combinations for complex searches
- Advanced features: multiline (`-U`), PCRE2 (`-P`), replace preview (`-r`)
- File search modifiers: `--files-without-match`, `--hidden`, `--no-ignore`
- Pipe composition patterns
- File type filters reference (`-t` flags)
- Pattern syntax examples
- Decision flow for choosing Grep tool vs Bash(rg)

The guide focuses on practical patterns for getting targeted results in minimal calls.

### Pipeline Combinations
- **rg | fzf**: Interactive selection from search results
- **rg | sd**: Batch replacements on search results
- **rg | xargs**: Execute commands on matched files
