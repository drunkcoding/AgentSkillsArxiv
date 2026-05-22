# Sub-agents

Three specialist agents ship in `.claude/agents/`. All communicate with the optimizer via on-disk artifacts — the artifact is the contract, never the nested context response. Customize the `description:` field per kernel if needed, but keep the artifact paths stable so the optimizer loop can find them.

## `profiler` (reactive, on-judgment)

Measures **where time goes** inside the current kernel and names the single biggest bottleneck. Does not write optimizations.

- **When to call**: before committing to a large rewrite, when you don't know which phase dominates. Not on a fixed cadence.
- **Writes**: `experiments/profile.md` (overwrite each run).
- **Method**: `torch.cuda.Event` pairs gated by a project-specific env var (e.g. `DSA_PROFILE=1`). Instrumented kernel lives in a copy under `scripts/` or the experiment folder — never modify the submitted kernel.
- **Reports**: phase breakdown (p50/p90, split small vs large), worst-5 workloads by µs and by µs/unit, observed-vs-memory-floor check, current Triton config (`num_warps`, `num_stages`, `BLOCK_*`).
- **Output rots** after structural changes; re-run then.

## `workload-inspector` (on-hunch)

Characterizes the **input data**, not the kernel — shapes, distributions, padding, locality. Does not run the kernel.

- **When to call**: when you suspect a data-shape angle — "are most workloads batch_size=1?", "what fraction of `(b, h)` have zero weight?", "is `block_table` contiguous?".
- **Writes**: `experiments/workload_profile.md`. Trace set is static, so the file is durable — typically one call is enough. `research` calls it when needed, so you don't have to pre-stage.
- **What to measure**: shape distributions (min/p10/p50/p90/max), intra-batch skew, indirection locality (fraction of consecutive `prev+1` entries, cross-item reuse), padding/sentinel values, value sparsity.
- **Every finding** names the tensor, the statistic, and a concrete kernel-level lever. Vague observations are rejected.

## `research` (clean-context, last resort)

Forms conclusions from disk only — has no knowledge of the optimizer's recent attempts. Writes a plan, not code.

- **When to call**: only when the optimizer is genuinely stuck (see triggers in `workflow.md`).
- **Reads**: `CLAUDE.md`, current kernel + baseline, `experiments/summary.md`, `experiments/LESSONS.md`, `experiments/workload_profile.md` (calls `workload-inspector` first if missing), `experiments/profile.md`, relevant prior `experiments/exp_N/{plan,result}.md`.
- **Diagnose** via the pathology checklist: repetition loop, local minimum, correctness wall, wrong bottleneck, missing fundamental, over-engineering, ignored prior research, buffer persistence, overlooked shortcuts.
- **Judge ceiling, not current** — fresh approach at iter 1 will lose to mature one at iter 20. Recommend pivot when alternative's ceiling > current's.
- **Refine `LESSONS.md`** — remove stale or wrong lessons that are blocking the optimizer.
- **Writes**: `experiments/exp_(N+1)/plan.md` (do NOT write `result.md` or snapshot the kernel — `/log-experiment` fills those in).

### `plan.md` template

```markdown
# Plan — exp (N+1)

## Diagnosis
2-3 sentences. Cite specific experiment numbers.

## Strategy
One of: **pivot** | **refactor** | **targeted fixes**. One sentence on which and why.

## Actions (priority ordered)
1. **What:** specific change (name the function, tile, constant — not "improve memory access").
   **Why:** research finding or architectural reason.
   **Impact:** rough estimate + reasoning.
2. ...

## Do not try
Bullet list of dead ends with exp-number references. Critical for preventing cycles.

## Coordination notes
Quick iterations vs one bigger change? Profile before coding? Read a reference impl first?
```

## Agent invocation

The optimizer launches sub-agents via Claude Code's `Agent` tool:

```
subagent_type: "research"     (or "profiler", "workload-inspector")
```

Prompts to sub-agents should NOT summarize recent attempts — the agent reads from disk for clean-context diagnosis. Just give a one-line trigger ("plateau on tile tuning", "correctness wall on tf32x3").
