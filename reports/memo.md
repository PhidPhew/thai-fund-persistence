# Skill or Exposure? Performance Persistence in Thai Active Equity Funds

**Research memo · October 2026 · Chawankorn Khamtue (Kasetsart University, Computer Engineering)**
Code, data pipeline and pre-registration: this repository. All design decisions were locked in
`preregistration.md` (with dated amendments) before any persistence statistic was computed.

---

## 1. Question and hypothesis

When a Thai active equity fund beats the market, is it because of skill that persists, or because of the risk
it happened to take? If skill persists, last year's winners should keep winning more often than chance.

- **H0:** a fund in the top quintile of risk-adjusted performance over the past 36 months is no more likely than
  chance to be in the top quintile over the next 12 months.
- **H1:** it is more likely.
- **Pre-specified "no persistence" result:** the repeat rate is not significantly above its exact chance level
  (one-sided α = 0.05).

## 2. Data and method

**Data.** Daily NAV for every Thai mutual fund from the SEC Open API (v2), including liquidated and cancelled funds.
Universe: open-end, Thai-equity, actively managed, retail funds of all statuses — **272 funds** (27 already closed),
from 22 asset management companies (AMCs). Primary sample: returns 2017–2025, rankings each January 2020–2025.

**Benchmark.** SCB SET Index Fund (SCBSET) — the index fund an investor could actually buy. Both sides are net of
fees. It tracks the SET Total Return Index within −0.95%/yr and 0.05% daily tracking error (2021–2026 check).

**Measurement problems solved before testing** (each documented in `reports/`):
1. *Dividends.* SEC NAVs are price-only and the dividend endpoint is empty. NAV-based payout detection caught only
   31% of payers. Instead, each fund-year is constrained to the fund-reported calendar-year total return from its
   factsheet; 72% of fund-years matched NAV to ±0.05 pp, 23% needed a payout correction. A missed payout would lower
   the same fund every year and *manufacture* persistence — which is why the sample starts in 2017, the first year
   with reliable factsheet data.
2. *Survivorship.* Closure is taken from the SEC register, never from the date NAV stops. Metadata fields used for
   filtering are blank for funds that died before ~2018; filtering on them would have silently dropped dead funds.
3. *Share-class renames* that would have created fake fund deaths were chained (39 links, checked for continuity).
4. *Clones.* RMF/SSF/ESG versions of one strategy were grouped by return similarity (same AMC, daily tracking
   error < 0.08%, complete-linkage) into **239 strategy families**; one representative per family per year.
   Name-based grouping was wrong in both directions.

**Test.** Risk-adjusted performance = CAPM alpha vs SCBSET. Funds in the same AMC are correlated (median residual
correlation 0.35 vs 0.19 across AMCs); a standard fund-level permutation test rejected a true H0 11.8% of the time in
simulation. Inference therefore uses a **wild cluster bootstrap-t clustered by AMC** (Webb weights, CR2, one weight per
AMC across all years), testing the repeat rate against its exact chance level. Independent reviews (OpenAI Codex) of the dividend,
family and inference designs are in `reports/reviews/`.

## 3. Findings

**F1 — Rankings persist, statistically.** Of 207 top-quintile observations (2020–2025, 18 AMCs), **33.3% stayed in the
top quintile** the next year, against a chance level of 19.8%. One-sided p = 0.025; 95% CI for the repeat rate
19.8%–45.8%. The result survives all 11 pre-registered sensitivity checks (family definitions, dividend timing,
excluding dividend-paying funds — which strengthens it to 39% —, flagged data, missing data), all with p < 0.05.
Within the same AMC, prior winners also beat their sibling funds (Holm-adjusted p = 0.0002).

**F2 — But much of it is "extreme stays extreme", not "good stays good".** The transition matrix is U-shaped:
prior top-quintile funds were almost as likely to fall to the **bottom** quintile (27%) as to stay on top (33%).
Two thirds of top-quintile funds are high active-risk funds; among them 37% stayed on top and 35% fell to the
bottom. High active-risk funds landed in one of the two tails 62% of the time, vs 40% expected by chance.
*(Exploratory, not pre-registered.)*

**F3 — The persistence is not stable over time.** Repeat rates by year: 16%, 49%, 9%, 54%, 23%, 46% (2020–2025).
In the 2017–2019 exploratory period (price-only data) it was 13%, below chance. One AMC supplies 20% of top
observations; dropping it lowers the excess repeat rate from +13.5 to +8.7 pp.

**F4 — An investor cannot reliably harvest it.** Buying last year's top quintile each January (equal weight) beat
SCBSET by **+1.1%/yr before switching costs, not statistically significant (alpha t = 0.50)**, and almost entirely
because of 2021 (+16.2 pp). Without 2021 it lagged by about 1.4 pp/yr. Break-even round-trip switching cost ≈ 2%.
The average active fund roughly tied the index fund net of fees (+0.1%/yr).

## 4. Limitations — why this could be wrong

- **CAPM only.** Alpha vs one market index cannot separate stock-picking from persistent style tilts (small caps,
  dividend stocks). F2 suggests style is a large part of the story, but a multi-factor model is needed to show it.
- **Short sample.** Six evaluation years and ~20 AMCs (effective cluster count ~11–14). The test has low power: in
  simulation it detects a true 33% repeat rate only ~58% of the time. The CI lower bound sits at the chance level.
- **Dividend timing is approximated.** Annual totals are exact, but payouts are spread evenly within each year;
  results were robust to moving them to January, December or the worst month.
- **Fund-level, not manager-level.** Manager changes are not tracked; "persistence" is of the fund, not a person.
- **Return-based family grouping** infers clones from returns, not holdings.
- **Not modelled in G4:** RMF/SSF holding-period rules, taxes, platform minimums.

## 5. Investment implications

1. **Do not pick Thai equity funds by last year's ranking alone.** It mostly selects funds that take large active
   bets; the next year they are about as likely to be the worst as the best.
2. **If past performance is used, look at the risk taken to get it.** Among lower-risk prior winners, falls to the
   bottom were much rarer (11% vs 35%) — a lead worth testing properly, not yet a rule.
3. **The index fund is a hard benchmark.** Over 2020–2025 the average active fund only tied a low-cost SET index fund,
   and the best simple selection rule did not beat it significantly.

## 6. Reproducibility

`src/` runs the full pipeline from the SEC API to the results; `tests/test_persistence.py` checks the inference code
on synthetic data with a known answer. See README for the run order. Every design change is a dated amendment in
`preregistration.md`; `git log` shows each was committed before the results it could have influenced.
