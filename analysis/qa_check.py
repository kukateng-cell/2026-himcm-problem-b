"""P4 QA: scan the integrated paper for stale numbers / forbidden claims."""

import re
from docx import Document

DOC = "2026_HiMCM_ProblemB_Full_Paper_v0.9.docx"
doc = Document(DOC)

texts = []
for p in doc.paragraphs:
    if p.text.strip():
        texts.append(p.text)
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            if cell.text.strip():
                texts.append(cell.text)
full = "\n".join(texts)

checks = [
    ("0.3011", "old Table 4 1-unit E"),
    ("0.3410", "old Table 4 2-unit E"),
    ("28.14", "old Phoenix fan WBGT"),
    ("0.1247", "old Phoenix electricity price"),
    ("0.850", "old HK BWS"),
    ("0.465", "old HK EF"),
    ("68%", "old universal RH crossover"),
    ("do not deploy evaporative cooling at all", "old blanket HK claim"),
    ("2× MC37V (recommended)", "old 2-unit recommendation"),
    ("Table 7", "non-existent table number"),
    ("Figure 7", "non-existent figure number"),
]
print("=== forbidden/stale string scan ===")
for needle, why in checks:
    hits = [m.start() for m in re.finditer(re.escape(needle), full, flags=re.I)]
    print("%-45s %2d hit(s)  [%s]" % (needle, len(hits), why))
    for pos in hits[:3]:
        print("    ...", full[max(0, pos - 70):pos + 80].replace("\n", " "), "...")

print("\n=== 2x MC37V occurrences (context) ===")
for m in re.finditer(r"2[×x] MC37V", full):
    print("  ...", full[max(0, m.start() - 90):m.start() + 90].replace("\n", " "), "...")

print("\n=== table/figure labels present ===")
for label in ["Table 1", "Table 2A", "Table 2B", "Table 3", "Table 3b", "Table 4", "Table 5", "Table 6", "Table 6b",
              "Figure 1", "Figure 2", "Figure 3", "Figure 4", "Figure 5", "Figure 6"]:
    print("  %-10s %s" % (label, "yes" if label in full else "MISSING"))

print("\n=== word count (rough) ===")
print("  characters:", len(full), " words:", len(full.split()))
print("\n=== headings ===")
for p in doc.paragraphs:
    if p.style.name.startswith("Heading") and p.text.strip():
        print("  %-10s %s" % (p.style.name, p.text[:90]))
