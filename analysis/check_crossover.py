# -*- coding: utf-8 -*-
"""Full-model RH crossover for MC37V vs the 2.081 C fan, per city."""
import copy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import recompute as R

for city, T in (("PHX", 41.0), ("HK", 31.7)):
    base = copy.deepcopy(R.CITY[city])
    R.CITY[city]["T"] = T
    for venue in ("bus", "rail"):
        def dt(rh):
            R.CITY[city]["RH"] = rh
            return R.calc(city, venue, "MC37V", 1, "pressure")["dT"]
        fan = R.calc(city, venue, "Fan", 1, "pressure")["dT"]
        lo, hi = 10.0, 95.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if dt(mid) > fan:
                lo = mid
            else:
                hi = mid
        print(f"{city} T={T} {venue:4s} fan={fan:.3f}  crossover={((lo+hi)/2):.2f}%")
    R.CITY[city] = base
