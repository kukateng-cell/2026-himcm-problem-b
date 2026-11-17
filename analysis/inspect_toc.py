from docx import Document
from lxml import etree
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
doc = Document(r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx")

# TOC paragraphs
started=False; count=0
for p in doc.paragraphs:
    if p.text.strip()=="Table of Contents":
        started=True; continue
    if started:
        if p.text.strip().startswith("1. Understanding"):
            break
        count+=1
        if count<=3 or "3.2 Thermodynamic" in p.text:
            print("STYLE:", p.style.name, "| TEXT:", repr(p.text))
            for i,r in enumerate(p.runs):
                print("   run",i, repr(r.text), "| bold",r.bold, "italic",r.italic, "sz", r.font.size)
            print("   xml:", etree.tostring(p._p, pretty_print=True).decode()[:1200])
print("toc paras:", count)

# heading page break before?
for p in doc.paragraphs:
    if p.text.strip()=="3. Mathematical Model":
        print("heading style:", p.style.name, "pbb:", p.paragraph_format.page_break_before)
        print(etree.tostring(p._p.pPr, pretty_print=True).decode() if p._p.pPr is not None else "no pPr")
        st = p.style
        print("style pbb:", st.paragraph_format.page_break_before, "next:", st.paragraph_format.keep_with_next)
        break
# check Heading 1 style definition
for s in doc.styles:
    if s.name=="Heading 1":
        print("Heading1 style pbb:", s.paragraph_format.page_break_before)
        break
