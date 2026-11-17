# -*- coding: utf-8 -*-
import io
p = r"analysis/apply_math.py"
s = io.open(p, encoding="utf-8").read()
old = '''        num = m.group(3).replace(",", "")
        if "$" in num or "−" in num:'''
new = '''        num = m.group(3)
        b = m.end()
        while num.endswith(","):
            num = num[:-1]
            b -= 1
        num = num.replace(",", "")
        if "$" in num or "−" in num:'''
assert old in s
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8").write(s)
print("patched trailing comma")
