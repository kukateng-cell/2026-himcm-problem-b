"""Independent recomputation of Tables 4-6 for the 2026 HiMCM Problem B paper.

Pure Python (no third-party dependencies). Run:

    python analysis/recompute.py

It reproduces:
  * Table 5 (16-scenario baseline, SC-01..SC-16)
  * Table 6 (four COO weight profiles, 4 venue-city groups)
  * the Table 4 normalisation check (one-unit vs two-unit deployment)

Parameter values are taken from the paper's Table 2 and Section 3.
"""

import itertools
import math

KAPPA = 45.0       # jet mixing attenuation, s/m
GPSY = 0.665       # isenthalpic humidification slope, hPa/degC

EQUIPMENT = {
    "MC37V": dict(P=0.250, CFM=3100, A=88,  eps=0.80, dTnom=11.0, V=10.6, C=398,  L=5, r=0.08),
    "MC61V": dict(P=0.430, CFM=5300, A=148, eps=0.80, dTnom=11.0, V=18.2, C=609,  L=5, r=0.08),
    "Porta": dict(P=0.391, CFM=2400, A=65,  eps=0.80, dTnom=11.0, V=11.4, C=1099, L=7, r=0.06),
    "Fan":   dict(P=0.350, CFM=10500, A=75, eps=0.00, dTnom=0.0,  V=0.0,  C=260,  L=6, r=0.03),
}
CITY = {
    "PHX": dict(T=41.0, RH=18.0, v=1.8, pe=0.1247, pw=2.0766, EF=0.303, BWS=2.482, H=1440),
    "HK":  dict(T=32.5, RH=78.0, v=1.5, pe=0.1923, pw=0.9615, EF=0.465, BWS=0.850, H=1200),
}
VENUE = {
    "bus":  dict(Az=15,  g=0.55, N=6),
    "rail": dict(Az=120, g=0.30, N=45),
}
PROFILES = {
    "Balanced":   (0.30, 0.30, 0.20, 0.20),
    "Safety":     (0.45, 0.25, 0.15, 0.15),
    "Cost":       (0.20, 0.20, 0.45, 0.15),
    "Eco":        (0.20, 0.20, 0.15, 0.45),
}


def es(T):
    """Saturation vapour pressure, hPa (Magnus-Tetens)."""
    return 6.112 * math.exp(17.67 * T / (T + 243.5))


def stull(T, RH):
    """Stull (2011) wet-bulb temperature, degC."""
    RH = min(max(RH, 1.0), 99.9)
    return (T * math.atan(0.151977 * math.sqrt(RH + 8.313659))
            + math.atan(T + RH) - math.atan(RH - 1.676331)
            + 0.00391838 * RH ** 1.5 * math.atan(0.023101 * RH) - 4.686035)


def tapp(T, e, v):
    """Steadman shade apparent temperature, degC."""
    return T + 0.33 * e - 0.70 * v - 4.00


def calc(city, venue, eq, n=1):
    c, v, e = CITY[city], VENUE[venue], EQUIPMENT[eq]
    Twb = stull(c["T"], c["RH"])
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
    Twbz = stull(Tz, 100 * ez / es(Tz))
    wbgt = 0.7 * Twbz + 0.3 * Tz
    return dict(city=city, venue=venue, eq=eq, n=n, dT=dTeff, phi=phi, eta=eta,
                lcc=lcc, eco2=eco2, weq=weq, wbgt=wbgt)


def norm(rows):
    return dict(dT=max(r["dT"] for r in rows), L=max(r["lcc"] for r in rows),
                E=max(r["eco2"] for r in rows), W=max(r["weq"] for r in rows))


def score(r, g, w=(0.30, 0.30, 0.20, 0.20)):
    ssafe = max(0.0, 1 - max(0.0, r["wbgt"] - 28.0) / 6.0)
    scomf = min(1.0, r["phi"] * r["dT"] / g["dT"])
    ienv = 0.5 * r["eco2"] / g["E"] + 0.5 * r["weq"] / g["W"]
    return (w[0] * ssafe + w[1] * scomf
            - w[2] * r["lcc"] / g["L"] - w[3] * ienv), ienv


def table5():
    rows = [calc(c, v, e) for c, v, e in itertools.product(CITY, VENUE, EQUIPMENT)]
    g = norm(rows)
    label = ("city", "venue", "eq", "dTeff", "phi", "eta", "LCC", "I_env", "WBGT", "E")
    print("%-5s %-5s %-6s %8s %6s %9s %8s %8s %7s %8s" % label)
    for r in rows:
        E, I = score(r, g)
        print("%-5s %-5s %-6s %8.3f %6.4f %9.2f %8.2f %8.4f %7.2f %8.4f"
              % (r["city"], r["venue"], r["eq"], r["dT"], r["phi"], r["eta"],
                 r["lcc"], I, r["wbgt"], E))
    return rows, g


def table4_check():
    # Table 4 compares MC37V and Portacool only, at n=1 and n=2, in Phoenix/HK.
    rows = [calc(c, "rail", e, n) for c, e, n in
            itertools.product(CITY, ["MC37V", "Porta"], [1, 2])]
    g_global = norm([calc(c, v, e) for c, v, e in itertools.product(CITY, VENUE, EQUIPMENT)])
    g_two = norm([calc(c, "rail", e, 2) for c, e in itertools.product(CITY, ["MC37V", "Porta"])])
    print("normalisers (16-scenario):", {k: round(v, 3) for k, v in g_global.items()})
    print("normalisers (two-unit subset):", {k: round(v, 3) for k, v in g_two.items()})
    print("\n%-5s %-6s %2s %8s %8s %8s" % ("city", "eq", "n", "I_env", "E(16)", "E(two)"))
    for r in rows:
        e16, i16 = score(r, g_global)
        e2, i2 = score(r, g_two)
        print("%-5s %-6s %2d %8.4f %8.4f %8.4f" % (r["city"], r["eq"], r["n"], i16, e16, e2))


def table6(rows, g):
    for name, w in PROFILES.items():
        print("\n" + name)
        for city, venue in itertools.product(CITY, VENUE):
            cand = [r for r in rows if r["city"] == city and r["venue"] == venue]
            best = max(cand, key=lambda r: score(r, g, w)[0])
            print("  %s %-4s -> %-5s %.4f" % (city, venue, best["eq"], score(best, g, w)[0]))


if __name__ == "__main__":
    print("=" * 72)
    print("Table 5 — 16-scenario baseline")
    print("=" * 72)
    rows, g = table5()
    print("\n" + "=" * 72)
    print("Table 4 — one-unit vs two-unit normalisation check")
    print("=" * 72)
    table4_check()
    print("\n" + "=" * 72)
    print("Table 6 — winners under four COO weight profiles")
    print("=" * 72)
    table6(rows, g)
