"""
G3 EXPLORATORY (not pre-registered) — why is the transition matrix U-shaped?
Hypothesis: funds that take more active risk (higher residual volatility vs SCBSET in the ranking window) land in
the tails (top OR bottom) more often, so part of the "top stays top" result is "extreme stays extreme".
Uses data/processed/g3_panel.csv + monthly returns. Writes reports/g3_exploratory_tails.md
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "data/processed"
pan = pd.read_csv(P / "g3_panel.csv")
pan = pan[pan["year"] >= 2020].copy()
m = pd.read_csv(P / "monthly_returns.csv")
m["month"] = pd.PeriodIndex(m["month"], freq="M")
ret = m.pivot(index="month", columns="proj_id", values="r_tr")
b = pd.read_csv(P / "benchmark_monthly.csv")
bench = pd.Series(b["bench"].values, index=pd.PeriodIndex(b.iloc[:, 0], freq="M"))


def resid_vol(pid, Y):
    rk = pd.period_range(f"{Y-3}-01", f"{Y-1}-12", freq="M")
    y, x = ret.loc[rk, pid].values, bench.reindex(rk).values
    X = np.column_stack([np.ones(36), x])
    c, *_ = np.linalg.lstsq(X, y, rcond=None)
    return np.std(y - X @ c, ddof=2) * np.sqrt(12)


pan["te_rank"] = [resid_vol(p, y) for p, y in zip(pan["proj_id"], pan["year"])]
pan["te_tercile"] = pan.groupby("year")["te_rank"].transform(lambda s: pd.qcut(s.rank(method="first"), 3, labels=["low", "mid", "high"]))
ev = pan[pan["status"] == "eval"].copy()
ev["eval_q"] = ev.groupby("year")["alpha_eval"].transform(lambda s: pd.qcut(s.rank(method="first"), 5, labels=[5, 4, 3, 2, 1])).astype(int)
ev["rank_q"] = ev.groupby("year")["alpha_rank"].transform(lambda s: pd.qcut(s.rank(method="first"), 5, labels=[5, 4, 3, 2, 1])).astype(int)
ev["tail_next"] = ev["eval_q"].isin([1, 5])

out = ["# G3 exploratory — tails and active risk (NOT pre-registered; descriptive, no p-values)\n"]
t1 = ev.groupby("te_tercile").agg(funds=("proj_id", "size"), median_te=("te_rank", "median"),
                                  in_tail_next=("tail_next", "mean"),
                                  share_in_top_q_now=("rank_q", lambda s: (s == 1).mean()),
                                  share_in_bottom_q_now=("rank_q", lambda s: (s == 5).mean()))
out.append("## 1. Active risk in the ranking window vs landing in a tail next year (expected 40% if unrelated)\n" + t1.to_markdown(floatfmt=".2f") + "\n")
top = ev[ev["rank_q"] == 1]
t2 = top.groupby("te_tercile").agg(n=("proj_id", "size"), stay_top=("eval_q", lambda s: (s == 1).mean()),
                                   fall_bottom=("eval_q", lambda s: (s == 5).mean()))
out.append("## 2. Prior top-quintile funds, by their active risk\n" + t2.to_markdown(floatfmt=".2f") + "\n")
# within-tercile repeat rate controls for active risk crudely
out.append("## 3. Top→top repeat rate, all vs low/mid-risk funds only\n")
out.append(f"- all prior-top funds: {(top['eval_q'] == 1).mean():.1%} stay top, {(top['eval_q'] == 5).mean():.1%} fall to bottom (n={len(top)})")
lm = top[top["te_tercile"] != "high"]
out.append(f"- prior-top excluding high-risk tercile: {(lm['eval_q'] == 1).mean():.1%} stay top, {(lm['eval_q'] == 5).mean():.1%} fall to bottom (n={len(lm)})")
out.append("\nCaveats: descriptive only; residual volatility vs SCBSET mixes style bets (size/value/dividend) and stock picking; "
           "the proper test is a multi-factor model (phase 2, parked in later.md).")
(ROOT / "reports/g3_exploratory_tails.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
