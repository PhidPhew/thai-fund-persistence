# G2 — NAV cleaning & benchmark check (2026-10-13)

Script: `src/clean_nav.py` → `data/processed/nav_clean/`, full event log `data/processed/cleaning_log.csv`.
302 NAV files (272 universe funds + benchmark/check funds). 476 rows dropped in total.

| Rule | Events | Funds | Action |
|---|---|---|---|
| Missing / non-positive NAV | 456 | 3 | dropped (445 are one class, PRINCIPAL iDIV-C) |
| One-day spike-and-reverse | 20 | 18 | bad day dropped |
| Stale NAV (≥5 unchanged records, benchmark moved >2%) | 131 | 51 | flagged only — 117 before 2014, 14 from 2014 |
| Gap > 10 days | 601 | 257 | flagged only |

Dropping a spike-reverse day leaves every multi-day return unchanged; it matters only for daily payout detection
or if the bad day is a month-end. Examples: T-SPT 2007-03-01 (+70%/−69.5%), STD2 1999-01-22 (−987%/+987%).

## Findings
1. **Market-wide data hole, 2024-11-01 → 2024-11-14.** No NAV for any fund, SCBSET included (389 gap flags).
   Month-ends Oct-31 and Nov-29 exist, so monthly returns are unaffected; daily payout detection spans the hole.
2. **Share-class breaks.** A few funds (Krungsri LTF-related) have their history split across classes:
   `main` ends 2024-10-31 and a renamed class starts 2024-11-15, another again from 2025-12-29.
   Picking the single longest class would make these funds look **closed in Oct 2024 — fake deaths** that would
   corrupt the "closed" column. → class selection must chain classes across renames (check NAV continuity).
3. **Early-2004 staleness.** SCBSET and K-EQUITY (and others) show identical NAV for several days around
   2004-01-30 → 2004-02-05; several funds show −5.6%/+5.5% on 2004-02-02 against a stale benchmark.
   Affects the 2002+ robustness sample only.
4. **Stale NAVs are mostly a 1990s phenomenon** (117 of 131 flags before 2014).

## SCBSET as benchmark — payout check before 2021
Compared with K-SET50 (2005–2026) and ES-SET50 (2001–2006): no day on which SCBSET drops while the comparison fund
does not (the signature of a payout). Yearly gaps of ±3–8% (e.g. 2003 −8.7%, 2011 −8.0%) are smooth through the
year — SET vs SET50 composition differences, not payouts. → **No evidence of SCBSET distributions 2001–2026.**
1996–2000 cannot be checked (no comparison index fund) — outside both samples.
