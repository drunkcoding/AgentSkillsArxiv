# Triton Question Bank — Seed Pool

> 60 seed questions (10 per topic × 6 topics). These are STARTING POINTS for the quiz tutor — NOT a closed bank. Per `quiz-rules.md`, the tutor must rephrase / rotate context / change GPU backend / change failure scenario when re-using a seed in a follow-up round on the same concept.
>
> Each seed lists the concept it probes; the tutor uses that to update the matching row in `concepts/{topic}.md` after grading.

---

## 1. Triton Basics (10 seeds)

1. **[program_id]** Launch grid `(triton.cdiv(N, BLOCK_SIZE),)` for a vector-add kernel. What does `tl.program_id(axis=0)` return on the 4th block instance? What happens if you call `tl.program_id(axis=1)`?
2. **[mask semantics]** Kernel does `x = tl.load(ptr + offsets, mask=offsets < N)`. For masked-out lanes, what value does `x` contain? Contrast with `tl.load(ptr + offsets, mask=offsets < N, other=0.0)`.
3. **[constexpr]** Mark `BLOCK_SIZE: tl.constexpr` in the signature. What changes about the compilation cache compared to a runtime int arg? What happens if you call the kernel with 3 different `BLOCK_SIZE` values?
4. **[pointer arithmetic]** A 2D kernel computes `a_ptrs = a_ptr + offs_m[:, None] * stride_am + offs_k[None, :] * stride_ak`. What dtype is `a_ptrs`? Why are `[:, None]` and `[None, :]` necessary?
5. **[broadcasting]** `tl.where(mask[:, None], a, 0.0)` where `a` has shape `(M, N)` and `mask` has shape `(M,)`. What gets selected? How is broadcasting different from NumPy here?
6. **[tl.arange]** Why must the argument to `tl.arange(0, BLOCK_SIZE)` be a `tl.constexpr` power of 2? What error does the compiler give for `tl.arange(0, 100)`?
7. **[block_ptr]** Contrast `tl.make_block_ptr(...)` + `tl.advance(...)` with raw pointer arithmetic. When does block_ptr enable TMA lowering on Hopper?
8. **[atomic add]** `tl.atomic_add(ptr, value, mask)` for a reduction across blocks. What ordering guarantee do you get? What happens if two blocks race on the same address?
9. **[tl.where vs Python if]** `if pid == 0: tl.store(...)` — what does the compiler do with the Python `if`? Contrast with `tl.where(pid == 0, x, y)`.
10. **[reshape]** `tl.reshape(x, (BLOCK_M, BLOCK_K))` from a flat `(BLOCK_M * BLOCK_K,)` tile. Restrictions? Does the data layout change?

---

## 2. Tiling & Autotuning (10 seeds)

1. **[Config space]** Define 4 `triton.Config({"BLOCK_SIZE_M": ...}, num_warps=..., num_stages=...)` for a matmul autotune. What's the effective Cartesian product? When does this explode?
2. **[cache key]** `@triton.autotune(configs=..., key=["M", "N", "K"])`. What does `key` actually cache on? Call the kernel with `M=512, N=512, K=512` then `M=512, N=512, K=513` — recompiled?
3. **[num_warps]** A 128×128 BLOCK with `num_warps=4` vs `num_warps=8` — how many threads per warp? How does the compiler distribute the tile across warps?
4. **[num_stages]** `num_stages=3` triggers what compiler pass? What hardware does software pipelining require? Why does `num_stages=1` differ?
5. **[heuristics]** `@triton.heuristics({"BLOCK_SIZE_M": lambda args: ...})` vs `@triton.autotune`. When to use which?
6. **[prune_configs_by]** `prune_configs_by={"perf_model": ..., "top_k": 10}` — what does the perf model decide? When does pruning prevent finding the optimal config?
7. **[reset_to_zero / restore_value]** `@triton.autotune(reset_to_zero=["c_ptr"])` — when does this matter? What goes wrong without it for an accumulator output?
8. **[pre_hook / post_hook]** Autotuner pre-hook example use case (e.g., zeroing an output buffer); failure mode if you forget.
9. **[shape cache miss]** Each unique `M, N, K` combination retriggers autotuning. Strategies to reduce the cost in production?
10. **[warp specialization]** Hopper `num_warps=8` + warp specialization. How does this change the compiler's emitted code vs `num_warps=4`?

---

## 3. Matmul Patterns (10 seeds)

1. **[pid swizzling]** Standard matmul kernel uses `pid // num_pid_n` for row; swizzled version uses `GROUP_SIZE_M` to group `GROUP_SIZE_M` row-blocks together. Why does swizzling improve L2 hit rate for large matmuls?
2. **[tl.dot signature]** `acc = tl.dot(a, b, acc)` vs `acc += tl.dot(a, b)`. Which one does the compiler emit as a fused MMA? Why does the 3-arg form matter?
3. **[FP8 dot]** `tl.dot(a_fp8, b_fp8, acc_fp32, input_precision="ieee")` on Hopper. Required tile shapes? Scale tensor handling?
4. **[split-K]** Implement split-K matmul: each block computes a partial sum over a K-slice, then `tl.atomic_add` into the output. When does split-K beat single-block over K?
5. **[stream-K]** Stream-K vs split-K: what's the load-balancing difference? When does stream-K shine (skinny matmuls, small K)?
6. **[persistent kernel]** Persistent matmul kernel: each program processes multiple tiles in a `while pid < num_tiles` loop. Why does this reduce kernel-launch overhead? How does it interact with the grid size?
7. **[accumulator dtype]** FP16 inputs, FP16 accumulator vs FP32 accumulator — error propagation? When is FP16 acc acceptable?
8. **[A^T B layout]** Transposed-A matmul: how do you change the pointer-stride computation? Does `tl.dot` care about layout, or does the compiler swizzle for you?
9. **[K-loop epilogue]** Fused epilogue (`acc = acc * scale + bias`) inside the matmul kernel — does it stay in registers? When does it spill?
10. **[grouped GEMM]** Grouped GEMM (one kernel processes B small matmuls) — pattern for variable shapes? Pointer arrays vs offsets array?

---

## 4. Attention & Reductions (10 seeds)

1. **[online softmax]** Standard softmax = max → sub → exp → sum → div (2 passes). Online softmax: how does it fuse into a single pass while maintaining numerical stability? Show the running `m`, `l` update.
2. **[FA-2 vs FA-3]** FlashAttention-2 vs FlashAttention-3 — what changed in the KV iteration order? Why does FA-3 (Hopper-targeted) reach higher utilization?
3. **[causal mask]** Causal mask via `tl.where(offs_q[:, None] >= offs_k[None, :], qk, -float("inf"))`. What's the alternative using `tl.load` mask? Which is faster on Ampere vs Hopper?
4. **[block reductions]** `tl.sum(x, axis=0)` over a 2D `(M, N)` tile. Lowers to what underlying primitive? Compare to a warp-shuffle reduction in hand-written CUDA.
5. **[associative_scan]** `tl.associative_scan(x, axis=0, combine_fn=lambda a, b: a + b)` for prefix-sum. How does it compare to a manual `tl.cumsum`? When do you need the explicit combine function (non-add ops)?
6. **[Q/K/V tile shapes]** FlashAttention with `BLOCK_M=128, BLOCK_N=64, HEAD_DIM=128`. Reg pressure problem? Recommended `num_warps` and `num_stages` on H100?
7. **[KV cache loop]** Inference with KV cache: loop K and V over a long sequence. `tl.load(K_ptrs + n_offset * stride_kn)` — what mask handles the tail of unfilled cache?
8. **[dropout]** Dropout inside attention via `tl.rand(seed, offsets) > p`. Determinism guarantees? Why use `philox` and not `randn`?
9. **[FlashDecoding]** Split the sequence across multiple programs for long-context decoding. Reduction pattern (each program writes partial `(m, l, o)`, then a second kernel reduces). Why two kernels?
10. **[layer norm]** Two-pass layer norm vs Welford's online algorithm in a Triton kernel. Numerical precision and register pressure tradeoffs.

---

## 5. Compiler Internals (10 seeds)

1. **[IR pipeline]** Source → TTIR → TTGIR → LLIR → PTX/AMDGCN. What does each stage own? Where does layout assignment happen?
2. **[#blocked layout]** `#triton_gpu.blocked<{sizePerThread = [1, 4], threadsPerWarp = [8, 4], warpsPerCTA = [4, 1], order = [1, 0]}>` — decode this. How many elements per thread? Per warp?
3. **[#mma layout]** `#mma` layout encoding for Hopper `wgmma.mma_async`. How does it differ from Ampere `mma.sync`? Why does Triton emit different encodings per arch?
4. **[#shared layout swizzle]** Swizzled `#shared` layout for matmul tiles. How does it prevent bank conflicts? Compare to a naive row-major shared layout.
5. **[layout conversion]** `convert_layout` op between `#blocked` and `#mma`. When is it free, when expensive (requires smem round-trip)?
6. **[coalescing pass]** Triton's coalescing pass restructures `tl.load` patterns. Example: a strided load gets re-tiled how?
7. **[pipeliner pass]** With `num_stages=3`, the pipeliner inserts `async_copy_global_to_local` + `wait` ops. On Hopper, this becomes TMA; on Ampere, `cp.async`. How does the pass identify pipelinable loads?
8. **[dot_op layout]** `#dot_op<{opIdx = 0, parent = #mma}>` — what does `opIdx` mean? Why does each operand of `tl.dot` need a different layout?
9. **[AMD backend]** AMD MI300 backend: what replaces `wgmma` lowering? How does the `#mfma` layout differ from `#mma`?
10. **[interpreter]** `TRITON_INTERPRET=1` runs the kernel in pure Python. What does it skip? When does it diverge from device behavior (e.g., race conditions, FP precision)?

---

## 6. Ecosystem & Production (10 seeds)

1. **[torch.compile / Inductor]** Inductor codegens Triton kernels for pointwise + reduction patterns. When does it fall back to ATen? How do you inspect the generated Triton?
2. **[AOT]** `triton.compile(kernel, signature=..., constants=...)` produces a `.cubin`. Why AOT? Limitations vs JIT (no autotune, fixed shapes)?
3. **[proton profiler]** `proton.start("profile.json", hook="triton")` — what does it capture? Compare to Nsight Compute on the same kernel.
4. **[CUDA Graphs]** Wrap a Triton kernel in a CUDA Graph for inference. Re-tuning issue when input shapes change? `cudaGraphExecKernelNodeSetParams` use case.
5. **[kernel libraries]** flash-attn, xformers, FBGEMM-GPU — when use these vs hand-write Triton? Maintenance burden?
6. **[TRITON_CACHE_DIR]** Default cache location; multi-user contention; how to share cache across processes?
7. **[debug printing]** `tl.device_print` vs `tl.static_print`. When is each printed (compile-time vs runtime)? Performance impact of `tl.device_print` in a hot kernel?
8. **[Triton release cadence]** Triton tracks PyTorch releases. Compatibility breaks: which IR layer breaks most often? How to pin a Triton version against a PyTorch wheel?
9. **[Inductor recompile]** Each unique input shape (dim, dtype) triggers Inductor recompile. Strategies (`torch._dynamo.config.dynamic_shapes`)?
10. **[CI testing]** Strategies to test Triton kernels in CI without a GPU (interpreter mode, mocked PTX, fixtures).

---

## Rotation Hooks (for the tutor to vary seeds)

When the tutor needs to rephrase a seed (e.g., user already missed it once), apply one of these rotations:

- **Change GPU backend** — NVIDIA Ampere (A100, `mma.sync`) → Hopper (H100, `wgmma`) → AMD MI300 (`mfma`) → Intel PVC; observe how the lowering and layout change.
- **Change API surface** — `@triton.jit` JIT vs `triton.compile` AOT vs Inductor codegen.
- **Change failure scenario** — "what happens if you …" instead of "what does X do" (e.g., autotune cache thrash, illegal memory access from mask off).
- **Change dtype** — FP32 → FP16 → BF16 → FP8 (E4M3 / E5M2); observe `tl.dot` constraints, accumulator choice, layout encoding.
- **Change scale** — single kernel → fused multi-op kernel → `torch.compile`-orchestrated multi-kernel graph.

Document the chosen rotation in the concept-file error note so the next session can rotate further.
