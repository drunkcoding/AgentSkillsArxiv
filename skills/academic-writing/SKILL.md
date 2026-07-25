---
name: academic-writing
description: "Write conference papers for systems venues (OSDI, NSDI, SIGCOMM, MOBICOM, SOSP, FAST) and the AAAI AI/ML venue. Organized by venue: pick the paradigm (systems problem-solution-evaluation vs. AAAI/AI-ML method-experiment), then follow venue-specific structure, format, citation style, and review rules. Covers paper structure per venue, writing style, IEEE/ACM numbered vs. AAAI author-year citations, figures/tables, AAAI's mandatory reproducibility checklist and double-blind two-phase review, and FAST short/deployed-systems papers. Use when asked to write, draft, structure, or format a systems or AAAI conference paper."
---

# Conference Paper Writing

This skill covers two paper paradigms across two venue families. Start by identifying the target venue, then follow the matching structure and load the matching reference file.

## 1. Choose the Venue and Paradigm (start here)

Two paradigms, because a systems paper and an AAAI paper are organized around fundamentally different things:

| | Systems paradigm | AI/ML paradigm (AAAI) |
|---|---|---|
| **Organized around** | A system that was built, deployed, measured | A method/model/theory and the evidence it works |
| **Structure** | Problem → Design → Implementation → Evaluation | Problem → Method → Analysis → Experiments |
| **Detailed reference** | `references/systems_paper_structure.md` | `references/aaai_paper_structure.md` |

### Master venue table

| Venue | Paradigm | Format / template | Tech. pages | Review | Citations | Reproducibility |
|-------|----------|-------------------|-------------|--------|-----------|-----------------|
| **OSDI** | Systems | USENIX | 12 | Single-blind | Numbered (IEEE) | Artifact: strongly encouraged |
| **NSDI** | Systems | USENIX | 12 | Single-blind | Numbered (IEEE) | Artifact: encouraged |
| **SIGCOMM** | Systems | ACM sigconf | 12 | Double-blind | Numbered (ACM) | Artifact: encouraged |
| **MOBICOM** | Systems | ACM sigconf | 15 | Double-blind | Numbered (ACM) | Artifact: encouraged |
| **SOSP** | Systems | ACM sigconf | 15 | Double-blind | Numbered (ACM) | Artifact: required |
| **FAST** | Systems | USENIX | 12 long / 6 short | Double-blind | Numbered (IEEE) | Artifact: encouraged |
| **AAAI** | AI/ML | AAAI Press two-column (`article` + `aaai<NN>.sty`) | 7 (refs + checklist outside) | Double-blind, two-phase | Author-year (natbib) | Checklist: **mandatory in PDF** |

> Numbers drift each year. Confirm page limits, deadlines, and template names against the current edition's official author kit / Call for Papers before submitting.

**Routing:** for a systems venue → read Section 3 and load `references/systems_paper_structure.md`. For AAAI → read Section 4 and load `references/aaai_paper_structure.md`. Writing craft shared by both (principles, citations, figures) is in Section 5.

---

## 2. The Two Paradigms in One Screen

| Aspect | Systems (OSDI/SIGCOMM/FAST) | AAAI / AI-ML |
|--------|-----------------------------|--------------|
| Core contribution | A built system + its engineering | A method/model/theory + scientific evidence |
| Implementation section | Common, explicit (LOC, frameworks) | Not required; folded into Experimental Setup |
| Related Work placement | After Evaluation | Frequently early (convention) |
| Mathematics | Minimal, practical | Central: objectives, proofs, assumptions |
| Evaluation axes | Throughput, latency, scalability, cost | Accuracy/quality, robustness, sample/compute efficiency, provable properties |
| Length | 12-15 pages | 7 technical pages |
| Reproducibility | Artifact evaluation (badges) | Mandatory reproducibility checklist in the PDF |

Everything downstream — structure, section order, what "evaluation" means, citation style — follows from which column you are in.

---

## 3. Systems Conference Papers (OSDI, NSDI, SIGCOMM, MOBICOM, SOSP, FAST)

Standard structure (problem-solution-evaluation). Design + Evaluation together should be ~50% of the paper.

| Section | Pages | Purpose |
|---------|-------|---------|
| Introduction | 1.5-2 | Problem, solution overview, numbered contributions |
| Background/Motivation | 1-2 | Technical context + **empirical evidence** the problem exists |
| Design | 2-3 | Architecture, mechanisms, trade-offs (explain WHY) |
| Implementation | 0.5-1 | LOC, languages, frameworks, integration |
| Evaluation | 2-3 | Macro/micro-benchmarks, ablation, scaling |
| Related Work | 0.5-1 | Differentiation from prior systems (placed after Evaluation) |
| Conclusion | 0.25-0.5 | Summary, no new information |

**Section highlights:**
- **Title**: "SystemName: Descriptive Subtitle." Name the system.
- **Abstract**: unstructured narrative (150-250 words): problem → gap → solution → key numbers → availability. Write last.
- **Introduction**: 6-7 paragraphs — broad context with numbers, technical gap, solution + key insight, 3-4 numbered contributions mapping to sections.
- **Motivation**: must DEMONSTRATE the problem with measurements/profiling, not assert it.
- **Design**: explain WHY, discuss rejected alternatives, address failure modes.
- **Evaluation**: exact hardware/software/workloads/baselines; every introduction claim must be supported here.
- **Related Work**: after Evaluation; organize by category; always differentiate ("Unlike X, we do Y because Z").

**Venue-specific requirements:**

| Venue | Format | Pages | Review | Artifact |
|-------|--------|-------|--------|----------|
| OSDI | USENIX | 12 | Single-blind | Strongly encouraged |
| NSDI | USENIX | 12 | Single-blind | Encouraged |
| SIGCOMM | ACM sigconf | 12 | Double-blind | Encouraged |
| MOBICOM | ACM sigconf | 15 | Double-blind | Encouraged |
| SOSP | ACM sigconf | 15 | Double-blind | Required |
| FAST | USENIX | 12 / 6 | Double-blind | Encouraged |

**Double-blind systems venues (SIGCOMM, MOBICOM, SOSP, FAST):** anonymize the system name, remove repository URLs, cite own work in third person, remove acknowledgments.

**FAST paper categories:**
- *Short papers (6 pages, excl. references):* complete research with full problem statement and evaluation; prefix title "Short Paper: " at submission; same rigor as long papers on a focused contribution — do not sacrifice evaluation for space.
- *Deployed-systems papers:* operational systems with practical deployment lessons; prefix "Deployed System: "; validate with production data; emphasize operational experience, failure modes, lessons at scale.
- *Supplemental material:* optional single PDF, no page limit; reviewers not required to read it.

For full section-by-section guidance, examples, tense guide, and per-venue variations, load `references/systems_paper_structure.md`.

---

## 4. AAAI (AI / ML) Papers

AAAI follows the **method-experiment** paradigm. Conventional structure (strong convention, not an AAAI compliance rule):

Abstract → Introduction → Related Work → Background/Preliminaries → Method → Theory *(if any)* → Experimental Setup → Results → Ablations → Limitations → Conclusion → References → **Reproducibility Checklist**.

**Hard format rules (enforced strictly — violations risk desk rejection):**
- **7 pages of technical content.** References are outside the limit; the reproducibility checklist is appended after references and also does not count. Any in-paper appendix with proofs/experiments IS technical content and must fit in 7 pages — push overflow to the separately uploaded technical appendix.
- **AAAI Press two-column template, required even for anonymous submission.** LaTeX = `article` class + the edition-specific style package (`\usepackage{aaai2026}`), **not** an `aaai.cls`. Do not add `hyperref`/`navigator`.
- **No page numbers/headers/footers.** Body text black; color only in figures (CMYK, grayscale-safe). **Table captions go BELOW the table.**
- Camera-ready: 7 base pages + up to 2 purchasable extra technical pages.

**Structure implications of the 7-page budget:** background and related work are compressed; Method + Experiments (or Method + Theory) form the bulk; there is **no required standalone Implementation section**; AI/ML papers use substantially more mathematics (objectives, proofs, assumptions) than systems papers.

**Reproducibility checklist (mandatory):** completed by every author at submission, placed in the main PDF after the references, shared with reviewers, and factored into the decision. It covers general clarity, theory (assumptions/proofs), datasets (appropriateness/availability), and computation (seeds, hardware/software versions, number of runs, variance, significance tests, hyperparameters/search ranges). Write the paper so every item can honestly be answered "yes."

**Review process:** double-blind (cite own work in third person; preprints/arXiv allowed but not cited/linked from the anonymous paper); mandatory **abstract registration** ~a week before the paper deadline; **two-phase review** where Phase-1 rejects get no feedback; a single author-feedback/rebuttal window for survivors (AAAI-26: 2,500-char cap, no URLs/files/new results). No dual/concurrent archival submission.

> There is **no separate "CARE" checklist** and **no official fixed reference count** for AAAI — do not invent either.

For full section-by-section guidance, the complete checklist breakdown, appendix mechanics, and the systems↔AAAI contrast, load `references/aaai_paper_structure.md`.

---

## 5. Shared Craft (both paradigms)

### 5.1 Writing principles

- **Clarity**: precise technical language; define terms at first use; active voice ("We design", "We propose", "We evaluate").
- **Conciseness**: strict page limits; every sentence earns its space; ~15-20 word sentences.
- **Directness**: state claims with numbers ("2.3x higher throughput", "+4.1 points accuracy"); avoid hype ("novel", "groundbreaking").
- **Precision**: exact configurations; consistent units and metrics; distinguish observation from interpretation; report variance.

Full guidance, revision checklists, and the systems-vs-ML style comparison: `references/writing_principles.md`.

### 5.2 Citations

- **Systems venues** → numbered citations `[1]`: IEEE (USENIX: OSDI/NSDI/FAST) or ACM (SIGCOMM/MOBICOM/SOSP). Cite systems by name ("Borg [5]").
- **AAAI** → author-year `(Smith 2025)` via `natbib` (`\citet`/`\citep`/`\citeauthor`/`\citeyear`); the AAAI `.sty` sets the matching `.bst`.
- Cite recent work heavily; cite every baseline you compare against; keep self-citation modest and third-person in double-blind submissions.

Full formats, BibTeX, and the numbered↔author-year comparison: `references/citation_styles.md`.

### 5.3 Figures and tables

- **Tables** for exact numbers, configurations, and comparisons; **figures** for trends, distributions (CDFs), scaling, and architecture/method diagrams.
- Self-explanatory captions; error bars on measurements; **bold the best result**; consistent colors; grayscale-safe.
- AAAI-specific: table captions **below** tables; figures ≥300 dpi in `.pdf`/`.png`/`.jpg` (no EPS/GIF), no Type 3 fonts.

Full guidance and per-venue requirements: `references/figures_tables.md`.

### 5.4 Terminology

Use precise subfield terminology. Systems: consistency models, fault tolerance, scheduling, memory hierarchy, RDMA/DPDK/eBPF, parallelism (data/model/pipeline/tensor), TTFT, p50/p99. AI/ML: objective/loss, optimization, generalization, ablation, sample/compute efficiency, seeds/variance, assumptions/propositions/proofs. Define abbreviations at first use; use standard ones (GPU, API, SGD) without definition.

---

## 6. Common Pitfalls

**Both paradigms:**
- Passive voice obscuring who did what; vague quantification ("significant" vs. a number); overstated claims not supported by results; inconsistent terminology; abstract that is a prose table of contents.

**Systems-specific rejection reasons:** not solving a real problem (weak motivation, no evidence); not actually solving it (evaluation doesn't support claims); missing/unfair baselines; unjustified design trade-offs; incomplete related work.

**AAAI-specific pitfalls:** exceeding 7 pages or hiding technical content in "reference" pages; formatting violations (wrong template, added page numbers, `hyperref`); single-seed point estimates without variance/significance; a reproducibility checklist the paper cannot honestly support; de-anonymizing via first-person self-citation or arXiv links.

---

## 7. Workflow

**Systems paper drafting order:**
1. Design + architecture figures → 2. Evaluation + result figures → 3. Introduction → 4. Background/Motivation → 5. Implementation → 6. Related Work → 7. Conclusion → 8. Abstract → 9. Title.

**AAAI paper drafting order:**
1. Method + core equations/pseudocode → 2. Experiments (setup, results, ablations) *or* Theory → 3. Introduction → 4. Related Work + Preliminaries → 5. Limitations + Conclusion → 6. Abstract → 7. Title → 8. Reproducibility checklist (fill as experiments finalize; if an item can't be "yes", fix the paper, not the answer).

**Shared revision + final prep (both):**
1. Verify every introduction/abstract claim is supported by results.
2. Check all figures/tables are referenced and numbers match across text/tables/figures.
3. Ensure consistent terminology and correct citation style for the venue.
4. Format with the exact venue template; check page limit and figure readability (grayscale).
5. Anonymize for double-blind venues (systems double-blind venues and all of AAAI).
6. Systems: prepare the artifact. AAAI: complete the reproducibility checklist and any uploaded appendix.

---

## References

Load the reference that matches your venue and task:

- `references/systems_paper_structure.md`: Full systems paper structure (OSDI/NSDI/SIGCOMM/MOBICOM/SOSP/FAST) — section-by-section content, examples, tense guide, artifact evaluation, per-venue variations.
- `references/aaai_paper_structure.md`: Full AAAI (AI/ML) paper structure — format/length hard rules, section-by-section content, the mandatory reproducibility checklist, double-blind two-phase review, appendix mechanics, and the systems↔AAAI contrast.
- `references/citation_styles.md`: IEEE and ACM numbered styles (systems) and AAAI author-year (natbib), BibTeX management, and anonymization.
- `references/figures_tables.md`: Architecture/method diagrams, performance plots, CDFs, evaluation tables, visual design, and per-venue figure requirements.
- `references/writing_principles.md`: Core writing principles (clarity, conciseness, accuracy), systems-vs-ML style, and revision checklists.
