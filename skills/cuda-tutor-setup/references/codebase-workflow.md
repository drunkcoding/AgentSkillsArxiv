# Codebase Mode — CUDA Onboarding Vault Workflow

> Generate a StudyVault that helps a new developer understand a CUDA / CUTLASS / NCCL / NVSHMEM / driver codebase.
> All scanning and output MUST stay within CWD.

## Phase C1: Project Exploration

1. **Scan project structure**: Glob source files (`*.cu`, `*.cuh`, `*.cpp`, `*.h`, `*.py`, `*.cmake`, `CMakeLists.txt`, `setup.py`, `pyproject.toml`, `Makefile`, `Kbuild`). Build a file tree.
2. **Detect tech stack and CUDA features used**:
   - Toolkit version: parse `CMakeLists.txt` for `find_package(CUDAToolkit ...)` or `CMAKE_CUDA_COMPILER` / `nvcc --version` output.
   - Target SM: look for `-arch=sm_XX`, `CMAKE_CUDA_ARCHITECTURES`, `TORCH_CUDA_ARCH_LIST`.
   - External libs: scan `#include` for `cublas`, `cudnn`, `cutlass/`, `cute/`, `nccl.h`, `nvshmem.h`.
   - PyTorch / Triton / DLPack integration markers.
   - For driver repos: detect `kernel-open/`, `src/nvidia/`, GSP firmware references.
3. **Identify role**:
   - Kernel library (CUTLASS-style, FlashInfer, sgl-kernel) → focus on per-kernel notes + MMA/TMA tile structure.
   - Collective library (NCCL fork, custom communication) → focus on algorithm + transport layers.
   - Driver (open-gpu-kernel-modules) → focus on RM / GSP / UVM boundary.
   - Application / training code → focus on host orchestration + which kernels are called.
4. **Read key files**: `README.md`, `CONTRIBUTING.md`, entry points (`main.cu`, top-level Python `__init__.py`), build config.
5. **Present findings** to user for confirmation before proceeding.

## Phase C2: Architecture Analysis

1. **Identify patterns**:
   - Host wrapper → device kernel dispatch (single-stream, multi-stream, CUDA Graph).
   - Tile structure (CTA tile / warp tile / register tile sizes).
   - MMA atom usage (`mma.sync`, `wgmma.mma_async`, `cute::Mma_Atom`).
   - Async copy pattern (`cp.async` / `cp.async.bulk` / TMA descriptors).
   - Memory tiling (shared memory swizzles).
2. **Trace one representative kernel end-to-end**: pick a high-traffic kernel (e.g., the main GEMM or attention kernel) and document:
   - Host wrapper signature.
   - Launch config (`<<<grid, block, smem>>>` or `cuLaunchKernelEx`).
   - Device entry point.
   - Memory hierarchy used.
   - Sync pattern (`__syncthreads`, `__syncwarp`, `cuda::barrier`, `cooperative_groups::sync`).
   - Exit (epilogue, output store).
3. **Map dependencies**: which modules use which.
4. **Document data flow**: input tensors → host wrapper → device kernel → output.
5. **Build architecture summary**: ASCII diagram + description.

## Phase C3: Tag Standard

Define vocabulary before creating notes (English, lowercase, kebab-case):

| Category | Examples |
|----------|----------|
| Architecture | `#arch-ampere`, `#arch-hopper`, `#arch-blackwell` |
| SM target | `#sm-80`, `#sm-90`, `#sm-100` |
| Kernel role | `#kernel-gemm`, `#kernel-attention`, `#kernel-conv`, `#kernel-allreduce` |
| API surface | `#api-host-wrapper`, `#api-device-entry`, `#api-python-binding` |
| MMA/TMA | `#mma-sync`, `#mma-wgmma`, `#mma-wmma`, `#tma`, `#cp-async` |
| Pattern | `#pattern-mainloop-pipeline`, `#pattern-split-k`, `#pattern-ring-allreduce` |

## Phase C4: Vault Structure

```
StudyVault/
├── 00-Dashboard/
├── 01-Architecture/          # System overview, kernel dispatch flow, memory model
├── 02-<Module1>/             # e.g., 02-GEMM-Mainloop/
├── 03-<Module2>/
├── ...
├── NN-DevOps/                # Build flags, CI, profiling commands
└── NN+1-Exercises/           # Onboarding exercises
```

## Phase C5: Dashboard

### MOC (Map of Content)
- **Architecture Overview** → `[[01-Architecture/System-Overview]]`, `[[01-Architecture/Kernel-Dispatch-Flow]]`.
- **Module Map** — table of all modules with purpose + Key Kernel + link.
- **Kernel Surface** — table of every public kernel: name, file, target SM, MMA usage, host wrapper.
- **Build Matrix** — supported SMs × precision (FP16/BF16/FP8/FP4) × feature flags.
- **Getting Started** — exact build, test, benchmark commands.
- **Tag Index** with rules.
- **Onboarding Path** — recommended reading order.

### Quick Reference
- Build commands (debug, release, ASan, profile).
- Profile commands (`ncu`, `nsys`, `compute-sanitizer`).
- Common env vars (e.g., `CUDA_VISIBLE_DEVICES`, `NCCL_DEBUG`, `NVSHMEM_DEBUG`, `CUDA_LAUNCH_BLOCKING=1`).
- Important file locations.

## Phase C6: Module Notes

Per [cuda-codebase-templates.md](cuda-codebase-templates.md). Key fields:
- YAML frontmatter: `module`, `path`, `keywords`, `target_sm`, `mma_atoms` (when applicable).
- **Purpose**, **Key Files**, **Public Interface** (host wrappers + Python bindings), **Device Entry**, **Memory Tiling** (CTA/warp/reg sizes), **Sync Pattern**, **Dependencies**, **Testing**, **Related Notes**.
- ASCII diagram of internal data flow.

For API-heavy modules, create separate Kernel notes (one per significant kernel) using the Kernel template in `cuda-codebase-templates.md`.

## Phase C7: Onboarding Exercises

Per [cuda-codebase-templates.md](cuda-codebase-templates.md). Categories:
- **Code reading** ("Trace what happens when you call X with these arguments")
- **Configuration** ("How would you change the tile size to support a new shape?")
- **Debugging** ("If `compute-sanitizer` reports a race in this kernel, where would you look first?")
- **Extension** ("How would you add a new dtype to this kernel?")
- Minimum 5 per major module. Answers in `> [!answer]- View Answer` fold callouts.

## Phase C8: Interlinking

1. `## Related Notes` on every module note.
2. MOC links to every module + exercise file.
3. Host wrapper ↔ device kernel ↔ MMA atom cross-linked.
4. Architecture notes reference specific module implementations.
5. Exercises reference the modules they cover.

## Phase C9: Self-Review

Verify against [quality-checklist.md](quality-checklist.md) **Codebase Mode** section. Fix and re-verify until all checks pass.
