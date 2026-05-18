# Triton Quiz Design Rules

This file aggregates shared and Triton-specific quiz rules. Read in this order:

1. **Shared rules** (apply to ALL tutor questions): see [`quiz-rules-shared.md`](quiz-rules-shared.md).
2. **Triton-specific addenda** (distractor pools, identifier whitelist, examples): see [`quiz-rules-triton.md`](quiz-rules-triton.md).
3. **Cross-stack mapping** (when the session covers Triton Basics, Tiling/Autotuning, Matmul Patterns, Attention/Reductions, or Compiler Internals): see [`cross-stack-rosetta.md`](cross-stack-rosetta.md).

## Precedence

If a Triton-specific rule in (2) contradicts the shared rule in (1), the shared rule wins for workflow/format concerns; Triton-specific addenda only EXTEND, never override, the shared format rules.

The cross-stack file (3) is OPTIONAL for monoglot Triton quizzes but MANDATORY when the active session includes a topic with a CUDA/CUTLASS/cuTile peer, per the Cross-Stack Question Rule in `quiz-rules-shared.md`.
