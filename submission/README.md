# Submission snapshot — v1.0 (model rebuilt, 2026-11-15)

This folder is the **shareable snapshot** of the integrated English paper. The root files remain the source of truth.

## Files

- `2026_HiMCM_ProblemB_Full_Paper_v1.0.docx` — editable master (19 pages)
- `2026_HiMCM_ProblemB_Full_Paper_v1.0.pdf` — PDF view (19 pages)

## What changed from v0.9

The model was rebuilt after the review: platform and waiting-zone areas are separated; cooling water is derived from the adiabatic mass balance; a do-nothing baseline is scored with the same normalisers; safety is a graded, population-weighted WBGT proxy; kappa is dimensionless; per-venue normalisation replaces Set A/Set B.

## Status

- Text complete at 19 pages (<= 25-page limit); footer carries page numbers and the TOC matches this PDF.
- `analysis/qa_check.py` reports zero hits for superseded values.
- Only remaining item: fill the team number on the cover (`Team [Team Number]`).

## Reproduce

```bash
python analysis/recompute.py          # model, tables 3-6
python analysis/build_full_paper.py   # docx
python analysis/make_figures.py       # figures 1-6 (needs matplotlib)
python analysis/qa_check.py           # stale-value scan
```
