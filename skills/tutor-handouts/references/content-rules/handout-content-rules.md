# Rules — Handout Content (H1, H3, H4, H5)

Apply these rules to EVERY emitted handout. Violations are blocking; if the
banned-phrase scan in TH8 finds a hit, regenerate the offending section before
reporting completion.

## INV-7 Application

These rules implement invariant **INV-7 (Anti-AI-slop)** from the skill's
SKILL.md. Every rule below has a stable ID (`HCR-N`) referenced by the quality
checklist.

## Universal Rules (apply to H1, H3, H4, H5)

1. **HCR-1 (Title banner)** — Every handout starts with `\maketitle` rendering
   course / handout-number / title / due-date. No generic taglines, no
   motivational subtitles.

2. **HCR-2 (Opening paragraph contract)** — The first paragraph must state:
   (a) what the reader will be able to do after this handout,
   (b) what they need to know first,
   (c) estimated time.
   Banned: motivational openers of the "In today's high-performance computing landscape" form.

3. **HCR-3 (Code-name rule)** — Every API / type / function name appears in
   `\lstinline|...|` or a `lstlisting` block, never in narrative italics. Examples:
   - GOOD: `the \lstinline|cuda::pipeline::producer_acquire| API`
   - BAD: `the producer-acquire functionality`

4. **HCR-4 (Numeric specificity)** — At least 1 specific number per page.
   Examples: SM count, tile size, bandwidth (GB/s), clock (GHz), register
   count, shared-memory bytes, warp size, launch overhead in microseconds.
   Banned: "very large", "extremely fast", "high performance", "significant".

5. **HCR-5 (Primary citation)** — At least 1 named source per page.
   Examples: "CUDA C++ Programming Guide §7.4", "PTX ISA 8.5 §9.7.13.5.10",
   "Triton tutorial 06-fused-attention.py L42–L88", "GitHub
   NVIDIA/cutlass@abc1234 include/cute/atom/copy_atom.hpp".
   Banned: "NVIDIA's documentation", "the official guide", "various sources".

6. **HCR-6 (Banned fluff openers)** — These phrases are forbidden in any prose:
   - "In today's world"
   - "It is important to note"
   - "Note that" (sentence-initial)
   - "Essentially"
   - "Basically"
   - "It's worth mentioning"
   - "Let's dive into"
   - "In conclusion"
   - "As we can see"

7. **HCR-7 (Banned hedges)** — These quantifier-hedges are forbidden:
   - "various"
   - "several" (use the exact number)
   - "many"
   - "some" (use the exact number or a specific example)
   - "may or may not"

   Exception: when the rule file or quality checklist enumerates them in a
   `banned:` block, the words may appear inside that list.

8. **HCR-8 (Lead with claim, then evidence)** — Every paragraph must lead with
   a claim sentence, then supply evidence. Banned: paragraphs that warm up
   with background before stating their point.

## H3-Specific Rules (Programming Assignment)

9. **HCR-9 (10-section template, fixed order)** —
   1. Overview
   2. Background
   3. Task
   4. Starter Code
   5. Correctness
   6. Performance
   7. Submission
   8. Rubric
   9. Writeup
   10. Due

10. **HCR-10 (Task → \taskpart{}{} → 100 pts)** — Task section MUST use
    `\taskpart{name}{points}` for each sub-part; per-part points MUST sum
    exactly to 100.

11. **HCR-11 (Rubric is a table)** — Rubric section MUST be a `booktabs`
    table with explicit row-by-row check criteria and per-row point values
    that sum to 100. Never bulleted prose.

12. **HCR-12 (Starter Code section paths)** — Starter Code section MUST list
    the exact files in the paired E1 folder by relative path
    (e.g., `../../Exercises/01-cuda-kernels/02-tiled-matmul/starter/starter.cu`).
    Every listed file must actually exist after TH5.

13. **HCR-13 (Correctness invariants)** — Correctness section MUST list:
    - At least one explicit invariant the student must maintain (atomicity,
      ordering, determinism, monotonicity, etc.)
    - At least one explicit anti-invariant the student MUST NOT assume
      (e.g., "do NOT assume the grid is launched with a power-of-2 size").

14. **HCR-14 (Performance reference)** — Performance section MUST give a
    reference time on a specific GPU with a specific input size and a specific
    baseline algorithm.
    Example: "Reference: 0.8 ms for N=2^22 on H100 SXM 80GB at sm_90, beating
    a naive 1-thread-per-element baseline by 14×."

## H4-Specific Rules (Problem Set)

15. **HCR-15 (6–10 problems)** — Each problem set MUST contain 6 to 10 problems
    inclusive.

16. **HCR-16 (Each problem cites a concept note)** — Every `\problem{title}`
    MUST include a parenthetical reference to the vault concept note exercised,
    e.g., `\problem{Bank Conflicts} % see StudyVault/01-CUDA-Kernels/Concepts/bank-conflicts.md`.

17. **HCR-17 (Mix problem types)** — Each problem set MUST include at least
    one of: `\mcq{}{}{}{}{}`, at least one `\answerbox{...}`, at least one
    short-answer fill-in.

## H1-Specific Rules (Lecture Handout)

18. **HCR-18 (At least one ASCII diagram per H1)** — Lecture handout must
    include at least one `lstlisting` rendering an ASCII diagram (memory
    hierarchy, pipeline, warp layout, etc.).

19. **HCR-19 (Code listing density)** — At least 1 `lstlisting` block per page.

## H5-Specific Rules (Capstone)

20. **HCR-20 (Cross-topic justification)** — Capstone MUST explicitly name the
    topics it synthesizes and explain why the chosen combination is non-trivial
    (i.e., requires a genuine integration, not just chaining).

21. **HCR-21 (4 milestones with due-date placeholders)** — Capstone must list
    exactly 4 milestones with `\duedate{TBD}` placeholders that the instructor
    can fill in.

## Idempotence Header

Every emitted `.tex` file MUST start with:
```
% Generated by tutor-handouts at <ISO8601> — manual edits will be lost on re-run.
```

## How These Rules Are Enforced

- **At generation time**: the agent re-reads this file before generating each
  handout; treats every rule as a per-section gate.
- **At TH8 build time**: `quality-checklist.md` runs each HCR-N as an explicit
  check; failures are reported per file:line:rule.
