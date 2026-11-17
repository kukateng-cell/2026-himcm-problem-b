import sys
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.ns import qn

path = r"C:\Users\kukat\Desktop\USA\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"
doc = Document(path)

def iter_block_items(parent):
    parent_elm = parent.element.body
    for child in parent_elm.iterchildren():
        if child.tag == qn('w:p'):
            yield Paragraph(child, parent)
        elif child.tag == qn('w:tbl'):
            yield Table(child, parent)

out = []
i = 0
for block in iter_block_items(doc):
    if isinstance(block, Paragraph):
        i += 1
        style = block.style.name if block.style is not None else ''
        txt = block.text.replace('\t', ' ')
        has_omml = bool(block._p.findall('.//' + qn('m:oMath')))
        has_omml_para = bool(block._p.findall('.//' + qn('m:oMathPara')))
        marker = ''
        if has_omml or has_omml_para:
            marker = ' [MATH]'
        if txt.strip() or marker:
            out.append(f"P{i:04d} [{style}]{marker} {txt}")
    else:
        i += 1
        out.append(f"P{i:04d} [TABLE] rows={len(block.rows)}")
        for r_i, row in enumerate(block.rows):
            cells = []
            for cell in row.cells:
                cells.append(cell.text.replace('\n', ' / '))
            out.append("   | " + " | ".join(cells))

with open(r"C:\Users\kukat\Desktop\USA\_extract\v12_text.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print(len(out))
