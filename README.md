# AgentSkillsArxiv

Claude Code skills collection for academic research and development tooling.

## Skills

| Skill | Description |
|-------|-------------|
| `academic-reviewer` | Review systems conference papers (OSDI, NSDI, SIGCOMM, MOBICOM, SOSP) with structured HotCRP-style reviews, merit/confidence scoring, and constructive feedback |
| `academic-writing` | Write systems conference papers — covers paper structure, systems writing style, IEEE/ACM citations, architecture diagrams, and evaluation |
| `ast-grep` | AST-aware structural code search, rewriting, and linting via [ast-grep](https://ast-grep.github.io/) — for when text-based grep is too imprecise |
| `better-grep` | Fast text search with one-shot patterns that get files, lines, and context in a single call |
| `citation-convert` | Fetch BibTeX citations from DOI, arXiv ID, journal URL, or paper title |
| `conference-plot` | Publication-quality matplotlib figures for two-column conference papers (ACM, IEEE, USENIX) with colorblind-safe palettes and dual PDF+PNG output |
| `function-dep-search` | AST-accurate function dependency analysis using Tree-sitter — trace call chains, find callers/callees, detect unused functions across 8 languages |
| `openclaw-remote-bridge` | Bridge OpenClaw messaging channels (WhatsApp, Discord, Telegram, Slack) to Claude Code CLI |
| `openviking` | Context database reference for [OpenViking](https://github.com/openviking) — an open-source context database for AI agents |

## Community Skills

The `community-skills/` submodule includes Anthropic's official skill collection (pdf, docx, pptx, xlsx, and more). Initialize it with:

```bash
git submodule update --init
```

Local skills take precedence over community skills with the same name.

## Installation

`install.sh` validates and symlinks skills into `~/.claude/skills/`.

```bash
# Install all skills
./install.sh install --all

# Interactive selection
./install.sh install

# List skills and their install status
./install.sh list

# Validate all skills without installing
./install.sh validate

# Remove all installed symlinks
./install.sh uninstall --all

# Preview changes without modifying anything
./install.sh install --all --dry-run

# Install to a custom target
./install.sh install --target ~/.cline --all
```

## Repository Structure

```
AgentSkillsArxiv/
├── academic-reviewer/     # Paper review skill
├── academic-writing/      # Paper writing skill
├── ast-grep/              # Structural code search
├── better-grep/           # Fast text search
├── citation-convert/      # BibTeX fetcher
├── conference-plot/       # Publication figures
├── function-dep-search/   # Function dependency analysis
├── openclaw-remote-bridge/ # Messaging channel bridge
├── openviking/            # Context database reference
├── community-skills/      # Git submodule — Anthropic's official skills
└── install.sh             # Installer script
```
