"""
04_check_no_leakage.py
----------------------
Checker task (Duong Hoang): confirm that NO explanatory variable uses in-match data.

The brief says every explanatory variable must be information available BEFORE
the match. This script checks that independently of 01_build_datasets.py:

  Check 1  Static team variables (rank, value, host) are constant for a team
           across the whole tournament, so they cannot contain any match result.
  Check 2  Every "form" variable is recomputed from scratch using ONLY matches
           with an earlier date than the match being predicted, and compared
           with the values stored in the datasets.
  Check 3  Every team's first match has form = 0 (nothing known yet).
  Check 4  Neither target (goal_difference, goals) and no raw score column
           appears among the explanatory variables.
  Check 5  Each dataset has the required row count and exactly 8 variables.

Run from the project root:   python src/04_check_no_leakage.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC = ROOT / "data" / "raw", ROOT / "data" / "processed"

FEATURES_21 = ["fifa_rank_diff", "log_value_ratio", "avg_age_diff", "host_diff",
               "wc_experience_diff", "elite_conf_diff", "rest_days_diff", "form_gd_pg_diff"]
FEATURES_22 = ["fifa_rank", "opp_fifa_rank", "log_market_value", "opp_log_market_value",
               "is_host", "is_knockout", "form_gf_pg", "opp_form_ga_pg"]
SCORE_WORDS = ["goals", "goal_difference", "goals1", "goals2", "goals_for", "goals_against"]

matches = pd.read_csv(RAW / "match_results.csv", parse_dates=["date"])
ds21 = pd.read_csv(PROC / "dataset_2_1_goal_difference.csv", parse_dates=["date"])
ds22 = pd.read_csv(PROC / "dataset_2_2_team_goals.csv", parse_dates=["date"])
results = []


def record(name, passed, detail):
    results.append({"check": name, "result": "PASS" if passed else "FAIL", "detail": detail})


def form_before(team, date):
    """Goals for / against per game for `team`, using only matches BEFORE `date`."""
    past = matches[(matches["date"] < date) &
                   ((matches["team1"] == team) | (matches["team2"] == team))]
    if past.empty:
        return 0.0, 0.0, 0
    gf = np.where(past["team1"] == team, past["goals1"], past["goals2"]).sum()
    ga = np.where(past["team1"] == team, past["goals2"], past["goals1"]).sum()
    return gf / len(past), ga / len(past), len(past)


# Check 1: static variables never change for a team
static_cols = ["fifa_rank", "log_market_value", "is_host"]
changes = sum(ds22.groupby("team")[c].nunique().gt(1).sum() for c in static_cols)
record("1. Static team variables are constant across the tournament", changes == 0,
       f"{changes} team/variable combinations change value (should be 0)")

# Check 2: recompute form features from earlier-dated matches only
bad22, firsts, first_nonzero = 0, 0, 0
for _, r in ds22.iterrows():
    gf_pg, _, n_prev = form_before(r["team"], r["date"])
    _, opp_ga_pg, _ = form_before(r["opponent"], r["date"])
    if not (np.isclose(gf_pg, r["form_gf_pg"]) and np.isclose(opp_ga_pg, r["opp_form_ga_pg"])):
        bad22 += 1
    if n_prev == 0:
        firsts += 1
        first_nonzero += int(r["form_gf_pg"] != 0)
bad21 = 0
for _, r in ds21.iterrows():
    gf1, ga1, _ = form_before(r["team1"], r["date"])
    gf2, ga2, _ = form_before(r["team2"], r["date"])
    if not np.isclose((gf1 - ga1) - (gf2 - ga2), r["form_gd_pg_diff"]):
        bad21 += 1
record("2a. LR2.2 form variables use only earlier matches", bad22 == 0,
       f"{bad22} of {len(ds22)} rows differ from the strict earlier-date recomputation")
record("2b. LR2.1 form variable uses only earlier matches", bad21 == 0,
       f"{bad21} of {len(ds21)} rows differ from the strict earlier-date recomputation")

# Check 3: first appearances carry no information
record("3. Form = 0 for every team's first match", firsts == 48 and first_nonzero == 0,
       f"{firsts} first-match rows found (expected 48), {first_nonzero} with non-zero form")

# Check 4: no target or score column among the predictors
leaked = [c for c in FEATURES_21 + FEATURES_22 if c in SCORE_WORDS]
record("4. No target or raw score column used as a predictor", not leaked,
       f"score-type columns among predictors: {leaked or 'none'}")

# Check 5: shape required by the brief
ok_shape = (len(ds21) == 104 and len(ds22) == 208 and len(FEATURES_21) == 8 and len(FEATURES_22) == 8
            and set(FEATURES_21) <= set(ds21.columns) and set(FEATURES_22) <= set(ds22.columns))
record("5. 104 / 208 rows, exactly 8 explanatory variables each", ok_shape,
       f"2.1: {len(ds21)} rows x {len(FEATURES_21)} vars; 2.2: {len(ds22)} rows x {len(FEATURES_22)} vars")

report = pd.DataFrame(results)
print(report.to_string(index=False))
out = ROOT / "outputs" / "tables" / "leakage_check.csv"
out.parent.mkdir(parents=True, exist_ok=True)
report.to_csv(out, index=False)
print("\nALL CHECKS PASSED" if (report["result"] == "PASS").all() else "\nSOME CHECKS FAILED")
