"""Plugin configuration — defaults overridable via env vars or CLI flags."""

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

# Dispatch checklist items (ticked off as stages complete)
DISPATCH_CHECKLIST = [
    "Validate remote host & folder",
    "Launch opencode serve via SSH",
    "Send prompt to agent",
    "Monitor progress",
    "Collect results & diff",
]
