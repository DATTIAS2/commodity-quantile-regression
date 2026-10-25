"""Consolidated CAC40 analysis, with explicit historical and corrected timing.

Historical returns are daily simple returns multiplied by 252. This unusual
scale is preserved for comparison; it is not daily percentage points.
"""
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.tools.sm_exceptions import IterationLimitWarning

QUANTILES = (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)
SPECS = {
    "full": (1, 2, 3, 4, 5),
    "report_reduced": (1, 2, 4),
    "notebook_reduced": (3, 5),
}

def load_snapshot(path):
    """Read the original derived Yahoo Finance snapshot without modifying it."""
    data = pd.read_csv(path, parse_dates=["Date"]).set_index("Date")
    required = {"r_GSCI", "r_GSCI_lag", "r_CAC40", "VIX"}
    if not required.issubset(data.columns):
        raise ValueError(f"Missing columns: {sorted(required - set(data.columns))}")
    if data.index.has_duplicates or not data.index.is_monotonic_increasing:
        raise ValueError("Dates must be unique and sorted")
    return data


def add_regimes(data, *, historical=False):
    """Overlapping regimes are intentional; boundary differences are explicit."""
    data = data.copy()
    dates = data.index
    data["D1"] = ((dates >= "2004-01-01") & (dates <= "2013-12-31")).astype(int)
    data["D2"] = ((dates > "2008-01-01") & (dates <= "2009-12-31")).astype(int) if historical else ((dates >= "2008-01-01") & (dates <= "2009-12-31")).astype(int)
    data["D3"] = ((dates > "2014-01-01") & (dates <= "2017-06-30")).astype(int) if historical else ((dates >= "2014-01-01") & (dates <= "2017-06-30")).astype(int)
    data["D4"] = ((dates > "2020-01-30") & (dates <= "2022-06-01")).astype(int) if historical else ((dates >= "2020-01-30") & (dates <= "2022-06-01")).astype(int)
    data["D5"] = (dates >= "2021-12-17").astype(int)
    for j in range(1, 6):
        data[f"gamma{j}"] = data["r_CAC40"] * data[f"D{j}"]
    return data


def prepare_snapshot(snapshot, *, mode="corrected"):
    """Corrected is an explanatory same-day model, not a trading forecast.

    At date t the snapshot stores t-to-t+1 returns. Move each series one row
    down to obtain returns ending at t. Build the true lag only afterward.
    Historical mode keeps the future-valued 'lag' to audit the old results,
    and drops 19 rows because the full original notebook did so for a rolling
    20-observation volatility plot before fitting its models.
    """
    if mode not in {"historical", "corrected"}:
        raise ValueError("mode must be historical or corrected")
    if mode == "historical":
        data = add_regimes(snapshot, historical=True).iloc[19:].copy()
    else:
        data = snapshot[["r_GSCI", "r_CAC40", "VIX"]].copy()
        for name in ["r_GSCI", "r_CAC40"]:
            data[name] = snapshot[name].shift(1)
        data["r_GSCI_lag"] = data["r_GSCI"].shift(1)
        data = add_regimes(data)
    cols = ["r_GSCI", "r_GSCI_lag", "r_CAC40", "VIX"] + [f"gamma{j}" for j in range(1, 6)]
    return data[cols].dropna()


def synthetic_sample(n=1200, seed=42):
    """Offline demonstration only: not observed market data or thesis evidence."""
    if n < 20:
        raise ValueError("n must be at least 20")
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2003-01-01", "2025-03-26")
    dates = dates[np.linspace(0, len(dates)-1, n, dtype=int)] if n <= len(dates) else pd.bdate_range("2003-01-01", periods=n)
    equity = rng.standard_t(6, n) * 2
    vix = np.maximum(8, 19 + 5 * rng.standard_normal(n))
    commodity = np.zeros(n)
    for t in range(1, n):
        commodity[t] = 0.08 * commodity[t-1] + 0.3 * equity[t] + rng.standard_t(5) * (1 + vix[t]/30)
    data = pd.DataFrame({"r_GSCI": commodity, "r_CAC40": equity, "VIX": vix}, index=dates)
    data["r_GSCI_lag"] = data["r_GSCI"].shift(1)
    return add_regimes(data).dropna()


def pseudo_r2(y, fitted, q):
    """Koenker-Machado check-loss improvement over an intercept-only fit."""
    if not 0 < q < 1:
        raise ValueError("q must be strictly between 0 and 1")
    y, fitted = np.asarray(y, dtype=float), np.asarray(fitted, dtype=float)
    if y.shape != fitted.shape:
        raise ValueError("y and fitted must have equal shape")
    def loss(residual):
        return np.sum(residual * (q - (residual < 0)))
    denominator = loss(y - np.quantile(y, q))
    return float(1 - loss(y - fitted) / denominator) if denominator else np.nan


def fit_models(data, specification="full", quantiles=QUANTILES):
    """Fit each quantile once; export coefficients, p-values and intervals.

    Default robust QuantReg covariance is a historical convention and does
    not address general serial dependence. No cross-quantile Wald tests are
    performed: the old notebooks ignored joint covariance between estimates.
    """
    interactions = SPECS[specification]
    terms = ["r_GSCI_lag", "r_CAC40", "VIX"] + [f"gamma{j}" for j in interactions]
    columns = ["r_GSCI"] + terms
    clean = data[columns].dropna()
    if not np.isfinite(clean.to_numpy()).all():
        raise ValueError("Model data must be finite")
    formula = "r_GSCI ~ " + " + ".join(terms)
    records, diagnostics = [], []
    model = smf.quantreg(formula, clean)
    for q in quantiles:
        if not 0 < q < 1:
            raise ValueError("Quantiles must lie strictly between 0 and 1")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            result = model.fit(q=q, max_iter=10000, p_tol=1e-6)
        ci = result.conf_int()
        for term in result.params.index:
            records.append({"quantile": q, "term": term, "coefficient": result.params[term], "p_value": result.pvalues[term], "ci_low": ci.loc[term, 0], "ci_high": ci.loc[term, 1]})
        diagnostics.append({"quantile": q, "nobs": int(result.nobs), "pseudo_r2": pseudo_r2(clean.r_GSCI, result.fittedvalues, q), "iterations": result.iterations, "iteration_limit": any(issubclass(w.category, IterationLimitWarning) for w in caught), "warnings": " | ".join(str(w.message) for w in caught)})
    ols = smf.ols(formula, clean).fit()
    x = ols.model.exog
    metadata = {"formula": formula, "nobs": len(clean), "start": str(clean.index.min().date()), "end": str(clean.index.max().date()), "rank": int(np.linalg.matrix_rank(x)), "columns": x.shape[1], "condition_number": float(np.linalg.cond(x))}
    return pd.DataFrame(records), pd.DataFrame(diagnostics), ols, metadata


def save_outputs(data, output, *, specification="full", label="Analysis"):
    import json
    import matplotlib.pyplot as plt
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    coefficients, diagnostics, ols, metadata = fit_models(data, specification)
    coefficients.to_csv(output / "quantile_coefficients.csv", index=False)
    diagnostics.to_csv(output / "fit_diagnostics.csv", index=False)
    ols.conf_int().rename(columns={0: "ci_low", 1: "ci_high"}).assign(coefficient=ols.params, p_value=ols.pvalues).to_csv(output / "ols_coefficients.csv")
    (output / "ols_summary.txt").write_text(ols.summary().as_text())
    (output / "run_metadata.json").write_text(json.dumps(dict(metadata, label=label), indent=2))
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.7), layout="constrained")
    for ax, term in zip(axes[:2], ["r_CAC40", "VIX"]):
        subset = coefficients.loc[coefficients.term == term]
        ax.plot(subset["quantile"], subset.coefficient, marker="o")
        ax.fill_between(subset["quantile"], subset.ci_low, subset.ci_high, alpha=0.2)
        ax.axhline(ols.params[term], color="grey", linestyle="--", label="OLS")
        ax.set(title=term, xlabel="Conditional quantile", ylabel="Coefficient (95% interval)")
        ax.legend()
    axes[2].plot(diagnostics["quantile"], diagnostics.pseudo_r2, marker="o")
    axes[2].set(title="In-sample fit", xlabel="Conditional quantile", ylabel="Pseudo R²")
    fig.suptitle(label)
    fig.savefig(output / "quantile_summary.png", dpi=180)
    plt.close(fig)
    return coefficients, diagnostics, metadata
