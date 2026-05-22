---
name: auto-gpu-kernel
description: Scaffold and operate an autonomous Triton GPU-kernel optimization loop on FlashInfer-Bench + Modal, modeled on the MLSys-2026 DSA contest winner (Dogacel/auto-gpu-kernel). Provides a ready-to-run template (CLAUDE.md, .claude/commands/{optimize,benchmark,log-experiment}, .claude/agents/{profiler,research,workload-inspector}, Modal benchmark + paired A/B harness, packed-solution scripts), plus customization guidance for retargeting to a different FlashInfer-Bench kernel definition. Use when the user wants to (1) bootstrap an autonomous Triton-kernel optimizer for any FlashInfer-Bench kernel, (2) set up an experiment-logged optimization loop with sub-agents for profiling, workload inspection, and plateau-breaking research, (3) run cloud-only (no local GPU) GPU benchmarking via Modal B200, or (4) reproduce or adapt the auto-gpu-kernel architecture for FlashInfer competition tracks or similar kernel-optimization workflows.
---

# Auto GPU Kernel

Autonomous Triton kernel optimization loop. Originally won MLSys-2026 DSA track at 34.93x speedup (kernel/loop/sub-agent design from [Dogacel/auto-gpu-kernel](https://github.com/Dogacel/auto-gpu-kernel)).

## What this skill provides

A complete drop-in template (under `assets/template/`) and the workflow knowledge to run + adapt it:

- **`CLAUDE.md`** — non-negotiable rules and kernel I/O contract (per-kernel).
- **`.claude/commands/{optimize,benchmark,log-experiment}.md`** — the three slash commands that drive the loop.
- **`.claude/agents/{profiler,research,workload-inspector}.md`** — three specialist sub-agents that communicate via on-disk artifacts (`experiments/profile.md`, `experiments/workload_profile.md`, `experiments/exp_N/plan.md`).
- **`.claude/settings.json`** — sandbox config allowing Modal network, denying web/pip/git.
- **`scripts/{run_modal,ab_benchmark,pack_solution}.py`** — Modal B200 harness with cupti-accurate timing + paired same-VM A/B harness.
- **`solution/triton/<name>_{fused,baseline}.py`** — kernel + PyTorch reference (per-kernel).
- **`config.toml`** — solution metadata fed to FlashInfer-Bench's packer.

## Quick start

To scaffold a new kernel-optimization project:

```bash
# From this skill's directory:
scripts/scaffold.sh /path/to/new-project \
    --kernel-name <flashinfer-bench-definition> \
    --kernel-file <name>_fused.py
```

Then customize the four kernel-specific surfaces — see [references/customization.md](references/customization.md):

1. `CLAUDE.md` — kernel description, I/O shapes, numerical hazards.
2. `config.toml` — solution name, definition, entry_point.
3. `solution/triton/<name>_baseline.py` — PyTorch reference (read by sub-agents for numerical semantics).
4. `solution/triton/<name>_fused.py` — the kernel under optimization (ships as `NotImplementedError` stub).

Then one-time Modal setup, then launch the loop. Full sequence in [references/customization.md § 8-9](references/customization.md).

## Core loop architecture

```
/optimize  (main loop, one optimization per iteration)
   │
   ├─ Assess (summary.md, LESSONS.md, profile.md, workload_profile.md)
   ├─ Plan ONE change
   ├─ Implement (preserve DPS, stay in Triton/Gluon)
   ├─ Validate  → /benchmark quick   (2 workloads: smallest + largest)
   ├─ Measure   → /benchmark stride 2 (~10 workloads)
   │              └─ sub-5% delta? → ab_benchmark.py (paired same-VM)
   ├─ Log       → /log-experiment    (NEVER skip, even failures)
   └─ Decide    → keep | A/B confirm | revert | pivot

   When stuck (plateau / correctness wall / out of ideas):
       → fire `research` sub-agent (clean context, reads disk only)
       → writes experiments/exp_(N+1)/plan.md
       → next iteration implements that plan
```

Full workflow details in [references/workflow.md](references/workflow.md). Sub-agent contracts in [references/agents.md](references/agents.md).

## Non-negotiable rules (preserved in template)

- **Stay in Triton.** No CUDA, no language switching. Gluon counts as Triton.
- **Absolute latencies only.** Cross-VM reference latency swings 20-30%. Speedup ratios lie.
- **One optimization per iteration.** Coupled changes misattribute wins.
- **No GPU locally.** All compile + benchmark through Modal.
- **Log every experiment** via `/log-experiment`, including failures.
- **No benchmark gaming.** No memoization, no CUDA graphs, no `--quick` shortcuts, no input-pointer caching.
- **Never stop the loop.** Only the user ends optimization.

Full hazards and numerical gotchas (FP8 SOA layout, LSE base-2, tf32x3 fallback, DPS contract, etc.) in [references/hazards.md](references/hazards.md).

## Sub-agent triggers

The optimizer fires `research` when ANY of:

- **Plateau** — 5+ experiments within 5% of each other.
- **Correctness wall** — 3 consecutive correctness failures on different approaches.
- **About to repeat a failure** — `summary.md` shows the attempt already died.
- **Out of ideas on the current axis**.

NOT a trigger: 3 honest micro-wins on the same axis (tile tuning legitimately does this).

`profiler` and `workload-inspector` are called on judgment, not cadence. See [references/agents.md](references/agents.md).

## When to load which reference

- **Setting up a new project** → [references/customization.md](references/customization.md)
- **Modal image, env vars, A/B harness** → [references/modal_setup.md](references/modal_setup.md)
- **The optimize/benchmark/log-experiment loop** → [references/workflow.md](references/workflow.md)
- **Sub-agent contracts and artifact paths** → [references/agents.md](references/agents.md)
- **Triton/FP8/LSE/cupti pitfalls** → [references/hazards.md](references/hazards.md)

## Adapting beyond DSA

The template ships parameterized for DSA sparse attention (`dsa_sparse_attention_h16_ckv512_kpe64_topk2048_ps64`), but the workflow is kernel-agnostic. The winning project also targeted the DSA TopK indexer; both used identical commands and sub-agents with only `CLAUDE.md`, `config.toml`, and `solution/triton/` changed. For non-DSA FlashInfer-Bench definitions, follow the same customization steps.

## Reference report

The technical write-up (architecture, ablations, lessons) ships in the upstream repo as `report.pdf`. The skill does not bundle it — fetch from [Dogacel/auto-gpu-kernel](https://github.com/Dogacel/auto-gpu-kernel) when needed.
