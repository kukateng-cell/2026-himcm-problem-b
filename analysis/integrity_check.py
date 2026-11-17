# -*- coding: utf-8 -*-
"""Integrity check: new Desktop docx vs the original backup."""
from docx import Document

ORIG = r"C:\Users\kukat\Desktop\USA\_extract\backup_desktop_v1.2_original.docx"
NEW = r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"

a = Document(ORIG)
b = Document(NEW)

print("tables:", len(a.tables), "->", len(b.tables))
print("paragraphs:", len(a.paragraphs), "->", len(b.paragraphs))

# compare the 19 original tables (indices 0..18 in original; the new table is index 1? locate by header)
new_tables = b.tables
nol = [t for t in new_tables if 'Symbol' in t.rows[0].cells[0].text and 'Definition' in t.rows[0].cells[1].text]
print("nomenclature tables found in new:", len(nol))

diffs = 0
for i, ta in enumerate(a.tables):
    # find matching table in b by first cell text and row count
    key = (ta.rows[0].cells[0].text, len(ta.rows), len(ta.columns))
    match = [tb for tb in new_tables if (tb.rows[0].cells[0].text, len(tb.rows), len(tb.columns)) == key]
    if not match:
        print("NO MATCH for table", i, key)
        diffs += 1
        continue
    tb = match[0]
    for r in range(len(ta.rows)):
        for c in range(len(ta.columns)):
            if ta.rows[r].cells[c].text != tb.rows[r].cells[c].text:
                print("CELL DIFF table", i, r, c, repr(ta.rows[r].cells[c].text[:30]), "->", repr(tb.rows[r].cells[c].text[:30]))
                diffs += 1
print("table cell diffs:", diffs)

# paragraph diff
pa = [p.text for p in a.paragraphs]
pb = [p.text for p in b.paragraphs]
import difflib
for line in difflib.unified_diff(pa, pb, lineterm="", n=0):
    if line.startswith(('+++','---','@@')):
        continue
    print(line[:160])
