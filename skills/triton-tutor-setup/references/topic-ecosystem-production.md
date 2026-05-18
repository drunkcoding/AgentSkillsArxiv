# Topic 6: Ecosystem & Production

> **Lazy-load**: read this file ONLY when authoring `06-Ecosystem-Production/` in Phase TU6. Drop from working memory before reading the next topic file.

## Authoritative URLs

- PyTorch Inductor: https://pytorch.org/docs/stable/torch.compiler.html
- Inductor design doc: https://pytorch.org/docs/stable/torch.compiler_inductor_profiling.html
- `proton` profiler (Triton-aware): https://github.com/triton-lang/triton/tree/main/third_party/proton
- Triton AOT (`triton.compile`): https://triton-lang.org/main/python-api/generated/triton.compile.html
- flash-attention (includes Triton kernels): https://github.com/Dao-AILab/flash-attention
- xformers: https://github.com/facebookresearch/xformers
- FBGEMM-GPU (Triton kernels in some paths): https://github.com/pytorch/FBGEMM
- Liger-Kernel (fused training ops): https://github.com/linkedin/Liger-Kernel
- Unsloth (training-time Triton kernels): https://github.com/unslothai/unsloth
- TritonBench: https://github.com/meta-pytorch/tritonbench
- Applied AI (PyTorch Labs): https://github.com/pytorch-labs/applied-ai

## Prerequisites

- **Topic 1: Triton Basics** — you should be able to read someone else's `@triton.jit` kernel.
- **Topic 3: Matmul Patterns** + **Topic 4: Attention & Reductions** — most production Triton kernels are matmul, attention, or norm. Without owning these, the libraries are opaque.
- PyTorch deployment basics (`torch.compile`, `torch.jit`, AOTInductor at a conceptual level).

## Core Concepts / Keywords (Beginner → Expert)

| Stage | Concepts |
|-------|----------|
| **Beginner** | `torch.compile(model)` and Inductor's role, locating Inductor-generated Triton kernels (`TORCHINDUCTOR_CACHE_DIR` / `torch._dynamo.config.verbose=True`), `TRITON_INTERPRET=1` for kernel debugging, `TRITON_CACHE_DIR` for the compile cache, `tl.device_print` for runtime debug printing, `tl.static_print` for compile-time, kernel libraries (flash-attn, xformers) used as drop-ins |
| **Intermediate** | `proton.start("profile.json", hook="triton")` / `proton.activate()` / `proton.deactivate()` profiler, comparing `proton` output to Nsight Compute, Inductor codegen patterns (pointwise fusion, reduction fusion, persistent reductions), `torch._inductor.config.triton.cudagraphs = True`, CUDA Graphs + Triton (graph capture pitfalls with autotune cold-start), `torch._dynamo.config.dynamic_shapes` to reduce Inductor recompile |
| **Advanced** | `triton.compile(kernel, signature=..., constants=...)` AOT compilation producing a `.cubin`, AOT vs JIT tradeoffs (no autotune, fixed shapes, smaller binaries, deployable to systems without PyTorch), `TRITON_PRINT_AUTOTUNING=1` log mining for prod tuning, custom Inductor lowering rules (`torch._inductor.lowering.register_lowering`), `@torch.library.custom_op` to wrap a Triton kernel for `torch.compile`, kernel-library version pinning (Triton ↔ PyTorch compatibility table), AMD ROCm Triton support status |
| **Expert** | Multi-GPU Triton (NCCL + Triton kernels in the same training loop), Triton kernels in distributed inference stacks (vLLM, SGLang, TGI all ship Triton kernels), CI testing strategies (interpreter mode + shape sweeps + golden output regression), contributing a Triton kernel to PyTorch Inductor (lowering rule + test fixture), measuring Triton compile-time impact on first-token latency, hot-reload patterns for serving systems |

## Hands-On Milestones

1. **M1: Inductor codegen inspection** — write a small PyTorch model (3 ops: matmul + ReLU + add); compile with `torch.compile`; locate the generated Triton kernel in the Inductor cache; read it. Success: identify the Inductor-fused pattern.
2. **M2: `tl.device_print` debugging** — add `tl.device_print("dbg", value)` inside a hot loop; run; observe the output. Success: see the print AND notice the throughput drop.
3. **M3: `proton` profile** — write a 3-kernel pipeline (matmul + softmax + matmul); profile with `proton --hook=triton`; load the JSON in Chrome trace viewer. Success: identify per-kernel time and ordering.
4. **M4: AOT compile a kernel** — use `triton.compile(kernel, signature="*fp16, *fp16, *fp32, i32, i32, i32", constants={"BLOCK": 128})`; produce a `.cubin`; load and launch it via `cuda-python` or PyTorch raw launch API. Success: AOT binary produces the same output as the JIT path.
5. **M5: CUDA Graphs + Triton** — wrap your matmul + autotune in a CUDA Graph; benchmark steady-state. Success: graph capture works AFTER autotune has converged (warm cache).
6. **M6: Use flash-attn** — install `flash-attn`; run its Triton variant; compare to your own FA kernel from Topic 4 M5. Success: explain perf gap; identify what flash-attn does differently (warp spec, scheduling).
7. **M7: Dynamic-shape Inductor** — run M1 with `torch._dynamo.config.dynamic_shapes=True`; vary input shape; observe recompile behavior. Success: identify Dynamo guards and which shape changes trigger Inductor recompile.

## Common Pitfalls / Exam Traps

- **Inductor recompile per shape** — every unique input shape (different `dim` or `dtype`) triggers Inductor + Triton recompile. Without `dynamic_shapes`, a varying-batch-size workload thrashes the cache. Use `mark_dynamic` for sequence dims.
- **`tl.device_print` in production** — leaves a slow path in the kernel (serialized print). Always strip before deploy.
- **CUDA Graph captured before autotune** — if you `graph.capture()` while autotune is still benchmarking, you bake in the wrong config. Always warm-up (5-10 calls) before capture.
- **AOT no-autotune trap** — `triton.compile` AOT requires fixed `tl.constexpr` values. You lose autotune. For prod, autotune once offline, hard-code the winner, then AOT.
- **`TRITON_CACHE_DIR` collision** — multi-user systems / shared filesystems / containers may share cache dir; users see each other's stale binaries with different signatures. Always set per-user / per-container cache dir.
- **Inductor fallback to ATen** — Inductor falls back to ATen for unsupported patterns; you assume the slow path is your Triton, when actually Inductor never codegens Triton for that op. Check the generated kernel.
- **Triton version drift** — Triton ships separately from PyTorch but is required for `torch.compile`. Upgrading Triton without checking the PyTorch compat table breaks Inductor. PyTorch pins specific Triton commits.
- **`proton` overhead** — proton hooks add per-kernel overhead. Profile selectively (`proton.activate()` / `proton.deactivate()` around hot regions) rather than always-on.
- **Drop-in kernel library mismatch** — flash-attn / xformers / Liger expect specific input layouts (contiguous, head-major). Passing a non-contiguous or transposed view silently produces wrong results in older versions, errors in newer.
- **CI without GPU** — `TRITON_INTERPRET=1` runs kernels on CPU for unit-test correctness, but cannot catch perf or layout bugs. Production CI needs GPU runners for golden-output regression.

## Cross-Links to Other Topics

- **→ Topic 1 (Triton Basics)** — Inductor codegen uses primitive `tl.load`, `tl.where`, `tl.sum`. Reading the generated code is reading basics.
- **→ Topic 3 (Matmul Patterns)** + **→ Topic 4 (Attention & Reductions)** — most prod Triton time is spent in matmul + attention + norm kernels. The libraries shipped here implement those patterns at high quality.
- **→ Topic 5 (Compiler Internals)** — when Inductor produces a slow kernel, you need to read TTGIR to understand why. Production debugging requires the compiler-internals skills.
- **→ Topic 2 (Tiling & Autotuning)** — Inductor invokes autotune on every codegen kernel; understanding autotune cache + perf models matters for prod compile-time budgets.

## Practice Question Seeds

1. Inductor codegens Triton kernels for pointwise + reduction patterns. When does it fall back to ATen? How do you inspect the generated Triton?
2. `triton.compile(kernel, signature=..., constants=...)` produces a `.cubin`. Why AOT? Limitations vs JIT (no autotune, fixed shapes)?
3. `proton.start("profile.json", hook="triton")` — what does it capture? Compare to Nsight Compute on the same kernel.
4. Wrap a Triton kernel in a CUDA Graph for inference. Re-tuning issue when input shapes change? `cudaGraphExecKernelNodeSetParams` use case.
5. flash-attn, xformers, FBGEMM-GPU — when use these vs hand-write Triton? Maintenance burden?
6. Default `TRITON_CACHE_DIR` location; multi-user contention; how to share cache across processes?
7. `tl.device_print` vs `tl.static_print`. When is each printed (compile-time vs runtime)? Performance impact of `tl.device_print` in a hot kernel?
8. Triton tracks PyTorch releases. Compatibility breaks: which IR layer breaks most often? How to pin a Triton version against a PyTorch wheel?
9. Each unique input shape (dim, dtype) triggers Inductor recompile. Strategies (`torch._dynamo.config.dynamic_shapes`)?
10. Strategies to test Triton kernels in CI without a GPU (interpreter mode, mocked PTX, fixtures).
