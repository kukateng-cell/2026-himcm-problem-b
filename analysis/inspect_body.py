from docx import Document
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
doc = Document(r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx")
body = doc.element.body
kinds = {}
for i, ch in enumerate(body.iterchildren()):
    tag = etree.QName(ch).localname
    kinds[tag] = kinds.get(tag,0)+1
print(kinds)
# find sdt elements
sdts = body.findall('{%s}sdt' % W)
print("sdt count:", len(sdts))
for s in sdts[:2]:
    txt = ''.join(t.text or '' for t in s.iter('{%s}t' % W))
    print("SDT text start:", repr(txt[:200]))
    print(etree.tostring(s, pretty_print=True).decode()[:1500])
