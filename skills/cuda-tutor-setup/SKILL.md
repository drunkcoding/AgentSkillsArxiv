---
name: cuda-tutor-setup
description: >
  Generate an Obsidian-format CUDA StudyVault for learning NVIDIA's GPU programming stack.
  Three modes: (1) Curriculum mode (default, no source files needed) builds a prereq-ordered
  vault around the 6-topic learning path: CUDA kernels (threads/blocks/warps, memory hierarchy,
  TMA, WGMMA, cp.async), CUTLASS + CuTe (Layout/Tensor, MMA atoms, GEMM pipelines), cuTile
  (Python tile DSL), open-gpu-kernel-modules (RM, GSP firmware, UVM, kernel-open), NCCL
  (collectives, NVLink-SHARP, transports), and NVSHMEM (PGAS, symmetric heap, IBGDA);
  (2) Codebase mode generates an onboarding vault from a real CUDA/CUTLASS/NCCL/NVSHMEM/driver
  source tree; (3) Document mode turns NVIDIA whitepapers, GTC slide decks, and PDFs into
  study notes. Mode is auto-detected from CWD markers. Use when the user wants to learn CUDA
  from scratch, onboard onto a GPU codebase, build an exercise list for CUDA topics, or
  preprocess NVIDIA PDFs/docs into structured study material. Pair with the `cuda-tutor` skill
  to quiz against the resulting vault.
---

# CUDA Tutor Setup — Build an Obsidian CUDA StudyVault

## CWD Boundary Rule (ALL MODES)

> **NEVER access files outside the current working directory (CWD).**
> All source scanning, reading, and vault output MUST stay within CWD and its subdirectories.
> If the user provides an external repo path, ask them to either clone or symlink it into CWD first.

## Mode Detection

On invocation, auto-detect the mode:

1. **Scan CWD** for code markers: `CMakeLists.txt`, `setup.py`, `pyproject.toml`, `Makefile`, `Kbuild`, `*.cu`, `*.cuh`, `cutlass/`, `cute/`, `nccl.h`, `nvshmem.h`, `kernel-open/`, `src/nvidia/`.
2. **Scan CWD** for document markers: `*.pdf`, `*.txt`, `*.md` (excluding `README.md`), `*.html`, `*.epub`.
3. **Decide:**
   - **CUDA codebase markers found** (`.cu`/`.cuh`/`cutlass/`/`cute/`/`nccl.h`/`nvshmem.h`/`kernel-open/`) → **Codebase Mode**.
   - **No code markers AND document markers found** → **Document Mode**.
   - **Neither found** (empty dir or only `.git/`) → **Curriculum Mode** (the default for this skill).
4. **Announce** detected mode and ask the user to confirm or override (they may force any mode).

> **Default bias:** when in doubt between Document mode and Curriculum mode, choose **Curriculum Mode** — it is this skill's headline use case.

---

## Curriculum Mode (default)

> Generates a complete CUDA learning StudyVault organized around the **6-topic curriculum**.
> Full workflow: see [curriculum-workflow.md](references/curriculum-workflow.md).
> Per-topic content lives in `references/topic-*.md` (loaded only for the topic being authored).
> Templates: [templates.md](references/templates.md).

### Topic List & Order (fixed)

The 6 topics, ordered by prerequisite chain. Build the StudyVault in this order. Do not reorder.

| # | Topic | Reference File | Vault Folder |
|---|-------|----------------|--------------|
| 1 | CUDA Kernels (foundation)              | [topic-cuda-kernels.md](references/topic-cuda-kernels.md) | `01-CUDA-Kernels/` |
| 2 | CUTLASS + CuTe                         | [topic-cutlass.md](references/topic-cutlass.md) | `02-CUTLASS/` |
| 3 | cuTile (Python tile DSL)               | [topic-cutile.md](references/topic-cutile.md) | `03-cuTile/` |
| 4 | NVIDIA open-gpu-kernel-modules         | [topic-open-gpu-kernel-modules.md](references/topic-open-gpu-kernel-modules.md) | `04-Open-GPU-Kernel-Modules/` |
| 5 | NCCL                                   | [topic-nccl.md](references/topic-nccl.md) | `05-NCCL/` |
| 6 | NVSHMEM                                | [topic-nvshmem.md](references/topic-nvshmem.md) | `06-NVSHMEM/` |

Prerequisite chain (encode in the Dashboard's prereq DAG):

```
                    ┌────────────────────────────┐
                    │ 1. CUDA Kernels (foundation)│
                    └──────┬──────────────────────┘
                           │
              ┌────────────┼────────────────────────┐
              ▼            ▼                        ▼
        ┌─────────┐  ┌─────────┐           ┌────────────────────┐
        │ 2. CUTLASS│  │ 3. cuTile│           │ 4. Open GPU Kernel │
        │  (CuTe)  │◀─▶│  (DSL)   │           │       Modules      │
        └─────────┘  └─────────┘           └────────────────────┘
              │            │
              └────────────┼────────────────────────┐
                           ▼                        ▼
                     ┌──────────┐               ┌───────────┐
                     │ 5. NCCL  │◀─────────────▶│ 6. NVSHMEM│
                     └──────────┘               └───────────┘
```

### Phase Summary (CU1-CU9)

| Phase | Name | Key Action |
|-------|------|------------|
| CU1 | Pre-flight | Ask user about target hardware (e.g., A100/H100/B200), prior knowledge, language preference. Skip topics already mastered if user opts in. |
| CU2 | Topic Plan | Build the topic dependency DAG. Materialize the prereq chain in the dashboard. |
| CU3 | Tag Standard | Define tag registry: `#topic-cuda-kernels`, `#topic-cutlass`, `#topic-cutile`, `#topic-driver`, `#topic-nccl`, `#topic-nvshmem`, plus `#concept-*`, `#milestone-*`, `#pitfall-*`. English kebab-case. |
| CU4 | Vault Structure | Create `StudyVault/` with `00-Dashboard/` + the 6 numbered topic folders + `99-Exercises/`. |
| CU5 | Dashboard | MOC + Prereq DAG + Glossary + Quick Reference + Pitfall Index. |
| CU6 | Per-Topic Notes | For each of the 6 topics: load `references/topic-{slug}.md` (lazy, one at a time to manage context), then generate concept notes per [templates.md](references/templates.md). |
| CU7 | Hands-On Milestones | Per topic, materialize 3-7 "build/run/measure X" milestones as standalone notes with success criteria. |
| CU8 | Pitfall Notes | Per topic, materialize the pitfalls section as `Pitfalls.md` with fold callouts. |
| CU9 | Interlinking + Self-Review | Cross-link all notes per the prereq DAG, then verify against [quality-checklist.md](references/quality-checklist.md) **Curriculum Mode** section. |

See [curriculum-workflow.md](references/curriculum-workflow.md) for the full procedural detail of each phase.

### Lazy-Loading Discipline for Topic Content (IMPORTANT)

The 6 topic reference files (`topic-*.md`) are large. Load them **one at a time** in Phase CU6 — read `topic-cuda-kernels.md` while authoring `01-CUDA-Kernels/`, drop it from working memory before reading `topic-cutlass.md`, etc. Do not pre-load all 6.

---

## Codebase Mode

> Generate an onboarding StudyVault from a real CUDA / CUTLASS / NCCL / NVSHMEM / driver codebase.
> Full workflow: [codebase-workflow.md](references/codebase-workflow.md). Templates: [cuda-codebase-templates.md](references/cuda-codebase-templates.md).

### Phase Summary (C1-C9)

| Phase | Name | Key Action |
|-------|------|------------|
| C1 | Project Exploration | Detect CUDA toolchain (`nvcc` version target via CMakeLists / setup.py), detect target SM (`sm_70`/`80`/`90`/`100`), identify role of the repo (kernel library / collective lib / driver / app). |
| C2 | Architecture Analysis | Trace a representative kernel from host launch (`<<<>>>` or `cuLaunchKernel`) through device entry, identify the memory hierarchy used, map MMA/TMA usage, identify host-side wrappers. |
| C3 | Tag Standard | Same kebab-case rules; add `#arch-*`, `#sm-*`, `#kernel-*`, `#api-*`, `#mma-*` categories. |
| C4 | Vault Structure | Dashboard, Architecture, per-module, DevOps (CI, build flags), Exercises. |
| C5 | Dashboard | MOC + Module Map + Kernel Surface table + Build Matrix + Getting Started (build & run a representative test). |
| C6 | Module Notes | Per-module note: Purpose, Key Kernels, Host Wrappers, Device Entry, Memory Tiling, Sync Pattern, Dependencies, How to Test. |
| C7 | Exercises | Code reading (trace a kernel), config (toggle SM target / FP type), debugging (`compute-sanitizer`, Nsight Compute), extension (add a new kernel). |
| C8 | Interlinking | Cross-link host wrapper ↔ device kernel ↔ MMA atom ↔ test. |
| C9 | Self-Review | [quality-checklist.md](references/quality-checklist.md) **Codebase Mode** section. |

Common CUDA codebases this mode targets: NVIDIA/cutlass, NVIDIA/nccl, NVIDIA/nvshmem, NVIDIA/cutile-python, NVIDIA/open-gpu-kernel-modules, NVIDIA/cuda-samples, flashinfer-ai/flashinfer, sgl-project/sgl-kernel, huggingface/kernels, plus user repos.

---

## Document Mode

> Transform PDFs (NVIDIA whitepapers, GTC slide decks, programming guides), text, and web pages into study notes. Same workflow as upstream tutor-skills document mode — see [document-workflow.md](references/document-workflow.md).

### Phase Summary (D1-D9)

| Phase | Name |
|-------|------|
| D1 | Source Discovery & Extraction (use `pdftotext` CLI, NEVER `Read` directly on PDF) |
| D2 | Content Analysis |
| D3 | Tag Standard |
| D4 | Vault Structure |
| D5 | Dashboard |
| D6 | Concept Notes |
| D7 | Practice Questions (active recall fold callouts) |
| D8 | Interlinking |
| D9 | Self-Review |

See [document-workflow.md](references/document-workflow.md) for detail.

**Special handling for NVIDIA documents**: when processing the CUDA Programming Guide, PTX ISA, CUTLASS docs, NCCL user guide, or NVSHMEM API guide, prefer reorganizing extracted content **into the 6-topic structure** (same folders as Curriculum mode) rather than mirroring the source's TOC. The 6-topic structure is the canonical taxonomy.

---

## Language

- Match the user's language (Korean → Korean prose, etc.).
- **Tags, keywords, and CUDA identifiers** stay verbatim in English regardless: `cp.async.bulk`, `cute::Layout`, `ncclAllReduce`, `nvshmem_put`, `nvidia.ko`, `GSP`, `WGMMA`, `WPR2`, etc.
- Fold-callout labels can be localized (e.g., Korean: `정답 보기`, English: `View Answer`).

## Pairing with `cuda-tutor`

The generated StudyVault is the input to the `cuda-tutor` skill. Once Phase CU9 / C9 / D9 self-review passes, tell the user:

> "Vault built at `./StudyVault/`. Run the `cuda-tutor` skill in the same directory to start quiz sessions."
