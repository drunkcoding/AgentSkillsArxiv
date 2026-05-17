# Topic 2: CUTLASS + CuTe

> **Lazy-load**: read this file ONLY when authoring `02-CUTLASS/` in Phase CU6. Drop from working memory before reading the next topic file.

## Authoritative URLs

- Main repo: https://github.com/NVIDIA/cutlass
- Docs site: https://docs.nvidia.com/cutlass/
- GEMM API (3.x): https://docs.nvidia.com/cutlass/media/docs/cpp/gemm_api.html
- CuTe Layout Algebra quickstart: https://docs.nvidia.com/cutlass/media/docs/cpp/cute/00_quickstart.html
- CuTe DSL (Python) overview: https://docs.nvidia.com/cutlass/media/docs/pythonDSL/overview.html
- Functionality matrix: https://github.com/NVIDIA/cutlass/blob/main/media/docs/cpp/functionality.md

## Prerequisites

- **Topic 1: CUDA Kernels** — must own CTA tiling, shared memory, warp-level operations.
- C++ templates, SFINAE, type traits, variadic templates (CUTLASS is header-only and heavily templated).
- Linear algebra: GEMM (C = α·A·B + β·C), row-major vs column-major, blocking strategies.
- Tensor Core basics: `mma.sync` operates on 16×16×16 or 8×8×16 fragments; operand layout must be swizzled.

## Core Concepts / Keywords (Beginner → Expert)

| Stage | Concepts |
|-------|----------|
| **Beginner** | `cutlass::gemm::device::Gemm`, `cutlass::gemm::device::GemmUniversal`, layout types (`cutlass::layout::RowMajor`, `cutlass::layout::ColumnMajor`), mixed precision (FP16 inputs + FP32 accum), epilogue concept (linear combination after MMA), cuBLAS-like interface |
| **Intermediate** | Threadblock-level GEMM (CTA tile), warp-level MMA (`cutlass::gemm::warp::MmaTensorOp`), register tiling, smem tile iteration, shared-memory swizzle (bank-conflict avoidance), prologue + mainloop + epilogue structure, `EpilogueOp` template, CUTLASS profiler (`./build/profiler --operation=Gemm ...`) |
| **Advanced** | CUTLASS 3.x collective API (`cutlass::gemm::collective::`), `cute::Layout` (shape:stride), `cute::Tensor`, `cute::Mma_Atom`, `cute::Copy_Atom`, `cute::TiledMma`, `cute::TiledCopy`, layout algebra (`coalesce`, `divide`, `complement`, `composition`), TMA tensors (`cute::SM90_TMA_LOAD`), mainloop pipeline stages, `_sm*` arch-gated headers (e.g., `_sm90.hpp`) |
| **Expert** | CUTLASS 4.x Python DSL (CuTe DSL), `cutlass.cute` module, `@cute.jit` decorator, DLPack interop with PyTorch, JIT compilation pipeline (Python → MLIR → ptxas), NVFP4 / MXFP4 / MXFP6 / MXFP8 block-scaled types, binary (Popcount) types, multi-level GEMM hierarchy (device → kernel → threadblock → warp → thread), CUTLASS instance library generation, Blackwell (SM100) tuning, persistent kernels |

## Hands-On Milestones

1. **M1: Run the profiler** — `./build/tools/profiler/cutlass_profiler --operation=Gemm --m=1024 --n=1024 --k=1024`. Success: prints TFLOPS for the GPU.
2. **M2: Plain FP16 GEMM** — instantiate `cutlass::gemm::device::Gemm<half_t, RowMajor, half_t, ColumnMajor, float, RowMajor, ...>`, multiply two random FP16 matrices, verify against CPU. Success: max abs error ≤ 1e-2.
3. **M3: Mixed-precision** — modify M2 to FP16×FP16+FP32 accum; compare bandwidth vs FP32. Success: TFLOPS ≥ 2× FP32.
4. **M4: Fused bias+ReLU epilogue** — write a custom `EpilogueOp` adding bias and applying ReLU. Success: matches NumPy reference.
5. **M5: Custom Mma_Atom** — build a warp-level MMA with `cute::TiledMma` over a non-standard data type (e.g., FP8 with FP32 accum). Success: passes correctness vs Python reference.
6. **M6: CuTe DSL Python GEMM** — write a `@cute.jit` kernel computing GEMM with `cute.make_layout` / `cute.compose` / `cute.mma_atom`; call from PyTorch via DLPack. Success: matches `torch.matmul`.
7. **M7: Profile-and-tune** — Nsight Compute a CUTLASS GEMM, find the bottleneck (compute-bound vs memory-bound), adjust ThreadblockShape and K-tile to improve utilization. Success: ≥10% TFLOPS gain.

## Common Pitfalls / Exam Traps

- **Layout transposition confusion** — `cutlass::layout::RowMajor` is stride `(N, 1)`; column-major is `(1, M)`. For column-major output GEMM, operands A and B are transposed and swapped. Classic mistake.
- **Swizzle mismatch** — TensorOp instructions require permuted shared-memory layouts. Wrong swizzle → 10× slowdown silently. Know `SwizzleThreadBanking` vs `SwizzleInterleave`.
- **Epilogue assumes row-major** — efficient epilogue path is row-major output only. Column-major output uses a different template path (which transposes internally).
- **CUTLASS 2.x vs 3.x API confusion** — `cutlass::gemm::threadblock::Mma` (2.x) is replaced by `cutlass::gemm::collective::` (3.x). Mixing causes linker errors or wrong results.
- **CuTe DSL dynamic shapes** — `@cute.jit` accepts dynamic shapes but tile dimensions must be powers of 2 AND compile-time constants. Non-power-of-2 silently miscompiles.
- **Warp-level vs thread-level MMA** — `wmma_tensor_op` is warp-level on registers loaded from smem; SIMT thread-level uses scalar fma. Wrong choice = no speedup.
- **Ignoring `--resource-usage`** — kernels exceeding per-SM register/smem limits silently underutilize. Always check.
- **Async copy without barrier** — TMA loads (`cute::tma_load_async`) require an `mbarrier::wait` before the loaded tile is safe to consume.
- **WGMMA pipeline stall** — too few pipeline stages → mainloop waits on WGMMA; too many → smem pressure. CUTLASS tuning guides give starting stage counts per arch.

## Cross-Links to Other Topics

- **→ Topic 1 (CUDA Kernels)** — CUTLASS is a library of CUDA kernels. Every CUTLASS concept maps to a CUDA-level mechanism: CTA tile = thread block, warp tile = warp, swizzle = bank-conflict layout, async copy = `cp.async` / TMA.
- **→ Topic 3 (cuTile)** — cuTile and CuTe DSL share the same tile-based programming philosophy. CuTe's `Layout` concept is the conceptual ancestor of cuTile's tile layout. Mastering `cute::Layout` makes cuTile's `index`/`shape` parameters intuitive.
- **→ Topic 4 (Open GPU Kernel Modules)** — CUTLASS runs in user space; kernels reach the GPU via `cuLaunchKernel` through `libcuda.so` → `nvidia.ko` → GSP firmware.
- **→ Topic 5 (NCCL)** — NCCL kernels are not GEMMs but use the same hardware atoms CUTLASS exposes (`cutlass::arch::*` MMA primitives). In distributed training, CUTLASS GEMMs produce gradients that NCCL all-reduces.
- **→ Topic 6 (NVSHMEM)** — NVSHMEM's tile-granular collectives were designed to compose with CUTLASS-tile-sized payloads in multi-GPU training loops (communication-computation fusion).

## Practice Question Seeds

1. Multiply row-major A (M×K) × column-major B (K×N) → row-major C (M×N). Choose CUTLASS 2.x `cutlass::gemm::device::Gemm` template args; pick ThreadblockShape and WarpShape for A100 (target: 256×128×32).
2. Contrast `cutlass::epilogue::EpilogueOp` vs `cutlass::epilogue::EpilogueNoPadding`. When does the epilogue become the bottleneck?
3. CUTLASS 3.x `cute::TiledMma` combines an `Mma_Atom` with tile dims. Target Blackwell `mma.sync` 16×16×16 fragments in a 64×64 threadblock. How is tiling composed? How many warps participate in one MMA?
4. Purpose of `cute::coalesce` in layout algebra. Given `L = (4,(2,2)):(2,(4,1))`, show `coalesce(L)` and explain why it matters for memory coalescing.
5. `cutlass::gemm::device::GemmUniversal` supports SplitK. When to use `GemmSplitKParallel` vs single-kernel `Gemm`? Tradeoffs in the K dimension?
6. Profiler shows `deviceGEMM` reaches 80% peak FP16 TFLOPS but only 40% peak FP32. Two possible causes; how to confirm with Nsight Compute?
7. CuTe `Layout` `S:D` maps coords to flat indices. Row-major `(M,N)` with strides `(N,1)`: what is `L(2,3)`? How does composition `L1 ∘ L2` enable nested tiling?
8. CuTe DSL `@cute.jit` translates Python to Tile IR via MLIR. What are the current GPU-support limits of the `tileiras` compiler? Compare to the PTX path via `nvcc`.
9. CUTLASS implicit GEMM for convolution (`cutlass::conv::device::ImplicitGemm`) vs direct convolution in CUDA: what tiling strategy aligns it with the GEMM hierarchy?
10. A CUTLASS kernel uses `cutlass::arch::wmma`. On Ampere, max warpgroup size that participates in one `mma.sync`? How does this change on Hopper with WGMMA?
