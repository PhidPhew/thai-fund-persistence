# Skill or Exposure? Performance Persistence in Thai Active Equity Funds

Do Thai active equity funds that beat the market keep beating it — and can an investor profit from that?
**Read the 3-page memo first: [`reports/memo.md`](reports/memo.md).**

## Findings (2020–2025, 239 strategy families, 22 AMCs)
| | |
|---|---|
| Top-quintile funds that stay top next year | **33.3%** vs 19.8% by chance — p = 0.025 (AMC-clustered wild bootstrap) |
| …that fall to the bottom quintile instead | **27%** — persistence is largely "extreme stays extreme" |
| Robustness | all 11 pre-registered sensitivity checks p < 0.05 |
| Buying last year's top quintile vs SCB SET index fund | **+1.1%/yr**, not significant (t = 0.50), driven by 2021 |
| Average active fund vs index fund, net of fees | +0.1%/yr (a tie) |

Statistically, rankings persist; economically, an investor could not reliably harvest it. CAPM cannot separate
skill from persistent style bets — the main limitation.

## Research process
| Gate | Status | Evidence |
|---|---|---|
| G0 Question | ✅ 2026-10-12 | `preregistration.md` (+ 7 dated amendments, each committed before the results it affects) |
| G1 Data feasibility | ✅ | `reports/g1_data_feasibility.md` |
| G2 Clean dataset | ✅ | `reports/g2_cleaning_summary.md`, `g2_dividend_findings.md`, `g2_series_summary.md`, `classification_notes.md` |
| G3 Analysis | ✅ | `reports/g3_results.md`, `g3_exploratory_tails.md` (exploratory) |
| G4 Investability | ✅ | `reports/g4_investability.md` |
| G5 Write-up | ✅ | `reports/memo.md` |

Independent design reviews (OpenAI Codex, read-only): `reports/reviews/`. Ideas beyond scope: `later.md`.

## Reproduce
Raw and processed data are **not** committed (SEC data is re-downloadable; size). You need a free SEC Open API key
(https://secopendata.sec.or.th → profile → Subscribe).
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # paste SEC_API_KEY
python src/sec_probe.py              # 1. fund profiles (all statuses) -> data/raw/probe_profiles.csv
python src/build_universe.py         # 2. universe review file (hand decisions: config/manual_overrides.csv)
python src/fetch_nav.py              # 3. daily NAV, all classes (~20 min, resumable)
python src/fetch_div_policy.py       # 4. factsheet dividend policy + fund-reported returns
python src/clean_nav.py              # 5. logged NAV cleaning
python src/build_series.py           # 6. class lineage + factsheet-constrained monthly total returns
python src/build_families.py         # 7. return-based strategy families
python tests/test_persistence.py     # 8. inference code on synthetic data with a known answer
python src/run_g3.py                 # 9. pre-registered analysis -> reports/g3_results.md
python src/g3_timing_sensitivity.py  # 10. payout-timing sensitivity
python src/g3_exploratory_tails.py   # 11. exploratory: active risk and tails
python src/g4_investability.py       # 12. investability -> reports/g4_investability.md
```
`src/sec_probe*.py` (probes 2–5) document the G1 feasibility checks. Results depend on the SEC data snapshot
(downloaded 2026-10-12/13); `config/` holds every hand decision and frozen input (e.g. family pairs hash).

## Repository map
```
preregistration.md   locked design + amendments          trials.md / later.md
config/              universe, overrides, lineage, families (committed decisions)
src/                 pipeline and analysis               tests/   synthetic checks
reports/             gate reports, memo, reviews/        data/    raw + processed (git-ignored)
```
