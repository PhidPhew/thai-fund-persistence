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

## Open decision — strategy families (Amendment 1)
Name-based families (247 families) are wrong in both directions, measured by daily return tracking error (TE)
between same-AMC funds, 2014+:
- **Missed clones:** KFSTARRMF/KFTSTAR2 TE 0.01%, STD/STD2 0.02%, KFEQRMF/KFSEQ 0.02%, BKA/BKA2 0.02% …
- **False families:** K-SELECT/K-SELECTRMF TE 0.56%, ES-SMCAP/ES-SMCAPRMF 0.63%, B-TOPTEN/B-TOPTENRMF 0.72%.
TE distribution of same-AMC pairs has a soft dip around 0.10–0.12%. Clusters by threshold:
TE < 0.03% → 263; < 0.06% → 247; **< 0.10% → 224**; < 0.15% → 207 clusters.
Draft clusters at 0.10%: `data/processed/tmp/clone_clusters_te010.csv`.
Beyond clones, same-AMC funds are strongly related (median same-AMC TE 0.49%) → observations are not independent;
relevant to the significance test in G3.
