# Cross-Funder Section Drafting Playbook

Most funders require the same logical components under different names. This file gives a section-by-section playbook that maps to NSF/NIH/ERC/Horizon/UKRI terminology.

## Table of Contents

1. [Aims / Objectives / Specific Aims](#aims--objectives--specific-aims)
2. [Significance / Excellence / Importance](#significance--excellence--importance)
3. [Innovation / Ground-breaking / Novelty](#innovation--ground-breaking--novelty)
4. [Approach / Methodology / Research Plan](#approach--methodology--research-plan)
5. [Preliminary Results / Feasibility Evidence](#preliminary-results--feasibility-evidence)
6. [Broader Impact / Impact / Pathways](#broader-impact--impact--pathways)
7. [Team / Track Record / PI Qualifications](#team--track-record--pi-qualifications)
8. [Timeline / Work Plan / Gantt](#timeline--work-plan--gantt)
9. [Risks and Mitigation](#risks-and-mitigation)
10. [Management Plan (multi-PI / consortium)](#management-plan-multi-pi--consortium)

---

## Aims / Objectives / Specific Aims

**Funder names:** NIH "Specific Aims"; NSF "Goals" / "Research Thrusts"; ERC B1 "Objectives"; Horizon "Objectives"; UKRI "Objectives".

### Universal pattern

3-4 numbered, **independent**, parallel Aims. Each Aim:
- Begins with a strong action verb (Determine, Develop, Test, Characterize, Quantify, Build)
- Has a stated working hypothesis
- Has a measurable outcome with a specific metric
- Stands alone (would yield a publishable result if other Aims fail)

```
Aim 1: [Verb] [object]. Hypothesis: [H1]. We will [approach], measuring [metric].
   Expected outcome: [quantitative target].
Aim 2: [Verb] [object]. Hypothesis: [H2]. We will [approach], measuring [metric].
Aim 3: [Verb] [object]. Hypothesis: [H3]. We will [approach], measuring [metric].
```

### Strong vs weak verbs

| Strong | Weak |
|---|---|
| Determine, Develop, Test, Build, Characterize, Quantify, Define | Study, Investigate, Explore, Examine, Look at, Consider |

### Independence test

Mentally remove Aim 1's success: can Aims 2 and 3 still execute and produce results? If no, restructure. Reviewers explicitly flag dependent Aims as a feasibility risk.

### Number of Aims

| Funder/Mechanism | Typical |
|---|---|
| NIH R01 | 3 |
| NIH R21 | 2 |
| NSF (any) | 3-4 thrusts |
| ERC StG/CoG | 4-6 objectives |
| Horizon RIA | 4-7 objectives |
| DARPA white paper | 3-5 TAs |

More than 5 Aims signals scope creep; reviewers cut down rather than reward.

## Significance / Excellence / Importance

**Funder names:** NIH "Significance"; NSF "Intellectual Merit" (also Broader Impacts); ERC "Ground-breaking nature"; Horizon "Excellence"; UKRI "Quality, Importance, National Importance".

### What reviewers want

- Quantified evidence the problem matters (incidence, market size, scaling pressure, knowledge gap with citations)
- Explanation of **why prior approaches fail** — be specific, not "X has limitations"
- A clear statement of what changes if the project succeeds — what textbook, clinical guideline, or computational practice gets updated

### Drafting template

```
Paragraph 1 — Magnitude: [Problem] affects [N people / costs $M / blocks Y deployments].
Paragraph 2 — Gap: Current approaches [A1, A2, A3] fall short because [specific limitation].
Paragraph 3 — Opportunity: Recent advances in [enabling technology] now make it possible to [specific advance].
Paragraph 4 — Promise: If successful, this project will [specific transformative outcome], unlocking [downstream consequences].
```

### Common failures

- Generic motivation ("AI is important")
- Old citations (>5 years) for fast-moving fields without contextual update
- Equating "novelty" with "significance" — they are different criteria
- Writing this section last and underweighting it

## Innovation / Ground-breaking / Novelty

**Funder names:** NIH "Innovation"; NSF embedded in Intellectual Merit; ERC "Ground-breaking"; Horizon "Excellence — Ambition vs SoTA"; UKRI "Novelty".

### Two valid axes of innovation

1. **Conceptual** — new theoretical framework, new hypothesis, new problem framing
2. **Methodological** — new measurement, new algorithm, new instrument enabling previously-impossible studies

State which axis explicitly. "We propose deep learning for X" is not innovative; "We propose [specific architectural choice] that breaks the [known barrier] of [SOTA approach]" is.

### Differentiate from prior work explicitly

```
Innovation: This work goes beyond [prior approach P1, P2] in three ways:
  I1. We address [aspect prior work avoided].
  I2. We replace [their assumption] with [our weaker / stronger assumption], enabling [new capability].
  I3. We exploit [new enabling resource — dataset, hardware, theoretical result] unavailable to prior work.
```

### Funder-specific calibration

| Funder | Risk tolerance |
|---|---|
| NIH R01 | Moderate — innovation is criterion 2, must be feasible |
| NIH R21 | High — exploratory mechanism rewards risk |
| NSF | Moderate — incremental work survives if elegantly executed |
| ERC | **Maximum** — incremental ambition fails; reviewers demand bold |
| DARPA | High — disruption is the point |
| Horizon RIA | Moderate-high; pair ambition with feasibility |

## Approach / Methodology / Research Plan

**Funder names:** NIH "Approach"; NSF "Research Plan"; ERC "Methodology"; Horizon "Methodology"; UKRI "Programme of Work / Workpackages"; DARPA "Technical Approach".

### Per-Aim/WP structure

For each Aim or work package:

1. **Rationale and Hypothesis** (paragraph)
2. **Preliminary Data / Prior Art** (figure(s) + brief narrative)
3. **Experimental / Algorithmic Design** (detailed methods)
4. **Specific tasks / steps** (numbered, with leads)
5. **Expected Outcomes** (quantitative)
6. **Pitfalls and Alternative Strategies** (named risks + mitigations)
7. **Success Criteria / Milestones** (quantitative)

### Methodology depth calibration

| Audience | Depth |
|---|---|
| NSF/NIH panels (mixed-discipline) | Self-contained: define algorithms, datasets, metrics |
| ERC PE6 panel (discipline) | Higher technical density; assume basic CS literacy |
| DARPA reviewers (technical PMs) | Architectural diagrams, integration plans; less background |

### CS/ML-specific elements

Always include:
- Datasets with sample sizes, data splits, licensing
- Baselines (named systems, with citations)
- Hardware / compute resources (GPU type, cluster name, allocation)
- Software stack and reproducibility commitments

## Preliminary Results / Feasibility Evidence

**Funder names:** NIH "Preliminary Studies" (within Approach); NSF "Results from Prior Support"; ERC implicit in methodology; Horizon "Capacity"; UKRI "Track Record".

### What counts as preliminary data

- Published or unpublished experiments showing the approach works at small scale
- Pilot benchmark numbers
- Successful prototype implementations
- Theoretical results justifying the approach

### Required by funder

| Funder | Required |
|---|---|
| NIH R01 | Heavily expected — usually a section per Aim |
| NIH R21 | Encouraged but not strictly required |
| NSF (CAREER, Small) | Some preliminary work expected; Results from Prior Support if PI has had NSF funding |
| ERC StG | Limited; relies more on PI's published track record |
| ERC AdG | Substantial — track record carries the role of preliminary data |
| DARPA | Concept feasibility; full preliminary study not required |

### When preliminary data is missing

For early-career mechanisms or genuinely new directions, substitute:
- Closely related published papers by the PI
- Theoretical analysis showing feasibility
- Successful preliminary implementations on adjacent problems
- Letters from collaborators committing data/access

## Broader Impact / Impact / Pathways

**Funder names:** NSF "Broader Impacts" (mandatory criterion); NIH "Significance" + DMP; ERC limited; Horizon "Impact" (1/3 of score); UKRI "Pathways to Impact" (now embedded).

### Framework: Beneficiaries × Activities × Evidence

For each section:

| Beneficiary | Activities | Evidence of credibility |
|---|---|---|
| Other researchers | Open-source software, datasets, benchmarks | GitHub URL of prior releases + adoption metrics |
| Industry | Partnerships, licensing, secondments | Letters of support with named contacts |
| Students | Course integration, REU, CDT slots | Specific course numbers; named programmes |
| Society | Public engagement, policy briefs | Named outlets; prior op-eds, government testimony |
| Underrepresented groups | Recruitment plans, mentoring | MSI/HBCU partnerships; named programmes |

### What scores well in CS/ML proposals

- **Open-source artifacts** with prior adoption (cite GitHub stars, downloads, dependent projects)
- **Released datasets / benchmarks** that became community standards
- **Course integration** — name the course, semester, # students
- **Industry partnerships** with concrete commitments (compute, data, secondments) — letters in appendix
- **Standards / policy** engagement — IETF, IEEE, MLCommons, AI Act consultations
- **Diverse training** — REU sites, CDT cohorts, named partnerships with MSI/HBCU/UK Widening Participation institutions

### What fails

- "We will publish papers and give talks" — papers are research output, not impact
- Unsigned, future-tense industry commitments
- Generic "we will engage the public" without specific outlets or formats
- Boilerplate copied across proposals (funder duplicate detection flags this)

## Team / Track Record / PI Qualifications

**Funder names:** NIH "Biosketch + Personal Statement"; NSF "Biosketch + Current/Pending"; ERC "Track Record"; Horizon "Capacity of Participants"; UKRI "R4RI / Track Record".

### What reviewers grade

- Prior delivery on similar-scale projects
- Publications relevant to the proposal (not just total publication count)
- Technical match between team and Aims (every Aim should have a clear lead)
- Independence from PhD/postdoc supervisors (early-career)
- Diversity of expertise across Aims (no single point of failure)

### Drafting the Team subsection of Approach/Implementation

```
The team brings the necessary expertise:
- PI [name] led [system X], adopted by [users]; relevant to Aim 1 and Aim 3.
- Co-PI [name] developed [technique Y]; relevant to Aim 2.
- [Senior personnel] contributes [data/access/instrument] (letter of support, App N).
- A [postdoc / PhD student] will be hired to lead [WP].
```

Match every Aim to a named lead with cited prior work.

## Timeline / Work Plan / Gantt

**Funder names:** universal — "Timeline", "Schedule", "Workplan", "Gantt".

### Required elements

- Year-by-year (or month-by-month for ≤2-yr projects) breakdown
- Per Aim/WP: start month, end month, key milestones
- Personnel allocation across Aims/years
- Dependencies between Aims (acknowledge but minimize)
- **Decision gates** for high-risk programs (DARPA go/no-go)

### Format

| Length | Best format |
|---|---|
| ≤2 years | Quarterly Gantt chart (4-quarter rows × Aim columns) |
| 3-5 years | Annual Gantt + milestone table |
| Multi-WP (Horizon, DARPA) | Pert chart + Gantt + milestone/deliverable table |

Always check for **conflicts**: Person X on 80% Aim 1 and 80% Aim 2 in Year 2 sums to 160%.

## Risks and Mitigation

**Funder names:** NIH "Pitfalls and Alternative Strategies"; ERC "Risks"; Horizon **"Critical Risks Register"** (mandatory table); DARPA "Risks"; UKRI typically embedded.

### Risk register format (Horizon-style; works everywhere)

| Risk ID | Description | Likelihood | Severity | WPs | Mitigation |
|---|---|---|---|---|---|
| R1 | Dataset access denied | Med | High | WP2 | Secondary dataset secured (App C); proxy benchmark |
| R2 | Compute over budget | Low | Med | WP3 | Pre-allocated NAIRR access; cloud fallback budgeted |
| R3 | Algorithm fails to converge | Med | Med | WP4 | Alternative training scheme prepared (preliminary results in Sec 2.3) |

### What strong risk treatment looks like

- 3-7 named risks (not "no risks identified")
- Concrete, **already-prepared** mitigations
- Mitigations referenced in Aims/WPs ("Aim 2 includes a fallback ablation if R3 materializes")

## Management Plan (multi-PI / consortium)

Required for: NSF multi-PI, NIH multi-PI MPI Plan, Horizon (always), DARPA team proposals, UKRI Programme Grants.

### Address

- Decision-making authority and dispute resolution
- Communication cadence (weekly/monthly/quarterly meetings, types)
- Coordination instruments (shared repository, project tracker, advisory board)
- Authorship and IP policy
- Annual review and corrective-action process
- Budget reallocation procedures

### NIH MPI specifics

NIH multi-PI requires a **Leadership Plan** addressing the above. Reviewers explicitly check this for multi-institution proposals.

### Horizon specifics

Beyond management plan: **General Assembly**, **Project Coordinator**, **WP leads**, **Steering Committee**, **Advisory Board**, **Innovation Board**, **Ethics Advisor** (if applicable). Standard Horizon governance terminology should appear by name.
