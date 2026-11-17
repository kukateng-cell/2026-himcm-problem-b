# -*- coding: utf-8 -*-
"""Insert a nomenclature table (Table 1b) into the v1.2 paper."""
from copy import deepcopy
from docx import Document
from docx.shared import Pt, Twips
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

SRC = r"C:\Users\kukat\Desktop\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"
OUT = r"C:\Users\kukat\Desktop\USA\_extract\v1.2_nomenclature.docx"

GROUPS = [
    ("Thermodynamics and psychrometrics", [
        ("T_db", "Ambient dry-bulb temperature", "°C", "1–3"),
        ("T_wb", "Ambient psychrometric wet-bulb temperature at surface pressure", "°C", "1"),
        ("T_wb,zone", "Wet-bulb temperature of the cooled zone", "°C", "6"),
        ("T_zone", "Dry-bulb temperature of the cooled zone", "°C", "2, 6"),
        ("e_amb, e_zone", "Water-vapour pressure of the ambient air and of the cooled zone", "hPa", "1, 2"),
        ("e_s(T)", "Saturation water-vapour pressure at temperature T", "hPa", "1, 2"),
        ("p_s", "Local surface pressure (950 Phoenix, 1,000 Hong Kong)", "hPa", "1"),
        ("γ_p", "Psychrometric constant used to solve the ambient wet bulb", "hPa/K", "1"),
        ("ΔT_nom", "Nominal maximum dry-bulb drop of the unit (11.0 assumed)", "°C", "1"),
        ("ΔT_phys", "Physical dry-bulb drop before boundary loss (0 for a fan)", "°C", "1, 2, 7"),
        ("ΔT_eff", "Felt (apparent) temperature drop of a person in the zone", "°C", "2, 3, 6"),
        ("AT(T, e, v)", "Steadman apparent-temperature index, T + 0.33e − 0.70v − 4.00", "°C", "2"),
        ("WBGT_proxy", "Heat-index proxy, 0.7 × zone wet bulb + 0.3 × zone dry bulb", "°C", "6"),
    ]),
    ("Airflow, jet mixing and geometry", [
        ("v_amb", "Ambient wind speed at 2 m", "m/s", "2"),
        ("v_eff", "Effective air speed in the cooled zone", "m/s", "2"),
        ("Q_air", "Rated airflow, CFM × 1.699/3600", "m³/s", "2, 7"),
        ("κ", "Dimensionless jet-mixing coefficient (design value 45)", "—", "2"),
        ("γ", "Fraction of generated cooling lost at the opening (0.55 bus / 0.30 rail)", "—", "2"),
        ("A_cov", "Effective coverage area of one unit", "m²", "2, 3"),
        ("A_waiting", "Modelled waiting-zone area", "m²", "3"),
        ("φ", "Coverage ratio, covered area ÷ waiting-zone area, capped at 1", "—", "3, 6"),
        ("N_eff", "Number of occupants inside the waiting zone", "persons", "3, 6"),
        ("u(x), u0, A0, C", "Centreline velocity at distance x, outlet velocity, outlet area, von Glahn constant (2.4)", "m/s, m/s, m², —", "3.3"),
        ("q", "Zone velocity scale, airflow ÷ coverage area", "m/s", "3.3"),
    ]),
    ("Equipment and operation", [
        ("n", "Number of identical units deployed", "—", "3, 4, 5"),
        ("P_elec", "Rated electrical power per unit", "kW", "3, 4, 5"),
        ("ε", "Saturation efficiency of the wetted medium (0.80)", "—", "1"),
        ("η", "Cooling efficiency, persons·°C per kW", "persons·°C/kW", "3"),
        ("H_yr", "Annual peak-season operating hours", "h/yr", "4, 5"),
        ("L_life", "Equipment service life", "yr", "4"),
        ("r_om", "Annual maintenance cost as a fraction of C_cap", "1/yr", "4"),
        ("V_w", "Water consumption rate", "L/h", "4, 5, 7"),
        ("ṁ_da, ρ_da", "Dry-air mass flow and dry-air density, p/(287T)", "kg/s, kg/m³", "7"),
        ("p, T", "Local pressure and absolute temperature in Eq. 7", "hPa, K", "7"),
        ("c_p, L_v", "Specific heat of moist air (1.006) and latent heat of vaporisation (2,450)", "kJ/(kg·K), kJ/kg", "7"),
        ("C_cap", "Capital cost per unit", "USD", "4"),
    ]),
    ("Economics and environmental externality", [
        ("p_elec, p_water", "Electricity and water tariffs", "USD/kWh, USD/m³", "4"),
        ("LCC_annual", "Annualised life-cycle cost", "USD/yr", "4"),
        ("LCC̃", "Normalised annual LCC (annual LCC ÷ its venue maximum)", "—", "6"),
        ("EF_grid", "Grid carbon emission factor", "kg CO₂e/kWh", "5"),
        ("E_CO2", "Annual indirect CO₂e emissions", "kg CO₂e/yr", "5"),
        ("BWS_raw", "Baseline water stress (WRI Aqueduct 4.0)", "—", "5"),
        ("W_eq", "Water-stress-weighted annual water burden", "m³·stress/yr", "5"),
        ("I_env", "Composite water–carbon externality index", "—", "5, 6"),
        ("α_c, α_w", "Weights of the carbon and water terms (0.50 each)", "—", "5"),
    ]),
    ("Decision score", [
        ("E", "Composite decision score", "—", "6"),
        ("S_safe", "Graded heat-safety score of the WBGT proxy: 0 at 35 °C, 1 at 29 °C", "—", "6"),
        ("B", "Persons-weighted cooling benefit (coverage × occupants × felt drop, normalised)", "—", "6"),
        ("B_max, LCC_max, E_CO2,max, W_eq,max", "Normalisers: maximum of each term over the deployment set for the same venue type", "—", "5, 6"),
        ("w1–w4", "Weights on safety, benefit, cost and environment (0.30/0.30/0.20/0.20)", "—", "6"),
        ("clamp(x, 0, 1)", "Truncation of x to the interval [0, 1]", "—", "6"),
    ]),
]

EXPLICIT = {
    "e_s(T)": [("e", "i"), ("s", "s"), ("(T)", "i")],
    "AT(T, e, v)": [("AT(T, e, v)", "i")],
    "u(x), u0, A0, C": [("u(x), u", "i"), ("0", "s"), (", A", "i"), ("0", "s"), (", C", "i")],
    "ṁ_da, ρ_da": [("ṁ", "i"), ("da", "s"), (", ρ", "i"), ("da", "s")],
    "p, T": [("p", "i"), (", ", "n"), ("T", "i")],
    "c_p, L_v": [("c", "i"), ("p", "s"), (", ", "n"), ("L", "i"), ("v", "s")],
    "p_elec, p_water": [("p", "i"), ("elec", "s"), (", ", "n"), ("p", "i"), ("water", "s")],
    "α_c, α_w": [("α", "i"), ("c", "s"), (", ", "n"), ("α", "i"), ("w", "s")],
    "B_max, LCC_max, E_CO2,max, W_eq,max": [
        ("B", "i"), ("max", "s"), (", ", "n"),
        ("LCC", "i"), ("max", "s"), (", ", "n"),
        ("E", "i"), ("CO2,max", "s"), (", ", "n"),
        ("W", "i"), ("eq,max", "s")],
    "w1–w4": [("w", "i"), ("1", "s"), ("–", "n"), ("w", "i"), ("4", "s")],
    "e_amb, e_zone": [("e", "i"), ("amb", "s"), (", ", "n"), ("e", "i"), ("zone", "s")],
}

def segs(sym):
    if sym in EXPLICIT:
        return EXPLICIT[sym]
    if "_" in sym:
        base, sub = sym.split("_", 1)
        return [(base, "i"), (sub, "s")]
    return [(sym, "i")]

def add_run(p, text, kind="n", size=8, bold=False, italic=False):
    r = p.add_run(text)
    rpr = r._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    rfonts.set(qn("w:ascii"), "Times New Roman")
    rfonts.set(qn("w:hAnsi"), "Times New Roman")
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic or kind in ("i", "s")
    if kind == "s":
        r.font.subscript = True
    return r

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)

def cell_p(cell):
    """Return the single paragraph of a cell, removing extra (merged) paragraphs."""
    for p in cell.paragraphs[1:]:
        p._p.getparent().remove(p._p)
    p = cell.paragraphs[0]
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = Pt(10)
    pPr = p._p.get_or_add_pPr()
    rPr = pPr.find(qn("w:rPr"))
    if rPr is None:
        rPr = OxmlElement("w:rPr")
        pPr.append(rPr)
    for tag in ("w:sz", "w:szCs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = OxmlElement(tag)
            rPr.append(el)
        el.set(qn("w:val"), "16")
    return p

def set_tr_props(tr, header=False):
    trPr = tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))
    if header:
        trPr.append(OxmlElement("w:tblHeader"))

doc = Document(SRC)
ref_tbl = doc.tables[0]

heading = None
for p in doc.paragraphs:
    if p.style.name == "Heading 1" and p.text.strip() == "3. Mathematical Model":
        heading = p
        break
assert heading is not None, "heading not found"

caption = doc.add_paragraph()
cpf = caption.paragraph_format
cpf.page_break_before = True
cpf.keep_with_next = True
cpf.space_before = Pt(0)
cpf.space_after = Pt(3)
add_run(caption, "Table 1b. Nomenclature: every symbol used in Eqs. 1–7, with its meaning, unit and equation number (— = dimensionless).",
        "n", size=9, italic=True)

table = doc.add_table(rows=0, cols=4)
tbl = table._tbl
new_pr = deepcopy(ref_tbl._tbl.tblPr)
tbl.remove(tbl.tblPr)
tbl.insert(0, new_pr)
tblW = new_pr.find(qn("w:tblW"))
tblW.set(qn("w:w"), "9972")
tblW.set(qn("w:type"), "dxa")

widths = [1815, 5857, 1400, 900]
grid = tbl.find(qn("w:tblGrid"))
for gc, w in zip(grid.findall(qn("w:gridCol")), widths):
    gc.set(qn("w:w"), str(w))

hdr = table.add_row()
set_tr_props(hdr._tr, header=True)
for cell, text, w in zip(hdr.cells, ["Symbol", "Definition", "Unit", "Equation"], widths):
    cell.width = Twips(w)
    shade(cell, "D8D8D8")
    add_run(cell_p(cell), text, "n", bold=True)

for title, rows in GROUPS:
    row = table.add_row()
    set_tr_props(row._tr)
    merged = row.cells[0].merge(row.cells[3])
    merged.width = Twips(sum(widths))
    shade(merged, "F2F2F2")
    add_run(cell_p(merged), title, "n", bold=True, italic=True)
    for sym, definition, unit, eq in rows:
        r_ = table.add_row()
        set_tr_props(r_._tr)
        c = r_.cells
        for i in range(4):
            c[i].width = Twips(widths[i])
        for txt, kind in segs(sym):
            add_run(cell_p(c[0]), txt, kind)
        add_run(cell_p(c[1]), definition, "n")
        add_run(cell_p(c[2]), unit, "n")
        add_run(cell_p(c[3]), eq, "n")

heading._p.addprevious(caption._p)
heading._p.addprevious(tbl)
heading.paragraph_format.page_break_before = True

for p in doc.paragraphs:
    if p.text.startswith("Figure 1 is the roadmap for this section"):
        p.add_run(" Every symbol used in Eqs. 1–7 is defined in Table 1b.")
        break

doc.save(OUT)
print("saved", OUT)
print("table rows:", len(table.rows), "cols:", len(table.columns))
