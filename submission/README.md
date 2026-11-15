# Submission snapshot — v0.9 (2026-11-15)

This folder is the **shareable snapshot** of the integrated English paper. It is a copy of the working files in the repository root; the root files remain the source of truth.

## Files

- `2026_HiMCM_ProblemB_Full_Paper_v0.9.docx` — editable master (18 pages)
- `2026_HiMCM_ProblemB_Full_Paper_v0.9.pdf` — PDF view (18 pages)

## Status

- P0–P2 integrated; P4 QA passed; T01 review round applied; Figures 1–6 generated and embedded; Summary (p.2) and AI Use Report (p.17) written.
- **Text complete at 18 pages** (≤ 25-page limit); footer carries page numbers and the TOC matches this PDF.
- Only remaining item: fill the team number on the cover (`Team [Team Number]`).

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
