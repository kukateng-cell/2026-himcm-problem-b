"""Build the single all-in-one docx deliverable.

The consolidated English paper (with its placeholder pages) plus one internal
checklist page listing the items that are still unfilled.

Run: python analysis/build_single_file.py
"""

import os

import docx
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "2026_HiMCM_ProblemB_Full_Paper_v0.9.docx")
OUT = os.path.join(ROOT, "2026_HiMCM_ProblemB_Full_Paper_v0.9_AllInOne.docx")


def set_font(run, size=10, bold=False, italic=False, color=None):
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.italic = italic
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    if color:
        run.font.color.rgb = color


def main():
    doc = docx.Document(SRC)
    doc.add_page_break()

    h = doc.add_heading(level=1)
    r = h.add_run("Internal checklist — delete this page before submission")
    set_font(r, 15, True, color=RGBColor(0x1F, 0x3B, 0x57))

    para = doc.add_paragraph()
    r = para.add_run(
        "这份单档 = 完整英文论文（18 页：Summary、Section 1–6、Figure 1–6、Appendix A、References 1–14）"
        "＋ 1 页内部清单（下面）。清单外的正文已无占位页。"
    )
    set_font(r, 9.5)

    items = [
        ("队号", "封面仍是 Team [Team Number]；换成实际队号即可，其余（Summary、AI Report、Figures 1–6、页码、目录）均已完成。"),
        ("再改正文时", "重跑 analysis/build_full_paper.py → WPS 导出 PDF → 按新 PDF 核一次目录（当前 18 页版已对齐）。"),
        ("交付前", "python analysis/qa_check.py → 导出 PDF → 删除本页。"),
    ]
    for title, body in items:
        p = doc.add_paragraph(style="List Bullet")
        r = p.add_run(title + "：")
        set_font(r, 9.5, bold=True)
        r = p.add_run(body)
        set_font(r, 9.5)

    p = doc.add_paragraph()
    r = p.add_run(
        "模型口径 D1–D6 见 docs/model_decisions.md；数据与假设见 Appendix A 与 docs/data_provenance.md；"
        "评审记录见 docs/reviews/2026-11-15_T01_學生回饋.html。"
    )
    set_font(r, 8.5, italic=True)

    doc.save(OUT)
    print("saved", OUT)


if __name__ == "__main__":
    main()
