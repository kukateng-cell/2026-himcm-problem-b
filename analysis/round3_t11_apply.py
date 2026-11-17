# -*- coding: utf-8 -*-
"""Round 3d: Table 11 and its Reading paragraph under v2."""
from docx import Document

PATH = r"C:\Users\kukat\Desktop\USA\_extract\v1.3_work.docx"
doc = Document(PATH)

def set_cell(cell, text):
    p = cell.paragraphs[0]
    for r in p.runs[1:]:
        r._r.getparent().remove(r._r)
    if p.runs:
        p.runs[0].text = text
    else:
        p.add_run(text)

t11 = doc.tables[16]
set_cell(t11.rows[1].cells[2], "HK rail MC37V 0.1467 > do-nothing 0.1365; HK bus fan 0.2467 > MC37V 0.2009")
set_cell(t11.rows[2].cells[2], "32.5/78: fan bus 0.3528 vs MC37V 0.3045, MC37V rail 0.2506 vs MC61V 0.2404; 33.5/62: fan bus 0.4033 vs MC37V 0.3914; rail MC37V 0.3242 ≈ MC61V 0.3239")
set_cell(t11.rows[3].cells[2], "B E = 0.385 < A 0.432; the Q2a ranking holds")
set_cell(t11.rows[4].cells[2], "η 862 → 115 (MC37V) and 685 → 91 (MC61V); E unchanged at 0.4020/0.4034 because N cancels in the normaliser; no ranking change")
set_cell(t11.rows[5].cells[2], "Water-limited Phoenix: the fan wins (0.413) over MC37V (0.367); κ remains the largest single lever on the bus ranking")

READING = ("Reading: the Phoenix bus-shelter choice survives the safety and design-day entries but not κ: at the adopted κ = 84 the margin over the fan is "
           "0.479 vs 0.413, and the fan overtakes at κ ≈ 92. The Phoenix platform is a near-tie (MC61V 0.4034 vs MC37V 0.4020) and flips if the effective "
           "MC37V area is only 0.6% larger (88.5 m²); occupancy does not flip it, because E is invariant to N once the normalisers are recomputed. "
           "The Hong Kong bus choice holds at both design hours once the fan’s felt cooling is credited (0.397 at 31.7/77 and 0.403 at 33.5/62, against "
           "0.391 for MC37V). The Hong Kong platform is below doing nothing at baseline, so it is not a deployment case. Q2a is robust, and κ remains the "
           "entry that can reverse the bus ranking.")

hit = 0
for p in doc.paragraphs:
    if p.text.startswith("Reading: the Phoenix bus-shelter choice"):
        for r in p.runs[1:]:
            r._r.getparent().remove(r._r)
        p.runs[0].text = READING
        hit += 1
print("reading paragraph replaced:", hit)

doc.save(PATH)
for row in doc.tables[16].rows:
    print(" | ".join(c.text for c in row.cells)[:200])
