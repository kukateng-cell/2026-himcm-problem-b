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

OUT = "2026_HiMCM_ProblemB_Full_Paper_v1.0.docx"

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
    p.add_run().add_picture(path, width=Cm(width_cm))
    cp = doc.add_paragraph()
    cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cp.paragraph_format.space_after = Pt(8)
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
r = p.add_run("Team [Team Number]   |   November 2026"); set_font(r, 11)
doc.add_page_break()

# ---------------------------------------------------------------- summary
h1("Summary Sheet")
para("Public cooling is usually judged by kilowatt-hours, but energy alone cannot separate a working system from a failing one. An open freezer and a semi-open transit shelter share the same physics: cold air is produced inside a boundary and leaks through an opening, so the useful cooling delivered to the people inside — not the electricity drawn — is what should be counted. We build a six-equation model and apply it to a 15 m² bus shelter and a rail platform in Phoenix (41 °C / 18% RH) and Hong Kong (32.5 °C / 78% RH).")
para(f"Eqs. 1–2 give the thermodynamic cooling and its apparent-temperature effect; Eq. 3 converts them into η, in persons·°C per kW; Eq. 4 prices the life-cycle cost after the cooling water is derived from an adiabatic mass balance; Eq. 5 prices the water–carbon externality; Eq. 6 combines a graded heat-safety proxy, a persons-weighted cooling benefit, cost and environment. Coverage is measured against the modelled waiting zone (120 m² in Phoenix, 128 m² in Hong Kong), not the whole platform (425 m² and 128 m²), and every result is compared with a do-nothing baseline.")
para(f"The model reverses two intuitions and corrects a third. In Q2a the 0.25 kW fan is {T3[0]['eta']:.1f} times more efficient than the 2.5 kW cooler (η = {T3[0]['eta']:.2f} vs {T3[2]['eta']:.2f}), because extra power buys little extra cooling. In Q2b, at a Phoenix platform 1× MC61V scores E = {find(T4,'PHX','rail','MC61V',1)['E']:.4f} and covers the waiting zone, while 2× MC37V scores {find(T4,'PHX','rail','MC37V',2)['E']:.4f} at twice the capital cost; a second small unit can still pay when it closes a coverage gap (2× Portacool {find(T4,'PHX','rail','Porta',2)['E']:.4f} vs 1× {find(T4,'PHX','rail','Porta',1)['E']:.4f}). In Hong Kong the bus shelter favours the drum fan (E = {find(T5,'HK','bus','Fan',1)['E']:.4f} vs {find(T5,'HK','bus','MC37V',1)['E']:.4f} for MC37V), while the rail station is a near-tie that favours MC37V ({find(T5,'HK','rail','MC37V',1)['E']:.4f} vs {find(T5,'HK','rail','MC61V',1)['E']:.4f}).")
para(f"A do-nothing baseline is reported throughout: its score is {nd_E('PHX','bus'):.4f} in Phoenix and {nd_E('HK','bus'):.4f} in Hong Kong, below every recommended unit, so the recommendations are no longer artefacts of ignoring the alternative. Water use is not a free assumption: at rated airflow a 11 °C drop on 3,100 CFM requires about 25 L/h, roughly double the tank-based rate often quoted, and this cost is carried through Eq. 4 and Eq. 5.")
para("Recommendations: size for coverage first, then minimise cost and environmental burden. In Phoenix, 1× MC37V at the bus shelter and 1× MC61V at the platform; in Hong Kong, 1× drum fan at bus shelters and 1× MC37V at the platform, with shade or windbreak for the occupants outside the jet. Limitations: the drum fan is a hypothetical benchmark, several parameters remain assumptions, the heat index is an approximate WBGT proxy rather than a compliance measurement, and the ranking of near-ties is sensitive to the jet-mixing coefficient.")
doc.add_page_break()

# ---------------------------------------------------------------- TOC (page numbers filled after layout)
h1("Table of Contents")
toc = [
    ("Summary Sheet", "2"),
    ("1. Understanding the Problem (Q1)", "4"),
    ("2. Assumptions and Justifications", "5"),
    ("3. Mathematical Model", "6"),
    ("   3.1 Parameter Baselines", "6"),
    ("   3.2 Thermodynamic Cooling Constraint (Eq. 1)", "8"),
    ("   3.3 Apparent Temperature and Jet Velocity (Eq. 2)", "8"),
    ("   3.4 Spatial Cooling Efficiency (Eq. 3)", "8"),
    ("   3.5 Annualised Life-Cycle Cost (Eq. 4)", "8"),
    ("   3.6 Water–Carbon Externality (Eq. 5)", "8"),
    ("   3.7 Safety Proxy and Decision Score (Eq. 6)", "8"),
    ("4. Model Application and Results (Q2–Q4)", "10"),
    ("   4.1 Bus Stop Shelter (Q2a)", "10"),
    ("   4.2 Rail Platform and Multi-Unit Scaling (Q2b)", "10"),
    ("   4.3 Cross-Climate Comparison (Q3)", "11"),
    ("   4.4 Multi-Objective Trade-Offs (Q4)", "12"),
    ("5. Sensitivity Analysis and Model Evaluation", "14"),
    ("6. Decision Memorandum, Public Blog and References", "16"),
    ("AI Use Report", "18"),
    ("Appendix A. Data and Assumption Register", "19"),
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
     "The zone velocity is v_eff = v_amb + κ(Q_air/A_cov), with κ = 45 (dimensionless momentum amplification, sensitivity 30–60); κ is a calibration coefficient for jet mixing, not a physical velocity. Commuters are uniformly distributed, so beneficiaries scale with φ = min(1, n·A_cov/A_waiting), with N_eff = 6 (bus) and 45 (rail)."),
    ("Assumption 5 — Commercial tariffs and straight-line depreciation.",
     "Capital costs depreciate linearly over L = 5–7 years and annual maintenance is r_om = 3–8% of capital. Energy uses the latest local tariffs (Phoenix 2024 APS E-32 with demand; Hong Kong 2026 CLP) and water the City of Phoenix 2024 card and the Hong Kong WSD schedule; the 2026 Phoenix scenario and the Hong Kong 50% water concession are tested separately."),
    ("Assumption 6 — Shaded conditions and an approximate heat index.",
     "Both venue types provide overhead shading, so the heat index is the proxy WBGT ≈ 0.7 T_wb + 0.3 T_db (ISO 7243 no-solar-load form, with the natural wet bulb approximated by the psychrometric wet bulb and the globe temperature by the dry-bulb). This is an index approximation, not a compliance measurement; the 30 °C reference is used as a graded benchmark (Section 3.7) and 28 °C as a stricter sensitivity. Black-globe offsets of +3 and +6 K are tested in Section 5."),
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
    ["4 Jet mixing, occupancy", "2–3", "κ dimensionless, calibrated; N_eff assumed"],
    ["5 Tariffs and depreciation", "4–5", "APS/CLP/WSD; L, r_om assumed"],
    ["6 Shaded proxy WBGT", "6", "Approximate index; 30 °C reference, 28 °C sensitivity"],
], widths=[5.6, 3.0, 7.4], size=8)
doc.add_page_break()

# ---------------------------------------------------------------- section 3
h1("3. Mathematical Model")
h2("3.1 Parameter Baselines")
para("Table 2A lists the four commercial benchmark units. Status codes: S = sourced, D = derived, A = assumption, U = unverified. The 36-inch drum fan has no product source and is treated as a hypothetical benchmark. Water use is not listed as a free parameter: it is derived from the energy balance in Eq. 4 (Section 3.5) and the values in the table are the resulting design-point rates.")
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
    ["Hong Kong rail platform", "128", "128", "0.30", "45", "D: measured side platform ≈ 32 m × 4 m (Open3Dhk)"],
], widths=[3.8, 2.6, 2.6, 1.2, 1.2, 6.0], size=7.5)

h3("3.1.1 Transit Network Basis")
para("Valley Metro Rail's 2023 NTD profile reports 71 facilities and 29,846 average weekday unlinked trips; the 71 figure is a facility count, not a station count (about 38 stations in 2024), so network costs in Section 6 use 38 stations. The 12th St & Washington/Jefferson profile reports 384 weekday boardings (208 + 176) and 27,462 full-system weekday boardings. Valley Metro's design criteria set a 280 ft (85.3 m) calculated platform with a 16 ft 4 in (4.98 m) minimum centre-platform width, a peak 12-minute boarding/alighting design load at 7 ft² (0.65 m²) per person, and a 1.0% cross slope (Ch. 6.3.1–6.3.5). The South Central Extension/Downtown Hub opened on 7 June 2025 with eight new stations and a 12-minute weekday headway (20 minutes after 19:00; 15/20 minutes on Saturday; 20 minutes on Sunday; 365 days, about 20 h/day). The 2024 count of 38 stations is kept for the network-cost illustration so that station count, tariffs and ridership share the same 2024 basis; the 2026 system has about 46 stations. Hong Kong's Light Rail has 68 unique stops on 11 lines, with 439,200 daily journeys in March 2026; five routes (505, 507, 614, 614P, 751) run 6–18 min peak headways. 149 LRVs and 3.90 million daily bus journeys are marked U because the PDF text layer is unreliable and the figures need a page-level check.")
figure("docs/figures/fig1_system.png", "Figure 1. System boundary and Eq. 1→6 coupling. Left: semi-open venue cross-section with the cold jet, lateral escape γ and coverage φ. Right: the Eq. 1→2→3→(4,5)→6 chain, grouped into thermodynamics, economics/externality and safety/decision.")
doc.add_page_break()

h2("3.2 Thermodynamic Cooling Constraint (Eq. 1)")
para("ΔT_phys = min(ΔT_nom, ε(T_db − T_wb)).   (Eq. 1)")
para("T_wb is solved from the psychrometric relation at surface pressure p_s: e_s(T_wb) − γ_p(T_db − T_wb) = e_amb, where γ_p = 1.006 p_s /(0.622 × 2,450) hPa/K. At 41 °C/18% and 950 hPa this gives 21.8 °C; at 32.5 °C/78% and 1,000 hPa it gives 29.1 °C. For pure fans ε = 0 and ΔT_phys = 0.")

h2("3.3 Apparent Temperature and Jet Velocity Coupling (Eq. 2)")
para("ΔT_eff = AT(T_db, e_amb, v_amb) − AT(T_zone, e_zone, v_eff),   AT(T,e,v) = T + 0.33e − 0.70v − 4.00.   (Eq. 2)")
para("T_zone = T_db − (1−γ)ΔT_phys; e_zone = min(e_s(T_zone), e_amb + 0.665(1−γ)ΔT_phys); v_eff = v_amb + κ(Q_air/A_cov), with Q_air = CFM × 1.699/3600 m³/s. κ = 45 is a dimensionless momentum-amplification coefficient, not a velocity: Q_air/A_cov already has units of m/s, and κ is calibrated from jet-mixing experiments (sensitivity 30–60).")
para("The humidity penalty is measured, not hypothetical. Field tests of misting at a semi-open bus stop lowered air temperature by a few tenths of a degree to about 1 °C while adding 0.5–1 g/kg of absolute humidity under low wind (Kyogoku & Takebayashi, 2023); whether that feels cooler depends on the ratio of the two changes, which is exactly what the apparent-temperature form in Eq. 2 evaluates.")

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
para("Two changes from a conventional weighted score matter. First, the safety term is graded over 26–32 °C with the 30 °C reference line at one third, so cooling below 30 °C still earns credit instead of saturating at zero cost. Second, safety is population-weighted: S_safe = φ·S_safe(W_zone) + (1−φ)·S_safe(W_ambient), so the share of occupants outside the jet is not ignored. The benefit term is proportional to persons, so the same 2 °C gain is worth more at a 45-person platform than at a 6-person shelter.")
para("A do-nothing option (φ = 0, ΔT = 0, zero cost) is evaluated with the same normalisers and compared with every configuration. E ranks units and configurations within a venue; it is not a compliance test, and the WBGT proxy is not ISO 7243 certification.")
doc.add_page_break()

# ---------------------------------------------------------------- section 4
h1("4. Model Application and Results (Q2–Q4)")
h2("4.1 Bus Stop Shelter Evaluation (Q2a)")
nd_bus = nd_E("PHX", "bus")
para(f"Table 3 reports the Q2a comparison at the Phoenix bus shelter. System A (0.25 kW fan) is the most efficient (η = {T3[0]['eta']:.2f} persons·°C/kW, E = {T3[0]['E']:.4f}), System B has E = {T3[1]['E']:.4f} and System C E = {T3[2]['E']:.4f}; the A/C efficiency ratio is {T3[0]['eta']/T3[2]['eta']:.1f}×. The do-nothing baseline scores {nd_bus:.4f}, below all three systems, so the recommendation is not an artefact of ignoring the alternative. System A's cooled-zone proxy WBGT is {T3[0]['wbgt']:.2f} °C, below the 30 °C reference.")
para("Table 3. Q2a comparison (Phoenix bus shelter, 30 °C, per-venue normalisers).", 8.5, italic=True)
table(["System", "P (kW)", "ΔT_eff (°C)", "φ", "η (persons·°C/kW)", "LCC (USD/yr)", "WBGT proxy (°C)", "E"], [
    [r["eq"], f"{r['P']:.3f}", f"{r['dT']:.3f}", f"{r['phi']:.3f}", f"{r['eta']:.2f}", f"{r['lcc']:.2f}", f"{r['wbgt']:.2f}", f"{r['E']:.4f}"] for r in T3
], widths=[1.3, 1.5, 1.8, 1.1, 3.0, 2.2, 2.2, 1.5], size=8)
para("Table 3b. Assumed Q2a parameter set: A 0.25 kW / 2,250 CFM / ΔT_nom 0 / C $250 / L 7 / r 3%; B 1.2 kW / 917 CFM / ΔT_nom 5 / C $750 / L 5 / r 8%; C 2.5 kW / 1,031 CFM / ΔT_nom 8 / C $1,277 / L 5 / r 8%. A_cov = A_waiting = 15 m², γ = 0.55, N_eff = 6.", 8.5)
para("Note: the “Energy Use” values in Requirement 2a are power ratings in kW (not kWh per hour); annual energy is obtained as P_elec × H_yr.", 8.5, italic=True)
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
para(f"At the 30 °C reference the Phoenix cooled-zone proxy is 25.3–26.5 °C and the uncovered platform proxy is {find(T5,'PHX','rail','MC37V',1)['wbgt_amb']:.2f} °C, so the exposure is modest. In Hong Kong the cooled-zone proxy is 29.6–29.8 °C, but the uncovered share sits at {find(T5,'HK','rail','MC37V',1)['wbgt_amb']:.2f} °C, so a “pass” applies to the cooled zone only. At 28 °C no Hong Kong option clears the reference in both zones, which is reported as a stricter stress test rather than a compliance result.")
para("Table 5. Sixteen-scenario cross-climate matrix (30 °C).", 8.5, italic=True)
table(["ID", "City", "Venue", "Equipment", "ΔT_eff", "φ", "η", "LCC", "I_env", "WBGT proxy", "E"], [
    [f"SC-{i:02d}", r["city"], r["venue"], r["eq"], f"{r['dT']:.3f}", f"{r['phi']:.3f}", f"{r['eta']:.2f}",
     f"{r['lcc']:.2f}", f"{r['I_env']:.4f}", f"{r['wbgt']:.2f}", f"{r['E']:.4f}"] for i, r in enumerate(T5, start=1)
], widths=[1.1, 1.1, 1.1, 1.6, 1.4, 1.2, 1.5, 1.7, 1.3, 1.7, 1.4], size=7.5)

figure("docs/figures/fig3_rh_crossover.png", "Figure 3. RH crossover at 41 °C. MC37V in a bus shelter (γ = 0.55) crosses the drum-fan line at about 69.6% RH, the rail station (γ = 0.30) at about 79.7%; dotted lines mark Phoenix (18%) and Hong Kong (78%).")

h2("4.4 Multi-Objective Trade-Offs (Q4)")
para(f"On the revised environmental baseline the fan has the lowest I_env in Phoenix ({find(T5,'PHX','bus','Fan',1)['I_env']:.4f}) but not in Hong Kong ({find(T5,'HK','bus','Fan',1)['I_env']:.4f} > MC37V {find(T5,'HK','bus','MC37V',1)['I_env']:.4f}), because Hong Kong's water stress is low (BWS 0.179) and the fan's higher power dominates the carbon term. 'Zero water = lower environmental burden' is therefore false in Hong Kong under Eq. 5; the claim should be limited to water consumption, not to the composite index.")
figure("docs/figures/fig4_pareto.png", "Figure 4. LCC vs I_env trade-off. The 16 scenarios collapse to eight distinct cost–externality pairs; marker shape = city, colour = WBGT proxy pass/fail at the 30 °C reference. Labels mark the Phoenix points.")
para(f"In Phoenix, MC61V has the highest I_env ({find(T5,'PHX','rail','MC61V',1)['I_env']:.4f}) and the highest water use, and 1× MC61V's LCC is ${find(T5,'PHX','rail','MC61V',1)['lcc']:.2f} vs ${find(T5,'PHX','rail','MC37V',1)['lcc']:.2f} for 1× MC37V. The trade-off is coverage vs cost/water, not cooling magnitude: all evaporative units deliver about 4.4 °C in bus shelters and 6.5 °C on platforms. The memorandum in Section 6.1 turns this into a decision rule.")
doc.add_page_break()

# ---------------------------------------------------------------- section 5
h1("5. Sensitivity Analysis and Model Evaluation")
h2("5.1 Parameter, Policy and Decision-Weight Sensitivity")

R.KAPPA = 60.0
t5_60, _ = R.table5_rows("pressure", 30.0, "B")
e60_37 = find(t5_60, "HK", "rail", "MC37V", 1)["E"]
e60_fan = find(t5_60, "HK", "rail", "Fan", 1)["E"]
R.KAPPA = 45.0

R.WATER_MODE = "manufacturer"
t5_m, _ = R.table5_rows("pressure", 30.0, "B")
em_37 = find(t5_m, "HK", "rail", "MC37V", 1)["E"]
R.WATER_MODE = "balance"

para(f"Table 6 lists the winning unit for each COO weight profile. Under Balanced and Safety weights, Phoenix chooses MC37V at the bus shelter and MC61V on the platform; Hong Kong chooses the fan at the bus shelter and MC37V on the platform (MC61V under Safety, where full coverage and the higher safety term dominate). Under Cost weights the platform switches to the cheaper MC37V in Phoenix and to the fan in Hong Kong, and the Eco profile keeps the fan at the bus shelter and MC37V on the platform.")
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
for name in ("Balanced", "Safety", "Cost", "Eco"):
    row = [name]
    for c, v in (("PHX", "bus"), ("PHX", "rail"), ("HK", "bus"), ("HK", "rail")):
        eq, sc = T6_28[(name, c, v)]
        row.append(f"{eq} ({sc:.3f})")
    t6b.append(row)
para("Table 6b. 28 °C non-acclimatised stress test (winners only).", 8.5, italic=True)
table(["Profile", "Phoenix bus", "Phoenix rail", "HK bus", "HK rail"], t6b, widths=[2.4, 3.1, 3.1, 3.0, 3.0], size=8)

figure("docs/figures/fig5_gamma_heatmap.png", "Figure 5. γ sweep and weight matrix. Left: η vs γ (0.20–0.75) for the Phoenix bus shelter with MC37V; dashed lines at γ = 0.30 and 0.55. Right: best unit and its score for each COO weight profile and city–venue.")
para(f"Sensitivity runs hold the per-venue normalisers fixed, so a change in E reflects the parameter rather than a rescaling. The jet-mixing coefficient is the largest single uncertainty on the Hong Kong platform, but it does not flip the rebuilt ranking: at κ = 60 MC37V still leads the fan ({e60_37:.4f} vs {e60_fan:.4f}), because the fan raises felt cooling without lowering the heat-index proxy; at κ = 30 the ordering is unchanged. Using manufacturer water rates instead of the energy balance lowers the Hong Kong MC37V score to {em_37:.4f} and leaves the ordering unchanged. A black-globe offset of +3 K reduces every S_safe by 0.5 and compresses all E scores by about 0.15, which does not reorder the units but weakens any claim of absolute safety. γ, ε, ΔT_nom, L_life, r_om, V_w and A_cov each shift the near-ties by less than 0.05 E-points; the full single-factor table is in docs/sensitivity_report.md.")
para("The approximate proxy and the fixed design day are the main uncertainties. The 30 °C line is a benchmark, not a certification, and the ranking of near-ties should be read as “within model uncertainty” rather than as a field guarantee.")

h2("5.2 Model Strengths, Limitations and Future Improvements")
para("Strengths: the six-equation chain is transparent; every number comes from one locked table; water is derived from the same energy balance as the temperature drop; the decision score is compared with a do-nothing baseline and separates the whole platform from the waiting zone.")
para("Limitations: the drum fan is a hypothetical benchmark; κ, γ, ε, ΔT_nom, L_life, r_om and N_eff remain assumptions; the heat index is an approximate proxy built from dry- and wet-bulb values with no globe or solar term, so it is not ISO 7243 compliance (CCOHS); the design day is a representative summer day rather than a full time series; and the multi-unit model adds nominal coverage areas rather than modelling the union of overlapping jets. Future work: field calibration of κ and γ, measured water flow, hourly TMY/HKO time series, and a two-unit deployment with independent placement.")
doc.add_page_break()

# ---------------------------------------------------------------- section 6
h1("6. Decision Memorandum, Public Blog and References")
h2("6.1 Executive Memorandum to the COO (Q5a)")
para("MEMORANDUM — TO: Chief Operating Officer; FROM: Modelling team; DATE: November 2026; SUBJECT: Climate-matched cooling for semi-open transit spaces.")
para(f"Recommendation: size for coverage first, then choose the smallest unit that achieves it, and always compare against doing nothing. The do-nothing baseline scores {nd_E('PHX','bus'):.3f} in Phoenix and {nd_E('HK','bus'):.3f} in Hong Kong; every recommendation below beats it, but the margin in Hong Kong is small and depends on shade.")
para(f"For Phoenix, deploy 1× Hessaire MC61V per 120 m² waiting zone: φ = {phx61['phi']:.2f}, ΔT_eff = {phx61['dT']:.2f} °C, proxy WBGT = {phx61['wbgt']:.2f} °C, LCC = ${phx61['lcc']:.2f}/station/yr and E = {phx61['E']:.4f}; if capital and water budgets bind and partial coverage is acceptable, 1× MC37V gives E = {phx37['E']:.4f} at ${phx37['lcc']:.2f} for 73% coverage. Do not deploy 2× MC61V: it doubles cost without improving coverage.")
para(f"For Hong Kong, deploy 1× MC37V on the platform (E = {hk37['E']:.4f}, ${hk37['lcc']:.2f}, φ = {hk37['phi']:.2f}) and pair it with shade or windbreak for the occupants outside the jet; 1× MC61V is the full-coverage alternative (E = {hk61['E']:.4f}, ${hk61['lcc']:.2f}). At 15 m² bus shelters, use 1× drum fan (E = {find(T5,'HK','bus','Fan',1)['E']:.4f} vs {find(T5,'HK','bus','MC37V',1)['E']:.4f}) with a humidity interlock.")
para(f"Network: Phoenix 38 stations × ${phx61['lcc']:.2f} = ${38*phx61['lcc']:,.0f}/yr; Hong Kong 68 stops × ${hk37['lcc']:.2f} = ${68*hk37['lcc']:,.0f}/yr. Action plan: (1) shade and windbreak retrofits first (γ 0.55 → 0.30); (2) humidity interlock at 70–80% RH for bus shelters; (3) meter water on evaporative units; (4) pilot 1× MC61V vs 1× MC37V on two Phoenix platforms; (5) re-check the Hong Kong platform choice after measuring κ on site.")
para("Table 6c. Memorandum decision table (30 °C).", 8.5, italic=True)
table(["City", "Venue", "Recommended", "φ", "LCC (USD/yr)", "E", "Do-nothing E"], [
    ["Phoenix", "Bus shelter", "1× MC37V", f"{find(T5,'PHX','bus','MC37V',1)['phi']:.2f}", f"{find(T5,'PHX','bus','MC37V',1)['lcc']:.2f}", f"{find(T5,'PHX','bus','MC37V',1)['E']:.4f}", f"{nd_E('PHX','bus'):.4f}"],
    ["Phoenix", "Platform", "1× MC61V", f"{phx61['phi']:.2f}", f"{phx61['lcc']:.2f}", f"{phx61['E']:.4f}", f"{nd_E('PHX','rail'):.4f}"],
    ["Hong Kong", "Bus shelter", "1× drum fan", f"{find(T5,'HK','bus','Fan',1)['phi']:.2f}", f"{find(T5,'HK','bus','Fan',1)['lcc']:.2f}", f"{find(T5,'HK','bus','Fan',1)['E']:.4f}", f"{nd_E('HK','bus'):.4f}"],
    ["Hong Kong", "Platform", "1× MC37V", f"{hk37['phi']:.2f}", f"{hk37['lcc']:.2f}", f"{hk37['E']:.4f}", f"{nd_E('HK','rail'):.4f}"],
], widths=[1.8, 2.2, 2.6, 1.2, 2.4, 1.6, 2.2], size=8)

h2("6.2 Public-Facing Blog Post (Q5b)")
para("Why misting fans feel great in Phoenix — but change little in Hong Kong (and what your commute needs instead).")
para(f"In Phoenix's dry 41 °C / 18% air, an evaporative cooler can lower the air by several degrees and the felt temperature by more; at a 120 m² platform, one MC61V covers the whole waiting zone. In Hong Kong's 32.5 °C / 78% air, the wet-bulb depression shrinks, so the air drops by only about 2.7 °C and the felt temperature by about 2 °C. At an open 15 m² bus shelter, a 10,500 CFM drum fan delivers more felt cooling than a small evaporative unit and uses no water.")
para(f"At a 128 m² platform the comparison is close: one MC37V (${hk37['lcc']:.2f}, E {hk37['E']:.4f}) slightly beats one fan ({hkfan['lcc']:.2f}, E {hkfan['E']:.4f}), and two fans (E {hk2fan['E']:.4f}) lose to one MC37V. The practical rule is: shade first, windbreak second, then match the machine to the venue.")

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
]
for i, ref in enumerate(refs, start=1):
    para(f"{i}. {ref}", 9)
doc.add_page_break()

# ---------------------------------------------------------------- AI report
h1("AI Use Report")
para("AI tools were used in this project and are disclosed here. The assistant was a large-language-model coding and writing agent (DeepSeek, accessed through the DeepSeek Harness interface) on 14–15 November 2026. It was used for four purposes: (1) drafting and editing English prose; (2) writing and running the Python scripts in analysis/ (recompute.py, sensitivity.py, make_figures.py); (3) consistency checks between the paper, the tables and the data register; and (4) translation between the team's Chinese notes and the English manuscript.")
para("Representative prompts included: “Check whether the one- and two-unit rows use the same normalisers, and recompute E if they do not”; “Restrict the safety score to the cooled zone, report the occupants and WBGT in the uncovered zone, and add a do-nothing baseline”; and “Derive the water flow from the adiabatic mass balance and rebuild the cost and externality terms”.")
para("Every number was recomputed by analysis/recompute.py, the tables were regenerated from it, the figures come from the same locked table, and analysis/qa_check.py scans the manuscript for superseded values. AI output was treated as draft text and code only: all citations refer to primary sources, no data were generated by the model, and the team reviewed the wording, assumptions and recommendations.")
para("Tools and versions: DeepSeek Harness (deepseek-flash model) in an agent interface; Python 3.12 with standard libraries for the recomputation, NumPy 2.5 and Matplotlib 3.11 for the figures, python-docx 1.2 for document assembly, and WPS Writer for PDF export.")
doc.add_page_break()

# ---------------------------------------------------------------- appendix
h1("Appendix A. Data and Assumption Register")
para("Status: S = sourced, D = derived, A = assumption, U = unverified. Full details in docs/data_provenance.md.", 9)
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
    ["κ (dimensionless)", "45", "A", "Jet-mixing calibration; sensitivity 30–60"],
    ["γ (bus / rail)", "0.55 / 0.30", "A", "Urban ventilation ranges; swept 0.20–0.75"],
    ["ε", "0.80", "A", "Data pack: no manufacturer guarantee; 0.70–0.90"],
    ["ΔT_nom", "11.0 °C", "A", "Assumed maximum drop; 8.8–13.2"],
    ["V_w", "derived", "D", "Adiabatic mass balance, Eq. 8; manufacturer rates as sensitivity"],
    ["L_life / r_om", "5–7 yr / 3–8%", "A", "No published service data"],
    ["N_eff", "6 / 45", "A", "Peak occupancy assumption"],
    ["Phoenix stations", "38", "S", "NTD 71 facilities ≠ stations"],
], widths=[3.8, 4.4, 1.3, 7.0], size=8)

doc.save(OUT)
print("saved", OUT)
