---
topic: cuda-kernels
keywords: warp, block, sm, memory hierarchy
hardware: hopper
---

# CUDA Kernels — Overview (test fixture)

#topic-cuda-kernels

The CUDA programming model exposes the GPU as a grid of thread blocks, each
containing up to 1024 threads grouped into 32-thread warps. On H100 SM90,
132 SMs each execute up to 64 warps concurrently across 4 warp schedulers.
