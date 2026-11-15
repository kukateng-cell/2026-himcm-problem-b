"""Model v1.0 - recompute Tables 3-6 for the 2026 HiMCM Problem B paper.

P0 fixes applied (2026-11-15):
  D7  Areas are separated: A_platform is context, A_waiting is what the model cools,
      A_cov is the unit's nominal coverage. HK rail waiting zone = 128 m2 (measured
      32 m x 4 m side platform); Phoenix waiting zone = 120 m2 (modelled boarding zone
      inside a 425 m2 centre platform).
  D8  Water is derived from the adiabatic mass balance at the modelled dT_phys:
      V_w = 3600 * m_da * cp * dT_phys / L_v  (L/h). Manufacturer tank/run-time rates
      are kept only as a sensitivity (--vw manufacturer).
  D9  Decision score: safety is a graded proxy index anchored at 32 C and evaluated for
      the population (covered + uncovered); benefit scales with persons; normalisers are
      per venue (bus / rail), so E is comparable within a venue, not across venues.
      A "no device" baseline is reported alongside every table.
  D10 WBGT is an approximate proxy (0.7 T_wb + 0.3 T_db), not ISO 7243 compliance.
  D11 kappa is dimensionless (momentum amplification of Q/A_cov), not s/m.

Run:
  python analysis/recompute.py
  python analysis/recompute.py --threshold 28
  python analysis/recompute.py --csv docs
"""

import argparse
import csv
import itertools
import math
import os

KAPPA = 45.0
GPSY = 0.665
CP = 1.006          # kJ/(kg K)
LV = 2450.0         # kJ/kg
RHO_W = 1.0         # kg/L

EQUIPMENT = {
    "MC37V": dict(P=0.250, CFM=3100, A=88, eps=0.80, dTnom=11.0, C=398, L=5, r=0.08, V=10.6),
    "MC61V": dict(P=0.430, CFM=5300, A=148, eps=0.80, dTnom=11.0, C=609, L=5, r=0.08, V=18.2),
    "Porta": dict(P=0.391, CFM=2400, A=65, eps=0.80, dTnom=11.0, C=1099, L=7, r=0.06, V=11.4),
    "Fan":   dict(P=0.350, CFM=10500, A=75, eps=0.00, dTnom=0.0, C=260, L=6, r=0.03, V=0.0),
}

CITY = {
    "PHX": dict(T=41.0, RH=18.0, v=1.8, pe=0.1595, pw=2.0766, EF=0.303, BWS=2.482,
                H=1440, psurf=950.0, Aplat=425.0),
    "HK":  dict(T=32.5, RH=78.0, v=1.5, pe=0.1923, pw=0.9615, EF=0.390, BWS=0.179,
                H=1200, psurf=1000.0, Aplat=128.0),
}

# Az = modelled waiting zone; Aplat = whole platform (context only)
VENUE = {
    "bus":  dict(Az=15.0, N=6, g=0.55, Aplat=20.0),
    "rail": dict(Az=120.0, N=45, g=0.30, Aplat=None),
}
HK_RAIL_AZ = 128.0

PROFILES = {
    "Balanced": (0.30, 0.30, 0.20, 0.20),
    "Safety":   (0.45, 0.25, 0.15, 0.15),
    "Cost":     (0.20, 0.20, 0.45, 0.15),
    "Eco":      (0.20, 0.20, 0.15, 0.45),
}

WATER_MODE = "balance"


def es(T):
    return 6.112 * math.exp(17.67 * T / (T + 243.5))


def stull(T, RH):
    RH = min(max(RH, 1.0), 99.9)
    return (T * math.atan(0.151977 * math.sqrt(RH + 8.313659))
            + math.atan(T + RH) - math.atan(RH - 1.676331)
            + 0.00391838 * RH ** 1.5 * math.atan(0.023101 * RH) - 4.686035)


def twb_psychro(T, RH, P_hPa):
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


def zone_area(city, venue):
    if venue == "rail" and city == "HK":
        return HK_RAIL_AZ
    return VENUE[venue]["Az"]


def calc(city, venue, eq, n=1, wetbulb="pressure", eqtable=None):
    c, v, e = CITY[city], VENUE[venue], (eqtable or EQUIPMENT)[eq]
    Az = zone_area(city, venue)
    Twb = twb(c["T"], c["RH"], c["psurf"], wetbulb)
    dTphys = min(e["dTnom"], e["eps"] * (c["T"] - Twb))
    Tz = c["T"] - (1 - v["g"]) * dTphys
    eamb = es(c["T"]) * c["RH"] / 100
    ez = min(es(Tz), eamb + GPSY * (1 - v["g"]) * dTphys)
    Q = e["CFM"] * 1.699 / 3600
    veff = c["v"] + KAPPA * Q / e["A"]
    dTeff = tapp(c["T"], eamb, c["v"]) - tapp(Tz, ez, veff)
    phi = min(1.0, n * e["A"] / Az)

    rho = c["psurf"] * 100 / (287.05 * (c["T"] + 273.15))
    mda = Q * rho
    Vw_bal = 3600.0 * mda * (CP * dTphys / LV) / RHO_W
    Vw = Vw_bal if WATER_MODE == "balance" else e["V"]
    if e["eps"] == 0:
        Vw = 0.0

    lcc = ((1 / e["L"] + e["r"]) * n * e["C"]
           + c["H"] * (n * e["P"] * c["pe"] + n * Vw / 1000 * c["pw"]))
    eco2 = n * e["P"] * c["H"] * c["EF"]
    weq = n * Vw / 1000 * c["H"] * c["BWS"]
    Twbz = twb(Tz, 100 * ez / es(Tz), c["psurf"], wetbulb)
    wbgt = 0.7 * Twbz + 0.3 * Tz
    wbgt_amb = 0.7 * Twb + 0.3 * c["T"]
    return dict(city=city, venue=venue, eq=eq, n=n, dT=dTeff, phi=phi, eta=phi * v["N"] * dTeff / (n * e["P"]),
                lcc=lcc, eco2=eco2, weq=weq, wbgt=wbgt, wbgt_amb=wbgt_amb, Vw=Vw,
                dTphys=dTphys, twb=Twb, P=e["P"], C=e["C"], L=e["L"], r=e["r"],
                CFM=e["CFM"], A_cov=e["A"], eps=e["eps"], dTnom=e["dTnom"], Az=Az)


def sat(wbgt, threshold=30.0):
    """Graded heat-safety proxy: 1 at 26 C and below, 0 at 32 C and above,
    anchored so that the 30 C reference line gives 1/3."""
    return max(0.0, min(1.0, (32.0 - wbgt) / 6.0))


def norm(rows):
    """Per-venue normalisers: B (persons x dT), LCC, E_CO2, W_eq."""
    out = {}
    for venue in VENUE:
        sub = [r for r in rows if r["venue"] == venue]
        if not sub:
            continue
        out[venue] = dict(B=max(r["phi"] * VENUE[venue]["N"] * r["dT"] for r in sub),
                          L=max(r["lcc"] for r in sub),
                          E=max(r["eco2"] for r in sub),
                          W=max(r["weq"] for r in sub))
    return out


def score(r, g, w=(0.30, 0.30, 0.20, 0.20), threshold=30.0):
    """E with population-weighted graded safety and per-venue normalisers."""
    gg = g[r["venue"]]
    N = VENUE[r["venue"]]["N"]
    ssafe = r["phi"] * sat(r["wbgt"], threshold) + (1 - r["phi"]) * sat(r["wbgt_amb"], threshold)
    benefit = r["phi"] * N * r["dT"] / gg["B"]
    ienv = 0.5 * r["eco2"] / gg["E"] + 0.5 * r["weq"] / gg["W"]
    E = (w[0] * ssafe + w[1] * benefit
         - w[2] * r["lcc"] / gg["L"] - w[3] * ienv)
    return E, ienv, benefit, ssafe


def no_device(city, venue):
    """E of the do-nothing baseline, with the same per-venue normalisers."""
    c = CITY[city]
    Twb = twb(c["T"], c["RH"], c["psurf"], "pressure")
    wbgt_amb = 0.7 * Twb + 0.3 * c["T"]
    return dict(city=city, venue=venue, eq="none", n=0, dT=0.0, phi=0.0, eta=0.0,
                lcc=0.0, eco2=0.0, weq=0.0, wbgt=wbgt_amb, wbgt_amb=wbgt_amb,
                Vw=0.0, dTphys=0.0, P=0.0, C=0.0, L=1.0, r=0.0,
                CFM=0, A_cov=0, eps=0.0, dTnom=0.0, Az=zone_area(city, venue))


def set_B():
    rows = [calc(c, v, e, n) for c, v, e, n in itertools.product(CITY, VENUE, EQUIPMENT, (1, 2))]
    return norm(rows)


MODE = "pressure"
THRESH = 30.0


def table5_rows(wetbulb, threshold, norm_mode="B"):
    rows = [calc(c, v, e, 1) for c, v, e in itertools.product(CITY, VENUE, EQUIPMENT)]
    g = set_B()
    for r in rows:
        r["E"], r["I_env"], r["S_comf"], r["S_safe"] = score(r, g, threshold=threshold)
    return rows, g


def table4_rows(wetbulb, threshold):
    rows = [calc(c, "rail", e, n) for c, e, n in itertools.product(CITY, EQUIPMENT, (1, 2))]
    g = set_B()
    for r in rows:
        r["E"], r["I_env"], r["S_comf"], r["S_safe"] = score(r, g, threshold=threshold)
    return rows, g


def table3_rows(wetbulb, threshold):
    """Q2a systems A/B/C at the Phoenix bus shelter (waiting zone 15 m2)."""
    q2a = {
        "A": dict(P=0.25, CFM=2250, A=15, eps=0.00, dTnom=0.0, C=250, L=7, r=0.03, V=0.0),
        "B": dict(P=1.20, CFM=917, A=15, eps=0.80, dTnom=5.0, C=750, L=5, r=0.08, V=15.0),
        "C": dict(P=2.50, CFM=1031, A=15, eps=0.80, dTnom=8.0, C=1277, L=5, r=0.08, V=30.0),
    }
    rows = [calc("PHX", "bus", k, 1, eqtable=q2a) for k in q2a]
    g = set_B()
    for r in rows:
        r["E"], r["I_env"], r["S_comf"], r["S_safe"] = score(r, g, threshold=threshold)
    return rows, g


def table6(rows5, g, threshold):
    res = {}
    for name, w in PROFILES.items():
        for city, venue in itertools.product(CITY, VENUE):
            cand = [r for r in rows5 if r["city"] == city and r["venue"] == venue]
            best = max(cand, key=lambda r: score(r, g, w, threshold)[0])
            res[(name, city, venue)] = (best["eq"], score(best, g, w, threshold)[0])
    return res


def sweep_rh(threshold):
    out = []
    for T in (41.0, 32.5):
        for venue, g in (("bus", 0.55), ("rail", 0.30)):
            lo, hi = 10.0, 99.0
            for _ in range(60):
                mid = (lo + hi) / 2
                c = dict(CITY["PHX"])
                c["T"] = T
                Twb = twb_psychro(T, mid, c["psurf"])
                dTp = min(11.0, 0.8 * (T - Twb))
                Q = 3100 * 1.699 / 3600
                dT = (1 - g) * dTp * 0.78055 + 0.7 * KAPPA * Q / 88
                if dT > 2.081:
                    lo = mid
                else:
                    hi = mid
            out.append((T, venue, (lo + hi) / 2))
    return out


def write_csv(path, rows, fields):
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "numbers_v2.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in fields})


def main():
    global MODE, THRESH, WATER_MODE
    ap = argparse.ArgumentParser()
    ap.add_argument("--wetbulb", choices=["pressure", "stull"], default="pressure")
    ap.add_argument("--threshold", type=float, default=30.0)
    ap.add_argument("--vw", choices=["balance", "manufacturer"], default="balance")
    ap.add_argument("--csv", default="")
    args = ap.parse_args()
    MODE, THRESH, WATER_MODE = args.wetbulb, args.threshold, args.vw

    print("=" * 92)
    print("Table 3 - Q2a systems (Phoenix bus shelter, per-venue normalisers)")
    print("=" * 92)
    t3, g = table3_rows(MODE, THRESH)
    print("%-3s %6s %8s %6s %9s %8s %8s %8s" % ("sys", "P", "dTeff", "phi", "eta", "LCC", "S_safe", "E"))
    for r in t3:
        print("%-3s %6.2f %8.3f %6.3f %9.2f %8.2f %8.3f %8.4f"
              % (r["eq"], r["P"], r["dT"], r["phi"], r["eta"], r["lcc"], r["S_safe"], r["E"]))

    print("\n" + "=" * 92)
    print("Table 5 - 16 scenarios (per-venue normalisers, threshold %.0f)" % THRESH)
    print("=" * 92)
    t5, g = table5_rows(MODE, THRESH)
    print("%-5s %-5s %-6s %7s %6s %7s %8s %8s %9s %7s" % ("city", "venue", "eq", "dTeff", "phi", "Vw", "LCC", "S_safe", "benefit", "E"))
    for r in t5:
        print("%-5s %-5s %-6s %7.2f %6.2f %7.1f %8.2f %8.3f %9.3f %7.4f"
              % (r["city"], r["venue"], r["eq"], r["dT"], r["phi"], r["Vw"], r["lcc"], r["S_safe"], r["S_comf"], r["E"]))

    print("\nno-device baseline")
    for city in CITY:
        for venue in VENUE:
            nd = no_device(city, venue)
            E, I, b, s = score(nd, g, threshold=THRESH)
            print("  %-4s %-5s WBGT_proxy=%.2f  S_safe=%.3f  E=%.4f" % (city, venue, nd["wbgt_amb"], s, E))

    print("\n" + "=" * 92)
    print("Table 4 - rail, 1 vs 2 units")
    print("=" * 92)
    t4, g4 = table4_rows(MODE, THRESH)
    print("%-5s %-6s %2s %7s %6s %8s %8s %7s" % ("city", "eq", "n", "phi", "LCC", "S_safe", "benefit", "E"))
    for r in t4:
        print("%-5s %-6s %2d %6.3f %8.2f %8.3f %8.3f %7.4f"
              % (r["city"], r["eq"], r["n"], r["phi"], r["lcc"], r["S_safe"], r["S_comf"], r["E"]))

    print("\n" + "=" * 92)
    print("Table 6 - winners (threshold %.0f)" % THRESH)
    print("=" * 92)
    t6 = table6(t5, g, THRESH)
    for name in PROFILES:
        print(name)
        for city in CITY:
            for venue in VENUE:
                eq, E = t6[(name, city, venue)]
                print("  %s %-4s -> %-5s %.4f" % (city, venue, eq, E))

    print("\nRH crossover (MC37V vs fan 2.081)")
    for T, venue, rh in sweep_rh(THRESH):
        print("  T=%.1f %-4s crossover RH=%.1f%%" % (T, venue, rh))

    if args.csv:
        rows = []
        for r in t5:
            rows.append(dict(r, table="T5"))
        for r in t4:
            rows.append(dict(r, table="T4"))
        for r in t3:
            rows.append(dict(r, table="T3"))
        fields = ["table", "city", "venue", "eq", "n", "dT", "dTphys", "phi", "eta", "lcc",
                  "Vw", "eco2", "weq", "I_env", "wbgt", "wbgt_amb", "S_safe", "S_comf", "E"]
        write_csv(args.csv, rows, fields)
        print("\nwrote", os.path.join(args.csv, "numbers_v2.csv"))


if __name__ == "__main__":
    main()
