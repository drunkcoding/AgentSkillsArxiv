# Codebase Mode — Triton Onboarding Vault Workflow

> Generate a StudyVault that helps a new developer understand a Triton kernel library / Inductor backend / Triton compiler fork.
> All scanning and output MUST stay within CWD.

## Phase C1: Project Exploration

1. **Scan project structure**: Glob source files (`*.py`, `*.cpp`, `*.h`, `*.td`, `*.mlir`, `CMakeLists.txt`, `setup.py`, `pyproject.toml`, `requirements.txt`). Build a file tree.
2. **Detect tech stack and Triton features used**:
   - Triton version: parse `setup.py` / `pyproject.toml` / `requirements*.txt` for `triton==` or `triton>=`. Also check `__init__.py` for `triton.__version__` references.
   - Target backends: scan `third_party/` for `nvidia/`, `amd/`, `intel/`. Scan kernel files for backend-specific paths.
   - External libs: scan `import` for `torch`, `triton`, `cuda`, `cupy`, `flash_attn`, `xformers`, `fbgemm`, `proton`.
   - PyTorch / Inductor integration: detect `torch._inductor`, `torch.compile`, `@torch.library.custom_op`.
   - For Triton-compiler forks: detect `lib/Dialect/Triton`, `lib/Conversion`, `python/triton/_C/libtriton.so` build artifacts.
3. **Identify role**:
   - Kernel library (flash-attn Triton, xformers, Liger-Kernel, unsloth) → focus on per-kernel notes + autotune configs + tile shapes.
   - Inductor backend / codegen → focus on PyTorch fx-graph → Triton lowering rules.
   - Triton compiler fork → focus on IR passes, layout conversion, target lowerings.
   - Application / training code → focus on Python entry points + which Triton kernels are called.
4. **Read key files**: `README.md`, `CONTRIBUTING.md`, entry points (top-level `__init__.py`, main Python script), build config.
5. **Present findings** to user for confirmation before proceeding.

## Phase C2: Architecture Analysis

1. **Identify patterns**:
   - Python wrapper → `@triton.jit` kernel dispatch (single-stream, persistent, fused).
   - Tile structure (BLOCK_SIZE_M/N/K, GROUP_SIZE_M, num_warps, num_stages).
   - `tl.dot` usage (FP16/BF16/FP8 operand dtypes, FP32 accumulator).
   - Autotune surface (number of configs, cache key, pruning hooks).
   - Memory access pattern (raw pointer vs `tl.make_block_ptr` + `tl.advance`).
2. **Trace one representative kernel end-to-end**: pick a high-traffic kernel (e.g., the main matmul or FlashAttention kernel) and document:
   - Python wrapper signature and how it computes the grid.
   - Autotune config space + cache key.
   - `@triton.jit` kernel signature including `tl.constexpr` parameters.
   - Tile shape and accumulator dtype.
   - Memory access pattern (pointer arithmetic vs `tl.make_block_ptr`).
   - Reduction / synchronization pattern (atomics, second-stage kernel).
   - Exit (epilogue, output store with mask).
3. **Map dependencies**: which Python modules call which Triton kernels; which kernels share helper `@triton.jit` functions.
4. **Document data flow**: input tensors → Python wrapper → autotune → JIT compile → `@triton.jit` kernel → output.
5. **Build architecture summary**: ASCII diagram + description.

## Phase C3: Tag Standard

Define vocabulary before creating notes (English, lowercase, kebab-case):

| Category | Examples |
|----------|----------|
| Backend | `#backend-nvidia`, `#backend-amd`, `#backend-intel` |
| Architecture | `#arch-ampere`, `#arch-hopper`, `#arch-blackwell`, `#arch-cdna3` |
| SM target | `#sm-80`, `#sm-90`, `#sm-100` |
| Kernel role | `#kernel-matmul`, `#kernel-attention`, `#kernel-rmsnorm`, `#kernel-rope`, `#kernel-quant` |
| API surface | `#api-python-wrapper`, `#api-triton-jit`, `#api-pytorch-custom-op` |
| Triton mechanism | `#tl-dot`, `#tl-make-block-ptr`, `#triton-autotune`, `#triton-heuristics`, `#tl-associative-scan` |
| Pattern | `#pattern-persistent-kernel`, `#pattern-split-k`, `#pattern-online-softmax`, `#pattern-fused-epilogue` |
| IR stage | `#ir-ttir`, `#ir-ttgir`, `#ir-llir` |

## Phase C4: Vault Structure

```
StudyVault/
├── 00-Dashboard/
├── 01-Architecture/          # System overview, kernel dispatch flow, autotune flow
├── 02-<Module1>/             # e.g., 02-Matmul-Kernels/
├── 03-<Module2>/
├── ...
├── NN-DevOps/                # Build flags, CI, benchmarking
└── NN+1-Exercises/           # Onboarding exercises
```

## Phase C5: Dashboard

### MOC (Map of Content)
- **Architecture Overview** → `[[01-Architecture/System-Overview]]`, `[[01-Architecture/Kernel-Dispatch-Flow]]`, `[[01-Architecture/Autotune-Flow]]`.
- **Module Map** — table of all modules with purpose + Key Kernel + link.
- **Kernel Surface** — table of every public `@triton.jit` kernel: name, file, target backend, `tl.dot` usage, Python wrapper, autotune key.
- **Backend Matrix** — supported backends × precision (FP16/BF16/FP8) × feature flags.
- **Getting Started** — exact install, test, benchmark commands.
- **Tag Index** with rules.
- **Onboarding Path** — recommended reading order.

### Quick Reference
- Install / build commands (editable install, custom Triton fork).
- Benchmark commands (`pytest benchmarks/`, `python bench/run.py`, `proton --hook=triton`).
- IR-dump env vars (`TRITON_KERNEL_DUMP=1`, `MLIR_ENABLE_DUMP=1`, `LLVM_IR_ENABLE_DUMP=1`, `TRITON_CACHE_DIR`).
- Common runtime env vars (`TRITON_INTERPRET=1`, `TRITON_PRINT_AUTOTUNING=1`, `CUDA_VISIBLE_DEVICES`).
- Important file locations.

## Phase C6: Module Notes

Per [triton-codebase-templates.md](triton-codebase-templates.md). Key fields:
- YAML frontmatter: `module`, `path`, `keywords`, `target_backend`, `tl_mechanisms` (when applicable).
- **Purpose**, **Key Files**, **Public Interface** (Python wrappers + PyTorch custom ops), **`@triton.jit` Kernel**, **Tile Shapes**, **Autotune Config Space**, **Dependencies**, **Testing**, **Related Notes**.
- ASCII diagram of internal data flow + tile decomposition.

For autotune-heavy modules, create separate Kernel notes (one per significant kernel) using the Kernel template in `triton-codebase-templates.md`.

## Phase C7: Onboarding Exercises

Per [triton-codebase-templates.md](triton-codebase-templates.md). Categories:
- **Code reading** ("Trace what happens when you call `<wrapper>(M=4096, N=4096, K=4096)`")
- **Configuration** ("How would you add a new autotune config for skinny matmuls (`M << N`)?")
- **Debugging** ("If `TRITON_INTERPRET=1` produces different results than GPU run, where would you look first?")
- **IR exploration** ("Dump TTGIR for this kernel and identify the `#mma` layout in use; what changes if you set `num_warps=8`?")
- **Extension** ("How would you add an FP8 path to this kernel?")
- Minimum 5 per major module. Answers in `> [!answer]- View Answer` fold callouts.

## Phase C8: Interlinking

1. `## Related Notes` on every module note.
2. MOC links to every module + exercise file.
3. Python wrapper ↔ `@triton.jit` kernel ↔ autotune config cross-linked.
4. Architecture notes reference specific module implementations.
5. Exercises reference the modules they cover.

## Phase C9: Self-Review

Verify against [quality-checklist.md](quality-checklist.md) **Codebase Mode** section. Fix and re-verify until all checks pass.
