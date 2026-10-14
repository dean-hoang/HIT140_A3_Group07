"""
02_regression_2_1_goal_difference.py
------------------------------------
Linear Regression 2.1: predict the goal difference (team1 goals − team2 goals)
of a FIFA World Cup 2026 match from 8 pre-match explanatory variables.

Each variable is a team1-minus-team2 difference, so a positive value means
"team1 has more of this than team2".

Run from the project root:   python src/02_regression_2_1_goal_difference.py
"""

from pipeline import run_task

FEATURES = [
    "fifa_rank_diff",       # FIFA ranking position, team1 − team2 (positive = team1 ranked lower)
    "log_value_ratio",      # ln(team1 squad value / team2 squad value), Transfermarkt
    "avg_age_diff",         # average squad age, team1 − team2 (years)
    "host_diff",            # host nation indicator, team1 − team2 (+1 / 0 / −1)
    "wc_experience_diff",   # previous World Cup appearances, team1 − team2
    "elite_conf_diff",      # UEFA/CONMEBOL member, team1 − team2
    "rest_days_diff",       # days since previous match, team1 − team2
    "form_gd_pg_diff",      # goal difference per game in earlier 2026 matches, team1 − team2
]

if __name__ == "__main__":
    run_task(tag="LR2.1",
             csv_name="dataset_2_1_goal_difference.csv",
             features=FEATURES,
             target="goal_difference",
             target_label="goal difference")
