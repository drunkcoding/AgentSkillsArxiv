# Proficiency Tracking — Triton Addendum

> Read this AFTER `proficiency-tracking-shared.md`. Adds Triton-flavored examples for templates and the dual-attribution rule.

## Triton-Flavored Dual-Attribution Example

Per `proficiency-tracking-shared.md` Dual-Attribution Rule, a concept that genuinely spans two topics is written in BOTH concept files with the same name plus a `(↔ {other-topic})` suffix:

```
| autotune cache key for matmul shapes (↔ matmul-patterns) | 2 | 1 | 2026-05-15 | 🔴 |
```

This concept appears in both `concepts/tiling-autotuning.md` (autotune is the primary mechanism) and `concepts/matmul-patterns.md` (matmul is where it's used). Both files' badges include this concept; the global `unresolved_total` counts it ONCE.

## Template-Path References

When `proficiency-tracking-shared.md` Edge Cases reference "the parent skill's `SKILL.md`":
- Concept file template → see `triton-tutor/SKILL.md` `## Concept File Template`.
- Dashboard template → see `triton-tutor/SKILL.md` `## Dashboard Template`.

The Triton dashboard initializes all 6 rows with `0/0/-/⬜`, one for each of: Triton Basics, Tiling & Autotuning, Matmul Patterns, Attention & Reductions, Compiler Internals, Ecosystem & Production.
