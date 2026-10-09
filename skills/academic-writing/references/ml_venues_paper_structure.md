# ICML, ICLR, and NeurIPS Conference Paper Structure (ML Papers)

## Table of Contents

1. Overview and shared ML-paper paradigm
2. Master comparison table (ICML vs ICLR vs NeurIPS vs AAAI)
3. ICML: format and length hard rules
4. ICML: required statements and policies
5. ICLR: format and length hard rules
6. ICLR: recommended statements and policies
7. NeurIPS: format, checklist, and policies
8. Paper structure (shared conventions, per-section guidance)
9. Review process (OpenReview mechanics per venue)
10. Reciprocal reviewing requirements
11. Dual submission, arXiv, and LLM-usage policies
12. Citation style
13. Section length proportions and writing order
14. Official NeurIPS sources

## 1. Overview

ICML (International Conference on Machine Learning), ICLR (International Conference on Learning Representations), and NeurIPS (Conference on Neural Information Processing Systems) are top-tier archival ML venues. All three follow the **method-experiment** paradigm shared with AAAI (see `aaai_paper_structure.md`): organize the paper around *a method (model, algorithm, theory) and the scientific evidence that it works*, not around a built-and-deployed system.

The section-level structure conventions of ICML/ICLR/NeurIPS papers are essentially the same as AAAI's (Section 8 below). What differs — and what this file focuses on — are the **format hard rules, required statements, and review mechanics**, which are venue-specific and change yearly.

> **Standards drift every year. Always confirm exact numbers against the current edition's official Call for Papers / Author Guide** (`icml.cc/Conferences/<YYYY>/CallForPapers`, `icml.cc/Conferences/<YYYY>/AuthorInstructions`, `iclr.cc/Conferences/<YYYY>/AuthorGuide`, `neurips.cc/Conferences/<YYYY>/CallForPapers`). Facts below are verified against **ICML 2026**, **ICLR 2026**, and **NeurIPS 2025/2026**; treat dated deadlines and reviewer counts as illustrative.

## 2. Master Comparison (ICML vs ICLR vs NeurIPS vs AAAI)

| | ICML (2026) | ICLR (2026) | NeurIPS (2025/2026) | AAAI (26) |
|---|---|---|---|---|
| Main-text pages | **8** (+1 at camera-ready) | **9** at submission, **10** at rebuttal/camera-ready | **9** (+1 at camera-ready) | 7 (+2 purchasable) |
| References count? | No (unlimited) | No (unlimited) | No | No |
| Appendix | Unlimited, same single file, doesn't count | Unlimited after references (same PDF or separate supplement), doesn't count | Optional and unlimited; doesn't count; reviewers may ignore it | Separate technical appendix upload; in-paper appendix counts |
| Columns | Two-column | **Single-column** | Two-column | Two-column |
| Style file | `icml<YYYY>.zip` (`icml2026.sty`) | `iclr<YYYY>.zip` from `github.com/ICLR/Master-Template` | Edition kit (`neurips_2025.sty` in 2025) | `aaai<NN>.sty` |
| Citations | Author-year (natbib) | Author-year (natbib) | Numeric via the bundled natbib/template settings | Author-year (natbib) |
| Platform | OpenReview | OpenReview | OpenReview | OpenReview |
| Reviews public? | Published for accepted papers (with rebuttal + discussion; new 2026 policy); rejected papers opt-in | **Fully public** for all submissions; de-anonymized after decisions | Private during review; accepted and opted-in rejected records become public after notification (2025) | Not public |
| Rebuttal | Per-review responses; three 5,000-char rounds (rebuttal, reviewer follow-up, author follow-up; 2026) | **Open discussion thread**, Nov-Dec window, unlimited comments (per-comment word limit), **paper revisions allowed** | Per-review responses, **10,000 chars each** (2025), then rolling discussion; no revised PDF/supplement | Single 2,500-char response, no new results |
| Required extra sections | **Impact Statement** (mandatory, doesn't count) | Ethics Statement + Reproducibility Statement (recommended, don't count); **LLM-usage section mandatory if significant LLM role** | **Paper Checklist mandatory**, last in PDF, doesn't count | Reproducibility checklist (mandatory, in PDF) |
| Reciprocal reviewing | Yes — per-submission + per-author (4+ subs) | Yes — authors on 3+ papers review ≥6 papers | Authors may be asked to review; reviewer-authors face access restrictions/sanctions for non-compliance; no numeric quota stated in the 2025 CFP | No equivalent |
| Withdrawal | Standard | **Withdrawn-after-deadline papers stay public and are de-anonymized** | Standard | Standard |

## 3. ICML: Format and Length Hard Rules

Verified against ICML 2026 CFP. Non-conforming papers are **rejected without review**.

- **8 pages for the main paper.** Unlimited additional pages for **references, the impact statement, and appendices**. Everything goes in a **single file** — there is no separate supplementary-material deadline.
- **Camera-ready: one extra page** for the main paper (8 → 9).
- **Two-column ICML template**: use the edition style files (`icml2026.zip` → `icml2026.sty`) and check the official example paper. LaTeX skeleton:

  ```latex
  \documentclass{article}
  \usepackage{icml2026}            % submission (anonymous, line numbers)
  % \usepackage[accepted]{icml2026} % camera-ready
  ```

- The submission version of the style adds **line numbers and anonymization automatically** — do not fight the style file.
- **Abstract registration deadline ~5 days before the paper deadline.** Placeholder abstracts that are substantially rewritten risk removal without consideration.
- **Author list is frozen at the abstract deadline.** Reordering is allowed afterwards; additions/removals need written justification and case-by-case program-chair approval (granted only in exceptional circumstances).

## 4. ICML: Required Statements and Policies

### Impact Statement (mandatory)

- A statement of the **potential broader impact** of the work, including ethical aspects and future societal consequences.
- Placement: **separate section at the end of the paper, co-located with Acknowledgements, before References.** Does **not** count toward the page limit.
- Where impacts are the well-established ones of advancing ML generally, the official boilerplate may be used verbatim: *"This paper presents work whose goal is to advance the field of machine learning. There are many potential societal consequences of our work, none of which we feel must be specifically highlighted here."*
- Reviewers/ACs may flag submissions for **ethics review**; ethics reviewers comment but cannot reject — program chairs can reject on ethical grounds in extreme cases.

### Other ICML policies (2026)

- **Publication of the submitted version (new 2026):** for accepted papers, ICML publishes the originally submitted version, anonymized reviews, meta-reviews, rebuttal, and reviewer-author discussion alongside the camera-ready. Rejected papers may opt in. Write the *submission* as if it will be public.
- **Lay summary (camera-ready):** accepted papers must submit a short plain-language summary in OpenReview.
- **Optional self-rankings:** authors with multiple submissions may rank their own papers; disagreements with reviewer scores flag papers for AC attention.
- **Attendance optional (2026):** accepted papers may be proceedings-only (virtual registration required); equal treatment for awards/orals/spotlights.
- Proceedings are indexed in **PMLR** (Proceedings of Machine Learning Research).

## 5. ICLR: Format and Length Hard Rules

Verified against the ICLR 2026 Author Guide. Violations → **desk rejection**.

- **9 pages of main text at submission.** The limit increases to **10 pages** during the discussion/rebuttal phase and for camera-ready (to accommodate new results/discussion). Strictly enforced — an over-limit main text is desk-rejected.
- **References: unlimited pages,** don't count. **Acknowledgements don't count.**
- **Appendices: unlimited,** placed after the bibliography — either in the same PDF or as a separate supplementary file. Reviewers are **not required to read the appendix**. Supplementary material (including code as a .zip) is due **with the main paper**.
- **Single-column ICLR template**: LaTeX style files from `https://github.com/ICLR/Master-Template` (`iclr2026.zip`). Uses natbib author-year citations.
- **Abstract deadline ~5 days before the paper deadline**; abstracts must be genuine (used for reviewer bidding); placeholders are deleted. **No authors can be added after the abstract deadline**; order may change up to the paper deadline; no author changes at all after the paper deadline.
- **Withdrawal warning:** after the submission deadline, withdrawn papers remain **publicly hosted on OpenReview and are immediately de-anonymized**. ICLR submissions cannot be deleted. Do not submit half-finished work to ICLR.

## 6. ICLR: Recommended Statements and Policies

- **Ethics Statement** *(recommended when relevant, not required for all papers)*: a paragraph at the **end of the main text, before references**, addressing human subjects, dataset releases, harmful insights, bias/fairness, privacy, legal compliance, research integrity. Does not count toward the page limit; max 1 page. All authors must read and acknowledge the **ICLR Code of Ethics** at submission regardless.
- **Reproducibility Statement** *(strongly encouraged)*: a paragraph at the **end of the main text, before references**, that **points to** where reproducibility material lives (anonymous code in supplement, proofs and assumptions in appendix, data-processing steps in supplementary materials) rather than describing details itself. Does not count toward the page limit.
- **LLM-usage section (mandatory when applicable, new for 2026):** if LLMs played a significant role in research ideation and/or writing — to the extent they could be regarded as a contributor — describe the precise role in a separate section (appendix OK, doesn't count). **Not disclosing significant LLM usage can lead to desk rejection.** LLMs are not eligible for authorship.
- **Anonymous code:** three sanctioned routes — (1) anonymized .zip as supplementary material, (2) anonymous repository link in the paper, (3) reviewer-visible-only link posted as an OpenReview comment after forums open. Ensure the host does not track visitors.

## 7. NeurIPS: Format, Checklist, and Policies

Facts in this section are verified against the **NeurIPS 2025 CFP and Author FAQ**, the **NeurIPS 2026 CFP and Main Track Handbook**, and the current official **Paper Checklist Guidelines**. Re-check the current edition before submission.

### Format and length hard rules

- Use **9 content pages at submission** and at most **10 content pages at camera-ready**. Count all main-text figures and tables. Do not count references, optional technical appendices, or the mandatory checklist.
- Submit one PDF in this order: paper content → references → optional technical appendices → **NeurIPS Paper Checklist**. Reviewers may ignore appendices and supplementary material; keep the main text self-contained.
- Use the edition's official **two-column LaTeX kit** (`neurips_2025.sty` in the 2025 kit; use the 2026 formatting package for NeurIPS 2026). Do not change margins or font sizes. Style or page-limit violations may be rejected without review.
- Register a substantive abstract before the full paper. The gap was **4 days in 2025** (May 11 → May 15) and **2 days in 2026** (May 4 → May 6). Freeze the author list at the abstract deadline; only reordering is allowed afterward.

### Paper Checklist (mandatory)

- Keep the checklist supplied by the style file. Place it **last**, after references and any optional appendices/supplemental text. It does **not** count toward the page limit.
- Complete every item with `yes`, `no`, or `n/a`, and point to supporting sections or add a short justification. Answers are visible to reviewers and become part of the final published paper.
- Do not remove it: omission is a **desk-rejection** condition. A justified `no` or `n/a` is generally not itself grounds for rejection.
- Use the checklist to audit claims, limitations, proofs, reproducibility, code/data access, experimental details and uncertainty, compute, ethics, impacts, licenses, released assets, human subjects, IRB approval, and applicable LLM use.

### OpenReview, rebuttal, and publication

- Submit through **OpenReview** under double-blind review. Keep the submission, appendices, code, and links anonymous; omit acknowledgements and cite self-work in the third person.
- Treat reviews and responses as private during review. For **NeurIPS 2025**, accepted papers' reviews, meta-reviews, author responses, and discussion become public after notification; rejected papers become public only if authors opt in.
- For **NeurIPS 2025**, answer each review separately with up to **10,000 characters** in OpenReview markdown. Do not upload files, link external material, or revise the paper/supplement during rebuttal. Use the one-week response period, then continue only through the rolling reviewer-author discussion.

### Reviewing, preprints, dual submission, and LLM use

- Expect author-reviewer obligations if invited. The **2025 CFP states no numeric reciprocal-reviewing quota**; it asks authors to help review when requested. Reviewer-authors who submit late, missing, or persistently low-quality reviews may lose access to their own reviews and can put their submissions at desk-rejection risk. Confirm the current handbook.
- Allow a non-anonymous arXiv/preprint before or during review, but do not cite the submission's own preprint in the anonymous paper, label it “under review at NeurIPS,” or advertise it aggressively. Use the template's `preprint` option for public versions.
- Do not concurrently submit substantially similar work to another archival venue, another NeurIPS track, or a journal. Non-archival workshop versions are allowed. The policy applies throughout review; violations may be desk-rejected.
- Disclose LLM/agent use in the experimental setup when it is an important, original, or non-standard part of the method. Do not disclose ordinary grammar, editing, formatting, or basic coding assistance. Keep humans solely responsible for correctness and originality; do not list an LLM as an author or use prompt injection.

### Datasets and Benchmarks / Evaluations and Datasets track

- Route dataset/benchmark-centered work through the track-specific CFP and **separate OpenReview portal**; papers are not transferred after closing and cannot be submitted to multiple tracks.
- For **NeurIPS 2025**, the Datasets & Benchmarks track followed main-track formatting and deadlines but allowed single- or double-blind review and required accessible dataset/benchmark code at submission.
- For **NeurIPS 2026**, the track is renamed **Evaluations & Datasets (E&D)** and broadens to evaluation science. It defaults to double-blind review, permits declared single-blind review when a dataset cannot be anonymized, and applies contribution-dependent artifact requirements. Confirm its current CFP rather than applying old D&B rules.

## 8. Paper Structure (Shared ML Conventions)

The conventional structure is the same method-experiment skeleton as AAAI — see `aaai_paper_structure.md` for full per-section guidance (Introduction density, Method as the core, formal Preliminaries, Experimental Setup for fairness/reproducibility, Results + Ablations, Limitations). Differences to apply here:

1. Abstract → Introduction → Related Work *(early by convention; late acceptable for theory papers)* → Background/Preliminaries → Method → Theory *(if any)* → Experiments (Setup, Results, Ablations) → Limitations → Conclusion
2. **ICLR:** + Ethics Statement and Reproducibility Statement before references (when included)
3. **ICML:** + Impact Statement (with Acknowledgements, camera-ready) before references
4. **NeurIPS:** + mandatory Paper Checklist after references and optional appendices
5. References → Appendices (ICML/ICLR); References → optional Appendices → Checklist (NeurIPS)

Structural notes specific to ICML/ICLR/NeurIPS:

- **More room than AAAI** (8-10 pages vs 7): Method and Experiments can breathe; a thorough ablation/analysis section is expected at these venues, not optional.
- **ICLR single-column format** fits wide figures and equations naturally; don't shrink figures to two-column sizes.
- **Use appendices deliberately** at all three venues for full proofs, extended ablations, hyperparameter tables, and additional qualitative results. Keep the main text self-contained because reviewers need not read supplementary material; follow each venue's current packaging rules.
- **ICLR discussion-phase revisions are part of the writing process**: reserve the 10th page for rebuttal-phase additions (new experiments, clarifications). Plan the submission at 9 pages knowing one more page becomes available.
- **NeurIPS:** put the mandatory checklist last and keep contribution-critical evidence in the first 9 content pages; do not plan on a rebuttal-phase PDF revision.
- Titles describe the **method or finding** (named methods/models are common); no "SystemName:" convention. Avoid hype.

## 9. Review Process (OpenReview Mechanics)

All three venues use **double-blind** review on OpenReview; keep profiles current, cite prior self-work in the **third person**, and never advertise the work as under submission during review. Profile-activation timing and sanctions vary by venue; check the current guide.

### ICML

- Reviews are released to authors; the author-reviewer discussion has **three rounds — rebuttal, reviewer follow-up, author follow-up — each limited to 5,000 characters** (ICML 2026 Reviewer Instructions). Markdown, no file uploads, no revised PDF during the feedback period; reviewers must acknowledge responses. Verify the current edition's exact mechanics.
- Reviews historically private; from 2026, published for accepted papers (see Section 4).

### ICLR

- **Reviews are public** (anonymous) from the moment they are released.
- **Public discussion period (~3 weeks, Nov-Dec):** authors post responses as comments — unlimited comments, per-comment word limit, multiple replies per reviewer allowed. Anyone logged in may comment publicly (non-author/reviewer comments are non-anonymous).
- **Authors may revise the paper (and title/abstract/supplement) during the discussion period**; a pdfdiff is applied against the original, and reviewers/ACs may ignore changes that substantially diverge from the submitted paper. Clearly communicate what changed.
- After public discussion: private reviewer/AC discussion → decisions. **All submissions (accepted, rejected, withdrawn) are de-anonymized and released with their reviews after notification.** Rejected papers are considered non-archival and may be resubmitted elsewhere, but the ICLR record persists.
- Treat the ICLR rebuttal as an **evolving conversation, not a terminal message** — see `academic-rebuttal` skill for rebuttal strategy.

### NeurIPS

- Reviews and author responses are not public during review; the public cannot comment. For NeurIPS 2025, accepted records and opted-in rejected records become public after notification, including anonymous reviews and discussion.
- Use **per-review rebuttals** (10,000 characters each in 2025), then participate in the rolling discussion. Do not upload a revised PDF or supplement during rebuttal.
- Keep the response anonymous and self-contained. Do not add links or files; new results may clarify questions, but the original submission remains the decision basis.

## 10. Reciprocal Reviewing (Venue-Specific — Desk-Rejection Risk)

- **ICML (2026):** (a) *per-submission*: every submission must designate ≥1 qualified author as a reciprocal reviewer; one person can be the designated reviewer for **at most 2 submissions**; (b) *per-author*: every author with **4+ submissions** must review (threshold can drop to 3 in a reviewer shortage). Failing either requirement — or delivering late/insufficient reviews — can desk-reject **your own submissions**.
- **ICLR (2026):** authors on **3+ papers** must review **at least 6 papers**; every submission needs ≥1 registered reviewer-author (qualified = prior ICLR/NeurIPS/ICML or equivalent publication; teams with no qualified author are exempt). Non-compliance → desk rejection.
- **NeurIPS (verified 2025; sanctions also documented in the 2026 handbook):** authors may be recruited as reviewers, but the 2025 CFP states no fixed per-submission or per-author numeric quota. Reviewer-authors who neglect assigned reviews can lose access to reviews of their own papers; gross or persistent failures can put their submissions at desk-rejection risk. Confirm the current Main Track Handbook.
- Exemptions and sanctions vary by venue. Budget reviewing time into the submission plan — this is a real acceptance risk, not paperwork.

## 11. Dual Submission, arXiv, and LLM Policies

- **Dual submission (all three):** identical or substantially similar papers may not be concurrently under review or previously published at archival venues. Workshop papers without archival proceedings are fine. ICML and NeurIPS treat overlapping concurrent submissions as prior work and may reject papers made incremental by another submission; NeurIPS also forbids duplicate submission across its tracks.
- **arXiv (all three):** allowed before and during review. Do not reference the submission's own non-anonymous version in the anonymized paper or advertise the preprint as under review. OpenReview provides anonymous BibTeX entries for citing papers under review at ICLR.
- **LLM use (all three):** authors bear full responsibility; LLMs cannot be authors; prompt injection is forbidden. ICLR requires a section for significant contribution; ICML encourages methodological disclosure; NeurIPS requires disclosure when agents/LLMs are important, original, or non-standard parts of the method but not for ordinary editing/formatting/basic code assistance.

## 12. Citation Style

ICML and ICLR use **author-year citations via natbib**, set by the venue style file — same family as AAAI, different rendering (comma before year: "(Sutton & Barto, 1998)"):

```latex
\citep{sutton1998}     % (Sutton & Barto, 1998)   — parenthetical
\citet{sutton1998}     % Sutton & Barto (1998)    — textual
\citep[e.g.,][]{a,b}   % (e.g., A et al., 2020; B et al., 2021)
```

- Use `\citet` when the authors are the sentence's subject; `\citep` otherwise. Never write "(see \citet{...})".
- Use the `.bst` shipped in the venue style zip; do not substitute another bibliography style.
- **NeurIPS uses the numeric citation mode supplied by its official LaTeX kit.** Keep the bundled natbib and bibliography configuration; do not override it with an author-year or custom `.bst` setup. Confirm against the current style package.
- Cite every baseline compared against; heavy recent-work coverage is expected; self-citations in third person.
- See `citation_styles.md` for the full author-year vs numbered comparison.

## 13. Section Length Proportions and Writing Order

Indicative allocation for an 8-9 page empirical paper (theory papers shift ~1-1.5 pages from Experiments to Theory):

| Section | Approx. space |
|---------|---------------|
| Introduction | ~1 page |
| Related Work | 0.5-0.75 page |
| Background / Preliminaries | 0.5-1 page |
| Method | 2-2.5 pages |
| Experiments (setup + results + ablations) | 2.5-3.5 pages |
| Limitations + Conclusion | ~0.5 page |
| Statements/checklist (impact / ethics / reproducibility / NeurIPS checklist) | outside the limit where the venue permits |

**Writing order** (same as AAAI): Method → Experiments (or Theory) → Introduction → Related Work + Preliminaries → Limitations + Conclusion → Abstract → Title → venue statements (ICML impact statement; ICLR ethics/reproducibility statements; NeurIPS checklist) → appendix polish. For ICLR, additionally plan which rebuttal-phase experiments would occupy the 10th page if reviewers ask. For NeurIPS, finish the checklist only after every answer points to evidence in the paper or appendix.

## 14. Official NeurIPS Sources

Use these primary sources and replace the edition year when preparing a future submission:

- **NeurIPS 2025 CFP** — page limits, template, OpenReview/privacy, double-blind review, checklist requirement, abstract gap, appendices/supplement, preprints, dual submission, author-response/publication mechanics, and D&B routing: https://neurips.cc/Conferences/2025/CallForPapers
- **NeurIPS 2025 Author FAQ** — 10,000-character per-review rebuttal, markdown/no files, no PDF or supplement revision, links/new-results constraints, and author-list/checklist clarifications: https://neurips.cc/Conferences/2025/PaperInformation/NeurIPS-FAQ
- **NeurIPS 2025 official style archive** — `neurips_2025.sty`, two-column layout, and bundled citation/bibliography configuration: https://media.neurips.cc/Conferences/NeurIPS2025/Styles.zip
- **NeurIPS Paper Checklist Guidelines** — placement, page-limit exclusion, mandatory/desk-reject status, visibility, answer mechanics, and checklist topics: https://neurips.cc/public/guides/PaperChecklist
- **NeurIPS 2025 LLM Policy** — methodological disclosure threshold, editing exception, author responsibility, and no LLM authorship: https://neurips.cc/Conferences/2025/LLM
- **NeurIPS 2025 Datasets & Benchmarks CFP** — separate portal, review mode, and dataset/code requirements: https://neurips.cc/Conferences/2025/CallForDatasetsBenchmarks
- **NeurIPS 2026 CFP and Main Track Handbook** — current deadlines/template link, 9+1 rule, checklist, LLM/agent use, preprints, dual submission, and reviewer-author sanctions: https://neurips.cc/Conferences/2026/CallForPapers and https://neurips.cc/Conferences/2026/MainTrackHandbook
- **NeurIPS 2026 Evaluations & Datasets CFP** — renamed/broadened track, review mode, separate portal, and contribution-dependent artifact rules: https://neurips.cc/Conferences/2026/CallForEvaluationsDatasets
