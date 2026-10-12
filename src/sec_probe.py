"""
SEC API v2 feasibility probe for Project 2 (Thai Active Fund Alpha).
No analysis here: it only answers "what data exists and how far back".

Usage (from the project root):
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env      # paste your key after SEC_API_KEY=
    python src/sec_probe.py

Output: prints a summary and writes data/raw/probe_profiles.csv
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

BASE = "https://api.sec.or.th"
KEY = os.environ.get("SEC_API_KEY")
if not KEY:
    sys.exit("SEC_API_KEY missing: copy .env.example to .env and paste your key")

S = requests.Session()
S.headers.update({"Ocp-Apim-Subscription-Key": KEY, "Accept": "application/json"})


def get_all(path, max_pages=10_000, **params):
    """Follow next_cursor until done. Returns list of items."""
    items, cursor, pages = [], "", 0
    while pages < max_pages:
        p = {"page_size": 100, **params}
        if cursor:
            p["next_cursor"] = cursor
        r = S.get(BASE + path, params=p, timeout=60)
        if r.status_code == 421:  # rate limited
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
            print(f"  {path}: page {pages}, {len(items)} rows so far", flush=True)
        time.sleep(0.07)  # documented minimum gap is 60 ms
        if not cursor:
            break
    return items


# 1) All fund profiles, every status (survivorship check starts here)
print("Fetching all fund profiles (every status)...", flush=True)
prof =pd.DataFrame(get_all("/v2/fund/general-info/profiles"))
prof.to_csv(ROOT / "data/raw/probe_profiles.csv", index=False, encoding="utf-8-sig")
print("\n=== Profiles ===")
print("rows:", len(prof))
# SEC docs: profiles can return one row per share class, so rows != funds
print("unique funds (proj_id):", prof["proj_id"].nunique())
print("classes per fund:\n", prof.groupby("proj_id").size().value_counts().sort_index())
print(prof.drop_duplicates("proj_id")["fund_status"].value_counts(dropna=False))
print("\nmanagement_style:\n", prof["management_style"].value_counts(dropna=False))
print("\npolicy_desc (top 20):\n", prof["policy_desc"].value_counts().head(20))

# Candidate: active equity funds, any status
eq = prof[
    prof["policy_desc"].fillna("").str.contains("ตราสารทุน|Equity", case=False)
    & prof["management_style"].isin(["AM"])
].drop_duplicates("proj_id")
print("\nActive equity candidate funds (all statuses):", len(eq))
print(eq["fund_status"].value_counts())


def nav_span(proj_id):
    rows = get_all("/v2/fund/daily-info/nav", proj_id=proj_id,
                   start_nav_date="2000-01-01", end_nav_date="2026-12-31")
    if not rows:
        return None
    d = pd.DataFrame(rows)
    d["nav_date"] = pd.to_datetime(d["nav_date"])
    return {
        "proj_id": proj_id,
        "n_rows": len(d),
        "classes": sorted(d["fund_class_name"].dropna().unique().tolist()),
        "first": d["nav_date"].min().date(),
        "last": d["nav_date"].max().date(),
    }


# 2) History depth: oldest registered active equity funds
alive = eq[eq["fund_status"] == "Registered"].sort_values("regis_date").head(3)
print("\n=== NAV depth, oldest live funds ===")
for pid in alive["proj_id"]:
    print(nav_span(pid))

# 3) THE key test: do dead funds still return NAV?
dead = eq[eq["fund_status"].isin(["Canceled", "Liquidated"])].head(5)
print("\n=== NAV for dead funds (survivorship test) ===")
for _, r in dead.iterrows():
    print(r["proj_id"], r["fund_status"], "cancel_date=", r.get("cancel_date"),
          "->", nav_span(r["proj_id"]))

# 4) Benchmark history: is it point-in-time, how far back?
if len(alive):
    pid = alive["proj_id"].iloc[0]
    bm = pd.DataFrame(get_all("/v2/fund/factsheet/benchmarks", proj_id=pid))
    print(f"\n=== Benchmark history for {pid} ===")
    if len(bm):
        print(bm[["start_date", "end_date", "prospectus_type", "group_seq",
                  "benchmark"]].sort_values("start_date").to_string())

    # 5) Dividends
    dv = pd.DataFrame(get_all("/v2/fund/daily-info/dividend-history", proj_id=pid))
    print(f"\n=== Dividends for {pid} === rows:", len(dv))
    if len(dv):
        print(dv.head(10).to_string())
