"""Generate docs/tables_v2.md from the v1.0 model (analysis/recompute.py)."""

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
    parts.append("# 锁定数字表 v1.0（重建版）\n")
    parts.append("口径：压力修正湿球（Phoenix 950 hPa / HK 1000 hPa）、30 °C 参考、"
                 "近似 WBGT proxy、按场地（bus / rail）分别归一化、耗水由水-能平衡推导。\n")
    parts.append("生成脚本：`analysis/build_tables_md.py`（依赖 `analysis/recompute.py`）。\n")
    parts.append("E 只用于同场地内比较（bus 与 bus、rail 与 rail），不跨场地比较。\n")

    parts.append("\n## 归一化基准（按场地）\n")
    parts.append("| 场地 | N_eff | B_max (persons·°C) | LCC_max | E_CO2,max | W_eq,max |")
    parts.append("|---|---:|---:|---:|---:|---:|")
    for venue, label in (("bus", "Bus shelter"), ("rail", "Rail platform")):
        g = g5[venue]
        parts.append("| %s | %d | %.2f | %.2f | %.1f | %.1f |" %
                     (label, R.VENUE[venue]["N"], g["B"], g["L"], g["E"], g["W"]))

    parts.append("\n## Table 3（Q2a，Phoenix 公交亭，30 °C）\n")
    parts.append(md_table(
        ["System", "P (kW)", "ΔT_eff (°C)", "φ", "η (pers·°C/kW)", "LCC (USD/yr)", "WBGT proxy", "E"],
        [[r["eq"], r["P"], r["dT"], r["phi"], r["eta"], r["lcc"], r["wbgt"], r["E"]] for r in t3],
        [None, "%.3f", "%.3f", "%.3f", "%.2f", "%.2f", "%.2f", "%.4f"]))

    parts.append("\n## Table 4（Q2b，rail，1 vs 2 台，30 °C）\n")
    parts.append(md_table(
        ["City", "Equipment", "n", "φ", "ΔT_eff (°C)", "LCC (USD/yr)", "WBGT proxy", "S_safe", "E"],
        [[r["city"], r["eq"], r["n"], r["phi"], r["dT"], r["lcc"], r["wbgt"], r["S_safe"], r["E"]] for r in t4],
        [None, None, "%d", "%.3f", "%.3f", "%.2f", "%.2f", "%.3f", "%.4f"]))

    parts.append("\n## Table 5（Q3，16 情景，30 °C）\n")
    parts.append(md_table(
        ["ID", "City", "Venue", "Equipment", "ΔT_eff", "φ", "η", "LCC", "I_env", "WBGT proxy", "E"],
        [["SC-%02d" % (i + 1), r["city"], r["venue"], r["eq"], r["dT"], r["phi"], r["eta"],
          r["lcc"], r["I_env"], r["wbgt"], r["E"]] for i, r in enumerate(t5)],
        [None, None, None, None, "%.3f", "%.3f", "%.2f", "%.2f", "%.4f", "%.2f", "%.4f"]))

    parts.append("\n## 零设备基准\n")
    parts.append("| 场地 | WBGT proxy | S_safe | E（do nothing） |")
    parts.append("|---|---:|---:|---:|")
    for city in R.CITY:
        for venue in R.VENUE:
            nd = R.no_device(city, venue)
            E, _, _, s = R.score(nd, g5, threshold=30.0)
            parts.append("| %s %s | %.2f | %.3f | %.4f |" % (city, venue, nd["wbgt_amb"], s, E))

    parts.append("\n## Table 6（COO 权重，30 °C）\n")
    parts.append("| Profile | Phoenix Bus | Phoenix Rail | HK Bus | HK Rail |")
    parts.append("|---|---|---|---|---|")
    for name in ["Balanced", "Safety", "Cost", "Eco"]:
        row = [name]
        for city in ["PHX", "HK"]:
            for venue in ["bus", "rail"]:
                eq, E = t6_30[(name, city, venue)]
                row.append("%s (%.4f)" % (eq, E))
        parts.append("| " + " | ".join(row) + " |")

    parts.append("\n## Table 6b（28 °C 压力测试）\n")
    parts.append("| Profile | Phoenix Bus | Phoenix Rail | HK Bus | HK Rail |")
    parts.append("|---|---|---|---|---|")
    for name in ["Balanced", "Safety", "Cost", "Eco"]:
        row = [name]
        for city in ["PHX", "HK"]:
            for venue in ["bus", "rail"]:
                eq, E = t6_28[(name, city, venue)]
                row.append("%s (%.4f)" % (eq, E))
        parts.append("| " + " | ".join(row) + " |")

    parts.append("\n## 关键对比（30 °C）\n")
    def e(city, eq, n):
        return next(r for r in t4 if r["city"] == city and r["eq"] == eq and r["n"] == n)
    p37, p61, p2, h37, h61, hf, h2f = (e("PHX", "MC37V", 1), e("PHX", "MC61V", 1),
                                        e("PHX", "MC37V", 2), e("HK", "MC37V", 1),
                                        e("HK", "MC61V", 1), e("HK", "Fan", 1),
                                        e("HK", "Fan", 2))
    parts.append("| 对比 | A | B | 结论 |")
    parts.append("|---|---|---|---|")
    parts.append("| Phoenix 全覆盖 | 1×MC61V %.4f | 2×MC37V %.4f | 1×MC61V 胜 |" % (p61["E"], p2["E"]))
    parts.append("| Phoenix 部分覆盖 | 1×MC37V %.4f | 1×MC61V %.4f | 全覆盖略高，差 %.4f |" % (p37["E"], p61["E"], p61["E"] - p37["E"]))
    parts.append("| 2 台是否可能更优 | 1×Portacool %.4f | 2×Portacool %.4f | 2 台可补覆盖缺口（新结论） |" % (
        e("PHX", "Porta", 1)["E"], e("PHX", "Porta", 2)["E"]))
    parts.append("| HK 站台 | 1×MC37V %.4f | 1×MC61V %.4f | 接近；MC37V 略高 |" % (h37["E"], h61["E"]))
    parts.append("| HK 风扇 | 1×Fan %.4f | 2×Fan %.4f | 1 台更优 |" % (hf["E"], h2f["E"]))

    open("docs/tables_v2.md", "w", encoding="utf-8").write("\n".join(parts) + "\n")
    print("wrote docs/tables_v2.md")


if __name__ == "__main__":
    main()
