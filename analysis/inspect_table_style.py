from docx import Document
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
doc = Document(r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx")
t = doc.tables[0]
print("=== Table 0 tblPr ===")
print(etree.tostring(t._tbl.tblPr, pretty_print=True).decode()[:3000])
print("=== first row trPr ===")
print(etree.tostring(t.rows[0]._tr.trPr, pretty_print=True).decode()[:1500])
print("=== header cell xml (first 2000) ===")
print(etree.tostring(t.rows[0].cells[0]._tc, pretty_print=True).decode()[:2500])
print("=== data cell xml (first 2500) ===")
print(etree.tostring(t.rows[1].cells[0]._tc, pretty_print=True).decode()[:2500])
print("=== widths ===", [c.width for c in t.rows[0].cells])
# caption paragraph
for p in doc.paragraphs:
    if p.text.strip().startswith("Table 1. Summary"):
        print("=== caption pPr ===")
        print(etree.tostring(p._p.pPr, pretty_print=True).decode())
        print("=== caption runs ===")
        for r in p.runs:
            print(repr(r.text), etree.tostring(r._r.rPr, pretty_print=True).decode() if r._r.rPr is not None else None)
        break
