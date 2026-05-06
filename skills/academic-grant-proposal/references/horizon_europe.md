# Horizon Europe Proposals

EU Framework Programme for Research and Innovation (2021-2027). **Collaborative, consortium-driven** — distinct from ERC (single-PI). CS/ML projects typically map to:

- **Pillar I**: ERC, MSCA (covered separately), Research Infrastructures
- **Pillar II**: Cluster 4 (Digital, Industry, Space) — most CS calls; Cluster 5 (Climate); Cluster 1 (Health)
- **Pillar III**: European Innovation Council (EIC) — Pathfinder (high-risk research), Transition, Accelerator (SME-led)

## Table of Contents

1. [Mechanism Selection](#mechanism-selection)
2. [Three-Criterion Evaluation: Excellence, Impact, Implementation](#three-criterion-evaluation-excellence-impact-implementation)
3. [Part A (Forms)](#part-a-forms)
4. [Part B (Technical Annex)](#part-b-technical-annex)
5. [Excellence Section (typically ~10 pp)](#excellence-section-typically-10-pp)
6. [Impact Section (~10 pp)](#impact-section-10-pp)
7. [Implementation Section (~25 pp)](#implementation-section-25-pp)
8. [Consortium Building](#consortium-building)
9. [EIC Pathfinder Specifics](#eic-pathfinder-specifics)
10. [Submission Logistics](#submission-logistics)

---

## Mechanism Selection

| Action Type | Purpose | Funding rate | Typical budget | Consortium |
|---|---|---|---|---|
| **RIA** (Research and Innovation Action) | Frontier research, basic/applied | 100% | €3-7M | ≥3 partners from ≥3 EU/Associated countries |
| **IA** (Innovation Action) | Closer-to-market | 70% (non-profits 100%) | €5-15M | ≥3/3 |
| **CSA** (Coordination and Support) | Coordination, networking | 100% | €1-3M | varies |
| **EIC Pathfinder Open** | Bottom-up high-risk research | 100% | up to €3M | ≥3/3 OR single applicant |
| **EIC Pathfinder Challenges** | Top-down high-risk on stated themes | 100% | up to €4M | ≥3/3 |
| **EIC Transition** | Pathfinder → market | 100% | up to €2.5M | ≥1 (existing IP) |
| **MSCA Doctoral Networks** | PhD training networks | 100% | varies | ≥3 EU + ≥1 non-academic |

CS Cluster 4 frequent topics: trustworthy AI, HPC + AI convergence, edge AI, 6G, cybersecurity, quantum computing/communications.

## Three-Criterion Evaluation: Excellence, Impact, Implementation

Every Horizon Europe proposal is scored on three equally weighted criteria:

| Criterion | Weight | Threshold | Pass mark |
|---|---|---|---|
| **Excellence** | 1/3 | 3.0 / 5 | usually need 4.5+ |
| **Impact** | 1/3 | 3.0 / 5 | usually need 4.0+ |
| **Implementation** | 1/3 | 3.0 / 5 | usually need 4.0+ |

Score 0-5 per criterion (half points allowed); fail any threshold → unfunded. Funded proposals typically score 14.0+/15. **Impact is where most proposals lose points** — it is treated as boilerplate by inexperienced authors but graded rigorously.

## Part A (Forms)

Administrative metadata via the EU Funding & Tenders Portal. Captures:
- Project title, acronym, abstract (≤2000 chars)
- Keywords, panel descriptors
- Consortium partners (PIC numbers), legal status, country
- Per-partner budget (personnel, equipment, travel, other direct, subcontracting, indirect)
- Ethics issues table

## Part B (Technical Annex)

Single PDF, page-limited per call. Typical RIA limit: **45 pages** for Sections 1+2+3 (Excellence + Impact + Implementation). Sections 4 (consortium descriptions) and 5 (ethics) plus annexes are **outside** the 45-page count for most calls — **verify in the specific call topic**.

Mandatory section headers (do not invent your own — reviewers look for these literally):

```
1. Excellence
   1.1 Objectives and Ambition
   1.2 Methodology
2. Impact
   2.1 Project's Pathways towards Impact
   2.2 Measures to Maximise Impact
3. Quality and Efficiency of the Implementation
   3.1 Work Plan and Resources
   3.2 Capacity of Participants and Consortium as a Whole
4. Members of the Consortium (per-partner descriptions)
5. Ethics and Security
```

## Excellence Section (typically ~10 pp)

### 1.1 Objectives and Ambition (~3-4 pp)
- **Specific, measurable objectives** (numbered O1, O2, … typically 4-6)
- Ambition vs. state of the art — quantify gaps
- "Beyond-state-of-the-art" advances claim, mapped to objectives
- For high-risk topics (Pathfinder, RIAs in trustworthy AI): explicit risk-reward framing

### 1.2 Methodology (~6-7 pp)
- Concept and overall methodology — diagram
- Per-objective methods, including theoretical/algorithmic foundations
- Interdisciplinary integration where relevant
- Open-science practices (FAIR data, open access publishing, reproducibility)
- Gender dimension — **mandatory consideration in research content where relevant**, evaluated under Excellence; for CS, address training-data bias, demographic generalization, AI fairness; document why N/A if it truly is

## Impact Section (~10 pp)

### 2.1 Pathways towards Impact
- **Expected outcomes** (immediate, after project end)
- **Expected wider scientific, economic, societal impacts** (2-5 years and 5+ years out)
- Explicit mapping to **Key Impact Pathways (KIPs)** — call topic specifies which KIPs the project should address (e.g., "Strengthening Europe's AI ecosystem", "Open Strategic Autonomy")
- **Magnitude and significance** — quantify (jobs, market size, citations, policy uptake)

### 2.2 Measures to Maximise Impact
- **Communication** — public engagement, plain-language outputs
- **Dissemination** — papers, conferences, workshops, open-source releases
- **Exploitation** — IP management, commercial pathways, licensing model, standards bodies
- **Plan for Communication, Dissemination, and Exploitation (PCDE)** — reviewers expect a structured table of activities, channels, audiences, timelines, KPIs

CS / open-source hint: explicit commitment to upstream contributions to widely used projects (e.g., PyTorch, vLLM, OpenStack), benchmark suites (MLPerf), and standards bodies (IEEE, IETF, MLCommons) reads strongly under Exploitation.

## Implementation Section (~25 pp)

### 3.1 Work Plan and Resources

**Work Packages (WPs)** — typical project has 5-8 WPs:

- **WP1**: Project Management (always)
- **WP2-WPn**: Scientific WPs (one per major thrust)
- **WP-final-1**: Dissemination, Exploitation, Communication
- **WP-final**: Ethics (only if substantial ethics workload)

Per WP, fill the standard tables:

- **WP description** — objectives, tasks, lead partner, participating partners, person-months per partner, start/end month
- **Deliverables** (D-numbers, e.g., D2.1) — due dates, dissemination level (Public/Sensitive)
- **Milestones** (MS-numbers) — verification means, due dates, gating future WPs
- **Critical Risks Register** — risk description, likelihood (Low/Med/High), severity, mitigation, WPs affected

Plus:
- **Pert chart** — WP interdependencies
- **Gantt chart** — month-by-month timeline
- **Effort table** — person-months per partner per WP

### 3.2 Capacity of Participants and Consortium

Demonstrate the consortium can execute. Address:
- Each partner's role and unique expertise
- Complementarity of partners (no overlap, no gaps)
- Track record of partners on similar projects
- Geographic balance (often weighted in CSAs and broader programmes)
- Industry-academia balance where relevant

## Consortium Building

Horizon Europe is **fundamentally collaborative**. Strong consortia have:

- **3+ partners from 3+ different EU/Associated countries** (mandatory minimum for most calls)
- **Topic-aligned competences**: every WP has a partner with demonstrable prior work on it
- **Industry/academia mix** for IA and Cluster 4 — at least 1 SME or industry partner usually expected
- **A coordinator with prior Horizon coordination experience** (graded under 3.2)
- **Geographic diversity** — Widening Countries (EU-13 + associated) participation often boosts scores

Partner search tools: EU Funding & Tenders portal Partner Search, CORDIS database of past projects, NCP (National Contact Point) network in your country.

## EIC Pathfinder Specifics

EIC Pathfinder is closer to ERC in spirit (high-risk frontier research) but consortium-based. Distinguishing features:

- Either **single applicant** (Pathfinder Open only) or **3+ partners** consortium
- Funds **science-toward-technology breakthroughs** — must articulate a future technology, not just science
- **Three-step evaluation**: remote → consensus → interview (for shortlisted)
- **15-page Part B** for Pathfinder Open (much shorter than RIA)
- **EIC Programme Manager** assigned post-award; portfolio-managed actively
- **EIC Pathfinder Challenges**: top-down topics — read the specific challenge text *very* carefully; the challenge defines acceptance criteria

## Submission Logistics

- **Portal:** EU Funding & Tenders Opportunities Portal (https://ec.europa.eu/info/funding-tenders/opportunities/portal/)
- **PIC number** — every legal entity needs a 9-digit Participant Identification Code; obtain via the portal **before** filling consortium forms
- **Calls** — published in the biennial Work Programme; typical call open windows are 4-6 months
- **Single deadline** (no rolling) for most calls, with hard cut-off times in Brussels time
- **Ethics screening** — automatic flagging of human/animal/dual-use issues; some require Ethics Review Procedure post-submission
- **Common rejection reasons:**
  - Impact section reads as boilerplate or unsupported by quantitative claims
  - Methodology not specific enough, no interdisciplinary integration
  - Missing gender dimension where relevant (drops Excellence score)
  - Consortium lacks complementarity or geographic balance
  - Risk register absent or naïve ("no risks identified")
  - Work plan not aligned with budget (effort tables don't sum)
- **Resubmission:** allowed on subsequent calls in the same Work Programme cycle; revise based on Evaluation Summary Report (ESR) feedback

## CS / Systems / ML Notes for Horizon Europe

- Trustworthy AI, GenAI, foundation models, and AI Act compliance are **active** topics in Cluster 4 — align language with the EU AI Act risk categories
- **EuroHPC JU** (separate but Horizon-adjacent) funds compute and HPC-AI projects — pre-exascale and exascale machines available as in-kind compute
- **GAIA-X** / **EOSC** alignment scores points in data-infrastructure proposals
- Open-source mandates: Horizon Europe defaults to **open-source software, open-access publishing (Plan S compliant), FAIR data** — write the DMP accordingly
- Exclude UK/CH/IL etc. from financial budgets only when current Work Programme excludes them — eligibility for association status changes; verify in the specific call
