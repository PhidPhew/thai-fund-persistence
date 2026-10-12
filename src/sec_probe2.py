"""
Probe 2 — closes the open G1 questions left by sec_probe.py:
  A) Does NAV go back before 2000? (probe 1 asked from 2000-01-01, so 2000 may be our floor, not SEC's)
  B) Do funds that died BEFORE 2018 (management_style empty) still return NAV?
  C) Does dividend history exist, and how far back? (probe 1 got 0 rows for a fund that may simply not pay)
  D) How far back do factsheet benchmarks go across ALL funds? (probe 1 saw only 2022-06 onward)

Run from project root:  python src/sec_probe2.py
Needs data/raw/probe_profiles.csv from probe 1.
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
KEY = os.environ.get("SEC_API_KEY")
if not KEY:
    sys.exit("SEC_API_KEY missing in .env")

BASE = "https://api.sec.or.th"
S = requests.Session()
S.headers.update({"Ocp-Apim-Subscription-Key": KEY, "Accept": "application/json"})


def get_all(path, max_pages=10_000, **params):
    items, cursor, pages = [], "", 0
    while pages < max_pages:
        p = {"page_size": 100, **params}
        if cursor:
            p["next_cursor"] = cursor
        r = S.get(BASE + path, params=p, timeout=60)
        if r.status_code == 421:
            wait = int(r.headers.get("Retry-After", 5))
            print(f"  rate limited, waiting {wait}s", flush=True)
            time.sleep(wait)
            continue
        if r.status_code == 204:
            break
        r.raise_for_status()
        body = r.json()
        items += body.get("items", [])
        cursor = body.get("next_cursor")
        pages += 1
        if pages % 10 == 0:
            print(f"  {path}: page {pages}, {len(items)} rows", flush=True)
        time.sleep(0.07)
        if not cursor:
            break
    return items


def nav_span(proj_id, start="1980-01-01"):
    rows = get_all("/v2/fund/daily-info/nav", proj_id=proj_id,
                   start_nav_date=start, end_nav_date="2026-12-31")
    if not rows:
        return None
    d = pd.DataFrame(rows)
    d["nav_date"] = pd.to_datetime(d["nav_date"])
    return f"{len(d)} rows, {d['nav_date'].min().date()} -> {d['nav_date'].max().date()}, classes={sorted(d['fund_class_name'].dropna().unique())}"


prof = pd.read_csv(ROOT / "data/raw/probe_profiles.csv", encoding="utf-8-sig", low_memory=False)
funds = prof.drop_duplicates("proj_id")
eq = funds[funds["policy_desc"].fillna("").str.strip() == "ตราสารทุน"]

print("\n=== A) NAV before 2000? (start=1980) ===")
for pid in ["M0027_2535", "M0004_2535"]:
    print(pid, "->", nav_span(pid), flush=True)

print("\n=== B) Funds dead BEFORE 2018 (management_style empty) ===")
old_dead = eq[eq["management_style"].isna() & eq["fund_status"].isin(["Liquidated", "Expired"])]
print("count:", len(old_dead))
for _, r in old_dead.sample(min(6, len(old_dead)), random_state=0).iterrows():
    print(r["proj_id"], r["proj_abbr_name"], r["fund_status"], "cancel=", r["cancel_date"],
          "->", nav_span(r["proj_id"]), flush=True)

print("\n=== C) Dividend history, whole market, by year ===")
for y in [2005, 2010, 2015, 2020, 2025]:
    rows = get_all("/v2/fund/daily-info/dividend-history", max_pages=3,
                   start_dividend_date=f"{y}-01-01", end_dividend_date=f"{y}-12-31")
    print(y, "-> rows in first 3 pages:", len(rows), flush=True)
    if rows and y == 2015:
        print(pd.DataFrame(rows).head(5).to_string())

print("\n=== D) Earliest benchmark records, whole market ===")
for y in [2010, 2015, 2018, 2020, 2021, 2022]:
    rows = get_all("/v2/fund/factsheet/benchmarks", max_pages=1,
                   start_date=f"{y}-01-01", end_date=f"{y}-12-31")
    print(y, "-> rows (first page):", len(rows), flush=True)
