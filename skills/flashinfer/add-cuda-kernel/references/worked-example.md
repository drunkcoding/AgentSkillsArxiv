# Worked Scale Kernel Example

This reference contains the complete source listings for the tutorial's element-wise `scale` kernel, including the CUDA kernel, TVM-FFI binding, JIT generator, Python API, and tests.

## Contents

- [CUDA Kernel](#cuda-kernel)
- [Launcher and TVM-FFI Binding](#launcher-and-tvm-ffi-binding)
- [JIT Generator](#jit-generator)
- [Python API](#python-api)
- [Tests](#tests)

## CUDA Kernel

Create `include/flashinfer/scale.cuh`:

```cpp
#pragma once
#include <cuda_runtime.h>
#include <cuda_fp16.h>
#include <cuda_bf16.h>

namespace flashinfer {

/*!
 * \brief Element-wise scale kernel
 * \tparam T Data type (half, __nv_bfloat16, float)
 * \param input Input tensor
 * \param output Output tensor
 * \param factor Scale factor
 * \param n Number of elements
 */
template <typename T>
__global__ void ScaleKernel(const T* input, T* output, T factor, int n) {
  int idx = blockIdx.x * blockDim.x + threadIdx.x;
  if (idx < n) {
    output[idx] = input[idx] * factor;
  }
}

/*!
 * \brief Launch scale kernel
 * \tparam T Data type
 * \param input Input pointer
 * \param output Output pointer
 * \param factor Scale factor
 * \param n Number of elements
 * \param stream CUDA stream
 */
template <typename T>
cudaError_t ScaleLauncher(const T* input, T* output, T factor, int n,
                          cudaStream_t stream = nullptr) {
  const int threads = 256;
  const int blocks = (n + threads - 1) / threads;

  ScaleKernel<T><<<blocks, threads, 0, stream>>>(input, output, factor, n);

  return cudaGetLastError();
}

}  // namespace flashinfer
```

**Key points:**

- Framework-agnostic (no Torch headers)
- Uses raw pointers
- Template-based for dtype flexibility
- Only includes what's needed (cuda_runtime, cuda_fp16, cuda_bf16)

## Launcher and TVM-FFI Binding

Create `csrc/scale.cu`:

```cpp
#include "flashinfer/scale.cuh"

using namespace flashinfer;

void scale_launcher(TensorView input, TensorView output,
                    float factor) {
  CHECK_INPUT(input);
  CHECK_INPUT(output);
  TVM_FFI_ICHECK_EQ(input.dtype(), output.dtype());
  int n = input.numel();
  auto stream = get_stream(input.device());

  DISPATCH_DLPACK_DTYPE_TO_CTYPE_FP32_FP16(input.dtype(), DType, [&] {
    cudaError_t status = ScaleLauncher<DType>(
      input.data_ptr<DType>(),
      output.data_ptr<DType>(),
      static_cast<DType>(factor),
      n,
      stream
    );
    TVM_FFI_ICHECK(status == cudaSuccess)
        << "Failed to run ScaleLauncher: " << cudaGetErrorString(status);
    return true;
  });
}
```

Create `csrc/scale_jit_binding.cu`:

```cpp
#include "scale.cu"
#include "tvm_ffi_utils.h"

// Forward declaration
void scale_launcher(TensorView input, TensorView output, float factor);

// Export to TVM-FFI
TVM_FFI_DLL_EXPORT_TYPED_FUNC(run, scale_launcher);
```

The launcher uses TVM FFI tensor checks, stream lookup, dtype dispatch, raw pointer conversion, and `TVM_FFI_ICHECK` status handling. Forward-declare the launcher before exporting it with `TVM_FFI_DLL_EXPORT_TYPED_FUNC`.

TVM-FFI error handling uses `TVM_FFI_THROW(ValueError) << "message"` for custom value errors and `TVM_FFI_THROW(TypeError) << "message"` for type errors. The `<<` operator chains multiple values into the message, and errors propagate back to Python.

Use `TVM_FFI_THROW` for normal runtime errors that Python should catch. Use `TVM_FFI_LOG_AND_THROW` only when a function may run during object construction, when an exception may not be caught properly during module initialization, or when an internal error or unsupported dispatch combination almost never fails in practice. Logging before throwing keeps those failures visible.

For example, setup validation can use:

```cpp
void check_weights_shape(std::string which_weights) const {
  if (which_weights != "gemm1" && which_weights != "gemm2") {
    TVM_FFI_LOG_AND_THROW(InternalError)
        << "Internal error: which_weights = " << which_weights;
  }
  if (weight_layout is unsupported) {
    TVM_FFI_LOG_AND_THROW(NotImplementedError)
        << "Unsupported weight_layout: " << (int)weight_layout;
  }
}
```

A normal runtime validation can use:

```cpp
void scale_run(TensorView input, TensorView output, double factor) {
  if (!input_tensor.is_cuda()) {
    TVM_FFI_THROW(ValueError) << "Input must be a CUDA tensor";
  }
}
```

## JIT Generator

Create `flashinfer/jit/scale.py`:

```python
import os
import shutil
from pathlib import Path

from . import JitSpec, gen_jit_spec
from . import env as jit_env
from .core import write_if_different


def get_scale_uri(dtype_in: str, dtype_out: str) -> str:
    """Generate unique identifier for scale module."""
    return f"scale_dtype_in_{dtype_in}_dtype_out_{dtype_out}"


def gen_scale_module(dtype_in, dtype_out):
    """
    Generate JIT module for scale operation.

    Note: This is a simple example without Jinja templating.
    The dtype dispatch is handled at runtime in the C++ code.
    """
    # Compute URI
    uri = get_scale_uri(dtype_in, dtype_out)

    # Create generation directory
    gen_directory = jit_env.FLASHINFER_GEN_SRC_DIR / uri
    os.makedirs(gen_directory, exist_ok=True)

    # Copy source files (no Jinja needed for this simple case)
    sources = []
    for fname in ["scale.cu", "scale_jit_binding.cu"]:
        src_path = jit_env.FLASHINFER_CSRC_DIR / fname
        dest_path = gen_directory / fname
        shutil.copy(src_path, dest_path)
        sources.append(dest_path)

    # Return JitSpec
    return gen_jit_spec(
        name=uri,
        sources=sources,
        extra_cuda_cflags=[],
    )
```

This simple operation needs no Jinja template. Copy the sources into the generated source directory, use a URI that identifies the dtype configuration, and never write to package directories.

## Python API

Create `flashinfer/scale.py`:

```python
import functools
import torch
from typing import Optional

from .jit.scale import gen_scale_module
from .utils import backend_requirement, supported_compute_capability
from .api_logging import flashinfer_api


@functools.cache
def get_scale_module(dtype_in, dtype_out):
    """Get or compile scale module (cached)."""
    return gen_scale_module(dtype_in, dtype_out).build_and_load()


@supported_compute_capability([80, 86, 89, 90, 100, 103, 110, 120])
def _check_scale_problem_size(input: torch.Tensor, factor: float,
                               out: Optional[torch.Tensor] = None) -> bool:
    """Validate inputs for scale operation."""
    # Validate input
    if not input.is_cuda:
        raise ValueError("Input must be a CUDA tensor")

    # Validate output if provided
    if out is not None:
        if out.shape != input.shape:
            raise ValueError("Output shape mismatch")
        if out.dtype != input.dtype:
            raise ValueError("Output dtype mismatch")
        if not out.is_cuda:
            raise ValueError("Output must be a CUDA tensor")

    return True


@flashinfer_api
@backend_requirement(
    backend_checks={},  # No backend choices for this simple kernel
    common_check=_check_scale_problem_size,
)
def scale(input: torch.Tensor, factor: float,
          out: Optional[torch.Tensor] = None) -> torch.Tensor:
    """
    Element-wise scale operation.

    Parameters
    ----------
    input : torch.Tensor
        Input tensor (CUDA)
    factor : float
        Scale factor
    out : Optional[torch.Tensor]
        Output tensor (if None, allocate new tensor)

    Returns
    -------
    output : torch.Tensor
        Scaled tensor (input * factor)

    Examples
    --------
    >>> import torch
    >>> import flashinfer
    >>> x = torch.randn(1024, dtype=torch.float16, device="cuda")
    >>> y = flashinfer.scale(x, 2.0)
    >>> torch.allclose(y, x * 2.0)
    True
    """
    # Allocate output if needed
    if out is None:
        out = torch.empty_like(input)

    # Get module (compile if first call with this dtype)
    dtype_str = str(input.dtype).replace("torch.", "")
    module = get_scale_module(dtype_str, dtype_str)

    # Call TVM-FFI function (exported as "run")
    module.run(input, out, float(factor))

    return out
```

The API caches compiled modules, validates CUDA inputs through the decorators, supports an optional destination tensor, and exposes the TVM-FFI function as `run`.

## Tests

Create tests in an appropriate subdirectory, for example `tests/elementwise/test_scale.py`:

```python
import pytest
import torch


@pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16, torch.float32])
@pytest.mark.parametrize("size", [128, 1024, 4096])
def test_scale_correctness(dtype, size):
    """Test scale operation correctness."""
    import flashinfer

    # Setup
    x = torch.randn(size, dtype=dtype, device="cuda")
    factor = 3.14

    # Run FlashInfer kernel
    y = flashinfer.scale(x, factor)

    # Reference implementation
    expected = x * factor

    # Compare
    if dtype == torch.float32:
        rtol, atol = 1e-5, 1e-6
    else:
        rtol, atol = 1e-3, 1e-3

    torch.testing.assert_close(y, expected, rtol=rtol, atol=atol)


@pytest.mark.parametrize("dtype", [torch.float16, torch.bfloat16])
def test_scale_inplace(dtype):
    """Test scale with pre-allocated output."""
    import flashinfer

    x = torch.randn(1024, dtype=dtype, device="cuda")
    out = torch.empty_like(x)
    factor = 2.0

    result = flashinfer.scale(x, factor, out=out)

    # Should return the same tensor
    assert result is out

    # Check correctness
    expected = x * factor
    torch.testing.assert_close(result, expected, rtol=1e-3, atol=1e-3)


def test_scale_cpu_error():
    """Test that CPU tensors raise an error."""
    import flashinfer

    x = torch.randn(128, dtype=torch.float32)

    with pytest.raises(ValueError, match="CUDA"):
        flashinfer.scale(x, 2.0)
```

Use parametrization for dtypes and sizes, compare with a reference implementation, set dtype-appropriate tolerances, and cover validation errors.
