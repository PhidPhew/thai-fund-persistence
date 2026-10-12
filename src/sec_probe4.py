"""
Probe 4 — is the dividend-history endpoint usable at all?
Probe 3: per-fund queries returned 0 rows even for dividend-class funds, and
start_/end_dividend_date were rejected as invalid. So the third-party docs are
wrong about this endpoint. Here we ask with NO filters and with alternative
parameter names, and print what actually comes back.

Run from project root:  python src/sec_probe4.py
"""
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
KEY = os.environ.get("SEC_API_KEY") or sys.exit("SEC_API_KEY missing in .env")
S = requests.Session()
S.headers.update({"Ocp-Apim-Subscription-Key": KEY, "Accept": "application/json"})
URL = "https://api.sec.or.th/v2/fund/daily-info/dividend-history"

tries = {
    "1 no filters": {},
    "2 start_date/end_date": {"start_date": "2024-01-01", "end_date": "2024-12-31"},
    "3 class_abbr_name=K-GROWTH-A(D)": {"class_abbr_name": "K-GROWTH-A(D)"},
    "4 fund_class_name=K-GROWTH-A(D)": {"fund_class_name": "K-GROWTH-A(D)"},
}
for name, params in tries.items():
    r = S.get(URL, params={"page_size": 100, **params}, timeout=60)
    print(f"\n=== {name} -> HTTP {r.status_code}")
    if r.status_code != 200:
        print(r.text[:300])
        continue
    body = r.json()
    items = body.get("items", [])
    print("items on first page:", len(items), "| has next page:", bool(body.get("next_cursor")))
    if items:
        dates = sorted(i.get("dividend_date") or "" for i in items)
        print("fields:", list(items[0].keys()))
        print("dividend_date range on this page:", dates[0], "->", dates[-1])
        print(json.dumps(items[:2], ensure_ascii=False, indent=1))
