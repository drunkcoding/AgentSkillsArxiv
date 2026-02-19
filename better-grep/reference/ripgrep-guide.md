# ripgrep Search Patterns Reference

Practical search patterns for efficient one-shot searches with ripgrep.

# One-Shot Search Strategy

**Goal: Get files + line numbers + context in ONE call.**

## The Primary Pattern

```bash
rg -n -C 2 -t TYPE -e 'pattern'
```

**What this gives:**
- `-n` - Line numbers
- `-C 2` - 2 lines context before/after
- `-t TYPE` - File type filter
- `-e 'pattern'` - The search pattern

**Use this as the default.** Adjust only when needed.

---

# Essential Flag Combinations

## 1. Standard Search with Context
```bash
rg -n -C 2 -t js -e 'functionName'
```
Most common pattern - gives everything needed.

## 2. Fixed String (Literal) Search
```bash
rg -F -n -C 2 -t js -e 'exact.string.with.dots'
```
Use `-F` when pattern has regex special chars (`.` `*` `(` `)` etc.)
**Avoids regex escaping hell.**

## 3. Word Boundary (Precise) Search
```bash
rg -w -n -C 2 -t js -e 'variable'
```
`-w` matches whole words only. Finds "variable" but not "variableName".

## 4. Case-Insensitive Search
```bash
rg -i -n -C 2 -t js -e 'pattern'
```
`-i` for case-insensitive matching.

## 5. List Files Only (Quick Overview)
```bash
rg -l -t js -e 'pattern' | head -20
```
`-l` lists filenames only. Pipe to `head` to limit.

## 6. Count Matches
```bash
rg -c -t js -e 'pattern'
```
`-c` shows count per file.

## 7. Invert Line Match
```bash
rg -v -n -t js -e 'pattern'
```
`-v` shows lines that do NOT match the pattern. Useful for filtering output.

## 8. Find Files WITHOUT a Pattern
```bash
rg --files-without-match -t js -e 'pattern'
```
Lists files that contain zero matches. No short flag exists for this.

**Note:** `-L` is `--follow` (follow symlinks), NOT files-without-match.

## 9. Find Files with X but not Y
```bash
# Method 1: set subtraction
comm -23 <(rg -l -t js -e 'pattern-x' | sort) <(rg -l -t js -e 'pattern-y' | sort)

# Method 2: pipe to --files-without-match
rg -l -t js -e 'pattern-x' | xargs rg --files-without-match -e 'pattern-y'
```

## 10. Multiple Patterns (OR Logic)
```bash
rg -n -C 2 -t js -e 'pattern1' -e 'pattern2'
```
Matches either pattern.

## 11. Specific Directory
```bash
rg -n -C 2 -t js -e 'pattern' src/components
```
Add directory path at end to narrow scope.

---

# Pipe Composition Patterns

## Limit Results
```bash
rg -n -t js -e 'pattern' | head -30
```
Get first 30 result lines.

## Count Total Matches
```bash
rg -n -t js -e 'pattern' | wc -l
```

## Sort and Deduplicate
```bash
rg -o -t js -e 'import.*from.*' | sort | uniq
```
`-o` shows only matching part. Useful for extracting patterns.

## Filter Results Further
```bash
rg -n -t js -e 'function' | rg -e 'export'
```
Find functions, then filter to only exported ones.

---

# Advanced Features

## Multiline Matching (-U)
```bash
rg -U -e 'function \w+\(.*\)\s*\{.*\n.*return' -t js
```
`-U` enables patterns that span multiple lines. Add `--multiline-dotall` to make `.` match newlines.

## PCRE2 Regex (-P)
```bash
rg -P -e '(?<=function )\w+' -o -t js     # Lookbehind: extract function names
rg -P -e '\w+(?=\(.*\))' -o -t js          # Lookahead: names before calls
```
`-P` enables PCRE2 for lookahead/lookbehind assertions. Not available in Grep tool.

## Replace Preview (-r)
```bash
rg -e 'oldName' -r 'newName' -n src/       # Preview replacements (no files modified)
rg -e '(\w+)\.exec\(' -r '$1.run(' -n      # Capture group replacement
```
`-r` shows what replacements would look like. **Does not modify files** — use `sd` or `sed` for actual changes.

## Limit Matches Per File (-m)
```bash
rg -m 1 -n -e 'import' -t js               # First match per file only
```

## Limit Directory Depth (--max-depth)
```bash
rg --max-depth 2 -l -e 'pattern'           # Only search top 2 levels
```

## Search Hidden and Ignored Files
```bash
rg --hidden -e 'pattern'                    # Include dotfiles (.env, .config, etc.)
rg --no-ignore -e 'pattern'                 # Include gitignored files
rg --hidden --no-ignore -e 'pattern'        # Both
```

## Custom File Types (--type-add)
```bash
rg --type-add 'web:*.{js,ts,html,css}' -t web -e 'pattern'
```

## Sort Results (--sort)
```bash
rg --sort path -l -e 'pattern'             # Alphabetical by path
rg --sort modified -l -e 'pattern'          # By modification time
```

## Asymmetric Context (-B / -A)
```bash
rg -B 2 -A 5 -n -e 'error' src/           # 2 lines before, 5 after
```
Use instead of `-C` when you need more context in one direction.

## JSON Output (--json)
```bash
rg --json -e 'pattern' | jq '.data.submatches'
```
Machine-readable output for tooling/scripts.

## Statistics (--stats)
```bash
rg --stats -e 'TODO' src/ 2>&1
```
Prints summary (files searched, matches found, time taken) to stderr.

---

# File Type Filters (-t)

**Common types** (main extensions shown; run `rg --type-list` for full list):
- `-t js` - JavaScript (.js, .jsx, .mjs, .cjs, .vue)
- `-t ts` - TypeScript (.ts, .tsx, .cts, .mts)
- `-t py` - Python (.py, .pyi)
- `-t go` - Go (.go)
- `-t rust` - Rust (.rs)
- `-t java` - Java (.java, .jsp, .jspx, .properties)
- `-t ruby` - Ruby (.rb, .rbw, .gemspec, Gemfile, Rakefile, config.ru)
- `-t c` - C (.c, .h, .H, .cats, + .in variants)
- `-t cpp` - C++ (.cpp, .hpp, .cc, .hh, .cxx, .hxx, .inl, + .in variants)
- `-t sh` - Shell (.sh, .bash, .zsh, .ksh, .csh, + rc/profile files)
- `-t html` - HTML (.html, .htm, .ejs)
- `-t css` - CSS (.css, .scss)
- `-t md` - Markdown (.md, .markdown, .mdx, .mkd, .mkdn, .mdown)
- `-t json` - JSON (.json, .sarif, composer.lock)
- `-t yaml` - YAML (.yaml, .yml)

**Multiple types:**
```bash
rg -t js -t ts -e 'pattern'
```

**Glob patterns (more flexible):**
```bash
rg -g '*.test.js' -e 'pattern'          # Test files only
rg -g '!*.test.js' -e 'pattern'         # Exclude test files
rg -g 'src/**/*.js' -e 'pattern'        # Specific directory pattern
```

---

# Pattern Syntax Quick Reference

## Literal Search (Use -F)
```bash
rg -F -e 'exact.string'
```
When pattern has special chars, use `-F` instead of escaping.

## Regex Patterns
```bash
rg -e 'function\s+\w+'           # Function declarations
rg -e 'import.*from\s+["\']'     # Import statements
rg -e 'class\s+\w+.*\{'          # Class definitions
rg -e '^\s*#'                    # Lines starting with #
rg -e 'TODO:|FIXME:|XXX:'        # Multiple comment markers
```

## Common Regex Elements
- `\s` - whitespace
- `\w` - word character
- `\d` - digit
- `.` - any character
- `.*` - zero or more any character
- `\b` - word boundary (or use `-w` flag)
- `^` - start of line
- `$` - end of line
- `[abc]` - character class
- `(foo|bar)` - alternation

---

# Decision Flow

```
Need to search code?
│
├─ Simple pattern, no special needs?
│  → Use Grep tool (structured output)
│
├─ Need one-shot with context?
│  → rg -n -C 2 -t TYPE -e 'pattern'
│
├─ Pattern has dots, parens, special chars?
│  → rg -F -n -C 2 -t TYPE -e 'exact.string'
│
├─ Need precise word matching?
│  → rg -w -n -C 2 -t TYPE -e 'word'
│
├─ Need to find files WITHOUT something?
│  → rg --files-without-match -t TYPE -e 'pattern'
│
├─ Need multiline or lookahead/lookbehind?
│  → rg -U -e 'multi\nline' (multiline)
│  → rg -P -e '(?<=prefix)\w+' (PCRE2)
│
├─ Need to preview replacements?
│  → rg -e 'old' -r 'new' -n
│
├─ Need to search hidden/ignored files?
│  → rg --hidden --no-ignore -e 'pattern'
│
└─ Need to compose with other commands?
   → rg -n -t TYPE -e 'pattern' | head/wc/sort/etc
```

---

# Common Workflows

## "Find all uses of this function"
```bash
rg -n -C 2 -t js -e 'functionName\('
```
Use `\(` to find actual calls (not definitions).

## "Which files import this package?"
```bash
rg -l -t js -e 'from ["\']package-name["\']'
```

## "How is this class used?"
```bash
rg -n -C 3 -t py -e 'ClassName'
```
More context (C 3) to see usage patterns.

## "Find TODOs in specific directory"
```bash
rg -n -e 'TODO:' src/
```

## "Find files that import X but not Y"
```bash
# Subtract file lists (correct: searches file contents, not filenames)
comm -23 <(rg -l -t js -e 'import.*from.*package-x' | sort) \
         <(rg -l -t js -e 'import.*from.*package-y' | sort)

# Or: pipe to --files-without-match
rg -l -t js -e 'import.*from.*package-x' | xargs rg --files-without-match -e 'package-y'
```

## "Count files with matches"
```bash
rg -l -t js -e 'pattern' | wc -l
```

## "Count total matches across codebase"
```bash
rg -c -t js -e 'pattern'
```
Shows count per file. Sum with: `rg -c -e 'pattern' | awk -F: '{s+=$NF} END {print s}'`

---

# Best Practices

## 1. Start with Standard Pattern
```bash
rg -n -C 2 -t TYPE -e 'pattern'
```
Adjust only if needed.

## 2. Use -F for Literal Strings
Don't escape regex chars - use `-F`:
```bash
# BAD: rg -e 'function\(\)'
# GOOD: rg -F -e 'function()'
```

## 3. Always Use Single Quotes
```bash
# GOOD: rg -e 'pattern'
# BAD:  rg -e "pattern"  # Shell may interpret special chars
```

## 4. Use Type Filters
```bash
# GOOD: rg -t js -e 'pattern'
# LESS GOOD: rg -e 'pattern'  # Searches everything
```

## 5. Limit Large Results
```bash
rg -n -t js -e 'common_word' | head -50
```

## 6. Use -w for Precision
```bash
# Finds "test" in "testing", "latest", etc:
rg -e 'test'

# Finds only "test" as whole word:
rg -w -e 'test'
```

---

# When to Use Grep Tool Instead

Use Grep tool when:
- Simple pattern matching (supports regex, `-i`, context lines, type filters)
- Want structured output modes (files/content/count)
- Don't need to pipe results
- Handles most search needs

Use Bash(rg) when:
- Need `-F` (literal), `-v` (invert), `-w` (word boundary)
- Need `--files-without-match`, `-U` (multiline), `-P` (PCRE2)
- Need `-r` (replace preview), `--hidden`, `--no-ignore`
- Need `-m` (max count), `--max-depth`, `--sort`, `--stats`
- Want to pipe/compose with other commands
- Need `--type-add` for custom file type groups

---

# Summary

**Default search command:**
```bash
rg -n -C 2 -t TYPE -e 'pattern'
```

**Key flags to remember:**
- `-F` - Literal search (avoid escaping)
- `-w` - Word boundaries (precise)
- `-v` - Invert line match (show lines that DON'T match)
- `-l` - List files with matches only
- `--files-without-match` - List files that DON'T match (no short flag)
- `-U` - Multiline matching
- `-P` - PCRE2 regex (lookahead/lookbehind)
- `-r` - Replace preview (output only, doesn't modify files)
- `--hidden` - Include hidden/dotfiles
- `--no-ignore` - Include gitignored files

**Compose with pipes:**
```bash
rg ... | head -N      # Limit results
rg ... | wc -l        # Count
rg ... | rg ...       # Filter further
```

This reference provides practical patterns for efficient one-shot searches.
