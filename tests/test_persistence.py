"""
Synthetic checks for src/persistence.py — data with a KNOWN answer, before touching real results.
Run: python tests/test_persistence.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from persistence import build_panel, holm, k_top, wcr_fe_test, wcr_mean_test  # noqa: E402

AMC_SIZES = [27, 22, 18, 15, 13, 12, 11, 10, 9, 8, 7, 6, 5, 5, 4, 3, 3, 2, 1, 1]   # ~ real imbalance
MONTHS = pd.period_range("2016-01", "2025-12", freq="M")
YEARS = list(range(2020, 2026))


def simulate(skill_sd, seed, amc_sd=0.004, close_frac=0.0):
    rng = np.random.default_rng(seed)
    T = len(MONTHS)
    bench = pd.Series(rng.normal(0.006, 0.045, T), index=MONTHS)
    ids, amcs = [], []
    for a, s in enumerate(AMC_SIZES):
        for j in range(s):
            ids.append(f"F{a:02d}_{j:02d}")
            amcs.append(f"AMC{a:02d}")
    n = len(ids)
    skill = rng.normal(0, skill_sd, n)                                   # persistent fund alpha (monthly)
    year_alpha = rng.normal(0, 0.003, (len(set(MONTHS.year)), n))       # transient yearly alpha (luck)
    amc_code = pd.factorize(pd.Series(amcs))[0]
    amc_shock = rng.normal(0, amc_sd, (T, len(AMC_SIZES)))[:, amc_code]  # common within-AMC monthly shock
    yidx = (MONTHS.year - MONTHS.year.min()).values
    beta = rng.uniform(0.8, 1.05, n)
    R = (skill[None, :] + year_alpha[yidx, :] + beta[None, :] * bench.values[:, None]
         + amc_shock + rng.normal(0, 0.012, (T, n)))
    ret = pd.DataFrame(R, index=MONTHS, columns=ids)
    meta = pd.DataFrame({"amc": amcs, "family": ids, "is_wrapper": False, "regis_date": "2010-01-01",
                         "closed_date": pd.NaT}, index=ids)
    if close_frac:
        dead = rng.choice(ids, int(close_frac * n), replace=False)
        for d in dead:
            yr = rng.choice(YEARS)
            meta.at[d, "closed_date"] = pd.Timestamp(f"{yr}-06-30")
            ret.loc[pd.Period(f"{yr}-07", "M"):, d] = np.nan
    return build_panel(ret, bench, meta, "family", YEARS)


def primary(panel, draws=1999):
    x = panel[(panel["X"] == 1) & panel["Y"].notna()]
    return wcr_mean_test(x["Y"] - x["p0"], x["amc"], draws=draws)


fails = 0


def check(name, cond, detail=""):
    global fails
    print(("PASS " if cond else "FAIL ") + name + (f"  [{detail}]" if detail else ""))
    fails += (not cond)


# 1. helpers
check("k_top rounding", [k_top(n) for n in (10, 12, 13, 17, 18)] == [2, 2, 3, 3, 4])
check("holm", np.allclose(holm(np.array([0.01, 0.04])), [0.02, 0.04]))

# 2. strong persistence must be detected
pan = simulate(skill_sd=0.006, seed=1)
d, t, p = primary(pan)
P = pan.loc[pan.X == 1, "Y"].mean()
check("strong H1 detected (p < 0.05)", p < 0.05, f"P={P:.2f}, delta={d:+.3f}, p={p:.4f}")

# 3. under H0 the test must not over-reject (AMC shocks present, no skill)
rej = []
for s in range(40):
    _, _, p = primary(simulate(skill_sd=0.0, seed=100 + s), draws=999)
    rej.append(p < 0.05)
check("H0 rejection rate <= 10% over 40 runs", np.mean(rej) <= 0.10, f"rate={np.mean(rej):.3f}")

# 4. closures: counted as Y=0 and the exact null drops below 20%
pan = simulate(skill_sd=0.0, seed=7, close_frac=0.15)
closed = pan[pan.status == "closed"]
check("closed members get Y = 0", len(closed) > 0 and (closed["Y"] == 0).all(), f"{len(closed)} closed rows")
check("exact null p0 < 0.20 when closures exist", (pan.groupby("year")["p0"].first() < 0.2).any(),
      str(pan.groupby("year")["p0"].first().round(3).to_dict()))

# 5. representative: one row per family per year
check("one row per family-year", not pan.duplicated(["year", "family"]).any())

# 6. secondary within-AMC test runs and detects strong H1
pan = simulate(skill_sd=0.006, seed=3)
b, t, p, G = wcr_fe_test(pan["Y"], pan["X"], pan["amc"] + "_" + pan["year"].astype(str), pan["amc"], draws=999)
check("within-AMC secondary detects strong H1", p < 0.05, f"beta={b:+.3f}, p={p:.4f}, clusters={G}")

print("\nALL PASS" if fails == 0 else f"\n{fails} FAILED")
sys.exit(fails)
