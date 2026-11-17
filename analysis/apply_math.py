# -*- coding: utf-8 -*-
"""Apply professional OMML formatting to every remaining linear formula."""
import re
import sys
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

import mathdoc

WIDTH = 9978
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"

# ---------------------------------------------------------------- symbols
SYM_LATEX = {
    "T_db": r"T_{\mathrm{db}}",
    "T_wb": r"T_{\mathrm{wb}}",
    "T_zone": r"T_{\mathrm{zone}}",
    "T_nwb": r"T_{\mathrm{nwb}}",
    "T_g": r"T_{\mathrm{g}}",
    "ΔT_phys": r"\Delta T_{\mathrm{phys}}",
    "ΔT_nom": r"\Delta T_{\mathrm{nom}}",
    "ΔT_eff": r"\Delta T_{\mathrm{eff}}",
    "S_safe": r"S_{\mathrm{safe}}",
    "N_eff": r"N_{\mathrm{eff}}",
    "A_cov": r"A_{\mathrm{cov}}",
    "A_waiting": r"A_{\mathrm{waiting}}",
    "A_platform": r"A_{\mathrm{platform}}",
    "p_s": r"p_{s}",
    "e_s": r"e_{s}",
    "e_amb": r"e_{\mathrm{amb}}",
    "e_zone": r"e_{\mathrm{zone}}",
    "γ_p": r"\gamma_{p}",
    "p_elec": r"p_{\mathrm{elec}}",
    "p_water": r"p_{\mathrm{water}}",
    "V_w": r"V_{\mathrm{w}}",
    "L_life": r"L_{\mathrm{life}}",
    "r_om": r"r_{\mathrm{om}}",
    "H_yr": r"H_{\mathrm{yr}}",
    "C_cap": r"C_{\mathrm{cap}}",
    "EF_grid": r"EF_{\mathrm{grid}}",
    "BWS_raw": r"BWS_{\mathrm{raw}}",
    "BWS_HK": r"BWS_{\mathrm{HK}}",
    "EF_HK": r"EF_{\mathrm{HK}}",
    "EF_PHX": r"EF_{\mathrm{PHX}}",
    "I_env": r"I_{\mathrm{env}}",
    "E_CO2": r"E_{\mathrm{CO₂}}",
    "W_eq": r"W_{\mathrm{eq}}",
    "Q_air": r"Q_{\mathrm{air}}",
    "c_p": r"c_{p}",
    "L_v": r"L_{\mathrm{v}}",
    "ρ_da": r"\rho_{\mathrm{da}}",
    "ṁ_da": r"ṁ_{\mathrm{da}}",
    "v_amb": r"v_{\mathrm{amb}}",
    "v_eff": r"v_{\mathrm{eff}}",
    "u_0": r"u_{0}",
    "A_0": r"A_{0}",
    "u_j": r"u_{j}",
    "κ_bus": r"\kappa_{\mathrm{bus}}",
    "κ_rail": r"\kappa_{\mathrm{rail}}",
    "LCC_max": r"LCC_{\mathrm{max}}",
    "B_max": r"B_{\mathrm{max}}",
    "W_zone": r"W_{\mathrm{zone}}",
    "W_ambient": r"W_{\mathrm{ambient}}",
    "u_1": r"u_{1}",
}
TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_])(" + "|".join(sorted(map(re.escape, SYM_LATEX), key=len, reverse=True)) + r")(?![A-Za-z0-9_])"
)
GREEK_BARE = "ηφγκεαβσρμλ"
GREEK_RE = re.compile(r"(?<![A-Za-z])([" + GREEK_BARE + r"])(?![A-Za-z])")
E_RE = re.compile(r"(?<![A-Za-z0-9])E(?![A-Za-z0-9\-])")
REL_RE = re.compile(
    r"(?<![A-Za-z0-9_])((?:[A-Za-zΔ][A-Za-z0-9]*(?:_[A-Za-z0-9,]+)?)|[ηφγκε])"
    r"\s*(=|≈|≤|≥|<|>)\s*(\$?[−–-]?\d[\d,]*(?:\.\d+)?(?:\s*[–-]\s*\d[\d,]*(?:\.\d+)?)?)"
)

# ------------------------------------------------------------- paragraph specs
B = "b"
T = "t"
M = "m"
D = "disp"

SPECS = {
    25: ("Assumption 2", [
        (B, "Assumption 2 — Isenthalpic adiabatic humidification."),
        (T, " Air through the wetted medium follows a constant wet-bulb line, so the dry-bulb drop is bounded by "),
        (M, r"\varepsilon\left(T_{\mathrm{db}}-T_{\mathrm{wb}}\right)"),
        (T, ", with "), (M, r"\varepsilon=0.80"),
        (T, " (sensitivity 0.70–0.90). "), (M, r"T_{\mathrm{wb}}"),
        (T, " is the psychrometric wet bulb at the local surface pressure (950 hPa Phoenix, 1,000 hPa Hong Kong)."),
    ]),
    27: ("Assumption 4", [
        (B, "Assumption 4 — Jet mixing and uniform occupancy."),
        (T, " The zone velocity is "),
        (M, r"v_{\mathrm{eff}}=v_{\mathrm{amb}}+\kappa\left(Q_{\mathrm{air}}/A_{\mathrm{cov}}\right)"),
        (T, ", with "), (M, r"\kappa=45"),
        (T, " (dimensionless momentum amplification, sensitivity 30–60); "), (M, r"\kappa"),
        (T, " is a lumped jet-mixing coefficient, not a physical velocity; 45 is a literature-informed assumption "
            "(sensitivity 30–60), and it is not calibrated in this study. Commuters are uniformly distributed, so "
            "beneficiaries scale with "),
        (M, r"\varphi=\min\left(1,\;n\,A_{\mathrm{cov}}/A_{\mathrm{waiting}}\right)"),
        (T, ", with "), (M, r"N_{\mathrm{eff}}=6"),
        (T, " (bus) and 45 (rail design capacity). The 6-person figure is a peak-hour estimate, not a headcount: "
            "384 weekday boardings in both directions (208 + 176), a 12–15% peak-hour share (an assumption, not a "
            "measurement), a 16-hour analysis window inside a service day of about 20 h, and a 6-minute mean wait on "
            "a 12-minute headway give "),
        (M, r"N\approx4.6\text{–}5.8"),
        (T, "; we take the upper end, 6. Occupancy scales "), (M, r"\eta"),
        (T, " but cancels in "), (M, r"E"), (T, " (Section 5.7)."),
    ]),
    28: ("Assumption 5", [
        (B, "Assumption 5 — Commercial tariffs and straight-line depreciation."),
        (T, " Capital costs depreciate linearly over "), (M, r"L=5\text{–}7"),
        (T, " years and annual maintenance is "), (M, r"r_{\mathrm{om}}=3\text{–}8\%"),
        (T, " of capital. Energy uses the latest local tariffs (Phoenix 2024 APS E-32 with demand [5]; Hong Kong "
            "2026 CLP [6]) and water the City of Phoenix 2024 card and the Hong Kong WSD schedule; the 2026 Phoenix "
            "scenario and the Hong Kong 50% water concession are tested separately."),
    ]),
    29: ("Assumption 6", [
        (B, "Assumption 6 — Shaded conditions and an approximate heat index."),
        (T, " Both venue types provide overhead shading, so the heat index is the proxy "),
        (M, r"\mathrm{WBGT}\approx0.7\,T_{\mathrm{wb}}+0.3\,T_{\mathrm{db}}"),
        (T, " (ISO 7243 no-solar-load form [3], with the natural wet bulb approximated by the psychrometric wet bulb "
            "and the globe temperature by the dry-bulb). This is an index approximation, not a compliance measurement; "
            "the 33 °C reference (ISO 7243 115 W) is the graded benchmark (Section 3.7), with 30 °C as a "
            "vulnerable-population screen and 28 °C as a stress test. A black-globe offset of +3 K is tested in "
            "Section 5.1."),
    ]),
    47: ("", [
        (D, r"\Delta T_{\mathrm{phys}}=\min\left(\Delta T_{\mathrm{nom}},\;\varepsilon\left(T_{\mathrm{db}}-T_{\mathrm{wb}}\right)\right).", "(Eq. 1)"),
    ]),
    48: ("T_wb is solved", [
        (M, r"T_{\mathrm{wb}}"),
        (T, " is solved from the psychrometric relation at surface pressure "), (M, r"p_{s}"),
        (T, " [1]: "),
        (M, r"e_{s}\left(T_{\mathrm{wb}}\right)-\gamma_{p}\left(T_{\mathrm{db}}-T_{\mathrm{wb}}\right)=e_{\mathrm{amb}},"),
        (T, " where "),
        (M, r"\gamma_{p}=1.006\,p_{s}/(0.622\times2450)"),
        (T, " hPa/K. At 41 °C/18% and 950 hPa this gives 21.8 °C; at 31.7 °C/77% and 1,000 hPa it gives 28.2 °C. "
            "For pure fans "), (M, r"\varepsilon=0"), (T, " and "), (M, r"\Delta T_{\mathrm{phys}}=0."),
    ]),
    50: ("", [
        (D, r"\Delta T_{\mathrm{eff}}=AT\left(T_{\mathrm{db}},\,e_{\mathrm{amb}},\,v_{\mathrm{amb}}\right)-AT\left(T_{\mathrm{zone}},\,e_{\mathrm{zone}},\,v_{\mathrm{eff}}\right),", "(Eq. 2) [2]"),
        (D, r"AT\left(T,e,v\right)=T+0.33e-0.70v-4.00.", ""),
    ]),
    51: ("", [
        (D, r"T_{\mathrm{zone}}=T_{\mathrm{db}}-\left(1-\gamma\right)\Delta T_{\mathrm{phys}};", ""),
        (D, r"e_{\mathrm{zone}}=\min\left(e_{s}\left(T_{\mathrm{zone}}\right),\;e_{\mathrm{amb}}+0.665\left(1-\gamma\right)\Delta T_{\mathrm{phys}}\right);", ""),
        (D, r"v_{\mathrm{eff}}=v_{\mathrm{amb}}+\kappa\left(Q_{\mathrm{air}}/A_{\mathrm{cov}}\right),", ""),
        (D, r"\text{with }Q_{\mathrm{air}}=\mathrm{CFM}\times1.699/3600\ \mathrm{m³/s}.", ""),
    ]),
    54: ("", [
        (D, r"\eta=\frac{\varphi\cdot N_{\mathrm{eff}}\cdot\Delta T_{\mathrm{eff}}}{n\cdot P_{\mathrm{elec}}},", "(Eq. 3)"),
        (D, r"\varphi=\min\left(1,\;\frac{n\cdot A_{\mathrm{cov}}}{A_{\mathrm{waiting}}}\right).", ""),
    ]),
    57: ("", [
        (D, r"LCC_{\mathrm{annual}}=\left(\frac{1}{L_{\mathrm{life}}}+r_{\mathrm{om}}\right)n\,C_{\mathrm{cap}}+H_{\mathrm{yr}}\left(n\,P_{\mathrm{elec}}\,p_{\mathrm{elec}}+\frac{n\,V_{\mathrm{w}}}{1000}\,p_{\mathrm{water}}\right).", "(Eq. 4)"),
    ]),
    59: ("", [
        (D, r"V_{\mathrm{w}}=\frac{3600\;\dot{m}_{\mathrm{da}}\,c_{p}\,\Delta T_{\mathrm{phys}}}{L_{\mathrm{v}}},\qquad \dot{m}_{\mathrm{da}}=Q_{\mathrm{air}}\,\rho_{\mathrm{da}}.", "(Eq. 7)"),
    ]),
    62: ("", [
        (D, r"I_{\mathrm{env}}=\alpha_{c}\frac{E_{\mathrm{CO₂}}}{E_{\mathrm{CO₂,max}}}+\alpha_{w}\frac{W_{\mathrm{eq}}}{W_{\mathrm{eq,max}}},\qquad \text{with }\alpha_{c}=\alpha_{w}=0.50;", "(Eq. 5)"),
        (D, r"E_{\mathrm{CO₂}}=n\,P_{\mathrm{elec}}\,H_{\mathrm{yr}}\,EF_{\mathrm{grid}};\qquad W_{\mathrm{eq}}=\frac{n\,V_{\mathrm{w}}}{1000}\,H_{\mathrm{yr}}\,BWS_{\mathrm{raw}}.", ""),
    ]),
    65: ("", [
        (D, r"E=w_{1}S_{\mathrm{safe}}+w_{2}B-w_{3}LCC̃-w_{4}I_{\mathrm{env}}.", "(Eq. 6)"),
    ]),
    66: ("", [
        (D, r"\mathrm{WBGT}_{\mathrm{proxy}}=0.7\,T_{\mathrm{wb,zone}}+0.3\,T_{\mathrm{zone}};", ""),
        (D, r"S_{\mathrm{safe}}\left(W\right)=\mathrm{clamp}\left(\frac{35-W}{6},\;0,\;1\right);", ""),
        (D, r"B=\frac{\varphi\,N_{\mathrm{eff}}\,\Delta T_{\mathrm{eff}}}{B_{\mathrm{max}}};\qquad LCC̃=\frac{LCC}{LCC_{\mathrm{max}}};", ""),
        (D, r"\text{baseline weights }\left(w_{1},w_{2},w_{3},w_{4}\right)=\left(0.30,\;0.30,\;0.20,\;0.20\right).", ""),
    ]),
    60: ("with c_p", [
        (T, "with "), (M, r"c_{p}=1.006"), (T, " kJ/(kg·K), "), (M, r"L_{\mathrm{v}}=2450"),
        (T, " kJ/kg and "), (M, r"\rho_{\mathrm{da}}=p/(287T)"),
        (T, ". At the Phoenix design point a 3,100 CFM unit with an 11 °C drop requires about 25 L/h; at the Hong "
            "Kong design point the smaller drop requires about 6.9 L/h. Manufacturer tank/run-time rates "
            "(10.6–18.2 L/h) are treated as a sensitivity, because they are refill rates rather than measurements of "
            "evaporated water. Eq. 7 is the auxiliary water balance that supplies "),
        (M, r"V_{\mathrm{w}}"), (T, " to Eqs. 4–5; it is not one of the six decision equations."),
    ]),
    67: ("OSHA and CCOHS", [
        (T, "OSHA and CCOHS define the indoor index as "),
        (M, r"\mathrm{WBGT}=0.7\,T_{\mathrm{nwb}}+0.3\,T_{\mathrm{g}}"),
        (T, " [19,14], where "), (M, r"T_{\mathrm{nwb}}"),
        (T, " is the natural wet bulb, which responds to air speed. Our proxy replaces "), (M, r"T_{\mathrm{nwb}}"),
        (T, " with the psychrometric wet bulb and "), (M, r"T_{\mathrm{g}}"),
        (T, " with the dry bulb, so it is wind-blind by construction; Section 5.6 gives a sensitivity and the "
            "fan-beneficial limit."),
    ]),
    68: ("Two changes", [
        (T, "Two changes from a conventional weighted score matter. First, the safety term is graded over 29–35 °C "
            "with the 33 °C reference line at one third, so cooling below 33 °C still earns credit instead of "
            "saturating at zero cost; the 29–35 °C window is a −4/+2 K band around the resting reference, and its "
            "endpoints are a design choice tested at 30 °C and 28 °C in Section 5.7. Second, safety is "
            "population-weighted: "),
        (M, r"S_{\mathrm{safe}}=\varphi\,S_{\mathrm{safe}}\left(W_{\mathrm{zone}}\right)+\left(1-\varphi\right)S_{\mathrm{safe}}\left(W_{\mathrm{ambient}}\right),"),
        (T, " so the share of occupants outside the jet is not ignored. Before normalisation the benefit term is "
            "proportional to persons, so a platform and a shelter cannot be compared on "), (M, r"E"),
        (T, "; inside a venue the normaliser removes the occupancy scale, and "), (M, r"\eta"),
        (T, " carries the absolute service level."),
    ]),
    83: ("Q2b revises", [
        (T, "Q2b revises the Q2a model in three ways. Q2a assumed one unit that covers a small shelter completely, "
            "but a rail waiting zone is 120 m² in Phoenix and 128 m² in Hong Kong, so coverage must be explicit. "
            "First, "),
        (M, r"\varphi=\min\left(1,\;n\,A_{\mathrm{cov}}/A_{\mathrm{waiting}}\right)"),
        (T, " gives partial credit for partial coverage instead of assuming "), (M, r"\varphi=1"),
        (T, ". Second, the normalisers ("),
        (M, r"B_{\mathrm{max}},\;LCC_{\mathrm{max}},\;E_{\mathrm{CO₂,max}},\;W_{\mathrm{eq,max}}"),
        (T, ") are computed per venue type, so "), (M, r"E"),
        (T, " compares bus with bus and rail with rail instead of mixing a 6-person shelter with a 45-person "
            "platform. Third, safety is population-weighted, "),
        (M, r"S_{\mathrm{safe}}=\varphi\,S\left(W_{\mathrm{zone}}\right)+\left(1-\varphi\right)S\left(W_{\mathrm{ambient}}\right)"),
        (T, ", so occupants outside the jet are counted. The revision changes the answer. With Q2a's full-coverage "
            "assumption the one- versus two-unit question is only a cost question; with explicit coverage, one MC61V "
            "covers the zone ("), (M, r"\varphi=1.000"), (T, ", "), (M, r"E=0.4034"),
        (T, ") while two MC37V cover it at higher cost (LCC $487.60 vs $397.41, "), (M, r"E=0.3642"),
        (T, "), and no second unit pays in this base (2× Portacool 0.2114 vs 1× 0.3046)."),
    ]),
    137: ("Equation 2 is wind-neutral", [
        (T, "Equation 2 is wind-neutral: "), (M, r"v_{\mathrm{amb}}"),
        (T, " appears in both "), (M, r"AT_{\mathrm{amb}}"), (T, " and "), (M, r"AT_{\mathrm{zone}}"),
        (T, " and cancels. To give the model a wind dependence we borrow the flight-effect form of von Glahn [16], "),
        (M, r"F\left(v\right)=1+0.9\,AR^{1/3}\left(v/u_{j}\right)^{3/2}"),
        (T, ", but the step from that study to this paper is an assumption, not a result: the cited report describes "
            "how an external flow changes centreline decay and core length, and we map it to a retained-cooling "
            "fraction "),
        (M, r"\gamma_{\mathrm{eff}}\left(v\right)=1-\left(1-\gamma_{0}\right)F\left(v_{\mathrm{ref}}\right)/F\left(v\right)"),
        (T, " without deriving that mapping. The correction is normalised at each city's own design wind "
            "(Phoenix 1.8 m/s, Hong Kong 1.5 m/s), so the baseline tables are unchanged at "),
        (M, r"v=v_{\mathrm{ref}}"),
        (T, "; AR is the assumed outlet aspect ratio (1.25 for MC37V, 1.6 for MC61V, 1.0 for Portacool, 1.7 for the "
            "drum fan) and "), (M, r"u_{j}=Q/A_{0}"),
        (T, ". The scenario is illustrative and the final recommendations use the base model without it. The CBE "
            "fans-and-heat map [18] places 31.7 °C / 77% in the fan-beneficial band and excludes conditions above "
            "40 °C for healthy adults with the listed inputs; that is why Section 4.1 separates the Q2a efficiency "
            "ranking from deployment at 41 °C."),
    ]),
}

# new prose paragraph created after p51
P51_PROSE = [
    (T, "Rectangular jets decay more slowly than circular ones, and the rate depends on the nozzle aspect ratio and "
        "on the sidewalls [17]; following von Glahn's rectangular-plume model [16], the low-speed centreline decay "
        "can be written "),
    (M, r"u\left(x\right)\approx C\,u_{0}\frac{\sqrt{A_{0}}}{x}"),
    (T, ", with "), (M, r"A_{0}"), (T, " the outlet area and "), (M, r"C\approx2.4"),
    (T, ". For the 3,100 CFM unit ("), (M, r"Q=1.463\ \mathrm{m³/s}"), (T, ", "),
    (M, r"A_{0}\approx0.45\ \mathrm{m²}"),
    (T, " assumed from the grille envelope, "), (M, r"u_{0}=3.25\ \mathrm{m/s}"), (T, ", "),
    (M, r"q=Q/A_{\mathrm{cov}}=0.0166\ \mathrm{m/s}"),
    (T, ") this gives "), (M, r"\kappa\left(x\right)=u\left(x\right)/q\approx315/x"),
    (T, ": 157 at 2 m, 79 at 4 m, 52 at 6 m and 39 at 8 m. "), (M, r"\kappa=45"),
    (T, " therefore corresponds to a throw of about 7.0 m, and using one value for both venues assumes the same "
        "throw distance: a 3–4 m bus shelter implies "), (M, r"\kappa\approx80\text{–}105"),
    (T, ", a 6–8 m platform "), (M, r"\kappa\approx39\text{–}52"),
    (T, ". We keep "), (M, r"\kappa=45"),
    (T, " as the design value and test 30–60 in Section 5.1; because the bus-shelter estimate (80–105) lies outside "
        "that range, Section 5.1 also reports "), (M, r"\kappa=80"), (T, " and 105, where the fan overtakes the "
        "evaporative unit above "), (M, r"\kappa\approx92"),
    (T, ". No site calibration is available in this study."),
]

# explicit literal replacements for paragraphs converted in place
EXPLICIT = {
    74: [
        ("ΔT_nom 0", r"\Delta T_{\mathrm{nom}}=0"),
        ("ΔT_nom 5", r"\Delta T_{\mathrm{nom}}=5"),
        ("ΔT_nom 8", r"\Delta T_{\mathrm{nom}}=8"),
        ("A_cov = A_waiting = 15 m²", r"A_{\mathrm{cov}}=A_{\mathrm{waiting}}=15\ \mathrm{m²}"),
        ("γ = 0.55", r"\gamma=0.55"),
        ("N_eff = 6", r"N_{\mathrm{eff}}=6"),
    ],
    75: [("P_elec × H_yr", r"P_{\mathrm{elec}}\times H_{\mathrm{yr}}")],
    120: [
        ("κ_bus ~ U(60,105)", r"\kappa_{\mathrm{bus}}\sim U\left(60,105\right)"),
        ("κ_rail ~ U(35,55)", r"\kappa_{\mathrm{rail}}\sim U\left(35,55\right)"),
        ("γ ~ U(0.45,0.65)", r"\gamma\sim U\left(0.45,0.65\right)"),
        ("E(MC61V) > E(MC37V)", r"E\left(\mathrm{MC61V}\right)>E\left(\mathrm{MC37V}\right)"),
    ],
    89: [],
}

# ---------------------------------------------------------------- table cells
TABLE_SPECS = {
    # (table, row, col): parts
    (0, 4, 2): [(T, "κ dimensionless, assumed 45; "), (M, r"N_{\mathrm{eff}}"), (T, " assumed")],
    (0, 5, 2): [(T, "APS/CLP/WSD; "), (M, r"L"), (T, ", "), (M, r"r_{\mathrm{om}}"), (T, " assumed")],
    (2, 0, 3): [(M, r"A_{\mathrm{cov}}"), (T, " (m²)")],
    (2, 0, 5): [(M, r"V_{\mathrm{w}}"), (T, " PHX/HK (L/h)")],
    (2, 0, 6): [(M, r"C_{\mathrm{cap}}"), (T, " (USD)")],
    (3, 1, 1): [(M, r"T_{\mathrm{db}}"), (T, ", RH")],
    (3, 2, 1): [(M, r"T_{\mathrm{wb}}")],
    (3, 3, 1): [(M, r"p_{s}")],
    (20, 2, 0): [(M, r"\varepsilon=0.70")],
    (20, 3, 0): [(M, r"\varepsilon=0.90")],
    (20, 4, 0): [(M, r"\Delta T_{\mathrm{nom}}=8.8")],
    (20, 5, 0): [(M, r"\Delta T_{\mathrm{nom}}=13.2")],
    (20, 18, 0): [(M, r"\kappa=30")],
    (20, 19, 0): [(M, r"\kappa=105")],
    (20, 20, 0): [(M, r"\gamma=-0.10")],
    (20, 21, 0): [(M, r"\gamma=+0.10")],
    (20, 24, 0): [(M, r"BWS_{\mathrm{HK}}=0.850")],
    (20, 25, 0): [(M, r"EF_{\mathrm{HK}}=0.465")],
    (20, 26, 0): [(M, r"EF_{\mathrm{PHX}}=0.25")],
    (20, 27, 0): [(M, r"EF_{\mathrm{PHX}}=0.36")],
}

# nomenclature table (table 1), symbol column
NOMEN = {
    2: r"T_{\mathrm{db}}",
    3: r"T_{\mathrm{wb}}",
    4: r"T_{\mathrm{wb,zone}}",
    5: r"T_{\mathrm{zone}}",
    6: r"e_{\mathrm{amb}},\;e_{\mathrm{zone}}",
    7: r"e_{s}\left(T\right)",
    8: r"p_{s}",
    9: r"\gamma_{p}",
    10: r"\Delta T_{\mathrm{nom}}",
    11: r"\Delta T_{\mathrm{phys}}",
    12: r"\Delta T_{\mathrm{eff}}",
    13: r"AT\left(T,e,v\right)",
    14: r"\mathrm{WBGT}_{\mathrm{proxy}}",
    16: r"v_{\mathrm{amb}}",
    17: r"v_{\mathrm{eff}}",
    18: r"Q_{\mathrm{air}}",
    19: r"\kappa",
    20: r"\gamma",
    21: r"A_{\mathrm{cov}}",
    22: r"A_{\mathrm{waiting}}",
    23: r"\varphi",
    24: r"N_{\mathrm{eff}}",
    25: r"u\left(x\right),\;u_{0},\;A_{0},\;C",
    26: r"q",
    28: r"n",
    29: r"P_{\mathrm{elec}}",
    30: r"\varepsilon",
    31: r"\eta",
    32: r"H_{\mathrm{yr}}",
    33: r"L_{\mathrm{life}}",
    34: r"r_{\mathrm{om}}",
    35: r"V_{\mathrm{w}}",
    36: r"ṁ_{\mathrm{da}},\;\rho_{\mathrm{da}}",
    37: r"p,\;T",
    38: r"c_{p},\;L_{\mathrm{v}}",
    39: r"C_{\mathrm{cap}}",
    41: r"p_{\mathrm{elec}},\;p_{\mathrm{water}}",
    42: r"LCC_{\mathrm{annual}}",
    43: r"LCC̃",
    44: r"EF_{\mathrm{grid}}",
    45: r"E_{\mathrm{CO₂}}",
    46: r"BWS_{\mathrm{raw}}",
    47: r"W_{\mathrm{eq}}",
    48: r"I_{\mathrm{env}}",
    49: r"\alpha_{c},\;\alpha_{w}",
    51: r"E",
    52: r"S_{\mathrm{safe}}",
    53: r"B",
    54: r"B_{\mathrm{max}},\;LCC_{\mathrm{max}},\;E_{\mathrm{CO₂,max}},\;W_{\mathrm{eq,max}}",
    55: r"w_{1}\text{–}w_{4}",
    56: r"\mathrm{clamp}\left(x,0,1\right)",
}

# ---------------------------------------------------------------- helpers
def iter_runs(p):
    out = []
    for ch in p._p.iterchildren():
        if ch.tag == qn("w:r"):
            txt = "".join(t.text or "" for t in ch.findall(qn("w:t")))
            out.append((ch, txt))
    return out


def convert_spans(p, explicit=(), size=None):
    runs = iter_runs(p)
    if not runs:
        return 0
    text = "".join(t for _, t in runs)
    nchars = len(text)
    if not nchars:
        return 0
    # per-char rPr
    char_rpr = []
    for r, t in runs:
        rpr = r.find(qn("w:rPr"))
        for _ in t:
            char_rpr.append(rpr)
    spans = []  # (start, end, latex)
    used = [False] * nchars
    for old, latex in explicit:
        i = text.find(old)
        if i < 0:
            raise SystemExit("explicit span not found: %r" % old[:60])
        for k in range(i, i + len(old)):
            used[k] = True
        spans.append((i, i + len(old), latex))
    def free(a, b):
        return not any(used[a:b])
    for m in REL_RE.finditer(text):
        a, b = m.span()
        if not free(a, b):
            continue
        num = m.group(3)
        b = m.end()
        while num.endswith(","):
            num = num[:-1]
            b -= 1
        num = num.replace(",", "")
        if "$" in num or "−" in num:
            continue
        if "–" in num:
            num = num.replace("–", r"\text{–}")
        left = m.group(1)
        if left not in SYM_LATEX and not (len(left) == 1 and (left in GREEK_BARE or left in "EBNnqx")):
            continue
        latex = "%s = %s" % (sym_latex(left), num)
        spans.append((a, b, latex))
        for k in range(a, b):
            used[k] = True
    for m in TOKEN_RE.finditer(text):
        a, b = m.span()
        if not free(a, b):
            continue
        spans.append((a, b, SYM_LATEX[m.group(1)]))
        for k in range(a, b):
            used[k] = True
    for m in GREEK_RE.finditer(text):
        a, b = m.span()
        if not free(a, b):
            continue
        spans.append((a, b, m.group(1)))
        for k in range(a, b):
            used[k] = True
    for m in E_RE.finditer(text):
        a, b = m.span()
        if not free(a, b):
            continue
        spans.append((a, b, "E"))
        for k in range(a, b):
            used[k] = True
    if not spans:
        return 0
    spans.sort()
    # merge adjacent math spans to reduce run count
    merged = []
    for s in spans:
        if merged and merged[-1][1] == s[0]:
            merged[-1] = (merged[-1][0], s[1], merged[-1][2] + r"\ " + s[2])
        else:
            merged.append(list(s))
    merged = [tuple(x) for x in merged]
    # rebuild
    from docx.oxml import parse_xml
    for ch in list(p._p.iterchildren()):
        if ch.tag in (qn("w:r"), qn("m:oMath"), qn("m:oMathPara")):
            p._p.remove(ch)
    pos = 0
    for a, b, latex in merged:
        if a > pos:
            emit_text(p, text[pos:a], char_rpr[pos:a])
        p._p.append(parse_xml(omml.omath(latex, size=size)))
        pos = b
    if pos < nchars:
        emit_text(p, text[pos:], char_rpr[pos:])
    return len(merged)


def sym_latex(name):
    return SYM_LATEX.get(name, name)


def emit_text(p, chunk, rprs):
    from docx.oxml import OxmlElement
    import copy
    if not chunk:
        return
    # group by identical rPr xml
    groups = []
    cur = []
    cur_xml = None
    for ch, rpr in zip(chunk, rprs):
        x = rpr.xml if rpr is not None else ""
        if cur and x != cur_xml:
            groups.append("".join(cur))
            cur = []
        cur.append(ch)
        cur_xml = x
    if cur:
        groups.append("".join(cur))
    # rebuild with rPr of first char in each group
    idx = 0
    for g in groups:
        r = OxmlElement("w:r")
        rpr = rprs[idx]
        if rpr is not None:
            r.append(copy.deepcopy(rpr))
        t = OxmlElement("w:t")
        t.set(XML_SPACE, "preserve")
        t.text = g
        r.append(t)
        p._p.append(r)
        idx += len(g)


import omml


def main(src, dst):
    doc = Document(src)
    paras = list(doc.paragraphs)
    for idx, (prefix, parts) in SPECS.items():
        p = paras[idx]
        cur = p.text
        if prefix and prefix not in cur:
            raise SystemExit("paragraph %d mismatch: %r" % (idx, cur[:60]))
        mathdoc.rebuild(p, parts, width=WIDTH, display=any(k == "disp" for k, *_ in parts))
    # split p51: prose paragraph after it (styled like the following body paragraph)
    import copy
    from docx.text.paragraph import Paragraph
    p51 = paras[51]
    newp = OxmlElement("w:p")
    ref_pPr = paras[52]._p.find(qn("w:pPr"))
    if ref_pPr is not None:
        newp.append(copy.deepcopy(ref_pPr))
    p51._p.addnext(newp)
    prose = Paragraph(newp, p51._parent)
    rpr = mathdoc.base_rpr(paras[52])
    for part in P51_PROSE:
        if part[0] == "m":
            mathdoc.add_math(prose, part[1])
        else:
            mathdoc.add_text(prose, part[1], rpr=rpr)
    # in-place span conversion for remaining body paragraphs
    rebuilt = set(SPECS)
    count = 0
    for i, p in enumerate(paras):
        if i in rebuilt:
            continue
        if p._p.find(qn("w:hyperlink")) is not None:
            continue
        if p._p.find(qn("m:oMath")) is not None:
            continue
        count += convert_spans(p, EXPLICIT.get(i, ()))
    # tables: explicit cells first
    for (ti, ri, ci), parts in TABLE_SPECS.items():
        cell = doc.tables[ti].rows[ri].cells[ci]
        mathdoc.rebuild(cell.paragraphs[0], parts, size=16)
        mathdoc.relax_line(cell.paragraphs[0])
    for row_i, latex in NOMEN.items():
        cell = doc.tables[1].rows[row_i].cells[0]
        mathdoc.rebuild(cell.paragraphs[0], [(M, latex)], size=16)
        mathdoc.relax_line(cell.paragraphs[0], 170)
    mathdoc.tight_table(doc.tables[1], top=6, bottom=6, left=70, right=70)
    for row in doc.tables[1].rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                mathdoc.relax_line(p, 170)
    for ti, tb in enumerate(doc.tables):
        for ri, row in enumerate(tb.rows):
            for ci, cell in enumerate(row.cells):
                if (ti, ri, ci) in TABLE_SPECS:
                    continue
                for p in cell.paragraphs:
                    if p._p.find(qn("w:hyperlink")) is not None:
                        continue
                    if p._p.find(qn("m:oMath")) is not None:
                        continue
                    if convert_spans(p, (), size=16):
                        mathdoc.relax_line(p)
    doc.save(dst)
    print("paragraph math spans:", count)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
