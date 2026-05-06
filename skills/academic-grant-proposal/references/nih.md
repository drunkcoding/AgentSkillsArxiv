# NIH Proposals

US National Institutes of Health. CS/ML proposals typically go to **NIBIB** (Bioimaging/Bioengineering), **NLM** (Library of Medicine — biomedical informatics, computational biology), or as cross-cutting BD2K / Bridge2AI / DataScience initiatives.

## Table of Contents

1. [Mechanism Selection](#mechanism-selection)
2. [SF424 Components](#sf424-components)
3. [Specific Aims (1 page) — the most important page](#specific-aims-1-page--the-most-important-page)
4. [Research Strategy (12 pages)](#research-strategy-12-pages)
5. [Significance, Innovation, Approach Scoring](#significance-innovation-approach-scoring)
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
| **R21** | Exploratory / high-risk-high-reward | $275K total over 2 yr | 2 yr | 6 pp |
| **R03** | Small grants, pilot projects | $50K/yr | 2 yr | 6 pp |
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
9. **Biosketch** (per senior person, NIH format) — 5 pages max, SciENcv-generated
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

## Significance, Innovation, Approach Scoring

NIH 1-9 scoring (1 = exceptional, 9 = poor). Each criterion scored separately, plus an Overall Impact score. Funding line is currently around **2.0-3.0** at most institutes (varies by NI). Below 2.5 has a strong chance; above 4.0 rarely funded.

| Score | Descriptor | Likelihood |
|---|---|---|
| 1-2 | Exceptional / Outstanding | High |
| 3 | Excellent | Probable |
| 4-5 | Very good / Good | Discussed but unlikely |
| 6-9 | Satisfactory / Poor | Triaged (not discussed) |

**Triage threshold:** the bottom ~50% of applications are not discussed at study section. Your goal in the Specific Aims is to avoid triage.

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

### NIH Biosketch (5 pages max)
SciENcv-generated. Structure:
- **A. Personal Statement** — narrative; explain why you are qualified for THIS specific project; cite up to 4 publications relevant to this proposal
- **B. Positions, Scientific Appointments, and Honors**
- **C. Contributions to Science** — up to 5 contributions, each with a paragraph + up to 4 cited publications. **Each contribution should describe an arc of research**, not list one paper.
- **D. (removed since 2015)** — research support is now in Other Support

### Other Support
SciENcv-generated. Lists active and pending support per senior person. Disclose foreign affiliations (mandatory since 2021 due to research-security policies).

### Data Management and Sharing Plan (DMS Plan)
**Mandatory since January 2023** for all R-mechanism applications. ≤2 pages. Address: data types, related tools/software, standards, data preservation/sharing, access/distribution, oversight. CS proposals: code release plan (license, repository) belongs here.

### Vertebrate Animals / Human Subjects
If applicable, structured sections required by NIH. CS-only proposals usually mark "no" and skip.

## Submission Logistics

- **Portal:** eRA Commons (via Grants.gov or ASSIST)
- **Standard deadlines:** Feb 5, June 5, Oct 5 (R01 new); Mar 5, July 5, Nov 5 (R01 renewals/resubmissions); other mechanisms have separate dates — check the specific FOA
- **Compliance check:** Office of Sponsored Research must validate before submission; allow ≥1 week
- **Resubmission policy:** A1 (one resubmission) allowed for most mechanisms, must be submitted within 37 months of original A0; **the Introduction page (1 page) addresses prior reviewer comments**
- **Just-in-Time (JIT) information** requested ~3 months before award (after favorable score) — IRB/IACUC approvals, Other Support updates
- **Common pitfalls:** Specific Aims over 1 page; Research Strategy over page limit; missing required appendix sections; Biosketch over 5 pages; not using SciENcv
