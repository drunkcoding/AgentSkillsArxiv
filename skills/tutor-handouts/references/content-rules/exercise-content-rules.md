# Rules — Exercise Content (E1, E2, E3, E4)

Apply these rules to EVERY emitted programming exercise scaffold under
`Coursepack/Exercises/`.

## INV-5 + INV-6 + INV-7 Application

These rules implement:
- **INV-5 (Identifier preservation)** — CUDA / Triton identifiers verbatim
- **INV-6 (Idempotence)** — Every file gets a generated-at header
- **INV-7 (Anti-AI-slop)** — No fluff, no fake examples

Rule IDs are `ECR-N` and referenced by the quality checklist.

## Universal Rules

1. **ECR-1 (Idempotence header)** — Every emitted file starts with a
   generated-at comment in the file's native comment syntax:
   - `.cu`, `.tex`: `% Generated...` or `// Generated...`
   - `.py`, `Makefile`: `# Generated...`
   - `.md`: `<!-- Generated... -->`

2. **ECR-2 (No banned hedges)** — Same banned hedge list as HCR-7. Especially
   in FIXME comments and SOLUTION_KEY.md content. Banned words:
   `various`, `several`, `many`, `some`, `may or may not`.

3. **ECR-3 (Identifier preservation)** — CUDA / Triton API names verbatim in
   English even when surrounding prose is `{LANG}` ≠ English. Examples that
   must stay English: `cp.async.bulk`, `tl.dot`, `cute::Layout`,
   `ncclAllReduce`, `nvshmem_quiet`, `tl.program_id`, `__syncthreads`,
   `cudaMemcpyAsync`, `triton.autotune`, `num_warps`, `num_stages`.

## README.md Rules

4. **ECR-4 (Compressed mirror)** — `README.md` mirrors the paired H3's
   structure but each section is ≤ 2 lines. It is a roadmap, not a duplicate.

5. **ECR-5 (Cross-link to H3 PDF)** — README MUST link to the paired
   `../../Handouts/{NN-topic}/assignment-{NN}-{slug}.pdf` by relative path.

6. **ECR-6 (Cross-link to vault concepts)** — README's Background section
   MUST list the StudyVault concept notes the exercise exercises, each as a
   `../../StudyVault/{NN-topic}/Concepts/{slug}.md` relative path.

## challenge.py Rules

7. **ECR-7 (reference_impl ≤ 30 lines)** — The `reference_impl` method body
   MUST be ≤ 30 lines (excluding decorators and docstring), pure torch (no
   third-party deps beyond `torch`).

8. **ECR-8 (Test sizes from bank)** — `generate_functional_test()` test sizes
   MUST match the bank entry's `Test sizes:` field exactly. No invented sizes.

9. **ECR-9 (atol/rtol from bank)** — `metadata.atol` and `metadata.rtol` MUST
   match the bank entry's `atol/rtol:` field exactly.

10. **ECR-10 (Defensible tolerances)** — The chosen atol/rtol MUST be
    defensible for the math:
    - FP32 reduction: atol=1e-3, rtol=1e-4
    - FP32 matmul N≤4096: atol=1e-3, rtol=1e-4
    - FP16 matmul: atol=1e-2, rtol=1e-3
    - BF16 matmul: atol=1e-2, rtol=1e-3
    - FP8 matmul: atol=5e-2, rtol=1e-2
    - Integer ops: atol=0, rtol=0

11. **ECR-11 (Performance test size realism)** — `generate_performance_test()`
    size MUST be large enough to amortize launch overhead (≥ 1ms wall time
    for the reference impl). Concrete minimums:
    - Vector ops: N ≥ 2^22
    - Matmul: N ≥ 1024 (each dim)
    - Reduction: N ≥ 2^20
    - Attention: seq_len ≥ 512, head_dim ≥ 64

## starter/starter.{cu,triton.py,pytorch.py} Rules

12. **ECR-12 (Must compile/import)** — Every starter MUST compile/import out
    of the box:
    - `nvcc -E starter.cu` exits 0
    - `python -c "import ast; ast.parse(open('starter.triton.py').read())"`
      exits 0

13. **ECR-13 (Must NOT solve)** — Running the starter MUST produce wrong
    output (or no output if the FIXMEs gate execution). The whole point is
    that the learner must fill in the FIXMEs.

14. **ECR-14 (≥3 numbered FIXMEs)** — Every starter has ≥ 3 numbered FIXME
    markers, one per line:
    ```
    // FIXME 1: <imperative description>
    // FIXME 2: <imperative description>
    // FIXME 3: <imperative description>
    ```

15. **ECR-15 (FIXMEs cite vault concepts)** — Each FIXME line MUST contain
    `(see StudyVault/...)` pointing at a real concept note that explains the
    needed concept.

16. **ECR-16 (Working main() harness)** — Every starter has a working `main()`
    or `__main__` block that runs and prints output, even if the output is
    wrong. The learner must see SOMETHING when they run it.

## reference/reference.{cu,triton.py,pytorch.py} Rules

17. **ECR-17 (Compiles + runs)** — `make reference` succeeds; running the
    reference produces correct output matching `challenge.py::reference_impl()`.

18. **ECR-18 (allclose validated)** — Validated by
    `runner.py --validate-reference` using
    `torch.allclose(reference_output, reference_impl_output,
                    atol=metadata.atol, rtol=metadata.rtol)`.

19. **ECR-19 (No FIXME in reference)** — `grep -c FIXME reference.*` == 0.

20. **ECR-20 (Same I/O signature as starter)** — Reference and starter MUST
    use the same `main()` API so the learner can swap them for verification.

## Solutions/ Rules (★★★ only)

21. **ECR-21 (SOLUTION_KEY.md required)** — Every `Solutions/` directory MUST
    contain `SOLUTION_KEY.md` with:
    - Section "Key Insight" — 1 paragraph on the algorithmic idea
    - Section "Common Student Mistakes" — ≥ 3 numbered mistakes, each with
      symptom + fix
    - Section "Canonical Reference" — ≥ 1 named primary source

22. **ECR-22 (No FIXME in Solutions)** — Same as ECR-19 for the
    `Solutions/reference.*` files.

23. **ECR-23 (Hand-edit protection)** — On re-run of the skill,
    `SOLUTION_KEY.md` files trigger a user prompt before overwrite if mtime is
    newer than the generated-at header timestamp by more than 60 seconds.

## Makefile Rules

24. **ECR-24 (Standard targets)** — Every per-exercise Makefile MUST provide
    targets: `starter`, `reference` (or `solutions`), `test`, `bench`,
    `clean`. All declared `.PHONY`.

25. **ECR-25 (Parameterized ARCH)** — Makefile uses `ARCH ?= -arch=sm_80` as a
    user-overridable default; supports `make ARCH=-arch=sm_90` for H100.

26. **ECR-26 (Out-of-tree builds)** — All build outputs go under
    `./build/`, which is in `.gitignore`. `make clean` removes `./build/`.

## Cross-Cutting

27. **ECR-27 (No absolute paths)** — No emitted file contains an absolute path.
    All paths are relative.

28. **ECR-28 (No school branding in exercises)** — Exercise files (`.cu`,
    `.py`, `.md`) MUST NOT contain school colors, fonts, or branding (those
    live in `_common/`). Exercises are pedagogy-pure.
