# Writing Principles for Systems Conference Papers

## Overview

Effective systems paper writing requires mastering fundamental principles that ensure clarity, precision, and impact. Systems conference papers prioritize accuracy, conciseness, directness, and quantitative rigor. This guide covers the core principles that distinguish well-written systems papers from poorly written ones and provides practical strategies for improvement.

## The Three Pillars of Scientific Writing

### 1. Clarity

**Definition:** Writing that is immediately understandable to the intended audience without ambiguity or confusion.

**Why it matters:** Science is complex enough without unclear writing adding confusion. Readers should focus on understanding the science, not deciphering the prose.

#### Strategies for Clarity

**Use precise, unambiguous language:**
```
Poor: "The system was faster in most cases."
Better: "The system achieved 2.3x higher throughput (15.2K vs. 6.6K tokens/sec)."
```

**Define technical terms at first use:**
```
"We use Remote Direct Memory Access (RDMA), a protocol that enables zero-copy
network transfers between machines without involving the CPU."
```

**Maintain logical flow within and between paragraphs:**
- Each paragraph should have one main idea
- Topic sentence introduces the paragraph's focus
- Supporting sentences develop that focus
- Transition sentences connect paragraphs

**Use active voice when it improves clarity:**
```
Passive (less clear): "The requests were processed by the load balancer."
Active (clearer): "The load balancer processes incoming requests."
```

However, passive voice is acceptable in descriptions where the action matters more than the actor:
```
"Checkpoints are loaded into GPU memory before serving begins."
```

**Break up long, complex sentences:**
```
Poor: "Our system, which consists of a scheduler that assigns requests to
workers based on checkpoint locality and a storage layer that streams model
weights using RDMA, achieves 2.3x higher throughput than existing systems."

Better: "Our system consists of a locality-aware scheduler and a streaming
storage layer. The scheduler assigns requests to workers based on checkpoint
locality. The storage layer streams model weights using RDMA. Together, these
components achieve 2.3x higher throughput than existing systems."
```

**Use specific verbs:**
```
Weak: "The system deals with load balancing issues."
Stronger: "The system distributes requests across workers based on GPU memory
availability."
```

#### Common Clarity Problems

**Ambiguous pronouns:**
```
Poor: "System A uses data parallelism and System B uses pipeline parallelism.
It achieved higher throughput."
(Which system is "it"?)

Better: "System A uses data parallelism and System B uses pipeline parallelism.
System B achieved higher throughput due to reduced communication overhead."
```

**Misplaced modifiers:**
```
Poor: "We profiled inference latency on GPUs using a custom tracer."
(Are the GPUs using the tracer, or are we?)

Better: "Using a custom tracer, we profiled inference latency on GPUs."
```

**Unclear referents:**
```
Poor: "The increase in batch size was accompanied by higher latency, which
was unexpected."
(What was unexpected—the latency increase, the accompaniment, or both?)

Better: "The increase in batch size was accompanied by higher latency. This
positive correlation was unexpected given the improved GPU utilization."
```

### 2. Conciseness

**Definition:** Expressing ideas in the fewest words necessary without sacrificing clarity or completeness.

**Why it matters:** Concise writing respects readers' time. Every unnecessary word is a missed opportunity for clarity and impact. As the principle states: "We value concise writing because we value time."

#### Strategies for Conciseness

**Eliminate redundant words and phrases:**

| Wordy | Concise |
|-------|---------|
| "due to the fact that" | "because" |
| "in order to" | "to" |
| "it is important to note that" | [delete] |
| "a total of 50 participants" | "50 participants" |
| "completely eliminate" | "eliminate" |
| "has been shown to be" | "is" |
| "in the event that" | "if" |
| "at the present time" | "now" or "currently" |
| "conduct an investigation into" | "investigate" |
| "give consideration to" | "consider" |

**Avoid throat-clearing phrases:**
```
Wordy: "It is interesting to note that the results of our study demonstrate that..."
Concise: "Our results demonstrate that..." or "The results show that..."
```

**Use strong verbs instead of noun+verb combinations:**

| Wordy | Concise |
|-------|---------|
| "make a decision" | "decide" |
| "perform an analysis" | "analyze" |
| "conduct a study" | "study" or "studied" |
| "make an assessment" | "assess" |
| "provide information about" | "inform" |

**Eliminate unnecessary intensifiers:**
```
Wordy: "The results were very significant."
Concise: "The results were significant." (p-value conveys the degree)
```

**Avoid repeating information unnecessarily:**
```
Redundant: "The results showed that participants in the intervention group, who
received the treatment intervention, had better outcomes."
Concise: "The intervention group had better outcomes."
```

**Favor shorter constructions:**
```
Wordy: "In spite of the fact that the sample size was small..."
Concise: "Although the sample size was small..."
```

#### Acceptable Length vs. Unnecessary Length

**Not all long sentences are bad:**
```
This detailed sentence is fine: "We analyzed blood samples using liquid
chromatography-tandem mass spectrometry (LC-MS/MS) with a Waters Acquity UPLC
system coupled to a Xevo TQ-S mass spectrometer (Waters Corporation, Milford, MA)."

Why? Because each element is necessary information.
```

**The key question:** Can any word be removed without losing meaning or precision? If yes, remove it.

### 3. Accuracy

**Definition:** Precise, correct representation of data, methods, and interpretations.

**Why it matters:** Scientific credibility depends on accuracy. Inaccurate reporting undermines the entire scientific enterprise.

#### Strategies for Accuracy

**Report exact values with appropriate precision:**
```
Poor: "Throughput was about 15K."
Better: "Throughput was 15,200 ± 340 tokens/sec (mean ± std dev over 5 runs)."
```

**Match precision to measurement capability:**
```
Inappropriate: "Latency was 12.34567 ms" (implies false precision)
Appropriate: "Latency was 12.3 ms"
```

**Use consistent terminology throughout:**
```
Inconsistent: Introduction calls it "serving throughput," Design calls it
"inference speed," Evaluation calls it "token generation rate."

Consistent: Use "inference throughput" throughout, measured in tokens/sec.
```

**Distinguish observations from interpretations:**
```
Observation: "p99 latency increased from 45ms to 120ms when batch size doubled."
Interpretation: "This suggests memory bandwidth becomes the bottleneck at larger
batch sizes."
```

**Be specific about uncertainty:**
```
Vague: "There is some variance in the measurements."
Specific: "Throughput measurements show a standard deviation of ±340 tokens/sec
over 5 independent runs with different random seeds."
```

**Ensure fair comparisons:**
```
Poor: "Our system is faster than the baseline."
Better: "Using identical hardware (8x A100 GPUs) and workload (LLaMA-70B,
batch size 32), our system achieves 2.3x higher throughput than vLLM v0.3.1."
```

**Verify all numbers:**
- Check that numbers in text match tables/figures
- Verify speedup ratios are correctly calculated
- Confirm percentages are consistent throughout
- Double-check all performance claims

#### Common Accuracy Problems

**Overgeneralization:**
```
Poor: "Our system is the fastest LLM serving framework."
Better: "On the LLaMA-70B workload with batch size 32, our system achieves
2.3x higher throughput than vLLM and 1.9x higher than TensorRT-LLM using
8x A100 GPUs."
```

**Unwarranted causal claims:**
```
Poor: "RDMA eliminates all network bottlenecks."
Better: "Switching from TCP to RDMA reduced communication overhead by 3.2x
in our all-reduce benchmark, though the benefit diminishes for compute-bound
workloads (Section 5.3)."
```

**Imprecise numerical descriptions:**
```
Vague: "The system handles many requests."
Precise: "The system sustains 15,200 requests/sec at p99 latency under 50ms."
```

## Additional Key Principles

### 4. Objectivity

**Definition:** Presenting information impartially without bias, exaggeration, or unsupported opinion.

**Strategies:**

**Present results without bias:**
```
Biased: "As expected, our novel approach vastly outperformed all baselines."
Objective: "Our system achieved 2.3x higher throughput than vLLM and 1.9x higher
than TensorRT-LLM on the LLaMA-70B benchmark."
```

**Acknowledge where baselines perform better:**
```
"While ServerlessLLM achieves higher throughput at large batch sizes, vLLM shows
lower latency for single requests due to its lightweight scheduling overhead.
This trade-off is expected given our system's focus on batch throughput."
```

**Avoid hype and evaluative language:**
```
Subjective: "The results were groundbreaking and transformative."
Objective: "The system achieved 2.3x higher throughput, enabling serving
LLaMA-70B at interactive latencies on a single node."
```

**Distinguish measurement from hypothesis:**
```
"The throughput improvement correlates with increased GPU memory bandwidth
utilization (from 45% to 82%), suggesting that our scheduling strategy better
exploits available memory bandwidth."
(Uses "suggesting" to indicate interpretation of correlation)
```

### 5. Consistency

**Maintain consistency throughout the manuscript:**

**Terminology:**
- Use the same term for the same concept (not synonyms for variety)
- Define abbreviations at first use and use consistently thereafter
- Use standard systems terminology consistently

**Notation:**
- Performance metrics (consistent units: tokens/sec, ms, Gbps)
- Number formatting (consistent decimal places across tables)
- Speedup notation (use "x" consistently: "2.3x" not "2.3 times")

**Tense:**
- Past tense for experiments you ran
- Present tense for how the system works
- See detailed tense guide in systems paper structure reference

**Style:**
- Follow venue template consistently
- Citation format (IEEE or ACM)
- Heading capitalization
- Number vs. word for numerals

### 6. Logical Organization

**Create a clear "red thread" through the manuscript:**

**Paragraph structure:**
1. Topic sentence (main idea)
2. Supporting sentences (evidence, explanation)
3. Concluding/transition sentence (link to next idea)

**Section flow:**
- Each section builds logically on the previous
- Problems raised in Introduction are solved in Design
- Claims made in Introduction are validated in Evaluation

**Signposting:**
```
"First, we examined..."
"Next, we investigated..."
"Finally, we assessed..."
```

**Parallelism:**
```
Not parallel: "Our contributions are: (1) a new scheduling algorithm,
(2) we implemented a storage layer, and (3) evaluation of the system."

Parallel: "Our contributions are: (1) a locality-aware scheduling algorithm,
(2) a streaming storage layer, and (3) a comprehensive evaluation on
production workloads."
```

## Verb Tense in Systems Papers

### General Guidelines

**Present tense** for:
- How the system works (design descriptions)
  - "The scheduler assigns requests to workers based on locality."
- Established facts and general truths
  - "LLM inference is memory-bandwidth bound during the decode phase."
- Referring to figures and tables
  - "Figure 3 shows the throughput comparison."

**Past tense** for:
- Experiments you ran and results you obtained
  - "We measured inference throughput on 8x A100 GPUs."
  - "ServerlessLLM achieved 2.3x higher throughput."
- Implementation actions
  - "We implemented the scheduler in 3,000 lines of Go."

**Present perfect** for:
- Recent developments with current relevance
  - "Recent systems have demonstrated the benefits of disaggregation."
- Research area background
  - "Several approaches have been proposed for LLM serving."

### Section-Specific Tense

| Section | Primary Tense | Examples |
|---------|---------------|----------|
| **Abstract - Problem** | Present | "Serving LLMs requires..." |
| **Abstract - What we did** | Present or past | "We present..." / "We designed..." |
| **Abstract - Results** | Past | "achieved 2.3x higher throughput" |
| **Introduction - Context** | Present | "Models continue to grow..." |
| **Introduction - This work** | Present | "We present SystemName" |
| **Introduction - Contributions** | Mixed | "We identify... We design... We evaluate..." |
| **Background - Facts** | Present | "GPUs use shared memory architectures..." |
| **Background - Measurements** | Past | "We profiled the existing system and found..." |
| **Design - System description** | Present | "The scheduler assigns... Workers load..." |
| **Implementation** | Past | "We implemented... We integrated..." |
| **Evaluation - Setup** | Past | "We ran experiments on..." |
| **Evaluation - Results** | Past | "SystemName achieved..." |
| **Evaluation - Interpretation** | Present | "This shows that... This is because..." |
| **Related Work** | Present | "Borg [5] uses... vLLM [8] supports..." |
| **Conclusion** | Mixed | "We presented... SystemName achieves..." |

## Common Writing Pitfalls

### 1. Jargon Overload

**Problem:** Excessive use of technical terms without definition

**Example:**
```
Poor: "We leveraged RDMA-based zero-copy DMA transfers via the NIC's IOMMU-mapped
MRs with adaptive CQ polling using CQE batching over RC QPs."

Better: "We use Remote Direct Memory Access (RDMA) for zero-copy data transfers.
The NIC performs direct memory access (DMA) through pre-registered memory regions,
and our system batches completion queue events to reduce polling overhead."
```

### 2. Nominalization

**Problem:** Turning verbs into nouns, making writing heavy and indirect

**Examples:**

| Nominalized | Direct |
|-------------|--------|
| "give consideration to" | "consider" |
| "make an assumption" | "assume" |
| "perform an investigation" | "investigate" |
| "conduct an examination" | "examine" |
| "achieve a reduction" | "reduce" |

### 3. Hedging Excessively or Insufficiently

**Excessive hedging** (sounds uncertain):
```
"It could perhaps be possible that our approach might possibly improve throughput
under certain conditions in some configurations."
```

**Insufficient hedging** (overstates conclusions):
```
"Our system eliminates all latency problems in LLM serving."
```

**Appropriate hedging:**
```
"Our system reduces p99 latency by 2.7x on the LLaMA-70B workload, suggesting
that locality-aware scheduling can significantly improve tail latency in LLM
serving clusters."
```

**Hedging in systems papers:**
- Systems papers hedge less than other fields
- In evaluation: state results directly ("achieves 2.3x speedup")
- In interpretation: hedge appropriately ("suggesting that", "we attribute this to")
- In limitations: be honest ("our approach is limited to", "we do not address")

### 4. Anthropomorphism

**Problem:** Attributing human characteristics to non-human entities

**Examples:**

| Anthropomorphic | Scientific |
|----------------|-----------|
| "The study wanted to examine..." | "We aimed to examine..." or "The study examined..." |
| "The data suggest they want..." | "The data suggest that..." |
| "This paper will prove..." | "This paper demonstrates..." |
| "Table 1 tells us..." | "Table 1 shows..." |

### 5. Abbreviation Abuse

**Problems:**
- Too many abbreviations burden the reader
- Abbreviating terms used only once or twice
- Not defining abbreviations at first use

**Guidelines:**
- Only abbreviate terms used ≥3-4 times
- Define at first use in abstract (if used in abstract)
- Define at first use in main text
- Don't abbreviate in title
- Limit to 3-4 new abbreviations per paper when possible
- Use standard abbreviations (GPU, CPU, RDMA, API, etc.) without definition

**Example:**
```
Poor: "We measured Time-To-First-Token (TTFT) for a single request. TTFT
was under 100ms."
(Only used twice, abbreviation unnecessary)

Better: "We measured time-to-first-token for a single request, which was
under 100ms."
```

## Specific Sentence-Level Issues

### Dangling Modifiers

**Problem:**
```
"After running for 30 minutes, we collected the throughput results."
(The sentence suggests "we" were running)

Better: "After running the benchmark for 30 minutes, we collected the
throughput results."
Or: "After a 30-minute warm-up period, we collected the throughput results."
```

### Misplaced Commas

**Common errors:**

**Between subject and verb:**
```
Wrong: "The workers in the GPU cluster, achieved higher throughput."
Right: "The workers in the GPU cluster achieved higher throughput."
```

**In compound predicates:**
```
Wrong: "We measured throughput, and recorded latency."
Right: "We measured throughput and recorded latency."
(No comma before "and" when it doesn't join independent clauses)
```

### Pronoun Agreement

```
Wrong: "Each worker processes their assigned requests."
Right: "Each worker processes its assigned requests."
Or better: "Workers process their assigned requests."
```

### Subject-Verb Agreement

```
Wrong: "The set of GPUs were fully utilized."
Right: "The set of GPUs was fully utilized."
(Subject is "set" [singular], not "GPUs")

But: "The GPUs were fully utilized." (Plural subject)
```

## Word Choice

### Commonly Confused Words in Scientific Writing

| Often Misused | Correct Usage |
|---------------|---------------|
| **affect / effect** | Affect (verb): influence; Effect (noun): result; Effect (verb): bring about |
| **among / between** | Among: three or more; Between: two |
| **continual / continuous** | Continual: repeated; Continuous: uninterrupted |
| **data is / data are** | Data are (plural); datum is (singular) |
| **fewer / less** | Fewer: countable items; Less: continuous quantities |
| **i.e. / e.g.** | i.e. (that is): restatement; e.g. (for example): examples |
| **imply / infer** | Imply: suggest; Infer: deduce |
| **parameter / variable** | Parameter: configuration setting; Variable: measured quantity |
| **principal / principle** | Principal: main; Principle: rule or concept |
| **significant** | Use for meaningful differences, prefer quantifying ("2.3x faster") |
| **that / which** | That: restrictive clause; Which: nonrestrictive clause |

### Words to Avoid or Use Carefully

**Avoid informal language:**
- "a lot of" → "many" or "substantial"
- "got" → "obtained" or "became"
- "showed up" → "appeared" or "was evident"

**Avoid vague quantifiers:**
- "some" → specify how many
- "often" → specify frequency
- "recently" → specify timeframe

**Avoid unnecessary modifiers:**
- "very significant improvement" → state the actual speedup ("2.3x faster")
- "quite large overhead" → quantify ("12% overhead")
- "rather interesting result" → delete or explain why it matters

## Numbers and Units

### When to Use Numerals vs. Words

**Use numerals for:**
- All numbers ≥10
- Numbers with units (5 ms, 3 GB, 8 GPUs)
- Performance metrics (2.3x speedup, 15K tokens/sec)
- Counts with technical context (4 workers, 3 pipeline stages)
- Percentages (15%)

**Use words for:**
- Numbers <10 when not connected to units (five experiments)
- Numbers beginning a sentence (spell out or restructure)

**Examples:**
```
"Five participants withdrew" OR "There were 5 withdrawals"
(NOT: "5 participants withdrew")

"We tested 15 samples at 3 time points"
"Mean age was 45 years"
```

### Units and Formatting

**Guidelines:**
- Space between number and unit (5 mg, not 5mg)
- No period after units (mg not mg.)
- Use SI units unless field convention differs
- Be consistent in decimal places
- Use commas for thousands in text (12,500 not 12500)

**Ranges:**
- Use en-dash (–) for ranges: 15–20 mg
- Include unit only after second number: 15–20 mg (not 15 mg–20 mg)

## Paragraph Structure

### Ideal Paragraph Length

**Guidelines:**
- 3-7 sentences typically
- One main idea per paragraph
- Too short (<2 sentences): may indicate idea needs development or combining
- Too long (>10 sentences): may need splitting

### Paragraph Coherence

**Techniques:**

**1. Topic sentence:**
```
"Exercise training improves cardiovascular function through multiple mechanisms.
[Following sentences explain these mechanisms]"
```

**2. Transitional phrases:**
- First, second, third, finally
- Furthermore, moreover, in addition
- However, nevertheless, conversely
- Therefore, thus, consequently
- For example, specifically, particularly

**3. Repetition of key terms:**
```
"...this mechanism of action. This mechanism may explain..."
(Not: "...this mechanism. This process may explain...")
```

**4. Parallel structure:**
```
"Worker A processes prefill requests. Worker B processes decode requests. Worker C
handles scheduling."
(Not: "Worker A processes prefill requests. Decode requests were handled by Worker B.
The third worker is responsible for scheduling.")
```

## Revision Checklist

### Content Level

- [ ] Does every sentence add value?
- [ ] Are claims supported by data?
- [ ] Is the logic clear and sound?
- [ ] Are interpretations warranted by results?

### Paragraph Level

- [ ] Does each paragraph have one main idea?
- [ ] Are paragraphs in logical order?
- [ ] Are transitions smooth?
- [ ] Is there a clear "red thread"?

### Sentence Level

- [ ] Are sentences clear and concise?
- [ ] Is sentence structure varied?
- [ ] Are there no dangling modifiers?
- [ ] Do subjects and verbs agree?

### Word Level

- [ ] Is word choice precise?
- [ ] Are technical terms defined?
- [ ] Is terminology consistent?
- [ ] Are abbreviations necessary and defined?
- [ ] Are numbers formatted correctly?

### Grammar and Mechanics

- [ ] Is verb tense correct and consistent?
- [ ] Are commas used correctly?
- [ ] Do pronouns agree with antecedents?
- [ ] Is punctuation correct?
- [ ] Is spelling correct (including technical terms)?

## Tools for Improving Writing

### Grammar and Style Checkers

- **Grammarly**: Grammar, style, clarity
- **ProWritingAid**: In-depth writing analysis
- **Hemingway Editor**: Readability, simplification
- **LanguageTool**: Open-source grammar checker

**Caution:** These tools don't understand scientific writing conventions. Use them as a starting point, not final arbiter.

### Readability Metrics

**Flesch Reading Ease:**
- 60-70: acceptable for scientific papers
- <60: may be too complex

**Caution:** Don't sacrifice precision for readability scores designed for general audiences.

### Peer Review

**Most valuable tool:**
- Ask colleagues to read and provide feedback
- Identify unclear passages
- Check logical flow
- Verify interpretations are warranted

## Additional Resources

### Books and Guides on Systems Paper Writing

- *Style: Lessons in Clarity and Grace* by Joseph Williams and Joseph Bizup
- *The Elements of Style* by Strunk & White
- "How (and How Not) to Write a Good Systems Paper" by Roy Levin and David Redell (USENIX)
- "How to Increase the Chances Your Paper is Accepted at ACM SIGCOMM" by Craig Partridge
- "Top-10 Tips for Writing a Paper" by Jim Kurose (SIGCOMM CoNEXT)

### Online Resources

- **USENIX Author Resources**: Writing advice for systems papers
- **SIGCOMM Author Guide**: Tips for networking papers
- **Academic Phrasebank** (University of Manchester): Common academic phrases
- **Purdue OWL**: Grammar, punctuation, style

## Systems Conference Writing Style

### Characteristics

Systems conference papers have a distinctive writing style:

- **Direct and technical**: Assumes reader expertise in systems
- **Problem-focused**: Leads with the problem, not the solution
- **Active voice strongly preferred**: "We design", "We implement", "We evaluate"
- **Quantitative**: Specific numbers, not vague qualifications
- **No hype**: Let contributions and numbers speak for themselves
- **Practical**: Emphasizes real-world impact and deployments

### Systems Conference Style Details

| Aspect | Systems Conference (OSDI/NSDI/SIGCOMM) |
|--------|---------------------------------------|
| **Sentence length** | 15-20 words average |
| **Vocabulary** | Systems terminology, assumes expertise |
| **Tone** | Direct, confident, problem-focused |
| **Key phrases** | "We present", "The key insight is", "We make the following contributions" |
| **Paragraph length** | 4-6 sentences |
| **Math/equations** | Minimal, practical (complexity analysis, optimization objectives) |
| **Active voice** | Strongly preferred |
| **Hedging** | Minimal in evaluation; moderate in interpretation |
| **Figure integration** | Dense, inline, immediately discussed in text |

### Example Opening (OSDI/NSDI style)

```
Serving large language models (LLMs) requires loading multi-gigabyte model
checkpoints into GPU memory, creating cold-start latencies of tens of seconds.
Existing serverless platforms are designed for lightweight functions and cannot
handle these requirements. We present ServerlessLLM, a system that reduces LLM
serving cold start from 30 seconds to under 500 milliseconds through
locality-aware checkpoint loading across a GPU cluster. The key insight is that
checkpoint data can be streamed incrementally while overlapping with computation.

We make the following contributions:
(1) We characterize the checkpoint loading bottleneck in serverless LLM serving
    and identify locality as the key factor (Section 2).
(2) We design a locality-aware scheduler that routes requests to workers with
    cached checkpoints (Section 3).
(3) We implement ServerlessLLM in 12K lines of Python and C++, integrated with
    PyTorch and Kubernetes (Section 4).
(4) We evaluate ServerlessLLM on production workloads and demonstrate 2.3x
    higher throughput than vLLM (Section 5).
```

- Problem stated with specific numbers (tens of seconds)
- Gap identified (existing platforms can't handle)
- Solution previewed with key insight
- Numbered contributions with section references
- Quantitative claim (2.3x)

### Systems vs. ML Conference Style Comparison

| Aspect | Systems (OSDI/SIGCOMM) | ML (NeurIPS/ICML) |
|--------|----------------------|-------------------|
| **Focus** | Problem + system design + evaluation | Algorithm + theory + benchmarks |
| **Math** | Minimal, practical | Central, formal proofs |
| **Evaluation** | End-to-end + microbenchmarks | Standard benchmarks + ablation |
| **Related Work** | After evaluation | Varies (intro or end) |
| **Contribution style** | "We build X that achieves Y" | "We propose X with guarantee Y" |
| **Page length** | 12-15 pages | 8-9 pages |
| **Implementation** | Detailed (LOC, frameworks) | Brief or absent |
| **Reproducibility** | Artifact evaluation | Code release |

### Evaluation Focus by Venue

| Venue | Key Evaluation Criteria |
|-------|------------------------|
| **OSDI/SOSP** | Real system built? Practical impact? Design trade-offs justified? Comprehensive evaluation? |
| **NSDI** | Networking impact? Deployment experience? Scalability shown? |
| **SIGCOMM** | Networking contribution? Formal analysis if applicable? Real traffic evaluation? |
| **MOBICOM** | Mobile/wireless contribution? Hardware prototype? Real-world testing? |

### Common Rejection Reasons

1. "I'm not convinced you're solving a real problem" - Weak motivation
2. "I'm not convinced you're solving the problem" - Evaluation doesn't support claims
3. "I don't understand" - Paper too badly written
4. "Insufficient contribution" - Incremental over existing systems
5. Missing or unfair baseline comparisons
6. Design trade-offs not explained
7. Related work incomplete

### Pre-Submission Style Checklist

**Writing quality:**
- [ ] Writing style matches 3-5 recent papers from target venue
- [ ] Active voice used predominantly
- [ ] Sentence length averages 15-20 words
- [ ] No hype words ("novel", "groundbreaking", "revolutionary")
- [ ] All claims supported by specific numbers from evaluation
- [ ] Consistent terminology throughout

**Systems paper conventions:**
- [ ] Contributions clearly numbered in introduction
- [ ] Motivation section includes empirical evidence
- [ ] Design explains WHY, not just WHAT
- [ ] Implementation mentions LOC and frameworks
- [ ] Evaluation includes macrobenchmarks, microbenchmarks, and ablation
- [ ] Related work placed after evaluation
- [ ] All baseline systems compared fairly (same hardware, configuration)
- [ ] Limitations acknowledged

## Final Thoughts

Effective systems paper writing is a skill developed through practice. Key principles:

1. **Clarity** trumps complexity
2. **Conciseness** respects readers' time and page limits
3. **Accuracy** builds credibility (especially in evaluation)
4. **Objectivity** maintains scientific integrity
5. **Consistency** aids comprehension
6. **Logical organization** guides readers through the story
7. **Venue-specific adaptation** maximizes acceptance probability

**Remember:** The goal is not to impress reviewers with vocabulary or complexity, but to communicate your system's contribution clearly and precisely so reviewers can understand the problem, the solution, and the evidence that the solution works. Write for the tired reviewer reading their 20th paper.
