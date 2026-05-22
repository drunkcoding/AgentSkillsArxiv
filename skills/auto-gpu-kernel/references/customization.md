# Customizing the template for a new kernel

The template ships parameterized for DSA sparse attention. To target a different FlashInfer-Bench kernel, edit these files **before** launching the loop. The optimize/benchmark/log-experiment workflow is kernel-agnostic and rarely needs edits.

## 1. `CLAUDE.md` — kernel description

This is the source of truth read by every sub-agent. Update:

- **Title line** — kernel definition name (`<definition>` in the FlashInfer-Bench trace set).
- **Non-negotiable rules** — usually keep as-is. Adjust only if Gluon isn't applicable, or if the kernel has special constraints.
- **Modal commands table** — adjust `--stride` for your workload count. Default heuristic: stride should yield ~10-16 workloads per iteration (~2-3 min). For a 128-workload set use `--stride 8` or `--stride 2` depending on per-workload cost.
- **Repo layout** — rename file paths (e.g. `solution/triton/<name>_fused.py`).
- **Kernel I/O** — fixed shapes, input dtypes, output DPS contract.
- **Numerical hazards** — `tl.dot` precision policy, FP8 layout quirks, LSE base, accumulator dtype concerns.

Keep CLAUDE.md under ~70 lines. It loads into every agent's context.

## 2. `config.toml` — solution metadata

```toml
[solution]
name = "<your-solution-name>"
definition = "<flashinfer-bench-definition>"  # exact name from the trace set
author = "YOUR NAME"

[build]
language = "triton"             # or "cuda" — but CLAUDE.md forbids leaving Triton
source_dir = "triton"
entry_point = "<file>.py::kernel"
```

## 3. `solution/triton/` — kernel + baseline

- `<name>_baseline.py` — PyTorch reference. **Read by sub-agents** for numerical semantics and tensor consumption patterns. Keep it correct and readable, not fast.
- `<name>_fused.py` — the kernel being optimized. Initial state: stub raising `NotImplementedError`. The optimizer loop bootstraps from PyTorch → tiled Triton → fused.

The entry function signature must match the FlashInfer-Bench definition exactly (positional args, DPS outputs at the end).

## 4. `.claude/commands/` — slash commands

Usually no edits. Two parameters to tune per kernel:

- `optimize.md` § "Research-agent triggers" — adjust plateau threshold if your kernel converges fast/slow.
- `optimize.md` § "Gluon migration" — adjust the 15-20 iteration trigger.

## 5. `.claude/agents/` — sub-agents

Optionally edit the `description:` frontmatter to make the routing clearer to Claude (e.g. mention your kernel name). Body rarely needs edits — it reads `CLAUDE.md` for kernel specifics.

## 6. `.claude/settings.json` — sandbox

The default config permits Modal network access and denies `pip install`, `git clone`, web fetch. Adjust `network.allowedDomains` only if you need additional infrastructure (e.g. an artifact registry).

## 7. `scripts/` — runtime

- `run_modal.py` — entry. Update the Modal image only if your kernel needs extra Python deps. The image is pinned to `flashinfer/flashinfer-ci-cu132:latest` + force-reinstall of `flashinfer-bench` `main` + `cupti-python`.
- `pack_solution.py` — reads `config.toml`, packs source into a Solution JSON. Rarely needs edits.
- `ab_benchmark.py` — paired same-VM A/B harness. Has a **separate Modal image definition** that must be kept in sync with `run_modal.py` when image changes happen. The `DEFINITION` constant must be updated for your kernel.

## 8. One-time host setup

```bash
conda create -n fi-bench python=3.12
conda activate fi-bench
pip install flashinfer-bench modal
modal setup
modal volume create flashinfer-trace
modal volume put flashinfer-trace /path/to/flashinfer-trace/
```

The trace set comes from the [MLSys-2026 Contest Dataset](https://huggingface.co/datasets/flashinfer-ai/mlsys26-contest). For a custom kernel, see the FlashInfer-Trace "Bring Your Own Kernel" guide.

## 9. Launching

One iteration:

```bash
claude --dangerously-skip-permissions -p "/optimize"
```

Continuous loop (interactive mode):

```bash
claude --dangerously-skip-permissions
# then: /loop Run /optimize every 15 minutes
```

The loop runs indefinitely. Stop with Ctrl+C when you want to step in.
