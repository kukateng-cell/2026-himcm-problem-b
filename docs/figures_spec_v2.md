# Figures 1–6 重绘说明（2026-11-15 锁定数据）

**用途：** 让任何绘图工具/同事按本文件重画，保证与论文 Table 3–6、备忘录、附录一致。
**数据来源：** `analysis/recompute.py`（`--wetbulb pressure --threshold 30 --norm B`）；机器可读版 `docs/numbers_v2.csv`。
**通用要求：** 300 dpi；成品宽约 16 cm（单张图 ≤ 17.5 cm）；英文标题与图注用衬线体（Times New Roman / STIX）；坐标轴与图例字号 ≥ 8 pt。
**配色：** 蓝 `#2f5aa8`、橙 `#d9731a`、青 `#1f8a70`、紫 `#6a4c93`、绿 `#2e9e6b`。
**禁止出现：** `kW/hr`、`0.3011`、`0.3410`、`28.14`、`63–70%`、`28 °C` 作为主阈值、`per 1 kWh` 这类论文没有定义的指标。

## Figure 1 — System boundary and Eq. 1→6 coupling

**版式：** 左右两栏（沿用现有示意图，不需要改数字）。

- 左栏剖面：Cooler → 冷射流（`ΔT_phys, v_eff`）→ `N_eff` 人；右侧 `Lateral escape γ` 与 `Ambient heat entrainment`；底部 `Target Coverage A_cov (φ = A_cov/A_zone)`。
- 左栏脚注：`γ = 0.55 (bus shelter) / 0.30 (rail station)`。
- 右栏流程：Eq. 1（wet-bulb limit, `ΔT_phys`）→ Eq. 2（Steadman apparent, `ΔT_eff`）→ Eq. 3（η）→ Eq. 4（`LCC_annual`）；Eq. 3 虚线指向 Eq. 6（WBGT safety + E）；Eq. 5（`I_env`）→ Eq. 6；Eq. 4 → Eq. 6。
- 右栏底部条：`Thermodynamics (Eq. 1–3) → Economics & Externality (Eq. 4–5) → Safety & Decision (Eq. 6)`。

**英文图注：** Figure 1. System boundary and Eq. 1→6 coupling. Left: semi-open venue cross-section with the cold jet, lateral escape γ and coverage φ. Right: the Eq. 1→2→3→(4,5)→6 chain.

## Figure 2 — Q2a efficiency paradox and Q2b scaling

### (a) Q2a：Systems A/B/C（Phoenix bus shelter, Set A）

| System | 功率 P (kW) | 柱：ΔT_eff (°C) | 线：η (persons·°C/kW) |
|---|---:|---:|---:|
| A | 0.25 | **2.230** | **53.52** |
| B | 1.20 | **2.665** | **13.33** |
| C | 2.50 | **3.832** | **9.20** |

- 柱用蓝色，线用橙色圆点；双 y 轴：左轴 `Effective apparent cooling ΔT_eff (°C)` 0–5.2；右轴 `Cooling efficiency η (persons·°C/kW)` 0–72。
- 数值标注直接写在柱顶/点旁（三位小数）。
- 标题示例：`(a) Q2a efficiency paradox: power vs marginal return`。

### (b) Q2b：1× vs 2×（Phoenix rail, A_zone = 120 m², Set B）

| 设备 | 1× E | 1× φ | 2× E | 2× φ |
|---|---:|---:|---:|---:|
| Hessaire MC37V | **0.4051** | 0.733 | **0.3708** | 1.000 |
| Hessaire MC61V | **0.4093** | 1.000 | **0.2193** | 1.000 |
| Portacool 220 | **0.2888** | 0.542 | **0.2526** | 1.000 |

- 每组两根柱：1× 浅蓝灰、2× 深青；y 轴 `Composite evaluation score E`，0–0.50。
- 柱顶写 `E = x.xxxx` 与 `(φ = 0.xx)` 两行。
- 标题示例：`(b) Q2b multi-unit scaling (A_zone = 120 m², Phoenix rail)`。

**英文图注：** Figure 2. Q2a efficiency paradox and Q2b scaling. Left: Systems A/B/C, bars = ΔT_eff, line = η. Right: 1× vs 2× deployment of MC37V, MC61V and Portacool at a 120 m² Phoenix platform, annotated with E and φ.

## Figure 3 — RH crossover at 41 °C

两条 MC37V 曲线 + 一条风扇水平线；41 °C、950 hPa。

| RH (%) | ΔT_eff, bus shelter (γ=0.55) | ΔT_eff, rail station (γ=0.30) | Drum fan 36" |
|---:|---:|---:|---:|
| 10 | 4.39 | 6.53 | 2.08 |
| 20 | 4.39 | 6.53 | 2.08 |
| 30 | 4.39 | 6.53 | 2.08 |
| 40 | 4.03 | 5.97 | 2.08 |
| 50 | 3.31 | 4.85 | 2.08 |
| 60 | 2.65 | 3.84 | 2.08 |
| 70 | 2.06 | 2.91 | 2.08 |
| 80 | 1.51 | 2.05 | 2.08 |
| 90 | 1.00 | 1.26 | 2.08 |

- 曲线在 RH 低于约 35% 时是**平的**：ΔT_phys 被 ΔT_nom = 11 °C 截顶，不是画错。
- 交叉点（论文值）：bus **69.6%**、rail **79.7%**；风扇恒为 2.081 °C。
- 竖虚线：Phoenix RH = 18%（橙）、Hong Kong RH = 78%（青），并在图上标 RH=18/78 文字。
- 轴：x 10–90%，y 0–6.4 °C；图例三行（bus / rail / fan）。
- 交叉点用圆点/菱形标出，不要写“63–70%”这种区间。

**英文图注：** Figure 3. RH crossover at 41 °C. MC37V in a bus shelter (γ = 0.55) crosses the drum-fan line at about 69.6% RH, the rail station (γ = 0.30) at about 79.7%; dotted lines mark Phoenix (18%) and Hong Kong (78%).

## Figure 4 — LCC vs I_env trade-off（30 °C 基准）

16 个情景（去重后 8 个不同 LCC–I_env 坐标）：

| ID | City | Venue | Equipment | LCC (USD/yr) | I_env | WBGT (°C) | E |
|---|---|---|---|---:|---:|---:|---:|
| SC-01 | PHX | bus | MC37V | 200.56 | 0.2811 | 26.13 | 0.3866 |
| SC-02 | PHX | bus | MC61V | 323.71 | 0.4831 | 26.13 | 0.3111 |
| SC-03 | PHX | bus | Porta | 346.83 | 0.3685 | 26.13 | 0.3281 |
| SC-04 | PHX | bus | Fan | 131.52 | 0.1897 | 27.55 | 0.3193 |
| SC-05 | PHX | rail | MC37V | 200.56 | 0.2811 | 25.33 | 0.4051 |
| SC-06 | PHX | rail | MC61V | 323.71 | 0.4831 | 25.33 | 0.4093 |
| SC-07 | PHX | rail | Porta | 346.83 | 0.3685 | 25.33 | 0.2888 |
| SC-08 | PHX | rail | Fan | 131.52 | 0.1897 | 27.55 | 0.2836 |
| SC-09 | HK | bus | MC37V | 181.36 | 0.1541 | 29.79 | 0.2840 |
| SC-10 | HK | bus | MC61V | 290.75 | 0.2650 | 29.79 | 0.2307 |
| SC-11 | HK | bus | Porta | 326.32 | 0.2367 | 29.79 | 0.2268 |
| SC-12 | HK | bus | Fan | 131.90 | 0.2035 | 30.15 | 0.3090 |
| SC-13 | HK | rail | MC37V | 181.36 | 0.1541 | 29.59 | 0.2837 |
| SC-14 | HK | rail | MC61V | 290.75 | 0.2650 | 29.59 | 0.2547 |
| SC-15 | HK | rail | Porta | 326.32 | 0.2367 | 29.59 | 0.2085 |
| SC-16 | HK | rail | Fan | 131.90 | 0.2035 | 30.15 | 0.2733 |

- 形状：Phoenix 圆点、Hong Kong 三角；颜色：WBGT ≤ 30 °C 绿色、> 30 °C 橙色。
- 轴：x `LCC_annual (USD/yr)` 100–400（数据只到 346.83；旧图的 720 会显得很空）；y `I_env` 0.1–1.0。
- 标注：在 Phoenix 的 4 个点上标 MC37V / MC61V / Portacool / Drum fan；**不要**用 28.14 或 28 °C。
- 图例：形状 + 颜色各四项。

**英文图注：** Figure 4. LCC vs I_env trade-off. Sixteen scenarios collapse to eight distinct cost–externality pairs (bus and rail share LCC and I_env); marker shape = city, colour = WBGT pass/fail at 30 °C.

## Figure 5 — γ sweep and winner matrix

### 左：η vs γ（Phoenix bus shelter, MC37V）

| γ | η (persons·°C/kW) |
|---:|---:|
| 0.20 | **177.42** |
| 0.25 | **167.12** |
| 0.30 | **156.81** |
| 0.35 | **146.51** |
| 0.40 | **136.21** |
| 0.45 | **125.90** |
| 0.50 | **115.60** |
| 0.55 | **105.30** |
| 0.60 | **94.99** |
| 0.65 | **84.69** |
| 0.70 | **74.39** |
| 0.75 | **64.09** |

- 两条竖线 γ = 0.30（rail）与 γ = 0.55（bus）；x 0.20–0.75，y 约 60–185。
- 不要画 43→10 的旧曲线（那是错的口径）。

### 右：4×4 权重 × 城市/场地 最优设备

| Profile | Phoenix bus | Phoenix rail | HK bus | HK rail |
|---|---|---|---|---|
| Balanced | MC37V (0.3866) | MC61V (0.4093) | Fan (0.3090) | MC37V (0.2837) |
| Safety | MC37V (0.5317) | MC61V (0.5569) | Fan (0.4591) | MC37V (0.4433) |
| Cost | MC37V (0.1615) | MC37V (0.1738) | Fan (0.1424) | Fan (0.1186) |
| Eco | MC37V (0.1639) | MC37V (0.1762) | Fan (0.1384) | MC37V (0.1360) |

- 热图格子写 `E 值 + 设备名`；按设备着色（MC37V 蓝 / MC61V 紫 / Portacool 青 / Fan 橙）。
- 注意：**Balanced 的 HK rail 是 MC37V**，不是 Fan。

**英文图注：** Figure 5. γ sweep and weight matrix. Left: η vs γ (0.20–0.75) for the Phoenix bus shelter with MC37V; dashed lines at γ = 0.30 and 0.55. Right: best unit and its score for each COO weight profile and city–venue.

## Figure 6 — Public infographic

两栏对比（不要方程，不要 `per 1 kWh`）：

| 项目 | Phoenix（41 °C / 18% RH） | Hong Kong（32.5 °C / 78% RH） |
|---|---|---|
| 推荐 | 1× MC37V per bus shelter | 1× 36-inch pure fan per bus shelter |
| 体感降温 ΔT_eff | **4.39 °C** | **2.08 °C**（蒸冷仅 1.47 °C，风扇高 42%） |
| WBGT | **26.13 °C**（< 30 °C 基准） | **30.15 °C**（30 °C 基准处略超，需配合遮阳） |
| 耗水 | **42 L/kWh** | **0 L**（蒸冷为 42 L/kWh） |
| 年成本 | **$200.56** | **$131.90** |

- 底部规则条：`shade → windbreak → machine`；脚注：`Model values at the 30 °C reference; partial coverage leaves the uncovered zone at ambient WBGT (see Table 4b).`
- **不要把 26.7 °C 或 “< 28 °C” 写进去**：Phoenix 是 26.13 °C，基准是 30 °C。

**英文图注：** Figure 6. Public-facing infographic: Phoenix and Hong Kong side by side (felt cooling, water, cost, and the shade → windbreak → machine rule), no equations.

## 与旧图（2026-11-15 前）的差异清单

| 位置 | 旧值（不要再用） | 新值（本文件） |
|---|---|---|
| Fig 2(a) System B | ΔT_eff 3.120 °C、η 15.60 | **2.665 °C、13.33** |
| Fig 2(b) MC37V 1× | E 0.3011，φ 0.58 | **0.4051，0.733** |
| Fig 2(b) MC37V 2× | E 0.3410 | **0.3708** |
| Fig 2(b) Portacool 1× / 2× | 0.2785 / 0.3120，φ 0.65 | **0.2888 / 0.2526，φ 0.542** |
| Fig 3 交叉点 | “≈ 63–70%” | **bus 69.6%、rail 79.7%** |
| Fig 4 阈值 | 28 °C | **30 °C** |
| Fig 4 风扇 WBGT | 28.14 °C | **27.55 °C** |
| Fig 4 各点 WBGT | 26.69 / 27.10 / 27.50 | **26.13 / 25.33**（按设备/场地） |
| Fig 5 左 η 范围 | 43→10 | **约 180→62**（γ 0.20→0.75） |
| Fig 5 右 Balanced HK rail | Fan | **MC37V** |
| Fig 6 温度徽标 | 26.7 °C、< 28 °C | **26.13 °C、30 °C 基准** |
