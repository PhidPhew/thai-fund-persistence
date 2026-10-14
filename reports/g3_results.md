# G3 results — primary pre-registered analysis (Amendment 7)

Run with seed 20261014, 99,999 bootstrap draws. Panel: data/processed/g3_panel.csv

## Cohorts 2020–2025
|   year |   families |   top |   closed |   missing |       p0 |
|-------:|-----------:|------:|---------:|----------:|---------:|
|   2020 |        126 |    25 |        0 |         0 | 0.198413 |
|   2021 |        164 |    33 |        0 |         0 | 0.20122  |
|   2022 |        177 |    35 |        0 |         0 | 0.19774  |
|   2023 |        186 |    37 |        1 |         0 | 0.198925 |
|   2024 |        198 |    40 |        1 |         0 | 0.19697  |
|   2025 |        185 |    37 |        5 |         1 | 0.195652 |

## Primary result

- Top-quintile observations: **207** from **18** AMCs
- Repeat rate P̂ = **33.3%** vs exact null P̂0 = 19.8% (Δ = +13.5%)
- 95% CI for Δ (inverted WCR, 9,999 draws/grid point): [+0.0%, +26.0%] → P in [19.8%, 45.8%]
- Wild cluster bootstrap-t (AMC, Webb, CR2): t = 2.31, one-sided **p = 0.0253**
- Decision (α = 0.05): **reject H0 — persistence**

## Diagnostics

- Share of top observations from the largest AMC (TISCO ASSET MANAGEMENT COMPANY LIMITED): 20.3%
- Leave-one-AMC-out Δ: min +8.7% (drop TISCO ASSET MANAGEMENT COMPANY LIMITED), max +15.5% (drop MFC ASSET MANAGEMENT PUBLIC COMPANY LIMITED )

By year (descriptive, not a test):
|   year |    top |   repeat |    p0 |
|-------:|-------:|---------:|------:|
|   2020 | 25.000 |    0.160 | 0.198 |
|   2021 | 33.000 |    0.485 | 0.201 |
|   2022 | 35.000 |    0.086 | 0.198 |
|   2023 | 37.000 |    0.541 | 0.199 |
|   2024 | 40.000 |    0.225 | 0.197 |
|   2025 | 37.000 |    0.459 | 0.196 |

## Transition matrix 2020–2025 (row = ranking quintile, 1 = top; share of row)
|   rank_q |   Q1 |   Q2 |   Q3 |   Q4 |   Q5 |   closed |   missing |
|---------:|-----:|-----:|-----:|-----:|-----:|---------:|----------:|
|        1 | 0.33 | 0.15 | 0.11 | 0.13 | 0.27 |     0.00 |      0.00 |
|        2 | 0.20 | 0.20 | 0.18 | 0.23 | 0.18 |     0.00 |      0.00 |
|        3 | 0.20 | 0.22 | 0.21 | 0.20 | 0.16 |     0.00 |      0.00 |
|        4 | 0.11 | 0.23 | 0.27 | 0.25 | 0.12 |     0.01 |      0.00 |
|        5 | 0.15 | 0.19 | 0.21 | 0.17 | 0.28 |     0.00 |      0.00 |

## Secondary (Holm-adjusted, 19,999 draws)

- Within-AMC: β = +0.166 (top vs sibling families, same AMC-year), p = 0.0001, Holm p = 0.0002, AMCs = 16
- Top − bottom quintile evaluation alpha: +2.91%/yr, p = 0.0023, Holm p = 0.0023, AMCs = 19

## Sensitivity (primary statistic; 19,999 draws)

| variant                           |   n_top | P_hat   | P0    | delta   |      p |
|:----------------------------------|--------:|:--------|:------|:--------|-------:|
| primary                           |     207 | 33.3%   | 19.8% | +13.5%  | 0.0263 |
| gray pairs merged                 |     196 | 33.2%   | 19.8% | +13.3%  | 0.0348 |
| T-NSET excluded                   |     207 | 33.3%   | 19.8% | +13.5%  | 0.0263 |
| flagged NAV-only months removed   |     192 | 33.9%   | 20.0% | +13.9%  | 0.0179 |
| missing evaluation counted as Y=0 |     207 | 33.3%   | 19.8% | +13.5%  | 0.0263 |
| no-payout sub-sample              |      82 | 39.0%   | 19.9% | +19.1%  | 0.0124 |
| family TE<0.06%                   |     212 | 34.0%   | 19.9% | +14.1%  | 0.0183 |
| family TE<0.15%                   |     190 | 33.2%   | 19.8% | +13.4%  | 0.0337 |

### Payout-timing variants (src/g3_timing_sensitivity.py; 19,999 draws)

| variant                       |   n_top | P_hat   | P0    | delta   |      p |
|:------------------------------|--------:|:--------|:------|:--------|-------:|
| payout all in January         |     207 | 32.9%   | 19.8% | +13.0%  | 0.0197 |
| payout all in December        |     207 | 33.8%   | 19.8% | +14.0%  | 0.0175 |
| payout in lowest-excess month |     207 | 33.3%   | 19.8% | +13.5%  | 0.014  |

Not run: YTD-derived monthly proxy (2023–2025).

## Exploratory: evaluation years 2017–2019 (ranking on 2014–2016 NAV-only data — not pooled)

- P̂ = 12.9% vs P̂0 = 19.6%, n_top = 62, p = 0.8886
