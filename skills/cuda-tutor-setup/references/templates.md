# Templates Reference (Curriculum + Document Modes)

## Vault Folder Structure (Curriculum Mode canonical)

```
StudyVault/
├── 00-Dashboard/           # MOC + Prereq-DAG + Glossary + Quick-Reference + Pitfall-Index
├── 01-CUDA-Kernels/
├── 02-CUTLASS/
├── 03-cuTile/
├── 04-Open-GPU-Kernel-Modules/
├── 05-NCCL/
├── 06-NVSHMEM/
└── 99-Exercises/           # Cross-topic hands-on
```

## Dashboard MOC Template

```markdown
---
topic: dashboard
target_hardware: <ampere|hopper|blackwell|ada|mixed>
scope: [cuda-kernels, cutlass, cutile, open-gpu-kernel-modules, nccl, nvshmem]
keywords: MOC, cuda, curriculum, <user-focus>
---

# CUDA Learning StudyVault — MOC

#dashboard #curriculum

## Curriculum Order
| # | Topic | Overview | Status |
|---|-------|----------|--------|
| 1 | CUDA Kernels | [[01-CUDA-Kernels/Overview]] | [ ] |
| 2 | CUTLASS + CuTe | [[02-CUTLASS/Overview]] | [ ] |
| 3 | cuTile | [[03-cuTile/Overview]] | [ ] |
| 4 | Open GPU Kernel Modules | [[04-Open-GPU-Kernel-Modules/Overview]] | [ ] |
| 5 | NCCL | [[05-NCCL/Overview]] | [ ] |
| 6 | NVSHMEM | [[06-NVSHMEM/Overview]] | [ ] |

## Prereq DAG
→ [[Prereq-DAG]]

## Quick Reference
→ [[Quick-Reference]]

## Glossary
→ [[Glossary]]

## Pitfall Index
→ [[Pitfall-Index]]

## Tag Index
| Tag | Description | Rule |
|-----|-------------|------|
| `#topic-cuda-kernels` | CUDA Kernels topic | Exactly one topic tag per concept note. |
| `#concept-*` | Specific concept | One or more. MUST co-attach the topic tag. |
| `#milestone-*` | Hands-on milestone | Only on milestone notes. |
| `#pitfall-*` | Common mistake | Only on pitfall entries. |
| `#sm-80`/`#sm-90`/`#sm-100` | Architecture-specific | Optional, when a concept is arch-gated. |

## Recommended Order
- **Absolute beginner** → 1 → 2 → 3 → 4 → 5 → 6.
- **Distributed-LLM focus** → 1 → (5 + 6 in parallel) → 2 → 3.
- **Driver / systems focus** → 1 → 4 → (2 or 5 optional).
- **Inference-kernel focus** → 1 → 2 → 3 → (5 if multi-GPU).
```

## Overview Note Template (per topic)

```markdown
---
topic: <slug>
keywords: <3-5 English keywords>
hardware: <ampere|hopper|blackwell|all>
---

# <Topic Display Name> — Overview

#topic-<slug>

## What it is
<2-3 sentences>

## Concept Ladder
| Stage | Concepts |
|-------|----------|
| Beginner | <concept-1>, <concept-2>, ... |
| Intermediate | ... |
| Advanced | ... |
| Expert | ... |

## Prerequisites
- [[<prereq-topic>/Overview]] — why you need it (1 sentence)

## Where this leads
- [[<dependent-topic>/Overview]] — what builds on this

## Sections in this folder
- [[Concepts/<concept-1>]]
- [[Concepts/<concept-2>]]
- [[Milestones]]
- [[Pitfalls]]
- [[Resources]]
```

## Concept Note Template

```markdown
---
topic: <slug>
concept: <concept-slug>
source: <URL from topic-<slug>.md Resources, or "nvidia-docs">
hardware: <sm-80|sm-90|sm-100|all>
keywords: <3-5 English keywords>
---

# <Concept Name> (<Importance: ★~★★★>)

#topic-<slug> #concept-<concept-slug>

## TL;DR
<1-2 lines>

## How it works
<3-5 lines or an ASCII diagram>

## Comparison Table (when applicable)
| Item | Key Property | Notes |
|------|--------------|-------|
| `cp.async` | per-thread 4/8/16-byte | works on Ampere+ |
| `cp.async.bulk` (TMA) | tensor-descriptor-driven 1D-5D | Hopper+ |

## API / Identifiers (verbatim English)
- `<identifier>` — description

## Common Pitfalls
> [!warning]- <pitfall title>
> <explanation>

## Related Notes
- [[Concepts/<peer-concept>]] (same topic)
- [[../<prereq-topic>/Concepts/<concept>]] (prerequisite)
- [[../<dependent-topic>/Concepts/<concept>]] (where this is used)
```

## Milestones Template (per topic)

```markdown
---
topic: <slug>
keywords: milestones, hands-on, <topic>
---

# <Topic> — Hands-On Milestones

#topic-<slug> #milestone-<slug>

## M1: <milestone name>
**Goal**: <one-line objective>
**Success criteria**: <specific measurable outcome>
**Effort**: <≤1h | half-day | multi-day>
**Verification**: `<command or check>`

> [!tip]- Hints (click to reveal)
> <hint without giving away the answer>

## M2: ...
```

## Pitfalls Template (per topic)

```markdown
---
topic: <slug>
keywords: pitfalls, traps, <topic>
---

# <Topic> — Pitfalls

#topic-<slug> #pitfall-<slug>

> [!danger]- <pitfall title>
> - **What happens**: <symptom>
> - **Why**: <root cause>
> - **Fix**: <correction>
> - **Related**: [[Concepts/<concept>]]

> [!danger]- <next pitfall>
> ...
```

## Practice Question Template (Document Mode + cross-topic)

```markdown
---
topic: <slug or "cross-topic">
keywords: practice, <topic keywords>
---

# <Topic> — Practice Questions (N questions)

#practice #topic-<slug>

## Related Concepts
- [[Concepts/<concept>]]

> [!hint]- Key Patterns (click to reveal)
> | Keyword | Answer |
> |---------|--------|
> | <pattern> | <answer> |

---

## Q1 — <label> [recall]
> Scenario / question in one blockquote line.

> [!answer]- View Answer
> Answer + 1-line explanation.

---

## Q2 — <label> [application]
> Applied scenario.

> [!answer]- View Answer
> Worked answer.

---

## Q3 — <label> [analysis]
> Comparison or "why" question.

> [!answer]- View Answer
> Analytical answer.
```

### Practice Question Rules
- Every topic folder MUST have at least one practice file with 8+ questions (Document Mode requirement; Curriculum Mode optional — `cuda-tutor` generates questions on demand).
- Answers in `> [!answer]- View Answer` fold callouts. Localize label to user language (`정답 보기`, etc.).
- Diversify question types: tag each `[recall]`, `[application]`, or `[analysis]`. Target ≥60% recall, ≥20% application, ≥2 analysis per file.
- Distractors must be real CUDA concepts from the same topic — see `cuda-tutor/references/quiz-rules.md` distractor pools.

## Formatting Rules

- `[[wiki-links]]` for all cross-references.
- Callouts: `> [!tip]`, `> [!important]`, `> [!warning]`, `> [!danger]`.
- Comparison tables over prose; **bold** for critical CUDA identifiers.
- ASCII diagrams for:
  - Memory hierarchy (Global / L2 / L1-shared / Registers).
  - Warp / block / grid layout.
  - Ring vs tree algorithms (NCCL).
  - Driver stack (user / kernel / GSP firmware).
- Preserve technical identifiers verbatim in English even in non-English prose.
