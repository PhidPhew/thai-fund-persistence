# G2 — Dividend handling: what the data can and cannot tell us (2026-10-13)

## 1. NAV-based payout detection is not good enough on its own
Scan of 269 funds (beta-adjusted residual vs SCBSET, drops > max(1%, 3σ), recurring by season):
vs. factsheet dividend policy → precision 39/55 = 71%, **recall 39/124 = 31%**.
False positives are mostly RMF/SSF and small-cap funds (style mismatch vs SCBSET, the 2024-11 data hole).
Known case: KFLTFA50-D, announced 0.30 THB (~1.6%) XD 2021-02-11, residual only ≈ −0.8%.

## 2. Factsheet dividend policy (SEC API, factsheets from 2022-06)
- 263 of 272 universe funds covered. Missing: 11 funds that closed before 2022 (incl. the 5 Thanachart funds).
- Funds: 137 only "N" classes, 36 only "Y", 88 mixed. 197 funds have at least one class that never pays.
- **Policy changes over time:** 57 classes changed policy within 2022–2026 (52 of them N → Y).
  → A 2022+ policy cannot be assumed to hold back to 2014.

## 3. Fund-reported calendar-year returns include dividends — usable as ground truth
Factsheet "ผลตอบแทนกองทุนรวม" by calendar year vs our NAV-only return:
- K-EQUITY: 2020 +0.03, 2021 −0.00, 2024 +0.04, 2025 +0.00 pp (no payout years → match exactly);
  2017 +11.98, 2018 +4.70, 2022 +2.53 pp (payout years).
- KF-ASET50: +1.35 to +4.47 pp every year (regular payer).
→ Reported − NAV-only = implied payouts for that year. Also validates our NAV data in non-payout years.
Coverage (funds with a reported return for that year): 2017: 184, 2018: 207, … 2025: 246; **2014–2016: ~2**.

## Open decision
How to build total returns given: exact annual totals for 2017–2025, no payout dates, and almost nothing for 2014–2016
(which the pre-registered design uses for the first ranking windows).
