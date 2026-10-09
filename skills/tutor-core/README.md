# tutor-core

Shared reference container for `cuda-tutor` and `triton-tutor`. Holds workflow rules, proficiency formulas, and the cross-stack CUDA↔Triton Rosetta — symlinked from both consumer skills.

## Why this exists

`cuda-tutor` and `triton-tutor` originally shipped ~70 % duplicated content (quiz rules, proficiency math, dashboard templates). This directory holds the single canonical copy; the two tutors point at it via relative symlinks under their `references/` directories.

## Not a standalone skill

This directory has **no `SKILL.md`** by design — it is **not installable on its own**. The repo's skill installer (`infra/scripts/install-skills.sh`) filters discovery by `[ -f "${dir}SKILL.md" ]`, so `tutor-core/` is silently skipped and never appears in `~/.claude/`.

## Layout

```
tutor-core/
└── references/
    ├── quiz-rules-shared.md              ← stack-agnostic quiz design rules
    ├── proficiency-tracking-shared.md    ← exact proficiency math + edge cases
    └── cross-stack-rosetta.md            ← bidirectional CUDA/CUTLASS/cuTile ↔ Triton mapping
```

## Consumers

- `skills/cuda-tutor/references/{quiz-rules-shared,proficiency-tracking-shared,cross-stack-rosetta}.md` → symlinks to the three files above.
- `skills/triton-tutor/references/{quiz-rules-shared,proficiency-tracking-shared,cross-stack-rosetta}.md` → same.
- `skills/cuda-tutor-setup/references/topic-*.md` (cutlass, cutile, cuda-kernels) → reference the Rosetta via a local `references/cross-stack-rosetta.md` symlink in the `cuda-tutor-setup` skill (which points at the canonical copy above) in their "Cross-Stack Equivalent" appendix. The local symlink keeps the reference resolvable after the installer symlinks the skill directory into `~/.claude/` (where `tutor-core/` itself is absent).
- `skills/triton-tutor-setup/references/topic-*.md` (triton-basics, tiling-autotuning, matmul-patterns, attention-reductions, compiler-internals) → same, via a local `references/cross-stack-rosetta.md` symlink in the `triton-tutor-setup` skill.

## Validation

The Rosetta linter (`infra/scripts/check_rosetta_consistency.sh`) enforces:
- Every mapping-table row has a stable RID and a Source citation.
- Minimum row counts per mapping section.
- Question-seed YAML schema + distribution requirements.
- Topic-appendix RIDs resolve to canonical rows.

Run it pre-commit alongside `./infra/scripts/install-skills.sh validate`.
