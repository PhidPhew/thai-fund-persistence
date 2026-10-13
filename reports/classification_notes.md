# Classification notes — funds with missing metadata (G2, 2026-10-13)

For use in the memo's **Method / Limitations** section.

## Principle
Funds are classified by **mandate** (what the fund is set up to do), not by **behaviour** (how its returns look).
Excluding active funds because they hug the index would select the sample on an outcome-related variable and
remove closet indexers — which are themselves part of the "skill vs exposure" answer.
Return behaviour is used only to *infer* mandate when documents are missing.

## Why inference was needed
`management_style` and `invest_country_flag` are empty for funds that closed before ~2018. Filtering on those fields
silently drops dead funds (survivorship bias). Five long-lived Thanachart funds (NAV 1993–2017, all closed 2017-02-03)
had no policy text at all.

## Evidence used (vs SCBSET index fund; reference = K-EQUITY, a known Thai active equity fund)
| Fund | Monthly corr / R² | Beta | Alpha/yr | Decision |
|---|---|---|---|---|
| K-EQUITY (reference) | 0.92 / 0.85 | 0.87 | −2.6% | — |
| T-PISD | 0.94 / 0.88 | 0.84 | −2.4% | include |
| T-USD | 0.90 / 0.81 | 0.78 | −2.6% | include |
| T-USD2 | 0.92 / 0.84 | 0.77 | −1.9% | include |
| T-SPT | 0.92 / 0.85 | 0.83 | −1.6% | include |
| T-NSET | 0.97 / 0.94 | 0.90 | +2.2% | include, **flagged** |
| PHR (contrast: China fund) | daily 0.39 | 0.43 | — | exclude |

- **Country:** foreign-investing funds show far lower correlation with the Thai market (PHR: 0.39).
- **Active vs index:** index funds show beta ≈ 1 and alpha ≈ −fee (K-SET50: 1.03 / −0.2%, 2005–16).
- **T-NSET:** name suggests an index fund; behaviour does not (beta 0.90, alpha +1.5%/yr over 2005–16).
  Daily tracking error alone cannot separate it from an SET50 index fund (0.27–0.69% vs SET). Treated as active;
  **all results are also reported excluding T-NSET**. A prospectus, if found, would override this inference.

## Data-quality finding
T-SPT's low daily correlation (0.70 overall, 0.23 in 2007) came from a one-day NAV error
(2007-03-01 +70%, 2007-03-02 −69.5%), not from its strategy. → G2 adds a cleaning step for one-day spike-and-reverse
NAVs and stale (unchanged) NAVs **before** payout detection, otherwise such errors would be read as dividends.

## Stakes
These funds closed in Feb 2017: in the primary sample (2014+) they enter one ranking (Jan 2017) and count as "closed";
in the 2002+ robustness sample they contribute ~15 years each.
