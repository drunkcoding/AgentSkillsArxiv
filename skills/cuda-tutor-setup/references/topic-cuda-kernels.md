# Topic 1: CUDA Kernels (Foundation)

> **Lazy-load**: read this file ONLY when authoring `01-CUDA-Kernels/` in Phase CU6. Drop from working memory before reading the next topic file.

## Authoritative URLs

- CUDA C++ Programming Guide: https://docs.nvidia.com/cuda/cuda-c-programming-guide/
- PDF mirror: https://docs.nvidia.com/cuda/pdf/CUDA_C_Programming_Guide.pdf
- PTX ISA Reference: https://docs.nvidia.com/cuda/parallel-thread-execution/
- CUDA Best Practices Guide: https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/
- CUDA Toolkit docs root: https://docs.nvidia.com/cuda/
- CUDA Samples: https://github.com/NVIDIA/cuda-samples
- Nsight Compute User Guide: https://docs.nvidia.com/nsight-compute/

## Prerequisites

- C++ fundamentals (pointers, stack vs heap, templates).
- Basic computer architecture (registers, cache hierarchy, SIMD concept).
- Linux command line.
- **No prior GPU knowledge required** — this is the foundation topic.

## Core Concepts / Keywords (Beginner → Expert)

| Stage | Concepts |
|-------|----------|
| **Beginner** | `__global__`, kernel launch `<<<grid, block>>>`, thread hierarchy (`threadIdx`, `blockIdx`, `blockDim`, `gridDim`), 1D/2D/3D indexing, `cudaMalloc`/`cudaMemcpy`, `cudaStream_t`, error handling (`cudaGetLastError`, `cudaPeekAtLastError`), `nvcc` compilation, host vs device code |
| **Intermediate** | Shared memory `__shared__`, bank conflicts (32 banks × 4 bytes on most archs), `__syncthreads()`, `__syncwarp()`, constant memory + broadcast cache, texture memory, pinned (page-locked) memory, unified memory `cudaMallocManaged` + `cudaMemPrefetchAsync`, `cudaMemcpyAsync`, atomics (`atomicAdd`, `atomicCAS`, scoped atomics), `__threadfence()`, occupancy calculator, NVCC `--resource-usage` |
| **Advanced** | Cooperative Groups (`thread_block`, `grid_group`, `cluster_group`), warp-level primitives (`__shfl_sync`, `__shfl_xor_sync`, `__ballot_sync`, `__any_sync`, `__all_sync`), warp reduction patterns, `__ldg()` read-only path, `cp.async` (Ampere), `cp.async.bulk` / TMA (Hopper+), CUDA Graphs (`cudaGraph_t`, `cudaGraphExec_t`), dynamic parallelism, thread block clusters (Hopper), async barriers (`cuda::barrier`), `cuda::pipeline` |
| **Expert** | Inline PTX assembly (`asm volatile`), WGMMA (`wgmma.mma_async`), `mma.sync` (HMMA/IMMA), L2 cache residency hints, Tensor Core operand layout (swizzle/permute), `wgmma.fence` / `wgmma.commit_group` / `wgmma.wait_group`, mbarrier-based pipelining, NVRTC runtime compilation, JIT linking, PTX-vs-SASS analysis with `cuobjdump --dump-sass` |

## Hands-On Milestones

1. **M1: Vector add** — compile `nvcc vecadd.cu -o vecadd`, launch `<<<N/256, 256>>>` kernel, verify with `compute-sanitizer --tool=memcheck`. Success: zero memcheck errors, output matches CPU reference.
2. **M2: Tiled GEMM (shared memory)** — implement 16×16 tile GEMM, show ≥2× speedup over naive global-memory matmul on a 4096×4096 problem. Success: measured speedup ratio + correctness vs cuBLAS.
3. **M3: Warp reduction** — implement parallel reduction using `__shfl_xor_sync` for the intra-warp step + shared memory for inter-warp. Success: result matches CPU sum for 1 M floats, ≤1 ULP drift.
4. **M4: cp.async pipeline** — convolution kernel using `cp.async` to hide global-load latency behind compute. Success: Nsight Compute shows ≥80% memory throughput utilization.
5. **M5: Cooperative grid sync** — launch a kernel using `grid_group::sync()` (requires `cudaLaunchCooperativeKernel`). Success: kernel sees correct global state after sync.
6. **M6: Occupancy tuning** — profile a kernel, identify reg/smem pressure, tune `__launch_bounds__` to reach ≥80% achieved occupancy. Success: Nsight Compute reports the target.
7. **M7: WGMMA hello-world** (Hopper+) — write a minimal PTX `wgmma.mma_async` invocation, verify result against a CPU reference. Success: bitwise-correct FP16 GEMM tile.

## Common Pitfalls / Exam Traps

- **`__syncthreads()` inside divergent branch** — causes deadlock. The barrier must be hit by ALL threads in the block. Classic interview trap.
- **Warp divergence** — `if (threadIdx.x % 2)` causes both paths to execute serially with masking. Not free branching.
- **Bank conflicts** — `smem[threadIdx.x * stride]` where `stride % 32 == 0` serializes a warp's accesses.
- **Coalesced load mis-assumption** — global loads are coalesced only when consecutive threads access consecutive addresses within a 128-byte segment. Strided access breaks coalescing.
- **Occupancy ≠ performance** — high occupancy with poor locality can be slower than low occupancy with cache-friendly tiling.
- **`cudaMemcpy` vs `cudaMemcpyAsync`** — synchronous vs stream-enqueued. Async needs pinned host memory to actually overlap.
- **Error checking after kernel launch** — `cudaGetLastError()` catches launch errors; execution errors require a stream/device sync first.
- **Unified memory false-share** — concurrent CPU+GPU access to the same page causes thrashing. Use `cudaMemPrefetchAsync` and `cudaMemAdvise`.
- **Constant memory scatter** — constant cache broadcasts on uniform access, serializes on scattered access. Not free random-access memory.
- **`cp.async` without commit/wait** — `cp.async` enqueues; you must `cp.async.commit_group` + `cp.async.wait_group N` to ensure the data is visible.
- **WGMMA without fence** — `wgmma.mma_async` is async; the operand registers cannot be read until `wgmma.commit_group` + `wgmma.wait_group` complete.

## Cross-Links to Other Topics

- **→ Topic 2 (CUTLASS)** — CUTLASS kernels are CUDA kernels. CTA tiling, shared-memory swizzles, warp-level MMA all build directly on the concepts here. You cannot meaningfully read CUTLASS without owning this topic.
- **→ Topic 3 (cuTile)** — cuTile is a Python tile-DSL that **compiles to** these same CUDA kernels. Understanding the underlying execution model (warps, smem, sync) explains the cost model cuTile abstracts.
- **→ Topic 4 (Open GPU Kernel Modules)** — CUDA kernels are launched via `cuLaunchKernel` in `libcuda.so`, which dispatches an RPC through `nvidia.ko` into GSP firmware. The driver stack is what runs your kernel.
- **→ Topic 5 (NCCL)** — NCCL's collectives are CUDA kernels using ring/tree patterns over peer-to-peer memory. Warp-level scatter/gather and `__threadfence_system` are the building blocks.
- **→ Topic 6 (NVSHMEM)** — `nvshmem_put` from device code is a CUDA-thread-initiated remote write. Memory ordering (`__threadfence`, `cuda::memory_order`) is prerequisite to using NVSHMEM correctly.

## Practice Question Seeds

1. Launch config `<<<128, 256>>>`, 32 regs/thread, 4 KiB smem/block, A100 (108 SMs, max 2048 threads/SM, 64K regs/SM, 164 KiB smem/SM). Compute theoretical occupancy.
2. Given `__shared__ float smem[256]` accessed as `smem[threadIdx.x * 4]` on Ampere (4-byte banks, 32 banks). Are there bank conflicts? Show your work.
3. Write a warp-OR using only `__shfl_sync`. How does this differ from `__any_sync`?
4. A kernel does `if (threadIdx.x == 0) {...}`. What are the two performance concerns, and how do they differ for a 32-thread block vs a 128-thread block?
5. Draw the memory hierarchy for a 1024×1024 tiled GEMM with 16×16 thread blocks and 16×16 shared-memory tiles. Label global / L2 / L1-smem / registers, indicate reuse across the K loop.
6. Contrast `cp.async` and a regular global-to-shared load. Include the `cp.async.commit_group` / `cp.async.wait_group` pattern.
7. A kernel reads `const float data[16]` via `data[threadIdx.x % 16]`. What happens in the constant cache? What's the effective per-warp bandwidth?
8. Contrast `__threadfence()` vs `__syncthreads()`. Name a scenario where you need `__threadfence()` but NOT `__syncthreads()`.
9. Using cooperative groups, design a kernel where all threads in a 128×128 2D grid synchronize without deadlock.
10. On Hopper, `wgmma.mma_async` takes operands with specific layouts. Why does CUTLASS 3.x use `cute::Layout` to describe MMA operands, and how does that map to the hardware's expected stride pattern?
