---
name: triton-tutor-setup
description: >
  Generate an Obsidian-format Triton StudyVault for learning OpenAI Triton's GPU programming stack.
  Three modes: (1) Curriculum mode (default, no source files needed) builds a prereq-ordered vault
  around the 6-topic learning path: Triton basics (`@triton.jit`, program_id, masks, pointers,
  `tl.load`/`tl.store`), tiling & autotuning (`triton.autotune`, configs, `num_warps`/`num_stages`,
  `tl.constexpr`), matmul patterns (tiled GEMM, pid swizzling, persistent kernels, split-K, FP8
  `tl.dot`), attention & reductions (online softmax, FlashAttention, `tl.associative_scan`),
  compiler internals (TTIR → TTGIR → LLIR → PTX/AMDGCN, `#blocked`/`#mma`/`#shared`/`#dot_op`
  layouts, NVIDIA/AMD backends, WGMMA + TMA lowering), and ecosystem/production
  (`torch.compile`/Inductor codegen, AOT, `proton` profiler, kernel libraries like flash-attn /
  xformers / FBGEMM); (2) Codebase mode generates an onboarding vault from a real Triton/Inductor
  source tree; (3) Document mode turns Triton docs, blog posts, OpenAI/Meta papers, and tutorial
  PDFs into study notes. Mode is auto-detected from CWD markers. Use when the user wants to learn
  Triton from scratch, onboard onto a Triton codebase, build an exercise list for Triton topics,
  or preprocess Triton-related PDFs/docs into structured study material. Pair with the
  `triton-tutor` skill to quiz against the resulting vault.
---

# Triton Tutor Setup — Build an Obsidian Triton StudyVault

## CWD Boundary Rule (ALL MODES)

> **NEVER access files outside the current working directory (CWD).**
> All source scanning, reading, and vault output MUST stay within CWD and its subdirectories.
> If the user provides an external repo path, ask them to either clone or symlink it into CWD first.

## Mode Detection

On invocation, auto-detect the mode:

1. **Scan CWD** for code markers: `setup.py`, `pyproject.toml`, `CMakeLists.txt`, `*.py` containing `import triton` / `@triton.jit` / `triton.language as tl`, `triton/` source dir, `python/triton/`, `lib/Dialect/Triton`, `third_party/nvidia`, `third_party/amd`.
2. **Scan CWD** for document markers: `*.pdf`, `*.txt`, `*.md` (excluding `README.md`), `*.html`, `*.epub`, `*.ipynb` (tutorials).
3. **Decide:**
   - **Triton codebase markers found** (`@triton.jit`/`triton.language`/`lib/Dialect/Triton`) → **Codebase Mode**.
   - **No code markers AND document markers found** → **Document Mode**.
   - **Neither found** (empty dir or only `.git/`) → **Curriculum Mode** (the default for this skill).
4. **Announce** detected mode and ask the user to confirm or override (they may force any mode).

> **Default bias:** when in doubt between Document mode and Curriculum mode, choose **Curriculum Mode** — it is this skill's headline use case.

---

## Curriculum Mode (default)

> Generates a complete Triton learning StudyVault organized around the **6-topic curriculum**.
> Full workflow: see [curriculum-workflow.md](references/curriculum-workflow.md).
> Per-topic content lives in `references/topic-*.md` (loaded only for the topic being authored).
> Templates: [templates.md](references/templates.md).

### Topic List & Order (fixed)

The 6 topics, ordered by prerequisite chain. Build the StudyVault in this order. Do not reorder.

| # | Topic | Reference File | Vault Folder |
|---|-------|----------------|--------------|
| 1 | Triton Basics (foundation)             | [topic-triton-basics.md](references/topic-triton-basics.md) | `01-Triton-Basics/` |
| 2 | Tiling & Autotuning                    | [topic-tiling-autotuning.md](references/topic-tiling-autotuning.md) | `02-Tiling-Autotuning/` |
| 3 | Matmul Patterns                        | [topic-matmul-patterns.md](references/topic-matmul-patterns.md) | `03-Matmul-Patterns/` |
| 4 | Attention & Reductions                 | [topic-attention-reductions.md](references/topic-attention-reductions.md) | `04-Attention-Reductions/` |
| 5 | Compiler Internals                     | [topic-compiler-internals.md](references/topic-compiler-internals.md) | `05-Compiler-Internals/` |
| 6 | Ecosystem & Production                 | [topic-ecosystem-production.md](references/topic-ecosystem-production.md) | `06-Ecosystem-Production/` |

Prerequisite chain (encode in the Dashboard's prereq DAG):

```
              ┌────────────────────────────┐
              │ 1. Triton Basics            │
              │   (@triton.jit, masks,      │
              │    tl.load/store)           │
              └──────┬──────────────────────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
        ┌──────────┐  ┌──────────────┐
        │ 2. Tiling│  │ 3. Matmul    │
        │ & Auto-  │◀▶│   Patterns   │
        │ tuning   │  │   (tl.dot)   │
        └─────┬────┘  └───────┬──────┘
              │               │
              └───────┬───────┘
                      ▼
            ┌─────────────────────┐
            │ 4. Attention &      │
            │    Reductions       │
            │   (FlashAttention)  │
            └────────┬────────────┘
                     │
              ┌──────┴──────┐
              ▼             ▼
       ┌────────────┐  ┌──────────────┐
       │ 5. Compiler│  │ 6. Ecosystem │
       │   Internals│  │  & Production│
       │ (TTIR/TTGIR│  │  (Inductor,  │
       │  /PTX)     │  │   proton)    │
       └────────────┘  └──────────────┘
```

### Phase Summary (TU1-TU9)

| Phase | Name | Key Action |
|-------|------|------------|
| TU1 | Pre-flight | Ask user about target hardware (NVIDIA A100/H100/B200, AMD MI250/MI300, Intel PVC), prior knowledge (PyTorch user / CUDA writer / Triton kernel author), language preference. Skip topics already mastered if user opts in. |
| TU2 | Topic Plan | Build the topic dependency DAG. Materialize the prereq chain in the dashboard. |
| TU3 | Tag Standard | Define tag registry: `#topic-triton-basics`, `#topic-tiling-autotuning`, `#topic-matmul-patterns`, `#topic-attention-reductions`, `#topic-compiler-internals`, `#topic-ecosystem-production`, plus `#concept-*`, `#milestone-*`, `#pitfall-*`. English kebab-case. |
| TU4 | Vault Structure | Create `StudyVault/` with `00-Dashboard/` + the 6 numbered topic folders + `99-Exercises/`. |
| TU5 | Dashboard | MOC + Prereq DAG + Glossary + Quick Reference + Pitfall Index. |
| TU6 | Per-Topic Notes | For each of the 6 topics: load `references/topic-{slug}.md` (lazy, one at a time to manage context), then generate concept notes per [templates.md](references/templates.md). |
| TU7 | Hands-On Milestones | Per topic, materialize 3-7 "build/run/measure X" milestones as standalone notes with success criteria. |
| TU8 | Pitfall Notes | Per topic, materialize the pitfalls section as `Pitfalls.md` with fold callouts. |
| TU9 | Interlinking + Self-Review | Cross-link all notes per the prereq DAG, then verify against [quality-checklist.md](references/quality-checklist.md) **Curriculum Mode** section. |

See [curriculum-workflow.md](references/curriculum-workflow.md) for the full procedural detail of each phase.

### Lazy-Loading Discipline for Topic Content (IMPORTANT)

The 6 topic reference files (`topic-*.md`) are large. Load them **one at a time** in Phase TU6 — read `topic-triton-basics.md` while authoring `01-Triton-Basics/`, drop it from working memory before reading `topic-tiling-autotuning.md`, etc. Do not pre-load all 6.

---

## Codebase Mode

> Generate an onboarding StudyVault from a real Triton / Inductor / kernel-library codebase.
> Full workflow: [codebase-workflow.md](references/codebase-workflow.md). Templates: [triton-codebase-templates.md](references/triton-codebase-templates.md).

### Phase Summary (C1-C9)

| Phase | Name | Key Action |
|-------|------|------------|
| C1 | Project Exploration | Detect Triton version (parse `setup.py`/`pyproject.toml`/`requirements.txt`), target backends (NVIDIA / AMD / Intel via `third_party/`), identify role of the repo (kernel library / compiler fork / inference engine / training framework). |
| C2 | Architecture Analysis | Trace a representative kernel from Python entry (`kernel[grid](...)`) through `@triton.jit` compile cache, autotune flow, generated IR (dump with `TRITON_KERNEL_DUMP=1`), into PTX/AMDGCN. Identify host-side wrappers and PyTorch integration points. |
| C3 | Tag Standard | Same kebab-case rules; add `#backend-*`, `#arch-*`, `#kernel-role-*`, `#api-*`, `#ir-stage-*` categories. |
| C4 | Vault Structure | Dashboard, Architecture, per-module, DevOps (build flags, CI, benchmarks), Exercises. |
| C5 | Dashboard | MOC + Module Map + Kernel Surface table + Backend Matrix + Getting Started (build & run a representative benchmark). |
| C6 | Module Notes | Per-module note: Purpose, Key Kernels, Python Wrappers, Autotune Configs, Block Sizes, IR Lowering Notes, Dependencies, How to Test. |
| C7 | Exercises | Code reading (trace a kernel + dump IR), config (change BLOCK_SIZE, swap backend), debugging (`TRITON_INTERPRET`, `tl.device_print`, IR dump), extension (add a new kernel or autotune config). |
| C8 | Interlinking | Cross-link Python wrapper ↔ `@triton.jit` kernel ↔ autotune config ↔ test. |
| C9 | Self-Review | [quality-checklist.md](references/quality-checklist.md) **Codebase Mode** section. |

Common Triton-adjacent codebases this mode targets: `triton-lang/triton`, `pytorch/pytorch` (Inductor codegen), `Dao-AILab/flash-attention` (Triton variants), `facebookresearch/xformers`, `linkedin/Liger-Kernel`, `unslothai/unsloth`, `pytorch-labs/applied-ai`, `meta-pytorch/tritonbench`, `openai/triton` examples, plus user repos containing `@triton.jit` kernels.

---

## Document Mode

> Transform PDFs (Triton papers, OpenAI/Meta blog posts in PDF, conference slides on Triton), text, and web pages into study notes. Same workflow as upstream tutor-skills document mode — see [document-workflow.md](references/document-workflow.md).

### Phase Summary (D1-D9)

| Phase | Name |
|-------|------|
| D1 | Source Discovery & Extraction (use `pdftotext` CLI, NEVER `Read` directly on PDF; for `.ipynb` use `jupyter nbconvert --to markdown`) |
| D2 | Content Analysis |
| D3 | Tag Standard |
| D4 | Vault Structure |
| D5 | Dashboard |
| D6 | Concept Notes |
| D7 | Practice Questions (active recall fold callouts) |
| D8 | Interlinking |
| D9 | Self-Review |

See [document-workflow.md](references/document-workflow.md) for detail.

**Special handling for Triton documents**: when processing the official Triton docs, the original Triton paper (Tillet et al., MAPL 2019), FlashAttention papers (Dao et al.), or PyTorch 2.x Inductor design docs, prefer reorganizing extracted content **into the 6-topic structure** (same folders as Curriculum mode) rather than mirroring the source's TOC. The 6-topic structure is the canonical taxonomy.

---

## Language

- Match the user's language (Korean → Korean prose, etc.).
- **Tags, keywords, and Triton identifiers** stay verbatim in English regardless: `@triton.jit`, `triton.autotune`, `tl.load`, `tl.dot`, `tl.constexpr`, `BLOCK_SIZE_M`, `num_warps`, `num_stages`, `TTIR`, `TTGIR`, `#blocked`, `#mma`, `#shared`, `#dot_op`, `torch.compile`, `Inductor`, `proton`, `TRITON_INTERPRET`, etc.
- Fold-callout labels can be localized (e.g., Korean: `정답 보기`, English: `View Answer`).

## Pairing with `triton-tutor` and `tutor-handouts`

The generated StudyVault is the input to two paired skills:

- **`triton-tutor`** — interactive quiz tutor over the vault (4-question rounds, concept-level proficiency tracking).
- **`tutor-handouts`** — produces a `Coursepack/` of CMU 15-418 / Stanford CS149-style PDF lecture handouts, programming assignment writeups, cheatsheets, problem sets, capstone project, syllabus, plus matching LeetGPU-style graded exercise scaffolds (CUDA / Triton / PyTorch starters + autograder harness).

Once Phase TU9 / C9 / D9 self-review passes, tell the user:

> "Vault built at `./StudyVault/`. Run the `triton-tutor` skill in the same directory to start quiz sessions, or `tutor-handouts` to generate a printable course pack with programming exercises."
