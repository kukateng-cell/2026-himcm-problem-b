# -*- coding: utf-8 -*-
import re
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

SRC = r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
doc = Document(SRC)

def omml_text(el):
    return ''.join(t.text or '' for t in el.iter('{%s}t' % M))

def iter_block_items(parent):
    for child in parent.element.body.iterchildren():
        if child.tag == qn('w:p'):
            yield Paragraph(child, parent)
        elif child.tag == qn('w:tbl'):
            yield Table(child, parent)

out = []
for i, block in enumerate(iter_block_items(doc), start=1):
    if isinstance(block, Paragraph):
        maths = block._p.findall('.//{%s}oMath' % M)
        mt = ' ⟦' + ' | '.join(omml_text(m) for m in maths) + '⟧' if maths else ''
        t = block.text
        if t.strip() or mt:
            out.append(f"P{i:04d} [{block.style.name}]{mt} {t}")
    else:
        out.append(f"P{i:04d} [TABLE rows={len(block.rows)}]")
        for row in block.rows:
            out.append("   | " + " | ".join(c.text.replace('\n',' / ') for c in row.cells))

with open(r"C:\Users\kukat\Desktop\USA\_extract\current_final.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("blocks", len(out), "tables", len(doc.tables))
