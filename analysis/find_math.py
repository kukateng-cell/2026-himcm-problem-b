from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
tree = etree.parse(r"C:\Users\kukat\Desktop\USA\_extract\desktop_xml\pkg\word\document.xml")
root = tree.getroot()

def omml_text(el):
    return ''.join(t.text or '' for t in el.iter('{%s}t' % M))

rows=[]
for i, p in enumerate(root.iter('{%s}p' % W), start=1):
    maths = p.findall('.//{%s}oMath' % M)
    if not maths:
        continue
    # parent chain
    chain=[]
    a=p.getparent()
    while a is not None:
        chain.append(etree.QName(a).localname)
        a=a.getparent()
    wtxt=''.join(t.text or '' for t in p.iter('{%s}t' % W))
    rows.append((i, '>'.join(chain[:4]), ' | '.join(omml_text(m) for m in maths), wtxt[:60]))

with open(r"C:\Users\kukat\Desktop\USA\_extract\math_paragraphs.txt","w",encoding="utf-8") as f:
    for r in rows:
        f.write(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\n")
print(len(rows))
for r in rows[:20]:
    print(r[0], r[1], repr(r[2][:80]), repr(r[3][:40]))
