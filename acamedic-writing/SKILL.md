---
name: acamedic-writing
description: "Write systems conference papers for OSDI, NSDI, SIGCOMM, and MOBICOM. Covers paper structure (Introduction, Background/Motivation, Design, Implementation, Evaluation, Related Work), systems writing style, IEEE/ACM citations, architecture diagrams, performance evaluation, and artifact preparation."
---

# Systems Conference Paper Writing

## Overview

Systems conference papers communicate the design, implementation, and evaluation of computer systems. They follow a problem-solution-evaluation structure: identify a real problem, build a system to solve it, and demonstrate its effectiveness through empirical evaluation. This skill covers writing for top systems venues including OSDI, NSDI, SIGCOMM, MOBICOM, and SOSP.

## When to Use This Skill

This skill should be used when:
- Writing or revising any section of a systems conference paper
- Structuring a paper using the standard systems format (Introduction, Background/Motivation, Design, Implementation, Evaluation, Related Work, Conclusion)
- Writing a problem-solution introduction with numbered contributions
- Creating motivation sections with measurement-driven evidence
- Describing system architecture and design trade-offs
- Writing evaluation sections with microbenchmarks, macrobenchmarks, and ablation studies
- Formatting citations in IEEE or ACM style
- Creating architecture diagrams, performance plots, and CDF figures
- Preparing artifacts for artifact evaluation
- Adapting a paper for a specific venue (OSDI vs SIGCOMM vs MOBICOM)
- Improving writing clarity, directness, and technical precision
- Addressing reviewer comments and revising systems papers

## Core Capabilities

### 1. Paper Structure and Organization

Systems conference papers follow a standardized structure:

| Section | Pages | Purpose |
|---------|-------|---------|
| Introduction | 1.5-2 | Problem, solution overview, contributions |
| Background/Motivation | 1-2 | Technical context, evidence the problem exists |
| Design | 2-3 | Architecture, mechanisms, trade-offs |
| Implementation | 0.5-1 | LOC, languages, frameworks, integration |
| Evaluation | 2-3 | Macrobenchmarks, microbenchmarks, ablation |
| Related Work | 0.5-1 | Differentiation from prior systems |
| Conclusion | 0.25-0.5 | Summary, no new information |

Design and Evaluation together should occupy approximately 50% of the paper.

For detailed guidance on each section, refer to `references/systems_paper_structure.md`.

### 2. Section-Specific Writing Guidance

**Title**: Follow the "SystemName: Descriptive Subtitle" pattern. Name the system. Be specific about the problem and approach.

**Abstract**: Unstructured narrative paragraph (150-250 words). Flow: problem context -> gap -> solution overview -> key quantitative results -> availability. Write this LAST.

**Introduction**: Problem-solution structure in 6-7 paragraphs:
1. Broad context with concrete numbers showing importance
2. Specific technical gap and why existing approaches fail
3. Solution overview with key insight
4. Numbered contributions (3-4) mapping to paper sections
5. Optional paper organization roadmap

**Background/Motivation**: Provide technical prerequisites, then DEMONSTRATE the problem with measurements, profiling, or workload analysis. This section must contain empirical evidence, not just assertions.

**Design**: Present architecture with diagrams. For each mechanism: state the challenge, present the approach, justify trade-offs. Explain WHY, not just WHAT.

**Implementation**: Lines of code, programming languages, library versions, framework integration. Be specific and factual.

**Evaluation**: Experimental setup (exact hardware, software, workloads, baselines), end-to-end results, component analysis, ablation studies, scalability experiments. Every claim in the introduction must be supported here.

**Related Work**: Placed AFTER evaluation. Organize by category/approach. Always differentiate ("Unlike X, our system does Y because Z").

**Conclusion**: Brief summary of system and key results. 1-2 paragraphs. No new information.

### 3. Writing Principles and Style

Apply fundamental writing principles adapted for systems conference papers. For detailed guidance, refer to `references/writing_principles.md`.

**Clarity**:
- Use precise, unambiguous technical language
- Define systems terms at first use (e.g., "Remote Direct Memory Access (RDMA)")
- Maintain logical flow within and between paragraphs
- Use active voice: "We design", "We implement", "We evaluate"

**Conciseness**:
- Eliminate filler words and phrases
- Favor direct statements over hedged ones
- Systems papers have strict page limits; every sentence must earn its space
- Average sentence length: 15-20 words

**Directness**:
- State claims confidently: "SystemName achieves 2.3x higher throughput"
- Avoid hype: do NOT use "novel", "groundbreaking", "revolutionary"
- Let the numbers speak: "3.5x speedup" is stronger than "significant improvement"
- Avoid excessive hedging in evaluation: "achieves" not "seems to achieve"

**Technical Precision**:
- Specify exact configurations (GPU models, memory sizes, network bandwidth)
- Report metrics consistently (same units, decimal places, measurement methodology)
- Distinguish between median and tail latency (p50 vs p99)
- Specify whether speedups are end-to-end or component-level

### 4. Citation and Reference Management

Systems papers use numbered citation styles. For comprehensive style guides, refer to `references/citation_styles.md`.

**Primary Citation Styles:**
- **IEEE**: Numbered citations in square brackets [1], common in USENIX venues (OSDI, NSDI)
- **ACM**: Numbered citations, used by SIGCOMM, MOBICOM, SOSP

**Systems-Specific Citation Practices:**
- Cite systems by name: "Borg [1]" not just "[1]"
- 30-50 references typical for a 12-page paper
- Cite recent work heavily (last 3-5 years for active areas)
- Always cite the systems you compare against in evaluation
- Use BibTeX with entries from DBLP or ACM Digital Library

### 5. Figures and Tables

Create effective visualizations for systems papers. For detailed best practices, refer to `references/figures_tables.md`.

**When to Use Tables vs. Figures:**
- **Tables**: Hardware configurations, benchmark results with exact numbers, feature comparisons across systems
- **Figures**: Performance trends, scaling behavior, latency distributions, architecture diagrams

**Common Figure Types in Systems Papers:**
- Architecture diagrams: System components, data flow, control flow
- Performance bar charts: Comparing systems on throughput or latency
- Scaling line plots: Performance vs. number of GPUs/nodes/clients
- CDF plots: Latency distribution analysis
- Timeline charts: Scheduling decisions, resource allocation
- Stacked bar/area: Resource breakdown by component

**Design Principles:**
- Make each figure/table self-explanatory with complete captions
- Bold the best result in comparison tables
- Include error bars or confidence intervals on measurements
- Use consistent colors and formatting across all figures
- 5-8 figures typical for a 12-page paper
- Figures should be readable in grayscale (for printing)

### 6. Systems-Specific Terminology

Use precise terminology appropriate to the systems subfield:

**Distributed Systems:**
- Consistency models: linearizable, sequentially consistent, eventually consistent, causal
- Fault tolerance: crash-stop, Byzantine, failover, replication, checkpointing
- Scalability: horizontal, vertical, weak scaling, strong scaling
- Coordination: consensus, leader election, distributed locking

**Networking (SIGCOMM, MOBICOM):**
- Bandwidth, throughput, goodput
- Round-trip time (RTT), flow completion time (FCT)
- Congestion control, flow scheduling, traffic engineering
- RDMA, DPDK, eBPF, programmable switches

**Operating Systems (OSDI, NSDI):**
- Scheduling: preemption, priority, fairness, work-stealing
- Memory: virtual memory, page tables, TLB, cache hierarchy
- Storage: block layer, file system, journaling, write-ahead log
- Virtualization: containers, VMs, hypervisor, paravirtualization

**ML Systems:**
- Training: data parallelism, model parallelism, pipeline parallelism, tensor parallelism
- Inference: batching, KV cache, prefill, decode, time-to-first-token (TTFT)
- Throughput: tokens/sec, samples/sec, FLOPS utilization
- Memory: activation memory, gradient memory, optimizer state

**Performance Metrics:**
- Throughput: requests/sec, tokens/sec, ops/sec, MB/s, Gbps
- Latency: p50, p95, p99, tail latency, jitter
- Utilization: GPU%, CPU%, memory%, network bandwidth%
- Efficiency: speedup, scaling efficiency, cost per operation

### 7. Venue-Specific Requirements

| Venue | Format | Pages | Review | Artifact Eval |
|-------|--------|-------|--------|---------------|
| OSDI | USENIX | 12 | Single-blind | Strongly encouraged |
| NSDI | USENIX | 12 | Single-blind | Encouraged |
| SIGCOMM | ACM sigconf | 12 | Double-blind | Encouraged |
| MOBICOM | ACM sigconf | 15 | Double-blind | Encouraged |
| SOSP | ACM sigconf | 15 | Double-blind | Required |

**Double-blind venues (SIGCOMM, MOBICOM, SOSP):**
- Anonymize system name in submission
- Remove repository URLs
- Cite own work in third person
- Remove acknowledgments

**USENIX venues (OSDI, NSDI):**
- Single-blind: authors are identified
- System name and URLs can be included
- Use USENIX LaTeX template

### 8. Common Pitfalls to Avoid

**Top Rejection Reasons for Systems Papers:**
1. "Not solving a real problem" - Weak motivation, no evidence the problem matters
2. "Not solving the problem" - System doesn't actually achieve what is claimed
3. "Paper too badly written" - Unclear prose obscures the contribution
4. "Insufficient contribution" - Incremental improvement over existing systems
5. Missing or unfair baselines in evaluation
6. Evaluation doesn't support the claims in the introduction
7. Design trade-offs not explained or justified
8. Related work incomplete (missing key systems)

**Writing Quality Issues:**
- Passive voice obscuring who did what ("it was observed" vs "we observed")
- Vague quantification ("significant improvement" vs "2.3x speedup")
- Overstated claims not supported by evaluation
- Inconsistent terminology for the same concept
- Forward references to undefined terms
- Prose table-of-contents abstracts instead of substantive abstracts

## Workflow for Systems Paper Development

**Stage 1: Planning**
1. Identify target venue and review page limits, deadlines, review type
2. Outline the system's key contributions (what is new?)
3. Plan the evaluation: what experiments prove the claims?
4. Sketch the architecture diagram and key result figures

**Stage 2: Drafting (recommended order)**
1. Design section + architecture figures (the core contribution)
2. Evaluation section + result figures (proof it works)
3. Introduction (now you know the full story)
4. Background/Motivation (setup for the design)
5. Implementation (factual, straightforward)
6. Related Work (position against the field)
7. Conclusion (summary)
8. Abstract (compress the whole story)
9. Title (capture the essence)

**Stage 3: Revision**
1. Verify every claim in the introduction is supported by evaluation
2. Check that all figures and tables are referenced in the text
3. Ensure consistent terminology throughout
4. Verify numbers match between text, tables, and figures
5. Check page limits and formatting requirements
6. Proofread for grammar, spelling, and clarity

**Stage 4: Final Preparation**
1. Format according to venue template (USENIX or ACM)
2. Prepare artifact (code, scripts, README, Docker)
3. Anonymize if double-blind venue
4. Check figure resolution and readability
5. Verify all references are complete and correctly formatted
6. Build from clean git checkout before submission

## References

This skill includes comprehensive reference files covering specific aspects of systems conference paper writing:

- `references/systems_paper_structure.md`: Detailed guide to systems paper structure, section-by-section content, venue variations, and writing order
- `references/citation_styles.md`: IEEE and ACM citation formats, BibTeX management, systems-specific citation conventions
- `references/figures_tables.md`: Architecture diagrams, performance plots, CDFs, evaluation tables, and visual design
- `references/writing_principles.md`: Core writing principles (clarity, conciseness, accuracy), systems-specific style, and revision checklists

Load these references as needed when working on specific aspects of systems paper writing.
