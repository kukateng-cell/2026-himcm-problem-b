# -*- coding: utf-8 -*-
"""v2 model numbers (stage 1): Tables 3, 4, 5, 6 and the open-air table."""
import itertools, json
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recompute as R

KAPPA_V = {"bus": 84.0, "rail": 45.0, "oa": 45.0}
OVERLAP = 0.30
FAN_CAP = 3.0

def calc2(city, venue, eq, n=1, eqtable=None):
    R.KAPPA = KAPPA_V[venue]
    r = R.calc(city, venue, eq, n, eqtable=eqtable)
    if r["eq"].startswith("Fan") or (eqtable and eqtable.get(eq, {}).get("eps") == 0):
        r["dT"] = min(r["dT"], FAN_CAP)
        r["eta"] = r["phi"] * R.VENUE[venue]["N"] * r["dT"] / (n * r["P"])
    if n == 2:
        r["phi"] = min(1.0, n * r["A_cov"] * (1 - OVERLAP) / r["Az"])
        r["eta"] = r["phi"] * R.VENUE[venue]["N"] * r["dT"] / (n * r["P"])
    return r

# open-air venue
R.VENUE["oa"] = dict(Az=300.0, N=120, g=0.75, Aplat=None)
GLOBE = 1.8

def rows_for(venues, ns=(1, 2)):
    return [calc2(c, v, e, n) for c, v, e, n in itertools.product(R.CITY, venues, R.EQUIPMENT, ns)]

BASE = rows_for(("bus", "rail", "oa"))
for r in BASE:
    if r["venue"] == "oa":
        r["wbgt"] += GLOBE; r["wbgt_amb"] += GLOBE
G = R.norm(BASE)

def E(r, w=(0.30, 0.30, 0.20, 0.20)):
    return R.score(r, G, w)

out = {}

# Q2a
q2a = {
    "A": dict(P=0.25, CFM=2250, A=15, eps=0.00, dTnom=0.0, C=250, L=7, r=0.03, V=0.0),
    "B": dict(P=1.20, CFM=917, A=15, eps=0.80, dTnom=5.0, C=750, L=5, r=0.08, V=15.0),
    "C": dict(P=2.50, CFM=1031, A=15, eps=0.80, dTnom=8.0, C=1277, L=5, r=0.08, V=30.0),
}
out["T3"] = []
for k in q2a:
    r = calc2("PHX", "bus", k, 1, eqtable=q2a)
    e, i, b, s = E(r)
    out["T3"].append(dict(system=k, P=r["P"], dT=round(r["dT"], 3), phi=round(r["phi"], 3),
                          eta=round(r["eta"], 2), lcc=round(r["lcc"], 2), wbgt=round(r["wbgt"], 2),
                          E=round(e, 4)))

# T5
out["T5"] = []
for c in ("PHX", "HK"):
    for v in ("bus", "rail"):
        for eq in R.EQUIPMENT:
            r = calc2(c, v, eq, 1)
            e, i, b, s = E(r)
            out["T5"].append(dict(city=c, venue=v, eq=eq, dT=round(r["dT"], 3), phi=round(r["phi"], 3),
                                  eta=round(r["eta"], 2), lcc=round(r["lcc"], 2), ienv=round(i, 4),
                                  wbgt=round(r["wbgt"], 2), E=round(e, 4)))

# T6 winners
out["T6"] = []
for name, w in R.PROFILES.items():
    for c in ("PHX", "HK"):
        for v in ("bus", "rail"):
            cands = [(eq, E(calc2(c, v, eq, 1), w)[0]) for eq in R.EQUIPMENT]
            eq, e = max(cands, key=lambda t: t[1])
            nd = R.score(R.no_device(c, v), G, w)[0]
            out["T6"].append(dict(profile=name, city=c, venue=v, eq=eq, E=round(e, 4), none=round(nd, 4)))

# T4 rail 1v2
out["T4"] = []
for c in ("PHX", "HK"):
    for eq in R.EQUIPMENT:
        for n in (1, 2):
            r = calc2(c, "rail", eq, n)
            e, i, b, s = E(r)
            out["T4"].append(dict(city=c, eq=eq, n=n, phi=round(r["phi"], 3), dT=round(r["dT"], 3),
                                  lcc=round(r["lcc"], 2), wbgt=round(r["wbgt"], 2),
                                  s=round(s, 3), E=round(e, 4)))

# open-air
out["OA"] = []
for c in ("PHX", "HK"):
    nd = R.no_device(c, "oa"); nd["wbgt"] += GLOBE; nd["wbgt_amb"] += GLOBE
    out["OA"].append(dict(city=c, eq="none", E=round(R.score(nd, G)[0], 4)))
    for eq in R.EQUIPMENT:
        r = calc2(c, "oa", eq, 1)
        r["wbgt"] += GLOBE; r["wbgt_amb"] += GLOBE
        out["OA"].append(dict(city=c, eq=eq, phi=round(r["phi"], 3), dT=round(r["dT"], 3),
                              eta=round(r["eta"], 1), E=round(R.score(r, G)[0], 4)))

with open(r"C:\Users\kukat\Desktop\USA\_extract\v2_numbers.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

for r in out["T3"]:
    print("T3", r)
for r in out["T5"]:
    if r["venue"] == "bus":
        print("T5", r)
for r in out["T6"]:
    print("T6", r)
for r in out["T4"]:
    print("T4", r)
for r in out["OA"]:
    print("OA", r)
