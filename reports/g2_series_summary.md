# G2 — Monthly total-return series (2026-10-14)

Script: `src/build_series.py` → `data/processed/monthly_returns.csv` (272 funds, ~31k fund-months, 2014-01 → 2026-09),
`data/processed/benchmark_monthly.csv`, `data/processed/fundyear_adjustments.csv`, `config/class_lineage.csv`.
Method: Amendment 5 (factsheet calendar-year return as annual constraint, modal snapshot value, correction spread evenly).

## Fund-year status
| Year | adjusted | small −ve | match | NAV-only (flagged) | excluded |
|---|---|---|---|---|---|
| 2014–2016 | 2 | 3 | 1 | 429 | 0 |
| 2017–2025 | 406 | 39 | 1,340 | 83 | 7 |

- 2017–2025: **71.8% of fund-years match NAV within ±0.05pp**, 23.5% needed a payout correction.
- **Check passed:** compounded monthly total returns equal the factsheet annual return (max error 7e-14 pp).
- **Large corrections are real payouts, not errors:** e.g. TISCOEQF 2021 (+29.7pp) = one-day NAV drop of −23.7% on
  2021-09-14 vs SCBSET −0.6%; BCAP 2021 (+33.1pp) = drops of −15.3% (Feb), −8.9% (Nov), −7.3% (May).
  These lumpy payouts are what the even spreading smooths → evaluation-alpha timing sensitivity is required.
- **Small negative corrections** (−0.05 to −0.39pp, 39 fund-years) cluster by AMC-year (ONE 2024: 12; KTAM 2023: 10)
  → likely an AMC-level calculation convention (year-end cutoff), applied as-is.
- **Excluded** (implied payout < −0.5%): 7 fund-years, all explained as data alignment issues to check later.
- Class choice now prefers a class whose stated policy is "never pays" when its history is ≥ 80% of the longest
  (e.g. M-MIDSMALL: accumulating class instead of the dividend class).

## Class lineage (`config/class_lineage.csv`)
- 39 seams chained as *probable* (same proj_id, seam return within 5pp of SCBSET). KF-ASET50 chain:
  main → KFLTFA50-D (seam −4.3% vs SCBSET −1.5%, across the 2024-11 data hole) → KF-ASET50-L (−0.7% vs −0.5%).
- 4 *unresolved* (not chained): K-EQD and K-GROWTH (+5.8% vs +0.4%, 2025-12-24), UTACTIVE-M (−26%), UTHAISME-M
  (+91%, 2024-11) — new classes at a different unit price level. These funds' series stop at the seam
  (their register status decides closure, not the NAV end).
- 4 isolated rows quarantined (KF-ASET50-D 2004-10-27 etc.).

## Strategy families — decided (Amendment 6)
Return-based, complete-linkage (`src/build_families.py`): **239 families** from 272 funds in the primary analysis;
sensitivity 225 (gray merged), 247 / 229 / 217 (TE-only 0.06 / 0.10 / 0.15%).
My first draft used single-linkage (224 clusters) — wrong: it chained TLEQRMF with TLEQ-SELECT (TE 0.76%).
Caught by the Codex review (reports/reviews/2026-10-14_families_codex_summary.md).

## G2 status: CLOSED 2026-10-14
Clean NAV → class lineage → monthly total returns (factsheet-constrained) → families. Carried into G3:
representative-per-date selection, AMC-level dependence in inference, timing sensitivity for payouts,
flagged NAV-only fund-years, 4 unresolved class seams.
