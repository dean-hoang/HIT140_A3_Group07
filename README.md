# FIFA World Cup 2026: Objective 2 (Linear Regression)
HIT140 Foundations of Data Science · Assessment 3 · Sydney Group 07

Two linear regression models built on all 104 matches of the 2026 FIFA World Cup:

| Task | Rows | Target | 8 explanatory variables (all known before kick-off) |
|---|---|---|---|
| **2.1** | 104 (one per match) | `goal_difference` = team1 goals − team2 goals | team1 − team2 differences in FIFA rank, ln squad value, average age, host status, prior WC appearances, UEFA/CONMEBOL membership, rest days, and in-tournament goal difference per game so far |
| **2.2** | 208 (one per team per match) | `goals` scored by the team | team FIFA rank, opponent FIFA rank, ln team squad value, ln opponent squad value, host, knockout stage, team goals scored per game so far, opponent goals conceded per game so far |

## How to run
```bash
pip install -r requirements.txt
python run_all.py
```
`run_all.py` rebuilds both datasets from `data/raw/`, fits and evaluates both models, and writes every table and figure to `outputs/`. It is fully reproducible (fixed `random_state = 42`).

## Project structure
```
data/raw/            transcribed source data + SOURCES.md (where every value came from)
  match_results.csv    104 matches: date, stage, teams, score, extra time, shoot-out winner
  team_profiles.csv    48 teams: FIFA rank, squad value, age, WC history, confederation, host
  group_tables.csv     official group tables, used to auto-check the group-stage scores
data/processed/      the two modelling datasets (104 and 208 rows) + intermediate long table
src/
  01_build_datasets.py                   data wrangling and feature engineering
  pipeline.py                            the shared modelling workflow (run_task)
  regression_helpers.py                  OLS inference, VIF, backward elimination, evaluation, plots
  02_regression_2_1_goal_difference.py   Linear Regression 2.1
  03_regression_2_2_team_goals.py        Linear Regression 2.2
  optional_verify_with_statsmodels.py    cross-check against statsmodels (if installed)
outputs/tables/      CSV results (descriptives, VIF, coefficients, model comparison, diagnostics)
outputs/figures/     PNG figures for the report
outputs/console_output.txt   full printed output of run_all.py
submission/          report template (.docx), AI declaration form, code-link .txt, checklist
  build_report_template.js   regenerates the report template from outputs/figures
  HIT140_A3_Group07_Slides.pptx + build_slides.js   11-slide summary deck (optional supporting material)
```

## Method summary
1. **Wrangling:** reshape matches into team-match rows. Compute each team's form *only from its earlier matches* (no leakage). Attach pre-tournament team attributes and the opponent's attributes. Build the 104-row and 208-row datasets.
2. **EDA:** descriptive statistics, target distribution, correlation matrix, VIF.
3. **Model A:** OLS with all 8 variables (coefficients, 95% CIs, p-values, standardised coefficients, R², adjusted R², F-test).
4. **Model B:** backward elimination (drop the largest p-value until all p < 0.05).
   **Model C (2.2 only):** an improvement attempt that refits Model A on a log(1 + goals) target, with predictions back-transformed to goals.
5. **Evaluation:** 80/20 hold-out and 20× repeated 10-fold cross-validation. R², MSE, RMSE, MAE and NRMSE (RMSE ÷ range of y) are compared against a "predict the mean" baseline.
6. **Diagnostics:** residuals vs fitted, normal Q-Q, Shapiro–Wilk (normality), Breusch–Pagan (constant variance).

## Data conventions
- Scores include extra time but exclude penalty shoot-outs (a shoot-out = a draw, goal difference 0).
- A team's first match has form = 0 and rest days = 7.
- Sources and limitations: see `data/raw/SOURCES.md`.
