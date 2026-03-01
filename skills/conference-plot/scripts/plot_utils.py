"""Generalized plotting utilities for two-column conference papers.

Provides style presets, a colorblind-safe palette, and a dual-output
(PDF + PNG) workflow for paper submission and review.

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
    "#EEBA0C",  # orange
    "#56B4E9",  # sky blue
    "#009E73",  # bluish green
    "#F0E442",  # yellow
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#CC79A7",  # reddish purple
    "#0000FF",  # blue saturated
    "#FF0000",  # red saturated
]

# ── Bar hatch patterns ──────────────────────────────────────────────────────

HATCHES = ["", "//", "\\\\", "xx", "..", "++", "OO", "**"]


# ── Style context managers ──────────────────────────────────────────────────

@contextmanager
def paper_style(
    width: float = 3.3,
    height: float = 2.5,
    font_size: float = 8,
):
    """Context manager setting rcParams for paper-quality figures.

    Produces compact, column-width figures suitable for two-column
    conference papers (Type 42 fonts for PDF).

    Parameters
    ----------
    width, height : float
        Figure dimensions in inches.
    font_size : float
        Base font size in points (tick labels use font_size).
    """
    saved = matplotlib.rcParams.copy()
    try:
        matplotlib.rcParams.update({
            "font.size": font_size - 1,
            "font.family": "YaHei Consolas Hybrid",
            "figure.figsize": (width, height),
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "lines.linewidth": 1.0,
            "axes.linewidth": 0.6,
            "axes.edgecolor": "black",
            "axes.labelsize": font_size,
            "axes.titlesize": font_size,
            "axes.titleweight": "bold",
            "axes.grid": True,
            "xtick.direction": "in",
            "ytick.direction": "in",
            "xtick.major.size": 3.5,
            "ytick.major.size": 3.5,
            "xtick.labelsize": font_size,
            "ytick.labelsize": font_size,
            "xtick.major.width": 0.6,
            "ytick.major.width": 0.6,
            "legend.fontsize": font_size,
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


# ── Save helpers ────────────────────────────────────────────────────────────

def save_dual_output(
    fig,
    pdf_path: Path | None,
    png_path: Path | None,
    save_both: bool = True,
) -> None:
    """Save a figure as PDF and/or PNG, creating parent dirs as needed.

    Parameters
    ----------
    fig : matplotlib Figure
        The figure to save.
    pdf_path : Path or None
        Target path for the PDF output.
    png_path : Path or None
        Target path for the PNG output.
    save_both : bool
        When True (default), auto-derive the missing path by swapping
        the extension (.pdf ↔ .png).  When False, save only the
        explicitly provided path(s).
    """
    if save_both:
        if pdf_path is not None and png_path is None:
            png_path = pdf_path.with_suffix(".png")
        elif png_path is not None and pdf_path is None:
            pdf_path = png_path.with_suffix(".pdf")

    if pdf_path is not None:
        pdf_path = Path(pdf_path)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(pdf_path, bbox_inches="tight", pad_inches=0.05, facecolor="white")
        print(f"Saved PDF: {pdf_path}")
    if png_path is not None:
        png_path = Path(png_path)
        png_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(png_path, dpi=150, bbox_inches="tight", pad_inches=0.05, facecolor="white")
        print(f"Saved PNG: {png_path}")
