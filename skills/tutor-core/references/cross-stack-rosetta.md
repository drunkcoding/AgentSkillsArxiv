# Cross-Stack Rosetta — CUDA / CUTLASS / cuTile ↔ Triton

> Bidirectional concept map. Used by both `cuda-tutor` and `triton-tutor` when a session includes any topic with a cross-stack peer (per `quiz-rules-shared.md` Cross-Stack Question Rule).

## How to read this file

- **Section 2–6** are the mapping tables (Memory & Tile, Compute, Scheduling, DSL, Compiler).
- Every mapping-table row has a stable `RID` (`R{section}-{row:02d}`). RIDs are never renumbered; appended rows take new RIDs at the end of their section.
- Every row's `Source` column cites either an in-repo topic reference (`topic-X.md §Section`) or an upstream URL listed in the topic's "Authoritative URLs" section.
- **Section 7** contains the cross-stack question seeds. Each seed is a YAML-fenced block with a stable schema; the linter parses these blocks mechanically to enforce distribution requirements.

## Citation rule (MANDATORY)

No mapping row and no question seed may be added without a verified `Source`. Hallucinated mappings are a correctness bug. The linter (`infra/scripts/check_rosetta_consistency.sh`) rejects empty/`TBD`/`?` sources.

---

## 2. Memory & Tile Abstractions

| RID | CUDA / CUTLASS / cuTile concept | Triton equivalent | Notes | Source |
|-----|----------------------------------|-------------------|-------|--------|
| R2-01 | `cute::Layout` + `Stride` (shape and stride tuple) | `tl.make_block_ptr(base, shape, strides, offsets, block_shape, order)` | Both describe a strided tile in N-D memory. CuTe layout algebra is more general; `make_block_ptr` is restricted to rectangular block-of-elements with constant strides. | topic-cutlass.md §Core Concepts (Advanced row) ; triton-lang.org/main/python-api/generated/triton.language.make_block_ptr.html |
| R2-02 | `cute::Tensor<Engine, Layout>` | block pointer + `tl.load(mask=…, other=…)` | `cute::Tensor` couples a layout with a backing pointer/engine. Triton's equivalent is the (block-ptr, mask, other) triple at the load site. | topic-cutlass.md §Core Concepts ; triton-lang.org/main/python-api/generated/triton.language.load.html |
| R2-03 | `cute::Swizzle<B, M, S>` (shared-mem bank-conflict layout) | `#shared` layout encoding with swizzle attribute (TTGIR) | CuTe swizzle and Triton `#shared` both avoid bank conflicts on smem. CuTe parameterizes (bits, mode, shift); Triton's compiler picks the swizzle during the coalescing/lowering pass. | docs.nvidia.com/cutlass/media/docs/cpp/cute/02_layout_algebra.html ; topic-compiler-internals.md §Layout encodings |
| R2-04 | CuTe register-resident `Layout` (per-thread fragment) | `#blocked` layout encoding (TTGIR) | Both describe how the elements of a tile are partitioned across threads of a CTA at register level. `#blocked` has `sizePerThread / threadsPerWarp / warpsPerCTA / order` attributes. | topic-cutlass.md §Core Concepts ; triton-lang.org/main/programming-guide/chapter-3/debugging.html |
| R2-05 | CUTLASS warp-MMA fragment layout (operand A/B/C) | `#dot_op` layout encoding (TTGIR) | Both pre-arrange operands into the layout the MMA hardware expects. The compiler inserts conversion layouts between `#blocked` (loaded form) and `#dot_op` (MMA-ready form). | topic-cutlass.md §Common Pitfalls (Swizzle mismatch) ; topic-compiler-internals.md §Layout encodings |
| R2-06 | `cp.async.bulk.tensor.*` (TMA, descriptor-based) | `tl.load(make_block_ptr(...))` lowered to TMA on SM90+ | TMA descriptors encode shape/stride/box in a single 128-byte object; one instruction launches the entire 1D–5D bulk copy. Triton emits TMA only when the pointer is from `tl.make_block_ptr` AND the target is SM90+. | topic-cuda-kernels.md §Core Concepts (Expert) ; docs.nvidia.com/cuda/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async-bulk-tensor |
| R2-07 | `cp.async` (Ampere per-thread async copy, 4/8/16 B) | `tl.load` inside an autotune config with `num_stages > 1` | Both implement pipelined global→shared loads. Ampere `cp.async` is per-thread; Triton's pipelining pass emits the cp.async instructions when `num_stages > 1`. | topic-cuda-kernels.md §Core Concepts ; topic-tiling-autotuning.md §Core Concepts |
| R2-08 | `mbarrier::arrive` / `mbarrier::wait` after a TMA load | implicit pipeline barrier emitted by Triton's pipeliner | A TMA load is async; consumers must wait on an mbarrier. CUTLASS exposes the mbarrier directly; Triton hides it — the pipeliner emits the barrier between stages. | topic-cuda-kernels.md §Common Pitfalls (Async copy without barrier) ; topic-compiler-internals.md §Core Concepts |
| R2-09 | `cutlass::layout::RowMajor` / `ColumnMajor` (template tag) | `(stride_m, stride_n)` arguments to `tl.make_block_ptr` | CUTLASS encodes major-ness in a layout type; Triton encodes it as runtime stride values you pass at launch. | topic-cutlass.md §Common Pitfalls (Layout transposition confusion) ; topic-triton-basics.md §Core Concepts (Intermediate) |
| R2-10 | CUTLASS epilogue boundary predicate (`PredicatedTileIterator`) | `tl.load(..., mask=offs < N, other=0.0)` | Both handle the ragged-tail problem when the matrix size is not a multiple of the tile shape. | topic-cutlass.md §Core Concepts (Intermediate) ; topic-triton-basics.md §Core Concepts |
| R2-11 | CuTe `cute::copy(TiledCopy, src, dst)` (2D tile copy with vectorization) | `tl.store(make_block_ptr(...), tile, boundary_check=...)` | Both move a tile and respect vectorization width / alignment automatically. | docs.nvidia.com/cutlass/media/docs/cpp/cute/00_quickstart.html ; triton-lang.org/main/python-api/generated/triton.language.store.html |
| R2-12 | Bank-conflict avoidance: `cute::Swizzle` parameter triple | Triton swizzling pass (one of the compiler passes between TTIR and TTGIR) | Conceptually identical; Triton's choice is automatic during lowering. | topic-cutlass.md §Common Pitfalls ; topic-compiler-internals.md §Compiler passes |

## 3. Compute Primitives

| RID | CUDA / CUTLASS / cuTile concept | Triton equivalent | Notes | Source |
|-----|----------------------------------|-------------------|-------|--------|
| R3-01 | CUTLASS `cutlass::arch::Mma_Atom<...>` (abstract MMA atom) | `tl.dot(a, b, acc)` | Both pick a hardware MMA instruction matching operand dtype + shape. CUTLASS exposes the atom explicitly in the type system; Triton hides it behind `tl.dot`. | topic-cutlass.md §Core Concepts (Advanced) ; topic-matmul-patterns.md §Core Concepts |
| R3-02 | Hopper `wgmma.mma_async.sync.aligned.*` (warp-group MMA) | `tl.dot` lowered to `#mma` encoding with Hopper backend | On SM90+, the Triton compiler lowers `tl.dot` to WGMMA when tile shapes meet the constraints (M%64==0, K%16==0 for FP16). | topic-cuda-kernels.md §Core Concepts (Expert) ; topic-matmul-patterns.md §Common Pitfalls (WGMMA tile-shape mismatch) |
| R3-03 | Ampere `mma.sync.aligned.m16n8k16.row.col.*` | `tl.dot` lowered to `mma.sync` (Ampere backend) | Per-warp MMA on Ampere. Triton emits this when targeting `sm_80`/`sm_86`. | docs.nvidia.com/cuda/parallel-thread-execution/index.html#warp-level-matrix-instructions ; topic-compiler-internals.md §Backends |
| R3-04 | (no CUTLASS analogue — CUTLASS is NVIDIA-only) | `tl.dot` lowered to AMD CDNA3 `mfma_*` instructions | Triton's multi-backend reach beyond NVIDIA is one of its main differentiators. | topic-compiler-internals.md §Backends (NVIDIA/AMD/Intel) |
| R3-05 | CUTLASS FP8 GEMM (`cutlass::float_e4m3_t` / `e5m2_t`, per-tensor scale) | `tl.dot(a_fp8, b_fp8, acc_fp32, input_precision="ieee")` with scale tensors | Both require per-tensor or per-block FP8 scales for any meaningful accuracy. Hopper FP8 MMA expects specific scale-layout conventions. | topic-cutlass.md §Core Concepts (Expert) ; topic-matmul-patterns.md §Core Concepts (Advanced) |
| R3-06 | CUTLASS epilogue α·MMA + β·C (single fused MAC step) | `tl.dot(a, b, acc)` 3-arg form (fused MAC, single MMA op) | The 3-arg form is the canonical idiom; older Triton versions only fused this form, recent versions fuse both but the 3-arg form is more robust. | topic-cutlass.md §Core Concepts ; topic-matmul-patterns.md §Common Pitfalls |
| R3-07 | CUTLASS `tfloat32_t` accumulator (TF32 inputs, FP32 accum) | Triton `input_precision="tf32"` arg to `tl.dot` | Both lower to TF32 MMA on Ampere+. Default is IEEE FP32 unless requested. | topic-cutlass.md §Core Concepts ; triton-lang.org/main/python-api/generated/triton.language.dot.html |
| R3-08 | CUTLASS `ElementAccumulator` template parameter | Accumulator-init dtype in `acc = tl.zeros((BM, BN), dtype=tl.float32)` | Both choose accumulator precision separately from input precision. FP32 accum is the safe default for FP16/BF16/FP8 inputs over large K. | topic-cutlass.md §Common Pitfalls ; topic-matmul-patterns.md §Common Pitfalls (Accumulator dtype mismatch) |

## 4. Scheduling & Tiling

| RID | CUDA / CUTLASS / cuTile concept | Triton equivalent | Notes | Source |
|-----|----------------------------------|-------------------|-------|--------|
| R4-01 | CUTLASS persistent kernel scheduler | Triton `while pid < num_tiles` persistent pattern | Both amortize kernel-launch overhead by letting one CTA process multiple tiles in a loop. Grid is sized to SM count, not tile count. | topic-cutlass.md §Core Concepts (Expert, persistent kernels) ; topic-matmul-patterns.md §Core Concepts (Advanced) |
| R4-02 | CUTLASS `ThreadblockSwizzle` (e.g., `GemmIdentityThreadblockSwizzle<8>`) | Triton pid swizzling with `GROUP_SIZE_M` (group rows of `GROUP_SIZE_M` × `num_pid_n` blocks) | Both reorder the CTA dispatch order to maximize L2 reuse across a wave. | docs.nvidia.com/cutlass/media/docs/cpp/efficient_gemm.md ; topic-matmul-patterns.md §Common Pitfalls (No pid swizzling) |
| R4-03 | CUTLASS `GemmSplitKParallel` (split-K kernel) | Triton split-K kernel + `tl.atomic_add` to output + `reset_to_zero=["c_ptr"]` autotune option | Both split the K dimension across CTAs and reduce partial sums into the output. Triton requires `reset_to_zero` so subsequent autotune calls don't accumulate stale data. | topic-cutlass.md §Practice Questions (SplitK) ; topic-matmul-patterns.md §Common Pitfalls (Split-K without reset_to_zero) |
| R4-04 | CUTLASS stream-K scheduler (Osama et al., 2023) | Triton stream-K pattern (block claims K-chunks from a global counter) | Both fix the "wave quantization" tail by load-balancing K splits across SMs. | arxiv.org/abs/2301.03598 ; topic-matmul-patterns.md §Core Concepts (Advanced) |
| R4-05 | CUTLASS `Stages` template parameter (mainloop pipeline depth) | Triton `num_stages` autotune knob | Both control how many in-flight async loads are interleaved with MMAs in the mainloop. | topic-cutlass.md §Common Pitfalls (WGMMA pipeline stall) ; topic-tiling-autotuning.md §Core Concepts |
| R4-06 | CUTLASS `ThreadblockShape::kWarpCount` (warps per CTA) | Triton `num_warps` autotune knob | Both fix the number of warps cooperating on one tile. Triton typical values: 4, 8; CUTLASS warp counts derive from `ThreadblockShape / WarpShape`. | topic-cutlass.md §Core Concepts ; topic-tiling-autotuning.md §Core Concepts |
| R4-07 | CUTLASS Hopper warp-specialized mainloop (producer/consumer warps via `cluster_launch_control`) | Triton `num_warps=8` producer/consumer split (e.g., persistent matmul on Hopper) | Both split warps into producers (issue TMA loads) and consumers (run WGMMA). | topic-cutlass.md §Core Concepts (Expert) ; topic-matmul-patterns.md §Core Concepts (Expert) |
| R4-08 | CUTLASS `dim3 grid` for `kernel_launch<<<grid, block>>>` | Triton `kernel[grid]` callable with a `grid` tuple or lambda | Same concept (grid of CTAs); Triton's grid can be a callable receiving the meta-parameters. | docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#kernels ; topic-triton-basics.md §Core Concepts |

## 5. Python Tile DSLs (cuTile ↔ Triton)

| RID | CUDA / CUTLASS / cuTile concept | Triton equivalent | Notes | Source |
|-----|----------------------------------|-------------------|-------|--------|
| R5-01 | cuTile / CuTe-DSL: Python-first tile DSL, NVIDIA-only | Triton: Python-first tile DSL, multi-backend (NVIDIA + AMD + Intel) | Both occupy the same mental slot — Python decorator on a kernel function operating on tiles. cuTile is NVIDIA-only; Triton's multi-backend reach is one of its main differentiators. | topic-cutile.md §Core Concepts ; topic-compiler-internals.md §Backends |
| R5-02 | cuTile / CuTe-DSL `@cute.jit` decorator | Triton `@triton.jit` decorator | Both compile the decorated Python function to a GPU kernel at first call. | docs.nvidia.com/cutlass/media/docs/pythonDSL/overview.html ; triton-lang.org/main/python-api/generated/triton.jit.html |
| R5-03 | CuTe-DSL `cute.make_layout(shape, stride)` (Python form) | `tl.make_block_ptr(base, shape, strides, offsets, block_shape, order)` | Both construct a tile descriptor in Python. CuTe's `make_layout` is more general (supports nested shapes / strides for hierarchical tiling). | docs.nvidia.com/cutlass/media/docs/pythonDSL/overview.html ; triton-lang.org/main/python-api/generated/triton.language.make_block_ptr.html |
| R5-04 | CuTe-DSL `cute.mma_atom(...)` (Python tile-level MMA call) | `tl.dot(a, b, acc)` | Both invoke the underlying MMA atom from Python. | topic-cutile.md §Core Concepts ; topic-matmul-patterns.md §Core Concepts |
| R5-05 | cuTile / CuTe-DSL DLPack interop (PyTorch ↔ CuTe via DLPack `to_dlpack`/`from_dlpack`) | Direct `torch.Tensor` argument to a Triton kernel (auto-extracts data_ptr/strides) | Both interop with PyTorch tensors. Triton is more ergonomic (no DLPack dance); cuTile requires explicit DLPack conversion. | topic-cutile.md §Common Pitfalls ; topic-triton-basics.md §Core Concepts |
| R5-06 | cuTile / CuTe-DSL backend: NVIDIA only (compiles via MLIR → ptxas) | Triton backend: NVIDIA + AMD + Intel (compiles via MLIR → PTX/AMDGCN/SPIR-V) | The fundamental portability differentiator. | topic-cutile.md §Core Concepts ; topic-compiler-internals.md §Backends |

## 6. Compiler & Profiling

| RID | CUDA / CUTLASS / cuTile concept | Triton equivalent | Notes | Source |
|-----|----------------------------------|-------------------|-------|--------|
| R6-01 | IR pipeline: `.cu` → PTX → SASS (via `nvcc` + `ptxas`) | IR pipeline: Python → TTIR → TTGIR → LLIR → PTX (NVIDIA) / AMDGCN (AMD) | Both pipelines go through multiple lowering stages. Triton's TTIR/TTGIR are GPU-specific MLIR dialects. | topic-cuda-kernels.md §Core Concepts ; topic-compiler-internals.md §Core Concepts |
| R6-02 | CUTLASS / C++: frontend is C++ templates (no separate frontend dialect) | Triton frontend dialect: TTIR (GPU-agnostic) | Triton has an explicit frontend dialect; CUTLASS uses C++ templates as the "frontend". | topic-cutlass.md §Core Concepts ; topic-compiler-internals.md §Core Concepts |
| R6-03 | PTX (NVIDIA virtual ISA) carries thread/warp/cta abstractions | TTGIR carries layout encodings (`#blocked`, `#mma`, `#shared`, `#dot_op`) | Both are GPU-aware IRs but at different abstraction levels — PTX is per-thread; TTGIR is per-tile-with-layout. | docs.nvidia.com/cuda/parallel-thread-execution/index.html ; topic-compiler-internals.md §Layout encodings |
| R6-04 | dump tools: `cuobjdump`, `nvdisasm`, `ptxas -v` | dump tools: `TRITON_KERNEL_DUMP=1`, `triton-opt`, `triton-translate` | Both inspect compiled artifacts. Triton dumps each IR stage to disk when the env var is set. | docs.nvidia.com/cuda/cuda-binary-utilities/index.html ; topic-compiler-internals.md §Tooling |
| R6-05 | Profiler: Nsight Compute (kernel-level), Nsight Systems (system-level) | Profiler: `proton` (Triton's first-party profiler) | Both give per-kernel timing + hardware counters. Nsight Compute is more detailed; `proton` is Triton-native and lower-overhead. | docs.nvidia.com/nsight-compute/ ; topic-ecosystem-production.md §Core Concepts |
| R6-06 | Debug: `cuda-gdb`, `compute-sanitizer` (race / memcheck / synccheck) | Debug: `TRITON_INTERPRET=1` (Python interpreter mode), `tl.device_print(...)` | Triton's interpreter mode runs the kernel on CPU as plain Python — the easiest way to debug logic errors. | topic-cuda-kernels.md §Common Pitfalls ; topic-ecosystem-production.md §Common Pitfalls |
| R6-07 | Autotune surface: CUTLASS profiler + instance-library generator (offline) | Autotune surface: `@triton.autotune` decorator + `triton.Config` list (online JIT autotuning) | CUTLASS does its autotuning offline at instance-library build time; Triton autotunes online at first call, then caches per `key=[...]`. | topic-cutlass.md §Hands-On Milestones (M1, M7) ; topic-tiling-autotuning.md §Core Concepts |
| R6-08 | Compile cache: `nvcc` object file + ptxas SASS cache | Compile cache: Triton JIT cache (`TRITON_CACHE_DIR`, default `~/.triton/cache/`) | Both avoid recompilation on identical inputs. Triton's cache key includes the function source hash + tuning meta-parameters. | docs.nvidia.com/cuda/cuda-compiler-driver-nvcc/index.html ; topic-ecosystem-production.md §Core Concepts |

---

## 7. Cross-Stack Question Seeds

Each seed is a YAML-fenced block. The linter parses every block and enforces:

- ≥36 total seeds
- ≥18 `cuda-to-triton` and ≥18 `triton-to-cuda`
- ≥6 each from `mapping-section` 2/3/4/6, ≥4 from section 5
- ≥6 each of `question-type` `recall` / `conceptual` / `distinction` / `behavioral` / `debugging`
- 100 % have a non-empty `source:` and a `rid:` that resolves to an existing canonical row

Seeds:

```yaml
id: Q01
rid: R2-03
direction: cuda-to-triton
mapping-section: 2
question-type: distinction
primary-topic: cutlass
source: R2-03 ; docs.nvidia.com/cutlass/media/docs/cpp/cute/02_layout_algebra.html
stem: "What is the closest Triton equivalent of `cute::Swizzle<3,3,3>`?"
options:
  - "#shared layout encoding (TTGIR)"
  - "#blocked layout encoding (TTGIR)"
  - "#mma layout encoding (TTGIR)"
  - "#dot_op layout encoding (TTGIR)"
correct: 0
```

```yaml
id: Q02
rid: R3-02
direction: triton-to-cuda
mapping-section: 3
question-type: behavioral
primary-topic: matmul-patterns
source: R3-02 ; topic-matmul-patterns.md §Common Pitfalls
stem: "On H100, which PTX instruction does `tl.dot(a_fp16, b_fp16, acc_fp32)` lower to when M%64==0, K%16==0?"
options:
  - "wgmma.mma_async.sync.aligned"
  - "mma.sync.aligned.m16n8k16"
  - "cp.async.bulk.tensor"
  - "ldmatrix.sync.aligned"
correct: 0
```

```yaml
id: Q03
rid: R4-05
direction: cuda-to-triton
mapping-section: 4
question-type: distinction
primary-topic: cutlass
source: R4-05 ; topic-tiling-autotuning.md §Core Concepts
stem: "Which Triton autotune knob corresponds to CUTLASS's `Stages` template parameter for mainloop pipelining?"
options:
  - "num_stages"
  - "num_warps"
  - "GROUP_SIZE_M"
  - "BLOCK_SIZE_K"
correct: 0
```

```yaml
id: Q04
rid: R5-06
direction: cuda-to-triton
mapping-section: 5
question-type: recall
primary-topic: cutile
source: R5-06 ; topic-cutile.md §Core Concepts
stem: "cuTile / CuTe-DSL and Triton are both Python-first tile DSLs. Which is multi-backend (NVIDIA + AMD + Intel)?"
options:
  - "Triton"
  - "cuTile / CuTe-DSL"
  - "Both, since they share the same backend"
  - "Neither, both compile via ptxas only"
correct: 0
```

```yaml
id: Q05
rid: R4-01
direction: cuda-to-triton
mapping-section: 4
question-type: conceptual
primary-topic: cutlass
source: R4-01 ; topic-matmul-patterns.md §Core Concepts
stem: "A CUTLASS persistent matmul kernel reduces launch overhead by reusing CTAs across many output tiles. What is the equivalent Triton idiom?"
options:
  - "while pid < num_tiles: ... loop inside the kernel, grid sized to SM count"
  - "grid = (num_tiles,), recompiled per launch"
  - "torch.compile() the matmul to fuse adjacent calls"
  - "TRITON_INTERPRET=1 to skip launch overhead"
correct: 0
```

```yaml
id: Q06
rid: R2-03
direction: triton-to-cuda
mapping-section: 2
question-type: recall
primary-topic: compiler-internals
source: R2-03 ; topic-compiler-internals.md §Layout encodings
stem: "A TTGIR dump shows a tensor with `#shared` encoding and a swizzle attribute. What CUTLASS / CuTe construct is the closest analogue?"
options:
  - "cute::Swizzle<B, M, S>"
  - "cute::Layout shape:stride"
  - "cutlass::layout::RowMajor"
  - "cutlass::epilogue::EpilogueOp"
correct: 0
```

```yaml
id: Q07
rid: R2-06
direction: triton-to-cuda
mapping-section: 2
question-type: behavioral
primary-topic: matmul-patterns
source: R2-06 ; topic-cuda-kernels.md §Core Concepts (Expert)
stem: "A Triton matmul kernel on H100 uses `tl.make_block_ptr` for both A and B. Inspecting the TTGIR, you see TMA descriptor ops. What CUDA-side mechanism is the compiler emitting?"
options:
  - "cp.async.bulk.tensor (TMA)"
  - "cp.async (Ampere per-thread async copy)"
  - "ldmatrix.sync (per-warp shared-mem load)"
  - "Standard global load via ld.global"
correct: 0
```

```yaml
id: Q08
rid: R4-03
direction: triton-to-cuda
mapping-section: 4
question-type: distinction
primary-topic: matmul-patterns
source: R4-03 ; topic-cutlass.md §Practice Questions
stem: "A Triton split-K matmul uses `tl.atomic_add` to the output and the autotune decorator has `reset_to_zero=[\"c_ptr\"]`. Which CUTLASS kernel template is the closest analogue?"
options:
  - "cutlass::gemm::device::GemmSplitKParallel"
  - "cutlass::gemm::device::Gemm (single-kernel)"
  - "cutlass::gemm::device::GemmUniversal (no split)"
  - "cutlass::conv::device::ImplicitGemm"
correct: 0
```

```yaml
id: Q09
rid: R3-01
direction: cuda-to-triton
mapping-section: 3
question-type: conceptual
primary-topic: cutlass
source: R3-01 ; topic-matmul-patterns.md §Core Concepts
stem: "CUTLASS exposes MMA atoms (e.g., `cutlass::arch::Mma_Atom<...>`) explicitly in the type system. What is the closest Triton equivalent, and how is the atom selected?"
options:
  - "tl.dot(a, b, acc) — the compiler picks the atom from operand dtype + shape + target arch"
  - "@triton.jit decorator — the atom is fixed at decoration time"
  - "triton.Config(num_warps=...) — the atom is selected by warp count"
  - "tl.load(...) — the atom is encoded in the pointer"
correct: 0
```

```yaml
id: Q10
rid: R3-05
direction: cuda-to-triton
mapping-section: 3
question-type: behavioral
primary-topic: cutlass
source: R3-05 ; topic-matmul-patterns.md §Common Pitfalls
stem: "You're porting a CUTLASS FP8 (E4M3) GEMM with per-tensor scales to Triton on Hopper. Which `tl.dot` invocation matches?"
options:
  - "tl.dot(a_fp8, b_fp8, acc_fp32, input_precision=\"ieee\") with scale tensors applied in the epilogue"
  - "tl.dot(a_fp8, b_fp8) — scales are auto-detected by the compiler"
  - "tl.dot(a_fp8, b_fp8, acc_fp16) — FP16 accumulator is required for FP8"
  - "tl.dot is not supported for FP8; you must drop to PTX"
correct: 0
```

```yaml
id: Q11
rid: R4-02
direction: cuda-to-triton
mapping-section: 4
question-type: conceptual
primary-topic: cutlass
source: R4-02 ; topic-matmul-patterns.md §Common Pitfalls
stem: "CUTLASS uses `ThreadblockSwizzle` (e.g., `GemmIdentityThreadblockSwizzle<8>`) to reorder CTA dispatch for L2 reuse. What is the Triton equivalent, and what parameter controls it?"
options:
  - "pid swizzling using `GROUP_SIZE_M` autotune parameter"
  - "num_stages autotune parameter — more stages improve L2 reuse"
  - "num_warps autotune parameter — more warps improve L2 reuse"
  - "Triton's compiler does this automatically; no parameter is needed"
correct: 0
```

```yaml
id: Q12
rid: R6-01
direction: triton-to-cuda
mapping-section: 6
question-type: recall
primary-topic: compiler-internals
source: R6-01 ; topic-compiler-internals.md §Core Concepts
stem: "Triton's lowering pipeline is Python → TTIR → TTGIR → LLIR → PTX. Which CUDA-side pipeline is the closest analogue (excluding CUTLASS templates)?"
options:
  - ".cu → PTX → SASS (via nvcc + ptxas)"
  - ".cu → SASS directly (no PTX)"
  - "C++ → LLVM IR → PTX (without nvcc)"
  - "Python → Cython → PTX"
correct: 0
```

```yaml
id: Q13
rid: R4-06
direction: cuda-to-triton
mapping-section: 4
question-type: distinction
primary-topic: cutlass
source: R4-06 ; topic-tiling-autotuning.md §Core Concepts
stem: "CUTLASS's `ThreadblockShape::kWarpCount` derives from `ThreadblockShape / WarpShape`. Which Triton autotune knob plays the same role?"
options:
  - "num_warps"
  - "num_stages"
  - "GROUP_SIZE_M"
  - "BLOCK_SIZE_K"
correct: 0
```

```yaml
id: Q14
rid: R5-02
direction: cuda-to-triton
mapping-section: 5
question-type: recall
primary-topic: cutile
source: R5-02 ; topic-cutile.md §Core Concepts
stem: "Which decorator in CuTe-DSL plays the same role as Triton's `@triton.jit`?"
options:
  - "@cute.jit"
  - "@cuda.jit"
  - "@cutlass.jit"
  - "@nvidia.jit"
correct: 0
```

```yaml
id: Q15
rid: R6-05
direction: triton-to-cuda
mapping-section: 6
question-type: distinction
primary-topic: ecosystem-production
source: R6-05 ; topic-ecosystem-production.md §Core Concepts
stem: "Triton's first-party kernel profiler `proton` plays the same role as which NVIDIA tool?"
options:
  - "Nsight Compute"
  - "cuda-gdb"
  - "compute-sanitizer"
  - "nvcc --resource-usage"
correct: 0
```

```yaml
id: Q16
rid: R6-06
direction: triton-to-cuda
mapping-section: 6
question-type: debugging
primary-topic: ecosystem-production
source: R6-06 ; topic-ecosystem-production.md §Common Pitfalls
stem: "A Triton kernel produces wrong results and you want to step through it on CPU. Which env var is the analogue of running CUDA in `cuda-gdb`?"
options:
  - "TRITON_INTERPRET=1"
  - "TRITON_KERNEL_DUMP=1"
  - "TRITON_CACHE_DIR=/tmp"
  - "TRITON_DEBUG=1"
correct: 0
```

```yaml
id: Q17
rid: R2-07
direction: cuda-to-triton
mapping-section: 2
question-type: behavioral
primary-topic: cuda-kernels
source: R2-07 ; topic-tiling-autotuning.md §Core Concepts
stem: "An Ampere CUDA kernel uses `cp.async.commit_group` + `cp.async.wait_group` to overlap global → shared loads with compute. What Triton mechanism produces the equivalent pipelined load pattern?"
options:
  - "An autotune config with num_stages > 1"
  - "An autotune config with num_warps > 4"
  - "tl.make_block_ptr (it implies pipelining)"
  - "@triton.heuristics (it inserts pipeline barriers)"
correct: 0
```

```yaml
id: Q18
rid: R2-08
direction: triton-to-cuda
mapping-section: 2
question-type: conceptual
primary-topic: compiler-internals
source: R2-08 ; topic-cuda-kernels.md §Common Pitfalls
stem: "A Triton matmul with num_stages=3 on H100 emits TMA loads. The user asks: 'where's the mbarrier?' Why don't they see it in their kernel source?"
options:
  - "Triton's pipeliner pass emits the mbarrier implicitly between stages"
  - "Hopper TMA does not require an mbarrier — only Ampere cp.async does"
  - "mbarriers are only needed when num_warps == 1"
  - "The mbarrier is a CUTLASS-only construct"
correct: 0
```

```yaml
id: Q19
rid: R3-08
direction: cuda-to-triton
mapping-section: 3
question-type: debugging
primary-topic: matmul-patterns
source: R3-08 ; topic-matmul-patterns.md §Common Pitfalls
stem: "A CUTLASS GEMM uses `ElementAccumulator=float` even though inputs are FP16, and gets full accuracy. A learner ports it to Triton with `acc = tl.zeros((BM, BN), dtype=tl.float16)` and sees large errors on K=8192. What's the fix?"
options:
  - "Change to `tl.zeros((BM, BN), dtype=tl.float32)` — match the FP32 accumulator"
  - "Increase num_stages so loads pipeline better"
  - "Use input_precision=\"tf32\" — that's the FP16-accum mode"
  - "Switch to tl.bfloat16 — BF16 has better range"
correct: 0
```

```yaml
id: Q20
rid: R2-01
direction: triton-to-cuda
mapping-section: 2
question-type: distinction
primary-topic: triton-basics
source: R2-01 ; topic-cutlass.md §Core Concepts (Advanced)
stem: "Triton's `tl.make_block_ptr(base, shape, strides, offsets, block_shape, order)` constructs a tile descriptor. What is the closest CuTe construct, and what is the main expressiveness difference?"
options:
  - "cute::Layout + cute::Stride — CuTe supports nested shapes for hierarchical tiling; make_block_ptr is rectangular only"
  - "cute::Tensor — they are exactly equivalent"
  - "cute::Swizzle — both describe smem layouts"
  - "cute::Copy_Atom — both describe copy patterns"
correct: 0
```

```yaml
id: Q21
rid: R6-07
direction: triton-to-cuda
mapping-section: 6
question-type: conceptual
primary-topic: tiling-autotuning
source: R6-07 ; topic-cutlass.md §Hands-On Milestones
stem: "Triton's `@triton.autotune` searches configs online at the first call and caches by `key=[...]`. CUTLASS does autotuning differently. What's the main timing difference?"
options:
  - "CUTLASS autotunes offline at instance-library build time; Triton autotunes online at first call"
  - "CUTLASS autotunes per launch; Triton autotunes per kernel"
  - "CUTLASS autotunes at compile time of the user's source file; Triton autotunes at PyTorch init"
  - "Both autotune online at the first launch — they are equivalent"
correct: 0
```

```yaml
id: Q22
rid: R4-04
direction: cuda-to-triton
mapping-section: 4
question-type: behavioral
primary-topic: matmul-patterns
source: R4-04 ; topic-matmul-patterns.md §Core Concepts (Advanced)
stem: "CUTLASS stream-K (Osama et al.) load-balances by having each CTA claim K-chunks from a global counter. A learner wants the same in Triton. What is the idiom?"
options:
  - "atomic-add fetch of a global counter inside the kernel, claim K-chunks dynamically"
  - "An autotune config with num_stages=K"
  - "Persistent kernel with a while loop on pid only"
  - "Set GROUP_SIZE_M = K to swizzle"
correct: 0
```

```yaml
id: Q23
rid: R2-10
direction: triton-to-cuda
mapping-section: 2
question-type: distinction
primary-topic: triton-basics
source: R2-10 ; topic-cutlass.md §Core Concepts (Intermediate)
stem: "Triton handles the ragged tail with `tl.load(..., mask=offs < N, other=0.0)`. What is the CUTLASS analogue inside an epilogue?"
options:
  - "PredicatedTileIterator (epilogue boundary predicates)"
  - "cute::Swizzle (smem layout)"
  - "cutlass::layout::ColumnMajor (layout tag)"
  - "ThreadblockSwizzle (CTA dispatch order)"
correct: 0
```

```yaml
id: Q24
rid: R5-05
direction: cuda-to-triton
mapping-section: 5
question-type: distinction
primary-topic: cutile
source: R5-05 ; topic-cutile.md §Common Pitfalls
stem: "CuTe-DSL hands a PyTorch tensor to a CuTe kernel via DLPack. Triton's interop is more direct. Which Triton mechanism replaces the DLPack dance?"
options:
  - "Pass the torch.Tensor directly — Triton extracts data_ptr/strides automatically"
  - "Call tl.from_dlpack() inside the kernel"
  - "Use TRITON_INTERPRET=1 to materialize the tensor"
  - "Wrap the tensor in tl.constexpr()"
correct: 0
```

```yaml
id: Q25
rid: R3-03
direction: triton-to-cuda
mapping-section: 3
question-type: recall
primary-topic: compiler-internals
source: R3-03 ; topic-compiler-internals.md §Backends
stem: "On `sm_80` (A100), `tl.dot(a_fp16, b_fp16, acc_fp32)` in Triton lowers to which PTX MMA instruction family?"
options:
  - "mma.sync.aligned.m16n8k16 (Ampere per-warp MMA)"
  - "wgmma.mma_async (Hopper warp-group MMA)"
  - "mfma_f32_16x16x16f16 (AMD CDNA MFMA)"
  - "wmma.mma.sync (Volta WMMA, since dropped)"
correct: 0
```

```yaml
id: Q26
rid: R6-08
direction: cuda-to-triton
mapping-section: 6
question-type: distinction
primary-topic: ecosystem-production
source: R6-08 ; topic-ecosystem-production.md §Core Concepts
stem: "CUDA caches compiled objects via nvcc + ptxas. Where does Triton cache compiled kernels by default?"
options:
  - "~/.triton/cache/ (override with TRITON_CACHE_DIR)"
  - "~/.cuda/cache/"
  - "/tmp/triton-jit/"
  - "Triton does not cache — it recompiles every call"
correct: 0
```

```yaml
id: Q27
rid: R3-06
direction: cuda-to-triton
mapping-section: 3
question-type: behavioral
primary-topic: cutlass
source: R3-06 ; topic-matmul-patterns.md §Common Pitfalls
stem: "A CUTLASS GEMM with α=1, β=0 fuses the epilogue's MAC step. What is the canonical Triton idiom that produces a fused MMA operation?"
options:
  - "acc = tl.dot(a, b, acc) — 3-arg form fuses into a single MMA op"
  - "acc += tl.dot(a, b) — 2-arg + separate add"
  - "tl.dot(a, b, acc, fuse=True) — explicit fuse flag"
  - "@triton.heuristics(fuse_mac=True) — heuristic flag"
correct: 0
```

```yaml
id: Q28
rid: R4-07
direction: cuda-to-triton
mapping-section: 4
question-type: conceptual
primary-topic: cutlass
source: R4-07 ; topic-matmul-patterns.md §Core Concepts (Expert)
stem: "CUTLASS Hopper warp-specialized mainloop splits warps into producers (issue TMA loads) and consumers (run WGMMA). What Triton autotune configuration plays the same role?"
options:
  - "num_warps=8 in a persistent matmul kernel on Hopper"
  - "num_stages=8"
  - "GROUP_SIZE_M=8"
  - "BLOCK_SIZE_M=128"
correct: 0
```

```yaml
id: Q29
rid: R6-04
direction: triton-to-cuda
mapping-section: 6
question-type: distinction
primary-topic: compiler-internals
source: R6-04 ; topic-compiler-internals.md §Tooling
stem: "Triton dumps each IR stage to disk when `TRITON_KERNEL_DUMP=1` is set. Which CUDA tool family plays the analogous inspection role for compiled CUDA artifacts?"
options:
  - "cuobjdump / nvdisasm / ptxas -v"
  - "cuda-gdb / compute-sanitizer"
  - "Nsight Compute"
  - "nvcc --keep"
correct: 0
```

```yaml
id: Q30
rid: R2-04
direction: triton-to-cuda
mapping-section: 2
question-type: recall
primary-topic: compiler-internals
source: R2-04 ; topic-compiler-internals.md §Layout encodings
stem: "A TTGIR tensor has `#blocked<{sizePerThread = [1, 8], threadsPerWarp = [8, 4], warpsPerCTA = [4, 1], order = [1, 0]}>`. What CUDA-side construct describes the same per-thread fragment idea?"
options:
  - "CuTe register-resident Layout (per-thread fragment)"
  - "PTX mma.sync operand layout"
  - "cutlass::layout::RowMajor"
  - "CUDA shared memory bank layout"
correct: 0
```

```yaml
id: Q31
rid: R3-07
direction: triton-to-cuda
mapping-section: 3
question-type: behavioral
primary-topic: matmul-patterns
source: R3-07 ; topic-cutlass.md §Core Concepts
stem: "A Triton matmul uses `tl.dot(a, b, acc, input_precision=\"tf32\")` on A100. Which CUTLASS template parameter is the equivalent control?"
options:
  - "Element type `cutlass::tfloat32_t` for the accumulator inputs (TF32 MMA path)"
  - "ElementAccumulator=float — TF32 is implied"
  - "Stages=3 — TF32 requires 3-stage pipeline"
  - "ThreadblockShape::kM=64 — TF32 needs M=64"
correct: 0
```

```yaml
id: Q32
rid: R5-04
direction: triton-to-cuda
mapping-section: 5
question-type: recall
primary-topic: matmul-patterns
source: R5-04 ; topic-cutile.md §Core Concepts
stem: "In CuTe-DSL, the Python-level tile MMA call is `cute.mma_atom(...)`. What is the Triton equivalent?"
options:
  - "tl.dot(a, b, acc)"
  - "tl.matmul(a, b)"
  - "@triton.mma decorator"
  - "tl.gemm(a, b, c, alpha, beta)"
correct: 0
```

```yaml
id: Q33
rid: R2-12
direction: cuda-to-triton
mapping-section: 2
question-type: conceptual
primary-topic: cutlass
source: R2-12 ; topic-compiler-internals.md §Compiler passes
stem: "CUTLASS picks a shared-memory swizzle template (e.g., `cute::Swizzle<3,3,3>`) to avoid bank conflicts. Triton picks one automatically. At which stage of Triton's pipeline?"
options:
  - "Triton's swizzling pass between TTIR and TTGIR"
  - "At Python-decoration time (@triton.jit)"
  - "At runtime, by the autotuner"
  - "At PyTorch torch.compile() time"
correct: 0
```

```yaml
id: Q34
rid: R4-08
direction: triton-to-cuda
mapping-section: 4
question-type: distinction
primary-topic: triton-basics
source: R4-08 ; topic-triton-basics.md §Core Concepts
stem: "A Triton kernel is launched with `kernel[(M_blocks, N_blocks)](...)`. What is the CUDA-side analogue, and what's the main difference?"
options:
  - "<<<dim3(M_blocks, N_blocks), dim3(...)>>> — CUDA also passes a block dim; Triton fixes block dim via num_warps"
  - "<<<dim3(M_blocks, N_blocks), 1>>> — identical, no difference"
  - "cuLaunchKernel(kernel, M_blocks, N_blocks) — no block dim in CUDA driver API"
  - "Triton has no equivalent — kernel launches go through PyTorch"
correct: 0
```

```yaml
id: Q35
rid: R6-02
direction: cuda-to-triton
mapping-section: 6
question-type: distinction
primary-topic: cutlass
source: R6-02 ; topic-compiler-internals.md §Core Concepts
stem: "CUTLASS uses C++ templates as its compile-time DSL. Triton has an explicit frontend dialect. What is it called?"
options:
  - "TTIR (Triton IR)"
  - "TTGIR (Triton GPU IR)"
  - "LLIR (LLVM IR)"
  - "PTX"
correct: 0
```

```yaml
id: Q36
rid: R2-05
direction: triton-to-cuda
mapping-section: 2
question-type: debugging
primary-topic: compiler-internals
source: R2-05 ; topic-cutlass.md §Common Pitfalls (Swizzle mismatch)
stem: "A TTGIR dump shows a `convert_layout` op between `#blocked` and `#dot_op`. A CUTLASS engineer asks: 'what's the equivalent step in our codebase?' Best answer?"
options:
  - "The pre-arrangement of operands into the MMA-required fragment layout before issuing mma.sync / wgmma"
  - "The cutlass::layout::RowMajor tag on the output tensor"
  - "The cute::Swizzle of the shared-memory output tile"
  - "The CUTLASS profiler's instance-library selection"
correct: 0
```

```yaml
id: Q37
rid: R4-03
direction: cuda-to-triton
mapping-section: 4
question-type: debugging
primary-topic: matmul-patterns
source: R4-03 ; topic-matmul-patterns.md §Common Pitfalls (Split-K without reset_to_zero)
stem: "A user ports a CUTLASS GemmSplitKParallel kernel to Triton split-K. The first launch is correct; the second launch returns wrong results. What is the most likely cause?"
options:
  - "Missing `reset_to_zero=[\"c_ptr\"]` in the @triton.autotune decorator — `tl.atomic_add` accumulates onto stale output data"
  - "BLOCK_SIZE_K is too small — split-K needs K to be a multiple of the launch count"
  - "num_warps is too low — split-K requires num_warps=8"
  - "Triton split-K does not support multiple launches; you must recompile"
correct: 0
```

```yaml
id: Q38
rid: R2-08
direction: cuda-to-triton
mapping-section: 2
question-type: debugging
primary-topic: cuda-kernels
source: R2-08 ; topic-cuda-kernels.md §Common Pitfalls (Async copy without barrier)
stem: "A CUTLASS engineer dumps Triton's TTGIR for a Hopper matmul with num_stages=3 and sees TMA loads but no explicit mbarrier ops in the user's kernel source. They suspect a race. What's the correct diagnosis?"
options:
  - "No race — Triton's pipeliner pass emits the mbarrier implicitly between stages; check the post-pipelining TTGIR, not the user source"
  - "Confirmed race — Triton does not emit mbarriers; the user must add them manually"
  - "No race — Hopper TMA does not require mbarriers, unlike Ampere cp.async"
  - "Confirmed race — num_stages=3 is too high for TMA; reduce to 1"
correct: 0
```

```yaml
id: Q39
rid: R6-06
direction: cuda-to-triton
mapping-section: 6
question-type: debugging
primary-topic: ecosystem-production
source: R6-06 ; topic-ecosystem-production.md §Common Pitfalls
stem: "A learner suspects their Triton kernel has a per-thread indexing bug. They want the simplest CPU-side reproduction (analogous to running CUDA under cuda-gdb without a GPU). Which env var?"
options:
  - "TRITON_INTERPRET=1 — runs the kernel in pure Python on CPU, slow but exact for logic bugs"
  - "TRITON_KERNEL_DUMP=1 — emits all IR stages but still runs on GPU"
  - "CUDA_VISIBLE_DEVICES= — disables the GPU but Triton then errors out"
  - "TRITON_CACHE_DIR=/tmp — clears the compile cache"
correct: 0
```
