# Curriculum Mode — CUDA Learning Path Workflow

> Generate a 6-topic CUDA StudyVault from scratch. No source files required.
> All vault output MUST stay within CWD.

## Topic Slugs (fixed canonical names)

These slugs must be used consistently in folder names, tags, frontmatter, and concept-file filenames in the paired `cuda-tutor` skill:

| Slug | Display Name | Folder |
|------|--------------|--------|
| `cuda-kernels` | CUDA Kernels | `01-CUDA-Kernels/` |
| `cutlass` | CUTLASS + CuTe | `02-CUTLASS/` |
| `cutile` | cuTile | `03-cuTile/` |
| `open-gpu-kernel-modules` | Open GPU Kernel Modules | `04-Open-GPU-Kernel-Modules/` |
| `nccl` | NCCL | `05-NCCL/` |
| `nvshmem` | NVSHMEM | `06-NVSHMEM/` |

## Phase CU1: Pre-flight

Use `AskUserQuestion` to determine:

1. **Target hardware** — Ampere (sm_80, A100/RTX 30) / Hopper (sm_90, H100) / Blackwell (sm_100, B200) / Ada (sm_89, RTX 40) / mixed. This selects which advanced features (TMA, WGMMA, NVLS) are emphasized.
2. **Prior knowledge** — none / wrote a kernel / shipped CUDA in prod / ML-engineer-using-PyTorch. Skip-or-emphasize toggle per topic.
3. **Audience language** — for prose only (technical identifiers always English).
4. **Scope** — all 6 topics / subset (let them deselect).
5. **Cuthrust-of-day** — optional "I am preparing for X" (e.g., MLPerf submission, NVIDIA interview, OS driver work) — adjusts milestone selection.

Persist answers in the dashboard frontmatter:
```yaml
target_hardware: hopper
prior_knowledge: wrote-a-kernel
audience_language: en
scope: [cuda-kernels, cutlass, nccl, nvshmem]
focus: distributed-llm-training
```

## Phase CU2: Topic Plan

Construct the prereq DAG. Use the canonical chain:

- `cuda-kernels` → `cutlass`
- `cuda-kernels` → `cutile`
- `cuda-kernels` → `open-gpu-kernel-modules`
- `cuda-kernels` → `nccl`
- `cuda-kernels` → `nvshmem`
- `cutlass` ↔ `cutile` (peer; shared `cute::Layout` lineage)
- `nccl` ↔ `nvshmem` (peer; complementary collective vs RMA)

If the user deselected topics in CU1, prune the DAG but keep cross-link annotations.

## Phase CU3: Tag Standard

Registry (English kebab-case, present to user for approval before use):

| Tag Category | Examples | Rule |
|--------------|----------|------|
| Topic | `#topic-cuda-kernels`, `#topic-cutlass`, `#topic-cutile`, `#topic-driver`, `#topic-nccl`, `#topic-nvshmem` | Exactly one per concept note (the owning topic). |
| Concept | `#concept-warp-divergence`, `#concept-tma`, `#concept-wgmma`, `#concept-bank-conflict`, `#concept-ring-allreduce`, `#concept-symmetric-heap` | One or more. Detail tags MUST co-attach the parent topic tag. |
| Milestone | `#milestone-vector-add`, `#milestone-tiled-gemm`, `#milestone-pingpong-nvshmem` | On hands-on milestone notes. |
| Pitfall | `#pitfall-bank-conflict`, `#pitfall-gsp-version-mismatch`, `#pitfall-group-deadlock` | On pitfall index entries. |
| Architecture | `#sm-80`, `#sm-90`, `#sm-100`, `#arch-ampere`, `#arch-hopper`, `#arch-blackwell` | When a concept is arch-specific. |

## Phase CU4: Vault Structure

```
StudyVault/
├── 00-Dashboard/
│   ├── MOC.md
│   ├── Prereq-DAG.md
│   ├── Glossary.md
│   ├── Quick-Reference.md
│   └── Pitfall-Index.md
├── 01-CUDA-Kernels/
├── 02-CUTLASS/
├── 03-cuTile/
├── 04-Open-GPU-Kernel-Modules/
├── 05-NCCL/
├── 06-NVSHMEM/
└── 99-Exercises/
```

Per-topic folder skeleton (created per topic in CU6):

```
0N-<TopicName>/
├── Overview.md             # 1-page summary + concept ladder
├── Concepts/
│   ├── <concept-1>.md
│   ├── <concept-2>.md
│   └── ...
├── Milestones.md           # Hands-on milestones with success criteria
├── Pitfalls.md             # Common mistakes (fold callouts)
└── Resources.md            # Authoritative URLs, papers, code samples
```

## Phase CU5: Dashboard

### `00-Dashboard/MOC.md` (required)

Per the dashboard template in [templates.md](templates.md), with these CUDA-specific sections:

- **Curriculum Order** table — 6 rows, one per topic, with status checkbox and links to `Overview.md`.
- **Prereq DAG** — link to `Prereq-DAG.md` plus inline ASCII diagram.
- **Hardware Target** — pulled from frontmatter (set in CU1).
- **Recommended Order** — explicit "If you have no prior CUDA: start at 1. If you know CUDA and want distributed: jump to 5↔6 after 1." narrative.
- **Tag Index** with the categories from CU3.

### `00-Dashboard/Prereq-DAG.md`

The ASCII DAG plus per-edge justification (1 sentence each):

> CUDA Kernels → CUTLASS: CUTLASS kernels assume comfort with shared memory tiling, `__syncthreads`, and warp-level MMA — none of which CUTLASS explains.

### `00-Dashboard/Glossary.md`

Terms that recur across topics: SM, warp, CTA, TMA, WGMMA, `cp.async`, `cute::Layout`, PE, symmetric heap, ring vs tree allreduce, GSP, RM, UVM. One row per term with the topic that "owns" it.

### `00-Dashboard/Quick-Reference.md`

CUDA-specific reference: peak FLOPS table by GPU (A100/H100/B200), memory bandwidth, NVLink generations, max threads/block, max shared mem/SM, warp size, max grid dims. Pulled from `topic-cuda-kernels.md` resources.

### `00-Dashboard/Pitfall-Index.md`

Aggregated pitfalls from all 6 topics. One table:

| Pitfall | Topic | Severity | → Note |
|---------|-------|----------|--------|
| `__syncthreads` inside divergent branch | CUDA Kernels | 🔥 | `[[01-CUDA-Kernels/Pitfalls#syncthreads-divergent]]` |

## Phase CU6: Per-Topic Notes (LAZY-LOADED)

> **CRITICAL**: load `references/topic-{slug}.md` ONLY when you start authoring that topic. Author the entire topic folder, then drop the reference from working memory before reading the next topic file. Never pre-load all 6.

For each topic, in canonical order:

1. **Read** `references/topic-<slug>.md`.
2. **Create** `0N-<TopicName>/Overview.md` containing:
   - Topic description (2-3 sentences).
   - Concept ladder table (Beginner / Intermediate / Advanced / Expert rows from the reference file).
   - "What you should know before starting" — prereqs section from the reference file.
   - "Where this leads" — cross-links to dependent topics.
3. **Create** one concept note per major concept in the Concepts column of the ladder. Use the concept note template from [templates.md](templates.md). Concept notes MUST include:
   - `source: nvidia-docs` or specific URL from the reference file's Authoritative URLs section.
   - Comparison table (e.g., for `cp.async` vs `cp.async.bulk`).
   - At least one ASCII diagram for flow/hierarchy concepts.
   - `## Related Notes` with `[[wiki-links]]` to peer concepts in the same topic and to the topic's predecessors/successors.
4. **Create** `0N-<TopicName>/Milestones.md` from the reference file's Hands-On Milestones section. For each milestone:
   - **Success criteria** (specific, measurable — e.g., ">2x speedup over naive matmul on A100" not "is faster").
   - **Estimated effort** (≤1h / half-day / multi-day).
   - **Verification command** when applicable (e.g., `compute-sanitizer ./vecadd`, `nvidia-smi -q | grep GSP`).
5. **Create** `0N-<TopicName>/Pitfalls.md` — one fold callout per pitfall (`> [!warning]- <Pitfall>`).
6. **Create** `0N-<TopicName>/Resources.md` — authoritative URLs from the reference file, plus links to existing skills in this repo when relevant:
   - For CUDA Kernels & CUTLASS & cuTile → also link to `skills/flashinfer/add-cuda-kernel/`, `skills/huggingface-kernels/cuda-kernels/`.
   - For codebase deep dives on NCCL or NVSHMEM → link to `skills/sglang/debug-cuda-crash/` and `skills/sglang/generate-profile/`.

## Phase CU7: Hands-On Milestones (cross-topic exercises)

Create `99-Exercises/` notes that intentionally span 2+ topics:

- **`Tiled-GEMM-with-AllReduce.md`** — implement CUTLASS GEMM + NCCL allreduce (topics 1+2+5).
- **`Distributed-Softmax-with-NVSHMEM.md`** — cuTile or raw CUDA softmax with NVSHMEM cross-GPU max (topics 1+3+6).
- **`Driver-Debug-Loop.md`** — instrument open-gpu-kernel-modules to trace a `cuLaunchKernel` event (topics 1+4).

Each cross-topic exercise note links back to the relevant per-topic concept notes.

## Phase CU8: Pitfall Notes

Already created per topic in CU6. Verify they all appear in the Dashboard `Pitfall-Index.md`.

## Phase CU9: Interlinking + Self-Review

1. Verify every concept note has `## Related Notes` populated.
2. Verify every `Overview.md` has cross-links per the prereq DAG.
3. Verify Dashboard MOC links to every concept note.
4. Run the **Curriculum Mode** section of [quality-checklist.md](quality-checklist.md). Fix and re-verify until all checks pass.
5. Report to user: vault location, topic count, total concept-note count, suggested next step (run `cuda-tutor`).
