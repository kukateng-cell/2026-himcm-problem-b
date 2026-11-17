# -*- coding: utf-8 -*-
"""List paragraphs containing oMath, with math text and surrounding text."""
import sys
from docx import Document

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

def mtxt(el):
    return "".join((n.text or "") for n in el.iter() if n.tag == M + "t")

def walk(p):
    out = []
    for ch in p._p.iterchildren():
        if ch.tag == W + "r":
            t = "".join((n.text or "") for n in ch.iter(W + "t"))
            if t:
                out.append(("t", t))
        elif ch.tag == M + "oMath":
            out.append(("m", mtxt(ch)))
        elif ch.tag == W + "hyperlink":
            t = "".join((n.text or "") for n in ch.iter(W + "t"))
            if t:
                out.append(("t", t))
    return out

doc = Document(sys.argv[1])
with open(sys.argv[2], "w", encoding="utf-8") as f:
    for i, p in enumerate(doc.paragraphs):
        seg = walk(p)
        if any(k == "m" for k, _ in seg):
            f.write("P%04d | " % i + "".join(("⟦%s⟧" % x) if k == "m" else x for k, x in seg) + "\n")
