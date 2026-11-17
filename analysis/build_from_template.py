import sys
from docx import Document
from docx.shared import Pt

TEMPLATE = r"C:\Users\kukat\Documents\xwechat_files\wxid_9ol1c92g384k22_a33c\msg\file\2026-11\2026_HiMCM_ProblemB_new(1).docx"
OUT = r"C:\Users\kukat\Desktop\USA\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx"

d = Document(TEMPLATE)


def set_para_text(p, text):
    """Replace paragraph text, keeping the first run's formatting."""
    runs = p.runs
    if not runs:
        r = p.add_run(text)
        return
    runs[0].text = text
    for r in runs[1:]:
        r._r.getparent().remove(r._r)


def replace_in_para(p, old, new):
    if old in p.text:
        set_para_text(p, p.text.replace(old, new))
        return True
    return False


done = {}

# 1. Summary: replace the limitations tail with the Data boundaries sentence
old_lim = ("Limitations: the drum fan is a hypothetical benchmark, several parameters remain assumptions, "
           "the heat index is an approximate WBGT proxy rather than a compliance measurement, and the ranking "
           "of near-ties is sensitive to the jet-mixing coefficient.")
new_lim = ("Data boundaries: both platforms use representative geometry; the drum fan is a hypothetical benchmark; "
           "κ has no field calibration; WBGT is a proxy, not a compliance measurement; and 31.7 °C/77% is a "
           "selected design hour, not the series maximum WBGT. Recommendations are conditional on these inputs, "
           "and the near-ties require a site pilot.")
for p in d.paragraphs:
    if old_lim in p.text:
        set_para_text(p, p.text.replace(old_lim, new_lim))
        done["summary"] = True
        break

# 2. §5.5 geometry sentence
old_geo = ("and no field measurement of ΔT_eff exists at either site; the Hong Kong geometry is a representative "
           "32 × 4 m side-platform measurement (Open3Dhk) applied to the Siu Hong stop, not a survey of that platform.")
new_geo = ("and no field measurement of ΔT_eff exists at either site; both platform geometries are representative: "
           "Phoenix uses design-criteria dimensions and an assumed waiting zone; Siu Hong uses a 32 × 4 m "
           "side-platform measurement (Open3Dhk), not a survey of that stop. Recommendations are conditional "
           "scenario results, not field-validated performance claims.")
for p in d.paragraphs:
    if old_geo in p.text:
        set_para_text(p, p.text.replace(old_geo, new_geo))
        done["geometry"] = True
        break

# 3. Memo caveat
old_memo = "the 33 °C proxy reference, and the model's κ, γ and water assumptions."
new_memo = ("the 33 °C proxy reference, and representative platform geometry and the model's uncalibrated "
            "κ, γ and water assumptions.")
for p in d.paragraphs:
    if old_memo in p.text:
        set_para_text(p, p.text.replace(old_memo, new_memo))
        done["memo"] = True
        break

# 4. Appendix A rows
rows = {
    "Hong Kong T_db / RH": "ERA5 hot-humid design hour (2026-07-12 18:00 local); selected design hour, not the series maximum WBGT; the listed maximum-WBGT hour has dry-bulb/RH 35.6 °C/60.2% (2026-08-08 15:00 local)",
    "Wet bulb": "Psychrometric estimate at 950/1,000 hPa; derived WBGT is a proxy",
    "A_platform": "Representative geometry: Valley Metro design criteria; side-platform measurement applied to Siu Hong; neither a site survey",
    "A_waiting": "Phoenix assumed shaded zone; HK representative platform area",
    "κ (dimensionless)": "Assumed 45; sensitivity 30–60 and bus 80–105; no field calibration",
}
for t in d.tables:
    hdr = " ".join(c.text.strip() for c in t.rows[0].cells)
    if hdr.startswith("Parameter") and "Value" in hdr:
        for row in t.rows[1:]:
            key = " ".join(row.cells[0].text.split())
            if key in rows:
                cell = row.cells[3]
                if cell.paragraphs and cell.paragraphs[0].runs:
                    cell.paragraphs[0].runs[0].text = rows[key]
                    for r in cell.paragraphs[0].runs[1:]:
                        r._r.getparent().remove(r._r)
                else:
                    cell.text = rows[key]
                done.setdefault("appendix", []).append(key)
        break

# 5. Compact tables so the page count stays within 25
for t in d.tables:
    for ri, row in enumerate(t.rows):
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                for r in p.runs:
                    r.font.size = Pt(8)
                    if ri == 0:
                        r.bold = True

d.save(OUT)
print("saved", OUT)
print("applied:", done)
