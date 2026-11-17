# -*- coding: utf-8 -*-
"""Inspect SDT/TOC structure."""
import sys
from docx import Document
from docx.oxml.ns import qn

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
doc = Document(sys.argv[1])
body = doc.element.body
for i, ch in enumerate(body.iterchildren()):
    tag = ch.tag.split("}")[-1]
    if tag == "sdt":
        txt = "".join(t.text or "" for t in ch.iter(W + "t"))
        print("SDT at", i, "text:", repr(txt[:300]))
        instr = "".join(t.text or "" for t in ch.iter(W + "instrText"))
        print("  instr:", repr(instr[:120]))
        for p in ch.iter(W + "p"):
            ptxt = "".join(t.text or "" for t in p.iter(W + "t"))
            print("   p:", repr(ptxt[:100]))
    elif tag == "p":
        pass
    else:
        print("child", i, tag)
