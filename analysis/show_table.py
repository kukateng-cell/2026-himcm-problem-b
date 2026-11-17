# -*- coding: utf-8 -*-
import sys
from docx import Document
from docx.oxml.ns import qn

d = Document(sys.argv[1])
for ti in [int(x) for x in sys.argv[2].split(",")]:
    tb = d.tables[ti]
    print("TABLE", ti, "autofit", tb.autofit)
    for ri, row in enumerate(tb.rows[:8]):
        tr = row._tr
        h = tr.find(qn("w:trPr") + "/" + qn("w:trHeight"))
        trh = tr.find(".//" + qn("w:trHeight"))
        print(" row", ri, "trHeight", None if trh is None else (trh.get(qn("w:val")), trh.get(qn("w:hRule"))))
    cell = tb.rows[2].cells[0]
    for p in cell.paragraphs:
        print("  cell pPr:", p._p.pPr.xml[:300] if p._p.pPr is not None else None)
        for r in p._p.findall(qn("w:r")):
            print("  run rPr:", r.find(qn("w:rPr")) is not None)
