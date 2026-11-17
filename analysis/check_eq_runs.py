from docx import Document
doc = Document(r"C:\Users\kukat\Desktop\USA\2026_HiMCM_ProblemB_Full_Paper_v1.2.docx")
targets = ["ΔT_phys = min", "ΔT_eff = AT", "η = (φ", "LCC_annual =", "V_w = 3600", "I_env = α_c", "E = w1"]
for p in doc.paragraphs:
    t = p.text
    if any(t.strip().startswith(x) for x in targets):
        print("PARA:", t[:90])
        for r in p.runs:
            print("   run:", repr(r.text), "sub=", r.font.subscript, "sup=", r.font.superscript, "italic=", r.italic)
        print()
