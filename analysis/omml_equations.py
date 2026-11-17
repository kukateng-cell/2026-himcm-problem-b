# -*- coding: utf-8 -*-
"""Build native OMML equations (subscripts) for the paper's formula lines."""
import re, sys
from docx import Document
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
TOKEN = re.compile(r"([^\s_()]+)_([A-Za-z0-9]+(?:,[A-Za-z0-9]+)*)")

def esc(t):
    return (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def run(text):
    return '<m:r><m:t xml:space="preserve">%s</m:t></m:r>' % esc(text)

def ssub(base, sub):
    return '<m:sSub><m:e>%s</m:e><m:sub>%s</m:sub></m:sSub>' % (run(base), run(sub))

def omath(text):
    parts = []
    pos = 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            parts.append(run(text[pos:m.start()]))
        parts.append(ssub(m.group(1), m.group(2)))
        pos = m.end()
    if pos < len(text):
        parts.append(run(text[pos:]))
    return ('<m:oMath %s>%s</m:oMath>' % (nsdecls("m"), "".join(parts)))

def replace_formula(paragraph, eq_text, label):
    p = paragraph._p
    for child in list(p):
        if child.tag.endswith('}r') or child.tag.endswith('}oMath') or child.tag.endswith('}hyperlink'):
            p.remove(child)
    p.append(parse_xml(omath(eq_text)))
    from docx.oxml import OxmlElement
    r = OxmlElement('w:r')
    t = OxmlElement('w:t')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = "   " + label
    r.append(t)
    p.append(r)

if __name__ == "__main__":
    path = sys.argv[1]
    doc = Document(path)
    done = 0
    for p in doc.paragraphs:
        if p.text.startswith("ΔT_phys = min(ΔT_nom"):
            eq = p.text.split("   (Eq. 1)")[0]
            replace_formula(p, eq, "(Eq. 1)")
            done += 1
            break
    doc.save(path)
    print("converted", done)
