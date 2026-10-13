"""
G2 step — clean raw daily NAV before any return is computed.

Rules (each one logged, nothing silently changed):
  1. duplicate dates            -> keep last
  2. NAV <= 0 or missing        -> drop row
  3. one-day spike-and-reverse  -> drop the bad day
       |r_t| > 5%, the next day undoes it (|r_t + r_t+1| < 1%), and the benchmark moved < 3% that day.
       Found via T-SPT: 2007-03-01 +70%, 2007-03-02 -69.5%.
       Must run BEFORE payout detection, or such errors would be read as dividends.
  4. stale NAV                  -> FLAG only (not changed)
       NAV unchanged for >= 5 consecutive records while the benchmark moved > 2% in that span.
  5. gaps                        -> FLAG only: > 10 calendar days between NAV dates.

Benchmark = SCBSET class of SCB SET Index Fund (M0026_2539).
In : data/raw/nav/<proj_id>.csv
Out: data/processed/nav_clean/<proj_id>.csv, data/processed/cleaning_log.csv
Run: python src/clean_nav.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "data/raw/nav", ROOT / "data/processed/nav_clean"
OUT.mkdir(parents=True, exist_ok=True)

SPIKE, UNDO, BENCH_QUIET = 0.05, 0.01, 0.03
STALE_RUN, STALE_BENCH = 5, 0.02
GAP_DAYS = 10

b = pd.read_csv(RAW / "M0026_2539.csv", parse_dates=["nav_date"])
b = (b[b["fund_class_name"] == "SCBSET"].drop_duplicates("nav_date", keep="last")
     .set_index("nav_date")["last_val"].astype(float).sort_index())
b_ret = np.log(b).diff()

log = []


def note(pid, cls, rule, date, detail):
    log.append({"proj_id": pid, "class": cls, "rule": rule, "date": date, "detail": detail})


def clean_class(pid, cls, g):
    n0 = len(g)
    g = g.sort_values("nav_date")
    dup = g.duplicated("nav_date", keep="last")
    for d in g.loc[dup, "nav_date"]:
        note(pid, cls, "1_duplicate_date", d.date(), "kept last")
    g = g[~dup]
    g["last_val"] = pd.to_numeric(g["last_val"], errors="coerce")
    bad = g["last_val"].isna() | (g["last_val"] <= 0)
    for d in g.loc[bad, "nav_date"]:
        note(pid, cls, "2_nonpositive_or_missing", d.date(), "dropped")
    g = g[~bad].set_index("nav_date")

    # 3. spike-and-reverse, iterate until none left
    while True:
        r = np.log(g["last_val"]).diff()
        nxt = r.shift(-1)
        br = b_ret.reindex(r.index).fillna(0)
        hit = (r.abs() > SPIKE) & ((r + nxt).abs() < UNDO) & (br.abs() < BENCH_QUIET)
        if not hit.any():
            break
        for d in r.index[hit]:
            note(pid, cls, "3_spike_reverse", d.date(), f"r={r[d]:+.1%}, next={nxt[d]:+.1%}, bench={br[d]:+.1%}; day dropped")
        g = g[~hit]

    # 4. stale runs (flag only)
    v = g["last_val"]
    run_id = (v != v.shift()).cumsum()
    for _, seg in v.groupby(run_id):
        if len(seg) >= STALE_RUN:
            s, e = seg.index[0], seg.index[-1]
            bmove = b.reindex([s, e], method="ffill")
            if len(bmove.dropna()) == 2 and abs(bmove.iloc[1] / bmove.iloc[0] - 1) > STALE_BENCH:
                note(pid, cls, "4_stale_flag", s.date(), f"{len(seg)} records unchanged to {e.date()}, bench moved {bmove.iloc[1]/bmove.iloc[0]-1:+.1%}")

    # 5. gaps (flag only)
    gaps = g.index.to_series().diff().dt.days
    for d, days in gaps[gaps > GAP_DAYS].items():
        note(pid, cls, "5_gap_flag", d.date(), f"{int(days)} days since previous NAV")

    return g.reset_index(), n0 - len(g)


files = sorted(RAW.glob("*.csv"))
dropped_total = 0
for f in files:
    d = pd.read_csv(f, parse_dates=["nav_date"])
    pid = f.stem
    if d.empty:
        d.to_csv(OUT / f.name, index=False)
        continue
    parts = []
    for cls, g in d.groupby("fund_class_name"):
        cg, dropped = clean_class(pid, cls, g.copy())
        dropped_total += dropped
        parts.append(cg)
    pd.concat(parts).to_csv(OUT / f.name, index=False)

lg = pd.DataFrame(log)
lg.to_csv(ROOT / "data/processed/cleaning_log.csv", index=False)
print(f"files: {len(files)} | rows dropped: {dropped_total}")
if len(lg):
    print(lg.groupby("rule").agg(events=("proj_id", "size"), funds=("proj_id", "nunique")).to_string())
