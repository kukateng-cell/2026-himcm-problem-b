# -*- coding: utf-8 -*-
"""Round 4b: Table 7 and Section 5.2 prose under the v2 hourly run."""
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

t7 = doc.tables[11]
rows = [
    ("MC37V 98% / Fan 2%", "MC37V 100%", "0%"),
    ("MC61V 89% / MC37V 11%", "MC61V 100%", "0%"),
    ("Fan 94% / MC37V 6%", "MC37V 59% / Fan 41%", "0%"),
    ("Fan 51% / MC37V 42% / MC61V 7%", "MC61V 74% / MC37V 26%", "75%"),
]
for row, vals in zip(t7.rows[1:], rows):
    for j, v in enumerate(vals, start=1):
        set_cell(row.cells[j], v)

REPL = [
 ("In Phoenix, MC37V wins 99% of bus-shelter device-hours and MC61V wins 89% of platform device-hours; both win every hour of the hottest decile. In Hong Kong the choice is time-dependent: the fan wins 88% of bus-shelter device-hours, but MC37V wins 98% of the hottest bus hours; on the platform the fan is the most frequent device winner (51%), MC37V follows at 42%, and MC61V wins 74% of the hottest platform hours.",
  "In Phoenix, MC37V wins 98% of bus-shelter device-hours and MC61V wins 89% of platform device-hours; both win every hour of the hottest decile. In Hong Kong the choice is time-dependent: the fan wins 94% of bus-shelter device-hours, and the hottest bus hours split between MC37V (59%) and the fan (41%); on the platform the fan is the most frequent device winner (51%), MC37V follows at 42%, and MC61V wins 74% of the hottest platform hours."),
]

def repl_para(p, old, new):
    if old not in p.text or not p.runs:
        return False
    text = p.text.replace(old, new)
    for r in p.runs[1:]:
        r._r.getparent().remove(r._r)
    p.runs[0].text = text
    return True

cnt = 0
for p in doc.paragraphs:
    for old, new in REPL:
        if old in p.text and repl_para(p, old, new):
            cnt += 1
print("prose replacements:", cnt)
doc.save(PATH)
for row in t7.rows:
    print(" | ".join(c.text for c in row.cells))
