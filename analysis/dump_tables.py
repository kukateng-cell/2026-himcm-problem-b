# -*- coding: utf-8 -*-
"""Dump table cells with math markers for inspection."""
import sys
from docx import Document

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

def mtxt(el):
    return "".join((n.text or "") for n in el.iter() if n.tag == M + "t")

def walk(p):
    out = []
    for ch in p._p.iterchildren():
        if ch.tag == W + "r":
            t = "".join((n.text or "") for n in ch.iter(W + "t"))
            if t:
                out.append(t)
        elif ch.tag == M + "oMath":
            out.append("⟦" + mtxt(ch) + "⟧")
    return "".join(out)

doc = Document(sys.argv[1])
with open(sys.argv[2], "w", encoding="utf-8") as f:
    for ti, tb in enumerate(doc.tables):
        f.write("\n=== TABLE %d (%d rows x %d cols) ===\n" % (ti, len(tb.rows), len(tb.columns)))
        for ri, row in enumerate(tb.rows):
            vals = []
            for ci, cell in enumerate(row.cells):
                vals.append(walk(cell.paragraphs[0]) if cell.paragraphs else "")
            f.write("  [%d] %s\n" % (ri, " | ".join(vals)))
