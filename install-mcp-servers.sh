#!/usr/bin/env bash
set -euo pipefail

# ─── MCP Server Installation Script ──────────────────────────────────────────
#
# Installs ast-grep-mcp-server and fdep-mcp-server for use with:
#   • Claude Code          (.mcp.json / ~/.claude.json)
#   • OpenAI Codex         (.codex/config.toml / ~/.codex/config.toml)
#   • OpenCode             (opencode.json / ~/.config/opencode/opencode.json)
#   • Cline                (VS Code extension / cline_mcp_settings.json)
#   • GitHub Copilot       (VS Code / .vscode/mcp.json)
#
# Usage:
#   ./install-mcp-servers.sh [options]
#
# Options:
#   --targets <list>   Comma-separated: claude,codex,opencode,cline,copilot,all (default: all)
#   --scope <scope>    project (writes to repo) or global (writes to ~/) (default: project)
#   --dry-run          Preview changes without writing
#   --skip-build       Skip npm install / pip install build steps
#   --help             Show this help
#
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AST_GREP_DIR="${SCRIPT_DIR}/ast-grep-mcp-server"
FDEP_DIR="${SCRIPT_DIR}/fdep-mcp-server"

# ─── Output helpers ──────────────────────────────────────────────────────────

if [ -t 1 ]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'
    BLUE='\033[0;34m'; BOLD='\033[1m'; DIM='\033[2m'; RESET='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; BLUE=''; BOLD=''; DIM=''; RESET=''
fi

info()    { printf "${BLUE}▸${RESET} %s\n" "$*"; }
success() { printf "${GREEN}✓${RESET} %s\n" "$*"; }
warn()    { printf "${YELLOW}⚠${RESET} %s\n" "$*" >&2; }
error()   { printf "${RED}✗${RESET} %s\n" "$*" >&2; }
header()  { printf "\n${BOLD}%s${RESET}\n" "$*"; }

# ─── Prerequisite checks ────────────────────────────────────────────────────

check_prereqs() {
    local ok=true

    if ! command -v node &>/dev/null; then
        error "node not found. Install Node.js >= 18: https://nodejs.org"
        ok=false
    fi

    if ! command -v npm &>/dev/null; then
        error "npm not found. Install Node.js >= 18: https://nodejs.org"
        ok=false
    fi

    if ! command -v python3 &>/dev/null; then
        error "python3 not found. Install Python >= 3.9"
        ok=false
    fi

    if ! command -v sg &>/dev/null; then
        warn "ast-grep CLI (sg) not found. ast-grep-mcp-server needs it at runtime."
        warn "Install: npm install -g @ast-grep/cli  or  cargo install ast-grep"
    fi

    if [ "$ok" = false ]; then
        error "Missing prerequisites. Aborting."
        exit 1
    fi
}

# ─── Build servers ───────────────────────────────────────────────────────────

build_ast_grep() {
    header "Building ast-grep-mcp-server"
    if [ ! -d "${AST_GREP_DIR}/node_modules" ]; then
        info "Installing npm dependencies..."
        npm --prefix "$AST_GREP_DIR" install --no-fund --no-audit
    fi
    info "Compiling TypeScript..."
    npm --prefix "$AST_GREP_DIR" run build
    success "ast-grep-mcp-server built → ${AST_GREP_DIR}/dist/index.js"
}

build_fdep() {
    header "Building fdep-mcp-server"
    info "Installing Python package in editable mode..."
    pip install -e "$FDEP_DIR" --quiet 2>/dev/null || python3 -m pip install -e "$FDEP_DIR" --quiet
    success "fdep-mcp-server installed → python3 -m fdep_mcp"
}

# ─── JSON merge helper ───────────────────────────────────────────────────────
# Merges MCP server entries into an existing JSON config file.
# Uses python3 for reliable JSON manipulation (no jq dependency).

json_merge_servers() {
    local file="$1"
    local servers_key="$2"  # e.g. "mcpServers" or "servers"
    local ast_entry="$3"
    local fdep_entry="$4"
    local dry_run="$5"

    if [ "$dry_run" = true ]; then
        info "[dry-run] Would merge into: ${file}"
        info "[dry-run] Key: ${servers_key}"
        return 0
    fi

    python3 -c "
import json, os, sys

file_path = sys.argv[1]
servers_key = sys.argv[2]
ast_json = sys.argv[3]
fdep_json = sys.argv[4]

# Load existing or start fresh
if os.path.exists(file_path):
    with open(file_path) as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            config = {}
else:
    os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
    config = {}

# Navigate to the servers key (supports nested like 'mcp.servers')
parts = servers_key.split('.')
obj = config
for part in parts[:-1]:
    obj = obj.setdefault(part, {})
servers = obj.setdefault(parts[-1], {})

# Merge entries
servers['ast-grep'] = json.loads(ast_json)
servers['fdep'] = json.loads(fdep_json)

# Write back
with open(file_path, 'w') as f:
    json.dump(config, f, indent=2)
    f.write('\n')
" "$file" "$servers_key" "$ast_entry" "$fdep_entry"
}

# ─── TOML merge helper ──────────────────────────────────────────────────────
# Merges MCP server entries into a TOML config file (for Codex).
# Pure python3 — uses tomllib (3.11+) for reading, manual write for compat.

toml_merge_servers() {
    local file="$1"
    local dry_run="$2"

    if [ "$dry_run" = true ]; then
        info "[dry-run] Would merge TOML into: ${file}"
        return 0
    fi

    python3 -c "
import os, sys, re

file_path = sys.argv[1]
ast_grep_dir = sys.argv[2]
fdep_dir = sys.argv[3]

# Read existing content
existing = ''
if os.path.exists(file_path):
    with open(file_path) as f:
        existing = f.read()

# Check if our sections already exist and remove them for re-merge
sections_to_add = ['mcp_servers.ast-grep', 'mcp_servers.fdep']
for section in sections_to_add:
    # Remove existing section block (from header to next section or EOF)
    pattern = r'\n?\[' + re.escape(section) + r'\][^\[]*'
    existing = re.sub(pattern, '', existing)

# Also remove env sub-sections
for sub in ['mcp_servers.ast-grep.env', 'mcp_servers.fdep.env']:
    pattern = r'\n?\[' + re.escape(sub) + r'\][^\[]*'
    existing = re.sub(pattern, '', existing)

# Clean up trailing whitespace
existing = existing.rstrip()

# Build new TOML sections
new_sections = '''

[mcp_servers.ast-grep]
command = \"node\"
args = [\"{ast_grep_dir}/dist/index.js\"]

[mcp_servers.fdep]
command = \"python3\"
args = [\"-m\", \"fdep_mcp\"]

[mcp_servers.fdep.env]
PYTHONPATH = \"{fdep_dir}\"
'''.format(ast_grep_dir=ast_grep_dir, fdep_dir=fdep_dir)

os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
with open(file_path, 'w') as f:
    if existing:
        f.write(existing)
    f.write(new_sections)
    f.write('\n')
" "$file" "$AST_GREP_DIR" "$FDEP_DIR"
}

# ─── Server entry builders ───────────────────────────────────────────────────
# Each function returns JSON for one server entry, parameterized by paths.

ast_grep_entry_standard() {
    # Standard format with "type": "stdio" (VS Code Copilot)
    cat <<EOF
{
  "type": "stdio",
  "command": "node",
  "args": ["${AST_GREP_DIR}/dist/index.js"]
}
EOF
}

fdep_entry_standard() {
    cat <<EOF
{
  "type": "stdio",
  "command": "python3",
  "args": ["-m", "fdep_mcp"],
  "env": {
    "PYTHONPATH": "${FDEP_DIR}"
  }
}
EOF
}

ast_grep_entry_no_type() {
    # Format without "type" field (Claude Code, Cline, Codex JSON fallback)
    cat <<EOF
{
  "command": "node",
  "args": ["${AST_GREP_DIR}/dist/index.js"]
}
EOF
}

fdep_entry_no_type() {
    cat <<EOF
{
  "command": "python3",
  "args": ["-m", "fdep_mcp"],
  "env": {
    "PYTHONPATH": "${FDEP_DIR}"
  }
}
EOF
}

# ─── Per-tool installers ─────────────────────────────────────────────────────

install_claude_code() {
    local scope="$1" dry_run="$2"
    header "Configuring Claude Code"

    local config_file
    if [ "$scope" = "project" ]; then
        config_file="${SCRIPT_DIR}/.mcp.json"
    else
        config_file="${HOME}/.claude.json"
    fi

    info "Config: ${config_file}"

    json_merge_servers \
        "$config_file" \
        "mcpServers" \
        "$(ast_grep_entry_no_type)" \
        "$(fdep_entry_no_type)" \
        "$dry_run"

    if [ "$dry_run" = false ]; then
        success "Claude Code configured → ${config_file}"
    fi
}

install_codex() {
    local scope="$1" dry_run="$2"
    header "Configuring OpenAI Codex"

    # Codex uses TOML config
    local config_file
    if [ "$scope" = "project" ]; then
        config_file="${SCRIPT_DIR}/.codex/config.toml"
    else
        config_file="${HOME}/.codex/config.toml"
    fi

    info "Config: ${config_file} (TOML)"

    toml_merge_servers "$config_file" "$dry_run"

    if [ "$dry_run" = false ]; then
        success "Codex configured → ${config_file}"
    fi
}

install_opencode() {
    local scope="$1" dry_run="$2"
    header "Configuring OpenCode"

    # OpenCode uses opencode.json with "mcp" key; command is a single array
    local config_file
    if [ "$scope" = "project" ]; then
        config_file="${SCRIPT_DIR}/opencode.json"
    else
        config_file="${HOME}/.config/opencode/opencode.json"
    fi

    info "Config: ${config_file}"

    # OpenCode format: "command" is a single array (no separate "args"),
    # "type": "local" for stdio, env key is "environment"
    local ast_entry fdep_entry
    ast_entry=$(cat <<EOF
{
  "type": "local",
  "command": ["node", "${AST_GREP_DIR}/dist/index.js"],
  "enabled": true
}
EOF
)
    fdep_entry=$(cat <<EOF
{
  "type": "local",
  "command": ["python3", "-m", "fdep_mcp"],
  "enabled": true,
  "environment": {
    "PYTHONPATH": "${FDEP_DIR}"
  }
}
EOF
)

    if [ "$dry_run" = true ]; then
        info "[dry-run] Would merge into: ${config_file}"
        return 0
    fi

    python3 -c "
import json, os, sys

file_path = sys.argv[1]
ast_json = sys.argv[2]
fdep_json = sys.argv[3]

if os.path.exists(file_path):
    with open(file_path) as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError:
            config = {}
else:
    os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
    config = {}

mcp = config.setdefault('mcp', {})
mcp['ast-grep'] = json.loads(ast_json)
mcp['fdep'] = json.loads(fdep_json)

with open(file_path, 'w') as f:
    json.dump(config, f, indent=2)
    f.write('\n')
" "$config_file" "$ast_entry" "$fdep_entry"

    success "OpenCode configured → ${config_file}"
}

install_cline() {
    local scope="$1" dry_run="$2"
    header "Configuring Cline"

    # Cline stores MCP settings in VS Code globalStorage
    local config_file
    if [ "$scope" = "project" ]; then
        config_file="${SCRIPT_DIR}/.vscode/cline_mcp_settings.json"
    else
        # Platform-specific globalStorage path
        case "$(uname -s)" in
            Darwin) config_file="${HOME}/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json" ;;
            *)      config_file="${HOME}/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json" ;;
        esac
    fi

    info "Config: ${config_file}"

    json_merge_servers \
        "$config_file" \
        "mcpServers" \
        "$(ast_grep_entry_no_type)" \
        "$(fdep_entry_no_type)" \
        "$dry_run"

    if [ "$dry_run" = false ]; then
        success "Cline configured → ${config_file}"
    fi
}

install_copilot() {
    local scope="$1" dry_run="$2"
    header "Configuring GitHub Copilot (VS Code)"

    # Copilot reads MCP config from .vscode/mcp.json (project) or VS Code settings
    local config_file
    if [ "$scope" = "project" ]; then
        config_file="${SCRIPT_DIR}/.vscode/mcp.json"
    else
        case "$(uname -s)" in
            Darwin) config_file="${HOME}/Library/Application Support/Code/User/settings.json" ;;
            *)      config_file="${HOME}/.config/Code/User/settings.json" ;;
        esac
        warn "Global Copilot MCP: merging into VS Code settings.json (mcp.servers key)"
    fi

    info "Config: ${config_file}"

    if [ "$scope" = "project" ]; then
        # .vscode/mcp.json uses "servers" at top level with "type": "stdio"
        json_merge_servers \
            "$config_file" \
            "servers" \
            "$(ast_grep_entry_standard)" \
            "$(fdep_entry_standard)" \
            "$dry_run"
    else
        # VS Code settings.json nests under "mcp.servers"
        json_merge_servers \
            "$config_file" \
            "mcp.servers" \
            "$(ast_grep_entry_standard)" \
            "$(fdep_entry_standard)" \
            "$dry_run"
    fi

    if [ "$dry_run" = false ]; then
        success "Copilot configured → ${config_file}"
    fi
}

# ─── Summary ─────────────────────────────────────────────────────────────────

print_summary() {
    local targets="$1" scope="$2"

    header "Installation complete"
    echo ""
    printf "${DIM}Servers installed:${RESET}\n"
    printf "  • ast-grep-mcp-server  → node %s/dist/index.js\n" "$AST_GREP_DIR"
    printf "  • fdep-mcp-server      → python3 -m fdep_mcp\n"
    echo ""
    printf "${DIM}Configured for:${RESET} %s (scope: %s)\n" "$targets" "$scope"
    echo ""
    printf "${DIM}Verify with:${RESET}\n"
    printf "  npx @modelcontextprotocol/inspector --cli --method tools/list node %s/dist/index.js\n" "$AST_GREP_DIR"
    printf "  PYTHONPATH=%s npx @modelcontextprotocol/inspector --cli --method tools/list python3 -m fdep_mcp\n" "$FDEP_DIR"
    echo ""
}

# ─── Usage ───────────────────────────────────────────────────────────────────

usage() {
    cat <<EOF
${BOLD}MCP Server Installer${RESET} — ast-grep + fdep for AI coding tools

${BOLD}Usage:${RESET}
  $(basename "$0") [options]

${BOLD}Options:${RESET}
  --targets <list>   Comma-separated targets (default: all)
                     Values: claude, codex, opencode, cline, copilot, all
  --scope <scope>    project = write to repo dir (default)
                     global  = write to ~/
  --skip-build       Skip dependency installation and build steps
  --dry-run          Preview what would be written
  -h, --help         Show this help

${BOLD}Examples:${RESET}
  $(basename "$0")                                  # install all, project scope
  $(basename "$0") --targets claude,copilot         # only Claude Code + Copilot
  $(basename "$0") --scope global                   # write to home directory configs
  $(basename "$0") --dry-run                        # preview changes
  $(basename "$0") --targets codex --skip-build     # codex only, skip build

${BOLD}Config file reference:${RESET}
  Claude Code (project)  .mcp.json                            key: mcpServers
  Claude Code (global)   ~/.claude.json                       key: mcpServers
  Codex (project)        .codex/config.toml                   key: [mcp_servers.NAME]
  Codex (global)         ~/.codex/config.toml                 key: [mcp_servers.NAME]
  OpenCode (project)     opencode.json                        key: mcp
  OpenCode (global)      ~/.config/opencode/opencode.json     key: mcp
  Cline (project)        .vscode/cline_mcp_settings.json      key: mcpServers
  Cline (global)         <vscode-storage>/cline_mcp_settings  key: mcpServers
  Copilot (project)      .vscode/mcp.json                     key: servers
  Copilot (global)       <vscode-settings>/settings.json      key: mcp.servers
EOF
}

# ─── Main ────────────────────────────────────────────────────────────────────

main() {
    local targets="all"
    local scope="project"
    local skip_build=false
    local dry_run=false

    while [ $# -gt 0 ]; do
        case "$1" in
            --targets)
                [ -z "${2:-}" ] && { error "--targets requires a value"; exit 1; }
                targets="$2"; shift ;;
            --scope)
                [ -z "${2:-}" ] && { error "--scope requires a value"; exit 1; }
                scope="$2"; shift ;;
            --skip-build) skip_build=true ;;
            --dry-run)    dry_run=true ;;
            -h|--help)    usage; exit 0 ;;
            *) error "Unknown option: $1"; usage >&2; exit 1 ;;
        esac
        shift
    done

    if [[ "$scope" != "project" && "$scope" != "global" ]]; then
        error "--scope must be 'project' or 'global'"
        exit 1
    fi

    header "MCP Server Installer"
    info "Targets: ${targets}"
    info "Scope: ${scope}"
    [ "$dry_run" = true ] && warn "DRY RUN — no files will be modified"

    # Prerequisites
    check_prereqs

    # Build
    if [ "$skip_build" = false ] && [ "$dry_run" = false ]; then
        build_ast_grep
        build_fdep
    else
        if [ "$skip_build" = true ]; then
            info "Skipping build (--skip-build)"
        fi
        # Verify dist exists even if skipping build
        if [ ! -f "${AST_GREP_DIR}/dist/index.js" ]; then
            error "ast-grep-mcp-server not built. Run: npm --prefix ${AST_GREP_DIR} install && npm --prefix ${AST_GREP_DIR} run build"
            exit 1
        fi
    fi

    # Parse targets
    local target_list
    if [ "$targets" = "all" ]; then
        target_list="claude codex opencode cline copilot"
    else
        target_list="${targets//,/ }"
    fi

    # Install per target
    for target in $target_list; do
        case "$target" in
            claude)   install_claude_code "$scope" "$dry_run" ;;
            codex)    install_codex "$scope" "$dry_run" ;;
            opencode) install_opencode "$scope" "$dry_run" ;;
            cline)    install_cline "$scope" "$dry_run" ;;
            copilot)  install_copilot "$scope" "$dry_run" ;;
            *) error "Unknown target: ${target} (valid: claude, codex, opencode, cline, copilot, all)"; exit 1 ;;
        esac
    done

    # Summary
    if [ "$dry_run" = false ]; then
        print_summary "$targets" "$scope"
    else
        header "Dry run complete — no files modified"
    fi
}

main "$@"
