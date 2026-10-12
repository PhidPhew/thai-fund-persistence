# Pre-registration (G0) — LOCKED 2026-10-12

Written after G1 (data feasibility) and **before any fund-performance result was computed**.
Any change after this date goes in the "Amendments" section with date and reason; the original text stays.

## Research question
Do Thai active equity funds that outperformed in the past keep outperforming — i.e. is there persistent manager skill,
or is past outperformance explained by market exposure and luck?

## Hypotheses
- **H0 (no persistence):** a fund in the top quintile of risk-adjusted performance over the ranking window is no more
  likely than chance (20%) to be in the top quintile over the following 12 months.
- **H1 (persistence):** that probability is significantly above 20%.

## Universe
- Open-ended mutual funds with `policy_desc` = ตราสารทุน, investing in Thailand (`invest_country_flag` = 3),
  actively managed (`management_style` = AM), retail.
- Funds with empty style/country fields (mostly died before 2018) are classified by hand from name and policy text;
  the classification list is committed to the repo.
- **All statuses included** (Registered, Liquidated, Expired, Canceled) — survivorship.
- Excluded: index / passive (PM, PN, SM), feeder funds (AN), foreign-investing funds, trigger / fixed-term funds,
  sector funds.
- One series per fund (`proj_id`): prefer the accumulating retail class with the longest history.
  LTF/RMF/SSF classes inside the same project are not counted as separate funds.
- No exclusion by fund size or age at the universe level. Funds with < 36 months of history are skipped only at
  ranking time.

## Data
- Daily NAV: SEC Open API v2 `/v2/fund/daily-info/nav`.
- Dividends: endpoint is empty → for classes that pay out, payouts are detected as NAV drops relative to the benchmark
  and added back. Validated against factsheet-reported returns (2022+).
- Monthly returns from month-end NAV.

## Benchmark
- **Primary:** SCB SET Index Fund, class SCBSET (`M0026_2539`) — the index fund an investor could actually buy.
  Both sides are net of fees. Tracks SET TRI at −0.95%/yr, daily TE 0.05% (2021–2026).
- Checks: real SET TRI (2021-10+); fund's own stated benchmark (2022-06+).

## Sample period
- **Primary:** returns from 2014-01. First ranking at 2017-01 (after 36 months) → evaluation years 2017 … 2025.
- **Robustness:** same tests from 2002-01, with the limitation that equity funds which died before 2014 may be
  missing from the SEC database.

## Method
1. **Ranking metric:** CAPM alpha vs SCBSET, estimated on the prior 36 monthly returns.
2. **Ranking date:** each January; non-overlapping 12-month evaluation windows.
3. **Evaluation metric:** CAPM alpha over the next 12 months, re-estimated.
4. **Transition matrix:** quintile at t → quintile at t+1, **plus a "closed / merged" column.**
5. **Primary statistic:** P(top quintile at t+1 | top quintile at t), pooled over all ranking years.
   Funds that close during the evaluation year count as **not** top quintile (primary); survivor-only version reported
   alongside to show the size of the bias.
6. **Significance:** permutation test — shuffle evaluation-period ranks within each year, 10,000 draws, one-sided,
   α = 0.05. Report the estimate with a 95% bootstrap confidence interval.
7. **Secondary:** Spearman rank correlation between consecutive periods; mean next-year alpha of top vs bottom
   quintile.
8. **Power rule:** if the average number of rankable funds per year is below 80, use terciles instead of quintiles
   (H0 base rate becomes 33%). Decided on fund count only, before looking at returns.

## Decision rule
- p ≥ 0.05 on the primary statistic → **"no evidence of persistence"** (and report the power, so "no evidence"
  is not misread as "evidence of no skill").
- p < 0.05 → persistence found → G4 checks whether a "buy last year's top quintile" rule beats SCBSET after
  switching costs.

## Not in scope (see later.md)
Multi-factor attribution (size/value/momentum), provident funds, foreign-investing funds.

## Amendments
(none)
