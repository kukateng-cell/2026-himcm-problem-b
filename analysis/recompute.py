"""Recompute Tables 3-6 for the 2026 HiMCM Problem B paper (v2, P0-P2).

Switches (CLI):
  --wetbulb pressure|stull     pressure-corrected psychrometric (default) or Stull (2011)
  --threshold 28|30            WBGT safety threshold, degC (default 30)
  --norm A|B                   normalisation set for Table 5/6 (default B)
  --units 1|2                  deployment size for Table 5 (default 1)
  --csv DIR                    write CSV outputs to DIR

Normalisation sets:
  A  Q2a stylised systems only (Table 3); not comparable with B.
  B  all 16 one-unit scenarios + all two-unit deployments of the four units
     (Tables 4-6 and the memo).  I_env is guaranteed <= 1 inside B.

Run:
  python analysis/recompute.py
  python analysis/recompute.py --threshold 28 --norm B
  python analysis/recompute.py --wetbulb stull --threshold 30
"""

import argparse
import csv
import itertools
import math
import os

KAPPA = 45.0
GPSY = 0.665

EQUIPMENT = {
    "MC37V": dict(P=0.250, CFM=3100, A=88, eps=0.80, dTnom=11.0, V=10.6, C=398, L=5, r=0.08),
    "MC61V": dict(P=0.430, CFM=5300, A=148, eps=0.80, dTnom=11.0, V=18.2, C=609, L=5, r=0.08),
    "Porta": dict(P=0.391, CFM=2400, A=65, eps=0.80, dTnom=11.0, V=11.4, C=1099, L=7, r=0.06),
    "Fan":   dict(P=0.350, CFM=10500, A=75, eps=0.00, dTnom=0.0, V=0.0, C=260, L=6, r=0.03),
}

# P2 data choices: APS E-32 2024 demand-inclusive marginal rate (0.1595),
# Phoenix 2024 inside-city water (2.0766), CLP 2023/24 EF 0.38-0.39 -> 0.39,
# Aqueduct 4.0 HKG sub-basin bws_raw 0.179.
CITY = {
    "PHX": dict(T=41.0, RH=18.0, v=1.8, pe=0.1595, pw=2.0766, EF=0.303, BWS=2.482,
                H=1440, psurf=950.0),
    "HK":  dict(T=32.5, RH=78.0, v=1.5, pe=0.1923, pw=0.9615, EF=0.390, BWS=0.179,
                H=1200, psurf=1000.0),
}
VENUE = {"bus": dict(Az=15, g=0.55, N=6), "rail": dict(Az=120, g=0.30, N=45)}

Q2A = {
    "A": dict(P=0.25, CFM=2250, A=15, eps=0.00, dTnom=0.0, V=0.0, C=250,  L=7, r=0.03),
    "B": dict(P=1.20, CFM=917,  A=15, eps=0.80, dTnom=5.0, V=15.0, C=750, L=5, r=0.08),
    "C": dict(P=2.50, CFM=1031, A=15, eps=0.80, dTnom=8.0, V=30.0, C=1277, L=5, r=0.08),
}

PROFILES = {
    "Balanced": (0.30, 0.30, 0.20, 0.20),
    "Safety":   (0.45, 0.25, 0.15, 0.15),
    "Cost":     (0.20, 0.20, 0.45, 0.15),
    "Eco":      (0.20, 0.20, 0.15, 0.45),
}


def es(T):
    return 6.112 * math.exp(17.67 * T / (T + 243.5))


def stull(T, RH):
    RH = min(max(RH, 1.0), 99.9)
    return (T * math.atan(0.151977 * math.sqrt(RH + 8.313659))
            + math.atan(T + RH) - math.atan(RH - 1.676331)
            + 0.00391838 * RH ** 1.5 * math.atan(0.023101 * RH) - 4.686035)


def twb_psychro(T, RH, P_hPa):
    """Psychrometric wet bulb at pressure P (hPa), degC."""
    e = es(T) * RH / 100.0
    gam = 1.006 * P_hPa / (0.622 * 2450.0)
    lo, hi = -30.0, T
    for _ in range(80):
        mid = (lo + hi) / 2
        if es(mid) - gam * (T - mid) > e:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def twb(T, RH, P_hPa, mode):
    return twb_psychro(T, RH, P_hPa) if mode == "pressure" else stull(T, RH)


def tapp(T, e, v):
    return T + 0.33 * e - 0.70 * v - 4.00


def calc(city, venue, eq, n=1, wetbulb="pressure", eqtable=None):
    c, v, e = CITY[city], VENUE[venue], (eqtable or EQUIPMENT)[eq]
    Twb = twb(c["T"], c["RH"], c["psurf"], wetbulb)
    dTphys = min(e["dTnom"], e["eps"] * (c["T"] - Twb))
    Tz = c["T"] - (1 - v["g"]) * dTphys
    eamb = es(c["T"]) * c["RH"] / 100
    ez = min(es(Tz), eamb + GPSY * (1 - v["g"]) * dTphys)
    Q = e["CFM"] * 1.699 / 3600
    veff = c["v"] + KAPPA * Q / e["A"]
    dTeff = tapp(c["T"], eamb, c["v"]) - tapp(Tz, ez, veff)
    phi = min(1.0, n * e["A"] / v["Az"])
    eta = phi * v["N"] * dTeff / (n * e["P"])
    lcc = ((1 / e["L"] + e["r"]) * n * e["C"]
           + c["H"] * (n * e["P"] * c["pe"] + n * e["V"] / 1000 * c["pw"]))
    eco2 = n * e["P"] * c["H"] * c["EF"]
    weq = n * e["V"] / 1000 * c["H"] * c["BWS"]
    Twbz = twb(Tz, 100 * ez / es(Tz), c["psurf"], wetbulb)
    wbgt = 0.7 * Twbz + 0.3 * Tz
    return dict(city=city, venue=venue, eq=eq, n=n, dT=dTeff, phi=phi, eta=eta,
                lcc=lcc, eco2=eco2, weq=weq, wbgt=wbgt, twb=Twb, dTphys=dTphys,
                P=e["P"], V=e["V"], C=e["C"], L=e["L"], r=e["r"],
                CFM=e["CFM"], A_cov=e["A"], eps=e["eps"], dTnom=e["dTnom"])


def norm(rows):
    return dict(dT=max(r["dT"] for r in rows), L=max(r["lcc"] for r in rows),
                E=max(r["eco2"] for r in rows), W=max(r["weq"] for r in rows))


def score(r, g, w=(0.30, 0.30, 0.20, 0.20), threshold=30.0):
    ssafe = max(0.0, 1 - max(0.0, r["wbgt"] - threshold) / 6.0)
    scomf = min(1.0, r["phi"] * r["dT"] / g["dT"])
    ienv = 0.5 * r["eco2"] / g["E"] + 0.5 * r["weq"] / g["W"]
    return (w[0] * ssafe + w[1] * scomf
            - w[2] * r["lcc"] / g["L"] - w[3] * ienv), ienv, scomf, ssafe


def set_B(rows):
    """Envelope over all one- and two-unit deployments of the four units."""
    allrows = [calc(c, v, e, n, wetbulb=MODE) for c, v, e, n in
               itertools.product(CITY, VENUE, EQUIPMENT, [1, 2])]
    return norm(list(rows) + allrows)


def table5_rows(wetbulb, threshold, norm_mode):
    rows = [calc(c, v, e, 1, wetbulb=wetbulb) for c, v, e in
            itertools.product(CITY, VENUE, EQUIPMENT)]
    g = set_B(rows) if norm_mode == "B" else norm(rows)
    out = []
    for r in rows:
        E, I, sc, ss = score(r, g, threshold=threshold)
        out.append(dict(r, E=E, I_env=I, S_comf=sc, S_safe=ss))
    return out, g


def table4_rows(wetbulb, threshold):
    rows = [calc(c, "rail", e, n, wetbulb=wetbulb) for c, e, n in
            itertools.product(CITY, EQUIPMENT, [1, 2])]
    g = set_B(rows)
    out = []
    for r in rows:
        E, I, sc, ss = score(r, g, threshold=threshold)
        out.append(dict(r, E=E, I_env=I, S_comf=sc, S_safe=ss))
    return out, g


def table3_rows(wetbulb, threshold):
    rows = [calc("PHX", "bus", k, 1, wetbulb=wetbulb, eqtable=Q2A) for k in Q2A]
    g = norm(rows)  # Set A: System C is the reference
    out = []
    for r in rows:
        E, I, sc, ss = score(r, g, threshold=threshold)
        out.append(dict(r, E=E, I_env=I, S_comf=sc, S_safe=ss))
    return out, g


def table6(rows5, g, threshold):
    res = {}
    for name, w in PROFILES.items():
        for city, venue in itertools.product(CITY, VENUE):
            cand = [r for r in rows5 if r["city"] == city and r["venue"] == venue]
            best = max(cand, key=lambda r: score(r, g, w, threshold)[0])
            res[(name, city, venue)] = (best["eq"], score(best, g, w, threshold)[0])
    return res


def sweep_rh(threshold):
    """Bus/rail crossover RH at 41 degC and 32.5 degC for MC37V vs Fan (2.081)."""
    out = []
    for T in (41.0, 32.5):
        for venue, g in (("bus", 0.55), ("rail", 0.30)):
            lo, hi = 10.0, 99.0
            for _ in range(60):
                mid = (lo + hi) / 2
                c = dict(CITY["PHX"])
                c["T"] = T
                # local calc for arbitrary RH
                Twb = twb_psychro(T, mid, c["psurf"]) if MODE == "pressure" else stull(T, mid)
                dTp = min(11.0, 0.8 * (T - Twb))
                Q = 3100 * 1.699 / 3600
                dT = (1 - g) * dTp * 0.78055 + 0.7 * KAPPA * Q / 88
                if dT > 2.081:
                    lo = mid
                else:
                    hi = mid
            out.append((T, venue, (lo + hi) / 2))
    return out


def tornado():
    """E of key options under one-at-a-time parameter changes."""
    base5, g5 = table5_rows(MODE, THRESH, "B")
    base4, g4 = table4_rows(MODE, THRESH)
    picks = {
        "PHX rail 1x MC37V": next(r for r in base4 if r["city"] == "PHX" and r["eq"] == "MC37V" and r["n"] == 1),
        "PHX rail 1x MC61V": next(r for r in base4 if r["city"] == "PHX" and r["eq"] == "MC61V" and r["n"] == 1),
        "PHX rail 2x MC37V": next(r for r in base4 if r["city"] == "PHX" and r["eq"] == "MC37V" and r["n"] == 2),
        "HK rail 1x MC37V": next(r for r in base4 if r["city"] == "HK" and r["eq"] == "MC37V" and r["n"] == 1),
        "HK rail 2x Fan": next(r for r in base4 if r["city"] == "HK" and r["eq"] == "Fan" and r["n"] == 2),
    }
    print("\nBaseline E of key options (threshold %.0f, norm B):" % THRESH)
    for k, r in picks.items():
        E = score(r, g4, threshold=THRESH)[0]
        print("  %-20s phi=%.3f dTeff=%.3f LCC=%.2f I=%.3f wbgt=%.2f E=%.4f"
              % (k, r["phi"], r["dT"], r["lcc"], score(r, g4, threshold=THRESH)[1], r["wbgt"], E))
    return picks


def write_csv(path, rows, fields):
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "numbers_v2.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})


def main():
    global MODE, THRESH
    ap = argparse.ArgumentParser()
    ap.add_argument("--wetbulb", choices=["pressure", "stull"], default="pressure")
    ap.add_argument("--threshold", type=float, default=30.0)
    ap.add_argument("--norm", choices=["A", "B"], default="B")
    ap.add_argument("--units", type=int, default=1)
    ap.add_argument("--csv", default="")
    args = ap.parse_args()
    MODE, THRESH = args.wetbulb, args.threshold

    print("=" * 78)
    print("Table 3 — Q2a (Set A, Phoenix bus shelter)")
    print("=" * 78)
    t3, g3 = table3_rows(MODE, THRESH)
    print("%-4s %6s %8s %6s %9s %8s %8s %8s" % ("sys", "P", "dTeff", "phi", "eta", "LCC", "I_env", "E"))
    for r in t3:
        print("%-4s %6.2f %8.3f %6.3f %9.2f %8.2f %8.4f %8.4f"
              % (r["eq"], r["P"], r["dT"], r["phi"], r["eta"], r["lcc"], r["I_env"], r["E"]))
    print("set A normalisers:", {k: round(v, 3) for k, v in g3.items()})

    print("\n" + "=" * 78)
    print("Table 5 — 16 scenarios (Set B, threshold %.0f)" % THRESH)
    print("=" * 78)
    t5, g5 = table5_rows(MODE, THRESH, "B")
    print("%-5s %-5s %-6s %8s %6s %9s %8s %8s %7s %8s"
          % ("city", "venue", "eq", "dTeff", "phi", "eta", "LCC", "I_env", "WBGT", "E"))
    for r in t5:
        print("%-5s %-5s %-6s %8.3f %6.4f %9.2f %8.2f %8.4f %7.2f %8.4f"
              % (r["city"], r["venue"], r["eq"], r["dT"], r["phi"], r["eta"],
                 r["lcc"], r["I_env"], r["wbgt"], r["E"]))
    print("set B normalisers:", {k: round(v, 3) for k, v in g5.items()})

    print("\n" + "=" * 78)
    print("Table 4 — rail station, 1 vs 2 units (Set B, threshold %.0f)" % THRESH)
    print("=" * 78)
    t4, g4 = table4_rows(MODE, THRESH)
    print("%-5s %-6s %2s %8s %6s %8s %8s %8s %7s %8s"
          % ("city", "eq", "n", "dTeff", "phi", "LCC", "I_env", "S_comf", "WBGT", "E"))
    for r in t4:
        print("%-5s %-6s %2d %8.3f %6.4f %8.2f %8.4f %8.4f %7.2f %8.4f"
              % (r["city"], r["eq"], r["n"], r["dT"], r["phi"], r["lcc"],
                 r["I_env"], r["S_comf"], r["wbgt"], r["E"]))

    print("\n" + "=" * 78)
    print("Table 6 — winners (threshold %.0f)" % THRESH)
    print("=" * 78)
    t6 = table6(t5, g5, THRESH)
    for name in PROFILES:
        print(name)
        for city in CITY:
            for venue in VENUE:
                eq, E = t6[(name, city, venue)]
                print("  %s %-4s -> %-5s %.4f" % (city, venue, eq, E))

    print("\n" + "=" * 78)
    print("RH crossover (MC37V vs Fan 2.081)")
    print("=" * 78)
    for T, venue, rh in sweep_rh(THRESH):
        print("  T=%.1f %-4s crossover RH=%.1f%%" % (T, venue, rh))

    tornado()

    if args.csv:
        rows = []
        for r in t5:
            rows.append(dict(r, table="T5"))
        for r in t4:
            rows.append(dict(r, table="T4"))
        for r in t3:
            rows.append(dict(r, table="T3"))
        fields = ["table", "city", "venue", "eq", "n", "dT", "phi", "eta", "lcc",
                  "eco2", "weq", "I_env", "wbgt", "S_safe", "S_comf", "E"]
        write_csv(args.csv, rows, fields)
        print("\nwrote", os.path.join(args.csv, "numbers_v2.csv"))


if __name__ == "__main__":
    MODE = "pressure"
    THRESH = 30.0
    main()
