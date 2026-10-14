"""
G3 — persistence panel + inference (preregistration Amendment 7).

build_panel(...)  : one row per (ranking year, family representative) with ranking/evaluation alphas,
                    X (top quintile at ranking), Y (top quintile in evaluation; closures = 0), p0 (exact null)
wcr_mean_test(...) : restricted wild cluster bootstrap-t for an intercept (Δ), CR2, Webb weights,
                    one weight per cluster for all rows of that cluster (i.e. all years)
wcr_fe_test(...)  : restricted WCR for a slope with fixed effects (secondary tests), CR1
"""
import numpy as np
import pandas as pd

WEBB = np.array([-np.sqrt(1.5), -1.0, -np.sqrt(0.5), np.sqrt(0.5), 1.0, np.sqrt(1.5)])


def k_top(n):
    return int(np.floor(0.2 * n + 0.5))


def ols_alpha(y, x):
    X = np.column_stack([np.ones(len(x)), x])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return coef[0]


def build_panel(ret, bench, meta, family_col, years, rep_priority=None, min_eval=9):
    """
    ret   : DataFrame index = month (Period[M]), columns = proj_id, monthly total returns (NaN = missing)
    bench : Series index = month, SCBSET monthly return
    meta  : DataFrame index = proj_id with columns: amc, closed_date (Timestamp or NaT), is_wrapper, regis_date,
            family columns, flagged (DataFrame-like set of (proj_id, year) flagged) optional
    returns panel DataFrame
    """
    rows = []
    for Y in years:
        rk = pd.period_range(f"{Y-3}-01", f"{Y-1}-12", freq="M")
        ev = pd.period_range(f"{Y}-01", f"{Y}-12", freq="M")
        start = pd.Timestamp(f"{Y}-01-01")
        win = ret.reindex(rk)
        alive = meta["closed_date"].isna() | (meta["closed_date"] >= start)
        ok = win.notna().all() & alive.reindex(win.columns).fillna(False)
        cands = [p for p in win.columns[ok]]
        if not cands:
            continue
        # family representative (only information up to Dec Y-1)
        hist = ret.loc[:f"{Y-1}-12"].notna().sum()
        cdf = meta.loc[cands, ["amc", family_col, "is_wrapper", "regis_date"]].copy()
        cdf["hist"] = hist.reindex(cands).values
        cdf["nflag"] = 0 if rep_priority is None else rep_priority(cands, Y)
        cdf["regis"] = pd.to_datetime(cdf["regis_date"]).fillna(pd.Timestamp("2100-01-01"))
        cdf = cdf.sort_values(["is_wrapper", "hist", "nflag", "regis"], ascending=[True, False, True, True])
        cdf = cdf.assign(pid=cdf.index).sort_values(["is_wrapper", "hist", "nflag", "regis", "pid"],
                                                    ascending=[True, False, True, True, True])
        reps = cdf.groupby(family_col, sort=False).head(1).index.tolist()
        b_rk = bench.reindex(rk).values
        a_rank = pd.Series({p: ols_alpha(win[p].values, b_rk) for p in reps})
        n = len(a_rank)
        top = set(a_rank.sort_values(ascending=False, kind="mergesort").index[:k_top(n)])
        # evaluation
        end = pd.Timestamp(f"{Y}-12-31")
        evw = ret.reindex(ev)
        b_ev = bench.reindex(ev)
        a_eval, status = {}, {}
        for p in reps:
            cd = meta.at[p, "closed_date"]
            if pd.notna(cd) and start <= cd <= end:
                status[p] = "closed"
                continue
            s = evw[p]
            m = s.notna() & b_ev.notna()
            if m.sum() >= min_eval:
                a_eval[p] = ols_alpha(s[m].values, b_ev[m].values)
                status[p] = "eval"
            else:
                status[p] = "missing"
        ae = pd.Series(a_eval, dtype=float)
        m_ev = len(ae)
        etop = set(ae.sort_values(ascending=False, kind="mergesort").index[:k_top(m_ev)]) if m_ev else set()
        n_closed = sum(1 for v in status.values() if v == "closed")
        N = m_ev + n_closed
        p0 = k_top(m_ev) / N if N else np.nan
        for p in reps:
            rows.append(dict(year=Y, proj_id=p, amc=meta.at[p, "amc"], family=meta.at[p, family_col],
                             alpha_rank=a_rank[p], X=int(p in top), status=status[p],
                             alpha_eval=a_eval.get(p, np.nan),
                             Y=(int(p in etop) if status[p] == "eval" else (0 if status[p] == "closed" else np.nan)),
                             p0=p0, n_rank=n, N_eval=N))
    return pd.DataFrame(rows)


def _cr2_se_mean(D, g_codes, n_g):
    n = len(D)
    e = D - D.mean()
    S = np.bincount(g_codes, weights=e, minlength=len(n_g))
    return np.sqrt(np.sum(S ** 2 / (1 - n_g / n))) / n


def wcr_mean_test(D, clusters, null=0.0, draws=99_999, seed=20261014, alternative="greater", return_t=False):
    D = np.asarray(D, float)
    codes, uniq = pd.factorize(pd.Series(clusters))
    n_g = np.bincount(codes).astype(float)
    if np.any(n_g / len(D) >= 1):
        return np.nan, np.nan, np.nan
    est = D.mean()
    t_obs = (est - null) / _cr2_se_mean(D, codes, n_g)
    rng = np.random.default_rng(seed)
    u = D - null                                   # restricted residuals (null imposed)
    W = rng.choice(WEBB, size=(draws, len(n_g)))
    Dstar = null + W[:, codes] * u                 # draws x n
    n = len(D)
    est_s = Dstar.mean(axis=1)
    e_s = Dstar - est_s[:, None]
    S = np.zeros((draws, len(n_g)))
    for gi in range(len(n_g)):
        S[:, gi] = e_s[:, codes == gi].sum(axis=1)
    se_s = np.sqrt((S ** 2 / (1 - n_g / n)).sum(axis=1)) / n
    t_s = (est_s - null) / se_s
    if alternative == "greater":
        p = (1 + np.sum(t_s >= t_obs)) / (draws + 1)
    else:
        p = (1 + np.sum(np.abs(t_s) >= abs(t_obs))) / (draws + 1)
    return (est, t_obs, p) if not return_t else (est, t_obs, p, t_s)


def wcr_ci(D, clusters, level=0.95, draws=9_999, seed=20261014, grid=None):
    """95% CI for the mean of D by inverting the two-sided restricted WCR test."""
    D = np.asarray(D, float)
    if grid is None:
        grid = np.linspace(D.mean() - 0.5, D.mean() + 0.5, 201)
    acc = [g for g in grid if wcr_mean_test(D, clusters, null=g, draws=draws, seed=seed,
                                             alternative="two-sided")[2] > 1 - level]
    return (min(acc), max(acc)) if acc else (np.nan, np.nan)


def wcr_fe_test(y, x, fe, clusters, draws=99_999, seed=20261014):
    """Slope of y on x with fixed effects `fe`; restricted WCR by `clusters` (CR1). One-sided (beta > 0)."""
    df = pd.DataFrame({"y": y, "x": x, "fe": fe, "g": clusters}).dropna()
    yd = df["y"] - df.groupby("fe")["y"].transform("mean")
    xd = df["x"] - df.groupby("fe")["x"].transform("mean")
    keep = xd.abs() > 1e-12
    # keep only FE cells with variation in x
    cell_var = df.assign(xd=xd).groupby("fe")["xd"].transform(lambda s: (s.abs() > 1e-12).any())
    df, yd, xd = df[cell_var], yd[cell_var].values, xd[cell_var].values
    codes, uniq = pd.factorize(df["g"])
    G, n = len(uniq), len(df)
    sxx = (xd ** 2).sum()

    def beta_se(yv):
        b = (xd * yv).sum() / sxx
        e = yv - b * xd
        S = np.bincount(codes, weights=xd * e, minlength=G)
        V = (S ** 2).sum() / sxx ** 2 * (G / (G - 1)) * ((n - 1) / (n - 2))
        return b, np.sqrt(V)

    b, se = beta_se(yd)
    t_obs = b / se
    rng = np.random.default_rng(seed)
    u = yd                                          # restricted residuals (beta = 0, FE already removed)
    W = rng.choice(WEBB, size=(draws, G))
    ts = np.empty(draws)
    for k in range(draws):
        bs, ses = beta_se(W[k, codes] * u)
        ts[k] = bs / ses
    p = (1 + np.sum(ts >= t_obs)) / (draws + 1)
    return b, t_obs, p, G


def holm(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    adj = np.empty(m)
    run = 0
    for i, k in enumerate(order):
        run = max(run, min(1, (m - i) * pvals[k]))
        adj[k] = run
    return adj
