# -*- coding: utf-8 -*-
"""Stage 3: update prose numbers for Summary and Sections 4.1-4.3 to the v2 model."""
import json
from docx import Document

PATH = r"C:\Users\kukat\Desktop\USA\_extract\v1.3_work.docx"
DATA = r"C:\Users\kukat\Desktop\USA\_extract\v2_numbers.json"
with open(DATA, encoding="utf-8") as f:
    D = json.load(f)

doc = Document(PATH)

REPL = [
 # Summary
 ("5.8 times more efficient than the 2.5 kW cooler (η = 53.52 vs 9.20)",
  "6.4 times more efficient than the 2.5 kW cooler (η = 72.0 vs 11.3)"),
 ("1× MC61V scores E = 0.4026 and covers the waiting zone, while 2× MC37V scores 0.3635 at twice the capital cost",
  "1× MC61V scores E = 0.4034 and covers the waiting zone, while 2× MC37V scores 0.3642 at twice the capital cost"),
 ("(2× Portacool 0.2834 vs 1× 0.3042)", "(2× Portacool 0.2114 vs 1× 0.3046)"),
 ("(E = 0.3541 vs 0.3278 for MC37V)", "(E = 0.3967 vs 0.3457 for MC37V)"),
 ("MC37V (0.2858) is essentially tied with doing nothing (0.2865) and only slightly ahead of MC61V (0.2716) and the fan (0.2684)",
  "MC37V (0.2860) is essentially tied with doing nothing (0.2865) and only slightly ahead of MC61V (0.2719) and the fan (0.2685)"),
 ("the Hong Kong platform is already a hair below it (0.2858 vs 0.2865)",
  "the Hong Kong platform is already a hair below it (0.2860 vs 0.2865)"),
 ("(0.4015 vs 0.4026; $243.80 vs $397.41)", "(0.4020 vs 0.4034; $243.80 vs $397.41)"),
 # Section 4.1
 ("(η = 53.52 persons·°C/kW, E = 0.3992)", "(η = 72.0 persons·°C/kW, E = 0.4317)"),
 ("System B has E = 0.2224 and System C E = 0.0434; the A/C efficiency ratio is 5.8×",
  "System B has E = 0.2531 and System C E = 0.0724; the A/C efficiency ratio is 6.4×"),
 ("it is below System A but above System B (0.2224) and System C (0.0434)",
  "it is below System A but above System B (0.2531) and System C (0.0724)"),
 ("the 0.25 kW MC37V ahead of the drum fan at this shelter (E = 0.4806 vs 0.3705)",
  "the 0.25 kW MC37V ahead of the drum fan at this shelter (E = 0.4794 vs 0.4131)"),
 # Section 4.2
 ("One MC61V covers the whole 120 m² waiting zone (φ = 1.000) and scores E = 0.4026; two MC37V also reach full coverage but cost about twice as much and score 0.3635. Under this base two units are uniformly worse: 2× MC37V scores 0.3635 against 0.4015 for one; 2× Portacool 0.2834 against 0.3042; 2× MC61V 0.2060 against 0.4026.",
  "One MC61V covers the whole 120 m² waiting zone (φ = 1.000) and scores E = 0.4034; two MC37V also reach full coverage but cost about twice as much and score 0.3642. Under this base two units are uniformly worse: 2× MC37V scores 0.3642 against 0.4020 for one; 2× Portacool 0.2114 against 0.3046; 2× MC61V 0.2068 against 0.4034."),
 ("1× MC37V (0.2858) is only marginally ahead of 1× MC61V (0.2716) and the fan (0.2684), and all three are at or below the do-nothing baseline (0.2865)",
  "1× MC37V (0.2860) is only marginally ahead of 1× MC61V (0.2719) and the fan (0.2685), and all three are at or below the do-nothing baseline (0.2865)"),
 ("Two fans score 0.2339", "Two fans score 0.2170"),
 ("while two MC37V cover it at higher cost (LCC $487.60 vs $397.41, E = 0.3635)",
  "while two MC37V cover it at higher cost (LCC $487.60 vs $397.41, E = 0.3642)"),
 ("(2× Portacool 0.2834 vs 1× 0.3042)", "(2× Portacool 0.2114 vs 1× 0.3046)"),
 # Section 4.3
 ("MC37V in bus shelters (E = 0.4806) and MC61V on platforms (0.4026)",
  "MC37V in bus shelters (E = 0.4794) and MC61V on platforms (0.4034)"),
 ("the drum fan (0.3541 vs 0.3278), while the platform is essentially tied with doing nothing and only marginally ahead of MC61V (0.2858 vs 0.2716)",
  "the drum fan (0.3967 vs 0.3457), while the platform is essentially tied with doing nothing and only marginally ahead of MC61V (0.2860 vs 0.2719)"),
 ("the 45-person platform has a 7.5× larger η than the 6-person shelter",
  "the 45-person platform has a 7.4× larger η than the 6-person shelter"),
 ("cuts η from 862 to 115 persons·°C/kW", "cuts η from 862 to 116 persons·°C/kW"),
 ("raises ΔT_eff only 1.7-fold, so η falls 5.8-fold", "raises ΔT_eff only 1.6-fold, so η falls 6.4-fold"),
]

def repl_para(p, old, new):
    if old not in p.text:
        return False
    if len(p.runs) == 0:
        return False
    text = p.text.replace(old, new)
    for r in p.runs[1:]:
        r._r.getparent().remove(r._r)
    p.runs[0].text = text
    return True

hits = {old: 0 for old, _ in REPL}
for p in doc.paragraphs:
    for old, new in REPL:
        if old in p.text:
            if repl_para(p, old, new):
                hits[old] += 1

missing = [o for o, c in hits.items() if c == 0]
print("applied", sum(hits.values()), "of", len(REPL))
for o, c in hits.items():
    if c != 1:
        print("COUNT", c, "::", o[:90])

doc.save(PATH)
print("saved")
