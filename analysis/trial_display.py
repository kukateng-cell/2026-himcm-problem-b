# -*- coding: utf-8 -*-
"""Trial: rebuild display equations (Eq. 1-7) with built-up OMML."""
import sys
from docx import Document
import mathdoc
import omml

src, dst = sys.argv[1], sys.argv[2]
doc = Document(src)
WIDTH = 9978

SPECS = {
    47: [("disp", r"\Delta T_{\mathrm{phys}}\;=\;\min\left(\Delta T_{\mathrm{nom}},\;\varepsilon\left(T_{\mathrm{db}}-T_{\mathrm{wb}}\right)\right).", "(Eq. 1)")],
    50: [("disp", r"\Delta T_{\mathrm{eff}}\;=\;AT\left(T_{\mathrm{db}},\,e_{\mathrm{amb}},\,v_{\mathrm{amb}}\right)-AT\left(T_{\mathrm{zone}},\,e_{\mathrm{zone}},\,v_{\mathrm{eff}}\right),", "(Eq. 2) [2]"),
         ("disp", r"AT\left(T,e,v\right)\;=\;T+0.33e-0.70v-4.00.", "")],
    54: [("disp", r"\eta\;=\;\frac{\varphi\cdot N_{\mathrm{eff}}\cdot\Delta T_{\mathrm{eff}}}{n\cdot P_{\mathrm{elec}}}", "(Eq. 3)"),
         ("disp", r"\varphi\;=\;\min\left(1,\;\frac{n\cdot A_{\mathrm{cov}}}{A_{\mathrm{waiting}}}\right).", "")],
    57: [("disp", r"LCC_{\mathrm{annual}}\;=\;\left(\frac{1}{L_{\mathrm{life}}}+r_{\mathrm{om}}\right)n\,C_{\mathrm{cap}}+H_{\mathrm{yr}}\left(n\,P_{\mathrm{elec}}\,p_{\mathrm{elec}}+\frac{n\,V_{\mathrm{w}}}{1000}\,p_{\mathrm{water}}\right).", "(Eq. 4)")],
    59: [("disp", r"V_{\mathrm{w}}\;=\;\frac{3600\;\dot{m}_{\mathrm{da}}\,c_{p}\,\Delta T_{\mathrm{phys}}}{L_{\mathrm{v}}},\qquad \dot{m}_{\mathrm{da}}\;=\;Q_{\mathrm{air}}\,\rho_{\mathrm{da}}.", "(Eq. 7)")],
    62: [("disp", r"I_{\mathrm{env}}\;=\;\alpha_{c}\frac{E_{\mathrm{CO_2}}}{E_{\mathrm{CO_2,max}}}+\alpha_{w}\frac{W_{\mathrm{eq}}}{W_{\mathrm{eq,max}}},\qquad \alpha_{c}=\alpha_{w}=0.50;", "(Eq. 5)"),
         ("disp", r"E_{\mathrm{CO_2}}\;=\;n\,P_{\mathrm{elec}}\,H_{\mathrm{yr}}\,EF_{\mathrm{grid}};\qquad W_{\mathrm{eq}}\;=\;\frac{n\,V_{\mathrm{w}}}{1000}\,H_{\mathrm{yr}}\,BWS_{\mathrm{raw}}.", "")],
    65: [("disp", r"E\;=\;w_{1}S_{\mathrm{safe}}+w_{2}B-w_{3}\widetilde{LCC}-w_{4}I_{\mathrm{env}}.", "(Eq. 6)")],
    66: [("disp", r"\mathrm{WBGT}_{\mathrm{proxy}}\;=\;0.7\,T_{\mathrm{wb,zone}}+0.3\,T_{\mathrm{zone}};", ""),
         ("disp", r"S_{\mathrm{safe}}\left(W\right)\;=\;\mathrm{clamp}\left(\frac{35-W}{6},\;0,\;1\right);", ""),
         ("disp", r"B\;=\;\frac{\varphi\,N_{\mathrm{eff}}\,\Delta T_{\mathrm{eff}}}{B_{\mathrm{max}}};\qquad \widetilde{LCC}\;=\;\frac{LCC}{LCC_{\mathrm{max}}};", ""),
         ("disp", r"\left(w_1,w_2,w_3,w_4\right)\;=\;\left(0.30,\;0.30,\;0.20,\;0.20\right).", "")],
}

for idx, parts in SPECS.items():
    p = doc.paragraphs[idx]
    mathdoc.clear_para(p)
    mathdoc.set_tabs(p, WIDTH)
    mathdoc.tight(p, 0, 0)
    for kind, *rest in parts:
        if kind == "disp":
            latex, label = rest
            mathdoc.add_tab(p)
            mathdoc.add_math(p, latex, display=False)
            if label:
                mathdoc.add_tab(p)
                mathdoc.add_text(p, label)
            mathdoc.add_break(p)
        else:
            text, bold = rest if len(rest) > 1 else (rest[0], False)
            mathdoc.add_text(p, text, bold=bold)
    # strip trailing break
    last = p._p[-1]
    if last.tag == mathdoc.qn("w:r") and last.find(mathdoc.qn("w:br")) is not None:
        p._p.remove(last)

doc.save(dst)
print("saved", dst)
