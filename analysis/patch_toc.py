# -*- coding: utf-8 -*-
"""Shift cached TOC page numbers by +1 for entries after the inserted nomenclature page."""
from docx import Document
from docx.oxml.ns import qn

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
PATH = r"C:\Users\kukat\Desktop\USA\_extract\v1.2_nomenclature.docx"
doc = Document(PATH)
body = doc.element.body
sdt = body.find('{%s}sdt' % W)
content = sdt.find('.//{%s}sdtContent' % W)

changed = []
for p in content.findall('{%s}p' % W):
    runs = p.findall('{%s}r' % W)
    texts = [''.join(t.text or '' for t in r.findall('{%s}t' % W)) for r in runs]
    idx = None
    for i, t in enumerate(texts):
        if t.strip().isdigit():
            idx = i
    if idx is None:
        continue
    title = ''.join(texts[:idx]).strip()
    first = title[:1]
    shift = first in '3456' or title.startswith('AI') or title.startswith('Appendix')
    if not shift:
        continue
    old = int(texts[idx].strip())
    new = old + 1
    t_el = runs[idx].find('{%s}t' % W)
    t_el.text = str(new)
    changed.append((title[:55], old, new))

for c in changed:
    print(f"{c[0]:<57} {c[1]} -> {c[2]}")
doc.save(PATH)
print("updated", len(changed), "TOC entries")
