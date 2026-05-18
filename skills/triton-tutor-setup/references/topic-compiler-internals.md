# Topic 5: Compiler Internals

> **Lazy-load**: read this file ONLY when authoring `05-Compiler-Internals/` in Phase TU6. Drop from working memory before reading the next topic file.

## Authoritative URLs

- Triton compiler source: https://github.com/triton-lang/triton/tree/main/lib
- `lib/Dialect/Triton` (TTIR): https://github.com/triton-lang/triton/tree/main/lib/Dialect/Triton
- `lib/Dialect/TritonGPU` (TTGIR): https://github.com/triton-lang/triton/tree/main/lib/Dialect/TritonGPU
- `lib/Conversion` (TTIR → TTGIR → LLIR lowering): https://github.com/triton-lang/triton/tree/main/lib/Conversion
- `third_party/nvidia` backend: https://github.com/triton-lang/triton/tree/main/third_party/nvidia
- `third_party/amd` backend: https://github.com/triton-lang/triton/tree/main/third_party/amd
- Triton paper (MAPL 2019): https://www.eecs.harvard.edu/~htk/publication/2019-mapl-tillet-kung-cox.pdf
- Triton GTC talks (search "Triton GTC <year>") for layout/encoding overviews.

## Prerequisites

- **Topic 1: Triton Basics** — you need real `@triton.jit` kernels to dump and read.
- **Topic 3: Matmul Patterns** — matmul kernels exercise the most interesting passes (layout assignment, pipeliner, swizzle).
- Conceptual familiarity with MLIR (dialects, ops, attributes). Reading TTGIR is reading MLIR.
- Basic understanding of PTX or AMDGCN assembly is a plus but not required.

## Core Concepts / Keywords (Beginner → Expert)

| Stage | Concepts |
|-------|----------|
| **Beginner** | The 5-stage pipeline: Source (Python) → TTIR → TTGIR → LLIR → PTX/AMDGCN, env vars to dump each (`TRITON_KERNEL_DUMP=1`, `MLIR_ENABLE_DUMP=1`, `LLVM_IR_ENABLE_DUMP=1`), location of dumps (`TRITON_CACHE_DIR/<hash>/`), reading TTIR (tensor-level ops, no layout info), reading TTGIR (layout attributes attached) |
| **Intermediate** | Layout encodings: `#blocked<{sizePerThread, threadsPerWarp, warpsPerCTA, order}>` (default tile layout), `#mma<{...}>` (MMA-fragment layout, backend-specific), `#shared<{...}>` (shared-memory layout with optional swizzle), `#dot_op<{opIdx, parent}>` (operand layout for `tl.dot`), `convert_layout` op (insert smem round-trip when layouts mismatch), `triton-opt` / `triton-translate` CLI tools |
| **Advanced** | Pass pipeline order: combine → coalesce → layout-assignment → pipeliner → prefetch → optimize-dot-operands → remove-layout-conversions → reduce-data-duplication → decompose-conversions, NVIDIA backend lowering (TTGIR → NVVM → PTX): MMA atom selection (`mma.sync` for Ampere, `wgmma.mma_async` for Hopper), TMA descriptor generation (Hopper, requires `tl.make_block_ptr`), `cp.async` insertion for pipelined loads, AMD backend (TTGIR → ROCDL → AMDGCN): MFMA atom selection on CDNA3 |
| **Expert** | Writing custom passes (C++ MLIR), adding a new backend, encoding-conversion cost model, warp-specialization pass (Hopper producer/consumer split via `num_warps=8` plus annotations), shared-memory allocator (size + layout), `triton-opt --convert-triton-to-tritongpu` invocation, contributing patches (CI gates, tests), interpreter implementation (`TRITON_INTERPRET` Python path), interaction with PyTorch Inductor's codegen patterns |

## Hands-On Milestones

1. **M1: Dump and read TTIR** — pick a vector-add kernel; `TRITON_KERNEL_DUMP=1 MLIR_ENABLE_DUMP=1 python kernel.py`; locate the TTIR in `$TRITON_CACHE_DIR/...`. Success: open the file, identify the kernel function and the `tt.load` / `tt.store` ops.
2. **M2: Read TTGIR layouts** — for a matmul kernel, locate TTGIR; identify the `#blocked` layout on load values and the `#mma` layout on `tt.dot`. Success: explain each tuple member (`sizePerThread`, `threadsPerWarp`, `warpsPerCTA`).
3. **M3: Trace `convert_layout`** — find a `convert_layout` op in the TTGIR; explain WHY (layout mismatch between source and consumer). Success: identify whether it's smem-round-trip or register-shuffle.
4. **M4: PTX/SASS bridge** — after TTGIR, locate the final PTX (or `.cubin` disassembled with `cuobjdump --dump-sass`). Identify the WGMMA / MMA instructions. Success: count the MMAs and reason about utilization.
5. **M5: Pipeliner pass** — change `num_stages=1` → `num_stages=3` on a matmul; dump TTGIR before and after; identify the inserted `async_copy_global_to_local` + `wait` ops. Success: explain the producer/consumer wait dependency.
6. **M6: AMD backend** — same matmul on an MI300; dump TTGIR; identify `#mfma` layout, `triton_amd_gpu.upcast_mxfp` or similar AMD-specific ops. Success: contrast with the NVIDIA dump from M4.
7. **M7: `triton-opt` standalone** — extract a TTIR file and run `triton-opt --convert-triton-to-tritongpu="num-warps=4 threads-per-warp=32" file.ttir`. Success: get a TTGIR file independent of the Python frontend.

## Common Pitfalls / Exam Traps

- **Confusing TTIR and TTGIR** — TTIR has tensor-level ops with NO layout attributes; TTGIR has the same ops with layout encodings attached. People conflate them.
- **`convert_layout` cost asymmetry** — a `convert_layout` between two `#blocked` layouts may be a free register shuffle, but between `#blocked` and `#mma` it usually involves a smem round-trip (slow). Reading TTGIR without knowing the cost model leads to wrong perf guesses.
- **Pipeliner needs loop-carried recognizable loads** — `num_stages > 1` only takes effect if the compiler can identify pipelinable loads in the loop. Conditional loads or pointer indirection often disable pipelining silently.
- **Hopper TMA fallback** — TMA descriptor generation requires `tl.make_block_ptr` AND the right tile shapes. Raw pointer-arithmetic kernels fall back to `cp.async` even on Hopper.
- **Stale `TRITON_CACHE_DIR`** — Triton caches across runs by hash of (source, signature, configs). If you edit a kernel but the hash doesn't change due to a subtle issue (e.g., an imported helper), you get a stale binary. Nuke the cache when in doubt.
- **`MLIR_ENABLE_DUMP` is verbose** — dumps EVERY pass; you'll get dozens of TTGIR files. Use `triton-opt --print-ir-after=<pass>` for targeted dumping in a custom build.
- **Warp specialization opacity** — on Hopper with `num_warps=8` + persistent kernel, the compiler may emit producer-consumer warp split. This is visible in TTGIR via `triton_nvidia_gpu.warp_specialize` ops; missing it explains a perf cliff.
- **Backend-specific encodings have different semantics** — `#mma` on NVIDIA encodes WGMMA/Ampere-MMA fragment layout; `#mfma` on AMD encodes MFMA fragment layout. Tuple members are different per backend.
- **PTX vs SASS divergence** — PTX is virtual ISA; the actual SASS instructions ptxas emits can reorder, fuse, or split. Comparing two PTX files without checking SASS misses real differences.
- **Interpreter ≠ device** — `TRITON_INTERPRET=1` skips IR generation entirely and runs the kernel in pure Python. Useful for logic bugs, USELESS for layout / perf / race-condition debugging.

## Cross-Links to Other Topics

- **→ Topic 1 (Triton Basics)** — every `tl.*` primitive has a TTIR op; reading TTIR teaches you what the Python is really doing.
- **→ Topic 2 (Tiling & Autotuning)** — `num_warps` shapes `#blocked` and `#mma` warp dims; `num_stages` triggers the pipeliner. Autotune choices manifest in IR.
- **→ Topic 3 (Matmul Patterns)** — matmul kernels exercise WGMMA / MMA / MFMA lowerings most directly. The whole layout machinery exists to make matmul fast.
- **→ Topic 6 (Ecosystem & Production)** — debugging Inductor-generated Triton requires the same IR-reading skills. `proton` profiler annotates by Triton kernel, but IR is needed to attribute hot spots.

## Practice Question Seeds

1. Source → TTIR → TTGIR → LLIR → PTX/AMDGCN. What does each stage own? Where does layout assignment happen?
2. `#triton_gpu.blocked<{sizePerThread = [1, 4], threadsPerWarp = [8, 4], warpsPerCTA = [4, 1], order = [1, 0]}>` — decode this. How many elements per thread? Per warp?
3. `#mma` layout encoding for Hopper `wgmma.mma_async`. How does it differ from Ampere `mma.sync`? Why does Triton emit different encodings per arch?
4. Swizzled `#shared` layout for matmul tiles. How does it prevent bank conflicts? Compare to a naive row-major shared layout.
5. `convert_layout` op between `#blocked` and `#mma`. When is it free, when expensive (requires smem round-trip)?
6. Triton's coalescing pass restructures `tl.load` patterns. Example: a strided load gets re-tiled how?
7. With `num_stages=3`, the pipeliner inserts `async_copy_global_to_local` + `wait` ops. On Hopper, this becomes TMA; on Ampere, `cp.async`. How does the pass identify pipelinable loads?
8. `#dot_op<{opIdx = 0, parent = #mma}>` — what does `opIdx` mean? Why does each operand of `tl.dot` need a different layout?
9. AMD MI300 backend: what replaces `wgmma` lowering? How does the `#mfma` layout differ from `#mma`?
10. `TRITON_INTERPRET=1` runs the kernel in pure Python. What does it skip? When does it diverge from device behavior (e.g., race conditions, FP precision)?

## Cross-Stack Equivalent: PTX / SASS + CuTe Layouts

For users who already know the CUDA compilation pipeline, Triton's compiler internals are conceptually parallel. Full table: `../../tutor-core/references/cross-stack-rosetta.md` §6 (Compiler & Profiling), §2 (Memory & Tile), §3 (Compute).

| RID   | This topic's concept                                              | CUDA / CUTLASS equivalent                                                |
|-------|-------------------------------------------------------------------|--------------------------------------------------------------------------|
| R6-01 | TTIR → TTGIR → LLIR → PTX/AMDGCN pipeline                         | `.cu` → PTX → SASS pipeline (via `nvcc` + `ptxas`)                       |
| R6-02 | TTIR (explicit frontend dialect)                                  | C++ templates as the CUTLASS "frontend" (no separate dialect)            |
| R6-03 | TTGIR (carries layout encodings `#blocked`/`#mma`/`#shared`/`#dot_op`) | PTX (carries thread/warp/cta abstractions, different abstraction level) |
| R6-04 | `TRITON_KERNEL_DUMP=1`, `triton-opt`, `triton-translate`          | `cuobjdump`, `nvdisasm`, `ptxas -v`                                      |
| R2-03 | `#shared` layout encoding (swizzle attribute)                     | CuTe `cute::Swizzle<B, M, S>` template                                   |
| R2-04 | `#blocked` layout encoding (per-thread fragment)                  | CuTe register-resident `Layout`                                          |
| R2-05 | `#dot_op` layout encoding (MMA-ready operand)                     | CUTLASS warp-MMA fragment layout (operand A/B/C)                         |
| R2-12 | Triton swizzling pass (between TTIR and TTGIR)                    | CUTLASS `cute::Swizzle` parameter triple (compile-time choice)           |

Every RID resolves to a row in the canonical `cross-stack-rosetta.md`. When `triton-tutor` includes Compiler Internals in a session, Phase 3 will pull ≥1 cross-stack question from `cross-stack-rosetta.md`.
