#!/usr/bin/env bash
set -euo pipefail

# ─── Constants ────────────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DEFAULT_TARGET_BASE="${HOME}/.claude"
VALIDATE_SCRIPT="${REPO_ROOT}/skills/community-skills/skills/skill-creator/scripts/quick_validate.py"
SUBMODULE_SKILLS_DIR="${REPO_ROOT}/skills/community-skills/skills"
LOCAL_SKILL_ROOTS=("skills" "openclaw")

# ─── Output helpers (color-aware) ─────────────────────────────────────────────

if [ -t 1 ]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'
    BLUE='\033[0;34m'; BOLD='\033[1m'; RESET='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; BLUE=''; BOLD=''; RESET=''
fi

info()    { printf "${BLUE}info:${RESET} %s\n" "$*"; }
success() { printf "${GREEN}ok:${RESET} %s\n" "$*"; }
warn()    { printf "${YELLOW}warn:${RESET} %s\n" "$*" >&2; }
error()   { printf "${RED}error:${RESET} %s\n" "$*" >&2; }

# ─── Install name resolution ──────────────────────────────────────────────────
#
# Direct skills:   skills/academic-rebuttal         → academic-rebuttal
# Upstream skills: skills/sglang/add-jit-kernel     → sglang-add-jit-kernel
# OpenClaw:        openclaw/openclaw-remote-bridge   → openclaw-remote-bridge
# Community:       skills/community-skills/skills/X  → X

get_install_name() {
    local skill_dir="$1"
    local parts
    IFS='/' read -ra parts <<< "$skill_dir"
    local nparts=${#parts[@]}

    if [ "$nparts" -ge 3 ] && [ "${parts[1]}" != "community-skills" ]; then
        # Nested upstream skill: prefix with parent dir to avoid collisions
        echo "${parts[$((nparts-2))]}-${parts[$((nparts-1))]}"
    else
        echo "${parts[$((nparts-1))]}"
    fi
}

# ─── Skill discovery ─────────────────────────────────────────────────────────

discover_skills() {
    local skills=()
    local skill_root
    for skill_root in "${LOCAL_SKILL_ROOTS[@]}"; do
        [ -d "${REPO_ROOT}/${skill_root}" ] || continue
        for dir in "${REPO_ROOT}/${skill_root}"/*/; do
            [ -d "$dir" ] || continue
            local name
            name="$(basename "$dir")"
            [[ "$name" == .* ]] && continue
            if [ -f "${dir}SKILL.md" ]; then
                # Direct skill (e.g. skills/academic-rebuttal/)
                skills+=("${skill_root}/${name}")
            else
                # Check for nested upstream skills (e.g. skills/sglang/add-jit-kernel/)
                for subdir in "${dir}"*/; do
                    [ -d "$subdir" ] || continue
                    local subname
                    subname="$(basename "$subdir")"
                    [[ "$subname" == .* ]] && continue
                    [ -f "${subdir}SKILL.md" ] || continue
                    skills+=("${skill_root}/${name}/${subname}")
                done
            fi
        done
    done
    # Collect local install names for deduplication against community skills
    local local_names=()
    for s in "${skills[@]}"; do
        local_names+=("$(get_install_name "$s")")
    done
    # Submodule skills (skills/community-skills/skills/*)
    if [ -d "$SUBMODULE_SKILLS_DIR" ]; then
        for dir in "${SUBMODULE_SKILLS_DIR}"/*/; do
            [ -d "$dir" ] || continue
            local name
            name="$(basename "$dir")"
            [[ "$name" == .* ]] && continue
            [ -f "${dir}SKILL.md" ] || continue
            # Skip if a local skill with the same name exists (local takes precedence)
            local duplicate=false
            for ln in "${local_names[@]}"; do
                if [ "$ln" = "$name" ]; then duplicate=true; break; fi
            done
            $duplicate && continue
            skills+=("skills/community-skills/skills/${name}")
        done
    fi
    printf '%s\n' "${skills[@]}"
}

# ─── Frontmatter parsing (pure Bash) ─────────────────────────────────────────

get_frontmatter_field() {
    local skill_dir="$1" field="$2"
    local skill_md="${REPO_ROOT}/${skill_dir}/SKILL.md"
    [ -f "$skill_md" ] || return 1
    local in_frontmatter=false
    while IFS= read -r line; do
        if [ "$line" = "---" ]; then
            if $in_frontmatter; then break; fi
            in_frontmatter=true
            continue
        fi
        if $in_frontmatter; then
            # Match "field: value" or "field: "value""
            if [[ "$line" =~ ^${field}:[[:space:]]*(.*) ]]; then
                local val="${BASH_REMATCH[1]}"
                # Strip surrounding quotes
                val="${val#\"}" ; val="${val%\"}"
                val="${val#\'}" ; val="${val%\'}"
                printf '%s' "$val"
                return 0
            fi
        fi
    done < "$skill_md"
    return 1
}

get_skill_name() { get_frontmatter_field "$1" "name"; }
get_skill_description() { get_frontmatter_field "$1" "description"; }

# ─── Validation ───────────────────────────────────────────────────────────────

validate_skill() {
    local skill_dir="$1"
    local skill_path="${REPO_ROOT}/${skill_dir}"

    # Try Python validator first
    if command -v python3 &>/dev/null && python3 -c "import yaml" &>/dev/null; then
        if [ -f "$VALIDATE_SCRIPT" ]; then
            local output
            if output=$(python3 "$VALIDATE_SCRIPT" "$skill_path" 2>&1); then
                success "${skill_dir}: ${output}"
                return 0
            else
                error "${skill_dir}: ${output}"
                return 1
            fi
        fi
    fi

    # Fallback: pure-Bash validation
    local skill_md="${skill_path}/SKILL.md"
    if [ ! -f "$skill_md" ]; then
        error "${skill_dir}: SKILL.md not found"
        return 1
    fi

    local first_line
    first_line=$(head -1 "$skill_md")
    if [ "$first_line" != "---" ]; then
        error "${skill_dir}: no YAML frontmatter found"
        return 1
    fi

    local name desc
    name=$(get_skill_name "$skill_dir" 2>/dev/null) || true
    desc=$(get_skill_description "$skill_dir" 2>/dev/null) || true

    if [ -z "$name" ]; then
        error "${skill_dir}: missing 'name' in frontmatter"
        return 1
    fi
    if [ -z "$desc" ]; then
        error "${skill_dir}: missing 'description' in frontmatter"
        return 1
    fi

    success "${skill_dir}: Skill is valid! (bash fallback)"
    return 0
}

# ─── Install / Uninstall ─────────────────────────────────────────────────────

install_skill() {
    local skill_dir="$1" target_base="$2" dry_run="$3" force="$4"
    local source="${REPO_ROOT}/${skill_dir}"
    local install_name
    install_name="$(get_install_name "$skill_dir")"
    local target="${target_base}/${install_name}"

    if [ -L "$target" ]; then
        local existing
        existing=$(readlink -f "$target" 2>/dev/null || readlink "$target")
        local source_resolved
        source_resolved=$(readlink -f "$source" 2>/dev/null || echo "$source")
        if [ "$existing" = "$source_resolved" ]; then
            info "${skill_dir}: already installed (same symlink), skipping"
            return 0
        fi
        if [ "$force" = "true" ]; then
            warn "${skill_dir}: overwriting existing symlink -> ${existing}"
            if [ "$dry_run" = "true" ]; then
                info "[dry-run] would remove ${target} and link to ${source}"
                return 0
            fi
            rm "$target"
        else
            warn "${skill_dir}: symlink already exists -> ${existing}"
            printf "  Overwrite? [y/N] "
            local answer
            read -r answer
            case "$answer" in
                [yY]*) rm "$target" ;;
                *)     info "skipped ${skill_dir}"; return 0 ;;
            esac
        fi
    elif [ -e "$target" ]; then
        if [ "$force" = "true" ]; then
            warn "${skill_dir}: overwriting existing path ${target}"
            if [ "$dry_run" = "true" ]; then
                info "[dry-run] would remove ${target} and link to ${source}"
                return 0
            fi
            rm -rf "$target"
        else
            warn "${skill_dir}: ${target} already exists (not a symlink)"
            printf "  Overwrite? [y/N] "
            local answer
            read -r answer
            case "$answer" in
                [yY]*) rm -rf "$target" ;;
                *)     info "skipped ${skill_dir}"; return 0 ;;
            esac
        fi
    fi

    if [ "$dry_run" = "true" ]; then
        info "[dry-run] would link ${target} -> ${source}"
        return 0
    fi

    mkdir -p "$target_base"
    ln -s "$source" "$target"
    success "${skill_dir}: installed -> ${target}"
}

uninstall_skill() {
    local skill_dir="$1" target_base="$2" dry_run="$3"
    local install_name
    install_name="$(get_install_name "$skill_dir")"
    local target="${target_base}/${install_name}"

    if [ ! -L "$target" ]; then
        if [ -e "$target" ]; then
            warn "${skill_dir}: ${target} exists but is not a symlink, skipping for safety"
        else
            info "${skill_dir}: not installed"
        fi
        return 0
    fi

    # Safety: only remove if symlink points back into this repo
    local link_target
    link_target=$(readlink -f "$target" 2>/dev/null || readlink "$target")
    local repo_resolved
    repo_resolved=$(readlink -f "$REPO_ROOT" 2>/dev/null || echo "$REPO_ROOT")
    if [[ "$link_target" != "${repo_resolved}"* ]]; then
        warn "${skill_dir}: symlink points outside this repo (${link_target}), skipping for safety"
        return 0
    fi

    if [ "$dry_run" = "true" ]; then
        info "[dry-run] would remove symlink ${target}"
        return 0
    fi

    rm "$target"
    success "${skill_dir}: uninstalled (removed ${target})"
}

# ─── List skills ──────────────────────────────────────────────────────────────

list_skills() {
    local target_base="$1"
    local skills
    mapfile -t skills < <(discover_skills)

    if [ ${#skills[@]} -eq 0 ]; then
        warn "no skills found in ${REPO_ROOT}"
        return 0
    fi

    printf "\n${BOLD}%-58s %-24s %-16s %s${RESET}\n" "DIRECTORY" "NAME" "STATUS" "DESCRIPTION"
    printf "%-58s %-24s %-16s %s\n" "─────────" "────" "──────" "───────────"

    for skill_dir in "${skills[@]}"; do
        local name desc status
        name=$(get_skill_name "$skill_dir" 2>/dev/null) || name="(unknown)"
        desc=$(get_skill_description "$skill_dir" 2>/dev/null) || desc=""
        # Truncate description for display
        if [ ${#desc} -gt 60 ]; then
            desc="${desc:0:57}..."
        fi

        local install_name
        install_name="$(get_install_name "$skill_dir")"
        local target="${target_base}/${install_name}"
        if [ -L "$target" ]; then
            local link_target
            link_target=$(readlink -f "$target" 2>/dev/null || readlink "$target")
            local source_resolved
            source_resolved=$(readlink -f "${REPO_ROOT}/${skill_dir}" 2>/dev/null || echo "${REPO_ROOT}/${skill_dir}")
            if [ "$link_target" = "$source_resolved" ]; then
                status="${GREEN}installed${RESET}"
            else
                status="${YELLOW}conflict${RESET}"
            fi
        elif [ -e "$target" ]; then
            status="${YELLOW}conflict${RESET}"
        else
            status="not installed"
        fi

        printf "%-58s %-24s %-16b %s\n" "$skill_dir" "$name" "$status" "$desc"
    done
    echo
}

# ─── Interactive selection ────────────────────────────────────────────────────

select_skills() {
    local -n result=$1
    shift
    local skills=("$@")

    echo
    for i in "${!skills[@]}"; do
        local name
        name=$(get_skill_name "${skills[$i]}" 2>/dev/null) || name=""
        printf "  %d) %s" "$((i + 1))" "${skills[$i]}"
        [ -n "$name" ] && printf " (%s)" "$name"
        echo
    done
    echo

    printf "Select skills (e.g. 1,3 or 'all'): "
    local input
    read -r input

    if [ "$input" = "all" ]; then
        result=("${skills[@]}")
        return 0
    fi

    result=()
    IFS=',' read -ra tokens <<< "$input"
    for token in "${tokens[@]}"; do
        token="$(echo "$token" | tr -d ' ')"
        if [[ "$token" =~ ^[0-9]+$ ]] && [ "$token" -ge 1 ] && [ "$token" -le "${#skills[@]}" ]; then
            result+=("${skills[$((token - 1))]}")
        else
            warn "ignoring invalid selection: ${token}"
        fi
    done

    if [ ${#result[@]} -eq 0 ]; then
        info "no skills selected"
        return 1
    fi
}

# ─── Commands ─────────────────────────────────────────────────────────────────

cmd_install() {
    local target_base="$1" select_all="$2" force="$3" dry_run="$4"

    local all_skills
    mapfile -t all_skills < <(discover_skills)
    if [ ${#all_skills[@]} -eq 0 ]; then
        error "no skills found in ${REPO_ROOT}"
        return 1
    fi

    # Validate all first
    info "validating skills..."
    local valid_skills=()
    for skill_dir in "${all_skills[@]}"; do
        if validate_skill "$skill_dir"; then
            valid_skills+=("$skill_dir")
        fi
    done

    if [ ${#valid_skills[@]} -eq 0 ]; then
        error "no valid skills to install"
        return 1
    fi

    echo
    info "${#valid_skills[@]} of ${#all_skills[@]} skills passed validation"

    # Select skills
    local selected=()
    if [ "$select_all" = "true" ]; then
        selected=("${valid_skills[@]}")
    else
        if ! select_skills selected "${valid_skills[@]}"; then
            return 0
        fi
    fi

    # Install
    echo
    info "installing ${#selected[@]} skill(s) to ${target_base}/"
    for skill_dir in "${selected[@]}"; do
        install_skill "$skill_dir" "$target_base" "$dry_run" "$force"
    done
}

cmd_uninstall() {
    local target_base="$1" select_all="$2" dry_run="$3"

    local all_skills
    mapfile -t all_skills < <(discover_skills)
    if [ ${#all_skills[@]} -eq 0 ]; then
        error "no skills found in ${REPO_ROOT}"
        return 1
    fi

    # Find installed skills
    local installed=()
    for skill_dir in "${all_skills[@]}"; do
        local install_name
        install_name="$(get_install_name "$skill_dir")"
        local target="${target_base}/${install_name}"
        if [ -L "$target" ]; then
            installed+=("$skill_dir")
        fi
    done

    if [ ${#installed[@]} -eq 0 ]; then
        info "no skills are currently installed in ${target_base}"
        return 0
    fi

    local selected=()
    if [ "$select_all" = "true" ]; then
        selected=("${installed[@]}")
    else
        echo
        info "installed skills:"
        if ! select_skills selected "${installed[@]}"; then
            return 0
        fi
    fi

    echo
    info "uninstalling ${#selected[@]} skill(s) from ${target_base}/"
    for skill_dir in "${selected[@]}"; do
        uninstall_skill "$skill_dir" "$target_base" "$dry_run"
    done
}

cmd_validate() {
    local all_skills
    mapfile -t all_skills < <(discover_skills)
    if [ ${#all_skills[@]} -eq 0 ]; then
        error "no skills found in ${REPO_ROOT}"
        return 1
    fi

    info "validating ${#all_skills[@]} skill(s)..."
    echo
    local passed=0 failed=0
    for skill_dir in "${all_skills[@]}"; do
        if validate_skill "$skill_dir"; then
            passed=$((passed + 1))
        else
            failed=$((failed + 1))
        fi
    done

    echo
    info "results: ${passed} passed, ${failed} failed (${#all_skills[@]} total)"
    [ "$failed" -eq 0 ]
}

# ─── Usage ────────────────────────────────────────────────────────────────────

usage() {
    cat <<EOF
Usage: $(basename "$0") [command] [options]

Commands:
  install      Validate and symlink skills (default)
  uninstall    Remove symlinks installed by this script
  list         Show skills and their install status
  validate     Validate all skills without installing

Options:
  --target <path>     Target <path>/skills/ (default: ~/.claude)
  --all               Skip interactive selection
  --force             Overwrite existing symlinks without prompting
  --dry-run           Preview changes without modifying anything
  -h, --help          Show this help

Examples:
  $(basename "$0")                                       # interactive install to ~/.claude/skills/
  $(basename "$0") install --all                         # install all skills
  $(basename "$0") install --all --dry-run               # preview install
  $(basename "$0") install --target ~/.cline --all       # install to ~/.cline/skills/
  $(basename "$0") list                                  # show skill status
  $(basename "$0") validate                              # validate all skills
  $(basename "$0") uninstall --all                       # remove all symlinks

Community skills (git submodule):
  git submodule update --init                            # fetch community skills
  Skills from skills/community-skills/skills/ are auto-discovered.
  Local skills take precedence over community skills with the same name.
EOF
}

# ─── Argument parsing & main ─────────────────────────────────────────────────

main() {
    local command="install"
    local target_base="$DEFAULT_TARGET_BASE"
    local select_all=false
    local force=false
    local dry_run=false

    # Warn if submodule is not initialized
    if [ -f "${REPO_ROOT}/.gitmodules" ] && [ ! -d "$SUBMODULE_SKILLS_DIR" ]; then
        warn "community-skills submodule not initialized; run: git submodule update --init"
    fi

    # Parse arguments
    local positional_set=false
    while [ $# -gt 0 ]; do
        case "$1" in
            install|uninstall|list|validate)
                if ! $positional_set; then
                    command="$1"
                    positional_set=true
                else
                    error "unexpected argument: $1"
                    usage >&2
                    return 1
                fi
                ;;
            --target)
                if [ -z "${2:-}" ]; then
                    error "--target requires a path argument"
                    return 1
                fi
                if [ ! -d "$2" ]; then
                    error "target path does not exist: $2"
                    return 1
                fi
                target_base="$2"
                shift
                ;;
            --all)
                select_all=true
                ;;
            --force)
                force=true
                ;;
            --dry-run)
                dry_run=true
                ;;
            -h|--help)
                usage
                return 0
                ;;
            *)
                error "unknown option: $1"
                usage >&2
                return 1
                ;;
        esac
        shift
    done

    # Resolve target to skills subdirectory
    target_base="${target_base}/skills"
    if [ ! -d "$target_base" ]; then
        mkdir -p "$target_base"
    fi

    case "$command" in
        install)   cmd_install "$target_base" "$select_all" "$force" "$dry_run" ;;
        uninstall) cmd_uninstall "$target_base" "$select_all" "$dry_run" ;;
        list)      list_skills "$target_base" ;;
        validate)  cmd_validate ;;
    esac
}

main "$@"
