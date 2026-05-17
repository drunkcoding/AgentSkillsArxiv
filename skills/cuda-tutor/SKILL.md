---
name: cuda-tutor
description: >
  Interactive quiz tutor for a CUDA StudyVault built by `cuda-tutor-setup`. Delivers 4-question
  rounds with concept-level proficiency tracking (🟥/🟨/🟩/🟦/⬜) across the 6 CUDA learning
  topics: CUDA kernels (threads/blocks/warps, memory hierarchy, TMA, WGMMA, cp.async),
  CUTLASS + CuTe (Layout/Stride/Tensor, MMA atoms, GEMM pipelines), cuTile (Python-first tile
  DSL), open-gpu-kernel-modules (RM, GSP firmware, UVM, kernel-open layout), NCCL (collectives,
  topology, NVLink-SHARP, transports), and NVSHMEM (PGAS, symmetric heap, IBGDA, on-stream API).
  Use when the user wants to (1) take a diagnostic CUDA assessment, (2) drill weak GPU concepts,
  (3) study a specific CUDA topic, (4) review the learning dashboard, or says things like
  "quiz me on CUDA", "test my CUTLASS knowledge", "drill NCCL", "/cuda-tutor", "퀴즈".
---

# CUDA Tutor

Quiz-based tutor that tracks what the user knows and doesn't know at the **concept level** across the
6 CUDA topics. The goal is to surface blind spots in NVIDIA GPU programming knowledge through
zero-hint questions and rephrased drills on missed concepts.

## Prerequisite: Paired Skill

This skill **requires a pre-built CUDA StudyVault**. If none exists in CWD, tell the user:

> "No StudyVault found. Run the `cuda-tutor-setup` skill first to generate one."

The expected vault layout — produced by `cuda-tutor-setup` Phase CU9 / C9 / D9 — is described under `## File Structure` below.

## Curriculum Structure (read once, internalize)

The vault is organized around 6 topics with a fixed prerequisite chain. Session-type selection in Phase 2 below depends on this DAG:

```
            1. CUDA Kernels (foundation)
                    │
        ┌───────────┼───────────────────────┐
        ▼           ▼                       ▼
   2. CUTLASS   3. cuTile          4. Open GPU Kernel Modules
        ↑           ↑
        └─peer──────┘
        │
        └────────────────┐
                         ▼
                  5. NCCL  ↔  6. NVSHMEM
```

When the user picks "Follow curriculum order", serve the next unmastered topic in this chain (CUDA Kernels first; never NCCL/NVSHMEM before CUDA Kernels is 🟩+).

## File Structure

```
StudyVault/
├── *dashboard*               ← Compact overview: proficiency table + stats
└── concepts/
    ├── cuda-kernels.md       ← Per-topic concept tracker
    ├── cutlass.md
    ├── cutile.md
    ├── open-gpu-kernel-modules.md
    ├── nccl.md
    └── nvshmem.md
```

- **Dashboard**: aggregated numbers only. Links to concept files. Stays small forever.
- **Concept files**: one per topic. Tracks each concept with attempts / correct / last tested / status / error notes. Bounded growth.

## Workflow

### Phase 0: Detect Language

Detect the user's language from their message → `{LANG}`. All quiz prompts, explanations, and file content render in `{LANG}`. Technical CUDA terms (e.g., `cp.async`, `ncclAllReduce`, `nvshmem_put`) stay verbatim in English regardless of `{LANG}`.

### Phase 1: Discover Vault

1. Glob `**/StudyVault/` in the project.
2. List section directories — expect numbered topic folders (e.g., `01-CUDA-Kernels/`, `02-CUTLASS/`, ...).
3. Glob `**/StudyVault/*dashboard*` for the dashboard.
4. If found, read it. Preserve existing file path regardless of `{LANG}`.
5. If not found, create from the Dashboard Template below.
6. If no StudyVault exists, tell the user to run `cuda-tutor-setup` first, then stop.

### Phase 2: Ask Session Type

**MANDATORY**: use AskUserQuestion to let the user pick a session. Read the dashboard proficiency table first, then build context-aware options:

1. Unmeasured areas (⬜) exist → include **"Diagnostic"** targeting those areas (e.g., "Cover the 2 unmeasured topics: cuTile, NVSHMEM").
2. Weak areas (🟥/🟨) exist → include **"Drill weak areas"** naming the weakest topic(s) (e.g., "Drill NCCL — currently 🟥 28%").
3. Always include **"Choose a topic"** so the user can pick any of the 6 topics.
4. All areas 🟩/🟦 → include **"Hard-mode review"** (hardest difficulty mix).
5. If the StudyVault declares a recommended prerequisite chain (it does: CUDA kernels → CUTLASS/cuTile, CUDA kernels → driver, CUDA kernels → NCCL ↔ NVSHMEM), include **"Follow curriculum order"** which serves the next unmastered topic in the chain.

Header: `"Session"`. Concise option descriptions that list which topics each option targets. No `(Recommended)` tag. The user MUST select before proceeding.

### Phase 3: Build Questions

1. Read the markdown files inside the target topic folder(s) of the StudyVault.
2. If drilling a weak area: also read `concepts/{topic}.md` to find 🔴 unresolved concepts — **rephrase these in a new context** (different API call, different hardware generation, different failure scenario). Never repeat the literal question.
3. For cross-topic drill sessions (e.g., NCCL + NVSHMEM): include at least one question that probes the **interaction** (e.g., "When does it make sense to layer NVSHMEM under NCCL?").
4. Craft exactly 4 questions following `references/quiz-rules.md`.

**CRITICAL**: read `references/quiz-rules.md` before crafting ANY question. Zero hints allowed.

### Phase 4: Present Quiz

Use AskUserQuestion:
- 4 questions per round, 4 options each, single-select.
- Header: `"Q1. <≤12-char tag>"` (examples: `Q1. WarpSched`, `Q2. CuTeLO`, `Q3. ncclAlgo`, `Q4. nvshmemAPI`).
- Descriptions: neutral, no hints. Distractors must be plausible CUDA concepts (not absurd).

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
| TMA cp.async.bulk vs cp.async | 2 | 1 | 2026-05-15 | 🔴 |
```

Error-note format (only for wrong answers):
```markdown
### Error Notes

**TMA cp.async.bulk vs cp.async**
- Confusion: user picked cp.async for 2D tiles
- Key point: cp.async.bulk (TMA) handles 1D-5D tensor copies via descriptor; cp.async is per-thread 4/8/16-byte
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
# CUDA Learning Dashboard

> Concept-level metacognition tracker for the 6-topic CUDA learning path. See linked files for details.

---

## Proficiency by Topic

| Topic | Correct | Wrong | Rate | Level | Details |
|-------|---------|-------|------|-------|---------|
| 1. CUDA Kernels | 0 | 0 | - | ⬜ Unmeasured | [[concepts/cuda-kernels]] |
| 2. CUTLASS | 0 | 0 | - | ⬜ Unmeasured | [[concepts/cutlass]] |
| 3. cuTile | 0 | 0 | - | ⬜ Unmeasured | [[concepts/cutile]] |
| 4. Open GPU Kernel Modules | 0 | 0 | - | ⬜ Unmeasured | [[concepts/open-gpu-kernel-modules]] |
| 5. NCCL | 0 | 0 | - | ⬜ Unmeasured | [[concepts/nccl]] |
| 6. NVSHMEM | 0 | 0 | - | ⬜ Unmeasured | [[concepts/nvshmem]] |
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

1. CUDA Kernels
2. CUTLASS  ·  cuTile  ·  Open GPU Kernel Modules  (parallel tier — all build on CUDA Kernels)
3. NCCL  ↔  NVSHMEM  (final tier — multi-GPU communication)
```

## Concept File Template

Create per topic when its first question is asked. Example for `concepts/cuda-kernels.md`:

```markdown
# CUDA Kernels — Concept Tracker

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
- Keep technical CUDA identifiers verbatim (`ncclAllReduce`, `cp.async.bulk`, `wgmma.mma_async`, `nvshmem_quiet`) even when prose is in another language.
- For cross-topic questions, attribute the concept to the topic that owns the **primary** mechanism being tested.
- For seed question banks per topic, see `references/cuda-question-bank-seeds.md`.
- For exact proficiency-tracking formulas and edge cases, see `references/proficiency-tracking.md`.
