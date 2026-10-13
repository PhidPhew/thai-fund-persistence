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

### Amendment 1 — 2026-10-13 (before any fund return was computed)
**Change:** strategy families. RMF / SSF / Thai ESG versions of a fund are often registered as *separate projects*
(e.g. K-SELECT and K-SELECTRMF), not as share classes. Counting them separately would double-count one manager's
decisions and overstate the effective sample size.
**Rule:** funds running the same strategy in a different tax wrapper form one family; the family is represented by the
non-wrapper fund with the longest NAV history (if none, the wrapper fund with the longest history).
Family grouping is proposed from fund names and confirmed by hand in `config/manual_overrides.csv`.
**Why now:** discovered while building the universe file (G2 step 1); no performance data had been looked at.

### Amendment 2 — 2026-10-13 (before any fund return was computed)
**Clarification:** funds with no NAV ever reported (21 funds, almost all status `Expired` with no registration
date — i.e. never launched) are excluded. This is not a survivorship exclusion: these funds never held investor money.

### Amendment 3 — 2026-10-13 (before any fund return was computed)
**Added robustness check:** T-NSET (`M0495_2546`) has an uncertain mandate (see reports/classification_notes.md).
It is included in the main analysis; every headline result is also reported with it excluded.

### Amendment 4 — 2026-10-13 (before any fund return was computed)
1. **Wording:** the study measures **fund-level** persistence (a `proj_id` over time), not individual manager skill —
   manager changes are not tracked. Conclusions are phrased accordingly.
2. **Closure is defined by the SEC register** (`fund_status` Liquidated/Canceled + `cancel_date`), never by the date
   NAV stops. A fund whose NAV ends but whose status is Registered is never counted as closed.
3. **Class lineage:** a fund's return series may chain several share classes across renames. Each link is recorded in
   `config/class_lineage.csv` with an evidence level (verified = AMC document; probable = same `proj_id` + NAV continuity;
   unresolved). Default: verified and probable links are chained; results are also reported without probable links.
4. **Added robustness check — dividend measurement:** NAV-based payout detection misses small payouts
   (test: KFLTFA50-D, announced 0.30 THB ≈ 1.6% on 2021-02-11, showed only ≈ −0.8% vs SCBSET). A missed payout lowers
   the same fund's return every year, which can manufacture persistence. Therefore the persistence test is also run on
   the sub-sample of funds with no detected or announced payouts in the sample period.

### Amendment 5 — 2026-10-14 (before any persistence statistic, transition matrix or p-value was computed)
**Reason:** measurement feasibility, not results. SEC NAV is price-only and the dividend-history endpoint is empty.
NAV-based payout detection has ~31% recall (reports/g2_dividend_findings.md). Fund-reported calendar-year returns
(factsheet, dividends included) exist for 2017–2025 (184–246 funds/year) but for only ~2 funds in 2014–2016.
A missed payout lowers the same fund's return every year, which manufactures persistence in the direction of H1.
Decided after an independent review (OpenAI Codex, read-only) compared with Claude's proposal; decision by the author.

**Total-return construction**
1. Monthly price returns from month-end NAV of the selected (lineage-chained) class.
2. For fund i, year y: k = [log(1+R_factsheet) − Σ log(1+r_NAV,m)] / 12, added to each month's log return, so the
   12 monthly returns compound exactly to the factsheet annual return. Payout timing is unknown; this is a
   timing-neutral convention, not a claim that payouts are monthly.
3. Factsheet annual value = modal value across monthly factsheet snapshots (rounded to 0.01pp), not the latest
   snapshot (110 keys disagree by >0.05pp, max 31.5pp). No unique mode → value stable over ≥3 consecutive snapshots;
   otherwise missing.
4. Negative implied payout below −0.5% that cannot be explained by class/date alignment → fund-year excluded (no
   "negative dividends").
5. Fund-years with no factsheet value: NAV-only returns, **flagged and kept** (not dropped, to avoid silent
   survivorship); all headline results also reported with flagged fund-years excluded.

**Sample (replaces the primary sample section)**
- Primary: returns from 2017-01; first ranking 2020-01; evaluation years **2020–2025** (6 years).
  36-month ranking, January ranking, 12-month evaluation, SCBSET benchmark and the power rule are unchanged.
  Provisional rankable funds per year: 168–226 (above the 80-fund threshold → quintiles).
- Evaluation years 2017–2019 (ranking on 2014–2016 NAV-only data): reported as exploratory only, not pooled
  into the primary statistic.
- The 2002+ series is renamed **price-return robustness** (no payout correction available).

**Sensitivity analyses added**
- Payout allocation: whole annual correction in (a) the month with the lowest fund-minus-benchmark residual,
  (b) January, (c) December; (d) YTD-derived monthly proxy for 2023–2025.
- No-payout sub-sample (Amendment 4).
- Report rank correlation and top-quintile overlap across methods, not only whether p-values change.
