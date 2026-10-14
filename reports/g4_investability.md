# G4 — Investability of 'buy last year's top quintile' (2020–2025)

Equal-weight, buy-and-hold within the year, switch each January; closed/missing months earn SCBSET.

| strategy                                       | ann_return   | vs_SCBSET   | alpha_ann   |   alpha_t |   beta | tracking_err   | vol    | max_dd   | years_beat   |
|:-----------------------------------------------|:-------------|:------------|:------------|----------:|-------:|:---------------|:-------|:---------|:-------------|
| Top quintile (0% switching cost)               | -1.36%       | +1.11%      | +0.95%      |      0.5  |   0.92 | 4.83%          | 17.21% | -32.87%  | 4/6          |
| All active funds (avg)                         | -2.39%       | +0.08%      | -0.23%      |     -0.17 |   0.9  | 3.78%          | 16.50% | -31.96%  | 3/6          |
| Bottom quintile                                | -3.26%       | -0.79%      | -1.06%      |     -0.42 |   0.88 | 6.13%          | 16.87% | -36.01%  | 3/6          |
| SCBSET (index fund)                            | -2.47%       | +0.00%      | +0.00%      |      0.03 |   1    | 0.00%          | 17.92% | -31.10%  | 0/6          |
| Top quintile, 0.5% round-trip on switched part | -1.63%       | +0.83%      | +0.68%      |      0.36 |   0.93 | 4.76%          | 17.23% | -33.27%  | 4/6          |
| Top quintile, 1.0% round-trip on switched part | -1.91%       | +0.56%      | +0.40%      |      0.22 |   0.93 | 4.72%          | 17.27% | -33.67%  | 3/6          |
| Top quintile, 2.0% round-trip on switched part | -2.46%       | +0.01%      | -0.14%      |     -0.08 |   0.94 | 4.67%          | 17.35% | -34.47%  | 3/6          |

- Average share of the portfolio replaced each January: **55%**
- Break-even round-trip switching cost (annual outperformance ÷ turnover): **2.02%**
- alpha_t uses Newey-West (3 lags) on 72 monthly returns; one strategy, no cluster issue.

## Year by year

|      |   top_quintile |   SCBSET |   all_active |   turnover |
|-----:|---------------:|---------:|-------------:|-----------:|
| 2020 |         -8.58% |   -9.39% |       -7.47% |    100.00% |
| 2021 |         30.68% |   14.52% |       21.60% |     69.70% |
| 2022 |         -3.71% |    3.28% |        0.33% |     42.86% |
| 2023 |        -10.68% |  -14.20% |      -11.73% |     27.03% |
| 2024 |         -4.49% |    1.56% |       -2.33% |     27.50% |
| 2025 |         -6.13% |   -7.83% |      -11.13% |     62.16% |
## Reading
- Gross outperformance vs SCBSET is small (+1.1%/yr, CAPM alpha +0.95%/yr) and **not statistically significant**
  (Newey-West t = 0.50). 4 of 6 years beat SCBSET.
- It depends on one year: annual excess return 2020 +0.8, **2021 +16.2**, 2022 −7.0, 2023 +3.5, 2024 −6.1, 2025 +1.7 pp.
  Without 2021 the average excess is about −1.4 pp/yr.
- Break-even switching cost ≈ 2.0% round-trip on the replaced share (55%/yr). Many Thai platforms waive front-end
  fees, so costs are not the binding problem — the small, unstable edge is.
- The average active fund roughly ties the index fund net of fees (+0.1%/yr vs SCBSET, alpha −0.2%).
- Consistent with G3: rank persistence is real but partly "extreme stays extreme" (U-shaped matrix); top-quintile
  funds that fall to the bottom offset those that stay on top, so the portfolio edge is thin.
- Not modelled: RMF/SSF/Thai ESG holding-period rules that restrict switching; taxes; fund minimums.
