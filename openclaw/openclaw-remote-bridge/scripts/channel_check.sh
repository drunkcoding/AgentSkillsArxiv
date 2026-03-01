#!/usr/bin/env bash
# Verify that an OpenClaw channel is connected and reachable.
# Usage: channel_check.sh <channel>
# Exit 0 = connected, Exit 1 = not connected or error

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: channel_check.sh <channel>" >&2
    exit 2
fi

CHANNEL="$1"

if ! command -v openclaw &>/dev/null; then
    echo "Error: openclaw CLI not found" >&2
    exit 1
fi

if openclaw channels status --probe 2>/dev/null | grep -qi "${CHANNEL}.*connected"; then
    echo "OK: ${CHANNEL} is connected"
    exit 0
else
    echo "Error: ${CHANNEL} is not connected" >&2
    exit 1
fi
