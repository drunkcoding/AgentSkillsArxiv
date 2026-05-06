# Biosketch / CV and Data Management Plan

Two of the most common auxiliary documents required across funders. Format mistakes here are a frequent reason for desk-rejection.

## Table of Contents

1. [Biosketch / CV Format Map](#biosketch--cv-format-map)
2. [NSF Biosketch (SciENcv-required)](#nsf-biosketch-sciencv-required)
3. [NIH Biosketch (SciENcv-required)](#nih-biosketch-sciencv-required)
4. [ERC CV and Track Record](#erc-cv-and-track-record)
5. [Horizon Europe Partner CVs](#horizon-europe-partner-cvs)
6. [UKRI R4RI Résumé](#ukri-r4ri-résumé)
7. [DoD/DARPA CVs](#doddarpa-cvs)
8. [Data Management Plan (DMP)](#data-management-plan-dmp)
9. [Funder-Specific DMP Templates](#funder-specific-dmp-templates)
10. [CS / ML Specifics for Biosketch and DMP](#cs--ml-specifics-for-biosketch-and-dmp)

---

## Biosketch / CV Format Map

| Funder | Required format | Page limit | Tool |
|---|---|---|---|
| **NSF** | NSF biosketch | 3 pp | **SciENcv mandatory** |
| **NIH** | NIH biosketch | 5 pp | **SciENcv mandatory** since 2023 (or fillable form for legacy) |
| **ERC** | ERC CV + Track Record | 2 pp + 2-4 pp | Word/PDF, ERC template |
| **Horizon Europe** | Partner CV (per institution) | usually 4 pp | EU template |
| **UKRI** | R4RI résumé | 4 pp | Word/PDF, council template |
| **DARPA / DoD** | Free-form CV | typically 2-3 pp per personnel | Word/PDF |
| **Royal Society** | Standard CV + Personal Statement | 2 pp CV + 1 pp statement | Word/PDF |

**Failing to use SciENcv for NSF/NIH = automatic compliance failure**. Generate via https://www.ncbi.nlm.nih.gov/sciencv/ and re-export each submission (new versions of templates roll out).

## NSF Biosketch (SciENcv-required)

3 pages max, four mandatory sections:

### (a) Professional Preparation
Reverse-chronological list of degrees + positions. Include institution, location, major, year.

### (b) Appointments and Positions
Reverse-chronological academic + non-academic positions. Include start year, end year (or "present"), institution, title.

### (c) Products
Up to **5 products most closely related to the proposal** + up to **5 other significant products**. Products can be: peer-reviewed publications, datasets, software, patents, technical reports. CS proposals: prioritize software releases and benchmarks alongside top-venue papers.

Format each product with full citation (authors, year, title, venue) and DOI/URL.

### (d) Synergistic Activities
Up to **5 examples** of: contributions to public welfare, professional/scientific society leadership, mentoring, broader impact. Quantify when possible ("Mentored 8 PhD students, 6 from underrepresented groups; 5 transitioned to faculty positions").

NSF removed Section (e) "Collaborators and Other Affiliations" — that's now a separate spreadsheet (COA).

## NIH Biosketch (SciENcv-required)

5 pages max, four mandatory sections:

### A. Personal Statement
**Most important section.** A narrative (typically 4-6 paragraphs) explaining why **you specifically** are qualified for **this specific project**. End with up to 4 publications cited as evidence.

Each new proposal needs a **fresh Personal Statement** tailored to the project. Generic boilerplate fails.

### B. Positions, Scientific Appointments, and Honors
Reverse-chronological list of academic, professional, and honorary positions.

### C. Contributions to Science
Up to **5 contributions**, each described as a paragraph + up to 4 cited publications. **Each contribution should describe an arc of research**, not list one paper.

```
1. [Contribution title]. We have shown that [scientific advance]. The work has [impact, e.g., "altered the practice of X", "established the field of Y"]. My role was [PI / first author / lead investigator on funding] for the following representative outputs:
   a. [Citation 1]
   b. [Citation 2]
   c. [Citation 3]
   d. [Citation 4]
```

NIH removed Section D (research support) — now in Other Support document, separate from biosketch.

## ERC CV and Track Record

### CV (max 2 pp)
Standard structure: education, positions held, supervision, fellowships/awards, prior funding, teaching. ERC template enforces specific headers — use the ERC-provided Word template verbatim.

### Track Record (max 2 pp; AdG: 4 pp)
Substantive section, often weighted heavily. Required sub-sections:

1. **10 most representative publications** (StG: 5 since PhD)
2. **Major invited presentations** at international conferences (5-10)
3. **Major prizes / awards / academic distinctions**
4. **Other achievements** — patents, software releases, organized workshops, editorial roles, mentorship, IP

For CS PIs, include: software/dataset releases with adoption metrics, GitHub URLs, citations of cited papers, h-index from a major source (Google Scholar / DBLP), reviewer service for top venues.

**StG/CoG**: lead-author / corresponding-author publications carry the most weight; demonstrating intellectual independence from the PhD/postdoc supervisor is critical.

## Horizon Europe Partner CVs

Each partner institution submits a "Partner CV" / "Description of Participating Organization" entry inside Section 4 of Part B. Typically 4 pages per partner. Address:

1. **Legal status** (university, RTO, SME, large enterprise)
2. **Role in the project** — which WPs led/contributed
3. **Key personnel** — short CV per person (typically 5-10 bullet points each)
4. **Relevant prior projects** — H2020 / Horizon / national grants on similar topics
5. **Publications and outputs** relevant to project

## UKRI R4RI Résumé

Up to 4 pages. Five contribution categories — write 1-3 contribution narratives per category. Length per category: ~half a page.

1. **Contributions to the generation of knowledge** — relevant outputs (publications, patents, software, datasets) with narrative explaining contribution and impact
2. **Contributions to the development of individuals** — students supervised, mentees, training programmes contributed to
3. **Contributions to the wider research community** — peer review, editorial, conference organising, EDI activities
4. **Contributions to broader research and innovation users and audiences** — public engagement, industry, policy, patient/community involvement
5. **Additional information** — career breaks, part-time working, secondments

R4RI rewards **diverse, narrative impact** over publication count. Plain-English explanation of each contribution is expected.

## DoD/DARPA CVs

No mandated template — use a clean 2-3 page CV per key personnel. Include:

- Education and positions
- Top 10 publications (skew toward systems/applied work, not theory)
- Prior DoD funding (if any) — DARPA reviewers care about prior performance
- Software releases, transitions to industry/Service, patents
- Security clearance status (if applicable to BAA)

## Data Management Plan (DMP)

Standard structure regardless of funder:

1. **Types and volumes of data** generated (datasets, code, models, intermediate artifacts)
2. **Data formats and standards** (open formats preferred; metadata standards)
3. **Storage during the project** (institutional, cloud, encryption)
4. **Sharing mechanism** (public repository name, license, embargo if any)
5. **Access policies** (open / restricted, conditions)
6. **Long-term archival plan** (institutional repository, Zenodo, OSF, domain repositories)
7. **Persistent identifiers** (DOIs for datasets, ORCID for personnel)
8. **Ethical and legal restrictions** (PII, IRB-restricted data, export-control)
9. **Software release plan** (license: MIT/Apache-2.0/GPL; repository: GitHub/GitLab; maintenance commitment)
10. **Roles and responsibilities** for data stewardship

CS/ML-specific DMP elements:

- **Datasets**: HuggingFace dataset cards, Croissant metadata
- **Models**: HuggingFace model cards, model weights archival, license (CC-BY, OpenRAIL, custom)
- **Code**: GitHub release with versioned tags, Zenodo archival for permanent DOI, Apache-2.0 default license unless required otherwise
- **Reproducibility**: Docker images, deterministic builds, paper-with-code linkage
- **Compute traces / logs**: WandB / TensorBoard logs archival decision

## Funder-Specific DMP Templates

| Funder | Format | Length |
|---|---|---|
| **NSF DMSP** | Free-form, but PAPPG mandates address of: data types, formats, metadata, sharing, archival, persistent IDs, ethical restrictions | 2 pp max |
| **NIH DMS Plan** | Mandatory since Jan 2023; structured 6-element template | 2 pp max |
| **ERC** | Annexed Data Management Plan; FAIR-aligned | varies |
| **Horizon Europe** | Mandatory FAIR DMP; updated at month 6, mid-term, end | initial 5-10 pp; iterative |
| **UKRI** | Council-specific (DCC checklist common); EPSRC mandatory | 1-2 pp |
| **DARPA / DoD** | Required only when explicitly called for in BAA | varies |

### NIH DMS Plan: 6 mandatory elements

1. **Data Type** — types and amounts; tools, software, code generated
2. **Related Tools, Software, Code** — versions; release plans
3. **Standards** — common formats and metadata standards used
4. **Data Preservation, Access, Timelines** — repository, access mechanism, timeline (data shared no later than time of associated publication or end of award)
5. **Access, Distribution, Reuse Considerations** — restrictions, IRB, consent provisions
6. **Oversight of Data Management and Sharing** — how DMS plan compliance is monitored

### Horizon Europe FAIR DMP

Required FAIR principles addressed:
- **Findable**: persistent IDs, rich metadata, indexed in searchable resource
- **Accessible**: open by default; if restricted, justified
- **Interoperable**: community-standard formats and ontologies
- **Reusable**: license (CC-BY-4.0 default for data), provenance, community standards

## CS / ML Specifics for Biosketch and DMP

### Biosketch

- **Software releases** carry weight — list with GitHub URL, commit count, contributors, stars, downstream-dependency count where impressive
- **Datasets / benchmarks released** as separate Products (NSF) or Contributions (NIH)
- **Open-source maintainership** of widely-used projects (PyTorch core, vLLM, HuggingFace transformers contributor) is a Synergistic Activity / Contribution
- **Industry transitions** of work (named systems deployed at companies) under Synergistic / Contributions to Science
- **Reviewer/PC service** for top venues (NeurIPS, ICML, ICLR, OSDI, NSDI) under Synergistic Activities

### DMP

- **Default license stance**: MIT / Apache-2.0 for code; CC-BY-4.0 for datasets; OpenRAIL-M for foundation-model weights
- **Repository commitments**: GitHub for development; Zenodo for archival DOI; HuggingFace for models/datasets
- **Reproducibility commitments**: artifact evaluation badges (USENIX, ACM AE), paperswithcode entries, Docker images
- **Sensitive datasets** (clinical, demographic, web-scraped): address consent, re-identification risk, access tier
- **Compute carbon accounting** (Horizon Europe encouraged): tonnes CO2-eq estimated, mitigation
- **Foundation model release decisions**: weights vs. API only vs. red-team-gated — justify under "Access, Distribution, Reuse"

## Pre-Submission Checklist

- [ ] Biosketch / CV format matches funder template **exactly**
- [ ] Biosketch within page limit (3 pp NSF, 5 pp NIH, 2+2 ERC)
- [ ] **NSF/NIH biosketches generated via SciENcv** (mandatory)
- [ ] Personal Statement (NIH) tailored to this proposal
- [ ] Synergistic Activities / Contributions are quantified, not narrative-only
- [ ] DMP within page limit
- [ ] DMP addresses all funder-mandated elements (NIH 6 elements, Horizon FAIR)
- [ ] DMP names specific repositories, licenses, retention periods
- [ ] DMP code/model release plan includes maintenance commitment
- [ ] If sensitive data: ethical / IRB / GDPR considerations addressed
- [ ] R4RI (UKRI): all 5 contribution categories addressed with narrative
