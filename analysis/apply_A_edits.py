# -*- coding: utf-8 -*-
"""Apply edits A1-A8 (incl. Figure 3 numbers) to the paper."""
import copy
from docx import Document
from docx.oxml.ns import qn

SRC = r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"
OUT = r"C:\Users\kukat\Desktop\USA\_extract\v1.2_A.docx"

doc = Document(SRC)

def find(prefix):
    for p in doc.paragraphs:
        if p.text.strip().startswith(prefix):
            return p
    raise SystemExit("not found: " + prefix)

# A1
p = find("Table 2A lists the four commercial benchmark units")
old = "balance in Eq. 4 (Section 3.5)"
assert old in p.runs[0].text
p.runs[0].text = p.runs[0].text.replace(old, "balance in Eq. 7 (Section 3.5)")

# A3
p = find("The Phoenix case is the 12th St")
old = " 149 LRVs and 3.90 million daily bus journeys are marked U because the PDF text layer is unreliable and the figures need a page-level check."
assert old in p.runs[0].text
p.runs[0].text = p.runs[0].text.replace(old, "")

# A2
p = find("with c_p = 1.006")
p.runs[0].text += (" Eq. 7 is the auxiliary water balance that supplies V_w to Eqs. 4–5; "
                   "it is not one of the six decision equations.")

# A4
p = find("Figure 3 shows the crossover")
assert "76.7%" in p.runs[0].text and "65.1%" in p.runs[0].text
p.runs[0].text = p.runs[0].text.replace("76.7%", "76.4%").replace("65.1%", "64.7%")

# A5
p = find("Figure 3. RH crossover")
assert "bus 65.1%" in p.runs[0].text and "rail 76.7%" in p.runs[0].text
p.runs[0].text = p.runs[0].text.replace("bus 65.1%", "bus 64.7%").replace("rail 76.7%", "rail 76.4%")

# A7
p = find("Assumption 6")
done = False
for r in p.runs:
    if "Black-globe offsets" in r.text:
        r.text = r.text.replace(
            "Black-globe offsets of +3 and +6 K are tested in Section 5.",
            "A black-globe offset of +3 K is tested in Section 5.1.")
        done = True
assert done, "A7 target run not found"

# A8
p = find("Note: the “Energy Use”")
p.runs[0].text += (" Systems A–C are the prompt’s illustrative inputs; their power and airflow are not "
                   "linked by a fan law, so the power–airflow ratio is not a physical equipment specification.")

# A6: new note paragraph after Table 2B, copying the formatting of the existing Note
note_p = find("Note: the “Energy Use”")
new_p = copy.deepcopy(note_p._p)
runs = new_p.findall(qn("w:r"))
for r in runs[1:]:
    new_p.remove(r)
t = runs[0].find(qn("w:t"))
t.text = ("Note: the Hong Kong grid factor is CLP’s 2023 emission intensity (0.390 kg CO₂e/kWh); "
          "the 2024 value is 0.38, and Appendix B tests 0.465.")

table_2b = None
for tb in doc.tables:
    hdr = [c.text.strip() for c in tb.rows[0].cells]
    if hdr[:2] == ["Parameter", "Symbol"] and "Phoenix" in hdr:
        table_2b = tb
        break
assert table_2b is not None
table_2b._tbl.addnext(new_p)

doc.save(OUT)
print("saved", OUT)
