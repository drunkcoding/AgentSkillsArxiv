---
name: academic-reviewer
description: "Use when reviewing, critiquing, or providing feedback on submissions to systems venues (OSDI, NSDI, SIGCOMM, MOBICOM, SOSP, FAST) or AI/ML venues (NeurIPS, ICML, ICLR, AAAI), including HotCRP-style and OpenReview-style reviews."
---

# Conference Paper Reviewing

Review systems and AI/ML papers against the target venue's actual form and norms. Route by venue before choosing fields or scores; never reuse a HotCRP scale for an OpenReview venue.

## Before you start: reviewer LLM policy (read first)

This skill drafts, scores and polishes reviews with an LLM. Some venues forbid exactly that for assigned reviewers of confidential submissions. Settle this before reading any paper.

**Step 1 — establish the user's role.** Ask (or infer from the request) whether the user is:
- the **assigned reviewer** of a confidential submission at a venue (HotCRP/OpenReview assignment), or
- wanting a **mock/practice review** of their own draft or of a public paper (e.g., an arXiv or published paper). Mock reviews of the user's own draft or of public papers are unrestricted by reviewer policies; proceed with the workflow below.

**Step 2 — if the user is the assigned reviewer, check the venue's current reviewer LLM policy BEFORE reading the submission.** Rules verified on 2026-11-12 (they change every cycle; re-read the current edition's reviewer instructions):
- **ICML 2026** — Policy A: "Use of LLMs for reviewing is strictly prohibited" (detailed text: "Use of LLMs in any stage of reviewing is strictly prohibited (except for inadvertent use in tools that are not traditionally LLM-based, like web search/retrieval and spelling/grammar checkers)"). Policy B (allowed to help understand the paper and related works and to polish reviews, with privacy-compliant LLMs) forbids asking an LLM to assess the paper's quality/significance, identify its strengths/weaknesses, suggest key points, suggest an outline or questions for authors, or write the full review. Each reviewer is told which policy to follow on all of their assigned papers (check the Reviewer Console).
- **NeurIPS 2025** — "You cannot share the submission and the code given to you as a reviewer to anyone or any LLMs."
- **NeurIPS 2026** — "Reviewers must not use LLMs except for papers where this is specifically allowed, and must only use the sanctioned LLM in such cases rather than other LLMs." (opt-in AI-assisted reviewing experiment). Also: "Do not share, discuss, or disclose any information related to submissions with anyone, including any unsanctioned LLMs."
- **ICLR 2026** — The Reviewer Guide says: "we mandate that reviewers disclose the use of LLMs in their reviews. The review form will include a field to specify how you used LLMs, if at all." The public OpenReview review form read on 2026-11-12 has no field for the reviewer's own LLM use; its optional `LLM_usage` checkbox is for flagging a paper that made significant undisclosed LLM use ("If you believe this paper made significant use of LLMs beyond typos and grammar, and this usage is not described in the paper, check this box to flag it for further review."). Follow the guide: disclose any LLM use (for example to the AC), and remain responsible for every claim.
- **ICLR 2027** — "We permit limited and responsible use of AI tools to assist human writing of peer reviews and meta-reviews. However, it is mandatory to disclose use of AI tools." If an LLM generated or edited any part of a review, "you will be required to report your original, self-written paper assessment, and any LM interactions, in an accompanying textbox." Consequences "may include desk-rejecting all papers authored by the (meta) reviewer".
- **ACM venues (SIGCOMM, MobiCom, SOSP, and other ACM conferences)** — the ACM Peer Review Policy applies. MobiCom 2027 CFP: "We remind all reviewers that the submitted papers are considered confidential and hence cannot be uploaded to language models." ACM Peer Review FAQ: "Reviewers may not upload confidential ACM submissions into any generative AI or LLM system or any system managed by a third party which does not promise to maintain the confidentiality of that information"; enterprise LLMs that promise confidentiality may be used "to draft or improve the readability or quality of their reviews provided that, in doing so, reviewers do not breach confidentiality". The SIGCOMM 2026/2027 and SOSP 2026 CFPs add no separate reviewer-side sentence, but a venue may run its own review model, so read its reviewer instructions. Treat uploading a submission to an LLM as prohibited unless the user can show the tool promises confidentiality.
- **USENIX (OSDI, NSDI, FAST)** — no reviewer-side generative-AI rule was found in the OSDI '26/'27, NSDI '27 or FAST '27 CFPs or the USENIX policy pages, and USENIX states it "does not have an organization-wide policy on the use of AI during the creation of a paper". Not verified: the user must ask the program chairs; as a conservative default, do not upload the submission to a third-party LLM.
- **AAAI** and other venues — no reviewer-side LLM rule verified here. AAAI-26 and AAAI-27 supply their own AI-generated, non-decisional review in Phase 1 (the AAAI-27 call: "Phase 1: Two reviews supplemented by one AI-generated, non-decisional review"); that is the conference's review, not reviewer permission. The user must check the reviewer instructions in the live reviewer console; do not assume LLM use is permitted.

**Step 3 — act on the policy.**
- **Prohibited** (or the user cannot show it is permitted): do **not** ingest the submission and do **not** draft or polish the review. Tell the user why, and offer only what the policy permits: explaining background concepts or related work without the submission, and guidance on the reviewing process, review form and tone from the reference files.
- **Unknown**: ask the user to confirm that the venue's policy permits LLM processing of the submission and review before proceeding.
- **Permitted** (e.g., ICLR with disclosure, ICML Policy B limits, NeurIPS 2026 sanctioned-LLM papers only, an ACM-compliant confidential enterprise LLM): stay inside the stated limits, and remind the user to make any required disclosure.

In all cases the humanizer pass and multi-review generation below are skipped when they would violate this policy.

## 1. Choose the Venue and Review Paradigm (start here)

| Venue | Paradigm | Review platform/style | Primary reference |
|-------|----------|-----------------------|-------------------|
| OSDI, NSDI, SIGCOMM, MOBICOM, SOSP, FAST | Systems | HotCRP-style | `references/review_form_templates.md` and `references/review_criteria.md` |
| NeurIPS, ICML, ICLR, AAAI | AI/ML | OpenReview-style; edition-specific fields and scales | `references/ml_venue_review_forms.md` |

Confirm the edition before drafting. Review forms, scales, visibility, rebuttal duties, and LLM-use rules can change annually. Check the live review form and reviewer instructions; if you have no network access, use the stored forms in the reference files, state which cycle they describe, and tell the user to confirm on the live form. For venue format rules that affect what a submission was required to contain, use `academic-writing`. For the author-response tactics your questions will trigger, use `academic-rebuttal`.

## Final delivery: humanize the output

> **Policy gate:** skip this pass (and all drafting) when the user is an assigned reviewer at a venue whose policy prohibits LLM processing of the review or submission — see "Before you start: reviewer LLM policy".

**REQUIRED SUB-SKILL (run before returning any draft to the user).** Load the `humanizer` skill (via the skill tool) and run the finished text through it as a final editing pass. It removes AI-writing tells (inflated significance, copula avoidance like "serves as", rule-of-three, overused AI vocabulary such as "delve"/"testament"/"landscape", filler phrases, sycophancy, and em/en-dash overuse) without inventing any fact, name, number, date, or citation. Preserve the target venue's format and conventions (HotCRP or OpenReview fields, score labels, severity labels, numbered questions), and if the user supplied a writing sample, pass it so humanizer matches their voice. If `humanizer` (or `humanizer-zh`) is unavailable, deliver the text as written and tell the user the humanizer pass was skipped.

**If the draft is written in Chinese, load the `humanizer-zh` skill instead of `humanizer`** (via the skill tool) — it applies the same no-fabrication discipline to Chinese prose, targeting 空话铺垫 (empty build-up), 模板化排比 (templated parallelism), over-used connectors (首先/其次/综上所述), and inflated 四字格, while preserving the same format and conventions required above.

## Core Capabilities

### 1. Review Structure and Format

Systems reviews follow the HotCRP form structure used by OSDI, NSDI, SIGCOMM, MOBICOM, SOSP, and FAST:

| Field | Required | Content |
|-------|----------|---------|
| Overall Merit | Yes | Score on the form's scale (illustrative 1-5) with calibrated justification |
| Reviewer Confidence / Expertise | Yes | Self-assessed expertise on the form's scale (illustrative 1-4; HotCRP's own templates use 1-3 confidence or 1-5 expertise) |
| Paper Summary | Yes | 3-5 sentence neutral summary in your own words |
| Strengths | Yes | 3-6 specific, prioritized positive observations |
| Weaknesses | Yes | 3-6 specific, prioritized concerns with severity labels |
| Detailed Comments | Yes | Technical feedback, elaboration, suggestions |
| Questions for Authors | Recommended | 3-5 numbered questions that could change your assessment |
| Minor Issues | Optional | Typos, formatting, editorial items |

*Illustrative scales only. None of OSDI, NSDI, SOSP, SIGCOMM, MobiCom or FAST publishes its HotCRP review form (checked 2026-11-12); HotCRP's own templates offer e.g. Overall merit 1-5 (Reject ... Strong Accept), Reviewer confidence 1-3 and Reviewer expertise 1-5, and each chair customizes them. This 1-5 merit / 1-4 confidence form is a representative template, not any venue's actual form: use the scales on the live review form.*

For detailed field-by-field guidance and complete example reviews, load `references/review_form_templates.md`.

For NeurIPS, ICML, ICLR, or AAAI, do not use this table or the systems score scales. Load `references/ml_venue_review_forms.md` and reproduce the target edition's OpenReview fields.

### 2. Evaluation Dimensions

Evaluate every paper along seven dimensions. Weight them according to venue-specific priorities (see Section 3).

| Dimension | Core Question | Most Common Issue |
|-----------|--------------|-------------------|
| **Novelty/Originality** | New ideas or incremental variation? | No clear key insight; approach anticipated by prior work |
| **Technical Soundness** | Is the design correct and consistent? | Hidden assumptions; unaddressed failure modes |
| **Significance/Impact** | If correct, how much does it matter? | Problem is real but niche; improvement too small to justify adoption |
| **Evaluation Quality** | Do experiments support the claims? | Unfair baselines; missing ablation; claims-evaluation mismatch |
| **Presentation/Clarity** | Can you understand it on one read? | Buried key insight; inconsistent terminology; ineffective figures |
| **Relevance** | Right paper for this venue? | Systems contribution unclear; better fit elsewhere |
| **Reproducibility** | Could someone reproduce the results? | Missing hardware specs; no code availability; insufficient methodology |

Evaluation quality is the **most common area of weakness** in systems paper submissions. Check it rigorously: map each numbered contribution to specific experiments and flag any unsupported claims.

**AI/ML adjustment:** separate soundness from significance and treat originality more broadly than “new method.” Credit new understanding, careful analysis of known methods, useful resources/data, removal of restrictive assumptions, and well-justified applications. Assess reproducibility checklists against evidence (seeds, run counts, variance, hyperparameter search, compute/software, data provenance, and proofs), not as box-ticking. Evaluate limitations and ethics flags independently from technical merit; reward candid limitations and flag ethics only when specialist review is warranted.

For detailed rubrics (5-point scale per dimension), venue-specific weights, and specific checks, load `references/review_criteria.md`.

### 3. Venue-Specific Review Expectations

Each venue has a distinct review culture. Adjust your emphasis accordingly.

| Venue | Philosophy | Top Priorities | Acceptance Rate |
|-------|-----------|---------------|----------------|
| **OSDI** | "Exciting papers over boring papers" | Novelty, significance, broad systems impact | OSDI '26 CFP: "Aims for an acceptance rate of 20% or more"; OSDI '25 55/327 = 16.8%, OSDI '26 136/681 = 20.0% (submission-site counts); OSDI '27 states no goal rate |
| **NSDI** | Deployment value matters | Significance, realistic evaluation, practical novelty | NSDI '25 83/666 = 12.5%; NSDI '26 150/659 = 22.8% (chairs' messages); NSDI '27 spring deadline 65/354 = 18.4% (fall pending) |
| **SIGCOMM** | "Lasting impact on the field" | Novelty, significance, rigorous networking analysis | No official count found (SIGCOMM publishes none on its conference site) |
| **MOBICOM** | Works in the real physical world | Soundness, real-world evaluation, wireless rigor | No official count found (MobiCom publishes none on its conference site) |
| **SOSP** | "Novel abstractions AND real systems" | Novelty, soundness, significance; artifact evaluation optional | SOSP 2025 66/369 = 17.9% (submission site); SOSP 2026 count not published |
| **FAST** | "Storage depth and practical impact" | Significance, evaluation quality, storage relevance | FAST '25 36/167 = 21.6%; FAST '26 44/253 = 17.4% (chairs' messages); FAST '27 spring deadline 17/92 = 18.5% |

*Acceptance figures are accepted/submitted counts from the program chairs' messages (NSDI '25-'26, FAST '25-'26) or the conference's own submission site (OSDI '25-'26, SOSP 2025, NSDI/FAST '27 spring deadline only), checked 2026-11-12. Venue facts last verified 2026-11-12 against the OSDI '26/'27, NSDI '27, FAST '27, SIGCOMM 2026/2027, MobiCom 2026/2027 and SOSP 2026 CFPs, the OSDI '26 call for artifacts, the ACM Peer Review Policy and FAQ, the ICML 2026 LLM Policy, the NeurIPS 2025 LLM page, the NeurIPS 2026 Main Track Handbook, the ICLR 2026 and 2027 reviewer guides and AI policy, the AAAI-27 call, and OpenReview review invitations. Forms and policies change every cycle — confirm on the live form and reviewer instructions.*

**Key venue-specific notes:**
- **OSDI**: Would you enthusiastically champion this paper? "Exciting and imperfect" can beat "boring and thorough." Artifact evaluation is optional (OSDI '26 call for artifacts).
- **NSDI**: Could this system actually be deployed? Production experience and operational lessons get extra credit. One-shot revision (OSR) available for borderline papers; artifact evaluation is optional (NSDI '27 call for artifacts).
- **SIGCOMM**: Papers need a strong advocate and a clear, substantial networking contribution. SIGCOMM 2027 uses "collaborative reviewing" and sends authors one short consensus review; no numeric acceptance threshold is published, so use the live form's scale. Artifact evaluation is voluntary and has no influence on acceptance (SIGCOMM CFP).
- **MOBICOM**: Real-world wireless experiments strongly preferred over simulation. Multiple environments and conditions required. Signal-level analysis expected. Artifact evaluation is voluntary and has no influence on acceptance (MobiCom 2027 CFP).
- **SOSP**: Must present new abstractions or principles, not just "faster X." Artifact evaluation is optional (SOSP 2026 CFP: "SOSP will continue the successful tradition of running an optional Artifact Evaluation process"), so do not penalize a paper merely for lacking an artifact. The system must be real and substantial.
- **Other systems venues (ASPLOS, EuroSys, USENIX Security, ATC, etc.)**: the generic systems workflow in this skill applies, but form fields, scales and policies must come from that venue's live review form and reviewer instructions.
- **FAST**: Deep storage/file systems expertise valued. Evaluation must use real storage workloads or production traces. Deployed-systems papers get credit for operational lessons. Short papers (6 pages) evaluated for completeness within their scope. Double-blind review. One-shot revision (OSR) available for borderline papers.

For full venue-specific rubrics, load `references/review_criteria.md`.

### 4. Review Writing Principles

Follow these seven principles when writing reviews:

1. **Be specific**: Reference exact sections, figures, equations, and claims. Never write "the evaluation is weak" without saying what is missing.
2. **Explain impact**: For each weakness, state why it matters: "This undermines the main throughput claim because..."
3. **Suggest remedies**: Where possible, indicate what would fix the problem: "Comparing against [baseline] on [workload] would address this."
4. **Prioritize by severity**: Label weaknesses as Fatal / Major / Minor. Fatal = fundamental flaw; Major = significant but potentially fixable; Minor = does not affect the contribution.
5. **Stay constructive**: Critique the work, not the authors. Frame negatives as paths to improvement. Ask: "Would my review help the authors write a better version?"
6. **Match tone to score**: Enthusiastic language for score 4-5, balanced for 3, respectful-but-clear for 1-2. Mismatched tone confuses everyone.
7. **Be honest about confidence**: Set reviewer confidence to your actual expertise level. Flag areas where a more expert reviewer should weigh in.

For detailed tone calibration, constructive rephrasing examples, and the Roscoe/Levin-Redell evaluation frameworks, load `references/review_ethics_and_tone.md`.

### 5. Common Paper Weaknesses

Weaknesses are classified by paper section with standardized IDs for consistent reference:

| Category | IDs | Common Examples |
|----------|-----|----------------|
| **Motivation** | W-M1 to W-M4 | Problem doesn't matter; no empirical evidence; strawman comparison; already solved |
| **Design** | W-D1 to W-D5 | No trade-off analysis; missing corner cases; unjustified complexity; hypothetical system; underspecified |
| **Evaluation** | W-E1 to W-E9 | Unfair baselines; cherry-picked workloads; unsupported claims; no error bars; no tail latency; insufficient scale; no ablation; claims mismatch; wrong metrics |
| **Presentation** | W-P1 to W-P5 | Poor writing; bad figures; inconsistent terminology; forward references; wrong organization |
| **Scope** | W-S1 to W-S4 | Incremental; too narrow; too broad; missing related work |

**Severity classification:**
- **Fatal**: Fundamental flaw that cannot be fixed without redesigning the system or rethinking the approach. Examples: core mechanism is incorrect; problem is already solved; evaluation contradicts claims.
- **Major**: Significant issue that affects the assessment but could be addressed with additional work. Examples: missing important baseline; hidden assumption; limited scale.
- **Minor**: Does not affect the core contribution. Examples: typos; figure formatting; missing citation.

For the complete weakness catalog with constructive phrasing templates, load `references/common_paper_weaknesses.md`.

### 6. Scoring Guidelines

Systems HotCRP forms typically pair an Overall Merit score (illustrative 1-5, Strong Reject to Strong Accept) with a reviewer confidence/expertise score (illustrative 1-4, Limited knowledge to Expert); the scales are not published by any of these venues, so use the live form's scales.
Read `references/review_form_templates.md` when filling in a systems (HotCRP-style) form: it has the label and guidance for every score level, the scale caveat, and example reviews at scores 5, 3 and 2 (plus a low-confidence variant). The accept/reject action per score is in `references/review_criteria.md`.

**Calibration reminders:**
- At the low acceptance rates of top systems venues (roughly 12-23% in recent editions with published counts, see the venue table), score 3 means "uncertain" — not "acceptable"
- Most accepted papers need at least one score of 4 or 5
- Use the full range: a clearly flawed paper should get 1 or 2, not a generous 3
- Roughly the venue's acceptance fraction (about one in five or fewer) of the papers you review should receive 4 or higher

### 7. One-Shot Revision (OSR) Reviews

Available currently at NSDI, MOBICOM, and FAST (per recent CFPs). SIGCOMM offered it through 2026, but the SIGCOMM 2027 CFP states "no rebuttals or one-shot revisions"; OSDI '26/'27 use conditional acceptance instead of revise-and-resubmit. OSR means the paper is not yet accepted: reviewers list required changes and the same reviewers re-check a resubmission at the next deadline (SIGCOMM 2026 handled it via a shepherd). MobiCom caps the list at three major changes/clarifications (MobiCom 2027 CFP); NSDI and FAST state no number.

**When to recommend OSR:**
- Core contribution is sound and significant
- Weaknesses are fixable by the resubmission deadline (NSDI and FAST state no fixed period; MobiCom's action points may take more than 4-6 weeks)
- Required changes are concrete and verifiable
- The paper would likely be accepted if changes are made

**When NOT to recommend OSR:**
- Fundamental approach is flawed
- Novelty is questionable (cannot be added in revision)
- Changes require new system design or major re-implementation

**OSR requirements must be:**
- Specific: "Add experiment comparing against X on workload Y"
- Achievable: Feasible within the revision period
- Verifiable: The PC can check whether each requirement is met

Read `references/review_form_templates.md` when you recommend OSR: it has the OSR template and a per-venue table.

### 8. Review Anti-Patterns

Avoid these six reviewer behaviors: Wish-List Reviewer, Benchmark Bully, Nitpick Reviewer, Silent Rejector, Positivity Mismatch, Copy-Paste Reviewer. Read `references/review_ethics_and_tone.md` when checking tone before delivery: it has each pattern's description, self-check and detection heuristic.

### 9. Multi-Perspective Review Generation

> **Policy gate:** do not generate these reviews when the user is an assigned reviewer at a venue whose policy prohibits LLM processing of the review or submission — see "Before you start: reviewer LLM policy". Mock reviews of the user's own or public papers are fine.

When asked to review a paper from multiple perspectives (or to simulate a PC sub-committee), generate four independent reviews — one at each confidence level. This surfaces issues that any single reviewer would miss.

**Output structure:**

| Review | Confidence | Persona | Primary Focus |
|--------|-----------|---------|---------------|
| A | 4 (Expert) | Deep domain specialist | Novelty, soundness, precise prior work positioning |
| B | 3 (Knowledgeable) | Well-read generalist in the area | Balanced assessment, claims-evidence alignment |
| C | 2 (Some familiarity) | Intelligent outsider | Presentation, methodology, accessibility |
| D | 1 (Limited knowledge) | Non-specialist PC member | Communication clarity, reproducibility, general methodology |

**Key behavioral differences:**
- **Expert**: Cites specific prior work, uses full scoring range, assesses all 7 dimensions with authority
- **Knowledgeable**: Hedges on niche novelty claims, provides balanced coverage, flags areas where expertise is limited
- **Some familiarity**: Defers on novelty and baseline appropriateness, excels at catching clarity and methodology issues
- **Limited knowledge**: Constrains scope to presentation and methodology, explicitly defers on domain-specific dimensions

**Each review must:**
- Use the full target-venue form: HotCRP for systems; the edition-specific OpenReview form for ML
- Set the overall merit score independently based on that reviewer's perspective and assessable dimensions
- State what the reviewer can and cannot assess at their confidence level
- Use hedging language appropriate to the confidence level (see reference below)
- Be an independent perspective — NOT a degraded copy of the expert review

The four levels use the illustrative 1-4 confidence scale; map them to the live form's scale. For detailed per-level behavioral profiles, dimension weight shifts, scoring behavior, worked examples, and anti-patterns, load `references/confidence_level_profiles.md`.

---

## Review Workflow

**Single vs. Multi-Perspective Mode**: The workflow below produces one review. In multi-perspective mode (Section 9), execute Stages 1-4 four times — once per confidence level (4, 3, 2, 1). The Expert review is generated first; each subsequent review is a fresh perspective, not a degradation of the expert review.

Follow this four-stage workflow to produce a thorough, calibrated review.

### Stage 1: First Read (understand the claims)

1. Read the title, abstract, and introduction. Identify:
   - The stated problem and why it matters
   - The key insight or approach
   - The numbered contributions (if any)
   - The target venue and its expectations
2. Skim the design and evaluation sections to understand the system architecture and experimental approach.
3. Read the conclusion to see if the narrative is coherent from introduction to conclusion.
4. Write the **Paper Summary** immediately after the first read — this forces you to articulate your understanding before diving into critique.

### Stage 2: Detailed Analysis (evaluate seven dimensions)

1. Re-read the paper carefully, section by section.
2. For each of the seven evaluation dimensions, make specific notes:
   - **Novelty**: What is the key insight? Is it genuinely new? Cite specific prior work if not.
   - **Soundness**: Are the design choices internally consistent? Check assumptions and failure modes.
   - **Significance**: If everything works as claimed, how much does it matter?
   - **Evaluation**: Map each contribution to experiments. Check baselines, workloads, metrics, statistical rigor, ablation.
   - **Presentation**: Note specific clarity issues, figure problems, or organizational weaknesses.
   - **Relevance**: Is this the right venue?
   - **Reproducibility**: Could you reproduce the results from what is described?
3. Cross-check: do the evaluation results actually support the claims in the introduction?
4. Identify the most common weakness type using the taxonomy in `references/common_paper_weaknesses.md`.

### Stage 3: Write the Review

For systems/HotCRP, write the review fields in this order:

1. **Paper Summary**: Neutral, factual, in your own words. 3-5 sentences.
2. **Strengths**: 3-6 specific positive observations, most important first. Reference sections and figures.
3. **Weaknesses**: 3-6 specific concerns with severity labels (Fatal/Major/Minor), most severe first. Each must include: what the problem is, why it matters, and how it could be addressed.
4. **Detailed Comments**: Elaborate on key points. Provide technical feedback that helps regardless of accept/reject.
5. **Questions for Authors**: 3-5 numbered questions whose answers could change your score. Flag which are critical.
6. **Overall Merit**: Score on the live form's scale (illustrative 1-5) based on the dimension assessments, calibrated to the venue's acceptance rate.
7. **Reviewer Confidence**: Honest self-assessment of your expertise.
8. **Minor Issues**: Typos, formatting, editorial items (optional).

For ML/OpenReview, load `references/ml_venue_review_forms.md` and write every field in the venue's current order. Never translate the venue's score into the illustrative systems 1-5 scale. Preserve required subscores, limitations/ethics fields, LLM-policy acknowledgement or disclosure, and post-rebuttal justification.

### Stage 4: Calibration (self-check before submission)

Run through the 8-item self-assessment checklist:

1. Does my summary demonstrate I understood the paper?
2. Does every strength and weakness reference specific sections or claims?
3. Would my review help the authors improve, even if rejected?
4. Does the tone match the score?
5. Have I evaluated the paper for what it is, not what I wish it were?
6. Have I addressed every dimension required by this venue (all seven for systems; the named form dimensions for ML)?
7. Is my summary neutral and factual?
8. Does my confidence accurately reflect my expertise?

If any answer is "no," revise before submitting.

---

## References

Read a reference only when its condition applies:

- `references/review_form_templates.md`: when filling in a systems (HotCRP-style) form, writing an example-quality review, recommending OSR, or evaluating author responses. Has field-by-field guidance, the illustrative score scales, 3 example reviews (score 5, 3, 2), and the per-venue OSR table.
- `references/review_criteria.md`: when weighting the seven dimensions for a specific systems venue or calibrating scores. Has detailed rubrics, venue-specific priorities, and scoring calibration.
- `references/review_ethics_and_tone.md`: when checking tone before delivery, rephrasing a harsh critique, or handling edge cases. Has the Roscoe and Levin-Redell frameworks, tone by score, the six anti-patterns with self-checks, and the self-assessment checklist.
- `references/common_paper_weaknesses.md`: when naming or phrasing a weakness. Has the ~27 weaknesses by section (motivation, design, evaluation, presentation, scope), severity classification, and constructive phrasing templates.
- `references/confidence_level_profiles.md`: when generating multi-perspective reviews (Section 9). Has per-confidence-level profiles, dimension weight shifts, scoring behavior, a worked 4-review example, and anti-patterns.
- `references/ml_venue_review_forms.md`: when reviewing for NeurIPS, ICML, ICLR or AAAI, or when you need an ML venue's LLM-use rules. Has edition-labelled OpenReview fields, scales, calibration, discussion duties, LLM-use policies, reproducibility and ethics guidance, and an ICML example review.
