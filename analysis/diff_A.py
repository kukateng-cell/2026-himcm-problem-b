# -*- coding: utf-8 -*-
import difflib
from docx import Document

A = r"C:\Users\kukat\Desktop\USA\_extract\v1.2_final.docx"
B = r"C:\Users\kukat\Desktop\USA\_extract\v1.2_A.docx"
a = [p.text for p in Document(A).paragraphs]
b = [p.text for p in Document(B).paragraphs]
print("paragraphs:", len(a), "->", len(b))
for line in difflib.unified_diff(a, b, lineterm="", n=0):
    if line.startswith(("+++", "---")):
        continue
    print(line[:220])
