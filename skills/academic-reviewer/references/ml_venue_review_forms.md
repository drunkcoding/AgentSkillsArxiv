# ML Venue Review Forms and Norms

Use this reference for NeurIPS, ICML, ICLR, and AAAI OpenReview-style reviews. Every fact below is edition-labelled. Forms change: confirm the live form and current official guide before submission, especially where the public guide does not expose a scale or character limit.

## Table of Contents

1. [Quick Reference](#1-quick-reference)
2. [ML-Specific Evaluation](#2-ml-specific-evaluation)
3. [NeurIPS 2025](#3-neurips-2025)
4. [ICML 2026](#4-icml-2026)
5. [ICLR 2026](#5-iclr-2026)
6. [AAAI-26](#6-aaai-26)
7. [Discussion-Phase Duties](#7-discussion-phase-duties)
8. [Common Mistakes](#8-common-mistakes)
9. [Filled Example: ICML 2026](#9-filled-example-icml-2026)
10. [Official Sources](#10-official-sources)

---

## 1. Quick Reference

| Venue / edition | Publicly verified overall scale | Confidence | Dimension scores | Distinctive process |
|-----------------|---------------------------------|------------|------------------|---------------------|
| NeurIPS 2025 | 1-6 | 1-5 | Quality, Clarity, Significance, Originality: 1-4 | Acknowledge rebuttal; reviews/discussion for accepted papers become public anonymously |
| ICML 2026 | 1-6 | 1-5 | Soundness, Presentation, Significance, Originality: 1-4 | Mandatory author-response acknowledgement and final post-rebuttal justification |
| ICLR 2026 | 0, 2, 4, 6, 8, 10 | 1-5 | Soundness, Presentation, Contribution: 1-4 | Public reviews; active public discussion; revisions allowed through Dec. 3 |
| AAAI-26 | Public guide does not publish anchors; confirm the live OpenReview form | Confirm live form | Reproducibility is explicitly decision-relevant | Two phases; Phase-1 rejects have no rebuttal opportunity |

Do not translate these scores to the systems 1-5 merit scale. Enter the venue's own fields and preserve its anchors.

---

## 2. ML-Specific Evaluation

Evaluate soundness, presentation, significance, originality, empirical/theoretical support, reproducibility, limitations, and ethics separately.

### 2.1 Originality is broader than “new method”

Credit new insights, analyses of existing methods, removal of restrictive assumptions, useful data/resources, strong real-world applications, and carefully justified combinations of known techniques. Do not reject merely because the paper lacks a new architecture or state-of-the-art result.

### 2.2 Significance is not systems deployability

Ask whether the work advances understanding, capabilities, methodology, data, theory, or practice for the relevant ML community. A specialized contribution can be significant if its scope is appropriate and its conclusions are durable.

### 2.3 Reproducibility is an assessed claim

Check seeds, run counts, variance or confidence intervals, statistical tests, hyperparameter search ranges and selection criteria, hardware/software versions, dataset provenance and licensing, preprocessing, code/data availability, theoretical assumptions, and complete proofs. Treat a checklist answer as a pointer to evidence, not as evidence by itself.

### 2.4 Limitations and ethics are separate from merit

Reward candid limitations. Flag an ethics concern only when specialist review is warranted; explain the concern privately where the form requests it. Do not use an ethics flag as a substitute for technical criticism.

---

## 3. NeurIPS 2025

**Edition source:** NeurIPS 2025 Reviewer Guidelines and LLM Policy.

### 3.1 Official review fields

1. Summary
2. Strengths and Weaknesses, addressing Quality, Clarity, Significance, and Originality
3. Quality score (1-4)
4. Clarity score (1-4)
5. Significance score (1-4)
6. Originality score (1-4)
7. Questions (ideally 3-5 actionable questions with score-change criteria)
8. Limitations and potential negative societal impact
9. Overall score (1-6)
10. Confidence (1-5)
11. Ethical-concerns flag
12. Code-of-conduct acknowledgement
13. Responsible-reviewing acknowledgement

The official 2025 form is **not** a 1-10 overall scale. Earlier-edition memories must not override the 2025 guide.

### 3.2 Dimension-score calibration

| Score | Anchor |
|-------|--------|
| 4 | Excellent: compelling evidence for this dimension with no material gap |
| 3 | Good: clearly meets the bar; remaining issues are bounded |
| 2 | Fair: mixed or incomplete evidence; explain the consequential gap |
| 1 | Poor: fails the dimension in a way central to assessment |

### 3.3 Overall-score calibration

| Score | Official label | Well-calibrated use |
|-------|----------------|---------------------|
| 6 | Strong Accept | Technically flawless, groundbreaking impact, exceptional evaluation/reproducibility/resources, no unaddressed ethics issue |
| 5 | Accept | Technically solid and high-impact, with good-to-excellent evidence and reproducibility |
| 4 | Borderline accept | Solid paper whose acceptance case narrowly outweighs limitations; use sparingly |
| 3 | Borderline reject | Solid paper whose rejection case narrowly outweighs merits; use sparingly |
| 2 | Reject | Technical, evaluation, reproducibility, or ethics gaps place it below the bar |
| 1 | Strong Reject | Well-known result or fundamental/unaddressed technical or ethics problem |

**Confidence 1-5:** 5 means essentially certain and deeply familiar with related work after checking details; 1 means an educated guess outside the reviewer's area. Intermediate points step down in certainty, literature familiarity, and checking of math/details.

### 3.4 Discussion and visibility

Read all reviews and all author responses. Explicitly acknowledge that the response was read even when it does not change the score. Participate in reviewer-author and reviewer-AC discussion; update the review and explain any changed evaluation. Accepted-paper reviews, meta-reviews, author discussion, and reviewer responses become public anonymously; opted-in rejected papers can also become public.

### 3.5 Reviewer LLM policy

Never share a submission, submitted code, review material, ideas, or results with an LLM. An LLM may be used only on external/public material to understand concepts or to check grammar/phrasing without leaking confidential information. The reviewer remains responsible for accuracy and quality.

---

## 4. ICML 2026

**Edition source:** ICML 2026 Reviewer Instructions, Call for Papers, and Policy for LLM Use in Reviewing.

### 4.1 Official main-track review fields

1. Summary
2. Strengths and Weaknesses addressing Soundness, Presentation, Significance, and Originality
3. Soundness score (1-4)
4. Presentation score (1-4)
5. Significance score (1-4)
6. Originality score (1-4)
7. Key Questions for Authors (ideally 3-5, with score-change conditions)
8. Limitations and potential negative societal impact
9. Overall Recommendation (1-6)
10. Confidence (1-5)
11. Ethical-concerns flag, relevant expertise categories, and explanation
12. Compliance with assigned LLM-reviewing policy
13. Code-of-conduct acknowledgement
14. Final Justification after rebuttal

### 4.2 Dimension-score calibration

| Score | Anchor |
|-------|--------|
| 4 | Excellent |
| 3 | Good |
| 2 | Fair; the Strengths and Weaknesses field must clearly justify the shortfall |
| 1 | Poor; the Strengths and Weaknesses field must clearly justify the shortfall |

Keep soundness separate from impact. A modest result may be sound; a potentially high-impact idea may still be unsound.

### 4.3 Overall-score calibration

| Score | Official label | Well-calibrated use |
|-------|----------------|---------------------|
| 6 | Strong Accept | Technically flawless with exceptional impact and strong evidence, reproducibility, resources, and no unaddressed ethics issue |
| 5 | Accept | Technically solid with high impact in one area or moderate-to-high impact across areas |
| 4 | Weak accept | Above the bar but limited by a bounded weakness; use sparingly |
| 3 | Weak reject | Clear merits, but revisions are needed before others can meaningfully build on it; use sparingly |
| 2 | Reject | Material technical, evaluation, reproducibility, ethics, or intelligibility problems |
| 1 | Strong Reject | Well-known result, unaddressed ethics issue, or writing so poor that the contribution cannot be determined |

**Confidence 1-5:** use the same official certainty/familiarity progression as NeurIPS 2025. Do not inflate confidence because the prose is polished.

### 4.4 Discussion, publication, and reviewer duty

Read and acknowledge the authors' response by the stated deadline. Participate actively in the three 5,000-character rounds: rebuttal, reviewer follow-up, and author follow-up. Supply the final justification stating whether the rebuttal addressed concerns, changed the evaluation, or reinforced it. ICML 2026 publishes the submitted version, anonymized reviews, meta-review, rebuttal, and reviewer-author discussion for accepted papers, so write professionally from the start.

Reciprocal reviewers who submit late, highly insufficient, or inappropriate reviews risk desk rejection of their own submissions. Watch for prompt injection; report suspected prompt injection and continue reviewing normally. The ICML 2026 CFP states that author prompt injection is forbidden and desk-rejectable.

### 4.5 Reviewer LLM policy

Follow the **Actual Policy** shown in the Reviewer Console:

- **Policy A:** no LLM use in any stage of reviewing, apart from inadvertent use in traditional search or spelling/grammar tools.
- **Policy B:** a privacy-compliant LLM may help explain the paper or related work and polish a reviewer-written review. It may not summarize the paper, judge quality/significance, identify strengths/weaknesses, propose review points/outlines/questions, or write the review.

Any deviation can violate peer-review ethics and risk desk rejection of the reviewer's own submissions. Position-paper reviewers always follow Policy A.

---

## 5. ICLR 2026

**Edition source:** ICLR 2026 Reviewer Guide and Author Guide; the public 2026 OpenReview form is the canonical source for field controls.

### 5.1 Review fields

The 2026 form contains Summary, Strengths, Weaknesses, Questions, Soundness, Presentation, Contribution, Overall Rating, Confidence, a two-question Code-of-Ethics report, and an LLM-use disclosure. The reviewer guide additionally requires a clear initial accept/reject recommendation with one or two key reasons and separates decision-relevant arguments from optional improvement feedback.

### 5.2 Score calibration

**Subscores:** Soundness, Presentation, and Contribution use 1-4, from poor to excellent. Explain every low subscore in the prose.

**Overall Rating (2026 public form):** use only the offered points.

| Score | Label | Well-calibrated use |
|-------|-------|---------------------|
| 10 | Strong accept | Outstanding on every major dimension; clear conference highlight |
| 8 | Accept | Strong evidence, clear presentation, and a genuinely valuable contribution |
| 6 | Weak accept | Solid and above the bar, with bounded weaknesses |
| 4 | Borderline reject | No fatal flaw, but the acceptance case is not yet strong enough |
| 2 | Reject | Major technical, experimental, novelty, or reproducibility problems |
| 0 | Strong reject | Fundamentally flawed, already known, or substantially unfinished |

**Confidence:** 1-5. Treat 5 as deep expertise plus careful checking and 1 as an educated guess. Confirm the current invitation before submission if OpenReview changes an option or label.

### 5.3 Public discussion and revisions

Official reviews are public. Engage actively from **November 11 through December 3, 2025**. Authors may post unlimited comments and revise title, abstract, paper, and supplement; `pdfdiff` exposes changes. Reviewers may ignore revisions that differ significantly from the original scope. Read revisions and other reviews, join a borderline-paper meeting if requested, then update the final recommendation and state what did or did not change it. All submissions are de-anonymized and released after decisions; post-deadline withdrawals are immediately public and de-anonymized.

### 5.4 Reviewer LLM policy

General-purpose writing assistance is allowed, but the reviewer owns every claim and must disclose any LLM use in the review form. Fabrication, plagiarism, scientific misconduct, low-quality generated content, or nondisclosure can put the reviewer's own papers at risk of desk rejection. Preserve submission confidentiality.

---

## 6. AAAI-26

**Edition source:** AAAI-26 Reviewer Instructions, Review Process, Reproducibility Checklist, and Ethical Guidelines.

### 6.1 Review structure and fields

AAAI-26 explicitly says it does not require a fixed prose structure. Its recommended substantive review contains:

1. Paper Summary (4-10 sentences): contribution, problem, key idea, realization/implementation, and claimed conclusion
2. Review Summary (4-10 sentences): overall conclusion; clarity, soundness/validity, novelty, relevance; highest-priority improvements
3. Specific Points of Feedback: strengths, flaws, and feasible improvements
4. Human paper rating/recommendation and reviewer confidence in the live OpenReview form
5. Reproducibility assessment informed by the submitted checklist
6. Ethics/conflict reporting and required acknowledgements in the live form

The public AAAI-26 reviewer pages do **not** publish the numeric rating or confidence anchors. Do not import another venue's scale or an older AAAI scale. Confirm both against the current OpenReview form.

### 6.2 Two-phase process

- **Phase 1:** human reviews are supplemented by a clearly labelled AI-generated review with no rating or recommendation. Papers with sufficiently negative human reviews may be rejected without an author-feedback/rebuttal opportunity; their reviews become visible when the Phase-1 decision is released.
- **Phase 2:** survivors receive additional independent human reviews. New reviewers do not see Phase-1 reviews until they submit their own. Authors then respond once to all reviews, and human reviewers may revise reviews/ratings during discussion.
- Do not copy human or AI reviews. Independently assess the paper, then state agreement or disagreement after other reviews become visible.

### 6.3 Reproducibility checklist assessment

The checklist is shared with reviewers and factors into decisions. Check whether the paper substantiates each answer:

- General: conceptual outline/pseudocode, fact-vs-speculation separation, background references
- Theory: assumptions/restrictions, formal claims, proofs, intuitions, citations, empirical checks where applicable
- Data: dataset rationale, citations, availability/licensing, and detailed treatment of unavailable data
- Computation: hyperparameter search and final settings, preprocessing/code availability, seeds, hardware/software, metrics, run counts, variation, and statistical tests

A “no” or “partial” answer is not automatically fatal. Explain which missing information prevents verification or reproduction and how that affects the claims.

### 6.4 Reviewer LLM and AI-pilot policy

AAAI-26 supplies an official AI-generated Phase-1 review and an AI-generated discussion summary; neither replaces human decision-making, and the AI review carries no rating/recommendation. Human reviewers may later reflect on it but must not duplicate it. The public reviewer pages do not grant a general permission to upload confidential submissions to external LLMs. Preserve confidentiality and follow any additional instruction shown in the live reviewer console.

---

## 7. Discussion-Phase Duties

| Venue | Minimum reviewer duty after initial review |
|-------|--------------------------------------------|
| NeurIPS 2025 | Read all responses/reviews, acknowledge the response, discuss disagreements, update changed evaluations |
| ICML 2026 | Acknowledge the response, complete discussion rounds, write a final justification tied to the rebuttal |
| ICLR 2026 | Participate publicly and asynchronously, inspect in-scope revisions, join borderline meeting if called, update final recommendation |
| AAAI-26 | For Phase-2 papers, read author feedback and other reviews after independence is preserved; discuss and revise if warranted |

Do not change a score merely to reach consensus. Change it when evidence, correction, rebuttal, revision, or argument changes the assessment.

---

## 8. Common Mistakes

| Mistake | Correction |
|---------|------------|
| Reusing systems 1-5 merit and 1-4 confidence | Route to the edition-specific OpenReview form first |
| Treating “not a new method” as “not original” | Assess new insight, understanding, data, theory, efficiency, or application value |
| Combining soundness and significance | Score correctness/evidence separately from likely impact |
| Penalizing honest limitations | Reward candor; penalize only consequential unresolved gaps |
| Trusting checklist answers without locating evidence | Verify every decision-relevant claim in paper/appendix/materials |
| Ignoring rebuttal or discussion | Acknowledge and participate as required; update review when warranted |
| Inventing a scale, field, or character limit | Confirm the live form; state uncertainty if the public guide is silent |
| Uploading confidential work to an LLM | Follow the venue's exact policy and preserve confidentiality |

---

## 9. Filled Example: ICML 2026

**Paper:** “Calibra: Distribution-Aware Calibration for Vision-Language Models” (hypothetical)

**Summary:**  
Calibra proposes a post-hoc calibration method for vision-language models under distribution shift. The method estimates shift-conditioned temperature parameters from unlabeled deployment data using agreement across augmented views. The paper provides a consistency analysis and evaluates five models on six image and multimodal benchmarks. It reports lower expected calibration error than global temperature scaling and two adaptation baselines while largely preserving task accuracy.

**Strengths and Weaknesses:**

- **S1:** The paper studies a practically important failure mode and separates in-distribution calibration from shifted-deployment calibration clearly.
- **S2:** The evaluation covers multiple model families, shifts, and calibration metrics, and Section 5.4 ablates both augmentation agreement and the shift-conditioned estimator.
- **W1 [Major]:** The central soundness concern is selection leakage: Section 5.1 appears to choose augmentation strength on the same shifted test sets used for reporting. If so, the results do not establish deployment-time generalization. A held-out shift-validation protocol or fixed pre-registered setting would address this concern.
- **W2 [Major]:** Significance is uncertain because the comparison omits the strongest recent unsupervised calibration baseline cited in Section 2. A fair comparison could materially narrow the reported gain.
- **W3 [Minor]:** The limitations section discusses compute cost but not failure under label-shift assumptions, despite Figure 6 suggesting degradation in that regime.

**Soundness:** 2 (Fair)  
The selection protocol may leak test-shift information into hyperparameter choice.

**Presentation:** 3 (Good)  
The method and experiments are clear, but the tuning protocol needs a precise algorithmic description.

**Significance:** 3 (Good)  
Reliable calibration under shift is important, though the missing baseline makes the improvement uncertain.

**Originality:** 3 (Good)  
Conditioning calibration on augmentation agreement is a credible new combination and is well motivated.

**Key Questions for Authors:**

1. **Critical:** Was augmentation strength selected using any result from the reported shifted test sets? A strictly held-out protocol would resolve W1 and could raise the recommendation.
2. **Critical:** Can the authors compare against the recent unsupervised calibration baseline cited in Section 2 under the same model and shift settings?
3. How sensitive are results to the amount and class balance of unlabeled deployment data?

**Limitations:**  
Please discuss the observed failure under label shift and specify which deployment assumptions are required. Otherwise, the limitations discussion is candid.

**Overall Recommendation:** 3 (Weak reject)  
The problem and idea are promising, but the possible selection leakage and missing key baseline currently outweigh the merits. A clear no-leakage protocol plus a competitive result against the omitted baseline could move this review to 4.

**Confidence:** 4  
The reviewer is familiar with calibration and distribution shift, though did not independently check every proof detail.

**Ethical Concerns:** No flag.

**Post-Rebuttal Final Justification template:**  
After reading the response, maintain/raise/lower the recommendation from X to Y. The response resolved/partially resolved/did not resolve W1 because ____. It resolved/partially resolved/did not resolve W2 because ____. The final recommendation therefore reflects ____.

---

## 10. Official Sources

### NeurIPS 2025

- Reviewer Guidelines: https://neurips.cc/Conferences/2025/ReviewerGuidelines
- LLM Policy: https://neurips.cc/Conferences/2025/LLM
- Call for Papers: https://neurips.cc/Conferences/2025/CallForPapers

### ICML 2026

- Reviewer Instructions: https://icml.cc/Conferences/2026/ReviewerInstructions
- LLM Policy: https://icml.cc/Conferences/2026/LLM-Policy
- Call for Papers: https://icml.cc/Conferences/2026/CallForPapers

### ICLR 2026

- Reviewer Guide: https://iclr.cc/Conferences/2026/ReviewerGuide
- Author Guide (public discussion/revisions/visibility): https://iclr.cc/Conferences/2026/AuthorGuide
- OpenReview conference portal (canonical live form): https://openreview.net/group?id=ICLR.cc/2026/Conference

### AAAI-26

- Reviewer Instructions: https://aaai.org/conference/aaai/aaai-26/instructions-for-aaai-26-reviewers/
- Review Process: https://aaai.org/conference/aaai/aaai-26/review-process/
- Reproducibility Checklist: https://aaai.org/conference/aaai/aaai-26/reproducibility-checklist/
- Ethical Guidelines: https://aaai.org/conference/aaai/aaai-26/ethical-guidelines-for-aaai-26-reviewers/
