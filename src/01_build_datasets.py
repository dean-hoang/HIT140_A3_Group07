"""
01_build_datasets.py
--------------------
Data wrangling for Objective 2.

Inputs  (data/raw/)
    match_results.csv   104 matches: date, stage, teams, final score
    team_profiles.csv   48 teams: pre-tournament attributes

Outputs (data/processed/)
    dataset_2_1_goal_difference.csv   104 rows  (one per match)      -> Linear Regression 2.1
    dataset_2_2_team_goals.csv        208 rows  (one per team-match) -> Linear Regression 2.2
    team_match_long.csv               the intermediate long table (for checking)

Key rule from the brief: every explanatory variable must be KNOWN BEFORE KICK-OFF.
So the only "in-tournament" information we use is each team's record in the
matches it had ALREADY played (computed strictly from earlier dates).

Run from the project root:   python src/01_build_datasets.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

FIRST_MATCH_REST_DAYS = 7   # rest value given to a team before its first match (see report)
ELITE_CONFEDERATIONS = {"UEFA", "CONMEBOL"}


# ---------------------------------------------------------------------------
# 1. Load and validate raw data
# ---------------------------------------------------------------------------
matches = pd.read_csv(RAW / "match_results.csv", parse_dates=["date"])
teams = pd.read_csv(RAW / "team_profiles.csv")

assert len(matches) == 104, "Brief requires exactly 104 matches"
assert len(teams) == 48, "There should be 48 teams"
assert matches["match_id"].is_unique

# every team named in the results must exist in the profile table
named = set(matches["team1"]) | set(matches["team2"])
missing = named - set(teams["team"])
assert not missing, f"Team names not found in team_profiles.csv: {missing}"

# Score convention: goals1/goals2 include extra time but NOT penalty shoot-outs.
# A shoot-out is recorded as a draw (goal difference 0), because shoot-out kicks
# are not goals and do not reflect how the teams played over 90-120 minutes.

# Sanity check: rebuild each group table from the scores (GF/GA/Pts should
# match the official group tables we transcribed the scores from).
group_games = matches[matches["stage"].str.startswith("Group")]
assert len(group_games) == 72
official = pd.read_csv(RAW / "group_tables.csv").set_index("team")
for team in teams["team"]:
    home = group_games[group_games["team1"] == team]
    away = group_games[group_games["team2"] == team]
    assert len(home) + len(away) == 3, f"{team} did not play 3 group games"
    gf = home["goals1"].sum() + away["goals2"].sum()
    ga = home["goals2"].sum() + away["goals1"].sum()
    pts = (3 * ((home["goals1"] > home["goals2"]).sum() + (away["goals2"] > away["goals1"]).sum())
           + (home["goals1"] == home["goals2"]).sum() + (away["goals1"] == away["goals2"]).sum())
    row = official.loc[team]
    assert (gf, ga, pts) == (row["GF"], row["GA"], row["Pts"]), \
        f"{team}: rebuilt GF/GA/Pts {gf}/{ga}/{pts} != official {row['GF']}/{row['GA']}/{row['Pts']}"
print("Group-stage scores reproduce all 12 official group tables.")

# Matches should be in date order for the rolling "form" features below
matches = matches.sort_values(["date", "match_id"]).reset_index(drop=True)


# ---------------------------------------------------------------------------
# 2. Long format: one row per team per match (208 rows)
# ---------------------------------------------------------------------------
side1 = matches.rename(columns={"team1": "team", "team2": "opponent",
                                "goals1": "goals_for", "goals2": "goals_against"})
side2 = matches.rename(columns={"team2": "team", "team1": "opponent",
                                "goals2": "goals_for", "goals1": "goals_against"})
side1["side"], side2["side"] = 1, 2
long = pd.concat([side1, side2], ignore_index=True)
long = long[["match_id", "date", "stage", "side", "team", "opponent",
             "goals_for", "goals_against", "extra_time"]]
long = long.sort_values(["team", "date"]).reset_index(drop=True)

# --- Pre-match form: uses only the team's EARLIER matches ---
# For each team (rows sorted by date), cumsum() gives the running total of goals
# INCLUDING the current match. Subtracting the current match's goals leaves only
# the goals from earlier matches, so the result of the match we are predicting
# (and of any later match) is never used.
# Example: a team scores 2, 0, 3 goals in its first three matches.
#   cumsum            = 2, 2, 5
#   minus this match  = 0, 2, 2   -> goals scored BEFORE each match
#   matches played    = 0, 1, 2   -> form_gf_pg = 0 (no games yet), 2.0, 1.0
# A team's first match has no earlier games, so its form is set to 0.
# src/04_check_no_leakage.py recomputes every value independently to confirm this.
g = long.groupby("team")
long["prior_games"] = g.cumcount()                        # matches already played
long["prior_gf"] = g["goals_for"].cumsum() - long["goals_for"]
long["prior_ga"] = g["goals_against"].cumsum() - long["goals_against"]

played = long["prior_games"].replace(0, np.nan)
long["form_gf_pg"] = (long["prior_gf"] / played).fillna(0)          # goals scored per game so far
long["form_ga_pg"] = (long["prior_ga"] / played).fillna(0)          # goals conceded per game so far
long["form_gd_pg"] = long["form_gf_pg"] - long["form_ga_pg"]

# --- Rest days since the team's previous match ---
long["rest_days"] = g["date"].diff().dt.days
long["rest_days"] = long["rest_days"].fillna(FIRST_MATCH_REST_DAYS)

# --- Attach pre-tournament team attributes ---
long = long.merge(teams, on="team", how="left")
long["log_market_value"] = np.log(long["market_value_eur_m"])
long["elite_conf"] = long["confederation"].isin(ELITE_CONFEDERATIONS).astype(int)
long["is_knockout"] = (~long["stage"].str.startswith("Group")).astype(int)

# Attach the OPPONENT's attributes and form for the same match
opp_cols = ["match_id", "team", "fifa_rank", "log_market_value",
            "form_gf_pg", "form_ga_pg"]
opp = long[opp_cols].rename(columns={c: f"opp_{c}" for c in opp_cols if c != "match_id"})
long = long.merge(opp, left_on=["match_id", "opponent"],
                  right_on=["match_id", "opp_team"], how="left").drop(columns="opp_team")

assert len(long) == 208
assert long.isna().sum().sum() == 0, "Unexpected missing values after merge"
long.to_csv(OUT / "team_match_long.csv", index=False)


# ---------------------------------------------------------------------------
# 3. Dataset for Linear Regression 2.1 — goal difference (104 rows)
#    Each explanatory variable = team1 value minus team2 value
# ---------------------------------------------------------------------------
t1 = long[long["side"] == 1].set_index("match_id")
t2 = long[long["side"] == 2].set_index("match_id")

ds21 = pd.DataFrame(index=t1.index)
ds21["date"] = t1["date"].dt.date
ds21["stage"] = t1["stage"]
ds21["team1"] = t1["team"]
ds21["team2"] = t2["team"]
# ---- 8 explanatory variables ----
ds21["fifa_rank_diff"] = t1["fifa_rank"] - t2["fifa_rank"]                 # +ve = team1 ranked LOWER
ds21["log_value_ratio"] = t1["log_market_value"] - t2["log_market_value"]  # ln(value1 / value2)
ds21["avg_age_diff"] = t1["avg_squad_age"] - t2["avg_squad_age"]
ds21["host_diff"] = t1["is_host"] - t2["is_host"]                          # +1 / 0 / -1
ds21["wc_experience_diff"] = t1["wc_prior_appearances"] - t2["wc_prior_appearances"]
ds21["elite_conf_diff"] = t1["elite_conf"] - t2["elite_conf"]              # UEFA/CONMEBOL vs others
ds21["rest_days_diff"] = t1["rest_days"] - t2["rest_days"]
ds21["form_gd_pg_diff"] = t1["form_gd_pg"] - t2["form_gd_pg"]              # tournament form so far
# ---- target ----
ds21["goal_difference"] = t1["goals_for"] - t1["goals_against"]
ds21 = ds21.reset_index().sort_values("match_id")

FEATURES_21 = ["fifa_rank_diff", "log_value_ratio", "avg_age_diff", "host_diff",
               "wc_experience_diff", "elite_conf_diff", "rest_days_diff", "form_gd_pg_diff"]
assert ds21.shape[0] == 104 and len(FEATURES_21) == 8
ds21.to_csv(OUT / "dataset_2_1_goal_difference.csv", index=False)


# ---------------------------------------------------------------------------
# 4. Dataset for Linear Regression 2.2 — goals scored by a team (208 rows)
# ---------------------------------------------------------------------------
ds22 = long[["match_id", "date", "stage", "team", "opponent"]].copy()
ds22["date"] = ds22["date"].dt.date
# ---- 8 explanatory variables ----
ds22["fifa_rank"] = long["fifa_rank"]
ds22["opp_fifa_rank"] = long["opp_fifa_rank"]
ds22["log_market_value"] = long["log_market_value"]
ds22["opp_log_market_value"] = long["opp_log_market_value"]
ds22["is_host"] = long["is_host"]
ds22["is_knockout"] = long["is_knockout"]
ds22["form_gf_pg"] = long["form_gf_pg"]            # own goals scored per game so far
ds22["opp_form_ga_pg"] = long["opp_form_ga_pg"]    # opponent goals conceded per game so far
# ---- target ----
ds22["goals"] = long["goals_for"]
ds22 = ds22.sort_values(["match_id", "team"]).reset_index(drop=True)

FEATURES_22 = ["fifa_rank", "opp_fifa_rank", "log_market_value", "opp_log_market_value",
               "is_host", "is_knockout", "form_gf_pg", "opp_form_ga_pg"]
assert ds22.shape[0] == 208 and len(FEATURES_22) == 8
ds22.to_csv(OUT / "dataset_2_2_team_goals.csv", index=False)

print("Built datasets:")
print(f"  2.1 goal difference : {ds21.shape[0]} rows x {len(FEATURES_21)} explanatory variables")
print(f"  2.2 team goals      : {ds22.shape[0]} rows x {len(FEATURES_22)} explanatory variables")
print(f"  total goals check   : {ds22['goals'].sum()} goals in {ds21.shape[0]} matches")
