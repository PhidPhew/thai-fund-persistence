# Skill or Exposure? Decomposing Alpha in Thai Active Equity Funds

**Question:** Do top Thai active equity funds win because of persistent manager skill, or just market/factor exposure?

**Status:** G5 — write-up (G3: persistence under CAPM, p = 0.025; G4: thin, non-significant edge)

| Gate | Status |
|---|---|
| G0 Question (preregistration.md) | ✅ locked 2026-10-12 |
| G1 Data feasibility | ✅ done |
| G2 Clean dataset | ✅ closed 2026-10-14 |
| G3 Analysis | ✅ primary + sensitivity done (reports/g3_results.md) |
| G4 Investability | ✅ done (reports/g4_investability.md) |
| G5 Write-up | next |

## Setup
```bash
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then paste your SEC API key
python src/sec_probe.py
```

Data source: SEC Open API — Fund API v2 (api.sec.or.th).
