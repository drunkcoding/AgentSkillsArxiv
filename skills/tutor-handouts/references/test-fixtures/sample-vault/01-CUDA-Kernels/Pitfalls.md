# Pitfalls — CUDA Kernels (test fixture)

> [!danger]- Bank conflicts on 32-bit stride
> **What**: Indexing `tile[ty][tx]` with both dims power-of-2 creates 32-way conflicts.
> **Why**: Shared memory has 32 banks of 4 bytes each.
> **Fix**: Pad the inner dim by 4 bytes, or apply XOR swizzle.
> **Related**: [[Concepts/cp-async]]
