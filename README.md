# AgentSkillsArxiv

Claude Code skills and MCP tooling for academic research and development workflows.

## Local Skills

| Skill | Canonical Source Path | Description |
|-------|------------------------|-------------|
| `academic-grant-proposal` | `skills/academic-grant-proposal/` | Grant proposal writing for NSF, NIH, ERC, Horizon Europe, DARPA/DoD/DOE, UKRI — sections, budget, biosketch/DMP, review critique |
| `academic-rebuttal` | `skills/academic-rebuttal/` | Conference paper rebuttal writing — false impression taxonomy, venue constraints (HotCRP + OpenReview) |
| `academic-reviewer` | `skills/academic-reviewer/` | Structured systems-paper review workflow |
| `academic-writing` | `skills/academic-writing/` | Systems paper writing workflow |
| `ast-grep` | `skills/ast-grep/` | AST-aware structural search and rewrites |
| `better-grep` | `skills/better-grep/` | One-shot high-signal text search patterns |
| `citation-convert` | `skills/citation-convert/` | DOI/arXiv/title to BibTeX conversion |
| `conference-plot` | `skills/conference-plot/` | Publication-quality conference figures |
| `function-dep-search` | `skills/function-dep-search/` | AST-accurate function dependency tracing |
| `mem0` | `skills/mem0/` | Persistent memory integration patterns |
| `openviking` | `skills/openviking/` | OpenViking context database reference |
| `openclaw-remote-bridge` | `openclaw/openclaw-remote-bridge/` | OpenClaw channel bridge to Claude CLI |
| `openclaw-remote-dispatch` | `openclaw/openclaw-remote-dispatch/` | TickTick-driven remote code dispatch |

## Community Skills

The Anthropic community skills submodule is located at `skills/community-skills/`.

```bash
git submodule update --init
```

Community skill folders are discovered from `skills/community-skills/skills/`.
Local skills with the same name take precedence.

## Installation

Skill installer:

```bash
./infra/scripts/install-skills.sh list
./infra/scripts/install-skills.sh validate
./infra/scripts/install-skills.sh install --all
```

MCP installer:

```bash
./infra/scripts/install-mcp-servers.sh --help
```

## Repository Structure

```text
AgentSkillsArxiv/
├── skills/                     # Core skills + community submodule
│   ├── ...
│   └── community-skills/
├── openclaw/                   # OpenClaw-specific skills
│   ├── openclaw-remote-bridge/
│   └── openclaw-remote-dispatch/
├── mcp/                        # MCP servers + shared compliance assets
│   ├── ast-grep-mcp-server/
│   ├── fdep-mcp-server/
│   └── mcp-compliance/
├── artifacts/skills/           # Versioned .skill bundles
└── infra/scripts/              # Installer scripts
```
