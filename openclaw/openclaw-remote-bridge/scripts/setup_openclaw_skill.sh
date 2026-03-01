#!/usr/bin/env bash
# Install the Claude Code bridge skill into OpenClaw's workspace.
#
# Prerequisites: openclaw CLI and claude CLI must be installed.
# Creates ~/.openclaw/workspace/skills/claude-code-bridge/SKILL.md
# with the bridge script path substituted into the template.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="${SCRIPT_DIR}/.."
TEMPLATE="${SKILL_DIR}/assets/openclaw-skill-template.md"
BRIDGE_SCRIPT="${SCRIPT_DIR}/bridge.py"
TARGET_DIR="${HOME}/.openclaw/workspace/skills/claude-code-bridge"

# --- Check prerequisites ---

if ! command -v openclaw &>/dev/null; then
    echo "Error: openclaw CLI not found. Install it first:" >&2
    echo "  https://docs.openclaw.ai/installation" >&2
    exit 1
fi

if ! command -v claude &>/dev/null; then
    echo "Error: claude CLI not found. Install Claude Code first:" >&2
    echo "  npm install -g @anthropic-ai/claude-code" >&2
    exit 1
fi

if [ ! -f "$TEMPLATE" ]; then
    echo "Error: Template not found at ${TEMPLATE}" >&2
    exit 1
fi

# --- Install ---

mkdir -p "$TARGET_DIR"

# Substitute bridge script path and write SKILL.md
sed "s|{{BRIDGE_SCRIPT_PATH}}|${BRIDGE_SCRIPT}|g" "$TEMPLATE" > "${TARGET_DIR}/SKILL.md"

echo "Installed Claude Code bridge skill to: ${TARGET_DIR}"
echo ""
echo "Next steps:"
echo "  1. Verify: openclaw skills list"
echo "  2. Pair a channel: openclaw channels pair <channel>"
echo "  3. Send a test message through the paired channel"
