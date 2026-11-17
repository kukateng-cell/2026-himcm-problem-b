# -*- coding: utf-8 -*-
"""Dump paragraph texts + math presence for inspection."""
import sys, re
from docx import Document

path = sys.argv[1]
out = sys.argv[2]
doc = Document(path)
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

def ptext(p):
    t = p.text
    return t.replace("\t", "\\t").replace("\n", "\\n")

def info(p):
    om = p._p.findall(M + "oMath")
    om += p._p.findall(M + "oMathPara/" + M + "oMath")
    return len(om)

lines = []
body = doc.element.body
idx = 0
for child in body.iterchildren():
    tag = child.tag.split("}")[-1]
    if tag == "p":
        from docx.text.paragraph import Paragraph
        p = Paragraph(child, doc)
        lines.append("[%04d] <%s> om=%d | %s" % (idx, p.style.name, info(p), ptext(p)))
        idx += 1
    elif tag == "tbl":
        from docx.table import Table
        t = Table(child, doc)
        lines.append("=== TABLE %d (%d rows) ===" % (idx, len(t.rows)))
        for ri, row in enumerate(t.rows):
            for ci, cell in enumerate(row.cells):
                for p in cell.paragraphs:
                    if p.text.strip():
                        lines.append("  T%d[%d,%d] om=%d | %s" % (idx, ri, ci, info(p), ptext(p)))
        idx += 1

open(out, "w", encoding="utf-8").write("\n".join(lines))
print("paras", idx, "lines", len(lines))
