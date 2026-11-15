"""Redraw Figure 1 (system boundary + Eq.1-6 coupling) without label overlaps.

The supplied artwork had two collisions: the "Cold jet" label sat on the dashed
zone boundary / jet arrows, and the "Coverage ..." label sat on the ground line.
This script redraws the same schematic at 1890 x 1140 px (300 dpi 15.5 cm wide
in the paper) with the labels moved into empty space.

Run: python analysis/make_fig1.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Circle, FancyArrowPatch

NAVY = "#1F3864"
BLUE = "#2F5597"
BLUE_FILL = "#E8EEF9"
ORANGE = "#C55A11"
ORANGE_FILL = "#FBE5D6"
PURPLE = "#7030A0"
PURPLE_FILL = "#E9E1F2"
GREEN = "#2E7D32"
GREEN_FILL = "#E2EFDA"
INK = "#22303F"

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["DejaVu Serif", "Times New Roman", "SimSun"]
plt.rcParams["mathtext.fontset"] = "dejavuserif"


def panel(ax, x, y, w, h):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.25,rounding_size=1.4",
        fc="white", ec="#2E3B4E", lw=1.6, zorder=0))


def text(ax, x, y, s, size=9, color=INK, weight="normal", ha="center", va="center",
         style="normal", z=5):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight, ha=ha, va=va,
            style=style, zorder=z)


def box(ax, x, y, w, h, fc, ec, lw=1.4):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.12,rounding_size=0.6",
        fc=fc, ec=ec, lw=lw, zorder=3))


def arrow(ax, p0, p1, color=INK, lw=1.6, ls="-", rad=0.0, style="-|>", z=4):
    ax.add_patch(FancyArrowPatch(
        p0, p1, arrowstyle=style, mutation_scale=13, color=color, lw=lw,
        linestyle=ls, connectionstyle=f"arc3,rad={rad}",
        shrinkA=0, shrinkB=0, zorder=z))


def person(ax, x, y, color=INK):
    ax.add_patch(Circle((x, y), 1.0, fc=color, ec=color, zorder=6))
    ax.add_patch(Polygon([[x - 1.05, y - 1.0], [x + 1.05, y - 1.0],
                          [x + 0.8, y - 4.6], [x - 0.8, y - 4.6]],
                         closed=True, fc=color, ec=color, zorder=6))


def main():
    fig, ax = plt.subplots(figsize=(12.6, 7.6), dpi=150)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # ------------------------------------------------ left panel: cross-section
    panel(ax, 1, 1, 46, 57.5)
    text(ax, 24, 56.2, "Semi-open Venue Cross-section", 13.5, NAVY, "bold")

    # shaded cooled zone and its dashed boundaries
    ax.add_patch(Rectangle((8, 8.6), 28, 37.8, fc="#DCE9F7", ec="none",
                           alpha=0.65, zorder=1))
    for x in (8, 36):
        ax.plot([x, x], [8.6, 46.4], color="#7FA8D4", lw=1.1,
                ls=(0, (5, 4)), zorder=2)

    # canopy and cooler unit
    ax.add_patch(Polygon([[6.5, 46.4], [11.0, 50.2], [36.0, 50.2], [40.5, 46.4]],
                         closed=True, fc="#3E4C5E", ec=INK, lw=1.2, zorder=3))
    box(ax, 22.5, 41.2, 9.6, 4.3, BLUE, NAVY, lw=1.1)
    text(ax, 27.3, 43.3, "Cooler", 10, "white", "bold")

    # cold jets
    for p1 in ((20.5, 20.6), (27.3, 20.0), (34.2, 20.6)):
        arrow(ax, (27.3, 41.2), p1, BLUE, lw=1.8)

    # occupants
    person(ax, 23.6, 16.9)
    person(ax, 33.4, 16.9)
    text(ax, 28.5, 11.0, r"$N_{eff}$ people", 9, INK, ha="center")

    # labels moved off the dashed boundary and off the jets
    text(ax, 9.6, 37.2, "Cold jet", 9.5, NAVY, "bold", ha="left")
    text(ax, 9.6, 34.6, r"$(\Delta T_{phys},\ v_{eff})$", 9.5, NAVY, ha="left")

    # lateral escape and ambient entrainment
    text(ax, 37.0, 37.4, r"Lateral escape $\gamma$", 9.5, ORANGE, "bold", ha="left")
    arrow(ax, (37.4, 34.6), (45.4, 34.6), ORANGE, lw=2.0)
    text(ax, 37.0, 24.6, "Ambient heat\nentrainment", 9.5, ORANGE, ha="left")
    arrow(ax, (45.4, 28.2), (37.8, 28.2), ORANGE, lw=1.6, ls=(0, (4, 3)))

    # ground line and coverage label (label now below the line, no collision)
    ax.plot([6, 44], [8.6, 8.6], color=INK, lw=2.2, zorder=5)
    text(ax, 24, 6.3, r"Coverage $A_{cov}$   ($\varphi = A_{cov}/A_{zone}$)", 9)

    # side note
    ax.add_patch(FancyBboxPatch((12.5, 1.8), 23, 2.6,
                                boxstyle="round,pad=0.10,rounding_size=0.4",
                                fc="white", ec="#B4B4B4", lw=0.9, zorder=4))
    text(ax, 24, 3.1, r"$\gamma$ = 0.55 (bus) / 0.30 (rail)", 8.8)

    # ------------------------------------------------ right panel: equation chain
    panel(ax, 52, 1, 47, 57.5)
    text(ax, 75.5, 56.2, r"Eq. 1 $\rightarrow$ 6 Mathematical Coupling", 13.5, NAVY, "bold")

    bw, bh, by = 9.4, 8.0, 40.6
    xs = (53.0, 63.8, 74.6, 85.4)
    boxes = [
        ("Eq. 1", "Wet-bulb limit", r"$\Delta T_{phys}$"),
        ("Eq. 2", "Steadman apparent", r"$\Delta T_{eff}$"),
        ("Eq. 3", "Efficiency", r"$\eta$"),
        ("Eq. 4", "Annual cost", r"$LCC_{annual}$"),
    ]
    for i, (x, (eq, l1, l2)) in enumerate(zip(xs, boxes)):
        fc, ec = (ORANGE_FILL, ORANGE) if i == 3 else (BLUE_FILL, BLUE)
        box(ax, x, by, bw, bh, fc, ec)
        text(ax, x + bw / 2, by + 6.3, eq, 10.5, ec, "bold")
        text(ax, x + bw / 2, by + 3.8, l1, 7.2 if i == 1 else 8.0)
        text(ax, x + bw / 2, by + 1.8, l2, 9.2)
        if i < 3:
            arrow(ax, (x + bw + 0.10, by + bh / 2), (x + bw + 1.25, by + bh / 2),
                  INK, lw=1.3)

    # Eq. 6 (safety / decision)
    box(ax, 56.5, 19.0, 17.5, 11.0, PURPLE_FILL, PURPLE)
    text(ax, 65.25, 27.4, "Eq. 6", 10.5, PURPLE, "bold")
    text(ax, 65.25, 24.7, "WBGT safety constraint", 8.6)
    text(ax, 65.25, 22.4, r"& composite score $E$", 8.6)

    # Eq. 5 (water-carbon externality)
    box(ax, 79.5, 21.2, 14.5, 11.0, GREEN_FILL, GREEN)
    text(ax, 86.75, 29.4, "Eq. 5", 10.5, GREEN, "bold")
    text(ax, 86.75, 26.7, "Water\u2013carbon", 8.6)
    text(ax, 86.75, 24.4, r"externality $I_{env}$", 8.6)

    # coupling arrows
    arrow(ax, (78.0, 40.6), (69.5, 30.2), BLUE, lw=1.5, ls=(0, (4, 3)), rad=0.12)
    arrow(ax, (88.6, 40.6), (87.4, 32.4), ORANGE, lw=1.6, rad=-0.25)
    arrow(ax, (79.4, 26.6), (74.2, 26.6), INK, lw=1.5)

    # bottom summary strip
    ax.add_patch(FancyBboxPatch((53.2, 4.6), 43.8, 5.6,
                                boxstyle="round,pad=0.12,rounding_size=0.5",
                                fc="#F2F2F2", ec="#7F7F7F", lw=0.9, zorder=3))
    text(ax, 75.1, 7.4,
         "Thermodynamics (Eq. 1\u20133)  \u2192  Economics & Externality (Eq. 4\u20135)"
         "  \u2192  Decision (Eq. 6)", 7.6, INK, "bold")

    fig.savefig("docs/figures/fig1_system.png", dpi=150, facecolor="white")
    plt.close(fig)
    print("saved docs/figures/fig1_system.png")


if __name__ == "__main__":
    main()
