# 2026 HiMCM Problem B — 半开放公共空间冷却效率模型

本仓库收录 **2026 HiMCM Problem B** 的论文草稿、数据包、审阅意见与复算脚本，供团队多人协作使用。

> **状态：草稿 + 审阅中，不是最终提交版。**  
> 审阅发现 5 处会改变结论的问题（Q2b 双机归一化、湿球口径、28°C 阈值、备忘录与 Table 5/6 冲突、68% 交叉点），详见 [`审阅报告_数据与论文一致性.md`](审阅报告_数据与论文一致性.md)。

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
| `审阅报告_数据与论文一致性.md` | 审阅报告（Markdown，含完整 17 行数据对照表、复算表、修改顺序） |
| `2026_HiMCM_ProblemB_审阅意见_数据与论文一致性.docx` | 审阅报告（Word 版，9 页） |
| `analysis/recompute.py` | 独立复算脚本（Table 4/5/6） |
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
