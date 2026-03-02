# Rebuttal Response Templates and Budgeting Strategy

## Table of Contents

1. [Full Response Templates](#full-response-templates)
2. [Budgeting Strategy by Cap Size](#budgeting-strategy)
3. [Drafting Workflow](#drafting-workflow)
4. [Common Failure Modes](#common-failure-modes)

---

## Full Response Templates

### Template 1: Tight Global Rebuttal (AAAI-like, ~2500 chars)

Use when a single short response must cover all reviews. Every word must earn its place.

```
We thank the reviewers for their feedback. We address the two central concerns.

(1) [Concern A — one sentence stating reviewer's point]
[Direct correction/clarification in 2–3 sentences with evidence pointer]
Evidence: [Table X / Section Y / Line Z]

(2) [Concern B — one sentence]
[Direct correction/clarification in 2–3 sentences]
Evidence: [Table X / Section Y]

Additional clarifications:
- R1 Q2: [one-line answer]
- R2 Q3: [one-line answer]
- R3 Q1: [one-line answer]

We will revise [specific sections] to make these points explicit in the camera-ready.
```

**Principles:**
- 60–70% of budget on top 2 decision-critical concerns
- Compressed syntax: "Concern → answer → evidence"
- Remove narrative transitions; keep factual density high
- Avoid repeating thanks/praise per reviewer

---

### Template 2: Per-Review Response (NeurIPS/ICML-like, 5K–10K chars)

Use when system enforces per-review response fields.

```
We thank [Reviewer] for the constructive feedback.

**Q1. [Reviewer concern — quoted or paraphrased]**

[Yes/No/Not exactly] — [concise explanation in 2–3 sentences].

Evidence: [Section X, Table Y]. Specifically, [quote or summarize the relevant result].

We will clarify this in [specific location] of the revised manuscript.

**Q2. [Reviewer concern]**

[Direct answer]. This is shown in [pointer]. We agree the current presentation
could be clearer and will [specific revision action].

**Q3. [If limitation — acknowledge and bound]**

This is a valid observation. Our current method does not address [limitation].
The impact is bounded because [reasoning]. We will state this explicitly
in [Section].

**Summary of planned revisions:**
1. [Specific change in Section X]
2. [Additional experiment/table in Section Y]
3. [Clarified wording in Abstract/Intro]
```

**Principles:**
- One compact paragraph per major issue
- Include one concrete number or citation per disputed claim
- Reserve ~10% for revision commitments
- Bold the reviewer's question for scannability

---

### Template 3: Grouped Concern Response (best for reviewer overlap)

Use when multiple reviewers raise the same concern. Saves budget and prevents contradiction.

```
We thank all reviewers for their detailed feedback. We organize our response
by concern, tagging relevant reviewers.

## C1: Novelty and relation to [Prior Work] (R1, R3)

[Both R1 and R3] question novelty relative to [Prior]. The key differences are:
- D1: [difference] — supported by [Section/Table]
- D2: [difference] — demonstrated in [Experiment]
- D3: [difference] — [result/insight not in prior work]

We will revise Related Work (Section X) to make these deltas explicit.

## C2: Evaluation fairness (R2, R3)

[Concern summary]. Our tuning protocol: [details]. Compute budget parity:
[specifics]. Under this protocol, results are [numbers from Table Y].

We will add the tuning configuration table to improve transparency.

## C3: Scalability concern (R1)

Complexity: O([formula]). Measured runtime at scale N: [value].
Memory footprint: [value]. Compared to baseline: [ratio].
Practical deployment target: [range]. We will add this to Section Z.

## Individual clarifications
- R1 minor Q: [one-line]
- R2 minor Q: [one-line]

We will incorporate all specified revisions in the camera-ready.
```

**Principles:**
- Group shared concerns to avoid contradictory answers
- Use reviewer tags (R1, R2, R3) for traceability
- Put decision-critical concerns first
- Keep individual clarifications compressed at end

---

### Template 4: Front-Loaded "Prefix-Optimal" Response

Use when strict limits or expectation that AC scans quickly. The first 25% of the response should be self-sufficient.

```
## Key corrections (decision-critical)

1. **[Most important misunderstanding]**: [1-sentence correction + evidence].
2. **[Second most important]**: [1-sentence correction + evidence].
3. **[Third]**: [1-sentence correction + evidence].

## Detailed responses

### R1
[Expanded answers to R1's concerns]

### R2
[Expanded answers to R2's concerns]

### R3
[Expanded answers to R3's concerns]

## Revision plan
[Bullet list of concrete changes]
```

---

## Budgeting Strategy

### ~2,500 characters total (AAAI-like)
- ~1,500 chars on top 2 decision-critical concerns
- ~600 chars on additional clarifications (one-liners)
- ~400 chars on opening + revision commitments
- **Zero budget for narrative or transitions**

### 5,000 characters per review (ICML-like)
- ~2,500 chars on primary concern (1–2 paragraphs with evidence)
- ~1,500 chars on secondary concerns (1 paragraph each)
- ~500 chars on minor clarifications
- ~500 chars on revision commitments
- **Plan for follow-up round** — save strongest new evidence for it

### 10,000 characters per review (NeurIPS-like)
- Full mini-structure per concern: direct answer → evidence → clarification → revision plan
- Can afford 3–4 substantial concern blocks per review
- Still avoid rambling — long responses get skimmed
- **Front-load**: put decision-critical corrections in first 3,000 chars

### 500–1,000 words (systems venues)
- Use concern grouping aggressively
- Prioritize shared concerns over isolated nitpicks
- Put "decision pivot points" first: novelty, correctness, evaluation adequacy
- **Every sentence must pass**: "does this help the AC flip a borderline decision?"

---

## Drafting Workflow

### T+0 to T+3h: Triage
1. Parse all reviews into one concern list
2. Label each concern:
   - **Must-fix misunderstanding** (reviewer is wrong → correct with evidence)
   - **High-impact disagreement** (reviewer may be right → acknowledge and bound)
   - **Minor clarification** (easy fix → one-liner)
3. Rank by decision impact: what flips the AC's assessment?

### T+3h to T+12h: Evidence Assembly
1. Gather precise pointers: section, table, line, figure
2. Run only essential additional analyses allowed by venue
3. Draft direct answers first, prose second
4. Cross-check: no contradictions across per-reviewer responses

### T+12h to T+24h: First Full Draft
1. Use appropriate template structure
2. Ensure every major concern has explicit response
3. Keep tone neutral throughout
4. Verify within word/character limits

### T+24h to T+30h: Compression + AC Pass
1. Cut low-impact text ruthlessly
2. Make first 25% of response maximally informative
3. Read as if you are the AC — is each concern clearly addressed?
4. Have a coauthor not involved in drafting do a fresh read

### T+30h to Submit: Policy Compliance Check
- [ ] Within word/character limit
- [ ] No forbidden links/files/attachments
- [ ] Anonymity preserved (double-blind venues)
- [ ] No revised paper upload if disallowed
- [ ] No new experiments if disallowed
- [ ] Final read by at least one coauthor

---

## Common Failure Modes

| Failure | Fix |
|---------|-----|
| Defensive opening paragraph | Open with shared concern acknowledgment + constructive tone |
| No direct answers, only explanation | Begin each item with explicit yes/no/not-exactly |
| Contradictory replies to different reviewers | Maintain one shared "claim boundary" sentence and reuse it |
| Overfocus on one unfair review | Spend most budget on concerns likely to influence AC outcome |
| "We will add" everywhere without substance | Include at least one concrete clarifying argument/result now |
| Unmarked uncertainty | Explicitly state what is unknown or not yet evaluated |
| Exceeding limit | Draft at 80% of limit, then expand selectively |
| Tone escalation on poor reviews | Write factual correction, delete emotional language, wait 6h, re-read |
