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
| `auto-gpu-kernel` | `skills/auto-gpu-kernel/` | Scaffold + workflow for an autonomous Triton GPU-kernel optimization loop on FlashInfer-Bench + Modal (MLSys-2026 DSA winner architecture) |
| `better-grep` | `skills/better-grep/` | One-shot high-signal text search patterns |
| `citation-convert` | `skills/citation-convert/` | DOI/arXiv/title to BibTeX conversion |
| `conference-plot` | `skills/conference-plot/` | Publication-quality conference figures |
| `cuda-tutor` | `skills/cuda-tutor/` | Interactive concept-level quiz tutor over a CUDA StudyVault built by `cuda-tutor-setup`. Shares quiz rules + proficiency math + CUDA↔Triton Rosetta with `triton-tutor` via `skills/tutor-core/` |
| `cuda-tutor-setup` | `skills/cuda-tutor-setup/` | Generates an Obsidian CUDA StudyVault (curriculum / codebase / document modes) over the 6-topic NVIDIA learning path: CUDA kernels, CUTLASS, cuTile, open-gpu-kernel-modules, NCCL, NVSHMEM |
| `function-dep-search` | `skills/function-dep-search/` | AST-accurate function dependency tracing |
| `mem0` | `skills/mem0/` | Persistent memory integration patterns |
| `openviking` | `skills/openviking/` | OpenViking context database reference |
| `triton-tutor` | `skills/triton-tutor/` | Interactive concept-level quiz tutor over a Triton StudyVault built by `triton-tutor-setup`. Shares quiz rules + proficiency math + CUDA↔Triton Rosetta with `cuda-tutor` via `skills/tutor-core/` |
| `triton-tutor-setup` | `skills/triton-tutor-setup/` | Generates an Obsidian Triton StudyVault (curriculum / codebase / document modes) over the 6-topic Triton learning path: Triton basics, tiling/autotuning, matmul patterns, attention/reductions, compiler internals, ecosystem/production |
| `tutor-core` (shared) | `skills/tutor-core/` | **NOT a standalone skill** — shared reference container for `cuda-tutor` and `triton-tutor`. Holds canonical `quiz-rules-shared.md`, `proficiency-tracking-shared.md`, and the bidirectional CUDA↔Triton `cross-stack-rosetta.md`. Has no `SKILL.md`; the installer (`infra/scripts/install-skills.sh`) discovers via `[ -f SKILL.md ]` and silently skips this directory |
| `tutor-handouts` | `skills/tutor-handouts/` | Generates a CMU 15-418 / Stanford CS149 / MIT 6.172-style course pack (PDF lecture handouts, programming assignments, cheatsheets, problem sets, capstone, syllabus) plus LeetGPU-style graded exercise scaffolds (CUDA / Triton / PyTorch starters + autograder harness) from a `StudyVault/` produced by `cuda-tutor-setup` or `triton-tutor-setup` |
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
