# -*- coding: utf-8 -*-
import io
P = r"C:\Users\kukat\Desktop\USA\analysis\sensitivity.py"
s = io.open(P, encoding="utf-8").read()
# restore KAPPA_V in apply()
s = s.replace(
    "    k0, t0, w0 = R.KAPPA, R.THRESH, R.WATER_MULT\n",
    "    k0, t0, w0 = R.KAPPA, R.THRESH, R.WATER_MULT\n"
    "    kv0 = dict(R.KAPPA_V)\n",
)
s = s.replace(
    "        R.EQUIPMENT, R.CITY, R.VENUE, R.KAPPA, R.THRESH, R.WATER_MULT = eq0, city0, venue0, k0, t0, w0\n",
    "        R.EQUIPMENT, R.CITY, R.VENUE, R.KAPPA, R.THRESH, R.WATER_MULT = eq0, city0, venue0, k0, t0, w0\n"
    "        R.KAPPA_V = kv0\n",
)
s = s.replace('("kappa=30", lambda: setattr(R, "KAPPA_V", {"bus": 30.0, "rail": 30.0})),',
              '("kappa=45", lambda: setattr(R, "KAPPA_V", {"bus": 45.0, "rail": 45.0})),')
s = s.replace('("kappa=60", lambda: setattr(R, "KAPPA_V", {"bus": 60.0, "rail": 60.0})),',
              '("kappa=105", lambda: setattr(R, "KAPPA_V", {"bus": 105.0, "rail": 105.0})),')
io.open(P, "w", encoding="utf-8").write(s)
print("sensitivity patched")
