---
name: add-cuda-kernel
description: Step-by-step tutorial for adding new CUDA kernels to FlashInfer
---

# Tutorial: Adding a New Kernel to FlashInfer

This tutorial walks through adding a simple element-wise scale operation to FlashInfer. We'll implement `scale(x, factor) = x * factor` to demonstrate the complete workflow.

## Goal

Add a new operation that scales each element of a tensor by a scalar factor:

- Input: tensor `x` and scalar `factor`
- Output: `x * factor` (element-wise)
- Support multiple dtypes (FP16, BF16, FP32)

## Step 1: Define CUDA Kernel in `include/`

The complete CUDA kernel source is preserved in [the worked example](references/worked-example.md#cuda-kernel). Keep the kernel framework-agnostic, use raw pointers, template the dtype, and include only the required CUDA headers.

## Step 2: Create Launcher in `csrc/`

The complete launcher and binding listings are in [the worked example](references/worked-example.md#launcher-and-tvm-ffi-binding). Keep TVM FFI utilities in `csrc/`, validate tensors, dispatch dtypes, obtain the CUDA stream, convert to raw pointers, and propagate status with descriptive errors.

Use `TVM_FFI_THROW` for normal runtime errors and `TVM_FFI_LOG_AND_THROW` only for construction-time, initialization, or exceptionally rare internal failures. The worked binding and error-handling examples are preserved in [the reference](references/worked-example.md#launcher-and-tvm-ffi-binding).

## Step 3: Create TVM-FFI Binding in `csrc/`

The complete binding is in [the worked example](references/worked-example.md#launcher-and-tvm-ffi-binding). Forward-declare the launcher and export it with `TVM_FFI_DLL_EXPORT_TYPED_FUNC(name, function)`.

## Step 4: Create JIT Generator (No Jinja for Simple Case)

The complete JIT generator is in [the worked example](references/worked-example.md#jit-generator). For a simple operation, copy source files into the generated source directory, use a unique URI, and never write to package directories.

### (Optional) Specifying Supported CUDA Architectures

FlashInfer uses `CompilationContext` to manage CUDA architecture targets. This is critical because some kernels only work on specific GPU architectures (e.g., Hopper SM90, Blackwell SM100).

#### How CompilationContext Works

**Automatic Detection** (default):
```python
from flashinfer.compilation_context import CompilationContext

ctx = CompilationContext()
# Automatically detects all GPUs in the system
# For SM90+, adds 'a' suffix (e.g., 9.0a for Hopper)
# Result: ctx.TARGET_CUDA_ARCHS = {(9, '0a'), (10, '0a'), ...}
```

**Manual Override** (via environment variable):
```bash
export FLASHINFER_CUDA_ARCH_LIST="8.0 9.0a 10.0a"
# Now only these architectures will be compiled
```

#### Specifying Architectures in Your JIT Module

When creating a JIT module, specify which major SM versions are supported:

```python
from flashinfer.jit.core import gen_jit_spec
from flashinfer.jit import current_compilation_context

def gen_my_hopper_only_module():
    """Example: Kernel works on SM90 and later supported architectures."""
    uri = get_my_uri(...)
    gen_directory = jit_env.FLASHINFER_GEN_SRC_DIR / uri
    # ... copy sources ...

    nvcc_flags = current_compilation_context.get_nvcc_flags_list(
        # Explicitly list supported SM versions - no automatic future compatibility
        supported_major_versions=[9, 10, 11, 12]  # SM90, SM100, SM110, SM120
    )

    return gen_jit_spec(
        name=uri,
        sources=sources,
        extra_cuda_cflags=nvcc_flags,
    )

def gen_my_blackwell_only_module():
    """Example: Kernel only works on SM100 (Blackwell)"""
    uri = get_my_uri(...)
    gen_directory = jit_env.FLASHINFER_GEN_SRC_DIR / uri
    # ... copy sources ...

    nvcc_flags = current_compilation_context.get_nvcc_flags_list(
        supported_major_versions=[10]  # SM100 only
    )

    return gen_jit_spec(
        name=uri,
        sources=sources,
        extra_cuda_cflags=nvcc_flags,
    )

def gen_my_universal_module():
    """Example: Kernel works on all architectures"""
    uri = get_my_uri(...)
    gen_directory = jit_env.FLASHINFER_GEN_SRC_DIR / uri
    # ... copy sources ...

    nvcc_flags = current_compilation_context.get_nvcc_flags_list(
        supported_major_versions=None  # All available architectures
    )

    return gen_jit_spec(
        name=uri,
        sources=sources,
        extra_cuda_cflags=nvcc_flags,
    )
```

**What Happens:**
- ✅ If user's GPU is SM90 and they call a Hopper-only module → Compiles and runs
- ❌ If user's GPU is SM80 and they call a Hopper-only module → `RuntimeError: No supported CUDA architectures found for major versions [9, 10, 11, 12]`

#### Real Examples from FlashInfer

```python
# MLA kernel: Blackwell and newer only
def gen_mla_module() -> JitSpec:
    nvcc_flags = current_compilation_context.get_nvcc_flags_list(
        supported_major_versions=[10, 11]  # SM100, SM110
    )
    return gen_jit_spec(
        name=uri,
        sources=sources,
        extra_cuda_cflags=nvcc_flags,
    )

# Blackwell FMHA: SM120 only
def gen_fmhav2_blackwell_module(...):
    nvcc_flags = current_compilation_context.get_nvcc_flags_list(
        supported_major_versions=[12]  # SM120 only
    )
    return gen_jit_spec(
        name=uri,
        sources=sources,
        extra_cuda_cflags=nvcc_flags,
    )

# Standard attention: Hopper and later supported architectures
def gen_batch_prefill_module(...):
    nvcc_flags = current_compilation_context.get_nvcc_flags_list(
        supported_major_versions=[9, 10, 11, 12]  # SM90, SM100, SM110, SM120
    )
    return gen_jit_spec(
        name=uri,
        sources=sources,
        extra_cuda_cflags=nvcc_flags,
    )
```

#### Common Architecture Specifications

| Supported Versions | Architectures | Use Case |
|-------------------|---------------|----------|
| `None` | All available GPUs | Universal kernels (default) |
| `[9, 10, 11, 12]` | SM90, SM100, SM110, SM120 | Hopper, Blackwell |
| `[10, 11, 12]` | SM100, SM110, SM120 | Blackwell only |
| `[12]` | SM120 | Specific architecture only |
| `[8, 9, 10, 11, 12]` | SM80, SM90, SM100, SM110, SM120 | Ampere, Hopper, Blackwell |

#### Testing with Architecture Requirements

When your kernel has architecture requirements, add skip checks in tests (see Step 6 below):

```python
import pytest
import torch
from flashinfer.utils import is_sm90a_supported

def test_hopper_kernel():
    if not is_sm90a_supported(torch.device("cuda")):
        pytest.skip("SM90a is not supported on this GPU")

    # Test code here
    ...
```

## Step 5: Create Python API in `flashinfer/`

The complete Python API is in [the worked example](references/worked-example.md#python-api). Cache compiled modules, validate inputs with the decorators, expose an optional destination tensor, and call the TVM-FFI function as `run`.

### Using `@backend_requirement` and `@supported_compute_capability` Decorators

FlashInfer provides two decorators for enforcing compute capability and backend requirements:

#### `@supported_compute_capability` Decorator

Marks a function with its supported CUDA compute capabilities:

```python
from flashinfer.utils import supported_compute_capability

@supported_compute_capability([80, 86, 89, 90, 100, 103, 110, 120])
def _my_check_function(input, output):
    """Supports SM80 (Ampere) through SM120 (Blackwell)."""
    # Validation logic here
    return True
```

#### `@backend_requirement` Decorator

Enforces backend and problem size requirements at runtime. There are three usage patterns:

**Pattern 1: Single Backend (No Backend Choices)**

For kernels with only one implementation (like our scale example):

```python
from flashinfer.utils import backend_requirement, supported_compute_capability

@supported_compute_capability([80, 86, 89, 90, 100, 103, 110, 120])
def _check_my_kernel(input, output):
    """Validate inputs. Must return True if valid."""
    if input.shape[-1] > 256:
        raise ValueError("Head dimension must be <= 256")
    return True

@backend_requirement(
    backend_checks={},  # Empty dict = no backend parameter
    common_check=_check_my_kernel,
)
def my_kernel(input, output):
    # Kernel implementation
    pass
```

**Pattern 2: Multiple Backends**

For kernels with multiple implementation backends (e.g., CUTLASS, cuDNN):

```python
@supported_compute_capability([80, 86, 89, 90])
def _cutlass_check(q, k, v, backend):
    """CUTLASS backend: Ampere through Hopper."""
    if q.shape[-1] > 256:
        raise ValueError("CUTLASS: head_dim must be <= 256")
    return True

@supported_compute_capability([75, 80, 86, 89, 90, 100])
def _cudnn_check(q, k, v, backend):
    """cuDNN backend: Turing through Blackwell."""
    return True

@backend_requirement(
    backend_checks={
        "cutlass": _cutlass_check,
        "cudnn": _cudnn_check,
    },
    common_check=None,  # Optional: shared validation for all backends
)
def attention(q, k, v, backend="cutlass"):
    if backend == "cutlass":
        # CUTLASS implementation
        pass
    elif backend == "cudnn":
        # cuDNN implementation
        pass
```

**Pattern 3: Auto Backend Selection**

For kernels that can automatically select the best backend:

```python
def _heuristic_func(suitable_backends, q, k, v, backend):
    """Return backends in order of preference."""
    # Prefer CUTLASS for small head dims, cuDNN for larger
    if q.shape[-1] <= 128:
        preferred = ["cutlass", "cudnn"]
    else:
        preferred = ["cudnn", "cutlass"]
    return [b for b in preferred if b in suitable_backends]

@backend_requirement(
    backend_checks={
        "cutlass": _cutlass_check,
        "cudnn": _cudnn_check,
    },
    common_check=_common_validation,
    heuristic_func=_heuristic_func,  # Required when backend="auto" is used
)
def attention(q, k, v, backend="auto"):
    if backend == "auto":
        # Use the first backend from suitable_auto_backends
        backend = attention.suitable_auto_backends[0]
    # ... rest of implementation
```

#### Features Added by `@backend_requirement`

The decorator adds these methods to the wrapped function:

```python
# Check if a backend is supported (optionally for a specific CC)
scale.is_backend_supported("cutlass")           # True/False
scale.is_backend_supported("cutlass", cc=90)    # True/False for Hopper

# Check if any backend supports this compute capability
scale.is_compute_capability_supported(90)       # True/False

# Check if a backend exists
scale.has_backend("cutlass")                    # True/False

# Check if there are multiple backend choices
scale.has_backend_choices()                     # True/False
```

#### `skip_check` Keyword Argument

The decorator adds a `skip_check` keyword argument to bypass validation for performance-critical code paths:

```python
# Normal call with validation
result = scale(x, 2.0)

# Skip validation for performance (use with caution!)
result = scale(x, 2.0, skip_check=True)
```

#### Check Function Requirements

Check functions must:
1. Accept the same arguments as the decorated function
2. Return `True` if validation passes
3. Raise `ValueError` with descriptive message if validation fails
4. Be decorated with `@supported_compute_capability` to specify supported architectures

## Step 6: Write Tests in `tests/`

The complete test file is in [the worked example](references/worked-example.md#tests). Use parametrization for dtypes and sizes, compare with a reference implementation, set dtype-appropriate tolerances, and cover validation errors.

## Step 7: Register in AOT

Register your kernel in AOT so users with `flashinfer-jit-cache` can skip JIT compilation.

Edit `flashinfer/aot.py`, add to the appropriate section:

```python
def gen_scale_modules() -> Iterator[JitSpec]:
    """Generate scale operation modules for AOT compilation."""
    from .jit.scale import gen_scale_module

    # Pre-compile common dtypes
    for dtype in ["float16", "bfloat16", "float32"]:
        yield gen_scale_module(dtype, dtype)


# In the main AOT build loop, add:
# for spec in gen_scale_modules():
#     spec.build()
```

**Key points:**

- Pre-compile common configurations
- Users with `flashinfer-jit-cache` won't need to compile at runtime

## Step 8: Export API

Edit `flashinfer/__init__.py`:

```python
from .scale import scale as scale

# Or in the existing imports section:
# from .scale import scale
```

## Step 9: Run and Test

```bash
# The kernel compiles automatically on first use
pytest tests/test_scale.py -v

# Run with different dtypes
pytest tests/test_scale.py::test_scale_correctness[float16-128] -v
```

## Step 10: Add Benchmark

**All new kernels should have benchmarks.** This helps track performance regressions and allows users to compare against other implementations.

Create a benchmark file in `benchmarks/` (e.g., `benchmarks/bench_scale.py`):

```python
import torch
from flashinfer.testing import bench_gpu_time

def bench_scale():
    """Benchmark scale kernel."""
    import flashinfer

    sizes = [1024, 4096, 16384, 65536, 262144]
    dtypes = [torch.float16, torch.bfloat16]

    print("Scale Kernel Benchmark")
    print("-" * 60)
    print(f"{'Size':>10} {'Dtype':>10} {'Time (us)':>12} {'Std (us)':>10}")
    print("-" * 60)

    for size in sizes:
        for dtype in dtypes:
            x = torch.randn(size, dtype=dtype, device="cuda")

            # Benchmark with CUPTI (auto-fallback to CUDA events)
            median_time, std_time = bench_gpu_time(
                flashinfer.scale,
                args=(x, 2.0),
                enable_cupti=True,
                dry_run_iters=10,
                repeat_iters=100,
            )

            print(f"{size:>10} {str(dtype):>10} {median_time*1e6:>12.2f} {std_time*1e6:>10.2f}")

if __name__ == "__main__":
    bench_scale()
```

**For more complex kernels**, consider:

- Adding comparisons against reference implementations (e.g., PyTorch native, cuBLAS, cuDNN)
- Using the unified benchmarking framework in `benchmarks/flashinfer_benchmark.py` if applicable
- Testing across different problem sizes and configurations

→ **For complete benchmarking guide, see [`.claude/skills/benchmark-kernel/SKILL.md`](../benchmark-kernel/SKILL.md)**

## Summary of Files Created/Modified

```
include/flashinfer/scale.cuh              # NEW: CUDA kernel definition
csrc/scale.cu                              # NEW: PyTorch launcher
csrc/scale_jit_binding.cu                  # NEW: TVM-FFI binding
flashinfer/jit/scale.py                    # NEW: JIT generator
flashinfer/scale.py                        # NEW: Python API
flashinfer/__init__.py                     # MODIFIED: Export API
flashinfer/aot.py                          # MODIFIED: Register AOT
tests/test_scale.py                        # NEW: Unit tests
benchmarks/bench_scale.py                  # NEW: Benchmark script
```
