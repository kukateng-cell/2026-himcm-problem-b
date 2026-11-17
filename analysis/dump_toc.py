# -*- coding: utf-8 -*-
"""List TOC paragraphs, their entry text and trailing page-number run."""
import sys
from docx import Document
from docx.oxml.ns import qn

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

doc = Document(sys.argv[1])
for i, p in enumerate(doc.paragraphs):
    if p.style.name.lower().startswith("toc"):
        txt = p.text
        runs = [t.text for r in p._p.findall(qn("w:r")) for t in r.findall(qn("w:t"))]
        print("P%03d [%s] %r | runs=%r" % (i, p.style.name, txt, runs[-4:]))
