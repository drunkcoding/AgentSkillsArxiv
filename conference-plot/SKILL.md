---
name: conference-plot
description: Create publication-quality matplotlib figures for two-column
  conference papers (ACM, IEEE, USENIX). Provides style presets, colorblind-safe
  Wong palette, venue-aware dimensions, and dual-output (PDF+PNG) workflow.
  Use when the user wants to create, style, or fix plots/figures/charts for
  academic paper submission, or asks for conference-quality matplotlib figures.
---

# Conference Paper Plotting

## Quick Start

Always import `plot_utils.py` from this skill's `scripts/` directory and use
the `paper_style()` context manager to set up correct dimensions and rcParams.

### Bar chart (ACM single-column)

```python
import sys
sys.path.insert(0, "/home/xly/.claude/skills/conference-plot/scripts")
from plot_utils import paper_style, WONG_PALETTE, HATCHES, savefig_paper
import matplotlib.pyplot as plt
import numpy as np

labels = ["A", "B", "C", "D"]
values = [4.2, 3.8, 5.1, 2.9]

with paper_style(venue="acm-single"):
    fig, ax = plt.subplots()
    bars = ax.bar(labels, values, color=WONG_PALETTE[1:5],
                  edgecolor="black", linewidth=0.4,
                  hatch=[HATCHES[i] for i in range(len(labels))])
    ax.set_ylabel("Throughput (Gbps)")
    ax.set_xlabel("Configuration")
    savefig_paper(fig, "throughput.pdf")
    plt.close(fig)
```

### Line plot (USENIX single-column)

```python
from plot_utils import paper_style, WONG_PALETTE, MARKERS, savefig_paper
import matplotlib.pyplot as plt
import numpy as np

x = np.arange(1, 6)
with paper_style(venue="usenix-single"):
    fig, ax = plt.subplots()
    for i, label in enumerate(["System A", "System B", "System C"]):
        ax.plot(x, np.random.rand(5) * 10, color=WONG_PALETTE[i + 1],
                marker=MARKERS[i], markersize=4, label=label)
    ax.set_xlabel("Thread Count")
    ax.set_ylabel("Latency (ms)")
    ax.legend()
    savefig_paper(fig, "latency.pdf")
    plt.close(fig)
```

### Heatmap (IEEE double-column)

```python
from plot_utils import paper_style, savefig_paper
import matplotlib.pyplot as plt
import numpy as np

data = np.random.rand(5, 8)
with paper_style(venue="ieee-double"):
    fig, ax = plt.subplots()
    im = ax.imshow(data, cmap="RdYlGn_r", aspect="auto")
    fig.colorbar(im, ax=ax, shrink=0.8)
    ax.set_xlabel("Benchmark")
    ax.set_ylabel("Configuration")
    savefig_paper(fig, "heatmap.pdf")
    plt.close(fig)
```

## Usage

1. **Import** from `scripts/plot_utils.py` (add the skill's `scripts/` dir to `sys.path`).
2. **Wrap** all plotting code in `paper_style()` (for submission) or `analysis_style()` (for review).
3. **Save** with `savefig_paper(fig, path)` for PDF submission or `savefig_analysis(fig, path)` for PNG review.
4. For dual output, use `save_dual_output(fig_paper, fig_analysis, pdf_path, png_path)`.

## Style Reference

### Color Palette (WONG_PALETTE)

| Index | Hex       | Color          | Typical Use              |
|-------|-----------|----------------|--------------------------|
| 0     | `#000000` | Black          | Baselines, reference     |
| 1     | `#E69F00` | Orange         | Primary comparison       |
| 2     | `#56B4E9` | Sky Blue       | Secondary comparison     |
| 3     | `#009E73` | Bluish Green   | Third system             |
| 4     | `#F0E442` | Yellow         | Fourth (use sparingly)   |
| 5     | `#0072B2` | Blue           | Fifth system             |
| 6     | `#D55E00` | Vermillion     | Sixth / alert            |
| 7     | `#CC79A7` | Reddish Purple | Seventh system           |

This is the Wong colorblind-safe palette (Nature Methods, 2011). Safe for
deuteranopia, protanopia, and tritanopia. Start from index 1 for data series
(index 0 is black, best for baselines or outlines).

### Markers (MARKERS)

`['o', 's', '^', 'D', 'v', 'P', 'X', '*']` — circle, square, triangle-up,
diamond, triangle-down, plus-filled, X-filled, star.

### Hatches (HATCHES)

`['', '//', '\\\\', 'xx', '..', '++', 'OO', '**']` — none, diagonal,
back-diagonal, cross-hatch, dots, plus, circles, stars.

### Venue Dimensions

| Preset Key      | Width  | Height | Use Case                |
|-----------------|--------|--------|-------------------------|
| `acm-single`   | 3.3"   | 2.5"   | ACM single column       |
| `acm-double`   | 7.0"   | 2.5"   | ACM full text width     |
| `ieee-single`  | 3.5"   | 2.5"   | IEEE single column      |
| `ieee-double`  | 7.16"  | 2.5"   | IEEE full text width    |
| `usenix-single`| 3.33"  | 2.5"   | USENIX single column    |
| `usenix-double`| 7.0"   | 2.5"   | USENIX full text width  |

Pass `venue="acm-single"` to `paper_style()` to auto-set width and height.
Override height as needed: `paper_style(venue="acm-single", height=3.0)` is
NOT supported — pass explicit `width` and `height` instead if you need custom
dimensions.

## Common Patterns

### Grouped bars with hatches

```python
x = np.arange(len(groups))
w = 0.25
for i, (series, vals) in enumerate(data.items()):
    ax.bar(x + i * w, vals, w, label=series,
           color=WONG_PALETTE[i + 1], edgecolor="black", linewidth=0.4,
           hatch=HATCHES[i + 1])
ax.set_xticks(x + w * (len(data) - 1) / 2)
ax.set_xticklabels(groups)
```

### Dual-axis (twinx) with color-coded labels

```python
ax1 = fig.add_subplot(111)
ax2 = ax1.twinx()
ax1.bar(x, throughput, color=WONG_PALETTE[1], label="Throughput")
ax2.plot(x, latency, color=WONG_PALETTE[5], marker=MARKERS[0], label="Latency")
ax1.set_ylabel("Throughput (Gbps)", color=WONG_PALETTE[1])
ax2.set_ylabel("Latency (ms)", color=WONG_PALETTE[5])
ax1.tick_params(axis="y", colors=WONG_PALETTE[1])
ax2.tick_params(axis="y", colors=WONG_PALETTE[5])
```

### Error bars

```python
ax.bar(x, means, yerr=stds, capsize=2, color=WONG_PALETTE[1:],
       edgecolor="black", linewidth=0.4, error_kw={"linewidth": 0.6})
```

### Heatmap with annotation

```python
im = ax.imshow(data, cmap="RdYlGn_r", aspect="auto")
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        ax.text(j, i, f"{data[i, j]:.1f}", ha="center", va="center", fontsize=6)
fig.colorbar(im, ax=ax, shrink=0.8)
```

## Guidelines

- **Always** use `paper_style()` — it sets `pdf.fonttype=42` and `ps.fonttype=42`
  to avoid Type 3 font rejection by venues.
- **Keep fonts >= 6pt** for readability. The default 8pt base / 7pt ticks is safe.
- **Use `WONG_PALETTE`** for colorblind safety. Start from index 1 for data
  series; index 0 (black) is best for baselines or outlines.
- **Export PDF for paper**, PNG for review. Use `savefig_paper()` and
  `savefig_analysis()` respectively.
- **Always `plt.close(fig)`** after saving to avoid memory leaks in batch scripts.
- **Pair hatches with colors** for bar charts so the plot remains distinguishable
  in grayscale printouts.

## Detailed Venue Specs

See [references/venue-specs.md](references/venue-specs.md) for column widths,
font requirements, LaTeX `\includegraphics` patterns, and common gotchas
(Type 3 fonts, minimum font size, vector vs raster) for ACM, IEEE, and USENIX.
