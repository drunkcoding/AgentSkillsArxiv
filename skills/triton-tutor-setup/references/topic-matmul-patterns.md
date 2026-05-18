# Topic 3: Matmul Patterns

> **Lazy-load**: read this file ONLY when authoring `03-Matmul-Patterns/` in Phase TU6. Drop from working memory before reading the next topic file.

## Authoritative URLs

- Tutorial 03 (Matrix Multiplication): https://triton-lang.org/main/getting-started/tutorials/03-matrix-multiplication.html
- Persistent matmul tutorial: https://triton-lang.org/main/getting-started/tutorials/09-persistent-matmul.html
- FP8 matmul tutorial: https://triton-lang.org/main/getting-started/tutorials/10-block-scaled-matmul.html
- Stream-K paper (Osama et al.): https://arxiv.org/abs/2301.03598
- Split-K technique (CUTLASS docs equivalent): https://github.com/NVIDIA/cutlass/blob/main/media/docs/efficient_gemm.md
- Triton matmul benchmark suite: https://github.com/meta-pytorch/tritonbench

## Prerequisites

- **Topic 1: Triton Basics** — 2D tiles, masks, pointer arithmetic, `tl.constexpr`.
- **Topic 2: Tiling & Autotuning** — matmul without autotune is academic; every real matmul kernel has 5-30 autotune configs.
- Conceptual understanding of cuBLAS / cuTLASS-style tiled GEMM: CTA tile → warp tile → MMA fragment hierarchy.

## Core Concepts / Keywords (Beginner → Expert)

| Stage | Concepts |
|-------|----------|
| **Beginner** | Naive tiled matmul: pid = `tl.program_id(0)`, row/col decomposition `pid_m = pid // num_pid_n`, K-loop accumulation `acc += tl.dot(a, b)`, output store with M/N mask, FP16 inputs + FP32 accumulator, comparison against `torch.mm` |
| **Intermediate** | pid swizzling with `GROUP_SIZE_M` (group rows of `GROUP_SIZE_M` × `num_pid_n` blocks together for L2 reuse), `tl.dot(a, b, acc)` 3-argument form (fused MAC, avoid separate add), `tl.make_block_ptr` for matmul tile pointers, `tl.advance` along K, BF16 input variant, K-tail mask via `tl.load(..., mask=offs_k < K - k, other=0.0)` |
| **Advanced** | Persistent kernels (`while pid < num_tiles` loop, reduces launch overhead), split-K (each block computes partial sum over K-slice, atomic-add to output; requires `reset_to_zero=["c_ptr"]`), stream-K (load-balanced K splits to fix the "wave quantization" tail), FP8 `tl.dot(a_fp8, b_fp8, acc_fp32, input_precision="ieee")` on Hopper with scale tensors, transposed-A / transposed-B variants, fused epilogue (activation, bias, scale) |
| **Expert** | Warp-specialized persistent matmul on Hopper (producer / consumer warps via `num_warps=8`), Hopper WGMMA fragment layout requirements (M-tile must be multiple of 64, N-tile multiple of 8, K-tile multiple of 16 for FP16), TMA descriptor matmul kernels (must use `tl.make_block_ptr`), grouped GEMM (variable-shape batch matmul via offsets array), low-precision integer matmul (INT8, INT4) with scale tensors, dispatch tables that route to specialized kernels per shape regime (square / skinny / batched) |

## Hands-On Milestones

1. **M1: Naive tiled matmul** — implement the basic FP16-input, FP32-acc matmul without swizzling. Success: matches `torch.mm` to FP16 tolerance, reach ≥50% cuBLAS perf at M=N=K=4096.
2. **M2: pid swizzling** — add `GROUP_SIZE_M` swizzling. Success: ≥85% cuBLAS at 4K square.
3. **M3: `tl.make_block_ptr` rewrite** — rewrite M2 with block_ptr + `tl.advance`. Success: same perf, cleaner code, on H100 the TTGIR dump should reference TMA descriptor ops.
4. **M4: Persistent kernel** — convert to persistent with `while pid < num_tiles`. Success: reduces launch overhead for many small matmuls (batch of 256 4K matmuls measurably faster).
5. **M5: Split-K** — implement split-K variant; verify correctness with `reset_to_zero=["c_ptr"]` autotune option. Success: for tall-skinny matmul (M=N=128, K=65536), beat non-split-K by ≥2x.
6. **M6: Stream-K** — implement stream-K (each block claims K-chunks from a global counter). Success: closes the wave-quantization gap on irregular shapes (e.g., M=N=K=3200).
7. **M7: FP8 matmul** — on Hopper, FP8 (E4M3) inputs, FP32 accumulator, per-tensor scale. Success: matches `cublasLtMatmul` FP8 within numerical tolerance, ≥70% of FP8 peak.
8. **M8: Grouped GEMM** — variable-shape batch matmul (e.g., MoE expert routing). Success: matches a loop over `torch.mm` calls.

## Common Pitfalls / Exam Traps

- **No pid swizzling** — naive row-major pid order has poor L2 reuse on large matmuls because consecutive blocks touch different A rows AND different B columns. Swizzling reuses A or B across `GROUP_SIZE_M` blocks within a wave.
- **`acc += tl.dot(a, b)` vs `acc = tl.dot(a, b, acc)`** — older Triton: the 3-arg form fused into one MMA op. Recent Triton: compiler should fuse both, but the 3-arg form is still the canonical idiom and more robust across versions.
- **Accumulator dtype mismatch** — FP16 accumulator drops precision dramatically for large K. Default to FP32 acc unless you know what you're doing.
- **K-tail not masked** — if `K % BLOCK_K != 0`, the last iteration reads OOB. `tl.load(..., mask=k_offs < K - k_start, other=0.0)` is required; `other=0.0` is critical so the `tl.dot` contribution is zero.
- **Stride bug on transposed inputs** — passing `A.T` to the kernel without recomputing strides silently transposes the math. Always pass `A.stride(0)`, `A.stride(1)` AFTER any view operations.
- **Wave quantization** — for `M=N=K=3200` and `BLOCK_M=BLOCK_N=128`, the grid is 25×25=625 blocks but the SM count is 108; the last wave runs 625 - 6*108 = 25 blocks idle on most SMs. Split-K or stream-K fix this.
- **Split-K without `reset_to_zero`** — first call works, second call accumulates onto stale data → wrong answer. Always pair split-K with `reset_to_zero=["c_ptr"]`.
- **FP8 without scale tensors** — FP8 has tiny dynamic range; per-tensor or per-block scale is mandatory for any meaningful accuracy. Hopper FP8 MMA expects specific scale-layout conventions.
- **WGMMA tile-shape mismatch** — on Hopper, FP16 WGMMA requires `M % 64 == 0`, `K % 16 == 0`. Setting `BLOCK_M=48` won't lower to WGMMA — falls back to slower path.
- **Persistent kernel grid sizing** — set grid = `(num_SMs,)` for persistent, not `(num_tiles,)`. Wrong grid size negates the benefit.

## Cross-Links to Other Topics

- **→ Topic 2 (Tiling & Autotuning)** — matmul kernels have the largest autotune surfaces in any Triton codebase. Co-design.
- **→ Topic 4 (Attention & Reductions)** — FlashAttention's Q·K^T and attention·V are matmuls inside the kernel. The patterns here (tile, accumulator, pid swizzle) directly transfer.
- **→ Topic 5 (Compiler Internals)** — `tl.dot` lowers to backend-specific MMA: NVIDIA Ampere `mma.sync`, Hopper `wgmma`, AMD CDNA3 `mfma`. Layout encodings differ; TTGIR dumps reveal the choice.
- **→ Topic 6 (Ecosystem & Production)** — Inductor's matmul codegen lowers to Triton matmul patterns. Liger-Kernel, Unsloth, TritonBench all ship hand-tuned matmul variants.

## Practice Question Seeds

1. Standard matmul kernel uses `pid // num_pid_n` for row; swizzled version uses `GROUP_SIZE_M` to group `GROUP_SIZE_M` row-blocks together. Why does swizzling improve L2 hit rate for large matmuls?
2. `acc = tl.dot(a, b, acc)` vs `acc += tl.dot(a, b)`. Which one does the compiler emit as a fused MMA? Why does the 3-arg form matter?
3. `tl.dot(a_fp8, b_fp8, acc_fp32, input_precision="ieee")` on Hopper. Required tile shapes? Scale tensor handling?
4. Implement split-K matmul: each block computes a partial sum over a K-slice, then `tl.atomic_add` into the output. When does split-K beat single-block over K?
5. Stream-K vs split-K: what's the load-balancing difference? When does stream-K shine (skinny matmuls, small K)?
6. Persistent matmul kernel: each program processes multiple tiles in a `while pid < num_tiles` loop. Why does this reduce kernel-launch overhead? How does it interact with the grid size?
7. FP16 inputs, FP16 accumulator vs FP32 accumulator — error propagation? When is FP16 acc acceptable?
8. Transposed-A matmul: how do you change the pointer-stride computation? Does `tl.dot` care about layout, or does the compiler swizzle for you?
9. Fused epilogue (`acc = acc * scale + bias`) inside the matmul kernel — does it stay in registers? When does it spill?
10. Grouped GEMM (one kernel processes B small matmuls) — pattern for variable shapes? Pointer arrays vs offsets array?

## Cross-Stack Equivalent: CUTLASS + cuTile

For users who already know CUTLASS/CuTe or cuTile, Triton matmul patterns map directly. Full table: `../../tutor-core/references/cross-stack-rosetta.md` §3 (Compute), §4 (Scheduling), §5 (Python Tile DSLs), §2 (Memory & Tile).

| RID   | This topic's concept                                              | CUTLASS / CuTe / cuTile equivalent                                                |
|-------|-------------------------------------------------------------------|------------------------------------------------------------------------------------|
| R3-01 | `tl.dot(a, b, acc)`                                               | CUTLASS `cutlass::arch::Mma_Atom<...>` ; cuTile `cute.mma_atom(...)` (R5-04)       |
| R3-02 | `tl.dot` lowered to `#mma` on Hopper                              | `wgmma.mma_async.sync.aligned.*`                                                   |
| R3-03 | `tl.dot` lowered to `mma.sync` on Ampere                          | `mma.sync.aligned.m16n8k16.row.col.*`                                              |
| R3-05 | FP8 `tl.dot(a_fp8, b_fp8, acc_fp32, input_precision="ieee")`      | CUTLASS FP8 GEMM (`cutlass::float_e4m3_t`, per-tensor scale)                       |
| R3-06 | `tl.dot(a, b, acc)` 3-arg form (fused MMA)                        | CUTLASS epilogue α·MMA + β·C (single fused MAC step)                               |
| R3-07 | `input_precision="tf32"` arg to `tl.dot`                          | CUTLASS `tfloat32_t` accumulator                                                   |
| R3-08 | Accumulator-init dtype in `acc = tl.zeros((BM, BN), dtype=tl.float32)` | CUTLASS `ElementAccumulator` template parameter                              |
| R4-01 | Persistent kernel (`while pid < num_tiles`)                       | CUTLASS persistent kernel scheduler                                                |
| R4-02 | pid swizzling with `GROUP_SIZE_M`                                 | CUTLASS `ThreadblockSwizzle` (e.g., `GemmIdentityThreadblockSwizzle<8>`)           |
| R4-03 | Split-K + `tl.atomic_add` + `reset_to_zero=["c_ptr"]`             | CUTLASS `GemmSplitKParallel`                                                       |
| R4-04 | Stream-K (block claims K-chunks from a global counter)            | CUTLASS stream-K scheduler (Osama et al., 2023)                                    |

Every RID resolves to a row in the canonical `cross-stack-rosetta.md`. When `triton-tutor` includes Matmul Patterns in a session, Phase 3 will pull ≥1 cross-stack question from `cross-stack-rosetta.md`. Matmul is the densest cross-stack topic (~10 mappings); the Rosetta question seeds are heavily concentrated here.
