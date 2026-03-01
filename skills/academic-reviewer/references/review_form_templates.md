# Review Form Templates

This reference provides the HotCRP review form field guide, complete example reviews at different score levels, and one-shot revision (OSR) templates for systems conference papers.

---

## 1. HotCRP Review Form Field Guide

HotCRP is the standard review platform for OSDI, NSDI, SIGCOMM, MOBICOM, and SOSP. Reviews follow a structured form with these fields.

### 1.1 Overall Merit (Required)

Score on a 1-5 scale. This is the primary signal for accept/reject decisions.

| Score | Label | Guidance |
|-------|-------|----------|
| 5 | Strong Accept | Top 5-10% of submissions. You will champion this paper. Significant, novel, sound, well-evaluated. |
| 4 | Accept | Above the bar. Solid contribution with only minor issues. You support acceptance. |
| 3 | Borderline | Real merit but notable weaknesses. Could go either way. You need discussion to decide. |
| 2 | Weak Reject | Some merit but significant problems. Below the bar. Needs major revision. |
| 1 | Strong Reject | Fundamental problems. Not suitable even with revision. |

**Calibration reminder**: At ~15-20% acceptance, a score of 3 means "uncertain" — not "acceptable." Most accepted papers need at least one score of 4 or 5.

### 1.2 Reviewer Confidence (Required)

| Score | Label | Guidance |
|-------|-------|----------|
| 4 | Expert | Published in this specific area. Know the state of the art deeply. |
| 3 | Knowledgeable | Read extensively in this area. Familiar with key prior work. |
| 2 | Some familiarity | General systems knowledge. May miss domain-specific nuances. |
| 1 | Limited knowledge | Outside your area. Focus review on general methodology and presentation. |

**Honesty principle**: State your actual expertise. Low confidence + insightful comments is valued. High confidence + superficial review damages credibility.

### 1.3 Paper Summary (Required)

**Purpose**: Demonstrate that you understood the paper. This is NOT a copy of the abstract.

**Structure** (3-5 sentences):
1. What problem does the paper address and why does it matter?
2. What is the key insight or approach?
3. What system was built and how was it evaluated?
4. What are the main results?

**Guidelines**:
- Write in your own words — do not copy from the abstract
- Be factual and neutral — save opinions for strengths/weaknesses
- Include enough detail that the authors can verify you understood their work
- Mention the specific system name if one is given
- State the claimed contributions accurately

**Example**:
> This paper presents Hydra, a distributed training system that addresses the communication bottleneck in large-scale model parallelism. The key insight is that pipeline bubble time can be repurposed for gradient compression without adding latency to the critical path. Hydra implements an adaptive compression scheme that selects compression ratios based on real-time pipeline utilization. Evaluated on 256 GPUs with GPT-3 scale models, the system achieves 1.4x throughput improvement over Megatron-LM while maintaining model accuracy within 0.1% of uncompressed training.

### 1.4 Strengths (Required)

**Purpose**: Identify what the paper does well. Be specific and substantive.

**Structure**: Bulleted list, 3-6 items, ordered from most to least important.

**Guidelines**:
- Each strength should be a specific, concrete observation — not generic praise
- Reference specific sections, figures, or experiments
- Explain WHY each item is a strength, not just WHAT it is
- Even for papers you recommend rejecting, identify genuine strengths

**Good strength examples**:
- "S1: The key insight that pipeline bubbles can be repurposed for compression (Section 3.2) is novel and well-motivated by the profiling study in Figure 2."
- "S2: The evaluation is thorough — the paper includes 5 baselines, 3 model sizes, ablation of each component, and measurement of convergence impact (Sections 6.1-6.4)."
- "S3: The adaptive compression scheme (Section 4) elegantly handles the trade-off between communication reduction and gradient quality, with a clean formulation."

**Bad strength examples** (too vague):
- "The paper is well-written" — specify what makes it well-written
- "Interesting problem" — explain why the problem is interesting
- "Good evaluation" — say what makes the evaluation good

### 1.5 Weaknesses (Required)

**Purpose**: Identify problems that affect your assessment. Be specific, constructive, and prioritized.

**Structure**: Bulleted list, 3-6 items, ordered from most to least severe. Label severity.

**Guidelines**:
- Each weakness should identify a specific problem AND explain its impact
- Distinguish between fatal flaws and fixable issues
- Suggest how the weakness could be addressed where possible
- Use the weakness taxonomy from `references/common_paper_weaknesses.md` for classification
- Be constructive: "The evaluation would be stronger with X" rather than "The evaluation is bad"

**Good weakness examples**:
- "W1 [Major]: The comparison with Megatron-LM (Section 6.1) uses an outdated version (v2.0 from 2021). The current version (v3.0) includes tensor-parallel optimizations that may significantly close the performance gap. This undermines the main performance claim."
- "W2 [Major]: The paper claims the compression scheme 'maintains accuracy' but only evaluates on GPT-3 at one scale (6.7B). Larger models may be more sensitive to gradient compression, and the convergence guarantee (Theorem 1) relies on an assumption (bounded gradient variance) that may not hold."
- "W3 [Minor]: Figure 5 uses log-scale y-axis which makes the 1.4x improvement visually appear larger. A linear-scale version should be included for fair comparison."

**Bad weakness examples** (unconstructive):
- "The paper is incremental" — explain what is incremental and what prior work anticipated it
- "Evaluation is weak" — specify exactly what is missing
- "Not convinced by the approach" — state your specific technical concern

### 1.6 Detailed Comments for Authors (Required)

**Purpose**: Provide detailed technical feedback that helps the authors improve their work, regardless of the accept/reject decision.

**Structure**: Free-form, typically 1-3 paragraphs or a structured list. May include:
- Elaboration on strengths and weaknesses
- Specific technical questions
- Suggestions for improvement
- References to related work the authors may have missed
- Clarifications you need from the authors

**Guidelines**:
- This section should help the authors even if the paper is rejected
- Point to specific sections, theorems, figures, or equations
- If you found a technical error, explain it precisely
- Suggest concrete experiments or analyses that would strengthen the paper
- If you know of directly relevant work the paper misses, cite it

### 1.7 Questions for Authors (Recommended)

**Purpose**: Questions you want answered during the author response period. These should be genuine questions that could change your assessment.

**Guidelines**:
- Ask questions whose answers could move your score up or down
- Be specific: "What is the throughput on a 128-GPU cluster?" not "Can you run more experiments?"
- Number your questions for easy reference in the author response
- Limit to 3-5 questions — focus on what matters most
- Flag which questions are most important to your assessment

**Example**:
> Q1 (critical): Has the system been tested with Megatron-LM v3.0? The tensor-parallel improvements in v3.0 may substantially affect the comparison.
>
> Q2: What is the convergence behavior beyond 100K steps? Figure 7 shows convergence up to 100K steps, but the full training run is 300K steps.
>
> Q3: The paper mentions "negligible overhead" for the compression metadata. Can you quantify this? At what scale does it become non-negligible?

### 1.8 Field Length Expectations

| Field | Expected Length | Too Short | Too Long |
|-------|---------------|-----------|----------|
| Paper Summary | 80-150 words (3-5 sentences) | < 50 words: probably just rephrasing the abstract, does not demonstrate understanding | > 200 words: probably including opinions that belong in strengths/weaknesses |
| Strengths | 100-250 words (3-6 bullet points) | < 60 words: too vague, likely missing specific references | > 350 words: may be inflating minor positives; focus on the most impactful strengths |
| Weaknesses | 150-350 words (3-6 bullet points) | < 80 words: likely the Silent Rejector anti-pattern; add specifics and suggestions | > 500 words: may be mixing major and minor issues; move minor items to "Minor Issues" |
| Detailed Comments | 150-400 words (1-3 paragraphs) | < 100 words: not enough to help the authors improve | > 600 words: consider whether all content is necessary; be concise |
| Questions for Authors | 50-150 words (2-5 questions) | < 30 words: not enough to drive meaningful author response | > 200 words: too many questions dilutes focus; prioritize the 3-5 most important |
| Minor Issues | 0-100 words (0-10 items) | 0 words: acceptable, not every paper has minor issues | > 150 words: you may be nitpicking; check if any items belong in "Weaknesses" instead |

**Total review length guidance**: A well-calibrated review for a top systems venue is typically **500-1000 words** (excluding minor issues). Reviews shorter than 400 words are almost certainly too superficial. Reviews longer than 1200 words may need tightening.

### 1.9 Minor Issues (Optional)

**Purpose**: Typos, formatting issues, unclear sentences, and other small items that do not affect the overall assessment.

**Guidelines**:
- Use a brief list format: "Page X, Line Y: issue"
- Do not let minor issues dominate the review
- These should never affect the overall merit score
- Include only if you have specific items — an empty section is fine

**Example**:
> - Page 3, paragraph 2: "their" should be "there"
> - Figure 4 caption: units should be "ms" not "s" (based on the text description)
> - Section 5.1: "c.f." should be "cf." (no periods in modern usage)
> - Table 2: the "Ours" row is not bolded like other tables in the paper

---

## 2. Complete Example Reviews

### 2.1 Score 5: Strong Accept

**Paper**: "StreamDB: A Log-Structured Storage Engine for Real-Time Stream Processing" (hypothetical, for illustration)

**Overall Merit**: 5 (Strong Accept)
**Reviewer Confidence**: 4 (Expert)

**Paper Summary**:
StreamDB addresses the mismatch between stream processing engines and their underlying storage layers. Current systems (Flink, Kafka Streams) use general-purpose storage engines (RocksDB) that are optimized for random access rather than the sequential, append-heavy workloads typical of stream processing state. The key insight is that stream processing state access patterns are highly predictable — they follow the watermark progression — and this predictability can be exploited to design a storage engine that pre-stages data along the time axis. StreamDB implements a watermark-aware log-structured merge tree that partitions state by time windows and uses watermark-based prefetching. Evaluated on 4 stream processing benchmarks across 3 engines (Flink, Kafka Streams, Spark Structured Streaming), StreamDB achieves 2.1-3.8x throughput improvement and 5-12x reduction in tail latency compared to RocksDB, while using 40% less memory through timely garbage collection of expired windows.

**Strengths**:
- S1: The core insight — exploiting watermark-driven predictability for storage optimization — is novel and elegant. Despite extensive work on both stream processing and LSM-trees, I am not aware of prior work that connects these two areas in this way. The observation that >92% of state accesses follow the watermark (Figure 3) is compelling and well-supported by the trace study.
- S2: The evaluation is exemplary. Four industry-standard benchmarks (NEXMark, Yahoo Streaming, Linear Road, and a production Uber workload), three engines, comparison against both RocksDB and a state-of-the-art streaming-optimized store (Anna), ablation of each component (Section 7.4), and memory analysis. This is one of the most thorough evaluations I have seen in a stream processing paper.
- S3: The design is clean and well-motivated. Each component (watermark-aware partitioning, prefetch scheduling, window-based GC) addresses a specific bottleneck identified in the profiling study. The trade-off analysis in Section 4.5 is particularly good — the authors honestly discuss when their approach degrades (out-of-order arrivals >15% of window size).
- S4: Strong artifact: open-source implementation (18K LOC in Rust), integration with three production engines, and reproducible benchmark scripts. The artifact appendix is thorough.
- S5: The paper is exceptionally well-written. Complex storage internals are explained clearly, figures are effective, and the paper maintains a logical flow from motivation through design to evaluation.

**Weaknesses**:
- W1 [Minor]: The paper focuses on window-based operations and does not address how StreamDB handles non-windowed state (e.g., global aggregations, session windows with long timeouts). Section 8 mentions this as future work, but a brief discussion of the limitations would strengthen the paper.
- W2 [Minor]: The production workload from Uber (Section 7.3) is described at a high level but the trace is not publicly available. While the other three benchmarks are standard and reproducible, the Uber workload provides some of the strongest results. It would be valuable to describe its characteristics in enough detail that a synthetic workload could approximate it.
- W3 [Minor]: The comparison with Anna (Section 7.1) uses the default configuration. The authors of Anna may argue that Anna can be tuned for streaming workloads. A brief sensitivity study on Anna's configuration would preempt this objection.

**Detailed Comments**:
This is an excellent paper that I would strongly champion at the PC meeting. The insight that stream processing state access is fundamentally different from general-purpose key-value access — and that this difference can be exploited at the storage layer — is both obvious in hindsight and surprisingly unexplored. The execution matches the insight: the system is real, the evaluation is thorough, and the writing is clear.

The watermark-aware prefetching mechanism (Section 4.3) is particularly clever. By treating the watermark as a "cursor" through the time-partitioned state, StreamDB effectively turns random access into sequential access for the common case. The fallback path for out-of-order accesses (Section 4.4) is well-designed and the analysis of when it degrades is honest.

I have one suggestion for the camera-ready: consider adding a brief discussion of how StreamDB interacts with checkpointing. Stream processing engines checkpoint state periodically for fault tolerance, and the interaction between checkpointing and the time-partitioned storage structure could be interesting (does it simplify checkpointing? does it complicate recovery?).

**Questions for Authors**:
Q1: How does StreamDB handle session windows with very long timeouts (e.g., hours or days)? The watermark-aware partitioning assumes windows are relatively short-lived.
Q2: What is the CPU overhead of the watermark-based prefetch scheduler? The paper reports throughput and latency but not CPU utilization.

**Minor Issues**:
- Page 5, Figure 4: The arrow from "Prefetch Scheduler" to "Block Cache" is hard to see — consider using a thicker line or different color.
- Page 9, Table 3: Consider adding a "Memory" column to complement the throughput and latency results.

---

### 2.2 Score 3: Borderline

**Paper**: "AdaptNet: Adaptive Network Function Placement in Edge Computing" (hypothetical)

**Overall Merit**: 3 (Borderline)
**Reviewer Confidence**: 3 (Knowledgeable)

**Paper Summary**:
AdaptNet proposes an adaptive placement system for network functions (NFs) across edge and cloud nodes. The system monitors network conditions (latency, bandwidth, load) and migrates NFs between edge and cloud to optimize end-to-end latency while respecting resource constraints. The key idea is a prediction model that anticipates load changes and proactively migrates NFs before performance degrades. AdaptNet is implemented as a controller that integrates with Kubernetes and Open vSwitch. The evaluation uses a 12-node testbed with 3 edge sites and shows 25-40% latency reduction compared to static placement and 15-20% improvement over a reactive migration baseline.

**Strengths**:
- S1: The problem is practical and timely. Edge-cloud NF placement is a real operational challenge, and the paper provides concrete evidence of the problem through production traces from a CDN operator (Section 2).
- S2: The system is implemented and integrated with production infrastructure (Kubernetes, OVS), making the deployment barrier low. The implementation section (Section 5) is detailed and honest about engineering challenges.
- S3: The evaluation includes a comparison with both static placement and a reactive migration system (NFP [32]), providing appropriate baselines. The use of real CDN traffic traces for workload generation adds credibility.

**Weaknesses**:
- W1 [Major]: The prediction model (Section 4.2) is an LSTM trained on historical load data, which is a standard approach in the ML-for-systems literature. The paper does not adequately differentiate this from prior prediction-based placement work (e.g., [18], [23], [27]). What is specifically new about using prediction for NF placement vs. VM placement or container placement? The paper needs to articulate a clearer technical novelty.
- W2 [Major]: The evaluation scale is limited. A 12-node testbed with 3 edge sites is small for the target deployment (CDN-scale edge computing). The paper does not include any simulation or analysis to suggest how the approach would scale to hundreds of edge sites. The migration overhead analysis (Section 6.4) only measures single-NF migration, not the cascading effects of multiple simultaneous migrations.
- W3 [Major]: The latency improvements (25-40% over static, 15-20% over reactive) are modest and the confidence intervals in Table 2 overlap for several workloads. The paper should include statistical significance tests or at minimum discuss the overlap.
- W4 [Minor]: The prediction accuracy analysis (Section 6.5) shows 87% accuracy at 5-minute horizons but drops to 62% at 30-minute horizons. The paper does not discuss how prediction errors affect placement decisions — what happens when the model is wrong? A robustness analysis would strengthen the paper.

**Detailed Comments**:
This paper addresses a real problem and presents a working system, which I appreciate. However, I am uncertain whether the contribution meets the bar for this venue. My main concern is novelty: prediction-based resource placement is well-studied, and the paper needs to more clearly articulate what is new about applying it to NF placement specifically. Is there something about NF placement that makes the problem fundamentally different from VM/container placement? If so, this needs to be front and center in the paper.

The evaluation is solid in methodology but limited in scale. I understand the difficulty of large-scale edge testbeds, but the paper should at minimum include a simulation study showing how the controller behaves at 100+ edge sites. The current 12-node evaluation leaves open questions about scalability of the controller itself (not just the NFs).

I would also like to see a more honest discussion of failure modes. What happens when the prediction model gives a wrong forecast and triggers an unnecessary migration? What is the cost of a bad migration vs. the cost of not migrating?

If the authors can convincingly address the novelty concern and provide scale evidence in a revision, this could be a strong paper. As it stands, I lean slightly negative but could be convinced by the author response.

**Questions for Authors**:
Q1 (critical): What is technically new about prediction-based NF placement compared to prediction-based VM/container placement? Can you point to a specific challenge unique to NFs that your system addresses?
Q2 (critical): Have you evaluated or simulated the system at larger scale (50+ edge sites)? What is the controller's decision latency as the number of sites grows?
Q3: What is the migration cost when the prediction is wrong? How often does this happen in your evaluation?

**Minor Issues**:
- Section 3.1: The system model assumes all edge sites have homogeneous hardware. Is this realistic?
- Figure 6: Y-axis label is cut off in my PDF rendering.
- The related work section (Section 8) should discuss EdgeAI [Liu et al., NSDI 2023] which addresses a similar placement problem for ML inference.

---

### 2.3 Score 2: Weak Reject

**Paper**: "FastCache: Accelerating Web Applications with Predictive Caching" (hypothetical)

**Overall Merit**: 2 (Weak Reject)
**Reviewer Confidence**: 3 (Knowledgeable)

**Paper Summary**:
FastCache proposes a predictive caching system for web applications that uses user behavior patterns to prefetch content into a CDN cache before it is requested. The system trains a Markov model on user clickstream data to predict the next page a user will visit, then proactively caches that page's resources at the nearest edge node. FastCache is implemented as a middleware layer between the application server and CDN. The evaluation uses traces from two web applications (an e-commerce site and a news site) and reports 30-45% reduction in page load time for predicted pages.

**Strengths**:
- S1: The paper clearly identifies a practical problem — CDN cache miss latency for dynamic content — and the motivation section (Section 2) provides concrete measurements showing the impact on user experience.
- S2: The system is implemented and tested with real web application traces, not just synthetic benchmarks. The e-commerce trace (Section 6.1) represents realistic usage.
- S3: The writing quality is good. The paper is well-organized and the system design (Section 4) is clearly presented with helpful diagrams.

**Weaknesses**:
- W1 [Fatal]: The core technique — Markov-based prediction for web prefetching — is well-studied dating back to the early 2000s (Padmanabhan & Mogul, 1996; Fan et al., 1999; Davison, 2002). The paper does not cite this foundational work or explain how FastCache differs from these approaches. The related work section (Section 7) only discusses CDN caching and misses the extensive web prefetching literature. This is a serious omission that undermines the claimed novelty.
- W2 [Major]: The evaluation only reports improvements for predicted pages (where the prediction was correct). The paper does not report the prediction accuracy or the cost of mispredictions (wasted bandwidth and cache space for prefetched content that is never accessed). Without this analysis, the 30-45% improvement is misleading — it could come at the cost of significant bandwidth waste.
- W3 [Major]: The baselines are inadequate. The paper compares against (1) no caching and (2) LRU caching. It does not compare against any existing prefetching system or even a simple popularity-based prediction baseline. The improvement over LRU caching (the more relevant baseline) is only 12-18%, which is modest.
- W4 [Major]: The evaluation uses only two web applications, both content-heavy sites where prefetching is naturally effective. The paper does not evaluate on applications where prediction is harder (e.g., search-driven sites, single-page applications with API calls) or discuss the types of applications where FastCache would not help.
- W5 [Minor]: The privacy implications of tracking user clickstreams for prediction are not discussed. Modern web applications face strict privacy requirements (GDPR, CCPA), and a system that builds per-user behavior models needs to address this.

**Detailed Comments**:
The paper addresses a real performance problem and the implementation is functional, but I believe it falls below the acceptance bar for two reasons.

First, the novelty concern is significant. Predictive web prefetching has been studied extensively for over two decades. The specific approach in this paper (Markov models on clickstreams) was explored in multiple papers in the early 2000s. To be a contribution in 2026, the paper would need to identify what has changed (scale? content types? privacy constraints?) that makes this problem worth revisiting, and demonstrate that the new system meaningfully advances beyond prior approaches. Currently, the paper reads as if this problem area is new, which it is not.

Second, the evaluation has important gaps. Reporting only the improvement for correctly-predicted pages is a form of cherry-picking. A fair evaluation must include: (a) overall prediction accuracy, (b) bandwidth overhead of mispredictions, (c) impact on cache utilization (does prefetching evict useful cached content?), and (d) end-to-end improvement across ALL page loads, not just predicted ones.

I appreciate the clean system design and good writing. If the authors address the novelty positioning (acknowledge and build on prior prefetching work) and fix the evaluation gaps (report overall accuracy, misprediction costs, and compare against a prefetching baseline), this could become a solid paper. However, these are not minor revisions — they require rethinking the paper's contribution and rerunning the evaluation.

**Questions for Authors**:
Q1 (critical): How does FastCache differ from prior Markov-based web prefetching systems (e.g., Padmanabhan & Mogul, 1996; Davison, 2002)? What has changed in the 25 years since that work that motivates this approach?
Q2 (critical): What is the prediction accuracy across all user sessions? What fraction of prefetched content is never accessed?
Q3: How does FastCache interact with CDN cache eviction? Does prefetched content displace content that would have been a cache hit?

**Minor Issues**:
- Abstract claims "up to 45% improvement" — this is the best case for predicted pages only and should be qualified.
- Section 4.3: The Markov model order (k=3) is chosen without justification. A sensitivity study would help.
- Table 1: Missing units for "Cache Size" column.

---

### 2.4 Score 3, Confidence 1: Limited Knowledge Perspective

**Paper**: "AdaptNet: Adaptive Network Function Placement in Edge Computing" (same paper as §2.2, reviewed at confidence 1 instead of confidence 3)

**Overall Merit**: 3 (Borderline)
**Reviewer Confidence**: 1 (Limited knowledge)

**Paper Summary**:
AdaptNet proposes a system for deciding where to place network functions — either at edge nodes close to users or in the cloud — and for moving them between locations as conditions change. The system uses a prediction model to anticipate when performance will degrade and proactively migrates network functions before problems occur. It is implemented on top of Kubernetes and tested on a 12-node setup with 3 edge sites. The evaluation reports latency reductions of 25-40% over static placement.

**Strengths**:
- S1: The problem is clearly motivated. Section 2 provides concrete evidence from a CDN operator showing that static placement leads to poor performance during load shifts. A reader without edge computing expertise can understand why adaptive placement matters.
- S2: The paper is well-organized and follows standard systems paper structure. The system architecture (Figure 2) is clear and the design section (Section 4) explains the main components and their interactions effectively.
- S3: The evaluation uses real CDN traffic traces for workload generation (Section 6.1), which is stronger methodology than relying solely on synthetic benchmarks.

**Weaknesses**:
- W1 [Major]: I have limited expertise in edge computing and network function placement. I cannot assess whether the prediction-based approach is novel relative to prior work in this area. The related work section (Section 8) discusses several prior systems, but as a non-expert, I cannot judge whether AdaptNet's contribution over these systems is significant. I defer to more expert reviewers on the novelty question.
- W2 [Major]: The confidence intervals in Table 2 overlap for several workloads, which raises concerns about statistical significance regardless of domain. The paper does not report the number of trials, discuss whether the differences are statistically significant, or explain why the improvements vary so much across workloads (25-40% is a wide range).
- W3 [Minor]: The prediction accuracy drops from 87% at 5-minute horizons to 62% at 30-minute horizons (Section 6.5), but the paper does not discuss the consequences of prediction errors. When the model predicts incorrectly and triggers an unnecessary migration, what is the cost? This seems like an important question that does not require domain expertise to ask.
- W4 [Minor]: Some terminology is introduced without sufficient explanation for a general systems audience. For example, "network function chaining" (Section 3.2) and "NF state migration" (Section 4.4) would benefit from brief definitions when first used.

**Detailed Comments**:
I have limited expertise in edge computing and network function placement. My review focuses on presentation, general methodology, and experimental rigor.

The paper communicates the problem effectively — even as a non-expert, I understand why adaptive placement matters and how the system works at a high level. The system architecture is clear and the integration with Kubernetes is a practical contribution.

My main methodological concern is the statistical treatment of results. The overlapping confidence intervals in Table 2 need to be addressed: either report significance tests, run additional trials, or discuss why certain workloads show smaller improvements. The prediction accuracy degradation at longer horizons (Section 6.5) also deserves more analysis — specifically, how often do prediction errors lead to bad placement decisions, and what is the recovery cost?

I assign a score of 3 reflecting genuine uncertainty. The paper appears to address a real problem with a reasonable approach, but I cannot assess the two most important aspects — novelty and whether the baselines are appropriate. I would weight expert reviewers' assessments more heavily for the final decision.

**Questions for Authors**:
Q1: How many trials were run for each experiment? Are the differences in Table 2 statistically significant?
Q2: What is the cost (in latency and resource usage) of an unnecessary migration triggered by a wrong prediction?
Q3: Could you add brief definitions of "network function chaining" and "NF state migration" for readers outside the edge computing community?

---

## 3. One-Shot Revision (OSR) Reviews

### 3.1 When OSR Applies

Some venues (NSDI, SIGCOMM, MOBICOM) offer a one-shot revision (OSR) process for borderline papers. OSR means the paper is not accepted outright but is given a specific set of required changes. If the authors successfully address these changes within a short revision period (typically 4-6 weeks), the paper is accepted.

**OSR is appropriate when:**
- The core contribution is sound and significant
- The weaknesses are fixable within the revision period
- The required changes are concrete and verifiable
- The PC can agree on a clear list of required changes
- The paper would likely be accepted if the changes are made

**OSR is NOT appropriate when:**
- The fundamental approach is flawed
- The novelty is questionable (novelty cannot be added in revision)
- The changes require new system design or major re-implementation
- The required experiments would take more than 4-6 weeks
- The weaknesses are subjective or hard to verify

### 3.2 OSR Review Template

When recommending OSR, include an explicit section in your review:

**OSR Recommendation Structure:**

```
## One-Shot Revision Recommendation

I recommend this paper for one-shot revision. The core contribution [brief statement]
is sound and significant, but the following issues must be addressed:

### Required Changes (must ALL be addressed for acceptance):

R1: [Specific, concrete, verifiable requirement]
    Rationale: [Why this is necessary]
    Verification: [How the PC will check this was done]

R2: [Specific, concrete, verifiable requirement]
    Rationale: [Why this is necessary]
    Verification: [How the PC will check this was done]

R3: ...

### Recommended Changes (encouraged but not required):

- [Suggestion 1]
- [Suggestion 2]

### Scope Boundary:
The revision should NOT require [state what would be out of scope — e.g.,
"redesigning the core algorithm" or "building a new prototype"].
```

**Example OSR section:**

> ## One-Shot Revision Recommendation
>
> I recommend this paper for one-shot revision. The adaptive NF placement approach is practical and the system integration with Kubernetes is valuable, but two gaps need to be closed.
>
> ### Required Changes:
>
> R1: Add a simulation study evaluating the controller at 50+ edge sites, measuring controller decision latency and placement quality as the number of sites scales.
>     Rationale: The current 12-node evaluation does not demonstrate scalability.
>     Verification: New section or subsection with simulation methodology and results.
>
> R2: Include a robustness analysis showing the effect of prediction errors on placement quality. Specifically, inject prediction errors at rates of 10%, 20%, 30% and measure the impact on end-to-end latency.
>     Rationale: The prediction model accuracy degrades at longer horizons and the cost of misprediction is unquantified.
>     Verification: New experiment with results table showing latency impact vs. error rate.
>
> R3: Add statistical significance tests (or confidence intervals that do not overlap) for the main comparison results in Table 2.
>     Rationale: Current confidence intervals overlap for some workloads.
>     Verification: Updated Table 2 with significance indicators.
>
> ### Recommended Changes:
> - Discuss the similarity to and differences from prediction-based VM placement more explicitly in Section 7.
> - Add a brief analysis of migration overhead when multiple NFs are migrated simultaneously.
>
> ### Scope Boundary:
> The revision should NOT require redesigning the prediction model or re-implementing the system. The focus is on additional evaluation and analysis.

### 3.3 OSR Guidelines by Venue

| Venue | OSR Available | Typical Revision Period | Max Required Changes |
|-------|--------------|------------------------|---------------------|
| NSDI | Yes (shepherd-based) | 6 weeks | 3-5 concrete items |
| SIGCOMM | Yes (revision process) | 4-6 weeks | 3-4 concrete items |
| MOBICOM | Yes (major/minor revision) | 4-8 weeks | Varies by major/minor |
| OSDI | No formal OSR | N/A (shepherd for accepted papers) | N/A |
| SOSP | No formal OSR | N/A (shepherd for accepted papers) | N/A |

**Key principle**: OSR requirements must be concrete, achievable, and verifiable. "Improve the writing" is not an OSR requirement. "Add an experiment comparing against Baseline X on Workload Y" is.

---

## 4. Evaluating Author Responses

### 4.1 When to Change Your Score

After reading the author response, you should update your review and potentially adjust your score. Here is guidance on when and how much to change.

**Raise your score when:**
- The authors provide new data or analysis that directly addresses your concern (e.g., missing baselines, missing error bars)
- The authors convincingly explain a misunderstanding in your review (you misread the paper or made an incorrect assumption)
- The authors commit to specific, verifiable changes in the camera-ready that would resolve your concern

**Keep your score when:**
- The authors acknowledge the issue but do not provide evidence or a concrete fix
- The authors dispute your concern without convincing technical argument
- The authors promise future work but do not address the current paper's gaps
- The response is generic ("we will improve the evaluation") rather than specific

**Lower your score when (rare):**
- The author response reveals additional problems you did not notice during review
- The authors' explanation contradicts claims made in the paper, exposing inconsistency
- The response demonstrates a fundamental misunderstanding of their own system's limitations

### 4.2 Author Response Evaluation Checklist

For each question you asked, evaluate the response:

| Your Question | Response Quality | Score Impact |
|--------------|-----------------|--------------|
| Answered with new data that resolves the concern | Strong response | Consider raising by 0.5-1 |
| Answered with a reasonable explanation but no new data | Adequate response | Score unchanged; note the explanation |
| Answered with a promise to add in camera-ready | Weak response | Score unchanged; note what is promised |
| Not answered or deflected | No response | Score unchanged or lowered; note the omission |
| Answer reveals a new problem | Negative response | Consider lowering by 0.5-1 |

### 4.3 Post-Response Review Update

After reading author responses, update your review with a clearly marked addendum:

```
## Post-Author-Response Update

After reading the author response, I [maintain / raise / lower] my score
from [X] to [Y].

The authors [addressed / partially addressed / did not address] my concerns:
- Concern 1: [status and brief explanation]
- Concern 2: [status and brief explanation]

[If score changed]: I changed my score because [specific reason].
```

**Important**: Never change your score based solely on other reviewers' opinions during PC discussion. Change your score only if the *arguments* convince you, not the people making them.