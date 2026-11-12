---
name: academic-writing
description: "Use when writing, drafting, structuring, or formatting papers for systems venues (OSDI, NSDI, SIGCOMM, MOBICOM, SOSP, FAST) or AI/ML venues (AAAI, ICML, ICLR, NeurIPS), including venue-specific structure, templates, page limits, citations, reproducibility/checklist requirements, OpenReview mechanics, and reciprocal reviewing."
---

# Conference Paper Writing

This skill covers two paper paradigms across two venue families. Start by identifying the target venue, then follow the matching structure and load the matching reference file.

## Final delivery: humanize the output

**REQUIRED SUB-SKILL (run before returning any draft to the user).** Load the `humanizer` skill (via the skill tool) and run the finished text through it as a final editing pass. It removes AI-writing tells (inflated significance, copula avoidance like "serves as", rule-of-three, overused AI vocabulary such as "delve"/"testament"/"landscape", filler phrases, sycophancy, and em/en-dash overuse) without inventing any fact, name, number, date, or citation. Preserve the format and conventions this skill requires (mandated section headers, citation style, page limits), and if the user supplied a writing sample, pass it so humanizer matches their voice.

**Fallback:** if the `humanizer` / `humanizer-zh` skill is unavailable, deliver the text anyway and tell the user the humanizer pass was skipped.

**If the draft is written in Chinese, load the `humanizer-zh` skill instead of `humanizer`** (via the skill tool) — it applies the same no-fabrication discipline to Chinese prose, targeting 空话铺垫 (empty build-up), 模板化排比 (templated parallelism), over-used connectors (首先/其次/综上所述), and inflated 四字格, while preserving the same format and conventions required above.

## 1. Choose the Venue and Paradigm (start here)

Two paradigms, because a systems paper and an AI/ML paper are organized around fundamentally different things:

| | Systems paradigm | AI/ML paradigm (AAAI, ICML, ICLR, NeurIPS) |
|---|---|---|
| **Organized around** | A system that was built, deployed, measured | A method/model/theory and the evidence it works |
| **Structure** | Problem → Design → Implementation → Evaluation | Problem → Method → Analysis → Experiments |
| **Detailed reference** | `references/systems_paper_structure.md` | `references/aaai_paper_structure.md` (AAAI) / `references/ml_venues_paper_structure.md` (ICML, ICLR, NeurIPS) |

### Master venue table

| Venue | Paradigm | Format / template | Tech. pages | Review | Citations | Reproducibility |
|-------|----------|-------------------|-------------|--------|-----------|-----------------|
| **OSDI** | Systems | USENIX | 12 | Double-blind | Numbered (IEEE) | Artifact: see the call for artifacts |
| **NSDI** | Systems | USENIX | 12 | Double-blind | Numbered (IEEE) | Artifact evaluation: optional, encouraged |
| **SIGCOMM** | Systems | ACM sigconf (template not stated in the CFP text checked; use the one the submission site specifies) | 12 | Double-blind | Numbered (ACM) | Artifact: strongly encouraged |
| **MOBICOM** | Systems | ACM `sigconf,10pt` | 12 incl. figures/tables/all other material (refs unlimited) | Double-blind | Numbered (ACM) | Artifact: strongly encouraged |
| **SOSP** | Systems | ACM `sigplan,10pt` (2026 CFP) | 12 technical (refs not included) | Double-blind | Numbered (ACM) | Artifact evaluation: optional |
| **FAST** | Systems | USENIX | 12 long / 6 short | Double-blind | Numbered (IEEE) | Artifact: optional, accepted papers encouraged |
| **AAAI** | AI/ML | AAAI Press two-column (`article` + `aaai<NN>.sty`) | 7 content (+2 pages refs only; 9-page PDF cap at AAAI-27) | Double-blind, two-phase | Author-year (natbib) | Checklist mandatory: **in PDF through AAAI-26; separate upload at AAAI-27** |
| **ICML** | AI/ML | ICML two-column (`icml<YYYY>.sty`) | 8 (+1 camera-ready; refs/appendix/impact stmt outside) | Double-blind, OpenReview, per-review rebuttal | Author-year (natbib) | **Impact statement mandatory** |
| **ICLR** | AI/ML | ICLR single-column (`iclr<YYYY>` Master-Template) | 9 at submission, 10 at rebuttal/camera-ready (refs/appendix outside) | Double-blind, OpenReview, **public reviews + open discussion** | Author-year (natbib) | Ethics + reproducibility statements recommended |
| **NeurIPS** | AI/ML | NeurIPS single-column edition kit (`neurips_2025.sty` in 2025) | 9 (+1 camera-ready; refs/appendix/checklist outside) | Double-blind, OpenReview, private during review; per-review rebuttal | Author-year or numeric, author's choice, kept internally consistent (natbib loaded by default) | **Paper Checklist mandatory in PDF** |

> Numbers drift each year. Confirm page limits, deadlines, and template names against the current edition's official author kit / Call for Papers before submitting. **If you have no network access,** use the stored values, state which cycle they were verified for (below), and tell the user to confirm them against the live CFP.
>
> Facts last verified 2026-11-12 against the latest official CFPs / author kits available that day (systems: OSDI '27, NSDI '27, SIGCOMM 2026-2027, MobiCom 2026-2027, SOSP 2026, FAST '27; ML: AAAI-27, ICML 2026, ICLR 2026 guide and ICLR 2027 CFP, NeurIPS 2025/2026). Venue rules change every cycle — confirm against the live CFP before relying on any number. Current-cycle items (submission caps, AI-use rules, blind-review changes) are in `references/systems_paper_structure.md` → "Current-cycle requirements".

**Routing:** for a systems venue → read Section 3 and load `references/systems_paper_structure.md`. For AAAI → read Section 4 and load `references/aaai_paper_structure.md`. For ICML, ICLR, or NeurIPS → read Sections 4-4b and load `references/ml_venues_paper_structure.md`. Writing craft shared by both paradigms (principles, citations, figures) is in Section 5.

---

## 2. The Two Paradigms in One Screen

| Aspect | Systems (OSDI/SIGCOMM/FAST) | AI-ML (AAAI/ICML/ICLR/NeurIPS) |
|--------|-----------------------------|------------------------|
| Core contribution | A built system + its engineering | A method/model/theory + scientific evidence |
| Implementation section | Common, explicit (LOC, frameworks) | Not required; folded into Experimental Setup |
| Related Work placement | After Evaluation | Frequently early (convention) |
| Mathematics | Minimal, practical | Central: objectives, proofs, assumptions |
| Evaluation axes | Throughput, latency, scalability, cost | Accuracy/quality, robustness, sample/compute efficiency, provable properties |
| Length | 12 pages of main text (references extra) | 7 (AAAI) / 8 (ICML) / 9-10 (ICLR) / 9+1 camera-ready (NeurIPS) technical pages |
| Reproducibility | Artifact evaluation (badges) | AAAI checklist / ICML impact statement / ICLR reproducibility + ethics statements / NeurIPS Paper Checklist |

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
| OSDI | USENIX | 12 | Double-blind | See the call for artifacts |
| NSDI | USENIX | 12 | Double-blind | Optional, encouraged |
| SIGCOMM | ACM sigconf | 12 | Double-blind | Strongly encouraged |
| MOBICOM | ACM `sigconf,10pt` | 12 (incl. everything except references; appendices after refs don't count) | Double-blind | Strongly encouraged |
| SOSP | ACM `sigplan,10pt` (2026 CFP) | 12 technical (refs not included) | Double-blind | Optional |
| FAST | USENIX | 12 / 6 | Double-blind | Optional, accepted papers encouraged |

**All six systems venues are double-blind (OSDI, NSDI, SIGCOMM, MOBICOM, SOSP, FAST):** anonymize the system name, remove repository URLs, cite own work in third person, remove acknowledgments.

**Edition notes:** the SOSP 2027 CFP was not yet published on 2026-11-12, so SOSP numbers here come from the 2025 and 2026 CFPs. **Current-cycle requirements (verified 2026-11-12)** such as submission caps, AI-use and ethics statements, and rebuttal changes are listed in `references/systems_paper_structure.md`. **Systems venues not in these tables** (ASPLOS, EuroSys, USENIX Security, ATC): the generic systems guidance applies, but every hard number (page limit, blind policy, artifact rules, dates) must come from that venue's own CFP.

**FAST paper categories:**
- *Short papers (6 pages, excl. references):* complete research with full problem statement and evaluation; prefix title "Short Paper: " at submission; same rigor as long papers on a focused contribution — do not sacrifice evaluation for space.
- *Deployed-systems papers:* operational systems with practical deployment lessons; prefix "Deployed System: "; validate with production data; emphasize operational experience, failure modes, lessons at scale.
- *Supplemental material:* optional single PDF, no page limit; reviewers not required to read it.

For full section-by-section guidance, examples, tense guide, and per-venue variations, load `references/systems_paper_structure.md`.

---

## 4. AAAI (AI / ML) Papers

AAAI follows the **method-experiment** paradigm. Conventional structure (strong convention, not an AAAI compliance rule):

Abstract → Introduction → Related Work → Background/Preliminaries → Method → Theory *(if any)* → Experimental Setup → Results → Ablations → Limitations → Conclusion → References → **Reproducibility Checklist** *(in-PDF through AAAI-26; separate form upload at AAAI-27)*.

**Hard format rules (enforced strictly — violations risk desk rejection):**
- **7 pages of technical content.** References are outside the limit; AAAI-27 caps the submission PDF at **9 pages total, pages 8-9 exclusively references**, and counts ethical statements inside the 7 content pages. Any in-paper appendix with proofs/experiments IS technical content and must fit in 7 pages — push overflow to the separately uploaded technical appendix.
- **AAAI Press two-column template, required even for anonymous submission.** LaTeX = `article` class + the edition-specific style package (`\usepackage[submission]{aaai2027}` for an anonymous AAAI-27 submission), **not** an `aaai.cls`. Do not add `hyperref`/`navigator`, and do not load font packages such as `\usepackage{times}` (the AAAI-27 `.sty` loads `newtxtext` itself).
- **No page numbers/headers/footers.** Body text black; color only in figures (CMYK, grayscale-safe). **Table captions go BELOW the table.**
- Camera-ready: 7 base pages + up to 2 purchasable extra technical pages.

**Structure implications of the 7-page budget:** background and related work are compressed; Method + Experiments (or Method + Theory) form the bulk; there is **no required standalone Implementation section**; AI/ML papers use substantially more mathematics (objectives, proofs, assumptions) than systems papers.

**Reproducibility checklist (mandatory):** completed by every author at submission — **AAAI-27: uploaded separately in a designated submission-form field; AAAI-25/26: placed in the main PDF after the references** — shared with reviewers, and factored into the decision. It covers general clarity, theory (assumptions/proofs), datasets (appropriateness/availability), and computation (seeds, hardware/software versions, number of runs, variance, significance tests, hyperparameters/search ranges). Write the paper so every item can honestly be answered "yes." **AAAI-27:** "code/data will be released after acceptance" is explicitly NOT evidence of reproducibility — include materials in the Code and Data Supplement / Supplementary Document at submission.

**Review process:** double-blind (cite own work in third person; preprints/arXiv allowed but not cited/linked from the anonymous paper); mandatory **abstract registration** ~a week before the paper deadline; **two-phase review** where Phase-1 rejects get no feedback; a single author-feedback/rebuttal window for survivors (AAAI-26: 2,500-char cap, no URLs/files/new results; AAAI-27: window was Oct 24-31, 2026 and has closed; its cap has not been published here — check the OpenReview form/instructions). AAAI-27 dates: final notification Nov 30, 2026; camera-ready Dec 14, 2026. No dual/concurrent archival submission; ≤10 submissions per author; AAAI-27 adds a **novelty check across submissions with overlapping authors** (thin-sliced or substantially similar papers may be summarily rejected). **Reciprocal reviewing:** the AAAI-27 instructions say all authors of AAAI-27 submissions are expected to join the reviewer pool unless prevented by extenuating circumstances (no quota stated).

**AAAI-27 LLM / authorship / attendance policy** (per the AAAI-27 author policies page, checked 2026-11-12): text generated by an LLM is prohibited unless it is presented as part of the paper's experimental analysis; using LLMs to edit or polish author-written text is allowed. AI systems cannot be authors and cannot be cited as sources. Authors are fully responsible for content, plagiarism and veracity. At least one author must register at the in-person rate and present the paper in person.

> There is **no separate "CARE" checklist** and **no official fixed reference count** for AAAI — do not invent either.

For full section-by-section guidance, the complete checklist breakdown, appendix mechanics, and the systems↔AAAI contrast, load `references/aaai_paper_structure.md`.

---

## 4b. ICML, ICLR, and NeurIPS (AI / ML) Papers

Use the same **method-experiment** paradigm and section skeleton as AAAI (Section 4), with more page budget and different hard rules. Facts are verified against ICML 2026, ICLR 2026, and NeurIPS 2025/2026 — always re-check the current CFP/Author Guide.

**ICML hard rules:**
- **8 pages main paper** (+1 at camera-ready); unlimited pages for references, the **impact statement**, and appendices, all in a **single PDF**. Optional Supplementary Material (code/data, referenced anonymous papers) may be uploaded at submission with the **same deadline as the paper** (no separate deadline, and none at camera-ready). Two-column `icml<YYYY>.sty`; non-conforming papers rejected without review.
- **Impact Statement mandatory**: broader-impact section co-located with Acknowledgements before References, outside the page limit; official boilerplate sentence allowed for standard cases.
- Abstract deadline ~5 days before paper deadline; **author list frozen at abstract deadline**.
- The ICML 2027 CFP was not yet published on 2026-11-12, so all ICML rules here are from the 2026 cycle.
- **Reciprocal reviewing**: each submission designates a qualified author-reviewer (max 2 submissions per person); authors with 4+ submissions must review. Violations or bad reviews can desk-reject your own papers.
- New for 2026: accepted papers get the submitted version + anonymized reviews + rebuttal **published**; lay summary required at camera-ready; per-review rebuttal on OpenReview (three 5,000-char discussion rounds at ICML 2026).

**ICLR hard rules:**
- **9 pages main text at submission → 10 pages at rebuttal/camera-ready** (strictly enforced; over-limit = desk reject). References + appendices unlimited (reviewers not required to read appendix); supplement due with the paper. **Single-column** `iclr<YYYY>` Master-Template.
- **Reviews are public**; at ICLR 2026 the open discussion ran ~3 weeks (Nov 11 - Dec 3, 2025) with unlimited author comments and **paper revisions allowed** (pdfdiff applied). Plan the 9-page submission so the 10th page can absorb rebuttal-phase results. Treat the rebuttal as an evolving thread.
- **Withdrawal trap**: papers withdrawn after the deadline stay publicly hosted and are **immediately de-anonymized**; all submissions are de-anonymized and released after decisions.
- **Statements** (recommended, outside page limit): Ethics Statement and Reproducibility Statement at the end of main text before references. **LLM-usage section mandatory if LLMs contributed significantly** — nondisclosure risks desk rejection.
- **Reciprocal reviewing**: authors on 3+ papers must review ≥6 papers; each submission needs a registered qualified reviewer-author.
- **ICLR 2027 (CFP checked 2026-11-12):** abstract Sep 18, 2026; paper Sep 25, 2026 (AoE); reviews released and author-reviewer discussion Nov 5-18, 2026; reviewer-AC discussion Nov 19 - Dec 16; final decisions Dec 16, 2026. The 2027 CFP announces new policies on co-authorship, reciprocal reviewing and AI use; the 2027 author guide was not available when this was verified, so the 9/10-page limits and the "3+ papers → review ≥6" rule above are confirmed for ICLR 2026 only.

**NeurIPS hard rules:**
- **9 content pages at submission → 10 at camera-ready**; references, optional technical appendices, and the mandatory checklist do not count. Use one PDF ordered paper → references → optional appendices → checklist. Use the official single-column edition kit (`neurips_2025.sty` in 2025).
- **Paper Checklist mandatory**: keep it last in the PDF; omission risks desk rejection. It does not count toward the limit; justified `no`/`n/a` answers are generally acceptable.
- OpenReview, double-blind, private during review. NeurIPS 2025 used per-review rebuttals (**10,000 characters each**), no files/links/PDF revisions, followed by rolling discussion. Responses may include new results, but the original submission remains the basis for the decision (2025 FAQ, 2026 handbook). Accepted and opted-in rejected records become public after notification.
- Abstract deadline gap: 4 days in 2025, 2 days in 2026; author list freezes at abstract registration. Authors may be asked to review; the 2025 CFP states no numeric reciprocal quota, but negligent reviewer-authors risk access restrictions and desk-rejection sanctions.
- arXiv is allowed without self-citing or advertising the anonymous submission. No concurrent substantially similar archival or cross-track submission. Disclose LLM/agent use when it is an important, original, or non-standard methodological component; ordinary editing need not be declared.
- Route dataset/benchmark work to the separate track/portal: Datasets & Benchmarks in 2025, renamed **Evaluations & Datasets** in 2026.

All three: OpenReview, double-blind, arXiv allowed under venue anonymity rules, and prompt injection forbidden. ICML/ICLR use author-year citations; NeurIPS lets authors choose author-year or numeric as long as they stay consistent (its kit loads plain natbib).

For the full comparison table, per-venue statement/checklist mechanics, OpenReview review-phase details, track notes, and section proportions, load `references/ml_venues_paper_structure.md`.

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
- **ICML / ICLR** → author-year with comma `(Smith, 2025)` via `natbib` (`\citep`/`\citet`); use the `.bst` shipped in the venue style zip.
- **NeurIPS** → the kit loads plain `natbib`; per the kit, citations may be author/year or numeric as long as you stay internally consistent, and any reference style is acceptable if used consistently.
- Cite recent work heavily; cite every baseline you compare against; keep self-citation modest and third-person in double-blind submissions.

Full formats, BibTeX, and the numbered↔author-year comparison: `references/citation_styles.md`.

### 5.3 Figures and tables

- **Tables** for exact numbers, configurations, and comparisons; **figures** for trends, distributions (CDFs), scaling, and architecture/method diagrams.
- Self-explanatory captions; error bars on measurements; **bold the best result**; consistent colors; grayscale-safe.
- AAAI-specific: table captions **below** tables; figures ≥300 dpi in `.pdf`/`.png`/`.jpg` (no EPS/GIF), no Type 3 fonts.

Full guidance (written for systems papers, plus short USENIX/ACM/AAAI notes): `references/figures_tables.md`.

### 5.4 Terminology

Use precise subfield terminology. Systems: consistency models, fault tolerance, scheduling, memory hierarchy, RDMA/DPDK/eBPF, parallelism (data/model/pipeline/tensor), TTFT, p50/p99. AI/ML: objective/loss, optimization, generalization, ablation, sample/compute efficiency, seeds/variance, assumptions/propositions/proofs. Define abbreviations at first use; use standard ones (GPU, API, SGD) without definition.

---

## 6. Common Pitfalls

**Both paradigms:**
- Passive voice obscuring who did what; vague quantification ("significant" vs. a number); overstated claims not supported by results; inconsistent terminology; abstract that is a prose table of contents.

**Systems-specific rejection reasons:** not solving a real problem (weak motivation, no evidence); not actually solving it (evaluation doesn't support claims); missing/unfair baselines; unjustified design trade-offs; incomplete related work.

**AAAI-specific pitfalls:** exceeding 7 pages or hiding technical content in "reference" pages; formatting violations (wrong template, added page numbers, `hyperref`); single-seed point estimates without variance/significance; a reproducibility checklist the paper cannot honestly support; de-anonymizing via first-person self-citation or arXiv links.

**ICML/ICLR/NeurIPS-specific pitfalls:** missing the early abstract-registration deadline or submitting a placeholder abstract; ignoring reviewer-author obligations; ICML: omitting the impact statement or exceeding 8 pages; ICLR: exceeding 9 pages at submission, burying contribution-critical material in the appendix, forgetting that withdrawn papers are published and de-anonymized, or failing to disclose significant LLM usage; NeurIPS: exceeding 9 content pages, removing/misplacing the checklist, treating the appendix as required reading, trying to revise the PDF during rebuttal, or submitting dataset/benchmark work to the wrong track portal.

---

## 7. Workflow

**Systems paper drafting order:**
1. Design + architecture figures → 2. Evaluation + result figures → 3. Introduction → 4. Background/Motivation → 5. Implementation → 6. Related Work → 7. Conclusion → 8. Abstract → 9. Title.

**AI/ML paper drafting order (AAAI, ICML, ICLR, NeurIPS):**
1. Method + core equations/pseudocode → 2. Experiments (setup, results, ablations) *or* Theory → 3. Introduction → 4. Related Work + Preliminaries → 5. Limitations + Conclusion → 6. Abstract → 7. Title → 8. Venue statements: AAAI reproducibility checklist / ICML impact statement / ICLR ethics + reproducibility statements / NeurIPS Paper Checklist. If a checklist item cannot be supported, fix the paper or justify the answer. For ICLR, plan which rebuttal-phase results would fill the 10th page; for NeurIPS, do not plan on rebuttal-phase PDF revisions.

**Shared revision + final prep (both):**
1. Verify every introduction/abstract claim is supported by results.
2. Check all figures/tables are referenced and numbers match across text/tables/figures.
3. Ensure consistent terminology and correct citation style for the venue.
4. Format with the exact venue template; check page limit and figure readability (grayscale).
5. Anonymize for double-blind venues (systems double-blind venues and all AI/ML venues: AAAI, ICML, ICLR, NeurIPS main track).
6. Systems: prepare the artifact. AAAI: complete the reproducibility checklist (separate form upload at AAAI-27; in-PDF through AAAI-26) and any uploaded appendix. ICML: write the impact statement. ICLR: add ethics/reproducibility statements and anonymized code supplement. NeurIPS: complete and place the Paper Checklist last; use the correct main/E&D track portal.

---

## References

Load the reference that matches your venue and task:

- `references/systems_paper_structure.md`: Full systems paper structure (OSDI/NSDI/SIGCOMM/MOBICOM/SOSP/FAST) — section-by-section content, examples, tense guide, artifact evaluation, per-venue variations.
- `references/aaai_paper_structure.md`: Full AAAI (AI/ML) paper structure — format/length hard rules, section-by-section content, the mandatory reproducibility checklist, double-blind two-phase review, appendix mechanics, and the systems↔AAAI contrast.
- `references/ml_venues_paper_structure.md`: ICML, ICLR, and NeurIPS paper rules — page limits and templates, required statements/checklists, OpenReview review mechanics, reciprocal reviewing, dual-submission/arXiv/LLM policies, NeurIPS E&D track routing, and section proportions.
- `references/citation_styles.md`: IEEE and ACM numbered styles (systems), AAAI/ICML/ICLR author-year, and NeurIPS template citations (author-year or numeric), plus BibTeX management and anonymization.
- `references/figures_tables.md`: Figure and table guidance written for systems papers (architecture diagrams, performance plots, CDFs, evaluation tables, visual design), with short per-venue notes for USENIX, ACM and AAAI; for ICML/ICLR/NeurIPS figure rules use `references/ml_venues_paper_structure.md` and the venue's author kit.
- `references/writing_principles.md`: Core writing principles (clarity, conciseness, accuracy), systems-vs-ML style, and revision checklists.
