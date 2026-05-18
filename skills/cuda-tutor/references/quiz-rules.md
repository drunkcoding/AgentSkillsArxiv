# CUDA Quiz Design Rules

This file aggregates shared and CUDA-specific quiz rules. Read in this order:

1. **Shared rules** (apply to ALL tutor questions): see [`quiz-rules-shared.md`](quiz-rules-shared.md).
2. **CUDA-specific addenda** (distractor pools, identifier whitelist, examples): see [`quiz-rules-cuda.md`](quiz-rules-cuda.md).
3. **Cross-stack mapping** (when the session covers CUTLASS, cuTile, or matmul-adjacent CUDA topics): see [`cross-stack-rosetta.md`](cross-stack-rosetta.md).

## Precedence

If a CUDA-specific rule in (2) contradicts the shared rule in (1), the shared rule wins for workflow/format concerns; CUDA-specific addenda only EXTEND, never override, the shared format rules.

The cross-stack file (3) is OPTIONAL for monoglot CUDA quizzes but MANDATORY when the active session includes a topic with a Triton peer (CUDA Kernels with matmul subset, CUTLASS, cuTile), per the Cross-Stack Question Rule in `quiz-rules-shared.md`.
