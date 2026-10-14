"""
optional_verify_with_statsmodels.py
-----------------------------------
Optional cross-check (needs `pip install statsmodels`, already included in Anaconda).
Prints the statsmodels OLS summary for Model A of both tasks so the group can
confirm the coefficients/p-values match outputs/tables/*_modelA_coefficients.csv.
"""
from pathlib import Path
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1] / "data" / "processed"
TASKS = {
    "dataset_2_1_goal_difference.csv": ("goal_difference", [
        "fifa_rank_diff", "log_value_ratio", "avg_age_diff", "host_diff",
        "wc_experience_diff", "elite_conf_diff", "rest_days_diff", "form_gd_pg_diff"]),
    "dataset_2_2_team_goals.csv": ("goals", [
        "fifa_rank", "opp_fifa_rank", "log_market_value", "opp_log_market_value",
        "is_host", "is_knockout", "form_gf_pg", "opp_form_ga_pg"]),
}
for csv, (target, feats) in TASKS.items():
    df = pd.read_csv(ROOT / csv)
    model = sm.OLS(df[target], sm.add_constant(df[feats])).fit()
    print(f"\n##### {csv}\n", model.summary())
