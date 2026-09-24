---
name: debug-cuda-crash
description: Call this skill when you need to debug CUDA crashes in SGLang using kernel API logging
---

# Tutorial: Debugging CUDA Crashes with Kernel API Logging

This tutorial shows how to debug CUDA crashes and errors in SGLang with the `@debug_kernel_api` logging decorator. It captures inputs before execution, records shapes and dtypes, and helps identify numerical or layout errors at the failing kernel boundary.

## Coverage

Logging covers custom ops registered through `register_custom_op(...)` and `register_custom_op_from_extern(...)`, LLM and diffusion attention, linear, quantization, rotary, and wrapper entry points, plus selected direct `torch.ops.sglang.*` hotspots. It does not automatically cover every pure PyTorch call.

## Workflow

1. Start with level 3 logging to capture function inputs and metadata.
2. Reproduce the crash with the smallest LLM or diffusion reproducer available.
3. Use level 5 for NaN or Inf diagnosis, and level 10 for crash-safe input dumps.
4. Use `%i` in log and dump paths for multi-process runs.
5. Restrict level-10 dumps with include and exclude wildcards when output is noisy.
6. Correlate the last logged API boundary with `compute-sanitizer`, `cuda-gdb`, or kernel `printf()` output.

The complete commands, real log excerpts, dump layouts, annotated debugging transcript, kernel print patterns, environment matrix, and troubleshooting output are preserved in [the example session reference](references/example-session.md).

## Logging Levels

```bash
export SGLANG_KERNEL_API_LOGLEVEL=3
export SGLANG_KERNEL_API_LOGDEST=debug.log
python my_script.py
```

Use level 1 for function names only, level 3 for metadata, level 5 for tensor statistics, and level 10 for crash-safe dumps. Level-10 dumps may be skipped during CUDA graph capture, and they preserve the observed call boundary without guaranteeing replay for methods that depend on unserialized module state.

## Reproduction and Diagnosis

The reference includes reproducible LLM and diffusion CUDA-crash scripts. For illegal access or device-side asserts, inspect shapes, dtypes, device placement, contiguity, and whether inputs appear without outputs. For NaN or Inf, inspect min, max, mean, and counts. For out-of-memory failures, inspect batch, sequence, frame, image, and per-token dimensions.

Use `compute-sanitizer --tool memcheck` for invalid accesses, `cuda-gdb` for stack traces, and `torch.cuda.synchronize()` after a kernel with `printf()` when you own the kernel. For warp-specialized kernels, print one representative lane per warp or specialization group instead of only `threadIdx.x == 0`.

## Best Practices

- Start at level 3.
- Use level 5 for numerical issues.
- Use level 10 for crash reproduction, disabling CUDA graph temporarily when successful dumps are needed.
- Log to a file when the process may abort.
- Unset `SGLANG_KERNEL_API_LOGLEVEL` in production. The disabled decorator returns the original callable.

If no logs appear, check both environment variables and whether the failing path crosses a covered API boundary. Statistics and tensor dumps being skipped during CUDA graph capture is expected.
