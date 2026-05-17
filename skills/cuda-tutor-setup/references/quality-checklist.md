# Quality Checklist — Self-Review

Before reporting completion, verify every item in the relevant mode's section. Fix and re-verify if any check fails.

---

## Curriculum Mode

### Topic Coverage
- [ ] All 6 canonical topics present (or only the user-selected subset, per Phase CU1).
- [ ] Folder names use the canonical numbering `01-` ... `06-` and the canonical display names.
- [ ] Each topic folder has: `Overview.md`, `Concepts/`, `Milestones.md`, `Pitfalls.md`, `Resources.md`.

### Per-Topic Concept Notes
- [ ] Every concept ladder entry (Beginner/Intermediate/Advanced/Expert from the topic reference file) maps to ≥1 concept note.
- [ ] Every concept note has YAML frontmatter: `topic`, `concept`, `source`, `hardware`, `keywords`.
- [ ] Every concept note has TL;DR, How-it-works, Related Notes.
- [ ] CUDA identifiers (`cp.async`, `cute::Layout`, `ncclAllReduce`, `nvshmem_put`, `nvidia.ko`, etc.) appear verbatim in English regardless of prose language.
- [ ] Comparison tables present where the topic reference file specifies them (e.g., `cp.async` vs `cp.async.bulk`, ring vs tree).
- [ ] ASCII diagrams present for memory hierarchy / warp layout / algorithm diagrams.

### Milestones
- [ ] Per topic: ≥3 hands-on milestones with **specific measurable success criteria** (not vague "make it work").
- [ ] Each milestone has effort estimate and verification command/check.
- [ ] At least one cross-topic exercise in `99-Exercises/` for users who selected ≥2 topics.

### Pitfalls
- [ ] Per topic: ≥5 pitfall entries.
- [ ] Each entry is a `> [!danger]- ...` fold callout with What / Why / Fix / Related.
- [ ] All pitfalls aggregated into `00-Dashboard/Pitfall-Index.md` with topic + severity + link.

### Dashboard
- [ ] `MOC.md` lists all 6 topics with status checkboxes and Overview links.
- [ ] `Prereq-DAG.md` shows the canonical DAG and includes per-edge justification.
- [ ] `Glossary.md` has the cross-topic terms (SM, warp, CTA, TMA, WGMMA, PE, symmetric heap, GSP, RM, UVM, NVLS, ring vs tree).
- [ ] `Quick-Reference.md` has the per-GPU spec table.
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

### Hardware Targeting
- [ ] Concept notes that are arch-gated carry the appropriate `#sm-*` tag and have `hardware:` in frontmatter.
- [ ] Quick-Reference matches the hardware target from CU1 (e.g., emphasize Hopper specs if target is hopper).

### CWD Boundary
- [ ] All vault output inside `<CWD>/StudyVault/`.
- [ ] No absolute paths in note content.

---

## Codebase Mode

### Project Coverage
- [ ] Tech stack documented: CUDA toolkit version, target SMs, build system (CMake/setup.py/Make), key external libs (cuBLAS, NCCL, CUTLASS, NVSHMEM).
- [ ] Representative kernel traced end-to-end from host wrapper through device entry to MMA / TMA / `__syncthreads` usage.
- [ ] Memory hierarchy used by the kernel documented (global / shared / register tiling).

### Module Completeness
- [ ] Every module has a note with YAML frontmatter (`module`, `path`, `keywords`).
- [ ] Each module note includes: Purpose, Key Kernels, Host Wrappers, Device Entry, Memory Tiling, Sync Pattern, Dependencies, How to Test.
- [ ] Tests / benchmarks for each module are linked.

### Tags
- [ ] Tags from registry only: `#arch-*`, `#sm-*`, `#kernel-*`, `#api-*`, `#mma-*`.
- [ ] Tag Index in MOC.

### Dashboard
- [ ] MOC: Architecture Overview + Module Map + Kernel Surface + Build Matrix + Getting Started + Tag Index + Onboarding Path.
- [ ] Getting Started has copy-paste commands that actually build the project.
- [ ] Kernel Surface table lists every public kernel/wrapper with module link.

### Exercises
- [ ] ≥5 onboarding exercises per major module covering: code reading, configuration, debugging (`compute-sanitizer` / Nsight Compute), extension.
- [ ] Answers in fold callouts.

### Interlinking
- [ ] Every module note has `## Related Notes`.
- [ ] Host wrapper ↔ device kernel ↔ MMA atom cross-linked.

### CWD Boundary
- [ ] No references to files outside the project directory.
- [ ] All paths in notes relative to project root.

---

## Document Mode

### Source Traceability
- [ ] Every source file's content verified (not filename-based assumption).
- [ ] Source content mapping table built and verified in Phase D1.
- [ ] Every `source_pdf` frontmatter matches verified mapping.
- [ ] PDFs extracted via `pdftotext` CLI, never via `Read` directly on `.pdf`.

### Coverage
- [ ] Every topic from Phase D2 checklist has a concept note.
- [ ] If source documents are NVIDIA programming guides / CUTLASS docs / NCCL guide / NVSHMEM guide, content is reorganized into the canonical 6-topic structure (NOT the source's TOC).
- [ ] No source topic missing or underrepresented.

### Tags
- [ ] All tags: English kebab-case, from registry only.
- [ ] Tag Index includes hierarchy rules.

### Practice — Active Recall
- [ ] Every topic folder has practice file (≥8 questions).
- [ ] All answers in `> [!answer]- View Answer` fold (or localized).
- [ ] Question type diversity: ≥60% recall, ≥20% application, ≥2 analysis per file.
- [ ] Distractors drawn from realistic CUDA confusion sets (see cuda-tutor `quiz-rules.md` pools).

### Dashboard
- [ ] MOC, Quick Reference, Pitfall Index present.
- [ ] MOC links to every concept and practice note.

### CWD Boundary
- [ ] No source files accessed outside CWD.
- [ ] No absolute file paths in notes.
