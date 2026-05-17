# Topic 6: NVSHMEM (NVIDIA OpenSHMEM Library)

> **Lazy-load**: read this file ONLY when authoring `06-NVSHMEM/` in Phase CU6. Drop from working memory before reading the next topic file.

## Authoritative URLs

- Docs: https://docs.nvidia.com/nvshmem/
- API reference: https://docs.nvidia.com/nvshmem/api/index.html
- Best-practices guide: https://docs.nvidia.com/nvshmem/release-notes-install-guide/best-practice-guide/apis.html
- Main repo: https://github.com/NVIDIA/nvshmem
- Developer page: https://developer.nvidia.com/nvshmem
- "Multi-GPU Programming in NCCL and NVSHMEM" GTC webinar (search the GTC archive)

## Prerequisites

- **Topic 1: CUDA Kernels** — `__threadfence()`, memory ordering, peer access.
- Multi-GPU programming concepts (peer-to-peer mappings).
- OpenSHMEM basics: symmetric memory, PE (Processing Element) model, `shmem_put` / `shmem_get`. NVSHMEM is based on OpenSHMEM 1.3 with features from 1.4 and 1.5.
- (Optional) MPI one-sided communication helps the mental model.

## Core Concepts / Keywords (Beginner → Expert)

| Stage | Concepts |
|-------|----------|
| **Beginner** | `nvshmem_init()`, `nvshmem_finalize()`, `nvshmem_malloc()` (collective symmetric-heap allocation), `nvshmem_putmem` / `nvshmem_getmem`, PE numbering, `nvshmem_my_pe()`, `nvshmem_n_pes()`, symmetric-address concept, host-side vs device-side API, `nvshmem_fence()`, `nvshmem_quiet()` semantics |
| **Intermediate** | `nvshmemx_put_block` / `nvshmemx_put_warp` (block/warp-scoped device-initiated), `nvshmemx_putmem_on_stream` (stream-based), `nvshmem_wait_until` / `nvshmem_test`, `nvshmem_barrier` / `nvshmem_barrier_all`, atomics (`nvshmem_atomic_fetch_add`, `nvshmem_atomic_cswap`), tile-granular collectives (`nvshmemx_broadcast_block`), memory-window registration (`nvshmem_comm_window_register`) |
| **Advanced** | One-sided RMA model (put/get), **weak ordering** (different from OpenSHMEM strong ordering — must use explicit `nvshmem_fence` if you need it), advantages of GPU-initiated communication (no kernel-launch overhead, no CPU sync), CUDA-stream integration (`nvshmemx_*_on_stream`), peer-to-peer pointer queries (`nvshmem_ptr`), NVLink vs InfiniBand transports, GPUDirect Async (IBGDA) transport, multi-NIC round-robin |
| **Expert** | Device-API architecture, integration with Kokkos / linear-algebra solvers, MPI / OpenSHMEM interop, tile-level collective design rationale, NVLS multicast (`nvshmemx_mc_ptr`), LTO-IR device-code optimization, multi-PE teams, error-code returns for tile APIs, custom transport plugin framework |

## Hands-On Milestones

1. **M1: Hello-NVSHMEM** — init, `nvshmem_malloc`, `nvshmem_putmem` GPU0 → GPU1, verify with `nvshmem_getmem`. Success: round-trip succeeds; correct data at destination.
2. **M2: Ping-pong latency** — 2-GPU ping-pong with `nvshmem_putmem` + `nvshmem_wait_until` on a flag. Plot latency vs message size. Success: reproducible curve; identify the proxy-vs-IBGDA inflection.
3. **M3: Block/warp-scoped throughput** — compare `nvshmemx_put_block` and single-thread `nvshmem_putmem` for 1 MB transfers. Success: throughput improvement ratio recorded.
4. **M4: Tile broadcast** — implement a kernel where each block broadcasts its tile to all other PEs via `nvshmemx_broadcast_block`. Success: matches a CPU-side reference.
5. **M5: PyTorch training-loop integration** — overlap gradient transfer (`nvshmem_putmem`) with next-iteration compute on the source PE. Success: nsys timeline shows overlap.
6. **M6: Multi-node setup** — 2 nodes × 2 GPUs, `nvshmem_barrier_all` across nodes, measure cross-node latency. Success: latency documented; identify proxy vs IBGDA transport.
7. **M7: Proxy vs IBGDA** — Nsight Compute profile of small-message vs large-message transfers; verify the proxy thread (or absence thereof under IBGDA). Success: optimal message size identified for the platform.

## Common Pitfalls / Exam Traps

- **Symmetric-memory requirement** — all buffers passed to NVSHMEM RMA must come from `nvshmem_malloc`. Passing `cudaMalloc`'d memory or stack memory = undefined behavior. `nvshmem_ptr` returns direct pointers but those still refer to symmetric memory.
- **Weak ordering vs OpenSHMEM** — OpenSHMEM guarantees ordering after `shmem_put` + `shmem_barrier`. NVSHMEM relaxes this for GPU efficiency. Code that ports OpenSHMEM strong-ordering assumptions WILL break unless you insert `nvshmem_fence` / `nvshmem_quiet` explicitly.
- **Proxy-thread overhead for small messages** — IB/UCX/libfabric transports use a single CPU proxy. Small messages (< ~128 B) have very high overhead. `nvshmem_p` (single-element put) is inefficient on proxy transports — batch into larger transfers.
- **`nvshmem_init` must be collective** — all PEs call it simultaneously. Calling from a single process without matching peers hangs.
- **IBGDA single-thread bottleneck** — IBGDA avoids the CPU proxy but needs multiple QPs driven by multiple GPU threads to saturate IB. A single thread cannot reach peak.
- **PE number vs MPI rank** — under MPI+NVSHMEM, `nvshmem_my_pe()` is the NVSHMEM rank, not the MPI rank. Confusing them sends data to the wrong destination.
- **Stream-API completion misunderstanding** — `nvshmemx_putmem_on_stream` returns immediately; data is not guaranteed visible until `nvshmem_quiet` or `nvshmem_barrier`. Stream-sync alone is NOT enough.
- **Tile-collective shape mismatch** — `nvshmemx_broadcast_block` requires all participating PEs to use the same tile shape and the same root PE index. Mismatches produce silently-wrong output.
- **Atomic-op portability** — not all `nvshmem_atomic_*` ops are supported on all transports. Check the best-practices guide before relying on `nvshmem_atomic_cswap` on a non-NVLink fabric.

## Cross-Links to Other Topics

- **→ Topic 1 (CUDA Kernels)** — NVSHMEM device-API calls are essentially CUDA thread-initiated remote memory ops. Thread-fences, memory ordering, and warp scheduling all apply.
- **→ Topic 2 (CUTLASS)** — tile-granular NVSHMEM collectives were designed to compose with CUTLASS GEMM tile sizes for communication-computation fusion in distributed training.
- **→ Topic 3 (cuTile)** — cuTile tile values can be the payload for `nvshmemx_put_block` / `nvshmemx_get_block`. Multi-GPU cuTile kernels naturally use NVSHMEM for cross-PE data movement.
- **→ Topic 4 (Open GPU Kernel Modules)** — NVSHMEM uses `nvidia-peermem.ko` for GPU Direct RDMA. NVLink P2P is mediated by `nvidia.ko`'s peer-access support.
- **→ Topic 5 (NCCL)** — complementary libraries. NVSHMEM = fine-grained one-sided GPU-initiated; NCCL = structured collectives. Many workloads use both. NCCL's P2P channel can use NVSHMEM as a transport on supported platforms.

## Practice Question Seeds

1. Transfer a 256-B gradient tensor GPU0 → GPU1. Compare single-thread `nvshmem_putmem` vs `nvshmemx_putmem_block`. Which wins? How does the answer change at 16 MB?
2. OpenSHMEM guarantees ordering via `shmem_put`+`shmem_barrier`; NVSHMEM relaxes this. Why is the relaxation safe on NVIDIA GPUs? What does the programmer need to do to restore ordering?
3. `nvshmem_malloc` allocates symmetric memory. Why must all PEs allocate the same size? What if PE 0 allocates 1 MB but PE 1 allocates 2 MB?
4. 4-GPU 2-node NVSHMEM program hangs at `nvshmem_barrier_all()`. List three likely causes and how to diagnose each (dmesg, NVTX, env vars).
5. Distributed training: each GPU shares gradients with 3 peer GPUs. CUTLASS for compute, NVSHMEM for transfer. Draw the compute/communication overlap timeline; pick a tile size that maximizes overlap with CUTLASS GEMM tiles.
6. On Ampere (32 threads/warp), when do you use `nvshmemx_put_block` vs `nvshmemx_put_warp`? Consider throughput and occupancy.
7. NVSHMEM uses a CPU proxy thread for IB transports. Why does this bottleneck small messages, and how do you fix it in application code?
8. `nvshmem_ptr(dest, pe)` returns a valid pointer for direct load/store vs returns NULL — under what interconnect conditions does each happen?
9. Compare `nvshmem_fence()` vs `nvshmem_quiet()`. When do you use fence but not quiet? When do you need quiet (not just a stream sync)?
10. Tile-granular collectives like `nvshmemx_broadcast_block` vs plain `nvshmem_putmem`-in-a-loop. Give a kernel pattern where tile-granular is strictly better.
