# Submission snapshot — v1.3 (2026-11-16)

This folder is the **shareable snapshot** of the integrated English paper. The root files remain the source of truth.

## Files

- `2026_HiMCM_ProblemB_Full_Paper_v1.2.docx` — v1.2, template format (23 pages)
- `2026_HiMCM_ProblemB_Full_Paper_v1.2.pdf` — v1.2 PDF (23 pages)
- `2026_HiMCM_ProblemB_Full_Paper_v1.2_AllInOne.docx` — v1.2 + internal checklist page

- `2026_HiMCM_ProblemB_Full_Paper_v1.1.docx` — editable master (v1.5 + review revisions, 22 pages)
- `2026_HiMCM_ProblemB_Full_Paper_v1.1.pdf` — PDF view (22 pages)
- `2026_HiMCM_ProblemB_Full_Paper_v1.1_AllInOne.docx` — paper + internal checklist page (23 pages; delete the checklist page before submission)

## What changed from v0.9

The model was rebuilt after the review: platform and waiting-zone areas are separated; cooling water is derived from the adiabatic mass balance; a do-nothing baseline is scored with the same normalisers; safety is a graded, population-weighted WBGT proxy; kappa is dimensionless; per-venue normalisation replaces Set A/Set B; hourly ERA5 scenarios, 1,000-draw joint uncertainty, installation/labour adders and a 30% jet-overlap scenario were added in Sections 5.1–5.3.

The 2026-11-16 v1.2 revision fixes six contradictions found in review (Q2a do-nothing comparison, HK rail comparator, Cost/Eco wording, blog fan power, kappa=60 values) and adds a safety screen, the full-cost reversal of the Hong Kong platform recommendation, Q2a robustness bounds, hourly/Monte-Carlo settings, and explicit structural limits (wind cancellation, fan safety asymmetry, uncalibrated kappa, coverage-area flip). The earlier revision adds: a one-paragraph Q2b model-revision statement (what changed / why / how the answer changed); a Q3 paragraph ranking coverage, climate and power as efficiency drivers; a 5.4 plausibility-check table; Appendix B with the full single-factor sensitivity table; Figure 1 redrawn (Eq. 4 and Eq. 5 as parallel inputs to Eq. 6; φ = min(1, n·A_cov/A_waiting)); Figure 3 redrawn as two design-day panels (41 °C and 31.7 °C); Figure 4 with an inset that separates the two fan points; Figure 6 with a platform note; bracketed citations [1]–[15] throughout; and the team number on the cover.

## Status

- 2026-11-16 (third review round): fixed the 1.2 kW / 0.25 kW device mix-up in §4.1, replaced the "no saving" wording with "not preferable under this scoring rule", turned the Hong Kong two-unit switching advice into a re-evaluation point in the summary and guidelines, added the κ≈92 caveat to the summary and guidelines, corrected κ=45 to a 7.0 m throw and the A_cov flip threshold to +0.6% (88.5 m²), added Table 10b (water-limited joint operating point: Phoenix bus flips to the fan, platform flips to MC37V), added full-cost columns to Table 6c, relabelled the 6-person occupancy as a peak-hour estimate, and reframed the safety threshold as a modelling reference.
- 2026-11-16 (review round): corrected the 115 W safety classification, separated the Q2a fan ranking from 41 °C deployment, removed the unreproducible occupancy-flip row (E is invariant to N once normalisers are recomputed), demoted the NASA crosswind correction to a stated scenario normalised per city, extended κ to 80-105 (bus order flips above κ≈92), fixed the water convention (0.2845), added the full-cost network budget ($24,222/yr), explained the 825-hour Phoenix window, added the design-hour record and geometry caveat.
- 2026-11-16 (final): added §6.3 Deployment Guidelines across the four city–venue cases (Problem B requirement 5), renumbered references to §6.4, fixed a missing currency symbol in the blog section, and started Appendix A on a new page. Page count is 22 after equations were typeset, and the TOC was updated to match.
- Text complete at 22 pages (<= 25-page limit); footer carries page numbers and the TOC matches this PDF.
- 2026-11-16 v1.5: base promoted to ISO 33 °C and the HK hot-humid design hour (31.7 °C / 77% RH); Table 3–6, Figures 2–6, MC and Appendix B regenerated. At this base the HK platform is a hair below doing nothing (0.2858 vs 0.2865), the HK bus fan still wins (0.3541), and the Phoenix platform is a near-tie (MC61V 0.4026 vs MC37V 0.4015).
- 2026-11-16 v1.4: hourly Table 7 now converts ERA5 UTC to local time (828 Hong Kong / 825 Phoenix hours); the memo answers Q5(a) for one named venue (Phoenix rail); 28 °C is both a real stricter safety-curve row in Appendix B and an exposure check in Table 6b; 5.7 + Table 11 report the definition sensitivity for the design day, ISO 30/33 °C, Q2a 5/8 °C, Phoenix N_eff and the fan/κ/water break-evens.
- `analysis/qa_check.py` reports no superseded values; Appendix B intentionally keeps the 0.850 / 0.465 sensitivity labels and Table 8 keeps the 68% Monte-Carlo probability.
- Team number: **19362**.

## Reproduce

```bash
python analysis/recompute.py          # model, tables 3-6
python analysis/build_full_paper.py   # docx
python analysis/make_figures.py       # figures 2-6 (needs matplotlib)
python analysis/make_fig1.py          # figure 1 (needs matplotlib)
python analysis/qa_check.py           # stale-value scan
```
