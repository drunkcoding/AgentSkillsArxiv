#!/usr/bin/env python3
"""
fdep - Function Dependency Search using Tree-sitter

AST-accurate function dependency analysis across multiple languages.
Faster and more precise than grep-based approaches.

Usage:
    fdep.py callees <function> <paths>...    # What does <function> call?
    fdep.py callers <function> <paths>...    # What calls <function>?
    fdep.py deps <function> <paths>...       # Transitive call chain (downstream)
    fdep.py rdeps <function> <paths>...      # Reverse transitive deps (upstream/impact)
    fdep.py graph <paths>...                 # Full call graph
    fdep.py unused <paths>...                # Functions never called
    fdep.py circular <paths>...              # Circular dependency detection
    fdep.py defs <paths>...                  # List all function definitions
    fdep.py calls <paths>...                 # List all function calls

Options:
    --json          Output as JSON
    --dot           Output as Graphviz DOT (graph/deps/rdeps only)
    --depth N       Max depth for transitive searches (default: 10)
    --lang LANG     Force language (auto-detected from extension by default)
    --install       Auto-install missing tree-sitter packages
"""

import argparse
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

__version__ = "0.2.0"
_MIN_PYTHON = (3, 10)
_MIN_TS_VERSION = (0, 23)

# ---------------------------------------------------------------------------
# Language configuration: extension -> (language_name, pip_package, module)
# ---------------------------------------------------------------------------
LANG_CONFIG = {
    "python": {
        "extensions": {".py", ".pyi"},
        "pip_package": "tree-sitter-python",
        "module": "tree_sitter_python",
        "queries": {
            "definitions": """
                (function_definition
                  name: (identifier) @name) @def
            """,
            "calls": """
                (call
                  function: (identifier) @name)
                (call
                  function: (attribute
                    attribute: (identifier) @name))
            """,
        },
    },
    "javascript": {
        "extensions": {".js", ".jsx", ".mjs", ".cjs"},
        "pip_package": "tree-sitter-javascript",
        "module": "tree_sitter_javascript",
        "queries": {
            "definitions": """
                (function_declaration
                  name: (identifier) @name) @def
                (variable_declarator
                  name: (identifier) @name
                  value: (arrow_function) @def)
                (variable_declarator
                  name: (identifier) @name
                  value: (function_expression) @def)
                (method_definition
                  name: (property_identifier) @name) @def
            """,
            "calls": """
                (call_expression
                  function: (identifier) @name)
                (call_expression
                  function: (member_expression
                    property: (property_identifier) @name))
            """,
        },
    },
    "typescript": {
        "extensions": {".ts", ".tsx"},
        "pip_package": "tree-sitter-typescript",
        "module": "tree_sitter_typescript",
        "lang_attr": "language_typescript",
        "queries": {
            "definitions": """
                (function_declaration
                  name: (identifier) @name) @def
                (variable_declarator
                  name: (identifier) @name
                  value: (arrow_function) @def)
                (variable_declarator
                  name: (identifier) @name
                  value: (function_expression) @def)
                (method_definition
                  name: (property_identifier) @name) @def
            """,
            "calls": """
                (call_expression
                  function: (identifier) @name)
                (call_expression
                  function: (member_expression
                    property: (property_identifier) @name))
            """,
        },
    },
    "go": {
        "extensions": {".go"},
        "pip_package": "tree-sitter-go",
        "module": "tree_sitter_go",
        "queries": {
            "definitions": """
                (function_declaration
                  name: (identifier) @name) @def
                (method_declaration
                  name: (field_identifier) @name) @def
            """,
            "calls": """
                (call_expression
                  function: (identifier) @name)
                (call_expression
                  function: (selector_expression
                    field: (field_identifier) @name))
            """,
        },
    },
    "rust": {
        "extensions": {".rs"},
        "pip_package": "tree-sitter-rust",
        "module": "tree_sitter_rust",
        "queries": {
            "definitions": """
                (function_item
                  name: (identifier) @name) @def
            """,
            "calls": """
                (call_expression
                  function: (identifier) @name)
                (call_expression
                  function: (scoped_identifier
                    name: (identifier) @name))
                (call_expression
                  function: (field_expression
                    field: (field_identifier) @name))
            """,
        },
    },
    "c": {
        "extensions": {".c", ".h"},
        "pip_package": "tree-sitter-c",
        "module": "tree_sitter_c",
        "queries": {
            "definitions": """
                (function_definition
                  declarator: (function_declarator
                    declarator: (identifier) @name)) @def
            """,
            "calls": """
                (call_expression
                  function: (identifier) @name)
            """,
        },
    },
    "cpp": {
        "extensions": {".cpp", ".cc", ".cxx", ".hpp", ".hxx", ".hh"},
        "pip_package": "tree-sitter-cpp",
        "module": "tree_sitter_cpp",
        "queries": {
            "definitions": """
                (function_definition
                  declarator: (function_declarator
                    declarator: (identifier) @name)) @def
                (function_definition
                  declarator: (function_declarator
                    declarator: (qualified_identifier
                      name: (identifier) @name))) @def
            """,
            "calls": """
                (call_expression
                  function: (identifier) @name)
                (call_expression
                  function: (qualified_identifier
                    name: (identifier) @name))
                (call_expression
                  function: (field_expression
                    field: (field_identifier) @name))
            """,
        },
    },
    "java": {
        "extensions": {".java"},
        "pip_package": "tree-sitter-java",
        "module": "tree_sitter_java",
        "queries": {
            "definitions": """
                (method_declaration
                  name: (identifier) @name) @def
                (constructor_declaration
                  name: (identifier) @name) @def
            """,
            "calls": """
                (method_invocation
                  name: (identifier) @name)
                (object_creation_expression
                  type: (type_identifier) @name)
            """,
        },
    },
}

# Build extension -> language lookup
EXT_TO_LANG = {}
for lang_name, cfg in LANG_CONFIG.items():
    for ext in cfg["extensions"]:
        EXT_TO_LANG[ext] = lang_name


# ---------------------------------------------------------------------------
# Dependency management
# ---------------------------------------------------------------------------
def check_and_install(lang_name, auto_install=False):
    """Check if tree-sitter and language package are available. Install if requested."""
    if sys.version_info < _MIN_PYTHON:
        print(
            f"Error: Python >= {_MIN_PYTHON[0]}.{_MIN_PYTHON[1]} required "
            f"(found {sys.version_info.major}.{sys.version_info.minor}).",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        import tree_sitter  # noqa: F401
    except ImportError:
        if auto_install:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", "tree-sitter"]
            )
            import tree_sitter
        else:
            print(
                "Error: 'tree-sitter' not installed. Run with --install or: pip install tree-sitter",
                file=sys.stderr,
            )
            sys.exit(1)

    from importlib.metadata import version as _meta_version
    ts_ver_str = _meta_version("tree-sitter")
    ts_ver = tuple(int(x) for x in ts_ver_str.split(".")[:2])
    if ts_ver < _MIN_TS_VERSION:
        if auto_install:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", "--upgrade", "tree-sitter"]
            )
        else:
            print(
                f"Error: tree-sitter >= {_MIN_TS_VERSION[0]}.{_MIN_TS_VERSION[1]} required "
                f"(found {ts_ver_str}). "
                f"Run with --install or: pip install --upgrade tree-sitter",
                file=sys.stderr,
            )
            sys.exit(1)

    cfg = LANG_CONFIG[lang_name]
    try:
        __import__(cfg["module"])
    except ImportError:
        if auto_install:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "-q", cfg["pip_package"]]
            )
        else:
            print(
                f"Error: '{cfg['pip_package']}' not installed. "
                f"Run with --install or: pip install {cfg['pip_package']}",
                file=sys.stderr,
            )
            sys.exit(1)


def get_parser(lang_name):
    """Create a tree-sitter parser for the given language."""
    from tree_sitter import Language, Parser

    cfg = LANG_CONFIG[lang_name]
    mod = __import__(cfg["module"])
    lang_func = getattr(mod, cfg.get("lang_attr", "language"), None)
    if lang_func is None:
        # Fallback: try common attribute names
        for attr in ["language", "LANGUAGE"]:
            lang_func = getattr(mod, attr, None)
            if lang_func is not None:
                break
    if lang_func is None:
        raise RuntimeError(f"Cannot find language() in {cfg['module']}")

    language = Language(lang_func())
    parser = Parser(language)
    return parser, language


# ---------------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------------
class FunctionInfo:
    """Parsed function info from a single file."""

    __slots__ = ("name", "file", "line", "end_line", "start_byte", "end_byte")

    def __init__(self, name, file, line, end_line, start_byte, end_byte):
        self.name = name
        self.file = file
        self.line = line
        self.end_line = end_line
        self.start_byte = start_byte
        self.end_byte = end_byte

    def to_dict(self):
        return {
            "name": self.name,
            "file": str(self.file),
            "line": self.line,
            "end_line": self.end_line,
        }


def _query_matches(language, query_str, node, *, start_byte=None, end_byte=None,
                   match_limit=None):
    """Run a tree-sitter query and return list of (pattern_idx, captures_dict) matches."""
    from tree_sitter import Query, QueryCursor

    q = Query(language, query_str)
    kwargs = {}
    if match_limit is not None:
        kwargs["match_limit"] = match_limit
    cursor = QueryCursor(q, **kwargs)
    if start_byte is not None and end_byte is not None:
        cursor.set_byte_range(start_byte, end_byte)
    result = cursor.matches(node)
    if match_limit is not None and cursor.did_exceed_match_limit:
        print("Warning: match limit exceeded; results may be incomplete.", file=sys.stderr)
    return result


def _query_captures(language, query_str, node, *, start_byte=None, end_byte=None,
                    match_limit=None):
    """Run a tree-sitter query and return captures dict {name: [nodes]}."""
    from tree_sitter import Query, QueryCursor

    q = Query(language, query_str)
    kwargs = {}
    if match_limit is not None:
        kwargs["match_limit"] = match_limit
    cursor = QueryCursor(q, **kwargs)
    if start_byte is not None and end_byte is not None:
        cursor.set_byte_range(start_byte, end_byte)
    result = cursor.captures(node)
    if match_limit is not None and cursor.did_exceed_match_limit:
        print("Warning: match limit exceeded; results may be incomplete.", file=sys.stderr)
    return result


def parse_file(filepath, parser, language, lang_name, *, match_limit=None):
    """Parse a single file and extract function definitions and calls."""
    cfg = LANG_CONFIG[lang_name]
    source = Path(filepath).read_bytes()
    tree = parser.parse(source)

    # Extract definitions using matches() to keep name/def paired
    def_matches = _query_matches(
        language, cfg["queries"]["definitions"], tree.root_node,
        match_limit=match_limit,
    )

    definitions = []
    def_nodes = []  # (FunctionInfo, def_node) pairs for scoping calls

    for _pat_idx, captures in def_matches:
        name_nodes = captures.get("name", [])
        def_node_list = captures.get("def", [])
        if not name_nodes:
            continue
        name_node = name_nodes[0]
        def_node = def_node_list[0] if def_node_list else name_node.parent
        fname = name_node.text.decode("utf8")
        info = FunctionInfo(
            name=fname,
            file=filepath,
            line=name_node.start_point[0] + 1,
            end_line=def_node.end_point[0] + 1 if def_node else name_node.end_point[0] + 1,
            start_byte=def_node.start_byte if def_node else name_node.start_byte,
            end_byte=def_node.end_byte if def_node else name_node.end_byte,
        )
        definitions.append(info)
        def_nodes.append((info, def_node))

    # Extract all call name nodes
    call_captures = _query_captures(
        language, cfg["queries"]["calls"], tree.root_node,
        match_limit=match_limit,
    )
    calls_per_func = defaultdict(list)  # func_name -> [called_names]
    global_calls = []  # calls not inside any function

    call_name_nodes = call_captures.get("name", [])

    for call_node in call_name_nodes:
        call_name = call_node.text.decode("utf8")
        call_byte = call_node.start_byte

        # Find which function this call is inside
        enclosing = None
        for info, def_node in def_nodes:
            if def_node and info.start_byte <= call_byte <= info.end_byte:
                # Pick the tightest enclosing function (for nested functions)
                if enclosing is None or (info.end_byte - info.start_byte) < (
                    enclosing.end_byte - enclosing.start_byte
                ):
                    enclosing = info

        if enclosing:
            calls_per_func[enclosing.name].append(call_name)
        else:
            global_calls.append(call_name)

    return definitions, calls_per_func, global_calls


def analyze_paths(paths, lang_override=None, auto_install=False, match_limit=None):
    """Analyze all files in the given paths."""
    files = collect_files(paths, lang_override)
    if not files:
        print("No supported source files found.", file=sys.stderr)
        sys.exit(1)

    all_defs = []  # list of FunctionInfo
    all_calls = defaultdict(list)  # func_name -> [called_names]
    all_global_calls = []
    parsers = {}  # lang_name -> (parser, language)

    for filepath, lang_name in files:
        if lang_name not in parsers:
            check_and_install(lang_name, auto_install)
            parsers[lang_name] = get_parser(lang_name)

        parser, language = parsers[lang_name]
        defs, calls, global_calls = parse_file(
            filepath, parser, language, lang_name, match_limit=match_limit,
        )
        all_defs.extend(defs)
        for fname, called in calls.items():
            all_calls[fname].extend(called)
        all_global_calls.extend(global_calls)

    return all_defs, all_calls, all_global_calls


def collect_files(paths, lang_override=None):
    """Collect all source files from paths with their detected language."""
    files = []
    for p in paths:
        path = Path(p)
        if path.is_file():
            lang = lang_override or EXT_TO_LANG.get(path.suffix)
            if lang:
                files.append((str(path), lang))
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    lang = lang_override or EXT_TO_LANG.get(child.suffix)
                    if lang:
                        files.append((str(child), lang))
    return files


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------
def cmd_defs(args):
    """List all function definitions."""
    defs, _, _ = analyze_paths(args.paths, args.lang, args.install, args.match_limit)
    if args.json:
        print(json.dumps([d.to_dict() for d in defs], indent=2))
    else:
        for d in defs:
            print(f"{d.file}:{d.line}\t{d.name}")


def cmd_calls(args):
    """List all function calls grouped by caller."""
    _, calls, global_calls = analyze_paths(args.paths, args.lang, args.install, args.match_limit)
    if args.json:
        result = dict(calls)
        if global_calls:
            result["<module>"] = global_calls
        print(json.dumps(result, indent=2))
    else:
        for func, called in sorted(calls.items()):
            unique_called = sorted(set(called))
            print(f"{func} -> {', '.join(unique_called)}")
        if global_calls:
            print(f"<module> -> {', '.join(sorted(set(global_calls)))}")


def cmd_callees(args):
    """What does a function call?"""
    _, calls, _ = analyze_paths(args.paths, args.lang, args.install, args.match_limit)
    target = args.function
    if target not in calls:
        print(f"Function '{target}' not found or makes no calls.", file=sys.stderr)
        sys.exit(1)
    callees = sorted(set(calls[target]))
    if args.json:
        print(json.dumps({"function": target, "callees": callees}, indent=2))
    else:
        for c in callees:
            print(c)


def cmd_callers(args):
    """What calls a function?"""
    _, calls, global_calls = analyze_paths(args.paths, args.lang, args.install, args.match_limit)
    target = args.function
    callers = []
    for func, called in calls.items():
        if target in called:
            callers.append(func)
    if target in global_calls:
        callers.append("<module>")
    callers = sorted(set(callers))
    if not callers:
        print(f"No callers found for '{target}'.", file=sys.stderr)
    if args.json:
        print(json.dumps({"function": target, "callers": callers}, indent=2))
    else:
        for c in callers:
            print(c)


def _transitive(calls, start, max_depth, reverse=False):
    """BFS for transitive dependencies."""
    if reverse:
        # Build reverse graph
        graph = defaultdict(set)
        for func, called in calls.items():
            for c in called:
                graph[c].add(func)
    else:
        graph = {func: set(called) for func, called in calls.items()}

    visited = set()
    queue = [(start, 0)]
    result = []  # (name, depth)

    while queue:
        current, depth = queue.pop(0)
        if current in visited or depth > max_depth:
            continue
        visited.add(current)
        if current != start:
            result.append((current, depth))
        for neighbor in sorted(graph.get(current, [])):
            if neighbor not in visited:
                queue.append((neighbor, depth + 1))

    return result


def cmd_deps(args):
    """Transitive dependencies (downstream)."""
    defs, calls, _ = analyze_paths(args.paths, args.lang, args.install, args.match_limit)
    target = args.function
    result = _transitive(calls, target, args.depth)

    # Build def lookup for file:line info
    def_lookup = {}
    for d in defs:
        def_lookup.setdefault(d.name, []).append(d)

    if args.json:
        deps = []
        for name, depth in result:
            entry = {"name": name, "depth": depth}
            if name in def_lookup:
                entry["locations"] = [d.to_dict() for d in def_lookup[name]]
            deps.append(entry)
        print(json.dumps({"function": target, "deps": deps}, indent=2))
    elif args.dot:
        _print_dot_subgraph(calls, target, result)
    else:
        for name, depth in result:
            indent = "  " * depth
            loc = ""
            if name in def_lookup:
                d = def_lookup[name][0]
                loc = f"  ({d.file}:{d.line})"
            print(f"{indent}{name}{loc}")


def cmd_rdeps(args):
    """Reverse transitive dependencies (upstream/impact)."""
    defs, calls, _ = analyze_paths(args.paths, args.lang, args.install, args.match_limit)
    target = args.function
    result = _transitive(calls, target, args.depth, reverse=True)

    def_lookup = {}
    for d in defs:
        def_lookup.setdefault(d.name, []).append(d)

    if args.json:
        rdeps = []
        for name, depth in result:
            entry = {"name": name, "depth": depth}
            if name in def_lookup:
                entry["locations"] = [d.to_dict() for d in def_lookup[name]]
            rdeps.append(entry)
        print(json.dumps({"function": target, "rdeps": rdeps}, indent=2))
    elif args.dot:
        # For rdeps, show reverse edges
        rev_calls = defaultdict(list)
        for func, called in calls.items():
            for c in called:
                rev_calls[c].append(func)
        names = {target} | {n for n, _ in result}
        print("digraph rdeps {")
        print('  rankdir=BT;')
        for name in sorted(names):
            for caller in rev_calls.get(name, []):
                if caller in names:
                    print(f'  "{caller}" -> "{name}";')
        print("}")
    else:
        for name, depth in result:
            indent = "  " * depth
            loc = ""
            if name in def_lookup:
                d = def_lookup[name][0]
                loc = f"  ({d.file}:{d.line})"
            print(f"{indent}{name}{loc}")


def _print_dot_subgraph(calls, root, result):
    """Print DOT graph for a dependency subgraph."""
    names = {root} | {n for n, _ in result}
    print("digraph deps {")
    print(f'  "{root}" [style=filled, fillcolor=lightblue];')
    for func, called in calls.items():
        if func in names:
            for c in called:
                if c in names:
                    print(f'  "{func}" -> "{c}";')
    print("}")


def cmd_graph(args):
    """Full call graph."""
    defs, calls, global_calls = analyze_paths(args.paths, args.lang, args.install, args.match_limit)

    if args.json:
        result = {}
        for func, called in sorted(calls.items()):
            result[func] = sorted(set(called))
        if global_calls:
            result["<module>"] = sorted(set(global_calls))
        print(json.dumps(result, indent=2))
    elif args.dot:
        print("digraph callgraph {")
        for func, called in sorted(calls.items()):
            for c in sorted(set(called)):
                print(f'  "{func}" -> "{c}";')
        if global_calls:
            for c in sorted(set(global_calls)):
                print(f'  "<module>" -> "{c}";')
        print("}")
    else:
        for func, called in sorted(calls.items()):
            unique_called = sorted(set(called))
            print(f"{func} -> {', '.join(unique_called)}")


def cmd_unused(args):
    """Find functions that are never called."""
    defs, calls, global_calls = analyze_paths(args.paths, args.lang, args.install, args.match_limit)

    # Collect all called names
    all_called = set()
    for called in calls.values():
        all_called.update(called)
    all_called.update(global_calls)

    # Find defs not in called set
    defined_names = {d.name for d in defs}
    unused = []
    seen = set()
    for d in defs:
        if d.name not in all_called and d.name not in seen:
            # Skip common entry points
            if d.name not in ("main", "__init__", "__new__", "setUp", "tearDown"):
                unused.append(d)
                seen.add(d.name)

    if args.json:
        print(json.dumps([d.to_dict() for d in unused], indent=2))
    else:
        if not unused:
            print("No unused functions found.")
        for d in unused:
            print(f"{d.file}:{d.line}\t{d.name}")


def cmd_circular(args):
    """Detect circular dependencies."""
    _, calls, _ = analyze_paths(args.paths, args.lang, args.install, args.match_limit)

    # Build adjacency
    graph = defaultdict(set)
    for func, called in calls.items():
        for c in called:
            graph[func].add(c)

    # DFS cycle detection
    cycles = []
    visited = set()
    rec_stack = set()
    path = []

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in sorted(graph.get(node, [])):
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in rec_stack:
                # Found cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        path.pop()
        rec_stack.discard(node)

    for node in sorted(graph.keys()):
        if node not in visited:
            dfs(node)

    if args.json:
        print(json.dumps({"cycles": [list(c) for c in cycles]}, indent=2))
    else:
        if not cycles:
            print("No circular dependencies found.")
        for cycle in cycles:
            print(" -> ".join(cycle))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _get_ts_version():
    """Get the installed tree-sitter version string."""
    from importlib.metadata import version
    return version("tree-sitter")


def _print_version(lang_name=None):
    """Print version diagnostics and exit."""
    import platform
    print(f"fdep {__version__}")
    try:
        ts_ver = _get_ts_version()
        print(f"tree-sitter {ts_ver}")
    except Exception:
        print("tree-sitter not installed")
    print(f"Python {platform.python_version()}")
    if lang_name:
        from tree_sitter import Language
        cfg = LANG_CONFIG.get(lang_name)
        if cfg:
            try:
                mod = __import__(cfg["module"])
                lang_func = getattr(mod, cfg.get("lang_attr", "language"), None)
                if lang_func:
                    language = Language(lang_func())
                    print(f"Language ABI version: {language.abi_version}")
                    print(f"Language semantic version: {language.semantic_version}")
            except Exception as e:
                print(f"Could not load language '{lang_name}': {e}")


def main():
    parser = argparse.ArgumentParser(
        prog="fdep",
        description="Function Dependency Search using Tree-sitter",
    )
    parser.add_argument("--version", action="store_true",
                        help="Print version info and exit")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--dot", action="store_true", help="Graphviz DOT output")
    parser.add_argument("--depth", type=int, default=10, help="Max transitive depth")
    parser.add_argument("--match-limit", type=int, default=None, dest="match_limit",
                        help="Max matches per query (warns if exceeded)")
    parser.add_argument("--lang", type=str, choices=list(LANG_CONFIG.keys()),
                        help="Force language detection")
    parser.add_argument("--install", action="store_true",
                        help="Auto-install missing tree-sitter packages")

    # Handle --version before requiring subcommand
    if "--version" in sys.argv:
        lang_name = None
        if "--lang" in sys.argv:
            idx = sys.argv.index("--lang")
            if idx + 1 < len(sys.argv):
                lang_name = sys.argv[idx + 1]
        _print_version(lang_name)
        sys.exit(0)

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Shared flags added to each subparser so they work before or after subcommand
    common_flags = [
        ("--json", dict(action="store_true", default=False, help="JSON output")),
        ("--dot", dict(action="store_true", default=False, help="Graphviz DOT output")),
        ("--depth", dict(type=int, default=10, help="Max transitive depth")),
        ("--match-limit", dict(type=int, default=None, dest="match_limit",
                               help="Max matches per query (warns if exceeded)")),
        ("--lang", dict(type=str, choices=list(LANG_CONFIG.keys()),
                        default=None, help="Force language detection")),
        ("--install", dict(action="store_true", default=False,
                           help="Auto-install missing tree-sitter packages")),
    ]

    # Commands with function argument
    for cmd_name in ("callees", "callers", "deps", "rdeps"):
        sp = subparsers.add_parser(cmd_name)
        sp.add_argument("function", help="Target function name")
        sp.add_argument("paths", nargs="+", help="Files or directories to analyze")
        for flag, kwargs in common_flags:
            sp.add_argument(flag, **kwargs)

    # Commands without function argument
    for cmd_name in ("graph", "unused", "circular", "defs", "calls"):
        sp = subparsers.add_parser(cmd_name)
        sp.add_argument("paths", nargs="+", help="Files or directories to analyze")
        for flag, kwargs in common_flags:
            sp.add_argument(flag, **kwargs)

    args = parser.parse_args()

    cmd_map = {
        "callees": cmd_callees,
        "callers": cmd_callers,
        "deps": cmd_deps,
        "rdeps": cmd_rdeps,
        "graph": cmd_graph,
        "unused": cmd_unused,
        "circular": cmd_circular,
        "defs": cmd_defs,
        "calls": cmd_calls,
    }

    cmd_map[args.command](args)


if __name__ == "__main__":
    main()
