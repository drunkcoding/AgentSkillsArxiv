---
name: academic-rebuttal
description: "Write conference paper rebuttals and author responses that effectively counter incorrect or unreasonable reviewer comments. Targets systems venues (OSDI, NSDI, SIGCOMM, MOBICOM, SOSP, ASPLOS, EuroSys, USENIX Security, CCS, PLDI) on HotCRP and ML venues (NeurIPS, ICML, ICLR, AAAI) on OpenReview. Core focus: identify and resolve reviewer false impressions with evidence-backed, firm-but-professional corrections. Covers rebuttal triage, false impression taxonomy (8 types with resolution playbooks), venue-specific constraints, response structure patterns, and ready-to-use phrase templates. Use when asked to write, draft, review, or improve a conference paper rebuttal, author response, or response to reviewer comments."
---

# Conference Paper Rebuttal Writing

## Core Purpose

Write rebuttals that **reject wrong reviewer comments with evidence** while maintaining professional tone. The primary function is correcting false impressions that would otherwise sink a paper at the AC/PC discussion stage.

**Guiding principle:** rebuttals win when they remove decision-critical false impressions quickly, politely, and with concrete evidence. Everything else — style, verbosity, rhetoric — is secondary.

## Rebuttal Workflow

### Stage 1: Triage Reviews (first 3 hours)

1. Extract every distinct concern from all reviews into a flat list.
2. Classify each concern:

| Label | Meaning | Rebuttal Priority |
|-------|---------|-------------------|
| **FI** (False Impression) | Reviewer is factually wrong or misunderstood the paper | **Highest** — correct with evidence |
| **VW** (Valid Weakness) | Reviewer identified a real limitation | **High** — acknowledge, bound impact, commit revision |
| **DQ** (Direct Question) | Reviewer asks a specific question | **Medium** — answer directly |
| **MC** (Minor Clarification) | Wording, typo, or presentation concern | **Low** — one-liner if budget allows |

3. Rank by **decision impact**: what would flip the AC's assessment from reject to accept?
4. Check venue constraints before drafting. Load `references/venue_policies.md` for limits, format, and what is allowed/forbidden.

### Stage 2: Draft Response

1. Select response structure based on venue (see [Response Patterns](#response-patterns)).
2. For each FI concern, apply the matching [False Impression Playbook](#false-impression-taxonomy).
3. For each VW concern, acknowledge → bound impact → commit concrete revision.
4. For DQ, answer directly with evidence pointer.
5. Cross-check: no contradictions across per-reviewer responses.

### Stage 3: Compress and Verify

1. Cut to 80% of limit, then selectively expand highest-impact items.
2. Front-load: the first 25% must be self-sufficient for a scanning AC.
3. Policy compliance check:
   - Within word/character limit
   - No forbidden links/files/attachments
   - Anonymity preserved (double-blind venues)
   - No new experiments if venue disallows
4. Coauthor review pass before submission.

### Self-Awareness Check

Before classifying a concern as FI (False Impression), verify:

- Did you re-read the relevant paper section from the reviewer's perspective?
- Could a reasonable reader reach the reviewer's interpretation?
- Is the concern actually a VW (Valid Weakness) that you are reluctant to admit?

**If in doubt, treat it as VW.** Wrongly dismissing a valid concern destroys credibility with the AC.

---

## False Impression Taxonomy

Eight types of false impressions with resolution strategies. Each includes: what happened, why, and how to correct it.

### FI-1: Scope Misread
**Reviewer believes the paper claims broader scope than it supports.**
Typical trigger: overgeneralized abstract/introduction.

**Resolution:**
1. Narrow claim explicitly in first sentence.
2. State what IS and IS NOT claimed.
3. Anchor to exact experiment/theorem boundary.

> "Thank you — this is a helpful point. Our claim is limited to **[specific regime]**, not **[broader regime]**. We will revise Abstract/Intro wording. Evidence for the supported scope is in [Table/Section]."

### FI-2: Method Mechanics Misunderstanding
**Reviewer believes the method uses/assumes X, but it does not.**
Typical trigger: notation density, unclear pseudocode.

**Resolution:**
1. Start with direct yes/no.
2. Give method in 3–4 steps.
3. Explain where confusion arose, commit to textual fix.

> "Short answer: **No, our method does not use X at test time.** Pipeline: (1)… (2)… (3)… (4)… We agree this was insufficiently explicit and will add this summary to Sec. [N]."

### FI-3: Baseline Fairness Dispute
**Reviewer claims comparison is unfair or baseline is weakly tuned.**
Typical trigger: missing hyperparameter/tuning details.

**Resolution:**
1. State tuning protocol and compute parity.
2. Report numbers under controlled conditions.
3. Add/offer missing baseline if already run; if not, explain why and bound likely effect.

> "We used identical tuning budget across methods: [details]. For baseline B, we followed [reference/config]. Results: [numbers]. We will add the tuning table."

### FI-4: Novelty Conflation
**Reviewer conflates contribution with prior work ("already known").**
Typical trigger: under-specified related work deltas.

**Resolution:**
1. Acknowledge overlap plainly.
2. Enumerate exact differentiators (D1, D2, D3).
3. Tie each to concrete section/result.

> "We agree our work builds on [prior]. The novelty is: D1: [diff] (Sec X), D2: [diff] (Table Y), D3: [new finding] (Experiment Z). We will revise Related Work."

### FI-5: Statistical Evidence Doubt
**Reviewer questions significance or reports "could be noise."**
Typical trigger: point estimates without variance/testing.

**Resolution:**
1. Provide seed count, variance, statistical test.
2. Distinguish significance from practical effect size.

> "We report mean±std over [n] seeds with [test]. Improvement: [x]% with [CI/p]. We will add effect-size framing to results discussion."

### FI-6: Scalability/Practicality Assumption
**Reviewer assumes method is impractical at realistic scale.**
Typical trigger: no complexity/runtime/memory table.

**Resolution:**
1. Provide asymptotic + measured runtime/memory.
2. Compare against baseline under matched hardware.
3. Clarify deployment envelope.

> "Complexity: O(…). Measured at scale N: [values]. Compared to baseline: [ratio]. Deployment target: [range]. We will add this to Sec [N]."

### FI-7: Wrong Evaluation Criteria
**Reviewer judges paper by criteria for a different subfield.**
Typical trigger: cross-disciplinary PC assignment.

**Resolution:**
1. Respectfully restate the paper's evaluation criteria and venue norms.
2. Show how the evaluation matches the stated contributions.
3. Point to venue-accepted precedent if possible.

> "We respectfully note that [venue] systems papers typically evaluate [metrics], as exemplified by [accepted paper]. Our evaluation follows this convention (Sec X). The [different metric] R2 suggests is standard in [other field] but not typically expected here."

### FI-8: Scoped-Out Experiment Request
**Reviewer demands an experiment the paper intentionally excluded.**
Typical trigger: different assumptions about evaluation scope.

**Resolution:**
1. Acknowledge the experiment would be interesting.
2. Explain why it was scoped out (compute, data access, orthogonal concern).
3. Provide proxy analysis if available.
4. If venue allows and feasible, offer to add it.

> "This is a valuable suggestion. We scoped [experiment] out because [reason]. As a proxy, [analysis/ablation] in Sec X suggests [bounded effect]. We will [add in revision / clarify scope statement]."

---

## Universal 5-Step Correction Sequence

Use for any false impression when in doubt about structure:

1. **Acknowledge** — "This is an important point."
2. **Direct correction** — Yes/no + corrected factual statement.
3. **Evidence** — Table, section, figure, or result pointer.
4. **Responsibility** — "We see how the current wording caused confusion."
5. **Concrete revision** — Exactly what text/section will change.

This sequence defuses tone risk while maximizing decision usefulness for the AC.

---

## Response Patterns

### Pattern A: Per-Review (NeurIPS/ICML)
System enforces per-review fields. Inside each:
1. One-line appreciation
2. Direct answer to primary concern
3. Evidence bullets
4. Short "we will clarify X in revision" line

### Pattern B: Single Global (AAAI, tight cap)
One response covering all reviews:
1. 2–3 line global summary
2. Top 2 concerns subsection
3. Additional clarifications as one-liners
4. Close with revision commitments

### Pattern C: Grouped by Concern (systems venues, reviewer overlap)
Group by concern, tag reviewers per item:
- **C1: Novelty clarification (R1, R3)**
- **C2: Evaluation fairness (R2, R3)**
- **C3: Runtime concern (R1)**

Saves budget, prevents contradictions across reviewers.

### Pattern D: Front-Loaded / Prefix-Optimal
Put highest-impact corrections first. First 25% is self-sufficient. Use when AC expected to scan quickly or at strict limits.

For full templates with examples and budgeting strategy by cap size, load `references/rebuttal_templates.md`.

---

## Phrase Templates

### Polite Factual Correction
> "Thank you for raising this. There appears to be a misunderstanding: we do **not** [incorrect interpretation]. We instead [correct statement], as shown in [Section/Table]. We will revise [location] to prevent this confusion."

### Already-in-Paper but Missed
> "The result is in [Sec X, lines Y–Z], but we agree it is easy to miss. We will move this to [more prominent location] and restate it clearly."

### Providing Requested Experiment (Allowed)
> "We ran the requested comparison: [setting]. Result: [number]. Consistent with our claim [claim]. We will include this in the revision."

### Requested Experiment Not Feasible
> "This is a valuable suggestion. [Venue rule or constraint] prevents adding experiment X now. To address the concern, we provide [proxy analysis] and clarify scope accordingly."

### Novelty Dispute
> "We agree our work is related to [prior]. Key differences: (1) …, (2) …, (3) … . We will revise Related Work to make these distinctions explicit."

### Strong but Professional Disagreement
> "We respectfully disagree with the premise that [premise]. Under [assumption], evidence in [table/theorem] indicates [result]. We will clarify the assumption boundary."

### Acknowledging Valid Weakness
> "This limitation is real. Our method does not address [limitation]. We will state this explicitly and narrow the claim to [supported scope]."

### Closing
> "We appreciate the reviewers' input and believe these clarifications address the key concerns. We will incorporate the specified revisions in the camera-ready manuscript."

---

## What Authors Can Do

1. Correct factual errors and misunderstandings with evidence.
2. Clarify ambiguous definitions, assumptions, and scope.
3. Point to exact paper locations (section/table/line) and restate.
4. Provide additional experimental results when venue permits.
5. Show revised text snippets for camera-ready.
6. Acknowledge valid limitations and bound their impact.
7. Consolidate repeated concerns across reviewers.
8. Prioritize by decision impact, not emotional salience.

## What Authors Must Not Do

1. Exceed strict word/character limits.
2. Include forbidden links/files when disallowed.
3. Upload revised paper when venue forbids it during feedback.
4. Reveal identity in double-blind venues.
5. Use hostile, sarcastic, or dismissive tone.
6. Claim reviewer is wrong without concrete evidence.
7. Introduce major new contributions not in the submission.
8. Promise changes that fundamentally alter the paper's scope.
9. Ignore negative reviews or cherry-pick which concerns to address.

---

## References

- `references/venue_policies.md`: Per-venue rebuttal constraints (limits, platform, format, what is allowed/forbidden) for 14 venues across OpenReview and HotCRP
- `references/platform_mechanics.md`: OpenReview vs HotCRP platform mechanics (configuration, formatting, visibility models, author actions)
- `references/rebuttal_templates.md`: 4 full response templates, budgeting strategy by cap size, end-to-end drafting workflow, and common failure modes

Load these references as needed when working on specific aspects of rebuttal writing.
