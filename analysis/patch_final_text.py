# -*- coding: utf-8 -*-
import io
p = r"analysis/apply_math.py"
s = io.open(p, encoding="utf-8").read()
old1 = r'''        (D, r"I_{\mathrm{env}}=\alpha_{c}\frac{E_{\mathrm{CO₂}}}{E_{\mathrm{CO₂,max}}}+\alpha_{w}\frac{W_{\mathrm{eq}}}{W_{\mathrm{eq,max}}},\qquad \alpha_{c}=\alpha_{w}=0.50;", "(Eq. 5)"),'''
new1 = r'''        (D, r"I_{\mathrm{env}}=\alpha_{c}\frac{E_{\mathrm{CO₂}}}{E_{\mathrm{CO₂,max}}}+\alpha_{w}\frac{W_{\mathrm{eq}}}{W_{\mathrm{eq,max}}},\qquad \text{with }\alpha_{c}=\alpha_{w}=0.50;", "(Eq. 5)"),'''
assert old1 in s
s = s.replace(old1, new1)
old2 = r'''        (D, r"\left(w_{1},w_{2},w_{3},w_{4}\right)=\left(0.30,\;0.30,\;0.20,\;0.20\right).", ""),'''
new2 = r'''        (D, r"\text{baseline weights }\left(w_{1},w_{2},w_{3},w_{4}\right)=\left(0.30,\;0.30,\;0.20,\;0.20\right).", ""),'''
assert old2 in s
s = s.replace(old2, new2)
io.open(p, "w", encoding="utf-8").write(s)
print("fixed with/baseline weights")
