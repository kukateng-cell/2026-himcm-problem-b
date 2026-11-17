# -*- coding: utf-8 -*-
"""Split the very long single-paragraph blocks into readable paragraphs."""
import copy, sys
from docx import Document
from docx.oxml import OxmlElement

PATH = r"C:\Users\kukat\Desktop\USA\_extract\v1.3_work.docx"

SPLITS = {
    "Limitations: the drum fan is a hypothetical benchmark": [
        "Structural limits remain:",
        "κ is a lumped, uncalibrated coefficient",
        "The water rate also mixes",
        "Closing these gaps would require",
    ],
    "Sensitivity runs hold the per-venue normalisers fixed": [
        "The paper's own geometric estimate",
        "A_cov is the exception:",
    ],
    "Table 7 repeats the comparison for nine local-time snapshots": [
        "In Hong Kong the choice is time-dependent",
        "A weather-switching strategy",
    ],
}

def split_para(p, markers):
    text = p.text
    pos = [text.find(m) for m in markers]
    if any(i <= 0 for i in pos) or pos != sorted(pos):
        return 0
    bounds = [0] + pos + [len(text)]
    segs = [text[bounds[i]:bounds[i + 1]].strip() for i in range(len(bounds) - 1)]
    pPr = p._p.pPr
    rPr = p.runs[0]._r.rPr if (p.runs and p.runs[0]._r.rPr is not None) else None
    # first segment into the original paragraph
    for ch in list(p._p):
        if ch.tag.split('}')[-1] in ("r", "oMath", "hyperlink"):
            p._p.remove(ch)
    run = OxmlElement('w:r')
    if rPr is not None:
        run.append(copy.deepcopy(rPr))
    t = OxmlElement('w:t')
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = segs[0]
    run.append(t)
    p._p.append(run)
    # remaining segments as new paragraphs
    ref = p._p
    for seg in segs[1:]:
        newp = OxmlElement('w:p')
        if pPr is not None:
            newp.append(copy.deepcopy(pPr))
        run = OxmlElement('w:r')
        if rPr is not None:
            run.append(copy.deepcopy(rPr))
        t = OxmlElement('w:t')
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        t.text = seg
        run.append(t)
        newp.append(run)
        ref.addnext(newp)
        ref = newp
    return len(segs)

doc = Document(PATH)
count = 0
for p in list(doc.paragraphs):
    for prefix, markers in SPLITS.items():
        if p.text.startswith(prefix):
            count += split_para(p, markers)
            break
doc.save(PATH)
print("paragraph pieces produced:", count)
