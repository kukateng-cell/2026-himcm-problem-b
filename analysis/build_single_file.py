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
        "这份单档 = 英文全文（Section 1–6、Table 1–6c、Figure 1–6、Appendix A、References 1–14）"
        "＋ 尚未填写的部分（下面清单）。占位页仍保留在正文原位，写作要点也在原位。"
    )
    set_font(r, 9.5)

    items = [
        ("Summary Sheet（第 2 页）", "350–450 词：问题、六式模型、3–4 个关键数字（Phoenix 1×MC61V 0.4093；2×MC37V 0.3708；HK 1×MC37V 0.2837 vs 风扇 0.2733）、建议、限制。"),
        ("AI Use Report（第 17 页）", "工具/模型/版本/日期/用途/2–3 个样例提示/人工核验方式；未用 AI 就明确写“no AI tools”。"),
        ("封面", "“Team [Team Number]”换成实际队号；删除 “Master draft v0.9 …” 两行草稿标记。"),
        ("页脚", "目前没有页码；补页码后按新 PDF 重排目录（当前 18 页：1→4、2→5、3→6、3.2→7、4→9、4.3→10、4.4→11、5→13、6→15、AI→17、App A→18）。"),
        ("交付前", "python analysis/qa_check.py → python analysis/build_full_paper.py → 导出 PDF → 删除本页。"),
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
