# -*- coding: utf-8 -*-
"""v2 model: venue-specific kappa (bus 84 / rail 45), 30% overlap for n=2."""
import itertools
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recompute as R

KAPPA_V = {"bus": 84.0, "rail": 45.0, "oa": 45.0}
OVERLAP = 0.30

def calc2(city, venue, eq, n=1, eqtable=None):
    R.KAPPA = KAPPA_V[venue]
    r = R.calc(city, venue, eq, n, eqtable=eqtable)
    if n == 2:
        r["phi"] = min(1.0, n * r["A_cov"] * (1 - OVERLAP) / r["Az"])
    return r

def rows_all(venues=("bus", "rail")):
    return [calc2(c, v, e, n) for c, v, e, n in itertools.product(R.CITY, venues, R.EQUIPMENT, (1, 2))]

G2 = R.norm(rows_all())

def score2(r, w=(0.30, 0.30, 0.20, 0.20), threshold=33.0):
    return R.score(r, G2, w, threshold)

print("=== Table 3 (Q2a, PHX bus, kappa=84) ===")
q2a = {
    "A": dict(P=0.25, CFM=2250, A=15, eps=0.00, dTnom=0.0, C=250, L=7, r=0.03, V=0.0),
    "B": dict(P=1.20, CFM=917, A=15, eps=0.80, dTnom=5.0, C=750, L=5, r=0.08, V=15.0),
    "C": dict(P=2.50, CFM=1031, A=15, eps=0.80, dTnom=8.0, C=1277, L=5, r=0.08, V=30.0),
}
for k in q2a:
    r = calc2("PHX", "bus", k, 1, eqtable=q2a)
    E, I, B, S = score2(r)
    print(f" {k}: dT={r['dT']:.3f} phi={r['phi']:.3f} eta={r['eta']:.2f} LCC={r['lcc']:.2f} WBGT={r['wbgt']:.2f} E={E:.4f}")

print("\n=== Table 5 bus rows (v2) ===")
for c in ("PHX", "HK"):
    for e in R.EQUIPMENT:
        r = calc2(c, "bus", e, 1)
        E, I, B, S = score2(r)
        print(f" {c} bus {e:6s}: dT={r['dT']:.3f} phi={r['phi']:.3f} eta={r['eta']:.1f} LCC={r['lcc']:.2f} I={I:.4f} E={E:.4f}")

print("\n=== Table 6 bus winners (v2) ===")
for name, w in R.PROFILES.items():
    for c in ("PHX", "HK"):
        best = None
        for e in R.EQUIPMENT:
            r = calc2(c, "bus", e, 1)
            E = score2(r, w)[0]
            if best is None or E > best[1]:
                best = (e, E)
        nd = R.no_device(c, "bus")
        print(f" {name:8s} {c} bus -> {best[0]} {best[1]:.4f} | none {R.score(nd, G2, w)[0]:.4f}")

print("\n=== Table 4 two-unit rows (v2, overlap) ===")
for c, e, n in itertools.product(("PHX", "HK"), R.EQUIPMENT, (1, 2)):
    r = calc2(c, c and "rail", e, n)
    E = score2(r)[0]
    print(f" {c} rail {e:6s} n={n}: phi={r['phi']:.3f} dT={r['dT']:.3f} E={E:.4f}")

print("\n=== no-device baselines (v2 normalisers) ===")
for c in ("PHX", "HK"):
    for v in ("bus", "rail"):
        nd = R.no_device(c, v)
        print(f" {c} {v}: E={score2(nd)[0]:.4f}")
