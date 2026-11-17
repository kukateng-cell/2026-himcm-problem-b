"""Hourly ERA5 scenarios for the v1.0 model.

Reads the workbook weather sheets (HK and Phoenix, 0.25 deg grid, hourly,
Jun-Aug 2026), averages the grid to a city series, converts the ERA5 UTC
valid_time to local time, restricts to the local 11:00-19:00 peak window, and
re-scores the four units at both venues for every hour.

Outputs:
  docs/hourly_scenarios.csv
  docs/hourly_scenarios.md
"""

import csv
import math
import os
import sys

import openpyxl
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recompute as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WB = os.path.join(ROOT, "蒸发冷却研究资料统整_全部保留并新增凤凰城.xlsx")

SHEETS = {"HK": "气象瞬时_数据明细", "PHX": "凤凰城气象数据"}
UNITS = ["MC37V", "MC61V", "Porta", "Fan"]
# ERA5 valid_time is UTC.  Hong Kong is UTC+8; Phoenix (MST, no DST) is UTC-7.
# The paper's peak window is local 11:00-19:00 inclusive, so convert before filtering.
TZ_OFFSET = {"HK": 8, "PHX": -7}


def es(T):
    return 6.112 * math.exp(17.67 * T / (T + 243.5))


def rh_from_dew(t2m, d2m):
    e = es(d2m)
    return max(1.0, min(99.0, 100.0 * e / es(t2m)))


def load_city(wb, sheet):
    ws = wb[sheet]
    rows = ws.iter_rows(min_row=2, values_only=True)
    by_time = {}
    for r in rows:
        if not r or r[0] is None:
            continue
        t = r[0]
        if isinstance(t, str):
            t = datetime.fromisoformat(t)
        u10, v10, d2m, t2m, sp = r[3], r[4], r[5], r[6], r[7]
        if t2m is None or d2m is None:
            continue
        acc = by_time.setdefault(t, [0.0, 0.0, 0.0, 0.0, 0.0])
        acc[0] += t2m; acc[1] += d2m; acc[2] += sp
        acc[3] += math.hypot(u10 or 0.0, v10 or 0.0); acc[4] += 1
    out = []
    for t, (st, sd, sp, sv, n) in by_time.items():
        T = st / n - 273.15
        Td = sd / n - 273.15
        v10 = sv / n
        v2 = 0.75 * v10          # log-law scaling 10 m -> 2 m
        out.append((t, T, rh_from_dew(T, Td), max(0.3, v2), sp / n / 100.0))
    out.sort()
    return out


def score_row(r, g):
    E, I, B, S = R.score(r, g, threshold=33.0)
    return E, I, B, S


def main():
    wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)
    g = R.set_B()
    base = {c: dict(R.CITY[c]) for c in R.CITY}
    recs = []
    for city, sheet in SHEETS.items():
        utc_series = load_city(wb, sheet)
        offset = timedelta(hours=TZ_OFFSET[city])
        series = [(t + offset, T, RH, v, ps) for (t, T, RH, v, ps) in utc_series]
        peak = [x for x in series
                if 11 <= x[0].hour <= 19
                and date(2026, 6, 1) <= x[0].date() <= date(2026, 8, 31)]
        print(city, "hours total", len(series), "peak (local 11-19)", len(peak))
        for t, T, RH, v, ps in peak:
            R.CITY[city].update(T=T, RH=RH, v=v, psurf=ps)
            for venue in R.VENUE:
                nd = R.no_device(city, venue)
                ndE = R.score(nd, g, threshold=33.0)[0]
                es_ = {}
                for eq in UNITS:
                    row = R.calc(city, venue, eq, 1)
                    E, I, B, S = R.score(row, g, threshold=33.0)
                    es_[eq] = (E, row)
                best_u = max(es_, key=lambda k: es_[k][0])
                best_all = "none" if ndE > es_[best_u][0] else best_u
                recs.append(dict(city=city, venue=venue, t=t, T=T, RH=RH,
                                 ndE=ndE, best_device=best_u, best_all=best_all,
                                 **{f"E_{u}": es_[u][0] for u in UNITS},
                                 **{f"wbgt_{u}": es_[u][1]["wbgt"] for u in UNITS}))
    R.CITY.update(base)

    os.makedirs(os.path.join(ROOT, "docs"), exist_ok=True)
    with open(os.path.join(ROOT, "docs", "hourly_scenarios.csv"), "w", newline="", encoding="utf-8-sig") as f:
        fields = ["city", "venue", "t", "T", "RH", "ndE", "best_device", "best_all"] + \
                 [f"E_{u}" for u in UNITS] + [f"wbgt_{u}" for u in UNITS]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in recs:
            w.writerow({k: r[k] for k in fields})

    lines = ["# 逐时气象情景（2026-06-01 至 08-31，当地 11:00–19:00）\n",
             "数据：工作簿 ERA5 0.25° 格点，按城市取格点平均；已把 UTC valid_time 转为当地时间（HK UTC+8，PHX UTC-7）；风为 10 m 风速 × 0.75 折算到 2 m。",
             "模型：v1.0（`analysis/recompute.py`），归一化固定为基线；每小时对 4 单位 × 2 场地评分，并与零设备比较。\n"]
    for city in ("PHX", "HK"):
        lines.append("## %s\n" % city)
        for venue in ("bus", "rail"):
            sub = [r for r in recs if r["city"] == city and r["venue"] == venue]
            n = len(sub)
            dev_win = {u: sum(1 for r in sub if r["best_device"] == u) for u in UNITS}
            all_win = {u: sum(1 for r in sub if r["best_all"] == u) for u in UNITS + ["none"]}
            meanE = {u: sum(r[f"E_{u}"] for r in sub) / n for u in UNITS}
            hot = sorted(sub, key=lambda r: -r["T"])[: max(1, n // 10)]
            hot_win = {u: sum(1 for r in hot if r["best_device"] == u) for u in UNITS}
            lines.append("### %s %s（%d 个高峰小时）\n" % (city, venue, n))
            lines.append("| 指标 | " + " | ".join(UNITS) + " |")
            lines.append("|---|" + "---:|" * len(UNITS))
            lines.append("| 设备间胜出比例 | " + " | ".join("%.0f%%" % (100 * dev_win[u] / n) for u in UNITS) + " |")
            lines.append("| 平均 E | " + " | ".join("%.4f" % meanE[u] for u in UNITS) + " |")
            lines.append("| 最热 10%% 小时胜出 | " + " | ".join("%.0f%%" % (100 * hot_win[u] / len(hot)) for u in UNITS) + " |")
            lines.append("\n零设备在 %.0f%% 的高峰小时中评分最高（E_none 平均 %.4f）。\n" %
                         (100 * all_win["none"] / n, sum(r["ndE"] for r in sub) / n))
    lines.append("> 说明：逐时 E 用于“胜出频率”，绝对值仍用基线归一化；跨场地不可比。")
    open(os.path.join(ROOT, "docs", "hourly_scenarios.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("wrote docs/hourly_scenarios.md")


if __name__ == "__main__":
    main()
