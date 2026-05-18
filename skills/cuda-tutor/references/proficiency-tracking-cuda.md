# Proficiency Tracking — CUDA Addendum

> Read this AFTER `proficiency-tracking-shared.md`. Adds CUDA-flavored examples for templates and the dual-attribution rule.

## CUDA-Flavored Dual-Attribution Example

Per `proficiency-tracking-shared.md` Dual-Attribution Rule, a concept that genuinely spans two topics is written in BOTH concept files with the same name plus a `(↔ {other-topic})` suffix:

```
| TMA cp.async.bulk in CUTLASS mainloop (↔ cutlass) | 2 | 1 | 2026-05-15 | 🔴 |
```

This concept appears in both `concepts/cuda-kernels.md` (TMA is the primary mechanism) and `concepts/cutlass.md` (CUTLASS mainloop is where it's used). Both files' badges include this concept; the global `unresolved_total` counts it ONCE.

## Template-Path References

When `proficiency-tracking-shared.md` Edge Cases reference "the parent skill's `SKILL.md`":
- Concept file template → see `cuda-tutor/SKILL.md` `## Concept File Template`.
- Dashboard template → see `cuda-tutor/SKILL.md` `## Dashboard Template`.

The CUDA dashboard initializes all 6 rows with `0/0/-/⬜`, one for each of: CUDA Kernels, CUTLASS, cuTile, Open GPU Kernel Modules, NCCL, NVSHMEM.
