"""Monte Carlo / joint uncertainty for the v1.0 model.

Samples the uncalibrated parameters jointly, re-scores the four units at both
venues in both cities, and reports P(best unit), P(do-nothing best), E quantiles
and the probability that one option beats another.

Outputs:
  docs/monte_carlo.md
"""

import copy
import itertools
import os
import random
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recompute as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = 1000
SEED = 20261115
UNITS = ["MC37V", "MC61V", "Porta", "Fan"]
CITIES = ["PHX", "HK"]
VENUES = ["bus", "rail"]

BASE_EQ = copy.deepcopy(R.EQUIPMENT)
BASE_CITY = copy.deepcopy(R.CITY)
BASE_VENUE = copy.deepcopy(R.VENUE)


def restore():
    R.EQUIPMENT = copy.deepcopy(BASE_EQ)
    R.CITY = copy.deepcopy(BASE_CITY)
    R.VENUE = copy.deepcopy(BASE_VENUE)
    R.KAPPA = 45.0
    R.WATER_MULT = 1.0
    R.WATER_MODE = "balance"


def draw(rng):
    restore()
    R.KAPPA = rng.uniform(30, 60)
    R.VENUE["bus"]["g"] = rng.uniform(0.45, 0.65)
    R.VENUE["rail"]["g"] = rng.uniform(0.25, 0.35)
    for k, e in R.EQUIPMENT.items():
        if e["eps"] > 0:
            e["eps"] = rng.uniform(0.70, 0.90)
            e["dTnom"] = rng.uniform(8.8, 13.2)
        e["L"] *= rng.uniform(0.7, 1.3)
        e["r"] *= rng.uniform(0.5, 1.5)
        e["A"] *= rng.uniform(0.8, 1.2)
    for v in R.VENUE:
        R.VENUE[v]["N"] = R.VENUE[v]["N"] * rng.uniform(0.8, 1.2)
    R.WATER_MULT = rng.uniform(0.7, 1.3)
    for c in R.CITY:
        R.CITY[c]["pe"] *= rng.uniform(0.8, 1.2)
        R.CITY[c]["pw"] *= rng.uniform(0.8, 1.2)


def main():
    rng = random.Random(SEED)
    best = {(c, v): {u: 0 for u in UNITS} for c in CITIES for v in VENUES}
    none_best = {(c, v): 0 for c in CITIES for v in VENUES}
    escore = {}
    beats = {"PHX_rail_61_over_37": 0, "HK_rail_37_over_fan": 0, "HK_rail_37_over_61": 0}

    for i in range(N):
        draw(rng)
        g = R.set_B()
        rows = {(c, v, e): R.calc(c, v, e, 1) for c, v, e in itertools.product(CITIES, VENUES, UNITS)}
        E = {}
        for key, r in rows.items():
            E[key] = R.score(r, g, threshold=30.0)[0]
        for c in CITIES:
            for v in VENUES:
                nd = R.no_device(c, v)
                ndE = R.score(nd, g, threshold=30.0)[0]
                best_unit = max(UNITS, key=lambda u: E[(c, v, u)])
                if ndE > E[(c, v, best_unit)]:
                    none_best[(c, v)] += 1
                else:
                    best[(c, v)][best_unit] += 1
        if E[("PHX", "rail", "MC61V")] > E[("PHX", "rail", "MC37V")]:
            beats["PHX_rail_61_over_37"] += 1
        if E[("HK", "rail", "MC37V")] > E[("HK", "rail", "Fan")]:
            beats["HK_rail_37_over_fan"] += 1
        if E[("HK", "rail", "MC37V")] > E[("HK", "rail", "MC61V")]:
            beats["HK_rail_37_over_61"] += 1
        for c in CITIES:
            for v in VENUES:
                for u in UNITS:
                    escore.setdefault((c, v, u), []).append(E[(c, v, u)])
        if (i + 1) % 200 == 0:
            print("draws", i + 1)

    def q(vals, p):
        s = sorted(vals)
        k = min(len(s) - 1, max(0, int(round(p * (len(s) - 1)))))
        return s[k]

    lines = ["# 蒙特卡罗 / 联合不确定性（v1.0）\n",
             "**样本：** %d 次联合抽样，seed = %d。" % (N, SEED),
             "**抽样：** κ~U(30,60)、γ~U(0.45,0.65)/U(0.25,0.35)、ε~U(0.70,0.90)、ΔT_nom~U(8.8,13.2)、"
             "L×U(0.7,1.3)、r~U(0.5,1.5)、A_cov×U(0.8,1.2)、N_eff×U(0.8,1.2)、水耗×U(0.7,1.3)、电价/水价×U(0.8,1.2)。",
             "**模型：** `analysis/recompute.py`，每次抽样重算归一化；E 只用于同场地比较。\n",
             "## 设备胜出概率（含零设备）\n",
             "| 场地 | MC37V / MC61V / Portacool / Fan | 零设备 |",
             "|---|---|---|"]
    for c in CITIES:
        for v in VENUES:
            n = N
            row = "| %s %s | " % (c, v)
            row += " / ".join("%s %.0f%%" % (u, 100 * best[(c, v)][u] / n) for u in UNITS)
            row += " | 零设备 %.0f%% |" % (100 * none_best[(c, v)] / n)
            lines.append(row)

    lines.append("\n## E 的 P5 / P50 / P95\n")
    lines.append("| 场地/选项 | P5 | P50 | P95 |")
    lines.append("|---|---:|---:|---:|")
    for c in CITIES:
        for v in VENUES:
            for u in UNITS:
                vals = escore[(c, v, u)]
                lines.append("| %s %s %s | %.4f | %.4f | %.4f |" %
                             (c, v, u, q(vals, 0.05), q(vals, 0.5), q(vals, 0.95)))

    lines.append("\n## 关键对比概率\n")
    lines.append("- Phoenix 站台：E(MC61V) > E(MC37V) 的概率 = **%.0f%%**" % (100 * beats["PHX_rail_61_over_37"] / N))
    lines.append("- HK 站台：E(MC37V) > E(风扇) 的概率 = **%.0f%%**" % (100 * beats["HK_rail_37_over_fan"] / N))
    lines.append("- HK 站台：E(MC37V) > E(MC61V) 的概率 = **%.0f%%**" % (100 * beats["HK_rail_37_over_61"] / N))
    lines.append("\n> 结论：近差距（Phoenix 1×MC61V vs 1×MC37V；HK 1×MC37V vs 风扇）在联合不确定性下并非稳定胜出，"
                 "应报告概率而不是单一 E 排序。")
    open(os.path.join(ROOT, "docs", "monte_carlo.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("wrote docs/monte_carlo.md")


if __name__ == "__main__":
    main()
