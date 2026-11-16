"""Patch v1.3: use the supplied sources (NASA TM 102047, Deo et al. 2007,
CBE fans/heat, OSHA OTM, CCOHS, Phoenix TOD profiles) in the paper."""

import io

P = r"C:\Users\kukat\Desktop\USA\analysis\build_full_paper.py"
s = io.open(P, encoding="utf-8").read()

def rep(old, new, count=1):
    global s
    n = s.count(old)
    assert n == count, (n, old[:90])
    s = s.replace(old, new)

# ---------- 3.3 kappa derivation
old = ("T_zone = T_db − (1−γ)ΔT_phys; e_zone = min(e_s(T_zone), e_amb + 0.665(1−γ)ΔT_phys); "
       "v_eff = v_amb + κ(Q_air/A_cov), with Q_air = CFM × 1.699/3600 m³/s. "
       "κ = 45 is a dimensionless momentum-amplification coefficient, not a velocity: Q_air/A_cov already has units of m/s. "
       "It is a literature-informed assumption (sensitivity 30–60), not a field calibration. For the 3,100 CFM unit, "
       "Q_air/A_cov ≈ 0.017 m/s, so κ = 45 corresponds to about 0.75 m/s at the occupant — the order of an indoor jet velocity, "
       "but not a measurement at either site.")
new = ("T_zone = T_db − (1−γ)ΔT_phys; e_zone = min(e_s(T_zone), e_amb + 0.665(1−γ)ΔT_phys); "
       "v_eff = v_amb + κ(Q_air/A_cov), with Q_air = CFM × 1.699/3600 m³/s. "
       "Rectangular jets decay more slowly than circular ones, and the rate depends on the nozzle aspect ratio and on the sidewalls [17]; "
       "following von Glahn's rectangular-plume model [16], the low-speed centreline decay can be written u(x) ≈ C·u0·√A0 / x, with A0 the outlet area "
       "and C ≈ 2.4. For the 3,100 CFM unit (Q = 1.463 m³/s, A0 ≈ 0.45 m², u0 = 3.25 m/s, q = Q/A_cov = 0.0166 m/s) this gives "
       "κ(x) = u(x)/q ≈ 315/x: 157 at 2 m, 79 at 4 m, 52 at 6 m and 39 at 8 m. κ = 45 therefore corresponds to a throw of about 6.5 m, "
       "and using one value for both venues assumes the same throw distance: a 3–4 m bus shelter implies κ ≈ 80–105, a 6–8 m platform "
       "κ ≈ 39–52. We keep κ = 45 as the design value and test 30–60 in Section 5.1; site calibration is specified in Section 5.5.")
rep(old, new)

# ---------- 3.7 WBGT provenance
rep('WBGT_proxy = 0.7 T_wb,zone + 0.3 T_zone; S_safe(W) = clamp((32 − W)/6, 0, 1); B = φ·N_eff·ΔT_eff / B_max; LCC̃ = LCC/LCC_max; baseline weights (w1,w2,w3,w4) = (0.30, 0.30, 0.20, 0.20).',
    'WBGT_proxy = 0.7 T_wb,zone + 0.3 T_zone; S_safe(W) = clamp((32 − W)/6, 0, 1); B = φ·N_eff·ΔT_eff / B_max; LCC̃ = LCC/LCC_max; baseline weights (w1,w2,w3,w4) = (0.30, 0.30, 0.20, 0.20).')
rep('para("Two changes from a conventional weighted score matter.',
    'para("OSHA and CCOHS define the indoor index as WBGT = 0.7 T_nwb + 0.3 T_g [19,14], where T_nwb is the natural wet bulb, which responds to air speed. Our proxy replaces T_nwb with the psychrometric wet bulb and T_g with the dry bulb, so it is wind-blind by construction; Section 5.6 quantifies the effect and the fan-beneficial limit.")\n'
    'para("Two changes from a conventional weighted score matter.')

# ---------- 3.1.1 named sites
rep("Valley Metro Rail's 2023 NTD profile [7] reports",
    "The Phoenix case is the 12th St & Washington/Jefferson Station (384 weekday boardings [8]); the Hong Kong case is the Siu Hong (兆康) stop, stop ID 100, 22.4120 N, 113.9783 E, served by seven routes [10]. Valley Metro Rail's 2023 NTD profile [7] reports")

# ---------- 5.6 new subsection before section 6
old = "# ---------------------------------------------------------------- section 6"
new = '''h2("5.6 Crosswind, Fan Limits and the Joint Operating Point")
para("Equation 2 is wind-neutral: v_amb appears in both AT_amb and AT_zone and cancels. To restore a wind dependence we follow the flight-effect correction of von Glahn [16], F(v) = 1 + 0.9·AR^(1/3)·(v/u_j)^(3/2), and normalise it at the design wind v_ref = 1.5 m/s so the baseline tables are unchanged: γ_eff(v) = 1 − (1−γ0)·F(v_ref)/F(v). AR is the outlet aspect ratio (1.25 for MC37V, 1.6 for MC61V, 1.0 for Portacool, 1.7 for the drum fan) and u_j = Q/A0.")
para("Table 10. Crosswind scenario: E with the flight-effect correction (Balanced weights, fixed normalisers).", 8.5, italic=True)
table(["v_amb (m/s)", "HK rail MC37V", "HK rail fan", "PHX rail MC61V", "PHX bus MC37V", "HK rail winner"], [
    ["1.5 (design)", "0.1005", "0.0744", "0.4026", "0.4743", "MC37V"],
    ["3.0", "0.0809", "0.0744", "0.3385", "0.3745", "MC37V (margin 0.007)"],
    ["5.0", "0.0650", "0.0744", "0.2592", "0.2932", "Fan"],
], widths=[2.6, 3.0, 2.8, 3.0, 2.8, 3.8], size=8)
para("At the design wind the baseline is recovered. At v = 3 m/s the Hong Kong platform margin falls from 0.026 to 0.007, and the fan overtakes at about 5 m/s; the Phoenix recommendations are unchanged. The CBE fans-and-heat map [18] places 32.5 °C / 78% in the fan-beneficial band and excludes conditions above 40 °C, so the zero fan credit in Eq. 6 is conservative at the Hong Kong design point and appropriate at Phoenix's 41 °C. A wind-corrected natural wet bulb (c_w = 0.15 K per m/s, following the natural-wet-bulb definition in [19]) raises the Hong Kong fan from 0.0744 to 0.0888 but leaves MC37V ahead (0.1084).")
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

# ---------------------------------------------------------------- section 6'''
rep(old, new)

# ---------- references 16-19
rep('    "Kyogoku, S., & Takebayashi, H. (2023). Experimental verification of mist cooling effect in front of air-conditioning condenser unit, open space, and bus stop. Atmosphere, 14(1), 177. https://doi.org/10.3390/atmos14010177",',
    '    "Kyogoku, S., & Takebayashi, H. (2023). Experimental verification of mist cooling effect in front of air-conditioning condenser unit, open space, and bus stop. Atmosphere, 14(1), 177. https://doi.org/10.3390/atmos14010177",\n'
    '    "von Glahn, U. H. (1989). Rectangular Nozzle Plume Velocity Modeling for Use in Jet Noise Prediction. NASA Technical Memorandum 102047 (AIAA-89-2357).",\n'
    '    "Deo, R. C., Nathan, G. J., & Mi, J. (2007). Comparison of turbulent jets issuing from rectangular nozzles with and without sidewalls. Experimental Thermal and Fluid Science, 32(2), 596–606. https://doi.org/10.1016/j.expthermflusci.2007.06.009",\n'
    '    "Tartarini, F., Schiavon, S., Cheung, T., & Hoyt, T. (2020). CBE Thermal Comfort Tool. SoftwareX, 12, 100563. https://doi.org/10.1016/j.softx.2020.100563; Fans & Heat page, https://comfort.cbe.berkeley.edu/fan_heatwaves, accessed 16 November 2026.",\n'
    '    "OSHA. Technical Manual, Section III, Chapter 4: Heat Hazards. https://www.osha.gov/otm/section-3-health-hazards/chapter-4, accessed 16 November 2026.",')

# ---------- appendix A source paragraph
rep('], widths=[3.8, 4.4, 1.3, 7.0], size=8)',
    '], widths=[3.8, 4.4, 1.3, 7.0], size=8)\n'
    'para("Source details: MC37V https://www.homedepot.com/p/Hessaire-3-100-CFM-3-Speed-Portable-Evaporative-Cooler-Swamp-Cooler-for-950-sq-ft-MC37V/304078772; MC61V https://hessaire.com/mobile-cooling/5300-cfm-mobile-cooler (price: https://www.sylvane.com/products/hessaire-mc61v-evaporative-air-cooler); Portacool catalog https://portacool.com/wp-content/uploads/2025/02/Portacool-Catalog_Jetstream_Industrial-Automotive-2023Reduced.pdf; Aqueduct Phoenix aqid 1628 / pfaf 772221 / string 772221-USA.3_1-1628 (33.44823 N, −112.075098), bws 2.482; Hong Kong sub-basins HKG.1_1 / HKG.10_1 / HKG.11_1, bws 0.179; Siu Hong stop coordinates from MTR route data and OpenStreetMap; Phoenix station profiles from the Valley Metro TOD PDF.", 8.5)')

# ---------- 5.5 structural limits: point to 5.6
rep("in Eq. 2 the ambient wind cancels algebraically, so v_amb does not change ΔT_eff and crosswind effects enter only through the γ sensitivity;",
    "Eq. 2 is wind-neutral, and Section 5.6 adds the flight-effect correction; the Hong Kong platform margin disappears above about 4 m/s;")

io.open(P, "w", encoding="utf-8").write(s)
print("v1.3 patched, length", len(s))
