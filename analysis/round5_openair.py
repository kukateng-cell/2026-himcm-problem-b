# -*- coding: utf-8 -*-
"""Round 5b: replace the obsolete stress block with the open-air scenario (body)."""
import copy
from docx import Document
from docx.shared import Pt, Twips
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

PATH = r"C:\Users\kukat\Desktop\USA\_extract\v1.3_work.docx"
doc = Document(PATH)

# ---- remove old stress paragraph
stress = None
for p in doc.paragraphs:
    if p.text.startswith("Structural stress tests (Table B2)"):
        stress = p
        break
assert stress is not None
stress._p.getparent().remove(stress._p)

# ---- remove Table B2 (caption + table)
cap = None
for p in doc.paragraphs:
    if p.text.startswith("Table B2. Structural stress tests"):
        cap = p
        break
assert cap is not None
tbl_b2 = None
for t in doc.tables:
    if t.rows[0].cells[0].text.strip() == "Case" and "Exercise" not in t.rows[0].cells[0].text:
        if "E (base)" in [c.text.strip() for c in t.rows[0].cells]:
            tbl_b2 = t
            break
assert tbl_b2 is not None
b2_pr = copy.deepcopy(tbl_b2._tbl.tblPr)
cap._p.getparent().remove(cap._p)
tbl_b2._tbl.getparent().remove(tbl_b2._tbl)

# ---- locate Reading paragraph
reading = None
for p in doc.paragraphs:
    if p.text.startswith("Reading: the Phoenix bus-shelter choice"):
        reading = p
        break
assert reading is not None

def new_para_after(ref, text, bold_lead=None):
    p = copy.deepcopy(reading._p)
    runs = p.findall(qn("w:r"))
    for r in runs[1:]:
        p.remove(r)
    t = runs[0].find(qn("w:t"))
    t.text = text
    ref.addnext(p)
    return p

para = new_para_after(reading._p,
    "Open-air venues. The same equations carry to an unroofed concourse by raising the boundary loss to γ = 0.75 and applying the "
    "black-globe offset as WBGT +1.8 K (+6 K globe); the waiting zone is 300 m². In Phoenix the concourse is led by 1× MC61V "
    "(E = 0.3088 against 0.2824 for doing nothing), because full coverage of a large zone is what earns the benefit, with the drum fan "
    "at 0.2957; in Hong Kong only the drum fan clears the baseline, and only marginally (0.2070 against 0.1965), because the wet-bulb "
    "depression is too small for evaporative cooling to repay its cost. Open-air cooling is therefore a coverage-and-climate problem, "
    "not a device problem, and the transit recommendations do not transfer to unroofed venues without this check.")

cap_p = new_para_after(para,
    "Table 12. Open-air concourse scenario: 300 m² zone, γ = 0.75, +6 K globe (WBGT +1.8 K); E is comparable within the venue.")

# ---- build table 12
table = doc.add_table(rows=0, cols=6)
tbl = table._tbl
pr = copy.deepcopy(b2_pr)
tbl.remove(tbl.tblPr)
tbl.insert(0, pr)
tblW = pr.find(qn("w:tblW"))
tblW.set(qn("w:w"), "9972"); tblW.set(qn("w:type"), "dxa")
widths = [1250, 1650, 900, 1400, 1200, 1500, 2072]
grid = tbl.find(qn("w:tblGrid"))
for gc, w in zip(grid.findall(qn("w:gridCol")), widths[:6]):
    gc.set(qn("w:w"), str(w))

def add_run(p, text, bold=False, size=8):
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r._element.get_or_add_rPr()
    r.font.size = Pt(size)
    r.font.bold = bold
    return r

def cp(cell):
    p = cell.paragraphs[0]
    for q in cell.paragraphs[1:]:
        q._p.getparent().remove(q._p)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = Pt(10)
    return p

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    tcPr.append(shd)

ROWS = [
    ("Phoenix", "Do nothing", "—", "—", "0.2824", "reference"),
    ("Phoenix", "1× MC37V", "0.293", "2.670", "0.2969", "+0.0145"),
    ("Phoenix", "1× MC61V", "0.493", "2.679", "0.3088", "+0.0264"),
    ("Phoenix", "1× Portacool", "0.217", "2.695", "0.2226", "−0.0598"),
    ("Phoenix", "1× drum fan", "0.250", "2.081", "0.2957", "+0.0133"),
    ("Hong Kong", "Do nothing", "—", "—", "0.1965", "reference"),
    ("Hong Kong", "1× MC37V", "0.293", "1.066", "0.1761", "−0.0204"),
    ("Hong Kong", "1× MC61V", "0.493", "1.074", "0.1654", "−0.0311"),
    ("Hong Kong", "1× Portacool", "0.217", "1.091", "0.1109", "−0.0856"),
    ("Hong Kong", "1× drum fan", "0.250", "2.081", "0.2070", "+0.0105"),
]

hdr = table.add_row()
for cell, text, w in zip(hdr.cells, ["City", "Unit", "φ", "ΔT_eff (°C)", "E", "E − do nothing"], widths):
    cell.width = Twips(w)
    shade(cell, "D8D8D8")
    add_run(cp(cell), text, bold=True)

for row in ROWS:
    r_ = table.add_row()
    for i, val in enumerate(row):
        r_.cells[i].width = Twips(widths[i])
        add_run(cp(r_.cells[i]), val)

cap_p.addnext(tbl)
doc.save(PATH)
print("open-air section inserted; tables:", len(doc.tables))
