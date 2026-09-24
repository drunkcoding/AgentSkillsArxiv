# Extracted Logging Artifacts

## Contents

- [Output listings](#output-listings)
- [Reference tables](#reference-tables)

## Output Listings

```
================================================================================
[2025-12-18 10:30:45] FlashInfer API Logging - System Information
================================================================================
FlashInfer version: 0.6.0
CUDA toolkit version: 12.1
GPU 0: NVIDIA H100 PCIe
  Compute capability: 9.0 (SM90)
PyTorch version: 2.1.0
================================================================================

================================================================================
[2025-12-18 10:30:46] FlashInfer API Call: batch_decode_with_padded_kv_cache
--------------------------------------------------------------------------------
Positional input arguments:
  arg[0]:
    Tensor(
      shape=(32, 8, 128)
      dtype=torch.bfloat16
      device=cuda:0
      requires_grad=False
      is_contiguous=True
    )
Keyword input arguments:
  kv_cache=
    Tensor(
      shape=(1024, 2, 8, 128)
      dtype=torch.bfloat16
      device=cuda:0
      requires_grad=False
      is_contiguous=True
    )
```

```
  Tensor(
    shape=(32, 8, 128)
    dtype=torch.bfloat16
    device=cuda:0
    requires_grad=False
    is_contiguous=True
    min=-3.125000
    max=4.250000
    mean=0.015625
    nan_count=0
    inf_count=0
  )
```

```
[2025-12-18 10:32:15] FlashInfer API Call: batch_decode_with_padded_kv_cache
Positional input arguments:
  arg[0]:
    Tensor(
      shape=(32, 8, 128)      # Query tensor
      ...
    )
Keyword input arguments:
  kv_cache=
    Tensor(
      shape=(1024, 2, 8, 64)  # ❌ Wrong! Should be (..., 128) not (..., 64)
      ...
    )
```

```
Tensor(
  ...
  min=-1234567.000000     # ❌ Suspiciously large
  max=9876543.000000      # ❌ Suspiciously large
  mean=nan                # ❌ NaN detected
  nan_count=128           # ❌ 128 NaN values!
  inf_count=0
)
```

```cpp
__global__ void MyKernel(const float* input, float* output, int n) {
  int idx = blockIdx.x * blockDim.x + threadIdx.x;

  // Print from one thread to avoid spam
  if (threadIdx.x == 0 && blockIdx.x == 0) {
    printf("n=%d, input[0]=%f\n", n, input[0]);
  }

  if (idx < n) {
    output[idx] = input[idx] * 2.0f;
  }
}
```

```cpp
__global__ void WarpSpecializedKernel(...) {
  // Define your group's representative thread
  // e.g., first thread of each warp: threadIdx.x % 32 == 0
  // e.g., first thread of each 4-warp group: threadIdx.x % 128 == 0

  if (is_group_representative) {
    printf("Group %d processing\n", group_id);
  }
}
```
| Kernel Type | Print Condition | Notes |
|-------------|-----------------|-------|
| Simple kernel | `threadIdx.x == 0` | One thread per block |
| Warp-specialized | One thread per group | Depends on kernel design |
| Variable | Values | Description |
|----------|--------|-------------|
| `FLASHINFER_LOGLEVEL` | `0` | No logging (default) |
|  | `1` | Function names only |
|  | `3` | Inputs/outputs with metadata |
|  | `5` | + Tensor statistics (min/max/mean/nan/inf) |
| `FLASHINFER_LOGDEST` | `stdout` | Log to console (default) |
|  | `stderr` | Log to stderr |
|  | `<path>` | Log to file |
|  | `log_%i.txt` | Multi-process: %i = process ID |

```python
import torch
from flashinfer import batch_decode_with_padded_kv_cache

q = torch.randn(32, 8, 128, dtype=torch.bfloat16, device="cuda")
kv = torch.randn(1024, 2, 8, 64, dtype=torch.bfloat16, device="cuda")  # Wrong dim!

output = batch_decode_with_padded_kv_cache(q, kv)  # ❌ Crashes
```

```
[2025-12-18 10:45:23] FlashInfer API Call: batch_decode_with_padded_kv_cache
Positional input arguments:
  arg[0]:
    Tensor(
      shape=(32, 8, 128)
      dtype=torch.bfloat16
      ...
    )
  arg[1]:
    Tensor(
      shape=(1024, 2, 8, 64)    # ❌ Found it! Last dim should be 128
      dtype=torch.bfloat16
      ...
    )
```
