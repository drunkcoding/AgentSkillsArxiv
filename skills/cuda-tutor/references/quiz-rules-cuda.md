# CUDA Quiz Rules — Stack-Specific Addendum

> Read this AFTER `quiz-rules-shared.md`. Adds CUDA-specific distractor pools, identifier whitelist, and stack-flavored examples. Extends but does NOT override the shared format rules.

## CUDA-Specific Distractor Pools

When picking the 3 wrong options, draw from realistic confusion sets within the same topic:

| Topic | Common distractor pool |
|-------|------------------------|
| CUDA Kernels | `cp.async` vs `cp.async.bulk` (TMA); `__syncthreads()` vs `__syncwarp()`; warp vs block scheduling; L1 vs shared memory bank conflicts; coalesced vs uncoalesced loads; constant vs texture cache; PTX vs SASS |
| CUTLASS / CuTe | `Layout` vs `Stride`; row-major vs column-major; MMA atoms vs Copy atoms; pipeline stages vs splits; `cute::Tensor` vs `cute::Layout`; CuTe DSL vs CUTLASS 2.x kernel |
| cuTile | tile vs warp tile vs CTA tile; cuTile vs Triton vs CuTe; autotuning vs explicit pipeline; Python-side vs device-side ops |
| Open GPU Kernel Modules | `nvidia.ko` vs `nvidia-uvm.ko` vs `nvidia-modeset.ko`; RM vs GSP firmware boundary; UVM page-fault path vs `cudaMallocManaged`; `ioctl` vs sysfs |
| NCCL | `ncclAllReduce` vs `ncclReduceScatter`+`ncclAllGather`; ring vs tree vs NVLink-SHARP; P2P vs SHM vs NET transport; `NCCL_ALGO` vs `NCCL_PROTO`; group calls vs serialized calls |
| NVSHMEM | `nvshmem_put` vs `nvshmem_get`; `nvshmem_quiet` vs `nvshmem_barrier`; on-stream vs host-initiated; IBGDA vs IBRC; symmetric heap vs CUDA managed memory |

## CUDA-Flavored Question-Type Examples

(The five types are defined in `quiz-rules-shared.md`. CUDA examples:)

1. **Factual recall** — "Which warp-scope barrier blocks until all threads of the warp have executed it?"
2. **Conceptual understanding** — "Why does CUTLASS use a multi-stage pipeline for the Hopper mainloop?"
3. **Behavioral prediction** — "What happens when an NCCL group call contains a self-send on rank 0?"
4. **Comparison / distinction** — "What is the difference between `cp.async` and `cp.async.bulk`?"
5. **Debugging scenario** — "Given this `nvshmem_quiet` placement, what race is still possible?"

## CUDA Rephrasing Examples (for 🔴 concept drills)

When rephrasing a previously-missed CUDA concept:
- Change the GPU generation (Ampere → Hopper → Blackwell), change the API surface (CUDA runtime vs driver vs PTX intrinsic), or change the failure scenario.
- Example: previous miss on `cp.async` vs `cp.async.bulk` for 2D tiles → next question asks about the **descriptor-encoded** addressing of `cp.async.bulk.tensor` for a strided 3D tensor.

## CUDA Topic Attribution Examples

For the Topic Attribution Rule in `quiz-rules-shared.md`:
- "How does CUTLASS dispatch a TMA load?" → CUTLASS (TMA is the mechanism used, but the question tests CUTLASS dispatch logic; dual-attribution applies).
- "What is TMA?" → CUDA Kernels.

## CUDA Identifier Whitelist (verbatim in any `{LANG}`)

- **CUDA / PTX**: `cp.async`, `cp.async.bulk`, `wgmma.mma_async`, `__syncwarp`, `__syncthreads`, `cudaMallocAsync`, `cudaStreamCapture`, `mma.sync`, `ldmatrix`
- **CUTLASS / CuTe**: `cute::Layout`, `cute::Tensor`, `make_layout`, `cute::copy`, `cute::gemm`, `cutlass::arch::Mma_Atom`, `cutlass::epilogue::EpilogueOp`, MMA atom names
- **Driver components**: `nvidia.ko`, `nvidia-uvm.ko`, `nvidia-modeset.ko`, `GSP`, `RM`, `kernel-open`
- **NCCL API**: `ncclAllReduce`, `ncclReduceScatter`, `ncclAllGather`, `ncclGroupStart`, `NCCL_ALGO`, `NCCL_PROTO`
- **NVSHMEM API**: `nvshmem_init`, `nvshmem_malloc`, `nvshmem_put`, `nvshmem_get`, `nvshmem_quiet`, `nvshmem_barrier`
