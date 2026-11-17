# -*- coding: utf-8 -*-
"""Stage 2: rewrite Tables 3, 4, 5, 6 with the v2 numbers."""
import json
from docx import Document

SRC = r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"
OUT = r"C:\Users\kukat\Desktop\USA\_extract\v1.3_work.docx"
DATA = r"C:\Users\kukat\Desktop\USA\_extract\v2_numbers.json"

with open(DATA, encoding="utf-8") as f:
    D = json.load(f)

doc = Document(SRC)

def set_cell(cell, text):
    p = cell.paragraphs[0]
    for r in p.runs[1:]:
        r._r.getparent().remove(r._r)
    if p.runs:
        p.runs[0].text = text
    else:
        p.add_run(text)

T = doc.tables

# ---- Table 3 (index 5): rows A/B/C
for row, r in zip(T[5].rows[1:], D["T3"]):
    set_cell(row.cells[2], "%.3f" % r["dT"])
    set_cell(row.cells[3], "%.3f" % r["phi"])
    set_cell(row.cells[4], "%.2f" % r["eta"])
    set_cell(row.cells[5], "%.2f" % r["lcc"])
    set_cell(row.cells[6], "%.2f" % r["wbgt"])
    set_cell(row.cells[7], "%.4f" % r["E"])

# ---- Table 4 (index 6): 16 rows
for row, r in zip(T[6].rows[1:], D["T4"]):
    set_cell(row.cells[3], "%.3f" % r["phi"])
    set_cell(row.cells[4], "%.3f" % r["dT"])
    set_cell(row.cells[5], "%.2f" % r["lcc"])
    set_cell(row.cells[6], "%.2f" % r["wbgt"])
    set_cell(row.cells[7], "%.3f" % r["s"])
    set_cell(row.cells[8], "%.4f" % r["E"])

# ---- Table 5 (index 8): 16 rows
for row, r in zip(T[8].rows[1:], D["T5"]):
    set_cell(row.cells[4], "%.3f" % r["dT"])
    set_cell(row.cells[5], "%.3f" % r["phi"])
    set_cell(row.cells[6], "%.2f" % r["eta"])
    set_cell(row.cells[7], "%.2f" % r["lcc"])
    set_cell(row.cells[8], "%.4f" % r["ienv"])
    set_cell(row.cells[9], "%.2f" % r["wbgt"])
    set_cell(row.cells[10], "%.4f" % r["E"])

# ---- Table 6 (index 9): 4 profile rows
order = ["Phoenix bus", "Phoenix rail", "HK bus", "HK rail"]
by_prof = {}
for r in D["T6"]:
    by_prof.setdefault(r["profile"], {})[(r["city"], r["venue"])] = r
profiles = ["Balanced", "Safety", "Cost", "Eco"]
for i, prof in enumerate(profiles):
    row = T[9].rows[i + 1]
    for j, key in enumerate([("PHX", "bus"), ("PHX", "rail"), ("HK", "bus"), ("HK", "rail")], start=1):
        r = by_prof[prof][key]
        set_cell(row.cells[j], "%s (%.3f)" % (r["eq"], r["E"]))
    # none columns
    none = by_prof[prof][("PHX", "bus")]["none"]
    none_hk = by_prof[prof][("HK", "bus")]["none"]
    set_cell(row.cells[5], "%.3f" % none)
    set_cell(row.cells[6], "%.3f" % none_hk)

doc.save(OUT)
print("saved", OUT)
for i in (5, 6, 8, 9):
    t = doc.tables[i]
    print("--- table", i)
    for row in t.rows[:4]:
        print(" | ".join(c.text for c in row.cells))
