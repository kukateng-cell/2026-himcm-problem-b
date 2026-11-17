# -*- coding: utf-8 -*-
"""Residual-issue audit of the delivered paper."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx import Document
import recompute as R

P = r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"
d = Document(P)

print("== paragraphs containing key phrases ==")
keys = ["kappa", "κ = 84", "κ ≈ 84", "Structural stress", "under the base normalisers",
        "149 LRVs", "65.1", "76.7", "+6 K", "unverified", "six-equation", "Eqs. 1–7"]
for p in d.paragraphs:
    t = p.text
    if any(k in t for k in keys):
        print("-", t[:300].replace("\n", " "))

print("\n== Appendix A status column ==")
for tb in d.tables:
    hdr = [c.text.strip() for c in tb.rows[0].cells]
    if "Status" in hdr:
        idx = hdr.index("Status")
        vals = [r.cells[idx].text.strip() for r in tb.rows[1:]]
        print("table status values:", sorted(set(vals)))

print("\n== kappa 80/84/92/105 recompute (base normalisers) ==")
g = R.set_B()
R.KAPPA = 45
print("base dT/E:", {e: (round(R.calc('PHX','bus',e,1)['dT'],3), round(R.score(R.calc('PHX','bus',e,1), g)[0],4)) for e in ('MC37V','Fan')})
for kap in (80, 84, 92, 105):
    R.KAPPA = kap
    row = {}
    for e in ("MC37V", "Fan"):
        r = R.calc("PHX", "bus", e, 1)
        row[e] = (round(r["dT"], 3), round(R.score(r, g)[0], 4))
    print(f"kappa={kap}: {row}")
R.KAPPA = 45

print("\n== stress paragraph ==")
for p in d.paragraphs:
    if p.text.startswith("Structural stress"):
        print(p.text)
