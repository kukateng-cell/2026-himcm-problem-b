# Submission snapshot — v0.9 (2026-11-15)

This folder is the **shareable snapshot** of the integrated English paper. It is a copy of the working files in the repository root; the root files remain the source of truth.

## Files

- `2026_HiMCM_ProblemB_Full_Paper_v0.9.docx` — editable master (15 pages)
- `2026_HiMCM_ProblemB_Full_Paper_v0.9.pdf` — PDF view (15 pages)

## Status

- P0–P2 integrated; P4 QA passed for this v0.9 build.
- **Not submission-ready yet.** Four pages are titled placeholders:
  - p.2 Summary Sheet
  - p.4 Section 1 (Q1 — open freezer case)
  - p.13 AI Use Report
  - p.14 Figures 1–6
- 15 pages now; expected 20–22 pages after the placeholders are filled (≤ 25-page limit).

## QA

See [`../docs/p4_qa_report.md`](../docs/p4_qa_report.md). The automated scan found zero occurrences of the old numbers (`0.3011`, `0.3410`, `28.14`, `0.1247`, `0.850`, `0.465`, `68%`) and zero occurrences of the old blanket claim.

## After filling the placeholders

```bash
python analysis/qa_check.py          # re-scan
python analysis/build_full_paper.py  # regenerate the docx (then re-export PDF)
```

Update the Table of Contents page numbers after the final layout, then replace both files in this folder and tag the next release.

## Source of truth

- Numbers: [`../docs/tables_v2.md`](../docs/tables_v2.md)
- Data/assumptions: [`../docs/data_provenance.md`](../docs/data_provenance.md)
- Chinese reference: [`../paper_v2/Revision_Pack_P0-P2_Bilingual.docx`](../paper_v2/Revision_Pack_P0-P2_Bilingual.docx)
