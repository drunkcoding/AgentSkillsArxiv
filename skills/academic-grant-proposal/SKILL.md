---
name: academic-grant-proposal
description: "Write, review, and revise academic GRANT proposals for major funders: NSF (CAREER, standard, CRII (archived)), NIH (R01, R21, K, F), ERC (Starting, Consolidator, Advanced, Synergy), EU Horizon Europe/EIC/MSCA, DARPA/DoD/DOE BAAs, and UKRI/EPSRC/Royal Society. Covers section drafting (Specific Aims, Project Description, Broader Impacts, Excellence/Impact/Implementation, Heilmeier Catechism), letters of intent, pre-proposals and white papers, mock-reviewer critique, budgets, biosketches, data management plans, and responses to funder reviews on grant resubmission. Focus: CS / systems / ML. Not for conference-paper rebuttals (use academic-rebuttal) or papers (academic-writing)."
---

# Academic Grant Proposal Writing

## Core Purpose

Produce **fundable** grant proposals — proposals that pass each funder's specific review rubric. A grant proposal is **not a research paper**: it sells future work, foregrounds significance and feasibility, and is evaluated by panels who skim. Optimize for the funder's published criteria, not for general academic prose.

**Guiding principle:** every paragraph must answer one of three reviewer questions — *"Why is this important?"*, *"Why will it work?"*, *"Why this team?"* If a paragraph answers none, cut it.

## Final delivery: humanize the output

**REQUIRED SUB-SKILL (run before returning any draft to the user).** Load the `humanizer` skill (via the skill tool) and run the finished text through it as a final editing pass. It removes AI-writing tells (inflated significance, copula avoidance like "serves as", rule-of-three, overused AI vocabulary such as "delve"/"testament"/"landscape", filler phrases, sycophancy, and em/en-dash overuse) without inventing any fact, name, number, date, or citation. Preserve the format and conventions this skill requires (funder page limits, required headings, budget tables), and if the user supplied a writing sample, pass it so humanizer matches their voice. **Fallback:** if `humanizer` (or `humanizer-zh`) is unavailable in this environment, deliver the text anyway and tell the user the humanizer pass was skipped.

**If the draft is written in Chinese, load the `humanizer-zh` skill instead of `humanizer`** (via the skill tool) — it applies the same no-fabrication discipline to Chinese prose, targeting 空话铺垫 (empty build-up), 模板化排比 (templated parallelism), over-used connectors (首先/其次/综上所述), and inflated 四字格, while preserving the same format and conventions required above.

## Workflow

### Stage 1: Identify Funder + Mechanism (before drafting anything)

Funder and mechanism determine structure, page limits, evaluation criteria, and tone. **Read the current solicitation/call before writing.** If you cannot fetch it (no network access), use the values stored in the reference files, state the date on which they were last verified (2026-11-12), and tell the user to confirm them against the current call. Different funders use different terms for similar concepts (NSF "Intellectual Merit" ≈ ERC "Ground-breaking nature" ≈ Horizon "Excellence").

Facts in the reference files were last verified 2026-11-12 against official funder pages (second verification pass resolved earlier unverified items). Funder rules change with every work programme or solicitation: confirm against the current call documents before relying on any limit, date or amount.

Route to the matching reference file:

| Funder / task | Trigger keywords | Load |
|---|---|---|
| **NSF** | NSF, CAREER, CRII (archived), CISE, Future CoRe, "Intellectual Merit", "Broader Impacts" | [references/nsf.md](references/nsf.md) |
| **NIH** | NIH, R01, R21, R03, K-award, F-award, "Specific Aims", SF424 | [references/nih.md](references/nih.md) |
| **ERC** | ERC, Starting Grant, StG, Consolidator, CoG, Advanced, AdG, Synergy, "Part I / Part II" (older: "B1/B2"), "ground-breaking" | [references/erc.md](references/erc.md) |
| **EU Horizon** | Horizon Europe, EIC, MSCA, "Excellence/Impact/Implementation", work package, deliverables | [references/horizon_europe.md](references/horizon_europe.md) |
| **DARPA/DoD/DOE** | DARPA, BAA, ARO, ONR, AFOSR, DOE, ASCR, Heilmeier, white paper | [references/darpa_dod_doe.md](references/darpa_dod_doe.md) |
| **UKRI/EPSRC/Royal Society** | UKRI, EPSRC, BBSRC, NERC, Royal Society, URF, Dorothy Hodgkin, Funding Service, R4RI, New Investigator Award, Early Independence Fellowship, Network grants. Legacy terms "Case for Support" and "Pathways to Impact" also route here and are mapped to their current Funding Service equivalents | [references/ukri.md](references/ukri.md) |
| **Pre-proposal / LOI** | letter of intent, pre-proposal, concept paper, white paper (general; see also DARPA row) | [references/proposal_sections.md](references/proposal_sections.md#letters-of-intent-pre-proposals-and-concept-outlines) |
| **Section drafting (any funder)** | Aims, significance, innovation, approach, impact, team, timeline, risks, management | [references/proposal_sections.md](references/proposal_sections.md) |
| **Budget** | budget, budget justification, costing | [references/budget_justification.md](references/budget_justification.md) |
| **Biosketch / DMP** | biosketch, CV, track record, data management plan | [references/biosketch_dmp.md](references/biosketch_dmp.md) |
| **Critique / resubmission** | mock review, rejection reasons, response to reviewers, resubmission | [references/review_critique.md](references/review_critique.md) |

If the user asks generally without naming a funder, ask which agency/mechanism before drafting.

### Stage 2: Decompose into Sections

Most funders require the same logical components under different names. Map the user's request to one of these standard components and consult [references/proposal_sections.md](references/proposal_sections.md) for the cross-funder drafting playbook:

- **Aims / Objectives** (NIH Specific Aims, ERC Part I, Horizon Objectives, NSF "Goals")
- **Significance / Excellence** — why this matters
- **Innovation / Ground-breaking** — why this is novel beyond incremental work
- **Approach / Methodology** — technical plan, work packages, milestones, risk mitigation
- **Preliminary Results** — feasibility evidence (critical for NIH R01, ERC, NSF resubmissions)
- **Broader Impact / Impact** (NSF Broader Impacts, Horizon Impact, NIH Significance, UKRI impact embedded in Vision/Approach; legacy "Pathways to Impact")
- **Team / PI Track Record** — why you/we can do this
- **Timeline / Work Plan / Gantt** — year-by-year plan, deliverables
- **Risks and Mitigation**
- **Management** — multi-PI / consortium proposals

### Stage 3: Draft Auxiliary Documents

Most submissions require auxiliary documents alongside the science:

- **Budget + Budget Justification** → [references/budget_justification.md](references/budget_justification.md)
- **Biosketch / CV** (NSF, NIH, ERC formats differ) → [references/biosketch_dmp.md](references/biosketch_dmp.md)
- **Data Management Plan / DMP / ORRP** → [references/biosketch_dmp.md](references/biosketch_dmp.md)
- **Letters of Support / Collaboration Letters**
- **Facilities & Resources / Current & Pending Support**
- **Mentoring Plan** (NSF: required when NSF funding is requested for postdoctoral scholars or graduate students; PAPPG 24-1), **Sponsor Plan** (NIH F-awards)

### Stage 4: Self-Review and Reviewer-Style Critique

Before submission, run a mock-reviewer pass against the funder's published criteria. See [references/review_critique.md](references/review_critique.md) for the rubric-by-rubric checklist and common rejection reasons.

### Stage 5: Resubmission / Response to Reviewers (if applicable)

NIH permits an A1 resubmission, NSF treats a resubmission as a new proposal, ERC restricts resubmissions by earlier outcome, and UKRI accepts only invited resubmissions (fellowships excepted). Responses and revisions must be evidence-based and concrete. See [references/review_critique.md](references/review_critique.md) §Response-to-Reviewers.

---

## Universal Drafting Principles

Distinct from paper writing. **Do not copy paper prose into proposals.**

1. **Future-tense, action-oriented.** Proposals describe work that *will* happen. Use "We will design…", "Aim 2 develops…". Reserve past tense for preliminary results.

2. **Front-load significance.** Reviewers read page one closely and skim the rest. The first paragraph of every section must state what is being proposed and why it matters.

3. **Sell the gap, not the solution.** Reviewers fund **important problems**, not clever methods. Spend ~30% of the introduction establishing the gap with quantitative evidence; only then introduce the approach.

4. **Hypothesis-driven framing, not method-driven.**
   - Bad: "We propose to apply transformer X to problem Y."
   - Good: "We hypothesize that the bottleneck in Y is information loss in step Z; three Aims progressively isolate Z."

5. **Aims/objectives must be independent and parallel.** Each Aim should yield a publishable result on its own. Avoid serial dependencies ("Aim 2 only succeeds if Aim 1 works") — reviewers see this as fragile.

6. **Show feasibility with preliminary data.** A novel idea without preliminary results reads as speculative. For senior mechanisms (NIH R01, ERC AdG, large NSF programs), preliminary data is effectively required. For early-career mechanisms (NIH K, ERC StG, NSF CAREER), prior closely-related publications substitute.

7. **Risks acknowledged + mitigated.** Naming risks builds credibility. Every risk needs a concrete mitigation or fallback aim. Do **not** claim "no risks" — reviewers read this as naïve.

8. **Quantitative milestones.** Replace "we will improve performance" with "we will reduce p99 latency below 10ms at 1M QPS." Vague milestones cannot be evaluated.

9. **Match the reviewer panel.** NSF/NIH panels include researchers outside your exact subfield: define jargon, motivate at the discipline level, keep one accessible figure per Aim. ERC and DARPA panels are more specialist — slightly higher technical density acceptable.

10. **Reuse text within a proposal; never plagiarise across proposals.** Rebuilding similar text across proposals is fine, but **never copy verbatim** from a previously funded proposal — funder duplicate-detection systems (NIH eRA, EU F&T) flag this.

---

## CS / Systems / ML Discipline Notes

This skill assumes a CS / systems / ML proposal context, matching sibling skills `academic-writing` and `academic-reviewer`. Discipline-specific levers:

- **Compute justification is mandatory.** Request and justify GPUs/cluster time line-by-line — reviewers actively scrutinize compute budgets in ML proposals. Cite specific hardware (H100, MI300X) and node-hours.
- **Open-source / artifact commitments strengthen Broader Impact / Impact.** Cite prior released systems (GitHub URL + adoption metrics) to demonstrate track record.
- **Benchmark / dataset choice matters.** Name specific benchmarks (MLPerf, ImageNet-1K, LLaMA-70B inference) — vague "we will evaluate on standard benchmarks" reads as underdeveloped.
- **Reproducibility commitments** (artifact evaluation, Docker, deterministic builds) are increasingly graded. Mention them in Broader Impact and DMP.
- **Distinguish systems contributions from ML contributions.** Systems venues reward measured throughput/latency; ML venues reward generalization/sample efficiency. Frame the proposal toward the relevant program officer's portfolio.

---

## What Authors Must Do

1. Read the **current** solicitation/call. Funder requirements change yearly. (No network access: use stored values, state their 2026-11-12 verification date, and tell the user to confirm.)
2. Match section headers and length limits to the funder's template exactly.
3. Quantify every claim of importance, novelty, and feasibility.
4. Write Aims/Objectives that are independent, hypothesis-driven, and milestone-quantified.
5. Acknowledge risks with concrete mitigations.
6. Align budget to the work plan; justify every line item.
7. Submit via the funder's portal (Research.gov, eRA Commons, EU F&T, UKRI Funding Service) well before the deadline — portals lock at the deadline minute.

## What Authors Must Not Do

1. Exceed page or character limits — most funders desk-reject without review.
2. Use "novel", "first-ever", "revolutionary" without quantitative substantiation.
3. Submit a paper rewritten as a proposal — different genre, different evaluation criteria.
4. Promise more than the budget supports.
5. Hide risks or claim "no risks identified."
6. Recycle text verbatim across proposals (duplicate-detection flags this).
7. Treat Broader Impact / Impact as boilerplate — reviewers read it.
8. Submit without institutional pre-award review — most funders require sponsored-research-office sign-off.

---

## References

All reference files are routed in the Stage 1 table above (funder guides, pre-proposals/LOIs, section drafting, budget, biosketch/DMP, critique/resubmission). Identify the funder or task first, then load only the relevant file(s) from `references/`.
