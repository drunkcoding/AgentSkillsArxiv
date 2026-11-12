# Horizon Europe Proposals

> Facts last verified 2026-11-12 against the Horizon Europe Work Programme 2026-2027 General Annexes and the official EIC Pathfinder FAQ. Funder rules change with every work programme — confirm against the current call documents before relying on any limit or amount.

EU Framework Programme for Research and Innovation (2021-2027). **Collaborative, consortium-driven** — distinct from ERC (single-PI). CS/ML projects typically map to:

- **Pillar I**: ERC, MSCA (covered separately), Research Infrastructures
- **Pillar II**: Cluster 4 (Digital, Industry, Space) — most CS calls; Cluster 5 (Climate); Cluster 1 (Health)
- **Pillar III**: European Innovation Council (EIC) — Pathfinder (high-risk research), Transition, Accelerator (SME-led)

## Table of Contents

1. [Mechanism Selection](#mechanism-selection)
2. [Three-Criterion Evaluation: Excellence, Impact, Implementation](#three-criterion-evaluation-excellence-impact-implementation)
3. [Part A (Forms)](#part-a-forms)
4. [Part B (Technical Annex)](#part-b-technical-annex)
5. [Excellence Section (~22% of the page limit)](#excellence-section-22-of-the-page-limit)
6. [Impact Section (~22% of the page limit)](#impact-section-22-of-the-page-limit)
7. [Implementation Section (~55% of the page limit)](#implementation-section-55-of-the-page-limit)
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
| **EIC Pathfinder Open** | Bottom-up high-risk research | 100% | requested EU contribution up to €4M | consortium (≥2 independent entities in different EU/Associated countries; ≥3 entities need ≥3 countries); single legal entities **not** eligible |
| **EIC Pathfinder Challenges** | Top-down high-risk on stated themes | 100% | requested EU contribution up to €4M | single legal entities may apply (mid-caps and larger companies cannot apply alone) or consortia meeting the same composition rules |
| **EIC Transition** | Pathfinder → market | 100% | up to €2.5M | ≥1 (existing IP) |
| **MSCA Doctoral Networks** | PhD training networks | 100% | varies | ≥3 EU + ≥1 non-academic |

CS Cluster 4 frequent topics: trustworthy AI, HPC + AI convergence, edge AI, 6G, cybersecurity, quantum computing/communications.

## Three-Criterion Evaluation: Excellence, Impact, Implementation

Every full Horizon Europe application is scored on three criteria (General Annexes 2026-2027): each criterion is scored out of 5, and "the threshold for individual criteria will be 3. The overall threshold, applying to the sum of the three individual scores, will be 10." Scores are not weighted except that, to rank **Innovation Actions**, the Impact score is given a weight of 1.5. Proposals that pass both the individual and overall thresholds are considered for funding within the call budget; the rest are rejected. Confirm the thresholds in the call conditions.

| Criterion | Formal threshold | Informal heuristic (experience, not a rule) |
|---|---|---|
| **Excellence** | 3 / 5 | competitive calls often need 4.5+ |
| **Impact** | 3 / 5 | often 4.0+ |
| **Implementation** | 3 / 5 | often 4.0+ |

Overall formal threshold: 10 / 15. Half-point steps are commonly used (confirm in the evaluation form). The funding cut-off in a competitive call usually sits well above these formal thresholds, depending on how many proposals compete. For first-stage applications in two-stage calls only Excellence and Impact are scored; the individual threshold is 4 and the overall threshold is set per call (expected to be about 8 or 8.5). **Impact is where most proposals lose points** — it is treated as boilerplate by inexperienced authors but graded rigorously.

## Part A (Forms)

Administrative metadata via the EU Funding & Tenders Portal. Captures:
- Project title, acronym, abstract (≤2000 chars)
- Keywords, panel descriptors
- Consortium partners (PIC numbers), legal status, country
- Per-partner budget (personnel, equipment, travel, other direct, subcontracting, indirect)
- Ethics issues table

## Part B (Technical Annex)

Single PDF, page-limited per call. General Annexes 2026-2027: "Unless provided otherwise in the specific call/topic conditions, the limit for a full application is **40 pages**" (Coordination and support actions: 25; Programme co-fund: 65). "For topics using lump sum funding, the limit for 'Research and Innovation' actions and 'Innovation' actions is **45 pages**" (CSA: 28). A first-stage application is limited to 10 pages. Excess pages are made invisible to evaluators after the deadline. The page limits and the sections they cover are shown in the application template for your topic — **verify in the specific call topic**.

**Template note:** the section headings and per-section page allocations below are drafting heuristics (proportions of the applicable page limit: about 22% Excellence, 22% Impact, 55% Implementation, i.e. ≈9 + 9 + 22 pages of a 40-page limit or ≈10 + 10 + 25 pages of a 45-page limit). Take the exact headings, numbering and any per-section limits from the current Part B template for your topic.

Typical section headers in earlier templates (confirm in the current template before reusing):

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

## Excellence Section (~22% of the page limit)

Heuristic: ≈9 pp of a 40-page limit, ≈10 pp of a 45-page limit.

### 1.1 Objectives and Ambition (about one third of Excellence)
- **Specific, measurable objectives** (numbered O1, O2, … typically 4-6; informal heuristic)
- Ambition vs. state of the art — quantify gaps
- "Beyond-state-of-the-art" advances claim, mapped to objectives
- For high-risk topics (Pathfinder, RIAs in trustworthy AI): explicit risk-reward framing

### 1.2 Methodology (about two thirds of Excellence)
- Concept and overall methodology — diagram
- Per-objective methods, including theoretical/algorithmic foundations
- Interdisciplinary integration where relevant
- Open-science practices (FAIR data, open access publishing, reproducibility)
- Gender dimension — **mandatory consideration in research content where relevant**, evaluated under Excellence; for CS, address training-data bias, demographic generalization, AI fairness; document why N/A if it truly is

## Impact Section (~22% of the page limit)

Heuristic: ≈9 pp of a 40-page limit, ≈10 pp of a 45-page limit.

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

## Implementation Section (~55% of the page limit)

Heuristic: ≈22 pp of a 40-page limit, ≈25 pp of a 45-page limit.

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

EIC Pathfinder is closer to ERC in spirit (high-risk frontier research) but is generally consortium-based. Distinguishing features:

- **Pathfinder Open: single legal entities are not eligible** ("Applications from single legal entities are not eligible under the EIC Pathfinder Open call"); single entities can apply under **Pathfinder Challenges**, where they compete with consortia. Consortium composition rules are in the FAQ and call text
- Requested EU contribution of **up to €4 million** for both Pathfinder Open and Challenges (larger requests are possible if properly justified); eligible costs take the form of a lump sum
- Funds **science-toward-technology breakthroughs** — must articulate a future technology, not just science (expected TRL range typically 1-4)
- **From 2027, Pathfinder Open is two-stage**: Stage 1 short proposals (Part B up to **10 pages**, evaluated on Excellence and Impact, plus letters of commitment, which are mandatory) → top-ranked invited to Stage 2 full proposals (Part B up to **23 pages**, all three criteria); the interview takes place during the panel evaluation of Stage 2 proposals (10-minute pitch, then three clarifying questions)
- **Pathfinder Challenges**: Part B sections 1-3 up to **30 pages**, with extra requirements from the Challenge Guide
- **EIC Programme Manager** assigned post-award; portfolio-managed actively
- **EIC Pathfinder Challenges** are top-down: read the specific challenge text and Challenge Guide *very* carefully; the challenge defines acceptance criteria

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
- Association status changes over time and some topics restrict participation. The United Kingdom and Switzerland are on the General Annexes 2026-2027 list of countries associated to Horizon Europe, so their entities are normally eligible for funding. Association can exclude some instruments: the General Annexes state the UK is associated "with the only exception of the EIC fund (which is part of the EIC Accelerator of Horizon Europe that provides investment through equity or other repayable form), for award procedures implementing Union budget for the year 2024 and onwards". Do not exclude associated countries from the budget by default; check the current association list and the topic-level restrictions on the Funding & Tenders Portal and confirm before finalising the consortium
