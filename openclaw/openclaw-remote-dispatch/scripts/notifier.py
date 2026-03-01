"""WhatsApp / channel notifications via openclaw CLI."""

from __future__ import annotations

import json
import logging
import re
import shutil
import subprocess

from config import DEFAULT_CHANNEL

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Message chunking (adapted from openclaw-remote-bridge format_response.py)
# ---------------------------------------------------------------------------

CHANNEL_LIMITS: dict[str, int] = {
    "whatsapp": 4096,
    "discord": 2000,
    "telegram": 4096,
    "slack": 4000,
    "signal": 6000,
    "imessage": 20000,
    "sms": 1600,
}
DEFAULT_LIMIT = 4000
CONT_FOOTER = "\n\n_(continued…)_"
CONT_HEADER = "_(…continued)_\n\n"


def _split_message(text: str, limit: int) -> list[str]:
    """Split long text into channel-appropriate chunks."""
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text
    is_first = True

    while remaining:
        if not is_first:
            remaining = CONT_HEADER + remaining

        effective = limit - len(CONT_FOOTER)
        if len(remaining) <= limit:
            chunks.append(remaining)
            break

        candidate = remaining[:effective]

        # Try paragraph, sentence, word boundary
        para = candidate.rfind("\n\n")
        if para > effective // 3:
            split_pos = para
        else:
            sentence = max(candidate.rfind(". "), candidate.rfind(".\n"))
            if sentence > effective // 3:
                split_pos = sentence + 1
            else:
                word = candidate.rfind(" ")
                split_pos = word if word > effective // 3 else effective

        chunk = remaining[:split_pos].rstrip()
        remaining = remaining[split_pos:].lstrip()
        if remaining:
            chunk += CONT_FOOTER
        chunks.append(chunk)
        is_first = False

    return chunks


# ---------------------------------------------------------------------------
# Notifier
# ---------------------------------------------------------------------------


class Notifier:
    """Send tagged notifications via 'openclaw message send'."""

    def __init__(self, to: str, channel: str = DEFAULT_CHANNEL) -> None:
        self.to = to
        self.channel = channel
        self._limit = CHANNEL_LIMITS.get(channel.lower(), DEFAULT_LIMIT)
        self._openclaw = shutil.which("openclaw")

    def _send(self, message: str) -> None:
        """Send a single message (auto-chunked if needed)."""
        if not self._openclaw:
            log.warning("openclaw CLI not found — printing notification instead")
            log.info("[NOTIFY → %s] %s", self.to, message)
            return

        for chunk in _split_message(message, self._limit):
            try:
                subprocess.run(
                    [
                        self._openclaw,
                        "message",
                        "send",
                        "--to",
                        self.to,
                        "--channel",
                        self.channel,
                        "--message",
                        chunk,
                    ],
                    capture_output=True,
                    timeout=30,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                log.error(
                    "openclaw send failed: %s",
                    e.stderr.decode(errors="replace") if e.stderr else str(e),
                )
            except subprocess.TimeoutExpired:
                log.error("openclaw send timed out")

    def _tag(self, emoji: str, host: str, folder: str) -> str:
        short_folder = folder.rsplit("/", 1)[-1] if "/" in folder else folder
        return f"[{emoji} {host}/{short_folder}]"

    def progress(self, host: str, folder: str, title: str, message: str) -> None:
        tag = self._tag("🔄", host, folder)
        self._send(f"{tag} *{title}*\n{message}")

    def question(self, host: str, folder: str, title: str, question: str) -> None:
        tag = self._tag("❓", host, folder)
        self._send(f"{tag} *{title}*\n{question}\n\n_Reply to answer the agent._")

    def done(self, host: str, folder: str, title: str, diff_summary: str) -> None:
        tag = self._tag("✅", host, folder)
        self._send(f"{tag} *{title}*\nDone. {diff_summary}")

    def failed(self, host: str, folder: str, title: str, reason: str) -> None:
        tag = self._tag("❌", host, folder)
        self._send(f"{tag} *{title}*\nFailed: {reason}")

    def blocked(self, host: str, folder: str, title: str, reason: str) -> None:
        tag = self._tag("⚠️", host, folder)
        self._send(f"{tag} *{title}*\n{reason}")

    def plan_approval(
        self,
        host: str,
        folder: str,
        title: str,
        plan_text: str,
        task_id: str,
    ) -> None:
        """Notify user that a plan needs approval."""
        tag = self._tag("📋", host, folder)
        truncated = plan_text[:2000] + ("…" if len(plan_text) > 2000 else "")
        self._send(
            f"{tag} *{title}*\n"
            f"Agent proposed a plan:\n\n{truncated}\n\n"
            f"Reply *approve {task_id[:8]}* to proceed or *reject {task_id[:8]}* to abort.\n"
            f"Auto-approves in 30 min."
        )

    def stuck_alert(
        self,
        host: str,
        folder: str,
        title: str,
        description: str,
        task_id: str,
    ) -> None:
        """Notify user that the agent appears stuck."""
        tag = self._tag("🔁", host, folder)
        self._send(
            f"{tag} *{title}*\n"
            f"Agent appears stuck: {description}\n\n"
            f"Reply *continue {task_id[:8]}* to let it keep going, "
            f"or *abort {task_id[:8]}* to stop."
        )

    def done_with_summary(
        self,
        host: str,
        folder: str,
        title: str,
        diff_summary: str,
        summary_bullets: list[str],
        session_id: str,
    ) -> None:
        """Enhanced done notification with summary bullets and fork info."""
        tag = self._tag("✅", host, folder)
        bullets = "\n".join(f"  • {b}" for b in summary_bullets[:10])
        msg = (
            f"{tag} *{title}*\n"
            f"Done. {diff_summary}\n"
        )
        if bullets:
            msg += f"\n{bullets}\n"
        if session_id:
            msg += f"\nSession: `{session_id}`  (reply *fork {session_id[:12]}* to continue)"
        self._send(msg)
