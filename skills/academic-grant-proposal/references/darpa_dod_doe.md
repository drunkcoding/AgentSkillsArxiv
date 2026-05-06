# DARPA / DoD / DOE Proposals

US Department of Defense and Department of Energy research funding. Proposals are judged on **disruption potential and concrete deliverables**, not academic rigor for its own sake. Different cultural conventions from NSF/NIH.

## Table of Contents

1. [Agency Map](#agency-map)
2. [BAA / FOA Anatomy](#baa--foa-anatomy)
3. [Two-Phase Process: White Paper → Full Proposal](#two-phase-process-white-paper--full-proposal)
4. [The Heilmeier Catechism](#the-heilmeier-catechism)
5. [Proposal Volume Structure](#proposal-volume-structure)
6. [Volume I (Technical) Drafting](#volume-i-technical-drafting)
7. [Milestones, Metrics, and TRLs](#milestones-metrics-and-trls)
8. [Volume II (Cost)](#volume-ii-cost)
9. [DoD-Specific (ARO, ONR, AFOSR)](#dod-specific-aro-onr-afosr)
10. [DOE-Specific (ASCR, BES, ARPA-E)](#doe-specific-ascr-bes-arpa-e)
11. [Submission Logistics](#submission-logistics)

---

## Agency Map

| Agency | Office/Program | CS/ML focus |
|---|---|---|
| **DARPA** | I2O, MTO, DSO, ITO | High-risk transformative; AI/ML/cyber/HPC |
| **ARO** (Army Research Office) | Computing Sciences | Robotics, autonomy, ISR analytics |
| **ONR** (Office of Naval Research) | Code 31/32 | Autonomy, AI for naval ops, HPC |
| **AFOSR** (Air Force Office of Scientific Research) | RTA1/RTA2 | AI/ML, cyber, autonomy |
| **DOE / ASCR** | Advanced Scientific Computing Research | Exascale, HPC, scientific ML |
| **DOE / BES** | Basic Energy Sciences | AI for materials, scientific discovery |
| **ARPA-E** | (DOE's high-risk arm) | Energy + AI, mission-driven |
| **IARPA** | (intelligence-community DARPA analog) | Specific intelligence challenges |

DARPA programs are time-limited (typically 4-year arc): a Program Manager (PM) launches a program, runs it 3-4 years, sunset. Program selection is **PM-driven**: contact the PM before submitting.

## BAA / FOA Anatomy

DoD: **Broad Agency Announcement (BAA)**. DOE: **Funding Opportunity Announcement (FOA)**. Read these documents in full — they define eligible topics, mandatory sections, evaluation factors, and page limits per section.

Common BAA sections:

1. **Funding Opportunity Description** — what the agency wants, scope, technical thrusts (TAs)
2. **Award Information** — total funding, # awards, period of performance
3. **Eligibility** — universities, industry, FFRDC restrictions
4. **Application & Submission Information** — required volumes, formats, page limits
5. **Application Review Information** — evaluation factors and **their relative weight** (read carefully — this is the rubric)
6. **Federal Award Administration Information**
7. **Federal Awarding Agency Contacts** (the PM's name and email)
8. **Other Information** — appendices, FAQs

DARPA BAAs additionally contain a **technical area description** specifying the program's Heilmeier framing.

## Two-Phase Process: White Paper → Full Proposal

Most DARPA / DoD BAAs use a two-step process:

### Phase 1: White Paper / Concept Paper (5-15 pp)

- Compact pitch of the technical approach
- Heilmeier-style framing
- High-level metrics and milestones
- Team and rough budget envelope
- Agency reviews and **encourages or discourages** full proposal — non-binding but strong signal

**Encourage rate is typically 20-40%.** Discouraged proposals can still submit but rarely fund.

### Phase 2: Full Proposal (typically 30-60 pp Vol I + Vol II cost)

- Full technical proposal (Volume I)
- Full cost proposal (Volume II)
- Optional: Past Performance Volume, Appendices

PMs frequently **invite phone calls** between Phase 1 and Phase 2 to refine the technical approach. Take the call — it is a signal of interest.

## The Heilmeier Catechism

Devised by George Heilmeier (former DARPA Director). Every DARPA white paper and proposal must answer these nine questions, **explicitly and concisely**. Many BAAs require these as a labeled section.

1. **What are you trying to do?** Articulate objectives in plain language. No jargon.
2. **How is it done today, and what are the limits of current practice?**
3. **What is new in your approach and why do you think it will be successful?**
4. **Who cares?** If you succeed, what difference does it make?
5. **What are the risks?**
6. **How much will it cost?**
7. **How long will it take?**
8. **What are the mid-term and final "exams" to check for success?**
9. **(Optional)** What is the path to transition / scale?

**Best practice:** include a 1-page Heilmeier-formatted summary at the front of every DoD/DARPA white paper — even when not explicitly required. Reviewers love it.

## Proposal Volume Structure

DoD proposals split into **Volumes**. Common configuration for DARPA:

- **Volume I — Technical and Management Proposal** (page-limited per BAA)
- **Volume II — Cost Proposal** (no page limit, structured workbook)
- **Volume III — Past Performance** (sometimes)
- **Volume IV — Appendices** (CVs, letters, IP assertions, sometimes outside page limit)

DOE FOAs vary; common is single Project Narrative + budget + biosketches.

## Volume I (Technical) Drafting

Recommended structure (tailor to specific BAA):

1. **Executive Summary / Heilmeier Summary** (1-2 pp)
2. **Goals and Impact** (2-3 pp) — what the program changes if it succeeds
3. **Technical Approach** (10-20 pp)
   - Per Technical Area (TA): challenge, approach, novelty
   - Architecture diagram
   - Algorithmic / hardware details
   - Integration plan with other TAs (if multi-TA program)
4. **Innovation and Disruption** (1-2 pp) — explicit comparison to SOTA, beat-on-metric claims
5. **Quantitative Milestones and Metrics** (2-3 pp) — phase-by-phase, with numerical targets
6. **Schedule / Phasing** (1 pp) — Gantt
7. **Risk and Mitigation** (1-2 pp) — explicit risk register
8. **Team and Organization** (2-3 pp) — PI, key personnel, partner roles, management plan
9. **Transition Plan** (1 pp) — who consumes the result (a Service, a downstream program, a standards body)
10. **Statement of Work (SOW)** (separate annex; legally binding) — task-level breakdown, deliverables, dates

DARPA Volume I is **direct, declarative, action-oriented**. Cut hedging. Reviewers skim — use bold for metric claims, tables for milestones.

## Milestones, Metrics, and TRLs

DoD/DARPA reviewers expect quantitative milestones, often phrased as **"go/no-go" decision gates** with TRL (Technology Readiness Level) progression.

### TRL Scale (DoD/NASA-aligned)
- TRL 1-2: basic principles / concept
- TRL 3: experimental proof of concept
- TRL 4: lab validation
- TRL 5: relevant-environment validation
- TRL 6: relevant-environment prototype
- TRL 7: operational-environment prototype
- TRL 8-9: deployment/operation

DARPA programs typically span TRL 3 → TRL 6. State your starting TRL and target TRL.

### Milestone format
```
M1.1 (Month 12): Demonstrate [capability] on [benchmark/dataset] achieving [metric ≥ threshold].
   Verification: [how the agency confirms success]
   Go/no-go: continue to Phase 2 if metric ≥ threshold.
```

Vague milestones ("we will report results") fail. Quantitative milestones with verification methods pass.

## Volume II (Cost)

Cost proposals are **scrutinized**. DoD requires DCAA-compliant cost accounting. Typical structure:

- **Cost Summary** — by year, by partner, by category
- **Personnel** — PI, co-I, postdoc, student labor; salary by year with 2-3% escalation; effort percent
- **Fringe Benefits** — institutional rate, applied to salary
- **Travel** — itemized: # trips × destination × cost
- **Equipment** — items >$5K, with quotes
- **Materials/Supplies** — itemized
- **Consultants/Subcontracts** — separate cost narratives per subaward
- **Indirect (F&A)** — institutional negotiated rate, applied to MTDC
- **Other Direct Costs** — publication, compute purchases

DoD requires **detailed budget narrative** justifying each line. Compute / cloud GPU lines need quote attachments. Subcontract budgets must be separately certified.

## DoD-Specific (ARO, ONR, AFOSR)

Single-investigator-friendly mechanisms (lower budget than DARPA, longer term, more academic in tone):

- **ARO Single Investigator** — typically $500K over 3 years, white-paper first
- **ONR YIP** (Young Investigator Program) — early-career, ~$510K over 3 yr
- **AFOSR YIP** — early-career, $450K over 3 yr
- **MURI** (Multidisciplinary University Research Initiative) — $1.5M/yr × 3-5 yr × team of 3-7 PIs

**MURI is the largest DoD basic-research mechanism**: topics published annually (~24 topics), team responds with white paper then full proposal. Highly competitive (~5%). Strategic differentiators: multidisciplinarity (real, not bolted on), Heilmeier framing, transition plan to a Service.

## DOE-Specific (ASCR, BES, ARPA-E)

DOE basic research differs from DoD:

- **ASCR** funds AI for science, exascale, scientific machine learning, applied math. Calls come via FOAs at https://science.osti.gov/grants
- DOE proposals typically **20-25 pages Project Narrative**, single FOA-defined structure
- **DOE National Lab partnerships** strengthen proposals — co-PI from a National Lab brings facility access (Argonne ALCF, Oak Ridge OLCF, NERSC) and DOE familiarity
- **ARPA-E** uses DARPA-style Heilmeier/program-manager-driven model; ~$2-5M / 2-3 yr awards focused on energy applications

DOE is **mission-driven**: align with one of DOE's strategic priorities (clean energy, scientific discovery, national security). Proposals that look like generic ML research without an energy/science mission are filtered.

## Submission Logistics

- **DARPA / DoD portal:** SAM.gov + agency-specific systems (DARPA BAA Tool, ARO eBRAP)
- **DOE portal:** PAMS (Portfolio Analysis and Management System) at https://pamspublic.science.energy.gov
- **SAM.gov registration** required for entity (institution) plus individual roles — allow ≥2 weeks if not registered
- **CAGE Code, UEI** required for all institutions
- **Classification:** most CS/ML BAAs are **unclassified**. Some DARPA programs require Secret/Top Secret personnel clearance — check the BAA's facility/personnel security clauses
- **Restrictions on foreign nationals:** some BAAs exclude or restrict participation by certain countries' nationals (especially China-related concerns under research-security policies). Verify in the specific BAA before listing students/postdocs
- **Common rejection reasons:**
  - White paper not encouraged → still submitted full proposal
  - Heilmeier not addressed
  - Milestones not quantitative or no verification method
  - Transition plan absent — DARPA cares deeply who picks up the technology
  - Cost not aligned with statement of work
  - Risk treatment naïve

## CS / Systems / ML Notes for DARPA/DoD/DOE

- **DARPA AI Forward / AI Cyber Challenge / Trojan AI / explainable-AI programs** are the historical high-volume CS programs. New DARPA programs in foundation-model robustness, post-quantum, autonomy at scale appear regularly
- **Compute access**: DoD HPCMP (High Performance Computing Modernization Program) allocations available to DoD-funded researchers — mention in Facilities
- **Open-source release** is increasingly accepted by DARPA but check the data-rights clauses in the BAA — some programs assert Government Purpose Rights or Unlimited Rights over funded software
- **Reach out to the PM**: DARPA program managers actively engage with potential performers. Do not blast cold; come with a focused 2-page concept that maps to their published vision
