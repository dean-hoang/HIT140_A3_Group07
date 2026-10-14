"""
Independent checks on the group's Model 2.2 (does not modify the pipeline).
Run: python review_2_2.py <path to dataset_2_2_team_goals.csv>
"""
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GroupKFold, GroupShuffleSplit, KFold, train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from statsmodels.stats.diagnostic import het_breuschpagan

df = pd.read_csv(sys.argv[1])
FEAT = ["fifa_rank", "opp_fifa_rank", "log_market_value", "opp_log_market_value",
        "is_host", "is_knockout", "form_gf_pg", "opp_form_ga_pg"]
B = ["opp_fifa_rank", "log_market_value"]
y, g = df["goals"], df["match_id"]
SEED = 42


def rmse(a, b):
    return np.sqrt(mean_squared_error(a, b))


def backward(X, y, alpha=0.05):
    cols = list(X.columns)
    while len(cols) > 1:
        m = sm.OLS(y, sm.add_constant(X[cols])).fit()
        pv = m.pvalues.drop("const")
        if pv.max() < alpha:
            break
        cols.remove(pv.idxmax())
    return cols


print("=" * 70, "\n1. STANDARD ERRORS: classical vs HC3 vs clustered by match\n" + "=" * 70)
for name, cols in [("Model A", FEAT), ("Model B", B)]:
    X = sm.add_constant(df[cols])
    ols = sm.OLS(y, X).fit()
    hc3 = sm.OLS(y, X).fit(cov_type="HC3")
    cl = sm.OLS(y, X).fit(cov_type="cluster", cov_kwds={"groups": g})
    t = pd.DataFrame({"coef": ols.params, "p_classical": ols.pvalues,
                      "p_HC3": hc3.pvalues, "p_cluster": cl.pvalues,
                      "CI_cluster_low": cl.conf_int()[0], "CI_cluster_high": cl.conf_int()[1]}).drop("const")
    print(f"\n{name}\n", t.round(4).to_string())

print("\n" + "=" * 70, "\n2. DIAGNOSTICS ON MODEL B (report only shows Model A)\n" + "=" * 70)
mB = sm.OLS(y, sm.add_constant(df[B])).fit()
sw = stats.shapiro(mB.resid)
bp = het_breuschpagan(mB.resid, mB.model.exog)
infl = mB.get_influence().cooks_distance[0]
print(f"Shapiro-Wilk W = {sw.statistic:.4f}, p = {sw.pvalue:.4f}")
print(f"Breusch-Pagan LM = {bp[0]:.3f}, p = {bp[1]:.4g}")
print(f"Cook's D > 4/n: {(infl > 4 / len(df)).sum()} rows")
top = df.assign(cooks=infl, fitted=mB.fittedvalues).nlargest(5, "cooks")[
    ["match_id", "stage", "team", "opponent", "goals", "fitted", "cooks"]]
print(top.round(3).to_string(index=False))
print(f"Negative fitted values (impossible goals): {(mB.fittedvalues < 0).sum()} rows, "
      f"min = {mB.fittedvalues.min():.2f}")

print("\n" + "=" * 70, "\n3. ROWS OF ONE MATCH SPLIT ACROSS TRAIN/TEST\n" + "=" * 70)
tr, te = train_test_split(np.arange(len(df)), test_size=0.2, random_state=SEED)
print(f"Current 80/20 row split: {len(set(g.iloc[tr]) & set(g.iloc[te]))} matches have one row in train "
      f"and its mirror in test")
print("Repeated CV by row vs by match: run cv_compare.py")

print("\n" + "=" * 70, "\n4. IS MODEL B's CV SCORE OPTIMISTIC? (selection inside each fold)\n" + "=" * 70)
# Model B's variables were chosen using ALL 208 rows, then scored by CV on the same rows.
# Honest version: rerun backward elimination inside every training fold.
r2_fixed, r2_honest, rm_fixed, rm_honest, picks = [], [], [], [], []
rng = np.random.default_rng(SEED)
for rep in range(20):
    perm = pd.Series(rng.permutation(g.unique()), index=g.unique())
    gg = g.map(perm)
    for a, b in GroupKFold(10).split(df, y, gg):
        Xa, ya = df.iloc[a], y.iloc[a]
        chosen = backward(Xa[FEAT], ya)
        picks.append(tuple(sorted(chosen)))
        pf = LinearRegression().fit(Xa[B], ya).predict(df.iloc[b][B])
        ph = LinearRegression().fit(Xa[chosen], ya).predict(df.iloc[b][chosen])
        r2_fixed.append(r2_score(y.iloc[b], pf)); r2_honest.append(r2_score(y.iloc[b], ph))
        rm_fixed.append(rmse(y.iloc[b], pf)); rm_honest.append(rmse(y.iloc[b], ph))
print(f"B's 2 vars fixed in advance : CV R2 = {np.mean(r2_fixed):.3f}, RMSE = {np.mean(rm_fixed):.3f}")
print(f"Elimination redone per fold : CV R2 = {np.mean(r2_honest):.3f}, RMSE = {np.mean(rm_honest):.3f}")
pc = pd.Series(picks).value_counts(normalize=True).head(5)
print("Most common variable sets chosen across 200 folds:")
print(pc.round(3).to_string())
freq = pd.Series([v for p in picks for v in p]).value_counts() / len(picks)
print("Share of folds keeping each variable:")
print(freq.reindex(FEAT).fillna(0).round(2).to_string())

print("\n" + "=" * 70, "\n5. FIRST-MATCH FORM = 0 (cannot tell 'not played' from 'scored 0')\n" + "=" * 70)
first = df["date"] == df.groupby("team")["date"].transform("min")
print(f"Rows that are a team's first match: {first.sum()} of {len(df)}")
print(f"form_gf_pg == 0 overall: {(df.form_gf_pg == 0).sum()}, of which first matches: "
      f"{((df.form_gf_pg == 0) & first).sum()}")
d2 = df.assign(first_match=first.astype(int))
m_fm = sm.OLS(y, sm.add_constant(d2[FEAT + ["first_match"]])).fit(cov_type="cluster", cov_kwds={"groups": g})
print("Model A + first_match flag (sensitivity only, not a 9th reported variable):")
print(m_fm.params[["form_gf_pg", "opp_form_ga_pg", "first_match"]].round(3).to_string())
print(m_fm.pvalues[["form_gf_pg", "opp_form_ga_pg", "first_match"]].round(3).rename("p").to_string())

print("\n" + "=" * 70, "\n6. INTERPRETATION HELPERS (Model B)\n" + "=" * 70)
b_val, b_rank = mB.params["log_market_value"], mB.params["opp_fifa_rank"]
print(f"log_market_value coef {b_val:.3f}: doubling squad value -> +{b_val*np.log(2):.2f} goals; "
      f"+10% value -> +{b_val*np.log(1.1):.3f} goals")
print(f"opp_fifa_rank coef {b_rank:.4f}: opponent 10 places weaker -> +{10*b_rank:.2f}; "
      f"50 places -> +{50*b_rank:.2f} goals")
print(f"Std coefs (SD units): value {b_val*df.log_market_value.std()/y.std():.2f}, "
      f"opp rank {b_rank*df.opp_fifa_rank.std()/y.std():.2f}")
base = rmse(y, np.full(len(y), y.mean()))
print(f"In-sample: within 1 goal = {(np.abs(y - mB.fittedvalues) <= 1).mean():.1%}")

print("\n" + "=" * 70, "\n7. WORKED EXAMPLE: THE FINAL (Model B fitted on all data)\n" + "=" * 70)
fin = df[df.stage == "Final"].assign(pred=mB.fittedvalues[df.stage == "Final"])
print(fin[["team", "opponent", "fifa_rank", "opp_fifa_rank", "log_market_value", "goals", "pred"]]
      .round(2).to_string(index=False))

print("\n" + "=" * 70, "\n8. IMPLIED GOAL DIFFERENCE FROM 2.2 vs ACTUAL\n" + "=" * 70)
d = df[["match_id", "team", "goals"]].assign(pred=mB.fittedvalues)
m = d.merge(d, on="match_id", suffixes=("", "_o"))
m = m[m.team != m.team_o].drop_duplicates("match_id")
gd, igd = m.goals - m.goals_o, m.pred - m.pred_o
print(f"Implied GD (Model B, in-sample): R2 = {r2_score(gd, igd):.3f}, RMSE = {rmse(gd, igd):.3f}")
print("(Compare with 2.1 Model B in-sample R2 = 0.495. Row order differs from 2.1's team1/team2, "
      "but R2/RMSE of a difference are order-invariant.)")

print("\n" + "=" * 70, "\n9. POISSON ROBUSTNESS (same 8 vars, clustered SEs)\n" + "=" * 70)
pois = sm.GLM(y, sm.add_constant(df[FEAT]), family=sm.families.Poisson()).fit(
    cov_type="cluster", cov_kwds={"groups": g})
print(f"Dispersion = {pois.pearson_chi2 / pois.df_resid:.2f}")
print(pd.DataFrame({"coef": pois.params, "p": pois.pvalues, "rate_ratio": np.exp(pois.params)})
      .drop("const").round(4).to_string())
