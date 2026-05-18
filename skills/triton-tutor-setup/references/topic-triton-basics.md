# Topic 1: Triton Basics (Foundation)

> **Lazy-load**: read this file ONLY when authoring `01-Triton-Basics/` in Phase TU6. Drop from working memory before reading the next topic file.

## Authoritative URLs

- Triton main repo: https://github.com/triton-lang/triton
- Triton docs site: https://triton-lang.org/main/
- Getting started tutorials: https://triton-lang.org/main/getting-started/tutorials/
- Tutorial 01 (Vector Add): https://triton-lang.org/main/getting-started/tutorials/01-vector-add.html
- Triton language reference: https://triton-lang.org/main/python-api/triton.language.html
- Triton paper (Tillet et al., MAPL 2019): https://www.eecs.harvard.edu/~htk/publication/2019-mapl-tillet-kung-cox.pdf
- OpenAI Triton blog post: https://openai.com/index/triton/

## Prerequisites

- Python 3.9+ proficiency (NumPy / PyTorch tensor semantics).
- Basic GPU concept (threads run in parallel, memory is on a separate device).
- PyTorch tensor basics (`.shape`, `.stride()`, `.dtype`, `.to("cuda")`).
- **No prior CUDA / kernel-programming knowledge required** — Triton's appeal is removing thread-level reasoning.

## Core Concepts / Keywords (Beginner → Expert)

| Stage | Concepts |
|-------|----------|
| **Beginner** | `@triton.jit` decorator, kernel launch with `kernel[grid](...)`, `tl.program_id(axis)`, `tl.num_programs(axis)`, `tl.arange(0, BLOCK_SIZE)`, `tl.constexpr`, `tl.load(ptr, mask, other)`, `tl.store(ptr, value, mask)`, pointer arithmetic (`ptr + offsets`), `triton.cdiv(M, BLOCK)` grid math, dtype handling (`x.to(tl.float16)`) |
| **Intermediate** | 2D tiles via `offs_m[:, None]` / `offs_k[None, :]` broadcasting, `tl.where(cond, a, b)`, elementwise ops (`+`, `*`, `tl.exp`, `tl.log`, `tl.maximum`), `tl.zeros`, `tl.full`, `tl.atomic_add` / `tl.atomic_min`, `tl.debug_barrier`, casting (`.to(tl.float32)`), `tl.cast` with rounding modes, `tl.reshape`, `tl.trans`, `tl.broadcast_to` |
| **Advanced** | `tl.make_block_ptr(base, shape, strides, offsets, block_shape, order)` + `tl.advance(ptr, offsets)`, TMA-eligible loads on Hopper, `tl.multiple_of` / `tl.max_contiguous` hints, `tl.assume`, `tl.philox` / `tl.rand` for stochastic ops, masked atomics, kernel-internal `@triton.jit` helper functions, `tl.static_assert`, `tl.static_print` |
| **Expert** | Stable vs experimental APIs, in-place mutation patterns (avoid), pipelining-friendly access patterns (compiler recognizes), `tl.inline_asm_elementwise` for PTX/AMDGCN escape, debugging compile errors, profile-driven block-size selection, when to switch to raw CUDA |

## Hands-On Milestones

1. **M1: Vector add** — port the tutorial 01 vector-add, run on GPU, verify against `a + b` in PyTorch. Success: max abs diff = 0.
2. **M2: Fused elementwise** — fuse `y = sigmoid(x) * x` ("SwiGLU lite") into a single kernel. Success: matches `torch.sigmoid(x) * x` and beats the unfused PyTorch version on a 16M-element tensor.
3. **M3: 2D tile load/store** — implement a kernel that copies a `(M, N)` tensor in `(BLOCK_M, BLOCK_N)` tiles using broadcasting `offs_m[:, None]` / `offs_n[None, :]`. Success: bit-exact copy, ≥80% of `torch.clone` bandwidth.
4. **M4: Mask + other** — modify M3 so `M` and `N` are non-multiples of `BLOCK_M`/`BLOCK_N`; correctly mask the tail using `tl.load(..., mask=..., other=0.0)`. Success: no OOB reads (verify with `compute-sanitizer`).
5. **M5: Block pointer rewrite** — rewrite M3/M4 using `tl.make_block_ptr` + `tl.advance` instead of raw pointer arithmetic. Success: same correctness; on Hopper, TTGIR dump shows TMA descriptor usage.
6. **M6: Atomic histogram** — kernel that increments a histogram bucket per input element using `tl.atomic_add`. Success: matches `torch.bincount` for a 1M-element input.
7. **M7: Interpreter sanity test** — run M3 under `TRITON_INTERPRET=1`, then on GPU; confirm both give the same result. Success: parity.

## Common Pitfalls / Exam Traps

- **`tl.load` without `other=`** — masked-out lanes contain undefined data. If the result is used in math (especially reductions), you get garbage. Always set `other=0.0` (or appropriate identity) when the masked value will participate in computation.
- **Forgetting `tl.constexpr` on tile sizes** — block sizes MUST be `tl.constexpr` to be used as `tl.arange` bounds. Without it: cryptic compile error.
- **`tl.arange` with non-power-of-2** — compiles only on powers of 2 (typically). Use `tl.arange(0, 64)`, not `tl.arange(0, 100)`.
- **Python `if` vs `tl.where`** — Python `if x > 0:` runs at trace time on a constexpr/literal, NOT at kernel time. Branching on data-dependent values requires `tl.where`. Subtle silent bug.
- **Broadcasting confusion** — Triton requires explicit `[:, None]` / `[None, :]` for shape promotion in 2D. NumPy-style implicit broadcast often errors.
- **Atomic without mask** — `tl.atomic_add(ptr, val)` on OOB pointers corrupts arbitrary memory. Always pass `mask=`.
- **Dtype mismatch in `tl.dot`** — operand dtype must match a supported MMA path. FP16 ⊗ FP16 → FP32 is the canonical case; mixing FP16 ⊗ FP32 will produce a compiler error or silent slow path.
- **`tl.program_id` axis confusion** — axes correspond to grid dims. A 1D grid only has `axis=0`; querying `axis=1` returns 0 (or errors depending on version).
- **Stride bug from contiguous-mismatch** — Triton kernels assume the caller passes correct strides. If you pass a transposed view's strides incorrectly, the kernel silently reads the wrong memory.

## Cross-Links to Other Topics

- **→ Topic 2 (Tiling & Autotuning)** — once a kernel works, `BLOCK_SIZE`, `num_warps`, `num_stages` selection becomes the dominant performance lever. Autotune systematizes the search.
- **→ Topic 3 (Matmul Patterns)** — matmul is the canonical use case for 2D tiles, `tl.dot`, and `tl.make_block_ptr`. The skills you build here transfer directly.
- **→ Topic 5 (Compiler Internals)** — `@triton.jit` → TTIR is the first hop. Understanding the IR explains compile errors and hints (`tl.multiple_of`, `tl.max_contiguous`).
- **→ Topic 6 (Ecosystem & Production)** — Inductor codegens Triton kernels using exactly the primitives in this topic. Reading Inductor output is much easier with Topic 1 ownership.

## Practice Question Seeds

1. Launch grid `(triton.cdiv(N, BLOCK_SIZE),)` for a vector-add kernel. What does `tl.program_id(axis=0)` return on the 4th block instance? What happens if you call `tl.program_id(axis=1)` on a 1D grid?
2. Kernel does `x = tl.load(ptr + offsets, mask=offsets < N)`. For masked-out lanes, what value does `x` contain? Contrast with `tl.load(ptr + offsets, mask=offsets < N, other=0.0)`.
3. Mark `BLOCK_SIZE: tl.constexpr` in the signature. What changes about the compilation cache compared to a runtime int arg? What happens if you call the kernel with 3 different `BLOCK_SIZE` values?
4. A 2D kernel computes `a_ptrs = a_ptr + offs_m[:, None] * stride_am + offs_k[None, :] * stride_ak`. What dtype is `a_ptrs`? Why are `[:, None]` and `[None, :]` necessary?
5. `tl.where(mask[:, None], a, 0.0)` where `a` has shape `(M, N)` and `mask` has shape `(M,)`. What gets selected? How is broadcasting different from NumPy here?
6. Why must the argument to `tl.arange(0, BLOCK_SIZE)` be a `tl.constexpr` power of 2? What error does the compiler give for `tl.arange(0, 100)`?
7. Contrast `tl.make_block_ptr(...)` + `tl.advance(...)` with raw pointer arithmetic. When does block_ptr enable TMA lowering on Hopper?
8. `tl.atomic_add(ptr, value, mask)` for a reduction across blocks. What ordering guarantee do you get? What happens if two blocks race on the same address?
9. `if pid == 0: tl.store(...)` — what does the compiler do with the Python `if`? Contrast with `tl.where(pid == 0, x, y)`.
10. `tl.reshape(x, (BLOCK_M, BLOCK_K))` from a flat `(BLOCK_M * BLOCK_K,)` tile. Restrictions? Does the data layout change?
