# -*- coding: utf-8 -*-
"""Audit: rebuild paragraph text with math spans marked, flag leftover ASCII math."""
import sys, re
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

def node_text(el):
    out = []
    for n in el.iter():
        if n.tag == M + "t" or n.tag == W + "t":
            out.append(n.text or "")
    return "".join(out)

def para_text(p):
    parts = []
    for child in p._p.iterchildren():
        tag = child.tag
        if tag == W + "r":
            parts.append(node_text(child))
        elif tag == M + "oMath":
            parts.append("《" + node_text(child) + "》")
        elif tag == W + "hyperlink":
            parts.append(node_text(child))
    return "".join(parts)

SUSPECT = re.compile(r"[A-Za-zΔφγκεηρμσ]_\w|\^|√|（ ?[^ ]+ ?/ ?[^ ]+ ?）| / |·")

path = sys.argv[1]
doc = Document(path)
rows = []
def scan(p, where):
    t = para_text(p)
    if SUSPECT.search(t.replace("《", "").replace("》", "")):
        # skip if suspect chars only inside math
        outside = re.sub(r"《[^》]*》", "", t)
        if SUSPECT.search(outside):
            rows.append((where, t))

for i, p in enumerate(doc.paragraphs):
    scan(p, "P%04d" % i)
for ti, t in enumerate(doc.tables):
    for ri, row in enumerate(t.rows):
        for ci, cell in enumerate(row.cells):
            for p in cell.paragraphs:
                scan(p, "T%02d[%d,%d]" % (ti, ri, ci))

print("flagged", len(rows))
with open(sys.argv[2], "w", encoding="utf-8") as f:
    for w, t in rows:
        f.write(w + " | " + t + "\n")
