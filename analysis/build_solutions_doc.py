"""Build the Chinese solution memo for the five open items.

Run:
    "C:\\Users\\kukat\\AppData\\Local\\Programs\\Python\\Python312\\python.exe" analysis/build_solutions_doc.py
"""

import os

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "2026_HiMCM_ProblemB_五项遗留问题解决方案_2026-11-16.docx"

doc = Document()
sec = doc.sections[0]
sec.top_margin = Cm(2.0); sec.bottom_margin = Cm(2.0)
sec.left_margin = Cm(2.2); sec.right_margin = Cm(2.2)

style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(10.5)
style.element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")


def set_font(run, size=10.5, bold=False, color=None, italic=False):
    run.font.name = "Calibri"
    run.font.size = Pt(size)
    run.font.bold = bold
    run.italic = italic
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts"); rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), "Calibri")
    rFonts.set(qn("w:hAnsi"), "Calibri")
    rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    if color:
        run.font.color.rgb = color


def h1(text):
    p = doc.add_heading(level=1)
    r = p.add_run(text); set_font(r, 14, True, RGBColor(0x1F, 0x3B, 0x57))


def h2(text):
    p = doc.add_heading(level=2)
    r = p.add_run(text); set_font(r, 11.5, True, RGBColor(0x1F, 0x3B, 0x57))


def h3(text):
    p = doc.add_heading(level=3)
    r = p.add_run(text); set_font(r, 10.5, True)


def para(text, size=10.5, italic=False, bold=False, space=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space)
    p.paragraph_format.line_spacing = 1.15
    r = p.add_run(text); set_font(r, size, bold=bold, italic=italic)
    return p


def bullet(text, size=10.5):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text); set_font(r, size)


def table(headers, rows, widths=None, size=8.8):
    t = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    if widths:
        for i, w in enumerate(widths):
            t.columns[i].width = Cm(w)
    for j, htxt in enumerate(headers):
        cell = t.cell(0, j); cell.text = ""
        r = cell.paragraphs[0].add_run(htxt); set_font(r, size, bold=True)
    for i, row in enumerate(rows, start=1):
        for j, v in enumerate(row):
            cell = t.cell(i, j); cell.text = ""
            r = cell.paragraphs[0].add_run(str(v)); set_font(r, size)
    doc.add_paragraph()
    return t


# ---------------------------------------------------------------- cover
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("2026 HiMCM Problem B"); set_font(r, 14, True, RGBColor(0x66, 0x66, 0x66))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("五项遗留问题的具体解决方案"); set_font(r, 20, True, RGBColor(0x1F, 0x3B, 0x57))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("κ 标定 · 横风模型 · 风敏感安全指标 · 联合工况约束 · 数据可追溯性")
set_font(r, 12, False, RGBColor(0x33, 0x33, 0x33))
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Team 19362 · 2026-11-16 · v1（方案稿）")
set_font(r, 10.5, False, RGBColor(0x55, 0x55, 0x55))
doc.add_page_break()

# ---------------------------------------------------------------- update note
p = doc.add_paragraph()
r = p.add_run("更新（2026-11-16 晚）：κ 射流推导、NASA TM 102047 的 flight-effect 横风模型、CBE/OSHA 安全依据与联合水耗区间已并入论文 v1.3（新增 5.6 节与 [16]–[19] 引用）。本文件 2.4 的线性 β 情景保留为备选；正式论文采用 NASA 模型，v≈3.7 m/s 时香港站台风扇反超，Phoenix 推荐不变。")
set_font(r, 9.5, italic=True)
p.paragraph_format.space_after = Pt(8)

# ---------------------------------------------------------------- overview
h1("0. 总览")
para("这份文件把评审留下的五个问题逐条变成“可执行的方案”：每条给出模型/公式、需要的观测或网页资料、默认参数、对现有排名的影响、论文里怎么写、以及代码接口。所有计算都可在 analysis/structural_checks.py 中复现。")
table(["问题", "推荐方案", "需要的数据/工作", "对结论的影响", "工作量"], [
    ["κ 无标定", "自由射流推导 + 现场热线风速仪标定；按场地取 κ", "风速仪、1 天/场地", "κ=45 对应约 6.5 m 射流；公交亭应更高、站台更低", "1–2 天/场地"],
    ["横风被抵消", "γ(v)=γ0+β(v−v_ref)，并用 φ(v) 作备选", "风洞/CFD 或现场 3–4 个风速点", "改变绝对 E，不改变同场地排序", "1 天（现场另计）"],
    ["安全指标对风不敏感", "自然湿球风修正：T_nwb=T_wb−c_w(v−v_ref)", "c_w 由 ISO 7726/现场标定；已重算", "c_w≤0.15 时香港站台排序不变；反超需 c_w≈0.61", "0.5 天"],
    ["风量/温降/耗水不同工况", "区间约束 V_w^bal∈[0.8,1.2]V_w^man，反解 ε 或 Q", "厂家测试条件、现场水表", "排名不变，E 变化 <0.01", "0.5 天"],
    ["站点/产品/子流域不可追溯", "具名站点 + 产品 URL + Aqueduct ID 表", "网页核对、站台复测", "只增强可信度，不改模型", "0.5 天"],
], widths=[3.0, 5.0, 3.6, 4.2, 1.8])

# ---------------------------------------------------------------- 1 kappa
h1("1. κ：从射流理论到现场标定")
h2("1.1 问题")
para("正文把 v_eff 写成 v_amb + κ·Q_air/A_cov，κ=45，但只给了“literature-informed assumption”。评委问的是：为什么把风量除以覆盖面积、再乘 45，就能得到乘客处的风速？")

h2("1.2 射流理论推导（可直接写进 3.3）")
para("对一台 3,100 CFM 的 MC37V：Q = 3,100 × 1.699/3,600 = 1.463 m³/s；出风格栅按 0.75 m × 0.60 m 估，A0 ≈ 0.45 m²；出口风速 u0 = Q/A0 = 3.25 m/s；按覆盖面积 88 m² 计，面积平均通量 q = Q/A_cov = 0.0166 m/s。")
para("矩形自由射流的中心线速度近似 u(x) ≈ C·u0·√A0 / x，C≈2.4（x/√A0 > 3）。于是")
para("κ(x) = u(x)/q = C·A_cov / (x·√A0)。", bold=True)
para("代入本机：κ(x) ≈ 315 / x（x 以 m 计）。数值如下：")
table(["到出风口距离 x (m)", "中心线风速 u (m/s)", "等效 κ"], [
    ["2", "2.62", "157"], ["3", "1.74", "105"], ["4", "1.31", "79"],
    ["6", "0.87", "52"], ["8", "0.65", "39"], ["10", "0.52", "31"],
], widths=[4.6, 5.0, 4.0])
para("结论：κ=45 对应约 6.5–7 m 的射流距离；公交亭（设备到人 3–4 m）的 κ 应在 80–105，站台（6–8 m）在 39–52。当前全文共用一个 45，相当于假设两种场地的射流距离相同——这是比“45 从哪来”更值得写进论文的一点。")

h2("1.3 现场标定方案")
bullet("仪器：热线风速仪（0.05–10 m/s，±3%），三脚架 0.6 m（坐姿）与 1.1 m（站姿），温湿度记录仪同步记录。")
bullet("布点：距离 x = 1、2、3、5、8 m；每个距离横向 5 点（−0.5、−0.25、0、0.25、0.5 倍射流宽度）；每点 30 s 平均、3 次重复。")
bullet("计算：v_occ 取 1.1 m 高度、横向 5 点的平均；κ = v_occ·A_cov/Q；给出 95% 置信区间。")
bullet("验收：重复性 ±10%；与 1.2 的理论 κ(x) 对照；偏差 >30% 时检查格栅面积、风量档位和遮挡。")
bullet("样本量：5 距离 × 5 横向 × 2 高度 × 3 重复 = 150 个读数/设备/档位；公交亭与站台各做一台。")
bullet("限制：站台不能封场，选夜间或低客流；横风 >2 m/s 时记录并分层，避免把风的影响算进 κ。")

h2("1.4 论文写法")
para("3.3 加一段推导（Q、A0、u0、q、κ(x) 与上表）；3.1 加“κ 按场地取 80（亭）/45（台）”或保留 45 但给出 κ∈[39,105] 的区间。5.5 把“κ 未标定”改为“κ 由射流理论给出量级、待现场复核”。")

h2("1.5 代码接口")
para("analysis/structural_checks.py 的 kappa_from_jet() 已实现上表；建议在 recompute.py 增加 KAPPA_MODE = 'const' | 'geometry'，geometry 模式用 κ = C·A_cov/(x·√A0)，x 由场地几何给出（亭 3.5 m、台 6.5 m）。")

# ---------------------------------------------------------------- 2 crosswind
h1("2. 横风依赖模型")
h2("2.1 为什么现在风会抵消")
para("把式 2 展开（未触及饱和截断时）：ΔT_eff = 0.7806·(1−γ)·ΔT_phys + 0.70·κ·Q/A_cov。v_amb 在 AT_amb 与 AT_zone 中同号出现，代数上完全抵消。因此现在无论环境风多大，设备带来的体感降温增量都不变。")

h2("2.2 三种可实现的模型")
para("A（推荐）冷气逃逸随风增大：γ(v) = γ0 + β·(v − v_ref)，v_ref 取设计风速（1.5 m/s）。物理含义直接：横风把冷射流吹散，边界损失上升。")
para("B 覆盖被风稀释：φ(v) = φ0 / (1 + α·v)。适合“风把冷区吹偏”的情形，但会改变覆盖人数。")
para("C 联合：γ(v) 与 φ(v) 同时生效，用于风速 >3 m/s 的站台。")
para("推荐先用 A：参数少、可直接用现有 Eq. 2/3 重算，且不会改变覆盖人数口径。")

h2("2.3 标定方法")
para("固定设备、固定档位，在同一测点测 ΔT_eff 随横风 v 的变化（风洞 0–5 m/s，或现场用可移动风机阵列；有条件的用 k-ε CFD）。由")
para("β = −(dΔT_eff/dv) / (0.7806·ΔT_phys)", bold=True)
para("得到 β。文献量级 β≈0.02–0.06 (m/s)⁻¹；默认取 0.03 做情景，0.02/0.06 做上下界。")

h2("2.4 对排名的影响")
para("在 v=3 m/s、β=0.03 时，公交亭 γ 从 0.55 升到约 0.60、站台从 0.30 升到约 0.35；ΔT_eff 下降约 4–9%（站台约 4%、公交亭约 9%），E 下降约 0.01–0.02。Appendix B 已经给出 γ±0.10 的结果：香港站台 MC37V 0.0911、风扇 0.0744，排序不变。因此横风模型主要改变绝对值和“是否值得装”，不改变同场地内的设备顺序。")
para("如果希望横风改变排序，必须让风对“风扇”和“蒸发冷却”影响不同（例如风对射流覆盖 φ 的稀释只作用于有冷射流的设备），这属于 B 或 C 模型，需单独标定 α。")

h2("2.5 论文写法")
para("3.3 加 γ(v) 的式子与 β 的区间；5.6 新增“横风情景”小节与一张表（v=1.5/3/5，β=0.02/0.03/0.06，列出 4–8 个关键方案的 E），并明确“风不改变同场地排序”的结论。")

# ---------------------------------------------------------------- 3 wind safety
h1("3. 风敏感安全指标与重算排名")
h2("3.1 问题")
para("WBGT_proxy = 0.7·T_wb + 0.3·T_zone 不含风速：风扇只改变 v_eff、不改变 T 和 e，所以安全分对风扇完全无收益；蒸发冷却靠降温拿安全分。这是指标结构上的不对称。")

h2("3.2 方案：自然湿球的风修正")
para("自然湿球（natural wet bulb）本身随风变化；用 T_nwb = T_wb − c_w·(v − v_ref) 近似，c_w 取 0.05–0.15 K/(m/s)（可用 ISO 7726 的自然湿球法或现场标定）。于是")
para("WBGT_wind = 0.7·T_nwb + 0.3·T_zone。", bold=True)
para("风扇的 v_eff 高，T_nwb 被压低，终于在安全项上有收益；蒸发冷却仍有降温收益。")

h2("3.3 重算结果（已跑）")
para("用 analysis/structural_checks.py 的 score_wind() 重算，Balanced 权重、固定分母：")
table(["c_w [K/(m/s)]", "HK 站台 MC37V", "HK 站台 Fan", "PHX 站台 MC37V", "PHX 站台 MC61V"], [
    ["0（现模型）", "0.1005", "0.0744", "0.3808", "0.4026"],
    ["0.05", "0.1031", "0.0792", "0.3814", "0.4026"],
    ["0.10", "0.1058", "0.0840", "0.3820", "0.4026"],
    ["0.15", "0.1084", "0.0888", "0.3826", "0.4026"],
], widths=[3.6, 4.2, 3.6, 4.4, 4.4])
para("结论：在 c_w ≤ 0.15（合理上限）时，香港站台仍是 MC37V 领先，风扇从 0.0744 升到 0.0888、差距从 0.026 缩到 0.020；要让风扇反超，需要 c_w ≈ 0.61 K/(m/s)，远高于自然湿球的合理范围。因此“安全指标对风扇不友好”是真实的偏置，但没有推翻现排名。")

h2("3.4 如果用 AT-based safety")
para("AT = T + 0.33e − 0.70v − 4.00（正是 Eq. 2 的公式）。可以直接定义 S_AT = clamp((AT_hi − AT)/(AT_hi − AT_lo))，但 AT 的尺度与 WBGT 不同（同一 30 °C/50% 条件下 AT≈32.6、WBGT≈24.3），阈值必须重新标定；否则会人为放大或抹平安全项。建议把 AT-based 作为第二校验，而不是替换主指标：先按 3.2 的风修正 WBGT 报主结果，再用 AT 的 S 重算一次，若排序一致则写“两种风敏感指标给出相同排序”。")

h2("3.5 论文写法")
para("5.6 表 11 给出 c_w=0/0.05/0.10/0.15 的 E；正文一句话：“风修正使风扇的安全分上升、差距缩小约 25%，但反超阈值 c_w≈0.61 超出自然湿球的合理范围，故香港站台排序不变。” 5.5 的结构性限制相应改写。")

# ---------------------------------------------------------------- 4 joint
h1("4. 风量/温降/耗水的联合工况约束")
h2("4.1 现状")
para("能量平衡水耗与厂家补水率的比值（balance/manufacturer）：")
table(["城市/设备", "能量平衡 V_w (L/h)", "厂家 V_w (L/h)", "比值"], [
    ["Phoenix MC37V", "25.1", "10.6", "2.36"],
    ["Phoenix MC61V", "42.8", "18.2", "2.35"],
    ["Phoenix Portacool", "19.4", "11.4", "1.70"],
    ["Hong Kong MC37V", "6.6", "10.6", "0.62"],
    ["Hong Kong MC61V", "11.3", "18.2", "0.62"],
    ["Hong Kong Portacool", "5.1", "11.4", "0.45"],
], widths=[4.4, 4.6, 4.0, 3.0])
para("比值在 Phoenix 约 2.35、在香港约 0.62，说明“额定风量 + 11 °C 温降”与“厂家补水率”不是同一工况；不能把两组数独立拼接。")

h2("4.2 约束模型")
para("把耗水写成区间约束：V_w^bal(Q, ε, ΔT) ∈ [0.8, 1.2]·V_w^man，反解有效 ε_eff（或 Q_eff）。若解落在 [0.6,0.9] 之外，说明额定风量/温降至少有一个不成立，应改用区间而不是点值。")
para("也可以直接做区间成本：LCC 用 V_w 的上下界算两次，报告 E 的区间；这比强行选一个点更诚实。")

h2("4.3 对结论的影响")
para("把 V_w 固定为厂家值时，香港站台 MC37V 的 E 从 0.1005 降到 0.0914（仍高于风扇 0.0744，排序不变）；Phoenix 变化 <0.01。因此联合约束主要影响水费/环境项的绝对值，不改变现有推荐。")

h2("4.4 需要的数据")
bullet("厂家测试条件：进风温湿度、风量档位、补水率是“蒸发量”还是“补水量”。")
bullet("现场：水箱补水计量（流量计或称重），至少 2 h 稳定运行。")
bullet("若拿不到，就在 Appendix A 把 V_w 标为区间 [0.8,1.2]×厂家值，并把区间结果写进 5.6。")

# ---------------------------------------------------------------- 5 traceability
h1("5. 可追溯性：站点、产品与 Aqueduct")
h2("5.1 可直接粘贴的来源表")
table(["对象", "采用值", "状态", "来源 / URL / ID"], [
    ["Phoenix 站点", "12th St & Washington/Jefferson Station", "S", "Valley Metro TOD 2024：384 weekday boardings（208+176）；NTD ID 90209"],
    ["Phoenix 站台", "85.34 m × 4.98 m（中心站台）", "S", "Valley Metro Design Criteria (2020) Ch.6.3.2–6.3.3, p.136"],
    ["Phoenix 候车区", "120 m²（模型）", "A", "遮阴 boarding zone 假设；A_platform 425 m²"],
    ["香港站点", "Siu Hong（兆康）站，Stop ID 100（SHL）", "S", "22.4120 N, 113.9783 E；MTR Light Rail 68 站/11 线，兆康 7 线"],
    ["香港站台", "侧式站台约 32 m × 4 m ≈ 128 m²", "D", "Open3Dhk 2026-11 量测截图；需现场复测"],
    ["MC37V", "3,100 CFM / 950 ft² / $398 / 0.25 kW", "S/D", "https://www.homedepot.com/p/Hessaire-3-100-CFM-3-Speed-Portable-Evaporative-Cooler-Swamp-Cooler-for-950-sq-ft-MC37V/304078772"],
    ["MC61V", "5,300 CFM / 0.43 kW / $609", "S", "https://hessaire.com/mobile-cooling/5300-cfm-mobile-cooler；价格 https://www.sylvane.com/products/hessaire-mc61v-evaporative-air-cooler"],
    ["Portacool Jetstream 220", "2,400 CFM / 65 m² / $1,099", "S", "https://portacool.com/wp-content/uploads/2025/02/Portacool-Catalog_Jetstream_Industrial-Automotive-2023Reduced.pdf"],
    ["36\" drum fan", "10,500 CFM / 1/2 HP（0.37 kW）", "S", "Continental Dynamics WB246558：https://www.globalindustrial.com/p/36in-tilt-drum-fan-belt-drive"],
    ["Aqueduct Phoenix", "bws_raw 2.482；aqid 1628；pfaf 772221", "S", "WRI Aqueduct 4.0，33.44823 N, −112.075098；string_id 772221-USA.3_1-1628"],
    ["Aqueduct Hong Kong", "bws_raw 0.179；子流域 HKG.1_1 / HKG.10_1 / HKG.11_1", "S", "WRI Aqueduct 4.0 全球明细；https://www.wri.org/aqueduct"],
], widths=[3.2, 5.0, 1.4, 8.0], size=8.0)

h2("5.2 论文里怎么放")
para("3.1.1 用一句话点明两个具名站点与坐标；Table 2C 的 Basis 列加站名；Appendix A 的 Source 列加 URL/ID；References 增补产品页与 Aqueduct 版本。不要把长 URL 堆在正文，放 Appendix A 即可。")
para("drum fan 建议直接换成有来源的 Continental Dynamics 36\"（10,500 CFM、1/2 HP），把“hypothetical benchmark”改为“sourced product”，并在敏感性里保留 ±20% 风量。")

h2("5.3 仍缺的三项")
bullet("香港站台尺寸：Open3Dhk 只是量级佐证，需现场卷尺复测（长、宽、站台边缘到轨道距离）。")
bullet("drum fan 价格：Global Industrial 页面有报价，但需确认运费/库存。")
bullet("Aqueduct 版本与日期：正文写 Aqueduct 4.0 + 访问日期；HK 三个子流域要说明取哪一个或取平均。")

# ---------------------------------------------------------------- 6 plan
h1("6. 实施计划与验收")
table(["步骤", "改动", "验收标准"], [
    ["1. κ", "3.3 加推导；3.1/5.5 改 κ 口径；structural_checks.py 已实现", "κ(x) 表进论文；现场标定后 κ 误差 <20%"],
    ["2. 横风", "3.3 加 γ(v)；5.6 新增表；recompute 加 WIND_MODE", "v=1.5/3/5 三档 E 与排序表"],
    ["3. 安全", "5.6 表 11（c_w=0/0.05/0.10/0.15）；5.5 改写", "c_w*≈0.61 写进正文；排序结论明确"],
    ["4. 工况", "3.5 加区间约束；Appendix A 标 V_w 区间", "V_w 区间与 E 区间进附录"],
    ["5. 来源", "3.1.1/Table 2C/Appendix A/References 补站名、URL、ID", "每个关键数字有 URL/ID 或标 A"],
], widths=[3.0, 7.5, 7.5])

para("建议顺序：先做第 5 项（半天，纯资料）→ 第 3 项（半天，已有结果）→ 第 4 项（半天）→ 第 1、2 项（需要仪器/现场，1–2 天/场地）。")

h1("7. 需要你拍板的四个选择")
bullet("κ：全文保留 45（简单、但公交亭/站台同值），还是按场地取 80/45（更合理、但要多一段推导）？")
bullet("横风：只做 γ(v)（推荐），还是同时做 γ(v)+φ(v)（更完整、但需要 α 标定）？")
bullet("安全指标：主指标用“风修正 WBGT”，AT-based 作第二校验（推荐）；还是直接换 AT-based？")
bullet("站点：香港用 Siu Hong（兆康，客流最大、7 线）是否可以？Phoenix 用 12th St & Washington/Jefferson 是否可以？")

para("以上四项确认后，我可以按 5→3→4→1→2 的顺序改代码、重跑表格与图，并把结果写进论文 5.6 与附录。")

doc.save(OUT)
print("saved", OUT)
