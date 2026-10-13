"""
G2 — strategy families from return similarity (Amendment 6).

Pairs: funds of the same AMC with >= 252 overlapping daily returns spanning >= 12 months (2014+).
  TE = sample SD of the daily return difference (not annualised).
Core link (primary): TE < 0.08%  AND  corr >= 0.995  AND  TE < 0.12% in BOTH halves of the overlap.
Gray: TE < 0.12% but not core. Default: separate (primary); merged in a sensitivity variant.
Clustering: complete-linkage — two clusters merge only if EVERY cross pair has overlap and passes the link rule.
Variants (sensitivity): gray merged; TE-only thresholds 0.06%, 0.10%, 0.15%.
Representative choice per ranking date is done in the analysis step (G3), using only data known at that date.

Out: config/families.csv, config/family_pairs.csv (all pairs with TE < 0.15%, incl. the gray list)
Run: python src/build_families.py
"""
import hashlib
import itertools
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
NAV = ROOT / "data/processed/nav_clean"
START = pd.Timestamp("2014-01-01")

uni = pd.read_csv(ROOT / "config/universe_review.csv", encoding="utf-8-sig")
uni = uni[uni["include"] == "y"].set_index("proj_id")

R = {}
for pid in uni.index:
    n = pd.read_csv(NAV / f"{pid}.csv", parse_dates=["nav_date"])
    n = n[n["nav_date"] >= START]
    if n.empty:
        continue
    cls = n.groupby("fund_class_name").size().idxmax()
    s = n[n["fund_class_name"] == cls].set_index("nav_date")["last_val"].sort_index()
    R[pid] = np.log(s).diff().dropna()

rows = []
for amc, g in uni.groupby("comp_name_en"):
    ids = [p for p in g.index if p in R]
    for a, b in itertools.combinations(sorted(ids), 2):
        d = pd.concat([R[a], R[b]], axis=1, join="inner").dropna()
        if len(d) < 252 or (d.index[-1] - d.index[0]).days < 365:
            continue
        diff = d.iloc[:, 0] - d.iloc[:, 1]
        h = len(d) // 2
        rows.append(dict(a=a, b=b, a_name=uni.loc[a, "proj_abbr_name"], b_name=uni.loc[b, "proj_abbr_name"],
                         amc=amc, n=len(d), first=d.index[0].date(), last=d.index[-1].date(),
                         te=diff.std(), corr=d.corr().iloc[0, 1],
                         te_h1=diff.iloc[:h].std(), te_h2=diff.iloc[h:].std()))
pairs = pd.DataFrame(rows)
pairs["core"] = (pairs["te"] < 0.0008) & (pairs["corr"] >= 0.995) & (pairs[["te_h1", "te_h2"]].max(axis=1) < 0.0012)
pairs["gray"] = (pairs["te"] < 0.0012) & ~pairs["core"]
key = {(r.a, r.b): r for r in pairs.itertuples()}


def complete_linkage(link):
    """link: set of (a, b) pairs allowed to link. Greedy by TE, merge only if all cross pairs are links."""
    cl = {p: {p} for p in uni.index}
    for r in pairs[pairs.apply(lambda r: (r.a, r.b) in link, axis=1)].sort_values("te").itertuples():
        A, B = cl[r.a], cl[r.b]
        if A is B:
            continue
        if all(tuple(sorted((x, y))) in link for x in A for y in B):
            M = A | B
            for p in M:
                cl[p] = M
    return {p: min(s) for p, s in cl.items()}


def links(mask):
    return set(map(tuple, pairs.loc[mask, ["a", "b"]].itertuples(index=False, name=None)))


variants = {
    "family_primary": links(pairs["core"]),
    "family_gray_merged": links(pairs["core"] | pairs["gray"]),
    "family_te006": links(pairs["te"] < 0.0006),
    "family_te010": links(pairs["te"] < 0.0010),
    "family_te015": links(pairs["te"] < 0.0015),
}
fam = pd.DataFrame(index=uni.index)
for name, L in variants.items():
    fam[name] = pd.Series(complete_linkage(L))
fam["proj_abbr_name"] = uni["proj_abbr_name"]
fam["is_wrapper"] = uni["is_wrapper"]
fam["regis_date"] = uni["regis_date"]
fam["comp_name_en"] = uni["comp_name_en"]
fam.reset_index().to_csv(ROOT / "config/families.csv", index=False)

out = pairs[pairs["te"] < 0.0015].sort_values("te").copy()
for c in ["te", "te_h1", "te_h2"]:
    out[c] = (out[c] * 100).round(4)  # in percent
out = out.rename(columns={"te": "te_pct", "te_h1": "te_h1_pct", "te_h2": "te_h2_pct"})
out["corr"] = out["corr"].round(4)
out.to_csv(ROOT / "config/family_pairs.csv", index=False)

h = hashlib.sha256(pairs.round(10).to_csv(index=False).encode()).hexdigest()[:16]
print("pairs evaluated:", len(pairs), "| sha256[:16]:", h)
print("core links:", int(pairs["core"].sum()), "| gray pairs:", int(pairs["gray"].sum()))
for c in variants:
    print(f"{c:20s}: {fam[c].nunique()} families (from {len(fam)} funds)")
print("\ngray pairs:\n", out[out["gray"]][["a_name", "b_name", "n", "te_pct", "te_h1_pct", "te_h2_pct", "corr"]].to_string())
