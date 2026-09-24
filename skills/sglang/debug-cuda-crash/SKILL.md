---
name: debug-cuda-crash
description: Call this skill when you need to debug CUDA crashes in SGLang using kernel API logging
---

## Contents

- [Tutorial](#tutorial-debugging-cuda-crashes-with-kernel-api-logging)
- [Logging levels](#step-1-enable-kernel-api-logging)
- [Reproduction](#step-2-reproduce-an-llm-cuda-crash)
- [Diagnosis](#step-6-common-cuda-errors-and-what-to-check)
- [Tools](#step-7-combine-with-compute-sanitizer)
- [Environment reference](#environment-variables-reference)

# Tutorial: Debugging CUDA Crashes with Kernel API Logging

This tutorial shows you how to debug CUDA crashes and errors in SGLang using the `@debug_kernel_api` logging decorator.

## Goal

When your code crashes with CUDA errors such as illegal memory access, device-side assert, out-of-bounds, or NaN/Inf, use kernel API logging to:
- Capture input tensors BEFORE the crash occurs
- Understand what data caused the problem
- Track tensor shapes, dtypes, and values through the call boundary that triggered the crash
- Detect numerical issues such as NaN, Inf, or obviously wrong shapes

## Why Use Kernel API Logging?

**Problem**: CUDA errors often crash the program before normal debugging output is flushed.

**Solution**: SGLang's `@debug_kernel_api` decorator logs inputs before execution, so you can still see what caused the crash even after the program aborts.

## What Is Covered?

The current logging coverage focuses on the highest-value kernel boundaries in SGLang:
- Custom ops registered through `register_custom_op(...)`
- External custom ops registered through `register_custom_op_from_extern(...)`
- LLM attention, linear, quantization, and multi-platform wrapper entry points
- Diffusion attention impl, linear, rotary, and custom-op wrapper entry points
- Selected direct `torch.ops.sglang.*` hotspots and model-specific bypasses

This means the logging is useful for both LLM and diffusion kernel debugging, but it does not automatically cover every pure PyTorch call in the repository.

## Step 1: Enable Kernel API Logging

### Basic Logging (Function Names Only)

```bash
export SGLANG_KERNEL_API_LOGLEVEL=1
export SGLANG_KERNEL_API_LOGDEST=stdout

python my_script.py
```

Output:
```
================================================================================
[2026-03-19 00:47:06] SGLang Kernel API Call: RMSNorm.forward
================================================================================
[2026-03-19 00:47:06] SGLang Kernel API Call: sglang.quant_method.UnquantizedLinearMethod.apply
================================================================================
[2026-03-19 00:47:06] SGLang Kernel API Call: sglang.custom_op.fused_inplace_qknorm
```

This is a real level-1 excerpt captured from `Qwen/Qwen3-0.6B`.

### Detailed Logging (Inputs with Metadata)

```bash
export SGLANG_KERNEL_API_LOGLEVEL=3
export SGLANG_KERNEL_API_LOGDEST=debug.log

python my_script.py
```

Output in `debug.log`:

> Full listing retained in [the example session reference](references/example-session.md). Apply the command above and compare the referenced output.


This is a real level-3 excerpt captured from `Qwen/Qwen3-0.6B`.

### Full Logging (With Tensor Statistics)

```bash
export SGLANG_KERNEL_API_LOGLEVEL=5
export SGLANG_KERNEL_API_LOGDEST=debug.log

python my_script.py
```

Additional output:

> Complete command/output listing moved to [the example session reference](references/example-session.md#logging-excerpts). Use the surrounding command and expected result as the operational procedure.


This is a real level-5 excerpt captured from `black-forest-labs/FLUX.1-dev`.

### Crash-Safe Dumps (Inputs Saved Before Execution)

Level 10 saves inputs before execution. CUDA graph capture may skip tensor dumps.

## Step 2: Reproduce an LLM CUDA Crash

Create the temporary LLM reproducer and run it at levels 1, 3, and 10. The expected crash, last API boundary, and dump metadata are preserved in [Step 2](references/example-session.md#llm-and-diffusion-reproducers).

> See [Step 2](references/example-session.md#llm-and-diffusion-reproducers) for the full reproducer commands and expected dump contents.

The level-10 run should produce the API entry, `inputs.pt`, exception metadata, and no `outputs.pt` when execution aborts.

Now you should see:
- A log entry for `sglang.custom_op.mock_llm_cuda_crash`
- A dump directory with `inputs.pt`
- `metadata.json` showing `execution_status: "exception"`
- No `outputs.pt`, because the kernel crashed before producing output

For real-model success-path level-10 dumps, it is often easier to temporarily disable CUDA graph and piecewise CUDA graph for the debug run.

## Step 3: Reproduce a Diffusion CUDA Crash

Create a temporary diffusion-side reproducer:


> Full listing retained in [the example session reference](references/example-session.md). Apply the command above and compare the referenced output.


Try level 3:

```bash
SGLANG_KERNEL_API_LOGLEVEL=3 \
SGLANG_KERNEL_API_LOGDEST=/tmp/sglang_diffusion_level3.log \
python3 /tmp/sglang_diffusion_crash.py
```

Try level 10:

```bash
SGLANG_KERNEL_API_LOGLEVEL=10 \
SGLANG_KERNEL_API_LOGDEST=/tmp/sglang_diffusion_level10.log \
SGLANG_KERNEL_API_DUMP_DIR=/tmp/sglang_diffusion_level10_dumps \
python3 /tmp/sglang_diffusion_crash.py
```

If your local environment has unrelated FlashInfer import issues, resolve them in the shell before running the example. The example itself does not set any `FLASHINFER_*` environment variable.

## Step 4: Multi-Process Debugging

When running with multiple GPUs or worker processes, use `%i` in the log path:

```bash
export SGLANG_KERNEL_API_LOGLEVEL=3
export SGLANG_KERNEL_API_LOGDEST=debug_rank_%i.log

torchrun --nproc_per_node=4 my_script.py
```

This creates separate logs such as:
- `debug_rank_12345.log`
- `debug_rank_12346.log`
- `debug_rank_12347.log`
- `debug_rank_12348.log`

Real multi-process example from a 2-GPU `Qwen/Qwen2.5-0.5B-Instruct` run:

```text
/tmp/sglang_kernel_api_validation_multi/qwen_qwen2_5_0_5b_instruct_level3_950201.log
/tmp/sglang_kernel_api_validation_multi/qwen_qwen2_5_0_5b_instruct_level3_950349.log
/tmp/sglang_kernel_api_validation_multi/qwen_qwen2_5_0_5b_instruct_level3_950350.log
/tmp/sglang_kernel_api_validation_multi/qwen_qwen2_5_0_5b_instruct_level3_950351.log
```

You should usually do the same for level-10 dump directories:

```bash
export SGLANG_KERNEL_API_LOGLEVEL=10
export SGLANG_KERNEL_API_LOGDEST=debug_rank_%i.log
export SGLANG_KERNEL_API_DUMP_DIR=/tmp/sglang_kernel_api_dumps_%i
```

This avoids multiple ranks writing into the same dump directory tree.

## Step 5: Filter Level-10 Dumps

If level 10 is too noisy, restrict dumps to specific APIs:

```bash
export SGLANG_KERNEL_API_LOGLEVEL=10
export SGLANG_KERNEL_API_LOGDEST=debug.log
export SGLANG_KERNEL_API_DUMP_DIR=/tmp/sglang_kernel_api_dumps
export SGLANG_KERNEL_API_DUMP_INCLUDE='sglang.custom_op.*'
export SGLANG_KERNEL_API_DUMP_EXCLUDE='*.fake_impl'
```

`SGLANG_KERNEL_API_DUMP_INCLUDE` and `SGLANG_KERNEL_API_DUMP_EXCLUDE` use shell-style wildcard matching.

## Step 6: Common CUDA Errors and What to Check

### Illegal Memory Access or Device-Side Assert

**Typical errors**:
```
RuntimeError: CUDA error: an illegal memory access was encountered
torch.AcceleratorError: CUDA error: device-side assert triggered
```

Use:

```bash
export SGLANG_KERNEL_API_LOGLEVEL=3
```

Check in the logs:
- ✅ Tensor shapes
- ✅ Tensor dtypes
- ✅ CUDA vs CPU device placement
- ✅ Tensor stride / contiguity
- ✅ Whether the failing call has inputs logged but no outputs logged

Typical shape-mismatch pattern:

```text
SGLang Kernel API Call: ...
arg[0]=Tensor(shape=(..., 128), ...)   # ✅ expected dimension
arg[1]=Tensor(shape=(..., 64), ...)    # ❌ mismatch
```

This often points to head-dim, hidden-dim, or cache-layout mismatch rather than a random CUDA failure.

### NaN or Inf

Use:

```bash
export SGLANG_KERNEL_API_LOGLEVEL=5
```

Check:
- `min`
- `max`
- `mean`
- `nan_count`
- `inf_count`

Typical bad pattern:

```text
Tensor(
  ...
  min=-1234567.000000   # ❌ suspiciously large
  max=9876543.000000    # ❌ suspiciously large
  mean=nan              # ❌ bad
  nan_count=128         # ❌ found NaNs
  inf_count=0           # ✅ no Infs here
)
```

This usually means the bad values were already present before the crashing kernel.

### Out of Memory

Use:

```bash
export SGLANG_KERNEL_API_LOGLEVEL=3
```

Check:
- Unexpectedly large tensor shapes
- Batch size
- Sequence length
- Frame count or image resolution in diffusion workloads

Also check whether a supposedly per-token or per-frame tensor accidentally became full-sequence or full-image sized.

Typical bad pattern:

```text
Tensor(
  shape=(1024, 8192, 128, 128)   # ❌ way too large
  ...
)
```

### Example: Spot a Shape Bug from the Log

Suppose the failing API log looks like this:

```text
[2026-03-19 00:47:30] SGLang Kernel API Call: RotaryEmbedding.forward
Positional input arguments:
  arg[0]=Tensor(shape=(1, 8), dtype=torch.int64, ...)
  arg[1]=Tensor(shape=(1, 8, 8, 256), dtype=torch.bfloat16, ...)    # ✅ query
  arg[2]=Tensor(shape=(1, 8, 4, 64), dtype=torch.bfloat16, ...)     # ❌ key head_dim mismatch
```

What this tells you:
- ✅ positions look reasonable
- ✅ query looks plausible
- ❌ key last dimension is inconsistent with the expected rotary/head dimension

That usually means the bug is in projection layout, head packing, or cache format rather than in the rotary kernel itself.

## Step 7: Combine with compute-sanitizer

For harder bugs, combine kernel API logging with CUDA memory checking:

```bash
export SGLANG_KERNEL_API_LOGLEVEL=3
export SGLANG_KERNEL_API_LOGDEST=debug.log

compute-sanitizer --tool memcheck python3 /tmp/sglang_llm_crash.py
```

Use `debug.log` to see the exact inputs that reached the crashing API boundary.

Typical `compute-sanitizer` output:

```text
========= COMPUTE-SANITIZER
========= Invalid __global__ write of size 4 bytes
=========     at 0x1234 in SomeKernel
=========     by thread (256,0,0) in block (10,0,0)
=========     Address 0x... is out of bounds
```

Use the sanitizer output to identify the failing kernel and use `debug.log` to identify the exact tensors that reached the API boundary right before it.

If you need more synchronous host-side error reporting, you can try `CUDA_LAUNCH_BLOCKING=1` as a separate follow-up experiment. It is not part of the default workflow because it changes execution timing and can hide concurrency-related behavior.

## Step 8: Combine with cuda-gdb

For crashes that need a stack trace instead of only memory diagnostics:

```bash
export SGLANG_KERNEL_API_LOGLEVEL=3
export SGLANG_KERNEL_API_LOGDEST=debug.log

cuda-gdb --args python3 /tmp/sglang_llm_crash.py
```

Inside `cuda-gdb`:

```text
(cuda-gdb) run
(cuda-gdb) where
```

Then correlate the backtrace with `debug.log`.

## Step 9: Kernel-Level Debugging with printf()

When you own the CUDA kernel, `printf()` is still useful for narrowing down bad indices, bad launch geometry, or broken state propagation.

Basic pattern:


> Full listing retained in [the example session reference](references/example-session.md). Apply the command above and compare the referenced output.


After launch, force the output to flush:

```python
my_kernel(...)
torch.cuda.synchronize()
```

For warp-specialized kernels, do not blindly print only on `threadIdx.x == 0`. Pick one representative thread per warp or per specialization group instead.

### Warp-Specialized Kernels: Choosing the Right Print Thread

Problem:
- `threadIdx.x == 0` only prints from the first warp in the block
- for warp-specialized kernels, that often misses the warp or group that is actually wrong

Better pattern:

```cpp
__global__ void WarpSpecializedKernel(...) {
  // Example: first lane of each warp
  if ((threadIdx.x % 32) == 0) {
    printf("warp=%d\n", threadIdx.x / 32);
  }
}
```

Or, if the kernel is organized in larger specialization groups, print once per group instead of once per block.

Common mistake:

```cpp
// Only warp 0 prints
if (threadIdx.x == 0) {
  printf("warp=%d\n", threadIdx.x / 32);
}
```

### Quick Reference

| Kernel Type | Print Condition | Notes |
|----------|----------|-------------|
| Simple kernel | `threadIdx.x == 0` | One thread per block is usually enough |
| Warp-specialized kernel | one representative lane per warp | e.g. `threadIdx.x % 32 == 0` |
| Group-specialized kernel | one representative lane per group | choose based on the kernel's scheduling layout |

### Other Kernel Debugging Tools

```cpp
assert(value >= 0.0f && "value must be non-negative");
static_assert(BLOCK_SIZE % 32 == 0, "BLOCK_SIZE must be warp aligned");
```

## Environment Variables Reference

| Variable | Values | Description |
|----------|--------|-------------|
| `SGLANG_KERNEL_API_LOGLEVEL` | `0` | No logging (default) |
|  | `1` | Function names only |
|  | `3` | Inputs and outputs with metadata |
|  | `5` | Level 3 plus tensor statistics |
|  | `10` | Level 5 plus crash-safe tensor dumps |
| `SGLANG_KERNEL_API_LOGDEST` | `stdout` | Log to stdout |
|  | `stderr` | Log to stderr |
|  | `<path>` | Log to file |
|  | `log_%i.txt` | `%i` expands to process ID |
| `SGLANG_KERNEL_API_DUMP_DIR` | `<path>` | Directory for level-10 dumps |
| `SGLANG_KERNEL_API_DUMP_INCLUDE` | wildcard list | Only dump matching API names |
| `SGLANG_KERNEL_API_DUMP_EXCLUDE` | wildcard list | Skip matching API names |

> Additional level-selection guidance is preserved in [Best Practices](references/example-session.md#best-practices).

## Troubleshooting

### No Logs Appear

Check:
1. `echo $SGLANG_KERNEL_API_LOGLEVEL`
2. `echo $SGLANG_KERNEL_API_LOGDEST`
3. Whether the failing path goes through a covered API boundary

### Too Much Output

Reduce the level:

```bash
export SGLANG_KERNEL_API_LOGLEVEL=3
```

### Statistics Are Skipped During CUDA Graph Capture

If you see:
```text
statistics=[skipped: CUDA graph capture in progress]
```

That is expected. Level-5 statistics are intentionally skipped during CUDA graph capture to avoid synchronization side effects.

### Tensor Dumps Are Skipped During CUDA Graph Capture

If you see:
```text
Tensor dump skipped: CUDA graph capture in progress
```

That is also expected. Level-10 dumps require copying tensors to CPU, which is not allowed during CUDA graph capture.
