# -*- coding: utf-8 -*-
import io
p = r"analysis/apply_math.py"
s = io.open(p, encoding="utf-8").read()
old = '''    for row_i, latex in NOMEN.items():
        cell = doc.tables[1].rows[row_i].cells[0]
        mathdoc.rebuild(cell.paragraphs[0], [(M, latex)], size=16)
        mathdoc.relax_line(cell.paragraphs[0])
'''
new = '''    for row_i, latex in NOMEN.items():
        cell = doc.tables[1].rows[row_i].cells[0]
        mathdoc.rebuild(cell.paragraphs[0], [(M, latex)], size=16)
        mathdoc.relax_line(cell.paragraphs[0], 170)
    mathdoc.tight_table(doc.tables[1], top=6, bottom=6, left=70, right=70)
    for row in doc.tables[1].rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                mathdoc.relax_line(p, 170)
'''
assert old in s
s = s.replace(old, new)
io.open(p, "w", encoding="utf-8").write(s)
print("patched nomen spacing")
