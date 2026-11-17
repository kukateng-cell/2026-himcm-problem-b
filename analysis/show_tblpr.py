# -*- coding: utf-8 -*-
import re, sys
from docx import Document
from docx.oxml.ns import qn
d = Document(sys.argv[1])
tb = d.tables[int(sys.argv[2])]
tblPr = tb._tbl.tblPr
print(re.sub(r' xmlns:[a-z0-9]+="[^"]+"', "", tblPr.xml)[:1500])
print("---- row 2 pPr spacing:")
p = tb.rows[2].cells[0].paragraphs[0]
print(re.sub(r' xmlns:[a-z0-9]+="[^"]+"', "", p._p.pPr.xml)[:400])
print("---- first row height:", tb.rows[0].height)
