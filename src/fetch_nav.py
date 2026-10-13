"""
G2 step 2 — download daily NAV (all share classes, full history) for every fund in
config/universe_review.csv whose include is not 'n'. Also fetches the benchmark SCBSET
and the two SET50 index funds used to check SCBSET before 2021.

Resumable: funds already saved in data/raw/nav/ are skipped, so you can stop (Ctrl+C) and rerun.
Run: python src/fetch_nav.py      (~300 funds; expect 15–30 minutes)
"""
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
KEY = os.environ.get("SEC_API_KEY") or sys.exit("SEC_API_KEY missing in .env")
OUT = ROOT / "data/raw/nav"
OUT.mkdir(parents=True, exist_ok=True)

S = requests.Session()
S.headers.update({"Ocp-Apim-Subscription-Key": KEY, "Accept": "application/json"})
BENCH = ["M0026_2539", "M0041_2543", "M0209_2548"]  # SCBSETFUND, ES-SET50, K-SET50


def nav(proj_id):
    items, cursor = [], ""
    while True:
        p = {"page_size": 100, "proj_id": proj_id,
             "start_nav_date": "1990-01-01", "end_nav_date": "2026-12-31"}
        if cursor:
            p["next_cursor"] = cursor
        try:
            r = S.get("https://api.sec.or.th/v2/fund/daily-info/nav", params=p, timeout=60)
        except requests.RequestException as e:
            print(f"   network error ({e.__class__.__name__}), retrying in 10s", flush=True)
            time.sleep(10)
            continue
        if r.status_code == 421:
            time.sleep(int(r.headers.get("Retry-After", 5)))
            continue
        if r.status_code in (500, 502, 503, 504):
            time.sleep(5)
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
    return pd.DataFrame(items)


rev = pd.read_csv(ROOT / "config/universe_review.csv", encoding="utf-8-sig")
ids = BENCH + rev.loc[rev["include"].astype(str) != "n", "proj_id"].tolist()
ids = list(dict.fromkeys(ids))
todo = [i for i in ids if not (OUT / f"{i}.csv").exists()]
print(f"{len(ids)} funds, {len(ids) - len(todo)} already saved, {len(todo)} to fetch", flush=True)

empty = []
for n, pid in enumerate(todo, 1):
    d = nav(pid)
    if d.empty:
        empty.append(pid)
        pd.DataFrame(columns=["proj_id", "nav_date", "fund_class_name", "last_val"]).to_csv(OUT / f"{pid}.csv", index=False)
    else:
        d.to_csv(OUT / f"{pid}.csv", index=False)
    print(f"[{n}/{len(todo)}] {pid}: {len(d)} rows", flush=True)

print("\ndone. funds with NO NAV at all:", len(empty), empty)
