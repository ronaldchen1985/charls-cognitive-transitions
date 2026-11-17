# -*- coding: utf-8 -*-
"""
DementiaTransition_W6: build analytic panel (2018 -> W6 2021-2023)
States: 1=Normal, 2=CIND, 3=Dementia, 4=Death
Output: output/analytic_panel.csv (long), output/covariates.csv, output/build_report.txt
"""
import pandas as pd, numpy as np, os, sys

ROOT = r"D:\CHARLS"
OUT = os.path.join(ROOT, "DementiaTransition_W6", "output")
os.makedirs(OUT, exist_ok=True)
log = open(os.path.join(OUT, "build_report.txt"), "w", encoding="utf-8")
def P(*a):
    s = " ".join(str(x) for x in a); print(s); log.write(s + "\n")

def rd(f, cols=None):
    return pd.read_stata(f, columns=cols, convert_categoricals=False)

MISS = {97, 98, 997, 998, 999, 8, 9}
def bin_correct(s):
    """1=correct ->1 ; 5/2/0 ->0 ; missing codes -> NaN"""
    s = s.copy()
    s = s.mask(s.isin([97, 98, 997, 998, 999]))
    return s.map({1.0: 1.0, 5.0: 0.0, 2.0: 0.5, 0.0: 0.0})

# ---------------- 2018 ----------------
si18 = rd(rf"{ROOT}\2018\Sample_Infor.dta")
si18 = si18[['ID', 'iyear', 'imonth']].rename(columns={'iyear': 'iy18', 'imonth': 'im18'})
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
              + ['dc033_w4', 'dc035_w4', 'dc037_w4', 'dc039_w4']
              + [f'dc{i:03d}' for i in range(9, 19)])
cog18 = rd(rf"{ROOT}\2018\Cognition.dta", cog18_cols)

hsf18 = rd(rf"{ROOT}\2018\Health_Status_and_Functioning.dta",
           ['ID', 'da007_1_', 'da007_3_', 'da007_7_', 'da007_8_',
            'db010', 'db011', 'db012', 'db013', 'db014', 'db015', 'da059', 'da067'])
ins18 = rd(rf"{ROOT}\2018\Insider.dta")
iq18_cols = [f'dd{i:03d}_w4' for i in range(16, 42)]
iq18_cols = [c for c in iq18_cols if c in ins18.columns]
P("2018 IQCODE item cols:", len(iq18_cols))

# --- 2018 domain scores ---
o18 = [bin_correct(cog18[c]) for c in ['dc001_w4', 'dc002_w4', 'dc003_w4', 'dc005_w4', 'dc006_w4']]
cog18['orient'] = pd.concat(o18, axis=1).sum(axis=1, min_count=4)

ans = [93, 86, 79, 72, 65]
s7 = []
for i, a in enumerate(ans, 1):
    v = cog18[f'dc014_w4_{i}_1'].mask(cog18[f'dc014_w4_{i}_1'].isin(MISS))
    s7.append((v == a).astype(float).where(v.notna()))
cog18['exec'] = pd.concat(s7, axis=1).sum(axis=1, min_count=3)

imm = []
for t in [28, 29, 30]:
    cols = [f'dc0{t}_w4_s{i}' for i in range(1, 11)]
    imm.append(cog18[cols].sum(axis=1, min_count=8))
cog18['mem_imm'] = pd.concat(imm, axis=1).mean(axis=1)
cog18['mem_del'] = cog18[[f'dc047_w4_s{i}' for i in range(1, 11)]].sum(axis=1, min_count=8)
cog18['mem'] = cog18[['mem_imm', 'mem_del']].sum(axis=1, min_count=2)

lang18 = [bin_correct(cog18[c]) for c in ['dc016_w4', 'dc017_w4', 'dc018_w4', 'dc019_w4',
                                          'dc020_w4', 'dc021_w4', 'dc022_w4', 'dc023_w4']]
cog18['lang'] = pd.concat(lang18, axis=1).sum(axis=1, min_count=5)
cog18['animal'] = cog18[['dc033_w4', 'dc035_w4', 'dc037_w4', 'dc039_w4']].sum(axis=1, min_count=2)
cog18['visuo'] = bin_correct(cog18['dc024_w4'])

# CES-D 2018 (dc009-018; positive dc013, dc016)
ces = pd.DataFrame({'ID': cog18['ID']})
for c in [f"dc{i:03d}" for i in range(9, 19)]:
    v = cog18[c].mask(cog18[c].isin(MISS)) - 1
    if c in ('dc013', 'dc016'):
        v = 3 - (cog18[c].mask(cog18[c].isin(MISS)) - 1)
    ces[c] = v
cog18['cesd'] = ces[[f'dc{i:03d}' for i in range(9, 19)]].sum(axis=1, min_count=8)

# ADL 2018
adl18 = hsf18[['db010', 'db011', 'db012', 'db013', 'db014', 'db015']].apply(lambda s: s.where(~s.isin(MISS)))
hsf18['adl_imp'] = (adl18 >= 2).any(axis=1).where(adl18.notna().any(axis=1))

# IQCODE 2018
iq = ins18[['ID'] + iq18_cols].copy()
for c in iq18_cols:
    iq[c] = iq[c].mask(iq[c].isin(MISS))
iq['iqcode'] = iq[iq18_cols].mean(axis=1, skipna=True).where(iq[iq18_cols].notna().sum(axis=1) >= 13)
iq18 = iq[['ID', 'iqcode']].rename(columns={'iqcode': 'iqcode18'})

d18 = (si18.merge(demo[['ID', 'xrgender', 'birthyr', 'bd001_w2_4', 'be001']], on='ID', how='left')
           .merge(cog18[['ID', 'orient', 'exec', 'mem', 'lang', 'visuo', 'animal', 'cesd']], on='ID', how='left')
           .merge(hsf18[['ID', 'da007_1_', 'da007_3_', 'da007_7_', 'da007_8_', 'adl_imp', 'da059', 'da067']], on='ID', how='left')
           .merge(iq18, on='ID', how='left'))
P("2018 merged n:", len(d18))

# ---------------- W6 (2021+2022+2023) ----------------
RENAME_2223 = {
    'dc109': 'dc001', 'dc110': 'dc002', 'dc111': 'dc003', 'dc112': 'dc004', 'dc113': 'dc005',
    'dc128_1': 'dc017_1', 'dc129_1': 'dc018_1', 'dc130_1': 'dc019_1', 'dc131_1': 'dc020_1', 'dc132_1': 'dc021_1',
    'dc135': 'dc024', 'dc136': 'dc025', 'dc137': 'dc026', 'dc138': 'dc027',
    'dc139': 'dc028', 'dc140': 'dc029', 'dc141': 'dc030', 'dc142': 'dc031', 'dc146': 'dc032',
}

def stack_wave(fname, cols=None, rename=None):
    dfs = []
    for y in [2021, 2022, 2023]:
        f = rf"{ROOT}\{y}\{fname}"
        if not os.path.exists(f):
            continue
        if rename and y in (2022, 2023):
            avail = pd.read_stata(f, convert_categoricals=False, iterator=True).variable_labels().keys()
            src = ['ID'] + [r for r, t in rename.items() if r in avail and t in (cols or [])]
            common = [c for c in (cols or []) if c in avail and c not in rename.values()]
            d = rd(f, list(dict.fromkeys(src + common)))
            d = d.rename(columns=rename)
        else:
            d = rd(f, cols)
        d['srcwave'] = y
        dfs.append(d)
    d = pd.concat(dfs, ignore_index=True)
    # dedupe: keep first row with any non-missing data
    d = d.sort_values('srcwave').drop_duplicates('ID', keep='first')
    return d

w6_cols = (['ID'] + [f'dc00{i}' for i in range(1, 6)]
           + [f'dc0{i}_1' for i in range(17, 22)]
           + [f'dc0{i}' for i in range(24, 33)]
           + ['xscorewr', 'xscoredr', 'xnscorrectnum']
           + [f'dc{i:03d}' for i in range(51, 61)])
cog6 = stack_wave("Cognition_Depression.dta", w6_cols, rename=RENAME_2223)
P("W6 cognition stacked n:", len(cog6), cog6['srcwave'].value_counts().to_dict())

hsf6 = stack_wave("Health_Status_and_Functioning.dta",
                 ['ID', 'da011_8_', 'db001', 'db003', 'db005', 'db007', 'db009', 'db011', 'da099'])
inf6 = stack_wave("Informant.dta")
iq6_cols = [f'dd{i:03d}' for i in range(16, 42)]
iq6_cols = [c for c in iq6_cols if c in inf6.columns]
P("W6 IQCODE item cols:", len(iq6_cols))

si23 = rd(rf"{ROOT}\2023\Sample_Infor.dta")
si23 = si23[['ID', 'res_wave', 'iyear', 'imonth', 'died']].rename(
    columns={'iyear': 'iy6', 'imonth': 'im6', 'died': 'died_w6'})

si20 = rd(rf"{ROOT}\2020\Sample_Infor.dta")[['ID', 'died']].rename(columns={'died': 'died_w5'})
exit20 = rd(rf"{ROOT}\2020\Exit_Module.dta", ['ID', 'exb001_1', 'exb001_2', 'exb001_3'])
exit20 = exit20.rename(columns={'exb001_1': 'dy', 'exb001_2': 'dm', 'exb001_3': 'dd'})

# --- W6 domain scores ---
o6 = [bin_correct(cog6[c]) for c in ['dc001', 'dc002', 'dc003', 'dc004', 'dc005']]
cog6['orient6'] = pd.concat(o6, axis=1).sum(axis=1, min_count=4)

s7 = []
for i, a in enumerate(ans, 17):
    v = cog6[f'dc0{i}_1'].mask(cog6[f'dc0{i}_1'].isin(MISS))
    s7.append((v == a).astype(float).where(v.notna()))
cog6['exec6'] = pd.concat(s7, axis=1).sum(axis=1, min_count=3)

cog6['mem6'] = cog6[['xscorewr', 'xscoredr']].sum(axis=1, min_count=2)

lang6 = [bin_correct(cog6[c]) for c in ['dc024', 'dc025', 'dc026', 'dc027', 'dc028', 'dc029', 'dc030', 'dc031']]
cog6['lang6'] = pd.concat(lang6, axis=1).sum(axis=1, min_count=5)
cog6['visuo6'] = bin_correct(cog6['dc032'])

ces6 = pd.DataFrame({'ID': cog6['ID']})
for c in [f"dc{i:03d}" for i in range(51, 61)]:
    v = cog6[c].mask(cog6[c].isin(MISS)) - 1
    if c in ('dc055', 'dc058'):
        v = 3 - (cog6[c].mask(cog6[c].isin(MISS)) - 1)
    ces6[c] = v
cog6['cesd6'] = ces6[[f'dc0{i}' for i in range(51, 61)]].sum(axis=1, min_count=8)

adl6 = hsf6[['db001', 'db003', 'db005', 'db007', 'db009', 'db011']].apply(lambda s: s.where(~s.isin(MISS)))
hsf6['adl_imp6'] = (adl6 >= 2).any(axis=1).where(adl6.notna().any(axis=1))

for c in iq6_cols:
    inf6[c] = inf6[c].mask(inf6[c].isin(MISS))
inf6['iqcode6'] = inf6[iq6_cols].mean(axis=1, skipna=True).where(inf6[iq6_cols].notna().sum(axis=1) >= 13)

d6 = (si23.merge(cog6.drop(columns=['srcwave']), on='ID', how='left')
          .merge(hsf6.drop(columns=['srcwave']), on='ID', how='left')
          .merge(inf6[['ID', 'iqcode6', 'dd012', 'dd014', 'dd015']], on='ID', how='left'))
P("W6 merged n:", len(d6))

# ---------------- merge panel ----------------
d = d18.merge(d6, on='ID', how='outer', indicator=True)
P("outer merge:", d['_merge'].value_counts().to_dict())
d = d.merge(si20, on='ID', how='left').merge(exit20[['ID', 'dy', 'dm']], on='ID', how='left')

# restrict: 2018 interview done (iy18 notna), age>=60 at 2018
for c in ['iy18', 'im18', 'iy6', 'im6', 'res_wave']:
    if c in d.columns:
        d[c] = pd.to_numeric(d[c], errors='coerce')
d['age18'] = d['iy18'] + d['im18'] / 12 - d['birthyr']
d.loc[d['age18'] > 105, 'age18'] = np.nan
base = d[d['iy18'].notna() & (d['age18'] >= 60)].copy()
P("baseline interviewed & age>=60:", len(base))

# education strata
edu_map = {1: 0, 2: 1, 3: 1, 4: 1, 5: 2, 6: 3, 7: 3, 8: 3, 9: 3, 10: 3, 11: 3}
base['edu4'] = base['bd001_w2_4'].map(edu_map)

# ---------------- state classification ----------------
DOMS = ['orient', 'exec', 'mem', 'lang', 'visuo']
def classify(df, doms, iqcol, adlcol, suffix):
    out = pd.DataFrame({'ID': df['ID']})
    avail = df[doms].notna()
    n_imp = pd.Series(0, index=df.index)
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
    n_avail = avail.sum(axis=1)
    selftest_ok = n_avail >= 4
    iq = df[iqcol]
    adl = df[adlcol]
    state = pd.Series(np.nan, index=df.index)
    # proxy-only rule
    proxy = ~selftest_ok
    state[proxy & (iq >= 3.6) & (adl == True)] = 3
    state[proxy & (state.isna()) & (iq >= 3.19)] = 2
    state[proxy & (state.isna()) & iq.notna()] = 1
    # self-test rule
    st = selftest_ok
    state[st & (imp_count >= 2) & (iq >= 3.6)] = 3
    state[st & state.isna() & ((imp_count >= 1) | ((iq >= 3.19) & (iq < 3.6)))] = 2
    # IQCODE missing with 2+ impaired domains but no informant -> CIND (cannot confirm dementia)
    state[st & state.isna()] = 1
    out['state' + suffix] = state
    out['imp_count' + suffix] = imp_count.where(selftest_ok)
    out['n_avail' + suffix] = n_avail
    return out

c18 = classify(base, DOMS, 'iqcode18', 'adl_imp', '18')
base = base.merge(c18, on='ID')

DOMS6 = ['orient6', 'exec6', 'mem6', 'lang6', 'visuo6']
c6 = classify(base, DOMS6, 'iqcode6', 'adl_imp6', '6')
base = base.merge(c6, on='ID')

P("\n2018 state counts:", base['state18'].value_counts(dropna=False).to_dict())
P("W6 state counts:", base['state6'].value_counts(dropna=False).to_dict())

# ---------------- deaths ----------------
base['death_date_known'] = base['dy'].notna() & (base['dy'] >= 2018)
base['died'] = ((base['died_w5'] == 1) | (base['died_w6'] == 1) | base['death_date_known'])
# exclude people who died before their (supposed) 2018 interview
P("\ndied by W5:", int((base['died_w5'] == 1).sum()), " died by W6 flag:", int((base['died_w6'] == 1).sum()),
  " exit date >=2018:", int(base['death_date_known'].sum()))

# ---------------- times (years since 2018-07-01) ----------------
base['t18'] = (base['iy18'] - 2018) + (base['im18'].astype(float) - 7) / 12
base['t6'] = (base['iy6'] - 2018) + (base['im6'].astype(float) - 7) / 12
base.loc[base['t6'].isna() & base['res_wave'].notna(), 't6'] = base['res_wave'] - 2018 + 0.5  # fallback
base['t_death'] = np.where(base['death_date_known'],
                           (base['dy'] - 2018) + (base['dm'].fillna(7).astype(float) - 7) / 12,
                           np.nan)
# midpoint imputation for deaths without date
last_alive = np.where(base['t6'].notna() & (base['died_w6'] != 1), base['t6'], base['t18'])
base['t_death_mid'] = np.where(base['death_date_known'], base['t_death'],
                               (base['t18'] + 5.5) / 2)  # midpoint 2018-intv to end 2023
# death must be after last observed alive time (W6 interview if present)
last_obs = base[['t18', 't6']].max(axis=1)
base['t_death_mid'] = np.where(base['t6'].notna(),
                               np.maximum(base['t_death_mid'], (base['t6'] + 6.0) / 2),
                               base['t_death_mid'])
base['t_death_mid'] = np.maximum(base['t_death_mid'], last_obs + 0.1)
P("\ndeath time known:", int(base['death_date_known'].sum()), "of", int(base['died'].sum()), "deaths")

# ---------------- covariates ----------------
base['female'] = (base['xrgender'] == 2).astype(float)
base['htn'] = (base['da007_1_'] == 1).astype(float)
base['dm'] = (base['da007_3_'] == 1).astype(float)
base['heart'] = (base['da007_7_'] == 1).astype(float)
base['stroke18'] = (base['da007_8_'] == 1).astype(float).where(base['da007_8_'].notna())
base['stroke6'] = ((base['da011_8_'] == 1) | (base['dd012'] == 1)).astype(float)
base.loc[base['da011_8_'].isna() & base['dd012'].isna(), 'stroke6'] = np.nan
base['stroke_inc'] = ((base['stroke18'] == 0) & (base['stroke6'] == 1)).astype(float)
smk = base['da059'].copy()
smk = smk.fillna(base['da099'])
base['smoke'] = (smk == 1).astype(float).where(smk.notna())
base['drink'] = base['da067'].isin([1, 2]).astype(float).where(base['da067'].notna())
base['cesd10'] = (base['cesd'] >= 10).astype(float).where(base['cesd'].notna())
base['married'] = base['be001'].isin([1, 2]).astype(float).where(base['be001'].notna())

# ---------------- long panel for msm ----------------
rows = []
for _, r in base.iterrows():
    if pd.notna(r['state18']):
        rows.append((r['ID'], max(r['t18'], 0.0), int(r['state18']), 1))
    died = r['died']
    has6 = pd.notna(r['state6']) and pd.notna(r['t6'])
    if died:
        td = r['t_death_mid']
        if pd.isna(td) or td <= max(r['t18'], 0):
            td = max(r['t18'], 0) + 2.75
        if has6:  # interviewed at W6 then died? rare; add both
            rows.append((r['ID'], r['t6'], int(r['state6']), 2))
        rows.append((r['ID'], td, 4, 9))
    elif has6:
        rows.append((r['ID'], r['t6'], int(r['state6']), 2))
panel = pd.DataFrame(rows, columns=['ID', 'time', 'state', 'src'])
panel = panel.sort_values(['ID', 'time'])
# drop duplicated same-time rows keeping last
panel = panel.drop_duplicates(['ID', 'time'], keep='last')

cov = base[['ID', 'age18', 'female', 'edu4', 'married', 'smoke', 'drink', 'htn', 'dm',
            'heart', 'stroke18', 'stroke_inc', 'stroke6', 'cesd10', 'adl_imp',
            'iqcode18', 'iqcode6', 'state18', 'state6', 'died', 't18', 't6',
            'imp_count18', 'imp_count6']].copy()
panel.to_csv(os.path.join(OUT, "analytic_panel.csv"), index=False)
cov.to_csv(os.path.join(OUT, "covariates.csv"), index=False)

# ---------------- report ----------------
P("\n=== panel rows:", len(panel), " persons:", panel['ID'].nunique())
P("rows per person:", panel.groupby('ID').size().value_counts().to_dict())
tr = panel.copy()
tr['next'] = tr.groupby('ID')['state'].shift(-1)
P("\nObserved 2018->W6 transitions:")
P(pd.crosstab(tr['state'], tr['next'], dropna=False).to_string())
P("\nbaseline state x died:", pd.crosstab(cov['state18'], cov['died'], dropna=False).to_string())
P("\nage18:", cov['age18'].describe().to_string())
P("\ncovariate missingness:\n", cov.isna().mean().round(3).to_string())
log.close()
print("DONE")
