"""
G2 — build one monthly total-return series per fund (Amendment 4 + 5).

Steps per fund (all decisions logged):
  1. Quarantine isolated rows: leading/trailing NAV rows separated from the rest of their class by > 365 days
     (e.g. a stray 2004 row in a class that otherwise starts in 2026).
  2. Primary class for 2017+: not PVD > has factsheet returns > history >= 80% of the longest > stated policy
     "never pays" in all factsheets (no payout correction needed) > most NAV rows since 2017.
  3. Lineage: if the primary class starts late / ends early, link a predecessor / successor class whose first/last
     NAV is within 30 days of the break. Seam return must be within 5pp of SCBSET over the same span
     -> "probable" (chained); otherwise "unresolved" (not chained). Written to config/class_lineage.csv.
  4. Monthly price return from the last NAV of each month of the chained daily series.
  5. Factsheet annual total return = modal value over snapshots (0.01pp); no unique mode -> value stable for >= 3
     consecutive snapshots; else missing.
  6. Fund-year correction (needs all 12 months): k = [log(1+R_fs) - sum log(1+r_nav)] / 12 added to each month.
       |R_fs - R_nav| <= 0.05pp  -> "match" (no change)
       implied payout < -0.5%    -> "neg_excluded" (returns set to NaN for that fund-year)
       no factsheet value        -> "nav_only" (kept, flagged)
Out: data/processed/monthly_returns.csv, data/processed/benchmark_monthly.csv,
     data/processed/fundyear_adjustments.csv, config/class_lineage.csv
Run: python src/build_series.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NAV = ROOT / "data/processed/nav_clean"
P = ROOT / "data/processed"
START = pd.Timestamp("2014-01-01")

uni = pd.read_csv(ROOT / "config/universe_review.csv", encoding="utf-8-sig")
uni = uni[uni["include"] == "y"].set_index("proj_id")

# ---------- benchmark ----------
b = pd.read_csv(NAV / "M0026_2539.csv", parse_dates=["nav_date"])
b = b[b["fund_class_name"] == "SCBSET"].set_index("nav_date")["last_val"].sort_index()
bm = b.groupby(b.index.to_period("M")).last()
bench_m = bm.pct_change().dropna().rename("bench")
bench_m.to_frame().to_csv(P / "benchmark_monthly.csv")

# ---------- factsheet annual returns (modal) ----------
fs = pd.read_csv(ROOT / "data/raw/factsheet/performance.csv", low_memory=False,
                 usecols=["proj_id", "fund_class_name", "start_date", "performance_type_desc",
                          "reference_period", "performance_value"])
fs = fs[(fs["performance_type_desc"] == "ผลตอบแทนกองทุนรวม") & fs["reference_period"].str.fullmatch(r"\d{4}")]
fs = fs.dropna(subset=["performance_value"]).copy()
fs["year"] = fs["reference_period"].astype(int)
fs["v"] = fs["performance_value"].round(2)


def consensus(g):
    vc = g["v"].value_counts()
    if len(vc) == 1 or vc.iloc[0] > vc.iloc[1]:
        return vc.index[0]
    seq = g.sort_values("start_date")["v"].tolist()
    best, run = None, 1
    for i in range(1, len(seq)):
        run = run + 1 if seq[i] == seq[i - 1] else 1
        if run >= 3:
            best = seq[i]
    return best


fsa = fs.groupby(["proj_id", "fund_class_name", "year"]).apply(consensus).dropna()
fsa = fsa.to_dict()  # (proj, class, year) -> pct
fs_classes = {}
for (pp, cc, _y) in fsa:
    fs_classes.setdefault(pp, set()).add(cc)

# stated dividend policy per class (factsheets 2022+); "N" in every snapshot = never pays in that period
pol = pd.read_csv(ROOT / "data/raw/factsheet/dividend_policy.csv").dropna(subset=["dividend_policy"])
never_pays = set(pol.groupby(["proj_id", "fund_class_name"])["dividend_policy"]
                 .agg(lambda x: set(x) == {"N"}).loc[lambda x: x].index)

lineage, adj_rows, out = [], [], []


def quarantine(pid, cls, s):
    s = s.sort_index()
    while len(s) > 20:
        gaps = s.index.to_series().diff().dt.days
        if gaps.iloc[1] > 365:                       # stray leading row
            lineage.append(dict(proj_id=pid, from_class=cls, to_class="", seam_from=s.index[0].date(),
                                seam_to=s.index[1].date(), seam_ret="", bench_ret="", evidence="",
                                status="quarantined_row", note=f"isolated leading row {s.iloc[0]}"))
            s = s.iloc[1:]
        elif gaps.iloc[-1] > 365:                    # stray trailing row
            lineage.append(dict(proj_id=pid, from_class=cls, to_class="", seam_from=s.index[-2].date(),
                                seam_to=s.index[-1].date(), seam_ret="", bench_ret="", evidence="",
                                status="quarantined_row", note=f"isolated trailing row {s.iloc[-1]}"))
            s = s.iloc[:-1]
        else:
            break
    return s


def seam_ok(pid, c_from, c_to, a_end, a_val, b_start, b_val):
    r = b_val / a_val - 1
    bb = b.reindex([a_end, b_start], method="ffill")
    br = bb.iloc[1] / bb.iloc[0] - 1
    ok = abs(r - br) <= 0.05
    lineage.append(dict(proj_id=pid, from_class=c_from, to_class=c_to, seam_from=a_end.date(),
                        seam_to=b_start.date(), seam_ret=round(r, 4), bench_ret=round(br, 4),
                        evidence="same proj_id + NAV continuity" if ok else "",
                        status="probable" if ok else "unresolved", note=""))
    return ok


for pid in uni.index:
    d = pd.read_csv(NAV / f"{pid}.csv", parse_dates=["nav_date"])
    if d.empty:
        continue
    cls = {c: quarantine(pid, c, g.set_index("nav_date")["last_val"].astype(float))
           for c, g in d.groupby("fund_class_name")}
    cls = {c: s for c, s in cls.items() if len(s)}
    # class choice: retail (not PVD/institutional-looking) > has factsheet returns > enough history
    # (>= 80% of the best) > never pays (no correction needed) > most rows since 2017
    has_fs = {c: c in fs_classes.get(pid, set()) for c in cls}
    n17 = {c: (s.index >= "2017-01-01").sum() for c, s in cls.items()}
    best = max(n17.values()) or 1
    score = {c: ("PVD" not in c.upper(), has_fs[c], n17[c] >= 0.8 * best, (pid, c) in never_pays, n17[c], len(s))
             for c, s in cls.items()}
    prim = max(score, key=score.get)
    chain = [prim]
    # successors
    cur = prim
    while True:
        end = cls[cur].index[-1]
        cands = [c for c in cls if c not in chain and end < cls[c].index[0] <= end + pd.Timedelta(days=30)]
        if not cands:
            break
        nxt = max(cands, key=lambda c: len(cls[c]))
        if not seam_ok(pid, cur, nxt, end, cls[cur].iloc[-1], cls[nxt].index[0], cls[nxt].iloc[0]):
            break
        chain.append(nxt)
        cur = nxt
    # predecessors
    cur = prim
    while True:
        start = cls[cur].index[0]
        cands = [c for c in cls if c not in chain and start - pd.Timedelta(days=30) <= cls[c].index[-1] < start]
        if not cands:
            break
        prv = max(cands, key=lambda c: len(cls[c]))
        if not seam_ok(pid, prv, cur, cls[prv].index[-1], cls[prv].iloc[-1], start, cls[cur].iloc[0]):
            break
        chain.insert(0, prv)
        cur = prv
    # chained daily index (log returns within classes + seam returns)
    parts, seg_cls = [], []
    for i, c in enumerate(chain):
        s = cls[c]
        if i > 0:
            s = s[s.index > parts[-1].index[-1]]
        lr = np.log(s).diff()
        if i > 0:
            lr.iloc[0] = np.log(s.iloc[0] / parts[-1].iloc[-1])
        parts.append(s)
        seg_cls.append(pd.Series(c, index=s.index))
    idx_parts, level = [], 0.0
    for i, s in enumerate(parts):
        l = np.log(s)
        if i == 0:
            idx = l - l.iloc[0]
        else:
            idx = (l - l.iloc[0]) + idx_parts[-1].iloc[-1] + np.log(s.iloc[0] / parts[i - 1].iloc[-1])
        idx_parts.append(idx)
    idx = pd.concat(idx_parts)
    cl_at = pd.concat(seg_cls)
    idx = idx[idx.index >= START - pd.Timedelta(days=40)]
    if idx.empty:
        continue
    mlast = idx.groupby(idx.index.to_period("M")).last()
    mday = idx.index.to_series().groupby(idx.index.to_period("M")).max()
    r_nav = np.expm1(mlast.diff()).dropna()
    r_nav = r_nav[r_nav.index >= START.to_period("M")]
    fdf = pd.DataFrame({"r_nav": r_nav})
    fdf["last_nav_day"] = mday.reindex(fdf.index).dt.day
    fdf["class_at_month_end"] = [cl_at[mday[m]] if not isinstance(cl_at[mday[m]], pd.Series) else cl_at[mday[m]].iloc[-1] for m in fdf.index]
    fdf["r_tr"] = fdf["r_nav"]
    fdf["flag"] = ""
    for y, g in fdf.groupby(fdf.index.year):
        if len(g) != 12:
            fdf.loc[g.index, "flag"] = "partial_year_nav_only"
            continue
        r_nav_y = np.expm1(np.log1p(g["r_nav"]).sum())
        cands = [g["class_at_month_end"].iloc[-1], g["class_at_month_end"].iloc[0]]
        R = next((fsa.get((pid, c, y)) for c in cands if fsa.get((pid, c, y)) is not None), None)
        row = dict(proj_id=pid, year=y, r_nav=round(r_nav_y * 100, 3), r_factsheet=R)
        if R is None:
            fdf.loc[g.index, "flag"] = "nav_only"
            row["status"] = "nav_only"
        else:
            diff = R - r_nav_y * 100
            row["diff_pp"] = round(diff, 3)
            implied = (1 + R / 100) / (1 + r_nav_y) - 1
            if abs(diff) <= 0.05:
                row["status"] = "match"
            elif implied < -0.005:
                fdf.loc[g.index, ["r_tr"]] = np.nan
                fdf.loc[g.index, "flag"] = "neg_excluded"
                row["status"] = "neg_excluded"
            else:
                k = (np.log1p(R / 100) - np.log1p(g["r_nav"]).sum()) / 12
                fdf.loc[g.index, "r_tr"] = np.expm1(np.log1p(g["r_nav"]) + k)
                fdf.loc[g.index, "flag"] = "adjusted" if diff > 0 else "adjusted_small_negative"
                row["status"] = fdf.loc[g.index[0], "flag"]
        adj_rows.append(row)
    fdf["proj_id"] = pid
    fdf.index.name = "month"
    out.append(fdf.reset_index())

m = pd.concat(out)
m["month"] = m["month"].astype(str)
m.to_csv(P / "monthly_returns.csv", index=False)
a = pd.DataFrame(adj_rows)
a.to_csv(P / "fundyear_adjustments.csv", index=False)
pd.DataFrame(lineage).to_csv(ROOT / "config/class_lineage.csv", index=False)

print("funds:", m["proj_id"].nunique(), "| fund-months:", len(m))
print("\nfund-year status:\n", a["status"].value_counts().to_string())
print("\nlineage events:\n", pd.DataFrame(lineage)["status"].value_counts().to_string())
