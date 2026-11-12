# Biosketch / CV and Data Management Plan

Facts last verified 2026-11-12 against NIH Guide notices NOT-OD-26-018 and NOT-OD-26-033 (US funders), PAPPG 24-1 with Supplements 1-2 (NSF), and DARPA/NIH pages as noted. Funder rules change frequently — confirm against the current solicitation/NOFO before relying on any limit or amount. (ERC, Horizon Europe and UKRI rows were not re-audited in this pass.)

Two of the most common auxiliary documents required across funders. Format mistakes here are a frequent reason for desk-rejection.

## Table of Contents

1. [Biosketch / CV Format Map](#biosketch--cv-format-map)
2. [NSF Biosketch (SciENcv-required)](#nsf-biosketch-sciencv-required)
3. [NIH Biosketch and Other Support (Common Forms, SciENcv-required)](#nih-biosketch-and-other-support-common-forms-sciencv-required)
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
| **NSF** | NSF Common Form biosketch | No page limit (PAPPG 24-1) | **SciENcv mandatory** |
| **NIH** | Common Form Biographical Sketch + NIH Biographical Sketch Supplement (due dates on/after Jan 25, 2026) | No page limit for the combined PDF; character limits on Supplement fields (NOT-OD-26-018) | **SciENcv mandatory** (single certified PDF) |
| **ERC** | Single "Curriculum Vitae (CV) and Track Record" section | up to 4 pp per Principal Investigator (WP2026/WP2027; see [erc.md](erc.md)) | ERC electronic proposal template |
| **Horizon Europe** | Partner CV (per institution) | usually 4 pp | EU template |
| **UKRI** | R4RI résumé (four modules + optional additional information) | Word limit set per opportunity (e.g., EPSRC New Investigator Award: 1,150 words for modules plus 500 for additions; see [ukri.md](ukri.md)) | Funding Service / council template |
| **DARPA / DoD** | Free-form CV | typically 2-3 pp per personnel | Word/PDF |
| **Royal Society** | Standard CV + Personal Statement | 2 pp CV + 1 pp statement | Word/PDF |

**Failing to use SciENcv for NSF/NIH = compliance failure** (NIH Common Forms: required for due dates on/after Jan 25, 2026 per NOT-OD-26-018; confirm current enforcement on grants.nih.gov). Generate via https://www.ncbi.nlm.nih.gov/sciencv/ and re-export each submission (new versions of templates roll out).

## NSF Biosketch (SciENcv-required)

Per PAPPG 24-1 II.D.2.h(i), the biosketch follows the federal Common Form and is generated in SciENcv; there is no page or character limit except where noted in the PAPPG. Mandatory sections:

### Professional Preparation
Reverse-chronological list (by start date) of degrees, postdoctoral and fellowship training, including organization, location, degree, start date, month/year received, and field of study.

### Appointments and Positions
Reverse-chronological list of academic, professional or institutional appointments (including adjunct, visiting, honorary, voluntary) with start year, end year, title, organization, department, location. Positions outside the primary organization need only be listed for up to three years back from submission.

### Products
Up to **5 products most closely related to the proposal** + up to **5 other significant products**; only this list of ten is used in review. Products can be: publications, conference papers, presentations, websites, technologies, patents, datasets, software, models, curricula. CS proposals: prioritize software releases and benchmarks alongside top-venue papers.

Give each product a full citation (authors — "et al." allowed for multi-author works —, title, date, URL / persistent identifier).

The biosketch itself has no Synergistic Activities section. PAPPG 24-1 II.D.2.h(iv) instead requires a **separate Synergistic Activities document** for each senior/key person: up to 1 page, up to 5 distinct examples demonstrating broader impact of professional and scholarly activities (integration and transfer of knowledge as well as its creation). Collaborators and Other Affiliations (COA) is another separate document (spreadsheet template).

## NIH Biosketch and Other Support (Common Forms, SciENcv-required)

**Policy:** NOT-OD-26-018 requires the **Biographical Sketch Common Form**, the **NIH Biographical Sketch Supplement** and the **Current and Pending (Other) Support Common Form** for application due dates, JIT, RPPR and prior-approval submissions on or after **Jan 25, 2026**, prepared in **SciENcv** (certified by the individual, not a delegate; ORCID iD linked to eRA Commons required). NOT-OD-26-033 extended a warning-only leniency period through May 2026, after which validations become errors on a date NIH announces; confirm current enforcement on grants.nih.gov. The Biographical Sketch Common Form and Supplement are completed in one SciENcv interface and produce a single PDF with **no page limit**.

### Biographical Sketch Common Form
Sections named in the notice: **Professional Preparation**, **Appointments and Positions**, and **Products** (Products Most Closely Related to the Proposed Project: limit 5 citations; up to 5 other significant products). Section D (Scholastic Performance, fellowships) is no longer required or accepted.

### NIH Biographical Sketch Supplement
- **Personal Statement** — narrative explaining why **you specifically** are qualified for **this specific project**; no citations allowed (refer to the Products cited in the Common Form); limited to 3,500 characters. Each new proposal needs a fresh, tailored statement.
- **Contributions to Science** — up to 5 narrative contributions, each up to 2,000 characters; no citations allowed, but you may refer to products listed under Other Significant Products in the Common Form. **Each contribution should describe an arc of research**, not one paper.

```
1. [Contribution title]. We have shown that [scientific advance]. The work has [impact, e.g., "altered the practice of X", "established the field of Y"]. My role was [PI / first author / lead investigator on funding]. Relevant products: [refer to entries in "Other Significant Products" of the Common Form]
```

### Current and Pending (Other) Support Common Form
Per NOT-OD-26-018: effort is reported in person-months only; "Overall Objectives" field limited to 1,500 characters; each proposal / active project / in-kind entry has its own Statement of Potential Overlap; in-kind contributions are reported only if estimated at $5,000 or more and require a commitment of the individual's time; supporting documentation (e.g., foreign contracts) is attached separately in JIT/RPPR/prior-approval modules and not appended to the form. Current and Pending (Other) Support is not required for Other Significant Contributors.

### Pre-2026 format (legacy; for reading older examples only)
The former NIH Biosketch had a 5-page limit with sections A. Personal Statement (up to 4 cited publications), B. Positions, Scientific Appointments, and Honors, C. Contributions to Science (up to 4 cited publications per contribution); Section D (research support) had been removed in favor of the separate Other Support document. Do not use this layout for due dates on or after Jan 25, 2026.

## ERC CV and Track Record

Under ERC WP2026/WP2027 this is **one combined section**, "Curriculum Vitae (CV) and Track Record", of **up to four pages for each Principal Investigator**. It contains personal details, education, key qualifications and positions; a list of **up to ten research outputs** of any type that show how you have advanced knowledge; selected examples of significant peer recognition; and optional explanations of each output's significance and your role, plus optional information on career breaks and diverse career paths. See [erc.md](erc.md) (PI Track Record) for details and the evaluation context.

For CS PIs, include: software/dataset releases with adoption metrics, GitHub URLs, citations and venue rank of listed outputs, reviewer service for top venues.

**StG/CoG**: lead-author / corresponding-author outputs carry the most weight; demonstrating intellectual independence from the PhD/postdoc supervisor is critical.

## Horizon Europe Partner CVs

Each partner institution submits a "Partner CV" / "Description of Participating Organization" entry inside Section 4 of Part B. Typically 4 pages per partner. Address:

1. **Legal status** (university, RTO, SME, large enterprise)
2. **Role in the project** — which WPs led/contributed
3. **Key personnel** — short CV per person (typically 5-10 bullet points each)
4. **Relevant prior projects** — H2020 / Horizon / national grants on similar topics
5. **Publications and outputs** relevant to project

## UKRI R4RI Résumé

UKRI's guidance asks applicants to structure their answer into four module headings; the **word limit is set in each funding opportunity** (e.g., EPSRC New Investigator Award: 1,150 words for the R4RI modules including references, plus up to 500 words for additions). Assessors never score individual modules. See [ukri.md](ukri.md) for detail.

1. **Module 1: contributions to the generation of new ideas, tools, methodologies or knowledge** — key outputs such as data sets, software, research and policy publications; how you communicated ideas and results
2. **Module 2: contributions to the development of others and maintenance of effective working relationships** — teaching, workshops, mentoring, leadership in shaping a team
3. **Module 3: contributions to the wider research and innovation community** — positions of responsibility, reviewing, editing, committee work, strategic leadership
4. **Module 4: contributions to broader research or innovation users and audiences** and wider societal benefit — public sector, clients, public understanding, policy
5. **Additional information (optional)** — context such as career breaks, secondments or voluntary work; not for extra skills or outputs (these "will not be assessed")

There is no "Personal Details" module. R4RI rewards **diverse, narrative impact** over publication count; plain-English explanation of each contribution is expected.

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
| **NSF DMSP** | PAPPG 24-1 lists: types of data/materials produced, data and metadata standards, access and sharing policies (privacy, confidentiality, IP), re-use/re-distribution, archiving; from Apr 27, 2026 created with a Research.gov tool (Supplement 2) | 2 pp max in PAPPG 24-1 (confirm in Research.gov tool) |
| **NIH DMS Plan** | Mandatory since Jan 2023; structured 6-element template (confirm on grants.nih.gov) | 2 pp max (confirm on grants.nih.gov) |
| **ERC** | Annexed Data Management Plan; FAIR-aligned | varies |
| **Horizon Europe** | Mandatory FAIR DMP; updated at month 6, mid-term, end | initial 5-10 pp; iterative |
| **UKRI** | Council-specific (DCC checklist common); EPSRC mandatory | 1-2 pp |
| **DARPA / DoD** | Required only when explicitly called for in BAA | varies |

### NIH DMS Plan: 6 mandatory elements (confirm on grants.nih.gov)

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
- **Open-source maintainership** of widely-used projects (PyTorch core, vLLM, HuggingFace transformers contributor) is a Contribution to Science (NIH Supplement) or a Synergistic Activities example (NSF)
- **Industry transitions** of work (named systems deployed at companies) under Contributions to Science (NIH) or Synergistic Activities (NSF)
- **Reviewer/PC service** for top venues (NeurIPS, ICML, ICLR, OSDI, NSDI) in the NIH Contributions to Science, or as an NSF Synergistic Activities example

### DMP

- **Default license stance**: MIT / Apache-2.0 for code; CC-BY-4.0 for datasets; OpenRAIL-M for foundation-model weights
- **Repository commitments**: GitHub for development; Zenodo for archival DOI; HuggingFace for models/datasets
- **Reproducibility commitments**: artifact evaluation badges (USENIX, ACM AE), paperswithcode entries, Docker images
- **Sensitive datasets** (clinical, demographic, web-scraped): address consent, re-identification risk, access tier
- **Compute carbon accounting** (Horizon Europe encouraged): tonnes CO2-eq estimated, mitigation
- **Foundation model release decisions**: weights vs. API only vs. red-team-gated — justify under "Access, Distribution, Reuse"

## Pre-Submission Checklist

- [ ] Biosketch / CV format matches funder template **exactly**
- [ ] Biosketch within page limit (NSF Common Form: no page limit; NSF Synergistic Activities ≤1 page; ERC CV and Track Record ≤4 pp per PI; NIH Common Form + Supplement: no page limit, observe Supplement character limits)
- [ ] **NSF/NIH biosketches and Current & Pending (Other) Support generated via SciENcv** (mandatory; NIH: Common Forms for due dates on/after Jan 25, 2026)
- [ ] Personal Statement (NIH Biographical Sketch Supplement) tailored to this proposal
- [ ] Contributions to Science (NIH) / Products (NSF) / separate Synergistic Activities document (NSF, ≤1 page, ≤5 examples) are quantified, not narrative-only
- [ ] DMP within page limit
- [ ] DMP addresses all funder-mandated elements (NIH 6 elements (confirm on grants.nih.gov), Horizon FAIR)
- [ ] DMP names specific repositories, licenses, retention periods
- [ ] DMP code/model release plan includes maintenance commitment
- [ ] If sensitive data: ethical / IRB / GDPR considerations addressed
- [ ] R4RI (UKRI): all four modules answered under their headings within the opportunity's word limit; optional additional information used only for context
