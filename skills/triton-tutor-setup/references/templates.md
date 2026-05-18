# Templates Reference (Curriculum + Document Modes)

## Vault Folder Structure (Curriculum Mode canonical)

```
StudyVault/
├── 00-Dashboard/           # MOC + Prereq-DAG + Glossary + Quick-Reference + Pitfall-Index
├── 01-Triton-Basics/
├── 02-Tiling-Autotuning/
├── 03-Matmul-Patterns/
├── 04-Attention-Reductions/
├── 05-Compiler-Internals/
├── 06-Ecosystem-Production/
└── 99-Exercises/           # Cross-topic hands-on
```

## Dashboard MOC Template

```markdown
---
topic: dashboard
target_hardware: <ampere|hopper|blackwell|ada|mi250|mi300|pvc|mixed>
target_backend: <nvidia|amd|intel|mixed>
scope: [triton-basics, tiling-autotuning, matmul-patterns, attention-reductions, compiler-internals, ecosystem-production]
keywords: MOC, triton, curriculum, <user-focus>
---

# Triton Learning StudyVault — MOC

#dashboard #curriculum

## Curriculum Order
| # | Topic | Overview | Status |
|---|-------|----------|--------|
| 1 | Triton Basics | [[01-Triton-Basics/Overview]] | [ ] |
| 2 | Tiling & Autotuning | [[02-Tiling-Autotuning/Overview]] | [ ] |
| 3 | Matmul Patterns | [[03-Matmul-Patterns/Overview]] | [ ] |
| 4 | Attention & Reductions | [[04-Attention-Reductions/Overview]] | [ ] |
| 5 | Compiler Internals | [[05-Compiler-Internals/Overview]] | [ ] |
| 6 | Ecosystem & Production | [[06-Ecosystem-Production/Overview]] | [ ] |

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
| `#topic-triton-basics` | Triton Basics topic | Exactly one topic tag per concept note. |
| `#concept-*` | Specific concept | One or more. MUST co-attach the topic tag. |
| `#milestone-*` | Hands-on milestone | Only on milestone notes. |
| `#pitfall-*` | Common mistake | Only on pitfall entries. |
| `#backend-{nvidia,amd,intel}` | Backend-specific | Optional, when a concept is backend-gated. |
| `#sm-80`/`#sm-90`/`#sm-100`/`#cdna3` | Architecture-specific | Optional, when arch-gated. |
| `#ir-{ttir,ttgir,llir,ptx,amdgcn}` | IR stage | Only on compiler-internals notes. |

## Recommended Order
- **Absolute beginner (PyTorch user)** → 1 → 2 → 3 → 4 → (5 and 6 as advanced).
- **CUDA writer learning Triton** → 1 (fast) → 3 → 4 → 5 → 2 → 6.
- **Inductor / torch.compile focus** → 1 → 2 → 6 → 3 → 4 → 5.
- **Compiler engineer focus** → 1 → 3 → 5 (deep) → 4 → 6 → 2.
```

## Overview Note Template (per topic)

```markdown
---
topic: <slug>
keywords: <3-5 English keywords>
backend: <nvidia|amd|intel|all>
hardware: <ampere|hopper|blackwell|mi300|all>
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
source: <URL from topic-<slug>.md Resources, or "triton-docs">
backend: <nvidia|amd|intel|all>
hardware: <sm-80|sm-90|sm-100|cdna3|all>
keywords: <3-5 English keywords>
---

# <Concept Name> (<Importance: ★~★★★>)

#topic-<slug> #concept-<concept-slug>

## TL;DR
<1-2 lines>

## How it works
<3-5 lines or an ASCII diagram, or a short Triton code snippet>

## Comparison Table (when applicable)
| Item | Key Property | Notes |
|------|--------------|-------|
| `tl.load(ptr, mask)` | masked-out lanes contain UB | use `other=0.0` for safe default |
| `tl.load(ptr, mask, other=0.0)` | masked-out lanes contain `other` | adds no extra latency |

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
- Every topic folder MUST have at least one practice file with 8+ questions (Document Mode requirement; Curriculum Mode optional — `triton-tutor` generates questions on demand).
- Answers in `> [!answer]- View Answer` fold callouts. Localize label to user language (`정답 보기`, etc.).
- Diversify question types: tag each `[recall]`, `[application]`, or `[analysis]`. Target ≥60% recall, ≥20% application, ≥2 analysis per file.
- Distractors must be real Triton concepts from the same topic — see `triton-tutor/references/quiz-rules.md` distractor pools.

## Formatting Rules

- `[[wiki-links]]` for all cross-references.
- Callouts: `> [!tip]`, `> [!important]`, `> [!warning]`, `> [!danger]`.
- Comparison tables over prose; **bold** for critical Triton identifiers.
- Code snippets (Python with `@triton.jit`) preferred over prose for kernel patterns.
- ASCII diagrams for:
  - Tile decomposition (CTA tile / warp tile / register fragment).
  - Autotune flow (config search → cache key → JIT).
  - IR pipeline (Source → TTIR → TTGIR → LLIR → PTX/AMDGCN).
  - Online softmax running-max/sum update.
- Preserve technical identifiers verbatim in English even in non-English prose.
