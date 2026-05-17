# CUDA Codebase Mode — Templates

## Vault Folder Structure

```
StudyVault/
├── 00-Dashboard/             # MOC + Quick Reference + Build Matrix + Kernel Surface
├── 01-Architecture/          # System overview, kernel dispatch flow, memory model
├── 02-<Module1>/             # Per-module notes
├── 03-<Module2>/
├── ...
├── NN-DevOps/                # Build flags, CI, profiling
└── NN+1-Exercises/
```

## Dashboard MOC Template

```markdown
---
module: dashboard
path: 00-Dashboard
keywords: MOC, onboarding, <project-name>, cuda
---

# <Project Name> — Onboarding MOC

#dashboard #onboarding

## Architecture Overview
- **Pattern**: <kernel library / collective lib / app / driver>
- **CUDA Toolkit**: <version>
- **Target SMs**: <e.g., sm_80 sm_90 sm_100>
- **External libs**: <cuBLAS / CUTLASS / NCCL / NVSHMEM / cuDNN>
- → [[01-Architecture/System-Overview]]
- → [[01-Architecture/Kernel-Dispatch-Flow]]
- → [[01-Architecture/Memory-Model]]

## Module Map
| Module | Purpose | Key Kernel | Host Wrapper | Notes |
|--------|---------|------------|--------------|-------|
| <name> | <1-line purpose> | `<kernel_fn>` | `<wrapper_fn>` | [[Module Note]] |

## Kernel Surface
| Kernel | File | Target SM | MMA Used | Host Wrapper | Notes |
|--------|------|-----------|----------|--------------|-------|
| `<kernel_fn>` | `<path>` | sm_90 | wgmma 64x128x16 | `<wrapper>` | [[Kernel Note]] |

## Build Matrix
| Precision | sm_80 | sm_90 | sm_100 | Notes |
|-----------|-------|-------|--------|-------|
| FP16 | ✅ | ✅ | ✅ | |
| BF16 | ✅ | ✅ | ✅ | |
| FP8 | — | ✅ | ✅ | sm_89+/sm_90+ |
| FP4 | — | — | ✅ | Blackwell only |

## Getting Started
1. Prerequisites: CUDA Toolkit <version>, NVIDIA Driver <version>+
2. Build: `<exact command>`
3. Run test: `<exact command>`
4. Run benchmark: `<exact command>`

## Profile / Debug Commands
| Tool | Command |
|------|---------|
| Nsight Compute | `ncu --kernel-name=<kernel> --launch-skip=0 --launch-count=1 ./bin` |
| Nsight Systems | `nsys profile -t cuda,nvtx -o profile.nsys-rep ./bin` |
| compute-sanitizer | `compute-sanitizer --tool=memcheck ./bin` |
| Memory race check | `compute-sanitizer --tool=racecheck ./bin` |

## Common Env Vars
| Var | Purpose |
|-----|---------|
| `CUDA_VISIBLE_DEVICES` | Restrict GPUs |
| `CUDA_LAUNCH_BLOCKING=1` | Serialize launches for debugging |
| `NCCL_DEBUG=INFO` | NCCL verbose log |
| `NVSHMEM_DEBUG=INFO` | NVSHMEM verbose log |

## Tag Index
| Tag | Description | Rule |
|-----|-------------|------|
| `#arch-*` | Architecture concepts | Top-level pattern tags |
| `#sm-*` | SM target | sm_80, sm_90, sm_100 |
| `#kernel-*` | Kernel role | One per kernel category |
| `#mma-*` / `#tma` / `#cp-async` | Hardware mechanism | When the module uses it |

## Onboarding Path
1. [[01-Architecture/System-Overview]] — big picture
2. [[01-Architecture/Kernel-Dispatch-Flow]] — how host code reaches device entry
3. [[01-Architecture/Memory-Model]] — tiling strategy across the codebase
4. Module-by-module deep dives (in dependency order)
5. [[Exercises]]
```

## Module Note Template

```markdown
---
module: <module-name>
path: <relative-path-from-project-root>
target_sm: [sm_80, sm_90]
mma_atoms: [wgmma_64_128_16_f16f16f32]
keywords: <3-5 English keywords>
---

# <Module Name> (<Importance: ★~★★★>)

#kernel-<role> #sm-<target>

## Purpose
<1-3 sentences>

## Key Files
| File | Role |
|------|------|
| `<path>` | <description> |

## Public Interface
| Export | Type | Description |
|--------|------|-------------|
| `<name>` | host function / device kernel / Python binding | <what it does> |

## Host Wrapper
- Entry: `<wrapper_fn>` at `<path>:<line>`
- Launch config: `<<<grid, block, smem, stream>>>` or `cuLaunchKernelEx(...)`
- Dispatch logic: <how it selects the right device kernel template>

## Device Entry
- Kernel: `<kernel_fn>` at `<path>:<line>`
- Template params: <key template parameters>
- Thread layout: <ThreadblockShape, WarpShape, InstructionShape>

## Memory Tiling
```text
Global → Shared (CTA tile = <M>x<N>x<K>)
       → Register (warp tile = <m>x<n>x<k>)
       → MMA fragment (<MMA instruction operand shape>)
```
- Smem layout / swizzle: <describe>
- Async copy mechanism: <cp.async / cp.async.bulk / TMA descriptor>

## Sync Pattern
- Barriers used: `__syncthreads()` / `__syncwarp()` / `cuda::barrier` / `cute::tma_load_arrive`
- Pipeline depth: <N stages>

## Dependencies
| Direction | Module / Lib | Via |
|-----------|--------------|-----|
| **Uses** | <dep> | `<#include / call>` |
| **Used by** | <dependent> | `<#include / call>` |

## Configuration
| Macro / Env / Template | Purpose | Default |
|------------------------|---------|---------|
| `<MACRO>` | <description> | `<default>` |

## Testing
- Unit test: `<test target>` — run with `<command>`
- Benchmark: `<bench target>` — run with `<command>`
- Reference: <how correctness is verified — cuBLAS, NumPy, etc.>

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
target_sm: [sm_90]
keywords: gemm, mma, wgmma
---

# Kernel: `<kernel_fn_name>`

#kernel-<role> #mma-<atom> #sm-<target>

## Signature
```cpp
template <class TiledMma, class TiledCopyA, class TiledCopyB, ...>
__global__ void <kernel_fn_name>(...) { ... }
```

## What it does
<2-3 lines>

## Algorithm
```text
<ASCII diagram of the algorithm: prologue → mainloop → epilogue>
```

## Per-Stage Detail
1. **Prologue** — load first tile via `cp.async.bulk` (TMA) / `cp.async`.
2. **Mainloop** — N-stage pipeline of TMA load + `wgmma.mma_async`.
3. **Epilogue** — store accumulator with optional fused activation.

## Tile Sizes
- CTA tile: <MxNxK>
- Warp / warpgroup tile: <MxNxK>
- MMA instruction: <MxNxK>

## Register Usage
- Accumulator regs: <N>
- Total regs/thread: <N> (from `--resource-usage`)
- Shared mem/CTA: <N KiB>

## Performance Notes
- Peak: <% of SM peak FLOPS at this shape>
- Memory-bound vs compute-bound: <which one>
- Known bottleneck: <e.g., L2 bandwidth>

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
> Trace what happens when `<wrapper>(M=4096, N=4096, K=4096, dtype=fp16)` is called.

> [!answer]- View Answer
> 1. `<wrapper>` selects template specialization `<spec>` (file:line).
> 2. Launch config: `<<<(<grid>), (<block>), <smem>>>`.
> 3. Device entry: `<kernel>` (file:line).
> 4. Prologue: TMA loads first K-tile of A and B via `cp.async.bulk.tensor`.
> 5. Mainloop: `<N>`-stage pipeline of TMA + WGMMA.
> 6. Epilogue: store accumulator to global.

---

## Ex 2 — Configuration [config]
> How would you add support for a new tile shape `<MxNxK>` to this kernel?

> [!answer]- View Answer
> - File: `<path>` — add a new template specialization.
> - Register usage check: `--resource-usage` must fit `<limit>`.
> - Smem usage check: must fit `<limit KiB>` per SM.
> - Add test case in `<test file>`.

---

## Ex 3 — Debugging [debug]
> `compute-sanitizer --tool=racecheck` reports a race in this kernel between the prologue TMA load and the first MMA. Where would you look?

> [!answer]- View Answer
> 1. Check the TMA arrival barrier: `cute::tma_load_arrive` vs `cute::tma_load_wait`.
> 2. Common cause: missing `cuda::barrier::arrive_and_wait` before consuming the loaded tile.
> 3. Look at file:line for the `mbarrier::wait` / `wgmma.fence` pair.

---

## Ex 4 — Extension [extend]
> How would you add a fused activation (e.g., ReLU) to the epilogue?

> [!answer]- View Answer
> 1. Modify the epilogue functor: file:line.
> 2. Add ReLU as a template parameter or a runtime arg.
> 3. Plumb it through the host wrapper template parameters.
> 4. Add a test in `<test file>`.

---

> [!summary]- Learning Points
> | Topic | Key Takeaway |
> |-------|-------------|
> | TMA / cp.async.bulk | Tensor-descriptor-driven async load on Hopper+ |
> | WGMMA | Warpgroup-async MMA, requires explicit fence/wait |
> | Pipeline | N-stage producer-consumer with mbarriers |
```

## Formatting Rules

- `[[wiki-links]]` for all cross-references.
- Callouts: `> [!tip]`, `> [!important]`, `> [!warning]`, `> [!danger]`.
- ASCII diagrams for kernel internal flow.
- Tables over prose.
- **Bold** for critical file paths.
- Code blocks with language hints (`cpp`, `cuda`, `bash`, `python`).
- CUDA identifiers verbatim in English regardless of prose language.
