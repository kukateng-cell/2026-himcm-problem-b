# -*- coding: utf-8 -*-
"""Structural stress tests (C1-C5) on top of the published model."""
import copy
import itertools
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recompute as R

BASE_G = R.set_B()

def fmt_row(r, E=None):
    E = E if E is not None else r.get("E")
    return "%-9s %-6s %-5s phi=%.3f dT=%.3f Eb=%.4f E=%.4f" % (
        r["city"], r["venue"], r["eq"], r["phi"], r["dT"], r["lcc"], E)

print("=== base check: PHX bus MC37V ===")
r = R.calc("PHX", "bus", "MC37V", 1)
print(" dT=%.3f E=%.4f" % (r["dT"], R.score(r, BASE_G)[0]))

# ---------------------------------------------------------------- C1 open-air
print("\n=== C1 open-air stadium concourse (gamma=0.75, globe +6 K -> WBGT +1.8 K) ===")
R.VENUE["oa"] = dict(Az=300.0, N=120, g=0.75, Aplat=None)

def oa_rows():
    rows = [R.calc(c, "oa", e, n) for c, e, n in itertools.product(R.CITY, R.EQUIPMENT, (1, 2))]
    for r in rows:
        r["wbgt"] += 1.8
        r["wbgt_amb"] += 1.8
    return rows

rows = oa_rows()
g_oa = R.norm(rows)
for r in rows:
    r["E"], r["I_env"], r["S_comf"], r["S_safe"] = R.score(r, g_oa)
for c in R.CITY:
    nd = R.no_device(c, "oa")
    nd["wbgt"] += 1.8
    nd["wbgt_amb"] += 1.8
    E_nd = R.score(nd, g_oa)[0]
    print(" %s do-nothing E=%.4f (S=%.3f)" % (c, E_nd, R.score(nd, g_oa)[3]))
    for r in [x for x in rows if x["city"] == c and x["n"] == 1]:
        print("  " + fmt_row(r) + " S=%.3f" % R.score(r, g_oa)[3])

# ---------------------------------------------------------------- C2 kappa
print("\n=== C2 kappa baseline: PHX bus, base normalisers ===")
for kap in (45, 84, 92, 105):
    R.KAPPA = kap
    for eq in ("MC37V", "Fan"):
        r = R.calc("PHX", "bus", eq, 1)
        print("  kappa=%3d %-5s dT=%.3f E=%.4f" % (kap, eq, r["dT"], R.score(r, BASE_G)[0]))
R.KAPPA = 45

# ---------------------------------------------------------------- C3 fan derating
print("\n=== C3 fan credit removed above 35 C (PHX only) ===")
for venue in ("bus", "rail"):
    base = R.calc("PHX", venue, "Fan", 1)
    E0 = R.score(base, BASE_G)[0]
    d = copy.deepcopy(base)
    d["dT"] = 0.0
    E1 = R.score(d, BASE_G)[0]
    print("  PHX %-4s fan base E=%.4f  no-credit E=%.4f (dT %.2f -> 0)" % (venue, E0, E1, base["dT"]))

# ---------------------------------------------------------------- C4 overlap
print("\n=== C4 30% jet overlap, two units (phi=min(1,1.4*A_cov/Az)) ===")
for city in ("PHX", "HK"):
    for eq in R.EQUIPMENT:
        base = R.calc(city, "rail", eq, 2)
        E0 = R.score(base, BASE_G)[0]
        d = copy.deepcopy(base)
        d["phi"] = min(1.0, 2 * R.EQUIPMENT[eq]["A"] * 0.70 / R.zone_area(city, "rail"))
        E1 = R.score(d, BASE_G)[0]
        if abs(E0 - E1) > 1e-9:
            print("  %s rail %-5s 2x: phi %.3f->%.3f  E %.4f->%.4f" % (city, eq, base["phi"], d["phi"], E0, E1))

# ---------------------------------------------------------------- C5 candidate set
print("\n=== C5 normaliser candidate-set sensitivity ===")
extra = dict(P=2.0, CFM=6000, A=120, eps=0.80, dTnom=11.0, C=2500, L=6, r=0.05, V=20.0)
eq2 = dict(R.EQUIPMENT); eq2["Premium"] = extra
rows2 = [R.calc(c, v, e, n, eqtable=eq2) for c, v, e, n in itertools.product(R.CITY, ("bus", "rail"), eq2, (1, 2))]
for r in rows2:
    if r["eq"] == "Premium":
        pass
g2 = R.norm(rows2)
for city in R.CITY:
    for venue in ("bus", "rail"):
        nd = R.no_device(city, venue)
        E_nd0 = R.score(nd, BASE_G)[0]
        E_nd1 = R.score(nd, g2)[0]
        r = R.calc(city, venue, "MC37V", 1)
        E0 = R.score(r, BASE_G)[0]
        E1 = R.score(r, g2)[0]
        print("  %s %-4s do-nothing %.4f->%.4f | MC37V %.4f->%.4f | gap %.4f->%.4f" %
              (city, venue, E_nd0, E_nd1, E0, E1, E0 - E_nd0, E1 - E_nd1))
