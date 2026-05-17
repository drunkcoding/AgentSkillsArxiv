# CUDA Question Bank — Seed Pool

> 60 seed questions (10 per topic × 6 topics). These are STARTING POINTS for the quiz tutor — NOT a closed bank. Per `quiz-rules.md`, the tutor must rephrase / rotate context / change GPU generation / change failure scenario when re-using a seed in a follow-up round on the same concept.
>
> Each seed lists the concept it probes; the tutor uses that to update the matching row in `concepts/{topic}.md` after grading.

---

## 1. CUDA Kernels (10 seeds)

1. **[Occupancy]** Launch `<<<128, 256>>>`, 32 regs/thread, 4 KiB smem/block, on A100 (108 SMs, max 2048 threads/SM, 64K regs/SM, 164 KiB smem/SM). Compute theoretical occupancy.
2. **[Bank conflict]** `__shared__ float smem[256]` accessed as `smem[threadIdx.x * 4]` on Ampere (4-byte banks, 32 banks). Bank conflicts? Show work.
3. **[Warp primitives]** Write a warp-OR using `__shfl_sync` only. How does it differ from `__any_sync`?
4. **[Warp divergence]** `if (threadIdx.x == 0) {...}` — name two performance concerns. How do they differ for a 32-thread vs 128-thread block?
5. **[Memory hierarchy]** Draw memory hierarchy for a 1024×1024 tiled GEMM with 16×16 thread blocks and 16×16 smem tiles. Label global / L2 / L1-smem / registers; mark reuse across the K loop.
6. **[Async copy]** Contrast `cp.async` vs a regular global-to-shared load. Include `cp.async.commit_group` / `cp.async.wait_group`.
7. **[Constant cache]** Kernel reads `const float data[16]` via `data[threadIdx.x % 16]`. What happens in constant cache? Per-warp bandwidth?
8. **[Memory fence]** `__threadfence()` vs `__syncthreads()` — name a scenario where you need fence but NOT syncthreads.
9. **[Cooperative groups]** Sync all threads in a 128×128 2D grid without deadlock; `__syncthreads` only syncs within a block.
10. **[WGMMA / layout]** On Hopper, `wgmma.mma_async` operands need specific layout. Why does CUTLASS 3.x use `cute::Layout` for MMA operands and how does that map to the HW-expected stride pattern?

---

## 2. CUTLASS + CuTe (10 seeds)

1. **[Layouts]** Multiply row-major A (M×K) × column-major B (K×N) → row-major C. Pick CUTLASS 2.x `cutlass::gemm::device::Gemm` template args; choose ThreadblockShape & WarpShape for A100 (target 256×128×32).
2. **[Epilogue]** Contrast `cutlass::epilogue::EpilogueOp` vs `cutlass::epilogue::EpilogueNoPadding`. When does epilogue become the bottleneck?
3. **[CuTe TiledMma]** CUTLASS 3.x `cute::TiledMma` composes an `Mma_Atom` with tile dims. Target Blackwell `mma.sync` 16×16×16 fragments in a 64×64 threadblock. How is tiling composed? How many warps participate in one MMA?
4. **[Layout algebra]** `cute::coalesce(L)` where `L = (4,(2,2)):(2,(4,1))`. Show result. Why does this matter for coalescing?
5. **[SplitK]** When to use `GemmSplitKParallel` vs single-kernel `Gemm`? Tradeoffs in K?
6. **[Profile interpretation]** Profiler reports 80% peak FP16 but 40% peak FP32. Two possible causes; how to confirm with Nsight Compute?
7. **[Layout composition]** `L = (M,N):(N,1)` (row-major). `L(2,3) = ?` How does composition `L1 ∘ L2` enable nested tiling?
8. **[CuTe DSL]** `@cute.jit` compiles via MLIR/Tile IR. Current `tileiras` GPU-support limitations? Compare to `nvcc` PTX path.
9. **[Implicit GEMM]** `cutlass::conv::device::ImplicitGemm` vs direct CUDA conv: what tiling strategy maps it to the GEMM hierarchy?
10. **[WMMA scale]** A CUTLASS kernel using `cutlass::arch::wmma`. On Ampere, max warpgroup per `mma.sync`? How does it change on Hopper with WGMMA?

---

## 3. cuTile (10 seeds)

1. **[Tile decomposition]** Write a cuTile Python kernel doing 3×3 convolution on an input tile via `ct.load`/`ct.store`/tile ops. Which ops are tile-space vs array-space?
2. **[Indexing]** `ct.bid(0)` is 0-indexed in Python, 1-indexed in Julia. Port a Python kernel to Julia without adjusting — what happens? Concrete example.
3. **[Padding]** `ct.load(arr, index=(pid,), shape=(T,))` with `len(arr) % T != 0`. What happens? How does `ct.cdiv` interact?
4. **[Immutability]** Tiles immutable; raw CUDA smem mutable. Implications for memory-bound kernels?
5. **[Compiler limits]** cuTile → Tile IR → PTX through `tileiras`. Current HW-support limits? Compare to direct `nvcc`.
6. **[ct.mma on Blackwell]** `ct.mma` on SM100 maps to WGMMA. Tile-shape requirement? Compare to manual WGMMA in PTX.
7. **[Compile-time shapes]** `Tile.ndim` / `Tile.shape` are compile-time. Why does this matter for the IR compiler? Contrast PyTorch runtime shapes.
8. **[Block allreduce]** cuTile has no built-in block-level allreduce. Implement one with tile ops (tree-reduction sketch).
9. **[TileGym]** Pick one TileGym kernel and trace: array → load → tile ops → store. What tile shapes, and why?
10. **[Order parameter]** `ct.store` `order` parameter — row-major vs column-major in the cuTile model. When do you override the default?

---

## 4. Open GPU Kernel Modules (10 seeds)

1. **[Failure trace]** `RmInitAdapter failed! (0x62:0x25:2015)` from `kernel_gsp.c`. Trace the call chain to the failing GSP boot function. What does 0x25 (`NV_ERR_INVALID_DATA`) indicate?
2. **[Architectural rationale]** Why must open modules use GSP while the proprietary driver makes it optional? Design rationale?
3. **[Kernel-version support]** To add Linux 6.12 support to open modules, which directory do you modify? Which specific file?
4. **[GSP-RC]** `_kgspRpcSendMessage` sends RPC to GSP-RM. Describe the mechanism, timeout path, and GSP-RC (runlist collapse) handling.
5. **[Contribution]** CLA process; "large reformatting" guideline; why your commits won't appear as separate commits in the public repo.
6. **[GPU Direct RDMA]** `nvidia-peermem.ko` for GPU Direct RDMA peer memory: trace the data path from NIC DMA into GPU memory across the kernel modules. UVM's role?
7. **[WPR2 16K-page bug]** RTX 3080 with `CONFIG_ARM64_16K_PAGES` → `unexpected WPR2 already up` at GSP boot. Why does 16K trigger this specifically?
8. **[Firmware selection]** GSP firmware ships as chip-specific files. How does the module pick the right one? Which source file decides?
9. **[NCCL ↔ driver]** NCCL needs GPU bus IDs and NVLink state. Trace how NCCL gets them via the kernel module. Which RM API?
10. **[Forced GSP]** `NVreg_EnableGpuFirmware=0` is silently ignored on open modules. Why? Practical implications for kernel-mode debugging?

---

## 5. NCCL (10 seeds)

1. **[Ring construction]** 8 GPUs across 2 nodes (4/node, IB). Default `ncclAllReduce` chooses ring. How does the ring traverse both nodes, and why suboptimal? How to enable hierarchical allreduce?
2. **[Ring math]** 4 GPUs single-node-NVLink ring allreduce. Reduce-scatter (K steps) + allgather (K steps). For a 4 MB reduce, 1 MB/step, total per-GPU traffic?
3. **[Single-kernel fusion]** NCCL fuses comm+compute. Contrast with separate memcpy+reduction kernels. Latency advantage?
4. **[In-place]** `ncclAllReduce` with `sendbuff==recvbuff`. What must the implementation guarantee? When do you NOT want in-place?
5. **[Tree on PCIe]** `ncclBroadcast` over 4 PCIe GPUs picks `tree` per `NCCL_DEBUG=INFO`. How does tree work for broadcast? Why slow on PCIe?
6. **[Device API]** Advantages of device-initiated `ncclAllReduce` vs host-initiated? Minimum thread count for efficient device API?
7. **[Two-sided vs RMA]** `ncclSend`/`ncclRecv` vs `ncclPutSignal`/`ncclWaitSignal`. When does one-sided beat two-sided in ping-pong?
8. **[Topology flattening]** `ncclTopoFlattenBcmSwitches` merges PCIe switches. Why is flattening important? What goes wrong if switches aren't flattened?
9. **[GDR level]** `NCCL_NET_GDR_LEVEL=FLUSH` — what does it do? When `SYS` or `W32` instead?
10. **[NVLS detection]** 64-GPU × 8-node training. What determines optimal `NCCL_TOPO_XML`? How do you detect that NVLS (NVLink SHARP) is NOT in use when it should be?

---

## 6. NVSHMEM (10 seeds)

1. **[Small vs large transfer]** 256-B transfer GPU0→GPU1 with single-thread `nvshmem_putmem` vs `nvshmemx_putmem_block`. Which wins? Same question for 16 MB?
2. **[Weak ordering]** OpenSHMEM strong ordering after put+barrier; NVSHMEM relaxes. Why safe on NVIDIA GPUs? What does the programmer do to restore ordering?
3. **[Symmetric heap]** Why must all PEs allocate the same size in `nvshmem_malloc`? PE 0 allocates 1 MB but PE 1 allocates 2 MB — what happens?
4. **[Barrier hang]** 4-GPU 2-node program hangs at `nvshmem_barrier_all()`. Three likely causes; how to diagnose with dmesg / NVTX / env vars?
5. **[Overlap design]** Each GPU shares gradients with 3 peer GPUs. CUTLASS compute + NVSHMEM transfer. Draw the overlap timeline; pick a tile size that maximizes overlap with CUTLASS GEMM tiles.
6. **[Block vs warp scope]** Ampere (32 threads/warp). When use `nvshmemx_put_block` vs `nvshmemx_put_warp`? Throughput AND occupancy considerations.
7. **[Proxy bottleneck]** Single CPU proxy thread for IB transports. Why does it bottleneck small messages? How to fix in application code?
8. **[nvshmem_ptr]** When does `nvshmem_ptr(dest, pe)` return a valid pointer (direct load/store) vs NULL (must use API)? Depends on interconnect?
9. **[fence vs quiet]** `nvshmem_fence()` vs `nvshmem_quiet()`. When use fence but not quiet? When do you need quiet (not just a stream sync)?
10. **[Tile collective]** `nvshmemx_broadcast_block` vs `nvshmem_putmem` in a loop. Kernel pattern where tile-granular is strictly better?

---

## Rotation Hooks (for the tutor to vary seeds)

When the tutor needs to rephrase a seed (e.g., user already missed it once), apply one of these rotations:

- **Change GPU generation** — A100 → H100 → B200; observe how the answer changes (e.g., `cp.async` vs TMA).
- **Change API surface** — runtime API vs driver API vs PTX intrinsic.
- **Change failure scenario** — "what happens if you …" instead of "what does X do".
- **Change scale** — single GPU → multi-GPU node → multi-node; observe transport / algorithm flip.
- **Change data type** — FP32 → FP16 → FP8 → FP4; observe MMA / TMA differences.

Document the chosen rotation in the concept-file error note so the next session can rotate further.
