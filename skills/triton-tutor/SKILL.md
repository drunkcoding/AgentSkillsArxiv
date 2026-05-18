---
name: triton-tutor
description: >
  Interactive quiz tutor for a Triton StudyVault built by `triton-tutor-setup`. Delivers 4-question
  rounds with concept-level proficiency tracking (🟥/🟨/🟩/🟦/⬜) across 6 Triton topics: Triton basics
  (`@triton.jit`, masks, `tl.load`/`tl.store`), tiling & autotuning (`triton.autotune`,
  `num_warps`/`num_stages`), matmul patterns (tiled GEMM, pid swizzling, persistent, split-K, FP8
  `tl.dot`), attention & reductions (FlashAttention, online softmax, `tl.associative_scan`),
  compiler internals (TTIR/TTGIR/LLIR, NVIDIA/AMD backends, WGMMA + TMA lowering), and
  ecosystem/production (`torch.compile`/Inductor, AOT, `proton`). Use when the user wants to take a
  diagnostic Triton assessment, drill weak Triton concepts, study a specific Triton topic, review
  the learning dashboard, or says things like "quiz me on Triton", "drill FlashAttention",
  "/triton-tutor", "퀴즈".
---

# Triton Tutor

Quiz-based tutor that tracks what the user knows and doesn't know at the **concept level** across the
6 Triton topics. The goal is to surface blind spots in OpenAI Triton GPU programming knowledge through
zero-hint questions and rephrased drills on missed concepts.

## Prerequisite: Paired Skill

This skill **requires a pre-built Triton StudyVault**. If none exists in CWD, tell the user:

> "No StudyVault found. Run the `triton-tutor-setup` skill first to generate one."

The expected vault layout — produced by `triton-tutor-setup` Phase TU9 / C9 / D9 — is described under `## File Structure` below.

## Curriculum Structure (read once, internalize)

The vault is organized around 6 topics with a fixed prerequisite chain. Session-type selection in Phase 2 below depends on this DAG:

```
            1. Triton Basics (foundation)
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
   2. Tiling &              3. Matmul Patterns
      Autotuning                │
        │                       │
        └───────────┬───────────┘
                    ▼
          4. Attention & Reductions
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
   5. Compiler            6. Ecosystem &
      Internals              Production
```

When the user picks "Follow curriculum order", serve the next unmastered topic in this chain (Triton Basics first; never Compiler Internals or Ecosystem before Attention & Reductions is 🟩+).

## File Structure

```
StudyVault/
├── *dashboard*                    ← Compact overview: proficiency table + stats
└── concepts/
    ├── triton-basics.md           ← Per-topic concept tracker
    ├── tiling-autotuning.md
    ├── matmul-patterns.md
    ├── attention-reductions.md
    ├── compiler-internals.md
    └── ecosystem-production.md
```

- **Dashboard**: aggregated numbers only. Links to concept files. Stays small forever.
- **Concept files**: one per topic. Tracks each concept with attempts / correct / last tested / status / error notes. Bounded growth.

## Workflow

### Phase 0: Detect Language

Detect the user's language from their message → `{LANG}`. All quiz prompts, explanations, and file content render in `{LANG}`. Technical Triton terms (e.g., `tl.load`, `tl.dot`, `triton.autotune`, `num_warps`, `BLOCK_SIZE`) stay verbatim in English regardless of `{LANG}`.

### Phase 1: Discover Vault

1. Glob `**/StudyVault/` in the project.
2. List section directories — expect numbered topic folders (e.g., `01-Triton-Basics/`, `02-Tiling-Autotuning/`, ...).
3. Glob `**/StudyVault/*dashboard*` for the dashboard.
4. If found, read it. Preserve existing file path regardless of `{LANG}`.
5. If not found, create from the Dashboard Template below.
6. If no StudyVault exists, tell the user to run `triton-tutor-setup` first, then stop.

### Phase 2: Ask Session Type

**MANDATORY**: use AskUserQuestion to let the user pick a session. Read the dashboard proficiency table first, then build context-aware options:

1. Unmeasured areas (⬜) exist → include **"Diagnostic"** targeting those areas (e.g., "Cover the 2 unmeasured topics: Compiler Internals, Ecosystem").
2. Weak areas (🟥/🟨) exist → include **"Drill weak areas"** naming the weakest topic(s) (e.g., "Drill Matmul Patterns — currently 🟥 28%").
3. Always include **"Choose a topic"** so the user can pick any of the 6 topics.
4. All areas 🟩/🟦 → include **"Hard-mode review"** (hardest difficulty mix).
5. If the StudyVault declares a recommended prerequisite chain (it does: Triton Basics → Tiling/Matmul → Attention → Compiler/Ecosystem), include **"Follow curriculum order"** which serves the next unmastered topic in the chain.

Header: `"Session"`. Concise option descriptions that list which topics each option targets. No `(Recommended)` tag. The user MUST select before proceeding.

### Phase 3: Build Questions

1. Read the markdown files inside the target topic folder(s) of the StudyVault.
2. If drilling a weak area: also read `concepts/{topic}.md` to find 🔴 unresolved concepts — **rephrase these in a new context** (different API call, different GPU backend, different failure scenario). Never repeat the literal question.
3. For cross-topic drill sessions (e.g., Matmul + Compiler): include at least one question that probes the **interaction** (e.g., "How does `tl.dot` lower differently on Hopper vs Ampere?").
4. Craft exactly 4 questions following `references/quiz-rules.md`. **Cross-stack requirement**: if the session covers Triton Basics, Tiling/Autotuning, Matmul Patterns, Attention/Reductions, or Compiler Internals, at least 1 of the 4 questions MUST be a cross-stack question from `references/cross-stack-rosetta.md` (CUDA/CUTLASS/cuTile equivalent of a Triton mechanism). The cross-stack question is attributed to its Triton-side primary topic for proficiency tracking. When this rule and the cross-topic rule in item 3 both apply, the cross-stack question may double-count as the cross-topic question.

**CRITICAL**: read `references/quiz-rules.md` before crafting ANY question. Zero hints allowed.

### Phase 4: Present Quiz

Use AskUserQuestion:
- 4 questions per round, 4 options each, single-select.
- Header: `"Q1. <≤12-char tag>"` (examples: `Q1. ProgID`, `Q2. Autotune`, `Q3. tl.dot`, `Q4. TTGIR`).
- Descriptions: neutral, no hints. Distractors must be plausible Triton concepts (not absurd).

### Phase 5: Grade & Explain

1. Show a results table: question / correct answer / user answer / ✅ or ❌.
2. Wrong answers: concise 1–3 line explanation that names the underlying concept and links the relevant StudyVault note via `[[wiki-link]]`.
3. Map each question to its topic for the file-update phase.

### Phase 6: Update Files

#### 1. Update concept file (`concepts/{topic}.md`)

For each question answered:
- **New concept** → add row to the concept table. If wrong, also add an error-note entry.
- **Existing 🔴 concept answered correctly** → increment `Attempts` and `Correct`, flip status to 🟢, keep the error note as learning history.
- **Existing 🟢 concept answered wrong again** → increment `Attempts`, flip status back to 🔴, update the error note.

Concept table format:
```markdown
| Concept | Attempts | Correct | Last Tested | Status |
|---------|----------|---------|-------------|--------|
| pid swizzling for L2 reuse | 2 | 1 | 2026-05-15 | 🔴 |
```

Error-note format (only for wrong answers):
```markdown
### Error Notes

**pid swizzling for L2 reuse**
- Confusion: user thought row-major pid order maximizes L2 hits
- Key point: grouped/swizzled pid ordering reuses A or B tiles across blocks in the same wave, improving L2 hit rate vs raw row-major
```

#### 2. Update dashboard

- Recalculate per-topic stats from the concept files (sum `Attempts` and `Correct` across each topic).
- Update proficiency badges:
  - 🟥 Weak 0–39%
  - 🟨 Fair 40–69%
  - 🟩 Good 70–89%
  - 🟦 Mastered 90–100%
  - ⬜ Unmeasured (no data)
- Update aggregate stats: total questions, cumulative rate, unresolved/resolved counts, weakest/strongest topic.

Dashboard stays compact — no per-session logs, no per-question records.

## Dashboard Template

Create when no dashboard exists. Filename localized to `{LANG}`. Example in English:

```markdown
# Triton Learning Dashboard

> Concept-level metacognition tracker for the 6-topic Triton learning path. See linked files for details.

---

## Proficiency by Topic

| Topic | Correct | Wrong | Rate | Level | Details |
|-------|---------|-------|------|-------|---------|
| 1. Triton Basics | 0 | 0 | - | ⬜ Unmeasured | [[concepts/triton-basics]] |
| 2. Tiling & Autotuning | 0 | 0 | - | ⬜ Unmeasured | [[concepts/tiling-autotuning]] |
| 3. Matmul Patterns | 0 | 0 | - | ⬜ Unmeasured | [[concepts/matmul-patterns]] |
| 4. Attention & Reductions | 0 | 0 | - | ⬜ Unmeasured | [[concepts/attention-reductions]] |
| 5. Compiler Internals | 0 | 0 | - | ⬜ Unmeasured | [[concepts/compiler-internals]] |
| 6. Ecosystem & Production | 0 | 0 | - | ⬜ Unmeasured | [[concepts/ecosystem-production]] |
| **Total** | **0** | **0** | **-** | ⬜ Unmeasured | |

> 🟥 Weak (0-39%) · 🟨 Fair (40-69%) · 🟩 Good (70-89%) · 🟦 Mastered (90-100%) · ⬜ Unmeasured

---

## Stats

- **Total Questions**: 0
- **Cumulative Rate**: -
- **Unresolved Concepts**: 0
- **Resolved Concepts**: 0
- **Weakest Topic**: -
- **Strongest Topic**: -

---

## Curriculum Order

Recommended progression (do not unlock the next tier until the prior is 🟩+):

1. Triton Basics
2. Tiling & Autotuning  ·  Matmul Patterns  (parallel tier — both build on Basics)
3. Attention & Reductions  (consolidates tiling + matmul into a single fused-kernel idiom)
4. Compiler Internals  ·  Ecosystem & Production  (parallel tier — for advanced understanding)
```

## Concept File Template

Create per topic when its first question is asked. Example for `concepts/triton-basics.md`:

```markdown
# Triton Basics — Concept Tracker

| Concept | Attempts | Correct | Last Tested | Status |
|---------|----------|---------|-------------|--------|

### Error Notes

(added as concepts are missed)
```

## Important Reminders

- ALWAYS read `references/quiz-rules.md` before creating questions.
- NEVER include hints in option labels or descriptions.
- NEVER tag any option with "(Recommended)".
- Randomize the correct answer's position across Q1–Q4.
- Wrong-answer explanations MUST link to the relevant `[[concept note]]` in the StudyVault.
- After grading, ALWAYS update both the concept file AND the dashboard.
- Keep technical Triton identifiers verbatim (`tl.load`, `tl.dot`, `triton.autotune`, `tl.program_id`, `tl.constexpr`, `num_warps`, `num_stages`, `BLOCK_SIZE_M`, `TTIR`, `TTGIR`) even when prose is in another language.
- For cross-topic questions, attribute the concept to the topic that owns the **primary** mechanism being tested.
- For seed question banks per topic, see `references/triton-question-bank-seeds.md`.
- For exact proficiency-tracking formulas and edge cases, see `references/proficiency-tracking.md`.
