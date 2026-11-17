import pandas as pd, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = r"D:\CHARLS\DementiaTransition_W6\output"
cov = pd.read_csv(f"{OUT}/covariates.csv")
d = cov[cov['state18'].notna()].copy()
d['state'] = d['state18'].map({1:'Normal',2:'CIND',3:'Dementia'})

rows = []
def fmt(n, d=len(d)): return f"{n} ({100*n/d:.1f}%)"
tbl = {}
tbl['N'] = d.groupby('state').size()
tbl['Age, mean (SD)'] = d.groupby('state')['age18'].agg(lambda s: f"{s.mean():.1f} ({s.std():.1f})")
for v, lab in [('female','Female, %'), ('married','Married/cohabiting, %'), ('smoke','Ever smoked, %'),
               ('drink','Drank in past year, %'), ('htn','Hypertension, %'), ('dm','Diabetes, %'),
               ('heart','Heart disease, %'), ('stroke18','Stroke, %'), ('cesd10','CES-D >= 10, %'),
               ('adl_imp','Any ADL impairment, %')]:
    tbl[lab] = d.groupby('state')[v].agg(lambda s: f"{100*s.mean():.1f}" if s.notna().any() else "")
tbl['IQCODE, mean (SD)'] = d.groupby('state')['iqcode18'].agg(lambda s: f"{s.mean():.2f} ({s.std():.2f})")
tbl['Education: illiterate, %'] = d.groupby('state')['edu4'].agg(lambda s: f"{100*(s==0).mean():.1f}")
tbl['Education: primary, %'] = d.groupby('state')['edu4'].agg(lambda s: f"{100*(s==1).mean():.1f}")
tbl['Education: middle, %'] = d.groupby('state')['edu4'].agg(lambda s: f"{100*(s==2).mean():.1f}")
tbl['Education: high+, %'] = d.groupby('state')['edu4'].agg(lambda s: f"{100*(s==3).mean():.1f}")
T = pd.DataFrame(tbl).T[['Normal','CIND','Dementia']]
T.to_csv(f"{OUT}/table1_baseline.csv")
print(T.to_string())

# ---- Figure: transition diagram ----
fig, ax = plt.subplots(figsize=(9, 6))
pos = {'Normal': (0.12, 0.75), 'CIND': (0.62, 0.75), 'Dementia': (0.62, 0.25), 'Death': (0.12, 0.25)}
colors = {'Normal': '#4C9F70', 'CIND': '#E8A33D', 'Dementia': '#C0392B', 'Death': '#5D6D7E'}
for k,(x,y) in pos.items():
    ax.add_patch(plt.Circle((x,y), 0.085, color=colors[k], alpha=0.9, zorder=3))
    ax.text(x, y, k, ha='center', va='center', color='white', fontsize=13, fontweight='bold', zorder=4)
Q = {('Normal','CIND'): 0.248, ('CIND','Normal'): 0.398,
     ('Normal','Dementia'): 0.001, ('CIND','Dementia'): 0.086,
     ('Normal','Death'): 0.019, ('CIND','Death'): 0.025, ('Dementia','Death'): 0.247,
     ('Dementia','CIND'): 0.320}
def arrow(p1, p2, lab, rad=0.0, lx=None, ly=None):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle='-|>', color='k', lw=1.4,
                                connectionstyle=f"arc3,rad={rad}", shrinkA=38, shrinkB=38))
    mx, my = (p1[0]+p2[0])/2 + (lx or 0), (p1[1]+p2[1])/2 + (ly or 0)
    ax.text(mx, my, lab, fontsize=10.5, ha='center', color='#1B2631',
            bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85))
arrow(pos['Normal'], pos['CIND'], "0.248", rad=-0.15, ly=0.045)
arrow(pos['CIND'], pos['Normal'], "0.398", rad=-0.15, ly=-0.06)
arrow(pos['Normal'], pos['Dementia'], "0.001", rad=-0.25, lx=-0.09, ly=0.075)
arrow(pos['CIND'], pos['Dementia'], "0.086", rad=0.0, lx=0.045)
arrow(pos['Dementia'], pos['CIND'], "0.320", rad=-0.3, lx=0.06, ly=-0.05)
arrow(pos['Normal'], pos['Death'], "0.019", rad=0.0, lx=-0.045)
arrow(pos['CIND'], pos['Death'], "0.025", rad=0.25, lx=0.03, ly=0.08)
arrow(pos['Dementia'], pos['Death'], "0.247", rad=-0.25, lx=-0.06, ly=-0.03)
ax.set_xlim(-0.02, 0.85); ax.set_ylim(0.08, 0.95); ax.axis('off')
ax.set_title("Annual transition intensities (per person-year), CHARLS 2018–2023", fontsize=13)
plt.tight_layout(); plt.savefig(f"{OUT}/fig1_transition_diagram.png", dpi=300); plt.close()

# ---- Figure: forest plot of stroke RRRs ----
rr = pd.read_csv(f"{OUT}/multinom_rrr.csv")
key = rr[rr['covariate'].isin(['stroke181','stroke_inc1'])].copy()
key['Exposure'] = key['covariate'].map({'stroke181':'Prevalent stroke (2018)','stroke_inc1':'Incident stroke (2018-W6)'})
key['Transition'] = key['baseline'] + " -> " + key['outcome']
key = key[key['U'] < 1e6]  # drop zero-cell rows
fig, ax = plt.subplots(figsize=(9, 6.5))
ypos = np.arange(len(key))[::-1]
cols = {'Prevalent stroke (2018)': '#2E5E8C', 'Incident stroke (2018-W6)': '#C0392B'}
for (y, (_, r)) in zip(ypos, key.iterrows()):
    c = cols[r['Transition'] and r['Exposure']]
    ax.plot([r['L'], r['U']], [y, y], color=c, lw=2)
    ax.plot(r['RRR'], y, 'o', color=c, ms=7)
ax.axvline(1, ls='--', color='grey')
ax.set_yticks(ypos); ax.set_yticklabels(key['Transition'] + "  |  " + key['Exposure'], fontsize=9)
ax.set_xscale('log'); ax.set_xlabel("Relative risk ratio (log scale)")
ax.set_title("Associations of prevalent and incident stroke with cognitive-state transitions\n(adjusted multinomial models)", fontsize=12)
plt.tight_layout(); plt.savefig(f"{OUT}/fig2_forest_stroke.png", dpi=300); plt.close()
print("figures saved")
