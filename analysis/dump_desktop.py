import sys
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

src = r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"
doc = Document(src)

def iter_block_items(parent):
    for child in parent.element.body.iterchildren():
        if child.tag == qn('w:p'):
            yield Paragraph(child, parent)
        elif child.tag == qn('w:tbl'):
            yield Table(child, parent)

out = []
for i, block in enumerate(iter_block_items(doc), start=1):
    if isinstance(block, Paragraph):
        t = block.text
        if t.strip():
            out.append(f"P{i:04d} [{block.style.name}] {t}")
    else:
        out.append(f"P{i:04d} [TABLE rows={len(block.rows)} cols={len(block.columns)}]")
        for row in block.rows:
            out.append("   | " + " | ".join(c.text.replace('\n',' / ') for c in row.cells))

with open(r"C:\Users\kukat\Desktop\USA\_extract\desktop_v12.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))
print("blocks", len(out))
print("paragraphs", len(doc.paragraphs), "tables", len(doc.tables))
s = doc.sections[0]
print("page", s.page_width.cm, s.page_height.cm, "margins", s.left_margin.cm, s.right_margin.cm, s.top_margin.cm, s.bottom_margin.cm)
print("usable width", (s.page_width - s.left_margin - s.right_margin).cm)
