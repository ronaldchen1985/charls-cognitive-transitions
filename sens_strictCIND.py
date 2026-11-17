# Strict CIND: self-test impaired >=1 domain AND IQCODE in [3.19, 3.6); dementia unchanged
import pandas as pd, numpy as np
OUT = r"D:\CHARLS\DementiaTransition_W6\output"
cov = pd.read_csv(f"{OUT}/covariates.csv")

def classify_strict(iq, imp, adl):
    st = imp.notna()
    s = pd.Series(np.nan, index=cov.index)
    proxy = ~st
    s[proxy & (iq >= 3.6) & (adl == True)] = 3
    s[proxy & s.isna() & (iq >= 3.19)] = 2
    s[proxy & s.isna() & iq.notna()] = 1
    s[st & (imp >= 2) & (iq >= 3.6)] = 3
    s[st & s.isna() & (imp >= 1) & (iq >= 3.19)] = 2   # strict: both required
    s[st & s.isna()] = 1
    return s

c = cov.copy()
c['state18'] = classify_strict(c['iqcode18'], c['imp_count18'], c['adl_imp'])
c['state6']  = classify_strict(c['iqcode6'],  c['imp_count6'],  c['adl_imp'])
c.to_csv(f"{OUT}/covariates_strictCIND.csv", index=False)
print("strict 2018:", c['state18'].value_counts(dropna=False).to_dict())
print("strict W6:", c['state6'].value_counts(dropna=False).to_dict())
