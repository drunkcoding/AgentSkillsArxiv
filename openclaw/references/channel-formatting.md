# Per-Channel Message Limits and Formatting

## Character Limits

| Channel   | Max chars | Notes                           |
|-----------|----------:|----------------------------------|
| WhatsApp  |     4,096 | Bold: `*text*`, italic: `_text_`, monospace: `` `code` ``, no headings |
| Discord   |     2,000 | Full Markdown, code blocks with syntax highlighting |
| Telegram  |     4,096 | Bold: `**text**`, code blocks supported, HTML alternative |
| Slack     |     4,000 | mrkdwn: `*bold*`, `_italic_`, `` `code` ``, code blocks |
| Signal    |     6,000 | Bold: `**text**`, minimal formatting |
| iMessage  |    20,000 | No formatting — plain text only  |
| SMS       |     1,600 | Plain text, may be split by carrier at 160-char segments |

## Markdown Support Matrix

| Feature        | WhatsApp | Discord | Telegram | Slack |
|----------------|:--------:|:-------:|:--------:|:-----:|
| Bold           | *        | **      | **       | *     |
| Italic         | _        | *       | __       | _     |
| Inline code    | ```      | `       | `        | `     |
| Code blocks    | ```      | ```     | ```      | ```   |
| Syntax highlight | No     | Yes     | No       | No    |
| Headings       | No       | Yes     | No       | No    |
| Links          | Auto     | [t](u)  | [t](u)   | <u\|t>|
| Lists          | Manual   | Yes     | No       | Yes   |

## Code Block Handling

Claude Code responses often include code blocks. The `format_response.py` splitter:

1. **Never splits mid-code-block** — if a fence is open at the split point, backs up to before it
2. **Preserves fence markers** — triple backticks pass through to channels that support them
3. **No stripping** — channels that don't render fences still show them as visual delimiters

## Continuation Markers

When a response is split into multiple messages:

- Last line of each part (except final): `_(continued…)_`
- First line of each part (except first): `_(…continued)_`

This helps users follow multi-part responses across the conversation.
