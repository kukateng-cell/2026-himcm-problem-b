# -*- coding: utf-8 -*-
"""Tighten four nomenclature rows so every symbol in Eqs. 1-7 is explicit."""
from docx import Document

SRC = r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"
OUT = r"C:\Users\kukat\Desktop\USA\_extract\v1.2_final.docx"

EDITS = {
    25: "Centreline velocity at distance x from the outlet, outlet velocity, outlet area, von Glahn constant (2.4)",
    35: "Water consumption rate from the energy balance (kg/h reported as L/h)",
    36: "Dry-air mass flow and dry-air density, p/(287T), with 287 J/(kg·K) the dry-air gas constant",
    52: "Graded heat-safety score of the WBGT proxy W: 0 at 35 °C, 1 at 29 °C",
}

doc = Document(SRC)
table = [t for t in doc.tables if t.rows[0].cells[0].text.strip() == "Symbol"][0]
for idx, text in EDITS.items():
    cell = table.rows[idx].cells[1]
    assert len(cell.paragraphs) == 1, idx
    assert len(cell.paragraphs[0].runs) == 1, idx
    cell.paragraphs[0].runs[0].text = text
    print(idx, "->", text)

doc.save(OUT)
print("saved", OUT)
