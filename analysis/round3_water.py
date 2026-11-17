# -*- coding: utf-8 -*-
"""Round 3a: water-limited Phoenix table (Table 10b) under v2 model."""
import copy, itertools, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recompute as R

KAPPA_V = {"bus": 84.0, "rail": 45.0, "oa": 45.0}
OVERLAP = 0.30
FAN_CAP = 3.0

# base normalisers (v2)
R.VENUE["oa"] = dict(Az=300.0, N=120, g=0.75, Aplat=None)
def calc2(city, venue, eq, n=1, eqtable=None):
    R.KAPPA = KAPPA_V[venue]
    r = R.calc(city, venue, eq, n, eqtable=eqtable)
    if r["eq"] == "Fan" or (eqtable and eqtable.get(eq, {}).get("eps") == 0):
        r["dT"] = min(r["dT"], FAN_CAP)
        r["eta"] = r["phi"] * R.VENUE[venue]["N"] * r["dT"] / (n * r["P"])
    if n == 2:
        r["phi"] = min(1.0, n * r["A_cov"] * (1 - OVERLAP) / r["Az"])
    return r

rows = [calc2(c, v, e, n) for c, v, e, n in itertools.product(R.CITY, ("bus", "rail"), R.EQUIPMENT, (1, 2))]
G = R.norm(rows)
base = {e: R.score(calc2("PHX", "rail", e, 1), G)[0] for e in R.EQUIPMENT}
base_bus = {e: R.score(calc2("PHX", "bus", e, 1), G)[0] for e in R.EQUIPMENT}

# water-limited: manufacturer water, implied dTphys
R.WATER_MODE = "manufacturer"
implied = {"MC37V": 4.5, "MC61V": 4.5, "Porta": 6.2, "Fan": 0.0}
eq2 = copy.deepcopy(R.EQUIPMENT)
for k, v in implied.items():
    eq2[k]["dTnom"] = v

print("unit   venue  baseE   waterE   dTphys")
for venue in ("bus", "rail"):
    for e in R.EQUIPMENT:
        r = calc2("PHX", venue, e, 1, eqtable=eq2)
        E = R.score(r, G)[0]
        b = base_bus[e] if venue == "bus" else base[e]
        print(f"{e:6s} {venue:4s}  {b:.4f}  {E:.4f}  {r['dTphys']:.2f}")

nd = R.no_device("PHX", "bus")
print("none", R.score(nd, G)[0])
