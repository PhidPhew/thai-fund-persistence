"""
G3 — run the pre-registered persistence analysis (Amendment 7) on the real data.
Run ONLY after preregistration.md (Amendment 7) is committed.
Out: data/processed/g3_panel.csv, reports/g3_results.md
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from persistence import build_panel, holm, wcr_ci, wcr_fe_test, wcr_mean_test  # noqa: E402

P = ROOT / "data/processed"
DRAWS = 99_999

m = pd.read_csv(P / "monthly_returns.csv")
m["month"] = pd.PeriodIndex(m["month"], freq="M")
ret = m.pivot(index="month", columns="proj_id", values="r_tr").sort_index()
flagged = m[m["flag"].isin(["nav_only", "partial_year_nav_only", "neg_excluded"])]
flag_month = flagged.pivot_table(index="month", columns="proj_id", values="r_nav", aggfunc="size").reindex(
    ret.index).fillna(0)
bench = pd.read_csv(P / "benchmark_monthly.csv")
bench = pd.Series(bench["bench"].values, index=pd.PeriodIndex(bench.iloc[:, 0], freq="M"))

uni = pd.read_csv(ROOT / "config/universe_review.csv", encoding="utf-8-sig")
uni = uni[uni["include"] == "y"].set_index("proj_id")
fam = pd.read_csv(ROOT / "config/families.csv").set_index("proj_id")
meta = pd.DataFrame(index=uni.index)
meta["amc"] = uni["comp_name_en"]
meta["is_wrapper"] = uni["is_wrapper"].astype(bool)
meta["regis_date"] = uni["regis_date"]
closed = uni["fund_status"].isin(["Liquidated", "Canceled"])
meta["closed_date"] = pd.to_datetime(uni["cancel_date"].where(closed))
for c in fam.columns:
    if c.startswith("family_"):
        meta[c] = fam[c]
meta["name"] = uni["proj_abbr_name"]


def nflag(cands, Y):
    return flag_month.loc[:f"{Y-1}-12", cands].sum().values


def panel_for(family_col="family_primary", r=ret, md=meta, years=range(2017, 2026)):
    cols = [c for c in r.columns if c in md.index]
    return build_panel(r[cols], bench, md.loc[cols], family_col, list(years), rep_priority=nflag)


def primary_stats(pan, years=range(2020, 2026), draws=DRAWS, missing_as_zero=False):
    x = pan[(pan["X"] == 1) & pan["year"].isin(years)].copy()
    if missing_as_zero:
        x["Y"] = x["Y"].fillna(0)
    x = x[x["Y"].notna()]
    D = x["Y"] - x["p0"]
    d, t, p = wcr_mean_test(D.values, x["amc"].values, draws=draws)
    P_hat = x["Y"].mean()
    P0 = x["p0"].mean()
    return dict(n_top=len(x), n_amc=x["amc"].nunique(), P_hat=P_hat, P0=P0, delta=d, t=t, p=p, x=x)


out = []
pan = panel_for()
pan.assign(name=pan["proj_id"].map(meta["name"])).to_csv(P / "g3_panel.csv", index=False)
prim = primary_stats(pan)
x = prim["x"]
lo, hi = wcr_ci((x["Y"] - x["p0"]).values, x["amc"].values, draws=9_999,
                grid=np.linspace(-0.25, 0.4, 131))
out.append("# G3 results — primary pre-registered analysis (Amendment 7)\n")
out.append(f"Run with seed 20261014, {DRAWS:,} bootstrap draws. Panel: data/processed/g3_panel.csv\n")
coh = pan[pan["year"] >= 2020].groupby("year").agg(families=("proj_id", "size"), top=("X", "sum"),
                                                   closed=("status", lambda s: (s == "closed").sum()),
                                                   missing=("status", lambda s: (s == "missing").sum()),
                                                   p0=("p0", "first"))
out.append("## Cohorts 2020–2025\n" + coh.to_markdown() + "\n")
out.append("## Primary result\n")
out.append(f"- Top-quintile observations: **{prim['n_top']}** from **{prim['n_amc']}** AMCs")
out.append(f"- Repeat rate P̂ = **{prim['P_hat']:.1%}** vs exact null P̂0 = {prim['P0']:.1%} (Δ = {prim['delta']:+.1%})")
out.append(f"- 95% CI for Δ (inverted WCR, 9,999 draws/grid point): [{lo:+.1%}, {hi:+.1%}] → "
           f"P in [{prim['P0']+lo:.1%}, {prim['P0']+hi:.1%}]")
out.append(f"- Wild cluster bootstrap-t (AMC, Webb, CR2): t = {prim['t']:.2f}, one-sided **p = {prim['p']:.4f}**")
out.append(f"- Decision (α = 0.05): **{'reject H0 — persistence' if prim['p'] < 0.05 else 'do not reject H0 — no evidence of persistence'}**\n")

# diagnostics
big = x["amc"].value_counts()
out.append("## Diagnostics\n")
out.append(f"- Share of top observations from the largest AMC ({big.index[0]}): {big.iloc[0]/len(x):.1%}")
loo = []
for a in x["amc"].unique():
    xa = x[x["amc"] != a]
    loo.append((a, (xa["Y"] - xa["p0"]).mean()))
loo = pd.DataFrame(loo, columns=["dropped_amc", "delta"]).sort_values("delta")
out.append(f"- Leave-one-AMC-out Δ: min {loo.delta.min():+.1%} (drop {loo.iloc[0].dropped_amc}), "
           f"max {loo.delta.max():+.1%} (drop {loo.iloc[-1].dropped_amc})")
by_year = x.groupby("year").apply(lambda g: pd.Series({"top": len(g), "repeat": g["Y"].mean(),
                                                       "p0": g["p0"].iloc[0]}))
out.append("\nBy year (descriptive, not a test):\n" + by_year.to_markdown(floatfmt=".3f") + "\n")

# transition matrix (pooled 2020-2025)
pp = pan[pan["year"] >= 2020].copy()
pp["rank_q"] = pp.groupby("year")["alpha_rank"].transform(lambda s: pd.qcut(s.rank(method="first"), 5, labels=[5, 4, 3, 2, 1]))
pp["eval_q"] = pp.groupby("year")["alpha_eval"].transform(
    lambda s: pd.qcut(s.rank(method="first"), 5, labels=[5, 4, 3, 2, 1]) if s.notna().sum() >= 5 else np.nan)
pp["eval_q"] = pp["eval_q"].astype("object").map(lambda v: v if pd.isna(v) else f"Q{int(v)}")
pp["eval_q"] = pp["eval_q"].where(pp["status"] == "eval", pp["status"])
tm = pd.crosstab(pp["rank_q"].astype(int), pp["eval_q"], normalize="index")
out.append("## Transition matrix 2020–2025 (row = ranking quintile, 1 = top; share of row)\n" + tm.to_markdown(floatfmt=".2f") + "\n")

# secondary
sec = []
pe = pp[pp["Y"].notna()]
b1, t1, p1, G1 = wcr_fe_test(pe["Y"], pe["X"], pe["amc"] + "_" + pe["year"].astype(str), pe["amc"], draws=19_999)
tb = pp[(pp["rank_q"].astype(int).isin([1, 5])) & pp["alpha_eval"].notna()].copy()
tb["top"] = (tb["rank_q"].astype(int) == 1).astype(int)
b2, t2, p2, G2 = wcr_fe_test(tb["alpha_eval"] * 12, tb["top"], tb["year"].astype(str), tb["amc"], draws=19_999)
adj = holm(np.array([p1, p2]))
out.append("## Secondary (Holm-adjusted, 19,999 draws)\n")
out.append(f"- Within-AMC: β = {b1:+.3f} (top vs sibling families, same AMC-year), p = {p1:.4f}, Holm p = {adj[0]:.4f}, AMCs = {G1}")
out.append(f"- Top − bottom quintile evaluation alpha: {b2:+.2%}/yr, p = {p2:.4f}, Holm p = {adj[1]:.4f}, AMCs = {G2}\n")

# sensitivity
out.append("## Sensitivity (primary statistic; 19,999 draws)\n")
rows = []


def sens(label, pan_s, **kw):
    s = primary_stats(pan_s, draws=19_999, **kw)
    rows.append(dict(variant=label, n_top=s["n_top"], P_hat=f"{s['P_hat']:.1%}", P0=f"{s['P0']:.1%}",
                     delta=f"{s['delta']:+.1%}", p=f"{s['p']:.4f}"))


sens("primary", pan)
sens("gray pairs merged", panel_for("family_gray_merged"))
tn = meta.index[meta["name"] == "T-NSET"]
sens("T-NSET excluded", panel_for(md=meta.drop(tn)))
r_noflag = ret.mask(flag_month > 0)
sens("flagged NAV-only months removed", panel_for(r=r_noflag))
sens("missing evaluation counted as Y=0", pan, missing_as_zero=True)
adjf = pd.read_csv(P / "fundyear_adjustments.csv")
payers = set(adjf.loc[adjf["status"].isin(["adjusted"]) & (adjf["year"] >= 2017), "proj_id"])
pol = pd.read_csv(P / "fund_div_policy.csv").set_index("proj_id")["pattern"]
payers |= set(pol[pol.str.contains("Y", na=False)].index)
sens("no-payout sub-sample", panel_for(md=meta.drop([p for p in meta.index if p in payers])))
sens("family TE<0.06%", panel_for("family_te006"))
sens("family TE<0.15%", panel_for("family_te015"))
out.append(pd.DataFrame(rows).to_markdown(index=False) + "\n")
out.append("Not yet run: payout-timing variants (need alternative series from build_series.py).\n")

# exploratory 2017-2019
ex = primary_stats(pan, years=range(2017, 2020), draws=9_999)
out.append("## Exploratory: evaluation years 2017–2019 (ranking on 2014–2016 NAV-only data — not pooled)\n")
out.append(f"- P̂ = {ex['P_hat']:.1%} vs P̂0 = {ex['P0']:.1%}, n_top = {ex['n_top']}, p = {ex['p']:.4f}\n")

(ROOT / "reports/g3_results.md").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
