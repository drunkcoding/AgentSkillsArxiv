# Quality Checklist — Self-Review (TH8)

Before reporting completion in TH8, verify every gate below. Each gate
references a rule ID from `content-rules/handout-content-rules.md`
(HCR-N), `content-rules/exercise-content-rules.md` (ECR-N),
`content-rules/rubric-rubric.md` (RR-N), or a skill invariant from
`SKILL.md` (INV-N). Failures must be fixed and re-verified — never reported
as passing.

## Tree Completeness

- [ ] **TC-1** `Coursepack/` exists at CWD root
- [ ] **TC-2** `Coursepack/Handouts/_common/` contains all 5 files: `handout.cls`, `cheatsheet.cls`, `problemset.cls`, `solution.cls`, `commonheader.sty`
- [ ] **TC-3** `Coursepack/Exercises/_harness/` contains `challenge_base.py` and `runner.py`
- [ ] **TC-4** Every topic folder under `Coursepack/Handouts/` has at minimum `lecture-handout.tex`, `cheatsheet.tex`, `problemset.tex`
- [ ] **TC-5** Every H3 `assignment-NN-{slug}.tex` has a paired E1 folder under `Coursepack/Exercises/{NN-topic}/{NN-slug}/`
- [ ] **TC-6** Every E1 folder contains at least `README.md`, `challenge.py`, `starter/`, (`reference/` OR `Solutions/`), `Makefile`
- [ ] **TC-7** `Coursepack/Syllabus/syllabus.tex` exists
- [ ] **TC-8** `Coursepack/Handouts/final-project.tex` exists (H5)
- [ ] **TC-9** `Coursepack/Makefile` (M2) exists
- [ ] **TC-10** `Coursepack/README.md` (M3) exists
- [ ] **TC-11** `Coursepack/.gitignore` exists and lists build artifacts

## LaTeX Hygiene (Run After `make all`)

- [ ] **LH-1** Every `.tex` under `Handouts/` and `Syllabus/` compiles to a PDF with `latexmk -pdf -halt-on-error`
- [ ] **LH-2** PDF file size > 1 KB for every emitted PDF (catches empty docs)
- [ ] **LH-3** No `Undefined control sequence` errors in any `.log`
- [ ] **LH-4** No `Missing $ inserted` errors in any `.log`
- [ ] **LH-5** No more than 2 `Overfull \hbox` warnings per file (cosmetic but fixable)
- [ ] **LH-6** No `Reference ... undefined` warnings (catches broken `\ref`)

## Code Hygiene

- [ ] **CH-1** Every `starter.cu` passes `nvcc -E starter.cu > /dev/null` (preprocessor parse only — does NOT require GPU)
- [ ] **CH-2** Every `starter.triton.py` passes `python -c "import ast; ast.parse(open(P).read())"`
- [ ] **CH-3** Every `challenge.py` passes the same AST parse
- [ ] **CH-4** Every `reference.cu` passes `nvcc -E` (same as CH-1)
- [ ] **CH-5** Every `challenge.py` defines a `Challenge*` subclass of `ChallengeBase`
- [ ] **CH-6** Every `reference.{cu,triton.py}` has 0 occurrences of `FIXME` (ECR-19)

## Content Hygiene — INV-7 Anti-AI-Slop

- [ ] **CHS-1** Banned-phrase scan returns 0 hits across all `.tex` and `.md` files in `Coursepack/`. Banned phrases (HCR-6, HCR-7): `In today's`, `Note that`, `Essentially`, `Basically`, `It's worth mentioning`, `Let's dive into`, `In conclusion`, `As we can see`, `various`, `several `, `many `, `some `, `may or may not`
- [ ] **CHS-2** Citation density ≥ 1.0 per page: count of `\S`, `§`, `arXiv:`, `GitHub`, named-source patterns ≥ page count (HCR-5)
- [ ] **CHS-3** Numeric-example density ≥ 1.0 per page: count of patterns like `\d+ (SM|GB/s|GHz|cycles|threads|bytes|warps|μs|ms)` ≥ page count (HCR-4)
- [ ] **CHS-4** Every `\section` is followed by at least one paragraph that leads with a claim (HCR-8) — sampled spot-check on 3 random sections per file
- [ ] **CHS-5** No emoji in any `.tex` or `.md` file
- [ ] **CHS-6** No `<h3>`-level or deeper sectioning in `.tex` (handouts cap at `\subsection`)

## Handout Structural Rules

- [ ] **HSR-1 (HCR-1)** Every handout `.tex` calls `\maketitle` in its body
- [ ] **HSR-2 (HCR-2)** Every handout's first paragraph names: (a) outcome, (b) prerequisite, (c) time estimate
- [ ] **HSR-3 (HCR-3)** Every API name (`cudaMemcpy`, `tl.dot`, etc.) appears in `\lstinline` or `lstlisting`, never in italics or plain text
- [ ] **HSR-4 (HCR-9)** Every H3 contains all 10 canonical sections in order: Overview, Background, Task, Starter Code, Correctness, Performance, Submission, Rubric, Writeup, Due
- [ ] **HSR-5 (HCR-10)** Every H3's `\taskpart{}{}` per-part points sum exactly to 100
- [ ] **HSR-6 (HCR-12)** Every H3's Starter Code section paths reference files that actually exist in the paired E1 folder
- [ ] **HSR-7 (HCR-13)** Every H3 Correctness section lists ≥1 invariant AND ≥1 anti-invariant
- [ ] **HSR-8 (HCR-14)** Every H3 Performance section names a specific GPU + input size + baseline
- [ ] **HSR-9 (HCR-15)** Every H4 contains 6–10 `\problem{}` invocations
- [ ] **HSR-10 (HCR-17)** Every H4 includes ≥1 `\mcq`, ≥1 `\answerbox`, ≥1 short-answer fill-in
- [ ] **HSR-11 (HCR-18)** Every H1 includes ≥1 ASCII diagram in a `lstlisting`
- [ ] **HSR-12 (HCR-19)** Every H1 has ≥1 `lstlisting` per page
- [ ] **HSR-13 (HCR-20)** H5 capstone names ≥2 topics it synthesizes and justifies the combination
- [ ] **HSR-14 (HCR-21)** H5 capstone lists exactly 4 milestones with `\duedate{TBD}`

## Rubric Quality (RR rules)

- [ ] **RQ-1 (RR-1)** Every rubric row has a concrete mechanical check
- [ ] **RQ-2 (RR-2)** Subjective terms in rubric rows are paired with concrete sub-criteria
- [ ] **RQ-3 (RR-3)** Every rubric's per-row point sum equals 100
- [ ] **RQ-4 (RR-4)** Test-count checks have explicit partial-credit boundaries (no "TA discretion")
- [ ] **RQ-5 (RR-6)** Rubrics are `booktabs` tables, not bulleted lists
- [ ] **RQ-6 (RR-7)** Every rubric table has ≥3 columns including a Check column

## Exercise Quality (ECR rules)

- [ ] **EQ-1 (ECR-1)** Every emitted file starts with a generated-at header in the file's native comment syntax
- [ ] **EQ-2 (ECR-4)** Every `README.md` mirrors the H3 sections in ≤2 lines per section
- [ ] **EQ-3 (ECR-5)** Every `README.md` cross-links to its paired H3 PDF
- [ ] **EQ-4 (ECR-7)** Every `reference_impl` method body is ≤30 lines
- [ ] **EQ-5 (ECR-10)** Every `metadata.atol`/`metadata.rtol` matches the appropriate range for its math type
- [ ] **EQ-6 (ECR-12)** Every starter compiles/imports out of the box (verified by CH-1, CH-2)
- [ ] **EQ-7 (ECR-14)** Every starter has ≥3 numbered `FIXME` markers
- [ ] **EQ-8 (ECR-15)** Every FIXME line contains `(see StudyVault/...)` pointing at a real concept note
- [ ] **EQ-9 (ECR-16)** Every starter has a working `main()` or `__main__` block
- [ ] **EQ-10 (ECR-21)** Every ★★★ exercise's `Solutions/SOLUTION_KEY.md` has 3 sections: Key Insight, Common Student Mistakes (≥3 numbered), Canonical Reference
- [ ] **EQ-11 (ECR-24)** Every per-exercise Makefile declares `starter`, `reference|solutions`, `test`, `bench`, `clean` as `.PHONY`

## Invariant Coverage (INV-1 … INV-8)

- [ ] **INV-1** No absolute paths in any emitted file (`grep -r "/home/\|/Users/\|^/" Coursepack/` returns 0 matches outside `.log` artifacts)
- [ ] **INV-2** No commercial fonts loaded; only `lmodern` family appears in PDF font lists
- [ ] **INV-3** No `minted` usage; only `listings` (`grep -r 'minted' Coursepack/Handouts/*.tex` = 0)
- [ ] **INV-4** Skill emitted `.tex + Makefile` regardless of latexmk availability; build was attempted only if `--build != skip`
- [ ] **INV-5** CUDA / Triton identifiers preserved verbatim in English even when prose is `{LANG}` ≠ English
- [ ] **INV-6** Every file has the `Generated by tutor-handouts at {ISO8601}` header; re-running on unchanged input produces byte-identical output (mod the timestamp itself)
- [ ] **INV-7** All HCR/ECR anti-slop rules pass
- [ ] **INV-8** TH8 build report distinguishes PASS / WARN / FAIL / SKIP per file; failures are NOT silently swallowed

## Reporting Format Compliance

- [ ] **RFC-1** Final report includes: PDF counts (PASS/WARN/FAIL/SKIP), exercise counts (emitted/compiled/imported), content scan results (banned-phrase hits, citation density, numeric-example density, rubric sums), checklist pass count
