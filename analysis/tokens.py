# -*- coding: utf-8 -*-
"""List underscore / caret tokens outside math, with counts and locations."""
import sys, re, collections
from docx import Document

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"

def nonmath_text(p):
    out = []
    for child in p._p.iterchildren():
        if child.tag == W + "r":
            for t in child.iter(W + "t"):
                out.append(t.text or "")
        elif child.tag == W + "hyperlink":
            for t in child.iter(W + "t"):
                out.append(t.text or "")
        # oMath ignored
    return "".join(out)

TOK = re.compile(r"[A-Za-z\u0391-\u03c9\u0394\u03c6\u03b3\u03ba\u03b5\u03b7\u03c1\u03bc\u03c3\u1e41]{1,12}(?:_[A-Za-z0-9,]+)+|\^\{?[^ \u00a0]{1,10}\}?")
path = sys.argv[1]
doc = Document(path)
cnt = collections.Counter()
locs = collections.defaultdict(list)
items = []
for i, p in enumerate(doc.paragraphs):
    t = nonmath_text(p)
    for m in TOK.finditer(t):
        cnt[m.group(0)] += 1
        locs[m.group(0)].append("P%04d" % i)
for ti, tb in enumerate(doc.tables):
    for ri, row in enumerate(tb.rows):
        for ci, cell in enumerate(row.cells):
            for p in cell.paragraphs:
                t = nonmath_text(p)
                for m in TOK.finditer(t):
                    cnt[m.group(0)] += 1
                    locs[m.group(0)].append("T%02d[%d,%d]" % (ti, ri, ci))
with open(sys.argv[2], "w", encoding="utf-8") as f:
    for k, v in cnt.most_common():
        f.write("%3d  %-22s %s\n" % (v, k, ",".join(locs[k][:6])))
print("tokens", len(cnt))
