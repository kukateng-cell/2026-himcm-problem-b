from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

path = r"C:\Users\kukat\Desktop\USA\2026_HiMCM_ProblemB_全篇符號說明表與核心邏輯鏈.docx"
doc = Document(path)

def iter_block_items(parent):
    for child in parent.element.body.iterchildren():
        if child.tag == qn('w:p'):
            yield Paragraph(child, parent)
        elif child.tag == qn('w:tbl'):
            yield Table(child, parent)

out = []
for block in iter_block_items(doc):
    if isinstance(block, Paragraph):
        if block.text.strip():
            out.append(f"[{block.style.name}] {block.text}")
    else:
        out.append(f"[TABLE rows={len(block.rows)}]")
        for row in block.rows:
            out.append("   | " + " | ".join(c.text.replace('\n',' / ') for c in row.cells))

with open(r"C:\Users\kukat\Desktop\USA\_extract\symbol_doc.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))
print(len(out))
