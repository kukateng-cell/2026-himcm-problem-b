# -*- coding: utf-8 -*-
from docx import Document
from lxml import etree
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
PATH = r"C:\Users\kukat\Desktop\USA\_extract\v1.2_nomenclature.docx"
doc = Document(PATH)
body = doc.element.body
kids = list(body.iterchildren())
print("body children:", len(kids), "tables:", len(doc.tables), "paragraphs:", len(doc.paragraphs))

# locate caption and table order
for i, ch in enumerate(kids):
    tag = etree.QName(ch).localname
    if tag == 'p':
        txt = ''.join(t.text or '' for t in ch.iter('{%s}t' % W))[:60]
        if 'Table 1b' in txt or txt.startswith('3. Mathematical Model'):
            print(i, "P:", txt)
    elif tag == 'tbl':
        first = ''.join(t.text or '' for t in ch.iter('{%s}t' % W))[:30]
        if 'Symbol' in first:
            print(i, "TBL:", first)

t = doc.tables[1]
print("nomenclature rows:", len(t.rows), "cols:", len(t.columns))
print("header:", [c.text for c in t.rows[0].cells])
print("row1:", [c.text for c in t.rows[1].cells])
print("row10:", [c.text for c in t.rows[10].cells])
print("last:", [c.text for c in t.rows[-1].cells])

# cross-reference sentence
for p in doc.paragraphs:
    if 'Table 1b' in p.text and 'roadmap' in p.text:
        print("XREF:", p.text[-120:])

# TOC numbers
sdt = body.find('{%s}sdt' % W)
content = sdt.find('.//{%s}sdtContent' % W)
nums = []
for p in content.findall('{%s}p' % W):
    txt = ''.join(x.text or '' for x in p.iter('{%s}t' % W))
    if txt.strip():
        nums.append(txt[-4:])
print("TOC tail:", nums[:6], "...", nums[-4:])
