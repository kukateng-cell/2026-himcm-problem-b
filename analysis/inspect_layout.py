from docx import Document
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
doc = Document(r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx")
for i, s in enumerate(doc.sections):
    print(i, "page", round(s.page_width.cm,2), round(s.page_height.cm,2),
          "margins L/R", round(s.left_margin.cm,2), round(s.right_margin.cm,2),
          "T/B", round(s.top_margin.cm,2), round(s.bottom_margin.cm,2),
          "orient", s.orientation)
t = doc.tables[0]
grid = t._tbl.find('{%s}tblGrid' % W)
print("gridCols (twips):", [g.get('{%s}w' % W) for g in grid])
print("tblW:", etree.tostring(t._tbl.tblPr.find('{%s}tblW' % W)).decode())
print("sum twips:", sum(int(g.get('{%s}w' % W)) for g in grid), "=", sum(int(g.get('{%s}w' % W)) for g in grid)/566.93, "cm")
for p in doc.paragraphs:
    if p.text.strip().startswith("Table 1. Summary"):
        print("caption text:", repr(p.text))
        print("style:", p.style.name, "align:", p.alignment)
        for r in p.runs:
            print("  run", repr(r.text[:40]), "bold", r.bold, "italic", r.italic, "size", r.font.size, "name", r.font.name)
        break
# body width from sectPr
body = doc.element.body
sect = body.find('{%s}sectPr' % W)
print(etree.tostring(sect, pretty_print=True).decode()[:1200])
