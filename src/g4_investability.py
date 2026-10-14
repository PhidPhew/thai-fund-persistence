"""
G4 — is "buy last year's top quintile" investable? (preregistration decision rule: run if persistence found)

Strategy, each January 2020–2025: equal-weight the top-quintile family representatives from the G3 panel,
buy-and-hold for 12 months (weights drift), then switch. A fund that closes or has a missing month earns SCBSET
for that month (proceeds parked in the index fund). Management fees are already inside NAV.
Switching cost (front-end + back-end fees, unknown per fund) is applied as a round-trip % on the share of the
portfolio that is replaced each January — shown for several levels plus the break-even level.
Comparisons: SCBSET buy-and-hold; average active fund (all rankable representatives); bottom quintile.
Out: reports/g4_investability.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data/processed"
pan = pd.read_csv(P / "g3_panel.csv")
pan = pan[pan["year"].between(2020, 2025)]
m = pd.read_csv(P / "monthly_returns.csv")
m["month"] = pd.PeriodIndex(m["month"], freq="M")
ret = m.pivot(index="month", columns="proj_id", values="r_tr")
b = pd.read_csv(P / "benchmark_monthly.csv")
bench = pd.Series(b["bench"].values, index=pd.PeriodIndex(b.iloc[:, 0], freq="M"))
pan["rank_q"] = pan.groupby("year")["alpha_rank"].transform(
    lambda s: pd.qcut(s.rank(method="first"), 5, labels=[5, 4, 3, 2, 1])).astype(int)


def portfolio(select, cost_rt=0.0):
    """select(year_df) -> list of proj_id. Returns monthly returns (Series) and turnover by year."""
    out, prev, turnover = [], set(), {}
    for Y, g in pan.groupby("year"):
        ids = list(select(g))
        months = pd.period_range(f"{Y}-01", f"{Y}-12", freq="M")
        R = ret.reindex(index=months, columns=ids)
        R = R.apply(lambda col: col.fillna(bench.reindex(months)))         # closed/missing -> SCBSET
        w = np.full(len(ids), 1 / len(ids))
        new = set(ids)
        to = 1 - len(new & prev) / len(new) if prev else 1.0
        turnover[Y] = to
        for i, mth in enumerate(months):
            r = float(w @ R.loc[mth].values)
            if i == 0:
                r -= cost_rt * to
            out.append((mth, r))
            w = w * (1 + R.loc[mth].values)
            w = w / w.sum()
        prev = new
    s = pd.Series(dict(out))
    return s, turnover


def stats(r, name):
    bm = bench.reindex(r.index)
    yrs = len(r) / 12
    ann = (1 + r).prod() ** (1 / yrs) - 1
    ann_b = (1 + bm).prod() ** (1 / yrs) - 1
    ex = r - bm
    X = np.column_stack([np.ones(len(r)), bm.values])
    c, *_ = np.linalg.lstsq(X, r.values, rcond=None)
    e = r.values - X @ c
    # Newey-West (lag 3) s.e. of alpha
    L, n = 3, len(e)
    Xe = X * e[:, None]
    S = Xe.T @ Xe
    for l in range(1, L + 1):
        G = Xe[l:].T @ Xe[:-l]
        S += (1 - l / (L + 1)) * (G + G.T)
    XtXi = np.linalg.inv(X.T @ X)
    V = XtXi @ S @ XtXi
    wealth = (1 + r).cumprod()
    mdd = (wealth / wealth.cummax() - 1).min()
    yearly = (1 + r).groupby(r.index.year).prod() - 1
    yearly_b = (1 + bm).groupby(bm.index.year).prod() - 1
    return dict(strategy=name, ann_return=ann, vs_SCBSET=ann - ann_b, alpha_ann=c[0] * 12,
                alpha_t=c[0] / np.sqrt(V[0, 0]), beta=c[1], tracking_err=ex.std() * np.sqrt(12),
                vol=r.std() * np.sqrt(12), max_dd=mdd, years_beat=f"{int((yearly > yearly_b).sum())}/{len(yearly)}")


rows, yearly = [], {}
top, to_top = portfolio(lambda g: g.loc[g["X"] == 1, "proj_id"])
allf, _ = portfolio(lambda g: g["proj_id"])
bot, _ = portfolio(lambda g: g.loc[g["rank_q"] == 5, "proj_id"])
rows += [stats(top, "Top quintile (0% switching cost)"), stats(allf, "All active funds (avg)"),
         stats(bot, "Bottom quintile"), stats(bench.reindex(top.index), "SCBSET (index fund)")]
mean_to = np.mean(list(to_top.values()))
for c in [0.005, 0.01, 0.02]:
    r, _ = portfolio(lambda g: g.loc[g["X"] == 1, "proj_id"], cost_rt=c)
    rows.append(stats(r, f"Top quintile, {c:.1%} round-trip on switched part"))
# exploratory variant: top quintile restricted to low/mid active risk (from g3_exploratory_tails)
tab = pd.DataFrame(rows)
for c in ["ann_return", "vs_SCBSET", "alpha_ann", "tracking_err", "vol", "max_dd"]:
    tab[c] = tab[c].map(lambda v: f"{v:+.2%}" if c in ("vs_SCBSET", "alpha_ann") else f"{v:.2%}")
tab["alpha_t"] = tab["alpha_t"].map(lambda v: f"{v:.2f}")
tab["beta"] = tab["beta"].map(lambda v: f"{v:.2f}")

gap = stats(top, "")["vs_SCBSET"]
be = gap / mean_to if mean_to > 0 else np.nan
yr = pd.DataFrame({"top_quintile": (1 + top).groupby(top.index.year).prod() - 1,
                   "SCBSET": (1 + bench.reindex(top.index)).groupby(top.index.year).prod() - 1,
                   "all_active": (1 + allf).groupby(allf.index.year).prod() - 1,
                   "turnover": pd.Series(to_top)})
out = ["# G4 — Investability of 'buy last year's top quintile' (2020–2025)\n",
       "Equal-weight, buy-and-hold within the year, switch each January; closed/missing months earn SCBSET.\n",
       tab.to_markdown(index=False) + "\n",
       f"- Average share of the portfolio replaced each January: **{mean_to:.0%}**",
       f"- Break-even round-trip switching cost (annual outperformance ÷ turnover): **{be:.2%}**",
       "- alpha_t uses Newey-West (3 lags) on 72 monthly returns; one strategy, no cluster issue.\n",
       "## Year by year\n", yr.to_markdown(floatfmt=".2%")]
(ROOT / "reports/g4_investability.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
