"""
pipeline.py
-----------
One function, run_task(), that performs the full modelling workflow for a
regression task. Both 2.1 and 2.2 call it with their own dataset/settings.

Steps
  1. Descriptive statistics of target and predictors
  2. EDA figures: target distribution + correlation matrix
  3. Multicollinearity check (VIF)
  4. Model A — full model with all 8 explanatory variables (OLS on all rows)
  5. Model B — reduced model by backward elimination (p < 0.05)
  6. Predictive evaluation of A and B: 80/20 hold-out + repeated 10-fold CV,
     each compared against a naive "predict the mean" baseline
  7. Residual diagnostics (linearity / constant variance / normality)
All tables are written to outputs/tables, figures to outputs/figures.
"""

from pathlib import Path

import pandas as pd
from scipy import stats

import regression_helpers as rh

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "outputs" / "tables"
FIG = ROOT / "outputs" / "figures"
TAB.mkdir(parents=True, exist_ok=True)
FIG.mkdir(parents=True, exist_ok=True)


def run_task(tag, csv_name, features, target, target_label, stratify_col=None):
    df = pd.read_csv(ROOT / "data" / "processed" / csv_name)
    X, y = df[features], df[target]
    print(f"\n{'=' * 70}\n{tag}: predicting '{target}'  (n = {len(df)}, k = {len(features)})\n{'=' * 70}")

    # 1. Descriptive statistics --------------------------------------------
    desc = df[features + [target]].describe().T
    desc["skew"] = df[features + [target]].skew()
    desc.to_csv(TAB / f"{tag}_descriptives.csv")
    print("\nDescriptive statistics:\n", desc.round(3).to_string())

    # 2. EDA figures ----------------------------------------------------------
    rh.plot_target_distribution(y, f"{tag}: distribution of {target_label}", target_label,
                                FIG / f"{tag}_target_distribution.png")
    rh.plot_correlation(df[features + [target]], f"{tag}: correlation matrix",
                        FIG / f"{tag}_correlation.png")
    corr_with_target = df[features].corrwith(y).sort_values(key=abs, ascending=False)
    print("\nCorrelation of each predictor with the target:\n", corr_with_target.round(3).to_string())

    # 3. Multicollinearity ----------------------------------------------------
    vif = rh.vif_table(X).sort_values(ascending=False)
    vif.to_csv(TAB / f"{tag}_vif.csv")
    print("\nVIF (>5 = concerning, >10 = serious):\n", vif.round(2).to_string())

    # 4. Model A: all 8 predictors ---------------------------------------------
    coef_a, fit_a, fitted_a, resid_a = rh.ols_summary(X, y)
    coef_a.to_csv(TAB / f"{tag}_modelA_coefficients.csv")
    print("\nModel A (all 8 predictors) - OLS on all rows:\n", coef_a.round(4).to_string())
    print({k: round(v, 4) if isinstance(v, float) else v for k, v in fit_a.items()})

    # 5. Model B: backward elimination ----------------------------------------
    kept, elim_log = rh.backward_eliminate(X, y)
    elim_log.to_csv(TAB / f"{tag}_backward_elimination_log.csv", index=False)
    coef_b, fit_b, fitted_b, resid_b = rh.ols_summary(X[kept], y)
    coef_b.to_csv(TAB / f"{tag}_modelB_coefficients.csv")
    print(f"\nBackward elimination removed: {list(elim_log.get('removed', []))}")
    print("Model B (reduced) - OLS on all rows:\n", coef_b.round(4).to_string())
    print({k: round(v, 4) if isinstance(v, float) else v for k, v in fit_b.items()})

    rh.plot_coefficients(coef_a, f"{tag} Model A: which predictors matter?",
                         FIG / f"{tag}_coefficients.png")

    # 6. Predictive evaluation --------------------------------------------------
    strat = df[stratify_col] if stratify_col else None
    hold_a, (yte_a, ypred_a) = rh.evaluate_holdout(X, y, stratify=strat)
    hold_b, _ = rh.evaluate_holdout(X[kept], y, stratify=strat)
    cv_a, cv_b = rh.evaluate_cv(X, y), rh.evaluate_cv(X[kept], y)
    print("\nHold-out (80/20) - Model A:\n", hold_a.round(3).to_string())
    print("Hold-out (80/20) - Model B:\n", hold_b.round(3).to_string())
    print("Repeated 10-fold CV - Model A:\n", cv_a.round(3).to_string())
    print("Repeated 10-fold CV - Model B:\n", cv_b.round(3).to_string())

    comparison = pd.DataFrame({
        "Model A (8 vars)": {
            "Predictors": len(features), "R2 (all data)": fit_a["R2"], "Adj R2": fit_a["adj_R2"],
            "AIC": fit_a["AIC"], "F p-value": fit_a["F_p_value"],
            "Test R2": hold_a.loc["Model (test)", "R2"], "Test RMSE": hold_a.loc["Model (test)", "RMSE"],
            "Test MAE": hold_a.loc["Model (test)", "MAE"],
            "Test NRMSE": hold_a.loc["Model (test)", "NRMSE"],
            "Baseline test RMSE": hold_a.loc["Baseline mean (test)", "RMSE"],
            "CV R2": cv_a.loc["CV R2", "mean"], "CV RMSE": cv_a.loc["CV RMSE", "mean"],
            "CV MAE": cv_a.loc["CV MAE", "mean"], "Baseline CV RMSE": cv_a.loc["Baseline RMSE", "mean"],
        },
        f"Model B ({len(kept)} vars)": {
            "Predictors": len(kept), "R2 (all data)": fit_b["R2"], "Adj R2": fit_b["adj_R2"],
            "AIC": fit_b["AIC"], "F p-value": fit_b["F_p_value"],
            "Test R2": hold_b.loc["Model (test)", "R2"], "Test RMSE": hold_b.loc["Model (test)", "RMSE"],
            "Test MAE": hold_b.loc["Model (test)", "MAE"],
            "Test NRMSE": hold_b.loc["Model (test)", "NRMSE"],
            "Baseline test RMSE": hold_b.loc["Baseline mean (test)", "RMSE"],
            "CV R2": cv_b.loc["CV R2", "mean"], "CV RMSE": cv_b.loc["CV RMSE", "mean"],
            "CV MAE": cv_b.loc["CV MAE", "mean"], "Baseline CV RMSE": cv_b.loc["Baseline RMSE", "mean"],
        },
    })
    comparison.to_csv(TAB / f"{tag}_model_comparison.csv")
    print("\nModel comparison:\n", comparison.round(4).to_string())

    # 7. Residual diagnostics (Model A) ----------------------------------------
    sw = stats.shapiro(resid_a)
    # Breusch-Pagan style check: regress squared residuals on the predictors
    bp_coef, bp_fit, *_ = rh.ols_summary(X, pd.Series(resid_a ** 2))
    bp_lm = len(y) * bp_fit["R2"]
    bp_p = stats.chi2.sf(bp_lm, df=len(features))
    diag = pd.Series({"Shapiro-Wilk W": sw.statistic, "Shapiro-Wilk p": sw.pvalue,
                      "Breusch-Pagan LM": bp_lm, "Breusch-Pagan p": bp_p})
    diag.to_csv(TAB / f"{tag}_diagnostics.csv")
    print("\nResidual diagnostics (Model A):\n", diag.round(4).to_string())
    rh.plot_diagnostics(fitted_a, resid_a, yte_a, ypred_a, f"{tag} Model A diagnostics",
                        target_label, FIG / f"{tag}_diagnostics.png")

    return {"coef_a": coef_a, "fit_a": fit_a, "coef_b": coef_b, "fit_b": fit_b,
            "kept": kept, "comparison": comparison, "vif": vif, "diag": diag}
