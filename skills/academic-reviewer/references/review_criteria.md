# Review Criteria for Systems Conference Papers

This reference defines the seven evaluation dimensions, venue-specific review priorities, and scoring calibration used when reviewing papers for OSDI, NSDI, SIGCOMM, MOBICOM, and SOSP.

---

## 1. Seven Evaluation Dimensions

### 1.1 Novelty and Originality

**Core Question**: Does this paper present new ideas, or is it an incremental variation of existing work?

**What to assess:**
- Does the paper identify a new problem, or provide a fundamentally new approach to an existing problem?
- Is there a clear "key insight" — a technical observation that enables the design and was not obvious beforehand?
- Would a knowledgeable researcher in this area say "I hadn't thought of that" or "that's an interesting way to look at it"?
- Does the system combine existing ideas in a way that creates emergent value beyond the individual parts?

**Scoring rubric:**
| Score | Description |
|-------|-------------|
| 5 | Introduces a fundamentally new abstraction, technique, or way of thinking about the problem. Changes how the community approaches this area. |
| 4 | Presents a clearly new approach with a non-obvious key insight. Experienced researchers would find it surprising and interesting. |
| 3 | Offers some new ideas, but the approach is partially anticipated by prior work. Insight is real but modest. |
| 2 | Mostly combines known techniques. The main ideas exist in prior work, though the particular combination is new. |
| 1 | Straightforward application of existing approaches. No discernible new insight. |

**Red flags:**
- The paper's design is a direct instantiation of a well-known pattern with no adaptation
- The "key insight" is actually a well-known observation in the area
- The system is essentially a re-implementation of an existing system with minor parameter changes
- The paper reads like engineering documentation rather than research

**Positive signals:**
- The authors articulate a clear tension or trade-off that prior work ignores
- The design reveals a surprising property of the problem space
- The approach is counterintuitive but well-justified
- The paper opens up a new design space for future work

### 1.2 Technical Soundness

**Core Question**: Is the system design correct, and are the technical claims supported by sound reasoning?

**What to assess:**
- Are the design choices internally consistent? Do different components of the system interact correctly?
- Are the assumptions stated explicitly? Are they reasonable for the target deployment?
- Does the system handle edge cases, failure modes, and adversarial conditions?
- Are the algorithms and protocols correct? Could a formal argument or proof sketch be constructed?
- Does the theoretical analysis (if any) match the system behavior?

**Scoring rubric:**
| Score | Description |
|-------|-------------|
| 5 | Design is rigorous and complete. All assumptions are explicit and justified. Failure modes are addressed systematically. No detectable correctness issues. |
| 4 | Design is sound with minor gaps. Assumptions are mostly explicit. Main failure modes are addressed. Any remaining issues are non-critical. |
| 3 | Design is generally reasonable but has notable gaps. Some assumptions are hidden. Important edge cases or failure modes are unaddressed. |
| 2 | Design has significant technical issues. Key assumptions are unjustified or unstated. Important correctness concerns exist. |
| 1 | Design is fundamentally flawed. Core mechanisms are incorrect or the system cannot work as described. |

**What to check specifically:**
- Consistency between the threat model and the design (e.g., claiming fault tolerance but not handling network partitions)
- Hidden assumptions about workload characteristics, hardware capabilities, or deployment environment
- Race conditions, deadlocks, or ordering issues in concurrent/distributed designs
- Whether optimizations break correctness guarantees
- Whether the formal model (if any) matches the actual implementation

### 1.3 Significance and Impact

**Core Question**: If this paper is correct, how much does it matter to the community and to practitioners?

**What to assess:**
- Does this paper address a problem that real systems face at scale?
- Would practitioners adopt this approach? What is the deployment barrier?
- Does the paper advance the state of the art meaningfully (not just incrementally)?
- Does the work open new research directions or enable new applications?
- Is the improvement large enough to justify the added complexity?

**Scoring rubric:**
| Score | Description |
|-------|-------------|
| 5 | Addresses a critical, widely-felt problem. Results would change how practitioners build systems. Opens significant new research directions. |
| 4 | Addresses an important problem. Results are useful to a substantial portion of the community. Clear practical or research implications. |
| 3 | Addresses a real problem but with limited scope. Improvements are meaningful but not transformative. Moderate community interest expected. |
| 2 | Problem is real but niche, or the improvement is too small to justify adoption. Limited impact beyond the specific setting studied. |
| 1 | Problem is artificial or already well-solved. Results have no clear path to impact. |

**Context-dependent assessment:**
- A 10% improvement on a widely-deployed system may matter more than a 10x improvement on a toy benchmark
- Simplicity and deployability can be as important as raw performance
- Impact on downstream research counts: does this paper enable others to build better systems?

### 1.4 Evaluation Quality

**Core Question**: Does the experimental evaluation convincingly support the paper's claims?

This is the **most common area of weakness** in systems paper submissions. Evaluate rigorously.

**What to assess:**
- Does every claim in the introduction have corresponding experimental support?
- Are the baselines appropriate, up-to-date, and fairly configured?
- Are the workloads representative of real-world use cases?
- Are the metrics appropriate for the claims being made?
- Is the experimental methodology sound (sufficient trials, error reporting, controlled variables)?
- Are ablation studies present to isolate the contribution of each design component?

**Scoring rubric:**
| Score | Description |
|-------|-------------|
| 5 | Comprehensive evaluation covering all claims. Strong baselines, realistic workloads, proper methodology. Ablation studies isolate each contribution. Results are compelling and reproducible. |
| 4 | Good evaluation covering most claims. Reasonable baselines and workloads. Minor gaps in methodology. Ablation covers main components. Results are convincing. |
| 3 | Adequate evaluation but with notable gaps. Some claims lack experimental support. Baselines may be outdated or improperly configured. Limited ablation. |
| 2 | Weak evaluation. Major claims unsupported. Baselines are missing, unfair, or stale. Workloads are unrealistic. No ablation. Methodology has significant issues. |
| 1 | Evaluation is insufficient to draw any conclusions. Missing critical baselines, toy workloads only, or results contradict claims. |

**Specific checks:**
- **Baselines**: Are they the current state of the art? Are they configured with recommended settings? Was the baseline code obtained from the original authors or is it a re-implementation?
- **Workloads**: Do they cover diverse scenarios (read-heavy, write-heavy, mixed)? Do they include real-world traces or only synthetic benchmarks?
- **Metrics**: Are they measuring the right thing? (e.g., throughput alone is insufficient if latency matters; mean latency alone is insufficient if tail latency matters)
- **Statistical rigor**: Are error bars or confidence intervals reported? How many trials were run? Is variance acknowledged?
- **Scale**: Is the evaluation at a realistic scale for the target deployment?
- **Ablation**: Can you tell which design decisions contribute how much to the overall improvement?
- **Claims-evaluation alignment**: Map each numbered contribution to specific experiments. Flag any unsupported claims.

### 1.5 Presentation and Clarity

**Core Question**: Is the paper well-written, well-organized, and easy to follow?

**What to assess:**
- Can a researcher in the area understand the main ideas on a single read-through?
- Is the paper organized logically? Does information appear where you expect it?
- Are figures and tables clear, well-captioned, and effectively used?
- Is terminology consistent throughout?
- Is the writing concise and precise, or is it verbose and vague?

**Scoring rubric:**
| Score | Description |
|-------|-------------|
| 5 | Exceptionally well-written. Clear, concise, and engaging. Excellent figures. A pleasure to read. |
| 4 | Well-written with minor issues. Organization is logical. Figures are effective. Minor editorial improvements possible. |
| 3 | Adequate writing but some sections are unclear or poorly organized. Figures could be improved. Noticeable editorial issues. |
| 2 | Writing quality significantly hinders understanding. Major organizational problems. Figures are confusing or missing. |
| 1 | Paper is very difficult to understand. Poor writing, disorganized structure, and inadequate figures make it hard to evaluate the technical contribution. |

**Key presentation issues to flag:**
- Forward references to undefined concepts
- Missing or unclear threat model / system model
- Figures that require extensive text explanation to understand
- Inconsistent terminology (using different terms for the same concept)
- Buried key ideas (e.g., the main insight appears on page 8 instead of page 2)
- Excessive use of passive voice obscuring who did what
- Claims without quantification ("significant improvement" instead of "2.3x speedup")

### 1.6 Relevance

**Core Question**: Is this paper appropriate for this specific venue?

**What to assess:**
- Does the paper address problems that the venue's community cares about?
- Does the paper make systems contributions (as opposed to purely algorithmic, theoretical, or application-level contributions)?
- Is the paper positioned correctly relative to the venue's scope?

**Venue fit assessment:**

| Venue | Core Scope | Boundary Areas | Out of Scope |
|-------|-----------|---------------|-------------|
| OSDI | OS, distributed systems, storage, networking, security, ML systems | Programming languages for systems, hardware-software co-design | Pure algorithms, pure ML, pure security/crypto |
| NSDI | Networked systems design, deployment, management | Cloud infrastructure, CDNs, datacenter networks | Pure networking theory, pure routing protocols |
| SIGCOMM | Network architecture, protocols, algorithms, measurement, applications | Networked systems, programmable networks | Pure systems without networking contribution |
| MOBICOM | Mobile computing, wireless networking, sensing, IoT | Edge computing, mobile ML | Pure cloud systems, wired networking |
| SOSP | Operating systems, distributed systems, storage, networking | Systems security, systems for ML | Pure algorithms, pure applications |

**Note**: A paper can be excellent but still a poor fit for a specific venue. Flag this clearly but do not penalize the technical quality — instead suggest a better venue.

### 1.7 Reproducibility

**Core Question**: Could another researcher reproduce the key results of this paper?

**What to assess:**
- Is the system implementation described in sufficient detail?
- Are the experimental setup and methodology documented precisely?
- Is the source code available (or will it be)?
- Are the benchmarks, workloads, and datasets accessible?
- Are hardware requirements and configurations specified?

**Scoring rubric:**
| Score | Description |
|-------|-------------|
| 5 | Open-source implementation, public datasets, detailed methodology. Artifact evaluation passed. Another group could reproduce results in a few days. |
| 4 | Code available or promised. Most methodology details present. Workloads are standard or well-described. Minor gaps that could be filled by contacting authors. |
| 3 | Some implementation details provided. Methodology is partially described. Key configuration details missing. Reproduction would require significant effort. |
| 2 | Minimal implementation details. Methodology has major gaps. No code availability mentioned. Reproduction would be very difficult. |
| 1 | Insufficient detail to understand what was implemented, let alone reproduce it. |

**Specific checks:**
- LOC, programming languages, libraries, and versions
- Hardware specifications (CPU model, GPU model, memory, network, storage)
- Software environment (OS, kernel version, compiler flags, runtime settings)
- Workload parameters and generation methodology
- Duration of experiments and warm-up procedures
- Whether artifact evaluation is planned or completed

---

## 2. Venue-Specific Review Priorities

Different venues weight the evaluation dimensions differently, shaped by their communities and review cultures.

### 2.1 OSDI (USENIX Symposium on Operating Systems Design and Implementation)

**Review philosophy**: "Exciting papers over boring papers." The PC actively looks for work that will spark discussion and inspire new research directions.

**Priority weights:**
1. **Novelty** (high) — New abstractions, surprising approaches, and paradigm shifts are highly valued
2. **Technical Soundness** (high) — Must be correct, but the PC will tolerate some roughness if the ideas are exciting
3. **Significance** (high) — Must address a problem that matters to the broad systems community
4. **Evaluation** (medium-high) — Must be convincing, but "exciting and imperfect" may beat "boring and thorough"
5. **Presentation** (medium) — Should be clear, but a well-motivated rough paper may survive
6. **Relevance** (medium) — Broad scope; most systems topics welcome
7. **Reproducibility** (medium) — Artifact evaluation strongly encouraged

**Key signals for OSDI reviewers:**
- Would you enthusiastically advocate for this paper in the PC meeting?
- Does the paper teach you something you didn't know?
- Will this paper still be cited in 5-10 years?
- Is there a "wow" moment in the design or results?

**Common rejection patterns at OSDI:**
- Incremental improvements to known systems (even if well-evaluated)
- Systems papers that are really just benchmarking studies
- Papers where the design is obvious given the problem statement

**Scoring adjustment guidance for OSDI:**

| Dimension | Scoring Adjustment |
|-----------|-------------------|
| Novelty ≤ 2 | Cap Overall Merit at 3 regardless of other dimensions. OSDI requires a clear new idea. |
| Technical Soundness ≤ 2 | Cap Overall Merit at 2. Fundamental correctness issues are disqualifying. |
| Significance ≤ 2 | Cap Overall Merit at 3. The problem must matter to the broad community. |
| Evaluation ≤ 2 | Cap Overall Merit at 3, unless novelty is 5 (exceptional ideas may survive weak evaluation if fixable). |
| Presentation ≤ 2 | Reduce Overall Merit by 1 if the writing obscures an otherwise good contribution. |
| Novelty = 5, Evaluation = 3 | Overall Merit can still reach 4. OSDI tolerates evaluation gaps for truly exciting ideas. |
| All dimensions = 3 | Overall Merit = 3 at best. A uniformly "okay" paper lacks the excitement OSDI seeks. |

### 2.2 NSDI (USENIX Symposium on Networked Systems Design and Implementation)

**Review philosophy**: Values systems that are deployed or deployable. Real-world impact and practical considerations matter significantly.

**Priority weights:**
1. **Significance** (high) — Deployment value is a first-class criterion
2. **Evaluation** (high) — Must include realistic workloads; production traces strongly preferred
3. **Technical Soundness** (high) — Deployed systems must be correct
4. **Novelty** (medium-high) — New ideas valued but practical novelty (deployment insights, operational lessons) counts too
5. **Presentation** (medium) — Clear communication of deployment context is important
6. **Relevance** (medium-high) — Must have a clear networking/networked-systems angle
7. **Reproducibility** (medium) — Production systems may have limitations here

**Key signals for NSDI reviewers:**
- Could this system be deployed in a real network/datacenter?
- Does the evaluation use realistic traffic patterns and workloads?
- Does the paper provide operational insights beyond the specific system?
- Is there a one-shot revision (OSR) path if the paper is close?

**NSDI-specific considerations:**
- Papers describing deployed systems get extra credit for production experience
- Measurement papers must provide new insights, not just data
- The OSR process means borderline papers may get a conditional accept

**Scoring adjustment guidance for NSDI:**

| Dimension | Scoring Adjustment |
|-----------|-------------------|
| Significance ≤ 2 | Cap Overall Merit at 2. NSDI prioritizes real-world deployment value above all. |
| Evaluation ≤ 2 | Cap Overall Merit at 2. Unconvincing evaluation is disqualifying at NSDI. |
| Novelty = 2, Significance = 5 | Overall Merit can reach 4. NSDI values deployment insights even with modest technical novelty. |
| Evaluation = 5 (production data), Novelty = 3 | Overall Merit can reach 4. Thorough production evaluation compensates for incremental novelty. |
| Relevance ≤ 2 | Cap Overall Merit at 2. The networked-systems angle must be clear. |
| Technical Soundness ≤ 2 | Cap Overall Merit at 2. Deployed systems must be correct. |
| Presentation ≤ 2 | Reduce Overall Merit by 1. Deployment context must be communicated clearly. |

### 2.3 SIGCOMM (ACM Conference on Data Communication)

**Review philosophy**: "Lasting impact on the field." SIGCOMM has a high bar and values work that fundamentally advances networking. Acceptance rate is typically ~15%.

**Priority weights:**
1. **Novelty** (very high) — Must advance the state of the art substantially
2. **Significance** (very high) — Must have potential for lasting impact
3. **Technical Soundness** (high) — Rigorous networking analysis expected
4. **Evaluation** (high) — Must be thorough, especially for protocol and algorithm claims
5. **Presentation** (medium-high) — SIGCOMM papers are expected to be well-polished
6. **Relevance** (high) — Must make a clear networking contribution
7. **Reproducibility** (medium) — Valued but not always feasible for ISP/datacenter-scale work

**SIGCOMM scoring convention:**
- Scores of 3 or higher (on a 1-5 scale) generally indicate the paper is acceptable
- A paper needs strong advocate(s) to be accepted — lukewarm support is insufficient
- The PC discussion is a critical stage; champion your paper or flag concerns clearly

**Key signals for SIGCOMM reviewers:**
- Does this change how we think about a networking problem?
- Would this work influence protocol design, network architecture, or operational practice?
- Is the networking contribution clear and substantial (not just a systems paper that uses a network)?

**Scoring adjustment guidance for SIGCOMM:**

| Dimension | Scoring Adjustment |
|-----------|-------------------|
| Novelty ≤ 2 | Cap Overall Merit at 2. SIGCOMM demands substantial advancement. |
| Significance ≤ 2 | Cap Overall Merit at 2. Lasting impact potential is essential. |
| Novelty = 3, Significance = 3 | Cap Overall Merit at 3. Both must be strong for acceptance at ~15% rate. |
| Evaluation ≤ 2 | Cap Overall Merit at 2. Protocol and algorithm claims need rigorous validation. |
| Relevance ≤ 2 | Cap Overall Merit at 2. A non-networking paper cannot be accepted regardless of quality. |
| Presentation ≤ 2 | Cap Overall Merit at 3. SIGCOMM expects polished papers but won't reject solely on writing. |
| Novelty = 5, Evaluation = 3 | Overall Merit can reach 4, but needs a champion on the PC to survive discussion. |

### 2.4 MOBICOM (ACM International Conference on Mobile Computing and Networking)

**Review philosophy**: Values systems that work in the real, messy physical world. Wireless and mobile-specific rigor is essential.

**Priority weights:**
1. **Technical Soundness** (very high) — Wireless/mobile systems require extreme rigor due to environmental variability
2. **Evaluation** (very high) — Must include real-world experiments, not just simulation
3. **Novelty** (high) — New approaches to mobile/wireless challenges
4. **Significance** (high) — Must address real mobile computing challenges
5. **Relevance** (high) — Must have a clear mobile/wireless/sensing contribution
6. **Presentation** (medium) — Should clearly explain the physical-layer or mobile-specific challenges
7. **Reproducibility** (medium) — Environmental conditions make exact reproduction hard; methodology clarity is key

**MOBICOM-specific evaluation requirements:**
- Real-world wireless experiments are strongly preferred over simulation alone
- Multiple environments and conditions must be tested
- Signal-level analysis (SNR, channel conditions, interference) is expected where relevant
- Battery life and resource consumption on mobile devices should be addressed
- Mobility scenarios (walking, driving, stationary) where applicable

**Common MOBICOM pitfalls:**
- Simulation-only evaluation for a system intended for real deployment
- Testing only in controlled lab environments (anechoic chamber results alone are insufficient)
- Ignoring the impact of environmental variability (multipath, interference, user mobility)
- Not comparing against physical-layer baselines

**Wireless-specific evaluation criteria:**

| Criterion | What to Check | Why It Matters |
|-----------|--------------|----------------|
| **SNR analysis** | Does the paper characterize performance across a range of SNR values? Are results reported at both high-SNR (>20 dB) and low-SNR (<10 dB) regimes? | A system that works only at high SNR is impractical for real mobile environments where signal quality varies constantly. |
| **Multi-environment testing** | Were experiments conducted in at least 3 distinct environments (e.g., indoor office, outdoor urban, indoor home)? Do environments vary in multipath, interference, and line-of-sight conditions? | Wireless channel characteristics vary dramatically across environments. Single-environment results do not generalize. |
| **Mobility scenarios** | Does the evaluation cover stationary, walking (~1.5 m/s), and vehicular (~30 m/s) mobility? Is Doppler shift addressed for high-speed scenarios? | Mobile systems must handle varying channel coherence times. A system tested only while stationary may fail with mobility. |
| **Interference resilience** | Is performance measured under co-channel and adjacent-channel interference? Are results shown with realistic numbers of competing devices? | Real deployments feature dense, uncontrolled interference from other devices and networks. |
| **Power consumption** | Is energy consumption measured on actual mobile hardware? Is battery life impact quantified for sustained operation? | Mobile devices are energy-constrained. A system that drains the battery in 2 hours is impractical regardless of performance. |
| **Hardware diversity** | Is the system tested on multiple chipsets or device types? Are results reproducible across different hardware platforms? | Wireless hardware varies significantly; results on a single SDR may not transfer to commodity devices. |

**Scoring adjustment guidance for MOBICOM:**

| Dimension | Scoring Adjustment |
|-----------|-------------------|
| Technical Soundness ≤ 2 | Cap Overall Merit at 1. Wireless/mobile rigor is non-negotiable. |
| Evaluation ≤ 2 | Cap Overall Merit at 2. Real-world experiments are essential. |
| Evaluation = simulation-only | Cap Overall Merit at 2 even if simulation is thorough. MOBICOM requires real-world validation. |
| Novelty ≤ 2 | Cap Overall Merit at 3. Modest novelty can survive if execution is exceptional. |
| Relevance ≤ 2 | Cap Overall Merit at 2. The mobile/wireless contribution must be clear. |
| Single-environment evaluation | Reduce Overall Merit by 1. Multi-environment testing is a community norm. |
| No power/energy analysis | Reduce Overall Merit by 0.5 for mobile-device systems. Not required for infrastructure-side work. |

### 2.5 SOSP (ACM Symposium on Operating Systems Principles)

**Review philosophy**: "Novel abstractions and real systems." SOSP has the highest bar among systems venues. Papers must present new ideas AND demonstrate them in real systems.

**Priority weights:**
1. **Novelty** (very high) — Must present genuinely new abstractions or principles
2. **Technical Soundness** (very high) — Must be rigorous and thorough
3. **Significance** (very high) — Must have broad impact on how systems are built
4. **Evaluation** (high) — Must demonstrate the ideas work in a real, substantial system
5. **Presentation** (high) — SOSP papers are expected to be well-crafted
6. **Relevance** (high) — Must contribute to operating systems principles (broadly defined)
7. **Reproducibility** (high) — Artifact evaluation is required

**Key signals for SOSP reviewers:**
- Does this paper introduce a new abstraction that others will build on?
- Is there a real, working system (not just a prototype or simulation)?
- Would this paper be relevant 10+ years from now?
- Does the paper advance our understanding of systems principles, not just systems performance?

**SOSP-specific requirements:**
- Artifact evaluation is mandatory — the system must work
- The paper must go beyond "we built a faster X" to "we discovered principle Y that enables faster X"
- Implementation must be substantial enough to validate the design

**Scoring adjustment guidance for SOSP:**

| Dimension | Scoring Adjustment |
|-----------|-------------------|
| Novelty ≤ 2 | Cap Overall Merit at 2. SOSP demands genuinely new abstractions or principles. |
| Technical Soundness ≤ 2 | Cap Overall Merit at 2. Rigorous and thorough technical work is required. |
| Significance ≤ 2 | Cap Overall Merit at 2. Broad systems impact is essential. |
| Evaluation = simulation-only | Cap Overall Merit at 2. A real, working system is required. |
| Reproducibility ≤ 2 | Cap Overall Merit at 3. Artifact evaluation is mandatory. |
| Presentation ≤ 2 | Cap Overall Merit at 3. SOSP papers should be well-crafted. |
| Novelty = 5, all others ≥ 3 | Overall Merit can reach 5. A breakthrough abstraction defines the best SOSP papers. |
| All dimensions = 3 | Cap Overall Merit at 2. SOSP's bar requires excellence, not adequacy. |

---

## 3. Scoring Calibration

### Overall Merit Scale (1-5)

Use this calibration to assign scores consistently. Remember that top systems venues accept ~15-20% of submissions.

| Score | Label | What It Means | Accept? |
|-------|-------|---------------|---------|
| **5** | Strong Accept | Excellent paper that makes a significant contribution. Would be among the best papers at the conference. You would champion this paper in the PC meeting. Clear accept. | Yes |
| **4** | Accept | Good paper with a solid contribution. Above the acceptance bar. Minor issues exist but do not undermine the contribution. You support acceptance. | Likely yes |
| **3** | Borderline | Paper has merit but also notable weaknesses. Could go either way. The contribution is real but may be insufficient for this venue, or execution has gaps. You could be convinced in either direction. | Maybe |
| **2** | Weak Reject | Paper has some merit but significant weaknesses outweigh strengths. Below the acceptance bar. Would need substantial revision. You lean against acceptance. | Likely no |
| **1** | Strong Reject | Paper has fundamental problems: flawed design, unsupported claims, or insufficient contribution. Not suitable for this venue even with major revision. | No |

### Calibration Guidelines

**Anchoring to acceptance rate:**
- At ~15-20% acceptance, a score of 3 is NOT a recommendation to accept — it means "I could be convinced either way"
- Most accepted papers should receive scores of 4 or 5 from at least one reviewer
- A paper with all 3s is typically rejected unless discussion reveals hidden strengths

**Score distribution guidance:**
- Do not cluster all scores at 3 — differentiate between papers
- Reserve 5s for genuinely excellent work (top 5-10% of submissions you review)
- Use the full range: a clearly flawed paper should get a 1 or 2, not a generous 3
- Your scores should roughly match the acceptance rate: ~15-20% of papers you review should receive 4 or higher

**Expected score distribution across a review batch:**

If you review 20 papers at a top systems venue (~15-20% acceptance rate), your scores should approximately distribute as follows:

| Score | Expected Count | Fraction | Description |
|-------|---------------|----------|-------------|
| 5 (Strong Accept) | 1-2 papers | ~5-10% | Genuinely excellent, would champion at PC meeting |
| 4 (Accept) | 2-3 papers | ~10-15% | Solid contributions above the bar |
| 3 (Borderline) | 4-5 papers | ~20-25% | Real merit but uncertain — need PC discussion |
| 2 (Weak Reject) | 6-7 papers | ~30-35% | Some merit but significant problems |
| 1 (Strong Reject) | 4-5 papers | ~20-25% | Fundamental issues, clear reject |

If your distribution deviates significantly from this:
- **Too many 3s** (>30%): You are not differentiating enough. Re-examine your borderline papers and push them toward 2 or 4.
- **Too many 4s and 5s** (>30%): You are being too generous. At 15-20% acceptance, most papers should be below the bar.
- **Too many 1s** (>30%): You may be too harsh, or you may have a particularly weak batch. Compare notes with co-reviewers.
- **No 5s at all**: Reconsider whether any paper in your batch is genuinely excellent. Being stingy with 5s can prevent strong papers from being championed.

**Score-text consistency:**
- A score of 4 or 5 should have enthusiastic language in the review: "important contribution," "well-executed," "I strongly support acceptance"
- A score of 3 should have balanced language: "interesting but..." "promising approach, however..."
- A score of 1 or 2 should clearly state the problems: "fundamental flaw," "insufficient contribution," "evaluation does not support claims"
- Never give a high score with only negative comments, or a low score with only positive comments

### 3.2 Score Boundary Examples

These worked examples illustrate how to reason about borderline cases where the score could go either way.

**Boundary: Score 4 vs. Score 3 — "Is this above the bar?"**

*Example A: Strong system, modest novelty.*
A paper presents a well-engineered distributed key-value store that achieves 2x throughput over the state of the art through careful optimization of the I/O path. The evaluation is thorough (5 baselines, realistic workloads, ablation). However, the key techniques (adaptive batching, NUMA-aware allocation) are individually known. The combination is competent but unsurprising.
→ **Score 3.** The execution is excellent but the insight is modest. Ask: "Would an experienced systems engineer, given the same goal, arrive at a similar design?" If yes, the novelty bar for a score of 4 is not met. This paper might be accepted at a workshop or a second-tier venue.

*Example B: Novel insight, imperfect evaluation.*
A paper introduces a new scheduling abstraction for serverless functions that reduces cold-start latency by 10x. The insight (exploiting function dependency graphs for predictive warming) is genuinely new. However, the evaluation only covers two workloads and lacks a comparison with the most recent competing approach (published 6 months ago).
→ **Score 4.** The core insight is strong and the results are promising. The evaluation gaps are fixable (missing baseline can be added). The contribution passes the "would this change how people think?" test. Note the evaluation gaps clearly but do not let them override the novelty signal.

*Example C: Deployed system, incremental contribution.*
A paper from a major cloud provider describes optimizations to their production storage system, including a new compaction strategy that reduced tail latency by 30% at scale. The paper includes production metrics from a fleet of 10,000 nodes. The techniques are specific to their system architecture and may not generalize.
→ **Score 4 at NSDI** (deployment experience at scale is valued), **Score 3 at OSDI/SOSP** (lacks generalizable insight or new abstraction).

**Boundary: Score 3 vs. Score 2 — "Does this have enough merit to discuss?"**

*Example D: Reasonable paper, unconvincing evaluation.*
A paper proposes a new replication protocol that claims to reduce commit latency by 40%. The protocol design is reasonable but the evaluation compares only against Paxos (not recent variants like EPaxos, Compartmentalized Paxos). The workloads are synthetic and do not stress the protocol's claimed advantage (geo-distribution). Error bars are absent.
→ **Score 2.** The evaluation has too many gaps to support the claims. The comparison is unfair (outdated baseline), the workloads are unrealistic, and there is no statistical rigor. While the protocol idea has some merit, the paper does not provide enough evidence to make a case for acceptance.

*Example E: Good problem, flawed design.*
A paper addresses a real problem (scheduling ML training jobs on heterogeneous clusters) with a working system. However, the design has a fundamental limitation: it assumes jobs can be preempted and migrated at arbitrary points, which in practice requires checkpointing that adds significant overhead. The paper acknowledges this overhead in passing but does not measure it. The evaluation excludes checkpointing time from the latency measurements.
→ **Score 2.** The design's central assumption is questionable and the evaluation is misleading because it excludes a significant cost. The problem is real and the approach has promise, but the paper needs to confront the checkpointing overhead honestly and include it in all measurements.

### Reviewer Confidence Scale (1-4)

| Score | Label | What It Means |
|-------|-------|---------------|
| **4** | Expert | You are an expert in this specific topic. You have published in this area and are familiar with the state of the art. You are confident in your assessment. |
| **3** | Knowledgeable | You have good knowledge of this area. You have read many papers on this topic. You are fairly confident in your assessment but might miss some nuances. |
| **2** | Some familiarity | You have some familiarity with the area but are not an expert. You may not be aware of all relevant prior work. Your assessment of novelty may be less reliable. |
| **1** | Limited knowledge | You have limited knowledge of this area. Your review focuses on general aspects (writing quality, evaluation methodology) rather than domain-specific assessment. |

**When to adjust confidence:**
- Lower your confidence if the paper is at the boundary of your expertise
- Higher confidence is appropriate when you can cite specific prior work that the paper misses
- Be honest — stating low confidence is better than overconfident incorrect claims
- Confidence 2 or lower means you should flag areas where a more expert reviewer should weigh in

**Confidence and review scope**: A reviewer's confidence level determines not just the confidence field but the entire review character. Lower-confidence reviewers should constrain their assessment to dimensions they can evaluate and explicitly defer on others. For detailed per-level behavioral profiles including dimension coverage tables, language patterns, scoring behavior, and a worked four-review example, see `references/confidence_level_profiles.md`.
