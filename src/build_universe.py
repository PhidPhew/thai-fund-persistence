"""
G2 step 1 — build the universe REVIEW file from the profile dump.

Output: config/universe_review.csv  (committed — this is our classification, the audit trail)
Hand decisions go in config/manual_overrides.csv (proj_id, include, reason, decided_by), never in the output.
One row per fund (proj_id). Columns you edit by hand:
  include   : y / n          (pre-filled suggestion; YOU confirm or change)
  family    : family key     (funds that are the same strategy in a different wrapper share one key)
  reason    : why excluded / note
Rules come from preregistration.md. Name-based flags are SUGGESTIONS only.

Run: python src/build_universe.py
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
p = pd.read_csv(ROOT / "data/raw/probe_profiles.csv", encoding="utf-8-sig", low_memory=False)

classes = (p.groupby("proj_id")["fund_class_name"]
             .apply(lambda s: " | ".join(sorted(s.dropna().astype(str).unique()))))
f = p.drop_duplicates("proj_id").set_index("proj_id")
f["classes"] = classes

eq = f[f["policy_desc"].fillna("").str.strip() == "ตราสารทุน"].copy()
styled = eq["management_style"].notna()

# Group A: fields populated -> rule-based
a = eq[styled & (eq["management_style"] == "AM") & (eq["invest_country_flag"] == 3)].copy()
a["group"] = "A_rule"
# Group B: fields empty (mostly died before 2018) -> needs hand review
b = eq[~styled].copy()
b["group"] = "B_manual"

u = pd.concat([a, b])
name = u["proj_abbr_name"].fillna("").str.upper() + " " + u["proj_name_en"].fillna("").str.upper()

SECTOR = r"BANK|FINANC|ENERGY|HEALTH|INFRA|PROPERTY|FOOD|ICT|TECH|COMM\b"
TRIGGER = r"TISEQT|TRIGGER|\d+P\d+|\dX\d|T\d+M\d|CHALLENGE|TARGET"
FOREIGN = (r"USA|US\b|USEQ|EURO|EUROPE|JAPAN|JP|CHINA|CH\b|ASIA|ASEAN|GLOBAL|GLOBE|INDIA|IN\b|INEQ|KOREA|KR\d|"
           r"TAIWAN|TW|MENA|EM\d|EMERGING|NA\d|S&P|SP500|NDQ|NASDAQ|CSI|HK\b|GERMAN|GER")
WRAPPER = r"RMF|SSF|LTF|THAIESG|THAI ESG|ESGX|TESGX|-M$"

sug, why = [], []
for i, r in u.iterrows():
    n = name.loc[i]
    if r["proj_retail_type"] not in ("R",) and r["group"] == "A_rule":
        sug.append("n"); why.append(f"non-retail ({r['proj_retail_type']})")
    elif re.search(TRIGGER, n):
        sug.append("n"); why.append("trigger / fixed-term (name)")
    elif r["group"] == "B_manual" and re.search(FOREIGN, n):
        sug.append("n"); why.append("foreign (name)")
    elif re.search(SECTOR, n):
        sug.append("?"); why.append("possible sector fund — check policy")
    elif r["group"] == "B_manual":
        sug.append("?"); why.append("no style/country field — check by hand")
    else:
        sug.append("y"); why.append("")
u["include"] = sug
u["reason"] = why


def family_key(abbr):
    k = str(abbr).upper()
    k = re.sub(r"[\s-]*(RMF|SSF|LTF|THAI ?ESGX?|TESGX|ESGX|MSSF|NONTAX|-M|-D)$", "", k)
    k = re.sub(r"[\s-]*(RMF|SSF|LTF)$", "", k)
    return k.strip(" -")


u["family"] = u["proj_abbr_name"].map(family_key)
u["is_wrapper"] = name.str.contains(WRAPPER, regex=True)

cols = ["group", "include", "reason", "family", "is_wrapper", "proj_abbr_name", "proj_name_en", "fund_status",
        "regis_date", "cancel_date", "comp_name_en", "proj_retail_type", "classes", "investment_policy_desc"]
out = u.reset_index()[["proj_id"] + cols].sort_values(["family", "regis_date"])

# Hand decisions live in config/manual_overrides.csv so re-running this script never erases them.
ov_path = ROOT / "config/manual_overrides.csv"
if ov_path.exists():
    ov = pd.read_csv(ov_path, encoding="utf-8-sig").set_index("proj_id")
    m = out["proj_id"].isin(ov.index)
    out.loc[m, "include"] = out.loc[m, "proj_id"].map(ov["include"])
    out.loc[m, "reason"] = out.loc[m, "proj_id"].map(ov["reason"])
    print(f"applied {m.sum()} manual overrides")
out["investment_policy_desc"] = out["investment_policy_desc"].fillna("").str.replace(r"\s+", " ", regex=True).str[:300]
out.to_csv(ROOT / "config/universe_review.csv", index=False, encoding="utf-8-sig")

print("funds in review file:", len(out))
print(out.groupby(["group", "include"]).size().to_string())
fam = out[out["include"] != "n"].groupby("family").size()
print("\nfamilies with >1 candidate fund (same strategy, different wrapper?):", (fam > 1).sum())
print(fam[fam > 1].sort_values(ascending=False).head(25).to_string())
