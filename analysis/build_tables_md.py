"""Generate docs/tables_v2.md from recompute.py (recommended D1-D4 + P2 data)."""

import os
import recompute as R

R.MODE = "pressure"
R.THRESH = 30.0


def md_table(headers, rows, fmt=None):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        cells = []
        for i, v in enumerate(row):
            if isinstance(v, float):
                cells.append(fmt[i] % v if fmt else ("%.4f" % v))
            else:
                cells.append(str(v))
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def main():
    os.makedirs("docs", exist_ok=True)
    t3, g3 = R.table3_rows("pressure", 30.0)
    t4, g4 = R.table4_rows("pressure", 30.0)
    t5, g5 = R.table5_rows("pressure", 30.0, "B")
    t6_30 = R.table6(t5, g5, 30.0)
    t5_28, g28 = R.table5_rows("pressure", 28.0, "B")
    t6_28 = R.table6(t5_28, g28, 28.0)

    parts = []
    parts.append("# 锁定数字表 v2（P0）\n")
    parts.append("口径：压力修正湿球（Phoenix 950 hPa / HK 1000 hPa）、30°C 主阈值、"
                 "Set A（Table 3）/ Set B（Table 4–6）。\n")
    parts.append("生成脚本：`analysis/build_tables_md.py`（依赖 `analysis/recompute.py`）。\n")

    parts.append("\n## Set A / Set B 归一化基准\n")
    parts.append("| 集合 | ΔT_max | LCC_max | E_CO2,max | W_eq,max | 适用 |")
    parts.append("|---|---:|---:|---:|---:|---|")
    parts.append("| A | %.3f | %.2f | %.1f | %.1f | Table 3（Q2a） |" %
                 (g3["dT"], g3["L"], g3["E"], g3["W"]))
    parts.append("| B | %.3f | %.2f | %.1f | %.1f | Table 4–6、备忘录 |" %
                 (g5["dT"], g5["L"], g5["E"], g5["W"]))
    parts.append("\n> E 只在同一集合内可比；Table 3 的 E 不能与 Table 4–6 比大小。\n")

    parts.append("\n## Table 3（Q2a，Phoenix 公交亭，Set A）\n")
    parts.append(md_table(
        ["System", "P (kW)", "Airflow (CFM)", "ΔT_eff (°C)", "η (pers·°C/kW)", "LCC (USD/yr)", "I_env", "E"],
        [[r["eq"], r["P"], r["CFM"], r["dT"], r["eta"], r["lcc"], r["I_env"], r["E"]] for r in t3],
        [None, "%.3f", "%d", "%.3f", "%.2f", "%.2f", "%.4f", "%.4f"]))
    parts.append("\nQ2a 参数（假设）：A 0.25 kW / 2,250 CFM / ΔT_nom 0 / C 250 / L 7 / r 3%；"
                 "B 1.2 kW / 917 CFM / ΔT_nom 5 / V 15 L/h / C 750 / L 5 / r 8%；"
                 "C 2.5 kW / 1,031 CFM / ΔT_nom 8 / V 30 L/h / C 1,277 / L 5 / r 8%。"
                 "A_cov = A_zone = 15 m²，γ=0.55，N_eff=6。\n")

    parts.append("\n## Table 4（Q2b，120 m² 站台，Set B，30°C）\n")
    parts.append(md_table(
        ["City", "Equipment", "n", "φ", "ΔT_eff (°C)", "LCC (USD/yr)", "I_env", "WBGT (°C)", "E"],
        [[r["city"], r["eq"], r["n"], r["phi"], r["dT"], r["lcc"], r["I_env"], r["wbgt"], r["E"]] for r in t4],
        [None, None, "%d", "%.4f", "%.3f", "%.2f", "%.4f", "%.2f", "%.4f"]))

    parts.append("\n## Table 5（Q3，16 情景，Set B，30°C）\n")
    parts.append(md_table(
        ["ID", "City", "Venue", "Equipment", "ΔT_eff (°C)", "φ", "η", "LCC (USD/yr)", "I_env", "WBGT (°C)", "E"],
        [["SC-%02d" % (i + 1), r["city"], r["venue"], r["eq"], r["dT"], r["phi"], r["eta"],
          r["lcc"], r["I_env"], r["wbgt"], r["E"]] for i, r in enumerate(t5)],
        [None, None, None, None, "%.3f", "%.4f", "%.2f", "%.2f", "%.4f", "%.2f", "%.4f"]))

    parts.append("\n## Table 6（COO 权重，30°C 主口径）\n")
    parts.append("| Profile | Phoenix Bus | Phoenix Rail | HK Bus | HK Rail |")
    parts.append("|---|---|---|---|---|")
    for name in ["Balanced", "Safety", "Cost", "Eco"]:
        row = [name]
        for city in ["PHX", "HK"]:
            for venue in ["bus", "rail"]:
                eq, E = t6_30[(name, city, venue)]
                row.append("%s (%.4f)" % (eq, E))
        parts.append("| " + " | ".join(row) + " |")

    parts.append("\n## Table 6（28°C 敏感性口径）\n")
    parts.append("| Profile | Phoenix Bus | Phoenix Rail | HK Bus | HK Rail |")
    parts.append("|---|---|---|---|---|")
    for name in ["Balanced", "Safety", "Cost", "Eco"]:
        row = [name]
        for city in ["PHX", "HK"]:
            for venue in ["bus", "rail"]:
                eq, E = t6_28[(name, city, venue)]
                row.append("%s (%.4f)" % (eq, E))
        parts.append("| " + " | ".join(row) + " |")

    parts.append("\n## 关键对比（30°C，Set B）\n")
    parts.append("| 对比 | 选项 A | 选项 B | 结论 |")
    parts.append("|---|---|---|---|")
    def e(city, eq, n):
        return next(r for r in t4 if r["city"] == city and r["eq"] == eq and r["n"] == n)
    p37, p61, p2, h37, h61, hf, h2f = (e("PHX", "MC37V", 1), e("PHX", "MC61V", 1),
                                        e("PHX", "MC37V", 2), e("HK", "MC37V", 1),
                                        e("HK", "MC61V", 1), e("HK", "Fan", 1),
                                        e("HK", "Fan", 2))
    parts.append("| Phoenix 全覆盖 | 1×MC61V %.4f | 2×MC37V %.4f | 1×MC61V 胜 |" % (p61["E"], p2["E"]))
    parts.append("| Phoenix 最大 E | 1×MC37V %.4f | 1×MC61V %.4f | 两者接近；全覆盖选 MC61V |" % (p37["E"], p61["E"]))
    parts.append("| HK 全覆盖 | 1×MC61V %.4f | 2×Fan %.4f | 1×MC61V 胜（但 LCC 更高） |" % (h61["E"], h2f["E"]))
    parts.append("| HK 最大 E | 1×MC37V %.4f | 1×Fan %.4f | 1×MC37V 略胜（0.01 级，接近平手） |" % (h37["E"], hf["E"]))
    parts.append("| HK 全覆盖（低成本） | 1×MC37V %.4f（73%%） | 2×Fan %.4f（100%%） | 若必须 100%%，2×Fan 仍低于 1×MC61V |" % (h37["E"], h2f["E"]))

    open("docs/tables_v2.md", "w", encoding="utf-8").write("\n".join(parts) + "\n")
    print("wrote docs/tables_v2.md")


if __name__ == "__main__":
    main()
