# Trial log — every run that produced a persistence number

The denominator for "how many things did you try before this worked?".
Design iterations before any result (dividends, families, inference) are documented as amendments in
preregistration.md and are not trials: no persistence statistic existed when they were made.

| date | run | what changed | result |
|---|---|---|---|
| 2026-10-14 | run_g3.py #1 | first run on real data | crashed at the transition-matrix table (dtype bug); the primary statistic was computed in memory but not saved or seen |
| 2026-10-14 | run_g3.py #2 | dtype fix only (presentation) | primary P̂ 33.3% vs 19.8%, p = 0.025; 8 sensitivities p 0.012–0.035; exploratory 2017–19 P̂ 12.9% |
| 2026-10-14 | g3_timing_sensitivity.py | pre-registered payout-timing variants (Jan / Dec / lowest-excess month) | p 0.014–0.020 |
| 2026-10-14 | g3_exploratory_tails.py | NOT pre-registered: split by ranking-window active risk | descriptive only; high-risk prior winners 37% stay top / 35% fall to bottom |
| 2026-10-14 | g4_investability.py | pre-registered G4 rule; switching-cost levels 0 / 0.5 / 1 / 2% chosen at run time | +1.1%/yr vs SCBSET gross, t = 0.50 |

No variant of the primary test was run and discarded. Number of primary tests run: 1.
