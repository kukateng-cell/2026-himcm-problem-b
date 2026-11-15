"""Generate Figures 1-6 for the paper from the locked numbers.

Run with the system Python that has matplotlib:
    "C:\\Users\\kukat\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" analysis/make_figures.py

Output: docs/figures/fig1_system.png ... fig6_infographic.png (300 dpi).
Figure 1 reuses the supplied schematic (converted from webp); Figures 2-6 are
re-drawn here because the supplied versions carried the pre-P0 numbers
(0.3011/0.3410, 28.14, 63-70% crossover, fan winning HK rail under Balanced).
"""

import copy
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recompute as R

R.MODE = "pressure"
R.THRESH = 30.0

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "figures")
os.makedirs(OUT, exist_ok=True)

BLUE = "#2f5aa8"
ORANGE = "#d9731a"
TEAL = "#1f8a70"
PURPLE = "#6a4c93"
GREEN = "#2e9e6b"
GRID = "#dcdcdc"

plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix",
    "font.size": 11,
    "axes.edgecolor": "#333333",
    "axes.linewidth": 0.8,
    "axes.grid": True,
    "grid.color": GRID,
    "grid.linewidth": 0.6,
    "grid.alpha": 0.8,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=300)
    plt.close(fig)
    print("wrote", path)


# ---------------------------------------------------------------- data
T3, _ = R.table3_rows("pressure", 30.0)
T4, _ = R.table4_rows("pressure", 30.0)
T5, G5 = R.table5_rows("pressure", 30.0, "B")
T6 = R.table6(T5, G5, 30.0)


def find(rows, city, eq, n):
    return next(r for r in rows if r["city"] == city and r["eq"] == eq and r["n"] == n)


# ---------------------------------------------------------------- fig 2
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.2, 5.0), gridspec_kw={"width_ratios": [1, 1.15]})

labels = ["A (0.25 kW)", "B (1.20 kW)", "C (2.50 kW)"]
dts = [r["dT"] for r in T3]
etas = [r["eta"] for r in T3]
x = np.arange(3)
bars = ax1.bar(x, dts, width=0.55, color=BLUE, alpha=0.9, label=r"Apparent cooling $\Delta T_{eff}$ (°C)")
ax1.set_xticks(x)
ax1.set_xticklabels(labels)
ax1.set_ylabel(r"Effective apparent cooling $\Delta T_{eff}$ (°C)", color=BLUE)
ax1.set_ylim(0, max(dts) * 1.35)
ax1.tick_params(axis="y", labelcolor=BLUE)
for xi, v in zip(x, dts):
    ax1.text(xi, v + 0.12, f"{v:.3f}°C", ha="center", va="bottom", color=BLUE, fontsize=10)

ax1b = ax1.twinx()
ax1b.grid(False)
ax1b.plot(x, etas, color=ORANGE, marker="o", ms=7, lw=2.4, label=r"Cooling efficiency $\eta$ (persons·°C/kW)")
ax1b.set_ylabel(r"Cooling efficiency $\eta$ (persons·°C/kW)", color=ORANGE)
ax1b.tick_params(axis="y", labelcolor=ORANGE)
ax1b.set_ylim(0, max(etas) * 1.35)
for xi, v in zip(x, etas):
    ax1b.text(xi + 0.07, v + 1.5, f"{v:.2f}", ha="left", va="bottom", color=ORANGE, fontsize=10)
ax1.set_title("(a) Q2a efficiency paradox: power vs marginal return", fontsize=11.5, pad=10)
h1, l1 = ax1.get_legend_handles_labels()
h2, l2 = ax1b.get_legend_handles_labels()
ax1.legend(h1 + h2, l1 + l2, loc="upper right", frameon=True, fontsize=8.5)

groups = ["MC37V", "MC61V", "Porta"]
glabels = ["MC37V", "MC61V", "Portacool"]
xs = np.arange(len(groups))
w = 0.34
one = [find(T4, "PHX", g, 1)["E"] for g in groups]
two = [find(T4, "PHX", g, 2)["E"] for g in groups]
phi1 = [find(T4, "PHX", g, 1)["phi"] for g in groups]
phi2 = [find(T4, "PHX", g, 2)["phi"] for g in groups]
b1 = ax2.bar(xs - w / 2, one, width=w, color="#8fa3c8", edgecolor="#3b4c6b", label="1 unit")
b2 = ax2.bar(xs + w / 2, two, width=w, color=TEAL, edgecolor="#14584a", label="2 units in parallel")
ax2.set_xticks(xs)
ax2.set_xticklabels(glabels)
ax2.set_ylim(0, 0.50)
ax2.set_ylabel("Composite evaluation score $E$")
for xi, v, ph in zip(xs - w / 2, one, phi1):
    ax2.text(xi, v + 0.008, f"E = {v:.4f}\n(φ = {ph:.2f})", ha="center", va="bottom", fontsize=8.2)
for xi, v, ph in zip(xs + w / 2, two, phi2):
    ax2.text(xi, v + 0.008, f"E = {v:.4f}\n(φ = {ph:.2f})", ha="center", va="bottom", fontsize=8.2)
ax2.legend(loc="upper right", fontsize=8.5, frameon=True)
ax2.set_title("(b) Q2b multi-unit scaling ($A_{zone}$ = 120 m², Phoenix rail)", fontsize=11.5, pad=10)
fig.tight_layout()
save(fig, "fig2_q2a_q2b.png")

# ---------------------------------------------------------------- fig 3
rhs = np.arange(10, 91, 2.0)
dts_bus, dts_rail = [], []
base_city = copy.deepcopy(R.CITY["PHX"])
for rh in rhs:
    R.CITY["PHX"]["T"] = 41.0
    R.CITY["PHX"]["RH"] = float(rh)
    dts_bus.append(R.calc("PHX", "bus", "MC37V", 1, "pressure")["dT"])
    dts_rail.append(R.calc("PHX", "rail", "MC37V", 1, "pressure")["dT"])
R.CITY["PHX"] = base_city
fan = R.calc("PHX", "bus", "Fan", 1, "pressure")["dT"]

fig, ax = plt.subplots(figsize=(9.6, 5.6))
ax.plot(rhs, dts_bus, color=ORANGE, lw=2.4, marker="o", ms=4, label=r"MC37V, bus shelter ($\gamma$ = 0.55)")
ax.plot(rhs, dts_rail, color=BLUE, lw=2.4, marker="s", ms=4, label=r"MC37V, rail station ($\gamma$ = 0.30)")
ax.axhline(fan, color=TEAL, lw=2.2, ls="--", label='Drum fan 36" (2.081 °C)')
ax.axvline(18, color=ORANGE, ls=":", lw=1.6)
ax.axvline(78, color=TEAL, ls=":", lw=1.6)
ax.text(19, 4.85, "Phoenix\nRH = 18%", color=ORANGE, fontsize=10, va="top")
ax.text(76.5, 4.30, "Hong Kong\nRH = 78%", color=TEAL, fontsize=10, va="top", ha="right")

# crossovers from the paper: bus 69.6%, rail 79.7%
ax.axvline(69.6, color=ORANGE, ls=":", lw=1.4)
ax.axvline(79.7, color=BLUE, ls=":", lw=1.4)
ax.text(68.8, 5.95, "bus crossover 69.6%", color=ORANGE, fontsize=9, ha="right")
ax.text(80.4, 5.55, "rail crossover 79.7%", color=BLUE, fontsize=9, ha="left")
ax.set_xlim(10, 90)
ax.set_ylim(0, 6.4)
ax.set_xlabel("Relative humidity RH (%)")
ax.set_ylabel(r"Effective apparent cooling $\Delta T_{eff}$ (°C)")
ax.set_title("RH sensitivity at 41 °C: evaporative cooler vs pure fan", fontsize=12, pad=10)
ax.legend(loc="lower left", fontsize=9, frameon=True)
fig.tight_layout()
save(fig, "fig3_rh_crossover.png")

# ---------------------------------------------------------------- fig 4
fig, ax = plt.subplots(figsize=(9.2, 5.8))
seen = {}
for r in T5:
    key = (r["city"], r["eq"])
    if key in seen:
        seen[key]["wbgt"] = max(seen[key]["wbgt"], r["wbgt"])
        continue
    seen[key] = dict(city=r["city"], eq=r["eq"], lcc=r["lcc"], ienv=r["I_env"], wbgt=r["wbgt"])

names = {"MC37V": "MC37V", "MC61V": "MC61V", "Porta": "Portacool", "Fan": 'Drum fan 36"'}
offsets = {("PHX", "MC37V"): (8, 0.015), ("HK", "MC37V"): (8, -0.045),
           ("PHX", "MC61V"): (8, 0.012), ("HK", "MC61V"): (-95, -0.055),
           ("PHX", "Porta"): (8, 0.010), ("HK", "Porta"): (-78, -0.060),
           ("PHX", "Fan"): (-72, -0.062), ("HK", "Fan"): (8, 0.020)}
offsets = {"MC37V": (8, 0.012), "MC61V": (8, 0.012), "Porta": (8, -0.035), "Fan": (8, 0.048)}
for (city, eq), d in seen.items():
    ok = d["wbgt"] <= 30.0
    color = GREEN if ok else ORANGE
    marker = "o" if city == "PHX" else "^"
    ax.scatter(d["lcc"], d["ienv"], s=110, color=color, marker=marker, edgecolor="#222222", lw=0.8, zorder=4)
    if city == "PHX":
        dx, dy = offsets[eq]
        ax.annotate(names[eq], xy=(d["lcc"], d["ienv"]),
                    xytext=(d["lcc"] + dx, d["ienv"] + dy), fontsize=8.0, color="#333333")
ax.set_xlabel(r"Annualised life-cycle cost $LCC_{annual}$ (USD/yr)")
ax.set_ylabel(r"Water–carbon externality $I_{env}$")
ax.set_title(r"$LCC$ vs $I_{env}$ trade-off (colour: WBGT at the 30 °C reference)", fontsize=12, pad=10)
ax.set_xlim(100, 400)
ax.set_ylim(0.1, 1.02)
from matplotlib.lines import Line2D
handles = [Line2D([], [], marker="o", ls="", color="#555555", label="Phoenix"),
           Line2D([], [], marker="^", ls="", color="#555555", label="Hong Kong"),
           Line2D([], [], marker="o", ls="", color=GREEN, label="WBGT ≤ 30 °C"),
           Line2D([], [], marker="o", ls="", color=ORANGE, label="WBGT > 30 °C")]
ax.legend(handles=handles, loc="upper right", fontsize=8.5, frameon=True)
fig.tight_layout()
save(fig, "fig4_pareto.png")

# ---------------------------------------------------------------- fig 5
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 5.2), gridspec_kw={"width_ratios": [1, 1.15]})
gammas = np.arange(0.20, 0.751, 0.05)
etas = []
base_venue = copy.deepcopy(R.VENUE["bus"])
for g in gammas:
    R.VENUE["bus"]["g"] = float(g)
    etas.append(R.calc("PHX", "bus", "MC37V", 1, "pressure")["eta"])
R.VENUE["bus"] = base_venue
ax1.plot(gammas, etas, color=BLUE, lw=2.4)
ax1.axvline(0.30, color=TEAL, ls="--", lw=1.6)
ax1.axvline(0.55, color=ORANGE, ls="--", lw=1.6)
ax1.text(0.305, min(etas) + 6, "rail $\\gamma$ = 0.30", color=TEAL, fontsize=9, rotation=90, va="bottom")
ax1.text(0.555, min(etas) + 6, "bus $\\gamma$ = 0.55", color=ORANGE, fontsize=9, rotation=90, va="bottom")
ax1.set_xlabel(r"Lateral escape rate $\gamma$")
ax1.set_ylabel(r"Cooling efficiency $\eta$ (persons·°C/kW)")
ax1.set_title(r"$\gamma$ scan: efficiency falls as escape rises (Phoenix bus, MC37V)", fontsize=11, pad=10)

profiles = ["Balanced", "Safety", "Cost", "Eco"]
venues = [("PHX", "bus"), ("PHX", "rail"), ("HK", "bus"), ("HK", "rail")]
display = {"MC37V": "MC37V", "MC61V": "MC61V", "Porta": "Portacool", "Fan": 'Fan 36"'}
colors = {"MC37V": BLUE, "MC61V": PURPLE, "Porta": TEAL, "Fan": ORANGE}
grid = np.zeros((4, 4, 3))
for i, p in enumerate(profiles):
    for j, (c, v) in enumerate(venues):
        eq, score = T6[(p, c, v)]
        rgb = matplotlib.colors.to_rgb(colors[eq])
        grid[i, j] = rgb
axes_img = ax2.imshow(grid, aspect="auto")
ax2.set_xticks(range(4))
ax2.set_xticklabels(["Phoenix\nBus", "Phoenix\nRail", "HK\nBus", "HK\nRail"], fontsize=9)
ax2.set_yticks(range(4))
ax2.set_yticklabels(profiles, fontsize=9)
ax2.grid(False)
for i, p in enumerate(profiles):
    for j, (c, v) in enumerate(venues):
        eq, score = T6[(p, c, v)]
        ax2.text(j, i, f"{score:.2f}\n{display[eq]}", ha="center", va="center", color="white" if eq != "Fan" else "#3a2a10", fontsize=8.6, fontweight="bold")
ax2.set_title("Winner matrix: best unit and its score per COO profile", fontsize=11, pad=10)
from matplotlib.patches import Patch
ax2.legend(handles=[Patch(facecolor=colors[k], label=display[k]) for k in ["MC37V", "MC61V", "Porta", "Fan"]],
           loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=4, fontsize=8, frameon=False)
fig.tight_layout()
save(fig, "fig5_gamma_heatmap.png")

# ---------------------------------------------------------------- fig 6
phx_bus = next(r for r in T5 if r["city"] == "PHX" and r["venue"] == "bus" and r["eq"] == "MC37V")
hk_bus_37 = next(r for r in T5 if r["city"] == "HK" and r["venue"] == "bus" and r["eq"] == "MC37V")
hk_bus_fan = next(r for r in T5 if r["city"] == "HK" and r["venue"] == "bus" and r["eq"] == "Fan")

fig, ax = plt.subplots(figsize=(12.4, 5.0))
ax.axis("off")
ax.set_xlim(0, 10)
ax.set_ylim(-0.05, 4.0)
ax.set_title("Shade first, then windbreak, then match the machine to the climate", fontsize=13, pad=14)

def panel(x0, color, title, subtitle, lines):
    ax.add_patch(FancyBboxPatch((x0, 0.22), 4.6, 3.48, boxstyle="round,pad=0.06,rounding_size=0.18",
                                fc="#f7f9fc", ec=color, lw=2.2))
    ax.add_patch(FancyBboxPatch((x0, 3.05), 4.6, 0.65, boxstyle="round,pad=0.06,rounding_size=0.18",
                                fc=color, ec=color, lw=2.2))
    ax.text(x0 + 2.3, 3.38, title, ha="center", va="center", color="white", fontsize=12, fontweight="bold")
    ax.text(x0 + 2.3, 2.88, subtitle, ha="center", va="center", fontsize=9.5, color="#333333")
    y = 2.42
    for big, small in lines:
        ax.text(x0 + 0.35, y, big, fontsize=15, color=color, fontweight="bold", ha="left", va="center")
        ax.text(x0 + 0.35, y - 0.30, small, fontsize=8.6, color="#444444", ha="left", va="center")
        y -= 0.60

water_phx = phx_bus["Vw"] / phx_bus["P"]
water_hk = hk_bus_37["Vw"] / hk_bus_37["P"]
ratio = (hk_bus_fan["dT"] / hk_bus_37["dT"] - 1) * 100
panel(0.15, ORANGE, "Phoenix — dry-hot (41 °C, 18% RH)", "Recommended: 1× MC37V per bus shelter",
      [(f"{phx_bus['dT']:.2f} °C", "effective apparent cooling (ΔT_eff)"),
       (f"{phx_bus['wbgt']:.1f} °C", "proxy WBGT, below the 30 °C reference"),
       (f"{water_phx:.0f} L/kWh", "water per kilowatt-hour of electricity"),
       (f"${phx_bus['lcc']:.0f} /yr", "annualised life-cycle cost")])
panel(5.05, TEAL, "Hong Kong — humid-hot (32.5 °C, 78% RH)", "Recommended: 1× 36-inch pure fan per bus shelter",
      [(f"{hk_bus_fan['dT']:.2f} °C", "effective apparent cooling (ΔT_eff)"),
       (f"+{ratio:.0f}%", f"more cooling than the evaporative option ({hk_bus_37['dT']:.2f} °C)"),
       ("0 L", f"water, versus {water_hk:.0f} L/kWh for evaporative cooling"),
       (f"${hk_bus_fan['lcc']:.0f} /yr", "annualised life-cycle cost")])
ax.text(5.0, 0.02, "Model values at the 30 °C reference; full-coverage and partial-coverage cases differ (see Table 4b).",
        ha="center", va="bottom", fontsize=7.6, style="italic", color="#555555")
save(fig, "fig6_infographic.png")
print("done")
