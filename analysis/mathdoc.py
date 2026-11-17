# -*- coding: utf-8 -*-
"""Helpers to write OMML math into python-docx paragraphs."""
import copy
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import qn
import omml

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"


def _children(p, tag):
    return [ch for ch in p._p.iterchildren() if ch.tag.split("}")[-1] == tag]


def clear_para(p):
    for ch in list(p._p.iterchildren()):
        tag = ch.tag.split("}")[-1]
        if tag in ("r", "oMath", "oMathPara", "hyperlink"):
            p._p.remove(ch)


def base_rpr(p):
    for r in _children(p, "r"):
        rpr = r.find(qn("w:rPr"))
        if rpr is not None:
            rpr = copy.deepcopy(rpr)
            for tag in ("w:b", "w:i"):
                el = rpr.find(qn(tag))
                if el is not None:
                    rpr.remove(el)
            return rpr
    rpr = OxmlElement("w:rPr")
    rf = OxmlElement("w:rFonts")
    rf.set(qn("w:eastAsia"), "Microsoft YaHei")
    rpr.append(rf)
    return rpr


def add_text(p, text, bold=False, rpr=None):
    if not text:
        return
    r = OxmlElement("w:r")
    if rpr is not None:
        r.append(copy.deepcopy(rpr))
    if bold:
        rpr_el = r.find(qn("w:rPr"))
        if rpr_el is None:
            rpr_el = OxmlElement("w:rPr")
            r.insert(0, rpr_el)
        rpr_el.append(OxmlElement("w:b"))
    t = OxmlElement("w:t")
    t.set(XML_SPACE, "preserve")
    t.text = text
    r.append(t)
    p._p.append(r)


def add_math(p, latex, size=None):
    p._p.append(parse_xml(omml.omath(latex, size=size)))


def set_tabs(p, width_twips):
    pPr = p._p.get_or_add_pPr()
    for old in pPr.findall(qn("w:tabs")):
        pPr.remove(old)
    tabs = OxmlElement("w:tabs")
    for val, pos in (("center", width_twips // 2), ("right", width_twips)):
        tab = OxmlElement("w:tab")
        tab.set(qn("w:val"), val)
        tab.set(qn("w:pos"), str(pos))
        tabs.append(tab)
    pPr.append(tabs)
    jc = pPr.find(qn("w:jc"))
    if jc is None:
        jc = OxmlElement("w:jc")
        pPr.append(jc)
    jc.set(qn("w:val"), "left")


def add_tab(p):
    r = OxmlElement("w:r")
    r.append(OxmlElement("w:tab"))
    p._p.append(r)


def add_break(p):
    r = OxmlElement("w:r")
    r.append(OxmlElement("w:br"))
    p._p.append(r)


def tight(p, before=0, after=0):
    pf = p.paragraph_format
    pf.space_before = before
    pf.space_after = after
    pf.line_spacing = 1.0
    pf.keep_together = True


def relax_line(p, twips=200):
    """Allow a table-cell paragraph to grow with tall math (atLeast rule)."""
    pPr = p._p.get_or_add_pPr()
    sp = pPr.find(qn("w:spacing"))
    if sp is None:
        sp = OxmlElement("w:spacing")
        pPr.append(sp)
    sp.set(qn("w:line"), str(twips))
    sp.set(qn("w:lineRule"), "atLeast")


def tight_table(table, top=0, bottom=0, left=60, right=60):
    """Set explicit cell margins (twips) on a table."""
    tblPr = table._tbl.tblPr
    for old in tblPr.findall(qn("w:tblCellMar")):
        tblPr.remove(old)
    mar = OxmlElement("w:tblCellMar")
    for tag, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement("w:" + tag)
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    look = tblPr.find(qn("w:tblLook"))
    if look is not None:
        look.addprevious(mar)
    else:
        tblPr.append(mar)


def rebuild(p, parts, width=9978, display=False, size=None):
    """parts: (kind, ...) where kind in t/m/b/disp/br."""
    rpr = base_rpr(p)
    clear_para(p)
    if display:
        from docx.shared import Pt
        set_tabs(p, width)
        tight(p)
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(3)
    for part in parts:
        kind = part[0]
        if kind == "t":
            add_text(p, part[1], rpr=rpr)
        elif kind == "b":
            add_text(p, part[1], bold=True, rpr=rpr)
        elif kind == "m":
            add_math(p, part[1], size=size)
        elif kind == "disp":
            latex, label = part[1], part[2]
            add_tab(p)
            add_math(p, latex, size=size)
            if label:
                add_tab(p)
                add_text(p, label, rpr=rpr)
            add_break(p)
        elif kind == "br":
            add_break(p)
    # drop trailing break
    last = p._p[-1] if len(p._p) else None
    if last is not None and last.tag == qn("w:r") and last.find(qn("w:br")) is not None:
        p._p.remove(last)
