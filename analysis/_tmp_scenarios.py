import json
import sys

sys.path.insert(0, "analysis")
import recompute as R

g = R.set_B()
out = {}


def add(key, value):
    out[key] = value


for c, v, e in [
    ("PHX", "bus", "MC37V"), ("PHX", "rail", "MC61V"),
    ("HK", "bus", "Fan"), ("HK", "bus", "MC37V"),
    ("HK", "rail", "MC37V"), ("HK", "rail", "MC61V"), ("HK", "rail", "Fan"),
]:
    r = R.calc(c, v, e, 1)
    E, I, b, s = R.score(r, g)
    add(f"{c}_{v}_{e}", dict(E=round(E, 4), phi=round(r["phi"], 3), dT=round(r["dT"], 2),
                             lcc=round(r["lcc"], 2), I=round(I, 4), wbgt=round(r["wbgt"], 2),
                             wbgt_amb=round(r["wbgt_amb"], 2), Vw=round(r["Vw"], 1),
                             benefit=round(b, 3), S=round(s, 3)))

for c in ("PHX", "HK"):
    for v in ("bus", "rail"):
        add(f"none_{c}_{v}", round(R.score(R.no_device(c, v), g)[0], 4))

L = g["rail"]["L"]
for key in ["HK_rail_MC37V", "HK_bus_Fan", "HK_bus_MC37V", "PHX_rail_MC61V", "PHX_bus_MC37V"]:
    c, v, e = key.split("_")
    r = R.calc(c, v, e, 1)
    add(f"inst_{key}", round(R.score(r, g)[0] - 0.2 * (900 / 10 + 150 if v == "rail" else 450 / 10 + 150) / L, 4))

R.WATER_MODE = "manufacturer"
for key in ["PHX_rail_MC37V", "PHX_rail_MC61V", "HK_rail_MC37V", "HK_bus_MC37V"]:
    c, v, e = key.split("_")
    add("wm_" + key, round(R.score(R.calc(c, v, e, 1), g)[0], 4))
R.WATER_MODE = "balance"

for e, phi, dT, lcc, I, S in [("MC37V", 0.733, 6.534, 243.80, 0.2817, 1.0),
                              ("MC61V", 1.0, 6.543, 397.41, 0.4831, 1.0)]:
    B = phi * 6 * dT / (45 * 2.0)
    add(f"n6_PHX_rail_{e}", round(0.3 * S + 0.3 * B - 0.2 * lcc / 794.817 - 0.2 * I, 4))

for c, v, e in [("HK", "rail", "MC37V"), ("HK", "bus", "Fan"), ("HK", "bus", "MC37V")]:
    add(f"iso30_{c}_{v}_{e}", round(R.score(R.calc(c, v, e, 1), g, threshold=30.0)[0], 4))
add("iso30_none_HK_rail", round(R.score(R.no_device("HK", "rail"), g, threshold=30.0)[0], 4))

base_hk = dict(R.CITY["HK"])
for T, RH, tag in [(32.5, 78, "d3278"), (33.5, 62, "d33562")]:
    R.CITY["HK"].update(T=T, RH=RH)
    for v, e in [("bus", "Fan"), ("bus", "MC37V"), ("rail", "MC37V"), ("rail", "Fan"), ("rail", "MC61V")]:
        add(f"{tag}_HK_{v}_{e}", round(R.score(R.calc("HK", v, e, 1), g)[0], 4))
R.CITY["HK"].update(base_hk)

g0 = R.VENUE["bus"]["g"]
R.VENUE["bus"]["g"] = 0.0
q2a = {
    "A": dict(P=0.25, CFM=2250, A=15, eps=0.00, dTnom=0.0, C=250, L=7, r=0.03, V=0.0),
    "B": dict(P=1.20, CFM=917, A=15, eps=0.80, dTnom=5.0, C=750, L=5, r=0.08, V=15.0),
    "C": dict(P=2.50, CFM=1031, A=15, eps=0.80, dTnom=8.0, C=1277, L=5, r=0.08, V=30.0),
}
for k in q2a:
    add("q2a_lit_" + k, round(R.score(R.calc("PHX", "bus", k, 1, eqtable=q2a), g)[0], 4))
R.VENUE["bus"]["g"] = g0

for c, e in [("PHX", "MC37V"), ("PHX", "MC61V"), ("PHX", "Porta"),
             ("HK", "MC37V"), ("HK", "MC61V"), ("HK", "Porta")]:
    r = R.calc(c, "rail", e, 1)
    add(f"vw_{c}_{e}", [round(r["Vw"], 1), R.EQUIPMENT[e]["V"], round(r["Vw"] / R.EQUIPMENT[e]["V"], 2)])

print(json.dumps(out, indent=1, ensure_ascii=False))
