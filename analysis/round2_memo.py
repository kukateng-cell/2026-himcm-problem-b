# -*- coding: utf-8 -*-
"""Round 2: update Table 6c and the memo / full-cost prose to v2 values."""
from docx import Document

PATH = r"C:\Users\kukat\Desktop\USA\_extract\v1.3_work.docx"
doc = Document(PATH)

def set_cell(cell, text):
    p = cell.paragraphs[0]
    for r in p.runs[1:]:
        r._r.getparent().remove(r._r)
    if p.runs:
        p.runs[0].text = text
    else:
        p.add_run(text)

# ---- Table 6c (index 17)
rows = [
    ("1.00", "397.41", "0.4034", "637.41", "0.3430", "0.3000"),
    ("1.00", "243.80", "0.4794", "438.80", "0.4303", "0.3000"),
    ("1.00", "131.90", "0.3967", "326.90", "0.3476", "0.2865"),
    ("0.69", "177.05", "0.2860", "417.05", "0.2256", "0.2865"),
]
for row, vals in zip(doc.tables[17].rows[1:], rows):
    for j, v in enumerate(vals, start=3):
        set_cell(row.cells[j], v)

REPL = [
 ("leaves E at 0.4015 (MC37V) and 0.4026 (MC61V)",
  "leaves E at 0.4020 (MC37V) and 0.4034 (MC61V)"),
 ("one MC61V covers the zone (φ = 1.000, E = 0.4026)",
  "one MC61V covers the zone (φ = 1.000, E = 0.4034)"),
 ("The Phoenix platform is a near-tie (MC61V 0.4026 vs MC37V 0.4015)",
  "The Phoenix platform is a near-tie (MC61V 0.4034 vs MC37V 0.4020)"),
 ("E = 0.4026, against a do-nothing baseline of 0.3000. Otherwise 1× MC37V is the cost-default at E = 0.4015 and $243.80; the two differ by only 0.0011. Do not deploy 2× MC61V: it doubles cost without improving coverage (E = 0.2060).",
  "E = 0.4034, against a do-nothing baseline of 0.3000. Otherwise 1× MC37V is the cost-default at E = 0.4020 and $243.80; the two differ by only 0.0014. Do not deploy 2× MC61V: it doubles cost without improving coverage (E = 0.2068)."),
 ("1× MC37V E = 0.2858 vs do-nothing 0.2865. The paper's installation ($900 over 10 years) and labour ($150/yr) add $240/yr, lowering E to 0.2255",
  "1× MC37V E = 0.2860 vs do-nothing 0.2865. The paper's installation ($900 over 10 years) and labour ($150/yr) add $240/yr, lowering E to 0.2256"),
 ("The Hong Kong platform is already below the do-nothing baseline (0.2858 vs 0.2865) and falls to 0.2255 at full cost.",
  "The Hong Kong platform is already below the do-nothing baseline (0.2860 vs 0.2865) and falls to 0.2256 at full cost."),
 ("(Phoenix MC37V 0.4315, Hong Kong fan 0.3050), and the Phoenix platform remains MC61V (0.3422), but the Hong Kong platform falls further: MC37V goes from 0.2858 to 0.2255",
  "(Phoenix MC37V 0.4303, Hong Kong fan 0.3476), and the Phoenix platform remains MC61V (0.3430), but the Hong Kong platform falls further: MC37V goes from 0.2860 to 0.2256"),
 ("the Hong Kong platform is a hair below doing nothing (0.2858 vs 0.2865) and the bus fan is a clear positive (0.3541 vs 0.2865)",
  "the Hong Kong platform is a hair below doing nothing (0.2860 vs 0.2865) and the bus fan is a clear positive (0.3967 vs 0.2865)"),
 ("changes the Hong Kong platform MC37V score from 0.2858 to 0.2845",
  "changes the Hong Kong platform MC37V score from 0.2860 to 0.2847"),
 ("On the Hong Kong rail platform the evaporative unit is only marginally ahead of the fan (E 0.2858 vs 0.2684), both are below doing nothing (0.2865), and once installation and labour are counted the evaporative unit falls to 0.2255.",
  "On the Hong Kong rail platform the evaporative unit is only marginally ahead of the fan (E 0.2860 vs 0.2685), both are below doing nothing (0.2865), and once installation and labour are counted the evaporative unit falls to 0.2256."),
 ("one MC37V ($177.05, E 0.2858) only marginally beats one fan ($131.90, E 0.2684), both sit below doing nothing (0.2865), and two fans (E 0.2339) lose to one MC37V",
  "one MC37V ($177.05, E 0.2860) only marginally beats one fan ($131.90, E 0.2685), both sit below doing nothing (0.2865), and two fans (E 0.2170) lose to one MC37V"),
]

def repl_para(p, old, new):
    if old not in p.text or not p.runs:
        return False
    text = p.text.replace(old, new)
    for r in p.runs[1:]:
        r._r.getparent().remove(r._r)
    p.runs[0].text = text
    return True

counts = [0] * len(REPL)
for p in doc.paragraphs:
    for i, (old, new) in enumerate(REPL):
        if old in p.text and repl_para(p, old, new):
            counts[i] += 1
for i, c in enumerate(counts):
    if c != 1:
        print("COUNT", c, "::", REPL[i][0][:80])

doc.save(PATH)
print("saved; replacements", sum(counts), "/", len(REPL))
for row in doc.tables[17].rows:
    print(" | ".join(c.text for c in row.cells))
