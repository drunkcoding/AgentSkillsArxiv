# Triton Codebase Mode — Templates

## Vault Folder Structure

```
StudyVault/
├── 00-Dashboard/             # MOC + Quick Reference + Backend Matrix + Kernel Surface
├── 01-Architecture/          # System overview, kernel dispatch, autotune flow
├── 02-<Module1>/             # Per-module notes
├── 03-<Module2>/
├── ...
├── NN-DevOps/                # Build flags, CI, benchmarking
└── NN+1-Exercises/
```

## Dashboard MOC Template

```markdown
---
module: dashboard
path: 00-Dashboard
keywords: MOC, onboarding, <project-name>, triton
---

# <Project Name> — Onboarding MOC

#dashboard #onboarding

## Architecture Overview
- **Pattern**: <kernel library / Inductor backend / compiler fork / training app>
- **Triton Version**: <version>
- **Target Backends**: <nvidia | amd | intel>
- **Target Archs**: <e.g., sm_80 sm_90 sm_100 cdna3>
- **External libs**: <torch / flash_attn / xformers / fbgemm / proton>
- → [[01-Architecture/System-Overview]]
- → [[01-Architecture/Kernel-Dispatch-Flow]]
- → [[01-Architecture/Autotune-Flow]]

## Module Map
| Module | Purpose | Key Kernel | Python Wrapper | Notes |
|--------|---------|------------|----------------|-------|
| <name> | <1-line purpose> | `<kernel_fn>` | `<wrapper_fn>` | [[Module Note]] |

## Kernel Surface
| Kernel | File | Target Backend | tl.dot dtypes | Wrapper | Autotune Key | Notes |
|--------|------|----------------|---------------|---------|--------------|-------|
| `<kernel_fn>` | `<path>` | nvidia (sm_90) | fp16/fp32 | `<wrapper>` | `[M, N, K]` | [[Kernel Note]] |

## Backend Matrix
| Precision | NVIDIA sm_80 | NVIDIA sm_90 | NVIDIA sm_100 | AMD MI300 | Notes |
|-----------|--------------|--------------|---------------|-----------|-------|
| FP16 | ✅ | ✅ | ✅ | ✅ | |
| BF16 | ✅ | ✅ | ✅ | ✅ | |
| FP8 (E4M3/E5M2) | — | ✅ | ✅ | ⚠️ partial | Hopper+ |

## Getting Started
1. Prerequisites: PyTorch <version>, Triton <version>, CUDA <version> / ROCm <version>
2. Install: `<exact command>` (typically `pip install -e .` or `pip install triton==X.Y`)
3. Run test: `<exact command>` (typically `pytest tests/`)
4. Run benchmark: `<exact command>`

## Profile / Debug Commands
| Tool | Command |
|------|---------|
| Triton interpreter | `TRITON_INTERPRET=1 python kernel.py` |
| IR dump (all stages) | `TRITON_KERNEL_DUMP=1 MLIR_ENABLE_DUMP=1 LLVM_IR_ENABLE_DUMP=1 python kernel.py` |
| proton profiler | `proton --hook=triton --name=run python bench.py` |
| Nsight Compute | `ncu --kernel-name regex:<kernel> --launch-skip=0 --launch-count=1 python bench.py` |
| Autotune trace | `TRITON_PRINT_AUTOTUNING=1 python bench.py` |

## Common Env Vars
| Var | Purpose |
|-----|---------|
| `CUDA_VISIBLE_DEVICES` | Restrict GPUs |
| `TRITON_INTERPRET` | Run kernels in pure-Python interpreter |
| `TRITON_CACHE_DIR` | Override compile cache location |
| `TRITON_KERNEL_DUMP` | Dump compiled artifacts per kernel |
| `MLIR_ENABLE_DUMP` | Dump TTIR/TTGIR between passes |
| `TRITON_PRINT_AUTOTUNING` | Print selected autotune config + bench timing |

## Tag Index
| Tag | Description | Rule |
|-----|-------------|------|
| `#backend-*` | Backend gating | nvidia / amd / intel |
| `#arch-*` | Architecture gating | ampere / hopper / blackwell / cdna3 |
| `#kernel-*` | Kernel role | One per kernel category |
| `#tl-*` / `#triton-autotune` | Triton mechanism | When the module uses it |
| `#ir-*` | IR stage | Only on compiler-internals notes |

## Onboarding Path
1. [[01-Architecture/System-Overview]] — big picture
2. [[01-Architecture/Kernel-Dispatch-Flow]] — how Python code reaches `@triton.jit`
3. [[01-Architecture/Autotune-Flow]] — autotune search, cache, perf model
4. Module-by-module deep dives (in dependency order)
5. [[Exercises]]
```

## Module Note Template

```markdown
---
module: <module-name>
path: <relative-path-from-project-root>
target_backend: [nvidia, amd]
target_arch: [sm_80, sm_90, cdna3]
tl_mechanisms: [tl.dot, tl.make_block_ptr, tl.associative_scan]
keywords: <3-5 English keywords>
---

# <Module Name> (<Importance: ★~★★★>)

#kernel-<role> #backend-<target>

## Purpose
<1-3 sentences>

## Key Files
| File | Role |
|------|------|
| `<path>` | <description> |

## Public Interface
| Export | Type | Description |
|--------|------|-------------|
| `<name>` | python function / `@triton.jit` kernel / PyTorch custom op | <what it does> |

## Python Wrapper
- Entry: `<wrapper_fn>` at `<path>:<line>`
- Grid: `<grid expression, e.g., (triton.cdiv(M, BM) * triton.cdiv(N, BN),)>`
- Dispatch logic: <how it picks autotune key / backend>

## `@triton.jit` Kernel
- Kernel: `<kernel_fn>` at `<path>:<line>`
- `tl.constexpr` params: <BLOCK_SIZE_M, BLOCK_SIZE_N, BLOCK_SIZE_K, GROUP_SIZE_M, ...>
- Runtime args: <pointers, strides, dims>

## Tile Shapes
```text
Block tile  = <BM>x<BN>x<BK>
Warp tile   = <warp_m>x<warp_n>x<warp_k> (implicit, driven by num_warps)
MMA fragment = <e.g., wgmma 64x256x16 for fp16 on Hopper>
```
- Smem usage: <approx KiB per CTA>
- Reg pressure: <approx per thread>

## Autotune Config Space
| Config | num_warps | num_stages | Notes |
|--------|-----------|------------|-------|
| `BM=128, BN=256, BK=64` | 8 | 3 | Big square shapes on H100 |
| `BM=64, BN=64, BK=32` | 4 | 2 | Small / skinny shapes |

- Cache key: `[M, N, K, dtype]`
- Pruning hook: <`prune_configs_by` if used>

## Dependencies
| Direction | Module / Lib | Via |
|-----------|--------------|-----|
| **Uses** | <dep> | `<import / call>` |
| **Used by** | <dependent> | `<import / call>` |

## Configuration
| Macro / Env / Constexpr | Purpose | Default |
|-------------------------|---------|---------|
| `<NAME>` | <description> | `<default>` |

## Testing
- Unit test: `<test target>` — run with `<command>`
- Benchmark: `<bench target>` — run with `<command>`
- Reference: <how correctness is verified — torch.mm, FP32 reference, etc.>

## Related Notes
- [[<Other Module>]]
- [[01-Architecture/<arch-note>]]
- [[Kernel Notes/<kernel-note>]] (if a per-kernel note exists)
```

## Kernel Note Template (one per significant kernel)

```markdown
---
module: <module>
kernel: <kernel_fn_name>
path: <file>:<line>
target_backend: [nvidia]
target_arch: [sm_90]
keywords: matmul, fp16, hopper
---

# Kernel: `<kernel_fn_name>`

#kernel-<role> #backend-<target>

## Signature
```python
@triton.autotune(configs=[...], key=["M", "N", "K"])
@triton.jit
def <kernel_fn_name>(
    a_ptr, b_ptr, c_ptr,
    M, N, K,
    stride_am, stride_ak,
    stride_bk, stride_bn,
    stride_cm, stride_cn,
    BLOCK_SIZE_M: tl.constexpr,
    BLOCK_SIZE_N: tl.constexpr,
    BLOCK_SIZE_K: tl.constexpr,
    GROUP_SIZE_M: tl.constexpr,
):
    ...
```

## What it does
<2-3 lines>

## Algorithm
```text
<ASCII diagram of the algorithm: pid swizzle → K-loop with tl.dot → epilogue store>
```

## Per-Stage Detail
1. **Grid + pid swizzling** — compute `pid_m`, `pid_n` with `GROUP_SIZE_M` swizzle for L2 reuse.
2. **Load tile pointers** — `a_ptrs`, `b_ptrs` via offset arithmetic or `tl.make_block_ptr`.
3. **K-loop** — N-stage pipelined `tl.load` + `tl.dot(a, b, acc)`.
4. **Epilogue** — `tl.store(c_ptrs, acc, mask=...)` with optional fused activation.

## Tile Shapes
- Block: <BM>x<BN>x<BK>
- `tl.dot` operand: <implicit per backend, e.g., wgmma 64x256x16 on Hopper>

## Autotune
- Configs: <N>
- Key: `[M, N, K, ...]`
- Typical winner on H100 for square 4K: `BM=128, BN=256, BK=64, GROUP_SIZE_M=8, num_warps=8, num_stages=3`

## Performance Notes
- Peak: <% of cuBLAS or theoretical SM peak at this shape>
- Memory-bound vs compute-bound: <which one>
- Known bottleneck: <e.g., autotune cache cold-start, smem pressure>

## Related
- [[<Module Note>]]
- [[<Test Note>]]
```

## Onboarding Exercise Template

```markdown
---
module: exercises
path: NN+1-Exercises
keywords: practice, onboarding, <topic>
---

# <Module> — Onboarding Exercises

#practice #onboarding #kernel-<role>

## Related Modules
- [[<Module Note>]]

---

## Ex 1 — Code Reading [trace]
> Trace what happens when `<wrapper>(M=4096, N=4096, K=4096, dtype=torch.float16)` is called.

> [!answer]- View Answer
> 1. `<wrapper>` computes grid = `(cdiv(4096, BM) * cdiv(4096, BN),)`.
> 2. Autotune evaluates configs with key `[4096, 4096, 4096, fp16]`; first call triggers benchmarking, subsequent calls hit cache.
> 3. Selected config: `<which one>` (file:line of config list).
> 4. `@triton.jit` kernel: `<kernel>` (file:line).
> 5. Pid swizzling: row-major to grouped-`GROUP_SIZE_M` for L2 reuse.
> 6. K-loop with `tl.dot(a, b, acc)`; on Hopper this lowers to `wgmma.mma_async`.
> 7. Epilogue: store `acc.to(tl.float16)` to `c_ptrs` with bounds-mask.

---

## Ex 2 — Configuration [config]
> How would you add an autotune config tuned for skinny matmuls (`M=8192, N=128, K=4096`)?

> [!answer]- View Answer
> - File: `<path>` — the `configs=[...]` list.
> - Add `triton.Config({"BLOCK_SIZE_M": 256, "BLOCK_SIZE_N": 32, "BLOCK_SIZE_K": 64, "GROUP_SIZE_M": 4}, num_warps=4, num_stages=3)`.
> - Verify with `TRITON_PRINT_AUTOTUNING=1 python bench.py --shapes 8192,128,4096`.
> - Add the shape to the bench harness.

---

## Ex 3 — Debugging [debug]
> The kernel returns NaN on the last row. `TRITON_INTERPRET=1` produces correct results. Where would you look?

> [!answer]- View Answer
> 1. Suspect a missing or wrong `mask` on `tl.load` for the M/N tail — interpreter handles OOB lazily, GPU does not.
> 2. Check `mask = offs_m[:, None] < M` and ensure `other=0.0` is set on `tl.load` for the K-loop accumulator inputs.
> 3. Check epilogue `tl.store(c_ptrs, acc, mask=mask_m[:, None] & mask_n[None, :])`.

---

## Ex 4 — IR Exploration [ir]
> Dump TTGIR for this kernel and identify the `#mma` layout. What happens if you halve `num_warps`?

> [!answer]- View Answer
> 1. Run `TRITON_KERNEL_DUMP=1 MLIR_ENABLE_DUMP=1 python kernel.py`.
> 2. Look in `$TRITON_CACHE_DIR/...` for `<hash>.ttgir`.
> 3. The `#mma` layout encodes `warpsPerCTA` — halving `num_warps` shrinks that dimension, increasing per-warp tile size and possibly causing reg spill.

---

## Ex 5 — Extension [extend]
> How would you add an FP8 path (E4M3 inputs, FP32 accumulator) to this kernel?

> [!answer]- View Answer
> 1. Add `tl.float8e4nv` casts on the `tl.load` results.
> 2. Use `tl.dot(a_fp8, b_fp8, acc_fp32, input_precision="ieee")`; ensure tile shapes match Hopper FP8 WGMMA requirements (M-tile multiple of 64, K-tile multiple of 32).
> 3. Add scale-tensor logic if using per-tensor scales.
> 4. Add a test with FP8 reference (cast → FP32 → matmul → cast).

---

> [!summary]- Learning Points
> | Topic | Key Takeaway |
> |-------|-------------|
> | Autotune | Cache key gates recompile cost |
> | tl.dot | Lowers to backend-specific MMA (wgmma / mma.sync / mfma) |
> | Masks | Required on M/N/K tails to avoid OOB |
> | IR dump | TTGIR layouts reveal warp-tile and shared-memory strategy |
```

## Formatting Rules

- `[[wiki-links]]` for all cross-references.
- Callouts: `> [!tip]`, `> [!important]`, `> [!warning]`, `> [!danger]`.
- ASCII diagrams for kernel internal flow + tile decomposition.
- Code blocks with language hints (`python`, `bash`, `mlir`).
- Tables over prose.
- **Bold** for critical file paths and `tl.*` identifiers.
- Triton identifiers verbatim in English regardless of prose language.
