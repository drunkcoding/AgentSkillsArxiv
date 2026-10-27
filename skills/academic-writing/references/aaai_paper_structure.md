# AAAI Conference Paper Structure (AI / ML Papers)

## Overview

AAAI (the AAAI Conference on Artificial Intelligence) is a top-tier archival venue for artificial intelligence and machine learning research. AAAI main technical track papers follow a **method-experiment** paradigm that is fundamentally different from the **problem-solution-evaluation** paradigm of systems conferences (OSDI, NSDI, SIGCOMM, SOSP, FAST). Where a systems paper is organized around *a system that was built and deployed*, an AAAI paper is organized around *a method (model, algorithm, theory) and the scientific evidence that it works*.

**Conventional AAAI paper structure** (strong convention, NOT an AAAI compliance rule):

1. Abstract
2. Introduction
3. Related Work
4. Background / Preliminaries / Problem Formulation
5. Method / Proposed Approach
6. Theoretical Analysis *(where applicable)*
7. Experimental Setup
8. Results
9. Ablations / Sensitivity / Error Analysis
10. Limitations / Broader Implications *(when relevant)*
11. Conclusion
12. References
13. Reproducibility Checklist *(mandatory; AAAI-25/26: appended after references in the PDF; AAAI-27: uploaded as a separate form field — see Reproducibility Checklist below)*
14. Separately uploaded technical appendix *(optional)*

**Target venue:** AAAI main technical track (this reference). Special tracks (AI for Social Impact, AI Alignment), Student Abstracts, IAAI, EAAI, Doctoral Consortium, and demos are separate programs with distinct page limits, templates, and review criteria — do **not** apply main-track rules to them.

**Typical length:** 7 pages of technical content (references are outside this limit — see Format and Length below).

> **Standards drift every year. Always confirm the exact numbers against the current edition's official author kit and Call for Papers** (e.g. `aaai.org/conference/aaai/aaai-<NN>/submission-instructions/` and the matching `authorkit<NN>` page). The rules below are stable across AAAI-24 through AAAI-27 unless flagged as edition-specific; treat dated fees, deadlines, and reviewer counts as illustrative, not permanent.

### AAAI-27 key facts (verified Oct 2026 against aaai.org)

- **Conference:** February 16-23, 2027, Montréal, Canada. Submission via **OpenReview**; author kit at `aaai.org/authorkit27/` (`aaai2027` style).
- **Timeline (AoE/UTC-12):** abstracts July 21, 2026; full papers July 28, 2026; supplementary material + code July 31, 2026; Phase-1 rejection notification September 24, 2026; **author feedback window October 24-31, 2026** (rescheduled from Oct 19-25); final notification November 30, 2026; camera-ready December 14, 2026.
- **Page limit:** the main submission PDF may have **up to 9 pages total, with pages 8-9 reserved exclusively for references** — i.e. up to 7 pages of non-reference content. Ethical statements, if included, count **inside** the 7 content pages. Acknowledgements are omitted at submission.
- **Reproducibility checklist is NOT in the PDF:** it is **uploaded separately in a designated field of the submission form** and shared with reviewers (change from AAAI-25/26, where it was appended after the references).
- **Reproducibility evidence rule:** reviewers evaluate reproducibility from materials included *at submission*; claims that code/data "will be released after acceptance" must **not** be treated as evidence of reproducibility.
- **Submission cap and novelty check:** ≤10 combined submissions per author to the technical track (excluding AI Alignment and AI for Social Impact special tracks); authors cannot be added after submission; the review process includes a **substantial novelty check across submissions with overlapping authors** — "thin-sliced" or substantially similar papers may be summarily rejected.
- **Contemporaneous work:** papers published less than two months before the July 28, 2026 deadline are contemporaneous; authors are not obliged to address them (encouraged at camera-ready).

## Format and Length Requirements (Hard Rules)

AAAI enforces formatting far more strictly than many venues. Formatting violations can cause desk rejection, so treat this section as a compliance checklist, not style advice.

### Page limit

- **7 pages of technical content** for regular main-track submissions (stable across AAAI-24 through AAAI-27).
- **References do not count** toward the 7 pages — additional pages are allowed *solely* for references. AAAI-27 makes the cap explicit: the submission PDF may have **at most 9 pages total**, with pages 8-9 exclusively for references.
- **Reproducibility checklist placement is edition-specific:** AAAI-25/26 appended it after the references inside the PDF (outside the page limit); **AAAI-27 uploads it separately in a designated submission-form field** — it does not appear in the PDF at all.
- **Any main-paper appendix containing proofs, experiments, methods, or other technical material IS technical content** and must fit within the 7 pages. The exempt pages are for references, not general-purpose appendix material. Push overflow technical material into the *separately uploaded* technical appendix instead. AAAI-27 also states explicitly that **ethical statements count inside the 7 content pages**.
- **Camera-ready:** 7 base technical pages plus **up to 2 purchasable additional technical pages** (fee per page, e.g. \$300/page at AAAI-25/26). Extra pages are not granted automatically.

### Template

- **AAAI Press two-column, camera-ready style is required even for the anonymous review submission.** US Letter (8.5 × 11 in), high-resolution PDF, embedded Type 1 or TrueType fonts.
- **LaTeX:** use the ordinary `article` class with the edition-specific AAAI **style package** (`.sty`) — NOT a document class. There is no current official `aaai.cls`.

  ```latex
  \documentclass[letterpaper]{article}
  \usepackage{aaai2027}   % edition-specific: aaai24.sty / aaai25.sty / aaai2026.sty / aaai2027.sty
  \usepackage{times}
  ```

- **BibTeX:** the AAAI style sets the matching edition-specific `.bst` (`aaai24.bst` / `aaai25.bst` / `aaai2026.bst` / `aaai2027.bst`), which produces an author-year bibliography. Do not manually select an incompatible bibliography style.
- **Word:** official templates exist for anonymous and camera-ready papers. Use the official edition template, not an approximate reproduction.
- **`hyperref` and `navigator` are incompatible with the AAAI style** and can corrupt references — do not add them.

### Typography and layout

- Body text: **10 pt Times Roman or Nimbus, 12 pt leading.** Computer Modern / Palatino are not allowed for body text (Computer Modern is fine for mathematics).
- Two columns ~3.3 in wide; inter-column gutter 0.375 in; left/right margins 0.75 in; bottom margin 1.25 in. Rely on the supplied style rather than setting margins by hand.
- **No page numbers, headers, or footers** — the kit prohibits `\pagestyle`. Do not add review page numbers manually.
- **No manuscript-wide line numbers are required.** Line numbering on algorithm/source listings is optional.
- **Body text must be black**; color is restricted to figures.

### Figures and tables

- Color figures should use **CMYK** (not RGB), maintain **WCAG contrast > 4.5:1**, and remain intelligible in **grayscale** (the archival version may print in grayscale).
- Raster images ≥ **300 dpi**. Accepted formats for pdfLaTeX: `.jpg`, `.png`, `.pdf` — **no EPS, PostScript, or GIF**, and **no Type 3 fonts** (including inside graphics).
- Figure labels ≥ 9 pt; figure captions are 10 pt roman placed **below** the illustration.
- **Table captions go BELOW the table** in AAAI style (a notable difference from many venues that place table captions above). Tables use 10 pt, reducible to 9 pt.
- Figures and tables must not cross the margins or the inter-column gutter.
- References may be reduced to `\small` but not below 9 pt / 10 pt leading.

## Title

- AAAI papers usually describe a **method or contribution**, not a named product. Titles are descriptive of the approach and finding rather than following the systems "SystemName: Subtitle" convention (though a named method/model is common in some subfields).
- Be specific about the technical contribution. Avoid hype words ("novel", "first").
- The submission first page shows title, abstract, and content areas — but **no author names or affiliations** (double-blind).

## Abstract

- **Unstructured narrative paragraph**, typically 150-250 words (confirm the edition's exact guidance).
- Flow: problem / motivation → gap in existing methods → proposed approach and key idea → main empirical or theoretical result → (optional) significance.
- Include the concrete result (e.g., accuracy/metric improvement, or the theoretical guarantee obtained). Write it last.
- Do not cite references in the abstract.

## Introduction

**Length:** ~1 page (of 7). Because the paper is short, the introduction is dense.

Typical flow (4-6 paragraphs):

1. **Context and importance** of the problem, with a concrete framing of why it matters for AI/ML.
2. **The specific technical gap** — what current methods cannot do, or do poorly, and why.
3. **The proposed approach and key insight** — one paragraph mental model of the method.
4. **Contributions** — a numbered or bulleted list (commonly 2-4). For AI/ML these are typically: a new method/formulation, a theoretical result or analysis, and empirical findings on benchmarks.
5. *(Optional)* a brief note on results or organization.

Voice: active ("We propose", "We show", "We prove"), direct, no hype. Let quantitative results and guarantees speak.

## Related Work

**Placement:** AAAI/AI-ML papers **frequently place Related Work early** (right after the Introduction), unlike systems papers which place it after evaluation. This is a strong convention, not an AAAI rule — placement late (before Conclusion) is also acceptable, especially for theory-heavy papers.

- Organize by **approach/theme**, not chronologically.
- **Differentiate**, don't just summarize: state precisely how the proposed method differs from and improves on each line of prior work.
- Kept compact because of the 7-page budget.
- In double-blind submission, cite your own prior work in the **third person** (see Review Process).

## Background / Preliminaries / Problem Formulation

**Purpose:** give the reader the definitions, notation, and formal problem statement needed to understand the method.

- Define the learning/inference setting formally: inputs, outputs, objective, assumptions.
- Introduce notation once, consistently.
- State the **formal problem** the method solves (e.g., an optimization objective, a decision problem, a learning task with a loss).
- Keep it tight — every definition should be used later.

## Method / Proposed Approach

**This is the intellectual core and gets the most space.**

For a method-centric paper, cover:

- **Formal problem statement** and the model/algorithm being proposed.
- **Objective functions**, and the **training / inference / optimization procedure** (pseudocode or numbered steps where it adds clarity).
- **Why the method works** — the key insight, and intuition for each design choice. Explain WHY, not just WHAT, exactly as in a good systems design section.
- Complexity or resource characteristics where relevant.

AI/ML papers use **substantially more mathematics** than systems papers: objectives, derivations, assumptions, and propositions are expected. Use math for precision, not decoration, and define every symbol.

## Theoretical Analysis (where applicable)

For theory contributions:

- State **assumptions and restrictions** explicitly.
- Give **formal statements** of novel claims (definitions, lemmas, theorems, propositions).
- Provide **proofs** in the main text where space allows, or **proof sketches / intuition** in the main text with full proofs in the technical appendix.
- Cite the theoretical tools you build on.
- Where possible, add an **empirical demonstration** consistent with the theory.

## Experimental Setup

**Purpose:** make the empirical claims reproducible and fair.

Report:

- **Datasets** (with citations, and justification of why they are appropriate). Newly introduced datasets go in a data appendix.
- **Baselines** — the methods you compare against, and how they were tuned (equal tuning budget / compute parity is expected).
- **Metrics** — what is measured and *why those metrics*.
- **Implementation / training details** — architecture, hyperparameters, optimizer, and search ranges; hardware and software (versions).
- **Protocol** — number of runs, random seeds, and how variance is reported.

AAAI does **not** require a standalone "Implementation" section (unlike systems papers); these details usually live in Experimental Setup.

## Results, Ablations, and Analysis

- **Main results** — the headline comparison(s) supporting the central claims. Report **mean ± variance over multiple seeds**, not single point estimates, and include statistical significance where appropriate (the reproducibility checklist asks for this).
- **Ablations** — remove or vary each component to show it is necessary and to isolate *why* the method works.
- **Sensitivity / error analysis** — robustness to hyperparameters, failure cases, qualitative examples.
- Explain WHY results look the way they do; acknowledge where baselines win.
- For AI/ML the dominant evaluation axes are **predictive quality, correctness, learning behavior, robustness, sample/compute efficiency, and (for theory) provable properties** — not end-to-end systems throughput/latency.

## Limitations and Conclusion

- A short **Limitations** paragraph (increasingly expected; some tracks require it) — state honestly what the method does not address.
- **Conclusion**: brief summary of the contribution and main result. 1-2 short paragraphs, no new claims.

## Reproducibility Checklist (Mandatory)

AAAI requires **every** author to complete the reproducibility checklist at submission (AAAI-24 through AAAI-27).

**Mechanics — edition-specific, do not mix them up:**

- **AAAI-27:** complete the checklist from the AAAI-27 Author Kit and **upload it separately from the main paper in the designated field of the submission form** at paper-submission time. It does not appear in the PDF. The completed checklist is made available to reviewers.
- **AAAI-25/26:** the answers went **in the main submission PDF, after the references** (outside the 7-page limit); no separate form.
- In all recent editions it is shared with reviewers, and the reproducibility assessment **contributes to the final decision**.
- **AAAI-27 evidence rule:** reviewers evaluate reproducibility only from materials included at submission (main paper, Code and Data Supplement, Supplementary Document). "Code/data will be released after acceptance" must **not** be treated as evidence — reviewers are told to assume such materials will not be made available. Address each reproducibility criterion in the Supplementary Document when relevant.
- A missing checklist generally cannot be newly uploaded during rebuttal — answer reproducibility concerns in the response, and the full checklist is collected at camera-ready for accepted papers.

**What it covers (four groups):**

| Group | Focus |
|-------|-------|
| **A. General** | Conceptual outline / pseudocode for introduced methods; separating results from speculation; pedagogical references |
| **B. Theory** | Assumptions/restrictions; formal statements; proofs; proof sketches; citations to tools; empirical support |
| **C. Datasets** | Why datasets are appropriate; new datasets in a data appendix; release plans and licensing; citations/availability for existing data |
| **D. Computation** | Preprocessing and experiment code; release plans; seeds; hardware/OS/memory/library versions; metrics and rationale; number of runs; variance/uncertainty; significance tests; final hyperparameters and search ranges |

Answers use variants of **yes / partial / no / N/A**, with optional explanation in a "Reproducibility Checklist" section at the end of the technical appendix. Writing the paper so that every checklist item can honestly be answered "yes" is one of the highest-leverage things an author can do for acceptance.

## Review Process

### Double-blind, anonymized submission

- AAAI is **double-blind** (not single-blind). The first page must NOT contain author names or affiliations; funding/assistance acknowledgements are omitted from the submission. Identifying information can cause summary rejection.
- **Cite your own published work in the third person** — "Hinton et al. (2006) showed…", never "in our previous work, we…". Do not remove relevant published self-work just because it is yours (that distorts the related-work assessment); if a citation would unmistakably de-anonymize and is not needed for review, use a suppressed form (e.g. "Anonymous (2019)").
- **Preprints (including arXiv), personal-site/social posts, non-archival workshop versions, and talks are allowed.** The constraint is only that the anonymous AAAI paper must not cite/link the non-anonymous version, and the online version must not announce it was submitted to that AAAI edition.

### Two-phase review and abstract registration

- **Mandatory abstract registration** roughly a week before the paper deadline. Placeholder titles/abstracts are deleted (blocking later full-paper submission), and substantial abstract changes before the paper deadline can trigger rejection.
- **Two-phase review:** Phase-1 papers with sufficiently negative reviews can be **rejected without an author-feedback opportunity**. Surviving papers get additional reviewers and a **single author-feedback (rebuttal) window** covering all reviews.
- **Rebuttal (AAAI-26 specifics):** one response, **max 2,500 characters**, markdown allowed, **no URLs, no code, no additional files, no new experimental results**, and no updating of supplementary material. **AAAI-27 has not published a rebuttal FAQ at the AAAI-26 URL** — its author feedback window is October 24-31, 2026; confirm the character cap and content rules on the live OpenReview form rather than assuming the AAAI-26 numbers.
- Recent editions submit via **OpenReview** (AAAI-25/26/27; AAAI-24 used CMT).

## Supplementary Material and Appendix

Authors may submit, separately from the paper:

1. A **technical appendix PDF** (extended proofs, additional experiments, detailed configs).
2. A **multimedia appendix ZIP**.
3. A **code-and-data ZIP**.

Rules across editions:

- The main paper must remain **self-contained**; essential proof ideas and contribution-critical evidence stay in the 7-page paper.
- Reviewers are **not obligated** to read the supplement.
- Supplementary content must be **anonymized**.
- Do **not** substitute a mutable web page or repository URL for the officially uploaded supplement.
- The supplement typically has its own deadline a few days after the paper deadline.

## Ethics and Dual-Submission Policy

- **No concurrent archival submission:** the work cannot be already published/accepted at, or simultaneously under review at, another archival conference or journal. Workshops and preprint servers (arXiv) are fine. Withdrawing from another venue is allowed if completed **before** the AAAI submission.
- After submitting to AAAI, do not submit the same work elsewhere until an AAAI decision or withdrawal. Non-identical submissions with excessive technical overlap can still violate policy.
- **AAAI-27 overlapping-submission novelty check:** submissions involving overlapping author sets are assessed together for novelty. Prohibited patterns include resubmitting with cosmetic changes, "thin slicing" one contribution into several minimally different papers, splitting results across methods/datasets/domains that belong in one paper, and obfuscated duplicates. Violations are **summarily rejected** (final), and the other venue may be informed.
- Authors must follow the **AAAI Publications Ethics and Malpractice Statement** and the **AAAI Code of Professional Conduct**. Responsible-research issues (human participants, sensitive data, data/algorithmic bias) are review considerations.

> There is **no separately branded "CARE" checklist** in the verified AAAI-24 through AAAI-27 main-track requirements. The mandatory items are the reproducibility checklist plus the ethics/conduct statements above. If a future edition introduces a new form, add it only from a primary AAAI source.

## Citation Style

AAAI uses **author-year citations**, not the numbered IEEE/ACM style of systems venues. Examples: `(Newell 1980)`, `(Feigenbaum and Engelmore 1988)`, `(Ford et al. 1997)`.

LaTeX (via `natbib`, loaded by the AAAI style):

```latex
\cite{smith2025}        % (Smith 2025)  — parenthetical author-year
\citep{smith2025}       % (Smith 2025)
\citet{smith2025}       % Smith (2025)  — textual
\citeauthor{smith2025}  % Smith
\citeyear{smith2025}    % 2025
\shortcite{smith2025}   % (2025)  — year only
```

Do not add `natbib` options that alter the AAAI style. There is **no official "typical reference count"** — reference count is topic-dependent; do not present a fixed number as a venue standard. See `citation_styles.md` for the full author-year vs numbered comparison.

## Section Length Proportions (7-page paper)

Indicative allocation — theory-heavy and empirics-heavy papers differ substantially:

| Section | Approx. space |
|---------|---------------|
| Introduction | ~1 page |
| Related Work | 0.5-1 page |
| Background / Preliminaries | 0.5-1 page |
| Method / Approach | 2-2.5 pages |
| Theory *(if applicable)* | 0.5-1.5 pages |
| Experiments (setup + results + ablations) | 2-2.5 pages |
| Limitations + Conclusion | ~0.5 page |

Method plus Experiments (or Method plus Theory) form the bulk of the paper.

## Writing Order (Recommended)

1. **Method / Approach** + core equations/pseudocode (the contribution)
2. **Experiments** (setup, results, ablations) — or **Theory** for a theory paper
3. **Introduction** (now the full story is known)
4. **Related Work** and **Background / Preliminaries**
5. **Limitations** and **Conclusion**
6. **Abstract** (compress the whole story)
7. **Title**
8. **Reproducibility checklist** — fill it as you finalize experiments; if an item cannot be "yes", fix the paper, not the answer

## Systems Paper vs AAAI/AI-ML Paper (Contrast)

| Aspect | Systems (OSDI/SIGCOMM/FAST) | AAAI / AI-ML |
|--------|-----------------------------|--------------|
| **Organizing paradigm** | Problem → design → implementation → evaluation | Problem formulation → method/model → analysis → experiments |
| **Core contribution** | A built system and its engineering | A method/model/theory and its scientific evidence |
| **Implementation section** | Common, explicit (LOC, frameworks) | Not required; details live in Experimental Setup |
| **Related Work placement** | After evaluation | Frequently early (convention) |
| **Mathematics** | Minimal, practical | Central: objectives, proofs, assumptions |
| **Evaluation axes** | Throughput, latency, scalability, cost | Accuracy/quality, robustness, sample/compute efficiency, provable properties |
| **Citations** | Numbered IEEE/ACM `[1]` | Author-year `(Smith 2025)` |
| **Length** | 12-15 pages | 7 pages of technical content |
| **Review** | Single- or double-blind by venue | Double-blind, two-phase, abstract-then-paper |
| **Reproducibility** | Artifact evaluation (badges) | Mandatory reproducibility checklist (in-PDF through AAAI-26; separate upload at AAAI-27) |
| **Template** | USENIX / ACM sigconf | AAAI Press two-column (`article` + `aaai<NN>.sty`) |

A paper describing an AI *system* may still include an implementation section — the correct framing is "not structurally required," not "forbidden." Match the norms of the specific subfield (learning, planning, reasoning, NLP, vision, robotics, KR, theory) by reading recent accepted AAAI papers in that area.
