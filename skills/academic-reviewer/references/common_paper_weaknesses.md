# Common Paper Weaknesses in Systems Conference Submissions

This reference catalogs recurring weaknesses found in systems conference paper submissions, organized by paper section. Each weakness includes an identifier, description, severity classification, and constructive phrasing templates for reviewer feedback.

---

## 1. Severity Classification

Every weakness should be classified by its impact on the paper's overall assessment.

| Severity | Definition | Impact on Score |
|----------|-----------|-----------------|
| **Fatal** | Undermines the core contribution. Cannot be fixed without fundamentally rethinking the paper. | Typically leads to score 1-2. A single fatal weakness usually warrants rejection. |
| **Major** | Significant gap in the paper that weakens the contribution substantially. Could potentially be addressed in a major revision. | Each major weakness reduces score by ~1 point. Two or more major weaknesses typically lead to rejection. |
| **Minor** | Noticeable issue that does not undermine the core contribution. Can be addressed in a revision without changing the paper's message. | Accumulated minor weaknesses may reduce score by 0.5-1 point. Alone, they do not warrant rejection. |

**Guidance on severity assignment:**
- A weakness is **fatal** if fixing it would require a different system, a different evaluation, or a different paper
- A weakness is **major** if fixing it would require significant new work but the core idea could survive
- A weakness is **minor** if fixing it requires editing, additional explanation, or small supplementary experiments

---

## 2. Motivation Weaknesses (W-M)

### W-M1: Problem Does Not Matter

**Description**: The paper solves a problem that few practitioners or researchers care about. The problem may be artificial, contrived, or too narrow to justify a full paper.

**Severity**: Fatal

**How to detect:**
- Ask yourself: "If this system worked perfectly, who would use it and why?"
- Check if the paper provides evidence of real-world demand (industry trends, production data, user studies)
- Check if the problem is well-known in the community or only relevant to a very specific setting

**Constructive phrasing:**
- "The paper would benefit from stronger motivation. It is unclear how frequently the described problem arises in practice. Can the authors provide data on how often real systems encounter [specific scenario]?"
- "While the technical approach is interesting, I am not convinced that [problem X] is a significant enough pain point to warrant a new system. The paper would be strengthened by evidence from production workloads or user surveys."

### W-M2: No Empirical Evidence for the Problem

**Description**: The paper claims a problem exists but provides no measurements, profiling data, or concrete examples to demonstrate it. The motivation relies on assertion rather than evidence.

**Severity**: Major

**How to detect:**
- The Background/Motivation section contains claims like "X is a bottleneck" without profiling data
- No measurements showing the gap between current and desired performance
- No workload analysis demonstrating the problem at scale

**Constructive phrasing:**
- "The claim that [X is a bottleneck] would be more convincing with profiling data from a representative workload. Consider adding a measurement study in Section 2 that quantifies the problem."
- "Section 2 asserts that [problem] is significant, but does not quantify its impact. How much performance/cost/resource is lost due to this problem in a typical deployment?"

### W-M3: Strawman Comparison

**Description**: The paper motivates the problem by comparing against a naive or outdated approach, making the problem appear worse than it is. State-of-the-art solutions are ignored or dismissed without evaluation.

**Severity**: Major

**How to detect:**
- The motivating example uses a simplistic baseline that no practitioner would actually use
- Recent related work that partially addresses the problem is mentioned only in passing or in Related Work
- The gap being addressed may already be significantly narrowed by existing optimizations

**Constructive phrasing:**
- "The motivating comparison in Section 2 uses [naive approach], but practitioners would typically use [better approach]. How does the problem severity change with a more realistic baseline?"
- "The paper mentions [recent system X] in related work but does not include it in the motivating analysis. Since X partially addresses the same problem, it is important to quantify the remaining gap."

### W-M4: Problem Already Solved

**Description**: The problem the paper addresses has already been solved (or substantially addressed) by existing work. The paper does not adequately distinguish its contribution from prior solutions.

**Severity**: Fatal

**How to detect:**
- A published system addresses the same problem with comparable or better results
- The paper's Related Work section does not compare against the most relevant prior work
- The delta between the proposed system and the best existing approach is marginal

**Constructive phrasing:**
- "[System Y] appears to address the same problem with a similar approach. The paper should clearly articulate what [this system] achieves that [Y] does not. A direct experimental comparison would strengthen the paper significantly."
- "Given the existence of [X, Y, Z] which address similar challenges, the paper needs to more precisely define its unique contribution and demonstrate its advantages experimentally."

---

## 3. Design Weaknesses (W-D)

### W-D1: No Trade-Off Analysis

**Description**: The paper presents its design as if it has no downsides. Every design choice involves trade-offs; failing to acknowledge and analyze them suggests either a lack of understanding or intentional omission.

**Severity**: Major

**How to detect:**
- The design section reads as a sequence of "we do X to achieve Y" without discussing what is given up
- No discussion of when the approach would perform poorly
- No comparison of alternative design choices

**Constructive phrasing:**
- "The paper would benefit from a more honest discussion of trade-offs. For example, the decision to use [approach X] likely comes at the cost of [Y]. Under what conditions would an alternative design be preferable?"
- "Section 3 presents the design as universally beneficial, but [technique X] typically trades off [A] for [B]. A discussion of when this trade-off is unfavorable would strengthen the paper."

### W-D2: Missing Corner Cases and Failure Modes

**Description**: The design does not address important edge cases, failure scenarios, or adversarial conditions that would arise in real deployment.

**Severity**: Major (sometimes Fatal for safety-critical systems)

**How to detect:**
- No discussion of what happens when components fail (crash, slow down, return errors)
- Network partitions, message reordering, and duplication are not addressed in distributed systems
- Concurrency issues (race conditions, deadlocks) are not analyzed
- The system assumes benign behavior in scenarios where adversarial behavior is possible

**Constructive phrasing:**
- "The paper does not discuss the system's behavior when [component X] fails. In a production deployment, this failure mode is not uncommon. How does the system detect and recover from this scenario?"
- "The design assumes [condition Y] always holds, but in practice [counterexample Z] can occur. This could lead to [consequence]. The authors should address this failure mode."

### W-D3: Unjustified Complexity

**Description**: The system design is more complex than necessary to achieve the stated goals. Simpler alternatives are not considered or dismissed without justification.

**Severity**: Minor to Major (depending on degree)

**How to detect:**
- The system has many components but the evaluation shows that a subset provides most of the benefit
- The paper introduces new abstractions or mechanisms that could be replaced by existing, well-understood ones
- The design requires significant infrastructure that the target users may not have

**Constructive phrasing:**
- "The design introduces [N] new mechanisms, but the ablation study shows that [mechanism X] provides [Y%] of the total improvement. Could a simpler design with fewer mechanisms achieve comparable results?"
- "The system requires [infrastructure X] which adds significant deployment complexity. Is this complexity justified by the performance gains, or could a simpler approach work for the common case?"

### W-D4: Hypothetical System

**Description**: The paper describes a design but has not actually built or evaluated a complete working system. The contribution is a design sketch rather than a validated system.

**Severity**: Fatal (for systems venues that require working systems)

**How to detect:**
- Evaluation uses simulation or analytical models only
- Implementation section is vague about what was actually built
- Key components are described as "future work"
- Evaluation environment does not match the intended deployment

**Constructive phrasing:**
- "The evaluation is simulation-based, but systems venues like [OSDI/SOSP] typically require a working implementation. The paper would be significantly strengthened by building and evaluating a real prototype."
- "Several important components are described as future work (Section X.Y). It is difficult to assess the feasibility and performance of the complete system without these components."

### W-D5: Underspecified Design

**Description**: The design description lacks sufficient detail for another researcher to understand and re-implement the system. Key mechanisms, algorithms, or data structures are described vaguely.

**Severity**: Major

**How to detect:**
- Algorithms are described in prose rather than pseudocode, making them ambiguous
- Key parameters or thresholds are not specified or justified
- The interaction between components is unclear
- You cannot determine from the paper how the system actually works

**Constructive phrasing:**
- "The description of [mechanism X] in Section 3.2 is too high-level to evaluate its correctness. Pseudocode or a more formal specification would help the reader understand exactly how this works."
- "How is [parameter Y] determined? The paper states it is 'configured appropriately' but does not explain how this value is chosen or how sensitive the system is to this choice."

---

## 4. Evaluation Weaknesses (W-E)

These are the most common weaknesses in systems paper submissions.

### W-E1: Unfair Baselines

**Description**: Baseline systems are outdated, misconfigured, or running on inferior hardware. The comparison does not reflect the true state of the art.

**Severity**: Major to Fatal

**How to detect:**
- Baseline versions are several years old when newer versions exist
- Baseline configuration is not described, or uses default settings when the original paper recommends different settings
- The authors re-implemented baselines rather than using original code (without justification)
- Hardware or software environment differs between the proposed system and baselines

**Constructive phrasing:**
- "The comparison against [baseline X] uses version [V1], but version [V2] was released in [year] with significant performance improvements. An updated comparison would be more convincing."
- "The paper does not describe how [baseline X] was configured. Was the recommended configuration from [baseline's paper] used? Misconfiguration can artificially inflate the performance gap."

### W-E2: Cherry-Picked Workloads

**Description**: The evaluation uses workloads specifically chosen to favor the proposed system, while ignoring workloads where the system would perform poorly.

**Severity**: Major

**How to detect:**
- All workloads are synthetic and designed to exercise the system's strengths
- Standard benchmarks for the area are notably absent
- The workload selection is not justified relative to real usage patterns
- The paper avoids workloads that stress the system's known weaknesses

**Constructive phrasing:**
- "The evaluation uses [N] custom workloads but does not include standard benchmarks like [X, Y]. These are commonly used in the area and their absence is conspicuous."
- "The workloads all seem to favor [property X] of the proposed system. How does the system perform under workloads with [opposite property Y], which are also common in practice?"

### W-E3: Unsupported Claims

**Description**: Claims in the introduction or abstract are not backed by experimental evidence. There is a mismatch between what is promised and what is demonstrated.

**Severity**: Major to Fatal (depending on which claims are unsupported)

**How to detect:**
- List each numbered contribution and check if there is a corresponding experiment
- Check if quantitative claims in the abstract match the evaluation numbers
- Check if qualitative claims ("works well at scale") are demonstrated experimentally

**Constructive phrasing:**
- "The introduction claims [specific claim], but I could not find experimental evidence supporting this in the evaluation. Which experiment demonstrates this property?"
- "The abstract states '[X] improvement,' but Table [N] shows this improvement only under [specific condition]. The claim should be qualified to reflect the conditions under which it holds."

### W-E4: Missing Error Bars and Statistical Rigor

**Description**: Results are reported without error bars, confidence intervals, or indication of variance. The number of experimental trials is not specified.

**Severity**: Minor to Major

**How to detect:**
- Figures show single data points without error bars
- The paper does not state how many trials were run
- Results report only mean without variance, standard deviation, or percentiles
- Small differences between systems are claimed as meaningful without statistical tests

**Constructive phrasing:**
- "The performance results in Figure [N] do not include error bars. How many trials were run, and what is the variance across runs? This is especially important given the small difference between [system A] and [system B]."
- "The claimed improvement of [X%] over [baseline] is within what might be natural variance. A statistical significance test (e.g., confidence interval analysis) would strengthen this claim."

### W-E5: No Tail Latency Analysis

**Description**: The evaluation reports only average or median latency, ignoring tail latency (p95, p99, p999) which is critical for many systems.

**Severity**: Minor to Major (depends on the system's latency sensitivity)

**How to detect:**
- Latency results show only mean or median
- The system targets interactive or latency-sensitive workloads but provides no percentile analysis
- CDF plots are absent when they would be informative

**Constructive phrasing:**
- "For a system targeting [latency-sensitive workloads], tail latency analysis (p95, p99) is essential. The current evaluation reports only median latency, which can hide significant outliers."
- "A CDF of request latency would be informative here. The average latency of [X ms] could mask a long tail that would be problematic in production."

### W-E6: Insufficient Scale

**Description**: The evaluation is conducted at a scale significantly smaller than the target deployment, making it unclear whether the results would hold at realistic scale.

**Severity**: Major

**How to detect:**
- A system targeting datacenter-scale deployment is evaluated on a single machine or small cluster
- Data sizes are orders of magnitude smaller than production
- Scalability experiments stop well below the claimed target scale
- The paper discusses scale but evaluates only at micro-scale

**Constructive phrasing:**
- "The system targets [datacenter-scale] deployment, but the evaluation uses only [N nodes]. At this scale, [bottleneck X] may not manifest. A larger-scale evaluation would be more convincing."
- "The dataset sizes in the evaluation (up to [X GB]) are much smaller than typical production workloads ([Y TB+]). How does the system behave as data size increases beyond memory capacity?"

### W-E7: No Ablation Study

**Description**: The system combines multiple techniques, but the evaluation does not isolate the contribution of each technique. It is impossible to tell which design choices actually matter.

**Severity**: Major

**How to detect:**
- The system has N design components but evaluation only shows the full system vs. baselines
- No experiments selectively disable components
- It is unclear whether a simpler system (with fewer components) would achieve similar results

**Constructive phrasing:**
- "The system combines [techniques A, B, C], but the evaluation does not isolate their individual contributions. An ablation study disabling each technique would help readers understand which design decisions are most important."
- "Given the system's complexity, it would be valuable to show what happens when [component X] is replaced with a simpler alternative. Is the full complexity necessary?"

### W-E8: Evaluation-Claims Mismatch

**Description**: The experiments measure things that do not directly correspond to the paper's main claims, or the experimental setup does not test the scenarios that motivate the system.

**Severity**: Major

**How to detect:**
- The paper motivates the system based on problem X but evaluates on scenario Y
- The metrics used do not capture the property being claimed
- The experimental conditions do not match the deployment conditions described in the paper

**Constructive phrasing:**
- "The paper motivates the system based on [problem X], but the evaluation primarily measures [metric Y]. A more direct evaluation of [X] would strengthen the paper."
- "The experiments use [conditions], but the motivating scenario in Section 2 assumes [different conditions]. How does the system perform under the conditions that motivate its design?"

### W-E9: Wrong or Misleading Metrics

**Description**: The evaluation uses metrics that do not capture what actually matters for the system's intended use case, or presents metrics in a misleading way.

**Severity**: Major

**How to detect:**
- Reporting throughput alone when latency also matters (or vice versa)
- Using aggregate metrics that hide per-component or per-request variation
- Comparing metrics at different operating points (e.g., throughput at different latency targets)
- Using speedup relative to a weak baseline rather than absolute numbers

**Constructive phrasing:**
- "The evaluation reports throughput but not latency. For [this type of workload], both metrics are important because higher throughput often comes at the cost of increased latency."
- "Figure [N] shows speedup relative to [weak baseline], which makes improvements look larger than they are in absolute terms. Including absolute numbers alongside speedup would provide a clearer picture."

---

## 5. Presentation Weaknesses (W-P)

### W-P1: Poor Writing Quality

**Description**: The prose is unclear, verbose, grammatically incorrect, or otherwise difficult to read. This obscures the technical contribution and makes the paper harder to evaluate.

**Severity**: Minor to Major (depends on degree)

**Constructive phrasing:**
- "The writing quality makes it difficult to evaluate the technical contribution. Several sections would benefit from careful revision for clarity and conciseness. Specific suggestions: [list 2-3 concrete examples]."
- "I encourage the authors to have the paper proofread by a native English speaker. Key ideas are present but sometimes obscured by the prose."

### W-P2: Ineffective Figures

**Description**: Figures are hard to read, lack informative captions, use poor color choices, or do not convey their intended message clearly.

**Severity**: Minor

**How to detect:**
- Can you understand what the figure shows without reading the surrounding paragraph? If not, the caption is insufficient.
- Are axis labels readable at print size? Check at 100% zoom — many figures are readable on-screen but illegible in print.
- Do bar charts or line plots use colors that are distinguishable in grayscale? ~8% of male readers have color vision deficiency.
- Is the figure type appropriate? Common mismatches: bar charts for distributions (use CDFs), line plots for categorical data (use bar charts), 3D plots that obscure data (use heatmaps).

**Constructive phrasing:**
- "Figure [N] would benefit from [larger font sizes / a legend / a more descriptive caption]. Currently, it is difficult to extract the intended message without reading the surrounding text."
- "Consider using a CDF instead of a bar chart in Figure [N] to better show the distribution. The current visualization hides important variance."
- "Figure [N] uses colors that may be indistinguishable for colorblind readers. Consider using different line styles (dashed, dotted) or a colorblind-safe palette."

### W-P3: Inconsistent Terminology

**Description**: The paper uses different terms for the same concept, or the same term for different concepts, creating confusion.

**Severity**: Minor

**How to detect:**
- Search the paper for synonyms of key terms. If "scheduler," "dispatcher," and "coordinator" all refer to the same component, flag it.
- Check whether the same term is defined differently in different sections (semantic overloading).
- Look for abbreviations that are introduced but then the full term is used inconsistently afterward.
- Check that terms in figures and tables match the terms used in the prose.

**Constructive phrasing:**
- "The paper uses both '[term A]' and '[term B]' to refer to what appears to be the same concept. Consistent terminology throughout would improve clarity."
- "The term '[X]' is used differently in Sections [A] and [B]. Please clarify the precise definition and use it consistently."
- "Table 3 uses '[term A]' but the text in Section 4 calls the same concept '[term B]'. Aligning terminology between figures/tables and text would reduce confusion."

### W-P4: Excessive Forward References

**Description**: Key concepts are used before they are defined, with references to later sections. This forces the reader to jump back and forth and makes the paper harder to follow on a first read.

**Severity**: Minor

**How to detect:**
- Count forward references in the Introduction and Section 2. More than 3 forward references to design sections suggests the introduction is not self-contained.
- Check whether any forward-referenced concept is essential to understanding the current section. If removing the forward reference would leave the reader confused, the paper should be restructured.
- Look for chains of forward references (A references B which references C) — these are especially disorienting.

**Constructive phrasing:**
- "Section 3.1 relies heavily on concepts not introduced until Section 3.4. Reordering or adding a brief preview of [concept X] would improve readability."
- "The introduction uses [N] forward references to later sections. Consider making the introduction more self-contained by briefly explaining each concept at first use."
- "The forward reference chain in Section 2 (referencing Section 4, which itself references Section 5) makes it difficult to follow the paper linearly. Consider providing a brief roadmap paragraph that previews all key concepts."

### W-P5: Wrong Paper Organization

**Description**: The paper deviates from the standard structure for the venue in ways that confuse rather than help the reader. Key information is in unexpected locations.

**Severity**: Minor to Major

**Constructive phrasing:**
- "The Related Work section appears before the Evaluation, which is unusual for this venue and makes it harder to assess the contribution before understanding how it compares to prior work."
- "The paper would benefit from splitting the current 'Design and Implementation' section into separate Design and Implementation sections, as the current structure mixes design rationale with implementation details."

---

## 6. Scope Weaknesses (W-S)

### W-S1: Incremental Contribution

**Description**: The paper's contribution is a small, expected improvement over existing work. The ideas are not sufficiently novel or significant for a top-tier venue.

**Severity**: Fatal

**Constructive phrasing:**
- "While the paper is technically sound, the contribution appears incremental relative to [prior work X]. The improvement of [Y%] over [X] is modest, and the underlying approach is similar. A stronger differentiation or a more substantial advance would be needed."
- "The paper extends [prior system] with [technique X]. While the results are positive, the extension is relatively straightforward and does not provide new insights into the problem space."

### W-S2: Too Narrow Scope

**Description**: The system targets an extremely specific scenario, limiting its applicability and interest to the broader community.

**Severity**: Major

**Constructive phrasing:**
- "The system is designed specifically for [narrow scenario X]. While the results are good in this setting, it is unclear how the ideas generalize to related but different scenarios. A discussion of broader applicability would strengthen the paper."
- "The contributions are tied closely to [specific hardware/platform/workload]. Can the approach be adapted to other settings, or is it inherently limited to this specific configuration?"

### W-S3: Too Broad Scope

**Description**: The paper tries to address too many problems at once, resulting in shallow treatment of each. None of the individual contributions is fully developed.

**Severity**: Major

**Constructive phrasing:**
- "The paper attempts to address [problems A, B, and C] simultaneously. While each is interesting, none receives sufficiently deep treatment. Consider focusing on [the strongest contribution] and developing it more thoroughly."
- "The breadth of the paper comes at the cost of depth. The evaluation of [component X] is particularly thin. A more focused paper with a deeper evaluation of the core contribution would be stronger."

### W-S4: Missing or Inadequate Related Work

**Description**: The paper omits important related work, mischaracterizes prior systems, or provides only a superficial comparison with the state of the art.

**Severity**: Minor to Major

**Constructive phrasing:**
- "The related work section omits [important systems X, Y]. These address similar challenges and a comparison (at minimum conceptual, ideally experimental) would help position this work."
- "The characterization of [prior system X] in Section 7 does not match my understanding. Specifically, [X does handle Y], contrary to what is stated. Please verify and correct the comparison."

---

## 7. Quick Reference: Weakness-to-Section Mapping

| ID | Weakness | Typical Severity | Relevant Sections |
|----|----------|-----------------|-------------------|
| W-M1 | Problem doesn't matter | Fatal | Motivation, Introduction |
| W-M2 | No empirical evidence for problem | Major | Motivation |
| W-M3 | Strawman comparison | Major | Motivation, Evaluation |
| W-M4 | Problem already solved | Fatal | Motivation, Related Work |
| W-D1 | No trade-off analysis | Major | Design |
| W-D2 | Missing corner cases / failure modes | Major | Design |
| W-D3 | Unjustified complexity | Minor-Major | Design, Evaluation |
| W-D4 | Hypothetical system | Fatal | Design, Implementation |
| W-D5 | Underspecified design | Major | Design |
| W-E1 | Unfair baselines | Major-Fatal | Evaluation |
| W-E2 | Cherry-picked workloads | Major | Evaluation |
| W-E3 | Unsupported claims | Major-Fatal | Introduction, Evaluation |
| W-E4 | Missing error bars / statistical rigor | Minor-Major | Evaluation |
| W-E5 | No tail latency analysis | Minor-Major | Evaluation |
| W-E6 | Insufficient scale | Major | Evaluation |
| W-E7 | No ablation study | Major | Evaluation |
| W-E8 | Evaluation-claims mismatch | Major | Introduction, Evaluation |
| W-E9 | Wrong or misleading metrics | Major | Evaluation |
| W-P1 | Poor writing quality | Minor-Major | All sections |
| W-P2 | Ineffective figures | Minor | All sections |
| W-P3 | Inconsistent terminology | Minor | All sections |
| W-P4 | Excessive forward references | Minor | Introduction, Design |
| W-P5 | Wrong paper organization | Minor-Major | All sections |
| W-S1 | Incremental contribution | Fatal | Introduction, Related Work |
| W-S2 | Too narrow scope | Major | Introduction, Evaluation |
| W-S3 | Too broad scope | Major | Introduction, Design |
| W-S4 | Missing or inadequate related work | Minor-Major | Related Work |

---

## 8. Venue-Specific Severity Modifiers

The same weakness may carry different weight at different venues. Use these modifiers to adjust severity based on the target venue's values and review culture.

| Weakness | OSDI | NSDI | SIGCOMM | MOBICOM | SOSP |
|----------|------|------|---------|---------|------|
| W-M1 (Problem doesn't matter) | Fatal | Fatal | Fatal | Fatal | Fatal |
| W-M2 (No empirical evidence) | Major | **Fatal** (NSDI demands evidence) | Major | Major | Major |
| W-D4 (Hypothetical system) | Fatal | Fatal | Major (theory papers exist) | Fatal | Fatal |
| W-E1 (Unfair baselines) | Major | **Fatal** (deployment credibility) | Major-Fatal | Major-Fatal | Major |
| W-E2 (Cherry-picked workloads) | Major | **Fatal** (realistic workloads required) | Major | **Fatal** (multi-environment required) | Major |
| W-E4 (Missing error bars) | Minor-Major | Minor-Major | Minor-Major | **Major** (wireless variance is high) | Minor-Major |
| W-E6 (Insufficient scale) | Major | **Fatal** (must show deployment scale) | Major | Minor-Major (mobile scale differs) | Major |
| W-E7 (No ablation) | Major | Major | Major | Major | **Fatal** (must isolate principles) |
| W-S1 (Incremental) | Fatal | Major-Fatal | Fatal | Fatal | Fatal |
| W-P1 (Poor writing) | Minor-Major | Minor-Major | **Major** (high polish expected) | Minor-Major | **Major** (high polish expected) |
| W-P5 (Wrong organization) | Minor | Minor | Minor-Major | Minor | Minor-Major |

**Key venue-specific notes:**
- **NSDI**: Evaluation weaknesses are weighted more heavily than at other venues because NSDI's identity centers on deployed/deployable systems. An NSDI paper with a weak evaluation is like a SIGCOMM paper with no networking contribution.
- **MOBICOM**: Missing error bars and single-environment testing are more severe than at other venues because wireless experiments inherently have high variance. What is "minor" at OSDI may be "major" at MOBICOM.
- **SOSP**: Ablation studies are especially important because SOSP values understanding *why* a system works (principles), not just *that* it works. Without ablation, the paper fails to deliver on SOSP's core value proposition.
- **SIGCOMM/SOSP**: Presentation weaknesses carry more weight because both venues expect polished papers. Poor writing at SIGCOMM is more likely to lead to rejection than at NSDI.

---

## 9. Weakness Interaction Patterns

Weaknesses rarely occur in isolation. Certain combinations are particularly damaging because they compound each other.

### Compound Weakness Effects

| Combination | Effect | Scoring Impact |
|-------------|--------|---------------|
| W-M2 (no evidence) + W-E8 (claims mismatch) | The paper neither motivates the problem with data nor validates the solution against the stated problem. The entire narrative is unsupported. | Treat as Fatal even though individually these are Major. |
| W-D1 (no trade-offs) + W-E2 (cherry-picked workloads) | The paper hides its weaknesses in both the design discussion and the evaluation. Suggests the authors know the system has weaknesses but chose not to expose them. | Treat as Fatal. |
| W-E1 (unfair baselines) + W-E3 (unsupported claims) | If the baselines are unfair AND the claims go beyond what experiments show, the contribution is essentially unverifiable. | Treat as Fatal. |
| W-D5 (underspecified) + W-E7 (no ablation) | You cannot understand what the system does AND you cannot tell which parts matter. The paper is not reproducible or evaluable. | Treat as Fatal. |
| W-P1 (poor writing) + W-D5 (underspecified) | Poor writing makes an already vague design even harder to evaluate. The reviewer cannot determine whether the design is sound. | Escalate both to Major. |
| W-S1 (incremental) + W-E6 (insufficient scale) | A modest contribution evaluated at small scale offers neither novelty nor convincing evidence. | Confirm as Fatal. |

### Mitigating Interactions

Some strengths can partially offset weaknesses:

| Weakness | Mitigating Strength | Net Effect |
|----------|---------------------|------------|
| W-E6 (insufficient scale) | Strong analytical model predicting scale behavior | Downgrade from Major to Minor if model is convincing |
| W-E4 (missing error bars) | Deterministic system with no randomness in execution | Downgrade from Major to Minor (bars would be trivially zero) |
| W-P1 (poor writing) | Exceptionally clear figures and tables that convey the design | Downgrade from Major to Minor if the technical content is still evaluable |
| W-D3 (unjustified complexity) | Thorough ablation showing every component is necessary | Dismiss the weakness entirely |

---

## 10. Constructive Feedback Patterns

When citing a weakness, always follow this structure:

### Pattern: Identify → Evidence → Impact → Suggestion

1. **Identify** the weakness specifically (reference sections, figures, claims)
2. **Provide evidence** from the paper showing the weakness
3. **Explain the impact** on your assessment (why does this matter?)
4. **Suggest** a concrete way to address the weakness

**Example (W-E1):**
> "The evaluation compares against [System X] version 2.1 (Section 5.2), but version 3.0 was released in 2024 with a reported 40% throughput improvement [reference]. This makes the comparison less convincing, as the performance gap may be substantially smaller with the current version of [X]. I recommend updating to the latest version or, if that is infeasible, explaining why the older version is appropriate."

**Example (W-D2):**
> "The design in Section 3.3 does not address what happens when the coordinator node fails during a migration operation. Given that the system targets production deployment where failures are routine, this omission raises concerns about the system's robustness. The authors should describe the failure handling and recovery mechanism for this scenario."

### Anti-Pattern: Vague Criticism

Avoid these:
- "The evaluation is weak." (How? Which specific aspect?)
- "The paper is poorly written." (Where? Give examples.)
- "The novelty is limited." (Compared to what? What exists that is similar?)
- "Not convincing." (What would convince you? What is missing?)

Every criticism should be specific enough that the authors know exactly what to fix.
