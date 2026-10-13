"""
G2 — who pays dividends? NAV alone cannot tell (see reports: payer scan), so ask the SEC factsheet.

Fetches, for every universe fund (include == y):
  /v2/fund/factsheet/dividend-policy   -> stated dividend policy per class (factsheets exist from 2022-06)
  /v2/fund/factsheet/performance       -> fund-reported returns, used later to validate our total-return series
Funds that closed before 2022-06 have no factsheet here; they are handled separately.

Out: data/raw/factsheet/dividend_policy.csv, data/raw/factsheet/performance.csv
Run: python src/fetch_div_policy.py      (~270 funds x 2 endpoints, a few minutes)
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
OUT = ROOT / "data/raw/factsheet"
OUT.mkdir(parents=True, exist_ok=True)
S = requests.Session()
S.headers.update({"Ocp-Apim-Subscription-Key": KEY, "Accept": "application/json"})


def get_all(path, **params):
    items, cursor = [], ""
    while True:
        p = {"page_size": 100, **params}
        if cursor:
            p["next_cursor"] = cursor
        try:
            r = S.get("https://api.sec.or.th" + path, params=p, timeout=60)
        except requests.RequestException:
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
        if r.status_code >= 400:
            print(f"   {path} {params.get('proj_id')}: HTTP {r.status_code} {r.text[:120]}")
            break
        b = r.json()
        items += b.get("items", [])
        cursor = b.get("next_cursor")
        time.sleep(0.07)
        if not cursor:
            break
    return items


rev = pd.read_csv(ROOT / "config/universe_review.csv", encoding="utf-8-sig")
ids = rev.loc[rev["include"] == "y", "proj_id"].tolist()
pol, perf = [], []
for i, pid in enumerate(ids, 1):
    pol += get_all("/v2/fund/factsheet/dividend-policy", proj_id=pid)
    perf += get_all("/v2/fund/factsheet/performance", proj_id=pid)
    if i % 20 == 0:
        print(f"[{i}/{len(ids)}] policy rows {len(pol)}, performance rows {len(perf)}", flush=True)

pd.DataFrame(pol).to_csv(OUT / "dividend_policy.csv", index=False)
pd.DataFrame(perf).to_csv(OUT / "performance.csv", index=False)
p = pd.DataFrame(pol)
print("\nfunds with a stated dividend policy:", p["proj_id"].nunique() if len(p) else 0, "of", len(ids))
if len(p):
    print(p.drop_duplicates(["proj_id", "fund_class_name", "dividend_policy"])["dividend_policy"].value_counts().head(10))
