# Submission snapshot — v1.1 (2026-11-16)

This folder is the **shareable snapshot** of the integrated English paper. The root files remain the source of truth.

## Files

- `2026_HiMCM_ProblemB_Full_Paper_v1.1.docx` — editable master (18 pages)
- `2026_HiMCM_ProblemB_Full_Paper_v1.1.pdf` — PDF view (18 pages)
- `2026_HiMCM_ProblemB_Full_Paper_v1.1_AllInOne.docx` — paper + internal checklist page (19 pages; delete the checklist page before submission)

## What changed from v0.9

The model was rebuilt after the review: platform and waiting-zone areas are separated; cooling water is derived from the adiabatic mass balance; a do-nothing baseline is scored with the same normalisers; safety is a graded, population-weighted WBGT proxy; kappa is dimensionless; per-venue normalisation replaces Set A/Set B; hourly ERA5 scenarios, 1,000-draw joint uncertainty, installation/labour adders and a 30% jet-overlap scenario were added in Sections 5.1–5.3.

The 2026-11-16 revision adds: a one-paragraph Q2b model-revision statement (what changed / why / how the answer changed); a Q3 paragraph ranking coverage, climate and power as efficiency drivers; a 5.4 plausibility-check table; Appendix B with the full single-factor sensitivity table; Figure 1 redrawn (Eq. 4 and Eq. 5 as parallel inputs to Eq. 6; φ = min(1, n·A_cov/A_waiting)); Figure 3 redrawn as two design-day panels (41 °C and 32.5 °C); Figure 4 with an inset that separates the two fan points; Figure 6 with a platform note; bracketed citations [1]–[15] throughout; and the team number on the cover.

## Status

- Text complete at 18 pages (<= 25-page limit); footer carries page numbers and the TOC matches this PDF.
- `analysis/qa_check.py` reports no superseded values; the two 0.850 / 0.465 hits and the 68% hits are intentional Appendix B sensitivity values and Monte-Carlo probabilities.
- Team number: **19362**.

## Reproduce

```bash
python analysis/recompute.py          # model, tables 3-6
python analysis/build_full_paper.py   # docx
python analysis/make_figures.py       # figures 2-6 (needs matplotlib)
python analysis/make_fig1.py          # figure 1 (needs matplotlib)
python analysis/qa_check.py           # stale-value scan
```
