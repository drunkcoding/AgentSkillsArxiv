# Budget and Budget Justification

Budgets are read **carefully** — reviewers check that costs match the scientific work plan. A mismatched budget triggers reduced scores even when the science is strong.

## Table of Contents

1. [Universal Budget Categories](#universal-budget-categories)
2. [Funder-Specific Frameworks](#funder-specific-frameworks)
3. [Budget Justification Narrative Pattern](#budget-justification-narrative-pattern)
4. [Personnel](#personnel)
5. [Equipment](#equipment)
6. [Travel](#travel)
7. [Materials, Supplies, Compute](#materials-supplies-compute)
8. [Subcontracts / Subawards / Linked Third Parties](#subcontracts--subawards--linked-third-parties)
9. [Indirect Costs (F&A / Overhead)](#indirect-costs-fa--overhead)
10. [CS / ML Compute Justification](#cs--ml-compute-justification)
11. [Common Budget Failures](#common-budget-failures)

---

## Universal Budget Categories

| Category | Description |
|---|---|
| **Personnel (Salaries)** | PI, co-I, postdoc, student, technician, admin |
| **Fringe Benefits** | Institutional rate × salary |
| **Equipment** | Items >$5K (US) or >£10K (UK), tangible, durable |
| **Travel** | Domestic/international conference, fieldwork, partner visits |
| **Materials/Supplies** | Consumables, software licenses, small instruments |
| **Compute / Cloud** | GPU/CPU compute purchases, cloud credits |
| **Publication / Open Access** | APC fees |
| **Consultants** | External experts paid hourly/daily |
| **Subawards / Subcontracts** | Work executed by partner institutions |
| **Other Direct Costs** | Conference fees, participant compensation, recruiting |
| **Indirect (F&A / Overhead)** | Institutional rate on direct costs |

## Funder-Specific Frameworks

| Funder | Budget Format | Typical narrative length | Indirect (F&A) handling |
|---|---|---|---|
| **NSF** | Detailed line-item via Research.gov | 5 pp narrative | Institutional negotiated rate; CISE typically allows up to ~58% MTDC |
| **NIH (modular)** | Round to $25K modules up to $250K direct/yr | Brief "Personnel + Other" justification | Negotiated rate; capped at federal rate on subawards |
| **NIH (detailed)** | Required when direct >$250K/yr | Full line-item narrative | Negotiated rate |
| **ERC** | EU lump-sum or actual costs (changing) | 1-2 pp resources section | EU flat 25% indirect on direct (excl. subcontracting) |
| **Horizon** | Per-partner detailed | Per-partner cost breakdown table | Flat 25% indirect (most actions) |
| **DARPA / DoD** | DCAA-compliant detailed | 5-10+ pp narrative | Negotiated rate; subaward fees layered |
| **UKRI fEC** | TRAC/fEC institutional tool | 2 pp Justification of Resources | 80% fEC paid by UKRI; institution covers 20% |

## Budget Justification Narrative Pattern

Per category, address three questions:

1. **What is requested** — number, role, duration, item, quantity
2. **Why it is needed** — link to specific Aim / WP / task
3. **How the cost was estimated** — quote, institutional rate, prior-year actuals

### Template paragraph

```
[Category]. We request [N units] of [item/role] over [duration] at [unit cost], totaling [total].
This supports [specific Aim/WP] by [specific function]. Cost basis: [quote / institutional rate /
prior award actual].
```

### Example (postdoc personnel)

> **Postdoctoral Researcher (Year 1-3, 100% effort).** We request salary support for one postdoctoral researcher at the institution's standard postdoc rate ($72,000/yr Year 1, escalating 3% annually). This person will lead Aim 2 (algorithm development and benchmarking) and contribute to Aim 3. Recruitment will target candidates with deep-learning systems backgrounds; PI's prior postdocs (5, all transitioned to faculty/industry roles) demonstrate successful mentoring. Fringe @ 27.4% institutional rate.

## Personnel

The largest line for most CS proposals. Address each role:

### PI Salary
- US (NSF/NIH): typically 1-2 months/year summer salary or partial AY buyout. NIH limit: NIH salary cap (varies annually, currently ~$221K/yr).
- ERC/Horizon/UKRI: PI time charged at investigator rate (estimated effort, not invoiced).
- DARPA/DoD: 1-2 months summer + AY buyout common; full effort allowed for sabbatical-funded years.

### Postdoctoral Researchers
- Institution's standard postdoc rate; NIH NRSA scale is the federal floor.
- Justify why the postdoc is needed (vs PhD student) — usually depth of methods expertise.
- One postdoc per Aim is a common ratio; >2 postdocs per Aim raises questions.

### PhD Students
- Stipend + tuition + fringe — institutional standard ranges from ~$35K (stipend) + $55K (tuition+fees) in US private universities.
- Justify number of students (1 per Aim is typical; 2+ per Aim needs explanation).
- UK: full studentship cost including stipend, fees, RTSG charged.
- DARPA: students often charged at higher rate due to project pace.

### Effort percentages

Per person per year:
- Total effort across all funded projects ≤100%
- Match effort to work plan: a person at 50% effort cannot lead 80% of an Aim
- Multi-PI: each PI's effort across all funding ≤100% (compliance check)

## Equipment

Items above the institution's capitalization threshold (typically $5K US, £10K UK). One-time purchase; not consumables.

### Justification structure

- **What**: GPU server, instrument, etc., with model number
- **Why**: which Aim requires this hardware?
- **Why now / why not shared**: explain why department's existing facility is insufficient (specs, queue, scheduling)
- **Quote**: vendor quote attached as appendix

### CS/ML common items
- GPU servers (e.g., 8× H100): $250K-$400K range
- Storage arrays: $30K-$80K
- High-bandwidth networking: $10K-$50K

Increasingly, **cloud compute substitutes for capital purchase** — many proposals now request operational cloud budgets instead of hardware.

## Travel

Itemize:

```
Year 1 — domestic:
  - 2× CS conference (e.g., NeurIPS, OSDI): 2 trips × $2,500/trip × 2 attendees = $10,000
  - 1× Project meeting (collaborator site): 1 trip × $1,200 × 2 attendees = $2,400
Year 1 — international:
  - 1× European workshop: 1 trip × $4,000 × 1 attendee = $4,000
```

Justify: which conference, which paper expected to be presented, which project meeting.

US: domestic vs foreign travel requires Fly America Act compliance for federal funds.

## Materials, Supplies, Compute

Itemize. CS-specific examples:
- Software licenses (e.g., commercial deep-learning frameworks, simulators)
- Cloud compute credits (AWS/GCP/Azure) — separate line, not "supplies"
- Open-access publication fees ($2-5K per paper for major venues)
- Workshop hosting (room rental, catering) for outreach activities

## Subcontracts / Subawards / Linked Third Parties

When work is done by another institution:

- **Subaward agreement**: separate budget + justification from the partner
- US: **first $25K of subaward MTDC** is included in your indirect-cost base; remainder is excluded
- Horizon: each consortium partner has its own budget; "Linked Third Parties" concept exists for legal entities not yet partners but contributing
- Justify: why this work is procured externally, not done in-house

## Indirect Costs (F&A / Overhead)

Institution's negotiated rate × Modified Total Direct Costs (MTDC) base.

- **MTDC base** = direct costs minus equipment, tuition, first-$25K-of-subaward, participant support
- Federal F&A rates (US): negotiated with cognizant agency (DHHS or ONR); typical R1 rate 55-70% MTDC
- ERC/Horizon: flat **25% indirect** (unit cost grants vary)
- UKRI fEC: institutional indirect via TRAC; UKRI pays 80% of fEC

Do not edit indirect rate; it is institutional. Sponsored Research Office computes.

## CS / ML Compute Justification

Increasingly the largest variable line in CS/ML proposals. **Justify granularly** — reviewers actively scrutinize this.

### Components to address

1. **Specific hardware**: GPU type (H100 80GB, MI300X, A100), node count, network (InfiniBand HDR/NDR)
2. **Total node-hours requested**: state the number, not just dollar amount
3. **Source**: cloud (which provider), HPC center (NAIRR, ACCESS, OLCF, NERSC, EuroHPC, JADE2, Isambard-AI, Bristol AI Centre), institutional cluster
4. **Why this scale**: tied to model size, dataset, # ablation runs
5. **Pricing basis**: published rates, prior allocation actuals

### Worked example

> **Compute (Cloud, Year 1-3).** Aim 2 requires pretraining 7B-parameter foundation models with 5 ablation variants × 3 random seeds = 15 runs. Each run: 256 H100 GPUs × 7 days = 43K H100-hours/run; 15 runs × 43K = 645K H100-hours total. At $2.85/H100-hour (institution-negotiated cloud rate), this totals $1.84M across 3 years. We have secured a NAIRR allocation for 200K H100-hours (letter, App E) reducing the requested cost to $1.27M. The remaining 200K H100-hours/year supports Aim 3 inference benchmarking.

This level of detail makes reviewers comfortable. Vague "we will use cloud GPUs ($500K total)" reads as underdeveloped.

### NAIRR / ACCESS / NSF compute

US researchers can apply for **NAIRR** (National AI Research Resource pilot) allocations of GPU hours separately from grant budget — request these alongside the proposal where eligible and reduce the proposal's compute ask accordingly. Cite NAIRR allocation letter in Facilities.

## Common Budget Failures

1. **Mismatch between work plan and budget**: budget shows 1 postdoc, work plan describes 3 postdoc-led Aims. Reconcile.
2. **Effort overcommit**: PI at 30% on this proposal + already 50% + 30% on existing grants = 110%. Compliance check fails.
3. **Compute not justified**: lump sum without GPU type, hours, or source.
4. **No quotes for equipment**: NSF/NIH require quotes attached.
5. **Subaward not detailed separately**: each subaward needs its own budget + justification.
6. **F&A miscalculation**: applying F&A to equipment or excluded costs.
7. **Cost escalation forgotten**: salaries should escalate (typically 2-3%/yr) over multi-year proposals.
8. **Travel without specific conferences named**: reviewers want to see "NeurIPS Year 2", not "1 international conference".
9. **Open-access publication fees omitted**: assume 2-3 papers per year × ~$3K APC for top CS venues.
10. **Currency/format errors in Horizon**: budgets must be in EUR, formatted per Funding & Tenders Portal templates.

### Pre-submission checklist

- [ ] Total adds up correctly each year
- [ ] Effort percentages do not exceed 100% for any person across all funded work
- [ ] Every line item is referenced in the justification narrative
- [ ] Every justification line is tied to a specific Aim/WP
- [ ] Quotes attached for equipment >threshold
- [ ] Subaward budgets separate and certified by partner institution
- [ ] Indirect rate = current institutional negotiated rate
- [ ] Travel itemized by conference/destination
- [ ] Compute fully detailed (GPU type, hours, source, rate basis)
- [ ] Open-access / publication costs included
