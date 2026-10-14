"""
regression_helpers.py
---------------------
Shared functions used by both regression tasks (2.1 and 2.2), so the two
models are built, evaluated and plotted in exactly the same way.

  ols_summary()        fit OLS on the full data and report coefficients,
                       standard errors, t-values, p-values, R², adj-R², F-test
  vif_table()          variance inflation factors (multicollinearity check)
  backward_eliminate() drop the least significant variable one at a time
  evaluate_holdout()   80/20 train-test split -> R², RMSE, MAE vs a mean baseline
  evaluate_cv()        repeated 10-fold cross-validation (more stable with small n)
  plot_*()             figures used in the report

OLS inference is computed directly with NumPy/SciPy using the textbook formulas
  b = (XᵀX)⁻¹ Xᵀy ,  SE(b) = sqrt(diag(σ² (XᵀX)⁻¹)),  t = b / SE,  σ² = RSS / (n − k − 1)
so it runs with only numpy/pandas/scipy/scikit-learn/matplotlib installed.
(These are the same numbers statsmodels.OLS(...).fit().summary() prints;
src/optional_verify_with_statsmodels.py checks this if statsmodels is installed.)
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, RepeatedKFold, cross_validate
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

RANDOM_STATE = 42

# Colours (colour-blind-safe pair + neutral ink), used consistently in every figure
BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 200, "font.size": 9,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "axes.titlesize": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
})


# ---------------------------------------------------------------------------
# Inference
# ---------------------------------------------------------------------------
def ols_summary(X: pd.DataFrame, y: pd.Series):
    """Fit OLS with an intercept and return (coef_table, fit_stats)."""
    Xc = np.column_stack([np.ones(len(X)), X.to_numpy(dtype=float)])
    yv = y.to_numpy(dtype=float)
    n, p = Xc.shape                     # p = k + 1 (includes intercept)
    k = p - 1

    beta, *_ = np.linalg.lstsq(Xc, yv, rcond=None)
    fitted = Xc @ beta
    resid = yv - fitted
    rss = float(resid @ resid)
    tss = float(((yv - yv.mean()) ** 2).sum())
    sigma2 = rss / (n - p)

    cov = sigma2 * np.linalg.inv(Xc.T @ Xc)
    se = np.sqrt(np.diag(cov))
    t_vals = beta / se
    p_vals = 2 * stats.t.sf(np.abs(t_vals), df=n - p)
    t_crit = stats.t.ppf(0.975, df=n - p)

    # standardised coefficients: effect of a 1-SD change in x, in SDs of y
    std_beta = np.r_[np.nan, beta[1:] * X.std(ddof=1).to_numpy() / yv.std(ddof=1)]

    coef = pd.DataFrame({
        "coef": beta, "std_err": se, "t": t_vals, "p_value": p_vals,
        "ci_low": beta - t_crit * se, "ci_high": beta + t_crit * se,
        "std_coef": std_beta,
    }, index=["const"] + list(X.columns))

    r2 = 1 - rss / tss
    adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p)
    f_stat = ((tss - rss) / k) / (rss / (n - p))
    fit = {k: float(v) for k, v in {
        "n": n, "k": k, "R2": r2, "adj_R2": adj_r2,
        "F": f_stat, "F_p_value": stats.f.sf(f_stat, k, n - p),
        "RMSE_in_sample": np.sqrt(rss / n),
        "residual_std_error": np.sqrt(sigma2),
        "AIC": n * np.log(rss / n) + 2 * p,
    }.items()}
    fit["n"], fit["k"] = n, k
    return coef, fit, fitted, resid


def vif_table(X: pd.DataFrame) -> pd.Series:
    """VIF_j = 1 / (1 − R²_j), where R²_j regresses x_j on the other predictors."""
    out = {}
    for col in X.columns:
        others = X.drop(columns=col)
        r2 = LinearRegression().fit(others, X[col]).score(others, X[col])
        out[col] = np.inf if r2 >= 1 else 1 / (1 - r2)
    return pd.Series(out, name="VIF")


def backward_eliminate(X: pd.DataFrame, y: pd.Series, alpha=0.05):
    """Repeatedly drop the predictor with the largest p-value until all p < alpha.
    Returns the kept columns and a log of what was removed (for the report)."""
    cols, log = list(X.columns), []
    while len(cols) > 1:
        coef, fit, *_ = ols_summary(X[cols], y)
        pv = coef["p_value"].drop("const")
        worst = pv.idxmax()
        if pv[worst] < alpha:
            break
        log.append({"removed": worst, "p_value": pv[worst], "adj_R2_before": fit["adj_R2"]})
        cols.remove(worst)
    return cols, pd.DataFrame(log)


# ---------------------------------------------------------------------------
# Predictive evaluation
# ---------------------------------------------------------------------------
def _metrics(y_true, y_pred):
    return {"R2": r2_score(y_true, y_pred),
            "MSE": mean_squared_error(y_true, y_pred),
            "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
            "MAE": mean_absolute_error(y_true, y_pred),
            # Normalised RMSE = RMSE / (max - min of the actual values), as in the unit notes
            "NRMSE": np.sqrt(mean_squared_error(y_true, y_pred)) / (np.max(y_true) - np.min(y_true))}


def evaluate_holdout(X, y, test_size=0.2, stratify=None):
    """80/20 split. Reports train and test metrics for the model and for a
    naive baseline that always predicts the training-set mean."""
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=test_size, random_state=RANDOM_STATE, stratify=stratify)
    model = LinearRegression().fit(X_tr, y_tr)
    baseline = np.full(len(y_te), y_tr.mean())
    rows = {
        "Model (train)": _metrics(y_tr, model.predict(X_tr)),
        "Model (test)": _metrics(y_te, model.predict(X_te)),
        "Baseline mean (test)": _metrics(y_te, baseline),
    }
    return pd.DataFrame(rows).T, (y_te, model.predict(X_te))


def evaluate_cv(X, y, n_splits=10, n_repeats=20):
    """Repeated k-fold CV: every row is used for testing many times, which is
    more reliable than a single split when n is only 104 or 208."""
    cv = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=RANDOM_STATE)
    res = cross_validate(LinearRegression(), X, y, cv=cv,
                         scoring=("r2", "neg_root_mean_squared_error", "neg_mean_absolute_error"))
    # Baseline: predict the training-fold mean
    base_rmse, base_mae = [], []
    for tr, te in cv.split(X):
        pred = np.full(len(te), y.iloc[tr].mean())
        base_rmse.append(np.sqrt(mean_squared_error(y.iloc[te], pred)))
        base_mae.append(mean_absolute_error(y.iloc[te], pred))
    return pd.DataFrame({
        "mean": [res["test_r2"].mean(), -res["test_neg_root_mean_squared_error"].mean(),
                 -res["test_neg_mean_absolute_error"].mean(), np.mean(base_rmse), np.mean(base_mae)],
        "sd": [res["test_r2"].std(), res["test_neg_root_mean_squared_error"].std(),
               res["test_neg_mean_absolute_error"].std(), np.std(base_rmse), np.std(base_mae)],
    }, index=["CV R2", "CV RMSE", "CV MAE", "Baseline RMSE", "Baseline MAE"])


def evaluate_log_target(X, y, n_splits=10, n_repeats=20):
    """Model improvement attempt for a count target (goals):
    fit OLS on log(1 + y), then back-transform predictions with exp(.) - 1 so the
    errors are in GOALS and directly comparable with the untransformed model."""
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)
    m = LinearRegression().fit(X_tr, np.log1p(y_tr))
    hold = pd.DataFrame({
        "Model (train)": _metrics(y_tr, np.expm1(m.predict(X_tr))),
        "Model (test)": _metrics(y_te, np.expm1(m.predict(X_te))),
    }).T
    cv = RepeatedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=RANDOM_STATE)
    r2s, rmses, maes = [], [], []
    for tr, te in cv.split(X):
        m = LinearRegression().fit(X.iloc[tr], np.log1p(y.iloc[tr]))
        pred = np.expm1(m.predict(X.iloc[te]))
        r2s.append(r2_score(y.iloc[te], pred))
        rmses.append(np.sqrt(mean_squared_error(y.iloc[te], pred)))
        maes.append(mean_absolute_error(y.iloc[te], pred))
    cvres = pd.DataFrame({"mean": [np.mean(r2s), np.mean(rmses), np.mean(maes)],
                          "sd": [np.std(r2s), np.std(rmses), np.std(maes)]},
                         index=["CV R2", "CV RMSE", "CV MAE"])
    return hold, cvres


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
def plot_target_distribution(y, title, xlabel, path):
    fig, ax = plt.subplots(figsize=(4.2, 2.8))
    counts = y.value_counts().sort_index()
    ax.bar(counts.index, counts.values, color=BLUE, width=0.8, edgecolor="white", linewidth=1.5)
    ax.axvline(y.mean(), color=ORANGE, lw=2, ls="--", label=f"mean = {y.mean():.2f}")
    ax.set(title=title, xlabel=xlabel, ylabel="Number of rows")
    ax.legend(frameon=False)
    ax.grid(axis="x", visible=False)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def plot_correlation(df, title, path):
    corr = df.corr()
    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)), corr.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(corr)), corr.columns)
    for i in range(len(corr)):
        for j in range(len(corr)):
            v = corr.iloc[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7,
                    color="white" if abs(v) > 0.6 else INK)
    ax.grid(False)
    ax.set_title(title)
    fig.colorbar(im, ax=ax, shrink=0.8, label="Pearson r")
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def plot_coefficients(coef, title, path):
    """Standardised coefficients with 95% CI (scaled the same way), sorted by size."""
    c = coef.drop("const").copy()
    scale = c["std_coef"] / c["coef"]
    c["lo"], c["hi"] = c["ci_low"] * scale, c["ci_high"] * scale
    c = c.sort_values("std_coef")
    colors = [BLUE if p < 0.05 else "#9ec5f4" for p in c["p_value"]]
    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    y = np.arange(len(c))
    ax.hlines(y, c["lo"], c["hi"], color=MUTED, lw=1.2)
    ax.scatter(c["std_coef"], y, color=colors, s=40, zorder=3, edgecolor="white", linewidth=1)
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_yticks(y, c.index)
    ax.set(title=title, xlabel="Standardised coefficient (95% CI)")
    ax.grid(axis="y", visible=False)
    ax.text(0.99, 0.02, "dark = p < 0.05, light = n.s.", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=7, color=MUTED)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)


def plot_diagnostics(fitted, resid, y_test, y_pred, title, ylabel, path):
    """Three panels: residuals vs fitted, normal Q-Q, actual vs predicted (test set)."""
    fig, axes = plt.subplots(1, 3, figsize=(7.2, 2.5))
    ax = axes[0]
    ax.scatter(fitted, resid, s=12, color=BLUE, alpha=0.7, edgecolor="none")
    ax.axhline(0, color=ORANGE, lw=1.5)
    ax.set(title="Residuals vs fitted", xlabel="Fitted value", ylabel="Residual")

    ax = axes[1]
    (osm, osr), (slope, intercept, _) = stats.probplot(resid, dist="norm")
    ax.scatter(osm, osr, s=12, color=BLUE, alpha=0.7, edgecolor="none")
    ax.plot(osm, slope * np.asarray(osm) + intercept, color=ORANGE, lw=1.5)
    ax.set(title="Normal Q-Q of residuals", xlabel="Theoretical quantile", ylabel="Sample quantile")

    ax = axes[2]
    jitter = np.random.default_rng(0).uniform(-0.12, 0.12, len(y_test))
    ax.scatter(np.asarray(y_pred), np.asarray(y_test) + jitter, s=14, color=BLUE,
               alpha=0.75, edgecolor="none")
    lims = [min(np.min(y_pred), np.min(y_test)) - 0.5, max(np.max(y_pred), np.max(y_test)) + 0.5]
    ax.plot(lims, lims, color=ORANGE, lw=1.5, ls="--")
    ax.set(title="Test set: actual vs predicted", xlabel="Predicted", ylabel=f"Actual {ylabel}")

    fig.suptitle(title, fontsize=10)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)
