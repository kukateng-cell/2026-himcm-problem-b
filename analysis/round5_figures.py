# -*- coding: utf-8 -*-
"""Round 5: swap Figures 2-6 with the v2 regenerated PNGs and update Figure 3 text."""
import io
from docx import Document
from docx.oxml.ns import qn

PATH = r"C:\Users\kukat\Desktop\USA\_extract\v1.3_work.docx"
FIGS = [
    r"C:\Users\kukat\Desktop\USA\docs\figures\fig1_system.png",
    r"C:\Users\kukat\Desktop\USA\docs\figures\fig2_q2a_q2b.png",
    r"C:\Users\kukat\Desktop\USA\docs\figures\fig3_rh_crossover.png",
    r"C:\Users\kukat\Desktop\USA\docs\figures\fig4_pareto.png",
    r"C:\Users\kukat\Desktop\USA\docs\figures\fig5_gamma_heatmap.png",
    r"C:\Users\kukat\Desktop\USA\docs\figures\fig6_infographic.png",
]
doc = Document(PATH)
shapes = doc.inline_shapes
print("inline shapes:", len(shapes))
for i, shape in enumerate(shapes):
    blip = shape._inline.graphic.graphicData.pic.blipFill.blip
    rId = blip.get(qn("r:embed"))
    part = doc.part.related_parts[rId]
    part._blob = io.open(FIGS[i], "rb").read()
print("images replaced")

REPL = [
 ("at 41 °C the rail crossover is 79.7%, while at Hong Kong's own 31.7 °C the rail crossover falls to 76.4%, so 77% is above it and the fan delivers slightly more felt cooling; at the bus shelter the crossover is 64.7%, well below 77%.",
  "at 41 °C the rail crossover is 79.7%, while at Hong Kong's own 31.7 °C the rail crossover falls to 76.4%, so 77% is above it and the fan delivers slightly more felt cooling; at the bus shelter the crossover is 61.7% in Phoenix and 55.6% in Hong Kong, well below 77%."),
 ("(a) Phoenix 41 °C: bus crossover 69.6%, rail 79.7%. (b) Hong Kong 31.7 °C: bus 64.7%, rail 76.4%. Dotted lines mark the design-day RH (18% and 77%); the fan line is 2.081 °C.",
  "(a) Phoenix 41 °C: bus crossover 61.7%, rail 79.7%. (b) Hong Kong 31.7 °C: bus 55.6%, rail 76.4%. Dotted lines mark the design-day RH (18% and 77%); the fan line is 3.00 °C."),
]

def repl_para(p, old, new):
    if old not in p.text or not p.runs:
        return False
    text = p.text.replace(old, new)
    for r in p.runs[1:]:
        r._r.getparent().remove(r._r)
    p.runs[0].text = text
    return True

cnt = 0
for p in doc.paragraphs:
    for old, new in REPL:
        if old in p.text and repl_para(p, old, new):
            cnt += 1
print("figure 3 text replacements:", cnt)
doc.save(PATH)
