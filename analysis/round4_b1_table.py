# -*- coding: utf-8 -*-
"""Round 4: rewrite Table B1 with the v2 sensitivity values."""
import json
from docx import Document

PATH = r"C:\Users\kukat\Desktop\USA\_extract\v1.3_work.docx"
with open(r"C:\Users\kukat\Desktop\USA\_extract\b1_v2.json", encoding="utf-8") as f:
    DATA = json.load(f)

doc = Document(PATH)
t = doc.tables[19]

def set_cell(cell, text):
    p = cell.paragraphs[0]
    for r in p.runs[1:]:
        r._r.getparent().remove(r._r)
    if p.runs:
        p.runs[0].text = text
    else:
        p.add_run(text)

print("rows:", len(t.rows), "data:", len(DATA))
for row, (label, vals) in zip(t.rows[1:], DATA):
    if row.cells[0].text.strip() == "kappa 60":
        set_cell(row.cells[0], "kappa 105")
    if row.cells[0].text.strip() == "kappa 30":
        set_cell(row.cells[0], "kappa=30")
    for j, v in enumerate(vals, start=1):
        set_cell(row.cells[j], "%.4f" % v)

doc.save(PATH)
for row in t.rows[:4]:
    print(" | ".join(c.text for c in row.cells))
print("...")
for row in t.rows[-3:]:
    print(" | ".join(c.text for c in row.cells))
