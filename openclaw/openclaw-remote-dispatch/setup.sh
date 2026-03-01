#!/usr/bin/env bash
# Install openclaw-remote-dispatch skill into ~/.openclaw/workspace/skills/
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_NAME="openclaw-remote-dispatch"
TARGET_BASE="${OPENCLAW_SKILLS_DIR:-$HOME/.openclaw/workspace/skills}"
TARGET_DIR="${TARGET_BASE}/${SKILL_NAME}"

echo "Installing $SKILL_NAME skill..."
echo "  Source: $SCRIPT_DIR"
echo "  Target: $TARGET_DIR"

# Remove existing symlink or directory
if [ -L "$TARGET_DIR" ]; then
    rm "$TARGET_DIR"
    echo "  Removed existing symlink"
elif [ -d "$TARGET_DIR" ]; then
    echo "  WARNING: $TARGET_DIR is a real directory, not a symlink."
    echo "  Remove it manually if you want to replace it:"
    echo "    rm -rf $TARGET_DIR"
    exit 1
fi

# Create parent directory
mkdir -p "$(dirname "$TARGET_DIR")"

# Create symlink
ln -s "$SCRIPT_DIR" "$TARGET_DIR"
echo "  Symlinked: $TARGET_DIR -> $SCRIPT_DIR"

# Verify SKILL.md exists
if [ -f "$TARGET_DIR/SKILL.md" ]; then
    echo "  ✓ SKILL.md found"
else
    echo "  ✗ WARNING: SKILL.md not found in $TARGET_DIR"
fi

# Verify scripts directory
if [ -d "$TARGET_DIR/scripts" ]; then
    SCRIPT_COUNT=$(find "$TARGET_DIR/scripts" -name "*.py" -type f | wc -l)
    echo "  ✓ scripts/ directory found ($SCRIPT_COUNT Python files)"
else
    echo "  ✗ WARNING: scripts/ directory not found"
fi

# Check Python version
if command -v python3 &>/dev/null; then
    PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 10 ]; then
        echo "  ✓ Python $PY_VERSION (>= 3.10 required)"
    else
        echo "  ✗ WARNING: Python $PY_VERSION found, but >= 3.10 required"
    fi
else
    echo "  ✗ WARNING: python3 not found in PATH"
fi

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install --user rapidfuzz 2>/dev/null && echo "  ✓ rapidfuzz installed" || echo "  ⚠ rapidfuzz install failed (optional: stuck detection arg-jitter)"

# Check TickTick credentials
CRED_FILE="${TICKTICK_CRED_PATH:-$HOME/.clawdbot/credentials/ticktick-cli/config.json}"
if [ -f "$CRED_FILE" ]; then
    echo "  ✓ TickTick credentials found at $CRED_FILE"
else
    echo "  ⚠ TickTick credentials not found at $CRED_FILE"
    echo "    Run: bun run ~/.openclaw/skills/ticktick/scripts/ticktick.ts auth"
fi

# Check SSH config
if [ -f "$HOME/.ssh/config" ]; then
    HOST_COUNT=$(grep -c "^Host " "$HOME/.ssh/config" 2>/dev/null || echo "0")
    echo "  ✓ SSH config found ($HOST_COUNT host entries)"
else
    echo "  ⚠ No ~/.ssh/config found (needed for remote dispatch)"
fi

echo ""
echo "Installation complete."
echo ""
echo "Usage:"
echo "  # General TickTick CLI"
echo "  python $TARGET_DIR/scripts/ticktick_cli.py tasks --json"
echo "  python $TARGET_DIR/scripts/ticktick_cli.py task \"My task\" --list \"Work\""
echo ""
echo "  # Dispatch daemon"
echo "  python $TARGET_DIR/scripts/dispatcher.py --daemon --notify \"+1234567890\""
echo ""
echo "  # One-shot dispatch"
echo "  python $TARGET_DIR/scripts/dispatcher.py --notify \"+1234567890\" --dry-run"
