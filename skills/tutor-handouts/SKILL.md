---
name: tutor-handouts
description: >
  Generate a university-style course pack (PDF lecture handouts, programming-assignment
  writeups, conceptual problem sets, topic cheatsheets, a capstone project, and a
  one-page syllabus) plus matching graded programming-exercise scaffolds (CUDA / Triton /
  PyTorch starters, a LeetGPU-style autograder harness, and gated solutions for hardest
  exercises) from a `StudyVault/` produced by `cuda-tutor-setup` or `triton-tutor-setup`.
  Visual style modeled on CMU 15-418, Stanford CS149, MIT 6.172, OLCF CUDA Training
  Series, and AlphaGPU LeetGPU challenges. Emits `.tex` + `Makefile`; compiles via
  `latexmk + pdflatex` if available, otherwise gracefully falls back to source-only.
  Use when the user wants to produce printable lecture handouts, programming assignments,
  problem sets, an autograder, or a complete course pack from an existing StudyVault, or
  says things like "make handouts for my StudyVault", "generate the course pack",
  "build programming exercises for CUDA", "/tutor-handouts".
---

# Tutor Handouts — Course Pack Generator

Consumes an existing `StudyVault/` and produces a sibling `Coursepack/` containing
printable lecture handouts, programming assignment writeups, autograded programming
exercises, cheatsheets, a final-project handout, and a one-page syllabus — all using
CMU 15-418 / Stanford CS149 / MIT 6.172-grade typography (LaTeX `article` 11pt,
`lmodern`, `listings`, `fancyhdr`, `booktabs`; no commercial fonts, no Pygments).

## Prerequisite: Existing StudyVault

This skill **requires a pre-built StudyVault** in CWD. Run `cuda-tutor-setup` or
`triton-tutor-setup` first if no `StudyVault/` exists. The skill auto-detects which
stack the vault contains from `00-Dashboard/MOC.md` frontmatter.

> If no `StudyVault/` is found, tell the user:
> "No StudyVault found. Run `cuda-tutor-setup` or `triton-tutor-setup` first to generate one, then re-run this skill."

## CWD Boundary Rule

> **NEVER access files outside CWD.** All vault reads and Coursepack writes MUST stay
> within CWD and its subdirectories. No absolute paths in any emitted file.

## Output Layout (canonical)

```
Coursepack/
├── Makefile                                # Top-level: make all / handouts / exercises / clean
├── README.md                               # Index of every artifact + how to build
├── Syllabus/
│   ├── syllabus.tex                        # One-page course syllabus
│   └── syllabus.pdf                        # (if latexmk available)
├── Handouts/
│   ├── _common/                            # Shared LaTeX assets
│   │   ├── handout.cls                     # H1/H3/H5 base class
│   │   ├── cheatsheet.cls                  # H2 landscape 2-col
│   │   ├── problemset.cls                  # H4 short-answer
│   │   ├── solution.cls                    # E2 instructor variant
│   │   └── commonheader.sty                # Shared typography + palette
│   ├── 01-cuda-kernels/                    # One folder per vault topic
│   │   ├── lecture-handout.tex             # H1 — 4–8 pp
│   │   ├── cheatsheet.tex                  # H2 — 1–2 pp
│   │   ├── problemset.tex                  # H4 — 2–4 pp
│   │   ├── assignment-01-vector-add.tex    # H3 — 8–15 pp (1:1 with E1 folder)
│   │   ├── assignment-02-tiled-matmul.tex
│   │   └── ...
│   ├── 02-cutlass/  ...
│   └── final-project.tex                   # H5 — cross-topic capstone
└── Exercises/
    ├── _harness/                           # Shared autograder
    │   ├── challenge_base.py               # Abstract base class
    │   └── runner.py                       # Discovers and runs all challenges
    ├── 01-cuda-kernels/
    │   ├── 01-vector-add/                  # ★☆☆ Easy
    │   │   ├── README.md                   # 10-section spec, mirrors H3
    │   │   ├── challenge.py                # Reference impl + test cases
    │   │   ├── starter/{starter.cu, starter.triton.py, starter.pytorch.py}
    │   │   ├── reference/{reference.cu, reference.triton.py, reference.pytorch.py}
    │   │   └── Makefile
    │   └── 03-cp-async-pipeline/           # ★★★ Hard — solutions gated
    │       ├── starter/
    │       ├── Solutions/{SOLUTION_KEY.md, reference.cu, ...}
    │       └── Makefile
    └── ...
```

## Skill Flags (optional, parse from user message)

| Flag | Default | Values | Effect |
|---|---|---|---|
| `--scope` | `full` | `full`, `handouts-only`, `exercises-only`, `topic:{slug}`, `minimal` | Limits emission scope. `minimal` = 1 H1 + 1 H3 per topic for fast sanity check |
| `--palette` | `generic-blue` | `generic-blue`, `cmu-red`, `stanford-cardinal`, `mit-cardinal`, `berkeley-blue` | Switches `commonheader.sty` color block |
| `--emit-solutions` | `hard` | `none`, `hard`, `all` | Whether to render E2 solution PDFs into `_instructor/` subdir |
| `--build` | `auto` | `auto`, `force`, `skip` | `auto` = build if `latexmk` present; `force` = fail loudly if missing; `skip` = emit `.tex` only |
| `--frameworks` | `cuda,triton` | comma-list of `cuda`, `triton`, `pytorch` | Which starter/reference variants to emit per exercise |
| `--exercises-per-topic` | `auto` (2–3 based on concept count) | integer 1–5 | Caps exercise count per topic |

## Hard Invariants (non-negotiable)

These have stable IDs used in the quality checklist:

- **INV-1 (CWD boundary)** — All reads/writes stay inside `<CWD>/StudyVault/` and `<CWD>/Coursepack/`. No absolute paths emitted.
- **INV-2 (No commercial fonts)** — `lmodern` only. No Minion Pro, no Adobe fonts.
- **INV-3 (No minted)** — Use `listings`. Avoids Python/Pygments dependency.
- **INV-4 (latexmk optional)** — Skill emits `.tex + Makefile` even without latexmk.
- **INV-5 (Identifier preservation)** — CUDA / Triton identifiers (`cp.async.bulk`, `tl.dot`, `cute::Layout`, `ncclAllReduce`, `nvshmem_quiet`, `tl.program_id`) appear verbatim in English regardless of `{LANG}`.
- **INV-6 (Idempotence)** — Re-running on the same vault produces byte-identical output. Hand-edited `Solutions/SOLUTION_KEY.md` files preserved via generated-at timestamp + user prompt before clobber.
- **INV-7 (Anti-AI-slop)** — Every handout cites named primary sources, uses code blocks for API names, includes concrete numeric examples, banned fluff phrases per `references/content-rules/handout-content-rules.md`.
- **INV-8 (Build verification)** — TH8 MUST `latexmk` every emitted `.tex` if `--build != skip`. Failures are NOT silently swallowed.

## Workflow (phases TH0–TH8)

### Phase TH0: Detect

1. Scan CWD for `StudyVault/`. If missing, tell user to run `*-tutor-setup` first.
2. Read `StudyVault/00-Dashboard/MOC.md` frontmatter → determine taxonomy:
   - `topic: dashboard` + topics include `cuda-kernels` → **CUDA stack**
   - `topic: dashboard` + topics include `triton-basics` → **Triton stack**
   - Other → **generic stack** (use vault's topic slugs as-is)
3. Read `Pitfall-Index.md` to discover available pitfalls per topic.
4. Detect `{LANG}` from user message (prose language). Code/identifiers stay English.
5. Probe toolchain: `latexmk --version` and `pdflatex --version` and `nvcc --version`.

### Phase TH1: Scope

`AskUserQuestion` with these options:

- **Topics**: all topics (default) / per-topic subset
- **Artifact scope**: full bundle (default) / handouts-only / exercises-only / minimal
- **Palette**: generic-blue (default) / cmu-red / stanford-cardinal / mit-cardinal / berkeley-blue
- **Solutions**: gated for ★★★ only (default) / all / none

### Phase TH2: Bootstrap

1. Create `Coursepack/`, `Coursepack/Handouts/_common/`, `Coursepack/Exercises/_harness/`, `Coursepack/Syllabus/`.
2. Copy `references/latex/*.cls` and `references/latex/commonheader.sty` to `Coursepack/Handouts/_common/`.
3. Copy `references/exercise-templates/challenge_base.py` to `Coursepack/Exercises/_harness/`.
4. Copy `references/exercise-templates/runner.template.py` → `Coursepack/Exercises/_harness/runner.py`.
5. Emit `Coursepack/.gitignore` listing `*.aux *.log *.pdf *.fls *.fdb_latexmk *.synctex.gz build/`.

### Phase TH3: Per-topic handouts

For each topic from TH0 (one at a time — drop prior topic from working memory before reading next):

1. Read `StudyVault/{NN-topic}/Overview.md`, `Concepts/*.md`, `Pitfalls.md`, `Milestones.md`.
2. Read `references/content-rules/handout-content-rules.md`.
3. Generate `Coursepack/Handouts/{NN-topic}/lecture-handout.tex` using `handout.cls` with `lecture` option.
4. Generate `cheatsheet.tex` using `cheatsheet.cls`.
5. Generate `problemset.tex` using `problemset.cls` with 6–10 conceptual short-answer problems.

Per-handout content checklist (enforced inline):
- 10-section template (Overview, Background, Task, Starter Code, Correctness, Performance, Submission, Rubric, Writeup, Due) for H3
- 1+ named primary citation per page
- 1+ concrete numeric example per page
- No banned fluff phrases (see `content-rules/handout-content-rules.md`)
- Header `% Generated by tutor-handouts at {ISO8601} — manual edits will be lost on re-run`

### Phase TH4: Programming assignments

1. Read `references/exercise-banks/{cuda|triton}-exercise-bank.md`.
2. For each topic, select 2–3 highest-priority entries that match the topic's concept-tracker contents.
3. Generate H3 `assignment-{N}-{slug}.tex` into `Coursepack/Handouts/{NN-topic}/` using `handout.cls` with `programming` option.
4. Each H3 MUST reference the paired E1 folder by relative path in its Starter Code section.

### Phase TH5: Exercise scaffolds

For each H3 from TH4, emit the matching E1 folder under `Coursepack/Exercises/{NN-topic}/{NN-slug}/`:

1. `README.md` — mirrors H3 sections in compressed form (≤2 lines/section)
2. `challenge.py` — instantiated from `references/exercise-templates/challenge.template.py` with reference_impl + test cases from the exercise bank entry
3. `starter/starter.cu`, `starter/starter.triton.py`, (optional) `starter/starter.pytorch.py` — based on `--frameworks` flag; each MUST compile/import out of the box but not solve; ≥3 numbered `FIXME N: ...` markers per starter
4. `reference/reference.cu`, `reference/reference.triton.py`, (optional) `reference/reference.pytorch.py` — full working solutions (for ★☆☆ and ★★☆)
5. For ★★★ exercises: emit `Solutions/` instead of `reference/`, plus `Solutions/SOLUTION_KEY.md` (1 para insight + 1 para common mistakes)
6. `Makefile` — nvcc-direct build (`make starter`, `make reference`, `make test`, `make bench`, `make clean`)

### Phase TH6: Capstone + syllabus

1. Read `StudyVault/00-Dashboard/Prereq-DAG.md` to identify cross-topic interactions.
2. Generate `Coursepack/Handouts/final-project.tex` (H5) — a multi-topic capstone (e.g., "NCCL-replacement using NVSHMEM" for CUDA; "FlashAttention with custom compiler pass" for Triton).
3. Generate `Coursepack/Syllabus/syllabus.tex` (M1) — one-page table of contents + due-date grid + grading-weight table linking H1–H5.

### Phase TH7: Solutions + orchestrator

1. If `--emit-solutions={hard,all}`: re-render each matching H3 with `\solutionstrue` into `Coursepack/Handouts/{NN-topic}/_instructor/{slug}-solution.tex` using `solution.cls`.
2. Emit `Coursepack/Makefile` (M2) — orchestrator with targets `all`, `handouts`, `syllabus`, `exercises`, `test-exercises`, `clean`.
3. Emit `Coursepack/README.md` (M3) — index of every emitted artifact with relative links + "How to build" section + skill version.

### Phase TH8: Build + self-review

1. If `--build != skip` AND `latexmk` available: `cd Coursepack && make all -k 2>&1 | tee build.log`.
2. Parse `build.log` per-file:
   - **PASS** = exit 0, no `Overfull`/`Underfull`, PDF > 1 KB
   - **WARN** = exit 0 with overfull/underfull or missing refs
   - **FAIL** = non-zero exit or missing PDF
3. Run self-review against `references/quality-checklist.md` (50+ gates).
4. Report results to user in the format documented in `references/handout-workflow.md`.

## Pairing with `cuda-tutor` / `triton-tutor`

After `Coursepack/` is built, tell the user:
> "Course pack built at `./Coursepack/`. Use `cuda-tutor` (or `triton-tutor`) in the same directory to drill the concepts from your StudyVault. Run `cd Coursepack && make test-exercises` to verify the autograder harness."

## Reference Files (lazy-loaded)

| File | Loaded in phase | Purpose |
|---|---|---|
| `references/handout-workflow.md` | TH0–TH8 | Procedural detail of every phase |
| `references/exercise-workflow.md` | TH4–TH5 | E1–E4 emission detail |
| `references/quality-checklist.md` | TH8 | 50+ self-review gates |
| `references/style-guide.md` | TH2, TH3 | Typography + palette swap |
| `references/content-rules/handout-content-rules.md` | TH3, TH4, TH6 | Per-section length budgets + anti-slop rules |
| `references/content-rules/exercise-content-rules.md` | TH5 | FIXME conventions + test-case sizing |
| `references/content-rules/rubric-rubric.md` | TH3, TH4 | How to write a non-vague grading rubric |
| `references/exercise-banks/cuda-exercise-bank.md` | TH4 (CUDA stack only) | 15 CUDA exercise seeds |
| `references/exercise-banks/triton-exercise-bank.md` | TH4 (Triton stack only) | 15 Triton exercise seeds |
| `references/latex/{handout,cheatsheet,problemset,solution}.cls`, `commonheader.sty` | TH2 (copied verbatim to `Coursepack/Handouts/_common/`) | LaTeX document classes |
| `references/exercise-templates/*` | TH2 + TH5 | challenge_base.py, runner, starter/reference/Makefile templates |

## Important Reminders

- READ `references/handout-workflow.md` before starting TH3 for per-phase detail.
- READ `references/content-rules/handout-content-rules.md` before generating ANY handout prose.
- READ `references/content-rules/exercise-content-rules.md` before generating ANY exercise scaffold.
- READ `references/exercise-banks/{stack}-exercise-bank.md` to pick exercises in TH4.
- READ `references/quality-checklist.md` in TH8 before reporting completion.
- ALWAYS emit `Coursepack/.gitignore` to prevent accidental commit of `*.aux *.log build/`.
- NEVER hand-write a `.cls` file — copy verbatim from `references/latex/`.
- NEVER emit absolute paths in any generated file.
- NEVER use `minted`, only `listings`.
- NEVER require commercial fonts; `lmodern` is the only mandatory font.
- For idempotence: every emitted file gets a `% Generated by tutor-handouts at {ISO8601}` header; on re-run, hand-edited `SOLUTION_KEY.md` files trigger a user prompt before clobber.
