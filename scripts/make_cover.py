"""Card / thumbnail image for the Kaggle Writeup (1200x630)."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = Path(__file__).resolve().parent.parent / "paper" / "figures" / "cover.png"
BG, FG, MUTED, ACCENT, WARN, PANEL = "#0f1420", "#f2f4f8", "#9aa4b5", "#4f8cff", "#ff8a3d", "#18202f"

fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 1200)
ax.set_ylim(0, 630)
ax.axis("off")

ax.text(70, 560, "GEMMA 4 DEVELOPER AGENT  ·  PAPER TRACK", color=ACCENT, fontsize=13, weight="bold")
ax.text(70, 470, "Tools Unused, Tests Fooled", color=FG, fontsize=46, weight="bold")
ax.text(70, 418, "What actually helps a Gemma 4 coding agent, and can we trust the score?",
        color=MUTED, fontsize=17)

def panel(x, big, colour, line1, line2):
    ax.add_patch(FancyBboxPatch((x, 110), 500, 220, boxstyle="round,pad=0,rounding_size=18",
                                facecolor=PANEL, edgecolor="#26304a", linewidth=1.5))
    ax.text(x + 36, 225, big, color=colour, fontsize=50, weight="bold")
    ax.text(x + 36, 168, line1, color=FG, fontsize=16)
    ax.text(x + 36, 136, line2, color=MUTED, fontsize=14)

panel(70, "50% → 47%", ACCENT, "Code-graph tools did not help", "Used in <10% of runs · 68 valid tasks")
panel(630, "14.7%", WARN, "of broken fixes pass the tests", "163 planted bugs · hand-reviewed")

ax.text(70, 50, "Manohar Papasani  ·  github.com/TechNaom/gemma4-agentic-swe", color=MUTED, fontsize=13)

OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, facecolor=BG)
print(OUT)
