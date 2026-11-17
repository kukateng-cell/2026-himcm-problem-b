from docx import Document
from docx.oxml.ns import qn

DOCX = r"C:\Users\kukat\Desktop\USA\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"

PAGES = {
    "Summary Sheet": 2,
    "Table of Contents": 3,
    "1. Understanding the Problem (Q1)": 4,
    "2. Assumptions and Justifications": 5,
    "3. Mathematical Model": 6,
    "3.1 Parameter Baselines": 6,
    "3.2 Thermodynamic Cooling Constraint (Eq. 1)": 7,
    "3.3 Apparent Temperature and Jet Velocity Coupling (Eq. 2)": 7,
    "3.4 Spatial Cooling Efficiency (Eq. 3)": 8,
    "3.5 Annualised Life-Cycle Cost (Eq. 4)": 8,
    "3.6 Water–Carbon Externality (Eq. 5)": 8,
    "3.7 Safety Proxy and Decision Score (Eq. 6)": 8,
    "4. Model Application and Results (Q2–Q4)": 9,
    "4.1 Bus Stop Shelter Evaluation (Q2a)": 9,
    "4.2 Rail Platform and Multi-Unit Scaling (Q2b)": 10,
    "4.3 Cross-Climate Comparison (Q3)": 10,
    "4.4 Multi-Objective Trade-Offs (Q4)": 12,
    "5. Sensitivity Analysis and Model Evaluation": 13,
    "5.1 Parameter, Policy and Decision-Weight Sensitivity": 13,
    "5.2 Hourly Weather Scenarios": 14,
    "5.3 Joint Uncertainty": 14,
    "5.4 Calculation Checks and Plausibility": 15,
    "5.5 Model Strengths, Limitations and Future Improvements": 15,
    "5.6 Crosswind, Fan Limits and the Joint Operating Point": 16,
    "5.7 Definition Sensitivity: Where the Recommendation Changes": 17,
    "6. Decision Memorandum, Public Blog, Guidelines and References": 17,
    "6.1 Executive Memorandum to the COO (Q5a)": 17,
    "6.2 Public-Facing Blog Post (Q5b)": 18,
    "6.3 Deployment Guidelines Across the Four Venues": 19,
    "6.4 References": 20,
    "AI Use Report": 21,
    "Appendix A. Data and Assumption Register": 22,
    "Appendix B. Single-Factor Sensitivity": 23,
}

d = Document(DOCX)
changed = 0
missing = []
for p in d.element.body.iter(qn("w:p")):
    pPr = p.find(qn("w:pPr"))
    if pPr is None:
        continue
    st = pPr.find(qn("w:pStyle"))
    if st is None or not (st.get(qn("w:val")) or "").startswith("TOC"):
        continue
    ts = [t for t in p.iter(qn("w:t"))]
    if not ts:
        continue
    # split title (all non-numeric text) and number (last numeric run)
    title_parts = []
    num_el = None
    for t in ts:
        txt = (t.text or "").strip()
        if txt.isdigit():
            num_el = t
        elif txt:
            title_parts.append(txt)
    title = " ".join(title_parts).strip()
    if num_el is None:
        continue
    key = None
    for k in PAGES:
        if title.startswith(k):
            key = k
            break
    if key:
        num_el.text = str(PAGES[key])
        changed += 1
    else:
        missing.append(title)

d.save(DOCX)
print("updated entries:", changed)
print("unmatched:", missing[:10])
