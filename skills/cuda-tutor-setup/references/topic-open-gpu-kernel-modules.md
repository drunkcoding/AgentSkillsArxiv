# Topic 4: NVIDIA Open GPU Kernel Modules

> **Lazy-load**: read this file ONLY when authoring `04-Open-GPU-Kernel-Modules/` in Phase CU6. Drop from working memory before reading the next topic file.

## Authoritative URLs

- Main repo: https://github.com/NVIDIA/open-gpu-kernel-modules
- `kernel_open` README (per-version): https://download.nvidia.com/XFree86/Linux-x86_64/<version>/README/kernel_open.html
- GSP firmware notes: https://download.nvidia.com/XFree86/Linux-x86_64/<version>/README/gsp.html
- 2022 announcement blog: https://developer.nvidia.com/blog/nvidia-releases-open-source-gpu-kernel-modules/
- Hardware-interface docs (separate repo): https://github.com/nvidia/open-gpu-doc

## Prerequisites

- **Topic 1: CUDA Kernels** — at the user-API level. Helps understand what `cuLaunchKernel` ultimately reaches.
- Linux kernel module basics: `Kbuild`, `Makefile` rules, `MODULE_LICENSE`, `module_init` / `module_exit`.
- Kernel vs user-space separation, `ioctl` interface.
- Familiarity with kernel data structures (linked lists, RB trees) helps when reading RM source.

## Core Concepts / Keywords (Beginner → Expert)

| Stage | Concepts |
|-------|----------|
| **Beginner** | `nvidia.ko`, `nvidia-modeset.ko`, `nvidia-drm.ko`, `nvidia-uvm.ko`, `nvidia-peermem.ko`, OS-agnostic layer (`src/`) vs kernel-interface layer (`kernel-open/`), GSP firmware binaries (`gsp_*.bin`), dual GPL/MIT license, building from source (`make modules -j`), `/proc/driver/nvidia/`, driver flavor selection in the `.run` installer |
| **Intermediate** | RM (Resource Manager) internal component, GSP (GPU System Processor) offload architecture, GSP firmware boot (`kgspBootGspRm`, WPR2 region), `nv-kernel.o_binary` precompiled OS-agnostic blob, `NVreg_EnableGpuFirmware` (mandatory ON for open modules — cannot be disabled), nouveau integration tools, MMU fault handling, channel teardown |
| **Advanced** | CPU-RM ↔ GSP-RM RPC mechanism, `kernel_gsp.c` send/receive (`_kgspRpcSendMessage`), GPU reset sequence, `kgspWaitForRmInitDone`, WPR2 (Work Priority Register 2) memory region, `kernel_gsp_<chip>.c` per-arch boot (`kernel_gsp_tu102.c`, `kernel_gsp_ga102.c`, etc.), strict version match between kernel modules and user-space driver, PCI topology handling, GPU Direct RDMA |
| **Expert** | Full RM source in `src/nvidia/`, GSP fault path (`_kgspRpcMMUFaultQueued`), channel API (`nvUvmInterface*`), UVM engine in `nvidia-uvm.ko`, DRM lease for VR, modeset DRM lifecycle, diagnosing `NVRM:` dmesg messages, contributing via PR (signed CLA), understanding the shared codebase with the proprietary driver |

## Hands-On Milestones

1. **M1: Build & install** — clone the repo, check out a tag matching your driver version, build the kernel modules, install with the proprietary user-space using `.run --no-kernel-modules`. Success: `nvidia-smi` works on freshly-built modules.
2. **M2: Inspect runtime** — `cat /proc/driver/nvidia/version`, `cat /proc/driver/nvidia/gpus/*/information`, `nvidia-smi -q | grep "GSP Firmware"`. Success: identify GSP firmware version actually loaded.
3. **M3: Trace GSP boot** — read `kernel_gsp.c` and trace `_kgspBootGspRm` → `kgspPrepareForBootstrap_HAL` → `kgspWaitForRmInitDone`. Identify the WPR2 region's purpose. Success: explain on paper to a peer.
4. **M4: Extract & diff GSP firmware** — build the `nouveau/` tools, extract a GSP firmware blob, compare to `/lib/firmware/nvidia/`. Success: identify the blob format.
5. **M5: Instrument with printk** — add a `printk(KERN_INFO "NVRM-debug: ...")` to a function in `kernel-open/nvidia/`, rebuild, verify in `dmesg`. Success: see your message after a GPU op.
6. **M6: Disable-vs-required GSP** — on proprietary driver, try `NVreg_EnableGpuFirmware=0` and observe the difference. Confirm it is silently ignored on open modules. Success: write a one-paragraph explanation.

## Common Pitfalls / Exam Traps

- **Version mismatch** — open kernel modules and user-space driver MUST be from the same release. Otherwise `RmInitAdapter failed`. Major recurring pain point.
- **GSP is mandatory** — open modules require GSP firmware. There is NO disable option. `NVreg_EnableGpuFirmware=0` works only on the proprietary driver.
- **`CONFIG_ARM64_16K_PAGES` boot failure** — on some Arm64 laptops, GSP boot fails with `unexpected WPR2 already up`. Workaround: `CONFIG_ARM64_4K_PAGES`. Known regression.
- **Toolchain mismatch** — kernel-interface layer must be built with the toolchain used to build the running kernel. Mixed toolchains cause silent bugs.
- **Closed binary blob** — `nv-kernel.o_binary` ships in the `.run` and is identical across open/proprietary. Only the kernel-interface layer is truly open. Do not expect a fully auditable driver.
- **Nouveau tools are not for nouveau** — the `nouveau/` directory provides firmware-extraction tools used by Nouveau developers, not a way to drive the GPU through Nouveau using the NVIDIA modules.
- **Patches don't appear as separate commits** — submitted PRs are integrated into NVIDIA's internal repo and re-exported as squashed updates. Do not be surprised your commit history disappears.

## Cross-Links to Other Topics

- **→ Topic 1 (CUDA Kernels)** — every `cuLaunchKernel` traverses: user code → `libcuda.so` (user-space driver) → ioctl → `nvidia.ko` (kernel-interface) → RM → RPC → GSP firmware → GPU hardware. Owning this topic explains the bottom half of the stack.
- **→ Topic 2 (CUTLASS)** — CUTLASS runs entirely in user space; kernels are dispatched through `cuLaunchKernel`. Driver-level issues (kernel launch latency, RM hangs) manifest as performance issues for CUTLASS.
- **→ Topic 3 (cuTile)** — cuTile JIT pipeline ends with the driver loading a cubin via `cuModuleLoad`, which goes through the same path.
- **→ Topic 5 (NCCL)** — NCCL's topology detection (`ncclTopoSystem`) reads GPU PCI topology and NVLink state via the driver API, which queries the kernel module's RM.
- **→ Topic 6 (NVSHMEM)** — NVSHMEM uses `nvidia-peermem.ko` for GPU Direct RDMA. NVLink P2P access between GPUs is mediated by the kernel module.

## Practice Question Seeds

1. dmesg shows `RmInitAdapter failed! (0x62:0x25:2015)` from `kernel_gsp.c`. Trace the call chain from `RmInitAdapter` down to the failing GSP boot function. What does error 0x25 (`NV_ERR_INVALID_DATA`) indicate here?
2. Architecturally, why must the open kernel modules use GSP, while the proprietary driver makes it optional? What's the design rationale?
3. Open modules are split into `kernel-open/` (kernel-interface) and `src/` (OS-agnostic). To add Linux 6.12 support, which directory do you change? Which specific file?
4. `_kgspRpcSendMessage` sends RPC to GSP-RM. Describe the mechanism, the timeout path, and how the kernel handles GSP-RC (runlist collapse) events.
5. To submit a patch to open-gpu-kernel-modules: describe the CLA process, the "large reformatting" guideline, and why your commits won't appear as separate commits in the public repo.
6. GPU Direct RDMA via `nvidia-peermem.ko`: trace the data path from NIC DMA into GPU memory across the kernel modules. What is UVM's role?
7. RTX 3080 + `CONFIG_ARM64_16K_PAGES` produces `unexpected WPR2 already up` at GSP boot. Why does 16K page granularity trigger this specifically?
8. GSP firmware ships as multiple chip-specific files (`gsp_tu10x.bin`, `gsp_ad10x.bin`). How does the module pick the right one for a given GPU? Which source file decides?
9. NCCL's topology detection wants GPU bus IDs and NVLink state. Trace how NCCL obtains them through the kernel module. Which RM API is used?
10. `NVreg_EnableGpuFirmware=0` is silently ignored on open kernel modules. Why did NVIDIA make this choice? What are the practical implications for kernel-mode debugging?
