# Triton Quiz Rules — Stack-Specific Addendum

> Read this AFTER `quiz-rules-shared.md`. Adds Triton-specific distractor pools, identifier whitelist, and stack-flavored examples. Extends but does NOT override the shared format rules.

## Triton-Specific Distractor Pools

When picking the 3 wrong options, draw from realistic confusion sets within the same topic:

| Topic | Common distractor pool |
|-------|------------------------|
| Triton Basics | `tl.program_id(axis)` vs `tl.num_programs(axis)`; `tl.load(ptr, mask)` vs `tl.load(ptr, mask, other)`; pointer arithmetic vs `tl.make_block_ptr`; `tl.arange` vs Python `range`; `tl.constexpr` vs runtime arg; `tl.broadcast_to` vs implicit broadcasting; `tl.where` vs Python `if` |
| Tiling & Autotuning | `triton.Config` vs `triton.heuristics`; `num_warps` vs `num_stages`; `key=[...]` cache key vs `prune_configs_by`; `reset_to_zero` vs `restore_value`; `triton.autotune` vs `triton.jit` cache; pre-hook vs post-hook |
| Matmul Patterns | tiled GEMM pid order vs swizzled pid (`pid_m`/`pid_n` group-of-`GROUP_SIZE_M`); persistent vs non-persistent kernels; split-K vs stream-K; `tl.dot(a, b, acc)` vs `acc = tl.dot(a, b) + acc`; FP8 `tl.dot` scale args; TF32 vs FP32 accumulation |
| Attention & Reductions | online softmax vs two-pass softmax; `tl.associative_scan` vs `tl.cumsum`; FlashAttention-1 vs 2 vs 3 KV iteration order; causal mask via `tl.where` vs `tl.load` mask; block-level reduction (`tl.sum`) vs warp-level shuffle |
| Compiler Internals | TTIR vs TTGIR vs LLIR; layout encodings (`#blocked` vs `#mma` vs `#shared` vs `#dot_op`); `triton-opt` vs `triton-translate`; coalescing pass vs swizzling pass; PTX vs SASS; cuBLAS-style template specialization vs Triton JIT autotuning |
| Ecosystem & Production | `torch.compile` Inductor codegen vs hand-written Triton; AOT (`triton.compile`) vs JIT; `proton` profiler vs Nsight Compute; FBGEMM/xformers/flash-attn vs raw Triton kernels; CUDA Graphs + Triton; `TRITON_INTERPRET=1` vs PTX dump |

## Triton-Flavored Question-Type Examples

(The five types are defined in `quiz-rules-shared.md`. Triton examples:)

1. **Factual recall** — "What does `tl.program_id(axis=0)` return?"
2. **Conceptual understanding** — "Why does pid swizzling improve L2 hit rate in matmul kernels?"
3. **Behavioral prediction** — "What happens when an autotune config has `num_stages=3` but the kernel has no pipelined load?"
4. **Comparison / distinction** — "What is the difference between `tl.constexpr` and a regular kernel argument?"
5. **Debugging scenario** — "Given this `tl.load(ptr, mask)` without `other=`, what does an out-of-bounds element contain?"

## Triton Rephrasing Examples (for 🔴 concept drills)

When rephrasing a previously-missed Triton concept:
- Change the GPU backend (NVIDIA Ampere → Hopper → AMD MI300), change the API surface (`@triton.jit` vs `triton.compile` AOT vs `torch.compile` Inductor), or change the failure scenario.
- Example: previous miss on `tl.dot` operand layout for FP16 → next question asks about the **accumulator layout** for FP8 `tl.dot` on Hopper with `acc_dtype=tl.float32`.

## Triton Topic Attribution Examples

For the Topic Attribution Rule in `quiz-rules-shared.md`:
- "How does the autotuner pick between `BLOCK_SIZE_M=64` and `BLOCK_SIZE_M=128` for a given matmul shape?" → Tiling & Autotuning (matmul is the mechanism used, but the question tests autotuner cache-key logic; dual-attribution applies).
- "What does `tl.dot(a, b, acc)` compute?" → Matmul Patterns.

## Triton Identifier Whitelist (verbatim in any `{LANG}`)

- **Triton language**: `tl.load`, `tl.store`, `tl.dot`, `tl.program_id`, `tl.num_programs`, `tl.arange`, `tl.constexpr`, `tl.where`, `tl.associative_scan`, `tl.cumsum`, `tl.sum`, `tl.max`, `tl.exp`, `tl.make_block_ptr`, `tl.advance`, `tl.atomic_add`, `tl.device_print`
- **Decorators / drivers**: `@triton.jit`, `@triton.autotune`, `@triton.heuristics`, `triton.Config`, `triton.compile`
- **Tuning knobs**: `BLOCK_SIZE_M`, `BLOCK_SIZE_N`, `BLOCK_SIZE_K`, `GROUP_SIZE_M`, `num_warps`, `num_stages`
- **IR layers**: `TTIR`, `TTGIR`, `LLIR`, `PTX`, `AMDGCN`, `#blocked`, `#mma`, `#shared`, `#dot_op`
- **Ecosystem tools**: `torch.compile`, Inductor, `proton`, `TRITON_INTERPRET`, `TRITON_CACHE_DIR`, `TRITON_KERNEL_DUMP`
