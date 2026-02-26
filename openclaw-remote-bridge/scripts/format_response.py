#!/usr/bin/env python3
"""Split and format Claude Code responses for messaging-channel limits.

Standalone CLI:
    python3 format_response.py --channel whatsapp --text "long response..."
    → prints JSON array of message chunks
"""

import argparse
import json
import re
import sys

# Per-channel character limits
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
CONTINUATION_FOOTER = "\n\n_(continued…)_"
CONTINUATION_HEADER = "_(…continued)_\n\n"


def get_limit(channel: str) -> int:
    return CHANNEL_LIMITS.get(channel.lower(), DEFAULT_LIMIT)


def _find_open_code_block(text: str) -> str | None:
    """Return the fence marker (e.g. ```) if a code block is open at end of text."""
    fences = re.findall(r"^(`{3,})", text, re.MULTILINE)
    # Odd number of fences means one is unclosed
    if len(fences) % 2 == 1:
        return fences[-1]
    return None


def _split_at_boundary(text: str, limit: int) -> tuple[str, str]:
    """Split text at a paragraph or sentence boundary within limit.

    Priority: paragraph break > sentence end > word boundary > hard cut.
    Never splits inside a code block.
    """
    if len(text) <= limit:
        return text, ""

    # Reserve space for continuation markers
    effective = limit - len(CONTINUATION_FOOTER)

    candidate = text[:effective]

    # Check if we'd cut inside a code block
    open_fence = _find_open_code_block(candidate)
    if open_fence:
        # Back up to before the opening fence
        fence_pos = candidate.rfind(open_fence)
        if fence_pos > 0:
            candidate = candidate[:fence_pos]

    # Try paragraph boundary (double newline)
    para = candidate.rfind("\n\n")
    if para > effective // 3:
        split_pos = para
    else:
        # Try sentence boundary
        sentence = max(candidate.rfind(". "), candidate.rfind(".\n"))
        if sentence > effective // 3:
            split_pos = sentence + 1  # include the period
        else:
            # Try word boundary
            word = candidate.rfind(" ")
            if word > effective // 3:
                split_pos = word
            else:
                split_pos = effective

    first = text[:split_pos].rstrip()
    rest = text[split_pos:].lstrip()
    return first, rest


def split_response(text: str, channel: str) -> list[str]:
    """Split response into channel-appropriate chunks."""
    limit = get_limit(channel)

    if len(text) <= limit:
        return [text]

    chunks = []
    remaining = text
    is_first = True

    while remaining:
        if not is_first:
            remaining = CONTINUATION_HEADER + remaining
        chunk, remaining = _split_at_boundary(remaining, limit)
        if remaining:
            chunk += CONTINUATION_FOOTER
        chunks.append(chunk)
        is_first = False

    return chunks


def main() -> None:
    parser = argparse.ArgumentParser(description="Format Claude responses for messaging channels")
    parser.add_argument("--channel", required=True, help="Target channel (whatsapp, discord, ...)")
    parser.add_argument("--text", help="Response text (reads stdin if omitted)")
    args = parser.parse_args()

    text = args.text if args.text is not None else sys.stdin.read()
    chunks = split_response(text, args.channel)
    print(json.dumps(chunks, ensure_ascii=False))


if __name__ == "__main__":
    main()
