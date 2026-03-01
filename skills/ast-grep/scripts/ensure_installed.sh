#!/usr/bin/env bash
# Ensure ast-grep is installed and available on PATH.
# Primary method: pip (Python environment assumed available).
# Fallbacks: cargo, npm.

set -euo pipefail

check_installed() {
    if command -v ast-grep &>/dev/null; then
        echo "✓ ast-grep $(ast-grep --version 2>/dev/null || echo '(version unknown)') is available"
        return 0
    fi
    return 1
}

# Already installed?
if check_installed; then
    exit 0
fi

echo "ast-grep not found. Installing..."

# Method 1: pip
if command -v pip3 &>/dev/null || command -v pip &>/dev/null; then
    PIP=$(command -v pip3 || command -v pip)
    echo "→ Installing via pip..."
    "$PIP" install ast-grep-cli --quiet 2>&1
    if check_installed; then
        exit 0
    fi
    echo "⚠ pip install succeeded but ast-grep not on PATH. Check ~/.local/bin"
fi

# Method 2: cargo
if command -v cargo &>/dev/null; then
    echo "→ Installing via cargo..."
    cargo install ast-grep --locked 2>&1
    if check_installed; then
        exit 0
    fi
fi

# Method 3: npm
if command -v npm &>/dev/null; then
    echo "→ Installing via npm..."
    npm install -g @ast-grep/cli 2>&1
    if check_installed; then
        exit 0
    fi
fi

echo "✗ Failed to install ast-grep automatically."
echo ""
echo "Manual installation options:"
echo "  pip install ast-grep-cli"
echo "  cargo install ast-grep --locked"
echo "  npm install -g @ast-grep/cli"
echo "  brew install ast-grep          (macOS)"
echo ""
echo "See https://ast-grep.github.io/guide/quick-start.html"
exit 1
