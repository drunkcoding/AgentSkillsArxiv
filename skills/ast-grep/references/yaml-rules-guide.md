# ast-grep YAML Rules Guide

Write custom lint rules and code scanners using ast-grep's YAML rule syntax. Rules are used with `ast-grep scan`.

## Table of Contents
- [Rule File Structure](#rule-file-structure)
- [Atomic Rules](#atomic-rules)
- [Relational Rules](#relational-rules)
- [Composite Rules](#composite-rules)
- [Constraints](#constraints)
- [Transforms](#transforms)
- [Running Rules](#running-rules)
- [Complete Examples](#complete-examples)

---

## Rule File Structure

A rule file is a YAML document with these top-level fields:

```yaml
id: rule-unique-id            # Required. Unique identifier.
language: python               # Required. Language to parse.
rule:                          # Required. The matching rule (see below).
  pattern: print($$$)
message: "Descriptive message" # Required for scan. Shown on match.
severity: warning              # Optional: hint | info | warning | error
note: "Explain why or how to fix" # Optional. Extra guidance.
fix: "logger.info($$$)"       # Optional. Auto-fix replacement.
url: "https://..."            # Optional. Link to docs.
constraints:                   # Optional. Restrict meta-variable matches.
  VAR:
    regex: "^_"
transform:                     # Optional. Derive new values from captures.
  NEW_VAR:
    substring:
      source: $VAR
      startChar: 1
```

---

## Atomic Rules

Atomic rules match a single AST property. Use one per rule node, or combine with composite rules.

### `pattern`
Match code structure using meta-variables. Most common rule type.
```yaml
rule:
  pattern: console.log($$$ARGS)
```

### `kind`
Match AST node type by its tree-sitter kind name. Useful when patterns are ambiguous.
```yaml
rule:
  kind: function_declaration
```

Find node kind names: `ast-grep run -p 'YOUR_CODE' -l LANG --debug-query` or use [ast-grep playground](https://ast-grep.github.io/playground.html).

### `regex`
Match a node whose text content matches a regex.
```yaml
rule:
  regex: "^test_"
```

Regex applies to the entire text of the matched node. Often combined with `kind`:
```yaml
rule:
  all:
    - kind: identifier
    - regex: "^__.*__$"
```

### `nthChild`
Match a node by its position among siblings.
```yaml
rule:
  nthChild: 1          # first child (1-indexed)

rule:
  nthChild:
    position: last      # last child
    ofRule:
      kind: argument    # only count nodes matching this rule
```

---

## Relational Rules

Relational rules match a node based on its relationship to other nodes in the AST.

### `inside`
Match node that is nested inside another node matching a rule.
```yaml
rule:
  pattern: console.log($$$)
  inside:
    kind: function_declaration
```

### `has`
Match node that contains a descendant matching a rule.
```yaml
rule:
  kind: if_statement
  has:
    pattern: return $$$
```

### `follows`
Match node that comes after a sibling matching a rule.
```yaml
rule:
  pattern: $EXPR
  follows:
    pattern: return $$$
```

### `precedes`
Match node that comes before a sibling matching a rule.
```yaml
rule:
  pattern: $EXPR
  precedes:
    pattern: return $$$
```

### `stopBy`
Control how far relational rules search. Applies to `inside`, `has`, `follows`, `precedes`.

```yaml
# Default: search all descendants/ancestors
has:
  pattern: $EXPR
  stopBy: end           # search to the end (default)

# Stop at nearest matching boundary
inside:
  kind: function_declaration
  stopBy:
    kind: class_declaration  # don't cross class boundaries
```

Values: `end` (search all, default), `neighbor` (immediate only), or a rule object (stop at matching node).

---

## Composite Rules

Combine multiple rules with logical operators.

### `all`
All sub-rules must match (logical AND).
```yaml
rule:
  all:
    - kind: identifier
    - regex: "^unused_"
    - inside:
        kind: function_declaration
```

### `any`
At least one sub-rule must match (logical OR).
```yaml
rule:
  any:
    - pattern: console.log($$$)
    - pattern: console.warn($$$)
    - pattern: console.error($$$)
```

### `not`
Negate a rule (logical NOT).
```yaml
rule:
  pattern: $EXPR.unwrap()
  not:
    inside:
      kind: test_function
```

### Nesting
Composite rules nest freely:
```yaml
rule:
  all:
    - pattern: $FUNC($$$)
    - any:
        - regex: "^get"
        - regex: "^fetch"
    - not:
        inside:
          kind: test_function
```

---

## Constraints

Restrict what meta-variables can match. Defined at the top level, keyed by meta-variable name (without `$`).

### `regex`
```yaml
rule:
  pattern: $FUNC($$$)
constraints:
  FUNC:
    regex: "^(get|fetch|load)"
```

### `kind`
```yaml
rule:
  pattern: $X + $Y
constraints:
  X:
    kind: string_literal
```

### `not`
Negate a constraint:
```yaml
constraints:
  VAR:
    not:
      regex: "^_"
```

---

## Transforms

Create new values from captured meta-variables, for use in `fix` strings.

### `substring`
```yaml
transform:
  METHOD:
    substring:
      source: $FUNC
      startChar: 4        # skip "get_" prefix
fix: "fetch_$METHOD()"
```

### `replace`
```yaml
transform:
  SNAKE:
    replace:
      source: $NAME
      replace: "([A-Z])"
      by: "_$1"
fix: "$SNAKE"
```

### `convert`
Change case:
```yaml
transform:
  UPPER:
    convert:
      source: $NAME
      toCase: upperCase    # lowerCase, upperCase, camelCase, snakeCase, pascalCase, etc.
```

---

## Running Rules

### Single rule file
```bash
ast-grep scan -r path/to/rule.yml
```

### Multiple rules via config
Create `sgconfig.yml` in project root:
```yaml
ruleDirs:
  - rules/          # directory containing .yml rule files
```

Then:
```bash
ast-grep scan           # uses sgconfig.yml automatically
ast-grep scan -c sgconfig.yml  # explicit config path
```

### Useful scan flags
```bash
ast-grep scan -r rule.yml --json          # JSON output
ast-grep scan -r rule.yml --update-all    # apply all fixes
ast-grep scan -r rule.yml -i              # DON'T USE: interactive (not supported in Claude)
```

---

## Complete Examples

### Example 1: Ban console.log in production code (JavaScript)

```yaml
id: no-console-log
language: javascript
rule:
  any:
    - pattern: console.log($$$)
    - pattern: console.debug($$$)
    - pattern: console.info($$$)
  not:
    inside:
      kind: catch_clause
message: "Remove console output before committing"
severity: warning
note: "Use a proper logger instead of console methods"
fix: ""
```

### Example 2: Require error message on .expect() (Rust)

```yaml
id: expect-with-message
language: rust
rule:
  pattern: $EXPR.expect($MSG)
constraints:
  MSG:
    regex: "^\"$"
message: "Empty .expect() message — add a descriptive error message"
severity: error
note: "Use .expect(\"meaningful message\") to help with debugging"
```

### Example 3: No bare except in Python

```yaml
id: no-bare-except
language: python
rule:
  all:
    - kind: except_clause
    - not:
        has:
          kind: identifier
message: "Bare 'except:' catches all exceptions including KeyboardInterrupt"
severity: warning
note: "Use 'except Exception:' at minimum, or a more specific exception type"
```

### Example 4: Prefer if-let over match for single arm (Rust)

```yaml
id: prefer-if-let
language: rust
rule:
  kind: match_expression
  has:
    kind: match_arm
    nthChild:
      position: 2
      ofRule:
        kind: match_arm
  not:
    has:
      kind: match_arm
      nthChild:
        position: 3
        ofRule:
          kind: match_arm
message: "Consider using if-let instead of match with only two arms"
severity: hint
note: "if let Some(x) = expr { ... } is more concise for single-pattern matches"
```

### Example 5: Detect unchecked errors in Go

```yaml
id: unchecked-error
language: go
rule:
  pattern: $VAR, _ := $FUNC($$$)
message: "Error return value is discarded"
severity: warning
note: "Handle the error or explicitly document why it's safe to ignore"
```
