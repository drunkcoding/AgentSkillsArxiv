---
topic: cutlass
keywords: cute, layout, mma, gemm
hardware: hopper
---

# CUTLASS + CuTe — Overview (test fixture)

#topic-cutlass

CUTLASS is NVIDIA's open-source GEMM template library. CuTe (CUDA Tensor) is
its layout algebra, providing `Layout<Shape, Stride>` primitives. On H100 SM90,
CUTLASS uses `wgmma.mma_async` warp-group MMA instructions for FP16/BF16 GEMM.
