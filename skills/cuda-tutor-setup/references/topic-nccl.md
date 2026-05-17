# Topic 5: NCCL (NVIDIA Collective Communications Library)

> **Lazy-load**: read this file ONLY when authoring `05-NCCL/` in Phase CU6. Drop from working memory before reading the next topic file.

## Authoritative URLs

- Main repo: https://github.com/NVIDIA/nccl
- User guide: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/
- API reference (collectives): https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/api/coll.html
- Getting started: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/getting_started.html
- Developer page: https://developer.nvidia.com/nccl
- Fault tolerance: https://docs.nvidia.com/deeplearning/nccl/user-guide/docs/usage/fault_tolerance.html

## Prerequisites

- **Topic 1: CUDA Kernels** — must know streams, peer-to-peer memory access, the SIMT execution model.
- Distributed-computing basics (MPI communicators map conceptually to NCCL communicators).
- Ring-reduction algorithm intuition.
- (Optional) MPI or `torch.distributed` exposure — many NCCL apps are bootstrapped via these.

## Core Concepts / Keywords (Beginner → Expert)

| Stage | Concepts |
|-------|----------|
| **Beginner** | `ncclGetUniqueId()`, `ncclCommInitRank()`, `ncclCommInitAll()`, `ncclAllReduce`, `ncclBroadcast`, `ncclReduce`, `ncclAllGather`, `ncclReduceScatter`, `ncclAlltoAll`, `ncclSend`/`ncclRecv`, stream argument, `ncclGroupStart`/`ncclGroupEnd`, `ncclDataType_t`, `ncclRedOp_t`, in-place vs out-of-place |
| **Intermediate** | `ncclCommInitRankConfig` (options), `ncclCommSplit`, `ncclCommShrink`, `ncclCommGrow`, fault tolerance (`ncclCommAbort`, `ncclCommGetAsyncError`), `NCCL_DEBUG=INFO`/`WARN`/`TRACE`, `NCCL_TOPO_DUMP`, multi-device-per-thread group semantics, single-kernel implementation (comm+compute fused), topology-aware paths |
| **Advanced** | Ring vs tree algorithm selection (`NCCL_ALGO=RING`/`TREE`/`PAT`), `NCCL_TREE_THRESHOLD`, `NCCL_SINGLE_RING_THRESHOLD`, channel concept (parallel data flows, up to 16), NVLS (NVLink SHARP), `NCCL_COLLNET_ENABLE`, topology detection (`ncclTopoSystem`), intra-node vs inter-node, double-binary-trees, P2P bar visibility, `NCCL_NET_GDR_LEVEL`, `NCCL_PROTO=Simple`/`LL`/`LL128`, NCCL RAS |
| **Expert** | NCCL device API (`ncclDevCommCreate`, device-initiated `ncclAllReduce` from CUDA kernels), one-sided RMA (`ncclPutSignal`/`ncclWaitSignal`), GIN (GPU-initiated networking), remote reduce-and-copy primitives (`ncclLsaReduceSumCopy`), multimem operations, CUDA Graphs + NCCL, plugin framework for custom transports |

## Hands-On Milestones

1. **M1: Single-process 4-GPU allreduce** — `ncclCommInitAll` for 4 GPUs, `ncclAllReduce` on 1 GB buffer, time with `cudaEvent`. Success: bandwidth ≥ 80% of theoretical NVLink for the platform.
2. **M2: Multi-node allreduce** — 2 nodes × 2 GPUs via MPI bootstrap. Verify cross-node `ncclAllReduce`. Success: latency and bandwidth measured; compare intra- vs inter-node.
3. **M3: Computation-communication overlap** — `ncclGroupStart`/`ncclGroupEnd` batching + multiple CUDA streams. Success: timeline (Nsight Systems) shows kernel and NCCL kernels concurrent.
4. **M4: Hierarchical allreduce** — `ncclCommSplit` by node; manual intra-node reduce-scatter → inter-node allreduce → intra-node allgather. Success: ≥10% bandwidth improvement vs flat allreduce on the same hardware.
5. **M5: Fault tolerance** — non-blocking communicators, handle `ncclCommGetAsyncError`, abort + reinit gracefully. Success: simulated rank failure recovers without process restart.
6. **M6: Device API** — `ncclDevCommCreate` + device-initiated `ncclAllReduce` inside a CUDA kernel. Success: end-to-end latency improvement vs host-initiated for small messages.
7. **M7: Tune `NCCL_SINGLE_RING_THRESHOLD`** — profile a workload, tune the threshold, demonstrate improved overlap. Success: documented before/after Nsight Systems traces.

## Common Pitfalls / Exam Traps

- **Blocking semantics misunderstood** — NCCL functions enqueue to a stream and return; the GPU work is not done until `cudaStreamSynchronize`. Reading `recvbuff` immediately after `ncclAllReduce` (without sync) is a classic bug.
- **In-place vs out-of-place size confusion** — `ncclAllGather` `recvbuff` size = `sendcount * nRanks`; `ncclReduceScatter` `recvbuff` = `sendcount / nRanks` per rank. Wrong size → silent buffer overrun.
- **Group-semantics deadlock** — `ncclGroupStart` / `ncclGroupEnd` must contain matched collective pairs; nested groups deadlock. Point-to-point `ncclSend`/`ncclRecv` inside a group requires symmetric ordering.
- **Finalize-vs-destroy ordering** — `ncclCommFinalize` is non-blocking (returns `ncclInProgress`); wait for the stream before `ncclCommDestroy`. Calling destroy too early hangs.
- **Silent topology fallback** — if NCCL fails to detect NVLink, it falls back to PCIe with no warning. Check `NCCL_DEBUG=INFO` + `NCCL_TOPO_DUMP` to confirm the selected graph.
- **`NCCL_SINGLE_RING_THRESHOLD` mis-tuning** — too high forces single-ring on huge messages; too low forces tree on small messages. Default depends on hardware; never guess blindly.
- **NCCL 1.x vs 2.x API** — `ncclInit()` is gone in 2.x. In-place requires `sendbuff == recvbuff` for some collectives, not all. Mixing causes linker errors.
- **Async error ignored** — non-blocking communicators report errors only via `ncclCommGetAsyncError`. Polling-free code drops errors silently.
- **Stream-capture incompatibility (older NCCL)** — until NCCL ~2.20 you could not capture NCCL collectives into a CUDA Graph. Check the version.

## Cross-Links to Other Topics

- **→ Topic 1 (CUDA Kernels)** — NCCL is implemented as CUDA kernels using warp-level operations and ring patterns over peer-to-peer memory. Understanding `__threadfence_system`, async copies, and warp shuffles explains NCCL's internals.
- **→ Topic 2 (CUTLASS)** — in distributed training, CUTLASS produces gradients that NCCL all-reduces. The two are layered: CUTLASS in compute, NCCL in communication.
- **→ Topic 3 (cuTile)** — NCCL added tile-granular collective APIs that align with cuTile tile sizes. Avoids synchronizing entire buffers when you only need to communicate a tile.
- **→ Topic 4 (Open GPU Kernel Modules)** — NCCL's topology detection reads GPU bus IDs / NVLink state through the driver. `nvidia.ko` RM provides the state.
- **→ Topic 6 (NVSHMEM)** — NCCL gives structured collectives; NVSHMEM gives one-sided RMA. Advanced workloads use both. NCCL's P2P transport can internally use NVSHMEM on supported hardware.

## Practice Question Seeds

1. 8 GPUs across 2 nodes (4/node, IB between). Default `ncclAllReduce` chooses ring. Show how the ring traverses both nodes and why this can be suboptimal. How do you enable a hierarchical allreduce?
2. Draw the ring algorithm for `ncclAllReduce` on 4 GPUs (single node, NVLink). Reduce-scatter (K steps) and allgather (K steps). For a 4 MB reduce, 1 MB per step, what's the total per-GPU traffic?
3. NCCL fuses comm+compute in one kernel. Contrast with separate memcpy + reduction kernels. What's the latency advantage?
4. `ncclAllReduce` with `sendbuff == recvbuff` (in-place): what must the implementation guarantee? When do you NOT want in-place?
5. `ncclBroadcast` on 4 GPUs over PCIe (no NVLink) picks `tree` per `NCCL_DEBUG=INFO`. How does the tree algorithm work for broadcast? Why slow on PCIe?
6. Device API: advantages of device-initiated collectives vs host-initiated? Minimum thread count for efficient device API use?
7. `ncclSend`/`ncclRecv` (two-sided) vs `ncclPutSignal`/`ncclWaitSignal` (one-sided RMA). When does one-sided beat two-sided for ping-pong?
8. In `src/graph/topo.cc`, `ncclTopoFlattenBcmSwitches` merges PCIe switches. Why does flattening matter for performance? What goes wrong if switches aren't flattened?
9. `NCCL_NET_GDR_LEVEL=FLUSH` — what does it do? When would you set `SYS` or `W32` instead?
10. Designing 64-GPU training across 8 nodes: what determines optimal `NCCL_TOPO_XML` content? How do you detect that NVLS (NVLink SHARP) is NOT in use when it should be?
