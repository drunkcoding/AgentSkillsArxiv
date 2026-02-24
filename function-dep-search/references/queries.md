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

## Adding a New Language

1. Install the grammar: `pip install tree-sitter-<lang>`
2. Add entry to `LANG_CONFIG` in `fdep.py`:

```python
"mylang": {
    "extensions": {".ml"},
    "pip_package": "tree-sitter-mylang",
    "module": "tree_sitter_mylang",
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

3. Use the [tree-sitter playground](https://tree-sitter.github.io/tree-sitter/playground) to explore the AST for your language and find the correct node types.
