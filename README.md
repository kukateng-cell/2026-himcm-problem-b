# 2026 HiMCM Problem B — 半开放公共空间冷却效率模型

本仓库收录 **2026 HiMCM Problem B** 的论文草稿、数据包、审阅意见与复算脚本，供团队多人协作使用。

> **状态：v1.1（18 页）——v1.0 重建 + 评审 P1 增强（逐时气象、蒙特卡罗、成本附加、重叠情景）+ 2026-11-16 修订（图 1 重绘、图 3 双面板、Q2b/Q3 补写、验证节、附录 B、正文引用）。** 面积分离、水-能平衡耗水、零设备基准、分级 WBGT proxy、κ 无量纲、按人数计收益均已落地；Summary、Section 1–6、Figures 1–6、AI Use Report、References 齐备。**队号已填（Team 19362）。** 旧版 v0.9 保留作对照。  
> 审阅发现 5 处会改变结论的问题（Q2b 双机归一化、湿球口径、28°C 阈值、备忘录与 Table 5/6 冲突、68% 交叉点），详见 [`审阅报告_数据与论文一致性.md`](审阅报告_数据与论文一致性.md)。  
> **P0–P2 产物：** [`docs/model_decisions.md`](docs/model_decisions.md)（D1–D4）、[`docs/tables_v2.md`](docs/tables_v2.md)（锁定数字）、[`docs/data_provenance.md`](docs/data_provenance.md)（来源/假设）、[`docs/sensitivity_report.md`](docs/sensitivity_report.md)（敏感性）、[`paper_v2/Revision_Pack_P0-P2_Bilingual.docx`](paper_v2/Revision_Pack_P0-P2_Bilingual.docx)（中英替换块）。  
> **整合稿：** [`2026_HiMCM_ProblemB_Full_Paper_v0.9.docx`](2026_HiMCM_ProblemB_Full_Paper_v0.9.docx) / [`.pdf`](2026_HiMCM_ProblemB_Full_Paper_v0.9.pdf)（v1.0，19 页：重建模型 + 新表格 + 新图；v0.9 为旧版，仅作对照）。  
> **P4 QA：** [`docs/p4_qa_report.md`](docs/p4_qa_report.md)。  
> **下一步（P3）：** 填 Summary、Section 1、AI Report、Figures 1–6，再跑 `analysis/qa_check.py` 并更新 TOC 页码。

---

## 1. 快速开始

```bash
git clone https://github.com/kukateng-cell/2026-himcm-problem-b.git
cd 2026-himcm-problem-b
```

- 论文：用 Word 打开 `*.docx`（中英对照，Part I English / Part II 中文）。
- 数据：`蒸发冷却研究资料统整_全部保留并新增凤凰城.xlsx` 约 **97 MB**，含 28 个工作表（Aqueduct 全量明细、ERA5 气象、电价/水费 PDF 文本、轻铁 CSV 等）；首次打开较慢。
- 复算：`python analysis/recompute.py`（纯 Python，无第三方依赖），可复现论文 Table 5、Table 6 与 Table 4 的归一化检查。

---

## 2. 文件地图

| 文件 | 内容 |
|---|---|
| `2026_HiMCM_Problem_B_副本.pdf` | 题面（Problem B: Air Conditioning the Environment） |
| `2026_HiMCM_ProblemB_Section2_and_3_Bilingual (1).docx` | Section 2 假设 + Section 3 六大公式（中英） |
| `2026_HiMCM_ProblemB_Section3_1_1_Transit_Basis_Bilingual.docx` | 3.1.1 双城路网参数依据 |
| `2026_HiMCM_ProblemB_Section4_Bilingual.docx` | Section 4 模型应用（Q2–Q4，Table 3–5） |
| `2026_HiMCM_ProblemB_Section5_Bilingual.docx` | Section 5 敏感性分析（Table 6） |
| `2026_HiMCM_ProblemB_Section6_Bilingual.docx` | Section 6 备忘录、博客、参考文献 |
| `2026_HiMCM_ProblemB_Figures_Specification_Bilingual.docx` | Figure 1–6 视觉与内容规格 |
| `2026_HiMCM_ProblemB_全篇符號說明表與核心邏輯鏈.docx` | 全篇符号表 + 公式 1→6 逻辑链 |
| `蒸发冷却研究资料统整_全部保留并新增凤凰城.xlsx` | 数据工作簿（28 个工作表） |
| `data/site_data/` | **2026-11 场地数据**：港铁轻铁班次/站台实测、Valley Metro 设计标准（424 页）/班距/SCE-DH FAQ |
| `data/literature/` | 雾化冷却试验原文与摘录（Kyogoku & Takebayashi 2023） |
| `docs/site_data_2026-11.md` | 场地数据整理与可用性评估（含“改哪些数会翻结论”的复算） |
| `docs/figures/` | Figure 1–6 的 300 dpi PNG |
| `docs/figures_spec_v2.md` | Figure 1–6 重绘说明（锁定数字、坐标、标注、图注、差异清单） |
| `docs/mist_cooling_2023.md` | Kyogoku & Takebayashi (2023) 雾化冷却试验的可用性评估 |
| `docs/hourly_scenarios.md` | 逐时气象胜出频率 |
| `docs/monte_carlo.md` | 联合不确定性 P(最优)/分位 |
| `docs/p1_scenarios.md` | 成本附加与重叠情景 |
| `analysis/build_figure_spec.py` | 生成上述重绘说明 |
| `审阅报告_数据与论文一致性.md` | 审阅报告（Markdown，含完整 17 行数据对照表、复算表、修改顺序） |
| `2026_HiMCM_ProblemB_审阅意见_数据与论文一致性.docx` | 审阅报告（Word 版，9 页） |
| `docs/model_decisions_v2.md` | **v1.0 模型口径 D7–D11**（面积分离、水-能平衡、零设备基准、WBGT proxy、κ 无量纲） |
| `ROADMAP.md` | 下一步路线图：P0 锁数字 → P1 改结论 → P2 补来源 → P3 补完整性 → P4 QA |
| `docs/model_decisions.md` | P0 的 D1–D4 决定、归一化集合、旧→新对照 |
| `docs/tables_v2.md` | 锁定数字：Table 3/4/5/6（30°C 与 28°C） |
| `docs/data_provenance.md` | P2 数据来源/假设登记表（含敏感性） |
| `docs/sensitivity_report.md` | P2 单因素敏感性、稳健结论、翻盘条件 |
| `docs/numbers_v2.csv` | 机器可读的锁定数字 |
| `docs/p4_qa_report.md` | P4 QA：旧数字残留、表/图编号、页数、TOC、占位页 |
| `paper_v2/Revision_Pack_P0-P2_Bilingual.docx` | **P1 中英替换块**：4.1–4.4、5.1–5.2、6.1–6.3 + 附录 |
| `2026_HiMCM_ProblemB_Full_Paper_v1.1.docx` | **v1.1 主稿**（18 页；P0 重建 + P1 增强 + 图重绘 + 验证节 + 附录 B） |
| `2026_HiMCM_ProblemB_Full_Paper_v1.0.docx` | v1.0（P0 重建，已被 v1.1 取代） |
| `2026_HiMCM_ProblemB_Full_Paper_v1.0.pdf` | v1.0 PDF |
| `2026_HiMCM_ProblemB_Full_Paper_v0.9.docx` | 旧版 v0.9（仅作对照，已被 v1.0 取代） |
| `2026_HiMCM_ProblemB_Full_Paper_v0.9.pdf` | 同上 PDF |
| `submission/` | **可分享快照**：v0.9 docx + pdf + 状态说明 |
| `analysis/recompute.py` | 独立复算脚本（Table 3/4/5/6，支持 --wetbulb/--threshold/--norm） |
| `analysis/sensitivity.py` | 单因素敏感性（固定基线分母；`--per-scenario` 仅作内部对照） |
| `analysis/build_sensitivity_md.py` | 生成 `docs/sensitivity_report.md`（固定分母） |
| `analysis/make_figures.py` | 生成 Figure 1–6（300 dpi，matplotlib） |
| `analysis/build_single_file.py` | 生成单档交付版 `…_AllInOne.docx` |
| `analysis/hourly_scenarios.py` | 逐时 ERA5 情景（828 h/城市） |
| `analysis/monte_carlo.py` | 1000 次联合不确定性抽样 |
| `analysis/p1_scenarios.py` | 安装/维护成本附加与 30% 射流重叠情景 |
| `analysis/build_tables_md.py` | 生成 `docs/tables_v2.md` |
| `analysis/build_revision_pack.py` | 生成 `paper_v2/Revision_Pack_P0-P2_Bilingual.docx` |
| `analysis/build_full_paper.py` | 生成整合论文 `Full_Paper_v0.9.docx` |
| `analysis/qa_check.py` | P4 自动扫描 |
| `analysis/README.md` | 复算脚本说明 |

---

## 3. 数据工作簿里有什么

- `产品规格与价格`：MC37V、MC61V、Portacool 的规格/价格（**没有** 36" Drum Fan）。
- `水费与耗水计算`：香港 4.58 + 2.92 HKD/m³；MC61V 耗水 13.8–18.4 L/h 估算。
- `来源网址与核实状态`、`来源缺口`、`全部来源网址`：每条数据的核实状态与缺口。
- `PDF来源目录` / `PDF逐页全文` / `PDF数字明细`：APS E-32、Phoenix 2024 水价卡、CLP 2026 电价表、香港运输月报 2603、NTD 90209、12th St TOD、WSD 宽减等。
- `Aqueduct地点导出` / `Aqueduct全球明细`：WRI Aqueduct 4.0，Phoenix `bws_raw = 2.482`；HKG 子流域 `bws_raw = 0.179`。
- `气象瞬时_*` / `气象辐射_*` / `凤凰城气象数据`：ERA5 2026-06-01 至 2026-08-31，0.25° 格点。
- `香港轻铁路线站点`：68 站、11 线（兆康 7 线、屯门码头 6 线）。

> **大文件提示：** 本仓库暂未启用 Git LFS。xlsx 约 97 MB，低于 GitHub 单文件 100 MiB 限制；如果后续频繁更新该文件，建议执行 `git lfs track "*.xlsx"` 并迁移。

---

## 4. 审阅结论摘要（5 处会改变结论）

1. **Q2b 双机结论是两套归一化混用**：Table 4 的 1 台行用 16 情景基准，2 台行用“本表两台子集”基准；统一尺度后 2 台反而更低（如 0.1616 vs 0.3005），且 2 台的 I_env = 1.037 > 1。备忘录 Phoenix 2× 建议证据不成立。
2. **湿球口径矛盾**：Table 2 写 21.8（950 hPa 精确值），模型用 Stull 22.63；用 21.8 风扇 WBGT = 27.56（<28），只有 22.63 才是 28.14。“风扇超标”落在公式误差内。
3. **28°C 不是 ISO 7243 的“轻度 115 W/m²”限值**：ISO 是 115 W→33°C、180 W→30°C、300 W→28°C；数据包《劳动强度》也写 28 是未适应行动限值、30 是适应 TLV。28/30 还会翻转 HK 站台最优。
4. **备忘录与 Table 5/6 冲突**：Table 6 的 HK Rail 三个权重选 MC37V；备忘录却“全面停用蒸冷”并推荐 2× 风扇，而该风扇 WBGT 30.20 > 蒸冷 29.62，E 栏空白。统一尺度下 1× MC37V 0.1708 > 2× 风扇 0.1151。
5. **68% 交叉点只对公交亭成立**：站台是 76–79%；HK 日均最高 RH 74.7%，此时站台蒸冷 2.19 > 风扇 2.08；最热 36.5°C/46% 时 4.65。

完整证据、复算表与 17 项数据对照见审阅报告。

---

## 5. 协作方式

- **邀请成员：** GitHub 仓库 → *Settings* → *Collaborators* → *Add people*（私有仓库需要对方接受邀请）。
- **分支约定（建议）：**
  - `main`：稳定稿（建议开启 branch protection，至少 1 人 review）。
  - `feature/<topic>`：每人一个分支，例如 `feature/recompute-normalization`、`feature/section1-q1`。
  - 通过 Pull Request 合并；PR 描述里写清改了哪张表/哪个数字。
- **改数字前先跑复算：** `python analysis/recompute.py`，确认新旧口径差异。
- **提交信息约定：** `docs: ...` / `data: ...` / `model: ...` / `review: ...`。

---

## 6. 建议的待办（从审阅报告来）

- [ ] 统一 E 的归一化（建议用“两台最大包络”），重算 Table 3/4/5/6，并给出 S_safe / S_comf / LCC̃ / I_env 分解。
- [ ] 湿球用气象表 `sp` 做压力修正；28°C 改为 30°C（已适应）或明确写“28°C 为未适应保守线”。
- [ ] 重算 1 台 vs 2 台，改备忘录；补 2× Drum Fan 的 E。
- [ ] 对齐 2024/2026 电价与水价；补 APS 需量费、Phoenix 商业水价/排污；补 Drum Fan 来源。
- [ ] 把 L_life、r_om、V_w、ε、ΔT_nom 标为 assumption/estimate，并做敏感性。
- [ ] 71 “facilities” 改为站台数（38–41，2024）或明确口径。
- [ ] 补 Section 1（Q1 开放式冰柜）、一页 Summary、目录、Figure 1–6 实际图片、AI 使用报告。
- [ ] 修参考文献年份（APS/Phoenix 2024）与符号表（`n_units`、`T_wb,zone`、各 max）。

---

## 7. 许可与归属

论文与数据为 2026 HiMCM Problem B 参赛材料，版权归作者所有。仓库默认私有；如需公开，请在 GitHub *Settings* → *Danger Zone* → *Change visibility* 中操作。
