# CUDA Quiz Design Rules

## Zero-Hint Policy (CRITICAL)

Every question must be answerable ONLY by someone who actually knows the CUDA material.

1. **Option descriptions** NEVER reveal correctness.
   - BAD: `label: "TMA"`, `description: "Hopper bulk async copy engine used to move tiles for WGMMA"` (definition leaks the answer)
   - GOOD: `label: "TMA"`, `description: "Tensor Memory Accelerator"`

2. **No "(Recommended)" tag** on any option.

3. **Randomize** the correct answer's position — never always first or last.

4. **Question phrasing** asks about behavior/purpose/output, not the name of the answer.
   - BAD: "Which Hopper feature uses `cp.async.bulk.tensor` to load tiles?"
   - GOOD: "When loading a 2D tile from global memory into shared memory on H100 using a tensor descriptor, which mechanism is invoked?"

5. **Plausible distractors** must be real CUDA concepts the user could plausibly confuse with the answer (common-misconception based, not absurd).

## CUDA-Specific Distractor Pools

When picking the 3 wrong options, draw from realistic confusion sets within the same topic:

| Topic | Common distractor pool (pick concepts the learner is most likely to confuse) |
|-------|------------------------------------------------------------------------------|
| CUDA Kernels | `cp.async` vs `cp.async.bulk` (TMA); `__syncthreads()` vs `__syncwarp()`; warp vs block scheduling; L1 vs shared memory bank conflicts; coalesced vs uncoalesced loads; constant vs texture cache; PTX vs SASS |
| CUTLASS / CuTe | `Layout` vs `Stride`; row-major vs column-major; MMA atoms vs Copy atoms; pipeline stages vs splits; `cute::Tensor` vs `cute::Layout`; CuTe DSL vs CUTLASS 2.x kernel |
| cuTile | tile vs warp tile vs CTA tile; cuTile vs Triton vs CuTe; autotuning vs explicit pipeline; Python-side vs device-side ops |
| Open GPU Kernel Modules | `nvidia.ko` vs `nvidia-uvm.ko` vs `nvidia-modeset.ko`; RM vs GSP firmware boundary; UVM page-fault path vs cudaMallocManaged; `ioctl` vs sysfs |
| NCCL | `ncclAllReduce` vs `ncclReduceScatter`+`ncclAllGather`; ring vs tree vs NVLink-SHARP; P2P vs SHM vs NET transport; `NCCL_ALGO` vs `NCCL_PROTO`; group calls vs serialized calls |
| NVSHMEM | `nvshmem_put` vs `nvshmem_get`; `nvshmem_quiet` vs `nvshmem_barrier`; on-stream vs host-initiated; IBGDA vs IBRC; symmetric heap vs CUDA managed memory |

## Question Types

1. **Factual recall** — "Which warp-scope barrier blocks until all threads of the warp have executed it?"
2. **Conceptual understanding** — "Why does CUTLASS use a multi-stage pipeline for the Hopper mainloop?"
3. **Behavioral prediction** — "What happens when an NCCL group call contains a self-send on rank 0?"
4. **Comparison / distinction** — "What is the difference between `cp.async` and `cp.async.bulk`?"
5. **Debugging scenario** — "Given this `nvshmem_quiet` placement, what race is still possible?"

## Difficulty Balancing

- **Diagnostic** session: 40% easy, 40% medium, 20% hard.
- **Weak-area drill**: 30% medium, 70% hard.
- **Curriculum-order** session: difficulty matches the topic's place in the chain (foundation = mostly medium; advanced = mostly hard).
- **Hard-mode review**: 100% hard.
- **Cross-topic** drill: at least 1 of the 4 questions probes the interaction (e.g., CUTLASS GEMM split-K reducing via NCCL).

## Drilling Unresolved 🔴 Concepts

When targeting 🔴 concepts from concept files:
- Do NOT repeat the literal previous question.
- Test the same underlying knowledge from a different angle: change the GPU generation (Ampere → Hopper → Blackwell), change the API surface (CUDA runtime vs driver vs PTX intrinsic), or change the failure scenario.
- Example: previous miss on `cp.async` vs `cp.async.bulk` for 2D tiles → next question asks about the **descriptor-encoded** addressing of `cp.async.bulk.tensor` for a strided 3D tensor.

## AskUserQuestion Format

- 4 questions per round, 4 options each, single-select.
- Header: max 12 chars, format `Q1. <tag>` (e.g., `Q1. WarpSync`, `Q2. CuTeLayout`, `Q3. ncclAlgo`, `Q4. nvshmemAPI`).
- Option labels: 1–5 words, preferably the actual CUDA identifier (`__syncwarp()`, `ncclAllReduce`, `cp.async.bulk`).
- Option descriptions: ≤1 sentence, neutral, no give-away.

## File Update Protocol

After grading:
1. Update `concepts/{topic}.md` — add/update concept rows + error notes.
2. Update the dashboard — recalculate topic stats from the concept files.
3. Badges: 🟥 0-39% · 🟨 40-69% · 🟩 70-89% · 🟦 90-100% · ⬜ no data.

## Topic Attribution Rule

If a question spans multiple topics, attribute it to the topic that owns the **primary mechanism** being tested:
- "How does CUTLASS dispatch a TMA load?" → CUTLASS (TMA is the mechanism used, but the question tests CUTLASS dispatch logic; the dual-attribution rule below applies).
- "What is TMA?" → CUDA Kernels.
- Dual-attribution (optional): when a question genuinely tests both, write the concept row in BOTH topic files with the same `Concept` text so progress tracks in both. Mark dual-attributed concepts with a trailing `(↔ {other-topic})` in the concept name.

## Language Rule

All prose (question text, descriptions, explanations, file body) in the user's detected `{LANG}`. **Always** preserve the following verbatim in English regardless of `{LANG}`:
- CUDA / PTX identifiers: `cp.async`, `cp.async.bulk`, `wgmma.mma_async`, `__syncwarp`, `__syncthreads`, `cudaMallocAsync`, `cudaStreamCapture`, etc.
- CUTLASS / CuTe API names: `cute::Layout`, `cute::Tensor`, `make_layout`, `cute::copy`, `cute::gemm`, MMA atom names.
- Driver components: `nvidia.ko`, `nvidia-uvm.ko`, `GSP`, `RM`, `kernel-open`.
- NCCL API: `ncclAllReduce`, `ncclGroupStart`, `NCCL_ALGO`, `NCCL_PROTO`.
- NVSHMEM API: `nvshmem_init`, `nvshmem_malloc`, `nvshmem_put`, `nvshmem_quiet`, `nvshmem_barrier`.

Badge emojis (🟥🟨🟩🟦⬜) and ✅/❌ are universal.
