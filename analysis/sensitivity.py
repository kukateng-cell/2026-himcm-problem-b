import copy
import recompute as R

R.MODE = "pressure"
R.THRESH = 30.0

OPTIONS = [
    ("PHX", "MC37V", 1), ("PHX", "MC61V", 1), ("PHX", "MC37V", 2),
    ("HK", "MC37V", 1), ("HK", "MC61V", 1), ("HK", "Fan", 1), ("HK", "Fan", 2),
]


def metrics():
    rows, g = R.table4_rows("pressure", R.THRESH)
    out = {}
    for city, eq, n in OPTIONS:
        r = next(x for x in rows if x["city"] == city and x["eq"] == eq and x["n"] == n)
        E, I, sc, ss = R.score(r, g, threshold=R.THRESH)
        out[(city, eq, n)] = dict(E=E, I=I, dT=r["dT"], phi=r["phi"], wbgt=r["wbgt"], lcc=r["lcc"])
    return out


def apply(fn):
    eq0, city0, venue0 = copy.deepcopy(R.EQUIPMENT), copy.deepcopy(R.CITY), copy.deepcopy(R.VENUE)
    k0, t0 = R.KAPPA, R.THRESH
    try:
        fn()
        return metrics()
    finally:
        R.EQUIPMENT, R.CITY, R.VENUE, R.KAPPA, R.THRESH = eq0, city0, venue0, k0, t0


def main():
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

    variations = [
        ("epsilon=0.70", lambda: set_eps(0.70)),
        ("epsilon=0.90", lambda: set_eps(0.90)),
        ("dTnom=8.8", lambda: set_dtn(8.8)),
        ("dTnom=13.2", lambda: set_dtn(13.2)),
        ("L_life -30%", lambda: scale("L", 0.7)),
        ("L_life +30%", lambda: scale("L", 1.3)),
        ("r_om -50%", lambda: scale("r", 0.5)),
        ("r_om +50%", lambda: scale("r", 1.5)),
        ("V_w -30%", lambda: scale("V", 0.7)),
        ("V_w +30%", lambda: scale("V", 1.3)),
        ("p_elec -20%", lambda: [R.CITY[c].__setitem__("pe", R.CITY[c]["pe"] * 0.8) for c in R.CITY]),
        ("p_elec +20%", lambda: [R.CITY[c].__setitem__("pe", R.CITY[c]["pe"] * 1.2) for c in R.CITY]),
        ("p_water -50%", lambda: [R.CITY[c].__setitem__("pw", R.CITY[c]["pw"] * 0.5) for c in R.CITY]),
        ("p_water +50%", lambda: [R.CITY[c].__setitem__("pw", R.CITY[c]["pw"] * 1.5) for c in R.CITY]),
        ("H_yr -20%", lambda: [R.CITY[c].__setitem__("H", R.CITY[c]["H"] * 0.8) for c in R.CITY]),
        ("H_yr +20%", lambda: [R.CITY[c].__setitem__("H", R.CITY[c]["H"] * 1.2) for c in R.CITY]),
        ("kappa=30", lambda: setattr(R, "KAPPA", 30.0)),
        ("kappa=60", lambda: setattr(R, "KAPPA", 60.0)),
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

    base = metrics()
    cols = [("PHX37", ("PHX", "MC37V", 1)), ("PHX61", ("PHX", "MC61V", 1)),
            ("PHX2x37", ("PHX", "MC37V", 2)), ("HK37", ("HK", "MC37V", 1)),
            ("HK61", ("HK", "MC61V", 1)), ("HKfan", ("HK", "Fan", 1)),
            ("HK2fan", ("HK", "Fan", 2))]
    print("%-18s" % "case" + "".join("%9s" % c[0] for c in cols))
    print("%-18s" % "BASE" + "".join("%9.4f" % base[k]["E"] for _, k in cols))
    for name, fn in variations:
        m = apply(fn)
        print("%-18s" % name + "".join("%9.4f" % m[k]["E"] for _, k in cols))


if __name__ == "__main__":
    main()
