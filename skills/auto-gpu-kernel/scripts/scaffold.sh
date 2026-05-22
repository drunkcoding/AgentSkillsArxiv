#!/usr/bin/env bash
# Scaffold an auto-gpu-kernel project from the bundled template.
#
# Usage:
#   scaffold.sh <target-dir> [--kernel-name NAME] [--kernel-file FILE]
#
# Copies the template tree to <target-dir>, then leaves it for the user to
# customize CLAUDE.md (kernel name, I/O shapes, numerical hazards),
# config.toml (solution.name, definition, author, entry_point), and the
# kernel stub at solution/triton/<kernel-file>.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../assets/template"

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <target-dir> [--kernel-name NAME] [--kernel-file FILE]" >&2
    exit 1
fi

TARGET="$1"; shift
KERNEL_NAME=""
KERNEL_FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --kernel-name) KERNEL_NAME="$2"; shift 2 ;;
        --kernel-file) KERNEL_FILE="$2"; shift 2 ;;
        *) echo "unknown arg: $1" >&2; exit 1 ;;
    esac
done

if [[ -e "$TARGET" ]]; then
    echo "target already exists: $TARGET" >&2
    exit 1
fi

mkdir -p "$TARGET"
cp -r "$TEMPLATE_DIR"/. "$TARGET"/

# Optional in-place rename of the kernel file (template ships as sparse_fused.py).
if [[ -n "$KERNEL_FILE" && "$KERNEL_FILE" != "sparse_fused.py" ]]; then
    mv "$TARGET/solution/triton/sparse_fused.py" "$TARGET/solution/triton/$KERNEL_FILE"
    mv "$TARGET/solution/triton/sparse_baseline.py" "$TARGET/solution/triton/${KERNEL_FILE%.*}_baseline.py" 2>/dev/null || true
    sed -i "s|sparse_fused.py::kernel|$KERNEL_FILE::kernel|g" "$TARGET/config.toml"
fi

if [[ -n "$KERNEL_NAME" ]]; then
    sed -i "s|dsa_sparse_attention_h16_ckv512_kpe64_topk2048_ps64|$KERNEL_NAME|g" "$TARGET/config.toml"
fi

echo "Scaffolded: $TARGET"
echo "Next steps:"
echo "  1. Edit $TARGET/CLAUDE.md  — kernel description, I/O shapes, numerical hazards"
echo "  2. Edit $TARGET/config.toml — solution.name, definition, author"
echo "  3. Place PyTorch reference in solution/triton/<name>_baseline.py"
echo "  4. Implement (or stub) solution/triton/<entry>.py"
echo "  5. Run 'modal setup' and 'modal volume create flashinfer-trace' once"
echo "  6. Launch the loop: claude --dangerously-skip-permissions -p '/optimize'"
