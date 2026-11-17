from docx import Document
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
doc = Document(r"C:\Users\kukat\Desktop\USA\_extract\v1.2_nomenclature.docx")
t = doc.tables[1]
print("tables:", len(doc.tables), "rows:", len(t.rows))
for i in [1,5,6,7,8,9,10]:
    tr = t.rows[i]._tr
    paras = sum(len(tc.findall('.//{%s}p' % W)) for tc in tr.findall('{%s}tc' % W))
    print(i, "cells", len(tr.findall('{%s}tc' % W)), "paras", paras, "|", t.rows[i].cells[1].text[:40])
# dump pPr of a tight vs tall row
for i in (1, 9):
    tc = t.rows[i]._tr.findall('{%s}tc' % W)[1]
    print("ROW", i, etree.tostring(tc.find('.//{%s}p' % W).find('{%s}pPr' % W), pretty_print=True).decode())
