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
| 6 | 章节完整 | Summary、1–6、AI Report、Figures、Appendix A | 全部存在；未完成的 4 项标 `[PLACEHOLDER]` |
| 7 | 页数 | PDF 转换 | 15 页 ≤ 25 |
| 8 | 目录页码 | 与 v0.9 PDF 实际页对照 | 已对齐（Summary 2、Sec 1 4、Sec 2 5、Sec 3 6、Sec 4 8、Sec 5 10、Sec 6 11、AI 13、Figures 14、App A 15） |
| 9 | 关键数字复算 | `analysis/recompute.py` | Table 3/4/5/6 与 `docs/tables_v2.md` 一致 |
| 10 | 参考文献 | 11 条 | APS/Phoenix 已改 2024；CLP 2026；Aqueduct 0.179；ISO 7243；NTD/Valley Metro |
| 11 | 占位页说明 | 检查每个 `[PLACEHOLDER]` 页 | 均有标题 + 写作要点 |

---

## 2. 仍未完成的内容（占位页）

| 页 | 标题 | 需要写什么 |
|---|---|---|
| 2 | Summary Sheet | 一页 350–450 词：问题、模型、3–4 个关键数字、建议、限制 |
| 4 | 1. Understanding the Problem (Q1) | 开放式冰柜的冷量外泄/热空气渗入；为什么效率不能只看能耗；引出 η 与 Eq. 1–6 |
| 13 | AI Use Report | 工具/版本/日期/用途/样例提示/核验方式；未用 AI 则明确声明 |
| 14 | Figures 1–6 | 按项目 figures 规格出图（300 DPI），替换占位符；图注保留 |

> 这 5 页（含封面/目录/附录）使 v0.9 为 15 页；补齐后预计 20–22 页，仍 ≤ 25 页。

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
- **v0.9 不是最终提交版**：Summary、Section 1、AI Report、Figures 1–6 仍是占位页；补齐后需再跑一次 `qa_check.py` 并把 TOC 页码更新。
- 中文对照未并入英文提交稿，保留在 `paper_v2/Revision_Pack_P0-P2_Bilingual.docx`；如果要做“中英合一”的团队版，可另建一份双语 master（页数会超过 25 页，仅作内部使用）。
