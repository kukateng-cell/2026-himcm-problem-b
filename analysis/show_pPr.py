# -*- coding: utf-8 -*-
import re, sys
from docx import Document
d = Document(sys.argv[1])
for i in [int(x) for x in sys.argv[2].split(",")]:
    p = d.paragraphs[i]
    print("### p", i)
    print(re.sub(r' xmlns:[a-z0-9]+="[^"]+"', "", p._p.pPr.xml))
