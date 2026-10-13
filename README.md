# Skill or Exposure? Decomposing Alpha in Thai Active Equity Funds

**Question:** Do top Thai active equity funds win because of persistent manager skill, or just market/factor exposure?

**Status:** G2 — building clean dataset (Amendment 5: primary evaluation 2020–2025)

| Gate | Status |
|---|---|
| G0 Question (preregistration.md) | ✅ locked 2026-10-12 |
| G1 Data feasibility | ✅ done |
| G2 Clean dataset | series built; family definition pending |
| G3 Analysis | — |
| G4 Investability | — |
| G5 Write-up | — |

## Setup
```bash
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then paste your SEC API key
python src/sec_probe.py
```

Data source: SEC Open API — Fund API v2 (api.sec.or.th).
