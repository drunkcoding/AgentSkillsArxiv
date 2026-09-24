# Handout Workflow — Procedural Detail of Phases TH0–TH8

## Contents

- [TH0: Detect](#th0-detect)
- [TH1: Scope](#th1-scope)
- [TH2: Bootstrap](#th2-bootstrap)
- [TH3: Per-Topic Handouts](#th3-per-topic-handouts)
- [TH4: Programming Assignments](#th4-programming-assignments)
- [TH5: Exercise Scaffolds](#th5-exercise-scaffolds)
- [TH6: Capstone + Syllabus](#th6-capstone--syllabus)
- [TH7: Solutions + Orchestrator](#th7-solutions--orchestrator)
- [TH8: Build + Self-Review](#th8-build--self-review)

## TH0: Detect

### Inputs
- CWD must contain `StudyVault/`. If not, abort with the message in SKILL.md.

### Actions
1. `ls StudyVault/00-Dashboard/` — assert `MOC.md` exists.
2. Parse YAML frontmatter from `MOC.md` to read:
   - `topic: dashboard`
   - `scope: [...]` — the list of topic slugs
   - `target_hardware`, `audience_language`, `focus` (optional)
3. Determine stack:
   - `cuda-kernels` ∈ scope → CUDA stack
   - `triton-basics` ∈ scope → Triton stack
   - Neither → generic stack (use slugs as-is, draw from no exercise bank — only emit H1, H2, H4, H5, M1, M2, M3; no H3 or E1)
4. List `StudyVault/` to enumerate actual topic folders (e.g., `01-CUDA-Kernels/`, `02-CUTLASS/`).
5. Read `StudyVault/00-Dashboard/Pitfall-Index.md` (if present) for cross-topic pitfalls.
6. Probe toolchain availability (Bash):
   - `latexmk --version`
   - `pdflatex --version`
   - `nvcc --version`
   Record which are present; this controls TH8 build behavior.
7. Detect `{LANG}` from the user's most recent message (default: English).

### Outputs
Nothing emitted to disk. Internal state populated.

---

## TH1: Scope

### Actions
Use `AskUserQuestion` with these headers and options:

**Header: "Scope"** — multi-select allowed:
- Full bundle (all topics, all artifact types) — default
- Handouts only (skip Exercises/)
- Exercises only (skip Handouts/)
- Minimal sanity check (1 H1 + 1 H3 per topic)
- Per-topic — follow up with topic checklist

**Header: "Palette"** — single-select:
- generic-blue — default, neutral, no school branding
- cmu-red
- stanford-cardinal
- mit-cardinal
- berkeley-blue

**Header: "Solutions"** — single-select:
- Gated for ★★★ only (default)
- All exercises emit `_instructor/` solution PDFs
- None (no solution rendering)

### Outputs
Internal state. Pass to TH2.

---

## TH2: Bootstrap

### Actions
1. Create directories:
   ```
   Coursepack/
   Coursepack/Handouts/_common/
   Coursepack/Exercises/_harness/
   Coursepack/Syllabus/
   ```
2. Copy from skill bundle:
   - `references/latex/handout.cls` → `Coursepack/Handouts/_common/handout.cls`
   - `references/latex/cheatsheet.cls` → `Coursepack/Handouts/_common/cheatsheet.cls`
   - `references/latex/problemset.cls` → `Coursepack/Handouts/_common/problemset.cls`
   - `references/latex/solution.cls` → `Coursepack/Handouts/_common/solution.cls`
   - `references/latex/commonheader.sty` → `Coursepack/Handouts/_common/commonheader.sty`
   - `references/exercise-templates/challenge_base.py` → `Coursepack/Exercises/_harness/challenge_base.py`
   - `references/exercise-templates/runner.template.py` → `Coursepack/Exercises/_harness/runner.py`
3. Apply the palette: edit `Coursepack/Handouts/_common/commonheader.sty` to set the `\selectedpalette` line to the chosen palette name.
4. Emit `Coursepack/.gitignore`:
   ```
   *.aux
   *.log
   *.out
   *.fls
   *.fdb_latexmk
   *.synctex.gz
   build/
   __pycache__/
   ```

### Verification
- `ls Coursepack/Handouts/_common/` should list 5 files.
- `ls Coursepack/Exercises/_harness/` should list 2 files.

---

## TH3: Per-Topic Handouts

### Per-topic procedure (repeat for each topic, one at a time)

1. **Read** the topic's vault contents:
   - `StudyVault/{NN-topic}/Overview.md`
   - `StudyVault/{NN-topic}/Concepts/*.md`
   - `StudyVault/{NN-topic}/Pitfalls.md`
   - `StudyVault/{NN-topic}/Milestones.md` (if present)
2. **Generate H1** (`lecture-handout.tex`):
   - Class: `\documentclass[lecture]{handout}`
   - Length: 4–8 pages
   - Sections: Overview, Background, Core Concepts (with code listings), Common Pitfalls, Further Reading
   - At least 1 ASCII diagram (memory hierarchy / pipeline / warp layout)
   - At least 1 `lstlisting` per page
   - Cite the StudyVault concept notes by relative path in comments (e.g., `% from StudyVault/01-CUDA-Kernels/Concepts/cp-async.md`)
3. **Generate H2** (`cheatsheet.tex`):
   - Class: `\documentclass{cheatsheet}`
   - Landscape, 2-col, 0.5in margins
   - Sections: Key APIs (table), Quick Reference (numbers), Top Pitfalls (list)
   - Length: 1–2 pages
4. **Generate H4** (`problemset.tex`):
   - Class: `\documentclass{problemset}`
   - 6–10 problems
   - Mix: multiple-choice, short-answer, fill-in
   - Each problem references a specific concept note from the vault

### Per-handout content rules (enforced)
Read `references/content-rules/handout-content-rules.md` before generating. Apply ALL invariants INV-1..INV-8 from SKILL.md.

### Drop topic content from working memory before next topic
Critical for context budget. After emitting all three files for topic N, do NOT keep its concept notes in context when moving to topic N+1.

---

## TH4: Programming Assignments

### Actions
1. **Load exercise bank** matching the stack:
   - CUDA stack → `references/exercise-banks/cuda-exercise-bank.md`
   - Triton stack → `references/exercise-banks/triton-exercise-bank.md`
   - Generic stack → SKIP TH4 and TH5 entirely
2. **Per topic**, select 2–3 entries from the bank where the entry's `Topic:` field matches the current topic slug. Prefer:
   - One ★☆☆ or ★★☆ entry (foundational)
   - One ★★☆ entry (intermediate)
   - One ★★★ entry (capstone for the topic)
3. **For each selected entry**, generate `Coursepack/Handouts/{NN-topic}/assignment-{NN}-{slug}.tex`:
   - Class: `\documentclass[programming]{handout}`
   - Length: 8–15 pages
   - Sections (10 canonical, in order):
     1. Overview (motivation, time estimate)
     2. Background (concepts needed, cite vault notes)
     3. Task (numbered `\taskpart{name}{points}` summing to 100)
     4. Starter Code (file list with relative paths to `../../Exercises/{NN-topic}/{NN-slug}/starter/*`)
     5. Correctness (explicit invariants + anti-invariants)
     6. Performance (reference time on specific GPU + input size)
     7. Submission (file naming convention)
     8. Rubric (booktabs table, points sum to 100)
     9. Writeup (what goes in the report)
     10. Due (date placeholder `\duedate{TBD}`)

### Per-assignment content rules
Read `references/content-rules/handout-content-rules.md` §"H3-specific" rules. Read `references/content-rules/rubric-rubric.md` for rubric construction rules.

---

## TH5: Exercise Scaffolds

For each H3 emitted in TH4, emit the matching E1 folder.

### Folder layout
```
Coursepack/Exercises/{NN-topic}/{NN-slug}/
├── README.md
├── challenge.py
├── starter/
│   ├── starter.cu                # always (if --frameworks includes cuda)
│   ├── starter.triton.py         # always (if --frameworks includes triton)
│   └── starter.pytorch.py        # optional (if --frameworks includes pytorch)
├── reference/                    # for ★☆☆ and ★★☆ ONLY
│   ├── reference.cu
│   ├── reference.triton.py
│   └── reference.pytorch.py
├── Solutions/                    # for ★★★ ONLY (instead of reference/)
│   ├── SOLUTION_KEY.md
│   ├── reference.cu
│   ├── reference.triton.py
│   └── reference.pytorch.py
└── Makefile
```

### Per-file emission rules

**`README.md`** — compressed H3 mirror, ≤2 lines per section. Use `references/exercise-templates/README.template.md`.

**`challenge.py`** — instantiate `references/exercise-templates/challenge.template.py`:
- Subclass `ChallengeBase` (imported from `../../_harness/challenge_base`)
- Fill `metadata` (name, topic, difficulty, atol/rtol, target_frameworks) from the bank entry
- Implement `reference_impl()` (≤30 lines, torch-only)
- Implement `generate_example_test()` (1 tiny case)
- Implement `generate_functional_test()` (3–6 cases per bank entry's `Test sizes`)
- Implement `generate_performance_test()` (1 large case)

**`starter/starter.cu`** — instantiate `references/exercise-templates/starter.cu.template`:
- MUST compile (`nvcc -E starter.cu` exits 0) but not solve
- ≥3 numbered FIXME markers: `// FIXME N: <description>  (see StudyVault/{NN-topic}/Concepts/{concept}.md)`
- Marker count must equal bank entry's `FIXME breakdown:` count

**`starter/starter.triton.py`** — same pattern, ≥3 FIXMEs, must `python -c "import starter"` cleanly.

**`reference/reference.{cu,triton.py}`** — full working solution. For CUDA: must `nvcc -E reference.cu` exit 0. For Triton: must import cleanly.

**`Solutions/SOLUTION_KEY.md`** (★★★ only):
- 1 paragraph: the key algorithmic insight
- 1 paragraph: 3+ common student mistakes with how to recognize each
- 1 line: pointer to the canonical reference (paper, blog, repo+commit)

**`Makefile`** — instantiate `references/exercise-templates/Makefile.template`.

### Per-exercise content rules
Read `references/content-rules/exercise-content-rules.md` before emitting.

---

## TH6: Capstone + Syllabus

### H5 (final-project.tex)
- Class: `\documentclass[capstone]{handout}`
- Length: 6–10 pages
- Stack-specific topic synthesis examples:
  - CUDA stack: "Build an AllReduce replacement using NVSHMEM RMA primitives, achieve ≥80% of NCCL Ring throughput on 8×H100"
  - Triton stack: "Implement FlashAttention-3 in pure Triton with a custom compiler pass for warp specialization"
- Sections: Project Overview, Learning Outcomes, Required Background (links to all 6 H1s), Milestones (4 with due dates), Deliverables (final report + code + benchmark), Grading Rubric (booktabs table, 100 pts), Suggested Reading

### M1 (syllabus.tex)
- Class: `\documentclass[capstone]{handout}` or a dedicated `syllabus` option
- Length: exactly 1 page (use `\thispagestyle{empty}`, dense table layout)
- Contents:
  - Header: course name, term, instructor (placeholder), meeting times (placeholder)
  - Course description (3 sentences synthesized from MOC.md)
  - Topic schedule (booktabs table: week | topic | H1 link | H3 due | weight%)
  - Grading weights (booktabs table summing to 100%)
  - Late policy (placeholder)
  - Academic integrity (placeholder)

---

## TH7: Solutions + Orchestrator

### E2 emission (conditional on `--emit-solutions != none`)

For each H3 to which solutions apply:
1. Read the H3 source.
2. Re-emit as `Coursepack/Handouts/{NN-topic}/_instructor/{slug}-solution.tex`:
   - Replace `\documentclass[programming]{handout}` with `\documentclass[programming]{solution}` (which sets `\solutiontrue`)
   - All `\ifsolution ... \fi` blocks now render
3. The `_instructor/` subdir is what prevents accidental student exposure (gated by directory name + Makefile excludes it from `make handouts`).

### M2 (Coursepack/Makefile)

```makefile
PDFLATEX  ?= latexmk -pdf -interaction=nonstopmode -halt-on-error
TEXFILES  := $(shell find Handouts Syllabus -name '*.tex' -not -path '*/_instructor/*')
PDFFILES  := $(TEXFILES:.tex=.pdf)

INSTRUCTOR_TEX := $(shell find Handouts -name '*.tex' -path '*/_instructor/*')
INSTRUCTOR_PDF := $(INSTRUCTOR_TEX:.tex=.pdf)

all: handouts syllabus

handouts: $(PDFFILES)

instructor: $(INSTRUCTOR_PDF)

%.pdf: %.tex
	@cd $(dir $<) && $(PDFLATEX) $(notdir $<)

syllabus: Syllabus/syllabus.pdf

exercises:
	@find Exercises -name 'Makefile' -not -path '*/_harness/*' \
	  -execdir $(MAKE) starter \;

test-exercises:
	@find Exercises -name 'Makefile' -not -path '*/_harness/*' \
	  -execdir $(MAKE) test \;

clean:
	@find Handouts Syllabus -type f \( -name '*.aux' -o -name '*.log' -o -name '*.out' \
	  -o -name '*.fls' -o -name '*.fdb_latexmk' -o -name '*.synctex.gz' \) -delete
	@find Exercises -type d -name build -exec rm -rf {} +

.PHONY: all handouts instructor syllabus exercises test-exercises clean
```

### M3 (Coursepack/README.md)

Auto-generated index. Sections:
1. **Course Pack Overview** — stack name, topic count, build status
2. **How to Build** — `make all`, `make handouts`, `make instructor`, `make exercises`
3. **Artifact Index** — table of every emitted file with relative link + 1-line description
4. **Toolchain Requirements** — `latexmk`, `pdflatex`, `nvcc` (optional), `python` + `torch`
5. **Generated By** — `tutor-handouts vX.Y` at ISO8601 timestamp

---

## TH8: Build + Self-Review

### Build phase (if `--build != skip` AND `latexmk` available)

```bash
cd Coursepack
make all -k 2>&1 | tee build.log
```

`-k` ensures we get the full picture in one pass.

### Per-file classification

Parse `build.log`:

| Status | Detection |
|---|---|
| **PASS** | latexmk exits 0; no `Overfull \\hbox` or `Underfull \\hbox` in log; PDF file size > 1 KB |
| **WARN** | latexmk exits 0 BUT has overfull/underfull boxes OR missing refs/citations |
| **FAIL** | latexmk exits non-zero OR PDF file missing |
| **SKIP** | `latexmk` not available |

### Self-review (always run)

Run every gate in `references/quality-checklist.md`. Report results.

### Final report format

```
Course pack built at ./Coursepack/

PDF compilation:
  PASS: 32 files
  WARN:  2 files
        - Handouts/05-nccl/assignment-01-ring-allreduce.pdf (1 overfull hbox)
        - Handouts/06-nvshmem/lecture-handout.pdf (missing ref: fig:topology)
  FAIL:  0 files
  SKIP:  0 files

Exercises:
  Emitted: 15 folders across 6 topics
  Compiled (starter.cu): 15/15 nvcc -E ok
  Imported (challenge.py): 15/15 python -c ok

Content checklist (anti-slop):
  Banned-phrase scan: 0 hits
  Citation density: 1.2/page avg (target ≥ 1.0) ✓
  Numeric-example density: 1.4/page avg (target ≥ 1.0) ✓
  Rubric point sums: 18/18 correct ✓

Quality checklist: 47/50 gates passed
  3 gates with warnings — see Coursepack/build.log

Next steps:
  - Open Coursepack/Syllabus/syllabus.pdf for the course overview
  - Run `cd Coursepack && make test-exercises` to run the autograder
  - See Coursepack/README.md for the full artifact index
```

### Failure handling
- If any FAIL: list the file, show the last 20 lines of its latexmk log, ask user whether to retry or abandon.
- If banned-phrase scan returns hits: list the offending file:line:phrase, regenerate that section, re-scan.
- If rubric point sum != 100: identify the assignment, regenerate the rubric, re-verify.

NEVER silently leave a broken `.tex` or a non-compiling exercise.
