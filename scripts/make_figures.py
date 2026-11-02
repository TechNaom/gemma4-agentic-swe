"""Figures for paper/paper.md.

Numbers come from the experiment summaries (paths below); rerun after any change there:
    python scripts/make_figures.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "paper" / "figures"

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
BLUE = "#2a78d6"

# experiments/g4swe-ablation-full-20261031/SUMMARY.md: resolved, tasks, Wilson 95% CI, graph-tool runs
ABLATION = [
    ("k0\nfile + shell tools", 34, 68, (38, 62), "graph tools: not offered"),
    ("k4\n+ 3 graph tools", 32, 68, (36, 59), "used in 4/68 runs"),
    ("n4\n+ graph tools, nudged", 14, 32, (28, 61), "used in 3/32 runs"),
]

# experiments/faults-2026-10-23/README.md: operator, mutants, escaped
FAULTS = [
    ("Boolean swap", 19, 10),
    ("Off-by-one", 15, 5),
    ("Drop a changed file", 16, 4),
    ("Drop a changed line", 60, 12),
    ("Return None", 21, 2),
    ("Flip a comparison", 26, 2),
    ("Remove a raise", 6, 0),
]


def style(ax: plt.Axes) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(INK_2)
    ax.tick_params(colors=INK_2, labelsize=10, length=0)


def resolve_rates() -> None:
    fig, ax = plt.subplots(figsize=(7.5, 3.6), dpi=200, facecolor=SURFACE)
    style(ax)
    for i, (label, solved, tasks, (lo, hi), use) in enumerate(ABLATION):
        y = len(ABLATION) - 1 - i
        rate = 100 * solved / tasks
        ax.plot([lo, hi], [y, y], color=BLUE, lw=2, solid_capstyle="round")
        ax.plot(rate, y, "o", ms=9, color=BLUE, mec=SURFACE, mew=2)
        ax.text(rate, y + 0.22, f"{rate:.0f}%  ({solved}/{tasks})", ha="center", va="bottom",
                fontsize=10, color=INK, fontweight="bold")
        ax.text(101, y, use, ha="left", va="center", fontsize=9, color=INK_2)
    ax.set_yticks(range(len(ABLATION)), [a[0] for a in reversed(ABLATION)], fontsize=10, color=INK)
    ax.set_xlim(20, 100)
    ax.set_ylim(-0.6, len(ABLATION) - 0.3)
    ax.set_xlabel("Tasks resolved (%), with 95% confidence interval", color=INK_2, fontsize=10)
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title("Adding code-graph tools did not raise the resolve rate",
                 loc="left", fontsize=12, color=INK, fontweight="bold", pad=12)
    fig.text(0.01, 0.01, "68 valid tasks (n4: first 32, stopped by its wall-clock cap). "
             "k4 vs k0 p = 0.69, n4 vs k0 p = 0.62 (paired McNemar).", fontsize=8, color=INK_2)
    fig.tight_layout(rect=(0, 0.04, 0.84, 1))
    fig.savefig(OUT / "fig1-resolve-rates.png", facecolor=SURFACE)
    plt.close(fig)


def fault_escapes() -> None:
    fig, ax = plt.subplots(figsize=(7.5, 3.8), dpi=200, facecolor=SURFACE)
    style(ax)
    rows = list(reversed(FAULTS))
    for y, (name, mutants, escaped) in enumerate(rows):
        rate = 100 * escaped / mutants
        ax.barh(y, rate, height=0.6, color=BLUE, edgecolor=SURFACE, linewidth=2)
        ax.text(rate + 1.2, y, f"{rate:.0f}%  ({escaped}/{mutants})", va="center",
                fontsize=9.5, color=INK)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=10, color=INK)
    ax.set_xlim(0, 65)
    ax.set_xlabel("Planted bugs the tests accepted (%)", color=INK_2, fontsize=10)
    ax.xaxis.grid(True, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.set_title("Where the tests let broken fixes through",
                 loc="left", fontsize=12, color=INK, fontweight="bold", pad=12)
    fig.text(0.01, 0.01, "163 planted bugs in the reference fixes of 62 valid tasks; 35 accepted (21%). "
             "After hand review, 24 are real misses (14.7%).", fontsize=8, color=INK_2)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(OUT / "fig2-fault-escapes.png", facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    resolve_rates()
    fault_escapes()
    print(f"wrote {OUT}")
