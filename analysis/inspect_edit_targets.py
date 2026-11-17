# -*- coding: utf-8 -*-
from docx import Document
from docx.oxml.ns import qn

SRC = r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"
doc = Document(SRC)

TARGETS = [
    ("A1", "Table 2A lists the four commercial benchmark units"),
    ("A3", "The Phoenix case is the 12th St"),
    ("A2", "with c_p = 1.006"),
    ("A4", "Figure 3 shows the crossover"),
    ("A5", "Figure 3. RH crossover"),
    ("A7", "Assumption 6"),
    ("A8", "Note: the “Energy Use”"),
]

for tag, prefix in TARGETS:
    for p in doc.paragraphs:
        if p.text.strip().startswith(prefix):
            print(f"=== {tag} | style={p.style.name} | runs={len(p.runs)}")
            for i, r in enumerate(p.runs):
                if r.text:
                    print(f"   [{i}] {r.text!r}")
            break
    else:
        print(f"=== {tag} NOT FOUND")
