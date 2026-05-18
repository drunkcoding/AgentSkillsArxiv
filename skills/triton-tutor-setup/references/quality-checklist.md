# Quality Checklist — Self-Review

Before reporting completion, verify every item in the relevant mode's section. Fix and re-verify if any check fails.

---

## Curriculum Mode

### Topic Coverage
- [ ] All 6 canonical topics present (or only the user-selected subset, per Phase TU1).
- [ ] Folder names use the canonical numbering `01-` ... `06-` and the canonical display names.
- [ ] Each topic folder has: `Overview.md`, `Concepts/`, `Milestones.md`, `Pitfalls.md`, `Resources.md`.

### Per-Topic Concept Notes
- [ ] Every concept ladder entry (Beginner/Intermediate/Advanced/Expert from the topic reference file) maps to ≥1 concept note.
- [ ] Every concept note has YAML frontmatter: `topic`, `concept`, `source`, `backend`, `hardware`, `keywords`.
- [ ] Every concept note has TL;DR, How-it-works, Related Notes.
- [ ] Triton identifiers (`@triton.jit`, `tl.load`, `tl.dot`, `triton.autotune`, `BLOCK_SIZE_M`, `num_warps`, `TTGIR`, `#mma`, etc.) appear verbatim in English regardless of prose language.
- [ ] Comparison tables present where the topic reference file specifies them (e.g., `tl.load` with vs without `other=`, autotune vs heuristics, FA-2 vs FA-3 KV iteration).
- [ ] ASCII diagrams OR Triton code snippets present for tile decomposition / autotune flow / IR pipeline / online softmax.

### Milestones
- [ ] Per topic: ≥3 hands-on milestones with **specific measurable success criteria** (not vague "make it work" — e.g., ">90% cuBLAS throughput", "TTGIR dump contains `#mma` layout").
- [ ] Each milestone has effort estimate and verification command/check.
- [ ] At least one cross-topic exercise in `99-Exercises/` for users who selected ≥2 topics.

### Pitfalls
- [ ] Per topic: ≥5 pitfall entries.
- [ ] Each entry is a `> [!danger]- ...` fold callout with What / Why / Fix / Related.
- [ ] All pitfalls aggregated into `00-Dashboard/Pitfall-Index.md` with topic + severity + link.

### Dashboard
- [ ] `MOC.md` lists all 6 topics with status checkboxes and Overview links.
- [ ] `Prereq-DAG.md` shows the canonical DAG and includes per-edge justification.
- [ ] `Glossary.md` has the cross-topic terms (program, block, tile, `tl.constexpr`, autotune, `num_warps`, `num_stages`, persistent kernel, split-K, online softmax, TTIR/TTGIR, Inductor).
- [ ] `Quick-Reference.md` has the per-GPU dtype × FLOPS table and the env-var cheatsheet.
- [ ] `Pitfall-Index.md` is populated and links to per-topic Pitfalls.

### Tags
- [ ] All tags from the registry only (no ad-hoc tags).
- [ ] Detail/concept tags always co-attach the parent `#topic-*` tag.
- [ ] Tag Index in MOC includes hierarchy rules.

### Interlinking
- [ ] Every `Overview.md` cross-links to its prereq topics and dependent topics per the DAG.
- [ ] Every concept note has populated `## Related Notes`.
- [ ] MOC links to every concept note, milestone note, and pitfall note.
- [ ] Cross-topic exercises in `99-Exercises/` link back to their constituent topics' concept notes.

### Hardware / Backend Targeting
- [ ] Concept notes that are arch-gated carry the appropriate `#sm-*` or `#cdna3` tag and have `hardware:`/`backend:` in frontmatter.
- [ ] Quick-Reference matches the hardware target from TU1 (e.g., emphasize Hopper WGMMA + TMA if target is hopper).
- [ ] Compiler-Internals notes correctly mark which lowering passes are NVIDIA-specific vs AMD-specific.

### CWD Boundary
- [ ] All vault output inside `<CWD>/StudyVault/`.
- [ ] No absolute paths in note content.

---

## Codebase Mode

### Project Coverage
- [ ] Tech stack documented: Triton version, target backends (NVIDIA/AMD/Intel), target archs, build system, key external libs (torch, flash_attn, xformers, fbgemm).
- [ ] Representative kernel traced end-to-end from Python wrapper through autotune to `@triton.jit` body to (optionally) dumped IR.
- [ ] Autotune config space documented per representative kernel.

### Module Completeness
- [ ] Every module has a note with YAML frontmatter (`module`, `path`, `keywords`, `target_backend`).
- [ ] Each module note includes: Purpose, Key Files, Python Wrapper, `@triton.jit` Kernel, Tile Shapes, Autotune Config Space, Dependencies, How to Test.
- [ ] Tests / benchmarks for each module are linked.

### Tags
- [ ] Tags from registry only: `#backend-*`, `#arch-*`, `#kernel-*`, `#tl-*`, `#triton-autotune`.
- [ ] Tag Index in MOC.

### Dashboard
- [ ] MOC: Architecture Overview + Module Map + Kernel Surface + Backend Matrix + Getting Started + Tag Index + Onboarding Path.
- [ ] Getting Started has copy-paste commands that actually install + run the project.
- [ ] Kernel Surface table lists every public `@triton.jit` kernel with module link.

### Exercises
- [ ] ≥5 onboarding exercises per major module covering: code reading, configuration (autotune), debugging (`TRITON_INTERPRET`, `tl.device_print`), IR exploration (dump + read TTGIR), extension.
- [ ] Answers in fold callouts.

### Interlinking
- [ ] Every module note has `## Related Notes`.
- [ ] Python wrapper ↔ `@triton.jit` kernel ↔ autotune config cross-linked.

### CWD Boundary
- [ ] No references to files outside the project directory.
- [ ] All paths in notes relative to project root.

---

## Document Mode

### Source Traceability
- [ ] Every source file's content verified (not filename-based assumption).
- [ ] Source content mapping table built and verified in Phase D1.
- [ ] Every `source_pdf` frontmatter matches verified mapping.
- [ ] PDFs extracted via `pdftotext` CLI, never via `Read` directly on `.pdf`. Notebooks extracted via `jupyter nbconvert --to markdown`.

### Coverage
- [ ] Every topic from Phase D2 checklist has a concept note.
- [ ] If source documents are Triton official docs / FlashAttention papers / PyTorch Inductor docs / OpenAI-Meta Triton blog posts, content is reorganized into the canonical 6-topic structure (NOT the source's TOC).
- [ ] No source topic missing or underrepresented.

### Tags
- [ ] All tags: English kebab-case, from registry only.
- [ ] Tag Index includes hierarchy rules.

### Practice — Active Recall
- [ ] Every topic folder has practice file (≥8 questions).
- [ ] All answers in `> [!answer]- View Answer` fold (or localized).
- [ ] Question type diversity: ≥60% recall, ≥20% application, ≥2 analysis per file.
- [ ] Distractors drawn from realistic Triton confusion sets (see triton-tutor `quiz-rules.md` pools).

### Dashboard
- [ ] MOC, Quick Reference, Pitfall Index present.
- [ ] MOC links to every concept and practice note.

### CWD Boundary
- [ ] No source files accessed outside CWD.
- [ ] No absolute file paths in notes.
