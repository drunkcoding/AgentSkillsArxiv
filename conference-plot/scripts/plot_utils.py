"""Generalized plotting utilities for two-column conference papers.

Provides style presets, a colorblind-safe palette, venue-aware dimensions,
and a dual-output (PDF + PNG) workflow for paper submission and review.

Based on the battle-tested patterns from NVBenchSuite/analysis/plot_utils.py,
generalized for any conference paper plotting task.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt


# ── Wong colorblind-safe palette (Nature Methods, 2011) ─────────────────────

WONG_PALETTE = [
    "#000000",  # black
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
    "#009E73",  # bluish green
    "#F0E442",  # yellow
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#CC79A7",  # reddish purple
]

# ── Bar hatch patterns ──────────────────────────────────────────────────────

HATCHES = ["", "//", "\\\\", "xx", "..", "++", "OO", "**"]

# ── Marker styles for line/scatter plots ────────────────────────────────────

MARKERS = ["o", "s", "^", "D", "v", "P", "X", "*"]

# ── Venue dimension presets ─────────────────────────────────────────────────

VENUE_PRESETS = {
    "acm-single":    {"width": 3.3,  "height": 2.5},
    "acm-double":    {"width": 7.0,  "height": 2.5},
    "ieee-single":   {"width": 3.5,  "height": 2.5},
    "ieee-double":   {"width": 7.16, "height": 2.5},
    "usenix-single": {"width": 3.33, "height": 2.5},
    "usenix-double": {"width": 7.0,  "height": 2.5},
}


# ── Style context managers ──────────────────────────────────────────────────

@contextmanager
def paper_style(
    width: float = 3.3,
    height: float = 2.5,
    font_size: float = 8,
    *,
    venue: str | None = None,
):
    """Context manager setting rcParams for paper-quality figures.

    Produces compact, column-width figures suitable for two-column
    conference papers (monospace font, Type 42 fonts for PDF).

    Parameters
    ----------
    width, height : float
        Figure dimensions in inches.  Ignored when *venue* is given.
    font_size : float
        Base font size in points (tick labels are font_size - 1).
    venue : str, optional
        Key into ``VENUE_PRESETS`` (e.g. ``"acm-single"``).  When provided,
        *width* and *height* are looked up automatically.
    """
    if venue is not None:
        preset = VENUE_PRESETS[venue]
        width = preset["width"]
        height = preset["height"]

    saved = matplotlib.rcParams.copy()
    try:
        matplotlib.rcParams.update({
            "font.size": font_size,
            "font.family": "monospace",
            "figure.figsize": (width, height),
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "lines.linewidth": 1.0,
            "axes.linewidth": 0.6,
            "axes.edgecolor": "black",
            "axes.labelsize": font_size,
            "axes.titlesize": font_size,
            "axes.grid": True,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.size": 3.5,
            "ytick.major.size": 3.5,
            "xtick.labelsize": font_size - 1,
            "ytick.labelsize": font_size - 1,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "legend.fontsize": font_size - 1,
            "legend.framealpha": 0.9,
            "grid.linewidth": 0.4,
            "grid.alpha": 0.4,
            "grid.linestyle": ":",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "scatter.edgecolors": "none",
        })
        yield
    finally:
        matplotlib.rcParams.update(saved)


@contextmanager
def analysis_style(font_size: float = 32):
    """Context manager setting rcParams for large analysis/review figures.

    Produces large-format figures with thick lines and big fonts, suitable
    for screen review, presentations, or Slack sharing.
    """
    saved = matplotlib.rcParams.copy()
    try:
        matplotlib.rcParams.update({
            "font.size": font_size,
            "font.family": "Consolas",
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "lines.linewidth": 3,
            "axes.linewidth": 3,
            "axes.edgecolor": "black",
            "axes.grid": True,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.size": 3.5,
            "ytick.major.size": 3.5,
            "xtick.major.width": 2,
            "ytick.major.width": 2,
            "grid.linewidth": 2,
            "grid.alpha": 0.4,
            "grid.linestyle": ":",
            "scatter.edgecolors": "none",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        })
        yield
    finally:
        matplotlib.rcParams.update(saved)


# ── Save helpers ────────────────────────────────────────────────────────────

def savefig_paper(fig, path, **kwargs) -> None:
    """Save a figure for paper submission (tight bbox, minimal padding).

    Creates parent directories automatically.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", pad_inches=0.05, facecolor="white", **kwargs)


def savefig_analysis(fig, path, dpi: int = 150, **kwargs) -> None:
    """Save a figure for review/analysis (higher DPI, more padding).

    Creates parent directories automatically.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", pad_inches=0.3, facecolor="white", **kwargs)


def save_dual_output(
    fig_paper,
    fig_analysis,
    pdf_path: Path | None,
    png_path: Path | None,
) -> None:
    """Save paper PDF and analysis PNG, creating parent dirs as needed."""
    if pdf_path is not None:
        savefig_paper(fig_paper, pdf_path)
        print(f"Saved PDF: {pdf_path}")
    if png_path is not None:
        savefig_analysis(fig_analysis, png_path)
        print(f"Saved PNG: {png_path}")
