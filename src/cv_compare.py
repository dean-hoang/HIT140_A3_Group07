import sys, numpy as np, pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, GroupKFold
from sklearn.metrics import r2_score, mean_squared_error
df=pd.read_csv(sys.argv[1]); y=df.goals; g=df.match_id
FEAT=["fifa_rank","opp_fifa_rank","log_market_value","opp_log_market_value","is_host","is_knockout","form_gf_pg","opp_form_ga_pg"]; B=["opp_fifa_rank","log_market_value"]
rng=np.random.default_rng(42); out=[]
for name,cols in [("A",FEAT),("B",B)]:
  for mode in ["by row","by match"]:
    fr2,frm,pr2,prm=[],[],[],[]
    for rep in range(20):
      oof=np.zeros(len(df))
      if mode=="by row": splits=KFold(10,shuffle=True,random_state=rep).split(df)
      else:
        perm=pd.Series(rng.permutation(g.unique()),index=g.unique()); splits=GroupKFold(10).split(df,y,g.map(perm))
      for a,b in splits:
        p=LinearRegression().fit(df.iloc[a][cols],y.iloc[a]).predict(df.iloc[b][cols]); oof[b]=p
        fr2.append(r2_score(y.iloc[b],p)); frm.append(np.sqrt(mean_squared_error(y.iloc[b],p)))
      pr2.append(r2_score(y,oof)); prm.append(np.sqrt(mean_squared_error(y,oof)))
    out.append(dict(model=name,split=mode,mean_fold_R2=np.mean(fr2),mean_fold_RMSE=np.mean(frm),pooled_R2=np.mean(pr2),pooled_RMSE=np.mean(prm)))
print(pd.DataFrame(out).round(3).to_string(index=False))
