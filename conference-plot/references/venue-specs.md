# Venue-Specific Formatting Specifications

Detailed reference for figure dimensions, font requirements, and submission
rules across major systems conference venues.

## Dimension Summary

| Venue | Column Width | Text Width | Default Height | Preset Key |
|-------|-------------|------------|----------------|------------|
| ACM (SIGCOMM, MOBICOM, etc.) | 3.33" (84.6mm) | 7.0" (177.8mm) | 2.5" | `acm-single` / `acm-double` |
| IEEE (INFOCOM, MICRO, etc.) | 3.5" (88.9mm) | 7.16" (181.9mm) | 2.5" | `ieee-single` / `ieee-double` |
| USENIX (OSDI, NSDI, ATC, etc.) | 3.33" (84.6mm) | 7.0" (177.8mm) | 2.5" | `usenix-single` / `usenix-double` |

Note: The `acm-single` preset uses 3.3" (slightly narrower) as a safe margin
to avoid any overflow issues with `\columnwidth`.

## ACM Venues

**Template:** `acmart` document class (sigconf, sigplan, or sigchi formats).

- `\columnwidth` = 3.333" (84.67mm)
- `\textwidth` = 7.0" (177.8mm)
- **Fonts:** Libertine (body), Inconsolata (mono). Figures typically use the
  document font, but monospace in figures is acceptable.
- **Font size requirements:** Body text is 9pt. Figure text should be no
  smaller than 6pt for readability.
- **Color model:** CMYK for print proceedings, RGB acceptable for digital-only.

### LaTeX inclusion

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{figures/my-plot.pdf}
  \caption{Caption text here.}
  \label{fig:my-plot}
\end{figure}
```

For double-column figures:

```latex
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{figures/my-wide-plot.pdf}
  \caption{Caption text here.}
  \label{fig:my-wide-plot}
\end{figure*}
```

## IEEE Venues

**Template:** `IEEEtran` document class.

- `\columnwidth` = 3.5" (88.9mm)
- `\textwidth` = 7.16" (181.9mm)
- **Fonts:** Times New Roman (body). Figures should use a similar serif or a
  clean monospace.
- **Font size requirements:** Body text is 10pt. Minimum figure font size is
  6pt (IEEE style guide).
- **Color model:** RGB is standard for digital proceedings.

### LaTeX inclusion

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{figures/my-plot.pdf}
  \caption{Caption text here.}
  \label{fig:my-plot}
\end{figure}
```

For double-column figures:

```latex
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{figures/my-wide-plot.pdf}
  \caption{Caption text here.}
  \label{fig:my-wide-plot}
\end{figure*}
```

## USENIX Venues

**Template:** `usenix2019_v3.sty` or later USENIX style files.

- `\columnwidth` ~ 3.33" (84.6mm)
- `\textwidth` = 7.0" (177.8mm)
- **Fonts:** Times (body). Figures should use a clean sans-serif or monospace.
- **Font size requirements:** Body text is 10pt. Minimum figure font size
  is 6pt.
- **Color model:** RGB for digital proceedings.

### LaTeX inclusion

Same `\includegraphics` patterns as ACM (identical column/text widths).

## Common Gotchas

### Type 3 Font Rejection

Many venues (especially IEEE and ACM) **reject PDFs containing Type 3 fonts**.
Type 3 fonts are bitmap-based and produce poor results when scaled.

**Solution:** Always set `pdf.fonttype: 42` and `ps.fonttype: 42` in
matplotlib rcParams. The `paper_style()` context manager does this
automatically. If you save figures outside the context manager, set these
explicitly:

```python
import matplotlib
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
```

### Minimum Font Size

All major venues require figure text to be **at least 6pt** for readability.
The default `paper_style()` uses 8pt base / 7pt tick labels, which is safe.
If you reduce `font_size`, ensure nothing drops below 6pt.

### Vector vs Raster

- **PDF** for submission: vector graphics, infinitely scalable, small file size.
- **PNG** for review/Slack: raster at 150+ DPI, easy to embed in slides or chat.
- **EPS** occasionally required by older IEEE templates; matplotlib can export
  EPS directly (`fig.savefig("plot.eps")`).

Avoid embedding raster images (PNG/JPEG) inside PDFs for submission. Use
vector output exclusively for camera-ready figures.

### Figure Placement

- Use `[t]` (top) placement for single-column figures.
- Use `\begin{figure*}[t]` for double-column figures spanning the full text width.
- Avoid `[h]` (here) — LaTeX often ignores it, and `[t]` produces better layouts.
- Place `\label{}` inside or immediately after `\caption{}` so `\ref{}` works correctly.

### Tight Bounding Boxes

Always save with `bbox_inches="tight"` to crop whitespace. For paper
submission, use minimal padding (`pad_inches=0.05`). For analysis/review
figures, use more padding (`pad_inches=0.3`) so labels aren't clipped in
quick viewers.
