# Modal setup and benchmarking infrastructure

The template uses [Modal](https://modal.com/) for all GPU work — no local GPU required.

## One-time setup

```bash
conda create -n fi-bench python=3.12
conda activate fi-bench
pip install flashinfer-bench modal
modal setup                                # log in
modal volume create flashinfer-trace
modal volume put flashinfer-trace /path/to/flashinfer-trace/
```

The `flashinfer-trace` volume is mounted at `/data` inside the container and holds the workload trace set.

## Modal image

`scripts/run_modal.py` defines the image:

- Base: `flashinfer/flashinfer-ci-cu132:latest` with Python 3.12 added.
- Force-reinstalls `flashinfer-bench` from git `main` (PyPI 0.1.2 is stale).
- Adds `cupti-python` — required for accurate timing. Without it `flashinfer-bench` falls back to CUDA events which include ~2-4 µs launch overhead and over-report latency.
- Env: `TORCH_EXTENSIONS_DIR=/results/torch_ext_cache`, `DSA_CUTLASS_DIR=/results/cutlass` (caches CUTLASS clone + torch extension builds across runs).

GPU: `B200:1`. Timeout: 1800s. Retries: 3.

## Modes

| Mode | Command | Workloads | Time |
|---|---|---|---|
| `--quick` | `modal run scripts/run_modal.py --quick` | 2 (smallest + largest) | <1 min |
| `--stride N` | `modal run scripts/run_modal.py --stride N` | every Nth of 128 | ~2-3 min @ N=2 |
| (default) | `modal run scripts/run_modal.py` | all 128 | 10-15 min |

`--quick` runs both ends because a single workload (usually the smallest) silently passes shape-assumption bugs.

## Env vars

Modal does NOT inherit shell env vars. Pass them via `--env`:

```bash
modal run scripts/run_modal.py --stride 2 --env "DSA_PROFILE=1,DSA_FOO=bar"
```

This is the only path to enable per-kernel profile builds (the project convention is `<PREFIX>_PROFILE=1`).

## A/B harness (`ab_benchmark.py`)

Paired same-VM comparison eliminates the 20-30% cross-VM reference-latency variance. Both candidate kernels are packed and run back-to-back in one Modal function call → one container → one GPU.

```bash
modal run scripts/ab_benchmark.py::run --a experiments/exp_N/sparse_fused.py
```

`A` is the baseline (e.g. previous best); `B` is always the current `solution/triton/<name>_fused.py`. Reports per-workload paired delta and aggregate win rate.

**WARNING:** `ab_benchmark.py` defines its own Modal image independently of `run_modal.py` (Modal only uploads the entrypoint script — `scripts.run_modal` cannot be imported remotely). Keep the two image definitions in sync.

## Result schema

`run_benchmark` returns a dict keyed by definition → workload UUID → entry:

```python
{
  "status": "passed" | "failed_correctness" | "failed_compile" | ...,
  "solution": <name>,
  "latency_ms": <float>,
  "reference_latency_ms": <float>,
  "speedup_factor": <float>,        # IGNORE — see CLAUDE.md "absolute latencies only"
  "max_abs_error": <float>,
  "max_rel_error": <float>,
}
```

Always report **absolute** kernel latency. Speedup ratios swing 20-30% across VMs; only A/B paired deltas are trustworthy for sub-5% changes.

## Pipe to bench.log

`/log-experiment` looks for `bench.log` in the repo root:

```bash
modal run scripts/run_modal.py --stride 2 2>&1 | tee bench.log
```

## Crash-loop handling

If a Modal container fails to boot repeatedly (not just slow): cancel and diagnose locally. Don't wait. Common causes: image-definition drift between `run_modal.py` and `ab_benchmark.py`, missing pip dep, broken `pack_solution`.
