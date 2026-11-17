# -*- coding: utf-8 -*-
"""Insert the structural stress-test paragraph (Section 5.5) and Table B2 (Appendix B)."""
import copy
from docx import Document
from docx.shared import Pt, Twips
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

SRC = r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"
OUT = r"C:\Users\kukat\Desktop\USA\_extract\v1.2_C.docx"

GROUPS = [
    ("Open-air concourse (300 m² zone, γ = 0.75, +6 K globe → +1.8 K WBGT)", [
        ("Phoenix", "Do nothing", "—", "0.2824"),
        ("Phoenix", "1× MC37V", "—", "0.2588"),
        ("Phoenix", "1× drum fan", "—", "0.2704"),
        ("Hong Kong", "Do nothing", "—", "0.1965"),
        ("Hong Kong", "1× MC37V", "—", "0.1609"),
        ("Hong Kong", "1× drum fan", "—", "0.1816"),
    ]),
    ("Jet-mixing coefficient (Phoenix bus shelter)", [
        ("1× MC37V", "κ = 84", "0.4806", "0.5114"),
        ("1× drum fan", "κ = 84", "0.3705", "0.4931"),
        ("1× drum fan", "κ = 105", "0.3705", "0.5591"),
    ]),
    ("Fan at 41 °C, no felt-cooling credit above 35 °C", [
        ("Phoenix bus", "1× drum fan", "0.3705", "0.2290"),
        ("Phoenix rail", "1× drum fan", "0.2885", "0.2290"),
    ]),
    ("Two units with 30% jet overlap", [
        ("Phoenix rail", "2× Portacool", "0.2834", "0.2109"),
        ("Hong Kong rail", "2× drum fan", "0.2339", "0.2168"),
    ]),
    ("Normaliser candidate set (one premium unit added)", [
        ("Hong Kong rail", "Do nothing", "0.2865", "0.2865"),
        ("Hong Kong rail", "1× MC37V", "0.2858", "0.3360"),
    ]),
]

doc = Document(SRC)
ref_tbl = doc.tables[-1]  # Table B1

# ---------- Section 5.5 paragraph
target = None
for p in doc.paragraphs:
    if p.text.strip().startswith("Limitations: the drum fan is a hypothetical benchmark"):
        target = p
        break
assert target is not None

new_p = copy.deepcopy(target._p)
# strip runs to one, keep paragraph formatting
runs = new_p.findall(qn("w:r"))
for r in runs[1:]:
    new_p.remove(r)
t = runs[0].find(qn("w:t"))
t.text = ("Structural stress tests (Table B2) probe what the base tables cannot. "
          "Open-air: at a concourse with γ = 0.75 and a +6 K globe offset (WBGT +1.8 K) no unit clears doing nothing in either city "
          "(Phoenix 0.2824, Hong Kong 0.1965), so the transit recommendations do not transfer to unroofed venues without a site-specific check. "
          "κ: at the distance-averaged κ ≈ 84 the Phoenix shelter order holds (MC37V 0.5114 vs fan 0.4931); the fan leads only above κ ≈ 92 "
          "and reaches 0.5591 at κ = 105. "
          "Heat: if the fan earns no felt cooling above 35 °C, its 41 °C score falls to 0.2290 in both Phoenix venues, below every baseline. "
          "Overlap: a 30% jet overlap lowers two-unit scores further (Phoenix 2× Portacool 0.2834 → 0.2109; Hong Kong 2× fan 0.2339 → 0.2168). "
          "Candidate set: adding one premium unit to the normaliser set raises every device score and flips the Hong Kong platform sign "
          "(1× MC37V 0.2858 → 0.3360 against 0.2865), so that 0.0007 margin is a near-tie, not a demonstrated failure.")
target._p.addnext(new_p)

# ---------- Table B2
b1_note = None
for p in doc.paragraphs:
    if p.text.strip().startswith("The 28 °C row shifts the safety curve"):
        b1_note = p
        break
assert b1_note is not None

caption = copy.deepcopy(b1_note._p)
runs = caption.findall(qn("w:r"))
for r in runs[1:]:
    caption.remove(r)
t = runs[0].find(qn("w:t"))
t.text = ("Table B2. Structural stress tests: open-air venue, jet-mixing coefficient, "
          "41 °C fan derating, jet overlap and normaliser candidate set.")

table = doc.add_table(rows=0, cols=4)
tbl = table._tbl
new_pr = copy.deepcopy(ref_tbl._tbl.tblPr)
tbl.remove(tbl.tblPr)
tbl.insert(0, new_pr)
tblW = new_pr.find(qn("w:tblW"))
tblW.set(qn("w:w"), "9972")
tblW.set(qn("w:type"), "dxa")
widths = [2500, 3300, 2000, 2172]
grid = tbl.find(qn("w:tblGrid"))
for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
    gc.set(qn("w:w"), str(w))

def add_run(p, text, bold=False, italic=False, size=8):
    r = p.add_run(text)
    r.font.name = "Times New Roman"
    r._element.get_or_add_rPr()
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    return r

def cell_p(cell):
    for p in cell.paragraphs[1:]:
        p._p.getparent().remove(p._p)
    p = cell.paragraphs[0]
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = Pt(10)
    return p

def set_tr(tr, header=False):
    trPr = tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))
    if header:
        trPr.append(OxmlElement("w:tblHeader"))

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    tcPr.append(shd)

hdr = table.add_row()
set_tr(hdr._tr, header=True)
for cell, text, w in zip(hdr.cells, ["Case", "Condition", "E (base)", "E (stress)"], widths):
    cell.width = Twips(w)
    shade(cell, "D8D8D8")
    add_run(cell_p(cell), text, bold=True)

for title, rows in GROUPS:
    row = table.add_row()
    set_tr(row._tr)
    merged = row.cells[0].merge(row.cells[3])
    merged.width = Twips(sum(widths))
    shade(merged, "F2F2F2")
    add_run(cell_p(merged), title, bold=True, italic=True)
    for a, b, c, d in rows:
        r_ = table.add_row()
        set_tr(r_._tr)
        cells = r_.cells
        for i, val in enumerate((a, b, c, d)):
            cells[i].width = Twips(widths[i])
            add_run(cell_p(cells[i]), val)

b1_note._p.addnext(tbl)
b1_note._p.addnext(caption)

doc.save(OUT)
print("saved", OUT, "rows", len(table.rows))
