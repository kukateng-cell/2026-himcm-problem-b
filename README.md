# 2026 HiMCM Problem B — 半开放公共空间冷却效率模型

本仓库收录 **2026 HiMCM Problem B** 的论文草稿、数据包、审阅意见与复算脚本，供团队多人协作使用。

> **状态：v1.5 + 评审修订（22 页，含 5.6 横风/联合工况节与 16–19 号新引用）——v1.0 重建 + P1 增强 + 2026-11-16 四轮修订（图重绘、Q2b/Q3 补写、计算核查节、附录 B、正文引用；Table 7 改按当地时间重算 828 HK / 825 PHX；memo 聚焦 Phoenix rail；28 °C 成为真实更严曲线；新增 5.7 定义敏感性；base 提升为 ISO 33 °C + HK 31.7/77，Table 3–6 与 Figures 2–6 全部重算；修正正文/表格矛盾、加入安全筛选与全成本反转、列出结构性限制）。** 面积分离、水-能平衡耗水、零设备基准、分级 WBGT proxy、κ 无量纲、按人数计收益均已落地；Summary、Section 1–6、Figures 1–6、AI Use Report、References 齐备。**队号已填（Team 19362）。** 旧版 v0.9 保留作对照。  
> **第二轮评审修订（22 页）：** 按 B 题提交清单逐条核对（7/7 齐备、5/5 覆盖）；新增 §6.3 Deployment Guidelines，参考文献顺延为 §6.4；纠正 115 W 安全分类、拆分 Q2a 风扇效率与 41 °C 部署、说明人数在 E 中抵消、NASA 横风降为情景、κ 扩至 105、耗水口径统一为 0.2845、补齐全成本网络预算 $24,222/年、解释 825 时刻缺口、补设计小时与几何说明。
> **第三轮评审修订（2026-11-16 深夜）：** 修正 §4.1 的 1.2 kW / 0.25 kW 机组错误；§6.3 “no saving” 改为“不优于不制冷”；摘要/指南/博客的“双机切换”改为“重新评估”；加入 κ≈92 明示；κ=45 投掷距离改为 7.0 m，覆盖翻转阈值改为 +0.6%（88.5 m²）；新增 Table 10b 联合工况；Table 6c 增加完整成本列；6 人改为尖峰估计；安全阈值改为建模参考。
> **第四轮补充（23 页）：** 以短段处理剩余非致命缺口——分区平均 κ（公交亭≈84、站台≈30；κ=30 时站台已由 MC37V 领先，与 Table 10b 同向）、三方案年度预算（风扇 $132、冷机 $177、双机 $243–309，双机额外 $66–177/年无法由 E 证明）、设计日与额定水耗口径披露（序列最大 WBGT 35.6/60.2 比测试的 33.5/62 更热更干，主表按额定水耗、Table 10b 为并列联合工况，非静默重算）。
> **排版修订：** Eq.1–7 改为专业排版（变量斜体、真下标/上标、分式写法），正文与表格里的 T_db、A_cov、N_eff 等全部转为真下标，^ 幂次转为上标；全文由 23 页变为 **22 页**，目录已同步（3.4→8、附录 A→21、附录 B→22）。  
> **合并对方修订：** 摘要末段改为 “Data boundaries”（两站台代表性几何、κ 无标定、WBGT 代理、31.7/77 为选定设计小时而非序列最大）；§5.5 改为“两种几何都是代表性测量 + 推荐是条件情景结果”；备忘录加入 representative platform geometry / uncalibrated κ；附录 A 五行数据登记加强（κ 无现场标定、几何非实测、湿球为心理测量估计、设计小时说明）。  
> **v1.2 格式版：** 按用户提供的 `2026_HiMCM_ProblemB_new(1).docx` 版式重排——正文 Times New Roman 10 pt、两端对齐、1.15 行距，标题黑色 14/12/11 pt，页脚 PAGE/NUMPAGES 字段，目录改为点线引导（非表格）；公式保持专业排版（变量斜体、真下标/上标）；表格压回 8 pt 控制页数，全文 **23 页**（≤25）。文件：`2026_HiMCM_ProblemB_Full_Paper_v1.2.docx/.pdf`。  
> **v1.2 定稿（模板原生格式）：** 直接基于用户手动排版稿重建：公式保持原生纯文本（不改为文本框/下标），目录保持 Word TOC 域（含 5.x 子条目），表头底纹 D9D9D9 保留；仅把表格字号压到 8 pt 以满足 25 页上限（原生 10 pt 为 27 页）。TOC 缓存页码已按实际 23 页刷新。  
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
| `docs/tables_v2.md` | 锁定数字：Table 3/4/5/6（33°C 与 28°C） |
| `docs/data_provenance.md` | P2 数据来源/假设登记表（含敏感性） |
| `docs/sensitivity_report.md` | P2 单因素敏感性、稳健结论、翻盘条件 |
| `docs/numbers_v2.csv` | 机器可读的锁定数字 |
| `docs/p4_qa_report.md` | P4 QA：旧数字残留、表/图编号、页数、TOC、占位页 |
| `paper_v2/Revision_Pack_P0-P2_Bilingual.docx` | **P1 中英替换块**：4.1–4.4、5.1–5.2、6.1–6.3 + 附录 |
| `2026_HiMCM_ProblemB_Full_Paper_v1.1.docx` | **v1.5 主稿**（21 页；P0 重建 + P1 增强 + 图重绘 + 计算核查 + 附录 B + 矛盾修正/安全筛选/成本反转 + Table 7 本地时区 + memo 单一场地 + ISO 33/HK 31.7 base） |
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

> 以下为 **2026-11-15** 审阅记录；v1.5 已把 base 提升为 **ISO 33 °C + HK 31.7/77**，最新数字见论文 Table 3–11 与 5.7。

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
