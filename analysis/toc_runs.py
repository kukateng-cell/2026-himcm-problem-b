# -*- coding: utf-8 -*-
import sys
from docx import Document
from docx.oxml.ns import qn
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
d = Document(sys.argv[1])
body = d.element.body
for ch in body.iterchildren():
    if ch.tag == qn("w:sdt"):
        ps = list(ch.iter(qn("w:p")))
        for p in ps[2:5]:
            print("----")
            for r in p.iter(qn("w:r")):
                ts = [t.text for t in r.findall(qn("w:t"))]
                fld = r.find(qn("w:fldChar"))
                print(" run:", ts, "fld" if fld is not None else "")
        break
