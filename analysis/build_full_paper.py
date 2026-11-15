"""Build the integrated English master paper (v0.9, P4) with placeholders for P3 items."""

import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
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


def find(tbl, city, eq, n=1):
    return next(r for r in tbl if r["city"] == city and r["eq"] == eq and r["n"] == n)


OUT = "2026_HiMCM_ProblemB_Full_Paper_v0.9.docx"

doc = Document()
sec = doc.sections[0]

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


def placeholder(title, lines):
    h1(title)
    p = para("[PLACEHOLDER — blank page to be completed]", size=11, italic=True)
    p.runs[0].font.color.rgb = RGBColor(0xC0, 0x00, 0x00)
    for ln in lines:
        bullet(ln, 9.5)
    doc.add_page_break()


# ============================================================ cover
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("2026 HiMCM"); set_font(r, 14, True, RGBColor(0x66, 0x66, 0x66))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Problem B: Air Conditioning the Environment"); set_font(r, 20, True, RGBColor(0x1F, 0x3B, 0x57))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Modeling Energy Waste in Public Cooling"); set_font(r, 16, False, RGBColor(0x1F, 0x3B, 0x57))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("A Six-Equation Thermodynamic, Economic and Environmental Framework\nfor Semi-Open Transit Cooling")
set_font(r, 12, False, RGBColor(0x33, 0x33, 0x33))
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Team [Team Number]   |   November 2026"); set_font(r, 11)
doc.add_page_break()

# ============================================================ summary
h1("Summary Sheet")
para("Public cooling is usually judged by kilowatt-hours, but energy alone cannot tell a working system from a failing one. An open freezer and a semi-open transit shelter share the same physics: cold air is produced inside a boundary and leaks through an opening, so the useful cooling actually delivered to the people or goods inside — not the electricity drawn — is what should be counted. We build a six-equation model that carries this logic from a freezer case to two real venues: a 15 m² bus shelter and a 120 m² rail platform in Phoenix (41 °C / 18% RH) and Hong Kong (32.5 °C / 78% RH).")
para("Eqs. 1–2 give the thermodynamic cooling and its apparent-temperature effect; Eq. 3 converts them into η, in persons·°C per kW; Eqs. 4–5 price the life-cycle cost and the water–carbon externality; Eq. 6 combines thermal safety (WBGT), coverage, cost and environment into a single score E. All numbers come from one locked table with two explicit normalisation sets, and a public recompute script reproduces them.")
para("Two intuitions fail under the model. In Q2a the 0.25 kW fan is 5.8 times more efficient than the 2.5 kW cooler (η = 53.52 vs 9.20 persons·°C/kW), because extra power buys little extra cooling. In Q2b two units do not help: at a Phoenix platform 1× MC61V scores E = 0.4093 and 2× MC37V only 0.3708 at twice the cost, while 2× MC61V falls to 0.2193. In Hong Kong the rail station is a near-tie (1× MC37V 0.2837 vs 1× drum fan 0.2733), and the bus shelter favours the fan (0.3090), so the claim that evaporative cooling fails in humid cities is too strong.")
para("We recommend sizing for coverage first: 1× MC61V per Phoenix platform (φ = 1.0, $323.71/yr), or 1× MC37V where 73% coverage and $200.56/yr are acceptable; in Hong Kong, 1× MC37V at the rail station — conditional on shade or windbreak for the 12 of 45 occupants outside the jet — and 1× 36-inch fan at bus shelters. The 30 °C reference is the main threshold, with 28 °C reported as a stricter non-acclimatised sensitivity.")
para("Limitations: the drum fan is a hypothetical benchmark, several parameters remain assumptions (Appendix A), and WBGT is a dry/wet-bulb approximation rather than a compliance measurement. Within those limits the ranking is robust to ±30% changes in lifetime, maintenance, water use, prices, carbon factors and water stress.")
doc.add_page_break()

# ============================================================ TOC
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
    ("   3.6 Water–Carbon Externality (Eq. 5)", "7"),
    ("   3.7 Thermal Safety and Multi-Objective Evaluation (Eq. 6)", "7"),
    ("4. Model Application (Q2–Q4)", "9"),
    ("   4.1 Bus Stop Shelter (Q2a)", "9"),
    ("   4.2 Rail Station and Multi-Unit Scaling (Q2b)", "9"),
    ("   4.3 Cross-Climate Validation (Q3)", "10"),
    ("   4.4 Multi-Objective Trade-Offs (Q4)", "11"),
    ("5. Sensitivity Analysis and Model Evaluation", "13"),
    ("6. Decision Memorandum, Public Blog and References", "15"),
    ("AI Use Report", "17"),
    ("Appendix A. Data and Assumption Register", "18"),
]
table(["Section", "Page"], [[a, b] for a, b in toc], widths=[13.0, 2.5], size=9)
doc.add_page_break()

# ============================================================ section 1
h1("1. Understanding the Problem (Q1)")
para("Consider an open-front freezer in a supermarket. Its job is to hold goods at about −18 °C while its front is open to a 24 °C aisle. The compressor removes the heat that leaks in through the opening; an air curtain, a night cover, or a change of door discipline changes how much of that removed heat actually reaches the goods. Two freezers can draw the same 1.2 kW while one holds its load at temperature and the other spills cold air into the aisle. Comparing only kilowatt-hours would call them equal — or prefer the one that cools nothing, because a case that fails to cool draws less power.")
para("A defensible cooling-efficiency measure therefore needs four kinds of quantities. First, the useful cooling delivered to the protected space — the heat removed from the goods zone per unit time, not the electricity. Second, the resource paid for — electrical power, and water for evaporative devices, integrated over the operating window. Third, the share of the delivered cooling that stays where it is needed, i.e. the boundary loss at the opening (cold-air spill, warm-air infiltration, radiation). Fourth, who benefits — the number of occupants, or the mass of goods, actually inside the protected envelope. The first two give a ratio; the last two decide whether that ratio describes a real benefit or a leak.")
para("Energy alone fails on three counts. It ignores the boundary: the same compressor power can deliver different useful cooling depending on how much cold air escapes. It ignores the medium: a fan moves air and can feel cooler while lowering no air temperature at all, whereas an evaporative cooler lowers temperature but adds humidity, and in humid air its useful effect is small. It ignores the beneficiary: cooling an empty platform is not the same service as cooling forty waiting passengers. A measure that cannot separate these cases cannot rank a fan, a small evaporative unit and a large one on the same platform.")
para("The transit shelter is the same problem with the roles changed. In the freezer, cold is produced inside a box and leaks out through the opening; in the semi-open shelter, cooling is produced inside a roofed space and leaks out through the sides. The opening is the boundary in both cases. The goods become people: what matters is not the air temperature at the nozzle but the apparent temperature experienced by someone waiting, and how many people are inside the cooled jet. The freezer's spoiled goods become the occupant's heat stress; its ice build-up and compressor load become the water and carbon embodied in the cooling.")
para("This mapping produces the six quantities used in Section 3. Eqs. 1–2 describe how much cooling reaches the zone and how much of it a person actually feels; Eq. 3 divides the covered, occupancy-weighted cooling by electrical power; Eqs. 4–5 price the resources; Eq. 6 adds thermal safety and combines the four objectives. The two headline metrics are related but not interchangeable: η (persons·°C per kW) answers 'how much useful cooling per kilowatt', while E answers 'which deployment is best for the operator'. A unit can be efficient and still be the wrong choice if it covers too little of the platform or costs too much.")
para("The answer to Q1 is therefore that efficiency should not depend on energy use alone. A cooling system should be judged by the useful cooling it delivers to the protected space per unit of resource, weighted by how much of that space and how many occupants it actually covers, and constrained by thermal safety and the water–carbon externality. The freezer case shows why in the dry: an open case with a failed air curtain is cheap to run and useless. The rest of this paper applies the same logic where the 'goods' are commuters.")
doc.add_page_break()

# ============================================================ section 2
h1("2. Assumptions and Justifications")
para("We adopt six assumptions. Each is either grounded in thermodynamics/standards or explicitly flagged as an assumption with a sensitivity range; the data register in Appendix A gives the status of every parameter.")
assumptions = [
    ("Assumption 1 — Quasi-steady peak operation.",
     "During the peak summer window (11:00–19:00, 8 h/day) units run at rated capacity and the waiting zone reaches a quasi-steady thermal and aerodynamic state. Semi-open shelters have negligible thermal mass and continuous air exchange, so the jet plume stabilises within minutes; a design-day peak gives a reproducible cross-city baseline."),
    ("Assumption 2 — Isenthalpic adiabatic humidification.",
     "Air through the wetted medium follows a constant wet-bulb line, so the dry-bulb drop is bounded by ε(T_db − T_wb). We use ε = 0.80 (sensitivity 0.70–0.90); ε is an assumption, not a manufacturer guarantee. T_wb is the psychrometric wet bulb at the local surface pressure (950 hPa Phoenix, 1,000 hPa Hong Kong), not the sea-level Stull approximation."),
    ("Assumption 3 — Linear cold-air boundary escape.",
     "A constant fraction γ of the generated sensible cooling escapes: γ = 0.55 for three-sided bus shelters and 0.30 for roofed rail platforms. The ranges (45–65% and 30–40% loss) are taken from urban ventilation studies; γ is a lumped parameter, and Section 5 sweeps it from 0.20 to 0.75."),
    ("Assumption 4 — Jet velocity and uniform occupancy.",
     "Convective velocity scales with airflow density, v_eff = v_amb + κ(Q_air/A_cov), with κ = 45 s/m (sensitivity 30–60). Commuters are uniformly distributed, so beneficiaries scale with φ = min(1, n·A_cov/A_zone); N_eff = 6 (bus) and 45 (rail) are the average occupancies before coverage adjustment."),
    ("Assumption 5 — Commercial tariffs and straight-line depreciation.",
     "Capital costs depreciate linearly over L = 5–7 years and annual maintenance is r_om = 3–8% of capital; both are assumptions because the data pack does not publish equipment life or service rates. Energy and water use the latest available local tariffs: Phoenix 2024 (APS E-32 TOU + demand; City water card) and Hong Kong 2026 (CLP; WSD). Years are labelled explicitly and a 2026 Phoenix scenario is tested; the Hong Kong 50% water concession is a separate scenario."),
    ("Assumption 6 — Shaded outdoor WBGT.",
     "Both venue types provide overhead shading, so WBGT = 0.7 T_wb + 0.3 T_db (ISO 7243 no-solar-load form). The assumption matches Phoenix design intent: Valley Metro's criteria make shade the single most important station design element and require at least 50% platform shading between 10:00 and 14:00 on 21 August (Ch. 6.4.1). The main threshold is 30 °C, the ISO 7243 light-work reference for acclimatised persons; 28 °C is reported as a stricter non-acclimatised sensitivity. The earlier draft's 28 °C 'light 115 W/m²' label mixed two different reference values and is not used."),
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
    ["4 Jet velocity and occupancy", "2–3", "Free-jet momentum; κ=45 assumed"],
    ["5 Tariffs and depreciation", "4–5", "APS/CLP/WSD; L, r_om assumed"],
    ["6 Shaded WBGT", "6", "ISO 7243; Valley Metro shade criteria; 30 °C main, 28 °C sensitivity"],
], widths=[5.6, 3.0, 7.4], size=8)
doc.add_page_break()

# ============================================================ section 3
h1("3. Mathematical Model")
h2("3.1 Parameter Baselines")
para("Table 2A lists the four commercial benchmark units. Status codes: S = sourced, D = derived from sourced data, A = assumption, U = unverified in the data pack. The 36-inch drum fan has no product source in the workbook and is treated as a hypothetical benchmark; it is included because the humid-climate comparison needs a zero-water convective option.")
para("Table 2A. Candidate commercial cooling units.", 8.5, italic=True)
table(["Parameter", "EQ-01 MC37V", "EQ-02 MC61V", "EQ-03 Portacool", "EQ-04 Drum Fan", "Status"], [
    ["Type", "Evaporative", "Evaporative", "Evaporative", "Pure fan", "—"],
    ["P_elec (kW)", "0.250", "0.430", "0.391", "0.350", "S/D/A"],
    ["Airflow (CFM)", "3,100", "5,300", "2,400", "10,500", "S/A"],
    ["A_cov (m²)", "88", "148", "65", "75", "S/A"],
    ["ε", "0.80", "0.80", "0.80", "0", "A"],
    ["ΔT_nom (°C)", "11.0", "11.0", "11.0", "0", "A"],
    ["V_w (L/h)", "10.6", "18.2", "11.4", "0", "A/D"],
    ["C_cap (USD)", "398", "609", "1,099", "260", "S/A"],
    ["L_life (yr)", "5", "5", "7", "6", "A"],
    ["r_om", "8%", "8%", "6%", "3%", "A"],
], widths=[3.6, 3.0, 3.0, 3.2, 3.2, 1.8], size=8)

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

para("Table 2C. Venue geometry and occupancy.", 8.5, italic=True)
table(["Venue", "A_zone (m²)", "γ", "N_eff", "Basis"], [
    ["Bus shelter (Q2a)", "15", "0.55", "6", "Assumption; typical peak occupancy"],
    ["Rail platform (Q2b)", "120", "0.30", "45", "D/A: HK LRT side platform ≈ 30 m × 4 m; 45 ≈ 24% of 0.65 m²/person design capacity"],
], widths=[4.4, 2.6, 1.6, 1.6, 6.0], size=8)

h3("3.1.1 Transit Network Basis")
para("Valley Metro Rail's 2023 NTD profile reports 71 facilities and 29,846 average weekday unlinked trips; the 71 figure is a facility count, not a station count (about 38 stations in 2024), so network costs in Section 6 use 38 stations. The 12th St & Washington/Jefferson profile reports 384 weekday boardings (208 + 176) and 27,462 full-system weekday boardings. Valley Metro's design criteria set a 280 ft (85.3 m) calculated platform with a 16 ft 4 in (4.98 m) minimum centre-platform width, a peak 12-minute boarding/alighting design load at 7 ft² (0.65 m²) per person, and a 1.0% cross slope (Ch. 6.3.1–6.3.5). The South Central Extension/Downtown Hub opened on 7 June 2025 with eight new stations and a 12-minute weekday headway (20 minutes after 19:00; 15/20 minutes on Saturday; 20 minutes on Sunday; 365 days, about 20 h/day). The 2024 count of 38 stations is kept for the network-cost illustration so that station count, tariffs and ridership share the same 2024 basis; the 2026 system has about 46 stations. Hong Kong's Light Rail has 68 unique stops on 11 lines (Siu Hong 7 lines, Tuen Mun Ferry Pier 6), with 439,200 daily journeys in March 2026; five routes (505, 507, 614, 614P, 751) run 6–18 min peak headways. 149 LRVs and 3.90 million daily bus journeys are marked U because the PDF text layer is unreliable and the figures need a page-level check.")
figure("docs/figures/fig1_system.png", "Figure 1. System boundary and Eq. 1→6 coupling. Left: semi-open venue cross-section with the cold jet, lateral escape γ and coverage φ. Right: the Eq. 1→2→3→(4,5)→6 chain, grouped into thermodynamics, economics/externality and safety/decision.")

h2("3.2 Thermodynamic Cooling Constraint (Eq. 1)")
para("ΔT_phys = min(ΔT_nom, ε(T_db − T_wb)).   (Eq. 1)")
para("T_wb is solved from the psychrometric relation at surface pressure p_s: e_s(T_wb) − γ_p(T_db − T_wb) = e_amb, where γ_p = 1.006 p_s /(0.622 × 2,450) hPa/K. At 41 °C/18% and 950 hPa this gives 21.8 °C; at 32.5 °C/78% and 1,000 hPa it gives 29.1 °C. For pure fans ε = 0 and ΔT_phys = 0.")

h2("3.3 Apparent Temperature and Jet Velocity Coupling (Eq. 2)")
para("ΔT_eff = AT(T_db, e_amb, v_amb) − AT(T_zone, e_zone, v_eff),   AT(T,e,v) = T + 0.33e − 0.70v − 4.00.   (Eq. 2)")
para("T_zone = T_db − (1−γ)ΔT_phys; e_zone = min(e_s(T_zone), e_amb + 0.665(1−γ)ΔT_phys); v_eff = v_amb + κ(Q_air/A_cov), with Q_air = CFM × 1.699/3600 m³/s and κ = 45 s/m.")

h2("3.4 Unified Spatial Cooling Efficiency (Eq. 3)")
para("η = (φ · N_eff · ΔT_eff) / (n · P_elec),   φ = min(1, n·A_cov/A_zone).   (Eq. 3)")
para("η is a human-centric total (persons·°C per kW), not a per-person equipment efficiency; it scales with N_eff, so it is not used to compare venues of different occupancy directly.")

h2("3.5 Annualised Life-Cycle Cost (Eq. 4)")
para("LCC_annual = (1/L_life + r_om)·n·C_cap + H_yr·(n·P_elec·p_elec + (n·V_w/1000)·p_water).   (Eq. 4)")

h2("3.6 Dimensionless Water–Carbon Externality (Eq. 5)")
para("I_env = α_c(E_CO2/E_CO2,max) + α_w(W_eq/W_eq,max), with α_c = α_w = 0.50; E_CO2 = n·P_elec·H_yr·EF_grid; W_eq = (n·V_w/1000)·H_yr·BWS_raw.   (Eq. 5)")
para("Two normalisation sets are fixed. Set A (Table 3 only) uses the System C reference: ΔT_max = 3.832, LCC_max = 1,021.47, E_CO2,max = 1,090.8, W_eq,max = 107.2. Set B (Tables 4–6 and the memorandum) uses the envelope over all 16 one-unit scenarios and all two-unit deployments of the four units: ΔT_max = 6.559, LCC_max = 693.67, E_CO2,max = 402.5, W_eq,max = 130.1. E is comparable only within a set; by construction I_env ≤ 1 in Set B.")

h2("3.7 Thermal Safety and Multi-Objective Evaluation (Eq. 6)")
para("E = w1·S_safe(WBGT) + w2·S_comf(φ, ΔT_eff) − w3·LCC̃ − w4·I_env.   (Eq. 6)")
para("WBGT = 0.7 T_wb,zone + 0.3 T_zone; S_safe = max(0, 1 − max(0, WBGT − 30)/6); S_comf = φ·ΔT_eff/ΔT_max; LCC̃ = LCC/LCC_max; baseline weights (w1,w2,w3,w4) = (0.30, 0.30, 0.20, 0.20). The 28 °C non-acclimatised sensitivity replaces 30 in S_safe.")
para("S_safe is evaluated in the cooled zone — the coverage φ of the waiting population — not for the whole platform. Occupants outside the jet, a share (1 − φ), experience the shaded ambient WBGT; that exposure is reported separately in Section 4.2 instead of being folded into E. E is therefore a unit-ranking score, not a platform-level safety certificate: a claim that the platform passes at 30 °C needs φ = 1, added shade and windbreak, or an explicit statement of the uncovered exposure. The 28 °C case is a stricter reference value applied in the same way.")
doc.add_page_break()

# ============================================================ section 4
h1("4. Model Application and Results (Q2–Q4)")
h2("4.1 Bus Stop Shelter Evaluation (Q2a)")
para(f"Table 3 reports the Q2a comparison under the revised price/water baseline and the 30 °C reference. System A (0.25 kW fan) remains the most efficient (η = 53.52 persons·°C/kW, E = {T3[0]['E']:.4f}); System B (1.2 kW) has E = {T3[1]['E']:.4f}; System C (2.5 kW) has E = {T3[2]['E']:.4f}; the A/C efficiency ratio is 5.8×. System A's post-cooling WBGT is 27.55 °C, below both 28 °C and 30 °C, so it is no longer described as exceeding the safety limit. Because Table 3 uses Set A, its E values are not comparable with Tables 4–6.")
para("Table 3. Q2a comparison under Set A (Phoenix bus shelter, 30 °C).", 8.5, italic=True)
table(["System", "P (kW)", "CFM", "ΔT_eff (°C)", "η", "LCC (USD/yr)", "I_env", "E"], [
    [r["eq"], f"{r['P']:.3f}", f"{r['CFM']:.0f}", f"{r['dT']:.3f}", f"{r['eta']:.2f}", f"{r['lcc']:.2f}", f"{r['I_env']:.4f}", f"{r['E']:.4f}"] for r in T3
], widths=[1.4, 1.6, 1.4, 2.0, 1.6, 2.4, 1.5, 1.5])
para("Note: The “Energy Use” values in Requirement 2a are power ratings in kW (not kWh per hour); annual energy is obtained as P_elec × H_yr.", 8.5, italic=True)
para("Table 3b. Assumed Q2a parameter set (for reproducibility): A 0.25 kW / 2,250 CFM / ΔT_nom 0 / C $250 / L 7 / r 3%; B 1.2 kW / 917 CFM / ΔT_nom 5 / V 15 L/h / C $750 / L 5 / r 8%; C 2.5 kW / 1,031 CFM / ΔT_nom 8 / V 30 L/h / C $1,277 / L 5 / r 8%. A_cov = A_zone = 15 m², γ = 0.55, N_eff = 6.", 8.5)

h2("4.2 Semi-Open Rail Station and Multi-Unit Scaling (Q2b)")
para("Table 4 compares one- and two-unit deployments on the same Set B basis and with the same normalisers. Two units do not improve E: in Phoenix, 1× MC37V gives E = 0.4051, 1× MC61V 0.4093 and 2× MC37V 0.3708; in Hong Kong, 1× MC37V gives 0.2837 and 2× drum fans 0.2303. The earlier comparison used different normalisers for the one- and two-unit rows, so it overstated the benefit of the second unit.")
para("If the operator requires full 120 m² coverage, 1× MC61V is preferred: φ = 1.0, ΔT_eff = 6.543 °C, LCC = $323.71/yr, I_env = 0.4831, E = 0.4093, which dominates 2× MC37V (E = 0.3708, LCC = $401.11, I_env = 0.5622) at the same coverage. If partial coverage is acceptable and cost/water are prioritised, 1× MC37V is the maximum-E option (0.4051) at 73.3% coverage. I_env ≤ 1 for every one- and two-unit scenario by construction.")
para("Table 4. One- vs two-unit deployment at a 120 m² rail station (Set B, 30 °C).", 8.5, italic=True)
table(["City", "Equipment", "n", "φ", "ΔT_eff (°C)", "LCC (USD/yr)", "I_env", "WBGT (°C)", "E"], [
    [r["city"], r["eq"], r["n"], f"{r['phi']:.4f}", f"{r['dT']:.3f}", f"{r['lcc']:.2f}", f"{r['I_env']:.4f}", f"{r['wbgt']:.2f}", f"{r['E']:.4f}"] for r in T4
], widths=[1.2, 1.7, 0.8, 1.5, 1.8, 2.1, 1.5, 1.6, 1.5])
hk37 = next(r for r in T4 if r["city"] == "HK" and r["eq"] == "MC37V" and r["n"] == 1)
hk61 = next(r for r in T4 if r["city"] == "HK" and r["eq"] == "MC61V" and r["n"] == 1)
n_wait = R.VENUE["rail"]["N"]
cov = hk37["phi"] * n_wait
unc = (1 - hk37["phi"]) * n_wait
wb_cov = hk37["wbgt"]
wb_unc = 0.7 * R.twb(32.5, 78.0, 1000.0, "pressure") + 0.3 * 32.5
wb_plat = (cov * wb_cov + unc * wb_unc) / n_wait
para(f"Table 4b makes the coverage assumption explicit for the Hong Kong rail case. With 1× MC37V, φ = {hk37['phi']:.3f}: {cov:.0f} of the {n_wait} waiting occupants are inside the cooled zone (WBGT {wb_cov:.2f} °C) and {unc:.0f} are outside it, where they experience the shaded ambient value of {wb_unc:.2f} °C. The cooled zone passes the 30 °C reference; the uncovered zone does not, so the platform as a whole is not compliant at 30 °C while {unc:.0f} occupants remain outside the jet. At 28 °C neither zone passes. The Hong Kong recommendation is therefore conditional: accept 73% coverage with the uncovered zone above 30 °C, choose 1× MC61V for φ = 1 (WBGT {hk61['wbgt']:.2f} °C at ${hk61['lcc']:.2f}/yr), or add shade and windbreak so that the uncovered zone approaches the shaded ambient. Phoenix partial-coverage cases are less exposed because the ambient shaded WBGT there is {0.7 * R.twb(41.0, 18.0, 950.0, 'pressure') + 0.3 * 41.0:.2f} °C, below both thresholds.")
para("Table 4b. Covered vs uncovered exposure, Hong Kong rail station, 1× MC37V.", 8.5, italic=True)
table(["Zone", "Persons", "WBGT (°C)", "30 °C reference", "28 °C reference"], [
    ["Covered zone (φ)", f"{cov:.0f}", f"{wb_cov:.2f}", "pass", "fail"],
    ["Uncovered zone (1 − φ)", f"{unc:.0f}", f"{wb_unc:.2f}", "fail", "fail"],
], widths=[6.4, 2.2, 2.4, 3.2, 3.2], size=8)
figure("docs/figures/fig2_q2a_q2b.png", "Figure 2. Q2a efficiency paradox and Q2b scaling. Left: Systems A/B/C, bars = ΔT_eff, line = η. Right: 1× vs 2× deployment of MC37V, MC61V and Portacool at a 120 m² Phoenix platform, annotated with E and φ.")

h2("4.3 Cross-Climate Validation (Q3)")
para("Table 5 gives the 16-scenario matrix. In Phoenix, evaporative cooling remains the best option: MC37V in bus shelters (E = 0.3866) and MC61V in rail stations (0.4093, narrowly above MC37V 0.4051). In Hong Kong, the bus shelter favours the drum fan (0.3090 vs MC37V 0.2840), but the rail station is a near-tie: MC37V 0.2837 vs fan 0.2733. The blanket statement that evaporative cooling fails in humid coastal cities is therefore too strong: the climate effect is technology- and venue-specific, and at the rail station the two options are within 0.01 E-points.")
para(f"At the 30 °C reference, Phoenix cooled-zone WBGT is 25.3–27.6 °C and the uncovered train-platform zone is {0.7 * R.twb(41.0, 18.0, 950.0, 'pressure') + 0.3 * 41.0:.2f} °C, so the platform-level claim holds in Phoenix. In Hong Kong the cooled zone is 29.6–29.8 °C, but the uncovered share of a partially covered platform sits at {0.7 * R.twb(32.5, 78.0, 1000.0, 'pressure') + 0.3 * 32.5:.2f} °C; 'pass' therefore applies to the cooled zone only, and the full-coverage MC61V case (φ = 1, {next(r for r in T4 if r['city'] == 'HK' and r['eq'] == 'MC61V' and r['n'] == 1)['wbgt']:.2f} °C) is the one that passes platform-wide. At 28 °C every Hong Kong option exceeds the limit in both zones.")
rows5 = []
for i, r in enumerate(T5, start=1):
    rows5.append([f"SC-{i:02d}", r["city"], r["venue"], r["eq"], f"{r['dT']:.3f}", f"{r['phi']:.4f}",
                  f"{r['eta']:.2f}", f"{r['lcc']:.2f}", f"{r['I_env']:.4f}", f"{r['wbgt']:.2f}", f"{r['E']:.4f}"])
para("Table 5. Sixteen-scenario cross-climate matrix (Set B, 30 °C).", 8.5, italic=True)
table(["ID", "City", "Venue", "Equipment", "ΔT_eff", "φ", "η", "LCC", "I_env", "WBGT", "E"],
      rows5, widths=[1.1, 1.1, 1.1, 1.6, 1.4, 1.2, 1.5, 1.7, 1.3, 1.3, 1.4], size=7.5)
figure("docs/figures/fig3_rh_crossover.png", "Figure 3. RH crossover at 41 °C. MC37V in a bus shelter (γ = 0.55) crosses the drum-fan line at about 69.6% RH, the rail station (γ = 0.30) at about 79.7%; dotted lines mark Phoenix (18%) and Hong Kong (78%).")

h2("4.4 Multi-Objective Trade-Offs (Q4)")
para("On the revised environmental baseline, the fan has the lowest I_env in Phoenix (0.1897) but not in Hong Kong (0.2035 > MC37V 0.1541), because Hong Kong's water stress is low (BWS 0.179) and the fan's higher power dominates the carbon term. Thus 'zero water = lower environmental burden' is false in Hong Kong under Eq. 5; the claim should be limited to water consumption, not to the composite index.")
para("In Phoenix, MC61V has the highest I_env (0.4831) and water use, and 1× MC61V's LCC is $323.71 vs $200.56 for 1× MC37V. The trade-off is coverage vs cost/water, not cooling magnitude: all three evaporative units deliver 4.39–4.41 °C in bus shelters and 6.53–6.56 °C in rail stations. The memorandum in Section 6.1 turns this into a decision rule.")
figure("docs/figures/fig4_pareto.png", "Figure 4. LCC vs I_env trade-off. The 16 scenarios collapse to eight distinct cost–externality pairs (bus and rail share LCC and I_env); marker shape = city, colour = WBGT pass/fail at the 30 °C reference. Labels mark the Phoenix points.")
doc.add_page_break()

# ============================================================ section 5
h1("5. Sensitivity Analysis and Model Evaluation")
h2("5.1 Parameter, Policy and Decision-Weight Sensitivity")
para("Table 6 (30 °C) shows: Phoenix bus/rail → MC37V/MC61V under Balanced and Safety; Cost/Eco switch the rail to MC37V. Hong Kong bus → fan under all four profiles; Hong Kong rail → MC37V under Balanced/Safety/Eco and fan under Cost. Under the stricter 28 °C non-acclimatised limit, Hong Kong bus Safety/Eco switch to MC37V, while the rail station remains MC37V; the 28/30 choice therefore changes the bus-shelter recommendation under safety/eco weights but not the rail-station choice.")
t6rows = []
for name in ["Balanced", "Safety", "Cost", "Eco"]:
    row = [name]
    for city in ["PHX", "HK"]:
        for venue in ["bus", "rail"]:
            eq, E = T6_30[(name, city, venue)]
            row.append(f"{eq} ({E:.4f})")
    t6rows.append(row)
para("Table 6. Optimal equipment under four COO weight profiles (30 °C).", 8.5, italic=True)
table(["Profile (w1/w2/w3/w4)", "Phoenix Bus", "Phoenix Rail", "HK Bus", "HK Rail"], t6rows,
      widths=[4.2, 3.2, 3.2, 3.2, 3.2])
para("Table 6b. 28 °C non-acclimatised sensitivity (winners only).", 8.5)
t6rows28 = []
for name in ["Balanced", "Safety", "Cost", "Eco"]:
    row = [name]
    for city in ["PHX", "HK"]:
        for venue in ["bus", "rail"]:
            eq, E = T6_28[(name, city, venue)]
            row.append(f"{eq} ({E:.4f})")
    t6rows28.append(row)
table(["Profile", "Phoenix Bus", "Phoenix Rail", "HK Bus", "HK Rail"], t6rows28,
      widths=[4.2, 3.2, 3.2, 3.2, 3.2])
para("The RH crossover is 69.6% for the 41 °C bus shelter and 79.7% for the rail station (65.6% and 77.0% at 32.5 °C); it should be reported per venue, not as a single universal value. The γ sweep gives ΔT_eff 7.393→2.670 °C and WBGT 25.02→26.76 °C as γ rises 0.20→0.75. The 50% water concession lowers Hong Kong MC37V LCC from $181.36 to $175.25 (E 0.2837→0.2855) and MC61V from $290.75 to $280.25 (E 0.2547→0.2577); it does not change the ranking.")
para("Every single-factor run holds the baseline Set B normalisers fixed, so a change in E reflects the parameter and not a rescaling of the denominator. The earlier draft recomputed the normalisers inside each scenario: a 30% lifetime reduction that raised annual cost from $323.71 to $375.91 then *raised* E from 0.4093 to 0.4119. With the fixed denominator the same case falls to 0.3942, which is the direction the cost change implies. Scores are therefore comparable across rows; the per-scenario variant is kept only as an internal 'relative ranking within scenario' check, not as evidence of robustness.")
figure("docs/figures/fig5_gamma_heatmap.png", "Figure 5. γ sweep and weight matrix. Left: η vs γ (0.20–0.75) for the Phoenix bus shelter with MC37V; dashed lines at γ = 0.30 and 0.55. Right: best unit and its score for each COO weight profile and city–venue.")

h2("5.2 Model Strengths, Limitations and Future Improvements")
para("Strengths: the six-equation chain is unchanged, and every number comes from one locked table with explicit normalisation sets; the model separates thermodynamics (Eq. 1–2), spatial coverage (Eq. 3), life-cycle cost (Eq. 4), water–carbon externality (Eq. 5) and thermal safety (Eq. 6).")
para("Limitations: E is a within-set relative score, not a physical quantity; the drum fan is a hypothetical benchmark; the wet bulb is pressure-corrected but still a psychrometric approximation of the natural wet bulb, and WBGT is computed from dry- and wet-bulb values with no globe or solar term, so it is an index approximation rather than ISO 7243 compliance (CCOHS); L_life, r_om, V_w, ε, ΔT_nom, κ, γ and N_eff remain assumptions (Appendix A). Future work: field calibration of κ and γ, measured water flow, hourly TMY/HKO time series, and a two-unit deployment with independent placement (the model assumes both units cover the same area and do not increase v_eff).")
doc.add_page_break()

# ============================================================ section 6
h1("6. Decision Memorandum, Public Blog and References")
h2("6.1 Executive Memorandum to the COO (Q5a)")
table(["Field", "Memorandum details"], [
    ["TO", "Chief Operating Officer (COO), Urban Transit Operations"],
    ["FROM", "Mathematical Modeling & Sustainability Analytics Team"],
    ["DATE", "November 2026"],
    ["SUBJECT", "Climate-matched cooling for 120 m² semi-open rail platforms: coverage first, then cost"],
], widths=[2.2, 15.0])
para("Recommendation: size for coverage first, then choose the smallest unit that achieves it.")
para("For Phoenix, deploy 1× Hessaire MC61V per 120 m² platform: φ = 100%, ΔT_eff = 6.543 °C, WBGT = 25.33 °C, LCC = $323.71/station/yr and E = 0.4093, the highest of the full-coverage options. If capital and water budgets are binding and 73% coverage is acceptable, 1× MC37V delivers E = 0.4051 at $200.56. Do not deploy 2× MC37V: at the same 100% coverage it costs $401.11 and scores 0.3708, below 1× MC61V.")
para("For Hong Kong, deploy 1× MC37V (E = 0.2837, $181.36, 73% coverage) or 1× MC61V for full coverage (E = 0.2547, $290.75); do not standardise 2× drum fans on platforms (E = 0.2303, below 1× MC37V), although two fans cost less than one MC61V ($263.80 vs $290.75) and use no water. For 15 m² bus shelters, use 1× drum fan (E = 0.3090 vs MC37V 0.2840) with a humidity interlock.")
para("Network: Phoenix 38 stations × $323.71 = $12,301/yr; Hong Kong 68 stops × $181.36 = $12,332/yr. Replacing 2× fans with 1× MC37V in Hong Kong saves $5,606/yr (68 × $82.44). Action plan: (1) shade and windbreak retrofits first (γ 0.55 → 0.30); (2) humidity interlock at 70–80% RH for bus shelters; (3) meter water on evaporative units; (4) pilot 1× MC61V vs 1× MC37V on two Phoenix platforms.")
para("Table 6c. Memorandum decision table (120 m² platform, 30 °C).", 8.5, italic=True)
table(["Configuration", "φ", "ΔT_eff (°C)", "WBGT (°C)", "LCC (USD/yr)", "E"], [
    ["Phoenix 1× MC61V (recommended)", "100.0%", "6.543", "25.33", "$323.71", "0.4093"],
    ["Phoenix 1× MC37V (budget)", "73.3%", "6.534", "25.33", "$200.56", "0.4051"],
    ["Phoenix 2× MC37V (not recommended)", "100.0%", "6.534", "25.33", "$401.11", "0.3708"],
    ["Hong Kong 1× MC37V (recommended)", "73.3%", "1.992", "29.59", "$181.36", "0.2837"],
    ["Hong Kong 1× MC61V (full coverage)", "100.0%", "2.000", "29.59", "$290.75", "0.2547"],
    ["Hong Kong 1× Drum Fan (platform, partial)", "62.5%", "2.081", "30.15", "$131.90", "0.2733"],
    ["Hong Kong 2× Drum Fan (not recommended)", "100.0%", "2.081", "30.15", "$263.80", "0.2303"],
], widths=[6.2, 1.6, 2.0, 1.8, 2.2, 1.4], size=8)

h2("6.2 Public-Facing Blog Post (Q5b)")
para("Why misting fans feel great in Phoenix—but fail in Hong Kong (and what your commute needs instead).")
para("In Phoenix's dry 41 °C / 18% air, a direct evaporative cooler can lower the air by about 11 °C and the felt temperature by 4.4–6.5 °C; at a 120 m² rail platform, one MC61V covers the whole platform. In Hong Kong's 32.5 °C / 78% air, the wet-bulb depression shrinks to about 3.3 °C, so the air drops by only about 2.7 °C and the felt temperature by about 2 °C. At an open 15 m² bus shelter, a 10,500 CFM drum fan delivers 2.08 °C of felt cooling at $131.90/yr—27% less than one MC37V ($181.36)—and uses no water; both cover the 15 m² shelter fully.")
para("At a 120 m² platform the comparison is closer: one MC37V ($181.36, E 0.2837) slightly beats one fan ($131.90, E 0.2733), and two fans ($263.80) score 0.2303, below one MC61V ($290.75, 0.2547). The practical rule is: shade first, windbreak second, then match the machine to the venue—a fan for open bus shelters, a right-sized evaporative unit for platforms where coverage and cost matter.")
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
    "Valley Metro (2025). South Central Extension/Downtown Hub (SCE/DH) Frequently Asked Questions, April 2025, pp. 1–2, 7: opened 7 June 2025 with eight new stations; 12-minute weekday headway (20 minutes after 7 p.m.), 15/20 minutes on Saturday, 20 minutes on Sunday; 365 days, about 20 hours per day.",
    "CCOHS (accessed 15 November 2026). OSH Answers: Heat Control — WBGT and the assumptions behind it. Canadian Centre for Occupational Health and Safety. https://www.ccohs.ca/oshanswers/phys_agents/heat/heat_control.html",
]
for i, ref in enumerate(refs, start=1):
    para(f"{i}. {ref}", 9)
doc.add_page_break()

# ============================================================ placeholders
h1("AI Use Report")
para("AI tools were used in this project and are disclosed here. The assistant was a large-language-model coding and writing agent (DeepSeek, accessed through the DeepSeek Harness coding interface) on 14–15 November 2026. It was used for four purposes: (1) drafting and editing English prose for this paper; (2) writing, debugging and running the Python scripts in analysis/ (recompute.py, sensitivity.py, make_figures.py); (3) consistency checks between the paper, the tables and the data register; and (4) translation between the team's Chinese working notes and the English manuscript.")
para("Representative prompts included: “Check whether the one-unit and two-unit rows in Table 4 use the same normalisation, and recompute E if they do not”; “Restrict the Eq. 6 safety score to the cooled zone and report the number of occupants and WBGT in the uncovered zone”; and “Redraw Figure 3 from the locked numbers and mark the 69.6% and 79.7% crossover points”.")
para("Every numerical result was independently recomputed by analysis/recompute.py and the output tables were regenerated from it; the figures are generated from the same locked table by analysis/make_figures.py, and analysis/qa_check.py scans the manuscript for superseded values. AI output was treated as draft text and code only: all citations refer to primary sources, no data were generated by the model, and the team reviewed and approved the final wording, assumptions and recommendations.")
para("Tools and versions: DeepSeek Harness (deepseek-flash model) in an agent interface; Python 3.12 with standard libraries for the recomputation, NumPy 2.5 and Matplotlib 3.11 for the figures, python-docx 1.2 for document assembly, and WPS Writer for PDF export.")
doc.add_page_break()


# ============================================================ appendix
h1("Appendix A. Data and Assumption Register")
para("Status: S = sourced, D = derived, A = assumption, U = unverified. Full details in docs/data_provenance.md.", 9)
para("Table A1. Data and assumption register.", 8.5, italic=True)
table(["Parameter", "Value", "Status", "Source / note"], [
    ["Phoenix T_db / RH", "41.0 °C / 18%", "D/A", "ERA5 2026 Jun–Aug; typical daily max 41.2/15.3"],
    ["Hong Kong T_db / RH", "32.5 °C / 78%", "D/A", "ERA5; typical daily max 31.0/74.7"],
    ["Wet bulb", "21.8 / 29.1 °C", "D", "Pressure-corrected at 950/1,000 hPa"],
    ["Phoenix p_elec", "0.1595 USD/kWh", "D", "APS E-32 2024: energy + 6-month demand; excl. basic charge"],
    ["Hong Kong p_elec", "0.1923 USD/kWh", "D", "CLP 2026: 150 cents/unit ÷ 7.8"],
    ["Phoenix p_water", "2.0766 USD/m³", "D", "2024 inside-city card; excludes sewer/tax; lower bound"],
    ["Hong Kong p_water", "0.9615 USD/m³", "D", "WSD 4.58 + 2.92 ÷ 7.8"],
    ["EF_grid", "0.303 / 0.390", "A/S", "PHX assumption; HK CLP 2023 0.39"],
    ["BWS", "2.482 / 0.179", "S", "Aqueduct 4.0 point / HKG sub-basins"],
    ["L / r / V_w", "5/5/7/6; 8/8/6/3%; 10.6/18.2/11.4", "A", "Not published; sensitivity ±30/50%"],
    ["ε / ΔT_nom", "0.80 / 11 °C", "A", "Generic; not equipment-specific"],
    ["Drum fan", "10,500 CFM / 0.35 kW / $260", "A", "Hypothetical benchmark"],
    ["Phoenix stations", "38", "S", "NTD 71 facilities ≠ stations"],
], widths=[3.8, 5.6, 1.4, 7.0], size=8)
para("Data note: the 97 MB workbook contains third-party PDFs (OECD reports, utility tariffs). Check redistribution terms before making the repository public.", 8.5, italic=True)

doc.save(OUT)
print("saved", OUT)
