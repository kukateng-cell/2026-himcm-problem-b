# -*- coding: utf-8 -*-
"""Round 4c: Table 8 and Section 5.3 prose under the v2 Monte Carlo."""
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

t8 = doc.tables[12]
rows = [
    ("88%", "0%", "11%", "1%", "0%"),
    ("48%", "52%", "0%", "0%", "0%"),
    ("0%", "0%", "0%", "100%", "0%"),
    ("38%", "3%", "0%", "0%", "58%"),
]
for row, vals in zip(t8.rows[1:], rows):
    for j, v in enumerate(vals, start=1):
        set_cell(row.cells[j], v)

REPL = [
 ("over κ ~ U(30,60), γ ~ U(0.45,0.65)", "over κ_bus ~ U(60,105) and κ_rail ~ U(35,55), γ ~ U(0.45,0.65)"),
 ("MC61V is best in 50% of draws and MC37V in 50%, and E(MC61V) > E(MC37V) in 50% of draws",
  "MC61V is best in 52% of draws and MC37V in 48%, and E(MC61V) > E(MC37V) in 52% of draws"),
 ("MC37V beats the fan in 92% of draws", "MC37V beats the fan in 96% of draws"),
 ("the do-nothing option is best in 67% of draws", "the do-nothing option is best in 58% of draws"),
 ("MC37V 85% in Phoenix, fan 79% in Hong Kong, with Portacool taking 14% of Phoenix draws",
  "MC37V 88% in Phoenix, fan 100% in Hong Kong, with Portacool taking 11% of Phoenix draws"),
]

def repl_para(p, old, new):
    if old not in p.text or not p.runs:
        return False
    text = p.text.replace(old, new)
    for r in p.runs[1:]:
        r._r.getparent().remove(r._r)
    p.runs[0].text = text
    return True

counts = [0]*len(REPL)
for p in doc.paragraphs:
    for i,(old,new) in enumerate(REPL):
        if old in p.text and repl_para(p, old, new):
            counts[i]+=1
print("counts", counts)
doc.save(PATH)
for row in t8.rows:
    print(" | ".join(c.text for c in row.cells))
