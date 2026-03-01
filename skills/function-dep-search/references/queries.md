# Tree-sitter Query Patterns by Language

This reference documents the tree-sitter queries used by `fdep.py` for each language.
Extend or customize these patterns by editing the `LANG_CONFIG` dict in `fdep.py`.

## Table of Contents

- [Query Syntax Quick Reference](#query-syntax-quick-reference)
- [Python](#python)
- [JavaScript](#javascript)
- [TypeScript](#typescript)
- [Go](#go)
- [Rust](#rust)
- [C](#c)
- [C++](#cpp)
- [Java](#java)
- [Adding a New Language](#adding-a-new-language)

## Query Syntax Quick Reference

```scheme
(node_type)                          ; Match node by type
(node_type field: (child_type))      ; Match with named field
(node_type (child_type) @cap)        ; Capture node as @cap
[pattern1 pattern2]                  ; Alternation (match either)
(_)                                  ; Wildcard (any named node)
((identifier) @x (#eq? @x "main"))  ; Predicate filter
```

### Predicates

```scheme
((identifier) @name (#eq? @name "main"))       ; Exact string match
((identifier) @name (#not-eq? @name "test"))   ; Negated string match
((identifier) @name (#match? @name "^test_"))  ; Regex match
((identifier) @name (#not-match? @name "^_"))  ; Negated regex match
((identifier) @name (#any-eq? @name "foo"))    ; Any capture equals string
((node) @n (#is? @n "keyword"))                ; Node property test
((node) @n (#is-not? @n "keyword"))            ; Negated node property
((node) @n (#set! "key" "value"))              ; Set metadata on match
```

### Quantifiers

```scheme
(block (statement)*)           ; Zero or more statements
(block (statement)+)           ; One or more statements
(function_call (argument)?)    ; Optional argument
```

### Anchors

```scheme
(block . (statement) @first)   ; First child only (. anchor)
(block (statement) @last .)    ; Last child only
```

### Negated Fields

```scheme
(function_definition !return_type)  ; Match only when field is absent
```

## Python

**Extensions:** `.py`, `.pyi`
**Package:** `tree-sitter-python`

### Definitions
```scheme
(function_definition
  name: (identifier) @name) @def
```
Matches both top-level functions and methods (methods are function_definition inside class body).

### Calls
```scheme
; Direct calls: foo()
(call
  function: (identifier) @name)

; Method/attribute calls: obj.method()
(call
  function: (attribute
    attribute: (identifier) @name))
```

## JavaScript

**Extensions:** `.js`, `.jsx`, `.mjs`, `.cjs`
**Package:** `tree-sitter-javascript`

### Definitions
```scheme
; function foo() {}
(function_declaration
  name: (identifier) @name) @def

; const foo = () => {}
(variable_declarator
  name: (identifier) @name
  value: (arrow_function) @def)

; const foo = function() {}
(variable_declarator
  name: (identifier) @name
  value: (function_expression) @def)

; class methods
(method_definition
  name: (property_identifier) @name) @def
```

### Calls
```scheme
(call_expression
  function: (identifier) @name)

(call_expression
  function: (member_expression
    property: (property_identifier) @name))
```

## TypeScript

**Extensions:** `.ts`, `.tsx`
**Package:** `tree-sitter-typescript`

Same query patterns as JavaScript. Uses `language_typescript` attribute from the module.

## Go

**Extensions:** `.go`
**Package:** `tree-sitter-go`

### Definitions
```scheme
(function_declaration
  name: (identifier) @name) @def

(method_declaration
  name: (field_identifier) @name) @def
```

### Calls
```scheme
(call_expression
  function: (identifier) @name)

(call_expression
  function: (selector_expression
    field: (field_identifier) @name))
```

## Rust

**Extensions:** `.rs`
**Package:** `tree-sitter-rust`

### Definitions
```scheme
(function_item
  name: (identifier) @name) @def
```

### Calls
```scheme
; Direct: foo()
(call_expression
  function: (identifier) @name)

; Scoped: module::func()
(call_expression
  function: (scoped_identifier
    name: (identifier) @name))

; Method: obj.method()
(call_expression
  function: (field_expression
    field: (field_identifier) @name))
```

## C

**Extensions:** `.c`, `.h`
**Package:** `tree-sitter-c`

### Definitions
```scheme
(function_definition
  declarator: (function_declarator
    declarator: (identifier) @name)) @def
```

### Calls
```scheme
(call_expression
  function: (identifier) @name)
```

## C++ {#cpp}

**Extensions:** `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hxx`, `.hh`
**Package:** `tree-sitter-cpp`

### Definitions
```scheme
; Regular functions
(function_definition
  declarator: (function_declarator
    declarator: (identifier) @name)) @def

; Qualified: Class::method()
(function_definition
  declarator: (function_declarator
    declarator: (qualified_identifier
      name: (identifier) @name))) @def
```

### Calls
```scheme
(call_expression
  function: (identifier) @name)

(call_expression
  function: (qualified_identifier
    name: (identifier) @name))

(call_expression
  function: (field_expression
    field: (field_identifier) @name))
```

## Java

**Extensions:** `.java`
**Package:** `tree-sitter-java`

### Definitions
```scheme
(method_declaration
  name: (identifier) @name) @def

(constructor_declaration
  name: (identifier) @name) @def
```

### Calls
```scheme
(method_invocation
  name: (identifier) @name)

; new ClassName()
(object_creation_expression
  type: (type_identifier) @name)
```

## Python API Reference (tree-sitter >= 0.23)

### Query + QueryCursor Pattern

```python
from tree_sitter import Language, Parser, Query, QueryCursor

parser = Parser(language)
tree = parser.parse(source_bytes)

q = Query(language, "(function_definition name: (identifier) @name) @def")
cursor = QueryCursor(q)

# matches() returns list[tuple[int, dict[str, list[Node]]]]
# Each tuple is (pattern_index, {capture_name: [nodes]})
for pattern_idx, captures in cursor.matches(tree.root_node):
    names = captures.get("name", [])

# captures() returns dict[str, list[Node]]
# Flat dict of all captures across all matches
caps = cursor.captures(tree.root_node)
for node in caps.get("name", []):
    print(node.text.decode("utf8"))
```

### QueryCursor Scoping

```python
cursor = QueryCursor(q)

# Restrict to byte range
cursor.set_byte_range(start_byte, end_byte)

# Match nodes whose range *contains* the given range
cursor.set_containing_byte_range(start_byte, end_byte)

# Restrict to row/column point range
cursor.set_point_range(start_point, end_point)

# Limit match depth from root (0 = root only)
cursor.set_max_start_depth(depth)
```

### Match Limits

```python
# Set limit in constructor
cursor = QueryCursor(q, match_limit=100)

# Check after execution
cursor.matches(node)
if cursor.did_exceed_match_limit:
    print("Results may be incomplete")
```

## Adding a New Language

**Requirements:** Python >= 3.10, tree-sitter >= 0.23

1. Install the grammar: `pip install tree-sitter-<lang>`
2. Add entry to `LANG_CONFIG` in `fdep.py`:

```python
"mylang": {
    "extensions": {".ml"},
    "pip_package": "tree-sitter-mylang",
    "module": "tree_sitter_mylang",
    # Optional: if the language function is not called "language()"
    # "lang_attr": "language_mylang",
    "queries": {
        "definitions": """
            (<definition_node_type>
              name: (identifier) @name) @def
        """,
        "calls": """
            (<call_node_type>
              function: (identifier) @name)
        """,
    },
}
```

   The `lang_attr` key is needed when the grammar module exposes the language
   under a non-default name (e.g., TypeScript uses `language_typescript`).

3. Use the [tree-sitter playground](https://tree-sitter.github.io/tree-sitter/playground) to explore the AST for your language and find the correct node types.
4. Verify the new language works:

```bash
python3 scripts/fdep.py defs <test-file>
python3 scripts/fdep.py calls <test-file>
```
