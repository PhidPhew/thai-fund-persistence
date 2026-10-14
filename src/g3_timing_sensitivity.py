"""
G3 — payout-timing sensitivity (Amendment 5/7): move each fund-year's whole payout correction into one month
instead of spreading it over 12. Variants: January, December, month with the lowest fund-minus-SCBSET return.
Annual totals are unchanged; only within-year timing (and therefore alphas) changes.
Appends a table to reports/g3_results.md.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import run_g3 as g  # noqa: E402  (re-uses data loading; running it re-creates the main report first)

m = pd.read_csv(ROOT / "data/processed/monthly_returns.csv")
m["month"] = pd.PeriodIndex(m["month"], freq="M")
m["year"] = m["month"].dt.year
adj = m[m["flag"].isin(["adjusted", "adjusted_small_negative"])].copy()
adj["lc"] = np.log1p(adj["r_tr"]) - np.log1p(adj["r_nav"])
adj["excess"] = adj["r_nav"] - adj["month"].map(g.bench)
K = adj.groupby(["proj_id", "year"])["lc"].sum()


def variant(pick):
    v = g.ret.copy()
    for (pid, y), k in K.items():
        rows = adj[(adj["proj_id"] == pid) & (adj["year"] == y)]
        base = rows.set_index("month")["r_nav"]
        v.loc[base.index, pid] = base.values            # undo the even spreading
        mm = pick(rows)
        v.loc[mm, pid] = np.expm1(np.log1p(base[mm]) + k)
    return v


variants = {
    "payout all in January": lambda r: r["month"].min(),
    "payout all in December": lambda r: r["month"].max(),
    "payout in lowest-excess month": lambda r: r.loc[r["excess"].idxmin(), "month"],
}
rows = []
for name, pick in variants.items():
    s = g.primary_stats(g.panel_for(r=variant(pick)), draws=19_999)
    rows.append(dict(variant=name, n_top=s["n_top"], P_hat=f"{s['P_hat']:.1%}", P0=f"{s['P0']:.1%}",
                     delta=f"{s['delta']:+.1%}", p=f"{s['p']:.4f}"))
tab = pd.DataFrame(rows).to_markdown(index=False)
txt = (ROOT / "reports/g3_results.md").read_text(encoding="utf-8")
txt = txt.replace("Not yet run: payout-timing variants (need alternative series from build_series.py).\n",
                  "### Payout-timing variants (src/g3_timing_sensitivity.py; 19,999 draws)\n\n" + tab +
                  "\n\nNot run: YTD-derived monthly proxy (2023–2025).\n")
(ROOT / "reports/g3_results.md").write_text(txt, encoding="utf-8")
print(tab)
