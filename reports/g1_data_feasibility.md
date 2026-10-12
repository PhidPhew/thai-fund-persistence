# G1 — Data feasibility ✅ CLOSED 2026-10-12 (SEC Open API, Fund v2) — probed 2026-10-12

Scripts: src/sec_probe.py … sec_probe4.py. Raw profile dump: data/raw/probe_profiles.csv (not committed).

| Question | Result | Evidence |
|---|---|---|
| NAV history depth | ✅ back to fund inception (1992) | M0027_2535: 1992-06-12 → 2026-10-09 |
| Dead funds listed | ✅ 5,747 Liquidated of 8,939 funds | profiles, all statuses |
| Dead funds have NAV | ✅ post-2018 deaths; ⚠️ patchy for pre-2018 deaths | M0028_2537 full to 2018-11-07; some 2015–17 deaths return none |
| Share classes | NAV is per class; LTF/RMF are classes inside a project | M0254_2550: K-GROWTH-* and KGLTF-* |
| Stated benchmark history | ❌ only from 2022-06-06, whole market | factsheet/benchmarks by year |
| Dividend history | ❌ endpoint empty (HTTP 204 with no filters) | probe 4 |
| SET TRI | ⚠️ free SET-website file = daily but only 2021-10 → 2026-10; SETSMART individual = also 5 yrs | data/raw/set_tri_daily_set_website.csv |
| Market proxy pre-2021 | ✅ SCBSETFUND class SCBSET (NAV since 1996-08-23) tracks SET TRI: gap −0.95%/yr (≈fee), daily TE 0.05%, corr 0.9985, no payout drops 2021–26 | src/sec_probe5.py |
| Payout detection from NAV | ✅ works for large payouts: ES-SET50-D drops −8.4%, −6.7%, −3.4% on payout dates vs index | src/sec_probe5.py |

## Traps found
- `management_style` and `invest_country_flag` are empty for funds that died before ~2018.
  Filtering `management_style == "AM"` silently re-introduces survivorship bias.
  The 201 empty-style equity funds are mostly foreign / trigger funds; ~10–15 may be Thai active equity → classify by hand.
- Oldest dead equity fund in the DB died in 2014, while NAV goes back to 1992 → equity funds that died before 2014 may be missing entirely. Undetectable from SEC data alone.
- Third-party schema docs were wrong about dividend-history parameters. Trust real pulls over docs.

## Decisions this forces (to lock in preregistration.md)
- Primary benchmark: SCBSET index-fund NAV (investable, net of fees) for every fund, 1996+. Real SET TRI = check 2021+. Stated benchmark = robustness 2022+ only.
- Research question sharpens to: do active funds beat the index fund an investor could actually buy?
- Open G2 check: SCBSET payout behaviour before 2021 is unverified → compare pairwise against K-SET50 / ES-SET50-A for unexplained jumps.
- SETSMART terms forbid redistribution → no SETSMART data in the public repo.
- Return series: prefer accumulating class; for dividend-paying-only funds, detect distributions from NAV vs SET TRI residual jumps, validated against factsheet-reported returns (2022+).
- Universe candidates: policy_desc == ตราสารทุน, invest_country_flag == 3, management_style == AM → 287 funds (all statuses) + hand-classified pre-2018 funds.
- Study start: open — 2014 (DB coverage of dead funds) vs earlier with stated limitation.
