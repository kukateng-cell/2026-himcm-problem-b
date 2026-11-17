# -*- coding: utf-8 -*-
"""Regenerate Table B1 (single-factor sensitivity) under the v2 model."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recompute as R
import sensitivity as S

R.THRESH = 33.0
g0 = R.table4_rows("pressure", R.THRESH)[1]
base = S.metrics(g0)
COLS = [("PHX", "MC37V", 1), ("PHX", "MC61V", 1), ("HK", "MC37V", 1), ("HK", "Fan", 1)]

out = [("BASE", [round(base[k]["E"], 4) for k in COLS])]
for name, fn in S.variations():
    m = S.apply(fn, g0)
    out.append((name, [round(m[k]["E"], 4) for k in COLS]))

for name, vals in out:
    print("%-18s" % name + "".join("%9.4f" % v for v in vals))

with open(r"C:\Users\kukat\Desktop\USA\_extract\b1_v2.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
