"""Plugin configuration — defaults overridable via env vars or CLI flags."""

from __future__ import annotations

import os
# TickTick
TICKTICK_PROJECT = os.environ.get("DISPATCH_PROJECT", "🤖 CodeDispatch")
TICKTICK_REGION = os.environ.get("TICKTICK_REGION", "cn")  # "cn" (dida365.com) or "intl" (ticktick.com)
TICKTICK_CRED_PATH = os.path.expanduser(
    os.environ.get(
        "TICKTICK_CRED_PATH",
        "~/.clawdbot/credentials/ticktick-cli/config.json",
    )
)

# API base URLs per region
TICKTICK_API_BASES = {
    "intl": "https://api.ticktick.com/open/v1",
    "cn": "https://api.dida365.com/open/v1",
}
TICKTICK_OAUTH_BASES = {
    "intl": "https://ticktick.com/oauth",
    "cn": "https://dida365.com/oauth",
}

# Polling
POLL_INTERVAL = int(os.environ.get("DISPATCH_POLL_INTERVAL", "60"))
MAX_CONCURRENT = int(os.environ.get("DISPATCH_MAX_CONCURRENT", "3"))

# SSH / remote opencode
SSH_RETRY_MAX = int(os.environ.get("DISPATCH_SSH_RETRY_MAX", "3"))
SSH_RETRY_DELAY = int(os.environ.get("DISPATCH_SSH_RETRY_DELAY", "5"))
HEALTH_CHECK_TIMEOUT = int(os.environ.get("DISPATCH_HEALTH_TIMEOUT", "30"))
REMOTE_PORT_MIN = 10000
REMOTE_PORT_MAX = 60000

# State
STATE_PATH = os.path.expanduser(
    os.environ.get(
        "DISPATCH_STATE_PATH",
        "~/.openclaw/remote-dispatch-state.json",
    )
)

# Notification defaults
DEFAULT_CHANNEL = os.environ.get("DISPATCH_CHANNEL", "whatsapp")
NOTIFY_TARGET = os.environ.get("DISPATCH_NOTIFY_TARGET", "")

DISPATCH_PHASES = [
    "Validate host & folder",
    "Launch opencode serve",
    "Create session",
    "Send prompt to agent",
    "Monitor events",
    "Validate completion",
    "Collect results",
    "Mark complete",
]

# ---------------------------------------------------------------------------
# Enhancement E1: Stuck / loop detection
# ---------------------------------------------------------------------------
STUCK_WINDOW_SIZE = int(os.environ.get("DISPATCH_STUCK_WINDOW", "20"))
STUCK_REPEAT_THRESHOLD = int(os.environ.get("DISPATCH_STUCK_THRESHOLD", "3"))
STUCK_JITTER_SIMILARITY = float(os.environ.get("DISPATCH_STUCK_JITTER_SIM", "0.85"))

# ---------------------------------------------------------------------------
# Enhancement E2: Plan gate
# ---------------------------------------------------------------------------
PLAN_GATE_TIMEOUT = int(os.environ.get("DISPATCH_PLAN_GATE_TIMEOUT", "1800"))  # 30 min auto-approve
PLAN_GATE_ENABLED = os.environ.get("DISPATCH_PLAN_GATE_ENABLED", "1") == "1"

# ---------------------------------------------------------------------------
# Enhancement E3: Intent / agent routing (keyword-based)
# ---------------------------------------------------------------------------
DEFAULT_AGENT = os.environ.get("DISPATCH_DEFAULT_AGENT", "build")

# ---------------------------------------------------------------------------
# Enhancement E5: LLM fallback chain for session matching
# ---------------------------------------------------------------------------
LLM_PROVIDERS = os.environ.get(
    "DISPATCH_LLM_PROVIDERS",
    "anthropic:claude-haiku-4-5,openai:gpt-5.1,openai:gpt-4o",
)
LLM_TIMEOUT = int(os.environ.get("DISPATCH_LLM_TIMEOUT", "5"))
LLM_CIRCUIT_FAIL_THRESHOLD = int(os.environ.get("DISPATCH_LLM_CIRCUIT_FAILS", "3"))
LLM_CIRCUIT_COOLDOWN = int(os.environ.get("DISPATCH_LLM_CIRCUIT_COOLDOWN", "600"))  # 10 min

# Session matching thresholds
SESSION_FORK_THRESHOLD = float(os.environ.get("DISPATCH_SESSION_FORK_THRESHOLD", "0.78"))
SESSION_NEW_THRESHOLD = float(os.environ.get("DISPATCH_SESSION_NEW_THRESHOLD", "0.35"))

# ---------------------------------------------------------------------------
# Enhancement E4 / E6: Session registry & graph
# ---------------------------------------------------------------------------
SESSION_REGISTRY_PATH = os.path.expanduser(
    os.environ.get(
        "DISPATCH_SESSION_REGISTRY_PATH",
        "~/.openclaw/session-registry.json",
    )
)
SESSION_GRAPH_PATH = os.path.expanduser(
    os.environ.get(
        "DISPATCH_SESSION_GRAPH_PATH",
        "~/.openclaw/session-graph.json",
    )
)
