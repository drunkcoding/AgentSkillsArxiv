# Review Ethics and Tone

This reference covers reviewer frameworks, constructive tone guidelines, anti-patterns to avoid, and edge case handling for systems conference paper reviews.

---

## 1. The Roscoe Framework

Based on Timothy Roscoe's "Writing Reviews for Systems Conferences," this framework provides seven guiding questions for evaluating systems papers. These questions help reviewers focus on what matters and produce useful feedback.

### 1.1 The Seven Questions

**Q1: Does the paper present original ideas?**
- Are the ideas genuinely new, or a recombination of known techniques?
- Has the paper adequately surveyed prior work to establish novelty?
- Even if the individual techniques exist, does the combination reveal something new?
- Beware of dismissing work as "not novel" without citing the specific prior work that anticipates it.

**Q2: Is it a real system?**
- Has the system been built and does it work?
- Is there evidence beyond simulation or analytical modeling?
- Can the system handle real workloads at realistic scale?
- A working system with limitations is more valuable than a perfect design that exists only on paper.

**Q3: Does the paper teach real lessons?**
- What does the reader learn from this paper that they did not know before?
- Are there insights that generalize beyond the specific system?
- Does the paper honestly discuss what did NOT work and why?
- Lessons from failure or unexpected behavior are often the most valuable contributions.

**Q4: Are the choices sensible?**
- Given the problem constraints, are the design decisions reasonable?
- Does the paper consider alternatives and justify its choices?
- Are the trade-offs clearly stated and appropriate for the target workload?
- A system that makes different trade-offs from prior work is not wrong — it serves a different point in the design space.

**Q5: Does the paper place the work in context?**
- Is the related work complete and fairly characterized?
- Does the paper explain how it relates to and differs from prior systems?
- Are the comparisons honest (not strawmen)?
- Does the paper acknowledge its own limitations?

**Q6: Does the paper focus?**
- Does the paper have a clear, coherent story?
- Are all sections contributing to the main narrative?
- Is the paper trying to do too many things (and doing none well)?
- A focused paper that does one thing convincingly is better than a scattered paper that touches five topics.

**Q7: Is the paper well-presented?**
- Is the writing clear and concise?
- Are figures effective and well-designed?
- Does the paper flow logically?
- Can you understand the main ideas on a first reading?

### 1.2 Common Reviewer Mistakes Per Question

| Question | Common Mistake | Correction |
|----------|---------------|------------|
| Q1 (Original ideas) | Claiming "not novel" without citing the specific prior work that anticipates the contribution. | Always provide a concrete citation. If you cannot name the prior work, soften to "the novelty is unclear to me." |
| Q2 (Real system) | Equating a small prototype with "not a real system." A 5K-LOC prototype that runs real workloads can be a real system. | Judge whether the system is functional enough to validate the design, not whether it is production-ready. |
| Q3 (Real lessons) | Expecting only positive lessons. Papers that teach "this approach does NOT work, and here is why" are equally valuable. | Value negative results and honest failure discussions as lessons. |
| Q4 (Sensible choices) | Penalizing design trade-offs that differ from your preferred approach. Different trade-offs serve different points in the design space. | Ask "are these trade-offs reasonable for the stated goals?" not "would I have made the same choices?" |
| Q5 (Context) | Treating incomplete related work as a fatal flaw. Missing one paper is minor; missing an entire research thread is major. | Distinguish between "the authors missed paper X" (minor, fixable) and "the authors are unaware of research area Y" (major). |
| Q6 (Focus) | Confusing breadth of contribution with lack of focus. A paper can address multiple aspects of a single coherent problem. | Ask whether all parts serve a single story, not whether the paper addresses exactly one technique. |
| Q7 (Presentation) | Letting writing quality dominate the review. Poor writing is fixable; a poor contribution is not. | Assess writing separately from technical merit. Writing issues belong in "Minor Issues," not "Weaknesses." |

### 1.3 Inter-Question Interactions and Priority Ordering

The seven questions are not independent. Use this priority ordering to guide your assessment:

1. **Q1 + Q3 first** (novelty and lessons): If the paper has neither new ideas nor new lessons, other questions are moot — the contribution is insufficient regardless of execution quality.
2. **Q2 + Q4 next** (real system with sensible choices): A paper with new ideas must demonstrate them in a working system with defensible design trade-offs.
3. **Q5 + Q6 then** (context and focus): Verify the contribution is properly positioned and the paper tells a coherent story.
4. **Q7 last** (presentation): Only after assessing substance should you evaluate the presentation.

**Key principle from Roscoe**: The reviewer's job is to help the PC make a good decision AND to help the authors improve their work. Both goals matter, even for papers you recommend rejecting.

---

## 2. The Levin-Redell Framework

Roy Levin and David Redell proposed a complementary evaluation approach focused on two questions about lasting value.

### 2.1 Contribution to the Field

**Question**: What does this paper contribute to the systems community's collective knowledge?

**Sub-questions**:
- Would you recommend this paper to a colleague working in this area?
- Would you cite this paper in your own future work?
- Does the paper change how you think about a problem or design space?
- Would a practitioner change their approach after reading this paper?

**Contribution types** (from most to least impactful):
1. **New abstraction**: Introduces a concept or interface that others will build on (e.g., MapReduce, containers, RDMA verbs)
2. **New understanding**: Reveals something about system behavior that was not previously known (e.g., measurement studies, failure analyses)
3. **New technique**: Provides a method that others can apply to their systems (e.g., specific scheduling algorithms, compression schemes)
4. **New system point**: Demonstrates that a particular set of trade-offs is viable and useful (e.g., eventual consistency works for shopping carts)
5. **New benchmark or methodology**: Provides tools for others to evaluate their work

### 2.2 Teaching Value

**Question**: Would you use this paper in a graduate systems course?

**What makes a paper teach well**:
- Clear problem motivation that students can relate to
- Design rationale that illustrates general systems principles
- Evaluation that demonstrates good experimental methodology
- Honest discussion of limitations and trade-offs
- Writing quality that serves as a model for students

**Note**: Teaching value is not the same as novelty. A paper with modest novelty but excellent exposition of a useful technique may have high teaching value. Conversely, a highly novel paper with poor writing may have low teaching value despite strong research contribution.

### 2.3 Examples by Contribution Type

| Type | Example Paper (hypothetical) | Why It Fits This Type |
|------|------------------------------|----------------------|
| New abstraction | "MapReduce: Simplified Data Processing on Large Clusters" | Introduced a programming model that became the standard interface for distributed batch processing. Others built entire ecosystems on this abstraction. |
| New understanding | "An Analysis of Linux Scalability to Many Cores" | Revealed that Linux kernel bottlenecks follow predictable patterns as core counts increase. Changed how OS developers think about scalability. |
| New technique | "RAFT: In Search of an Understandable Consensus Algorithm" | Provided a consensus algorithm that is functionally equivalent to Paxos but easier to implement correctly. Widely adopted due to clarity. |
| New system point | "Dynamo: Amazon's Highly Available Key-value Store" | Demonstrated that eventual consistency with client-side conflict resolution is viable for production shopping carts. Validated a specific trade-off. |
| New benchmark | "DeathStarBench: Benchmarking Cloud Microservices" | Provided representative microservice benchmarks that the community adopted for evaluation. |

### 2.4 Common Confusions Between Contribution Types

- **New abstraction vs. new technique**: An abstraction defines an interface or concept that others build on; a technique provides a method within an existing interface. If other papers cite the work to *use* its API/concept, it is an abstraction. If they cite it to *apply* its method, it is a technique.
- **New understanding vs. new system point**: Understanding reveals a general principle ("caches exhibit bimodal miss rates"); a system point demonstrates a specific design is viable ("this particular cache design works for this workload"). Understanding generalizes; a system point validates.
- **New technique vs. new system point**: A technique is reusable across systems ("this scheduling algorithm can be applied to any cluster scheduler"); a system point is specific ("this combination of design choices works for this problem").

---

## 3. Constructive vs. Destructive Critique

The goal of reviewing is to produce feedback that is honest, specific, and helpful. Every criticism should be phrased so the authors know exactly what the problem is and how to address it.

### 3.1 Principles of Constructive Criticism

1. **Be specific**: Point to exact sections, figures, equations, or claims
2. **Explain impact**: Say why the issue matters, not just that it exists
3. **Suggest remedies**: Where possible, indicate what would fix the problem
4. **Acknowledge effort**: Recognize what the authors did well before criticizing
5. **Separate severity**: Distinguish between fatal flaws and fixable issues
6. **Stay technical**: Critique the work, not the authors

### 3.2 Constructive Rephrasing Examples

**Evaluation criticism:**

| Destructive | Constructive |
|-------------|-------------|
| "The evaluation is weak." | "The evaluation would be strengthened by comparing against [specific baseline] on [specific workload], since the current baselines do not represent the state of the art." |
| "The experiments are not convincing." | "The throughput results in Figure 5 lack error bars. Given the variance typically seen in networked systems, multiple trials with confidence intervals would strengthen the claims." |
| "Cherry-picked results." | "The evaluation reports only the best-case workload (read-heavy, uniform key distribution). Including write-heavy and skewed workloads would test the system under more challenging conditions." |

**Novelty criticism:**

| Destructive | Constructive |
|-------------|-------------|
| "This is not novel." | "The approach is similar to [specific system, citation]. The paper should clarify how it differs, particularly in [specific aspect]." |
| "Incremental work." | "The main technique (adaptive partitioning) was introduced by [citation]. The contribution here appears to be applying it to [new context]. The paper should articulate what new challenges arise in this context." |
| "I've seen this before." | "This approach shares similarities with [X] in [specific way]. The paper would benefit from a more detailed comparison highlighting the technical differences." |

**Design criticism:**

| Destructive | Constructive |
|-------------|-------------|
| "The design is naive." | "The design assumes [specific assumption], which may not hold when [specific condition]. Section 4 should discuss how the system behaves when this assumption is violated." |
| "This won't work in practice." | "The prototype handles up to 10 nodes, but the target deployment is 1000+ nodes. The paper should discuss the scalability challenges (e.g., controller bottleneck, state synchronization overhead) and ideally include a simulation at larger scale." |
| "Overly complex." | "The system introduces [specific component] to handle [specific case], but Section 6.2 shows this case occurs in <2% of workloads. Consider whether the added complexity is justified by the marginal performance gain." |

**Scope criticism:**

| Destructive | Constructive |
|-------------|-------------|
| "Too narrow." | "The system targets [specific scenario], which limits the potential impact. The paper would be strengthened by discussing how the key ideas could generalize to [broader class of problems], or by demonstrating applicability in at least one additional domain." |
| "Not enough for a top venue." | "The contribution addresses a real problem, but the scope — [specific limitation] — may be too narrow for [venue]. Expanding to cover [related scenario] or deepening the evaluation of the core contribution would strengthen the case." |
| "This should be a workshop paper." | "The ideas here are promising but currently at an early stage. A full venue paper would benefit from [specific additions: broader evaluation, more baselines, deeper analysis]. Consider developing [specific aspect] further." |

**Significance criticism:**

| Destructive | Constructive |
|-------------|-------------|
| "This doesn't matter." | "The problem is clearly articulated, but the paper would benefit from stronger evidence of real-world impact. Can the authors provide data on how many systems or users are affected by [problem X], or cite industry reports documenting the issue?" |
| "Marginal improvement." | "The improvement of [X%] over [baseline] is modest. To justify the added complexity of the proposed system, the paper should either demonstrate larger gains on more challenging workloads, or argue that even modest gains at this scale translate to significant cost savings." |
| "Nobody will use this." | "The deployment barrier for this system appears high due to [specific requirement]. The paper would benefit from a discussion of the adoption path — what changes would a practitioner need to make to their existing infrastructure?" |

**Writing criticism:**

| Destructive | Constructive |
|-------------|-------------|
| "Badly written." | "The paper would benefit from a clearer presentation of the key insight. Currently, the main technical contribution (Section 4.2) is not introduced until page 6. Consider restructuring the introduction to preview this insight earlier." |
| "Hard to follow." | "The forward reference to the 'consistency protocol' on page 3 is confusing because the protocol is not defined until page 7. Consider either defining the term earlier or restructuring to avoid the forward reference." |
| "Too much jargon." | "Terms like 'speculative pre-staging' and 'temporal co-location' are used without definition in Section 3. Please define these terms at first use or add a brief terminology section." |

### 3.3 The "Even If Rejected" Test

Before submitting your review, ask: **"If this paper is rejected, will my review help the authors write a better version?"**

If the answer is no, revise your review. Every review — especially negative ones — should contain actionable feedback. The authors invested months or years in this work; the review should respect that investment.

---

## 4. Tone Calibration by Score Level

Your review's tone should match your score. Mismatched tone (harsh words + high score, or gentle words + low score) confuses authors and PC members.

### Score 5 (Strong Accept)
**Tone**: Enthusiastic, specific about what is excellent, still notes minor issues.
- Lead with genuine enthusiasm: "This is an important paper that I strongly support."
- Explain WHY you are enthusiastic — which specific aspects impress you
- Minor weaknesses framed as suggestions for camera-ready: "One small improvement..."
- Questions are genuine curiosity, not skepticism: "I'd be interested to know if..."

### Score 4 (Accept)
**Tone**: Positive and supportive, with clearly bounded concerns.
- Lead with clear support: "A solid contribution that I recommend accepting."
- Strengths first, then weaknesses with clear severity labels
- Weaknesses framed as improvements: "The paper would be even stronger with..."
- Convey that weaknesses do not undermine the core contribution

### Score 3 (Borderline)
**Tone**: Balanced, honest about both merits and concerns, explicitly uncertain.
- Acknowledge what is good: "The paper tackles an interesting problem and presents a working system."
- State concerns clearly but without dismissiveness: "However, I have concerns about..."
- Be explicit about what would change your mind: "If the authors can show X, I would move to accept."
- Signal openness to discussion: "I look forward to the author response on these points."

### Score 2 (Weak Reject)
**Tone**: Respectful, specific about problems, constructive about improvements.
- Acknowledge effort and any positive aspects first
- State problems clearly with evidence: "The main barrier to acceptance is..."
- Be concrete about what a revision would need: "A revised version should address..."
- Avoid condescension: treat the authors as peers who made specific mistakes, not as incompetent
- Frame as "not ready yet" rather than "not good enough"

### Score 1 (Strong Reject)
**Tone**: Direct, factual, still professional. Even fatally flawed papers deserve respectful reviews.
- State the fundamental issue immediately: "The core approach has a fundamental flaw..."
- Explain the flaw precisely with technical evidence
- If possible, suggest a different direction: "The measurement data in Section 2 is valuable; the authors might consider..."
- Keep the review concise — a long review for a score-1 paper wastes everyone's time
- Never be cruel, sarcastic, or dismissive

---

## 5. Reviewer Anti-Patterns

These are common reviewer behaviors that produce unhelpful reviews. Avoid them.

### 5.1 The Wish-List Reviewer

**Pattern**: Criticizes the paper for not solving a different (often harder) problem than the one it addresses.

**Examples**:
- "The paper should also handle Byzantine faults" (when the paper explicitly targets crash-stop failures)
- "Why not also support heterogeneous hardware?" (when the paper focuses on homogeneous clusters)
- "This should work for all possible workloads" (when the paper targets a specific, well-motivated class)

**Why it is harmful**: Every system makes trade-offs. Criticizing a system for the trade-offs it chose — rather than evaluating whether those trade-offs are reasonable for the stated goals — is unfair.

**Self-check**: Before writing a "the paper should also..." criticism, ask: "Is the paper's stated scope too narrow for a venue contribution, or am I imposing my preferred scope?"

### 5.2 The Benchmark Bully

**Pattern**: Demands specific baselines or workloads without justifying why they are necessary, often based on what the reviewer's own work uses.

**Examples**:
- "You must compare against [my system]" (without explaining why it is relevant)
- "Why didn't you use [specific benchmark]?" (without explaining what it would reveal)
- Insisting on a specific evaluation methodology when alternatives are equally valid

**Why it is harmful**: Authors cannot anticipate every possible baseline demand. Requests for additional comparisons should be justified by what they would reveal about the system's properties.

**Self-check**: Before requesting a baseline, explain: "Comparing against X is important because it would test [specific property] that the current evaluation does not cover."

### 5.3 The Nitpick Reviewer

**Pattern**: Focuses review on minor presentation issues while ignoring or underweighting technical substance.

**Examples**:
- Half the review is about typos and formatting
- "Figure 3 should use a different color scheme" as a major weakness
- Detailed critique of writing style with no assessment of the technical contribution
- Lowering the score due to presentation issues in an otherwise strong paper

**Why it is harmful**: Minor issues can be fixed in camera-ready. A review that focuses on them fails to assess what matters: is the contribution sound, novel, and significant?

**Self-check**: If your weaknesses section is mostly presentation issues, step back and re-evaluate the technical substance. Presentation issues should go in "Minor Issues," not "Weaknesses."

### 5.4 The Silent Rejector

**Pattern**: Gives a low score with minimal justification. The review is too short or vague for authors to understand why their paper was rejected.

**Examples**:
- "Not enough novelty. Score: 2." (without citing what prior work anticipates the contribution)
- "The evaluation is not convincing." (without specifying what is missing)
- A review shorter than 200 words for a 12-page paper

**Why it is harmful**: Authors cannot improve from vague feedback. The PC cannot calibrate scores from unjustified reviews. This is the most common complaint from authors about the review process.

**Self-check**: For every negative claim, ask: "Have I provided a specific, verifiable reason?" If not, add one.

### 5.5 The Positivity Mismatch Reviewer

**Pattern**: Writes a review that sounds positive but assigns a low score, or writes a critical review with a high score.

**Examples**:
- "Interesting paper with nice results! Score: 2."
- "Several fundamental issues undermine the contribution. Score: 4."
- Strengths section is longer and more detailed than weaknesses, but score is 2

**Why it is harmful**: Authors and PC members are confused by the mismatch. It undermines trust in the review process.

**Self-check**: Re-read your review as if you were the author. Does the tone match the score? Would the score surprise someone who only read the text?

### 5.6 The Copy-Paste Reviewer

**Pattern**: Uses generic, template-like language that could apply to any paper. Shows no evidence of careful reading.

**Examples**:
- "The motivation could be stronger" (for every paper)
- "More baselines would improve the evaluation" (without specifying which)
- Summary that paraphrases the abstract rather than demonstrating understanding
- Strengths and weaknesses that could be swapped between any two papers in the session

**Why it is harmful**: Authors can tell when a reviewer has not engaged deeply with their work. Generic reviews provide no useful signal for the PC and no useful feedback for the authors.

**Self-check**: Could your review be applied to a different paper in the same session with minimal changes? If so, it is too generic.

### 5.7 Self-Check Metrics for Detecting Anti-Patterns

Use these numeric thresholds to audit your own review before submission:

| Anti-Pattern | Metric | Threshold | Action if Triggered |
|-------------|--------|-----------|-------------------|
| Wish-List Reviewer | Count of "should also" / "why not" suggestions that ask for work outside the paper's stated scope | ≥ 2 | Rewrite each as a limitation acknowledgment or remove if the paper's scope is reasonable. |
| Benchmark Bully | Count of baseline/workload requests without a stated reason ("because it would test X") | ≥ 1 | Add justification for every requested baseline, or remove the request. |
| Nitpick Reviewer | Fraction of weaknesses that are purely presentational (typos, formatting, color choices) | > 50% | Move presentational items to "Minor Issues." Reassess technical substance. |
| Silent Rejector | Total word count of the review (excluding minor issues) | < 300 words | Expand every negative claim with specific evidence and a constructive suggestion. |
| Positivity Mismatch | Difference between the tone-implied score and the actual score | > 1 point | Revise tone to match score, or reconsider whether your score is correct. |
| Copy-Paste Reviewer | Count of paper-specific references (section numbers, figure numbers, specific claims) in strengths + weaknesses | < 4 | Add specific references. Every strength and weakness should cite a concrete location in the paper. |

---

## 6. Self-Assessment Checklist

Complete this 8-item checklist before submitting your review. Every item should be "yes."

### Pre-Submission Checklist

| # | Check | Question |
|---|-------|----------|
| 1 | **Understanding** | Does my summary demonstrate that I understood the paper's main contribution? Could the authors confirm I got it right? |
| 2 | **Specificity** | Does every strength and weakness reference specific sections, figures, or claims? Are there zero vague statements? |
| 3 | **Constructiveness** | Would my review help the authors improve their paper, even if it is rejected? Does every criticism suggest a path forward? |
| 4 | **Score-text alignment** | Does the tone of my review match my score? Would someone reading only the text guess the correct score? |
| 5 | **Fairness** | Have I evaluated the paper for what it IS, not what I wish it were? Have I avoided wish-list criticism? |
| 6 | **Completeness** | Have I addressed novelty, soundness, significance, evaluation, and presentation? Is any dimension missing? |
| 7 | **Neutrality in summary** | Is my paper summary factual and neutral, or does it contain opinions that belong in strengths/weaknesses? |
| 8 | **Confidence honesty** | Does my stated confidence accurately reflect my expertise? Have I flagged areas where I may be wrong? |

---

## 7. Handling Edge Cases

### 7.1 Bad Writing, Good Ideas

**Situation**: The paper has a strong technical contribution but is poorly written.

**Approach**:
- Score based on the contribution, not the writing (unless the writing is so poor that you cannot evaluate the contribution)
- Clearly separate the writing critique from the technical assessment
- Suggest specific structural changes: "Moving Section 4.2 before Section 4.1 would improve the logical flow"
- Consider whether the writing issues are fixable in camera-ready (minor) or require a rewrite (major)
- If accepting: note that significant writing revision is needed for camera-ready
- Frame: "The technical contribution is strong, but the paper needs substantial editing to clearly communicate its ideas."

### 7.2 Well-Written but Incremental

**Situation**: The paper is a pleasure to read but the contribution is small.

**Approach**:
- Acknowledge the writing quality explicitly
- Be specific about why the contribution is incremental: cite the prior work that anticipates it
- Do not inflate the score because of good writing — writing cannot compensate for insufficient contribution
- Suggest how the contribution could be strengthened: "If the authors could show X, the contribution would be more compelling."
- Frame: "This is a well-crafted paper, but the contribution is incremental given [prior work]. The key insight was already demonstrated in [citation]."

**Distinguishing "incremental" from "evolutionary":**
Not all building-on-prior-work is incremental. A paper is genuinely incremental when:
1. The core technique already exists in the cited prior work
2. The new context does not introduce fundamentally new challenges
3. The performance delta is modest and expected

A paper is evolutionary (and potentially publishable) when:
1. Applying a known technique to a new context reveals surprising challenges or insights
2. The engineering required is substantial and teaches real lessons (Roscoe Q3)
3. The results are significantly better than what the community expected

**Scoring guidance:**
- Well-written + incremental → Score 2-3 (writing does not increase score)
- Well-written + evolutionary → Score 3-4 (the new insights or surprising challenges may justify acceptance)
- If you are unsure whether it is incremental or evolutionary, ask in "Questions for Authors": "What was the most surprising challenge in applying [technique X] to [new context Y]?"

### 7.3 Suspected Evaluation Dishonesty

**Situation**: Results seem too good to be true, or there are signs of selective reporting.

**Approach**:
- Do NOT accuse the authors of dishonesty — there may be innocent explanations
- State your concern factually: "The 10x improvement in Table 3 is surprising given that the theoretical maximum speedup for this approach is 5x (based on Amdahl's law with the reported parallelizable fraction). I would like the authors to explain this discrepancy."
- Request clarification in "Questions for Authors"
- Ask for raw data, scripts, or methodology details that would resolve the concern
- If the concern is about missing error bars: "The results in Figure 5 show consistent improvements across all configurations, which is unusual for this type of workload. Error bars and the number of trials would help assess the reliability of these results."
- Escalate to the PC chair only if you find clear evidence of fabrication (identical result patterns, impossibly precise numbers, results that violate physical constraints)

**Red flags that warrant closer inspection (not accusation):**

| Red Flag | Possible Innocent Explanation | What to Ask |
|----------|------------------------------|-------------|
| Results exceed theoretical bounds | Different model assumptions, or your bound calculation is wrong | "The theoretical limit appears to be X. Can you explain how the system achieves Y > X?" |
| Perfectly consistent results across all configurations | Highly deterministic system (e.g., CPU-bound with no I/O variance) | "The variance across configurations is surprisingly low. Were multiple trials run? What is the experimental variance?" |
| Baselines perform much worse than published results | Different hardware, workload, or configuration | "Baseline X reports [Y] in its paper but [Z] in your evaluation. Can you explain the discrepancy?" |
| Key negative results are absent | Authors genuinely did not test those conditions | "How does the system perform under [adversarial condition]? This is a common case in production." |
| Identical decimal patterns across tables | Copy-paste error or rounding artifact | "Tables [N] and [M] share identical values for [columns]. Can you verify these are from independent experiments?" |

**Escalation decision tree:**
1. **Concern is about missing data or methodology gaps** → Ask in "Questions for Authors." This is normal reviewing.
2. **Concern is about results that are surprising but not impossible** → State the concern factually and ask for clarification. Do not accuse.
3. **Concern is about results that appear to violate physical constraints or mathematical bounds** → State the specific constraint and ask for explanation. If the author response is unsatisfactory, flag to the PC chair privately.
4. **Concern is about clear evidence of fabrication** (e.g., pixel-identical plots, data that matches a known formula exactly) → Report to the PC chair immediately and privately. Do not include accusations in the written review.

### 7.4 Resubmissions

**Situation**: You have seen an earlier version of this paper (at this venue or another).

**Approach**:
- Evaluate the paper on its current merits — do not penalize for being a resubmission
- If you reviewed the earlier version, note what has changed and whether previous concerns are addressed
- If changes were made, acknowledge the effort: "The authors have addressed [specific concern] from the prior submission by [specific change]."
- Do not assume the same weaknesses apply if the paper has changed significantly
- If little has changed since a prior rejection: "This appears to be a resubmission with minor changes. The core concerns from prior reviews ([specific issues]) remain unaddressed."

### 7.5 Conflict of Interest

**Situation**: You realize during reviewing that you have a conflict (collaborator, advisor, competitor).

**Approach**:
- Disclose the conflict to the PC chair immediately
- Do NOT continue reviewing if you have a direct conflict (advisor, collaborator, co-author within the last 2-3 years)
- For indirect conflicts (competitor, same institution but no collaboration): disclose and let the PC chair decide
- When in doubt, disclose. The PC chair would rather reassign a review than discover an undisclosed conflict later.

### 7.6 Papers Outside Your Expertise

**Situation**: The paper is in an area where you have limited knowledge.

**Approach**:
- Set reviewer confidence appropriately (1 or 2)
- Focus your review on aspects you CAN evaluate: methodology, presentation, evaluation rigor
- Be honest about what you cannot assess: "I am not an expert in [area] and cannot fully evaluate the novelty claim. I defer to more expert reviewers on this dimension."
- Still provide a thoughtful review — your outside perspective may catch issues that domain experts overlook
- Do NOT pretend to expertise you lack — it is immediately visible to the PC and harmful to the process

### 7.7 Papers You Love (or Hate)

**Situation**: You have a strong emotional reaction to the paper.

**Approach**:
- Recognize the bias and compensate
- For papers you love: actively look for weaknesses. Ask: "What would a skeptical reviewer say?"
- For papers you hate: actively look for strengths. Ask: "What is the best version of this paper's argument?"
- Write the review, then re-read it the next day before submitting
- Check score-text alignment especially carefully when you have a strong reaction
- Ask yourself: "Am I evaluating the paper, or am I reacting to the topic/approach/authors?"