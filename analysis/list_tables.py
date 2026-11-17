# -*- coding: utf-8 -*-
from docx import Document
P = r"C:\Users\kukat\Desktop\USA\_extract\v1.2_C.docx"
import os
if not os.path.exists(P):
    P = r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"
d = Document(P)
for i, t in enumerate(d.tables):
    hdr = [c.text.strip() for c in t.rows[0].cells]
    first = t.rows[1].cells[0].text.strip() if len(t.rows) > 1 else ""
    print(i, "rows", len(t.rows), "cols", len(t.columns), "|", " / ".join(hdr)[:110], "| first:", first[:30])
