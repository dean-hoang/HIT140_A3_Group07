# Assessment 3: report outline and key results (working notes, NOT report text)

> **Integrity note:** the brief says the report must be written **in your group's own words**. AI may only suggest the outline or proofread. This file is that outline plus the numbers the code produced. Write every sentence of the report yourselves, and declare this outline in the AI Usage Declaration Form.

Limit: 4 pages A4, 10 pt, single-spaced, including title, names and IDs. Suggested budget: 0.25 p title/intro · 1.6 p for 2.1 · 1.6 p for 2.2 · 0.5 p for comparison, limitations and conclusion. Use about 4 figures in total and keep tables compact.

---

## Suggested structure

### 0. Title block
- Title, group name, 4 names + student IDs, GitHub/OneDrive URL

### 1. Introduction and data (≈0.3 page)
- Goal: two regression tasks (2.1 match goal difference, 2.2 team goals)
- Sources: Wikipedia group pages + news sites for knockout scores, FIFA ranking (11 June 2026), Transfermarkt squad values, RotoWire ages, Wikipedia WC history (see `data/raw/SOURCES.md`)
- Raw prep: Excel/CSV only. All wrangling is in Python (`01_build_datasets.py`).
- Points to explain in your own words:
  - The "known before kick-off" rule and how you enforced it: form is computed from earlier matches only
  - The scoring convention: extra time counted, shoot-outs = draw
  - The validation check: group scores rebuild all 12 official tables

### 2. Linear Regression 2.1: goal difference (104 rows)
**2.1a Variable choice:** one line per variable explaining why it should matter before the match (a small table works well):
`fifa_rank_diff, log_value_ratio, avg_age_diff, host_diff, wc_experience_diff, elite_conf_diff, rest_days_diff, form_gd_pg_diff`
- Why the log of the value ratio: values are right-skewed (France €1.52bn vs Qatar €20m)

**2.1b EDA:** Figure `LR2.1_correlation.png`
- Target: mean 0.48, SD 2.02, range −4 to +6
- Strongest correlations with goal difference: log_value_ratio r = 0.66, fifa_rank_diff r = −0.62, wc_experience_diff r = 0.53
- Multicollinearity: log_value_ratio vs fifa_rank_diff r = −0.79. VIF of log_value_ratio = 7.4 (all others < 4).

**2.1c Model A (all 8) results:**
| | coef | p |
|---|---|---|
| log_value_ratio | 1.026 | <0.001 |
| avg_age_diff | 0.308 | 0.028 |
| elite_conf_diff | −0.735 | 0.026 |
| fifa_rank_diff | −0.007 | 0.44 |
| rest_days_diff | 0.267 | 0.25 |
| form_gd_pg_diff | −0.099 | 0.30 |
| wc_experience_diff | 0.005 | 0.87 |
| host_diff | 0.012 | 0.98 |

- R² = 0.511, adj R² = 0.469, F = 12.39 (p < 0.001)

**2.1d Model B (backward elimination):** keeps log_value_ratio (1.089), avg_age_diff (0.321), elite_conf_diff (−0.706)
- R² = 0.495, adj R² = **0.480** (higher than A), AIC 82.6 vs 89.3

**2.1e Evaluation** (table `LR2.1_model_comparison.csv`):
| | Model A | Model B | Baseline (mean) |
|---|---|---|---|
| Test RMSE (80/20) | 1.78 | **1.50** | 2.11 |
| Test MAE | 1.44 | **1.16** | 1.74 |
| Test R² | 0.28 | **0.50** | ≈0 |
| CV RMSE (10-fold ×20) | 1.53 | **1.45** | 1.98 |
| CV R² | 0.26 | **0.34** | n/a |

- Points to interpret: Model A overfits (train R² 0.53 vs test 0.28). The simpler B generalises better. Both beat the baseline by roughly 25%.

**2.1f Interpretation points to discuss:**
- A one-unit increase in ln value ratio (team1 worth about 2.7× team2) → about +1 goal difference, holding the others fixed
- Once value is controlled for, FIFA rank and WC experience add nothing (they overlap with value; see the VIF)
- elite_conf_diff is **negative** after controlling for value. Possible reasons: UEFA/CONMEBOL teams underperformed relative to their price tag, or a suppressor effect from collinearity. Avoid a causal claim.
- Older squad → slightly better goal difference (about +0.3 goals per extra year of average age)

**2.1g Diagnostics:** Figure `LR2.1_diagnostics.png`
- Shapiro–Wilk p = 0.60 (residuals look normal)
- Breusch–Pagan p = 0.15 (no strong evidence of heteroscedasticity)
- Assumptions reasonably met

### 3. Linear Regression 2.2: team goals (208 rows)
**3a Variables:** `fifa_rank, opp_fifa_rank, log_market_value, opp_log_market_value, is_host, is_knockout, form_gf_pg, opp_form_ga_pg`
- Why include opponent variables: goals depend on who you are AND who you face

**3b EDA:**
- Target: goals mean 1.48, SD 1.39, integers 0 to 7, right-skewed (count data). Figure `LR2.2_target_distribution.png`.
- Correlations are weaker than in 2.1: log_market_value 0.40, fifa_rank −0.37, opp_fifa_rank 0.35
- All VIF < 3.2

**3c Model A (all 8):**
- R² = 0.295, adj R² = 0.267, F = 10.40 (p < 0.001)
- Only log_market_value is significant (0.467, p < 0.001); opp_fifa_rank is borderline (p = 0.084)

**3d Model B:** keeps log_market_value (0.448) + opp_fifa_rank (0.020)
- Both p < 0.001; adj R² 0.261, AIC 78.1 vs 82.3
- Interpretation example: an opponent ranked 50 places lower → about +1 goal expected

**3e Evaluation:**
| | Model A | Model B | Baseline |
|---|---|---|---|
| Test RMSE | 1.02 | **1.01** | 1.18 |
| Test MAE | 0.81 | **0.78** | 0.98 |
| Test R² | 0.15 | **0.18** | <0 |
| CV RMSE | 1.21 | **1.19** | 1.37 |
| CV R² | 0.10 | **0.14** | n/a |

**3f Diagnostics:** Figure `LR2.2_diagnostics.png`
- Shapiro–Wilk p = 0.001: residuals are non-normal
- Breusch–Pagan p < 0.001: heteroscedastic
- The striped residual plot comes from an integer target
- Points to discuss: linear regression assumes a continuous, normal target, but goals are counts. Possible improvements: log(goals + 1) transformation, or Poisson regression (outside this unit's scope, so mention only).

**3g Model C, an improvement attempt (log(1 + goals) target, all 8 variables):** predictions are back-transformed to goals before scoring
- Test R² 0.247, RMSE 0.96, MAE 0.73, NRMSE 0.193 (best on the single 80/20 split)
- CV R² 0.093, CV RMSE 1.24 (no better than A or B under cross-validation)
- Residual normality improves: Shapiro–Wilk p rises from 0.001 to 0.021, but is still below 0.05
- Point to discuss: the transform helps the assumptions but not the predictions. A single split can be misleading, which is why CV is reported too.

**NRMSE (RMSE ÷ range of the actual values), test set:** 2.1 A 0.223 · 2.1 B 0.187 · 2.2 A 0.205 · 2.2 B 0.201 · 2.2 C 0.193

### 4. Comparing the two tasks, limitations, conclusion (≈0.5 page)
- 2.1 explains much more variance (about 0.48–0.51) than 2.2 (about 0.27–0.30). Points to consider:
  - A difference cancels shared match conditions
  - Single-team goal counts are noisy
  - Few goals per game means luck matters more
- Common finding: squad market value is the most consistent pre-match predictor in both models
- Limitations:
  - Small n (104/208); test-set metrics vary a lot between splits (see CV SD)
  - Transfermarkt snapshot published 18 June
  - Form = 0 for every team's first match
  - team1/team2 ordering is arbitrary in 2.1
  - The two rows of the same match in 2.2 are not independent
  - Ranking is ordinal
  - Knockout scores come from secondary sources
- Future work: more seasons/tournaments, Elo ratings, betting odds as a predictor, Poisson model

---

## Figure / table shortlist for 4 pages
1. `LR2.1_correlation.png` (or the VIF table)
2. `LR2.1_coefficients.png`
3. `LR2.2_coefficients.png` or `LR2.2_diagnostics.png`
4. One combined evaluation table: 2.1 A/B and 2.2 A/B vs baseline

## Things the marker may ask you to explain (know these)
- Why every variable is pre-match (show the `shift`/cumulative-minus-current logic in `01_build_datasets.py`)
- What VIF measures and why log_value_ratio's 7.4 matters
- Why repeated CV is used as well as one 80/20 split
- What adjusted R² penalises, and why Model B can have higher adjusted R² but lower R²
- How backward elimination works, and its weakness (p-value-based, data-driven)
