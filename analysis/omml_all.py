# -*- coding: utf-8 -*-
"""Convert all display formula lines to native OMML equations (with subscripts)."""
import re, sys
from docx import Document
from docx.oxml import parse_xml, OxmlElement

TOKEN = re.compile(r"([^\s_()]+)_([A-Za-z0-9]+(?:,[A-Za-z0-9]+)*)")

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def run(text):
    return '<m:r><m:t xml:space="preserve">%s</m:t></m:r>' % esc(text)

def ssub(base, sub):
    return '<m:sSub><m:e>%s</m:e><m:sub>%s</m:sub></m:sSub>' % (run(base), run(sub))

def omath(text):
    parts, pos = [], 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            parts.append(run(text[pos:m.start()]))
        parts.append(ssub(m.group(1), m.group(2)))
        pos = m.end()
    if pos < len(text):
        parts.append(run(text[pos:]))
    return '<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">%s</m:oMath>' % "".join(parts)

def clear_runs(p):
    for child in list(p):
        tag = child.tag.split('}')[-1]
        if tag in ("r", "oMath", "hyperlink", "bookmarkStart", "bookmarkEnd"):
            if tag == "bookmarkStart" or tag == "bookmarkEnd":
                continue
            p.remove(child)

def add_text(p, text):
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    r.append(t)
    p.append(r)

def convert_para(p, eq_text, tail=""):
    clear_runs(p._p)
    p._p.append(parse_xml(omath(eq_text)))
    if tail:
        add_text(p._p, tail)

LABELS = [
    ("ΔT_phys = min(ΔT_nom", "(Eq. 1)", None),
    ("ΔT_eff = AT(T_db", "(Eq. 2) [2]", None),
    ("η = (φ · N_eff", "(Eq. 3)", None),
    ("LCC_annual = (1/L_life", "(Eq. 4)", None),
    ("V_w = 3600", "(Eq. 7)", None),
    ("I_env = α_c", "(Eq. 5)", None),
    ("E = w1·S_safe", "(Eq. 6)", None),
    ("WBGT_proxy = 0.7", None, None),
]

path = sys.argv[1]
doc = Document(path)
count = 0
for p in list(doc.paragraphs):
    txt = p.text
    for prefix, label, _ in LABELS:
        if txt.startswith(prefix):
            eq = txt
            tail = ""
            if label:
                idx = txt.find("   " + label)
                if idx > 0:
                    eq = txt[:idx]
                    tail = "   " + label
            convert_para(p, eq.strip(), tail)
            count += 1
            break
    # mixed paragraph: Eq. 2 definitions
    if txt.startswith("T_zone = T_db"):
        cut = txt.find(" Rectangular jets")
        if cut > 0:
            eq = txt[:cut].strip()
            rest = txt[cut:]
            convert_para(p, eq, rest)
            count += 1

doc.save(path)
print("converted", count)
