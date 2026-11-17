# Sensitivity: alternative IQCODE dementia cutoffs 3.48 / 3.9
import pandas as pd, numpy as np
cov = pd.read_csv(r"D:\CHARLS\DementiaTransition_W6\output\covariates.csv")

def classify(iq, imp_count, adl, cut_dem):
    selftest_ok = imp_count.notna()
    state = pd.Series(np.nan, index=cov.index)
    proxy = ~selftest_ok
    state[proxy & (iq >= cut_dem) & (adl == True)] = 3
    state[proxy & state.isna() & (iq >= 3.19)] = 2
    state[proxy & state.isna() & iq.notna()] = 1
    st = selftest_ok
    state[st & (imp_count >= 2) & (iq >= cut_dem)] = 3
    state[st & state.isna() & ((imp_count >= 1) | ((iq >= 3.19) & (iq < cut_dem)))] = 2
    state[st & state.isna()] = 1
    return state

for cut in [3.48, 3.9]:
    c = cov.copy()
    c['state18'] = classify(c["iqcode18"], c["imp_count18"], c["adl_imp"], cut)
    c['state6'] = classify(c['iqcode6'], c['imp_count6'], c['adl_imp'], cut)
    c.to_csv(rf"D:\CHARLS\DementiaTransition_W6\output\covariates_cut{str(cut).replace('.','')}.csv", index=False)
    print("cutoff", cut, " 2018 states:", c['state18'].value_counts(dropna=False).to_dict())
