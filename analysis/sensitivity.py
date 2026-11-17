"""Single-factor sensitivity for the 2026 HiMCM Problem B paper.

Fixed-denominator policy (2026-11-15):
    The Set B normalisers (ΔT_max, LCC_max, E_CO2,max, W_eq,max) are computed
    ONCE from the baseline scenario and then held fixed for every variation.
    Recomputing them inside each scenario (the earlier behaviour) lets a cost
    increase raise E, because the cost row is renormalised against a higher
    denominator; such scores are not comparable across rows.

    The per-scenario variant is kept only for the internal check
    "relative ranking within scenario" (--per-scenario).

Run:
    python analysis/sensitivity.py                 # fixed baseline denominators
    python analysis/sensitivity.py --per-scenario  # old behaviour, internal only
"""

import copy
import sys

import recompute as R

R.MODE = "pressure"
R.THRESH = 33.0

OPTIONS = [
    ("PHX", "MC37V", 1), ("PHX", "MC61V", 1), ("PHX", "MC37V", 2),
    ("HK", "MC37V", 1), ("HK", "MC61V", 1), ("HK", "Fan", 1), ("HK", "Fan", 2),
]


def metrics(g=None):
    """E for the seven options; g=None recomputes normalisers (old behaviour)."""
    rows, g_calc = R.table4_rows("pressure", R.THRESH)
    g = g_calc if g is None else g
    out = {}
    for city, eq, n in OPTIONS:
        r = next(x for x in rows if x["city"] == city and x["eq"] == eq and x["n"] == n)
        E, I, sc, ss = R.score(r, g, threshold=R.THRESH)
        out[(city, eq, n)] = dict(E=E, I=I, dT=r["dT"], phi=r["phi"], wbgt=r["wbgt"], lcc=r["lcc"])
    return out


def apply(fn, g=None):
    eq0, city0, venue0 = copy.deepcopy(R.EQUIPMENT), copy.deepcopy(R.CITY), copy.deepcopy(R.VENUE)
    k0, t0, w0 = R.KAPPA, R.THRESH, R.WATER_MULT
    kv0 = dict(R.KAPPA_V)
    try:
        fn()
        return metrics(g)
    finally:
        R.EQUIPMENT, R.CITY, R.VENUE, R.KAPPA, R.THRESH, R.WATER_MULT = eq0, city0, venue0, k0, t0, w0
        R.KAPPA_V = kv0


def variations():
    def set_eps(v):
        for e in R.EQUIPMENT.values():
            if e["eps"] > 0:
                e["eps"] = v
    def set_dtn(v):
        for e in R.EQUIPMENT.values():
            if e["dTnom"] > 0:
                e["dTnom"] = v
    def set_gamma(d):
        for ve in R.VENUE.values():
            ve["g"] = min(0.95, max(0.05, ve["g"] + d))
    def scale(field, f, only=None):
        for e in R.EQUIPMENT.values():
            if only is None or e["P"] == only:
                e[field] *= f

    return [
        ("epsilon=0.70", lambda: set_eps(0.70)),
        ("epsilon=0.90", lambda: set_eps(0.90)),
        ("dTnom=8.8", lambda: set_dtn(8.8)),
        ("dTnom=13.2", lambda: set_dtn(13.2)),
        ("L_life -30%", lambda: scale("L", 0.7)),
        ("L_life +30%", lambda: scale("L", 1.3)),
        ("r_om -50%", lambda: scale("r", 0.5)),
        ("r_om +50%", lambda: scale("r", 1.5)),
        ("V_w -30%", lambda: setattr(R, "WATER_MULT", 0.7)),
        ("V_w +30%", lambda: setattr(R, "WATER_MULT", 1.3)),
        ("p_elec -20%", lambda: [R.CITY[c].__setitem__("pe", R.CITY[c]["pe"] * 0.8) for c in R.CITY]),
        ("p_elec +20%", lambda: [R.CITY[c].__setitem__("pe", R.CITY[c]["pe"] * 1.2) for c in R.CITY]),
        ("p_water -50%", lambda: [R.CITY[c].__setitem__("pw", R.CITY[c]["pw"] * 0.5) for c in R.CITY]),
        ("p_water +50%", lambda: [R.CITY[c].__setitem__("pw", R.CITY[c]["pw"] * 1.5) for c in R.CITY]),
        ("H_yr -20%", lambda: [R.CITY[c].__setitem__("H", R.CITY[c]["H"] * 0.8) for c in R.CITY]),
        ("H_yr +20%", lambda: [R.CITY[c].__setitem__("H", R.CITY[c]["H"] * 1.2) for c in R.CITY]),
        ("kappa=30", lambda: setattr(R, "KAPPA_V", {"bus": 30.0, "rail": 30.0})),
        ("kappa=105", lambda: setattr(R, "KAPPA_V", {"bus": 105.0, "rail": 105.0})),
        ("gamma -0.10", lambda: set_gamma(-0.10)),
        ("gamma +0.10", lambda: set_gamma(+0.10)),
        ("A_cov -20%", lambda: scale("A", 0.8)),
        ("A_cov +20%", lambda: scale("A", 1.2)),
        ("BWS_HK=0.850", lambda: R.CITY["HK"].__setitem__("BWS", 0.850)),
        ("EF_HK=0.465", lambda: R.CITY["HK"].__setitem__("EF", 0.465)),
        ("EF_PHX=0.25", lambda: R.CITY["PHX"].__setitem__("EF", 0.25)),
        ("EF_PHX=0.36", lambda: R.CITY["PHX"].__setitem__("EF", 0.36)),
        ("threshold=28", lambda: setattr(R, "THRESH", 28.0)),
    ]


def main():
    per_scenario = "--per-scenario" in sys.argv
    g0 = None
    if not per_scenario:
        g0 = R.table4_rows("pressure", R.THRESH)[1]

    base = metrics(g0)
    cols = [("PHX37", ("PHX", "MC37V", 1)), ("PHX61", ("PHX", "MC61V", 1)),
            ("PHX2x37", ("PHX", "MC37V", 2)), ("HK37", ("HK", "MC37V", 1)),
            ("HK61", ("HK", "MC61V", 1)), ("HKfan", ("HK", "Fan", 1)),
            ("HK2fan", ("HK", "Fan", 2))]
    print("%-18s" % "case" + "".join("%9s" % c[0] for c in cols))
    print("%-18s" % "BASE" + "".join("%9.4f" % base[k]["E"] for _, k in cols))
    for name, fn in variations():
        m = apply(fn, g0)
        print("%-18s" % name + "".join("%9.4f" % m[k]["E"] for _, k in cols))


if __name__ == "__main__":
    main()
