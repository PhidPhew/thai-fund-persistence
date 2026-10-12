"""
Probe 5 — can a SET index fund's NAV stand in for SET TRI before 2021?

Idea: SCB SET Index Fund (M0026_2539, since 1996) tracks the SET. If its NAV is
accumulating (no payouts), NAV ~ SET TRI minus fees. We have the real SET TRI
for 2021-10 → 2026-10 (data/raw/set_tri_daily_set_website.csv), so we can
measure how close the proxy is on that overlap before trusting it further back.

Also checks two SET50 index funds against SET50 TRI as a cross-check.

Run from project root:  python src/sec_probe5.py
Saves NAV to data/raw/nav_<proj_id>.csv
"""
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
KEY = os.environ.get("SEC_API_KEY") or sys.exit("SEC_API_KEY missing in .env")
S = requests.Session()
S.headers.update({"Ocp-Apim-Subscription-Key": KEY, "Accept": "application/json"})


def nav(proj_id):
    items, cursor = [], ""
    while True:
        p = {"page_size": 100, "proj_id": proj_id,
             "start_nav_date": "1990-01-01", "end_nav_date": "2026-12-31"}
        if cursor:
            p["next_cursor"] = cursor
        r = S.get("https://api.sec.or.th/v2/fund/daily-info/nav", params=p, timeout=60)
        if r.status_code == 421:
            time.sleep(int(r.headers.get("Retry-After", 5)))
            continue
        if r.status_code == 204:
            break
        r.raise_for_status()
        b = r.json()
        items += b.get("items", [])
        cursor = b.get("next_cursor")
        time.sleep(0.07)
        if not cursor:
            break
    d = pd.DataFrame(items)
    d["nav_date"] = pd.to_datetime(d["nav_date"])
    d.to_csv(ROOT / f"data/raw/nav_{proj_id}.csv", index=False)
    return d


tri = pd.read_csv(ROOT / "data/raw/set_tri_daily_set_website.csv", parse_dates=["Date"]).set_index("Date")

cases = [("M0026_2539", "SCBSETFUND", "SET TRI"),
         ("M0041_2543", "ES-SET50", "SET50 TRI"),
         ("M0209_2548", "K-SET50", "SET50 TRI")]

for pid, name, idx in cases:
    print(f"\n=== {name} ({pid}) vs {idx} ===", flush=True)
    d = nav(pid)
    print("classes:", sorted(d["fund_class_name"].dropna().unique()),
          "| NAV from", d["nav_date"].min().date(), "to", d["nav_date"].max().date(), "|", len(d), "rows")
    for cls, g in d.groupby("fund_class_name"):
        s = g.set_index("nav_date")["last_val"].astype(float).sort_index()
        both = pd.concat([s.rename("fund"), pd.to_numeric(tri[idx], errors="coerce").rename("index")],
                         axis=1, join="inner").dropna()
        if len(both) < 200:
            print(f"  [{cls}] overlap too short ({len(both)} days)")
            continue
        r = np.log(both).diff().dropna()
        years = (both.index[-1] - both.index[0]).days / 365.25
        gap = (r["fund"].sum() - r["index"].sum()) / years
        resid = r["fund"] - r["index"]
        big = resid[resid < -0.01]
        print(f"  [{cls}] overlap {both.index[0].date()}→{both.index[-1].date()} ({years:.1f}y)")
        print(f"     annual return gap fund − index: {gap:+.2%}  (≈ −fees if accumulating; ≈ −(fees+div yield) if paying out)")
        print(f"     daily tracking error: {resid.std():.4%} | corr: {r.corr().iloc[0,1]:.4f}")
        print(f"     days fund lagged index by >1%: {len(big)}  -> likely payout dates:",
              [f'{i.date()} {v:+.2%}' for i, v in big.sort_values().head(8).items()])
