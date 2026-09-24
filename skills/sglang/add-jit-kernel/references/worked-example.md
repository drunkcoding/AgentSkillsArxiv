---
name: add-jit-kernel
description: Step-by-step tutorial for adding a new lightweight JIT CUDA kernel to sglang's jit_kernel module
---

## Contents

- [Abstractions](#common-abstractions-in-pythonsglangjit_kernelincludesgl_kernel)
- [CUDA kernel](#step-1-implement-the-cuda-kernel-in-jit_kernelcsrc)
- [Python wrapper](#step-2-add-the-python-wrapper-in-jit_kernel)
- [Tests](#step-4-write-tests-required)
- [Benchmark](#step-5-add-a-benchmark-required)

# Tutorial: Adding a New JIT Kernel to SGLang

This tutorial walks through adding a simple element-wise scale operation as a JIT kernel. We'll implement `scale(x, factor) = x * factor` to demonstrate the complete workflow.

## Goal

Add a new operation that scales each element of a tensor by a scalar factor:

- Input: tensor `x` (CUDA) and scalar `factor` (float, passed at runtime)
- Output: `x * factor` (element-wise), allocated internally
- Supported dtypes: **FP16 (`torch.float16`), BF16 (`torch.bfloat16`), FP32 (`torch.float32`)**

## When to use JIT vs AOT (`sgl-kernel`)

- **JIT (`jit_kernel`)**: prefer this first for kernels that do **not** depend on CUTLASS or another large C++ project. It is the default choice for lightweight kernels that benefit from rapid iteration and first-use compilation.
- **AOT (`sgl-kernel`)**: prefer this when the kernel **does** depend on CUTLASS or another large C++ project, or when it should live in `sgl-kernel/` and participate in the wheel build / torch op registration flow.
- **Exception**: kernels that depend on `flashinfer`, or on CUTLASS that is already provided through `flashinfer`, can still be implemented as `jit_kernel`.

---

## Common Abstractions in `python/sglang/jit_kernel/include/sgl_kernel/`

**Always prefer these abstractions over raw CUDA primitives.** They provide safety, readability, and consistency with the rest of the codebase.

**Important include rule:** for every `#include <sgl_kernel/...>` line, add a short trailing comment explaining why that header is included (for example `// For TensorMatcher, SymbolicSize, SymbolicDevice`). This matches the current JIT kernel style and keeps include usage self-documenting.

### `utils.h` — Host-side utilities

```cpp
#include <sgl_kernel/utils.h>
```

- **`host::RuntimeCheck(cond, args...)`** — Assert a condition at runtime; throws `PanicError` with file/line info on failure. Prefer this over bare `assert`.
- **`host::Panic(args...)`** — Unconditionally throw a `PanicError` with a descriptive message.
- **`host::div_ceil(a, b)`** — Integer ceiling division `(a + b - 1) / b`.
- **`host::irange(n)`** / **`host::irange(start, end)`** — Range views for cleaner loops.
- **`host::pointer::offset(ptr, offsets...)`** — Byte-safe pointer arithmetic on `void*`. Use this instead of raw casts.

### `utils.cuh` — Device-side utilities + `LaunchKernel`

```cpp
#include <sgl_kernel/utils.cuh>
```

- **Type aliases**: `fp16_t`, `bf16_t`, `fp32_t`, `fp8_e4m3_t`, `fp8_e5m2_t` and their packed variants `fp16x2_t`, `bf16x2_t`, `fp32x2_t`, etc.
- **`SGL_DEVICE`** — Expands to `__forceinline__ __device__`. Use on all device functions.
- **`device::kWarpThreads`** — Constant `32`.
- **`device::load_as<T>(ptr, offset)`** / **`device::store_as<T>(ptr, val, offset)`** — Type-safe loads/stores from `void*`.
- **`device::pointer::offset(ptr, offsets...)`** — Pointer arithmetic on device.
- **`host::LaunchKernel(grid, block, device_or_stream [, smem])`** — RAII kernel launcher that:
  - Resolves the CUDA stream from a `DLDevice` via TVM-FFI automatically.
  - Checks the CUDA error with file/line info after launch via `operator()(kernel, args...)`.
  - Supports `.enable_pdl(bool)` for PDL (Programmatic Dependent Launch, SM90+).
- **`host::RuntimeDeviceCheck(cudaError_t)`** — Check a CUDA error; throw on failure.

### `tensor.h` — Tensor validation (`TensorMatcher`, Symbolic types)

```cpp
#include <sgl_kernel/tensor.h>
```

This is the **primary validation API** for all kernel launchers. Use it to validate every `tvm::ffi::TensorView` argument.

- **`host::SymbolicSize{"name"}`** — A named symbolic dimension. Call `.set_value(n)` to pin it, `.unwrap()` to extract after verification.
- **`host::SymbolicDType`** — Symbolic dtype. Use `.set_options<Ts...>()` to restrict allowed types.
- **`host::SymbolicDevice`** — Symbolic device. Use `.set_options<kDLCUDA>()` to restrict to CUDA.
- **`host::TensorMatcher({dims...})`** — Fluent builder for tensor validation:
  - `.with_dtype<T>()` — require a specific C++ type (e.g. `fp16_t`)
  - `.with_dtype<T1, T2, ...>()` — allow a set of types
  - `.with_device<kDLCUDA>(device_sym)` — require CUDA and bind the checked device to a `SymbolicDevice`
  - `.with_strides({strides...})` — validate strides (omit to require contiguous)
  - `.verify(tensor_view)` — execute the check; throws `PanicError` with full context on failure; **chainable** (`verify(a).verify(b)` to check multiple tensors with the same shape)

**Typical pattern:**
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

### `type.cuh` — `dtype_trait<T>` and `packed_t<T>`

```cpp
#include <sgl_kernel/type.cuh>
```

- **`dtype_trait<T>`** — Static trait struct for each scalar type. Provides:
  - `dtype_trait<T>::from(value)` — convert from another type (e.g. `fp32_t` → `fp16_t`)
  - `dtype_trait<T>::abs/sqrt/rsqrt/exp/sin/cos(x)` — type-dispatched unary math (primarily for `fp32_t`)
  - `dtype_trait<T>::max/min(x, y)` — type-dispatched binary math (primarily for `fp32_t`)
- **`packed_t<T>`** — Two-element packed alias: `packed_t<fp16_t>` = `fp16x2_t`, `packed_t<bf16_t>` = `bf16x2_t`, `packed_t<fp32_t>` = `fp32x2_t`. Use for vectorized loads/stores.
- **`device::cast<To, From>(value)`** — Type-safe cast using `dtype_trait`, e.g. `cast<fp32x2_t, fp16x2_t>(v)`.

### `vec.cuh` — Vectorized memory access (`AlignedVector`)

```cpp
#include <sgl_kernel/vec.cuh>
```

- **`device::AlignedVector<T, N>`** — Aligned storage for N elements of type T. N must be a power of two, `sizeof(T)*N <= 32`. Enables vectorized loads/stores for bandwidth efficiency. In terms of API/codegen constraints, the upper bound is 256-bit; in practice, 128-bit is the portable default, while 256-bit vectorization is typically only viable on `SM100+` and should be gated by an architecture check when needed.
  - `.load(ptr, offset)` — vectorized load from `ptr[offset]`
  - `.store(ptr, offset)` — vectorized store to `ptr[offset]`
  - `.fill(value)` — fill all lanes
  - `operator[](i)` — element access

### `tile.cuh` — `tile::Memory` (strided memory access pattern)

```cpp
#include <sgl_kernel/tile.cuh>
```

- `tile::Memory<T>` is fundamentally a **1D cooperative accessor** over a contiguous region.
- **`device::tile::Memory<T>::cta(blockDim.x)`** — Creates a tile accessor where each thread handles `tid = threadIdx.x` with stride `tsize` (for `cta(blockDim.x)`, this is `blockDim.x`). Common for loops over a 1D array.
- **`.load(ptr, offset)`** — loads `ptr[tid + offset * tsize]`
- **`.store(ptr, val, offset)`** — stores to `ptr[tid + offset * tsize]`
- **`.in_bound(n, offset)`** — boundary check

For a **2D tile**, either flatten `(row, col)` into a linear tile index first, or compute the address manually with `ptr[row * stride + col]` using your thread/block coordinates.

### `math.cuh` — Device math (`device::math::`)

```cpp
#include <sgl_kernel/math.cuh>
```

- `device::math::max/min<T>(a, b)` — type-dispatched binary math via `dtype_trait`
- `device::math::abs/sqrt/rsqrt/exp/sin/cos<T>(x)` — type-dispatched unary math via `dtype_trait`

### `warp.cuh` — Warp-level primitives

```cpp
#include <sgl_kernel/warp.cuh>
```

- `device::warp::reduce_sum<T>(value)` — warp-level sum reduction via `__shfl_xor_sync`
- `device::warp::reduce_max<T>(value)` — warp-level max reduction

### `cta.cuh` — CTA-level primitives

```cpp
#include <sgl_kernel/cta.cuh>
```

- `device::cta::reduce_max<T>(value, smem, min_value)` — CTA-wide max using shared memory + warp reduction. Caller is responsible for a `__syncthreads()` after if the result in `smem[0]` is needed.

### `atomic.cuh` — Atomic operations

```cpp
#include <sgl_kernel/atomic.cuh>
```

- `device::atomic::max(float* addr, float value)` — float atomic max (handles negative values correctly via bit tricks).

### `runtime.cuh` — Occupancy and device info

```cpp
#include <sgl_kernel/runtime.cuh>
```

- `host::runtime::get_blocks_per_sm(kernel, block_dim)` — max active blocks per SM (occupancy)
- `host::runtime::get_sm_count(device_id)` — number of SMs on the device
- `host::runtime::get_cc_major(device_id)` — compute capability major version

**Persistent kernel pattern** (cap blocks to SM count × occupancy):
```cpp
static const uint32_t max_occ = runtime::get_blocks_per_sm(kernel, kBlockSize);
static const uint32_t num_sm  = runtime::get_sm_count(device.unwrap().device_id);
const auto num_blocks = std::min(num_sm * max_occ, div_ceil(n, kBlockSize));
LaunchKernel(num_blocks, kBlockSize, device.unwrap())(kernel, params);
```

---

## Step 0 (optional): Generate a `.clangd` config for better IDE support

```bash
python -m sglang.jit_kernel
```

---

## Step 1: Implement the CUDA kernel in `jit_kernel/csrc/`

Create `python/sglang/jit_kernel/csrc/elementwise/scale.cuh`.

The implementation fully uses the project abstractions described above:


> Complete file listing moved to [the worked example reference](references/worked-example.md). Follow the surrounding step and use the full listing when implementing.


**Key points:**

- Include headers from `sgl_kernel/` — **not** raw CUDA headers for anything already covered
- Add a short trailing `// For ...` explanation to every `#include <sgl_kernel/...>` line
- Use `TensorMatcher` for all tensor validation; never manually check shape/dtype/device
- Use `AlignedVector` for vectorised 128-bit loads/stores — significant bandwidth win
- Use `LaunchKernel` — it resolves the stream and checks errors automatically
- Use `RuntimeCheck` for runtime assertions with useful error messages
- Prefer passing runtime scalars like `factor` directly unless compile-time specialisation is genuinely required
- `fp16_t` / `bf16_t` / `fp32_t` are the project's type aliases (from `utils.cuh`)
- `device::cast<To, From>` or `dtype_trait<T>::from(val)` for cross-type conversions
- `device::math::` functions for device math instead of bare `__` intrinsics

---

## Step 2: Add the Python wrapper in `jit_kernel/`

Create `python/sglang/jit_kernel/scale.py`:


> Complete file listing moved to [the worked example reference](references/worked-example.md). Follow the surrounding step and use the full listing when implementing.


**Key points:**

- Use `cache_once` — **not** `functools.lru_cache` (incompatible with `torch.compile`)
- `load_jit` first arg(s) form the unique build marker; same marker = same cached binary
- Only include compile-time specialisation knobs in the build marker; runtime values like `factor` should stay runtime unless the kernel truly needs templating
- `cuda_wrappers`: `(export_name, kernel_symbol)` — `export_name` is called from Python
- `make_cpp_args(dtype, ...)` converts `torch.dtype` to C++ type alias:
- Keep Python launchers thin, but still validate the basic invariants (`is_cuda`, supported dtype, `out` metadata). In the current JIT/FFI path, invalid tensors are not always rejected safely before launch

| `torch.dtype`      | C++ type   |
|--------------------|------------|
| `torch.float16`    | `fp16_t`   |
| `torch.bfloat16`   | `bf16_t`   |
| `torch.float32`    | `fp32_t`   |

---

## Step 3 (optional): Tune JIT build flags

```python
return load_jit(
    "scale",
    *args,
    cuda_files=["elementwise/scale.cuh"],
    cuda_wrappers=[("scale", f"scale<{args}>")],
    extra_cuda_cflags=["-O3", "--use_fast_math"],
)
```

If your kernel requires SM90+, raise a clear Python error before calling `load_jit`:

```python
if torch.cuda.get_device_capability()[0] < 9:
    raise RuntimeError("This kernel requires SM90 (Hopper) or later")
```

---

## Step 4: Write tests (required)

JIT kernel tests live under `python/sglang/jit_kernel/tests/`. **CI does not run `pytest` in that directory directly.** The unified runner `test/run_suite.py` discovers every `test_*.py` there (and every `bench_*.py` under `benchmark/`), collects `register_*_ci(...)` calls by **statically parsing each file’s AST**, and executes the selected suite. Every test file must register at least one CUDA entry or the collector fails its sanity check.

- **PR / per-commit CUDA suites** (see `test/run_suite.py` → `PER_COMMIT_SUITES`): JIT unit tests use `stage-b-kernel-unit-1-gpu-large` (see `.github/workflows/pr-test-jit-kernel.yml`: `python3 run_suite.py --hw cuda --suite stage-b-kernel-unit-1-gpu-large`).
- **Nightly kernel suite**: `nightly-kernel-1-gpu` with `--nightly` — typically used with `SGLANG_JIT_KERNEL_RUN_FULL_TESTS=1` in CI for expanded parameter grids (see `python/sglang/jit_kernel/utils.py` → `should_run_full_tests` / `get_ci_test_range`). Wired in `.github/workflows/nightly-test-nvidia.yml` (e.g. `python3 run_suite.py --hw cuda --suite nightly-kernel-1-gpu --nightly --continue-on-error`).

Registration pattern (module level, **literal** `est_time` and `suite` strings — required for AST parsing):

```python
from sglang.test.ci.ci_register import register_cuda_ci

register_cuda_ci(est_time=30, suite="stage-b-kernel-unit-1-gpu-large")
# Optional second registration: same file also listed under the nightly kernel suite
# register_cuda_ci(est_time=120, suite="nightly-kernel-1-gpu", nightly=True)
```

Keep `est_time` and `suite` as literal values. `run_suite.py` collects them from the file AST, so computed values and helper wrappers can break CI discovery.

Use `register_cuda_ci(..., disabled="reason")` if the file must stay in-tree but should be skipped in CI (e.g. multi-GPU only).

**Run like CI** (from repo root):

```bash
cd test && python3 run_suite.py --hw cuda --suite stage-b-kernel-unit-1-gpu-large
```

For fast iteration you can still run `pytest` on a single file locally; CI coverage is via `run_suite.py`.

Create `python/sglang/jit_kernel/tests/test_scale.py`:


> Complete file listing moved to [the worked example reference](references/worked-example.md). Follow the surrounding step and use the full listing when implementing.


---

## Step 5: Add a benchmark (required)

Benchmarks are `bench_*.py` files under `python/sglang/jit_kernel/benchmark/`. They are picked up by the same `run_suite.py` machinery as unit tests. Register them for **`stage-b-kernel-benchmark-1-gpu-large`** (PR JIT benchmark job: `python3 run_suite.py --hw cuda --suite stage-b-kernel-benchmark-1-gpu-large`).

Create `python/sglang/jit_kernel/benchmark/bench_scale.py`:


> Complete file listing moved to [the worked example reference](references/worked-example.md). Follow the surrounding step and use the full listing when implementing.


Run locally:

```bash
python python/sglang/jit_kernel/benchmark/bench_scale.py
```

Run the benchmark suite the way CI does:

```bash
cd test && python3 run_suite.py --hw cuda --suite stage-b-kernel-benchmark-1-gpu-large
```

---

## Troubleshooting

- **`No CI registry found in ...` from `run_suite.py`**: add a module-level `register_cuda_ci(...)` with literal `est_time` and `suite` (and optional `nightly=True`); starred args and non-literal values break AST collection
- **JIT compilation fails**: ensure the `.cuh` file is under `python/sglang/jit_kernel/csrc/`; reduce template argument combinations
- **CUDA crash / illegal memory access**: `CUDA_LAUNCH_BLOCKING=1`; `compute-sanitizer --tool memcheck python ...`
- **Unstable benchmark results**: `run_benchmark` uses CUDA-graph-based timing by default

---

## References

- `docs/developer_guide/development_jit_kernel_guide.md`
- `test/run_suite.py` — suite names, discovery of `jit_kernel/tests/` and `jit_kernel/benchmark/`, execution entrypoint for CI
- `python/sglang/test/ci/ci_register.py` — `register_cuda_ci` and AST registration rules
- `python/sglang/jit_kernel/utils.py` — `cache_once`, `load_jit`, `make_cpp_args`, `should_run_full_tests`, `get_ci_test_range`
- `python/sglang/jit_kernel/include/sgl_kernel/tensor.h` — `TensorMatcher`, `SymbolicSize/DType/Device`
- `python/sglang/jit_kernel/include/sgl_kernel/utils.cuh` — type aliases, `LaunchKernel`, `SGL_DEVICE`
- `python/sglang/jit_kernel/include/sgl_kernel/vec.cuh` — `AlignedVector`
- `python/sglang/jit_kernel/include/sgl_kernel/tile.cuh` — `tile::Memory`
- `python/sglang/jit_kernel/include/sgl_kernel/type.cuh` — `dtype_trait`, `packed_t`, `device::cast`
- `python/sglang/jit_kernel/include/sgl_kernel/math.cuh` — `device::math::`
- `python/sglang/jit_kernel/include/sgl_kernel/warp.cuh` — `warp::reduce_sum/max`
- `python/sglang/jit_kernel/include/sgl_kernel/cta.cuh` — `cta::reduce_max`
- `python/sglang/jit_kernel/include/sgl_kernel/atomic.cuh` — `atomic::max`
- `python/sglang/jit_kernel/include/sgl_kernel/runtime.cuh` — occupancy / SM count helpers
- `python/sglang/jit_kernel/csrc/add_constant.cuh` — minimal runnable reference
- `python/sglang/jit_kernel/csrc/elementwise/rmsnorm.cuh` — real example using `TensorMatcher` + `LaunchKernel` + `tile::Memory`
- `python/sglang/jit_kernel/csrc/elementwise/qknorm.cuh` — real example using `runtime::get_blocks_per_sm` + persistent kernel pattern
- `python/sglang/jit_kernel/benchmark/utils.py` — benchmark helpers

## Summary of Files Created

```
python/sglang/jit_kernel/csrc/elementwise/scale.cuh   # NEW: CUDA kernel
python/sglang/jit_kernel/scale.py                     # NEW: Python wrapper
python/sglang/jit_kernel/tests/test_scale.py          # NEW: Tests
python/sglang/jit_kernel/benchmark/bench_scale.py     # NEW: Benchmark
```
