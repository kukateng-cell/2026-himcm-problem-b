"""P1 scenarios: LCC adders (installation + labour) and multi-unit overlap.

Outputs docs/p1_scenarios.md with:
  (a) E ranking before/after adding installation amortisation and maintenance labour;
  (b) the effect of 30% jet overlap on two-unit deployments.
"""

import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recompute as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNITS = ["MC37V", "MC61V", "Porta", "Fan"]
CITIES = ["PHX", "HK"]
VENUES = ["bus", "rail"]

INSTALL = {("PHX", "bus"): 450.0, ("PHX", "rail"): 900.0, ("HK", "bus"): 450.0, ("HK", "rail"): 900.0}
INSTALL_LIFE = 10.0
LABOUR = 150.0  # USD/unit/yr
OVERLAP = 0.30


def main():
    g = R.set_B()
    rows = {k: R.calc(k[0], k[1], k[2], 1) for k in [(c, v, u) for c in CITIES for v in VENUES for u in UNITS]}
    base = {k: R.score(r, g, threshold=33.0) for k, r in rows.items()}

    # (a) cost adders
    added = {}
    for (c, v, u), r in rows.items():
        r2 = dict(r)
        r2["lcc"] = r["lcc"] + INSTALL[(c, v)] / INSTALL_LIFE + LABOUR
        added[(c, v, u)] = R.score(r2, g, threshold=33.0)

    # (b) overlap on two-unit deployments
    two = {k: R.calc(k[0], "rail", k[1], 2) for k in [(c, u) for c in CITIES for u in UNITS]}
    overlap = {}
    for (c, u), r in two.items():
        E, I, B, S = R.score(r, g, threshold=33.0)
        phi2 = min(1.0, (1 - OVERLAP) * r["phi"] * 2) if r["phi"] < 1 else 1.0
        phi2 = min(1.0, (1 - OVERLAP) * (2 * r["A_cov"] / r["Az"]))
        ss = phi2 * R.sat(r["wbgt"]) + (1 - phi2) * R.sat(r["wbgt_amb"])
        benefit = phi2 * 45 * r["dT"] / g["rail"]["B"]
        E2 = 0.30 * ss + 0.30 * benefit - 0.20 * r["lcc"] / g["rail"]["L"] - 0.20 * I
        overlap[(c, u)] = (E, E2, phi2)

    lines = ["# P1 情景：成本附加项与多台重叠（v1.0）\n",
             "## (a) 安装 + 人工维护\n",
             "假设：安装费 $450（公交亭）/ $900（站台），按 10 年摊销；维护人工 $150/台·年。",
             "LCC 只加这两项，其余不变；E 用基线归一化。\n",
             "| 场地/设备 | LCC（原） | LCC（含附加） | E（原） | E（含附加） |",
             "|---|---:|---:|---:|---:|"]
    for c in CITIES:
        for v in VENUES:
            for u in UNITS:
                r = rows[(c, v, u)]
                lines.append("| %s %s %s | %.2f | %.2f | %.4f | %.4f |" %
                             (c, v, u, r["lcc"], r["lcc"] + INSTALL[(c, v)] / INSTALL_LIFE + LABOUR,
                              base[(c, v, u)][0], added[(c, v, u)][0]))
    lines.append("\n**结论：** 加入安装与人工后，P0 的推荐是否改变见正文 5.4；本表用于展示数量级。\n")

    lines.append("## (b) 两台 30% 射流重叠\n")
    lines.append("假设：两台并排时有效覆盖降为名义并集的 70%（overlap=0.30）。\n")
    lines.append("| 城市/设备 | E（名义叠加） | E（30% 重叠） | φ（重叠后） |")
    lines.append("|---|---:|---:|---:|")
    for c in CITIES:
        for u in UNITS:
            E, E2, phi2 = overlap[(c, u)]
            lines.append("| %s %s (2×) | %.4f | %.4f | %.3f |" % (c, u, E, E2, phi2))
    lines.append("\n> 说明：重叠只影响两台方案的 φ；单台方案不变。")

    open(os.path.join(ROOT, "docs", "p1_scenarios.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("wrote docs/p1_scenarios.md")
    # console summary of whether rankings change
    for c in CITIES:
        for v in VENUES:
            b0 = max(UNITS, key=lambda u: base[(c, v, u)][0])
            b1 = max(UNITS, key=lambda u: added[(c, v, u)][0])
            print(c, v, "best before", b0, "after", b1,
                  "E", round(base[(c, v, b0)][0], 4), round(added[(c, v, b1)][0], 4))


if __name__ == "__main__":
    main()
