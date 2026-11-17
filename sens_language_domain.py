# -*- coding: utf-8 -*-
"""Pre-specified sensitivity (SAP section 4.1): cross-wave comparability of the
language domain. The W6 battery dropped animal naming (verbal fluency); the main
analysis therefore builds the language domain from MMSE language items common to
both waves. Here we reclassify 2018 states with the language domain INCLUDING
animal naming (the fuller 2018 battery) and quantify agreement with the main
2018 classification (Cohen's kappa, % agreement, state-shift matrix).
Output: output/sens_language_domain.txt
"""
import pandas as pd, numpy as np, os

ROOT = r"D:\CHARLS"
OUT = os.path.join(ROOT, "DementiaTransition_W6", "output")
lines = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); lines.append(s)

def rd(f, cols=None):
    return pd.read_stata(f, columns=cols, convert_categoricals=False)

MISS = {97, 98, 997, 998, 999, 8, 9}
def bin_correct(s):
    s = s.copy()
    s = s.mask(s.isin([97, 98, 997, 998, 999]))
    return s.map({1.0: 1.0, 5.0: 0.0, 2.0: 0.5, 0.0: 0.0})

# ---- 2018 data (identical loading to build_dataset.py) ----
si18 = rd(rf"{ROOT}\2018\Sample_Infor.dta")[['ID', 'iyear', 'imonth']].rename(
    columns={'iyear': 'iy18', 'imonth': 'im18'})
demo = rd(rf"{ROOT}\2018\Demographic_Background.dta",
          ['ID', 'xrgender', 'ba004_w3_1', 'ba002_1', 'bd001_w2_4', 'be001'])
demo['birthyr'] = demo['ba004_w3_1'].fillna(demo['ba002_1'])

cog18_cols = (['ID'] + [f'dc00{i}_w4' for i in [1, 2, 3, 5, 6]]
              + [f'dc014_w4_{i}_1' for i in range(1, 6)]
              + [f'dc0{i}_w4' for i in range(16, 25)]
              + [f'dc028_w4_s{i}' for i in range(1, 11)]
              + [f'dc029_w4_s{i}' for i in range(1, 11)]
              + [f'dc030_w4_s{i}' for i in range(1, 11)]
              + [f'dc047_w4_s{i}' for i in range(1, 11)]
              + ['dc033_w4', 'dc035_w4', 'dc037_w4', 'dc039_w4'])
cog18 = rd(rf"{ROOT}\2018\Cognition.dta", cog18_cols)
hsf18 = rd(rf"{ROOT}\2018\Health_Status_and_Functioning.dta",
           ['ID', 'db010', 'db011', 'db012', 'db013', 'db014', 'db015'])
ins18 = rd(rf"{ROOT}\2018\Insider.dta")
iq18_cols = [c for c in [f'dd{i:03d}_w4' for i in range(16, 42)] if c in ins18.columns]
P("2018 IQCODE item cols:", len(iq18_cols))

# ---- domain scores (identical to build_dataset.py) ----
cog18['orient'] = pd.concat([bin_correct(cog18[c]) for c in
    ['dc001_w4', 'dc002_w4', 'dc003_w4', 'dc005_w4', 'dc006_w4']], axis=1).sum(axis=1, min_count=4)
ans = [93, 86, 79, 72, 65]
s7 = []
for i, a in enumerate(ans, 1):
    v = cog18[f'dc014_w4_{i}_1'].mask(cog18[f'dc014_w4_{i}_1'].isin(MISS))
    s7.append((v == a).astype(float).where(v.notna()))
cog18['exec'] = pd.concat(s7, axis=1).sum(axis=1, min_count=3)
imm = []
for t in [28, 29, 30]:
    imm.append(cog18[[f'dc0{t}_w4_s{i}' for i in range(1, 11)]].sum(axis=1, min_count=8))
cog18['mem_imm'] = pd.concat(imm, axis=1).mean(axis=1)
cog18['mem_del'] = cog18[[f'dc047_w4_s{i}' for i in range(1, 11)]].sum(axis=1, min_count=8)
cog18['mem'] = cog18[['mem_imm', 'mem_del']].sum(axis=1, min_count=2)
cog18['lang'] = pd.concat([bin_correct(cog18[c]) for c in
    ['dc016_w4', 'dc017_w4', 'dc018_w4', 'dc019_w4', 'dc020_w4', 'dc021_w4',
     'dc022_w4', 'dc023_w4']], axis=1).sum(axis=1, min_count=5)
cog18['animal'] = cog18[['dc033_w4', 'dc035_w4', 'dc037_w4', 'dc039_w4']].sum(axis=1, min_count=2)
cog18['visuo'] = bin_correct(cog18['dc024_w4'])
# language domain including animal naming (fuller 2018 battery): lang (0-8) + animal (0-4)
cog18['lang_full'] = cog18['lang'] + cog18['animal']
cog18.loc[cog18['lang'].isna() | cog18['animal'].isna(), 'lang_full'] = np.nan

adl18 = hsf18[['db010', 'db011', 'db012', 'db013', 'db014', 'db015']].apply(
    lambda s: s.where(~s.isin(MISS)))
hsf18['adl_imp'] = (adl18 >= 2).any(axis=1).where(adl18.notna().any(axis=1))

iq = ins18[['ID'] + iq18_cols].copy()
for c in iq18_cols:
    iq[c] = iq[c].mask(iq[c].isin(MISS))
iq['iqcode18'] = iq[iq18_cols].mean(axis=1).where(iq[iq18_cols].notna().sum(axis=1) >= 13)

d = (si18.merge(demo[['ID', 'birthyr', 'bd001_w2_4']], on='ID', how='left')
         .merge(cog18[['ID', 'orient', 'exec', 'mem', 'lang', 'lang_full', 'visuo']],
                on='ID', how='left')
         .merge(hsf18[['ID', 'adl_imp']], on='ID', how='left')
         .merge(iq[['ID', 'iqcode18']], on='ID', how='left'))
d['iy18'] = pd.to_numeric(d['iy18'], errors='coerce')
d['im18'] = pd.to_numeric(d['im18'], errors='coerce')
d['age18'] = d['iy18'] + d['im18'] / 12 - d['birthyr']
d.loc[d['age18'] > 105, 'age18'] = np.nan
base = d[d['iy18'].notna() & (d['age18'] >= 60)].copy()
P("baseline interviewed & age>=60:", len(base))
edu_map = {1: 0, 2: 1, 3: 1, 4: 1, 5: 2, 6: 3, 7: 3, 8: 3, 9: 3, 10: 3, 11: 3}
base['edu4'] = base['bd001_w2_4'].map(edu_map)

def classify(df, doms, iqcol, adlcol):
    avail = df[doms].notna()
    imp = pd.DataFrame(index=df.index)
    for dom in doms:
        z = pd.Series(np.nan, index=df.index)
        for e in range(4):
            m = (df['edu4'] == e) & df[dom].notna()
            mu, sd = df.loc[m, dom].mean(), df.loc[m, dom].std()
            if sd and sd > 0:
                z[m] = (df.loc[m, dom] - mu) / sd
        imp[dom] = (z < -1.5)
    imp_count = imp.sum(axis=1)
    selftest_ok = avail.sum(axis=1) >= 4
    iq_, adl = df[iqcol], df[adlcol]
    state = pd.Series(np.nan, index=df.index)
    proxy = ~selftest_ok
    state[proxy & (iq_ >= 3.6) & (adl == True)] = 3
    state[proxy & state.isna() & (iq_ >= 3.19)] = 2
    state[proxy & state.isna() & iq_.notna()] = 1
    st = selftest_ok
    state[st & (imp_count >= 2) & (iq_ >= 3.6)] = 3
    state[st & state.isna() & ((imp_count >= 1) | ((iq_ >= 3.19) & (iq_ < 3.6)))] = 2
    state[st & state.isna()] = 1
    return state

base['state_main'] = classify(base, ['orient', 'exec', 'mem', 'lang', 'visuo'],
                              'iqcode18', 'adl_imp')
base['state_full'] = classify(base, ['orient', 'exec', 'mem', 'lang_full', 'visuo'],
                              'iqcode18', 'adl_imp')

both = base[base['state_main'].notna() & base['state_full'].notna()].copy()
P("classifiable under both definitions:", len(both))
agree = (both['state_main'] == both['state_full']).mean()
P("raw agreement: %.4f" % agree)
# Cohen's kappa
tab = pd.crosstab(both['state_main'], both['state_full'])
po = agree
pe = sum(tab.loc[i].sum() * tab[i].sum() for i in tab.index if i in tab.columns) / len(both) ** 2
P("Cohen's kappa: %.4f" % ((po - pe) / (1 - pe)))
P("\nstate-shift matrix (rows = main 2018 state, cols = with animal naming):")
P(tab.to_string())
P("\nstate distribution main:", dict(both['state_main'].value_counts().sort_index()))
P("state distribution with animal naming:", dict(both['state_full'].value_counts().sort_index()))
P("\nchanges by direction:")
ch = both[both['state_main'] != both['state_full']]
P(pd.crosstab(ch['state_main'], ch['state_full']).to_string())

with open(os.path.join(OUT, "sens_language_domain.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("saved", os.path.join(OUT, "sens_language_domain.txt"))
