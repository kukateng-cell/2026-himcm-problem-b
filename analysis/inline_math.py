# -*- coding: utf-8 -*-
"""Convert inline formulas embedded in prose to OMML, leaving surrounding text intact."""
import re, sys
from docx import Document
from docx.oxml import parse_xml, OxmlElement

TOKEN = re.compile(r"([^\s_()]+)_([A-Za-z0-9]+(?:,[A-Za-z0-9]+)*)")

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def r(text):
    return '<m:r><m:t xml:space="preserve">%s</m:t></m:r>' % esc(text)

def sub(base, s):
    return '<m:sSub><m:e>%s</m:e><m:sub>%s</m:sub></m:sSub>' % (r(base), r(s))

def sup(base, s):
    return '<m:sSup><m:e>%s</m:e><m:sup>%s</m:sup></m:sSup>' % (r(base), r(s))

def tokens(text):
    out, pos = [], 0
    for m in TOKEN.finditer(text):
        if m.start() > pos:
            out.append(("r", text[pos:m.start()]))
        out.append(("sub", m.group(1), m.group(2)))
        pos = m.end()
    if pos < len(text):
        out.append(("r", text[pos:]))
    return out

def omath(toks):
    body = []
    for t in toks:
        if t[0] == "r":
            body.append(r(t[1]))
        elif t[0] == "sub":
            body.append(sub(t[1], t[2]))
        elif t[0] == "sup":
            body.append(sup(t[1], t[2]))
    return ('<m:oMath xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">%s</m:oMath>'
            % "".join(body))

def wrun(text):
    el = OxmlElement("w:r")
    t = OxmlElement("w:t")
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    el.append(t)
    return el

def rebuild(p, segments):
    for ch in list(p._p):
        if ch.tag.split("}")[-1] in ("r", "oMath", "hyperlink"):
            p._p.remove(ch)
    for kind, payload in segments:
        if kind == "t":
            p._p.append(wrun(payload))
        else:
            p._p.append(parse_xml(omath(payload)))

def split_segments(text, spans):
    """spans: list of (substring, tokens)."""
    segs, rest = [], text
    for s, toks in spans:
        i = rest.find(s)
        if i < 0:
            raise SystemExit("span not found: " + s[:50])
        if i:
            segs.append(("t", rest[:i]))
        segs.append(("m", toks))
        rest = rest[i + len(s):]
    if rest:
        segs.append(("t", rest))
    return segs

SPECS = []

def add(prefix, spans):
    SPECS.append((prefix, spans))

add("T_wb is solved from the psychrometric relation", [
    ("p_s", tokens("p_s")),
    ("e_s(T_wb) − γ_p(T_db − T_wb) = e_amb,", tokens("e_s(T_wb) − γ_p(T_db − T_wb) = e_amb,")),
    ("γ_p = 1.006 p_s /(0.622 × 2,450)", tokens("γ_p = 1.006 p_s /(0.622 × 2,450)")),
    ("ε = 0", tokens("ε = 0")),
    ("ΔT_phys = 0.", tokens("ΔT_phys = 0.")),
])

add("Two changes from a conventional weighted score", [
    ("S_safe = φ·S_safe(W_zone) + (1−φ)·S_safe(W_ambient),",
     tokens("S_safe = φ·S_safe(W_zone) + (1−φ)·S_safe(W_ambient),")),
])

add("Q2b revises the Q2a model", [
    ("φ = min(1, n·A_cov/A_waiting)", tokens("φ = min(1, n·A_cov/A_waiting)")),
    ("φ = 1", tokens("φ = 1")),
    ("B_max, LCC_max, E_CO2,max, W_eq,max", tokens("B_max, LCC_max, E_CO2,max, W_eq,max")),
    ("S_safe = φ·S(W_zone) + (1−φ)·S(W_ambient)", tokens("S_safe = φ·S(W_zone) + (1−φ)·S(W_ambient)")),
])

add("Equation 2 is wind-neutral", [
    ("v_amb", tokens("v_amb")),
    ("AT_amb", tokens("AT_amb")),
    ("AT_zone", tokens("AT_zone")),
    ("F(v) = 1 + 0.9·AR^(1/3)·(v/u_j)^(3/2)",
     [("r", "F(v) = 1 + 0.9·"), ("sup", "AR", "(1/3)"), ("r", "·"), ("sup", "(v/u_j)", "(3/2)")]),
    ("γ_eff(v) = 1 − (1−γ0)·F(v_ref)/F(v)", tokens("γ_eff(v) = 1 − (1−γ0)·F(v_ref)/F(v)")),
    ("v = v_ref", tokens("v = v_ref")),
    ("u_j = Q/A0", tokens("u_j = Q/A0")),
])

path = sys.argv[1]
doc = Document(path)
n = 0
for p in list(doc.paragraphs):
    for prefix, spans in SPECS:
        if p.text.startswith(prefix):
            rebuild(p, split_segments(p.text, spans))
            n += 1
            break
doc.save(path)
print("inline paragraphs converted", n)
