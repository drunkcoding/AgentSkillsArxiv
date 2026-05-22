# Numerical and benchmarking hazards

Distilled from the MLSys-2026 DSA winning runs (`dsa_sparse_attention_*` and `dsa_topk_indexer_fp8_*`). Most apply to any FlashInfer-Bench Triton kernel.

## Numerical

- **`tl.dot` precision policy**: try `tf32x3` first → fall back to `tf32` → finally `ieee` only if `abs_err > ~0.02`. `ieee` is much slower.
- **Accumulator dtype**: bf16 accumulators can blow up over many terms. Promote to f32 for reductions across long axes (e.g. attention over topk=2048).
- **LSE base**: `flashinfer-bench` expects LSE in **base-2** (`logsumexp / log(2)`), NOT base-e. Easy to get wrong on first port from PyTorch.
- **FP8 KV cache SOA layout**: per-page bytes are `[fp8_data (64*128 bytes), scales (64*4 bytes)]`, viewed as `[P, 64, 1, 132]`. A strided view like `view[..., :128]` may read into the scale region on some shapes. Always extract fp8 + scales to **contiguous** tensors before use.
- **Sentinel handling**: padding indices are `-1` in `sparse_indices`. Mask out invalid logits with `-inf` before softmax. Topk output padding slots must also be `-1` (initialize `topk_indices.fill_(-1)`).
- **Softmax masking**: mask BEFORE applying `sm_scale`, or mask the scaled logits — order matters for fp32 stability when masking with `-inf`.

## Workload-driven shortcuts (huge wins)

Before optimizing the hard case, check if the input shape makes the kernel trivial. Examples from winning runs:

- Softmax over a size-1 axis is always 1.0.
- Reductions over a size-1 dim are no-ops.
- Attention with sequence length 1 just returns the value vector.
- Gather with `k <= N` is just an index select.
- Single-batch (`batch_size=1`) workloads can drop the outer loop.

If the workload distribution is skewed, optimizing for the common easy cases gives outsized wins. The `workload-inspector` agent surfaces this; call it once per project.

## Benchmark gaming — forbidden

- **No memoizing outputs.** Cupti measures CUDA runtime; caching results from prior calls is forbidden.
- **No CUDA graphs.** Forbidden by contest rules. Event streams for *debug* timing are fine.
- **No iteration-counter tricks.** No `--quick`-specific shortcuts.
- **No pointer-specific caching.** You may persist buffers across calls *as long as contents are recomputed every call* (e.g. eliminating `torch.empty()` for fixed shape+dtype). You may NOT cache input pointers.

## Measurement noise

- **Cross-VM reference latency swings 20-30%.** A single `summary.md` row showing a 4% improvement is noise. For sub-5% deltas, run `ab_benchmark.py` (paired same-VM).
- **Sanity check**: if reference latency is >30% off the moving median from recent `summary.md` rows, the VM is anomalous. Re-run once.
- **Report split**: small vs large workloads when both are present. Aggregated means hide regime-specific regressions.

## DPS contract

Outputs are **pre-allocated by the harness** and passed as the last positional args. Never allocate `output` / `lse` / `topk_indices` inside the kernel — overwrite in-place via `.copy_()` or `tl.store`. Allocating inside breaks the DPS contract and inflates measured latency.

## Memory-floor anchor

If observed latency is within ~10% of an empirical memory-floor (a `torch.matmul` or `memcpy` at the same byte volume), the kernel is memory-bound. Tuning compute is pointless — pivot to memory layout, prefetching, or input-shape specialization.

## Triton-specific gotchas

- **`tl.dot` shape requirements**: minimum tile sizes (e.g. M≥16, N≥16). Tiny tiles silently fall back to slow paths.
- **`num_stages` vs `num_warps`**: empirical sweep. Static PTX register-pressure estimates are unreliable.
- **Autotune cache**: lives at `TORCH_EXTENSIONS_DIR=/results/torch_ext_cache` on Modal. Warmup measurements after a kernel change include compile time on the first call — that's what `warmup_runs=3` in `BenchmarkConfig` is for.
- **`.contiguous()` calls** are launches + memory round-trips. Plumb strides into the kernel instead when possible.

## Gluon

Gluon counts as Triton (allowed). Suspected Triton/Python bugs are almost always something else — investigate before blaming the compiler. The winning DSA runs only switched to Gluon after 15-20 stuck Triton iterations and ran ≥5-10 Gluon iterations before finalizing.
