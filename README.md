# Skill or Exposure? Decomposing Alpha in Thai Active Equity Funds

**Question:** Do top Thai active equity funds win because of persistent manager skill, or just market/factor exposure?

**Status:** G3 — analysis (G2 closed; primary evaluation 2020–2025, 239 families)

| Gate | Status |
|---|---|
| G0 Question (preregistration.md) | ✅ locked 2026-10-12 |
| G1 Data feasibility | ✅ done |
| G2 Clean dataset | ✅ closed 2026-10-14 |
| G3 Analysis | next |
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
