---
name: add-jit-kernel
description: Step-by-step tutorial for adding a new lightweight JIT CUDA kernel to sglang's jit_kernel module
---

# Tutorial: Adding a New JIT Kernel to SGLang

This tutorial covers a lightweight element-wise scale kernel, from choosing JIT over AOT through implementation, Python wrapping, CI registration, testing, benchmarking, and troubleshooting. The full CUDA, Python, test, and benchmark listings are in [the worked example](references/worked-example.md).

## Choose JIT or AOT

Prefer `jit_kernel` for lightweight kernels that don't depend on CUTLASS or another large C++ project. Prefer `sgl-kernel` when such dependencies, wheel-build integration, or torch op registration are required. Kernels depending on FlashInfer, or CUTLASS supplied through FlashInfer, can still use JIT.

## Workflow

1. Generate `.clangd` support with `python -m sglang.jit_kernel` when useful.
2. Implement the CUDA kernel under `python/sglang/jit_kernel/csrc/`.
3. Use `TensorMatcher`, project type aliases, `AlignedVector`, `LaunchKernel`, and `RuntimeCheck` rather than raw CUDA helpers.
4. Add a thin Python wrapper using `cache_once`, `load_jit`, and `make_cpp_args`.
5. Keep runtime values runtime values, and put only true compile-time specializations in the build marker.
6. Register every test and benchmark file with literal `register_cuda_ci(...)` arguments.
7. Run the unified CUDA test and benchmark suites from `test/run_suite.py`.

The reference preserves the complete abstraction catalog and worked source files, including the vectorized kernel, wrapper, tests, and benchmark.

## Project Abstractions

Use `TensorMatcher` for tensor validation, `SymbolicSize` and `SymbolicDevice` for bound dimensions and devices, `AlignedVector` for 128-bit vectorized access, `LaunchKernel` for stream resolution and post-launch checks, and `RuntimeCheck` for runtime assertions. Use the project's dtype aliases and device math helpers. Every `#include <sgl_kernel/...>` line needs a short trailing explanation.

## CI and Verification

JIT tests live under `python/sglang/jit_kernel/tests/`, and benchmarks under `python/sglang/jit_kernel/benchmark/`. CI discovers them through AST parsing in `test/run_suite.py`, so each file needs a module-level registration with literal `est_time` and `suite` strings.

```bash
cd test && python3 run_suite.py --hw cuda --suite stage-b-kernel-unit-1-gpu-large
cd test && python3 run_suite.py --hw cuda --suite stage-b-kernel-benchmark-1-gpu-large
```

Use the nightly suite for expanded test ranges. For failures, check registration first, then source placement and template combinations. Use `CUDA_LAUNCH_BLOCKING=1` or `compute-sanitizer --tool memcheck` for illegal accesses. `run_benchmark` uses CUDA-graph timing by default.
