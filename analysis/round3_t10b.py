# -*- coding: utf-8 -*-
"""Round 3b: update Table 10b and its prose to v2 water-limited values."""
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

rows = [
    ("0.4794", "0.3671"),
    ("0.4015", "0.3087"),
    ("0.4417", "0.3536"),
    ("0.4131", "0.4131"),
    ("0.4020", "0.3103"),
    ("0.4034", "0.2878"),
    ("0.3046", "0.2548"),
    ("0.3000", "0.3000"),
]
for row, (b, w) in zip(doc.tables[15].rows[1:], rows):
    set_cell(row.cells[2], b)
    set_cell(row.cells[3], w)

REPL = [
 ("the Phoenix bus-shelter winner changes from MC37V (0.481) to the drum fan (0.371 vs 0.352), and the platform winner changes from MC61V (0.403) to MC37V (0.309 vs 0.287, with MC61V falling below doing nothing)",
  "the Phoenix bus-shelter winner changes from MC37V (0.479) to the drum fan (0.413 vs 0.367), and the platform winner changes from MC61V (0.403) to MC37V (0.310 vs 0.288, with MC61V falling below doing nothing)"),
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
doc.save(PATH)
print("table 10b updated; prose replacements:", cnt, "/", len(REPL))
for row in doc.tables[15].rows:
    print(" | ".join(c.text for c in row.cells))
