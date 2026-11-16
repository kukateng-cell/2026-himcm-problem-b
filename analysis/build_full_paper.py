"""Build the integrated English master paper v1.0 (model rebuilt after the review).

Run: python analysis/build_full_paper.py
"""

import os

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

import recompute as R

R.MODE = "pressure"
R.THRESH = 30.0

T3, G3 = R.table3_rows("pressure", 30.0)
T4, G4 = R.table4_rows("pressure", 30.0)
T5, G5 = R.table5_rows("pressure", 30.0, "B")
T6_30 = R.table6(T5, G5, 30.0)
T5_28, G28 = R.table5_rows("pressure", 28.0, "B")
T6_28 = R.table6(T5_28, G28, 28.0)

OUT = "2026_HiMCM_ProblemB_Full_Paper_v1.1.docx"

doc = Document()
sec = doc.sections[0]
sec.top_margin = Cm(1.9); sec.bottom_margin = Cm(1.9)
sec.left_margin = Cm(2.0); sec.right_margin = Cm(2.0)


def set_font(run, size=10, bold=False, color=None, italic=False):
    run.font.name = "Calibri"
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


style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(10)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
for i in range(1, 4):
    st = doc.styles["Heading %d" % i]
    st.font.name = "Calibri"
    st.element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")


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


add_page_numbers(sec)


def h1(text):
    h = doc.add_heading(level=1)
    r = h.add_run(text); set_font(r, 15, True, RGBColor(0x1F, 0x3B, 0x57))


def h2(text):
    h = doc.add_heading(level=2)
    r = h.add_run(text); set_font(r, 12, True, RGBColor(0x1F, 0x3B, 0x57))


def h3(text):
    h = doc.add_heading(level=3)
    r = h.add_run(text); set_font(r, 10.5, True)


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
    set_font(r, 8.5, italic=True)
    return p


def find(rows, city, venue, eq, n=1):
    return next(r for r in rows if r["city"] == city and r["venue"] == venue and r["eq"] == eq and r["n"] == n)


def nd_E(city, venue):
    nd = R.no_device(city, venue)
    return R.score(nd, G5, threshold=30.0)[0]


# ---------------------------------------------------------------- cover
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("2026 HiMCM"); set_font(r, 14, True, RGBColor(0x66, 0x66, 0x66))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Problem B: Air Conditioning the Environment"); set_font(r, 20, True, RGBColor(0x1F, 0x3B, 0x57))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Cooling per Kilowatt for Semi-Open Transit Spaces"); set_font(r, 16, False, RGBColor(0x1F, 0x3B, 0x57))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("A Six-Equation Framework with Heat–Water Balance and a Do-Nothing Baseline\nfor Semi-Open Transit Cooling")
set_font(r, 12, False, RGBColor(0x33, 0x33, 0x33))
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Team 19362   |   November 2026"); set_font(r, 11)
doc.add_page_break()

# ---------------------------------------------------------------- summary
h1("Summary Sheet")
para("Public cooling is usually judged by kilowatt-hours, but energy alone cannot separate a working system from a failing one. An open freezer and a semi-open transit shelter share the same physics: cold air is produced inside a boundary and leaks through an opening, so the useful cooling delivered to the people inside — not the electricity drawn — is what should be counted. We build a six-equation model and apply it to a 15 m² bus shelter and a rail platform in Phoenix (41 °C / 18% RH) and Hong Kong (32.5 °C / 78% RH).")
para(f"Eqs. 1–2 give the thermodynamic cooling and its apparent-temperature effect; Eq. 3 converts them into η, in persons·°C per kW; Eq. 4 prices the life-cycle cost after the cooling water is derived from an adiabatic mass balance; Eq. 5 prices the water–carbon externality; Eq. 6 combines a graded heat-safety proxy, a persons-weighted cooling benefit, cost and environment. Coverage is measured against the modelled waiting zone (120 m² in Phoenix, 128 m² in Hong Kong), not the whole platform (425 m² and 128 m²), and every result is compared with a do-nothing baseline.")
para(f"The model reverses two intuitions and corrects a third. In Q2a the 0.25 kW fan is {T3[0]['eta']/T3[2]['eta']:.1f} times more efficient than the 2.5 kW cooler (η = {T3[0]['eta']:.2f} vs {T3[2]['eta']:.2f}), because extra power buys little extra cooling. In Q2b, at a Phoenix platform 1× MC61V scores E = {find(T4,'PHX','rail','MC61V',1)['E']:.4f} and covers the waiting zone, while 2× MC37V scores {find(T4,'PHX','rail','MC37V',2)['E']:.4f} at twice the capital cost; a second small unit can still pay when it closes a coverage gap (2× Portacool {find(T4,'PHX','rail','Porta',2)['E']:.4f} vs 1× {find(T4,'PHX','rail','Porta',1)['E']:.4f}). In Hong Kong the bus shelter favours the drum fan (E = {find(T5,'HK','bus','Fan',1)['E']:.4f} vs {find(T5,'HK','bus','MC37V',1)['E']:.4f} for MC37V); on the rail platform MC37V ({find(T5,'HK','rail','MC37V',1)['E']:.4f}) edges MC61V ({find(T5,'HK','rail','MC61V',1)['E']:.4f}) and the fan ({find(T5,'HK','rail','Fan',1)['E']:.4f}), but its margin over doing nothing ({nd_E('HK','rail'):.4f}) disappears once installation and labour are charged.")
para(f"A do-nothing baseline is reported throughout: its score is {nd_E('PHX','bus'):.4f} in Phoenix and {nd_E('HK','bus'):.4f} in Hong Kong; every Phoenix recommendation and the Hong Kong bus-shelter fan clear it, while the Hong Kong platform margin is only 0.008 and reverses under full installation costs, so the recommendations are conditional rather than artefacts of ignoring the alternative. Water use is not a free assumption: at rated airflow a 11 °C drop on 3,100 CFM requires about 25 L/h, roughly double the tank-based rate often quoted, and this cost is carried through Eq. 4 and Eq. 5.")
para("Recommendations: size for coverage first, then minimise cost and environmental burden. In Phoenix, 1× MC37V at the bus shelter and 1× MC61V at the platform. In Hong Kong, 1× drum fan at bus shelters; on the rail platform the baseline margin is only 0.008 and reverses under full installation costs, so shade and windbreak come first and a unit is installed only if installation is shared. Limitations: the drum fan is a hypothetical benchmark, several parameters remain assumptions, the heat index is an approximate WBGT proxy rather than a compliance measurement, and the ranking of near-ties is sensitive to the jet-mixing coefficient.")
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
    ("   3.4 Spatial Cooling Efficiency (Eq. 3)", "7"),
    ("   3.5 Annualised Life-Cycle Cost (Eq. 4)", "7"),
    ("   3.6 Water–Carbon Externality (Eq. 5)", "8"),
    ("   3.7 Safety Proxy and Decision Score (Eq. 6)", "8"),
    ("4. Model Application and Results (Q2–Q4)", "8"),
    ("   4.1 Bus Stop Shelter (Q2a)", "8"),
    ("   4.2 Rail Platform and Multi-Unit Scaling (Q2b)", "9"),
    ("   4.3 Cross-Climate Comparison (Q3)", "10"),
    ("   4.4 Multi-Objective Trade-Offs (Q4)", "11"),
    ("5. Sensitivity Analysis and Model Evaluation", "12"),
    ("6. Decision Memorandum, Public Blog and References", "16"),
    ("AI Use Report", "18"),
    ("Appendix A. Data and Assumption Register", "19"),
    ("Appendix B. Single-Factor Sensitivity", "20"),
]
table(["Section", "Page"], [[a, b] for a, b in toc], widths=[13.0, 2.5], size=9)
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
     "The zone velocity is v_eff = v_amb + κ(Q_air/A_cov), with κ = 45 (dimensionless momentum amplification, sensitivity 30–60); κ is a lumped jet-mixing coefficient, not a physical velocity; 45 is a literature-informed assumption (sensitivity 30–60), and it is not calibrated in this study. Commuters are uniformly distributed, so beneficiaries scale with φ = min(1, n·A_cov/A_waiting), with N_eff = 6 (bus) and 45 (rail)."),
    ("Assumption 5 — Commercial tariffs and straight-line depreciation.",
     "Capital costs depreciate linearly over L = 5–7 years and annual maintenance is r_om = 3–8% of capital. Energy uses the latest local tariffs (Phoenix 2024 APS E-32 with demand [5]; Hong Kong 2026 CLP [6]) and water the City of Phoenix 2024 card and the Hong Kong WSD schedule; the 2026 Phoenix scenario and the Hong Kong 50% water concession are tested separately."),
    ("Assumption 6 — Shaded conditions and an approximate heat index.",
     "Both venue types provide overhead shading, so the heat index is the proxy WBGT ≈ 0.7 T_wb + 0.3 T_db (ISO 7243 no-solar-load form [3], with the natural wet bulb approximated by the psychrometric wet bulb and the globe temperature by the dry-bulb). This is an index approximation, not a compliance measurement; the 30 °C reference is used as a graded benchmark (Section 3.7) and 28 °C as a stricter sensitivity. Black-globe offsets of +3 and +6 K are tested in Section 5."),
]
for title, body in assumptions:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(title); set_font(r, 10, True)
    r = p.add_run(" " + body); set_font(r, 10)

para("Table 1. Summary of assumptions and supporting equations.", 8.5, italic=True)
table(["Assumption", "Equations", "Basis / status"], [
    ["1 Quasi-steady peak", "1–6", "Design-day method; assumption"],
    ["2 Isenthalpic humidification", "1–2", "Moist-air thermodynamics; ε=0.80 assumed"],
    ["3 Cold-air escape γ", "2–3, 6", "Urban ventilation ranges; lumped; swept"],
    ["4 Jet mixing, occupancy", "2–3", "κ dimensionless, assumed 45; N_eff assumed"],
    ["5 Tariffs and depreciation", "4–5", "APS/CLP/WSD; L, r_om assumed"],
    ["6 Shaded proxy WBGT", "6", "Approximate index; 30 °C reference, 28 °C sensitivity"],
], widths=[5.6, 3.0, 7.4], size=8)
doc.add_page_break()

# ---------------------------------------------------------------- section 3
h1("3. Mathematical Model")
figure("docs/figures/fig1_system.png", "Figure 1. System boundary and equation couplings. Left: semi-open venue cross-section with the cold jet, lateral escape γ and coverage φ. Right: the Eq. 1→2→3→6 chain with Eq. 4 and Eq. 5 as parallel inputs to Eq. 6, grouped into thermodynamics, economics/externality and safety/decision.")
para("Figure 1 is the roadmap for this section: the left panel fixes the boundary and the loss terms; the right panel shows how the six equations combine into the decision score E.")
h2("3.1 Parameter Baselines")
para("Table 2A lists the four commercial benchmark units. Status codes: S = sourced, D = derived, A = assumption, U = unverified. The 36-inch drum fan has no product source and is treated as a hypothetical benchmark [11]. Water use is not listed as a free parameter: it is derived from the energy balance in Eq. 4 (Section 3.5) and the values in the table are the resulting design-point rates.")
para("Table 2A. Candidate commercial cooling units (design-point water derived from Eq. 8).", 8.5, italic=True)
tab2a = []
for eq, name in (("MC37V", "Hessaire MC37V"), ("MC61V", "Hessaire MC61V"), ("Porta", "Portacool Jetstream 220"), ("Fan", 'Drum fan 36"')):
    e = R.EQUIPMENT[eq]
    phx = R.calc("PHX", "bus", eq, 1)["Vw"]
    hk = R.calc("HK", "bus", eq, 1)["Vw"]
    tab2a.append([name, f"{e['P']:.3f}", f"{e['CFM']:,}", f"{e['A']:.0f}", f"{e['eps']:.2f}",
                  f"{phx:.1f} / {hk:.1f}", f"{e['C']}", f"{e['L']}", f"{e['r']*100:.0f}%"])
table(["Unit", "P (kW)", "CFM", "A_cov (m²)", "ε", "V_w PHX/HK (L/h)", "C_cap (USD)", "L (yr)", "r_om"], tab2a,
      widths=[3.6, 1.5, 1.5, 1.8, 1.2, 2.9, 1.9, 1.2, 1.3], size=7.5)

para("Table 2B. City boundary conditions.", 8.5, italic=True)
table(["Parameter", "Symbol", "Unit", "Phoenix", "Hong Kong", "Status"], [
    ["Dry-bulb / RH", "T_db, RH", "°C, %", "41.0, 18", "32.5, 78", "D/A"],
    ["Wet bulb (pressure-corrected)", "T_wb", "°C", "21.8", "29.1", "D"],
    ["Surface pressure", "p_s", "hPa", "950", "1,000", "D"],
    ["Ambient wind", "v_amb", "m/s", "1.8", "1.5", "A"],
    ["Electricity", "p_elec", "USD/kWh", "0.1595", "0.1923", "D"],
    ["Water (+sewage)", "p_water", "USD/m³", "2.0766", "0.9615", "D"],
    ["Grid carbon factor", "EF_grid", "kg CO₂e/kWh", "0.303", "0.390", "A/S"],
    ["Baseline water stress", "BWS_raw", "—", "2.482", "0.179", "S"],
    ["Peak operating hours", "H_yr", "h/yr", "1,440", "1,200", "A"],
], widths=[6.0, 2.2, 2.6, 2.2, 2.2, 1.4], size=8)

para("Table 2C. Venue geometry: whole platform, modelled waiting zone and usage.", 8.5, italic=True)
table(["Venue", "A_platform (m²)", "A_waiting (m²)", "γ", "N_eff", "Basis"], [
    ["Bus shelter", "20", "15", "0.55", "6", "D/A: 2 m × 10 m canopy measured at a semi-open bus stop (Kyogoku & Takebayashi 2023); 15 m² modelled waiting area"],
    ["Phoenix rail platform", "425", "120", "0.30", "45", "D/A: Valley Metro design criteria 85.34 m × 4.98 m; 120 m² shaded boarding zone (28% of the platform)"],
    ["Hong Kong rail platform", "128", "128", "0.30", "45", "D: scaled from the Open3Dhk 3D map ≈ 32 m × 4 m"],
], widths=[3.8, 2.6, 2.6, 1.2, 1.2, 6.0], size=7.5)

h3("3.1.1 Transit Network Basis")
para("The Phoenix case is the 12th St & Washington/Jefferson Station (384 weekday boardings [8]); the Hong Kong case is the Siu Hong (兆康) stop, stop ID 100, 22.4120 N, 113.9783 E, served by seven routes [10]. Valley Metro Rail's 2023 NTD profile [7] reports 71 facilities and 29,846 average weekday unlinked trips; the 71 figure is a facility count, not a station count (about 38 stations in 2024), so network costs in Section 6 use 38 stations. The 12th St & Washington/Jefferson profile [8] reports 384 weekday boardings (208 + 176) and 27,462 full-system weekday boardings. Valley Metro's design criteria set a 280 ft (85.3 m) calculated platform with a 16 ft 4 in (4.98 m) minimum centre-platform width, a peak 12-minute boarding/alighting design load at 7 ft² (0.65 m²) per person, and a 1.0% cross slope (Ch. 6.3.1–6.3.5) [12]. The South Central Extension/Downtown Hub opened on 7 June 2025 with eight new stations and a 12-minute weekday headway [13] (20 minutes after 19:00; 15/20 minutes on Saturday; 20 minutes on Sunday; 365 days, about 20 h/day). The 2024 count of 38 stations is kept for the network-cost illustration so that station count, tariffs and ridership share the same 2024 basis; the 2026 system has about 46 stations. Hong Kong's Light Rail has 68 unique stops on 11 lines [10], with 439,200 daily journeys in March 2026 [9]; five routes (505, 507, 614, 614P, 751) run 6–18 min peak headways. 149 LRVs and 3.90 million daily bus journeys are marked U because the PDF text layer is unreliable and the figures need a page-level check.")

h2("3.2 Thermodynamic Cooling Constraint (Eq. 1)")
para("ΔT_phys = min(ΔT_nom, ε(T_db − T_wb)).   (Eq. 1)")
para("T_wb is solved from the psychrometric relation at surface pressure p_s [1]: e_s(T_wb) − γ_p(T_db − T_wb) = e_amb, where γ_p = 1.006 p_s /(0.622 × 2,450) hPa/K. At 41 °C/18% and 950 hPa this gives 21.8 °C; at 32.5 °C/78% and 1,000 hPa it gives 29.1 °C. For pure fans ε = 0 and ΔT_phys = 0.")

h2("3.3 Apparent Temperature and Jet Velocity Coupling (Eq. 2)")
para("ΔT_eff = AT(T_db, e_amb, v_amb) − AT(T_zone, e_zone, v_eff),   AT(T,e,v) = T + 0.33e − 0.70v − 4.00.   (Eq. 2) [2]")
para("T_zone = T_db − (1−γ)ΔT_phys; e_zone = min(e_s(T_zone), e_amb + 0.665(1−γ)ΔT_phys); v_eff = v_amb + κ(Q_air/A_cov), with Q_air = CFM × 1.699/3600 m³/s. Rectangular jets decay more slowly than circular ones, and the rate depends on the nozzle aspect ratio and on the sidewalls [17]; following von Glahn's rectangular-plume model [16], the low-speed centreline decay can be written u(x) ≈ C·u0·√A0 / x, with A0 the outlet area and C ≈ 2.4. For the 3,100 CFM unit (Q = 1.463 m³/s, A0 ≈ 0.45 m² assumed from the grille envelope, u0 = 3.25 m/s, q = Q/A_cov = 0.0166 m/s) this gives κ(x) = u(x)/q ≈ 315/x: 157 at 2 m, 79 at 4 m, 52 at 6 m and 39 at 8 m. κ = 45 therefore corresponds to a throw of about 6.5 m, and using one value for both venues assumes the same throw distance: a 3–4 m bus shelter implies κ ≈ 80–105, a 6–8 m platform κ ≈ 39–52. We keep κ = 45 as the design value and test 30–60 in Section 5.1; no site calibration is available in this study.")
para("The humidity penalty is measured, not hypothetical. Field tests of misting at a semi-open bus stop lowered air temperature by a few tenths of a degree to about 1 °C while adding 0.5–1 g/kg of absolute humidity under low wind [15]; whether that feels cooler depends on the ratio of the two changes, which is exactly what the apparent-temperature form in Eq. 2 evaluates.")

h2("3.4 Spatial Cooling Efficiency (Eq. 3)")
para("η = (φ · N_eff · ΔT_eff) / (n · P_elec),   φ = min(1, n·A_cov/A_waiting).   (Eq. 3)")
para(f"η is a human-centric total (persons·°C per kW), not a per-person equipment efficiency. Because the denominator is the waiting zone rather than the platform, η and φ answer “how much of the area where people actually wait is cooled”, which is the quantity the operator controls.")

h2("3.5 Annualised Life-Cycle Cost (Eq. 4)")
para("LCC_annual = (1/L_life + r_om)·n·C_cap + H_yr·(n·P_elec·p_elec + (n·V_w/1000)·p_water).   (Eq. 4)")
para("V_w is not a free input. For an adiabatic evaporative process the water flow follows from the same energy balance that produces the temperature drop:")
para("V_w = 3600 · ṁ_da · c_p · ΔT_phys / L_v,   ṁ_da = Q_air·ρ_da,   (Eq. 8)")
para("with c_p = 1.006 kJ/(kg·K), L_v = 2,450 kJ/kg and ρ_da = p/(287·T). At the Phoenix design point a 3,100 CFM unit with an 11 °C drop requires about 25 L/h; at the Hong Kong design point the smaller drop requires about 6.6 L/h. Manufacturer tank/run-time rates (10.6–18.2 L/h) are treated as a sensitivity, because they are refill rates rather than measurements of evaporated water.")

h2("3.6 Water–Carbon Externality (Eq. 5)")
para("I_env = α_c(E_CO2/E_CO2,max) + α_w(W_eq/W_eq,max), with α_c = α_w = 0.50; E_CO2 = n·P_elec·H_yr·EF_grid; W_eq = (n·V_w/1000)·H_yr·BWS_raw.   (Eq. 5)")
para("Normalisers are computed separately for the bus shelters and for the rail platforms, over all one- and two-unit deployments of the four units (the same deployment set for both venue types). E is therefore comparable within a venue type, not across venue types; the paper never ranks a bus option against a rail option.")

h2("3.7 Safety Proxy and Decision Score (Eq. 6)")
para("E = w1·S_safe + w2·B − w3·LCC̃ − w4·I_env.   (Eq. 6)")
para("WBGT_proxy = 0.7 T_wb,zone + 0.3 T_zone; S_safe(W) = clamp((32 − W)/6, 0, 1); B = φ·N_eff·ΔT_eff / B_max; LCC̃ = LCC/LCC_max; baseline weights (w1,w2,w3,w4) = (0.30, 0.30, 0.20, 0.20).")
para("OSHA and CCOHS define the indoor index as WBGT = 0.7 T_nwb + 0.3 T_g [19,14], where T_nwb is the natural wet bulb, which responds to air speed. Our proxy replaces T_nwb with the psychrometric wet bulb and T_g with the dry bulb, so it is wind-blind by construction; Section 5.6 gives a sensitivity and the fan-beneficial limit.")
para("Two changes from a conventional weighted score matter. First, the safety term is graded over 26–32 °C with the 30 °C reference line at one third, so cooling below 30 °C still earns credit instead of saturating at zero cost. Second, safety is population-weighted: S_safe = φ·S_safe(W_zone) + (1−φ)·S_safe(W_ambient), so the share of occupants outside the jet is not ignored. The benefit term is proportional to persons, so the same 2 °C gain is worth more at a 45-person platform than at a 6-person shelter.")
para("A do-nothing option (φ = 0, ΔT = 0, zero cost) is evaluated with the same normalisers and compared with every configuration. E ranks units and configurations within a venue; it is not a compliance test, and the WBGT proxy is not ISO 7243 certification [3].")


# ---------------------------------------------------------------- section 4
h1("4. Model Application and Results (Q2–Q4)")
h2("4.1 Bus Stop Shelter Evaluation (Q2a)")
nd_bus = nd_E("PHX", "bus")
para(f"Table 3 reports the Q2a comparison at the Phoenix bus shelter. System A (0.25 kW fan) is the most efficient (η = {T3[0]['eta']:.2f} persons·°C/kW, E = {T3[0]['E']:.4f}), System B has E = {T3[1]['E']:.4f} and System C E = {T3[2]['E']:.4f}; the A/C efficiency ratio is {T3[0]['eta']/T3[2]['eta']:.1f}×. The do-nothing baseline scores {nd_bus:.4f}: it is below System A but above System B ({T3[1]['E']:.4f}) and System C ({T3[2]['E']:.4f}). Only System A is worth deploying; B and C are worse than doing nothing, so the Q2a recommendation rests on a genuine comparison. System A's cooled-zone proxy WBGT is {T3[0]['wbgt']:.2f} °C, below the 30 °C reference. The ranking is insensitive to the added assumptions: System A stays ahead of B for fan airflow above about 300 CFM and for capital up to $3,000.")
para("Table 3. Q2a comparison (Phoenix bus shelter, 30 °C, per-venue normalisers).", 8.5, italic=True)
table(["System", "P (kW)", "ΔT_eff (°C)", "φ", "η (persons·°C/kW)", "LCC (USD/yr)", "WBGT proxy (°C)", "E"], [
    [r["eq"], f"{r['P']:.3f}", f"{r['dT']:.3f}", f"{r['phi']:.3f}", f"{r['eta']:.2f}", f"{r['lcc']:.2f}", f"{r['wbgt']:.2f}", f"{r['E']:.4f}"] for r in T3
], widths=[1.3, 1.5, 1.8, 1.1, 3.0, 2.2, 2.2, 1.5], size=8)
para("Table 3b. Assumed Q2a parameter set: A 0.25 kW / 2,250 CFM / ΔT_nom 0 / C $250 / L 7 / r 3%; B 1.2 kW / 917 CFM / ΔT_nom 5 / C $750 / L 5 / r 8%; C 2.5 kW / 1,031 CFM / ΔT_nom 8 / C $1,277 / L 5 / r 8%. A_cov = A_waiting = 15 m², γ = 0.55, N_eff = 6.", 8.5)
para("Note: the “Energy Use” values in Requirement 2a are power ratings in kW (not kWh per hour); annual energy is obtained as P_elec × H_yr.", 8.5, italic=True)
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
para(f"Table 4 compares one- and two-unit deployments on the same normalisers and against the do-nothing baseline ({nd_rail_phx:.4f}). One MC61V covers the whole 120 m² waiting zone (φ = {phx61['phi']:.3f}) and scores E = {phx61['E']:.4f}; two MC37V also reach full coverage but cost about twice as much and score {phx2['E']:.4f}. Two units are not uniformly worse, however: a second Portacool raises E from {porta1['E']:.4f} to {porta2['E']:.4f} because it closes a coverage gap, while a second MC61V falls to {find(T4,'PHX','rail','MC61V',2)['E']:.4f} because the second unit adds cost without adding coverage.")
para(f"In Hong Kong the rail platform has no single dominant option: 1× MC37V ({hk37['E']:.4f}) is slightly ahead of 1× MC61V ({hk61['E']:.4f}) and 1× fan ({hkfan['E']:.4f}), but it covers only φ = {hk37['phi']:.3f} of the 128 m² platform. Two fans score {hk2fan['E']:.4f}, below one MC37V, because the extra unit doubles capital and water-free but carbon-heavy power without improving safety.")
para("Q2b revises the Q2a model in three ways. Q2a assumed one unit that covers a small shelter completely, but a rail waiting zone is 120 m² in Phoenix and 128 m² in Hong Kong, so coverage must be explicit. First, φ = min(1, n·A_cov/A_waiting) gives partial credit for partial coverage instead of assuming φ = 1. Second, the normalisers (B_max, LCC_max, E_CO2,max, W_eq,max) are computed per venue type, so E compares bus with bus and rail with rail instead of mixing a 6-person shelter with a 45-person platform. Third, safety is population-weighted, S_safe = φ·S(W_zone) + (1−φ)·S(W_ambient), so occupants outside the jet are counted. The revision changes the answer. With Q2a's full-coverage assumption the one- versus two-unit question is only a cost question; with explicit coverage, one MC61V covers the zone (φ = 1.000, E = 0.4026) while two MC37V cover it at higher cost (LCC $487.60 vs $397.41, E = 0.3635), and a second unit pays only when it closes a real gap (2× Portacool 0.2834 vs 1× 0.2686).")
para("Table 4. One- vs two-unit deployment at a rail platform (30 °C).", 8.5, italic=True)
table(["City", "Equipment", "n", "φ", "ΔT_eff (°C)", "LCC (USD/yr)", "WBGT proxy (°C)", "S_safe", "E"], [
    [r["city"], r["eq"], r["n"], f"{r['phi']:.3f}", f"{r['dT']:.3f}", f"{r['lcc']:.2f}", f"{r['wbgt']:.2f}", f"{r['S_safe']:.3f}", f"{r['E']:.4f}"] for r in T4
], widths=[1.2, 1.7, 0.8, 1.3, 1.8, 2.1, 2.0, 1.4, 1.5], size=7.5)
unc = (1 - hk37["phi"]) * 45
para(f"Table 4b makes the coverage assumption explicit for the Hong Kong platform. With 1× MC37V, φ = {hk37['phi']:.3f}, so {hk37['phi']*45:.0f} of the 45 waiting occupants are inside the cooled jet (proxy WBGT {hk37['wbgt']:.2f} °C) and {unc:.0f} are outside it, where the shaded ambient proxy is {hk37['wbgt_amb']:.2f} °C. The covered zone is below the 30 °C reference; the uncovered zone is not. The decision is therefore conditional: accept a partial solution with shade/windbreak for the uncovered occupants, or choose 1× MC61V for full coverage at higher cost.")
para("Table 4b. Covered vs uncovered exposure, Hong Kong platform, 1× MC37V.", 8.5, italic=True)
table(["Zone", "Persons", "WBGT proxy (°C)", "Below 30 °C?"], [
    [f"Covered zone (φ = {hk37['phi']:.3f})", f"{hk37['phi']*45:.0f}", f"{hk37['wbgt']:.2f}", "yes"],
    [f"Uncovered zone (1 − φ)", f"{unc:.0f}", f"{hk37['wbgt_amb']:.2f}", "no"],
], widths=[7.0, 2.4, 3.2, 3.2], size=8)

h2("4.3 Cross-Climate Comparison (Q3)")
para(f"Table 5 gives the 16-scenario matrix; E is comparable within each venue type. In Phoenix, evaporative cooling remains the best option in both venues: MC37V in bus shelters (E = {find(T5,'PHX','bus','MC37V',1)['E']:.4f}) and MC61V on platforms ({find(T5,'PHX','rail','MC61V',1)['E']:.4f}). In Hong Kong the bus shelter favours the drum fan ({find(T5,'HK','bus','Fan',1)['E']:.4f} vs {find(T5,'HK','bus','MC37V',1)['E']:.4f}), while the platform slightly favours MC37V ({find(T5,'HK','rail','MC37V',1)['E']:.4f} vs MC61V {find(T5,'HK','rail','MC61V',1)['E']:.4f}). The blanket statement that evaporative cooling fails in humid cities is therefore too strong: the climate effect is technology- and venue-specific.")
para("Which characteristics contribute most to efficient cooling? With the venue fixed, η is linear in coverage φ and in the number of beneficiaries N_eff, linear in the felt temperature drop ΔT_eff, and inversely proportional to electrical power. Three comparisons order the drivers. First, coverage and occupancy: a unit at φ = 1.000 is worth 36% more η than the same unit at φ = 0.733, and the 45-person platform has a 7.5× larger η than the 6-person shelter; E, however, is normalised within a venue, so N_eff cancels in the E ranking and affects the absolute service level and the break-even calculation rather than the within-venue order. Second, climate: at Phoenix's 41 °C / 18% the wet-bulb depression allows 4.4 °C of felt cooling in a shelter and 6.5 °C on a platform, whereas at Hong Kong's 32.5 °C / 78% the same units deliver 1.5–2.0 °C, about three times less. Third, device power: moving from 0.25 kW to 2.5 kW multiplies power tenfold but raises ΔT_eff only 1.7-fold, so η falls 5.8-fold. Coverage and occupancy therefore dominate the ranking, climate decides whether evaporative cooling works at all, and power is the least productive lever.")
para(f"At the 30 °C reference the Phoenix cooled-zone proxy is 25.3–26.5 °C and the uncovered platform proxy is {find(T5,'PHX','rail','MC37V',1)['wbgt_amb']:.2f} °C, so the exposure is modest. In Hong Kong the cooled-zone proxy is 29.6–29.8 °C, but the uncovered share sits at {find(T5,'HK','rail','MC37V',1)['wbgt_amb']:.2f} °C, so a “pass” applies to the cooled zone only. At 28 °C no Hong Kong option clears the reference in both zones, which is reported as a stricter stress test rather than a compliance result.")
para("Table 5. Sixteen-scenario cross-climate matrix (30 °C).", 8.5, italic=True)
table(["ID", "City", "Venue", "Equipment", "ΔT_eff", "φ", "η", "LCC", "I_env", "WBGT proxy", "E"], [
    [f"SC-{i:02d}", r["city"], r["venue"], r["eq"], f"{r['dT']:.3f}", f"{r['phi']:.3f}", f"{r['eta']:.2f}",
     f"{r['lcc']:.2f}", f"{r['I_env']:.4f}", f"{r['wbgt']:.2f}", f"{r['E']:.4f}"] for i, r in enumerate(T5, start=1)
], widths=[1.1, 1.1, 1.1, 1.6, 1.4, 1.2, 1.5, 1.7, 1.3, 1.7, 1.4], size=7.5)

para("Figure 3 shows the crossover at both design days: at 41 °C the rail crossover is 79.7%, just above Hong Kong's 78% RH, but at Hong Kong's own 32.5 °C the crossover falls to 76.7%, so 78% is above it and the fan delivers more felt cooling.")
figure("docs/figures/fig3_rh_crossover.png", "Figure 3. RH crossover at the two design days. (a) Phoenix 41 °C: bus crossover 69.6%, rail 79.7%. (b) Hong Kong 32.5 °C: bus 65.2%, rail 76.7%. Dotted lines mark the design-day RH (18% and 78%); the fan line is 2.081 °C.")

h2("4.4 Multi-Objective Trade-Offs (Q4)")
para(f"On the revised environmental baseline the fan has the lowest I_env in Phoenix ({find(T5,'PHX','bus','Fan',1)['I_env']:.4f}) but not in Hong Kong ({find(T5,'HK','bus','Fan',1)['I_env']:.4f} > MC37V {find(T5,'HK','bus','MC37V',1)['I_env']:.4f}), because Hong Kong's water stress is low (BWS 0.179 [4]) and the fan's higher power dominates the carbon term. 'Zero water = lower environmental burden' is therefore false in Hong Kong under Eq. 5; the claim should be limited to water consumption, not to the composite index.")
para("Figure 4 plots the 16 scenarios as eight cost–externality pairs; the two fan options nearly coincide near $132, so the inset separates them.")
figure("docs/figures/fig4_pareto.png", "Figure 4. LCC vs I_env trade-off. The 16 scenarios collapse to eight distinct cost–externality pairs; shape = city, fill = WBGT proxy at the 30 °C reference; the inset separates the two fan points that nearly coincide near $132. Labels mark the Phoenix points.", width_cm=12.2)
para(f"In Phoenix, MC61V has the highest I_env ({find(T5,'PHX','rail','MC61V',1)['I_env']:.4f}) and the highest water use, and 1× MC61V's LCC is ${find(T5,'PHX','rail','MC61V',1)['lcc']:.2f} vs ${find(T5,'PHX','rail','MC37V',1)['lcc']:.2f} for 1× MC37V. The trade-off is coverage vs cost/water, not cooling magnitude: all evaporative units deliver about 4.4 °C in bus shelters and 6.5 °C on platforms. The memorandum in Section 6.1 turns this into a decision rule.")


# ---------------------------------------------------------------- section 5
h1("5. Sensitivity Analysis and Model Evaluation")
h2("5.1 Parameter, Policy and Decision-Weight Sensitivity")

g_fix = R.norm([R.calc(c, v, e, n) for c in R.CITY for v in R.VENUE for e in R.EQUIPMENT for n in (1, 2)])
R.KAPPA = 60.0
e60_37 = R.score(R.calc("HK", "rail", "MC37V", 1), g_fix, threshold=30.0)[0]
e60_fan = R.score(R.calc("HK", "rail", "Fan", 1), g_fix, threshold=30.0)[0]
R.KAPPA = 45.0

R.WATER_MODE = "manufacturer"
t5_m, _ = R.table5_rows("pressure", 30.0, "B")
em_37 = find(t5_m, "HK", "rail", "MC37V", 1)["E"]
R.WATER_MODE = "balance"

para(f"Table 6 lists the winning unit for each COO weight profile. Under Balanced and Safety weights, Phoenix chooses MC37V at the bus shelter and MC61V on the platform; Hong Kong chooses the fan at the bus shelter and MC37V on the platform (MC61V under Safety, where full coverage and the higher safety term dominate). Under Cost weights Phoenix switches to the cheaper MC37V on the platform while Hong Kong keeps MC37V on the platform and the fan at the bus shelter; the Eco profile selects MC37V in all four cases, because the fan's water-free advantage is offset by its higher power and carbon term in Hong Kong.")
para("Table 6. Optimal equipment under four COO weight profiles (30 °C).", 8.5, italic=True)
t6rows = []
for name in ("Balanced", "Safety", "Cost", "Eco"):
    row = [name]
    for c, v in (("PHX", "bus"), ("PHX", "rail"), ("HK", "bus"), ("HK", "rail")):
        eq, sc = T6_30[(name, c, v)]
        row.append(f"{eq} ({sc:.3f})")
    t6rows.append(row)
table(["Profile", "Phoenix bus", "Phoenix rail", "HK bus", "HK rail"], t6rows, widths=[2.4, 3.1, 3.1, 3.0, 3.0], size=8)

t6b = []
for label, c, v, eq, n in (
    ("Phoenix bus — 1× MC37V", "PHX", "bus", "MC37V", 1),
    ("Phoenix rail — 1× MC61V", "PHX", "rail", "MC61V", 1),
    ("Hong Kong bus — 1× drum fan", "HK", "bus", "Fan", 1),
    ("Hong Kong rail — 1× MC37V", "HK", "rail", "MC37V", 1),
):
    r = find(T5, c, v, eq, n)
    share = r["phi"] * (1.0 if r["wbgt"] <= 28.0 else 0.0) + (1 - r["phi"]) * (1.0 if r["wbgt_amb"] <= 28.0 else 0.0)
    t6b.append([label, f"{r['wbgt']:.2f}", f"{r['wbgt_amb']:.2f}", f"{share:.0%}", "Pass" if share > 0.999 else "Fail"])
para("Table 6b. 28 °C non-acclimatised exposure check for the recommended options. S_safe is graded, so the 28 °C line is an exposure test rather than a second scoring run: it reports the share of waiting occupants whose zone stays at or below 28 °C.", 8.5, italic=True)
table(["Recommended option", "Zone WBGT (°C)", "Ambient WBGT (°C)", "Occupants ≤ 28 °C", "Check"], t6b, widths=[4.6, 2.6, 2.8, 3.0, 1.7], size=8)

para("Figure 5 shows the γ sweep (left) and the weight matrix (right); the sweep is steep, which is why γ is a lumped parameter tested over 0.20–0.75.")
figure("docs/figures/fig5_gamma_heatmap.png", "Figure 5. γ sweep and weight matrix. Left: η vs γ (0.20–0.75) for the Phoenix bus shelter with MC37V; dashed lines at γ = 0.30 and 0.55. Right: best unit and its score for each COO weight profile and city–venue.")
para(f"Sensitivity runs hold the per-venue normalisers fixed, so a change in E reflects the parameter rather than a rescaling. The jet-mixing coefficient is the largest single uncertainty on the Hong Kong platform, but it does not flip the rebuilt ranking: at κ = 60 MC37V still leads the fan ({e60_37:.4f} vs {e60_fan:.4f}); the fan overtakes only above κ ≈ 75, because the fan raises felt cooling without lowering the heat-index proxy. Using manufacturer water rates instead of the energy balance lowers the Hong Kong MC37V score to {em_37:.4f} and leaves the ordering unchanged. A black-globe offset of +3 K raises the proxy WBGT by 0.9 K; in the linear range this lowers S_safe by 0.15 (0.04 where the baseline is already saturated) and E by 0.045 (0.012), which does not reorder the units but weakens any claim of absolute safety. γ, ε, ΔT_nom, L_life, r_om and V_w each shift the near-ties by less than 0.05 E-points. A_cov is the exception: a 20% larger MC37V coverage raises Phoenix MC37V to 0.4325, above MC61V (0.3986), and the two are equal at about +8% (95 m² vs the nominal 88 m²). The Phoenix full-coverage recommendation therefore assumes the manufacturer area is not understated by more than about 8%. The full table is in Appendix B.")
para("The approximate proxy and the fixed design day are the main uncertainties. The 30 °C line is a benchmark, not a certification, and the ranking of near-ties should be read as “within model uncertainty” rather than as a field guarantee.")

h2("5.2 Hourly Weather Scenarios")
para("Table 7 repeats the comparison for nine hourly snapshots per day (11:00–19:00 inclusive; 828 = 92 days × 9) of June–August 2026, using the ERA5 0.25° grid (2 m temperature, 2 m dew point, 10 m wind scaled to 2 m, UTC converted to local time) and treating the nine snapshots as the eight-hour peak window. The design-day ranking is reproduced in the hottest decile: Phoenix chooses MC37V at the bus shelter and MC61V on the platform in every hottest hour, while cooler hours close the MC37V–MC61V gap. In Hong Kong the fan dominates the bus shelter (98% of device-hours) and the platform on average hours (80%), but MC37V wins 82% of the hottest platform hours. The do-nothing option wins most Hong Kong platform hours (93%) because the proxy WBGT stays below the reference, which argues for scheduling cooling for heat events rather than continuous summer operation.")
para("Table 7. Hourly robustness over 828 peak-window hours per city (device winner share).", 8.5, italic=True)
table(["Venue", "Device winner share", "Hottest 10% winner", "Do-nothing share"], [
    ["PHX bus", "MC37V 92% / Fan 8%", "MC37V 100%", "0%"],
    ["PHX rail", "MC37V 67% / MC61V 32% / Fan 2%", "MC61V 100%", "3%"],
    ["HK bus", "Fan 98% / MC37V 2%", "Fan 84% / MC37V 16%", "0%"],
    ["HK rail", "Fan 80% / MC37V 18% / MC61V 1%", "MC37V 82% / MC61V 13%", "93%"],
], widths=[2.4, 6.8, 4.6, 2.6], size=8)

h2("5.3 Joint Uncertainty")
para("Table 8 reports 1,000 joint draws (seed 20261115) over κ ~ U(30,60), γ ~ U(0.45,0.65) for bus and U(0.25,0.35) for rail, ε ~ U(0.70,0.90), ΔT_nom ~ U(8.8,13.2), life × U(0.7,1.3), maintenance × U(0.5,1.5), coverage × U(0.8,1.2), occupancy × U(0.8,1.2), water × U(0.7,1.3) and prices × U(0.8,1.2), with the normalisers recomputed inside each draw. The full-coverage Phoenix choice is probabilistic rather than certain: MC61V is best in 68% of draws, MC37V in 32%, and E(MC61V) > E(MC37V) in 68% of draws. The Hong Kong platform is more robust among devices — MC37V beats the fan in 98% and MC61V in 81% of draws — but the do-nothing option is best in 35% of draws, so deployment should be conditional on heat events. The bus-shelter choices are the most stable: MC37V 80% in Phoenix, fan 75% in Hong Kong, with Portacool taking the remaining 19% of Phoenix draws.")
para("Table 8. Joint uncertainty: probability that each option is best (1,000 draws).", 8.5, italic=True)
table(["Venue", "MC37V", "MC61V", "Portacool", "Fan", "Do nothing"], [
    ["PHX bus", "80%", "1%", "19%", "0%", "0%"],
    ["PHX rail", "32%", "68%", "0%", "0%", "0%"],
    ["HK bus", "25%", "0%", "0%", "75%", "0%"],
    ["HK rail", "55%", "10%", "0%", "0%", "35%"],
], widths=[2.4, 2.1, 2.1, 2.4, 2.0, 2.4], size=8)

h2("5.4 Calculation Checks and Plausibility")
para("These are calculation and plausibility checks, not a validation of the predicted cooling of a specific unit (Table 9). They confirm the arithmetic, the wet-bulb approximation, the safety scale and the water order of magnitude; none of them shows that the model would reproduce a measured ΔT_eff on a real platform.")
para("Table 9. Plausibility checks against independent values.", 8.5, italic=True)
table(["Check", "Model value", "Independent reference", "Reading"], [
    ["Wet bulb, 41 °C / 18%, 950 hPa", "21.8 °C", "22.6 °C (Stull, sea level) [1]", "0.8 K lower; a lower wet bulb lowers WBGT, so this is not conservative"],
    ["Annual LCC, 1× MC37V, Phoenix", "$243.80", "$243.9 by hand: capital $111.4 + energy $57.4 + water $75.1", "arithmetic closes"],
    ["WBGT proxy, Phoenix fan", "27.55 °C", "28 °C at 300 W (ISO 7243) [3]", "below the reference"],
    ["WBGT proxy, Hong Kong fan", "30.15 °C", "30 °C at 180 W (ISO 7243) [3]", "above; “fail” is consistent"],
    ["Water, 3,100 CFM / 11 °C", "25.1 L/h", "Manufacturer 10.6–18.2 L/h", "1.4–2.4× higher; ranking unchanged (5.1)"],
    ["Mist cooling, semi-open bus stop", "humidity penalty", "0.3–1 °C air drop, 0.5–1 g/kg [15]", "bounds the penalty, not the unit scale"],
], widths=[4.6, 2.6, 6.2, 3.4], size=7.5)
para("The largest discrepancy is water: the energy balance gives 25.1 L/h while manufacturer refill rates are 10.6–18.2 L/h. The model keeps the energy-balance value because it is physically tied to the temperature drop, and Section 5.1 shows that switching to manufacturer rates changes E by less than 0.01 and does not reorder the units. The field test of Kyogoku & Takebayashi [15] bounds the humidity penalty (0.3–1 °C air-temperature drop with 0.5–1 g/kg humidification); it is not a validation of the larger 3,100 CFM unit. No check in this section validates the absolute ΔT_eff at either site; that requires field measurement and is the main remaining gap.")
h2("5.5 Model Strengths, Limitations and Future Improvements")
para("Strengths: the six-equation chain is transparent; every number comes from one locked table; water is derived from the same energy balance as the temperature drop; the decision score is compared with a do-nothing baseline and separates the whole platform from the waiting zone.")
para("Two further scenarios change the decision, not just the score. Adding installation ($450 for a shelter, $900 for a platform, amortised over 10 years) and $150 per unit per year of labour lowers every E by 0.03–0.06. The Phoenix and Hong Kong bus-shelter rankings survive, but the Hong Kong platform reverses: MC37V falls to 0.0401, below the do-nothing baseline (0.0925). Because installation and labour are fixed, running the unit fewer hours does not restore the margin — at zero operating hours the score is 0.085, still below 0.0925 — so heat-event scheduling cannot rescue the platform device; it is recommended only if installation is shared or avoided. A 30% jet overlap between two units lowers the two-unit scores; 2× Portacool falls from 0.2834 to 0.1921 and no longer beats 1× Portacool (0.2686), so the “two units can pay” result holds only when the units are placed to limit overlap.")
para("Safety screen: only the Phoenix options keep every waiting occupant at or below the 30 °C proxy (ambient 27.55 °C); in Hong Kong the uncovered share is 30.15 °C for every device, so no device alone meets an all-occupant screen. Hong Kong recommendations are therefore conditional on shade and windbreak first, and the device comparison there is a comparison of partial solutions, not of compliant ones.")
para("Limitations: the drum fan is a hypothetical benchmark; κ, γ, ε, ΔT_nom, L_life, r_om and N_eff remain assumptions; the heat index is an approximate proxy built from dry- and wet-bulb values with no globe or solar term, so it is not ISO 7243 compliance (CCOHS) [14]; the design-day tables use one representative day, while Section 5.2 tests 828 hourly scenarios, and a multi-year TMY remains future work; the multi-unit model adds nominal coverage areas rather than modelling the union of overlapping jets; and visitor experience is proxied by felt temperature and the graded safety term, while noise, humidity comfort and aesthetics are not modelled. Structural limits remain: Eq. 2 is wind-neutral, and Section 5.6 adds the flight-effect correction; the Hong Kong platform margin disappears above about 3.7 m/s; the WBGT proxy gives a fan no safety credit for air speed while an evaporative unit is credited for its temperature drop, which favours evaporative cooling in E; κ is a lumped, uncalibrated coefficient (the Hong Kong order holds to κ ≈ 75); γ is a lumped design assumption rather than a geometric derivation, so the bus/rail difference is not measured; manufacturer coverage areas are treated as effective areas (a +8% effective MC37V area flips the Phoenix platform choice); and no field measurement of ΔT_eff exists at either site; the Hong Kong geometry is a generic side-platform measurement (Open3Dhk), not a named stop. The water rate also mixes a rated-airflow energy balance with manufacturer refill rates (25.1 vs 10.6–18.2 L/h); the model does not enforce a common operating point for airflow, ΔT and water. Closing these gaps would require field calibration of κ and γ, measured water flow, a multi-year TMY/HKO series and a two-unit deployment with independent placement; none of these data are claimed in this paper.")


h2("5.6 Crosswind, Fan Limits and the Joint Operating Point")
para("Equation 2 is wind-neutral: v_amb appears in both AT_amb and AT_zone and cancels. To restore a wind dependence we follow the flight-effect correction of von Glahn [16], F(v) = 1 + 0.9·AR^(1/3)·(v/u_j)^(3/2), and normalise it at the design wind v_ref = 1.5 m/s so the baseline tables are unchanged: γ_eff(v) = 1 − (1−γ0)·F(v_ref)/F(v). AR is the assumed outlet aspect ratio (1.25 for MC37V, 1.6 for MC61V, 1.0 for Portacool, 1.7 for the drum fan) and u_j = Q/A0; this is an idealized scenario, not a measured wind response.")
para("Table 10. Idealized crosswind scenario: E with the flight-effect correction (Balanced weights, fixed normalisers).", 8.5, italic=True)
table(["v_amb (m/s)", "HK rail MC37V", "HK rail fan", "PHX rail MC61V", "PHX bus MC37V", "HK rail winner"], [
    ["1.5 (design)", "0.1005", "0.0744", "0.4026", "0.4743", "MC37V"],
    ["3.0", "0.0809", "0.0744", "0.3385", "0.3745", "MC37V (margin 0.007)"],
    ["5.0", "0.0650", "0.0744", "0.2592", "0.2932", "Fan"],
], widths=[2.6, 3.0, 2.8, 3.0, 2.8, 3.8], size=8)
para("At the design wind the baseline is recovered. At v = 3 m/s the Hong Kong platform margin falls from 0.026 to 0.007, and the fan overtakes at about 3.7 m/s; the Phoenix recommendations are unchanged. The CBE fans-and-heat map [18] places 32.5 °C / 78% in the fan-beneficial band and excludes conditions above 40 °C, so the zero fan credit in Eq. 6 is conservative at the Hong Kong design point and appropriate at Phoenix's 41 °C. An assumed wind correction of the natural wet bulb (c_w = 0.15 K per m/s, a sensitivity rather than a measurement; [19]) raises the Hong Kong fan from 0.0744 to 0.0888 but leaves MC37V ahead (0.1084).")
para("The water balance and the manufacturer data are not the same operating point. Table 11 gives the ratio of the energy-balance rate to the manufacturer refill rate; it is about 2.35 in Phoenix and 0.62 in Hong Kong. We therefore treat V_w as an interval [0.8, 1.2] × manufacturer and report the E range; using the manufacturer value changes the Hong Kong platform MC37V score from 0.1005 to 0.0914 without reordering the units.")
para("Table 11. Energy-balance water vs manufacturer refill rate.", 8.5, italic=True)
table(["City / unit", "Balance (L/h)", "Manufacturer (L/h)", "Ratio"], [
    ["Phoenix MC37V", "25.1", "10.6", "2.36"],
    ["Phoenix MC61V", "42.8", "18.2", "2.35"],
    ["Phoenix Portacool", "19.4", "11.4", "1.70"],
    ["Hong Kong MC37V", "6.6", "10.6", "0.62"],
    ["Hong Kong MC61V", "11.3", "18.2", "0.62"],
    ["Hong Kong Portacool", "5.1", "11.4", "0.45"],
], widths=[4.4, 3.6, 4.2, 2.6], size=8)
para("These checks do not change the main recommendations; they define the conditions under which the Hong Kong platform margin disappears: crosswind at or above about 4 m/s, or full installation and labour costs.")

# ---------------------------------------------------------------- section 6
h1("6. Decision Memorandum, Public Blog and References")
h2("6.1 Executive Memorandum to the COO (Q5a)")
para("MEMORANDUM — TO: Chief Operating Officer; FROM: Modelling team; DATE: November 2026; SUBJECT: Climate-matched cooling for semi-open transit spaces.")
para("Scope: this memorandum is about our chosen venue, the Phoenix rail platform. Table 6c and the closing paragraph record the other three venue–city cases as comparisons.")
para(f"Recommendation: size for coverage first, then choose the smallest unit that achieves it, and always compare against doing nothing. The do-nothing baseline scores {nd_E('PHX','bus'):.3f} in Phoenix and {nd_E('HK','bus'):.3f} in Hong Kong; every Phoenix recommendation and the Hong Kong bus-shelter fan beat it, but the Hong Kong platform margin is only 0.008 and reverses under full installation costs.")
para(f"For Phoenix, deploy 1× Hessaire MC61V per 120 m² waiting zone: φ = {phx61['phi']:.2f}, ΔT_eff = {phx61['dT']:.2f} °C, proxy WBGT = {phx61['wbgt']:.2f} °C, LCC = ${phx61['lcc']:.2f}/station/yr and E = {phx61['E']:.4f}; if capital and water budgets bind and partial coverage is acceptable, 1× MC37V gives E = {phx37['E']:.4f} at ${phx37['lcc']:.2f} for 73% coverage. Do not deploy 2× MC61V: it doubles cost without improving coverage.")
para(f"For the Hong Kong platform, shade and windbreak come first: with 1× MC37V the covered zone is below the 30 °C proxy but the uncovered share is 30.15 °C, so no device alone meets the screen. At baseline cost MC37V (E = {hk37['E']:.4f}, ${hk37['lcc']:.2f}, φ = {hk37['phi']:.2f}) edges MC61V (E = {hk61['E']:.4f}) and the fan (E = {find(T5,'HK','rail','Fan',1)['E']:.4f}), but the margin over doing nothing is 0.008 and the device falls to 0.0401 once installation and labour are charged. Install a unit only if installation is shared or avoided, and re-check after a season of logged heat hours. At 15 m² bus shelters, use 1× drum fan (E = {find(T5,'HK','bus','Fan',1)['E']:.4f} vs {find(T5,'HK','bus','MC37V',1)['E']:.4f}) with a humidity interlock. The 36-inch unit is a hypothetical benchmark; if it cannot be sourced, use 1× MC37V (E = 0.1364) or an equivalent 10,500 CFM fan and re-run the trade-off.")
para("Deployment timing: heat-event scheduling helps the bus shelters but cannot rescue the Hong Kong platform, because fixed costs dominate; the Phoenix platform choice switches to MC61V in the hottest decile, and most Hong Kong platform hours are already below the reference.")
para(f"Network: Phoenix 38 stations × ${phx61['lcc']:.2f} = ${38*phx61['lcc']:,.0f}/yr; the Hong Kong bus-shelter roll-out covers 68 stops with the fan; the platform case is deferred pending installation-cost sharing. Action plan: (1) shade and windbreak retrofits first (γ 0.55 → 0.30); (2) humidity interlock set from the local crossover (about 70% at 41 °C, about 65% at 32.5 °C); (3) meter water on evaporative units; (4) pilot 1× MC61V vs 1× MC37V on two Phoenix platforms; (5) re-check the Hong Kong platform choice after measuring κ on site.")
para("Table 6c. Memorandum decision table (30 °C).", 8.5, italic=True)
table(["City", "Venue", "Recommended", "φ", "LCC (USD/yr)", "E", "Do-nothing E"], [
    ["Phoenix", "Bus shelter", "1× MC37V", f"{find(T5,'PHX','bus','MC37V',1)['phi']:.2f}", f"{find(T5,'PHX','bus','MC37V',1)['lcc']:.2f}", f"{find(T5,'PHX','bus','MC37V',1)['E']:.4f}", f"{nd_E('PHX','bus'):.4f}"],
    ["Phoenix", "Platform", "1× MC61V", f"{phx61['phi']:.2f}", f"{phx61['lcc']:.2f}", f"{phx61['E']:.4f}", f"{nd_E('PHX','rail'):.4f}"],
    ["Hong Kong", "Bus shelter", "1× drum fan", f"{find(T5,'HK','bus','Fan',1)['phi']:.2f}", f"{find(T5,'HK','bus','Fan',1)['lcc']:.2f}", f"{find(T5,'HK','bus','Fan',1)['E']:.4f}", f"{nd_E('HK','bus'):.4f}"],
    ["Hong Kong", "Platform", "Shade/windbreak; device if shared", f"{hk37['phi']:.2f}", f"{hk37['lcc']:.2f}", f"{hk37['E']:.4f}", f"{nd_E('HK','rail'):.4f}"],
], widths=[1.8, 2.2, 2.6, 1.2, 2.4, 1.6, 2.2], size=8)
para("Note: E and LCC are baseline-cost values; with installation ($900, 10-year) and labour ($150/yr), the Hong Kong platform device falls to E = 0.0401, below the 0.0925 do-nothing baseline, so the platform row is conditional on shared installation.", 8.5, italic=True)

h2("6.2 Public-Facing Blog Post (Q5b)")
para("Why misting fans feel great in Phoenix — but change little in Hong Kong (and what your commute needs instead).")
phx_bus = find(T5, "PHX", "bus", "MC37V", 1)
hk_bus37 = find(T5, "HK", "bus", "MC37V", 1)
hk_busfan = find(T5, "HK", "bus", "Fan", 1)
para(f"Here is the question we started with: how much cooling do we actually get for the electricity we spend? The answer is a ratio, not a temperature. We count the people who feel cooler, multiply by the degrees they feel, and divide by the kilowatts: persons·°C per kW. In Phoenix, one 0.25 kW MC37V delivers about {phx_bus['eta']:.0f} persons·°C per kW at a bus shelter. In Hong Kong, the same unit delivers about {hk_bus37['eta']:.0f}, and a 36-inch fan about {hk_busfan['eta']:.0f} — roughly three times less cooling for the same electricity, because humid air refuses to evaporate much water.")
para("In Phoenix's 41 °C / 18% air, water evaporates readily. The cooler lowers the air by up to 11 °C before mixing and boundary losses, and a waiting passenger feels about 4.4 °C cooler; the unit uses about 100 litres of water per kilowatt-hour, which costs money and stresses a dry city.")
para(f"In Hong Kong's 32.5 °C / 78% air, the air is already close to saturation. The wet-bulb depression is small, so the same cooler lowers the air by only about 2.7 °C and a passenger feels about {hk_bus37['dT']:.1f} °C cooler; a fan, which spends its energy moving air rather than evaporating water, feels about {hk_busfan['dT']:.1f} °C cooler and uses no water at all. That is why the bus shelter in Hong Kong favours the fan even though the fan draws 0.35 kW, more than the cooler's 0.25 kW.")
para("The trade-off is not only comfort. On the Hong Kong rail platform the evaporative unit is slightly ahead on paper (E 0.1005 vs 0.0744), but it covers only 69% of the waiting area and, once installation and labour are counted, doing nothing plus shade scores higher (0.0925 vs 0.0401). The platform therefore needs shade and a windbreak first; a unit is justified only if installation is shared. Water and carbon pull in opposite directions: the fan uses no water but more electricity per degree of felt cooling.")
para("The practical rule is simple: shade first, windbreak second, then match the machine to the climate. In dry heat, evaporative cooling is worth its water; in humid heat, moving air is usually the better buy. Ask your city to meter the water and the electricity on a pilot unit before it scales either option — that is the number that settles the argument.")
para(f"At a 128 m² platform the comparison is close on cooling alone: one MC37V (${hk37['lcc']:.2f}, E {hk37['E']:.4f}) slightly beats one fan ({hkfan['lcc']:.2f}, E {hkfan['E']:.4f}), and two fans (E {hk2fan['E']:.4f}) lose to one MC37V. The cost and coverage caveats above decide the deployment, not the cooling difference.")

para("Figure 6 turns the two recommendation panels into a public-facing comparison: what a passenger feels, what the water costs, and what the city pays.")
figure("docs/figures/fig6_infographic.png", "Figure 6. Public-facing infographic: Phoenix and Hong Kong side by side (felt cooling, water, cost, and the shade → windbreak → machine rule), no equations.")

h2("6.3 References")
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
para("Tools and versions: DeepSeek Harness (deepseek-flash model) in an agent interface; Python 3.12 with standard libraries for the recomputation, NumPy 2.5 and Matplotlib 3.11 for the figures, python-docx 1.2 for document assembly, and WPS Writer/LibreOffice for PDF export.")


# ---------------------------------------------------------------- appendix
h1("Appendix A. Data and Assumption Register")
para("Status: S = sourced, D = derived, A = assumption, U = unverified. Sources are listed in Section 6.3; derived values follow Eq. 8.", 9)
para("Table A1. Data and assumption register.", 8.5, italic=True)
table(["Parameter", "Value", "Status", "Source / note"], [
    ["Phoenix T_db / RH", "41.0 °C / 18%", "D/A", "ERA5 2026 Jun–Aug; typical daily max"],
    ["Hong Kong T_db / RH", "32.5 °C / 78%", "D/A", "ERA5; typical daily max"],
    ["Wet bulb", "21.8 / 29.1 °C", "D", "Pressure-corrected at 950/1,000 hPa"],
    ["Phoenix p_elec", "0.1595 USD/kWh", "D", "APS E-32 2024: energy + 6-month demand"],
    ["Hong Kong p_elec", "0.1923 USD/kWh", "D", "CLP 2026: 150 cents/unit ÷ 7.8"],
    ["Phoenix p_water", "2.0766 USD/m³", "D", "2024 inside-city card; excludes sewer/tax"],
    ["Hong Kong p_water", "0.9615 USD/m³", "D", "WSD 4.58 + 2.92 ÷ 7.8"],
    ["A_platform", "425 / 128 m²", "D", "Valley Metro design criteria; HK LRT measured"],
    ["A_waiting", "120 / 128 m²", "D/A", "Phoenix shaded boarding zone; HK whole platform"],
    ["κ (dimensionless)", "45", "A", "Assumed 45; sensitivity 30–60; not measured"],
    ["γ (bus / rail)", "0.55 / 0.30", "A", "Urban ventilation ranges; swept 0.20–0.75"],
    ["ε", "0.80", "A", "Data pack: no manufacturer guarantee; 0.70–0.90"],
    ["ΔT_nom", "11.0 °C", "A", "Assumed maximum drop; 8.8–13.2"],
    ["V_w", "derived", "D", "Adiabatic mass balance, Eq. 8; manufacturer rates as sensitivity"],
    ["L_life / r_om", "5–7 yr / 3–8%", "A", "No published service data"],
    ["N_eff", "6 / 45", "A", "Peak occupancy assumption"],
    ["Phoenix stations", "38", "S", "NTD 71 facilities ≠ stations"],
], widths=[3.8, 4.4, 1.3, 7.0], size=8)
para("Source details: MC37V https://www.homedepot.com/p/Hessaire-3-100-CFM-3-Speed-Portable-Evaporative-Cooler-Swamp-Cooler-for-950-sq-ft-MC37V/304078772; MC61V https://hessaire.com/mobile-cooling/5300-cfm-mobile-cooler (price: https://www.sylvane.com/products/hessaire-mc61v-evaporative-air-cooler); Portacool catalog https://portacool.com/wp-content/uploads/2025/02/Portacool-Catalog_Jetstream_Industrial-Automotive-2023Reduced.pdf; Aqueduct Phoenix aqid 1628 / pfaf 772221 / string 772221-USA.3_1-1628 (33.44823 N, −112.075098), bws 2.482; Hong Kong sub-basins HKG.1_1 / HKG.10_1 / HKG.11_1, bws 0.179; Siu Hong stop coordinates from MTR route data and OpenStreetMap; Phoenix station profiles from the Valley Metro TOD PDF.", 8.5)


doc.add_page_break()
h1("Appendix B. Single-Factor Sensitivity")
para("Table B1 repeats the single-factor runs behind Section 5.1 with the baseline normalisers fixed. Each row changes one input by the stated amount; all other inputs stay at their baseline values. E is comparable only within a venue type.")
para("Table B1. Single-factor sensitivity of E (baseline normalisers).", 8.5, italic=True)
table(["Variation", "PHX 1x37", "PHX 1x61", "HK 1x37", "HK 1xfan"], [
    ["BASE", "0.3808", "0.4026", "0.1005", "0.0744"],
    ["epsilon 0.70", "0.3808", "0.4026", "0.0926", "0.0744"],
    ["epsilon 0.90", "0.3808", "0.4026", "0.1084", "0.0744"],
    ["dTnom 8.8", "0.3501", "0.3641", "0.1005", "0.0744"],
    ["dTnom 13.2", "0.4115", "0.4412", "0.1005", "0.0744"],
    ["L_life -30%", "0.3722", "0.3895", "0.0919", "0.0698"],
    ["L_life +30%", "0.3854", "0.4097", "0.1051", "0.0769"],
    ["r_om -50%", "0.3848", "0.4088", "0.1045", "0.0754"],
    ["r_om +50%", "0.3768", "0.3965", "0.0965", "0.0735"],
    ["p_elec -20%", "0.3837", "0.4076", "0.1034", "0.0785"],
    ["p_elec +20%", "0.3779", "0.3977", "0.0976", "0.0704"],
    ["p_water -50%", "0.3902", "0.4187", "0.1014", "0.0744"],
    ["p_water +50%", "0.3713", "0.3865", "0.0995", "0.0744"],
    ["H_yr -20%", "0.3987", "0.4334", "0.1097", "0.0866"],
    ["H_yr +20%", "0.3628", "0.3719", "0.0913", "0.0622"],
    ["kappa 30", "0.3749", "0.3945", "0.0950", "0.0558"],
    ["kappa 60", "0.3866", "0.4107", "0.1060", "0.0930"],
    ["gamma -0.10", "0.4096", "0.4419", "0.1098", "0.0744"],
    ["gamma +0.10", "0.3520", "0.3634", "0.0911", "0.0744"],
    ["A_cov -20%", "0.3291", "0.4036", "0.0874", "0.0744"],
    ["A_cov +20%", "0.4325", "0.3986", "0.1136", "0.0744"],
    ["BWS_HK 0.850", "0.3808", "0.4026", "0.0987", "0.0744"],
    ["EF_HK 0.465", "0.3808", "0.4026", "0.0949", "0.0666"],
    ["EF_PHX 0.25", "0.3855", "0.4108", "0.1005", "0.0744"],
    ["EF_PHX 0.36", "0.3757", "0.3939", "0.1005", "0.0744"],
], widths=[4.6, 2.7, 2.7, 2.7, 2.7], size=7.8)

for _p in doc.paragraphs:
    _t = _p.text.strip()
    if _t.startswith("Table ") and _p.runs and _p.runs[0].italic:
        _p.paragraph_format.keep_with_next = True

doc.save(OUT)
print("saved", OUT)
