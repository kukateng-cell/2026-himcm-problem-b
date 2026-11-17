"""Structural checks behind the five open items (kappa, crosswind, wind-aware
safety, joint operating point, traceability).

Run with the system Python (numpy/matplotlib not required):
    "C:\\Users\\kukat\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" analysis/structural_checks.py

Outputs
-------
1. kappa_from_jet(): free-jet estimate of kappa for the MC37V geometry.
2. wind_safe_table(): E with a wind-corrected natural wet bulb.
3. cw_threshold(): the c_w at which the HK platform fan overtakes MC37V.
4. joint_ratios(): energy-balance water vs manufacturer water for each unit.
"""

import math
import sys

import recompute as R

R.MODE = "pressure"
R.THRESH = 33.0


def kappa_from_jet():
    """Free-jet centreline velocity -> kappa = u(x) / (Q / A_cov)."""
    Q = 3100 * 1.699 / 3600.0          # m3/s, MC37V
    A0 = 0.45                           # m2, assumed outlet grille 0.75 x 0.60
    A_cov = 88.0                        # m2, manufacturer coverage
    u0 = Q / A0
    C = 2.4                             # rectangular free-jet constant
    q = Q / A_cov
    rows = []
    for x in (2, 3, 4, 6, 8, 10):
        u = C * u0 * math.sqrt(A0) / x
        rows.append((x, u, u / q))
    return Q, A0, u0, q, rows


def baseline_norm():
    rows = [R.calc(c, v, e, n) for c in R.CITY for v in R.VENUE
            for e in R.EQUIPMENT for n in (1, 2)]
    return R.norm(rows)


def score_wind(r, g, cw, v_ref=0.5, w=(0.30, 0.30, 0.20, 0.20)):
    """E with T_nwb = T_wb - cw (v - v_ref) in the WBGT proxy."""
    e = R.EQUIPMENT[r["eq"]]
    c = R.CITY[r["city"]]
    Q = e["CFM"] * 1.699 / 3600.0
    veff = c["v"] + R.KAPPA * Q / e["A"]
    wb = r["wbgt"] - 0.7 * cw * (veff - v_ref)
    wba = r["wbgt_amb"] - 0.7 * cw * (c["v"] - v_ref)
    phi = r["phi"]
    ss = phi * R.sat(wb) + (1 - phi) * R.sat(wba)
    gg = g[r["venue"]]
    N = R.VENUE[r["venue"]]["N"]
    benefit = phi * N * r["dT"] / gg["B"]
    ienv = 0.5 * r["eco2"] / gg["E"] + 0.5 * r["weq"] / gg["W"]
    return (w[0] * ss + w[1] * benefit - w[2] * r["lcc"] / gg["L"]
            - w[3] * ienv)


def wind_safe_table():
    g = baseline_norm()
    rows, _ = R.table4_rows("pressure", 33.0)
    pick = {("HK", "MC37V"): None, ("HK", "Fan"): None,
            ("PHX", "MC37V"): None, ("PHX", "MC61V"): None}
    for r in rows:
        if r["n"] == 1 and (r["city"], r["eq"]) in pick:
            pick[(r["city"], r["eq"])] = r
    out = []
    for cw in (0.0, 0.05, 0.10, 0.15):
        out.append((cw, {k: score_wind(v, g, cw) for k, v in pick.items()}))
    return out


def cw_threshold():
    g = baseline_norm()
    rows, _ = R.table4_rows("pressure", 33.0)
    hk = {r["eq"]: r for r in rows if r["city"] == "HK" and r["n"] == 1}
    def gap(cw):
        return score_wind(hk["MC37V"], g, cw) - score_wind(hk["Fan"], g, cw)
    lo, hi = 0.0, 2.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if gap(mid) > 0:
            lo = mid
        else:
            hi = mid
    return hi


def joint_ratios():
    rows = []
    for city in ("PHX", "HK"):
        for eq in ("MC37V", "MC61V", "Porta"):
            r = R.calc(city, "bus", eq, 1)
            vman = R.EQUIPMENT[eq]["V"]
            rows.append((city, eq, r["Vw"], vman, r["Vw"] / vman))
    return rows


if __name__ == "__main__":
    Q, A0, u0, q, rows = kappa_from_jet()
    print("kappa_from_jet: Q=%.3f m3/s A0=%.2f u0=%.2f q=%.4f m/s" % (Q, A0, u0, q))
    for x, u, k in rows:
        print("  x=%-2d m  u=%.2f m/s  kappa=%.0f" % (x, u, k))
    print("\nwind-aware safety (E):")
    for cw, vals in wind_safe_table():
        print("  cw=%.2f  " % cw + "  ".join("%s-%s %.4f" % (k[0], k[1], v) for k, v in vals.items()))
    print("\nfan overtakes MC37V at cw = %.3f K/(m/s)" % cw_threshold())
    print("\njoint water ratio (balance / manufacturer):")
    for city, eq, vbal, vman, ratio in joint_ratios():
        print("  %s %-6s balance %.1f L/h vs manufacturer %.1f L/h  ratio %.2f"
              % (city, eq, vbal, vman, ratio))
