"""Final publication figures (nature-figure pipeline, Python backend exclusive).
Re-renders all 5 figures with skill rcParams; exports PNG(600)+PDF+SVG+TIFF;
multi-panel figures pass the mandatory panel-alignment gate before export.
"""
import sys, os
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

NS_SCRIPTS = (r"C:\Users\ronaldchen\AppData\Roaming\kimi-desktop\daimon-share"
              r"\plugin-sources\nature-skills\nature-skills\skills\nature-figure\scripts")
sys.path.insert(0, NS_SCRIPTS)
from audit_panel_alignment import require_matplotlib_panel_alignment

OUT = r"D:\CHARLS\DementiaTransition_W6\output"
FIG = r"D:\CHARLS\DementiaTransition_W6\submission\figures"
os.makedirs(FIG, exist_ok=True)

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
})

def save_pub(fig, name, multi=False):
    if multi:
        require_matplotlib_panel_alignment(
            fig, json_out=os.path.join(FIG, f"{name}.alignment.json"),
            overlay_svg=os.path.join(FIG, f"{name}.alignment.svg"),
            tolerance_pt=1.5, gutter_tolerance_pt=1.5, strict=True)
    fig.savefig(os.path.join(FIG, f"{name}.png"), dpi=600, bbox_inches="tight")
    fig.savefig(os.path.join(FIG, f"{name}.pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(FIG, f"{name}.svg"), bbox_inches="tight")
    fig.savefig(os.path.join(FIG, f"{name}.tiff"), dpi=600, bbox_inches="tight")
    plt.close(fig)
    print(name, "saved")

C = {"Normal": "#4C9F70", "CIND": "#E8A33D", "Dementia": "#C0392B", "Death": "#5D6D7E"}

# ============ Figure 1: STROBE flowchart ============
fig, ax = plt.subplots(figsize=(7.2, 6.0))
ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
def box(x, y, w, h, text, fc="#F4F6F7", fs=8):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.12",
                                fc=fc, ec="#2E4053", lw=1.0))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs)
def earrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=12, color="#2E4053", lw=1.0))
box(1.6, 8.6, 4.2, 1.1, "CHARLS wave 4 (2018)\ninterviewed, n = 20,813")
box(1.6, 6.8, 4.2, 1.1, "Aged \u2265 60 years at 2018 interview\nn = 11,043")
box(6.6, 6.8, 3.0, 1.1, "Excluded: age < 60\nn = 9,770", fc="#FBEEE6")
box(1.6, 5.0, 4.2, 1.1, "Classifiable 2018 cognitive state\nn = 10,628")
box(6.6, 5.0, 3.0, 1.1, "Unclassifiable 2018 state\nn = 415", fc="#FBEEE6")
box(1.6, 3.2, 4.2, 1.1, "Analysis panel: wave-6 outcome\nor death record, n = 9,679")
box(6.6, 3.2, 3.0, 1.1, "Lost to follow-up\nn = 949 (8.9%)", fc="#FBEEE6")
box(1.6, 1.4, 4.2, 1.1, "Complete-case sample for adjusted\nmultinomial models, n = 8,178")
box(6.6, 1.4, 3.0, 1.1, "Missing covariates\nn = 1,501", fc="#FBEEE6")
earrow(3.7, 8.6, 3.7, 8.02)
earrow(3.7, 6.8, 3.7, 6.22); earrow(5.8, 7.35, 6.6, 7.35)
earrow(3.7, 5.0, 3.7, 4.42); earrow(5.8, 5.55, 6.6, 5.55)
earrow(3.7, 3.2, 3.7, 2.62); earrow(5.8, 3.75, 6.6, 3.75)
ax.text(5.0, 0.6, "Multi-state model fitted on n = 9,679; multinomial models on n = 8,178;\n"
        "multiple-imputation sensitivity on n = 9,679",
        ha="center", fontsize=7.5, style="italic", color="#424949")
save_pub(fig, "fig1_flowchart")

# ============ Figure 2: transition diagram ============
fig, ax = plt.subplots(figsize=(7.0, 4.7))
pos = {"Normal": (0.12, 0.75), "CIND": (0.62, 0.75), "Dementia": (0.62, 0.25), "Death": (0.12, 0.25)}
for k, (x, y) in pos.items():
    ax.add_patch(plt.Circle((x, y), 0.085, color=C[k], alpha=0.9, zorder=3))
    ax.text(x, y, k, ha="center", va="center", color="white", fontsize=11,
            fontweight="bold", zorder=4)
def arrow(p1, p2, lab, rad=0.0, lx=None, ly=None):
    ax.annotate("", xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="-|>", color="k", lw=1.2,
                                connectionstyle=f"arc3,rad={rad}", shrinkA=38, shrinkB=38))
    mx, my = (p1[0]+p2[0])/2 + (lx or 0), (p1[1]+p2[1])/2 + (ly or 0)
    ax.text(mx, my, lab, fontsize=9, ha="center", color="#1B2631")
arrow(pos["Normal"], pos["CIND"], "0.248", rad=-0.15, lx=-0.07, ly=0.075)
arrow(pos["CIND"], pos["Normal"], "0.398", rad=-0.15, lx=-0.14, ly=-0.105)
arrow(pos["Normal"], pos["Dementia"], "0.001", rad=-0.25, lx=-0.155, ly=0.10)
arrow(pos["CIND"], pos["Dementia"], "0.086", rad=0.0, lx=0.075, ly=0.035)
arrow(pos["Dementia"], pos["CIND"], "0.320", rad=-0.3, lx=0.115, ly=-0.045)
arrow(pos["Normal"], pos["Death"], "0.019", rad=0.0, lx=-0.075)
arrow(pos["CIND"], pos["Death"], "0.025", rad=0.25, lx=0.10, ly=0.16)
arrow(pos["Dementia"], pos["Death"], "0.247", rad=-0.25, lx=-0.13, ly=-0.115)
ax.set_xlim(-0.02, 0.85); ax.set_ylim(0.08, 0.95); ax.axis("off")
ax.set_title("Annual transition intensities (per person-year), CHARLS 2018\u20132023", fontsize=11)
save_pub(fig, "fig2_transition_diagram")

# ============ Figure 3: forest plots of stroke RRRs (two panels) ============
rr = pd.read_csv(os.path.join(OUT, "multinom_rrr.csv"))
key = rr[rr["covariate"].isin(["stroke181", "stroke_inc1"])].copy()
key["Transition"] = key["baseline"] + " \u2192 " + key["outcome"]
key = key[(key["U"] < 1e6) & (key["RRR"] > 0)]
order = [("Normal","CIND"),("Normal","Dementia"),("Normal","Death"),
         ("CIND","Normal"),("CIND","Dementia"),("CIND","Death"),
         ("Dementia","Normal"),("Dementia","CIND"),("Dementia","Death")]
key["ord"] = key.apply(lambda r: order.index((r["baseline"], r["outcome"])), axis=1)
panels = [("a", "stroke181", "Prevalent stroke (baseline 2018)", "#2E5E8C"),
          ("b", "stroke_inc1", "Incident stroke (follow-up survivors)", "#C0392B")]
fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.6))
for ax, (letter, cov, title, col) in zip(axes, panels):
    d = key[key["covariate"] == cov].sort_values("ord", ascending=False).reset_index(drop=True)
    ypos = np.arange(len(d)) * 1.0
    for y, (_, r) in zip(ypos, d.iterrows()):
        sig = (r["L"] > 1) or (r["U"] < 1)
        ax.plot([r["L"], r["U"]], [y, y], color=col, lw=1.8,
                alpha=1.0 if sig else 0.45, solid_capstyle="round", zorder=2)
        ax.plot(r["RRR"], y, "o", color=col, ms=6.5, mec="white", mew=1.0,
                alpha=1.0 if sig else 0.45, zorder=3)
        ax.text(26, y, f'{r["RRR"]+1e-9:.2f} ({r["L"]+1e-9:.2f}\u2013{r["U"]+1e-9:.2f})',
                va="center", fontsize=7.5, color="#1B2631" if sig else "#7B8794")
    ax.axvline(1, ls="--", color="grey", lw=0.9)
    ax.set_yticks(ypos)
    ax.set_yticklabels(d["Transition"], fontsize=8.5)
    ax.set_ylim(-0.7, len(d) + 0.55)
    ax.set_xscale("log"); ax.set_xlim(0.05, 55)
    ax.set_xticks([0.1, 0.25, 0.5, 1, 2, 4, 8, 16])
    ax.set_xticklabels(["0.1", "0.25", "0.5", "1", "2", "4", "8", "16"], fontsize=8)
    ax.set_xlabel("Adjusted RRR (log scale)", fontsize=9)
    ax.text(26, len(d) + 0.18, "RRR (95% CI)", fontsize=8, fontweight="bold")
    ax.grid(axis="x", color="#EAECEE", lw=0.6, zorder=0)
    ax.set_title(f"{letter}   {title}", fontsize=10, loc="left", pad=8,
                 fontweight="bold", color=col)
fig.suptitle("Associations of stroke with cognitive-state transitions, by baseline state",
             fontsize=10.5, y=1.00)
fig.tight_layout(rect=[0, 0, 1, 0.96])
save_pub(fig, "fig3_forest_stroke", multi=True)

# ============ Figure 4: 5-year probabilities vs observed (multi-panel) ============
states = ["Normal", "CIND", "Dementia", "Death"]
colors = [C[s] for s in states]
model5 = {"Normal": [54.4, 29.5, 4.0, 12.0], "CIND": [47.2, 30.9, 5.5, 16.3],
          "Dementia": [23.4, 20.4, 9.0, 47.2]}
observed = {"Normal": [62.2, 27.9, 2.8, 7.1], "CIND": [49.3, 37.3, 4.6, 8.8],
            "Dementia": [29.7, 32.3, 17.1, 21.0]}
fig, axes = plt.subplots(1, 3, figsize=(8.6, 3.9), sharey=True)
for ax, base in zip(axes, ["Normal", "CIND", "Dementia"]):
    for j, (vals, hatch) in enumerate([(model5[base], ""), (observed[base], "")]):
        left = 0
        for v, c in zip(vals, colors):
            ax.bar(j, v, bottom=left, color=c, width=0.62, edgecolor="none",
                   lw=0, alpha=1.0 if j == 0 else 0.55)
            if v >= 4:
                ax.text(j, left + v/2, f"{v:.0f}", ha="center", va="center",
                        fontsize=7.5, color="white", fontweight="bold")
            left += v
    ax.set_title(f"Baseline: {base}", fontsize=10)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Modelled\n5-year", "Observed\n2018\u2013W6"], fontsize=8)
    ax.set_ylim(0, 100)
    ax.tick_params(labelsize=8)
axes[0].set_ylabel("Probability / proportion (%)", fontsize=9)
handles = [plt.Rectangle((0, 0), 1, 1, fc=c) for c in colors]
fig.legend(handles, states, ncol=4, loc="lower center", fontsize=9)
fig.suptitle("Five-year transition probabilities (time-homogeneous model) vs observed proportions",
             fontsize=10.5, y=0.99)
fig.tight_layout(rect=[0, 0.08, 1, 0.94])
save_pub(fig, "fig4_5yr_probabilities", multi=True)

# ============ Supplementary Figure S1: GOF (redrawn in Python from exported data) ============
g = pd.read_csv(os.path.join(OUT, "gof_data.csv"))
keep = (g["obsT"] >= 1500) & (g["t"] <= 4.5)
gk = g[keep]
fig, ax = plt.subplots(figsize=(6.4, 4.4))
for j, (lab, c) in enumerate(zip(["Normal cognition", "CIND", "Dementia"],
                                 [C["Normal"], C["CIND"], C["Dementia"]])):
    ax.plot(gk["t"], 100*gk[f"obs{j+1}"]/gk["obsT"], "o", color=c, ms=5.5, label=lab)
    ax.plot(gk["t"], 100*gk[f"exp{j+1}"]/gk["expT"], "-", color=c, lw=1.6)
ax.set_xlabel("Years since July 2018", fontsize=9)
ax.set_ylabel("Prevalence (%)", fontsize=9)
ax.tick_params(labelsize=8)
ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1.02, 0.5))
ax.set_title("Observed (points) vs model-expected (lines)\ntransient-state prevalence", fontsize=10)
save_pub(fig, "figS1_gof")
print("ALL FIGURES DONE")
