# Example Session Artifacts

## Contents

- [Logging excerpts](#logging-excerpts)
- [LLM and diffusion reproducers](#llm-and-diffusion-reproducers)
- [Diagnostic outputs](#diagnostic-outputs)
- [Kernel debugging listings](#kernel-debugging-listings)

## Logging Excerpts

```
================================================================================
[2026-03-19 00:47:06] SGLang Kernel API Call: RMSNorm.forward
================================================================================
[2026-03-19 00:47:06] SGLang Kernel API Call: sglang.quant_method.UnquantizedLinearMethod.apply
================================================================================
[2026-03-19 00:47:06] SGLang Kernel API Call: sglang.custom_op.fused_inplace_qknorm
```

```
================================================================================
[2026-03-19 00:47:30] SGLang Kernel API Call: sglang.quant_method.UnquantizedLinearMethod.apply
Positional input arguments:
  arg[0]=QKVParallelLinear(
      repr=QKVParallelLinear(in_features=1024, output_features=4096, bias=False, tp_size=1, gather_output=False)
    )
  arg[1]=Tensor(
      shape=(1, 1024)
      dtype=torch.bfloat16
      device=cuda:0
      requires_grad=False
      is_contiguous=True
    )
  arg[2]=None
Output:
  return=Tensor(
      shape=(1, 4096)
      dtype=torch.bfloat16
      device=cuda:0
      requires_grad=False
      is_contiguous=True
    )
```

```
================================================================================
[2026-03-19 01:00:42] SGLang Kernel API Call: diffusion.quant_method.UnquantizedLinearMethod.apply
Positional input arguments:
  arg[1]=Tensor(
      shape=(1, 77, 768)
      dtype=torch.bfloat16
      device=cuda:0
      requires_grad=False
      is_contiguous=True
      min=-27.250000
      max=28.500000
      mean=0.011723
      nan_count=0
      inf_count=0
    )
Output:
  return=Tensor(
      shape=(1, 77, 2304)
      dtype=torch.bfloat16
      device=cuda:0
      requires_grad=False
      is_contiguous=True
      min=-8.937500
      max=9.375000
      mean=0.009460
      nan_count=0
      inf_count=0
    )
```

```json
{
  "function_name": "RotaryEmbedding.forward",
  "timestamp": "20260319_004821_182",
  "process_id": 919286,
  "execution_status": "completed",
  "input_tensor_keys": ["arg_0", "arg_1", "arg_2"],
  "output_tensor_keys": ["result_0", "result_1"]
}
```

## LLM and Diffusion Reproducers

```bash
python3 - <<'PY'
from pathlib import Path
Path("/tmp/sglang_llm_crash.py").write_text(
    "import torch\\n"
    "import torch.nn.functional as F\\n"
    "from sglang.srt.utils.custom_op import register_custom_op\\n\\n"
    "def _fake_embedding(indices, table):\\n"
    "    return torch.empty((*indices.shape, table.shape[-1]), device=table.device, dtype=table.dtype)\\n\\n"
    "@register_custom_op(op_name='mock_llm_cuda_crash', fake_impl=_fake_embedding)\\n"
    "def mock_llm_cuda_crash(indices, table):\\n"
    "    out = F.embedding(indices, table)\\n"
    "    torch.cuda.synchronize()\\n"
    "    return out\\n\\n"
    "table = torch.randn(4, 8, device='cuda', dtype=torch.float16)\\n"
    "indices = torch.tensor([0, 7], device='cuda', dtype=torch.long)\\n"
    "mock_llm_cuda_crash(indices, table)\\n"
)
PY

SGLANG_KERNEL_API_LOGLEVEL=1 \
SGLANG_KERNEL_API_LOGDEST=/tmp/sglang_llm_level1.log \
python3 /tmp/sglang_llm_crash.py
```

```bash
python3 - <<'PY'
from pathlib import Path
Path("/tmp/sglang_diffusion_crash.py").write_text(
    "import torch\\n"
    "import torch.nn.functional as F\\n"
    "from sglang.multimodal_gen.runtime.layers.utils import register_custom_op\\n\\n"
    "def _fake_embedding(positions, cache):\\n"
    "    return torch.empty((*positions.shape, cache.shape[-1]), device=cache.device, dtype=cache.dtype)\\n\\n"
    "@register_custom_op(op_name='mock_diffusion_cuda_crash', fake_impl=_fake_embedding)\\n"
    "def mock_diffusion_cuda_crash(positions, cache):\\n"
    "    out = F.embedding(positions, cache)\\n"
    "    torch.cuda.synchronize()\\n"
    "    return out\\n\\n"
    "cache = torch.randn(4, 64, device='cuda', dtype=torch.float16)\\n"
    "positions = torch.tensor([0, 9], device='cuda', dtype=torch.long)\\n"
    "mock_diffusion_cuda_crash(positions, cache)\\n"
)
PY

SGLANG_KERNEL_API_LOGLEVEL=1 \
SGLANG_KERNEL_API_LOGDEST=/tmp/sglang_diffusion_level1.log \
python3 /tmp/sglang_diffusion_crash.py
```

## Diagnostic Outputs

### Illegal Memory Access or Device-Side Assert

### NaN or Inf

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

### Out of Memory

### Example: Spot a Shape Bug from the Log

## Kernel Debugging Listings

```cpp
__global__ void MyKernel(const float* input, float* output, int n) {
  int idx = blockIdx.x * blockDim.x + threadIdx.x;

  if (threadIdx.x == 0 && blockIdx.x == 0) {
    printf("n=%d input0=%f\n", n, input[0]);
  }

  if (idx < n) {
    output[idx] = input[idx] * 2.0f;
  }
}
```

### Warp-Specialized Kernels: Choosing the Right Print Thread

```cpp
__global__ void WarpSpecializedKernel(...) {
  // Example: first lane of each warp
  if ((threadIdx.x % 32) == 0) {
    printf("warp=%d\n", threadIdx.x / 32);
  }
}
```

### Quick Reference
| Kernel Type | Print Condition | Notes |
|----------|----------|-------------|
| Simple kernel | `threadIdx.x == 0` | One thread per block is usually enough |
| Warp-specialized kernel | one representative lane per warp | e.g. `threadIdx.x % 32 == 0` |
| Group-specialized kernel | one representative lane per group | choose based on the kernel's scheduling layout |

### Other Kernel Debugging Tools
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

## Best Practices

### 1. Start with Level 3

```bash
export SGLANG_KERNEL_API_LOGLEVEL=3
```

Level 3 is usually enough to catch wrong shapes, wrong dtypes, and wrong devices.

### 2. Use Level 5 for Numerical Issues

```bash
export SGLANG_KERNEL_API_LOGLEVEL=5
```

Use it when you suspect NaN or Inf values.

### 3. Use Level 10 for Crash Reproduction

```bash
export SGLANG_KERNEL_API_LOGLEVEL=10
```

This is the most useful mode when the process crashes before you can inspect live tensors.

If you need successful input/output dumps from a real model run, temporarily disable CUDA graph for that debug session.

When level 10 is too noisy, pair it with `SGLANG_KERNEL_API_DUMP_INCLUDE` / `SGLANG_KERNEL_API_DUMP_EXCLUDE` instead of dumping every covered API.

### 4. Log to File for Crashes

```bash
export SGLANG_KERNEL_API_LOGDEST=crash.log
```

File logs are safer than stdout when the process aborts.

### 5. Disable Logging in Production

```bash
unset SGLANG_KERNEL_API_LOGLEVEL
```

When disabled, the decorator returns the original callable and adds no runtime logging overhead.
