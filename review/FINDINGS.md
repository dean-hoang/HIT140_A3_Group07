# Model 2.2 review: robustness checks and findings

Checks on the group's Linear Regression 2.2 (`03_regression_2_2_team_goals.py` + `regression_helpers.py`).
The group pipeline was re-run with `python run_all.py`. It reproduces every 2.2 number in the report exactly. **No pipeline files were changed.**

## How to run the checks
From the project root, with statsmodels installed (`pip install statsmodels`):
```
python src/review_2_2.py data/processed/dataset_2_2_team_goals.csv
python src/cv_compare.py data/processed/dataset_2_2_team_goals.csv
```
The full output is in `review/review_output.txt`. These are optional checks and are not run by `run_all.py`.

## Findings

| # | Check | Result | Suggested action |
|---|---|---|---|
| 1 | **Robust / clustered SEs** (Breusch–Pagan p < 0.001, and paired rows) | Model B is **unchanged**. Both variables have p < 0.001 under HC3 and match-clustered SEs. Clustered 95% CIs: opp_fifa_rank [0.011, 0.029], log_market_value [0.31, 0.59]. In Model A, opp_fifa_rank goes from p = 0.084 to 0.13. | One sentence in 3.2: "conclusions hold under heteroscedasticity-robust / clustered SEs." Optionally add to `optional_verify_with_statsmodels.py`. |
| 2 | **Diagnostics on Model B** (the report only shows Model A) | Shapiro–Wilk p = 0.0003, Breusch–Pagan p < 0.001. Same issues as Model A. 2 fitted values are negative (min −0.19 goals). | Add one line or a table row for Model B. Fill the blank cells in Table 2. |
| 3 | **Train/test split by row, not by match** | 30 of the 104 matches are split between train and test. Repeated CV grouped by match gives **almost identical** results: RMSE 1.191 vs 1.188 (B) and 1.216 vs 1.209 (A). | No code change needed. Say in the report that this was checked, which turns a limitation into evidence. |
| 4 | **Model B's CV is slightly optimistic** (variables chosen on all 208 rows, then scored by CV on the same rows) | Re-running backward elimination inside every fold: CV R² 0.155 vs 0.193, RMSE 1.217 vs 1.190. The same 2 variables were chosen in **82% of folds**, log_market_value in 100% and opp_fifa_rank in 89%. | Mention it: B is stable, but its CV advantage over A is partly selection bias. |
| 5 | **Form = 0 in first match** | 48 rows are first matches, and they make up 48 of the 60 rows with form = 0. A first-match flag isn't significant (p = 0.69), and the form coefficients barely move. | Keep the variables. One sentence: "sensitivity check showed this didn't affect results." |
| 6 | **Squad values dated 18 June** (a week after kick-off) | Already listed in `SOURCES.md` as a limitation. | Make sure it stays in Section 4. |
| 7 | **Poisson robustness check** | Dispersion 0.89, so a Poisson model fits well. log_market_value is still strongly significant. **is_host becomes significant (p = 0.027)**, while opp_fifa_rank is p = 0.12. | Good material for "future work". Count models may detect a host effect that OLS misses. |

Influential matches (Cook's D, Model B): Germany 7–1 Curaçao is by far the largest. Others are England 6–4 France in the third-place match, and England 0–0 Ghana, Ecuador 0 vs Curaçao and Spain 0 vs Cape Verde (big favourites that didn't score).

### Extra checks: variable choices against the report outline
| # | Check | Result | Action |
|---|---|---|---|
| 8 | Report text vs the outputs | The report template's 3.1 note says "VIF all < 3", but the **highest VIF is 3.16** (log_market_value). The outline correctly says < 3.2. | Write "all VIFs ≤ 3.2" in 3.1. |
| 9 | Expected vs observed signs (Model A) | Most signs make sense: own rank −, opponent rank +, own value +, opponent value −, host +, opponent goals conceded +. **form_gf_pg flips sign**: its simple correlation with goals is +0.06, but its coefficient is −0.13 (p = 0.13) once value and rank are controlled for. | Explain it as noise from 0–2 earlier games, plus overlap with squad value. It isn't a real "scoring more makes you score less" effect. |
| 10 | Backward elimination vs adjusted R² | Adjusted R² **peaked at 0.271** after dropping is_knockout and fifa_rank, then fell to 0.261 for B. Elimination by p-value doesn't maximise adjusted R². | Good point for the A vs B discussion. B is chosen for simplicity and CV performance, not for adjusted R². |
| 11 | Host sample size | Only **15 of 208 rows** are host-nation rows. | This is why is_host is imprecise in OLS (p = 0.11). |

All other 2.2 numbers in the outline and report match the re-run outputs: goals mean 1.48, SD 1.39, skew 1.15; Shapiro–Wilk p = 0.001; Breusch–Pagan p < 0.001; and Tables 2 and 3.
