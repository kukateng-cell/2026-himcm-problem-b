# analysis

独立复算脚本，用于核对论文 Table 3–6 的数字与归一化口径，并生成 P0–P2 的锁定表、敏感性报告和修订包。

## 快速运行

```bash
python recompute.py                 # 默认：压力修正湿球、30°C、Set B、n=1
python recompute.py --threshold 28  # 28°C 敏感性
python recompute.py --wetbulb stull # 旧口径（Stull 海平面）
python recompute.py --norm A        # Table 3 的 Set A
python recompute.py --csv docs      # 写出 docs/numbers_v2.csv
```

- 需要 Python 3.9+；**不需要**第三方库。
- 参数取自论文 Table 2 与 P2 数据口径（见 `../docs/data_provenance.md`）。
- 输出：
  1. **Table 3** — Q2a 三套系统（Set A）；
  2. **Table 5** — 16 个情景的 ΔT_eff、φ、η、LCC、I_env、WBGT、E；
  3. **Table 4** — 1 台 vs 2 台（Set B，同一尺度）；
  4. **Table 6** — 四种 COO 权重下的最优设备与得分；
  5. RH 交叉点与关键方案 E。

## 生成文件

```bash
python build_tables_md.py      # docs/tables_v2.md
python sensitivity.py          # 单因素敏感性（终端表格）
python build_revision_pack.py  # paper_v2/Revision_Pack_P0-P2_Bilingual.docx
python extras.py               # γ/RH/宽减/2026 情景的附加数字
```

## 口径说明

- **D1**：Set A（Q2a，Table 3）与 Set B（Q2b–Q4，Table 4–6）分开；E 只在同一集合内可比。
- **D2**：默认压力修正湿球（Phoenix 950 hPa、HK 1000 hPa）；`--wetbulb stull` 复现旧口径。
- **D3**：默认 30°C；`--threshold 28` 为未适应人群敏感性。
- **D4**：1 台/2 台同尺度；2 台不再自动更优。

## 已知差异（与旧稿）

- 旧稿 Table 4 的 1 台行用 16 情景基准、2 台行用“两台子集”基准；本脚本统一为 Set B，2 台 E 下降。
- 旧稿 Table 2 的 Phoenix 湿球 21.8°C 与模型 22.63°C 不一致；本脚本统一为 21.79°C（950 hPa）。
- 旧稿 HK BWS 0.850、EF 0.465、Phoenix 电价 0.1247；本脚本改为 0.179、0.39、0.1595（见 `../docs/data_provenance.md`）。

## 文件

- `recompute.py` — 主模型与表格。
- `sensitivity.py` — 单因素敏感性。
- `build_tables_md.py` — 生成锁定表。
- `build_revision_pack.py` — 生成中英修订包。
- `extras.py` — γ/RH/宽减/2026 情景。
