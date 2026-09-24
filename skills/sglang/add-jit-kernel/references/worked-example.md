# Extracted Artifacts

## Contents

- [Code and output listings](#code-and-output-listings)

## Code and Output Listings

```cpp
auto N = SymbolicSize{"num_elements"};
auto device = SymbolicDevice{};
device.set_options<kDLCUDA>();
TensorMatcher({N})  //
    .with_dtype<fp16_t>()
    .with_device<kDLCUDA>(device)
    .verify(dst)
    .verify(src);  // same shape, dtype, device as dst
const size_t n = N.unwrap();
const DLDevice dev = device.unwrap();
```

```cpp
#include <sgl_kernel/tensor.h>   // For TensorMatcher, SymbolicSize, SymbolicDevice
#include <sgl_kernel/type.cuh>   // For dtype_trait, fp16_t, bf16_t, fp32_t
#include <sgl_kernel/utils.h>    // For RuntimeCheck, div_ceil
#include <sgl_kernel/utils.cuh>  // For LaunchKernel, SGL_DEVICE
#include <sgl_kernel/vec.cuh>    // For AlignedVector

#include <dlpack/dlpack.h>
#include <tvm/ffi/container/tensor.h>

namespace {

// ----------------------------------------------------------------
// Kernel: element-wise scale using vectorized 128-bit loads/stores
// T       = fp16_t | bf16_t | fp32_t
// kVecN   = number of elements per vector load (e.g. 8 for fp16)
// factor  = runtime scale factor
// ----------------------------------------------------------------
template <typename T, int kVecN>
__global__ void scale_kernel(T* __restrict__ dst,
                              const T* __restrict__ src,
                              float factor,
                              uint32_t n_total) {
  using vec_t = device::AlignedVector<T, kVecN>;
  const uint32_t n_vecs = n_total / kVecN;

  // --- vectorised body ---
  const uint32_t vec_stride = blockDim.x * gridDim.x;
  for (uint32_t vi = blockIdx.x * blockDim.x + threadIdx.x;
       vi < n_vecs;
       vi += vec_stride) {
    vec_t v;
    v.load(src, vi);
#pragma unroll
    for (int i = 0; i < kVecN; ++i) {
      v[i] = static_cast<T>(static_cast<float>(v[i]) * factor);
    }
    v.store(dst, vi);
  }

  // --- scalar tail ---
  const uint32_t base = n_vecs * kVecN;
  const uint32_t scalar_stride = blockDim.x * gridDim.x;
  for (uint32_t i = blockIdx.x * blockDim.x + threadIdx.x;
       base + i < n_total;
       i += scalar_stride) {
    dst[base + i] = static_cast<T>(static_cast<float>(src[base + i]) * factor);
  }
}

// ----------------------------------------------------------------
// Launcher: validates tensors, selects vector width, launches kernel
// ----------------------------------------------------------------
template <typename T>
void scale(tvm::ffi::TensorView dst, tvm::ffi::TensorView src, float factor) {
  using namespace host;

  // 1. Validate input tensors with TensorMatcher
  SymbolicSize N = {"num_elements"};
  SymbolicDevice device_;
  device_.set_options<kDLCUDA>();

  TensorMatcher({N})  //
      .with_dtype<T>()
      .with_device<kDLCUDA>(device_)
      .verify(dst)
      .verify(src);  // same shape / dtype / device as dst

  const uint32_t n = static_cast<uint32_t>(N.unwrap());
  const DLDevice device = device_.unwrap();

  RuntimeCheck(n > 0, "scale: num_elements must be > 0, got ", n);

  // 2. Choose vector width for 128-bit loads (16 bytes)
  //    fp16/bf16: 8 elements × 2 bytes = 16 bytes
  //    fp32:      4 elements × 4 bytes = 16 bytes
  constexpr int kVecN = 16 / sizeof(T);
  const uint32_t n_work_items = div_ceil(n, static_cast<uint32_t>(kVecN));

  // 3. Launch
  constexpr uint32_t kBlockSize = 256;
  const uint32_t grid = div_ceil(n_work_items, kBlockSize);

  LaunchKernel(grid, kBlockSize, device)(
      scale_kernel<T, kVecN>,
      static_cast<T*>(dst.data_ptr()),
      static_cast<const T*>(src.data_ptr()),
      factor,
      n);
}

}  // namespace
```

```python
from __future__ import annotations

from typing import TYPE_CHECKING

import torch

from sglang.jit_kernel.utils import cache_once, load_jit, make_cpp_args

if TYPE_CHECKING:
    from tvm_ffi.module import Module


@cache_once
def _jit_scale_module(dtype: torch.dtype) -> Module:
    """Compile and cache the JIT scale module for a given dtype."""
    args = make_cpp_args(dtype)
    return load_jit(
        "scale",
        *args,
        cuda_files=["elementwise/scale.cuh"],
        cuda_wrappers=[("scale", f"scale<{args}>")],
    )


def scale(src: torch.Tensor, factor: float, out: torch.Tensor | None = None) -> torch.Tensor:
    """
    Element-wise scale: dst = src * factor.

    Supported dtypes: torch.float16, torch.bfloat16, torch.float32.

    Parameters
    ----------
    src    : CUDA tensor (FP16 / BF16 / FP32)
    factor : scale factor
    out    : optional pre-allocated output tensor (same shape/dtype as src)

    Returns
    -------
    Scaled tensor (dst = src * factor).
    """
    if not src.is_cuda:
        raise RuntimeError("src must be a CUDA tensor")
    if src.dtype not in (torch.float16, torch.bfloat16, torch.float32):
        raise RuntimeError(
            f"Unsupported dtype {src.dtype}. Supported: float16, bfloat16, float32"
        )
    if out is None:
        out = torch.empty_like(src)
    else:
        if out.shape != src.shape:
            raise RuntimeError("out shape must match src")
        if out.dtype != src.dtype:
            raise RuntimeError("out dtype must match src")
        if out.device != src.device:
            raise RuntimeError("out device must match src")

    # Keep the Python wrapper thin, but still enforce the basic preconditions
    # that the current JIT/FFI path does not reject safely on its own.
    module = _jit_scale_module(src.dtype)
    module.scale(out, src, factor)
    return out
```
| `torch.dtype`      | C++ type   |
|--------------------|------------|
| `torch.float16`    | `fp16_t`   |
| `torch.bfloat16`   | `bf16_t`   |
| `torch.float32`    | `fp32_t`   |

```python
return load_jit(
    "scale",
    *args,
    cuda_files=["elementwise/scale.cuh"],
    cuda_wrappers=[("scale", f"scale<{args}>")],
    extra_cuda_cflags=["-O3", "--use_fast_math"],
)
```

```python
import pytest
import torch
from sglang.jit_kernel.scale import scale
from sglang.test.ci.ci_register import register_cuda_ci

register_cuda_ci(est_time=30, suite="stage-b-kernel-unit-1-gpu-large")


@pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16, torch.float32])
@pytest.mark.parametrize("size", [1, 127, 128, 1024, 4097])  # cover tail remainder
@pytest.mark.parametrize("factor", [0.5, 1.0, 2.0, 3.0])
def test_scale_correctness(dtype, size, factor):
    src = torch.randn(size, dtype=dtype, device="cuda")
    out = scale(src, factor)
    expected = src * factor

    rtol, atol = (1e-5, 1e-6) if dtype == torch.float32 else (1e-2, 1e-2)
    torch.testing.assert_close(out, expected, rtol=rtol, atol=atol)


@pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16, torch.float32])
def test_scale_out_param(dtype):
    src = torch.randn(1024, dtype=dtype, device="cuda")
    out = torch.empty_like(src)
    result = scale(src, 2.0, out=out)
    assert result is out
    torch.testing.assert_close(out, src * 2.0, rtol=1e-2, atol=1e-2)


def test_scale_cpu_error():
    src = torch.randn(128, dtype=torch.float16)  # CPU tensor
    with pytest.raises(RuntimeError, match="CUDA"):
        scale(src, 2.0)


def test_scale_unsupported_dtype():
    src = torch.randint(0, 10, (128,), dtype=torch.int32, device="cuda")
    with pytest.raises(RuntimeError, match="dtype"):
        scale(src, 2.0)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
```

```python
import itertools

import torch
import triton
import triton.testing

from sglang.jit_kernel.benchmark.utils import (
    DEFAULT_DEVICE,
    DEFAULT_DTYPE,
    get_benchmark_range,
    run_benchmark,
)
from sglang.jit_kernel.scale import scale as jit_scale
from sglang.test.ci.ci_register import register_cuda_ci

register_cuda_ci(est_time=6, suite="stage-b-kernel-benchmark-1-gpu-large")

SIZE_LIST = get_benchmark_range(
    full_range=[2**n for n in range(10, 20)],  # 1K … 512K elements
    ci_range=[4096, 65536],
)

configs = list(itertools.product(SIZE_LIST))


@triton.testing.perf_report(
    triton.testing.Benchmark(
        x_names=["size"],
        x_vals=configs,
        line_arg="provider",
        line_vals=["jit", "torch"],
        line_names=["SGL JIT Kernel", "PyTorch"],
        styles=[("blue", "-"), ("red", "--")],
        ylabel="us",
        plot_name="scale-performance",
        args={},
    )
)
def benchmark(size: int, provider: str):
    src = torch.randn(size, dtype=DEFAULT_DTYPE, device=DEFAULT_DEVICE)
    factor = 2.0

    if provider == "jit":
        fn = lambda: jit_scale(src, factor)
    else:
        fn = lambda: src * factor

    return run_benchmark(fn)


if __name__ == "__main__":
    benchmark.run(print_data=True)
```
