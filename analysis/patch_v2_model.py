# -*- coding: utf-8 -*-
"""Patch recompute.py to the v2 model (venue kappa, fan cap, 30% overlap)."""
import io

P = r"C:\Users\kukat\Desktop\USA\analysis\recompute.py"
s = io.open(P, encoding="utf-8").read()
open(P.replace(".py", "_v1_backup.py"), "w", encoding="utf-8").write(s)

if "KAPPA_V" not in s:
    s = s.replace(
        "KAPPA = 45.0\n",
        "KAPPA = 45.0\n"
        "KAPPA_V = {\"bus\": 84.0, \"rail\": 45.0}   # v1.3: venue-specific jet-mixing coefficient\n"
        "OVERLAP = 0.30                              # v1.3: two-unit jet overlap\n"
        "FAN_CAP = 3.0                               # v1.3: prompt's 'up to 3 C' felt-cooling cap\n",
    )
s = s.replace(
    '    veff = c["v"] + KAPPA * Q / e["A"]\n'
    '    dTeff = tapp(c["T"], eamb, c["v"]) - tapp(Tz, ez, veff)\n'
    '    phi = min(1.0, n * e["A"] / Az)\n',
    '    kappa = KAPPA_V.get(venue, KAPPA)\n'
    '    veff = c["v"] + kappa * Q / e["A"]\n'
    '    dTeff = tapp(c["T"], eamb, c["v"]) - tapp(Tz, ez, veff)\n'
    '    if e["eps"] == 0:\n'
    '        dTeff = min(dTeff, FAN_CAP)\n'
    '    phi = min(1.0, n * e["A"] * (1 - OVERLAP * (n - 1)) / Az)\n',
)
io.open(P, "w", encoding="utf-8").write(s)

S = r"C:\Users\kukat\Desktop\USA\analysis\sensitivity.py"
t = io.open(S, encoding="utf-8").read()
t = t.replace('("kappa=30", lambda: setattr(R, "KAPPA", 30.0)),',
              '("kappa=30", lambda: setattr(R, "KAPPA_V", {"bus": 30.0, "rail": 30.0})),')
t = t.replace('("kappa=60", lambda: setattr(R, "KAPPA", 60.0)),',
              '("kappa=60", lambda: setattr(R, "KAPPA_V", {"bus": 60.0, "rail": 60.0})),')
io.open(S, "w", encoding="utf-8").write(t)
print("patched")
