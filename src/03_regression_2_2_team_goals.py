"""
03_regression_2_2_team_goals.py
-------------------------------
Linear Regression 2.2: predict the number of goals a team scores in a single
FIFA World Cup 2026 match (208 team-match rows) from 8 pre-match variables.

Note on the train/test split: every match appears twice (once per team).
The split is random over rows, so occasionally both rows of one match fall
in different sets. This is acceptable because the two rows have different
targets, but it is noted as a limitation in the report.

Run from the project root:   python src/03_regression_2_2_team_goals.py
"""

import numpy as np
import pandas as pd
from scipy import stats

import regression_helpers as rh
from pipeline import ROOT, TAB, run_task

FEATURES = [
    "fifa_rank",              # team's FIFA ranking position (1 = best)
    "opp_fifa_rank",          # opponent's FIFA ranking position
    "log_market_value",       # ln(team squad value, € millions)
    "opp_log_market_value",   # ln(opponent squad value, € millions)
    "is_host",                # 1 if Canada, Mexico or USA
    "is_knockout",            # 1 if Round of 32 or later
    "form_gf_pg",             # goals the team scored per game in earlier 2026 matches
    "opp_form_ga_pg",         # goals the opponent conceded per game in earlier 2026 matches
]

if __name__ == "__main__":
    run_task(tag="LR2.2",
             csv_name="dataset_2_2_team_goals.csv",
             features=FEATURES,
             target="goals",
             target_label="goals scored")

    # ---- Model C: improvement attempt with a log(1 + goals) target ---------
    # Goals are a skewed count, and Model A's residuals failed the normality and
    # constant-variance checks. A log transform is the standard remedy taught for
    # a right-skewed target; predictions are back-transformed to goals for scoring.
    df = pd.read_csv(ROOT / "data" / "processed" / "dataset_2_2_team_goals.csv")
    X, y = df[FEATURES], df["goals"]
    coef_c, fit_c, _, resid_c = rh.ols_summary(X, np.log1p(y))
    hold_c, cv_c = rh.evaluate_log_target(X, y)
    sw_c = stats.shapiro(resid_c)
    coef_c.to_csv(TAB / "LR2.2_modelC_log_coefficients.csv")
    summary_c = pd.Series({
        "R2 on log scale": fit_c["R2"], "Adj R2 on log scale": fit_c["adj_R2"],
        "Test R2 (goals)": hold_c.loc["Model (test)", "R2"],
        "Test RMSE (goals)": hold_c.loc["Model (test)", "RMSE"],
        "Test MAE (goals)": hold_c.loc["Model (test)", "MAE"],
        "Test NRMSE (goals)": hold_c.loc["Model (test)", "NRMSE"],
        "CV R2 (goals)": cv_c.loc["CV R2", "mean"],
        "CV RMSE (goals)": cv_c.loc["CV RMSE", "mean"],
        "CV MAE (goals)": cv_c.loc["CV MAE", "mean"],
        "Shapiro-Wilk p (log residuals)": sw_c.pvalue,
    })
    summary_c.to_csv(TAB / "LR2.2_modelC_log_summary.csv")
    print("\nModel C - log(1 + goals) target, all 8 predictors:\n", coef_c.round(4).to_string())
    print("Model C evaluation (predictions back-transformed to goals):\n", summary_c.round(4).to_string())
