# Pitfalls — CUTLASS (test fixture)

> [!danger]- MMA atom does not match arch
> **What**: Selecting `MMA_Atom<SM80_16x8x16>` for an sm_90 build silently
> falls back to slower kernels.
> **Why**: WGMMA atoms (`SM90_64x*x*`) require warp-specialization, not just sm_90.
> **Fix**: Use `MMA_Atom<SM90_64x128x16_F16F16F16_SS>` for Hopper FP16.
> **Related**: [[Concepts/cute-layout]]
