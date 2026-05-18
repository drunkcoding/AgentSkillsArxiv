# Topic 4: Attention & Reductions

> **Lazy-load**: read this file ONLY when authoring `04-Attention-Reductions/` in Phase TU6. Drop from working memory before reading the next topic file.

## Authoritative URLs

- Tutorial 06 (Fused Attention): https://triton-lang.org/main/getting-started/tutorials/06-fused-attention.html
- Tutorial 05 (Layer Normalization): https://triton-lang.org/main/getting-started/tutorials/05-layer-norm.html
- Tutorial 02 (Fused Softmax): https://triton-lang.org/main/getting-started/tutorials/02-fused-softmax.html
- FlashAttention paper (Dao et al., 2022): https://arxiv.org/abs/2205.14135
- FlashAttention-2 paper (Dao, 2023): https://arxiv.org/abs/2307.08691
- FlashAttention-3 paper (Shah et al., 2024): https://arxiv.org/abs/2407.08608
- `tl.associative_scan` reference: https://triton-lang.org/main/python-api/generated/triton.language.associative_scan.html

## Prerequisites

- **Topic 1: Triton Basics** — masks, 2D tiles, broadcasting.
- **Topic 3: Matmul Patterns** — FlashAttention is two matmuls (Q·K^T, P·V) wrapped around an online softmax. Without owning matmul, FA is opaque.
- Numerical understanding of softmax stability (subtract-max trick).

## Core Concepts / Keywords (Beginner → Expert)

| Stage | Concepts |
|-------|----------|
| **Beginner** | `tl.sum(x, axis=0)`, `tl.max(x, axis=0)`, `tl.min`, `tl.argmax`, fused softmax kernel (load row → subtract max → exp → sum → divide → store), one-row-per-program softmax, numerical stability via subtract-max, `tl.exp` vs `tl.exp2` (latter is faster on most HW) |
| **Intermediate** | Two-pass softmax (max → exp → sum → div), online (single-pass) softmax with running `m` (max) and `l` (sum) update, layer norm two-pass (mean, variance, normalize), RMSNorm (single-pass), `tl.where` for causal masking, dropout via `tl.rand(seed, offsets)`, `tl.philox` deterministic PRNG |
| **Advanced** | FlashAttention-1 forward: tile Q + iterate K, V; maintain `(m, l, o)` per Q-tile, update with online softmax; FA-2 iteration-order change (Q outer, KV inner becomes Q-outer / KV-inner with different reduction granularity), causal mask optimization (skip upper-triangular tiles entirely), KV cache layout for inference, `tl.associative_scan(x, axis=0, combine_fn=...)` for prefix-sum patterns, `tl.cumsum` |
| **Expert** | FlashAttention-3 (Hopper-specific): warp specialization (producer / consumer warpgroups), TMA-backed Q/K/V loads, async WGMMA overlap with softmax compute, FP8 attention with per-block scaling, FlashDecoding (split sequence across programs + second-stage reduction kernel for long-context inference), Paged Attention (block-table indirection for KV cache), backward pass (recompute or save intermediate softmax stats), Welford's algorithm for numerically-stable layer-norm variance, multi-head attention sharding strategies (head-parallel vs sequence-parallel) |

## Hands-On Milestones

1. **M1: Fused softmax** — port tutorial 02. Success: matches `torch.softmax`, beats unfused PyTorch implementation on `(1024, 1024)`.
2. **M2: Layer norm** — port tutorial 05 forward. Success: matches `torch.nn.functional.layer_norm` to FP16 tolerance, `>` PyTorch perf.
3. **M3: RMSNorm** — write a fused RMSNorm (subset of LN). Success: matches `torch.nn.functional.rms_norm`, single-pass kernel.
4. **M4: Online softmax (1-pass)** — rewrite M1 as single-pass with running max/sum. Success: matches reference and uses one less pass over memory.
5. **M5: FlashAttention-2 forward** — implement FA-2 forward (Q-outer, KV-inner) with online softmax. Success: matches `torch.nn.functional.scaled_dot_product_attention` for `(B=2, H=16, N=2048, D=128)` FP16, ≥70% flash-attn library throughput.
6. **M6: Causal mask** — add causal masking to M5 with the "skip upper-triangular tiles" optimization. Success: numerically correct, ≥1.5x faster than masking every element.
7. **M7: FlashDecoding** — implement split-sequence FA for long-context inference; two-kernel reduction. Success: scales for `N=131072` where vanilla FA does not.
8. **M8: Dropout** — add deterministic dropout via `tl.rand(seed, offsets)` inside attention. Success: bit-exact for same seed; correct expected dropout rate.

## Common Pitfalls / Exam Traps

- **Softmax without subtract-max** — FP16 `exp` overflows above ~12. Always subtract per-row max before `exp`.
- **`tl.exp` precision** — `tl.exp` on FP16 inputs can be imprecise. Cast to FP32 for the exp + sum, cast back for output.
- **Online softmax merge bug** — when combining two row-chunks `(m1, l1)` and `(m2, l2)`, the new sum is `l = exp(m1 - m_new) * l1 + exp(m2 - m_new) * l2` where `m_new = max(m1, m2)`. Missing the `exp(...) * lN` correction → wrong softmax.
- **FlashAttention output accumulator scaling** — the `o` accumulator must be rescaled by `exp(m_old - m_new)` on every iteration when the running max updates. Forgetting → silently wrong (off by a per-row factor).
- **Causal mask without skip** — applying `tl.where(q_idx >= k_idx, qk, -inf)` to every block wastes compute on the upper triangle. The "skip" optimization halves the runtime.
- **`tl.associative_scan` vs `tl.cumsum`** — `cumsum` is the addition special case. For non-add ops (max, min, or compound stateful scans), use `associative_scan` with a `combine_fn`.
- **Two-pass LN with FP16 intermediates** — variance in FP16 is unstable for large hidden sizes. Either accumulate in FP32 or use Welford's algorithm.
- **KV cache OOB on tail** — if KV cache length `< BLOCK_N` for the last block, you must mask the `tl.load(K_ptrs)` and `tl.load(V_ptrs)` with `mask=offs_n < kv_len`, else garbage participates in softmax.
- **Dropout non-determinism** — using PyTorch's `torch.rand` outside the kernel and passing as a mask tensor wastes memory and is non-deterministic across kernels. Use `tl.rand(seed, offsets)` for in-kernel deterministic dropout.
- **FA-3 fragment layout mismatch on Hopper** — FA-3 requires specific Q/K/V tile shapes for warp-specialized WGMMA. Off-by-power-of-2 → falls back to slow path.

## Cross-Links to Other Topics

- **→ Topic 3 (Matmul Patterns)** — FlashAttention's Q·K^T and P·V are matmuls; `tl.dot` and tile shapes carry over directly.
- **→ Topic 2 (Tiling & Autotuning)** — FA kernels have `BLOCK_M`, `BLOCK_N`, `BLOCK_HEADDIM` knobs; autotune surfaces are big.
- **→ Topic 5 (Compiler Internals)** — FA-3 on Hopper uses TMA + WGMMA + warp specialization, all visible in TTGIR. Understanding `#mma` and `#shared` layouts helps debug perf.
- **→ Topic 6 (Ecosystem & Production)** — flash-attn library ships official Triton variants; Liger-Kernel and Unsloth ship fused-RMSNorm + RoPE + attention chains.

## Practice Question Seeds

1. Standard softmax = max → sub → exp → sum → div (2 passes). Online softmax: how does it fuse into a single pass while maintaining numerical stability? Show the running `m`, `l` update.
2. FlashAttention-2 vs FlashAttention-3 — what changed in the KV iteration order? Why does FA-3 (Hopper-targeted) reach higher utilization?
3. Causal mask via `tl.where(offs_q[:, None] >= offs_k[None, :], qk, -float("inf"))`. What's the alternative using `tl.load` mask? Which is faster on Ampere vs Hopper?
4. `tl.sum(x, axis=0)` over a 2D `(M, N)` tile. Lowers to what underlying primitive? Compare to a warp-shuffle reduction in hand-written CUDA.
5. `tl.associative_scan(x, axis=0, combine_fn=lambda a, b: a + b)` for prefix-sum. How does it compare to a manual `tl.cumsum`? When do you need the explicit combine function (non-add ops)?
6. FlashAttention with `BLOCK_M=128, BLOCK_N=64, HEAD_DIM=128`. Reg pressure problem? Recommended `num_warps` and `num_stages` on H100?
7. Inference with KV cache: loop K and V over a long sequence. `tl.load(K_ptrs + n_offset * stride_kn)` — what mask handles the tail of unfilled cache?
8. Dropout inside attention via `tl.rand(seed, offsets) > p`. Determinism guarantees? Why use `philox` and not `randn`?
9. Split the sequence across multiple programs for long-context decoding. Reduction pattern (each program writes partial `(m, l, o)`, then a second kernel reduces). Why two kernels?
10. Two-pass layer norm vs Welford's online algorithm in a Triton kernel. Numerical precision and register pressure tradeoffs.

## Cross-Stack Equivalent: CUTLASS Fused MHA

For users who already know CUTLASS Fused MHA / FlashAttention C++ implementations, Triton's FlashAttention kernel uses the same fundamental tile abstractions. Full table: `../../tutor-core/references/cross-stack-rosetta.md` §3 (Compute), §4 (Scheduling), §2 (Memory & Tile).

| RID   | This topic's concept                                          | CUTLASS / CUDA equivalent                                                  |
|-------|---------------------------------------------------------------|----------------------------------------------------------------------------|
| R3-01 | `tl.dot(a, b, acc)` for Q·K^T inside the attention kernel     | CUTLASS Fused MHA inner GEMM atom (`cutlass::arch::Mma_Atom<...>`)         |
| R3-02 | `tl.dot` lowered to WGMMA on Hopper (FA-3 style)              | CUTLASS Hopper Fused MHA using `wgmma.mma_async`                           |
| R3-08 | FP32 `acc = tl.zeros((BM, BN), dtype=tl.float32)` accumulator for the softmax running sum | CUTLASS Fused MHA `ElementAccumulator=float`         |
| R4-05 | `num_stages` for the FA mainloop pipelining                   | CUTLASS Fused MHA `Stages` template parameter                              |
| R2-06 | `tl.load(make_block_ptr(...))` for K/V tiles on Hopper → TMA  | CUTLASS Fused MHA TMA load via `cp.async.bulk.tensor`                      |

Every RID resolves to a row in the canonical `cross-stack-rosetta.md`. When `triton-tutor` includes Attention & Reductions in a session, Phase 3 will pull ≥1 cross-stack question from `cross-stack-rosetta.md`. Note: FlashAttention specifics (online softmax, KV iteration order) are Triton-implementation-level; the cross-stack mapping covers the underlying GEMM atoms and pipelining primitives, not the algorithm itself.
