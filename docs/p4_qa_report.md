# P4 QA 报告 — 整合论文 v0.9

**日期：** 2026-11-15  
**目标文件：** `2026_HiMCM_ProblemB_Full_Paper_v0.9.docx` / `.pdf`  
**页数：** 15 页（≤ 25 页限制；含 5 个占位页）  
**语言：** 英文提交稿（中文对照保留在 `paper_v2/Revision_Pack_P0-P2_Bilingual.docx` 与各双语 section 草稿中）

---

## 1. 检查项与结果

| # | 检查 | 方法 | 结果 |
|---|---|---|---|
| 1 | 旧数字残留 | 对 docx 全文（段落+表格）grep：0.3011、0.3410、28.14、0.1247、0.850、0.465、68% | **0 命中** |
| 2 | 旧结论残留 | grep：“do not deploy evaporative cooling at all”“2× MC37V (recommended)”“Table 7”“Figure 7” | **0 命中** |
| 3 | 2 台方案表述 | 检查所有 “2× MC37V” 上下文 | 仅出现在“not recommended / dominated / 对照”语境，无正面推荐 |
| 4 | 表格编号 | 检查 Table 1、2A、2B、2C、3、3b、4、5、6、6b、6c、A1 | 全部存在，无跳号（Table 2C / 6c / A1 已补标题） |
| 5 | 图编号 | 检查 Figure 1–6 | 全部存在为占位符；无 Figure 7 |
| 6 | 章节完整 | Summary、1–6、AI Report、Figures、Appendix A | 全部存在；未完成的 3 项标 `[PLACEHOLDER]` |
| 7 | 页数 | PDF 转换 | 15 页 ≤ 25 |
| 8 | 目录页码 | 与 v0.9 PDF 实际页对照 | 已对齐（Summary 2、Sec 1 4、Sec 2 5、Sec 3 6、Sec 4 8、Sec 5 10、Sec 6 11、AI 13、Figures 14、App A 15） |
| 9 | 关键数字复算 | `analysis/recompute.py` | Table 3/4/5/6 与 `docs/tables_v2.md` 一致 |
| 10 | 参考文献 | 14 条 | APS/Phoenix 已改 2024；CLP 2026；Aqueduct 0.179；ISO 7243；NTD/Valley Metro 2024；Valley Metro 2020 设计标准、2025 SCE/DH FAQ；CCOHS WBGT |
| 11 | 占位页说明 | 检查每个 `[PLACEHOLDER]` 页 | 均有标题 + 写作要点 |

---

## 2. 仍未完成的内容（占位页）

| 页 | 标题 | 需要写什么 |
|---|---|---|
| 2 | Summary Sheet | 一页 350–450 词：问题、模型、3–4 个关键数字、建议、限制 |
| 13 | AI Use Report | 工具/版本/日期/用途/样例提示/核验方式；未用 AI 则明确声明 |
| 14 | Figures 1–6 | 按项目 figures 规格出图（300 DPI），替换占位符；图注保留 |

> Section 1（Q1）已于 2026-11-15 写成完整论证（第 4 页），不再是占位页。剩 3 处占位 + 封面/目录/附录使 v0.9 为 15 页；补齐后预计 17–19 页，仍 ≤ 25 页。

---

## 3. 与旧稿相比的关键修正

- **Table 4**：1 台与 2 台同尺度；2 台不再提升 E。Phoenix 1× MC37V 0.4051、1× MC61V 0.4093、2× MC37V 0.3708；HK 1× MC37V 0.2837、2× Fan 0.2303。
- **Memo**：Phoenix 全覆盖改推 **1× MC61V**（不是 2× MC37V）；HK 站台 1× MC37V / 1× MC61V，不再“全面停用蒸冷”；HK 公交亭 1× Fan。
- **湿球**：压力修正（Phoenix 21.8 @950 hPa；HK 29.1 @1000 hPa）；Phoenix 风扇 WBGT 27.55（不是 28.14），删除“风扇违反 ISO 7243”。
- **阈值**：30 °C 主口径；28 °C 未适应敏感性；Table 6b 给出 28 °C 版本。
- **环境口径**：HK BWS 0.179（不是 0.850）、EF 0.39（不是 0.465）；HK 风扇 I_env 0.2035 > 蒸冷 0.1541，修正“零水=更环保”。
- **数据年份**：Phoenix 2024 / HK 2026 明确标注；Phoenix 电价 0.1595（APS E-32 含需量）。
- **站台数**：网络成本用 38 站（不是 NTD 的 71 facilities）。

---

## 4. 复现命令

```bash
python analysis/recompute.py --csv docs      # 锁定数字
python analysis/sensitivity.py               # 单因素敏感性
python analysis/build_tables_md.py           # docs/tables_v2.md
python analysis/build_revision_pack.py       # 中英替换块
python analysis/build_full_paper.py          # 整合论文 v0.9
python analysis/qa_check.py                  # 本 QA 的自动扫描
```

---

## 5. 结论

- **P4 对“英文整合稿 v0.9”通过**：数字、表格/图编号、页数、目录、参考文献均一致；旧数字与旧结论 0 残留。
- **v0.9 不是最终提交版**：Summary、AI Report、Figures 1–6 仍是占位页（Section 1 已于 2026-11-15 完成）；补齐后需再跑一次 `qa_check.py` 并把 TOC 页码更新。
- 中文对照未并入英文提交稿，保留在 `paper_v2/Revision_Pack_P0-P2_Bilingual.docx`；如果要做“中英合一”的团队版，可另建一份双语 master（页数会超过 25 页，仅作内部使用）。

---

## 6. 更新记录

- **2026-11-15 12:26 — Requirement 2a 功率单位注**：按赛事澄清（"Energy Use" 列是功率 kW，写作 kW/hr 有误），在 Table 3 下加 8.5 pt 斜体注：*Note: The “Energy Use” values in Requirement 2a are power ratings in kW (not kWh per hour); annual energy is obtained as P_elec × H_yr.* 该注在 PDF 第 8 页、Table 3 与 Table 3b 之间。数字与公式均未改动（Eq. 4/5 本来就是 kW × h）。
- 同次重导出后目录两个子条目按实际 PDF 页码修正：3.3 → 7（原记 6）、4.3 → 9（原记 8；加注后该节落到第 9 页）。其余条目不变。
- PDF 由 WPS Writer（KWPS.Application）重导出，仍为 15 页；改为 WPS 导出是环境原因（沙箱内 Word 无法创建临时工作文件），不是排版决定。若之后改用 Word 导出，请按新 PDF 复核目录页码。
- **2026-11-15 14:34 — 方案 A：场地数据并入正文**：Table 1 第 6 行、Table 2C 的 rail 行、Assumption 6、3.1.1 加入 Valley Metro 2020 设计标准与 2025 SCE/DH FAQ 依据；References 11 → 13 条；站数保留 38（2024）并在 3.1.1 注明 2026 年约 46 站；E 与结论未变（复算见 `docs/site_data_2026-11.md`）。新增文字使 3.2 从第 6 页移到第 7 页，目录已同步。
- **2026-11-15 14:45 — T01 学生回馈三项**：
  1. **Section 1（Q1）写成完整论证**（第 4 页，约 620 词，6 段）：开放式冰柜 → 有效冷却/边界损失/受益人 → 为何不能只看能耗 → 迁移到半开放候车场地 → η 与 E 的分工。
  2. **安全评分范围（D5）**：3.7 明确 S_safe 只评冷却区、E 不是平台级安全证书；4.2 新增 **Table 4b**（HK 站台 1×MC37V：33 人 29.59°C 达标 / 12 人 30.15°C 超标，28°C 两区都超标）；4.3 改写“pass”口径；5.2 加 WBGT 近似/非 ISO 合规与 CCOHS 引用（Ref 14）。**E 不变。**
  3. **敏感性固定分母（D6）**：`analysis/sensitivity.py` 改为固定基线 Set B 分母；新增 `analysis/build_sensitivity_md.py` 自动生成 `docs/sensitivity_report.md`；5.1 加说明（L_life −30% 由 0.4119 改为 0.3942）。水费宽减 E（0.2855/0.2577）与 γ 扫描不受影响。
  PDF 仍 15 页；目录页码不变；qa_check 0 命中。
