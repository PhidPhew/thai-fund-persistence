"""
Probe 3 — the two questions probe 2 crashed before answering.
  C) Dividend history: whole-market date queries return HTTP 400, so query per fund.
     Tries funds whose class names end in (D) / dividend-paying classes, no date filter.
  D) How far back factsheet benchmarks go across the whole market.

Run from project root:  python src/sec_probe3.py
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

BASE = "https://api.sec.or.th"
S = requests.Session()
S.headers.update({"Ocp-Apim-Subscription-Key": KEY, "Accept": "application/json"})


def get(path, max_pages=50, **params):
    """Like get_all, but returns (items, error_text) instead of crashing on 4xx."""
    items, cursor, pages = [], "", 0
    while pages < max_pages:
        p = {"page_size": 100, **params}
        if cursor:
            p["next_cursor"] = cursor
        r = S.get(BASE + path, params=p, timeout=60)
        if r.status_code == 421:
            time.sleep(int(r.headers.get("Retry-After", 5)))
            continue
        if r.status_code == 204:
            break
        if r.status_code >= 400:
            return items, f"HTTP {r.status_code}: {r.text[:200]}"
        body = r.json()
        items += body.get("items", [])
        cursor = body.get("next_cursor")
        pages += 1
        time.sleep(0.07)
        if not cursor:
            break
    return items, None


print("\n=== C) Dividend history per fund ===")
prof = pd.read_csv(ROOT / "data/raw/probe_profiles.csv", encoding="utf-8-sig", low_memory=False)
eq = prof[prof["policy_desc"].fillna("").str.strip() == "ตราสารทุน"]
div_classes = eq[eq["fund_class_name"].fillna("").str.contains(r"\(D\)|-D$|DIV", regex=True)]
test_ids = ["M0254_2550"] + div_classes["proj_id"].drop_duplicates().head(4).tolist()
for pid in dict.fromkeys(test_ids):
    rows, err = get("/v2/fund/daily-info/dividend-history", proj_id=pid)
    if err:
        print(pid, "->", err)
        continue
    if not rows:
        print(pid, "-> 0 rows")
        continue
    d = pd.DataFrame(rows)
    dates = pd.to_datetime(d["dividend_date"], errors="coerce")
    print(pid, f"-> {len(d)} rows, {dates.min()} -> {dates.max()}, classes={sorted(d['class_abbr_name'].dropna().unique())}")
    print(d.head(3).to_string())

print("\n=== C2) Does the whole-market query work with a short window? ===")
rows, err = get("/v2/fund/daily-info/dividend-history", max_pages=1,
                start_dividend_date="2025-01-01", end_dividend_date="2025-01-31")
print("Jan 2025 ->", err or f"{len(rows)} rows on first page")

print("\n=== D) Factsheet benchmarks: earliest records, whole market ===")
for y in [2010, 2015, 2018, 2020, 2021, 2022]:
    rows, err = get("/v2/fund/factsheet/benchmarks", max_pages=1,
                    start_date=f"{y}-01-01", end_date=f"{y}-12-31")
    if err:
        print(y, "->", err)
    else:
        starts = sorted({r.get("start_date") for r in rows if r.get("start_date")})
        print(y, f"-> {len(rows)} rows on first page; earliest start_date seen: {starts[:1]}")
