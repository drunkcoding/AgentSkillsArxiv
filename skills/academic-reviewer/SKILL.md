---
name: academic-reviewer
description: "Review systems conference papers for OSDI, NSDI, SIGCOMM, MOBICOM, SOSP, and FAST. Produces structured HotCRP-style reviews with paper summary, strengths, weaknesses, detailed comments, questions for authors, and overall merit/confidence scoring. Covers evaluation criteria (novelty, soundness, significance, evaluation quality, clarity, relevance, reproducibility), venue-specific expectations, common paper weaknesses, constructive feedback tone, one-shot revision reviews, and reviewer ethics. Use when asked to review, critique, or provide feedback on a systems conference paper submission."
---

# Systems Conference Paper Reviewing

## Core Capabilities

### 1. Review Structure and Format

All reviews follow the HotCRP form structure used by OSDI, NSDI, SIGCOMM, MOBICOM, SOSP, and FAST:

| Field | Required | Content |
|-------|----------|---------|
| Overall Merit | Yes | Score 1-5 with calibrated justification |
| Reviewer Confidence | Yes | Score 1-4 reflecting actual expertise |
| Paper Summary | Yes | 3-5 sentence neutral summary in your own words |
| Strengths | Yes | 3-6 specific, prioritized positive observations |
| Weaknesses | Yes | 3-6 specific, prioritized concerns with severity labels |
| Detailed Comments | Yes | Technical feedback, elaboration, suggestions |
| Questions for Authors | Recommended | 3-5 numbered questions that could change your assessment |
| Minor Issues | Optional | Typos, formatting, editorial items |

For detailed field-by-field guidance and complete example reviews, load `references/review_form_templates.md`.

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

For detailed rubrics (5-point scale per dimension), venue-specific weights, and specific checks, load `references/review_criteria.md`.

### 3. Venue-Specific Review Expectations

Each venue has a distinct review culture. Adjust your emphasis accordingly.

| Venue | Philosophy | Top Priorities | Acceptance Rate |
|-------|-----------|---------------|----------------|
| **OSDI** | "Exciting papers over boring papers" | Novelty, significance, broad systems impact | ~15-18% |
| **NSDI** | Deployment value matters | Significance, realistic evaluation, practical novelty | ~18-20% |
| **SIGCOMM** | "Lasting impact on the field" | Novelty, significance, rigorous networking analysis | ~15% |
| **MOBICOM** | Works in the real physical world | Soundness, real-world evaluation, wireless rigor | ~18-20% |
| **SOSP** | "Novel abstractions AND real systems" | Novelty, soundness, significance, artifact required | ~15% |
| **FAST** | "Storage depth and practical impact" | Significance, evaluation quality, storage relevance | ~20% |

**Key venue-specific notes:**
- **OSDI**: Would you enthusiastically champion this paper? "Exciting and imperfect" can beat "boring and thorough."
- **NSDI**: Could this system actually be deployed? Production experience and operational lessons get extra credit. One-shot revision (OSR) available for borderline papers.
- **SIGCOMM**: Scores of 3+ generally indicate acceptability. Papers need a strong advocate. The networking contribution must be clear and substantial.
- **MOBICOM**: Real-world wireless experiments strongly preferred over simulation. Multiple environments and conditions required. Signal-level analysis expected.
- **SOSP**: Must present new abstractions or principles, not just "faster X." Artifact evaluation is mandatory. The system must be real and substantial.
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

**Overall Merit (1-5):**

| Score | Label | Meaning | Action |
|-------|-------|---------|--------|
| 5 | Strong Accept | Top 5-10%. You will champion this paper. | Accept |
| 4 | Accept | Above the bar. Solid contribution, minor issues only. | Likely accept |
| 3 | Borderline | Real merit but notable weaknesses. Could go either way. | Discuss |
| 2 | Weak Reject | Some merit but significant problems. Below the bar. | Likely reject |
| 1 | Strong Reject | Fundamental problems. Not suitable even with revision. | Reject |

**Reviewer Confidence (1-4):**

| Score | Label | Meaning |
|-------|-------|---------|
| 4 | Expert | Published in this area. Know the state of the art deeply. |
| 3 | Knowledgeable | Read extensively. Familiar with key prior work. |
| 2 | Some familiarity | General systems knowledge. May miss domain nuances. |
| 1 | Limited knowledge | Outside your area. Focus on methodology and presentation. |

**Calibration reminders:**
- At ~15-20% acceptance, score 3 means "uncertain" — not "acceptable"
- Most accepted papers need at least one score of 4 or 5
- Use the full range: a clearly flawed paper should get 1 or 2, not a generous 3
- ~15-20% of papers you review should receive 4 or higher

For full scoring rubrics and example reviews at each score level, load `references/review_form_templates.md`.

### 7. One-Shot Revision (OSR) Reviews

Available at NSDI, SIGCOMM, MOBICOM, and FAST. OSR means a conditional accept with specific required changes.

**When to recommend OSR:**
- Core contribution is sound and significant
- Weaknesses are fixable within 4-6 weeks
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

For OSR templates and venue-specific guidelines, load `references/review_form_templates.md`.

### 8. Review Anti-Patterns

Avoid these six common reviewer behaviors:

| Anti-Pattern | Description | Self-Check |
|-------------|-------------|------------|
| **Wish-List Reviewer** | Criticizes the paper for not solving a different problem | "Am I evaluating the stated scope, or imposing my preferred scope?" |
| **Benchmark Bully** | Demands specific baselines without justification | "Have I explained what the requested baseline would reveal?" |
| **Nitpick Reviewer** | Focuses on minor presentation issues, ignores substance | "Are my weaknesses mostly about formatting rather than the contribution?" |
| **Silent Rejector** | Low score with minimal justification | "Have I provided a specific, verifiable reason for every negative claim?" |
| **Positivity Mismatch** | Positive text with low score, or critical text with high score | "Would someone reading only the text guess my score correctly?" |
| **Copy-Paste Reviewer** | Generic language that could apply to any paper | "Could my review be applied to a different paper with minimal changes?" |

For detailed descriptions and examples, load `references/review_ethics_and_tone.md`.

### 9. Multi-Perspective Review Generation

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
- Use the full HotCRP form (summary, strengths, weaknesses, detailed comments, questions, merit, confidence)
- Set the overall merit score independently based on that reviewer's perspective and assessable dimensions
- State what the reviewer can and cannot assess at their confidence level
- Use hedging language appropriate to the confidence level (see reference below)
- Be an independent perspective — NOT a degraded copy of the expert review

For detailed per-level behavioral profiles, dimension weight shifts, scoring behavior, worked examples, and anti-patterns, load `references/confidence_level_profiles.md`.

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

Write the review fields in this order:

1. **Paper Summary**: Neutral, factual, in your own words. 3-5 sentences.
2. **Strengths**: 3-6 specific positive observations, most important first. Reference sections and figures.
3. **Weaknesses**: 3-6 specific concerns with severity labels (Fatal/Major/Minor), most severe first. Each must include: what the problem is, why it matters, and how it could be addressed.
4. **Detailed Comments**: Elaborate on key points. Provide technical feedback that helps regardless of accept/reject.
5. **Questions for Authors**: 3-5 numbered questions whose answers could change your score. Flag which are critical.
6. **Overall Merit**: Score 1-5 based on the dimension assessments, calibrated to venue acceptance rate.
7. **Reviewer Confidence**: Honest self-assessment of your expertise.
8. **Minor Issues**: Typos, formatting, editorial items (optional).

### Stage 4: Calibration (self-check before submission)

Run through the 8-item self-assessment checklist:

1. Does my summary demonstrate I understood the paper?
2. Does every strength and weakness reference specific sections or claims?
3. Would my review help the authors improve, even if rejected?
4. Does the tone match the score?
5. Have I evaluated the paper for what it is, not what I wish it were?
6. Have I addressed all seven dimensions?
7. Is my summary neutral and factual?
8. Does my confidence accurately reflect my expertise?

If any answer is "no," revise before submitting.

---

## References

This skill includes comprehensive reference files covering specific aspects of systems paper reviewing:

- `references/review_criteria.md`: Detailed rubrics for all 7 evaluation dimensions, venue-specific review priorities and weights, and scoring calibration guidelines
- `references/review_form_templates.md`: HotCRP field-by-field guide, 3 complete example reviews (score 5, 3, and 2), and one-shot revision templates
- `references/review_ethics_and_tone.md`: Roscoe and Levin-Redell frameworks, constructive vs. destructive critique examples, tone calibration by score, 6 anti-patterns, self-assessment checklist, and edge case handling
- `references/common_paper_weaknesses.md`: Catalog of ~27 common weaknesses by section (motivation, design, evaluation, presentation, scope), severity classification, and constructive phrasing templates
- `references/confidence_level_profiles.md`: Per-confidence-level behavioral profiles, dimension weight shifts, scoring behavior, worked 4-review example, and multi-perspective anti-patterns

Load these references as needed when working on specific aspects of paper reviewing.