# Figures and Tables for Systems Conference Papers

## Overview

Figures and tables are essential components of systems papers, serving to display system architecture, performance results, and comparative evaluations. Effective visual displays enhance comprehension and provide evidence for the paper's claims. Systems papers typically contain 5-8 figures and 1-3 tables in a 12-page paper.

## When to Use Tables vs. Figures

### Use Tables When:
- Presenting exact numerical results across systems or configurations
- Comparing features or capabilities of multiple systems
- Showing hardware/software experimental setup details
- Displaying ablation study results with precise numbers
- Readers need to look up specific data points

**Example use cases:**
- Hardware configuration (GPU models, memory, network bandwidth)
- Benchmark comparison (system names as columns, metrics as rows)
- Ablation study results (components enabled/disabled)
- Feature comparison across related systems
- Workload characteristics (dataset sizes, request patterns)

### Use Figures When:
- Showing performance trends across scales or configurations
- Displaying latency distributions (CDFs)
- Illustrating system architecture or data flow
- Comparing throughput or latency across systems visually
- Showing scaling behavior (performance vs. number of nodes/GPUs)
- Displaying resource utilization over time

**Example use cases:**
- Architecture block diagrams
- Throughput bar charts comparing systems
- Scaling line plots (performance vs. GPU count)
- CDF plots for latency analysis (p50, p95, p99)
- Timeline charts for scheduling decisions
- Stacked area charts for resource breakdown
- Motivation plots showing performance bottlenecks

### General Decision Rule

**Can the information be conveyed in 1-2 sentences of text?**
- Yes: Use text only
- No, and precise values are needed: Use a table
- No, and patterns/trends are most important: Use a figure

## Core Design Principles

### 1. Self-Explanatory Display Items

**Each figure or table must stand alone without requiring the main text.**

**Essential elements:**
- Complete, descriptive caption
- All abbreviations defined (in caption or footnote)
- Units of measurement clearly indicated
- Axis labels with units
- Legend included (for figures with multiple data series)
- Error bars or confidence intervals explained

**Example of self-explanatory caption:**
```
Figure 5. End-to-end throughput (tokens/sec) of ServerlessLLM vs. baselines
on LLaMA-70B with varying request rates. Error bars show standard deviation
over 5 runs. ServerlessLLM achieves 2.3x higher throughput than vLLM at 100
req/s due to locality-aware checkpoint loading.
```

### 2. Avoid Redundancy

**Do not duplicate information between text, tables, and figures.**

```
Poor:
"ServerlessLLM achieves 15,200 tokens/sec on LLaMA-70B, while vLLM achieves
6,600 tokens/sec and TensorRT-LLM achieves 8,100 tokens/sec. [Also shown in
Figure 5]"

Better:
"ServerlessLLM achieves 2.3x higher throughput than vLLM on LLaMA-70B (Figure 5),
primarily due to locality-aware checkpoint loading."
```

**Key principle:** Text should highlight key findings and explain WHY results look the way they do, not repeat all numbers from figures.

### 3. Consistency

**Maintain uniform formatting across all display items:**
- Font types and sizes
- Color schemes (same color for same system across all figures)
- Terminology and abbreviations
- Axis labels and units
- Bar/line widths and marker styles

**Example of inconsistency to avoid:**
- Figure 3 uses blue for "ServerlessLLM" while Figure 5 uses green
- Figure 3 labels the y-axis "Throughput (tok/s)" while Figure 4 uses "Tokens per second"
- Table 1 reports latency in ms while Table 2 uses seconds

### 4. Optimal Quantity

**Systems papers typically have 5-8 figures and 1-3 tables in 12 pages.**

Distribution pattern:
- 1 architecture diagram
- 1-2 motivation figures (profiling, bottleneck analysis)
- 3-4 evaluation figures (end-to-end, microbenchmarks, scaling, ablation)
- 1-2 tables (experimental setup, benchmark comparison, ablation)

### 5. Clarity and Simplicity

- Use clear, readable fonts (minimum 8-10 pt at final size)
- Provide adequate spacing between elements
- Use high contrast for readability
- Remove unnecessary grid lines, borders, or decoration
- Maximize data-ink ratio (minimize non-data ink)
- Ensure all figures are readable when printed in grayscale

## Figure Types for Systems Papers

### Architecture Diagrams

**Best for:**
- Showing system components and their interactions
- Illustrating data flow and control flow
- Communicating the high-level design

**Design guidelines:**
- Components as labeled boxes or rounded rectangles
- Solid arrows for data flow, dashed arrows for control flow
- Label arrows with what flows between components
- Group related components with shading or borders
- Include a caption explaining the high-level flow
- Keep the level of abstraction consistent (don't mix high-level and low-level)

**Tools:**
- **TikZ/PGF** (LaTeX): Publication-quality, integrates with paper
- **draw.io/diagrams.net**: Free, collaborative, exports to PDF/SVG
- **Inkscape**: Free vector graphics editor
- **OmniGraffle** (macOS): Professional diagramming
- **Lucidchart**: Web-based collaborative diagramming

**Common patterns:**
```
[Client Layer]
    |  requests
    v
[Scheduler / Router]
    |         |
    v         v
[Worker 1] [Worker 2] ... [Worker N]
    |         |
    v         v
[Storage / Memory Layer]
```

**Tips:**
- Keep it simple; a reader should understand the system in 10 seconds
- Use consistent shapes for the same type of component
- Color-code subsystems but ensure grayscale readability
- Architecture diagram is typically Figure 1 or Figure 2

### Performance Bar Charts

**Best for:**
- Comparing systems on a single metric
- Showing benchmark results across workloads
- Displaying ablation study results

**Design guidelines:**
- Group bars by workload or configuration
- Use consistent colors: one color per system across all figures
- Include value labels above bars for exact numbers (when space permits)
- Start y-axis at zero
- Order bars consistently (our system last or first for easy comparison)
- Include error bars for repeated experiments

**Example:**
```
Throughput (tokens/sec) for LLaMA-70B inference:

ServerlessLLM  |████████████████████| 15,200
vLLM           |████████████|         6,600
TensorRT-LLM   |██████████████|       8,100
Triton          |███████████|          5,900
```

### Scaling Line Plots

**Best for:**
- Showing how performance changes with system scale
- Demonstrating weak or strong scaling
- Comparing scaling behavior across systems

**Design guidelines:**
- X-axis: scale factor (number of GPUs, nodes, workers, model size)
- Y-axis: performance metric (throughput, latency, speedup)
- Use different line styles AND markers for each system
- Include a reference line for ideal/linear scaling when appropriate
- Show the knee point where scaling degrades
- Use logarithmic scale if range spans orders of magnitude

### CDF Plots (Cumulative Distribution Function)

**Best for:**
- Latency distribution analysis
- Showing tail latency (p95, p99)
- Comparing latency characteristics across systems

**Design guidelines:**
- X-axis: latency (ms or us)
- Y-axis: cumulative fraction (0 to 1.0)
- Mark key percentiles (p50, p95, p99) with dashed horizontal lines
- Use logarithmic x-axis if latency spans orders of magnitude
- Include vertical reference lines at SLA thresholds if relevant

**Why CDFs matter in systems:**
Median latency alone is misleading. Tail latency (p99) determines user experience and SLA compliance. CDFs show the full distribution and make tail behavior visible.

### Timeline / Gantt Charts

**Best for:**
- Visualizing scheduling decisions over time
- Showing resource allocation across workers/GPUs
- Illustrating pipeline parallelism stages

**Design guidelines:**
- X-axis: time
- Y-axis: workers, GPUs, or pipeline stages
- Color-code different tasks or operations
- Show idle time explicitly (white/gray gaps)
- Include a legend mapping colors to operations

### Stacked Bar / Area Charts

**Best for:**
- Showing resource breakdown by component
- Displaying where time is spent in a pipeline
- Illustrating memory or bandwidth utilization decomposition

**Design guidelines:**
- Order stacks consistently (largest at bottom or most relevant at bottom)
- Use colors that are distinguishable in grayscale
- Include a legend
- Report the total as well as components

### Motivation Figures

**Best for:**
- Demonstrating that a problem exists
- Showing performance bottlenecks in existing systems
- Profiling workload characteristics

**Common types:**
- Profiling breakdowns (pie charts or stacked bars showing where time is spent)
- Performance gap plots (ideal vs. actual)
- Workload characterization (distributions of request sizes, inter-arrival times)
- CDF of existing system performance showing tail latency problems

**Placement:** Background/Motivation section (typically Figures 1-3)

## Table Design Guidelines

### Structure

**Basic anatomy:**
1. **Table number and title** (above table)
2. **Column headers** (with units)
3. **Row labels**
4. **Data cells** (with appropriate precision)
5. **Footnotes** (below table for abbreviations and notes)

### Formatting Best Practices

**Column headers:**
- Use clear, concise labels
- Include units in parentheses
- Use abbreviations sparingly (define in footnote)

**Data presentation:**
- Align decimal points in columns
- Use consistent decimal places
- Use en-dash (--) for "not applicable"
- **Bold the best result** in each row or column (strong convention in systems papers)
- Use \textbf{} in LaTeX for bolding

**Footnotes:**
- Define all abbreviations
- Note measurement methodology
- Indicate baseline configuration

### Example: Benchmark Comparison Table

```
Table 1. End-to-end inference throughput (tokens/sec) on different models.
Best results in bold.

Model        ServerlessLLM   vLLM    TensorRT-LLM   Triton
──────────────────────────────────────────────────────────────
LLaMA-7B       45,200       32,100     38,500       28,700
LLaMA-13B      28,400       18,900     22,300       15,200
LLaMA-70B    **15,200**      6,600      8,100        5,900
Mixtral-8x7B   22,800       14,500     17,200       11,800
──────────────────────────────────────────────────────────────

All experiments run on 8x NVIDIA A100 80GB GPUs with NVLink.
Batch size = 32, sequence length = 2048.
```

### Example: Hardware Configuration Table

```
Table 2. Experimental setup.

Component        Configuration
──────────────────────────────────────────────────
GPU              8x NVIDIA A100 80GB SXM4
CPU              2x AMD EPYC 7763 64-Core
Memory           1 TB DDR4-3200
Network          200 Gbps InfiniBand HDR
Storage          4x 3.84 TB NVMe SSD
OS               Ubuntu 22.04 LTS
CUDA             12.1
PyTorch          2.1.0
──────────────────────────────────────────────────
```

### Example: Ablation Study Table

```
Table 3. Ablation study on ServerlessLLM components.
Throughput measured on LLaMA-70B, 8x A100.

Configuration                    Throughput    Speedup
                                 (tok/s)       vs. Base
──────────────────────────────────────────────────────
Base (no optimizations)           6,600        1.0x
+ Locality-aware loading          9,200        1.4x
+ Checkpoint streaming           12,100        1.8x
+ Live migration                 13,800        2.1x
Full system (all components)     15,200        2.3x
──────────────────────────────────────────────────────
```

### Common Table Mistakes

1. **Not bolding best results** (convention in systems papers)
2. **Excessive complexity** (too many rows/columns)
3. **Insufficient context** (missing units, hardware details)
4. **Inconsistent precision** (mixing 1 and 3 decimal places)
5. **No baseline comparison** (raw numbers without context)
6. **Duplicate information** with figures

## Evaluation Metrics in Figures and Tables

### What to Report

For each experiment, report:
1. **Primary metric** (throughput, latency, accuracy)
2. **Variability** (error bars, standard deviation, confidence intervals)
3. **Configuration** (hardware, software, workload parameters)
4. **Baseline comparison** (speedup or improvement over baseline)

### Error Bars and Variability

**Choose the appropriate measure:**

| Measure | Meaning | When to Use |
|---------|---------|-------------|
| **Std Dev (SD)** | Variability in the data | Showing spread of measurements |
| **Std Error (SE)** | Precision of mean estimate | Showing confidence in the mean |
| **95% CI** | Range likely to contain true mean | Showing statistical significance |
| **Min-Max** | Full range | Showing worst/best case |

**Key rule:** Always state which measure is shown in the caption.

### Speedup Reporting

```
Good: "2.3x higher throughput (15.2K vs. 6.6K tokens/sec)"
Poor: "2.3x improvement" (improvement in what? over what baseline?)
```

Always specify:
- What metric the speedup is for
- What the baseline is
- Whether it is end-to-end or component-level

## Accessibility Considerations

### Color-Blind Friendly Design

**Recommendations:**
- Use color palettes designed for color-blind accessibility
- Don't rely on color alone (add patterns, shapes, or labels)
- Test figures in grayscale
- Avoid red-green combinations

**Color-blind safe palettes:**
- Blue-Orange (most common in systems papers)
- Colorbrewer2.org qualitative palettes
- Viridis, Plasma, Inferno (for heatmaps)
- Tableau 10 palette

### High Contrast

- Dark text on light background
- Thick enough lines (minimum 0.5-1 pt)
- Large enough text (minimum 8-10 pt after scaling)
- Distinct marker shapes for each data series

## Technical Requirements

### File Formats

**Vector formats** (preferred for all graphs and diagrams):
- **PDF**: Universal, integrates with LaTeX
- **EPS**: PostScript, traditional publishing format
- **SVG**: Web-friendly vector format

**Raster formats** (for screenshots or photos only):
- **PNG**: Lossless compression, good quality
- **TIFF**: Uncompressed, high quality

**Avoid:**
- JPEG for data figures (lossy compression creates artifacts)
- Low-resolution screenshots
- Figures copied from presentations

### Resolution Requirements

- **Line art** (graphs, diagrams): 300-600 dpi minimum
- **Screenshots**: 300 dpi minimum
- **Best practice**: Create figures at final size and resolution using vector formats

### Dimensions

**USENIX template (OSDI, NSDI, FAST):**
- Single column: ~3.33 inches (8.5 cm) wide
- Double column: ~7 inches (17.8 cm) wide

**ACM sigconf template (SIGCOMM, MOBICOM, SOSP):**
- Single column: ~3.33 inches (8.5 cm) wide
- Double column: ~7 inches (17.8 cm) wide

**Recommendation:** Design figures to fit single column when possible. Use double column only for complex architecture diagrams or multi-panel figures.

## Figure and Table Numbering

### Numbering System

**Figures:**
- Number consecutively in order of first mention: Figure 1, Figure 2, ...
- Supplementary/appendix figures: Figure A1, Figure A2, ...

**Tables:**
- Number separately from figures: Table 1, Table 2, ...

### In-Text References

```
"Figure 3 shows the end-to-end throughput comparison."
"The hardware configuration is summarized in Table 1."
"As shown in Figures 4-6, the scaling behavior varies across workloads."
```

**NOT:**
```
"Figure 3 below shows..." (avoid "above" or "below" - pagination may change)
"The figure shows..." (always use specific number)
```

## Captions

### Caption Structure

**For figures:**
```
Figure X. [Brief title stating what is shown]. [Additional description:
what the axes represent, what different colors/lines mean, key takeaway,
error bar definition]. Configuration: [hardware, parameters].
```

**For tables:**
```
Table X. [Descriptive title]. [Best results in bold].
[Table contents]
[Footnotes: abbreviations, measurement methodology, hardware config]
```

### Systems Paper Caption Examples

```
Figure 2. System architecture of ServerlessLLM. The scheduler assigns
incoming requests to workers based on checkpoint locality. Workers load
model checkpoints from the distributed storage layer using streaming
prefetch. Solid arrows indicate data flow; dashed arrows indicate
control messages.
```

```
Figure 5. Throughput comparison on LLaMA-70B inference with varying
batch sizes. Error bars show standard deviation over 5 runs.
ServerlessLLM achieves consistent improvements across all batch sizes
due to overlap of checkpoint loading and computation. Hardware: 8x
NVIDIA A100 80GB, 200 Gbps InfiniBand.
```

```
Figure 7. CDF of request latency for 1000 inference requests on
LLaMA-13B. ServerlessLLM (blue) achieves p99 latency of 45ms vs.
120ms for vLLM (orange). The improvement is most significant in the
tail (>p95), where locality-aware scheduling eliminates cold starts.
```

## Tools for Creating Figures

### Plotting Libraries
- **Python (matplotlib, seaborn)**: Most common in systems research, highly customizable
- **R (ggplot2)**: Excellent for statistical visualizations
- **gnuplot**: Lightweight, scriptable, good for line plots
- **MATLAB**: Good for complex visualizations, common in networking

### Diagram Tools
- **TikZ/PGF** (LaTeX): Integrates directly with paper, highest quality
- **draw.io/diagrams.net**: Free, web-based, exports to PDF/SVG
- **Inkscape**: Free vector graphics editor, good for polishing
- **OmniGraffle** (macOS): Professional diagramming

### Best Practices
- **Script figure generation** for reproducibility (matplotlib scripts, gnuplot files)
- Use vector output for all graphs
- Save raw data separately from figure files
- Use a Makefile to regenerate all figures from data
- Keep figure generation code in the paper repository

## Venue-Specific Figure Requirements

### USENIX (OSDI, NSDI, FAST, ATC)

- USENIX LaTeX template
- Figures count toward page limit (12 pages for long papers; 6 pages for FAST short papers)
- Vector graphics (PDF) preferred
- No specific resolution requirement for vector figures
- Figures embedded in text (not at end)

### ACM (SIGCOMM, MOBICOM, SOSP)

- ACM sigconf template
- Figures count toward page limit (12-15 pages)
- PDF preferred for figures
- ACM requires figure permissions for adapted figures
- Figures embedded in text

### Common Across All Systems Venues

- Figures must be legible in grayscale (reviewers may print)
- Error bars expected for repeated experiments
- Baseline comparisons required in evaluation figures
- Architecture diagram expected (usually Figure 1 or 2)
- Ablation study results expected (figure or table)

## Pre-Submission Checklist

**For every figure:**
- [ ] Vector format (PDF/EPS) or sufficient resolution (300+ dpi)?
- [ ] Readable at final print size (text >= 8pt)?
- [ ] Self-explanatory caption with abbreviations defined?
- [ ] Error bars included and explained in caption?
- [ ] Consistent colors/styles across all figures?
- [ ] Works in grayscale?
- [ ] Referenced in text in correct order?
- [ ] Axes labeled with units?

**For every table:**
- [ ] Best results bolded?
- [ ] Units included in column headers?
- [ ] Consistent decimal precision?
- [ ] Abbreviations defined in footnotes?
- [ ] Hardware/configuration noted?
- [ ] Referenced in text in correct order?

**Overall:**
- [ ] 5-8 figures typical for 12-page paper?
- [ ] Architecture diagram included?
- [ ] No duplication between text, figures, and tables?
- [ ] Consistent formatting across all display items?
- [ ] All display items necessary for supporting claims?
- [ ] Figures fit within page limits?
