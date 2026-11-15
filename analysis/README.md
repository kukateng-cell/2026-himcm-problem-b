# analysis

独立复算脚本，用于核对论文 Table 3–6 的数字与归一化口径。

## 运行

```bash
python recompute.py
```

- 需要 Python 3.9+；**不需要**第三方库。
- 参数取自论文 Table 2（设备、城市、场馆）。
- 输出：
  1. **Table 5** — 16 个情景的 ΔT_eff、φ、η、LCC、I_env、WBGT、E；
  2. **Table 4** — 1 台 vs 2 台的归一化检查（16 情景基准 vs 两台子集基准）；
  3. **Table 6** — 四种 COO 权重下的最优设备与得分。

## 已知差异

- 脚本复现 Table 5/6 的误差 < 0.001（论文四舍五入）。
- Table 4 的 1 台行使用 16 情景基准，2 台行使用“MC37V/Portacool 两台子集”基准；脚本同时打印两套结果，便于看出差异。
- 论文 Table 2 的 Phoenix 湿球 21.8°C 与脚本的 Stull 22.63°C 不同：21.8 是 950 hPa 精确值，22.63 是海平面 Stull。脚本按论文模型使用 22.63；若要按 21.8 重算，把 `CITY["PHX"]["T"]` 与 `stull()` 改为压力修正版本即可。

## 文件

- `recompute.py` — 主脚本。
