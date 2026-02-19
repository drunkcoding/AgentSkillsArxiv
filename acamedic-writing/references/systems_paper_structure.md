# Systems Conference Paper Structure

## Overview

Systems conference papers follow a structure fundamentally different from journal papers. Instead of IMRAD (Introduction, Methods, Results, Discussion), systems papers use a problem-solution-evaluation structure that reflects how systems research is conducted: identify a real problem, design and build a system to solve it, and evaluate the system empirically.

**Standard systems paper structure:**
1. Introduction
2. Background / Motivation
3. Design
4. Implementation
5. Evaluation
6. Related Work
7. Conclusion

**Target venues:** OSDI, NSDI, SIGCOMM, MOBICOM, SOSP, ATC, EuroSys

**Typical length:** 12-14 pages (excluding references and appendices)

## Title

### Purpose
Identify the system and communicate its core contribution in a single line.

### The "SystemName: Subtitle" Pattern

Systems papers almost always name their system. The title follows the pattern:
```
SystemName: Descriptive Subtitle Explaining What It Does
```

### Guidelines
- Name the system (readers will refer to it by name)
- Subtitle should explain what the system does and for what purpose
- Be specific about the problem domain
- Include the key technical approach or insight when space permits
- Avoid question formats
- Keep under 15 words total

### Examples from Top Venues
```
Good:
- "ServerlessLLM: Low-Latency Serverless Inference for Large Language Models" (OSDI 2024)
- "Ekko: A Large-Scale Deep Learning Recommender System with Low-Latency Model Update" (OSDI 2022)
- "KungFu: Making Training in Distributed Machine Learning Adaptive" (OSDI 2020)
- "Tenplex: Dynamic Parallelism for Deep Learning using Parallelizable Tensor Collections" (SOSP 2024)
- "WaferLLM: Large Language Model Inference at Wafer Scale" (OSDI 2025)
- "Cameo: Fine-grained Real-time Stream Processing with Deadlines" (NSDI 2021)

Too vague:
- "A System for Machine Learning"
- "Improving Distributed Training"

Too long:
- "A Novel Framework for Dynamically Adapting GPU Allocation in Distributed Deep
  Learning Training Jobs Using Tensor Repartitioning and Virtual File Systems"
```

### System Naming Tips
- Short, memorable names (1-2 syllables ideal)
- Often evocative of the system's purpose or mechanism
- Must be easily searchable (avoid common English words alone)

## Abstract

### Format
**Unstructured narrative** (NOT structured with labeled Background/Methods/Results/Conclusions sections). Systems conference abstracts are a single flowing paragraph.

### Length
150-250 words (check venue-specific requirements)

### Internal Structure (within the narrative)

The abstract follows a 5-part narrative flow:

1. **Problem context** (1-2 sentences): What domain/workload matters and why
2. **Gap/challenge** (1-2 sentences): What current systems fail to do
3. **Solution overview** (1-2 sentences): What the system does and its key insight
4. **Key results** (2-3 sentences): Quantitative evaluation highlights with specific numbers
5. **Availability** (optional, 1 sentence): Open-source URL or deployment status

### Example Pattern
```
[Domain] is a rapidly growing workload that requires [resource]. Existing systems
for [domain] rely on [approach], which suffers from [limitation]. We present
[SystemName], a [description] that achieves [goal] through [key technique]. The
key insight is that [insight]. Our evaluation on [workloads] shows that
[SystemName] achieves [X]x speedup over [baseline] while reducing [metric] by
[Y]%. [SystemName] is available at [URL].
```

### Key Rules
- Write the abstract LAST
- Every claim must be backed by evaluation results
- Include specific numbers (speedup, latency reduction, throughput improvement)
- Use past tense for what you did, present tense for what the system is/does
- Do not cite references in the abstract
- Name the system in the abstract

## Introduction

### Length
1.5-2 pages (approximately 12-15% of the paper)

### Problem-Solution Structure

The introduction follows a highly standardized structure in systems papers. It consists of 6-7 paragraphs with clear roles:

#### Paragraphs 1-2: Broad Context and Importance

Establish the problem domain and why it matters. Use concrete numbers showing scale, growth, or cost.

```
Example pattern:
"Large language models have grown from billions to trillions of parameters,
requiring increasingly large GPU clusters for both training and inference.
Serving these models at scale has become a critical infrastructure challenge,
with companies deploying thousands of GPUs for inference alone."
```

**Tips:**
- Start broad, then narrow
- Use real-world numbers (model sizes, cluster sizes, costs, latencies)
- Cite recent trends and industry developments
- Establish urgency or practical importance

#### Paragraphs 3-4: Specific Problem and Technical Gap

Narrow from the domain to the specific technical problem. Show WHY existing approaches fail.

```
Example pattern:
"However, existing serving systems assume [X], which leads to [problem]. When
[condition], current approaches suffer from [specific limitation]. As we show
in Section 2, [measurement or analysis] reveals that [gap]."
```

**Tips:**
- Be precise about what fails and why
- Reference your motivation section ("As we show in Section 2...")
- Include a concrete example or scenario
- Distinguish between fundamental limitations vs. engineering gaps

#### Paragraph 5: Solution Overview

Brief description of the system and its key insight.

```
Example pattern:
"We present [SystemName], a [system type] that [achieves goal] by [approach].
The key insight behind [SystemName] is that [insight]. Unlike prior systems
that [old approach], [SystemName] [new approach]."
```

**Tips:**
- One paragraph, not a full design description
- Emphasize the key insight or design principle
- Briefly contrast with existing approaches
- Give readers a mental model of the system

#### Paragraph 6: Contributions

Numbered list of 3-4 contributions. This is a strong convention in systems papers.

```
Standard pattern:
"We make the following contributions:

(1) We identify [problem insight] through [measurement/analysis] of
    [workloads/systems] (Section 2).

(2) We design [key mechanism/algorithm] that [what it achieves] by
    [how it works] (Section 3).

(3) We implement [SystemName] in [X] lines of [language], integrating
    with [frameworks/systems] (Section 4).

(4) We evaluate [SystemName] on [workloads] and show [key result]:
    [X]x improvement over [baseline] (Section 5)."
```

**Tips:**
- Typically 3-4 contributions (rarely more)
- Each contribution maps to a paper section
- Include section references
- The evaluation contribution should have a specific quantitative result
- Order: insight/characterization, design, implementation, evaluation

#### Final Paragraph: Paper Organization (optional)

Some papers include a brief roadmap. Others fold this into the contributions by adding section references. Either approach is acceptable.

```
"The rest of this paper is organized as follows. Section 2 provides background
and motivation. Section 3 describes the design of [SystemName]..."
```

### Voice and Tone in the Introduction
- Active voice: "We present", "We identify", "We design", "We evaluate"
- Direct and confident but not boastful
- Avoid: "novel", "groundbreaking", "first-ever" (let the contributions speak)
- Appropriate: "We observe that", "Our key insight is", "We demonstrate that"

## Background / Motivation

### Length
1-2 pages (approximately 8-15% of the paper)

### Purpose
1. Provide technical context readers need to understand the design
2. **Demonstrate the problem exists** with evidence (measurements, profiling, analysis)
3. Establish why naive or existing approaches fail

### Structure

#### Background Subsection
Technical prerequisites the reader needs:
- System model (what components exist, how they interact)
- Key definitions and abstractions
- Relevant hardware or software architecture details
- Threat model (for security papers)

```
Example: For WaferLLM, the background explains wafer-scale architecture,
mesh-based memory, and the difference between GEMM and GEMV operations.
```

#### Motivation Subsection
**This is the most distinctive feature of systems papers.** The motivation must demonstrate the problem exists through empirical evidence:

- **Measurement study** showing the problem at scale
- **Profiling results** exposing performance bottlenecks
- **Workload analysis** from real deployments
- **Comparison** showing the gap between ideal and actual performance

```
Example from ServerlessLLM: Profiling checkpoint loading times showing that
existing serverless platforms take tens of seconds for cold starts, far too
slow for interactive LLM serving.

Example from Tenplex: Three real-world scenarios (elasticity, hardware
maintenance, GPU failure) motivating the need for dynamic GPU reallocation.

Example from WaferLLM: Measuring the mismatch between GPU-optimized LLM
inference code and wafer-scale hardware, showing "extremely poor performance"
when directly porting.
```

### Figures in Motivation
Motivation sections almost always include 1-2 figures:
- Performance profiles showing bottlenecks
- Workload characterization plots
- Comparison between existing and ideal performance
- Breakdown of where time/resources are spent

### Common Patterns

**"Problem in Three Acts"** (from Tenplex):
Present 3 distinct real-world scenarios that all require the same capability.

**"Measurement reveals gap"** (from ServerlessLLM):
Profile an existing system, show where it falls short, quantify the gap.

**"Hardware-software mismatch"** (from WaferLLM):
Show that existing software assumptions don't hold for new hardware.

## Design

### Length
2-3 pages (approximately 20-25% of the paper)

### Purpose
Present the system architecture, key mechanisms, and design rationale. The design section is the intellectual core of the paper.

### Structure

#### System Overview (first subsection)
- **Architecture diagram** (typically Figure 2 or 3)
- Component descriptions and their roles
- Data flow and control flow
- How components interact

#### Design Subsections (2-4 subsections, by component or mechanism)
Each subsection addresses one key design challenge:

1. **State the challenge**: What specific problem does this component solve?
2. **Present the approach**: How does the design address it?
3. **Justify trade-offs**: Why this approach over alternatives?
4. **Include algorithms**: Pseudocode or formal descriptions where they add clarity

### Design Principles

**Explain WHY, not just WHAT:**
```
Poor: "We use a hash table to store the mapping."
Better: "We use a hash table to store the mapping because lookups must complete
within the request processing budget of 10us. A tree-based index would add
O(log n) pointer chases, each incurring a cache miss."
```

**Discuss what you considered and rejected:**
```
"An alternative approach would be to [X]. However, this fails when [condition]
because [reason]. Instead, we [Y], which handles this case by [mechanism]."
```

**Address corner cases and failure modes:**
- What happens when a component fails?
- How does the system handle overload?
- What are the limitations of the design?

**Use precise systems terminology:**
- Consistency models (linearizable, sequentially consistent, eventually consistent)
- Failure modes (crash-stop, Byzantine, network partition)
- Performance characteristics (amortized, worst-case, expected)

### Architecture Diagrams
- Show components as labeled boxes
- Arrows indicate data flow (solid) and control flow (dashed)
- Label arrows with what flows between components
- Use color or shading to group related components
- Include a caption explaining the high-level flow

### Mathematical Formulations
- Use math when it adds precision (e.g., optimization objectives, complexity analysis)
- Do NOT use math for decoration
- Keep formulations simple and practical
- Always explain what each variable represents
- Systems papers use far less math than ML papers

## Implementation

### Length
0.5-1 page (approximately 5-8% of the paper)

### Purpose
Convince readers the system is real, usable, and reproducible. Provide details needed for artifact evaluation.

### Content

**What to include:**
- Total lines of code and programming language(s)
- Key libraries and frameworks used
- Operating system and hardware dependencies
- Integration points with existing systems
- Key implementation challenges and how they were solved
- Code availability (open-source URL)

```
Example from Tenplex:
"We implemented Tenplex in 6,700 lines of Go code. Tenplex integrates with
PyTorch, Megatron-LM, and DeepSpeed through a virtual file system layer..."

Example from WaferLLM:
"Our implementation consists of approximately 7,000 lines of CSL (Cerebras
Software Language) and 2,000 lines of Python..."

Example from KungFu:
"KungFu is implemented in [X] lines of Go and C++, with Python bindings for
integration with TensorFlow and PyTorch..."
```

### Tips
- Be specific about versions (Python 3.10, CUDA 12.1, PyTorch 2.1)
- Mention any non-obvious implementation decisions
- If the system is open-source, provide the URL
- Do not pad this section; keep it dense and factual

## Evaluation

### Length
2-3 pages (approximately 20-25% of the paper)

### Purpose
Demonstrate that the system works, achieves claimed benefits, and outperforms meaningful baselines. The evaluation must support every claim made in the introduction.

### Structure

#### Experimental Setup
- **Hardware**: Specific GPU models, CPU, memory, network (e.g., "8x NVIDIA A100 80GB GPUs, connected via NVLink, 200Gbps InfiniBand")
- **Software**: OS, driver versions, framework versions
- **Workloads**: Datasets, models, request patterns used
- **Baselines**: Systems compared against and their configurations
- **Metrics**: What is measured and how

#### End-to-End Results (Macrobenchmarks)
- Full system comparison against baselines
- Real-world or representative workloads
- Key metrics: throughput, latency, resource utilization
- Present the "headline numbers" that match introduction claims

#### Component Analysis (Microbenchmarks)
- Isolate individual component performance
- Show that each design decision contributes
- Measure specific operations in isolation

#### Ablation Studies
- Disable individual components to show their contribution
- "SystemName without X" vs "SystemName with X"
- Demonstrates that each contribution is necessary

#### Scalability
- Performance across different scales (number of GPUs, nodes, model sizes)
- Weak scaling and/or strong scaling experiments
- How the system behaves as load increases

#### Sensitivity Analysis (optional)
- Vary key parameters to show robustness
- Identify operating regions and limitations

### Systems-Specific Metrics

| Metric Category | Common Metrics |
|----------------|----------------|
| **Throughput** | Requests/sec, tokens/sec, ops/sec, MB/s, Gbps |
| **Latency** | p50, p95, p99, tail latency, time-to-first-token (TTFT) |
| **Resource utilization** | GPU utilization %, memory usage, network bandwidth |
| **Scalability** | Weak scaling efficiency, strong scaling speedup |
| **Cost** | Performance per dollar, energy per operation |
| **Availability** | Uptime, recovery time, failure handling overhead |

### Evaluation Figures
- **Bar charts**: Comparing systems on the same metric
- **Line plots**: Showing scaling behavior or trends over time
- **CDF plots**: Latency distributions (essential for tail latency analysis)
- **Heatmaps**: Parameter sensitivity or configuration exploration
- **Timeline charts**: Scheduling decisions, resource allocation over time
- **Stacked area/bar**: Resource breakdown by component
- **Throughput-latency curves**: System performance under varying load

### Common Evaluation Pitfalls
- Missing baselines (always compare against state-of-the-art)
- Unfair comparisons (using different hardware or configurations)
- Cherry-picked workloads that favor your system
- Missing error bars or confidence intervals on measurements
- Not reporting tail latency (p99) in addition to median
- Not explaining anomalies or unexpected results
- Claiming improvements without statistical significance

### Evaluation Writing Style
- Present results objectively: "SystemName achieves 2.3x higher throughput than Baseline"
- Explain WHY results look the way they do
- Acknowledge when baselines perform better in some scenarios
- Use consistent formatting for numbers (same decimal places, same units)

## Related Work

### Length
0.5-1 page (approximately 5-8% of the paper)

### Placement
**After evaluation.** This is a strong convention in systems papers, unlike ML papers where related work sometimes appears in the introduction. Placing related work after evaluation means readers already understand your system and results, making comparisons more meaningful.

### Structure
Organize by category/approach, NOT chronologically. Typical structure:

```
## Related Work

**Category 1: [Approach type].**
System A [1] does X. System B [2] extends this by Y. Unlike these systems,
[SystemName] addresses Z through [different approach].

**Category 2: [Different approach type].**
Recent work on [topic] includes C [3] and D [4]. These systems focus on
[aspect], while [SystemName] targets [different aspect].

**Category 3: [Broader area].**
[SystemName] builds on ideas from [area], particularly [specific technique]
from [5]. However, applying this technique to [our domain] requires [adaptation].
```

### Writing Style for Related Work
- Dense, citation-heavy paragraphs
- **Differentiate, don't just describe**: Always explain how your work differs
- Be fair to prior work (reviewers may be authors of cited work)
- Use present tense for describing what systems do: "System A uses..."
- 2-4 topical subsections or paragraph groups
- Cite 30-50 references total across the paper

### Common Mistakes
- Describing prior work without differentiating
- Being dismissive of prior work ("X is naive")
- Missing important related systems (reviewers will notice)
- Spending too much space on tangentially related work

## Conclusion

### Length
0.25-0.5 pages (approximately 2-4% of the paper)

### Content
- Brief summary of the system and its key contribution
- Restate the most important evaluation results
- Optional: 1-2 sentences on future work directions
- NO new information

### Example Pattern
```
We presented [SystemName], a [description] that [achieves goal]. Through
[key technique], [SystemName] achieves [main result] compared to [baseline].
Our evaluation on [workloads] demonstrates [claim]. [SystemName] is available
at [URL].
```

### Tips
- Keep it short (1-2 paragraphs)
- Do not repeat the abstract
- Do not introduce new claims
- End confidently but not with hype

## Artifact Evaluation

### Overview
Systems conferences (OSDI, SOSP, SIGCOMM, NSDI) increasingly require or strongly encourage artifact evaluation. Preparing a good artifact significantly strengthens the paper.

### What to Prepare
- **Source code**: Complete, buildable, with README
- **Build instructions**: Step-by-step, tested on a clean environment
- **Experiment scripts**: Automate all experiments from the paper
- **Expected output**: What results should look like
- **Hardware requirements**: Specify minimum and recommended configurations
- **Running time estimates**: How long each experiment takes

### Artifact Badges
- **Available**: Artifact is publicly accessible (e.g., GitHub, Zenodo)
- **Functional**: Artifact builds, runs, and produces results
- **Reproduced**: Independent evaluation confirms the paper's claims

### Tips
- Start artifact preparation DURING paper writing, not after
- Use Docker/containers for reproducible environments
- Include a `README.md` with quick-start instructions
- Provide both full experiments and quick "smoke test" versions
- Document known limitations and platform-specific issues

## Section Length Proportions

For a 12-14 page systems conference paper:

| Section | Pages | Percentage |
|---------|-------|------------|
| Introduction | 1.5-2 | 12-15% |
| Background/Motivation | 1-2 | 8-15% |
| Design | 2-3 | 20-25% |
| Implementation | 0.5-1 | 5-8% |
| Evaluation | 2-3 | 20-25% |
| Related Work | 0.5-1 | 5-8% |
| Conclusion | 0.25-0.5 | 2-4% |

Design and Evaluation together should occupy approximately 50% of the paper.

## Venue-Specific Variations

### OSDI / NSDI (USENIX)
- **Format**: USENIX LaTeX template
- **Pages**: 12 pages (excluding references)
- **Review**: Single-blind (typically)
- **Artifact evaluation**: Strongly encouraged
- **Style**: Practical systems focus, emphasis on real-world impact

### SIGCOMM (ACM)
- **Format**: ACM sigconf template
- **Pages**: 12 pages (excluding references)
- **Review**: Double-blind
- **Artifact evaluation**: Encouraged
- **Style**: Networking focus, may include formal models or protocol descriptions
- **Note**: Double-blind requires anonymizing system names and URLs in submission

### MOBICOM (ACM)
- **Format**: ACM sigconf template
- **Pages**: 15 pages (excluding references)
- **Review**: Double-blind
- **Style**: Mobile/wireless focus, often includes hardware prototypes
- **Note**: May require video demonstrations for hardware systems

### SOSP (ACM)
- **Format**: ACM sigconf template
- **Pages**: 15 pages (excluding references)
- **Review**: Double-blind
- **Style**: Systems focus, emphasis on novel abstractions and long-term impact

## Double-Blind Review Considerations

For venues requiring double-blind review (SIGCOMM, MOBICOM, SOSP):

- Replace system name with a placeholder in submission (e.g., "OurSystem")
- Remove repository URLs (add "available upon acceptance")
- Avoid institution-identifying statements
- Use "we" but do not mention specific labs, grants, or collaborators by name
- Do not self-cite in a way that reveals identity (cite own work in third person)
- Remove acknowledgments section from submission version

## Verb Tense Guide for Systems Papers

| Section | Primary Tense | Examples |
|---------|---------------|----------|
| Abstract - Problem | Present | "Serving LLMs requires..." |
| Abstract - What we did | Past/Present | "We present / We designed" |
| Abstract - Results | Past | "achieved 2.3x speedup" |
| Introduction - Context | Present | "Models continue to grow..." |
| Introduction - This work | Present | "We present SystemName" |
| Introduction - Contributions | Past + Present | "We identified... We design..." |
| Background - Facts | Present | "GPUs use shared memory..." |
| Background - Measurements | Past | "We measured... We observed..." |
| Design - System description | Present | "SystemName uses... The scheduler assigns..." |
| Implementation | Past | "We implemented... We integrated..." |
| Evaluation - Setup | Past | "We ran experiments on..." |
| Evaluation - Results | Past | "SystemName achieved..." |
| Evaluation - Interpretation | Present | "This shows that..." |
| Related Work | Present | "System A uses... System B supports..." |
| Conclusion | Past + Present | "We presented... SystemName achieves..." |

## Writing the Paper: Recommended Order

Unlike journal papers, systems papers are best written in this order:

1. **Design section + architecture figures** (the intellectual core)
2. **Evaluation section + result figures** (proves the design works)
3. **Introduction** (now you know what you built and what it achieves)
4. **Background/Motivation** (the setup for the design)
5. **Implementation** (straightforward factual section)
6. **Related Work** (position against the field)
7. **Conclusion** (summarize)
8. **Abstract** (compress the whole story)
9. **Title** (capture the essence)

### Why This Order Works
- Design + Evaluation are the substance; write these while results are fresh
- The Introduction is easier to write once you know the full story
- The Abstract should be the last thing written, as it must faithfully represent the paper
