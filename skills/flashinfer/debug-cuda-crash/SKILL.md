---
name: debug-cuda-crash
description: Tutorial for debugging CUDA crashes using API logging
---

# Tutorial: Debugging CUDA Crashes with API Logging

Use FlashInfer's `@flashinfer_api` decorator to capture inputs before CUDA execution. This preserves the call boundary, tensor metadata, and optional statistics when a crash prevents ordinary output from being flushed.

## Workflow

1. Start with `FLASHINFER_LOGLEVEL=3` and log to a file.
2. Reproduce the crash and inspect the last API call with inputs but no outputs.
3. Use level 5 for NaN or Inf diagnosis.
4. Use `%i` in log paths for multi-process runs.
5. Correlate API logs with `compute-sanitizer` or `cuda-gdb`.
6. Add targeted kernel `printf()` and synchronize after the launch when you own the kernel.
7. Disable logging after the investigation.

The complete environment-variable matrix, long output listings, annotated shape-mismatch walkthrough, and full debugging session are preserved in [the logging reference](references/logging-reference.md).

## Minimal Setup

```bash
export FLASHINFER_LOGLEVEL=3
export FLASHINFER_LOGDEST=debug.log
python my_script.py
```

Level 1 logs function names, level 3 logs inputs and outputs with metadata, and level 5 adds min, max, mean, NaN, and Inf statistics. File logs are safer than console output when the process aborts.

## Diagnosis

Check shapes, devices, strides, contiguity, and dtypes first. A first failed call with inputs but no outputs usually identifies the failing boundary. Unexpectedly large shapes suggest out-of-memory errors. Statistics with suspicious ranges or nonzero `nan_count` and `inf_count` point to earlier numerical corruption.

## Advanced Tools

```bash
export FLASHINFER_LOGLEVEL=3
export FLASHINFER_LOGDEST=debug.log
compute-sanitizer --tool memcheck python my_script.py
```

Use `cuda-gdb --args python my_script.py` for a stack trace. For warp-specialized kernels, print one representative lane per warp or group, not only `threadIdx.x == 0`, and call `torch.cuda.synchronize()` to flush output.

## Troubleshooting

If logs are missing, verify both environment variables and confirm the API has `@flashinfer_api`. If level 5 is too noisy, return to level 3. Statistics may be skipped during CUDA graph capture to avoid synchronization side effects.
