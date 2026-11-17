# -*- coding: utf-8 -*-
"""Inspect run structure of selected paragraphs/cells."""
import sys
from docx import Document
from docx.oxml.ns import qn

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

path = sys.argv[1]
doc = Document(path)
paras = doc.paragraphs

def show(p, name):
    print("###", name, "align=", p.alignment, "style=", p.style.name)
    for ch in p._p.iterchildren():
        tag = ch.tag.split("}")[-1]
        if tag == "r":
            txt = "".join(t.text or "" for t in ch.iter(W + "t"))
            rpr = ch.find(W + "rPr")
            desc = []
            if rpr is not None:
                for e in rpr.iter():
                    t2 = e.tag.split("}")[-1]
                    if t2 in ("b", "i", "color", "rFonts", "sz", "u", "vertAlign", "highlight"):
                        desc.append(t2 + "=" + str(e.get(qn("w:val")) or e.attrib))
            print("  r:", repr(txt[:60]), "|", ";".join(desc))
        else:
            print("  <" + tag + ">")
    pPr = p._p.find(W + "pPr")
    if pPr is not None:
        print("  pPr:", pPr.xml.replace("\n", " ")[:500])

for spec in sys.argv[2:]:
    kind, ref = spec.split(":", 1)
    if kind == "p":
        i = int(ref)
        show(paras[i], spec)
    else:
        ti, rc = ref.split("[")
        ri, ci = rc.rstrip("]").split(",")
        cell = doc.tables[int(ti)].rows[int(ri)].cells[int(ci)]
        for p in cell.paragraphs:
            show(p, spec)
