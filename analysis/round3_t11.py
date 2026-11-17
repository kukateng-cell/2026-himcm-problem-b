# -*- coding: utf-8 -*-
"""Round 3c: compute v2 values for Table 11 (definition sensitivity)."""
import copy, itertools, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recompute as R

KAPPA_V = {"bus": 84.0, "rail": 45.0}
OVERLAP = 0.30
FAN_CAP = 3.0
R.VENUE["oa"] = dict(Az=300.0, N=120, g=0.75, Aplat=None)

def calc2(city, venue, eq, n=1, eqtable=None):
    R.KAPPA = KAPPA_V[venue]
    r = R.calc(city, venue, eq, n, eqtable=eqtable)
    if r["eq"] == "Fan" or (eqtable and eqtable.get(eq, {}).get("eps") == 0):
        r["dT"] = min(r["dT"], FAN_CAP)
    if n == 2:
        r["phi"] = min(1.0, n * r["A_cov"] * (1 - OVERLAP) / r["Az"])
    return r

rows = [calc2(c, v, e, n) for c, v, e, n in itertools.product(R.CITY, ("bus", "rail"), R.EQUIPMENT, (1, 2))]
G = R.norm(rows)
base = {(c, v, e): R.score(calc2(c, v, e, 1), G)[0] for c in ("PHX", "HK") for v in ("bus", "rail") for e in R.EQUIPMENT}

print("== threshold 30 ==")
for k in [("HK", "rail", "MC37V"), ("HK", "bus", "Fan"), ("HK", "bus", "MC37V")]:
    r = calc2(*k)
    print(k, "thr30 E=%.4f" % R.score(r, G, threshold=30.0)[0], " base E=%.4f" % base[k])
for c in ("PHX", "HK"):
    for v in ("bus", "rail"):
        nd = R.no_device(c, v)
        print("none", c, v, "thr30 E=%.4f" % R.score(nd, G, threshold=30.0)[0])

print("\n== HK design-day variants ==")
orig = copy.deepcopy(R.CITY["HK"])
for T, RH in ((32.5, 78), (33.5, 62)):
    R.CITY["HK"]["T"] = T; R.CITY["HK"]["RH"] = RH
    for v in ("bus", "rail"):
        vals = {e: R.score(calc2("HK", v, e, 1), G)[0] for e in R.EQUIPMENT}
        best = max(vals, key=vals.get)
        print(f"T={T} RH={RH} HK {v}: best {best} {vals[best]:.4f} | " + " ".join(f"{e}={vals[e]:.4f}" for e in R.EQUIPMENT))
R.CITY["HK"] = orig

print("\n== Q2a B as shelter effect (gamma=0, drop=5) ==")
q2aB = dict(P=1.20, CFM=917, A=15, eps=0.80, dTnom=5.0, C=750, L=5, r=0.08, V=15.0)
saved_g = R.VENUE["bus"]["g"]
R.VENUE["bus"]["g"] = 0.0
rB = calc2("PHX", "bus", "B", 1, eqtable={"B": q2aB})
print("B E=%.4f (base B %.4f) dT=%.3f" % (R.score(rB, G)[0], base[("PHX", "bus", "MC37V")], rB["dT"]))
R.VENUE["bus"]["g"] = saved_g

print("\n== N_eff 45 -> 6 (eta only) ==")
for e in ("MC37V", "MC61V"):
    r = calc2("PHX", "rail", e, 1)
    print(e, "eta45=%.2f eta6=%.2f E=%.4f" % (r["eta"], r["eta"] * 6 / 45, R.score(r, G)[0]))
