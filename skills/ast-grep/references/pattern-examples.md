# ast-grep Pattern Cookbook

Quick-reference patterns organized by language. Each example shows the pattern and what it matches.

## Table of Contents
- [Meta-Variable Reference](#meta-variable-reference)
- [Python](#python)
- [JavaScript / TypeScript](#javascript--typescript)
- [Go](#go)
- [Rust](#rust)
- [C / C++](#c--c)
- [Java](#java)
- [Cross-Language Recipes](#cross-language-recipes)

---

## Meta-Variable Reference

| Syntax   | Name               | Matches                                    | Example Pattern          | Matches Code              |
|----------|--------------------|--------------------------------------------|--------------------------|---------------------------|
| `$VAR`   | Single node        | Exactly one AST node (expression, name)    | `print($MSG)`            | `print("hello")`         |
| `$$$`    | Multi node         | Zero or more nodes (args, statements)      | `func($$$)`              | `func()`, `func(a, b)`   |
| `$_`     | Wildcard           | Any single node (anonymous, non-capturing) | `$_ + $_`                | `a + b`, `1 + 2`         |
| `$$VAR`  | Named multi        | Zero or more, captured with name           | `[$$$ITEMS]`             | `[1, 2, 3]` (captures all) |

### Key rules
- `$VAR` with the same name must match the same content: `$A == $A` matches `x == x` but NOT `x == y`
- `$$$` is greedy — it consumes as many sibling nodes as possible
- `$_` never captures; use it when you don't need the matched value
- Named meta-variables (`$VAR`, `$$VAR`) capture their match for use in `-r` replacements

---

## Python

**Language flag:** `-l python`

### Find all print calls
```
ast-grep run -p 'print($$$)' -l python .
```

### Find print with single argument (for replacement)
```
ast-grep run -p 'print($MSG)' -l python .
```

### Replace print with logging
```
ast-grep run -p 'print($MSG)' -r 'logger.info($MSG)' -l python --update-all .
```

### Find decorated functions
```
# Any decorator on a function
ast-grep run -p '@$DECORATOR
def $FUNC($$$ARGS):
    $$$BODY' -l python .
```

### Find specific decorator
```
ast-grep run -p '@staticmethod
def $FUNC($$$ARGS):
    $$$BODY' -l python .
```

### List comprehension
```
ast-grep run -p '[$EXPR for $VAR in $ITER]' -l python .
```

### Dict comprehension
```
ast-grep run -p '{$KEY: $VAL for $VAR in $ITER}' -l python .
```

### Find assert statements
```
ast-grep run -p 'assert $COND' -l python .
ast-grep run -p 'assert $COND, $MSG' -l python .
```

### Find bare except
```
ast-grep run -p 'except:' -l python .
```

### Find type-annotated variables
```
ast-grep run -p '$VAR: $TYPE = $VAL' -l python .
```

### Find isinstance checks
```
ast-grep run -p 'isinstance($OBJ, $TYPE)' -l python .
```

### Find with-statement
```
ast-grep run -p 'with $EXPR as $VAR:
    $$$BODY' -l python .
```

### Find f-string usage (pattern matches the literal syntax)
```
ast-grep run -p 'f"$$$"' -l python .
```

### Find class definitions
```
ast-grep run -p 'class $NAME($$$BASES):
    $$$BODY' -l python .
```

### Find imports
```
ast-grep run -p 'from $MODULE import $$$NAMES' -l python .
ast-grep run -p 'import $MODULE' -l python .
```

### Find TODO/FIXME in strings
```
ast-grep run -p 'raise NotImplementedError($$$)' -l python .
```

---

## JavaScript / TypeScript

**Language flag:** `-l javascript` or `-l typescript` or `-l tsx`

### Find console.log
```
ast-grep run -p 'console.log($$$)' -l javascript .
```

### Remove console.log
```
ast-grep run -p 'console.log($$$)' -r '' -l javascript --update-all .
```

### require → import conversion
```
# Find require calls
ast-grep run -p 'const $NAME = require($PATH)' -l javascript .

# Rewrite to import
ast-grep run -p 'const $NAME = require($PATH)' -r 'import $NAME from $PATH' -l javascript --update-all .
```

### Find arrow functions
```
ast-grep run -p 'const $NAME = ($$$PARAMS) => $$$BODY' -l javascript .
```

### Find async functions
```
ast-grep run -p 'async function $NAME($$$PARAMS) { $$$BODY }' -l javascript .
```

### Find await expressions
```
ast-grep run -p 'await $EXPR' -l javascript .
```

### React: find useState hooks
```
ast-grep run -p 'const [$STATE, $SETTER] = useState($$$INIT)' -l tsx .
```

### React: find useEffect
```
ast-grep run -p 'useEffect(() => { $$$BODY }, [$$$DEPS])' -l tsx .
```

### React: find component definitions
```
ast-grep run -p 'function $NAME($$$PROPS) { $$$BODY }' -l tsx .
```

### Find try-catch blocks
```
ast-grep run -p 'try { $$$TRY } catch ($ERR) { $$$CATCH }' -l javascript .
```

### Find ternary expressions
```
ast-grep run -p '$COND ? $THEN : $ELSE' -l javascript .
```

### Find template literals
```
ast-grep run -p '`$$$`' -l javascript .
```

### Find optional chaining
```
ast-grep run -p '$OBJ?.$PROP' -l typescript .
```

### Find type assertions (TypeScript)
```
ast-grep run -p '$EXPR as $TYPE' -l typescript .
```

---

## Go

**Language flag:** `-l go`

### Find unchecked errors
```
ast-grep run -p '$VAR, _ := $FUNC($$$)' -l go .
```

### Find error handling pattern
```
ast-grep run -p 'if $ERR != nil { $$$BODY }' -l go .
```

### Find goroutine launches
```
ast-grep run -p 'go $FUNC($$$)' -l go .
```

### Find defer calls
```
ast-grep run -p 'defer $FUNC($$$)' -l go .
```

### Find fmt.Println (replace with log)
```
ast-grep run -p 'fmt.Println($$$ARGS)' -l go .
ast-grep run -p 'fmt.Println($$$ARGS)' -r 'log.Println($$$ARGS)' -l go --update-all .
```

### Find struct literal
```
ast-grep run -p '$TYPE{$$$FIELDS}' -l go .
```

### Find channel operations
```
ast-grep run -p '$CH <- $VAL' -l go .
ast-grep run -p '<-$CH' -l go .
```

### Find function declarations
```
ast-grep run -p 'func $NAME($$$PARAMS) $$$RET { $$$BODY }' -l go .
```

### Find method declarations
```
ast-grep run -p 'func ($RECV $TYPE) $NAME($$$PARAMS) $$$RET { $$$BODY }' -l go .
```

### Find interface declarations
```
ast-grep run -p 'type $NAME interface { $$$METHODS }' -l go .
```

---

## Rust

**Language flag:** `-l rust`

### Find .unwrap() calls
```
ast-grep run -p '$EXPR.unwrap()' -l rust .
```

### Replace unwrap with expect
```
ast-grep run -p '$EXPR.unwrap()' -r '$EXPR.expect("TODO: handle error")' -l rust --update-all .
```

### Find unsafe blocks
```
ast-grep run -p 'unsafe { $$$BODY }' -l rust .
```

### Find match expressions
```
ast-grep run -p 'match $EXPR { $$$ARMS }' -l rust .
```

### Find println! macros
```
ast-grep run -p 'println!($$$)' -l rust .
```

### Find function definitions
```
ast-grep run -p 'fn $NAME($$$PARAMS) -> $RET { $$$BODY }' -l rust .
```

### Find impl blocks
```
ast-grep run -p 'impl $TYPE { $$$METHODS }' -l rust .
```

### Find trait implementations
```
ast-grep run -p 'impl $TRAIT for $TYPE { $$$METHODS }' -l rust .
```

### Find clone calls
```
ast-grep run -p '$EXPR.clone()' -l rust .
```

### Find todo! macros
```
ast-grep run -p 'todo!($$$)' -l rust .
```

---

## C / C++

**Language flag:** `-l c` or `-l cpp`

### Find malloc without free (find malloc calls)
```
ast-grep run -p 'malloc($SIZE)' -l c .
```

### Find printf calls
```
ast-grep run -p 'printf($$$)' -l c .
```

### Find NULL pointer checks
```
ast-grep run -p 'if ($PTR == NULL)' -l c .
ast-grep run -p 'if ($PTR != NULL)' -l c .
```

### Find sizeof usage
```
ast-grep run -p 'sizeof($EXPR)' -l c .
```

### Find pointer dereference
```
ast-grep run -p '*$PTR' -l c .
```

### Find new/delete (C++)
```
ast-grep run -p 'new $TYPE($$$ARGS)' -l cpp .
ast-grep run -p 'delete $PTR' -l cpp .
```

### Find static_cast (C++)
```
ast-grep run -p 'static_cast<$TYPE>($EXPR)' -l cpp .
```

### Find auto declarations (C++)
```
ast-grep run -p 'auto $VAR = $EXPR' -l cpp .
```

### Find std::vector usage (C++)
```
ast-grep run -p 'std::vector<$TYPE>' -l cpp .
```

---

## Java

**Language flag:** `-l java`

### Find System.out.println
```
ast-grep run -p 'System.out.println($$$)' -l java .
```

### Find stream operations
```
ast-grep run -p '$COLLECTION.stream().$$$OPS' -l java .
```

### Find @Override methods
```
ast-grep run -p '@Override
public $RET $NAME($$$PARAMS) { $$$BODY }' -l java .
```

### Find @Deprecated annotations
```
ast-grep run -p '@Deprecated' -l java .
```

### Find try-with-resources
```
ast-grep run -p 'try ($TYPE $VAR = $EXPR) { $$$BODY }' -l java .
```

### Find instanceof checks
```
ast-grep run -p '$EXPR instanceof $TYPE' -l java .
```

### Find null checks
```
ast-grep run -p 'if ($VAR == null)' -l java .
ast-grep run -p 'if ($VAR != null)' -l java .
```

### Find synchronized blocks
```
ast-grep run -p 'synchronized ($LOCK) { $$$BODY }' -l java .
```

---

## Cross-Language Recipes

### Rename a function (any language)
```
# Step 1: Find all calls
ast-grep run -p 'oldFunctionName($$$ARGS)' -l javascript .

# Step 2: Rename calls
ast-grep run -p 'oldFunctionName($$$ARGS)' -r 'newFunctionName($$$ARGS)' -l javascript --update-all .
```

### Find unused variables pattern
```
# Find assignments where variable might be unused
# (combine with grep to verify no other references)
ast-grep run -p 'const $VAR = $EXPR' -l javascript .
```

### API migration pattern
```
# Example: migrate from old API to new API
# Old: axios.get(url).then(res => res.data)
# New: fetch(url).then(res => res.json())
ast-grep run -p 'axios.get($URL)' -r 'fetch($URL)' -l javascript --update-all .
```

### Find all function definitions (most languages)
```
# Python
ast-grep run -p 'def $NAME($$$): $$$' -l python .
# JavaScript
ast-grep run -p 'function $NAME($$$) { $$$ }' -l javascript .
# Go
ast-grep run -p 'func $NAME($$$) $$$' -l go .
# Rust
ast-grep run -p 'fn $NAME($$$) $$$' -l rust .
```

### Find TODO patterns in code (not comments)
```
# Find NotImplementedError / todo! / unimplemented patterns
ast-grep run -p 'raise NotImplementedError($$$)' -l python .
ast-grep run -p 'todo!($$$)' -l rust .
ast-grep run -p 'throw new Error("TODO$$$")' -l javascript .
```
