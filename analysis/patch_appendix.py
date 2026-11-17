# -*- coding: utf-8 -*-
"""Add Appendix B row-label specs to apply_math.py."""
import io

p = r"analysis/apply_math.py"
s = io.open(p, encoding="utf-8").read()

extra = '''    (20, 2, 0): [(M, r"\\varepsilon=0.70")],
    (20, 3, 0): [(M, r"\\varepsilon=0.90")],
    (20, 4, 0): [(M, r"\\Delta T_{\\mathrm{nom}}=8.8")],
    (20, 5, 0): [(M, r"\\Delta T_{\\mathrm{nom}}=13.2")],
    (20, 18, 0): [(M, r"\\kappa=30")],
    (20, 19, 0): [(M, r"\\kappa=105")],
    (20, 20, 0): [(M, r"\\gamma=-0.10")],
    (20, 21, 0): [(M, r"\\gamma=+0.10")],
    (20, 24, 0): [(M, r"BWS_{\\mathrm{HK}}=0.850")],
    (20, 25, 0): [(M, r"EF_{\\mathrm{HK}}=0.465")],
    (20, 26, 0): [(M, r"EF_{\\mathrm{PHX}}=0.25")],
    (20, 27, 0): [(M, r"EF_{\\mathrm{PHX}}=0.36")],
}
'''
s = s.replace('''    (3, 3, 1): [(M, r"p_{s}")],
}
''', '''    (3, 3, 1): [(M, r"p_{s}")],
''' + extra, 1)
io.open(p, "w", encoding="utf-8").write(s)
print("added appendix specs", s.count("BWS_{\\\\mathrm{HK}}=0.850"))
