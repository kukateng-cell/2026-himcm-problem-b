"""Generate docs/sensitivity_report.md from the fixed-denominator sensitivity run.

Run: python analysis/build_sensitivity_md.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import recompute as R
import sensitivity as S

R.MODE = "pressure"
R.THRESH = 30.0

COLS = [("PHX 1×37", ("PHX", "MC37V", 1)), ("PHX 1×61", ("PHX", "MC61V", 1)),
        ("PHX 2×37", ("PHX", "MC37V", 2)), ("HK 1×37", ("HK", "MC37V", 1)),
        ("HK 1×61", ("HK", "MC61V", 1)), ("HK 1×fan", ("HK", "Fan", 1)),
        ("HK 2×fan", ("HK", "Fan", 2))]

TITLE = """# 敏感性报告（固定分母版）

**口径：** D1–D4 + P2 数据（压力修正湿球、30 °C、Set B、APS 2024 需量电价、HK BWS 0.179、EF 0.39）。
**脚本：** `analysis/sensitivity.py`（固定基线分母；逐情境重算分母的旧结果已作废，见第 6 节）。
**基准：** `analysis/recompute.py` 的 Table 4。
**生成：** `python analysis/build_sensitivity_md.py`（本文件自动生成，勿手改数字）。

---
"""


def fmt_row(vals):
    return "| " + " | ".join("%.4f" % v for v in vals) + " |"


def main():
    g0 = R.table4_rows("pressure", R.THRESH)[1]
    base = S.metrics(g0)
    rows = {"BASE": base}
    for name, fn in S.variations():
        rows[name] = S.apply(fn, g0)

    def E(case, key):
        return rows[case][key]["E"]

    # base option table
    lines = [TITLE]
    lines.append("## 1. 基准 E（30 °C，Set B）\n")
    lines.append("| 方案 | φ | ΔT_eff | LCC | I_env | E |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for label, key in COLS:
        b = base[key]
        lines.append("| %s | %.3f | %.3f | %.2f | %.4f | **%.4f** |" % (label, b["phi"], b["dT"], b["lcc"], b["I"], b["E"]))
    lines.append("")

    # sensitivity table
    lines.append("## 2. 单因素敏感性（E 值，分母固定）\n")
    lines.append("| 变化 | " + " | ".join(c[0] for c in COLS) + " |")
    lines.append("|---|" + "---:|" * len(COLS))
    lines.append("| **BASE** | " + " | ".join("**%.4f**" % base[k]["E"] for _, k in COLS) + " |")
    for name, _ in S.variations():
        lines.append("| %s | %s |" % (name, " | ".join("%.4f" % rows[name][k]["E"] for _, k in COLS)))
    lines.append("")
    lines.append("> N_eff 只影响 η，不影响 E，故不在表中。\n")

    # key comparisons
    var_names = [n for n, _ in S.variations()]
    gap_phx = [(n, E(n, ("PHX", "MC61V", 1)) - E(n, ("PHX", "MC37V", 2))) for n in var_names]
    gap_hk = [(n, E(n, ("HK", "MC37V", 1)) - E(n, ("HK", "Fan", 2))) for n in var_names]
    min_phx = min(gap_phx, key=lambda x: x[1])
    min_hk = min(gap_hk, key=lambda x: x[1])
    fan_over_37 = [(n, E(n, ("HK", "Fan", 1)), E(n, ("HK", "MC37V", 1))) for n in var_names
                   if E(n, ("HK", "Fan", 1)) > E(n, ("HK", "MC37V", 1))]

    lines.append("## 3. 稳健结论（固定分母）\n")
    lines.append("### 3.1 2 台方案在所有单因素变化下都不占优\n")
    lines.append("- **Phoenix 1× MC61V vs 2× MC37V**：27 个情景中 1× MC61V 全部高于 2× MC37V；最小差距 **+%.3f**（%s：%.4f vs %.4f）。"
                 % (min_phx[1], min_phx[0], E(min_phx[0], ("PHX", "MC61V", 1)), E(min_phx[0], ("PHX", "MC37V", 2))))
    lines.append("- **HK 1× MC37V vs 2× Drum Fan**：全部高于 2× 风扇；最小差距 **+%.3f**（%s）。"
                 % (min_hk[1], min_hk[0]))
    lines.append("- **结论：** “2 台提升 E” 不成立；全覆盖优先 **1× MC61V**。\n")

    lines.append("### 3.2 HK 站台：1× MC37V 与 1× Drum Fan 是接近平手\n")
    lines.append("- 基准：MC37V %.4f vs Fan %.4f（差 %.4f）。" % (base[("HK", "MC37V", 1)]["E"], base[("HK", "Fan", 1)]["E"], base[("HK", "MC37V", 1)]["E"] - base[("HK", "Fan", 1)]["E"]))
    lines.append("- 风扇反超 MC37V 的情景：%s。" % ("；".join("%s（fan %.4f vs %.4f）" % (n, a, b) for n, a, b in fan_over_37) or "无"))
    lines.append("- **结论：** HK 站台写成“两方案接近，按覆盖率/成本取舍”，不写“蒸冷全面失败”。\n")

    lines.append("### 3.3 Phoenix：覆盖率决定 1× MC37V 与 1× MC61V 的取舍\n")
    a_lo, a_hi = "A_cov -20%", "A_cov +20%"
    lines.append("- 基准：MC61V %.4f vs MC37V %.4f。" % (E("BASE", ("PHX", "MC61V", 1)), E("BASE", ("PHX", "MC37V", 1))))
    lines.append("- A_cov −20%%：MC61V %.4f vs MC37V %.4f；A_cov +20%%：MC61V %.4f vs MC37V %.4f。"
                 % (E(a_lo, ("PHX", "MC61V", 1)), E(a_lo, ("PHX", "MC37V", 1)),
                    E(a_hi, ("PHX", "MC61V", 1)), E(a_hi, ("PHX", "MC37V", 1))))
    lines.append("- **结论：** 要求 100% 覆盖选 1× MC61V；接受 73% 覆盖、优先成本/节水选 1× MC37V。\n")

    lines.append("### 3.4 阈值 28/30\n")
    lines.append("- 30 °C：PHX 全部达标；HK 蒸冷冷却区达标、风扇 30.15 °C 超标。")
    lines.append("- 28 °C：HK 全部方案超标（28 °C 行的 E 普遍下降）。Table 6b 仍把 HK 公交亭 Safety/Eco 最优从 Fan 翻成 MC37V。")
    lines.append("- 28 °C 行（固定分母）：HK 1×37 %.4f、HK 1×fan %.4f、HK 2×fan %.4f。\n"
                 % (E("threshold=28", ("HK", "MC37V", 1)), E("threshold=28", ("HK", "Fan", 1)), E("threshold=28", ("HK", "Fan", 2))))

    lines.append("### 3.5 数据年份与 BWS\n")
    lines.append("- HK BWS 0.850（旧值）：HK 1×37 %.4f vs fan %.4f，排序不变。"
                 % (E("BWS_HK=0.850", ("HK", "MC37V", 1)), E("BWS_HK=0.850", ("HK", "Fan", 1))))
    lines.append("- EF 0.465（旧值）：HK 1×37 %.4f；EF_PHX 0.25/0.36：PHX 1×61 %.4f / %.4f，排序不变。\n"
                 % (E("EF_HK=0.465", ("HK", "MC37V", 1)),
                    E("EF_PHX=0.25", ("PHX", "MC61V", 1)), E("EF_PHX=0.36", ("PHX", "MC61V", 1))))

    lines.append("## 4. 什么情况下结论会变\n")
    lines.append("1. **κ_jet ≥ ~60**：HK 站台 1× 风扇反超 1× MC37V（κ=60：fan %.4f vs %.4f）。" % (E("kappa=60", ("HK", "Fan", 1)), E("kappa=60", ("HK", "MC37V", 1))))
    lines.append("2. **MC37V 实际覆盖 > ~105 m²**：A_cov +20%% 时 PHX 1×37 %.4f > 1×61 %.4f。" % (E(a_hi, ("PHX", "MC37V", 1)), E(a_hi, ("PHX", "MC61V", 1))))
    lines.append("3. **Drum Fan 性能明显更好**（CFM↑、价格↓、功率↓）：HK 公交亭/站台可能偏向风扇；当前是 hypothetical benchmark。")
    lines.append("4. **28 °C 作为主口径**：HK 公交亭 Safety/Eco 翻成 MC37V；HK 站台仍 MC37V。")
    lines.append("5. **HK BWS 回到 0.850**：不改变 HK 站台排序，但削弱蒸冷环境优势。\n")

    g_min = min(gap_phx, key=lambda x: x[1])[1]
    g_max = max(gap_phx, key=lambda x: x[1])[1]
    lines.append("## 5. 建议写进论文的不确定性段落\n")
    lines.append(
        "> The ranking of the two full-coverage Phoenix options (1× MC61V vs 2× MC37V) is robust to "
        "±30%% changes in lifetime, maintenance, water use, prices, EF, BWS and γ: 1× MC61V remains higher "
        "by %.3f–%.3f E-points. The Hong Kong rail-station choice between one MC37V and one drum fan is a "
        "near-tie (E %.4f vs %.4f); it flips when the jet-mixing coefficient is raised from 45 to 60 s/m "
        "(fan %.4f vs %.4f). The bus-shelter fan recommendation is robust at 30 °C but becomes MC37V under "
        "the stricter 28 °C non-acclimatised limit. All sensitivity runs hold the baseline normalisers fixed.\n"
        % (g_min, g_max,
           base[("HK", "MC37V", 1)]["E"], base[("HK", "Fan", 1)]["E"],
           E("kappa=60", ("HK", "Fan", 1)), E("kappa=60", ("HK", "MC37V", 1))))

    lines.append("## 6. 与旧版（逐情境重算分母）的差异\n")
    lines.append("- 旧版 `sensitivity.py` 在每个情景里重新计算 ΔT_max/LCC_max/E_CO2,max/W_eq,max，导致“成本上升”时 E 可能反而上升。")
    lines.append("- 典型例：L_life −30%% 使 PHX 1×61 年成本 $323.71 → **$375.91**；旧版 E 0.4093 → **0.4119**（上升），固定分母后 → **%.4f**（下降，符合成本方向）。" % E("L_life -30%", ("PHX", "MC61V", 1)))
    lines.append("- 旧报告中的全部 E 数值与“稳健性”表述作废；以本表为准（论文 5.1 已同步说明）。")

    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "sensitivity_report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
