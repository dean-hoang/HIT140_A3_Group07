# FIFA World Cup 2026: Objective 2 (Linear Regression)

HIT140 Foundations of Data Science · Assessment 3 · Sydney Group 07 · Charles Darwin University, Semester 2 2026

This repository has all the Python code and data for our Objective 2 report. We fit two multiple linear regression models on all 104 matches of the 2026 FIFA World Cup, using only information known **before kick-off**:

| Task | Rows | Target | 8 explanatory variables |
|---|---|---|---|
| **2.1** Goal difference | 104 (one per match) | `goal_difference` = team 1 goals − team 2 goals | team 1 − team 2 differences: `fifa_rank_diff`, `log_value_ratio`, `avg_age_diff`, `host_diff`, `wc_experience_diff`, `elite_conf_diff`, `rest_days_diff`, `form_gd_pg_diff` |
| **2.2** Goals scored | 208 (one per team per match) | `goals` scored by the team | own and opponent levels: `fifa_rank`, `opp_fifa_rank`, `log_market_value`, `opp_log_market_value`, `is_host`, `is_knockout`, `form_gf_pg`, `opp_form_ga_pg` |

## Group members

| Member | Code and checks |
|---|---|
| Yujan Bhattarai | Data collection (results, rankings, squad values), repository |
| Duong Hoang | Data wrangling and feature engineering (`01_build_datasets.py`), leakage check (`04_check_no_leakage.py`) |
| Vu Quang Huy Cu | Linear Regression 2.1 (`02_regression_2_1_goal_difference.py`), cross-check of 2.2 |
| Yonish Tamang | Linear Regression 2.2 (`03_regression_2_2_team_goals.py`), 2.2 robustness review (`review_2_2.py`, `cv_compare.py`) |

## Quick start

Requires Python 3.10 or newer (Anaconda works out of the box).

```bash
pip install -r requirements.txt
python run_all.py
```

`run_all.py` runs the four main scripts in order:

1. `src/01_build_datasets.py` rebuilds both datasets from `data/raw/`
2. `src/02_regression_2_1_goal_difference.py` runs Linear Regression 2.1
3. `src/03_regression_2_2_team_goals.py` runs Linear Regression 2.2
4. `src/04_check_no_leakage.py` checks that no variable uses in-match data

Every table goes to `outputs/tables/` and every figure to `outputs/figures/`. Results are fully reproducible (fixed random seed 42). The printed output from our run is saved in `outputs/console_output.txt`.

## Running each script on its own

Run all commands from the project root folder.

| Command | What it does | Main outputs |
|---|---|---|
| `python src/01_build_datasets.py` | Validates the raw scores against the 12 official group tables (stops if any table differs), reshapes 104 matches into 208 team-match rows, and builds every variable | `data/processed/dataset_2_1_goal_difference.csv`, `dataset_2_2_team_goals.csv`, `team_match_long.csv` |
| `python src/02_regression_2_1_goal_difference.py` | Regression 2.1: descriptive statistics, correlations, VIF, Model A (8 variables), Model B (backward elimination), 80/20 test, repeated 10-fold CV, residual diagnostics | `outputs/tables/LR2.1_*.csv`, `outputs/figures/LR2.1_*.png` |
| `python src/03_regression_2_2_team_goals.py` | Regression 2.2: the same steps, plus Model C (Model A refitted on log(1 + goals)) | `outputs/tables/LR2.2_*.csv`, `outputs/figures/LR2.2_*.png` |
| `python src/04_check_no_leakage.py` | Recomputes every form variable using only earlier matches and checks static variables, first matches, targets and row counts (6 checks) | `outputs/tables/leakage_check.csv` (all PASS) |
| `python src/optional_verify_with_statsmodels.py` | Optional: prints the statsmodels OLS summary for Model A of both tasks, to confirm our coefficients and p-values | printed only |
| `python src/review_2_2.py data/processed/dataset_2_2_team_goals.csv` | Optional 2.2 robustness review: robust and match-clustered standard errors, Model B diagnostics, selection stability, influential matches, Poisson model | printed (saved in `review/review_output.txt`) |
| `python src/cv_compare.py data/processed/dataset_2_2_team_goals.csv` | Optional: repeated 10-fold CV with folds split by row vs by match | printed (saved in `review/review_output.txt`) |

`pipeline.py` (the shared modelling workflow) and `regression_helpers.py` (OLS inference, VIF, backward elimination, evaluation and plots) are imported by scripts 02 and 03 and are not run on their own.

## Folder structure

```
run_all.py                 runs the whole pipeline
requirements.txt           Python packages
data/
  raw/                     source data transcribed into CSV (prepared before any analysis)
    match_results.csv        104 matches: date, stage, teams, score, extra time, shoot-out winner
    team_profiles.csv        48 teams: FIFA rank, squad value, average age, WC history, confederation, host
    group_tables.csv         official group tables, used only to validate the group-stage scores
    SOURCES.md               where every value came from, and known data limitations
  processed/               datasets built by 01_build_datasets.py
src/                       all Python code (see the table above)
outputs/
  tables/                  CSV results: descriptives, VIF, coefficients, backward elimination logs,
                           model comparison, diagnostics for Model A and Model B, leakage check
  figures/                 PNG figures used in the report
  console_output.txt       full printed output of run_all.py
review/
  FINDINGS.md              summary of the Model 2.2 robustness review
  review_output.txt        full output of review_2_2.py and cv_compare.py
submission/                earlier working drafts (report template, slides); not the final submission
```

## Method

1. **Data preparation:** all wrangling and analysis is done in Python, none in Excel. Group-stage scores are checked against the official tables.
2. **Pre-match rule:** ranking, squad value, age, World Cup history, confederation and host status are fixed before the tournament. Form uses **only a team's earlier matches**: the current match is subtracted from the running total. A team's first match has form 0 and rest days 7.
3. **Exploration:** descriptive statistics, target distributions, Pearson correlation matrix and VIF.
4. **Model A:** OLS with all 8 variables (coefficients, 95% CIs, p-values, standardised coefficients, R², adjusted R², F-test, AIC).
5. **Model B:** backward elimination, dropping the variable with the largest p-value until all p < 0.05.
6. **Model C (2.2 only):** Model A refitted on log(1 + goals), with predictions back-transformed to goals.
7. **Evaluation:** 80/20 hold-out test and 20× repeated 10-fold cross-validation, using R², MSE, RMSE, MAE and NRMSE (RMSE ÷ range of y), compared against a baseline that always predicts the mean.
8. **Diagnostics:** residuals vs fitted, normal Q–Q plot, Shapiro–Wilk (normality) and Breusch–Pagan (constant variance), for both Model A and Model B.

## Key results

| | 2.1 Model A | 2.1 Model B | 2.2 Model A | 2.2 Model B | 2.2 Model C |
|---|---|---|---|---|---|
| Variables | 8 | 3 | 8 | 2 | 8 |
| Adjusted R² | 0.469 | 0.480 | 0.267 | 0.261 | 0.242 (log scale) |
| Test RMSE (goals) | 1.78 | 1.50 | 1.02 | 1.01 | 0.96 |
| CV R² | 0.261 | 0.336 | 0.104 | 0.142 | 0.093 |
| CV RMSE (mean baseline) | 1.53 (1.98) | 1.45 (1.98) | 1.21 (1.37) | 1.19 (1.37) | 1.24 (1.37) |

- **2.1 Model B** keeps `log_value_ratio`, `avg_age_diff` and `elite_conf_diff`. **2.2 Model B** keeps `log_market_value` and `opp_fifa_rank`.
- Squad market value is the strongest predictor in both tasks.
- The 2.2 residuals are not normal and their spread is not constant, because goals are counts. Model C and a Poisson model (in `review_2_2.py`) were tried as improvements.

## Data conventions

- Scores include extra time but exclude penalty shoot-outs: a shoot-out counts as a draw (goal difference 0).
- Squad values are in € millions and are log-transformed in the models.
- Full sources and limitations are in `data/raw/SOURCES.md`.

## Use of AI

Generative AI (Claude, Anthropic) helped locate data sources and write the Python code. Every member reviewed and ran the code and can explain their own part. Details are in our signed AI Usage Declaration Form, submitted with the report.
