# Independent review — strategy families (OpenAI Codex, read-only, 2026-10-14)

*Summary of the review (full text in the project chat).* Codex read `preregistration.md`,
`reports/g2_series_summary.md` and `data/processed/tmp/pairs.csv`; it did not compute any persistence result.

**Codex recommended**
- Drop names as the rule; same-AMC daily-return TE with overlap ≥ 252 obs / 12 months.
- Core TE < 0.08% + corr ≥ 0.995; gray 0.08–0.12%; ≥ 0.12% separate; split-half stability check
  (e.g. TMSRMF/TMSFOCUS: 0.126% first half vs 0.012% second half).
- **Complete-linkage instead of single-linkage** — Claude's draft (224 clusters at 0.10%) used single-linkage and
  chained TLEQRMF with TLEQ-SELECT (TE 0.762%). Complete-linkage counts: 239 (0.08%), 229 (0.10%), 225 (0.12%).
- Representative chosen per ranking date from past information only, locked for the evaluation year.
- Amendment must say daily returns were used in designing the rule (only "before persistence results").
- Family de-duplication does not remove AMC-level dependence → AMC-clustered inference.
- Manual adjudication of the 21 gray pairs, ideally by two blind reviewers; default separate if unclear.

**Decision (author, with Claude):** adopted, except gray-pair hand adjudication was replaced by an automatic
bracket — gray separate in the primary analysis, merged in a sensitivity analysis — because no ground-truth
labels exist and hand judgment adds subjectivity and time. Codex's family counts were reproduced exactly by
`src/build_families.py`.
