import math
import recompute as R

R.MODE = "pressure"
R.THRESH = 30.0

def show_gamma():
    print("gamma sweep, PHX bus MC37V (pressure, 30C):")
    for g in [0.20, 0.35, 0.55, 0.75]:
        R.VENUE["bus"]["g"] = g
        r = R.calc("PHX", "bus", "MC37V", 1, wetbulb="pressure")
        print("  gamma=%.2f dTeff=%.3f eta=%.2f wbgt=%.2f" % (g, r["dT"], r["eta"], r["wbgt"]))
    R.VENUE["bus"]["g"] = 0.55

def show_rh():
    print("\nRH sweep, PHX bus MC37V at 41C (bus):")
    for rh in [10, 30, 40, 50, 60, 68, 70, 80, 90]:
        R.CITY["PHX"]["RH"] = rh
        r = R.calc("PHX", "bus", "MC37V", 1, wetbulb="pressure")
        print("  RH=%3d dTeff=%.3f dTphys=%.2f wbgt=%.2f" % (rh, r["dT"], r["dTphys"], r["wbgt"]))
    R.CITY["PHX"]["RH"] = 18.0
    print("\nRH sweep, HK rail MC37V at 32.5C:")
    for rh in [60, 70, 75, 78, 80, 85]:
        R.CITY["HK"]["RH"] = rh
        r = R.calc("HK", "rail", "MC37V", 1, wetbulb="pressure")
        print("  RH=%3d dTeff=%.3f dTphys=%.2f wbgt=%.2f" % (rh, r["dT"], r["dTphys"], r["wbgt"]))
    R.CITY["HK"]["RH"] = 78.0

def show_concession():
    rows, g = R.table4_rows("pressure", 30.0)
    for city, eq, n in [("HK", "MC37V", 1), ("HK", "MC61V", 1)]:
        r = next(x for x in rows if x["city"] == city and x["eq"] == eq and x["n"] == n)
        water = R.CITY["HK"]["H"] * (r["V"] / 1000) * R.CITY["HK"]["pw"]
        new_lcc = r["lcc"] - water / 2
        # recompute E with new lcc
        r2 = dict(r); r2["lcc"] = new_lcc
        E2, I, sc, ss = R.score(r2, g, threshold=30.0)
        print("  %s n=%d water=%.2f LCC %.2f -> %.2f E %.4f -> %.4f" % (eq, n, water, r["lcc"], new_lcc, R.score(r, g, threshold=30.0)[0], E2))

def show_2026():
    print("\n2026 scenario: PHX rates +3%/yr for 2 years (x1.0609):")
    e0, w0 = R.CITY["PHX"]["pe"], R.CITY["PHX"]["pw"]
    R.CITY["PHX"]["pe"] = e0 * 1.0609
    R.CITY["PHX"]["pw"] = w0 * 1.0609
    rows, g = R.table4_rows("pressure", 30.0)
    for eq, n in [("MC37V", 1), ("MC61V", 1), ("MC37V", 2), ("Fan", 1)]:
        r = next(x for x in rows if x["city"] == "PHX" and x["eq"] == eq and x["n"] == n)
        print("  PHX %-5s n=%d LCC=%.2f E=%.4f" % (eq, n, r["lcc"], R.score(r, g, threshold=30.0)[0]))
    R.CITY["PHX"]["pe"], R.CITY["PHX"]["pw"] = e0, w0

if __name__ == "__main__":
    show_gamma()
    show_rh()
    show_concession()
    show_2026()
