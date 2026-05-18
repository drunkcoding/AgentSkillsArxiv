# Topic 2: Tiling & Autotuning

> **Lazy-load**: read this file ONLY when authoring `02-Tiling-Autotuning/` in Phase TU6. Drop from working memory before reading the next topic file.

## Authoritative URLs

- `@triton.autotune` reference: https://triton-lang.org/main/python-api/generated/triton.autotune.html
- `triton.Config` reference: https://triton-lang.org/main/python-api/generated/triton.Config.html
- `@triton.heuristics` reference: https://triton-lang.org/main/python-api/generated/triton.heuristics.html
- Matmul tutorial (uses autotune): https://triton-lang.org/main/getting-started/tutorials/03-matrix-multiplication.html
- `num_stages` pipelining design: https://triton-lang.org/main/programming-guide/chapter-3/debugging.html
- AMD `num_warps` guidance (CDNA): https://rocm.docs.amd.com/projects/triton/

## Prerequisites

- **Topic 1: Triton Basics** — you must own `tl.constexpr`, `tl.program_id`, 2D tile loads. Autotune varies `tl.constexpr` parameters; without owning what they do, you can't write valid configs.
- Conceptual understanding of GPU resources: registers, shared memory, warps. (You don't need to write CUDA, but you need to know they exist and are bounded.)

## Core Concepts / Keywords (Beginner → Expert)

| Stage | Concepts |
|-------|----------|
| **Beginner** | `@triton.autotune(configs=[...], key=[...])`, `triton.Config({"BLOCK_SIZE": ...}, num_warps=..., num_stages=...)`, the role of `key=["M", "N"]` as the cache key, single-config baseline (autotune with one config), `TRITON_PRINT_AUTOTUNING=1` to inspect selected config |
| **Intermediate** | `num_warps` (4 / 8 / 16) and its effect on tile sharding, `num_stages` (1 / 2 / 3 / 4) and software pipelining of `tl.load` + `tl.dot`, `@triton.heuristics({"K": lambda args: ...})` for argument-derived constexprs, autotune cache thrash from too-many `key=` dims, `GROUP_SIZE_M` for pid swizzling (cross-link to matmul-patterns) |
| **Advanced** | `prune_configs_by={"perf_model": fn, "top_k": N}` to limit benchmarking, `reset_to_zero=["c_ptr"]` for accumulator buffers, `restore_value=[...]` for preserving inputs, `pre_hook` / `post_hook` for setup/cleanup, warp specialization on Hopper (effects of `num_warps=8` + persistent), tile-shape interaction with `tl.dot` MMA atom sizes |
| **Expert** | Custom perf-model functions that estimate runtime from config + shape, autotune cache serialization (so production deploys don't re-tune), interaction with `torch.compile` Dynamo recompiles, multi-objective tuning (latency vs throughput), heuristic-driven config space pruning, AMD CDNA3 vs NVIDIA Hopper tuning differences |

## Hands-On Milestones

1. **M1: Single-config autotune** — wrap a vector-add kernel with `@triton.autotune` and a single config. Success: kernel still runs; understand the boilerplate.
2. **M2: Multi-config autotune** — same kernel, 4-6 configs varying `BLOCK_SIZE` and `num_warps`. Run with `TRITON_PRINT_AUTOTUNING=1`. Success: print log shows benchmarking + selected config; second call hits cache.
3. **M3: Matmul autotune** — port the tutorial-03 matmul autotune list. Success: ≥90% cuBLAS FP16 throughput on square 4K matmul on A100/H100.
4. **M4: Cache thrash diagnosis** — call your matmul with 20 unique `(M, N, K)` triples; observe autotune re-triggering. Add `triton.cdiv`-quantization to `key=` to coalesce nearby shapes. Success: total cold-start time drops by ≥50%.
5. **M5: `prune_configs_by`** — define a simple perf model (`time ≈ FLOPS / peak`) and prune to top-10 configs. Success: ≥80% of full-search winner with ≤30% of the benchmarking time.
6. **M6: Heuristics for derived constexprs** — use `@triton.heuristics` to compute `BLOCK_SIZE_K = next_pow2(K) // 4`. Success: removes K from `key=` without losing perf.
7. **M7: `reset_to_zero` correctness** — split-K matmul that atomic-adds into the output. Without `reset_to_zero`, second call sees stale data. Add `reset_to_zero=["c_ptr"]`; verify second call correct. Success: 5 sequential calls all produce correct output.

## Common Pitfalls / Exam Traps

- **Autotune cache thrash** — every unique combination of `key` values triggers a new search. Too many key dims (e.g., `key=["M", "N", "K", "stride_a", "stride_b"]`) means every input recompiles. Coalesce with `triton.cdiv` quantization.
- **`num_stages` without pipelinable loads** — software pipelining needs `tl.load` calls inside a loop with predictable strides. Setting `num_stages=3` on a kernel with no such loop is wasted (or compile error).
- **`num_warps` too high → register spill** — `num_warps=16` gives small per-warp tiles but pushes register pressure. Nsight Compute or `--resource-usage` shows the spill. Default to 4 or 8.
- **`reset_to_zero` for non-accumulator output** — accidentally resetting a regular output buffer zero-fills it before every benchmark run, which is fine, but if the kernel partial-writes (skipped lanes), final result is missing those lanes' inputs.
- **`pre_hook` slowness** — pre_hook runs on EVERY benchmarking call during autotune. Heavy pre_hook (e.g., re-allocating tensors) inflates autotune time 100x. Keep pre_hook cheap.
- **Forgetting `key=` entirely** — `@triton.autotune(configs=...)` without `key=` re-tunes on every call. Subtle perf bug.
- **Tile size > problem size** — `BLOCK_SIZE_M=256` on a `M=32` matmul wastes work. Either constraint configs or use heuristics to clamp.
- **Autotune on first call only** — autotune is lazy; first call is slow due to benchmarking. Time the *second* call to measure steady-state perf. Otherwise you misattribute autotune overhead as kernel time.
- **Stale cache across Triton versions** — `TRITON_CACHE_DIR` mixes artifacts from different Triton versions if you don't separate them. Symptoms: weird runtime errors after upgrade.

## Cross-Links to Other Topics

- **→ Topic 3 (Matmul Patterns)** — matmul is THE canonical autotune target. `BLOCK_SIZE_M/N/K`, `GROUP_SIZE_M`, `num_warps`, `num_stages` all originate here.
- **→ Topic 4 (Attention & Reductions)** — FlashAttention kernels heavily autotune. `BLOCK_M` and `BLOCK_N` interact non-trivially with smem and reg pressure on FA-3.
- **→ Topic 5 (Compiler Internals)** — `num_stages` triggers the pipeliner pass; `num_warps` shapes the `#blocked` and `#mma` layouts. Reading TTGIR explains why a config wins.
- **→ Topic 6 (Ecosystem & Production)** — Inductor autotunes its codegen output; understanding `prune_configs_by` is essential for managing compile time in `torch.compile`-heavy workloads.

## Practice Question Seeds

1. Define 4 `triton.Config({"BLOCK_SIZE_M": ...}, num_warps=..., num_stages=...)` for a matmul autotune. What's the effective Cartesian product? When does this explode?
2. `@triton.autotune(configs=..., key=["M", "N", "K"])`. What does `key` actually cache on? Call the kernel with `M=512, N=512, K=512` then `M=512, N=512, K=513` — recompiled?
3. A 128×128 BLOCK with `num_warps=4` vs `num_warps=8` — how many threads per warp? How does the compiler distribute the tile across warps?
4. `num_stages=3` triggers what compiler pass? What hardware does software pipelining require? Why does `num_stages=1` differ?
5. `@triton.heuristics({"BLOCK_SIZE_M": lambda args: ...})` vs `@triton.autotune`. When to use which?
6. `prune_configs_by={"perf_model": ..., "top_k": 10}` — what does the perf model decide? When does pruning prevent finding the optimal config?
7. `@triton.autotune(reset_to_zero=["c_ptr"])` — when does this matter? What goes wrong without it for an accumulator output?
8. Autotuner pre_hook example use case (e.g., zeroing an output buffer); failure mode if you forget.
9. Each unique `M, N, K` combination retriggers autotuning. Strategies to reduce the cost in production?
10. Hopper `num_warps=8` + warp specialization. How does this change the compiler's emitted code vs `num_warps=4`?
