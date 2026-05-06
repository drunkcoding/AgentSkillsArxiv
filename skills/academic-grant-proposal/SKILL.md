---
name: academic-grant-proposal
description: "Write academic grant proposals for major funders — NSF (CAREER, standard, CRII), NIH (R01, R21, K-series, F-series), ERC (Starting, Consolidator, Advanced), EU Horizon Europe, DARPA/DoD/DOE BAAs, and UKRI/EPSRC/Royal Society. Covers section drafting (Specific Aims, Project Description, Broader Impacts, Excellence/Impact/Implementation, Heilmeier Catechism), mock-reviewer critique against funder criteria, budget and budget justification, biosketches, Data Management Plans, and responses to reviewer critique on resubmission. Discipline focus: CS / Systems / ML, with examples aligned to compute-heavy research. Use when asked to draft, review, critique, revise, or budget any academic grant proposal, white paper, pre-proposal, or LOI."
---

# Academic Grant Proposal Writing

## Core Purpose

Produce **fundable** grant proposals — proposals that pass each funder's specific review rubric. A grant proposal is **not a research paper**: it sells future work, foregrounds significance and feasibility, and is evaluated by panels who skim. Optimize for the funder's published criteria, not for general academic prose.

**Guiding principle:** every paragraph must answer one of three reviewer questions — *"Why is this important?"*, *"Why will it work?"*, *"Why this team?"* If a paragraph answers none, cut it.

## Workflow

### Stage 1: Identify Funder + Mechanism (before drafting anything)

Funder and mechanism determine structure, page limits, evaluation criteria, and tone. **Read the current solicitation/call before writing.** Different funders use different terms for similar concepts (NSF "Intellectual Merit" ≈ ERC "Ground-breaking nature" ≈ Horizon "Excellence").

Route to the matching reference file:

| Funder | Trigger keywords | Load |
|---|---|---|
| **NSF** | NSF, CAREER, CRII, CISE, "Intellectual Merit", "Broader Impacts" | [references/nsf.md](references/nsf.md) |
| **NIH** | NIH, R01, R21, R03, K-award, F-award, "Specific Aims", SF424 | [references/nih.md](references/nih.md) |
| **ERC** | ERC, Starting Grant, StG, Consolidator, CoG, Advanced, AdG, "B1/B2", "ground-breaking" | [references/erc.md](references/erc.md) |
| **EU Horizon** | Horizon Europe, EIC, MSCA, "Excellence/Impact/Implementation", work package, deliverables | [references/horizon_europe.md](references/horizon_europe.md) |
| **DARPA/DoD/DOE** | DARPA, BAA, ARO, ONR, AFOSR, DOE, ASCR, Heilmeier, white paper | [references/darpa_dod_doe.md](references/darpa_dod_doe.md) |
| **UKRI/EPSRC/Royal Society** | UKRI, EPSRC, BBSRC, NERC, Royal Society, URF, "Case for Support", "Pathways to Impact" | [references/ukri.md](references/ukri.md) |

If the user asks generally without naming a funder, ask which agency/mechanism before drafting.

### Stage 2: Decompose into Sections

Most funders require the same logical components under different names. Map the user's request to one of these standard components and consult [references/proposal_sections.md](references/proposal_sections.md) for the cross-funder drafting playbook:

- **Aims / Objectives** (NIH Specific Aims, ERC B1 synopsis, Horizon Objectives, NSF "Goals")
- **Significance / Excellence** — why this matters
- **Innovation / Ground-breaking** — why this is novel beyond incremental work
- **Approach / Methodology** — technical plan, work packages, milestones, risk mitigation
- **Preliminary Results** — feasibility evidence (critical for NIH R01, ERC, NSF resubmissions)
- **Broader Impact / Impact** (NSF Broader Impacts, Horizon Impact, NIH Significance, UKRI Pathways)
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
- **Mentoring Plan** (NSF postdoc), **Sponsor Plan** (NIH F-awards)

### Stage 4: Self-Review and Reviewer-Style Critique

Before submission, run a mock-reviewer pass against the funder's published criteria. See [references/review_critique.md](references/review_critique.md) for the rubric-by-rubric checklist and common rejection reasons.

### Stage 5: Resubmission / Response to Reviewers (if applicable)

NIH, NSF, and ERC permit resubmissions with substantive revisions. Responses must be evidence-based and concrete. See [references/review_critique.md](references/review_critique.md) §Response-to-Reviewers.

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

1. Read the **current** solicitation/call. Funder requirements change yearly.
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

This skill loads funder-specific guidance on demand. Identify the funder first, then load only the relevant files.

**Funder-specific guides** (load the one matching the user's funder):
- [references/nsf.md](references/nsf.md) — NSF CAREER, standard, CRII; Intellectual Merit + Broader Impacts
- [references/nih.md](references/nih.md) — NIH R01, R21, R03, K-series, F-series; Specific Aims structure
- [references/erc.md](references/erc.md) — ERC Starting, Consolidator, Advanced; B1 synopsis + B2 proposal
- [references/horizon_europe.md](references/horizon_europe.md) — Horizon Europe collaborative projects, work packages, consortium
- [references/darpa_dod_doe.md](references/darpa_dod_doe.md) — DARPA BAAs, Heilmeier Catechism, DoD/DOE programs
- [references/ukri.md](references/ukri.md) — UKRI / EPSRC / Royal Society Case for Support, J-aQR

**Cross-cutting guides** (load when the activity matches):
- [references/proposal_sections.md](references/proposal_sections.md) — Section-by-section drafting playbook (Aims, Significance, Approach, Broader Impact)
- [references/budget_justification.md](references/budget_justification.md) — Budget construction and justification narrative
- [references/biosketch_dmp.md](references/biosketch_dmp.md) — Biosketch (NSF, NIH, ERC formats) and Data Management Plan templates
- [references/review_critique.md](references/review_critique.md) — Mock-reviewer rubric, common rejection reasons, response-to-reviewers for resubmissions
