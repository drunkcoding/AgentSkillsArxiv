# Quiz Design Rules — Shared Core

> Stack-agnostic. `cuda-tutor` and `triton-tutor` both load this file via symlink, then load their own stack-specific addendum (`quiz-rules-{cuda,triton}.md`) for distractor pools, identifier whitelists, and stack-flavored examples.

## Zero-Hint Policy (CRITICAL)

Every question must be answerable ONLY by someone who actually knows the material. No exceptions.

1. **Option descriptions** NEVER reveal correctness. The description is a short neutral label (e.g., the API name), not a definition.
2. **No "(Recommended)" tag** on any option, ever.
3. **Randomize** the correct answer's position across Q1–Q4 — never always first or last.
4. **Question phrasing** asks about behavior, purpose, output, or failure mode — NOT the name of the answer. If the stem already names the answer, the question is broken.
5. **Plausible distractors** must be real concepts the user could plausibly confuse with the answer (common-misconception based, not absurd). Stack-specific distractor pools live in the per-stack addendum.

## Question Types (use a mix per round)

1. **Factual recall** — direct API / identifier knowledge.
2. **Conceptual understanding** — "Why does X work this way?"
3. **Behavioral prediction** — "What happens when Y?"
4. **Comparison / distinction** — "What is the difference between A and B?"
5. **Debugging scenario** — "Given this code/log, what's wrong?"

The per-stack addendum gives stack-flavored examples of each type.

## Difficulty Balancing (by session type)

| Session | Mix |
|---------|-----|
| Diagnostic | 40 % easy, 40 % medium, 20 % hard |
| Weak-area drill | 30 % medium, 70 % hard |
| Curriculum-order | matches the topic's position in the prereq chain (foundation → mostly medium; advanced → mostly hard) |
| Hard-mode review | 100 % hard |
| Cross-topic drill | at least 1 of 4 questions probes an interaction between the included topics |

## Drilling Unresolved 🔴 Concepts

When targeting 🔴 concepts from concept files:
- Do NOT repeat the literal previous question.
- Test the same underlying knowledge from a different angle: change the hardware generation, change the API surface, or change the failure scenario.
- Stack-specific rephrasing examples live in the per-stack addendum.

## AskUserQuestion Format

- 4 questions per round, 4 options each, single-select.
- Header: max 12 chars, format `Q1. <tag>` (e.g., `Q1. WarpSync`, `Q2. Autotune`).
- Option labels: 1–5 words, preferably the actual identifier from the API being tested.
- Option descriptions: ≤1 sentence, neutral, no give-away.

## File Update Protocol (after grading every round)

1. Update `concepts/{topic}.md` — add or update concept rows and error notes per `proficiency-tracking-shared.md`.
2. Update the dashboard — recalculate topic stats from the concept files.
3. Badges: 🟥 0–39 % · 🟨 40–69 % · 🟩 70–89 % · 🟦 90–100 % · ⬜ no data.

## Topic Attribution Rule

If a question spans multiple topics, attribute it to the topic that owns the **primary mechanism** being tested. Stack-specific examples in the addendum.

**Dual-attribution** (optional): when a question genuinely tests both topics, write the concept row in BOTH topic files with the same `Concept` text. Mark dual-attributed concepts with a trailing `(↔ {other-topic})` in the concept name.

## Cross-Stack Question Rule (CUDA ↔ Triton)

If the active session includes any topic that has a peer in the other stack (mapping listed in `cross-stack-rosetta.md`), **at least 1 of the 4 questions MUST be a cross-stack question** drawn from `cross-stack-rosetta.md`. The cross-stack question is attributed to its primary-stack topic for proficiency tracking (per the Topic Attribution Rule above). The cross-stack question may also satisfy the Difficulty-Balancing "cross-topic" requirement when both rules apply.

The eligibility list (which topics have a peer):
- **cuda-tutor**: CUDA Kernels (matmul/tile subset), CUTLASS, cuTile
- **triton-tutor**: Triton Basics, Tiling/Autotuning, Matmul Patterns, Attention/Reductions, Compiler Internals

Topics with NO peer (skip the cross-stack rule when these are the only topic in scope): NCCL, NVSHMEM, open-gpu-kernel-modules (CUDA side); Ecosystem & Production (Triton side).

## Language Rule

All prose (question text, descriptions, explanations, file body) in the user's detected `{LANG}`. **Always** preserve identifiers verbatim in English regardless of `{LANG}` — the per-stack addendum lists the identifier whitelist for that stack.

Badge emojis (🟥🟨🟩🟦⬜) and ✅/❌ are universal.
