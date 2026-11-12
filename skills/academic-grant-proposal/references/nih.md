# NIH Proposals

Facts last verified 2026-11-12 against NIH Guide notices NOT-OD-24-010 (Simplified Review Framework), NOT-OD-26-018 and NOT-OD-26-033 (Common Forms), and NOT-OD-25-132 (application limit). Funder rules change frequently — confirm against the current solicitation/NOFO before relying on any limit or amount.

US National Institutes of Health. CS/ML proposals typically go to **NIBIB** (Bioimaging/Bioengineering), **NLM** (Library of Medicine — biomedical informatics, computational biology), or as cross-cutting BD2K / Bridge2AI / DataScience initiatives.

## Table of Contents

1. [Mechanism Selection](#mechanism-selection)
2. [SF424 Components](#sf424-components)
3. [Specific Aims (1 page) — the most important page](#specific-aims-1-page--the-most-important-page)
4. [Research Strategy (12 pages)](#research-strategy-12-pages)
5. [Review Criteria and Scoring (Simplified Review Framework)](#review-criteria-and-scoring-simplified-review-framework)
6. [R01 vs R21 Strategic Differences](#r01-vs-r21-strategic-differences)
7. [K-Awards (Career Development)](#k-awards-career-development)
8. [F-Awards (Fellowships)](#f-awards-fellowships)
9. [Auxiliary Documents](#auxiliary-documents)
10. [Submission Logistics](#submission-logistics)

---

## Mechanism Selection

| Mechanism | Purpose | Budget (annual) | Duration | Research Strategy pp |
|---|---|---|---|---|
| **R01** | Mature, hypothesis-driven research | typically $250-500K direct | up to 5 yr | 12 pp |
| **R21** | Exploratory / high-risk-high-reward | $275K total over 2 yr (confirm on grants.nih.gov) | 2 yr | 6 pp (confirm on grants.nih.gov) |
| **R03** | Small grants, pilot projects | $50K/yr (confirm on grants.nih.gov) | 2 yr | 6 pp |
| **R37** | MERIT extension of R01 | as R01 | up to 7 yr | as R01 |
| **K99/R00** | Postdoc → faculty transition | varies | 5 yr (2+3) | 12 pp |
| **K01/K08/K23** | Career development for junior PIs | salary support + research | 3-5 yr | 12 pp |
| **F31** | Predoctoral fellowship | stipend + tuition | up to 5 yr | 6 pp |
| **F32** | Postdoctoral fellowship | stipend | up to 3 yr | 6 pp |
| **U01/U54** | Cooperative agreements (multi-PI consortia) | varies | 5 yr | varies |

**Discipline tip:** for ML-on-biomedical-data work, pick R01 / R21 over computer-science-only R-mechanisms. NIH study sections like **BDMA** (Biomedical Data Management and Analysis) and **MABS** (Modeling and Analysis of Biological Systems) review CS+biomedical work.

## SF424 Components

PHS 398/PHS 2590 / SF424 (R&R) Application Guide — required documents (most current SF424 forms; verify in the specific FOA):

1. **Cover Page / SF424 Face Page**
2. **Project Summary / Abstract** — 30 lines / ~3000 chars; describes goals + significance
3. **Project Narrative** — 2-3 sentences, public-health relevance
4. **Specific Aims** — exactly 1 page
5. **Research Strategy** — Significance + Innovation + Approach (page limit by mechanism)
6. **Bibliography & References Cited** — no page limit
7. **Facilities & Other Resources** — no page limit
8. **Equipment** — no page limit
9. **Biographical Sketch** (per senior person) — Common Form + NIH Biographical Sketch Supplement for due dates on/after Jan 25, 2026, SciENcv-generated, no page limit for the combined PDF (NOT-OD-26-018); also **Current and Pending (Other) Support** Common Form
10. **Budget + Budget Justification** — modular ($250K/yr cap) or detailed (>$250K)
11. **Resource Sharing Plans** — Data Management & Sharing Plan, Model Organism Sharing
12. **Vertebrate Animals** / **Human Subjects** sections (if applicable)
13. **Letters of Support**
14. **Authentication of Key Biological and/or Chemical Resources** (if applicable)

## Specific Aims (1 page) — the most important page

The **Specific Aims** page is the single most-read document at NIH study sections. Many reviewers form their score from this page alone. Allocate 30%+ of total writing time here.

### Required structure (paragraph-by-paragraph)

**Paragraph 1: Hook + Significance** (~5-6 lines)
- Open with the broad health problem, quantified
- Narrow to the specific knowledge gap
- Cite 1-2 key papers with [bracketed numbers]

**Paragraph 2: Long-term Goal + Objective** (~3-4 lines)
- "The **long-term goal** of this research is to [X]."
- "The **central objective** of this proposal is to [Y]."
- "The **central hypothesis** is that [Z], based on preliminary data showing [W]."

**Paragraph 3: Aims** (~12-15 lines for 3 Aims)

```
**Aim 1.** [Verb] [object]. [Working hypothesis]. We will [approach], measuring [outcome].
**Aim 2.** [Verb] [object]. [Working hypothesis]. We will [approach], measuring [outcome].
**Aim 3.** [Verb] [object]. [Working hypothesis]. We will [approach], measuring [outcome].
```

Each Aim begins with a **strong verb** (Determine, Develop, Test, Characterize, Define, Quantify). Avoid weak verbs (Study, Investigate, Explore, Examine).

**Paragraph 4: Innovation + Expected Outcomes + Impact** (~5-6 lines)
- "This proposal is innovative because [I1, I2, I3]."
- "Expected outcomes: [O1, O2, O3]."
- "Impact: [the science/health field that will be advanced]."

### Common Specific Aims mistakes

- More than 3 Aims (rare to fund 4+)
- Aims dependent on each other ("Aim 2 only works if Aim 1 succeeds") — reviewers see this as fragile
- Methods-driven rather than hypothesis-driven Aims
- Vague verbs (Study, Examine)
- Missing "central hypothesis" sentence
- Going over 1 page

## Research Strategy (12 pages)

Three NIH-mandated subsections with explicit headers. Recommended page allocation for R01:

### a. Significance (~2-3 pp)
Why does this matter? Address:
- Importance of the problem (incidence/prevalence/mortality numbers, economic cost)
- Critical barriers blocking progress
- How completing the Aims will *change* the field — be specific about which textbook, clinical guideline, or computational practice will need updating

### b. Innovation (~1 pp)
What is conceptually or methodologically new? Address:
- Refinements/improvements over current approaches (with concrete deltas)
- Novel theoretical concepts, methods, instrumentation, or interventions
- Cite the SOTA explicitly and beat it on a specific metric

Innovation is **not** "we use deep learning"; it is what your specific architectural/algorithmic/measurement choice unlocks that prior work could not.

### c. Approach (~8-9 pp for R01)
Per Aim, a self-contained subsection containing:
1. **Rationale + Working Hypothesis** (paragraph)
2. **Preliminary Data** (figures + brief narrative, ≥1 figure per Aim) — feasibility evidence
3. **Research Design** (detailed methods, sample sizes, controls, statistical analysis)
4. **Expected Outcomes**
5. **Potential Pitfalls and Alternative Strategies** — name 2-3 risks per Aim with concrete mitigations

Approach is graded most heavily of the three. Reviewers look for: rigor (statistical power, blinding, controls), feasibility (preliminary data + team expertise), and explicit alternative strategies.

## Review Criteria and Scoring (Simplified Review Framework)

For most research project grant (RPG) applications — including R01, R03, R21, R34, U01 and the other activity codes listed in NOT-OD-24-010 — with receipt dates **on or after Jan 25, 2025**, NIH uses the **Simplified Review Framework**. It reorganizes the five regulatory criteria (Significance, Investigators, Innovation, Approach, Environment) into three factors:

| Factor | Contains | How reviewers rate it |
|---|---|---|
| **1. Importance of the Research** | Significance, Innovation | Criterion score 1-9 |
| **2. Rigor and Feasibility** | Approach | Criterion score 1-9 |
| **3. Expertise and Resources** | Investigator(s), Environment | Not numerically scored; reviewer selects "Appropriate" or "Identify need for additional expertise and/or resources" (the latter requires a brief explanation of the gaps) |

All three factors feed an **Overall Impact** score (1-9; 1 = exceptional, 9 = poor). Additional review criteria (human subjects, vertebrate animals, biohazards, resubmission/renewal/revision) are considered in the overall score but get no separate score. Clinical-trial and inclusion considerations are folded into Factor 2. Because Factor 3 is a sufficiency check, put your effort into Factors 1 and 2: state why the work matters (Significance, Innovation) and show rigor and feasibility (Approach: controls, sample-size justification, preliminary data, pitfalls and alternatives). In Biographical Sketch and Facilities text, show the team and resources fit *this project* rather than general reputation.

Informal rules of thumb (unverified approximations, not NIH policy; they vary by institute and year — confirm on grants.nih.gov): funding lines are often cited as roughly 2.0-3.0 overall impact at many institutes, and scores above about 4 are rarely funded. The commonly cited "bottom ~50% not discussed (triaged)" threshold is likewise an unverified rule of thumb; check the current process for your study section.

## R01 vs R21 Strategic Differences

| Aspect | R01 | R21 |
|---|---|---|
| Preliminary data | Required (substantial) | Encouraged but not required (per FOA) |
| Innovation | Important but not primary | **Primary** criterion |
| Risk | Reviewer expects mitigation | Reviewer expects boldness |
| Typical Aims | 3 hypothesis-driven | 2 exploratory |
| Best for | Mature line of investigation | New direction, high-risk-high-reward |

R21 is **not** a "junior R01" — it is for genuinely exploratory work. Reviewers reject R21s that look like under-developed R01s.

## K-Awards (Career Development)

K-awards fund **protected research time** for junior investigators (K01, K08, K23, K99/R00). Distinguishing requirements:

- **Career Development Plan** (CDP) — separate document, 12 pp typical: training plan, mentor team, courses, seminars, milestones
- **Mentor Statement** — 6 pp, written by primary mentor, addresses mentoring plan, prior trainees, time commitment, lab resources
- **Co-mentor Statements** if multi-mentor team
- **Letters of Reference** — 3-5 letters describing PI's potential
- **Institutional Commitment** — letter from chair confirming protected time (≥75% effort for most Ks) and resources

CDP must be specific: list courses by name+number, conferences by year, statistical/methodological training. "I will learn statistics" fails; "I will complete BIOS 511 and BIOS 512 in Year 1" passes.

## F-Awards (Fellowships)

F31 (predoc), F32 (postdoc). Distinguishing requirements:

- **Sponsor Statement** is the most important external document — quality of mentor predicts outcome heavily
- **Training in Responsible Conduct of Research** plan required
- **Goals for Fellowship Training** section — what skills will you acquire?
- Research plan is 6 pages; training/career goals are evaluated equally with science

## Auxiliary Documents

### NIH Biographical Sketch (Common Form + NIH Supplement)
NOT-OD-26-018 requires the **Biographical Sketch Common Form** plus the **NIH Biographical Sketch Supplement**, prepared in **SciENcv**, for application due dates (and JIT, RPPR, prior-approval submissions) on or after **Jan 25, 2026**. NOT-OD-26-033 extended a warning-only leniency period through May 2026, after which validations become errors on a date NIH announces; confirm current enforcement on grants.nih.gov. The combined PDF has no page limit. Details and character limits: see [biosketch_dmp.md](biosketch_dmp.md#nih-biosketch-and-other-support-common-forms-sciencv-required). In brief:
- **Common Form** — Professional Preparation, Appointments and Positions, Products (up to 5 most closely related + up to 5 other significant)
- **Supplement** — Personal Statement (no citations; 3,500 characters) and Contributions to Science (up to 5, each up to 2,000 characters; no citations). **Each contribution should describe an arc of research**, not list one paper.
- Pre-2026 format (5 pages; sections A-C with cited publications) is legacy; Section D (research support) was removed earlier in favor of Other Support.

### Current and Pending (Other) Support
Common Form, SciENcv-generated, same Jan 25, 2026 effective date (NOT-OD-26-018); effort in person-months; own Statement of Potential Overlap per entry; supporting documentation (e.g., foreign contracts) attached separately. Disclose foreign affiliations (mandatory since 2021 due to research-security policies).

### Data Management and Sharing Plan (DMS Plan)
**Mandatory since January 2023** for all R-mechanism applications. ≤2 pages (confirm on grants.nih.gov). Address: data types, related tools/software, standards, data preservation/sharing, access/distribution, oversight. CS proposals: code release plan (license, repository) belongs here.

### Vertebrate Animals / Human Subjects
If applicable, structured sections required by NIH. CS-only proposals usually mark "no" and skip.

## Submission Logistics

- **Portal:** eRA Commons (via Grants.gov or ASSIST)
- **Standard deadlines:** Feb 5, June 5, Oct 5 (R01 new); Mar 5, July 5, Nov 5 (R01 renewals/resubmissions) (confirm on grants.nih.gov); other mechanisms have separate dates — check the specific FOA
- **Application limit:** NIH accepts at most six new, renewal, resubmission or revision applications per PI/PD (or MPI) per calendar year across all council rounds, for submissions from the Sep 25, 2025 receipt date onward; the limit applies to all activity codes except T codes and R13 (NOT-OD-25-132)
- **Compliance check:** Office of Sponsored Research must validate before submission; allow ≥1 week
- **Resubmission policy:** A1 (one resubmission) allowed for most mechanisms, must be submitted within 37 months of original A0 (confirm on grants.nih.gov); **the Introduction page (1 page) addresses prior reviewer comments**
- **Just-in-Time (JIT) information** requested ~3 months before award (after favorable score) — IRB/IACUC approvals, Other Support updates
- **Common pitfalls:** Specific Aims over 1 page; Research Strategy over page limit; missing required appendix sections; Biosketch not on the Common Form / Supplement; exceeding Supplement character limits; not using SciENcv
