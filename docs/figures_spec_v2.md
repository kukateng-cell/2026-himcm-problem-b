# Figure 1–6：来源与说明（v1.0）

**状态：** v1.0 的 6 张图由代码生成，不再是"按说明手绘"的版本。

- 生成脚本：`analysis/make_figures.py`（matplotlib 3.11，300 dpi，输出到 `docs/figures/`）
- 数值来源：`analysis/recompute.py`（v1.0 模型）→ `docs/tables_v2.md` / `docs/numbers_v2.csv`
- 图注：见论文 3.1.1、4.1–4.4、5.1、6.2 各处的 "Figure N." 段落

| 文件 | 内容 | 关键数字来源 |
|---|---|---|
| fig1_system.png | 系统边界与 Eq.1→6 链（示意图） | 结构图，无数据 |
| fig2_q2a_q2b.png | Q2a 三系统；Q2b 1× vs 2× | Table 3 / Table 4 |
| fig3_rh_crossover.png | 41 °C 下 RH 交叉（bus 69.6%、rail 79.7%） | Eq.1–2；`sweep_rh` |
| fig4_pareto.png | LCC vs I_env，按 30 °C proxy 着色 | Table 5 |
| fig5_gamma_heatmap.png | η vs γ；4×4 冠军队 | Table 5 / Table 6 |
| fig6_infographic.png | 公众信息图（Phoenix vs HK） | Table 5（bus 场景） |

**重画规则：** 若手工重画，数值必须取自 `docs/tables_v2.md`（v1.0），不要沿用 2026-11-15 之前的图片或旧稿数字。
