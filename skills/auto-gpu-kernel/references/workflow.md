# Optimization loop workflow

The bundled template ships three Claude Code slash commands. Their content lives in `assets/template/.claude/commands/{optimize,benchmark,log-experiment}.md` and is copied verbatim into every scaffolded project.

## `/optimize` — main loop

One iteration:

1. **Assess** — read the kernel under optimization, the baseline reference, `experiments/summary.md`, `experiments/LESSONS.md`. If the highest-numbered `exp_N/` has a `plan.md` but no `result.md`, implement that plan first (folder reservation).
2. **Plan one change** — pick ONE optimization. Progression: PyTorch → tiled Triton → fused → tile tuning → alternative tilings. Study workload distribution; specialize on regime when justified. Fold prologue/epilogue ops; avoid `.contiguous()`.
3. **Implement** — preserve DPS (do not allocate outputs inside the kernel).
4. **Validate** — `/benchmark quick` (2 workloads: smallest + largest).
5. **Measure** — `/benchmark stride 2` (~10 workloads). If reference latency drifts >30% from recent median, re-run. Sub-5% deltas are noise on cross-VM — confirm with `ab_benchmark.py`.
6. **Log** — `/log-experiment` (never skip, even failures).
7. **Decide** — keep / A/B confirm / revert / pivot.

Default per-iteration cost: ~2-3 min on Modal stride 2. Run `full` only on a confirmed new best or every ~5 iterations.

### When stuck

Write a targeted ablation kernel — isolate one phase (e.g. swap `tf32x3` ↔ `ieee`, stub a phase's output, skip a loop). Log it as its own experiment. Add CUDA-event instrumentation gated by an env var (`<PROJECT>_PROFILE=1`) when profiling would resolve the question.

### Sub-agent triggers (`research`)

Fire `research` when ANY:
- **Plateau**: 5+ experiments within 5% of each other.
- **Correctness wall**: 3 consecutive correctness failures on different approaches.
- **About to repeat a failure**: `summary.md` shows the attempt already died.
- **Out of ideas on current axis**.

Not triggers: 3 honest micro-wins in a row on the same axis (tile tuning legitimately does this).

`research` writes `experiments/exp_(N+1)/plan.md`. Optimizer implements it next iteration; `/log-experiment` fills `result.md` into the same folder.

### Gluon migration (last resort)

After ≥15-20 iterations stuck, spin up a fresh sub-agent and rewrite the kernel in Gluon. Re-add features one at a time based on prior experiments. Final solution may be a hybrid: Gluon for one regime, Triton for the rest. Run ≥5-10 Gluon iterations before finalizing.

## `/benchmark <mode>`

| Mode | Command | Purpose |
|---|---|---|
| `quick` | `modal run scripts/run_modal.py --quick` | smallest + largest workload — correctness only |
| `stride N` | `modal run scripts/run_modal.py --stride N` | default iteration (`N=2` → ~10 workloads) |
| `full` | `modal run scripts/run_modal.py` | lock in final numbers (128 workloads, 10-15 min) |

Pipe output to `bench.log` in repo root; `/log-experiment` attaches it. If Modal crash-loops (boot fails repeatedly, not just slow), cancel and diagnose.

Report back: pass/fail counts, absolute kernel latency (min / median / max, split small vs large), max abs/rel error, reference latency.

## `/log-experiment`

1. List `experiments/exp_*/`. Let `N` = highest. If `exp_N/plan.md` exists without `result.md` → use `exp_N/`; else create `exp_(N+1)/`. Never overwrite an existing `result.md`.
2. Copy the kernel file into the folder; copy `bench.log`.
3. Write `result.md` (template below).
4. Append one row to `experiments/summary.md`.

```markdown
# Experiment N — YYYY-MM-DD

**Description:** what changed, why.

## Results
- Pass: X/Y
- Kernel latency (ms): small=S.SSS / large=L.LLL / overall=O.OOO (min / median / max)
- Reference latency (ms): R.RRR
- Max abs err: X.XXe-X  |  Max rel err: X.XXe-X
- Mode: quick | stride N | full  (| ab-vs-exp_K if A/B)

## Learnings
What was learned. What to try or avoid. Append durable insights to `experiments/LESSONS.md`.
```

`summary.md` row:

```markdown
| N | YYYY-MM-DD | one phrase | O.OOO ms | R.RRR ms | X/Y | Δ% vs prior best, "new best" / "regression" / "ablation" |
```

## Folder reservation

If `exp_N/plan.md` exists without `result.md`, that folder is reserved. All new work lands in `exp_N` until either implemented (`result.md` appears) or the plan is marked abandoned by adding `abandoned: <reason>` at the top of `plan.md` — then move to `exp_(N+1)`.
