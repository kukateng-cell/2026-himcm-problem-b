# -*- coding: utf-8 -*-
"""Convert every display formula line to segmented native OMML (equations with subscripts)."""
import re, sys
from docx import Document
from docx.oxml import parse_xml, OxmlElement

TOKEN = re.compile(r"([^\s_()]+)_([A-Za-z0-9]+(?:,[A-Za-z0-9]+)*)")

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def mrun(text):
    return '<m:r><m:t xml:space="preserve">%s</m:t></m:r>' % esc(text)

def ssub(base, sub):
    return '<m:sSub><m:e>%s</m:e><m:sub>%s</m:sub></m:sSub>' % (mrun(base), mrun(sub))

def omath(text):
    parts, pos = [], 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            parts.append(mrun(text[pos:m.start()]))
        parts.append(ssub(m.group(1), m.group(2)))
        pos = m.end()
    if pos < len(text):
        parts.append(mrun(text[pos:]))
    return ('<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">%s</m:oMath>'
            % "".join(parts))

def wrun(text):
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    r.append(t)
    return r

def rebuild(p, parts):
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    for child in list(p._p):
        if child.tag.split('}')[-1] in ("r", "oMath", "hyperlink"):
            p._p.remove(child)
    for kind, text in parts:
        if kind == "m":
            p._p.append(parse_xml(omath(text)))
        else:
            p._p.append(wrun(text))

EQ = {
 "ΔT_phys = min": [("m", "ΔT_phys = min(ΔT_nom, ε(T_db − T_wb))."), ("t", "   (Eq. 1)")],
 "ΔT_eff = AT(T_db": [("m", "ΔT_eff = AT(T_db, e_amb, v_amb) − AT(T_zone, e_zone, v_eff),"), ("t", "   "),
                      ("m", "AT(T,e,v) = T + 0.33e − 0.70v − 4.00."), ("t", "   (Eq. 2) [2]")],
 "η = (φ · N_eff": [("m", "η = (φ · N_eff · ΔT_eff) / (n · P_elec),"), ("t", "   "),
                    ("m", "φ = min(1, n·A_cov/A_waiting)."), ("t", "   (Eq. 3)")],
 "LCC_annual = (1/L_life": [("m", "LCC_annual = (1/L_life + r_om)·n·C_cap +"), ("t", " "),
                            ("m", "H_yr·(n·P_elec·p_elec + (n·V_w/1000)·p_water)."), ("t", "   (Eq. 4)")],
 "V_w = 3600": [("m", "V_w = 3600 · ṁ_da · c_p · ΔT_phys / L_v,"), ("t", "   "),
                ("m", "ṁ_da = Q_air·ρ_da,"), ("t", "   (Eq. 7)")],
 "I_env = α_c": [("m", "I_env = α_c(E_CO2/E_CO2,max) + α_w(W_eq/W_eq,max),"), ("t", "   with "),
                 ("m", "α_c = α_w = 0.50;"), ("t", " "),
                 ("m", "E_CO2 = n·P_elec·H_yr·EF_grid;"), ("t", " "),
                 ("m", "W_eq = (n·V_w/1000)·H_yr·BWS_raw."), ("t", "   (Eq. 5)")],
 "E = w1·S_safe": [("m", "E = w1·S_safe + w2·B − w3·LCC̃ − w4·I_env."), ("t", "   (Eq. 6)")],
 "WBGT_proxy = 0.7": [("m", "WBGT_proxy = 0.7 T_wb,zone + 0.3 T_zone;"), ("t", " "),
                      ("m", "S_safe(W) = clamp((35 − W)/6, 0, 1);"), ("t", " "),
                      ("m", "B = φ·N_eff·ΔT_eff / B_max;"), ("t", " "),
                      ("m", "LCC̃ = LCC/LCC_max;"), ("t", " baseline weights "),
                      ("m", "(w1,w2,w3,w4) = (0.30, 0.30, 0.20, 0.20).")],
}

def convert_mixed(p, text):
    cut = text.find(" Rectangular jets")
    if cut < 0:
        return False
    head = text[:cut]
    rest = text[cut:]
    parts = []
    segs = head.split("; ")
    for i, seg in enumerate(segs):
        last = (i == len(segs) - 1)
        if last and ", with " in seg:
            a, b = seg.split(", with ", 1)
            parts.append(("m", a.strip() + ","))
            parts.append(("t", " with "))
            parts.append(("m", b.strip()))
        elif seg.strip():
            parts.append(("m", seg.strip() + ("" if last else ";")))
        if not last:
            parts.append(("t", " "))
    parts.append(("t", rest))
    rebuild(p, parts)
    return True


path = sys.argv[1]
doc = Document(path)
n = 0
for p in list(doc.paragraphs):
    t = p.text
    for prefix, parts in EQ.items():
        if t.startswith(prefix):
            rebuild(p, parts)
            n += 1
            break
    else:
        if t.startswith("T_zone = T_db") and convert_mixed(p, t):
            n += 1
doc.save(path)
print("converted", n)
