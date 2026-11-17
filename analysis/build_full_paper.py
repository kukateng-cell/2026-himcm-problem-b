"""Build the integrated English master paper v1.0 (model rebuilt after the review).

Run: python analysis/build_full_paper.py
"""

import os
import re
from copy import deepcopy

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import recompute as R

R.MODE = "pressure"
R.THRESH = 33.0

T3, G3 = R.table3_rows("pressure", 33.0)
T4, G4 = R.table4_rows("pressure", 33.0)
T5, G5 = R.table5_rows("pressure", 33.0, "B")
T6_30 = R.table6(T5, G5, 33.0)
T5_28, G28 = R.table5_rows("pressure", 28.0, "B")
T6_28 = R.table6(T5_28, G28, 28.0)

OUT = "2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"
TEMPLATE = r"C:\Users\kukat\Documents\xwechat_files\wxid_9ol1c92g384k22_a33c\msg\file\2026-11\2026_HiMCM_ProblemB_new(1).docx"

doc = Document(TEMPLATE)
body = doc.element.body
for child in list(body):
    if not child.tag.endswith("}sectPr"):
        body.remove(child)

sec = doc.sections[0]
sec.top_margin = Cm(1.9); sec.bottom_margin = Cm(1.9)
sec.left_margin = Cm(2.0); sec.right_margin = Cm(2.0)

_n = doc.styles["Normal"]
_n.font.name = "Times New Roman"; _n.font.size = Pt(10)
_n.element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
_n.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
_n.paragraph_format.line_spacing = 1.15
_n.paragraph_format.space_after = Pt(3)

for _i, _sz in ((1, 14), (2, 12), (3, 11)):
    _st = doc.styles["Heading %d" % _i]
    _st.font.name = "Times New Roman"; _st.font.size = Pt(_sz)
    _st.font.bold = True; _st.font.color.rgb = RGBColor(0, 0, 0)
    _st.paragraph_format.keep_with_next = True
    _st.paragraph_format.space_before = Pt(18 if _i == 1 else 10)
    _st.paragraph_format.space_after = Pt(4)


def set_font(run, size=10, bold=False, color=None, italic=False, name="Times New Roman"):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.italic = italic
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts"); rPr.append(rFonts)
    rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    if color:
        run.font.color.rgb = color


def add_page_numbers(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def field(par, code):
        run = par.add_run()
        for kind in ("begin", "instr", "end"):
            if kind == "instr":
                it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = code
                run._r.append(it)
            else:
                fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), kind)
                run._r.append(fc)

    field(p, " PAGE ")
    r = p.add_run(" of "); set_font(r, 9)
    field(p, " NUMPAGES ")


def h1(text):
    h = doc.add_heading(level=1)
    r = h.add_run(text); set_font(r, 14, True, RGBColor(0, 0, 0))


def h2(text):
    h = doc.add_heading(level=2)
    r = h.add_run(text); set_font(r, 12, True, RGBColor(0, 0, 0))


def h3(text):
    h = doc.add_heading(level=3)
    r = h.add_run(text); set_font(r, 11, True, RGBColor(0, 0, 0))


def para(text, size=10, italic=False, align=None, space=3):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space)
    if align:
        p.alignment = align
    r = p.add_run(text); set_font(r, size, italic=italic)
    return p


def bullet(text, size=9.5):
    p = doc.add_paragraph(style="List Bullet")
    r = p.add_run(text); set_font(r, size)


def formula(parts, size=10, space=4):
    """Typeset a display equation: italic variables, true sub/superscripts."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space)
    for text, kind in parts:
        r = p.add_run(text)
        italic = kind in ("var", "subv")
        set_font(r, size, italic=italic)
        if kind == "sub":
            r.font.subscript = True
        elif kind == "subv":
            r.font.subscript = True
        elif kind == "sup":
            r.font.superscript = True
    return p


_TOK = re.compile(
    r"([A-Za-zΔτηκεφραγρṁ][A-Za-z0-9Δτηκεφραγρ]{0,3})_([A-Za-z0-9]+(?:,[A-Za-z0-9]+)*)"
    r"|\^\(([^)]+)\)"
)
_ITALIC = set("TevNAPCQVLrnpBEISWHxuqmΔΔTηφεγρακṁ")


def _typeset_run(run):
    txt = run.text
    if not txt or not _TOK.search(txt):
        return
    if any(s in txt for s in ("http", ".py", "Jetstream")):
        return
    parts = []
    pos = 0
    for m in _TOK.finditer(txt):
        if m.start() > pos:
            parts.append((txt[pos:m.start()], "plain"))
        if m.group(1):
            base, sub = m.group(1), m.group(2)
            parts.append((base, "var" if base in _ITALIC else "plain"))
            parts.append((sub, "sub"))
        else:
            parts.append((m.group(3), "sup"))
        pos = m.end()
    if pos < len(txt):
        parts.append((txt[pos:], "plain"))
    el = run._r
    from docx.text.run import Run
    for text, kind in parts:
        new_el = deepcopy(el)
        new_run = Run(new_el, run._parent)
        new_run.text = text
        if kind == "var":
            new_run.italic = True
        elif kind == "sub":
            new_run.font.subscript = True
            new_run.italic = False
        elif kind == "sup":
            new_run.font.superscript = True
            new_run.italic = False
        el.addprevious(new_el)
    el.getparent().remove(el)


def typeset_inline():
    """Convert T_db style tokens in body text and tables to real sub/superscripts."""
    for p in doc.paragraphs:
        for r in list(p.runs):
            _typeset_run(r)
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for r in list(p.runs):
                        _typeset_run(r)


def _shade(cell, fill="D9D9D9"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def table(headers, rows, widths=None, size=8):
    t = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    if widths:
        for i, w in enumerate(widths):
            t.columns[i].width = Cm(w)
    for j, htxt in enumerate(headers):
        cell = t.cell(0, j); cell.text = ""
        _shade(cell)
        p = cell.paragraphs[0]
        r = p.add_run(htxt); set_font(r, size, True)
    trPr = t.rows[0]._tr.get_or_add_trPr()
    tblHeader = OxmlElement("w:tblHeader"); tblHeader.set(qn("w:val"), "true")
    trPr.append(tblHeader)
    for row in t.rows:
        trPr = row._tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit"); cant.set(qn("w:val"), "true")
        trPr.append(cant)
    for i, row in enumerate(rows, start=1):
        for j, v in enumerate(row):
            cell = t.cell(i, j); cell.text = ""
            p = cell.paragraphs[0]
            r = p.add_run(str(v)); set_font(r, size)
    doc.add_paragraph()
    return t


def figure(path, caption, width_cm=15.5):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Cm(width_cm))
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_after = Pt(8)
    cp.paragraph_format.keep_together = True
    r = cp.add_run(caption)
    set_font(r, 9, italic=True)
    return p


def find(rows, city, venue, eq, n=1):
    return next(r for r in rows if r["city"] == city and r["venue"] == venue and r["eq"] == eq and r["n"] == n)


def nd_E(city, venue):
    nd = R.no_device(city, venue)
    return R.score(nd, G5, threshold=33.0)[0]


# ---------------------------------------------------------------- cover
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("2026 HiMCM"); set_font(r, 14, True, RGBColor(0x66, 0x66, 0x66), name="Calibri")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Problem B: Air Conditioning the Environment"); set_font(r, 20, True, RGBColor(0x1F, 0x3B, 0x57), name="Calibri")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Cooling per Kilowatt for Semi-Open Transit Spaces"); set_font(r, 16, False, RGBColor(0x1F, 0x3B, 0x57), name="Calibri")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("A Six-Equation Framework with Heat–Water Balance and a Do-Nothing Baseline\nfor Semi-Open Transit Cooling")
set_font(r, 12, False, RGBColor(0x33, 0x33, 0x33), name="Calibri")
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Team 19362   |   November 2026"); set_font(r, 11, name="Calibri")
doc.add_page_break()

# ---------------------------------------------------------------- summary
h1("Summary Sheet")
para("Public cooling is usually judged by kilowatt-hours, but energy alone cannot separate a working system from a failing one. An open freezer and a semi-open transit shelter share the same physics: cold air is produced inside a boundary and leaks through an opening, so the useful cooling delivered to the people inside — not the electricity drawn — is what should be counted. We build a six-equation model and apply it to a 15 m² bus shelter and a rail platform in Phoenix (41 °C / 18% RH) and Hong Kong (31.7 °C / 77% RH).")
para(f"Eqs. 1–2 give the thermodynamic cooling and its apparent-temperature effect; Eq. 3 converts them into η, in persons·°C per kW; Eq. 4 prices the life-cycle cost after the cooling water is derived from an adiabatic mass balance; Eq. 5 prices the water–carbon externality; Eq. 6 combines a graded heat-safety proxy, a persons-weighted cooling benefit, cost and environment. Coverage is measured against the modelled waiting zone (120 m² in Phoenix, 128 m² in Hong Kong), not the whole platform (425 m² and 128 m²), and every result is compared with a do-nothing baseline.")
para(f"The model reverses two intuitions and corrects a third. In Q2a the 0.25 kW fan is {T3[0]['eta']/T3[2]['eta']:.1f} times more efficient than the 2.5 kW cooler (η = {T3[0]['eta']:.2f} vs {T3[2]['eta']:.2f}), because extra power buys little extra cooling. In Q2b, at a Phoenix platform 1× MC61V scores E = {find(T4,'PHX','rail','MC61V',1)['E']:.4f} and covers the waiting zone, while 2× MC37V scores {find(T4,'PHX','rail','MC37V',2)['E']:.4f} at twice the capital cost; under this base no two-unit deployment beats one, because the coverage gain does not repay the second unit (2× Portacool {find(T4,'PHX','rail','Porta',2)['E']:.4f} vs 1× {find(T4,'PHX','rail','Porta',1)['E']:.4f}). In Hong Kong the bus shelter favours the drum fan over most summer hours (E = {find(T5,'HK','bus','Fan',1)['E']:.4f} vs {find(T5,'HK','bus','MC37V',1)['E']:.4f} for MC37V), but the hottest local hours switch to MC37V (Section 5.2); on the rail platform MC37V ({find(T5,'HK','rail','MC37V',1)['E']:.4f}) is essentially tied with doing nothing ({nd_E('HK','rail'):.4f}) and only slightly ahead of MC61V ({find(T5,'HK','rail','MC61V',1)['E']:.4f}) and the fan ({find(T5,'HK','rail','Fan',1)['E']:.4f}), so it is not a deployment case.")
para(f"A do-nothing baseline is reported throughout: its score is {nd_E('PHX','bus'):.4f} in Phoenix and {nd_E('HK','bus'):.4f} in Hong Kong; every Phoenix recommendation and the Hong Kong bus-shelter fan clear it, while the Hong Kong platform is already a hair below it (0.2858 vs 0.2865) and falls further under full installation costs, so the recommendations are conditional rather than artefacts of ignoring the alternative. Water use is not a free assumption: at rated airflow a 11 °C drop on 3,100 CFM requires about 25 L/h, roughly double the tank-based rate often quoted, and this cost is carried through Eq. 4 and Eq. 5.")
para("Recommendations: size for coverage first, then minimise cost and environmental burden. In Phoenix, 1× MC37V at the bus shelter — conditional on the uncalibrated jet-mixing coefficient, because at the geometrically implied κ ≈ 80–105 the fan overtakes above κ ≈ 92; at the platform, 1× MC61V only if full coverage is a hard requirement, otherwise 1× MC37V (0.4015 vs 0.4026; $243.80 vs $397.41), and under the water-limited joint operating point the platform order reverses to MC37V. In Hong Kong, 1× drum fan at bus shelters; the hottest, driest hours are a re-evaluation point for the cooler, not a two-unit switching recommendation, because the second unit's fixed cost is not costed here. On the rail platform no device clears the do-nothing baseline, so shade and windbreak come first and no unit is recommended. Data boundaries: both platforms use representative geometry; the drum fan is a hypothetical benchmark; κ has no field calibration; WBGT is a proxy, not a compliance measurement; and 31.7 °C/77% is a selected design hour, not the series maximum WBGT. Recommendations are conditional on these inputs, and the near-ties require a site pilot.")
doc.add_page_break()

# ---------------------------------------------------------------- TOC (page numbers filled after layout)
h1("Table of Contents")
toc = [
    ("Summary Sheet", "2"),
    ("1. Understanding the Problem (Q1)", "4"),
    ("2. Assumptions and Justifications", "5"),
    ("3. Mathematical Model", "6"),
    ("   3.1 Parameter Baselines", "6"),
    ("   3.2 Thermodynamic Cooling Constraint (Eq. 1)", "7"),
    ("   3.3 Apparent Temperature and Jet Velocity (Eq. 2)", "7"),
    ("   3.4 Spatial Cooling Efficiency (Eq. 3)", "8"),
    ("   3.5 Annualised Life-Cycle Cost (Eq. 4)", "8"),
    ("   3.6 Water–Carbon Externality (Eq. 5)", "8"),
    ("   3.7 Safety Proxy and Decision Score (Eq. 6)", "8"),
    ("4. Model Application and Results (Q2–Q4)", "9"),
    ("   4.1 Bus Stop Shelter (Q2a)", "9"),
    ("   4.2 Rail Platform and Multi-Unit Scaling (Q2b)", "10"),
    ("   4.3 Cross-Climate Comparison (Q3)", "10"),
    ("   4.4 Multi-Objective Trade-Offs (Q4)", "12"),
    ("5. Sensitivity Analysis and Model Evaluation", "13"),
    ("6. Decision Memorandum, Public Blog, Guidelines and References", "18"),
    ("   6.1 Executive Memorandum to the COO (Q5a)", "18"),
    ("   6.2 Public-Facing Blog Post (Q5b)", "19"),
    ("   6.3 Deployment Guidelines Across the Four Venues", "20"),
    ("   6.4 References", "20"),
    ("AI Use Report", "21"),
    ("Appendix A. Data and Assumption Register", "22"),
    ("Appendix B. Single-Factor Sensitivity", "23"),
]
for _txt, _pg in toc:
    _sub = _txt.startswith("   ")
    _p = doc.add_paragraph()
    _p.paragraph_format.space_after = Pt(1)
    _p.paragraph_format.tab_stops.add_tab_stop(
        Cm(17.2), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
    if _sub:
        _p.paragraph_format.left_indent = Cm(0.7)
    _r = _p.add_run(_txt.strip())
    set_font(_r, 10)
    _r2 = _p.add_run("\t" + _pg)
    set_font(_r2, 10)
doc.add_page_break()

# ---------------------------------------------------------------- section 1
h1("1. Understanding the Problem (Q1)")
para("Consider an open-front freezer in a supermarket. Its job is to hold goods at about −18 °C while its front is open to a 24 °C aisle. The compressor removes the heat that leaks in through the opening; an air curtain, a night cover, or a change of door discipline changes how much of that removed heat actually reaches the goods. Two freezers can draw the same 1.2 kW while one holds its load at temperature and the other spills cold air into the aisle. Comparing only kilowatt-hours would call them equal — or prefer the one that cools nothing, because a case that fails to cool draws less power.")
para("A defensible cooling-efficiency measure therefore needs four kinds of quantities. First, the useful cooling delivered to the protected space — the heat removed from the goods zone per unit time, not the electricity. Second, the resource paid for — electrical power, and water for evaporative devices, integrated over the operating window. Third, the share of the delivered cooling that stays where it is needed, i.e. the boundary loss at the opening (cold-air spill, warm-air infiltration, radiation). Fourth, who benefits — the number of occupants actually inside the protected envelope. The first two give a ratio; the last two decide whether that ratio describes a real benefit or a leak.")
para("Energy alone fails on three counts. It ignores the boundary: the same compressor power can deliver different useful cooling depending on how much cold air escapes. It ignores the medium: a fan moves air and can feel cooler while lowering no air temperature at all, whereas an evaporative cooler lowers temperature but adds humidity, and in humid air its useful effect is small. It ignores the beneficiary: cooling an empty platform is not the same service as cooling forty waiting passengers.")
para("The transit shelter is the same problem with the roles changed. In the freezer, cold is produced inside a box and leaks out through the opening; in the semi-open shelter, cooling is produced inside a roofed space and leaks out through the sides. The opening is the boundary in both cases. The goods become people: what matters is the apparent temperature experienced by someone waiting and how many people are inside the cooled jet. One further distinction matters for the transit case and is often skipped: the platform is not the waiting zone. A Phoenix platform is about 425 m², but passengers wait only in the shaded boarding zone, which we model as 120 m²; the coverage metric must use the waiting zone, or a single unit appears to “cover the platform” when it does not.")
para("This mapping produces the six quantities used in Section 3. Eqs. 1–2 describe how much cooling reaches the zone and how much a person feels; Eq. 3 divides the covered, occupancy-weighted cooling by electrical power; Eqs. 4–5 price the resources; Eq. 6 combines safety, benefit, cost and environment and is compared with a do-nothing baseline. The answer to Q1 is therefore that efficiency should not depend on energy use alone: it should be judged by the useful cooling delivered to the protected space per unit of resource, weighted by how many occupants it actually covers, and constrained by thermal safety and the water–carbon externality.")
doc.add_page_break()

# ---------------------------------------------------------------- section 2
h1("2. Assumptions and Justifications")
para("We adopt six assumptions. Each is grounded in thermodynamics or standards, or is explicitly flagged as an assumption with a sensitivity range; the data register in Appendix A gives the status of every parameter.")
assumptions = [
    ("Assumption 1 — Quasi-steady peak operation.",
     "During the peak summer window (11:00–19:00, 8 h/day) units run at rated capacity and the waiting zone reaches a quasi-steady thermal and aerodynamic state. Semi-open shelters have negligible thermal mass and continuous air exchange, so the jet plume stabilises within minutes."),
    ("Assumption 2 — Isenthalpic adiabatic humidification.",
     "Air through the wetted medium follows a constant wet-bulb line, so the dry-bulb drop is bounded by ε(T_db − T_wb), with ε = 0.80 (sensitivity 0.70–0.90). T_wb is the psychrometric wet bulb at the local surface pressure (950 hPa Phoenix, 1,000 hPa Hong Kong)."),
    ("Assumption 3 — Linear cold-air boundary escape.",
     "A constant fraction γ of the generated sensible cooling escapes: γ = 0.55 for three-sided bus shelters and 0.30 for roofed rail platforms. The ranges (45–65% and 30–40% loss) come from urban ventilation studies; γ is a lumped parameter and Section 5 sweeps it from 0.20 to 0.75."),
    ("Assumption 4 — Jet mixing and uniform occupancy.",
     "The zone velocity is v_eff = v_amb + κ(Q_air/A_cov), with κ = 45 (dimensionless momentum amplification, sensitivity 30–60); κ is a lumped jet-mixing coefficient, not a physical velocity; 45 is a literature-informed assumption (sensitivity 30–60), and it is not calibrated in this study. Commuters are uniformly distributed, so beneficiaries scale with φ = min(1, n·A_cov/A_waiting), with N_eff = 6 (bus) and 45 (rail design capacity). The 6-person figure is a peak-hour estimate, not a headcount: 384 weekday boardings in both directions (208 + 176), a 12–15% peak-hour share (an assumption, not a measurement), a 16-hour analysis window inside a service day of about 20 h, and a 6-minute mean wait on a 12-minute headway give N ≈ 4.6–5.8; we take the upper end, 6. Occupancy scales η but cancels in E (Section 5.7)."),
    ("Assumption 5 — Commercial tariffs and straight-line depreciation.",
     "Capital costs depreciate linearly over L = 5–7 years and annual maintenance is r_om = 3–8% of capital. Energy uses the latest local tariffs (Phoenix 2024 APS E-32 with demand [5]; Hong Kong 2026 CLP [6]) and water the City of Phoenix 2024 card and the Hong Kong WSD schedule; the 2026 Phoenix scenario and the Hong Kong 50% water concession are tested separately."),
    ("Assumption 6 — Shaded conditions and an approximate heat index.",
     "Both venue types provide overhead shading, so the heat index is the proxy WBGT ≈ 0.7 T_wb + 0.3 T_db (ISO 7243 no-solar-load form [3], with the natural wet bulb approximated by the psychrometric wet bulb and the globe temperature by the dry-bulb). This is an index approximation, not a compliance measurement; the 33 °C reference (ISO 7243 115 W) is the graded benchmark (Section 3.7), with 30 °C as a vulnerable-population screen and 28 °C as a stress test. Black-globe offsets of +3 and +6 K are tested in Section 5."),
]
for title, body in assumptions:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(title); set_font(r, 10, True)
    r = p.add_run(" " + body); set_font(r, 10)

para("Table 1. Summary of assumptions and supporting equations.", 9, italic=True)
table(["Assumption", "Equations", "Basis / status"], [
    ["1 Quasi-steady peak", "1–6", "Design-day method; assumption"],
    ["2 Isenthalpic humidification", "1–2", "Moist-air thermodynamics; ε=0.80 assumed"],
    ["3 Cold-air escape γ", "2–3, 6", "Urban ventilation ranges; lumped; swept"],
    ["4 Jet mixing, occupancy", "2–3", "κ dimensionless, assumed 45; N_eff assumed"],
    ["5 Tariffs and depreciation", "4–5", "APS/CLP/WSD; L, r_om assumed"],
    ["6 Shaded proxy WBGT", "6", "Approximate index; 33 °C reference, 30/28 °C screens"],
], widths=[5.6, 3.0, 7.4], size=8)
doc.add_page_break()

# ---------------------------------------------------------------- section 3
h1("3. Mathematical Model")
figure("docs/figures/fig1_system.png", "Figure 1. System boundary and equation couplings. Left: semi-open venue cross-section with the cold jet, lateral escape γ and coverage φ. Right: the Eq. 1→2→3→6 chain with Eq. 4 and Eq. 5 as parallel inputs to Eq. 6, grouped into thermodynamics, economics/externality and safety/decision.")
para("Figure 1 is the roadmap for this section: the left panel fixes the boundary and the loss terms; the right panel shows how the six equations combine into the decision score E.")
h2("3.1 Parameter Baselines")
para("Table 2A lists the four commercial benchmark units. Status codes: S = sourced, D = derived, A = assumption, U = unverified. The 36-inch drum fan has no product source and is treated as a hypothetical benchmark [11]. Water use is not listed as a free parameter: it is derived from the energy balance in Eq. 4 (Section 3.5) and the values in the table are the resulting design-point rates.")
para("Table 2A. Candidate commercial cooling units (design-point water derived from Eq. 7).", 9, italic=True)
tab2a = []
for eq, name in (("MC37V", "Hessaire MC37V"), ("MC61V", "Hessaire MC61V"), ("Porta", "Portacool Jetstream 220"), ("Fan", 'Drum fan 36"')):
    e = R.EQUIPMENT[eq]
    phx = R.calc("PHX", "bus", eq, 1)["Vw"]
    hk = R.calc("HK", "bus", eq, 1)["Vw"]
    tab2a.append([name, f"{e['P']:.3f}", f"{e['CFM']:,}", f"{e['A']:.0f}", f"{e['eps']:.2f}",
                  f"{phx:.1f} / {hk:.1f}", f"{e['C']}", f"{e['L']}", f"{e['r']*100:.0f}%"])
table(["Unit", "P (kW)", "CFM", "A_cov (m²)", "ε", "V_w PHX/HK (L/h)", "C_cap (USD)", "L (yr)", "r_om"], tab2a,
      widths=[3.6, 1.5, 1.5, 1.8, 1.2, 2.9, 1.9, 1.2, 1.3], size=7.5)

para("Table 2B. City boundary conditions.", 9, italic=True)
table(["Parameter", "Symbol", "Unit", "Phoenix", "Hong Kong", "Status"], [
    ["Dry-bulb / RH", "T_db, RH", "°C, %", "41.0, 18", "31.7, 77", "D/A"],
    ["Wet bulb (pressure-corrected)", "T_wb", "°C", "21.8", "28.2", "D"],
    ["Surface pressure", "p_s", "hPa", "950", "1,000", "D"],
    ["Ambient wind", "v_amb", "m/s", "1.8", "1.5", "A"],
    ["Electricity", "p_elec", "USD/kWh", "0.1595", "0.1923", "D"],
    ["Water (+sewage)", "p_water", "USD/m³", "2.0766", "0.9615", "D"],
    ["Grid carbon factor", "EF_grid", "kg CO₂e/kWh", "0.303", "0.390", "A/S"],
    ["Baseline water stress", "BWS_raw", "—", "2.482", "0.179", "S"],
    ["Peak operating hours", "H_yr", "h/yr", "1,440", "1,200", "A"],
], widths=[6.0, 2.2, 2.6, 2.2, 2.2, 1.4], size=8)

para("Table 2C. Venue geometry: whole platform, modelled waiting zone and usage.", 9, italic=True)
table(["Venue", "A_platform (m²)", "A_waiting (m²)", "γ", "N_eff", "Basis"], [
    ["Bus shelter", "20", "15", "0.55", "6", "D/A: 2 m × 10 m canopy measured at a semi-open bus stop (Kyogoku & Takebayashi 2023); 15 m² modelled waiting area"],
    ["Phoenix rail platform", "425", "120", "0.30", "45", "D/A: Valley Metro design criteria 85.34 m × 4.98 m; 120 m² shaded boarding zone; 45 is design capacity, actual ≈6 at 384 boardings (5.7)"],
    ["Hong Kong rail platform", "128", "128", "0.30", "45", "D: scaled from the Open3Dhk 3D map ≈ 32 m × 4 m"],
], widths=[3.8, 2.6, 2.6, 1.2, 1.2, 6.0], size=7.5)

h3("3.1.1 Transit Network Basis")
para("The Phoenix case is the 12th St & Washington/Jefferson Station (384 weekday boardings [8]); the Hong Kong case is the Siu Hong (兆康) stop, stop ID 100, 22.4120 N, 113.9783 E, served by seven routes [10]; the weather and stop data are Siu Hong's, while the platform geometry is a representative 32 × 4 m side-platform measurement applied to it, so this is a scenario application at the named stop rather than a survey (§5.5). Valley Metro Rail's 2023 NTD profile [7] reports 71 facilities and 29,846 average weekday unlinked trips; the 71 figure is a facility count, not a station count (about 38 stations in 2024), so network costs in Section 6 use 38 stations. The 12th St & Washington/Jefferson profile [8] reports 384 weekday boardings (208 + 176) and 27,462 full-system weekday boardings. Valley Metro's design criteria set a 280 ft (85.3 m) calculated platform with a 16 ft 4 in (4.98 m) minimum centre-platform width, a peak 12-minute boarding/alighting design load at 7 ft² (0.65 m²) per person, and a 1.0% cross slope (Ch. 6.3.1–6.3.5) [12]. The South Central Extension/Downtown Hub opened on 7 June 2025 with eight new stations and a 12-minute weekday headway [13] (20 minutes after 19:00; 15/20 minutes on Saturday; 20 minutes on Sunday; 365 days, about 20 h/day). The 2024 count of 38 stations is kept for the network-cost illustration so that station count, tariffs and ridership share the same 2024 basis; the 2026 system has about 46 stations. Hong Kong's Light Rail has 68 unique stops on 11 lines [10], with 439,200 daily journeys in March 2026 [9]; five routes (505, 507, 614, 614P, 751) run 6–18 min peak headways. 149 LRVs and 3.90 million daily bus journeys are marked U because the PDF text layer is unreliable and the figures need a page-level check.")

h2("3.2 Thermodynamic Cooling Constraint (Eq. 1)")
formula([("ΔT", "var"), ("phys", "sub"), (" = min(", "op"), ("ΔT", "var"), ("nom", "sub"),
         (", ε(", "op"), ("T", "var"), ("db", "sub"), (" − ", "op"),
         ("T", "var"), ("wb", "sub"), (").   ", "op")])
para("T_wb is solved from the psychrometric relation at surface pressure p_s [1]: e_s(T_wb) − γ_p(T_db − T_wb) = e_amb, where γ_p = 1.006 p_s /(0.622 × 2,450) hPa/K. At 41 °C/18% and 950 hPa this gives 21.8 °C; at 31.7 °C/77% and 1,000 hPa it gives 28.2 °C. For pure fans ε = 0 and ΔT_phys = 0.")

h2("3.3 Apparent Temperature and Jet Velocity Coupling (Eq. 2)")
formula([("ΔT", "var"), ("eff", "sub"), (" = ", "op"), ("AT", "var"), ("(", "op"),
         ("T", "var"), ("db", "sub"), (", ", "op"), ("e", "var"), ("amb", "sub"),
         (", ", "op"), ("v", "var"), ("amb", "sub"), (") − ", "op"), ("AT", "var"),
         ("(", "op"), ("T", "var"), ("zone", "sub"), (", ", "op"), ("e", "var"), ("zone", "sub"),
         (", ", "op"), ("v", "var"), ("eff", "sub"), ("),   ", "op"),
         ("AT", "var"), ("(", "op"), ("T", "var"), (", ", "op"), ("e", "var"), (", ", "op"),
         ("v", "var"), (") = ", "op"), ("T", "var"), (" + 0.33", "op"), ("e", "var"),
         (" − 0.70", "op"), ("v", "var"), (" − 4.00.   ", "op"), (" [2]", "op")])
para("T_zone = T_db − (1−γ)ΔT_phys; e_zone = min(e_s(T_zone), e_amb + 0.665(1−γ)ΔT_phys); v_eff = v_amb + κ(Q_air/A_cov), with Q_air = CFM × 1.699/3600 m³/s. Rectangular jets decay more slowly than circular ones, and the rate depends on the nozzle aspect ratio and on the sidewalls [17]; following von Glahn's rectangular-plume model [16], the low-speed centreline decay can be written u(x) ≈ C·u0·√A0 / x, with A0 the outlet area and C ≈ 2.4. For the 3,100 CFM unit (Q = 1.463 m³/s, A0 ≈ 0.45 m² assumed from the grille envelope, u0 = 3.25 m/s, q = Q/A_cov = 0.0166 m/s) this gives κ(x) = u(x)/q ≈ 315/x: 157 at 2 m, 79 at 4 m, 52 at 6 m and 39 at 8 m. κ = 45 therefore corresponds to a throw of about 7.0 m, and using one value for both venues assumes the same throw distance: a 3–4 m bus shelter implies κ ≈ 80–105, a 6–8 m platform κ ≈ 39–52. We keep κ = 45 as the design value and test 30–60 in Section 5.1; because the bus-shelter estimate (80–105) lies outside that range, Section 5.1 also reports κ = 80 and 105, where the fan overtakes the evaporative unit above κ ≈ 92. No site calibration is available in this study.")
para("The humidity penalty is measured, not hypothetical. Field tests of misting at a semi-open bus stop lowered air temperature by a few tenths of a degree to about 1 °C while adding 0.5–1 g/kg of absolute humidity under low wind [15]; whether that feels cooler depends on the ratio of the two changes, which is exactly what the apparent-temperature form in Eq. 2 evaluates.")

h2("3.4 Spatial Cooling Efficiency (Eq. 3)")
formula([("η", "var"), (" = (", "op"), ("φ", "var"), (" · ", "op"), ("N", "var"), ("eff", "sub"),
         (" · ", "op"), ("ΔT", "var"), ("eff", "sub"), (") / (", "op"), ("n", "var"), (" · ", "op"),
         ("P", "var"), ("elec", "sub"), ("),   ", "op"), ("φ", "var"), (" = min(1, ", "op"),
         ("n", "var"), ("·", "op"), ("A", "var"), ("cov", "sub"), ("/", "op"), ("A", "var"),
         ("waiting", "sub"), (").   ", "op")])
para(f"η is a human-centric total (persons·°C per kW), not a per-person equipment efficiency. Because the denominator is the waiting zone rather than the platform, η and φ answer “how much of the area where people actually wait is cooled”, which is the quantity the operator controls.")

h2("3.5 Annualised Life-Cycle Cost (Eq. 4)")
formula([("LCC", "var"), ("annual", "sub"), (" = (1/", "op"), ("L", "var"), ("life", "sub"),
         (" + ", "op"), ("r", "var"), ("om", "sub"), (")·", "op"), ("n", "var"), ("·", "op"),
         ("C", "var"), ("cap", "sub"), (" + ", "op"), ("H", "var"), ("yr", "sub"), ("·(", "op"),
         ("n", "var"), ("·", "op"), ("P", "var"), ("elec", "sub"), ("·", "op"), ("p", "var"),
         ("elec", "sub"), (" + (", "op"), ("n", "var"), ("·", "op"), ("V", "var"), ("w", "sub"),
         ("/1000)·", "op"), ("p", "var"), ("water", "sub"), (").   ", "op")])
para("V_w is not a free input. For an adiabatic evaporative process the water flow follows from the same energy balance that produces the temperature drop:")
formula([("V", "var"), ("w", "sub"), (" = 3600 · ", "op"), ("ṁ", "var"), ("da", "sub"),
         (" · ", "op"), ("c", "var"), ("p", "sub"), (" · ", "op"), ("ΔT", "var"), ("phys", "sub"),
         (" / ", "op"), ("L", "var"), ("v", "sub"), (",   ", "op"), ("ṁ", "var"), ("da", "sub"),
         (" = ", "op"), ("Q", "var"), ("air", "sub"), ("·", "op"), ("ρ", "var"), ("da", "sub"),
         (",   ", "op")])
para("with c_p = 1.006 kJ/(kg·K), L_v = 2,450 kJ/kg and ρ_da = p/(287·T). At the Phoenix design point a 3,100 CFM unit with an 11 °C drop requires about 25 L/h; at the Hong Kong design point the smaller drop requires about 6.9 L/h. Manufacturer tank/run-time rates (10.6–18.2 L/h) are treated as a sensitivity, because they are refill rates rather than measurements of evaporated water.")

h2("3.6 Water–Carbon Externality (Eq. 5)")
formula([("I", "var"), ("env", "sub"), (" = ", "op"), ("α", "var"), ("c", "sub"), ("(", "op"),
         ("E", "var"), ("CO2", "sub"), ("/", "op"), ("E", "var"), ("CO2,max", "sub"), (") + ", "op"),
         ("α", "var"), ("w", "sub"), ("(", "op"), ("W", "var"), ("eq", "sub"), ("/", "op"),
         ("W", "var"), ("eq,max", "sub"), ("), with ", "op"), ("α", "var"), ("c", "sub"), (" = ", "op"),
         ("α", "var"), ("w", "sub"), (" = 0.50; ", "op"), ("E", "var"), ("CO2", "sub"), (" = ", "op"),
         ("n", "var"), ("·", "op"), ("P", "var"), ("elec", "sub"), ("·", "op"), ("H", "var"), ("yr", "sub"),
         ("·", "op"), ("EF", "var"), ("grid", "sub"), ("; ", "op"), ("W", "var"), ("eq", "sub"), (" = (", "op"),
         ("n", "var"), ("·", "op"), ("V", "var"), ("w", "sub"), ("/1000)·", "op"), ("H", "var"), ("yr", "sub"),
         ("·", "op"), ("BWS", "var"), ("raw", "sub"), (".   ", "op")])
para("Normalisers are computed separately for the bus shelters and for the rail platforms, over all one- and two-unit deployments of the four units (the same deployment set for both venue types). E is therefore comparable within a venue type, not across venue types; the paper never ranks a bus option against a rail option.")

h2("3.7 Safety Proxy and Decision Score (Eq. 6)")
formula([("E", "var"), (" = ", "op"), ("w", "var"), ("1", "subv"), ("·", "op"), ("S", "var"),
         ("safe", "sub"), (" + ", "op"), ("w", "var"), ("2", "subv"), ("·", "op"), ("B", "var"),
         (" − ", "op"), ("w", "var"), ("3", "subv"), ("·", "op"), ("LCC", "var"), ("̃", "op"),
         (" − ", "op"), ("w", "var"), ("4", "subv"), ("·", "op"), ("I", "var"), ("env", "sub"),
         (".   ", "op")])
para("WBGT_proxy = 0.7 T_wb,zone + 0.3 T_zone; S_safe(W) = clamp((35 − W)/6, 0, 1); B = φ·N_eff·ΔT_eff / B_max; LCC̃ = LCC/LCC_max; baseline weights (w1,w2,w3,w4) = (0.30, 0.30, 0.20, 0.20).")
para("OSHA and CCOHS define the indoor index as WBGT = 0.7 T_nwb + 0.3 T_g [19,14], where T_nwb is the natural wet bulb, which responds to air speed. Our proxy replaces T_nwb with the psychrometric wet bulb and T_g with the dry bulb, so it is wind-blind by construction; Section 5.6 gives a sensitivity and the fan-beneficial limit.")
para("Two changes from a conventional weighted score matter. First, the safety term is graded over 29–35 °C with the 33 °C reference line at one third, so cooling below 33 °C still earns credit instead of saturating at zero cost; the 29–35 °C window is a −4/+2 K band around the resting reference, and its endpoints are a design choice tested at 30 °C and 28 °C in Section 5.7. Second, safety is population-weighted: S_safe = φ·S_safe(W_zone) + (1−φ)·S_safe(W_ambient), so the share of occupants outside the jet is not ignored. Before normalisation the benefit term is proportional to persons, so a platform and a shelter cannot be compared on E; inside a venue the normaliser removes the occupancy scale, and η carries the absolute service level.")
para("A do-nothing option (φ = 0, ΔT = 0, zero cost) is evaluated with the same normalisers and compared with every configuration. E ranks units and configurations within a venue; it is not a compliance test, and the WBGT proxy is not ISO 7243 certification [3].")


# ---------------------------------------------------------------- section 4
h1("4. Model Application and Results (Q2–Q4)")
h2("4.1 Bus Stop Shelter Evaluation (Q2a)")
nd_bus = nd_E("PHX", "bus")
para(f"Table 3 reports the Q2a comparison at the Phoenix bus shelter. System A (0.25 kW fan) is the most efficient (η = {T3[0]['eta']:.2f} persons·°C/kW, E = {T3[0]['E']:.4f}), System B has E = {T3[1]['E']:.4f} and System C E = {T3[2]['E']:.4f}; the A/C efficiency ratio is {T3[0]['eta']/T3[2]['eta']:.1f}×. The do-nothing baseline scores {nd_bus:.4f}: it is below System A but above System B ({T3[1]['E']:.4f}) and System C ({T3[2]['E']:.4f}). Only System A wins the efficiency comparison; B and C score below doing nothing, so the Q2a ranking rests on a genuine comparison. This is an efficiency result, not a deployment instruction at 41 °C: CBE's fan guidance excludes conditions above about 40 °C for heat-stress relief, and the real-unit comparison in Table 5 puts the 0.25 kW MC37V ahead of the drum fan at this shelter (E = 0.4806 vs 0.3705). Systems A–C are the prompt's illustrative units; Tables 2A and 5 use commercial units, and the two sets are not ranked against each other. This ranking treats the prompt's 5/8 °C as outlet ratings; if they are read as shelter effects, B's E rises to 0.368 but A's 0.399 still leads, so the Q2a ranking is robust to this reading (Section 5.7). System A's cooled-zone proxy WBGT is {T3[0]['wbgt']:.2f} °C, well below the 33 °C reference. The ranking is insensitive to the added assumptions: System A stays ahead of B for fan airflow above about 300 CFM and for capital up to $3,000.")
para("Table 3. Q2a comparison (Phoenix bus shelter, 33 °C, per-venue normalisers).", 9, italic=True)
table(["System", "P (kW)", "ΔT_eff (°C)", "φ", "η (persons·°C/kW)", "LCC (USD/yr)", "WBGT proxy (°C)", "E"], [
    [r["eq"], f"{r['P']:.3f}", f"{r['dT']:.3f}", f"{r['phi']:.3f}", f"{r['eta']:.2f}", f"{r['lcc']:.2f}", f"{r['wbgt']:.2f}", f"{r['E']:.4f}"] for r in T3
], widths=[1.3, 1.5, 1.8, 1.1, 3.0, 2.2, 2.2, 1.5], size=8)
para("Table 3b. Assumed Q2a parameter set: A 0.25 kW / 2,250 CFM / ΔT_nom 0 / C $250 / L 7 / r 3%; B 1.2 kW / 917 CFM / ΔT_nom 5 / C $750 / L 5 / r 8%; C 2.5 kW / 1,031 CFM / ΔT_nom 8 / C $1,277 / L 5 / r 8%. A_cov = A_waiting = 15 m², γ = 0.55, N_eff = 6.", 8.5)
para("Note: the “Energy Use” values in Requirement 2a are power ratings in kW (not kWh per hour); annual energy is obtained as P_elec × H_yr.", 9, italic=True)
para("The problem states that the fan feels up to 3 °C cooler; we do not impose that number as an air-temperature drop, because a fan lowers no air temperature. Eq. 2 converts its air speed into felt cooling instead, which gives 2.23 °C at the Phoenix design point — inside the stated “up to 3 °C” band.")
para("Figure 2 summarises the Q2a paradox and the Q2b scaling: the left panel shows why extra power buys little extra cooling, and the right panel shows when a second unit pays.")
figure("docs/figures/fig2_q2a_q2b.png", "Figure 2. Q2a efficiency paradox and Q2b scaling. Left: Systems A/B/C, bars = ΔT_eff, line = η. Right: 1× vs 2× deployment of MC37V, MC61V and Portacool at a 120 m² Phoenix waiting zone, annotated with E and φ.")

h2("4.2 Rail Platform and Multi-Unit Scaling (Q2b)")
phx61 = find(T4, "PHX", "rail", "MC61V", 1)
phx37 = find(T4, "PHX", "rail", "MC37V", 1)
phx2 = find(T4, "PHX", "rail", "MC37V", 2)
porta1 = find(T4, "PHX", "rail", "Porta", 1)
porta2 = find(T4, "PHX", "rail", "Porta", 2)
hk37 = find(T4, "HK", "rail", "MC37V", 1)
hk61 = find(T4, "HK", "rail", "MC61V", 1)
hkfan = find(T4, "HK", "rail", "Fan", 1)
hk2fan = find(T4, "HK", "rail", "Fan", 2)
nd_rail_phx = nd_E("PHX", "rail")
para(f"Table 4 compares one- and two-unit deployments on the same normalisers and against the do-nothing baseline ({nd_rail_phx:.4f}). One MC61V covers the whole 120 m² waiting zone (φ = {phx61['phi']:.3f}) and scores E = {phx61['E']:.4f}; two MC37V also reach full coverage but cost about twice as much and score {phx2['E']:.4f}. Under this base two units are uniformly worse: 2× MC37V scores {phx2['E']:.4f} against {phx37['E']:.4f} for one; 2× Portacool {porta2['E']:.4f} against {porta1['E']:.4f}; 2× MC61V {find(T4,'PHX','rail','MC61V',2)['E']:.4f} against {phx61['E']:.4f}.")
para(f"In Hong Kong the rail platform has no deployment case: 1× MC37V ({hk37['E']:.4f}) is only marginally ahead of 1× MC61V ({hk61['E']:.4f}) and the fan ({hkfan['E']:.4f}), and all three are at or below the do-nothing baseline ({nd_E('HK','rail'):.4f}); MC37V covers only φ = {hk37['phi']:.3f} of the 128 m² platform. Two fans score {hk2fan['E']:.4f}, below one MC37V, because the extra unit doubles capital and carbon-heavy power without improving safety.")
para("Q2b revises the Q2a model in three ways. Q2a assumed one unit that covers a small shelter completely, but a rail waiting zone is 120 m² in Phoenix and 128 m² in Hong Kong, so coverage must be explicit. First, φ = min(1, n·A_cov/A_waiting) gives partial credit for partial coverage instead of assuming φ = 1. Second, the normalisers (B_max, LCC_max, E_CO2,max, W_eq,max) are computed per venue type, so E compares bus with bus and rail with rail instead of mixing a 6-person shelter with a 45-person platform. Third, safety is population-weighted, S_safe = φ·S(W_zone) + (1−φ)·S(W_ambient), so occupants outside the jet are counted. The revision changes the answer. With Q2a's full-coverage assumption the one- versus two-unit question is only a cost question; with explicit coverage, one MC61V covers the zone (φ = 1.000, E = 0.4026) while two MC37V cover it at higher cost (LCC $487.60 vs $397.41, E = 0.3635), and no second unit pays in this base (2× Portacool 0.2834 vs 1× 0.3042).")
para("Table 4. One- vs two-unit deployment at a rail platform (33 °C).", 9, italic=True)
table(["City", "Equipment", "n", "φ", "ΔT_eff (°C)", "LCC (USD/yr)", "WBGT proxy (°C)", "S_safe", "E"], [
    [r["city"], r["eq"], r["n"], f"{r['phi']:.3f}", f"{r['dT']:.3f}", f"{r['lcc']:.2f}", f"{r['wbgt']:.2f}", f"{r['S_safe']:.3f}", f"{r['E']:.4f}"] for r in T4
], widths=[1.2, 1.7, 0.8, 1.3, 1.8, 2.1, 2.0, 1.4, 1.5], size=7.5)
unc = (1 - hk37["phi"]) * 45
para(f"Table 4b makes the coverage assumption explicit for the Hong Kong platform. With 1× MC37V, φ = {hk37['phi']:.3f}, so {hk37['phi']*45:.0f} of the 45 waiting occupants are inside the cooled jet (proxy WBGT {hk37['wbgt']:.2f} °C) and {unc:.0f} are outside it, where the shaded ambient proxy is {hk37['wbgt_amb']:.2f} °C. At 31.7 °C/77% both zones are below the 33 °C limit and even below the 30 °C screen (28.69 vs 29.27 °C), so the coverage gap is a comfort gradient rather than a safety failure; 1× MC61V buys full coverage at higher cost, not safety.")
para("Table 4b. Covered vs uncovered exposure, Hong Kong platform, 1× MC37V.", 9, italic=True)
table(["Zone", "Persons", "WBGT proxy (°C)", "≤30 °C screen?"], [
    [f"Covered zone (φ = {hk37['phi']:.3f})", f"{hk37['phi']*45:.0f}", f"{hk37['wbgt']:.2f}", "yes"],
    [f"Uncovered zone (1 − φ)", f"{unc:.0f}", f"{hk37['wbgt_amb']:.2f}", "yes"],
], widths=[7.0, 2.4, 3.2, 3.2], size=8)

h2("4.3 Cross-Climate Comparison (Q3)")
para(f"Table 5 gives the 16-scenario matrix; E is comparable within each venue type. In Phoenix, evaporative cooling remains the best option in both venues: MC37V in bus shelters (E = {find(T5,'PHX','bus','MC37V',1)['E']:.4f}) and MC61V on platforms ({find(T5,'PHX','rail','MC61V',1)['E']:.4f}). In Hong Kong the bus shelter favours the drum fan ({find(T5,'HK','bus','Fan',1)['E']:.4f} vs {find(T5,'HK','bus','MC37V',1)['E']:.4f}), while the platform is essentially tied with doing nothing and only marginally ahead of MC61V ({find(T5,'HK','rail','MC37V',1)['E']:.4f} vs {find(T5,'HK','rail','MC61V',1)['E']:.4f}). The hourly run is time-dependent: the fan wins 88% of bus-shelter device-hours but MC37V wins 98% of the hottest bus hours (Section 5.2). The blanket statement that evaporative cooling fails in humid cities is therefore too strong: the climate effect is technology- and venue-specific.")
para("Which characteristics contribute most to efficient cooling? With the venue fixed, η is linear in coverage φ and in the number of beneficiaries N_eff, linear in the felt temperature drop ΔT_eff, and inversely proportional to electrical power. Three comparisons order the drivers. First, coverage and occupancy: a unit at φ = 1.000 is worth 36% more η than the same unit at φ = 0.733, and the 45-person platform has a 7.5× larger η than the 6-person shelter. Occupancy N_eff enters the benefit and its normaliser together, so it cancels in E: lowering N from 45 to 6 cuts η from 862 to 115 persons·°C/kW but leaves E at 0.4015 (MC37V) and 0.4026 (MC61V). Coverage does not cancel, because the normaliser is set by the best-covered option. Second, climate: at Phoenix's 41 °C / 18% the wet-bulb depression allows 4.4 °C of felt cooling in a shelter and 6.5 °C on a platform, whereas at Hong Kong's 31.7 °C / 77% the same units deliver 1.5–2.0 °C, about three times less. Third, device power: moving from 0.25 kW to 2.5 kW multiplies power tenfold but raises ΔT_eff only 1.7-fold, so η falls 5.8-fold. Coverage therefore dominates the E ranking, climate decides whether evaporative cooling works at all, and power is the least productive lever.")
para(f"At the 33 °C reference the Phoenix cooled-zone proxy is 25.3–26.5 °C and the uncovered platform proxy is {find(T5,'PHX','rail','MC37V',1)['wbgt_amb']:.2f} °C, so the exposure is modest. In Hong Kong the cooled-zone proxy is 28.7–29.3 °C and the uncovered share is {find(T5,'HK','rail','MC37V',1)['wbgt_amb']:.2f} °C: both are below the 33 °C limit and even below a 30 °C vulnerable-population screen, so cooling is a comfort service rather than a safety rescue. At 28 °C no Hong Kong option clears the stricter reference, which is reported as an exposure stress test rather than a compliance result.")
para("Table 5. Sixteen-scenario cross-climate matrix (33 °C).", 9, italic=True)
table(["ID", "City", "Venue", "Equipment", "ΔT_eff", "φ", "η", "LCC", "I_env", "WBGT proxy", "E"], [
    [f"SC-{i:02d}", r["city"], r["venue"], r["eq"], f"{r['dT']:.3f}", f"{r['phi']:.3f}", f"{r['eta']:.2f}",
     f"{r['lcc']:.2f}", f"{r['I_env']:.4f}", f"{r['wbgt']:.2f}", f"{r['E']:.4f}"] for i, r in enumerate(T5, start=1)
], widths=[1.1, 1.1, 1.1, 1.6, 1.4, 1.2, 1.5, 1.7, 1.3, 1.7, 1.4], size=7.5)

para("Figure 3 shows the crossover at both design days: at 41 °C the rail crossover is 79.7%, while at Hong Kong's own 31.7 °C the rail crossover falls to 76.7%, so 77% is above it and the fan delivers slightly more felt cooling; at the bus shelter the crossover is 65.1%, well below 77%.")
figure("docs/figures/fig3_rh_crossover.png", "Figure 3. RH crossover at the two design days. (a) Phoenix 41 °C: bus crossover 69.6%, rail 79.7%. (b) Hong Kong 31.7 °C: bus 65.1%, rail 76.7%. Dotted lines mark the design-day RH (18% and 77%); the fan line is 2.081 °C.")

h2("4.4 Multi-Objective Trade-Offs (Q4)")
para(f"On the revised environmental baseline the fan has the lowest I_env in Phoenix ({find(T5,'PHX','bus','Fan',1)['I_env']:.4f}) but not in Hong Kong ({find(T5,'HK','bus','Fan',1)['I_env']:.4f} > MC37V {find(T5,'HK','bus','MC37V',1)['I_env']:.4f}), because Hong Kong's water stress is low (BWS 0.179 [4]) and the fan's higher power dominates the carbon term. 'Zero water = lower environmental burden' is therefore false in Hong Kong under Eq. 5; the claim should be limited to water consumption, not to the composite index.")
para("Figure 4 plots the 16 scenarios as eight cost–externality pairs; the two fan options nearly coincide near $132, so the inset separates them.")
figure("docs/figures/fig4_pareto.png", "Figure 4. LCC vs I_env trade-off. The 16 scenarios collapse to eight distinct cost–externality pairs; shape = city, fill = WBGT proxy at the 33 °C reference; the inset separates the two fan points that nearly coincide near $132. Labels mark the Phoenix points.", width_cm=12.2)
para(f"In Phoenix, MC61V has the highest I_env ({find(T5,'PHX','rail','MC61V',1)['I_env']:.4f}) and the highest water use, and 1× MC61V's LCC is ${find(T5,'PHX','rail','MC61V',1)['lcc']:.2f} vs ${find(T5,'PHX','rail','MC37V',1)['lcc']:.2f} for 1× MC37V. The trade-off is coverage vs cost/water, not cooling magnitude: all evaporative units deliver about 4.4 °C in bus shelters and 6.5 °C on platforms. The memorandum in Section 6.1 turns this into a decision rule.")


# ---------------------------------------------------------------- section 5
h1("5. Sensitivity Analysis and Model Evaluation")
h2("5.1 Parameter, Policy and Decision-Weight Sensitivity")

g_fix = R.norm([R.calc(c, v, e, n) for c in R.CITY for v in R.VENUE for e in R.EQUIPMENT for n in (1, 2)])
R.KAPPA = 60.0
e60_37 = R.score(R.calc("HK", "rail", "MC37V", 1), g_fix, threshold=33.0)[0]
e60_fan = R.score(R.calc("HK", "rail", "Fan", 1), g_fix, threshold=33.0)[0]
R.KAPPA = 45.0

R.WATER_MODE = "manufacturer"
em_37 = R.score(R.calc("HK", "rail", "MC37V", 1), g_fix, threshold=33.0)[0]
R.WATER_MODE = "balance"

para(f"Table 6 lists the winning unit for each COO weight profile. Under Balanced and Safety, Phoenix chooses MC37V at the bus shelter and MC61V on the platform; Hong Kong chooses the fan at the bus shelter and MC37V on the platform. Under Cost, Phoenix switches to MC37V on the platform and Hong Kong chooses the fan on both; under Eco, Phoenix stays with MC37V on both and Hong Kong uses the fan at the bus shelter and MC37V on the platform.")
para("Table 6. Best device within each COO weight profile, shown against the do-nothing score (33 °C).", 9, italic=True)
t6rows = []
for name in ("Balanced", "Safety", "Cost", "Eco"):
    row = [name]
    for c, v in (("PHX", "bus"), ("PHX", "rail"), ("HK", "bus"), ("HK", "rail")):
        eq, sc = T6_30[(name, c, v)]
        row.append(f"{eq} ({sc:.3f})")
    w = R.PROFILES[name]
    phx_none = R.score(R.no_device("PHX", "bus"), G5, w)[0]
    hk_none = R.score(R.no_device("HK", "bus"), G5, w)[0]
    row += [f"{phx_none:.3f}", f"{hk_none:.3f}"]
    t6rows.append(row)
table(["Profile", "Phoenix bus", "Phoenix rail", "HK bus", "HK rail", "PHX none", "HK none"], t6rows,
      widths=[1.9, 2.7, 2.7, 2.6, 2.6, 1.8, 1.8], size=7.5)
para("A cell is a deployment only if it exceeds the city's do-nothing score. Under Cost and Eco the Phoenix platform (0.166/0.173) and all Hong Kong devices are below their none scores (PHX 0.200, HK 0.191); the platform recommendation therefore assumes Balanced or Safety weights.", 9, italic=True)

t6b = []
for label, c, v, eq, n in (
    ("Phoenix bus — 1× MC37V", "PHX", "bus", "MC37V", 1),
    ("Phoenix rail — 1× MC61V", "PHX", "rail", "MC61V", 1),
    ("Hong Kong bus — 1× drum fan", "HK", "bus", "Fan", 1),
    ("Hong Kong rail — 1× MC37V", "HK", "rail", "MC37V", 1),
):
    r = find(T5, c, v, eq, n)
    share = r["phi"] * (1.0 if r["wbgt"] <= 28.0 else 0.0) + (1 - r["phi"]) * (1.0 if r["wbgt_amb"] <= 28.0 else 0.0)
    t6b.append([label, f"{r['wbgt']:.2f}", f"{r['wbgt_amb']:.2f}", f"{share:.0%}", "yes" if share > 0.999 else "no"])
para("Table 6b. 28 °C non-acclimatised exposure check for the candidate options. This table is an exposure test, not a second scoring run: it reports the share of waiting occupants whose zone stays at or below 28 °C. The separate 28 °C scoring sensitivity, which shifts the whole safety curve to 24–30 °C, is reported in Appendix B.", 9, italic=True)
table(["Candidate option", "Zone WBGT (°C)", "Ambient WBGT (°C)", "Occupants ≤ 28 °C", "≤ 28 °C?"], t6b, widths=[4.6, 2.6, 2.8, 3.0, 1.7], size=8)

para("Figure 5 shows the γ sweep (left) and the weight matrix (right); the sweep is steep, which is why γ is a lumped parameter tested over 0.20–0.75.")
figure("docs/figures/fig5_gamma_heatmap.png", "Figure 5. γ sweep and weight matrix. Left: η vs γ (0.20–0.75) for the Phoenix bus shelter with MC37V; dashed lines at γ = 0.30 and 0.55. Right: best unit and its score for each COO weight profile and city–venue.")
para(f"Sensitivity runs hold the per-venue normalisers fixed, so a change in E reflects the parameter rather than a rescaling. The jet-mixing coefficient is the largest single uncertainty on the Hong Kong platform, but it does not flip the ranking at κ = 60: MC37V still leads the fan ({e60_37:.4f} vs {e60_fan:.4f}); the two cross at about κ ≈ 65, because the fan raises felt cooling without lowering the heat-index proxy. Using manufacturer water rates instead of the energy balance lowers the Hong Kong MC37V score to {em_37:.4f} (baseline normalisers held fixed, as in every run here) and leaves the ordering unchanged. The paper's own geometric estimate for a 3–4 m bus shelter is κ ≈ 80–105 (Section 3.3); at κ = 80 the Phoenix MC37V still leads the fan (0.508 vs 0.481), but the two cross at κ ≈ 92 and the fan leads at κ = 105 (0.559 vs 0.528), so the bus-shelter recommendation is conditional on κ ≲ 92. A distance-averaged estimate of the same profile over the waiting zone — the average of 315/x from 1.5 to 7.5 m at the bus shelter and from 2 to 30 m on the platform — gives κ ≈ 84 for the bus shelter and κ ≈ 30 for the platform. At κ = 84 the Phoenix bus order is unchanged (MC37V 0.512 vs fan 0.495); at κ = 30 the platform already puts MC37V ahead (0.396 vs 0.395), the same direction as the water-limited case in Table 10b. A black-globe offset of +3 K lowers S_safe by about 0.15 and E by about 0.045 in the linear range (less where the baseline is saturated), which does not reorder the units but weakens any claim of absolute safety. γ, ε, ΔT_nom, L_life, r_om and V_w each shift the near-ties by less than 0.05 E-points. A_cov is the exception: a 20% larger MC37V coverage raises Phoenix MC37V to 0.4418, above MC61V (0.4026), and the two are equal at about +0.6% (88.5 m² vs the nominal 88 m²). The Phoenix full-coverage recommendation therefore assumes the manufacturer area is not understated by more than about 0.6%. The full table is in Appendix B.")
para("The approximate proxy and the fixed design day are the main uncertainties. The 33 °C line is a benchmark, not a certification, and the ranking of near-ties should be read as “within model uncertainty” rather than as a field guarantee.")

h2("5.2 Hourly Weather Scenarios")
para("Table 7 repeats the comparison for nine local-time snapshots per day (11:00–19:00 inclusive) of June–August 2026, using the ERA5 0.25° grid (2 m temperature, 2 m dew point, 10 m wind scaled to 2 m, UTC converted to local time: 828 hours in Hong Kong, 825 in Phoenix — the Phoenix pull ends at 2026-08-31 16:00 local, so that day contributes 6 of 9 hours). The local-time window samples the actual afternoon. In Phoenix, MC37V wins 99% of bus-shelter device-hours and MC61V wins 89% of platform device-hours; both win every hour of the hottest decile. In Hong Kong the choice is time-dependent: the fan wins 88% of bus-shelter device-hours, but MC37V wins 98% of the hottest bus hours; on the platform the fan is the most frequent device winner (51%), MC37V follows at 42%, and MC61V wins 74% of the hottest platform hours. The do-nothing option wins 75% of Hong Kong platform hours, so the platform is not a continuous-operation case. A weather-switching strategy needs both units: at the Hong Kong bus shelter their combined annual LCC ($131.90 + $177.05) exceeds either single unit, so the hourly winner shares show where each unit is preferable, not that a two-unit deployment pays. A three-option annual budget follows without a new simulation: fan only $132/yr, cooler only $177/yr, both at least about $220/yr (the two capital/maintenance terms plus one energy stream) and at most $309/yr (the sum of both LCCs). That is $88–177/yr more than the fan alone, and the premium must be repaid by the hot-hour service where the other unit wins; E does not monetise that service, so the switch is not recommended.")
para("Table 7. Hourly robustness over local-time peak-window hours (828 Hong Kong, 825 Phoenix; device winner share).", 9, italic=True)
table(["Venue", "Device winner share", "Hottest 10% winner", "Do-nothing share"], [
    ["PHX bus", "MC37V 99% / Fan 1%", "MC37V 100%", "0%"],
    ["PHX rail", "MC61V 89% / MC37V 11%", "MC61V 100%", "0%"],
    ["HK bus", "Fan 88% / MC37V 12%", "MC37V 98% / Fan 2%", "0%"],
    ["HK rail", "Fan 51% / MC37V 42% / MC61V 7%", "MC61V 74% / MC37V 26%", "75%"],
], widths=[2.4, 6.8, 4.6, 2.6], size=8)

h2("5.3 Joint Uncertainty")
para("Table 8 reports 1,000 joint draws (seed 20261115) over κ ~ U(30,60), γ ~ U(0.45,0.65) for bus and U(0.25,0.35) for rail, ε ~ U(0.70,0.90), ΔT_nom ~ U(8.8,13.2), life × U(0.7,1.3), maintenance × U(0.5,1.5), coverage × U(0.8,1.2), water × U(0.7,1.3) and prices × U(0.8,1.2), with the normalisers recomputed inside each draw (occupancy cancels in E once the normalisers are recomputed, so it is not a source of ranking uncertainty). ΔT_nom, ε and κ are perturbed independently; they are physically linked through airflow and outlet area, so the joint draw is a scenario envelope, not a joint calibration. The full-coverage Phoenix choice is a coin flip: MC61V is best in 50% of draws and MC37V in 50%, and E(MC61V) > E(MC37V) in 50% of draws; the A_cov sensitivity explains why (a +0.6% effective MC37V area flips it). The Hong Kong platform is more robust among devices — MC37V beats the fan in 92% of draws — but the do-nothing option is best in 67% of draws, so deployment should be conditional on heat events. The bus-shelter choices are the most stable: MC37V 85% in Phoenix, fan 79% in Hong Kong, with Portacool taking 14% of Phoenix draws. These probabilities are conditional on the design day; the hour-to-hour switch in Table 7 is a separate axis.")
para("Table 8. Joint uncertainty: probability that each option is best (1,000 draws).", 9, italic=True)
table(["Venue", "MC37V", "MC61V", "Portacool", "Fan", "Do nothing"], [
    ["PHX bus", "85%", "0%", "14%", "1%", "0%"],
    ["PHX rail", "50%", "50%", "0%", "0%", "0%"],
    ["HK bus", "21%", "0%", "0%", "79%", "0%"],
    ["HK rail", "32%", "1%", "0%", "0%", "67%"],
], widths=[2.4, 2.1, 2.1, 2.4, 2.0, 2.4], size=8)

h2("5.4 Calculation Checks and Plausibility")
para("These are calculation and plausibility checks, not a validation of the predicted cooling of a specific unit (Table 9). They confirm the arithmetic, the wet-bulb approximation, the safety scale and the water order of magnitude; none of them shows that the model would reproduce a measured ΔT_eff on a real platform.")
para("Table 9. Plausibility checks against independent values.", 9, italic=True)
table(["Check", "Model value", "Independent reference", "Reading"], [
    ["Wet bulb, 41 °C / 18%, 950 hPa", "21.8 °C", "22.6 °C (Stull, sea level) [1]", "0.8 K lower; a lower wet bulb lowers WBGT, so this is not conservative"],
    ["Annual LCC, 1× MC37V, Phoenix", "$243.80", "$243.9 by hand: capital $111.4 + energy $57.4 + water $75.1", "arithmetic closes"],
    ["WBGT proxy, Phoenix fan", "27.55 °C", "33 °C at 115 W (ISO 7243) [3]", "well below the reference"],
    ["WBGT proxy, Hong Kong fan", "29.27 °C", "33 °C at 115 W (ISO 7243) [3]", "below; inside both modelling screens"],
    ["Water, 3,100 CFM / 11 °C", "25.1 L/h", "Manufacturer 10.6–18.2 L/h", "1.4–2.4× higher; ranking unchanged (5.1)"],
    ["Mist cooling, semi-open bus stop", "humidity penalty", "0.3–1 °C air drop, 0.5–1 g/kg [15]", "bounds the penalty, not the unit scale"],
], widths=[4.6, 2.6, 6.2, 3.4], size=7.5)
para("The largest discrepancy is water: the energy balance gives 25.1 L/h while manufacturer refill rates are 10.6–18.2 L/h. The model keeps the energy-balance value because it is physically tied to the temperature drop, and Section 5.1 shows that switching to manufacturer rates changes E by less than 0.01 and does not reorder the units. The field test of Kyogoku & Takebayashi [15] bounds the humidity penalty (0.3–1 °C air-temperature drop with 0.5–1 g/kg humidification); it is not a validation of the larger 3,100 CFM unit. No check in this section validates the absolute ΔT_eff at either site; that requires field measurement and is the main remaining gap.")
h2("5.5 Model Strengths, Limitations and Future Improvements")
para("Strengths: the six-equation chain is transparent; every number comes from one locked table; water is derived from the same energy balance as the temperature drop; the decision score is compared with a do-nothing baseline and separates the whole platform from the waiting zone.")
para("Two further scenarios change the decision, not just the score. Adding installation ($450 for a shelter, $900 for a platform, amortised over 10 years) and $150 per unit per year of labour lowers every E by 0.05–0.06. The Phoenix and Hong Kong bus-shelter rankings survive (Phoenix MC37V 0.4315, Hong Kong fan 0.3050), and the Phoenix platform remains MC61V (0.3422), but the Hong Kong platform falls further: MC37V goes from 0.2858 to 0.2255, below the do-nothing baseline (0.2865). Because installation and labour are fixed, running the unit fewer hours cannot restore the margin, so heat-event scheduling cannot rescue the platform device; it is not recommended. A 30% jet overlap between two units lowers the two-unit scores further, and no two-unit deployment beats one in the rebuilt base.")
para("Safety screen: 33 °C is the ISO 7243 reference for resting metabolism (115 W) and is used here as a modelling reference for waiting passengers, not as a compliance determination; light activity (180 W, e.g. walking to the stop) corresponds to 30 °C, which is why 30 °C is kept as the screen rather than called conservative. At 31.7 °C/77% the Hong Kong covered and uncovered zones are both below 30 °C (28.69 and 29.27 °C), so cooling there is a comfort service rather than a safety rescue; a 30 °C or 32.5 °C reading would suggest a failure, but at 31.7/77 both zones sit below it. Real exposure depends on radiation, wind and the natural wet bulb, which the proxy does not measure. At 33 °C the Hong Kong platform is a hair below doing nothing (0.2858 vs 0.2865) and the bus fan is a clear positive (0.3541 vs 0.2865). Section 5.7 reports the 30 °C and design-day alternatives.")
para("Limitations: the drum fan is a hypothetical benchmark; κ, γ, ε, ΔT_nom, L_life, r_om and N_eff remain assumptions; the heat index is an approximate proxy built from dry- and wet-bulb values with no globe or solar term, so it is not ISO 7243 compliance (CCOHS) [14]; the design-day tables use one representative day, while Section 5.2 tests 828 Hong Kong and 825 Phoenix local-time hourly scenarios, and a multi-year TMY remains future work; the multi-unit model adds nominal coverage areas rather than modelling the union of overlapping jets; and visitor experience is proxied by felt temperature and the graded safety term, while noise, humidity comfort and aesthetics are not modelled. Structural limits remain: Eq. 2 is wind-neutral, and Section 5.6 adds the flight-effect correction; crosswind narrows the Hong Kong near-tie and can let the fan overtake; the WBGT proxy gives a fan no safety credit for air speed while an evaporative unit is credited for its temperature drop, which favours evaporative cooling in E; κ is a lumped, uncalibrated coefficient (the Hong Kong order holds to κ ≈ 65); γ is a lumped design assumption rather than a geometric derivation, so the bus/rail difference is not measured; manufacturer coverage areas are treated as effective areas (a +0.6% effective MC37V area flips the Phoenix platform choice); and no field measurement of ΔT_eff exists at either site; both platform geometries are representative: Phoenix uses design-criteria dimensions and an assumed 120 m² waiting zone; Siu Hong uses a 32 × 4 m side-platform measurement (Open3Dhk), not a survey of that stop. Recommendations are conditional scenario results, not field-validated performance claims. The water rate also mixes a rated-airflow energy balance with manufacturer refill rates (25.1 vs 10.6–18.2 L/h); the model does not enforce a common operating point for airflow, ΔT and water. The main tables therefore use rated-water operation and Table 10b is its documented water-limited alternative, not a silent re-base; and because the series maximum WBGT (35.6 °C / 60.2%) is hotter and drier than the tested 33.5/62 case, the design-day tables order the options rather than fixing absolute levels. Closing these gaps would require field calibration of κ and γ, measured water flow, a multi-year TMY/HKO series and a two-unit deployment with independent placement; none of these data are claimed in this paper.")


h2("5.6 Crosswind, Fan Limits and the Joint Operating Point")
para("Equation 2 is wind-neutral: v_amb appears in both AT_amb and AT_zone and cancels. To give the model a wind dependence we borrow the flight-effect form of von Glahn [16], F(v) = 1 + 0.9·AR^(1/3)·(v/u_j)^(3/2), but the step from that study to this paper is an assumption, not a result: the cited report describes how an external flow changes centreline decay and core length, and we map it to a retained-cooling fraction γ_eff(v) = 1 − (1−γ0)·F(v_ref)/F(v) without deriving that mapping. The correction is normalised at each city's own design wind (Phoenix 1.8 m/s, Hong Kong 1.5 m/s), so the baseline tables are unchanged at v = v_ref; AR is the assumed outlet aspect ratio (1.25 for MC37V, 1.6 for MC61V, 1.0 for Portacool, 1.7 for the drum fan) and u_j = Q/A0. The scenario is illustrative and the final recommendations use the base model without it. The CBE fans-and-heat map [18] places 31.7 °C / 77% in the fan-beneficial band and excludes conditions above 40 °C for healthy adults with the listed inputs; that is why Section 4.1 separates the Q2a efficiency ranking from deployment at 41 °C.")
para("The water balance and the manufacturer data are not the same operating point. Table 10 gives the ratio of the energy-balance rate to the manufacturer refill rate; it is about 2.35 in Phoenix and 0.65/0.64 in Hong Kong. We therefore treat V_w as an interval [0.8, 1.2] × manufacturer and report the E range; using the manufacturer value changes the Hong Kong platform MC37V score from 0.2858 to 0.2845 without reordering the units.")
para("Table 10. Energy-balance water vs manufacturer refill rate.", 9, italic=True)
table(["City / unit", "Balance (L/h)", "Manufacturer (L/h)", "Ratio"], [
    ["Phoenix MC37V", "25.1", "10.6", "2.36"],
    ["Phoenix MC61V", "42.8", "18.2", "2.35"],
    ["Phoenix Portacool", "19.4", "11.4", "1.70"],
    ["Hong Kong MC37V", "6.9", "10.6", "0.65"],
    ["Hong Kong MC61V", "11.7", "18.2", "0.64"],
    ["Hong Kong Portacool", "5.3", "11.4", "0.47"],
], widths=[4.4, 3.6, 4.2, 2.6], size=8)
para("Table 10b ties the same constraint to the temperature drop. If each evaporative unit is held to its manufacturer water rate, the implied drop at rated airflow is 4.5 °C for MC37V and MC61V and 6.2 °C for the Portacool in Phoenix; Hong Kong is water-rich, so its energy-balance rate stays below the manufacturer rate and the base case is unchanged there. Under the base normalisers the Phoenix bus-shelter winner changes from MC37V (0.481) to the drum fan (0.371 vs 0.352), and the platform winner changes from MC61V (0.403) to MC37V (0.309 vs 0.287, with MC61V falling below doing nothing). The base tables therefore describe rated-water operation; where tank refill rather than the energy balance limits the unit, the water-limited ordering below applies.")
para("Table 10b. Water-limited joint operating point (Phoenix, manufacturer water with the implied temperature drop).", 9, italic=True)
table(["Venue", "Unit", "Base E", "Water-limited E", "Effect"], [
    ["PHX bus", "MC37V", "0.4806", "0.3521", "loses to the fan"],
    ["PHX bus", "MC61V", "0.4023", "0.2937", "below Portacool"],
    ["PHX bus", "Portacool", "0.4417", "0.3422", "second"],
    ["PHX bus", "Drum fan", "0.3705", "0.3705", "winner under the limit"],
    ["PHX rail", "MC37V", "0.4015", "0.3093", "winner under the limit"],
    ["PHX rail", "MC61V", "0.4026", "0.2869", "below doing nothing"],
    ["PHX rail", "Portacool", "0.3042", "0.2544", "unchanged"],
    ["Phoenix", "Do nothing", "0.3000", "0.3000", "reference"],
], widths=[2.6, 3.0, 2.6, 3.4, 5.0], size=8)
para("These checks do not change the wind or full-cost conclusions, but the water-limited ordering in Table 10b does change both Phoenix venue winners: the base tables describe rated-water operation, and the water-limited case is the one to use where tank refill rather than the energy balance limits the unit.")

h2("5.7 Definition Sensitivity: Where the Recommendation Changes")
para("The five definitional choices below are not parameter noise; they change the question being asked. The base case uses the design-capacity occupancy (45), the 33 °C resting reference (115 W), the 31.7 °C/77% hot-humid design hour (2026-07-12 18:00 local), the outlet-rating reading of the Q2a 5/8 °C, and point values κ = 45, 0.35 kW fan and 25.1 L/h water. Table 11 reports the alternative reading and the resulting winner, so the reader can see which conclusions are robust and which are conditional.")
para("Table 11. Definition sensitivity: base case vs alternative reading, with the resulting winner.", 9, italic=True)
table(["Definition", "Base → alternative", "What changes"], [
    ["Safety threshold", "33 °C (29–35; ISO 115 W) → 30 °C (26–32 vulnerable screen)", "HK rail MC37V 0.1465 > do-nothing 0.1365; HK bus fan 0.2041 > MC37V 0.1830"],
    ["HK design day", "31.7/77 (hot-humid hour) → 32.5/78 (humid) or 33.5/62 (dry)", "32.5/78: fan bus 0.3102 vs 0.2864, MC37V rail 0.2505 vs MC61V 0.2402; 33.5/62: bus MC37V 0.3786 vs fan 0.3607; rail MC37V 0.3239 ≈ MC61V 0.3235"],
    ["Q2a 5/8 °C", "outlet rating, then (1−γ) → shelter effect (γ = 0 for the given drop)", "B E = 0.368 < A 0.399; the Q2a ranking holds"],
    ["Phoenix N_eff", "45 (design capacity) → 6 (384 boardings × 12-min headway)", "η 862 → 115 (MC37V) and 685 → 91 (MC61V); E unchanged at 0.4015/0.4026 because N cancels in the normaliser; no ranking change"],
    ["Fan / κ / water", "10,500 CFM, 0.35 kW, $260; κ = 45; 25.1 L/h → break-even P ≤ 0.49 kW, C ≤ $740, CFM ≥ 8,700; κ bus 34 / rail 65; 10.6 L/h → ΔT 4.7 °C", "0.5–0.7 kW fan loses HK bus; κ < 34 flips bus to MC37V, κ > 92 flips it to the fan; water-limited Phoenix E 0.429 (MC37V) / 0.450 (MC61V)"],
], widths=[3.2, 6.6, 7.6], size=7.5)
para("Reading: the Phoenix bus-shelter choice is robust to the safety and design-day entries but not to κ: at the paper's own geometric estimate (κ ≈ 80–105) the fan overtakes above κ ≈ 92. The Phoenix platform is a near-tie (MC61V 0.4026 vs MC37V 0.4015) and flips if the effective MC37V area is only 0.6% larger (88.5 m²); occupancy does not flip it, because E is invariant to N once the normalisers are recomputed. The Hong Kong bus choice is a humid-hour result; at the dry-hot hour MC37V wins. The Hong Kong platform is below doing nothing at baseline, so it is not a deployment case. Q2a is robust, and κ is the entry that can reverse the bus ranking.")

# ---------------------------------------------------------------- section 6
h1("6. Decision Memorandum, Public Blog, Guidelines and References")
h2("6.1 Executive Memorandum to the COO (Q5a)")
para("MEMORANDUM — TO: Chief Operating Officer; FROM: Modelling team; DATE: November 2026; SUBJECT: Climate-matched cooling for the Phoenix rail platform.")
para("Scope: this memorandum answers Q5(a) for one named venue, the Phoenix rail platform (12th St & Washington/Jefferson; 120 m² shaded waiting zone). The other three city–venue cases are recorded as comparisons in Table 6c and the closing paragraph; they are not part of this recommendation.")
para(f"Recommendation: size for coverage first, then choose the smallest unit that achieves it, and always compare against doing nothing. For the 120 m² waiting zone, deploy 1× Hessaire MC61V only if 100% coverage is a hard requirement: φ = {phx61['phi']:.2f}, ΔT_eff = {phx61['dT']:.2f} °C, proxy WBGT = {phx61['wbgt']:.2f} °C, LCC = ${phx61['lcc']:.2f}/station/yr, E = {phx61['E']:.4f}, against a do-nothing baseline of {nd_E('PHX','rail'):.4f}. Otherwise 1× MC37V is the cost-default at E = {phx37['E']:.4f} and ${phx37['lcc']:.2f}; the two differ by only 0.0011. Do not deploy 2× MC61V: it doubles cost without improving coverage (E = {find(T4,'PHX','rail','MC61V',2)['E']:.4f}).")
para("Why this is a near-tie: MC61V buys full coverage for $153.61/yr more, but the scores differ by only 0.0011; MC37V is the cost-default and MC61V the full-coverage option. If the effective MC37V area is about 0.6% larger (88.5 m²), the two are equal, so the choice is conditional on the coverage rating, not on a field measurement.")
para("Conditions and pilot: the result assumes the design day (41 °C/18% RH), the 33 °C proxy reference, and representative platform geometry and the model's uncalibrated κ, γ and water assumptions. It also uses the 45-person design capacity; at the station's 384 weekday boardings the waiting population is roughly 5–6 (a 12–15% peak-hour share of the daily boardings times a 6-minute mean wait), but occupancy scales η and not E, so the ordering does not change (Section 5.7). Under a cost-only mandate the best platform device scores 0.166 against 0.200 for doing nothing, so the recommendation assumes a balanced mandate. The pilot should therefore compare both units, log WBGT, water and power for one season, and re-run the coverage check. If tank refill rather than the energy balance limits the unit, the water-limited case in Section 5.6 (Table 10b) puts MC37V ahead and MC61V below doing nothing, so the metered water rate decides between them. The recommendation is for the platform, not for the bus shelter; the bus-shelter case uses a different unit and a different E scale.")
para(f"Comparison (not recommendations): in Hong Kong the platform already sits below doing nothing — 1× MC37V E = {hk37['E']:.4f} vs do-nothing {nd_E('HK','rail'):.4f}. The paper's installation ($900 over 10 years) and labour ($150/yr) add $240/yr, lowering E to 0.2255, further below the baseline. We therefore do not recommend a Hong Kong platform unit in this memorandum; shade and windbreak come first. The Hong Kong bus shelter and the Phoenix bus shelter are recorded in Table 6c for context.")
para("Deployment timing: schedule the Phoenix platform for the hottest hours rather than continuous summer operation; the hourly analysis shows MC61V wins 89% of Phoenix platform device-hours and 100% of the hottest decile. Meter water and power on the pilot so the water-limited operating point can be checked against the rated 11 °C drop.")
para(f"Network: Phoenix 38 stations × ${phx61['lcc']:.2f} = ${38*phx61['lcc']:,.0f}/yr for the units alone if the platform unit is deployed system-wide; that is a device-cost component, not an upper bound. With the installation ($900 over 10 years, $90/yr) and labour ($150/yr) used in Section 5.5 the full-cost budget is 38 × $637.41 ≈ $24,222/yr. Action plan: (1) shade first; a windbreak is assumed to move the shelter toward the 0.30 rail loss value, an assumption rather than a measured effect; (2) install 1× MC61V on two pilot platforms; (3) meter water and power; (4) compare against 1× MC37V at the 0.6% coverage threshold; (5) re-check κ and the 33 °C reference after one season.")
para("Table 6c. Chosen venue (Phoenix platform) and context for the other three cases (33 °C).", 9, italic=True)
table(["City", "Venue", "Decision / context", "φ", "LCC (device)", "E (device)", "LCC (full cost)", "E (full cost)", "Do-nothing E"], [
    ["Phoenix", "Platform", "MC61V if full coverage; else MC37V", f"{phx61['phi']:.2f}", f"{phx61['lcc']:.2f}", f"{phx61['E']:.4f}", "637.41", "0.3422", f"{nd_E('PHX','rail'):.4f}"],
    ["Phoenix", "Bus shelter", "Context only", f"{find(T5,'PHX','bus','MC37V',1)['phi']:.2f}", f"{find(T5,'PHX','bus','MC37V',1)['lcc']:.2f}", f"{find(T5,'PHX','bus','MC37V',1)['E']:.4f}", "438.80", "0.4315", f"{nd_E('PHX','bus'):.4f}"],
    ["Hong Kong", "Bus shelter", "Context only", f"{find(T5,'HK','bus','Fan',1)['phi']:.2f}", f"{find(T5,'HK','bus','Fan',1)['lcc']:.2f}", f"{find(T5,'HK','bus','Fan',1)['E']:.4f}", "326.90", "0.3050", f"{nd_E('HK','bus'):.4f}"],
    ["Hong Kong", "Platform", "Context only: shade first", f"{hk37['phi']:.2f}", f"{hk37['lcc']:.2f}", f"{hk37['E']:.4f}", "417.05", "0.2255", f"{nd_E('HK','rail'):.4f}"],
], widths=[1.7, 1.9, 2.9, 0.9, 1.9, 1.4, 2.0, 1.4, 1.7], size=7.8)
para("Note: only the Phoenix platform row is a recommendation in this memorandum; the other rows are context. The device columns are the tables' baseline costs; the full-cost columns add installation ($450 per shelter or $900 per platform over 10 years) and $150 per unit per year of labour, and are the basis for the deployment choice. The Hong Kong platform is already below the do-nothing baseline (0.2858 vs 0.2865) and falls to 0.2255 at full cost.", 9, italic=True)

h2("6.2 Public-Facing Blog Post (Q5b)")
para("Why misting fans feel great in Phoenix — but change little in Hong Kong (and what your commute needs instead).")
phx_bus = find(T5, "PHX", "bus", "MC37V", 1)
hk_bus37 = find(T5, "HK", "bus", "MC37V", 1)
hk_busfan = find(T5, "HK", "bus", "Fan", 1)
para(f"Here is the question we started with: how much cooling do we actually get for the electricity we spend? The answer is a ratio, not a temperature. We count the people who feel cooler, multiply by the degrees they feel, and divide by the kilowatts: persons·°C per kW. In Phoenix, one 0.25 kW MC37V delivers about {phx_bus['eta']:.0f} persons·°C per kW at a bus shelter. In Hong Kong, the same unit delivers about {hk_bus37['eta']:.0f}, and a 36-inch fan about {hk_busfan['eta']:.0f} — roughly three times less cooling for the same electricity, because humid air refuses to evaporate much water.")
para("In Phoenix's 41 °C / 18% air, water evaporates readily. The cooler lowers the air by up to 11 °C before mixing and boundary losses, and a waiting passenger feels about 4.4 °C cooler; the unit uses about 100 litres of water per kilowatt-hour, which costs money and stresses a dry city.")
para(f"In Hong Kong's 31.7 °C / 77% air, the air is already close to saturation. The wet-bulb depression is small, so the same cooler lowers the air by only about 2.7 °C and a passenger feels about {hk_bus37['dT']:.1f} °C cooler; a fan, which spends its energy moving air rather than evaporating water, feels about {hk_busfan['dT']:.1f} °C cooler and uses no water at all. That is why the fan wins most Hong Kong summer hours even though it draws 0.35 kW, more than the cooler's 0.25 kW; on the hottest, driest afternoons the cooler deserves a second look — but that is not yet a recommendation to buy both, because a second unit brings its own fixed cost.")
para("The trade-off is not only comfort. On the Hong Kong rail platform the evaporative unit is only marginally ahead of the fan (E 0.2858 vs 0.2684), both are below doing nothing (0.2865), and once installation and labour are counted the evaporative unit falls to 0.2255. The platform therefore needs shade and a windbreak first; no unit is recommended. Water and carbon pull in opposite directions: the fan uses no water but more electricity per degree of felt cooling.")
para("The practical rule is simple: shade first, windbreak second, then match the machine to the climate. In dry heat, evaporative cooling is worth its water; in humid heat, moving air is usually the better buy. Ask your city to meter the water and the electricity on a pilot unit before it scales either option — that is the number that settles the argument.")
para(f"At a 128 m² platform the comparison is close on cooling alone: one MC37V (${hk37['lcc']:.2f}, E {hk37['E']:.4f}) only marginally beats one fan (${hkfan['lcc']:.2f}, E {hkfan['E']:.4f}), both sit below doing nothing (0.2865), and two fans (E {hk2fan['E']:.4f}) lose to one MC37V. The cost and coverage caveats above decide the deployment, not the cooling difference.")

para("Figure 6 turns the two recommendation panels into a public-facing comparison: what a passenger feels, what the water costs, and what the city pays.")
figure("docs/figures/fig6_infographic.png", "Figure 6. Public-facing infographic: Phoenix and Hong Kong side by side (felt cooling, water, cost, and the shade → windbreak → machine rule), no equations.")

h2("6.3 Deployment Guidelines Across the Four Venues")
para("These guidelines follow from the tables above and apply to the four city–venue cases; each is stated with the condition under which it holds, so an operator can act without re-deriving the model.")
bullet("Count useful cooling against doing nothing. Compare options on η and E; an option that does not beat the do-nothing score is not preferable under this scoring rule — E is a weighted score, not a money saving, so report its felt benefit and annual cost separately. On the humid Hong Kong platform nothing clears the baseline, so shade and windbreak come first.")
bullet("Size for coverage, then for cost. Coverage is the largest single lever: a unit at φ = 1.00 is worth 36% more η than the same unit at φ = 0.73, and coverage is measured against the waiting zone, not the whole platform. Treat the Phoenix bus-shelter pick as provisional: κ is uncalibrated and the fan overtakes above κ ≈ 92, inside the geometrically implied range.")
bullet("Match the technology to the climate. Evaporative cooling pays in dry heat and moving air in humid heat; at a Hong Kong bus shelter the fan wins routine hours and the cooler is competitive in the hottest, driest ones — a re-evaluation point, not a two-unit deployment, since buying both units is not costed here.")
bullet("Deploy one unit before two. In the base case no two-unit deployment beats one: the second unit adds capital and carbon for little extra coverage, and a 30% jet overlap makes it worse.")
bullet("Pilot before scaling. Run one unit for a season, meter water and power, log the proxy WBGT, and re-check κ and the coverage rating; the Phoenix platform near-tie and the water rate sit inside model uncertainty and should not be settled on paper.")

h2("6.4 References")
refs = [
    "Stull, R. (2011). Wet-bulb temperature from relative humidity and air temperature. J. Appl. Meteor. Climatol., 50(11), 2267–2269.",
    "Steadman, R. G. (1979). The assessment of sultriness. Part I. J. Appl. Meteor., 18(7), 861–873.",
    "ISO 7243:2017. Ergonomics of the thermal environment — WBGT index. Annex A: 115 W → 33 °C; 180 W → 30 °C; 300 W → 28 °C (acclimatised).",
    "WRI Aqueduct 4.0 (2023). Baseline water stress: Phoenix 2.482; Hong Kong sub-basins 0.179.",
    "Arizona Public Service (2024). Rate Schedule E-32 TOU S, effective 2024-03-08; City of Phoenix Water Services (2024). Water rates inside city, effective 2024-03-01.",
    "CLP Power Hong Kong (2026). Non-residential tariff: 110.6 + 39.4 = 150 cents/unit. CLP (2024). CO₂e emission intensity 0.38 kg/kWh (2023: 0.39).",
    "FTA (2024). 2023 National Transit Database, Valley Metro Rail (NTD ID 90209): 71 facilities; 29,846 average weekday UPT.",
    "Valley Metro (2024). TOD station profile, 12th St & Washington/Jefferson: 384 weekday boardings; 27,462 full-system weekday boardings; about 38 stations.",
    "Transport Department, HKSAR (2026, March). Monthly Traffic and Transport Digest: Light Rail 439,200 daily journeys; franchised buses 3,902,200 daily.",
    "MTR Corporation (2026). Light Rail routes and stops: 68 unique stops, 11 lines; Siu Hong 7 lines; Tuen Mun Ferry Pier 6 lines.",
    "36-inch drum fan: hypothetical benchmark in this study; specifications are assumptions, not manufacturer data.",
    "Valley Metro (2020). Design Criteria Manual, May 2020, Ch. 6.0 Station Design, pp. 136–139: 280 ft calculated platform length (260 ft minimum), 16 ft 4 in centre-platform width, 7 ft² per person at the 12-minute peak load, 1.0% cross slope, and shade criteria.",
    "Valley Metro (2025). South Central Extension/Downtown Hub (SCE/DH) Frequently Asked Questions, April 2025, pp. 1–2, 7: opened 7 June 2025 with eight new stations; 12/15/20-minute headways; 365 days, about 20 hours per day.",
    "CCOHS (accessed 15 November 2026). OSH Answers: Heat Control — WBGT and the assumptions behind it. Canadian Centre for Occupational Health and Safety. https://www.ccohs.ca/oshanswers/phys_agents/heat/heat_control.html",
    "Kyogoku, S., & Takebayashi, H. (2023). Experimental verification of mist cooling effect in front of air-conditioning condenser unit, open space, and bus stop. Atmosphere, 14(1), 177. https://doi.org/10.3390/atmos14010177",
    "von Glahn, U. H. (1989). Rectangular Nozzle Plume Velocity Modeling for Use in Jet Noise Prediction. NASA Technical Memorandum 102047 (AIAA-89-2357).",
    "Deo, R. C., Nathan, G. J., & Mi, J. (2007). Comparison of turbulent jets issuing from rectangular nozzles with and without sidewalls. Experimental Thermal and Fluid Science, 32(2), 596–606. https://doi.org/10.1016/j.expthermflusci.2007.06.009",
    "Tartarini, F., Schiavon, S., Cheung, T., & Hoyt, T. (2020). CBE Thermal Comfort Tool. SoftwareX, 12, 100563. https://doi.org/10.1016/j.softx.2020.100563; Fans & Heat page, https://comfort.cbe.berkeley.edu/fan_heatwaves, accessed 16 November 2026.",
    "OSHA. Technical Manual, Section III, Chapter 4: Heat Hazards. https://www.osha.gov/otm/section-3-health-hazards/chapter-4, accessed 16 November 2026.",
]
for i, ref in enumerate(refs, start=1):
    para(f"{i}. {ref}", 9)


# ---------------------------------------------------------------- AI report
h1("AI Use Report")
para("AI tools were used in this project and are disclosed here. The assistant was a large-language-model coding and writing agent (DeepSeek, accessed through the DeepSeek Harness interface) on 14–15 November 2026. It was used for four purposes: (1) drafting and editing English prose; (2) writing and running the Python scripts in analysis/ (recompute.py, sensitivity.py, make_figures.py); (3) consistency checks between the paper, the tables and the data register; and (4) translation between the team's Chinese notes and the English manuscript.")
para("Representative prompts included: “Check whether the one- and two-unit rows use the same normalisers, and recompute E if they do not”; “Restrict the safety score to the cooled zone, report the occupants and WBGT in the uncovered zone, and add a do-nothing baseline”; and “Derive the water flow from the adiabatic mass balance and rebuild the cost and externality terms”.")
para("Every number was recomputed by analysis/recompute.py, the tables were regenerated from it, the figures come from the same locked table, and analysis/qa_check.py scans the manuscript for superseded values. AI output was treated as draft text and code only: all citations refer to primary sources, no data were generated by the model, and the team reviewed the wording, assumptions and recommendations.")
para("Tools and versions: DeepSeek Harness (deepseek-flash model) in an agent interface; Python 3.12 with standard libraries for the recomputation, NumPy 2.3.5 and Matplotlib 3.11.0 for the figures, python-docx 1.2 for document assembly, and WPS Writer/LibreOffice for PDF export.")


# ---------------------------------------------------------------- appendix
doc.add_page_break()
h1("Appendix A. Data and Assumption Register")
para("Status: S = sourced, D = derived, A = assumption, U = unverified. Sources are listed in Section 6.4; derived values follow Eq. 7.", 9)
para("Table A1. Data and assumption register.", 9, italic=True)
table(["Parameter", "Value", "Status", "Source / note"], [
    ["Phoenix T_db / RH", "41.0 °C / 18%", "D/A", "ERA5 2026 Jun–Aug; typical daily max (series maximum 45.1 °C)"],
    ["Hong Kong T_db / RH", "31.7 °C / 77%", "D/A", "ERA5 hot-humid design hour (2026-07-12 18:00 local); selected design hour, not the series maximum WBGT; the listed maximum-WBGT hour has dry-bulb/RH 35.6 °C/60.2% (2026-08-08 15:00 local)"],
    ["Wet bulb", "21.8 / 28.2 °C", "D", "Psychrometric estimate at 950/1,000 hPa; derived WBGT is a proxy"],
    ["Phoenix p_elec", "0.1595 USD/kWh", "D", "APS E-32 2024: energy + 6-month demand"],
    ["Hong Kong p_elec", "0.1923 USD/kWh", "D", "CLP 2026: 150 cents/unit ÷ 7.8"],
    ["Phoenix p_water", "2.0766 USD/m³", "D", "2024 inside-city card; excludes sewer/tax"],
    ["Hong Kong p_water", "0.9615 USD/m³", "D", "WSD 4.58 + 2.92 ÷ 7.8"],
    ["A_platform", "425 / 128 m²", "D", "Representative geometry: Valley Metro design criteria; side-platform measurement applied to Siu Hong; neither a site survey"],
    ["A_waiting", "120 / 128 m²", "D/A", "Phoenix assumed shaded zone; HK representative platform area"],
    ["κ (dimensionless)", "45", "A", "Assumed 45; sensitivity 30–60 and bus 80–105; no field calibration"],
    ["γ (bus / rail)", "0.55 / 0.30", "A", "Urban ventilation ranges; swept 0.20–0.75"],
    ["ε", "0.80", "A", "Data pack: no manufacturer guarantee; 0.70–0.90"],
    ["ΔT_nom", "11.0 °C", "A", "Assumed maximum drop; 8.8–13.2"],
    ["V_w", "derived", "D", "Adiabatic mass balance, Eq. 7; manufacturer rates as sensitivity"],
    ["L_life / r_om", "5–7 yr / 3–8%", "A", "No published service data"],
    ["N_eff", "6 / 45", "A", "Bus 6; rail 45 design capacity; Phoenix actual ≈6 at 384 boardings (5.7)"],
    ["Phoenix stations", "38", "S", "NTD 71 facilities ≠ stations"],
], widths=[3.8, 4.4, 1.3, 7.0], size=8)
para("Source details: MC37V https://www.homedepot.com/p/Hessaire-3-100-CFM-3-Speed-Portable-Evaporative-Cooler-Swamp-Cooler-for-950-sq-ft-MC37V/304078772; MC61V https://hessaire.com/mobile-cooling/5300-cfm-mobile-cooler (price: https://www.sylvane.com/products/hessaire-mc61v-evaporative-air-cooler); Portacool catalog https://portacool.com/wp-content/uploads/2025/02/Portacool-Catalog_Jetstream_Industrial-Automotive-2023Reduced.pdf; Aqueduct Phoenix aqid 1628 / pfaf 772221 / string 772221-USA.3_1-1628 (33.44823 N, −112.075098), bws 2.482; Hong Kong sub-basins HKG.1_1 / HKG.10_1 / HKG.11_1, bws 0.179; Siu Hong stop coordinates from MTR route data and OpenStreetMap; Phoenix station profiles from the Valley Metro TOD PDF.", 8.5)


doc.add_page_break()
h1("Appendix B. Single-Factor Sensitivity")
para("Table B1 repeats the single-factor runs behind Section 5.1 with the baseline normalisers fixed. Each row changes one input by the stated amount; all other inputs stay at their baseline values. E is comparable only within a venue type.")
para("Table B1. Single-factor sensitivity of E (baseline normalisers).", 9, italic=True)
table(["Variation", "PHX 1x37", "PHX 1x61", "HK 1x37", "HK 1xfan"], [
    ["BASE", "0.4015", "0.4026", "0.2858", "0.2684"],
    ["epsilon 0.70", "0.4015", "0.4026", "0.2802", "0.2684"],
    ["epsilon 0.90", "0.4015", "0.4026", "0.2915", "0.2684"],
    ["dTnom 8.8", "0.3708", "0.3641", "0.2858", "0.2684"],
    ["dTnom 13.2", "0.4322", "0.4412", "0.2858", "0.2684"],
    ["L_life -30%", "0.3929", "0.3895", "0.2773", "0.2637"],
    ["L_life +30%", "0.4061", "0.4097", "0.2905", "0.2709"],
    ["r_om -50%", "0.4055", "0.4088", "0.2899", "0.2694"],
    ["r_om +50%", "0.3975", "0.3965", "0.2818", "0.2674"],
    ["V_w -30%", "0.4159", "0.4273", "0.2866", "0.2684"],
    ["V_w +30%", "0.3870", "0.3780", "0.2851", "0.2684"],
    ["p_elec -20%", "0.4043", "0.4076", "0.2888", "0.2724"],
    ["p_elec +20%", "0.3986", "0.3977", "0.2829", "0.2643"],
    ["p_water -50%", "0.4109", "0.4187", "0.2868", "0.2684"],
    ["p_water +50%", "0.3920", "0.3865", "0.2849", "0.2684"],
    ["H_yr -20%", "0.4194", "0.4334", "0.2951", "0.2806"],
    ["H_yr +20%", "0.3835", "0.3719", "0.2766", "0.2562"],
    ["kappa 30", "0.3956", "0.3945", "0.2804", "0.2498"],
    ["kappa 60", "0.4073", "0.4107", "0.2913", "0.2870"],
    ["gamma -0.10", "0.4303", "0.4419", "0.2927", "0.2684"],
    ["gamma +0.10", "0.3727", "0.3634", "0.2790", "0.2684"],
    ["A_cov -20%", "0.3611", "0.4046", "0.2744", "0.2684"],
    ["A_cov +20%", "0.4418", "0.3986", "0.2972", "0.2684"],
    ["BWS_HK 0.850", "0.4015", "0.4026", "0.2840", "0.2684"],
    ["EF_HK 0.465", "0.4015", "0.4026", "0.2803", "0.2605"],
    ["EF_PHX 0.25", "0.4062", "0.4108", "0.2858", "0.2684"],
    ["EF_PHX 0.36", "0.3964", "0.3939", "0.2858", "0.2684"],
    ["threshold 28 (24-30 C)", "0.3052", "0.3360", "0.0465", "0.0184"],
], widths=[4.6, 2.7, 2.7, 2.7, 2.7], size=7.8)
para("The 28 °C row shifts the safety curve to 24–30 °C; Table 6b's 28 °C line is a separate exposure check (share of occupants at or below 28 °C), not this scoring row.", 9, italic=True)

typeset_inline()
for _p in doc.paragraphs:
    _t = _p.text.strip()
    if _t.startswith("Table ") and _p.runs and _p.runs[0].italic:
        _p.paragraph_format.keep_with_next = True

doc.save(OUT)
print("saved", OUT)
