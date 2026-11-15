"""Generate the figure redraw specification (Figures 1-6) from the locked numbers.

Run: python analysis/build_figure_spec.py
Output: docs/figures_spec_v2.md
"""

import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recompute as R

R.MODE = "pressure"
R.THRESH = 30.0

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "figures_spec_v2.md")

T3, _ = R.table3_rows("pressure", 30.0)
T4, _ = R.table4_rows("pressure", 30.0)
T5, G5 = R.table5_rows("pressure", 30.0, "B")
T6 = R.table6(T5, G5, 30.0)


def find(rows, city, eq, n):
    return next(r for r in rows if r["city"] == city and r["eq"] == eq and r["n"] == n)


def t5(city, venue, eq):
    return next(r for r in T5 if r["city"] == city and r["venue"] == venue and r["eq"] == eq)


lines = []
A = lines.append

A("# Figures 1–6 重绘说明（2026-11-15 锁定数据）")
A("")
A("**用途：** 让任何绘图工具/同事按本文件重画，保证与论文 Table 3–6、备忘录、附录一致。")
A("**数据来源：** `analysis/recompute.py`（`--wetbulb pressure --threshold 30 --norm B`）；机器可读版 `docs/numbers_v2.csv`。")
A("**通用要求：** 300 dpi；成品宽约 16 cm（单张图 ≤ 17.5 cm）；英文标题与图注用衬线体（Times New Roman / STIX）；坐标轴与图例字号 ≥ 8 pt。")
A("**配色：** 蓝 `#2f5aa8`、橙 `#d9731a`、青 `#1f8a70`、紫 `#6a4c93`、绿 `#2e9e6b`。")
A("**禁止出现：** `kW/hr`、`0.3011`、`0.3410`、`28.14`、`63–70%`、`28 °C` 作为主阈值、`per 1 kWh` 这类论文没有定义的指标。")
A("")

# ------------------------------------------------------------------ fig 1
A("## Figure 1 — System boundary and Eq. 1→6 coupling")
A("")
A("**版式：** 左右两栏（沿用现有示意图，不需要改数字）。")
A("")
A("- 左栏剖面：Cooler → 冷射流（`ΔT_phys, v_eff`）→ `N_eff` 人；右侧 `Lateral escape γ` 与 `Ambient heat entrainment`；底部 `Target Coverage A_cov (φ = A_cov/A_zone)`。")
A("- 左栏脚注：`γ = 0.55 (bus shelter) / 0.30 (rail station)`。")
A("- 右栏流程：Eq. 1（wet-bulb limit, `ΔT_phys`）→ Eq. 2（Steadman apparent, `ΔT_eff`）→ Eq. 3（η）→ Eq. 4（`LCC_annual`）；Eq. 3 虚线指向 Eq. 6（WBGT safety + E）；Eq. 5（`I_env`）→ Eq. 6；Eq. 4 → Eq. 6。")
A("- 右栏底部条：`Thermodynamics (Eq. 1–3) → Economics & Externality (Eq. 4–5) → Safety & Decision (Eq. 6)`。")
A("")
A("**英文图注：** Figure 1. System boundary and Eq. 1→6 coupling. Left: semi-open venue cross-section with the cold jet, lateral escape γ and coverage φ. Right: the Eq. 1→2→3→(4,5)→6 chain.")
A("")

# ------------------------------------------------------------------ fig 2
A("## Figure 2 — Q2a efficiency paradox and Q2b scaling")
A("")
A("### (a) Q2a：Systems A/B/C（Phoenix bus shelter, Set A）")
A("")
A("| System | 功率 P (kW) | 柱：ΔT_eff (°C) | 线：η (persons·°C/kW) |")
A("|---|---:|---:|---:|")
for r in T3:
    A("| %s | %.2f | **%.3f** | **%.2f** |" % (r["eq"], r["P"], r["dT"], r["eta"]))
A("")
A("- 柱用蓝色，线用橙色圆点；双 y 轴：左轴 `Effective apparent cooling ΔT_eff (°C)` 0–5.2；右轴 `Cooling efficiency η (persons·°C/kW)` 0–72。")
A("- 数值标注直接写在柱顶/点旁（三位小数）。")
A("- 标题示例：`(a) Q2a efficiency paradox: power vs marginal return`。")
A("")
A("### (b) Q2b：1× vs 2×（Phoenix rail, A_zone = 120 m², Set B）")
A("")
A("| 设备 | 1× E | 1× φ | 2× E | 2× φ |")
A("|---|---:|---:|---:|---:|")
for eq, label in (("MC37V", "Hessaire MC37V"), ("MC61V", "Hessaire MC61V"), ("Porta", "Portacool 220")):
    a, b = find(T4, "PHX", eq, 1), find(T4, "PHX", eq, 2)
    A("| %s | **%.4f** | %.3f | **%.4f** | %.3f |" % (label, a["E"], a["phi"], b["E"], b["phi"]))
A("")
A("- 每组两根柱：1× 浅蓝灰、2× 深青；y 轴 `Composite evaluation score E`，0–0.50。")
A("- 柱顶写 `E = x.xxxx` 与 `(φ = 0.xx)` 两行。")
A("- 标题示例：`(b) Q2b multi-unit scaling (A_zone = 120 m², Phoenix rail)`。")
A("")
A("**英文图注：** Figure 2. Q2a efficiency paradox and Q2b scaling. Left: Systems A/B/C, bars = ΔT_eff, line = η. Right: 1× vs 2× deployment of MC37V, MC61V and Portacool at a 120 m² Phoenix platform, annotated with E and φ.")
A("")

# ------------------------------------------------------------------ fig 3
A("## Figure 3 — RH crossover at 41 °C")
A("")
A("两条 MC37V 曲线 + 一条风扇水平线；41 °C、950 hPa。")
A("")
A("| RH (%) | ΔT_eff, bus shelter (γ=0.55) | ΔT_eff, rail station (γ=0.30) | Drum fan 36\" |")
A("|---:|---:|---:|---:|")
city = copy.deepcopy(R.CITY["PHX"])
for rh in range(10, 91, 10):
    R.CITY["PHX"]["T"] = 41.0
    R.CITY["PHX"]["RH"] = float(rh)
    b = R.calc("PHX", "bus", "MC37V", 1, "pressure")["dT"]
    r_ = R.calc("PHX", "rail", "MC37V", 1, "pressure")["dT"]
    A("| %d | %.2f | %.2f | 2.08 |" % (rh, b, r_))
R.CITY["PHX"] = city
A("")
A("- 曲线在 RH 低于约 35% 时是**平的**：ΔT_phys 被 ΔT_nom = 11 °C 截顶，不是画错。")
A("- 交叉点（论文值）：bus **69.6%**、rail **79.7%**；风扇恒为 2.081 °C。")
A("- 竖虚线：Phoenix RH = 18%（橙）、Hong Kong RH = 78%（青），并在图上标 RH=18/78 文字。")
A("- 轴：x 10–90%，y 0–6.4 °C；图例三行（bus / rail / fan）。")
A("- 交叉点用圆点/菱形标出，不要写“63–70%”这种区间。")
A("")
A("**英文图注：** Figure 3. RH crossover at 41 °C. MC37V in a bus shelter (γ = 0.55) crosses the drum-fan line at about 69.6% RH, the rail station (γ = 0.30) at about 79.7%; dotted lines mark Phoenix (18%) and Hong Kong (78%).")
A("")

# ------------------------------------------------------------------ fig 4
A("## Figure 4 — LCC vs I_env trade-off（30 °C 基准）")
A("")
A("16 个情景（去重后 8 个不同 LCC–I_env 坐标）：")
A("")
A("| ID | City | Venue | Equipment | LCC (USD/yr) | I_env | WBGT (°C) | E |")
A("|---|---|---|---|---:|---:|---:|---:|")
for i, r in enumerate(T5, start=1):
    A("| SC-%02d | %s | %s | %s | %.2f | %.4f | %.2f | %.4f |" % (i, r["city"], r["venue"], r["eq"], r["lcc"], r["I_env"], r["wbgt"], r["E"]))
A("")
A("- 形状：Phoenix 圆点、Hong Kong 三角；颜色：WBGT ≤ 30 °C 绿色、> 30 °C 橙色。")
A("- 轴：x `LCC_annual (USD/yr)` 100–400（数据只到 346.83；旧图的 720 会显得很空）；y `I_env` 0.1–1.0。")
A("- 标注：在 Phoenix 的 4 个点上标 MC37V / MC61V / Portacool / Drum fan；**不要**用 28.14 或 28 °C。")
A("- 图例：形状 + 颜色各四项。")
A("")
A("**英文图注：** Figure 4. LCC vs I_env trade-off. Sixteen scenarios collapse to eight distinct cost–externality pairs (bus and rail share LCC and I_env); marker shape = city, colour = WBGT pass/fail at 30 °C.")
A("")

# ------------------------------------------------------------------ fig 5
A("## Figure 5 — γ sweep and winner matrix")
A("")
A("### 左：η vs γ（Phoenix bus shelter, MC37V）")
A("")
A("| γ | η (persons·°C/kW) |")
A("|---:|---:|")
base_venue = copy.deepcopy(R.VENUE["bus"])
for g in [round(0.20 + 0.05 * i, 2) for i in range(12)]:
    R.VENUE["bus"]["g"] = g
    eta = R.calc("PHX", "bus", "MC37V", 1, "pressure")["eta"]
    A("| %.2f | **%.2f** |" % (g, eta))
R.VENUE["bus"] = base_venue
A("")
A("- 两条竖线 γ = 0.30（rail）与 γ = 0.55（bus）；x 0.20–0.75，y 约 60–185。")
A("- 不要画 43→10 的旧曲线（那是错的口径）。")
A("")
A("### 右：4×4 权重 × 城市/场地 最优设备")
A("")
A("| Profile | Phoenix bus | Phoenix rail | HK bus | HK rail |")
A("|---|---|---|---|---|")
for p in ("Balanced", "Safety", "Cost", "Eco"):
    row = []
    for c, v in (("PHX", "bus"), ("PHX", "rail"), ("HK", "bus"), ("HK", "rail")):
        eq, score = T6[(p, c, v)]
        row.append("%s (%.4f)" % (eq, score))
    A("| %s | %s |" % (p, " | ".join(row)))
A("")
A("- 热图格子写 `E 值 + 设备名`；按设备着色（MC37V 蓝 / MC61V 紫 / Portacool 青 / Fan 橙）。")
A("- 注意：**Balanced 的 HK rail 是 MC37V**，不是 Fan。")
A("")
A("**英文图注：** Figure 5. γ sweep and weight matrix. Left: η vs γ (0.20–0.75) for the Phoenix bus shelter with MC37V; dashed lines at γ = 0.30 and 0.55. Right: best unit and its score for each COO weight profile and city–venue.")
A("")

# ------------------------------------------------------------------ fig 6
phx = t5("PHX", "bus", "MC37V")
hk_fan = t5("HK", "bus", "Fan")
hk_37 = t5("HK", "bus", "MC37V")
ratio = (hk_fan["dT"] / hk_37["dT"] - 1) * 100
water = 10.6 / 0.25

A("## Figure 6 — Public infographic")
A("")
A("两栏对比（不要方程，不要 `per 1 kWh`）：")
A("")
A("| 项目 | Phoenix（41 °C / 18% RH） | Hong Kong（32.5 °C / 78% RH） |")
A("|---|---|---|")
A("| 推荐 | 1× MC37V per bus shelter | 1× 36-inch pure fan per bus shelter |")
A("| 体感降温 ΔT_eff | **%.2f °C** | **%.2f °C**（蒸冷仅 %.2f °C，风扇高 %.0f%%） |" % (phx["dT"], hk_fan["dT"], hk_37["dT"], ratio))
A("| WBGT | **%.2f °C**（< 30 °C 基准） | **%.2f °C**（30 °C 基准处略超，需配合遮阳） |" % (phx["wbgt"], hk_fan["wbgt"]))
A("| 耗水 | **%.0f L/kWh** | **0 L**（蒸冷为 %.0f L/kWh） |" % (water, water))
A("| 年成本 | **$%.2f** | **$%.2f** |" % (phx["lcc"], hk_fan["lcc"]))
A("")
A("- 底部规则条：`shade → windbreak → machine`；脚注：`Model values at the 30 °C reference; partial coverage leaves the uncovered zone at ambient WBGT (see Table 4b).`")
A("- **不要把 26.7 °C 或 “< 28 °C” 写进去**：Phoenix 是 %.2f °C，基准是 30 °C。" % phx["wbgt"])
A("")
A("**英文图注：** Figure 6. Public-facing infographic: Phoenix and Hong Kong side by side (felt cooling, water, cost, and the shade → windbreak → machine rule), no equations.")
A("")

# ------------------------------------------------------------------ diff
A("## 与旧图（2026-11-15 前）的差异清单")
A("")
A("| 位置 | 旧值（不要再用） | 新值（本文件） |")
A("|---|---|---|")
A("| Fig 2(a) System B | ΔT_eff 3.120 °C、η 15.60 | **2.665 °C、13.33** |")
A("| Fig 2(b) MC37V 1× | E 0.3011，φ 0.58 | **0.4051，0.733** |")
A("| Fig 2(b) MC37V 2× | E 0.3410 | **0.3708** |")
A("| Fig 2(b) Portacool 1× / 2× | 0.2785 / 0.3120，φ 0.65 | **0.2888 / 0.2526，φ 0.542** |")
A("| Fig 3 交叉点 | “≈ 63–70%” | **bus 69.6%、rail 79.7%** |")
A("| Fig 4 阈值 | 28 °C | **30 °C** |")
A("| Fig 4 风扇 WBGT | 28.14 °C | **27.55 °C** |")
A("| Fig 4 各点 WBGT | 26.69 / 27.10 / 27.50 | **26.13 / 25.33**（按设备/场地） |")
A("| Fig 5 左 η 范围 | 43→10 | **约 180→62**（γ 0.20→0.75） |")
A("| Fig 5 右 Balanced HK rail | Fan | **MC37V** |")
A("| Fig 6 温度徽标 | 26.7 °C、< 28 °C | **26.13 °C、30 °C 基准** |")

with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("wrote", OUT)
