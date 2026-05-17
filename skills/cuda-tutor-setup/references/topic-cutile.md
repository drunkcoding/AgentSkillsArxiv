# Topic 3: cuTile (Python-First Tile DSL)

> **Lazy-load**: read this file ONLY when authoring `03-cuTile/` in Phase CU6. Drop from working memory before reading the next topic file.
>
> ⚠️ **Preview-quality topic**: cuTile is a recently announced (NVIDIA GTC 2025) Python-first tile programming model. APIs and supported hardware are evolving. Verify the latest version of the docs (URLs below) before authoring concept notes; date-stamp the source URL in each concept-note frontmatter.

## Authoritative URLs

- Main Python repo: https://github.com/NVIDIA/cutile-python
- Docs site: https://docs.nvidia.com/cuda/cutile-python/
- CUDA Tile landing page: https://developer.nvidia.com/cuda/tile
- Quickstart: https://docs.nvidia.com/cuda/cutile-python/quickstart.html
- Tile IR / `tileiras` compiler: https://github.com/NVIDIA/cuda-tile-iras
- TileGym (example kernels): https://github.com/NVIDIA/TileGym

> If any URL above 404s when authoring, drop a `> [!warning]` callout in the concept note and link the GTC 2025 talk archive instead. The cuTile project is moving quickly.

## Prerequisites

- Python 3.10+ proficiency.
- **Topic 1: CUDA Kernels** — must understand thread blocks, shared memory, and the SIMT execution model conceptually. cuTile is NOT thread-level — it replaces threads with tiles — but the underlying hardware constraints remain.
- NumPy / CuPy / PyTorch tensor semantics (shape, dtype, strided arrays).
- **Optional but helpful: Topic 2 (CUTLASS)** — CuTe DSL is the conceptual ancestor; tile programming is the same idea.

## Core Concepts / Keywords (Beginner → Expert)

| Stage | Concepts |
|-------|----------|
| **Beginner** | `@ct.kernel` decorator, `ct.launch(...)`, `ct.bid(n)` (block id along axis n), `ct.load(...)`, `ct.store(...)`, `Tile` (value) vs `Array` (memory), tile shapes must be compile-time powers of 2, `ct.Constant[T]` annotation, `ct.cdiv(M, T)` for grid computation, `ct.TConstant[int]` for kernel parameters |
| **Intermediate** | Tile-level parallelism (block-level only — no threads exposed), elementwise tile ops (`+`, `*`), tile reductions, `ct.mma(...)`, NumPy-like broadcasting, layout via `ct.load(..., index=..., shape=...)`, `PaddingMode`, `order` parameter for memory-layout override, `ct.astype(...)`, `@ct.function` for tile-level callables |
| **Advanced** | Tile IR compilation pipeline (Python → MLIR dialect → Tile IR bytecode → ptxas), `cuda.tile` stable module vs `cuda.tile.experimental`, `Tile.ndim` / `Tile.shape` (compile-time), `ct.range_constexpr` for unrolled loops, DLPack interop, multi-kernel fusion in the compiler, TileGym kernel library, stream-based dispatch |
| **Expert** | Tile IR spec internals (MLIR dialect design), Blackwell SM100 support + WGMMA mapping, JIT cache, debugging with Nsight Compute (tile-level vs SIMT-level metrics), Triton-to-Tile-IR backend interop, custom MMA atoms, Hopper support roadmap, profile-guided autotuning |

## Hands-On Milestones

1. **M1: Install & vector-add** — `pip install cuda-tile[tileiras]`, run `tileiras --version`, run the official vector_add quickstart. Success: prints the correct sum.
2. **M2: Tiled matmul** — implement matmul with `ct.mma` on 2D tiles; verify against NumPy CPU reference. Success: max abs error ≤ 1e-2 for FP16.
3. **M3: Tiled softmax** — load → subtract-max → exp → sum → divide → store, using tile-level reductions. Success: matches `torch.softmax` to FP16 tolerance.
4. **M4: PyTorch DLPack interop** — pass a PyTorch tensor through a cuTile kernel without copying. Success: kernel writes back; `torch.testing.assert_close` passes.
5. **M5: Nsight Compute profile** — profile a cuTile kernel, read the tile-level statistics, identify the bottleneck. Success: justify next tuning step from metrics.
6. **M6: cuTile-Python → cuTile-Julia port** — port a Python kernel to Julia (note 0-indexed vs 1-indexed `ct.bid`). Success: same output, accounting for indexing.
7. **M7: `@ct.function` composition** — extract a reusable tile-level function (e.g., a tile-broadcast reduction) and compose it into multiple kernels. Success: shared codepath verified across 2 kernels.

## Common Pitfalls / Exam Traps

- **Blocks vs tiles** — a *block* executes; a *tile* is a value (data). One block processes multiple tiles. New users confuse the two — different from raw CUDA where threads directly reference data.
- **0-indexed vs 1-indexed `ct.bid`** — Python is 0-indexed; cuTile.jl is 1-indexed. Port mistakes silently produce off-by-one bugs in the first row.
- **Tile dims must be powers of 2** — non-power-of-2 tile shapes compile but produce undefined behavior at runtime. Compiler does not always catch this in stable API.
- **Tiles are immutable** — `result = a + b` creates a new tile; the originals are unchanged. Different from in-place shared-memory writes in raw CUDA.
- **Compiler hardware support is narrow** — `tileiras` historically supported Blackwell (SM100) and Ampere/Ada; Hopper (SM90) lagged. Targeting unsupported hardware = compile error, not graceful fallback.
- **Negative-step ranges** — `range(start, end, -1)` is not supported in tile code. Use explicit reversed indexing.
- **Driver version requirement** — cuTile requires a recent NVIDIA driver (r580+ at time of writing). Older drivers produce a confusing "Tile IR bytecode failed to load" runtime error.
- **DLPack data ownership** — passing PyTorch tensors via DLPack does NOT take ownership. If the tensor is freed before the kernel completes, you get a use-after-free.

## Cross-Links to Other Topics

- **→ Topic 1 (CUDA Kernels)** — cuTile compiles down to CUDA kernels. SM resource limits (registers, shared memory, occupancy) still apply; the compiler hides the scheduling but cannot exceed hardware bounds.
- **→ Topic 2 (CUTLASS)** — CuTe DSL (CUTLASS 4.x Python) and cuTile share the tile-based philosophy. `cute::Layout` ↔ cuTile tile `index`/`shape`. CuTe DSL is generally lower-level and GEMM-focused; cuTile is general-purpose.
- **→ Topic 4 (Open GPU Kernel Modules)** — cuTile kernels go through the same `cuModuleLoad` / `cuLaunchKernel` driver path as any CUDA kernel.
- **→ Topic 5 (NCCL)** — cuTile's tile granularity is the natural payload size for NCCL collectives. Tile-level allreduce composes with cuTile mainloops.
- **→ Topic 6 (NVSHMEM)** — cuTile tiles can be the payload for `nvshmemx_put_block` / `nvshmemx_get_block`. Multi-GPU tile programs combine cuTile compute with NVSHMEM remote-memory access.

## Practice Question Seeds

1. Write a cuTile Python kernel doing 3×3 convolution on an input tile, using `ct.load` / `ct.store` and tile ops. Identify which ops are in tile-space vs array-space.
2. `ct.bid(0)` is 0-indexed in Python but 1-indexed in cuTile.jl. Port a Python kernel to Julia without adjusting `ct.bid(0)` — what happens? Give a concrete example.
3. In cuTile Python, `ct.load(arr, index=(pid,), shape=(T,))`. What happens when `len(arr) % T != 0`? How does `ct.cdiv` interact with this?
4. cuTile tiles are immutable; raw CUDA shared memory is mutable. Compare implications for memory-bound kernels.
5. cuTile compiles via Tile IR → PTX through `tileiras`. Current hardware-support limitations? Compare to `nvcc` PTX path.
6. `ct.mma` on Blackwell maps to WGMMA. Tile-shape requirement for `ct.mma` on SM100? Compare to manual WGMMA scheduling in PTX.
7. `Tile.ndim` and `Tile.shape` are compile-time. Why does this matter for the Tile IR compiler? Contrast PyTorch (runtime shape).
8. cuTile lacks a built-in block-level allreduce. Implement one with tile-level operations (tree reduction sketch).
9. TileGym ships FlashAttention-style tiled matmul kernels. Pick one and trace: array → load → tile ops → store. What tile shapes are used and why?
10. `ct.store` has an `order` parameter. Row-major vs column-major in the cuTile tile model — when do you override the default?
