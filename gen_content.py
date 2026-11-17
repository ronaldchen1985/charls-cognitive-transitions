"""Generate JSON content for docx-js builders from manuscript.md and output CSVs."""
import json, re, csv, os

ROOT = r"D:\CHARLS\DementiaTransition_W6"
OUT = os.path.join(ROOT, "output")
SUB = os.path.join(ROOT, "submission")
os.makedirs(SUB, exist_ok=True)

def parse_runs(text):
    """Split **bold** and *italic* markers into run dicts."""
    text = text.replace("`", "")
    runs = []
    parts = re.split(r"\*\*", text)
    for i, part in enumerate(parts):
        bold = (i % 2 == 1)
        sub = re.split(r"\*", part)
        for j, seg in enumerate(sub):
            if not seg:
                continue
            runs.append({"t": seg, "bold": bold, "ital": (j % 2 == 1) and not bold})
    return runs

def parse_md(path, stop_at=None):
    blocks = []
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    for ln in lines:
        s = ln.strip()
        if stop_at and s.startswith(stop_at):
            break
        if not s or s == "---":
            continue
        m = re.match(r"^(#{1,3})\s+(.*)", s)
        if m:
            lvl = len(m.group(1))
            blocks.append({"type": f"h{lvl}", "runs": parse_runs(m.group(2))})
        else:
            blocks.append({"type": "p", "runs": parse_runs(s)})
    return blocks

def read_csv(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.reader(f))

# ---------- main manuscript ----------
main = {"title": ("Transitions between normal cognition, cognitive impairment no "
                  "dementia, dementia, and death in Chinese older adults: a multi-state "
                  "analysis of the CHARLS 2018\u20132023 cohort with a focus on stroke"),
        "running": "Cognitive state transitions and stroke in CHARLS",
        "blocks": parse_md(os.path.join(ROOT, "manuscript", "manuscript.md"),
                           stop_at="## Tables")}

# Table 1
t1 = read_csv(os.path.join(OUT, "table1_baseline.csv"))
t1[0] = ["Characteristic", "Normal cognition (n = 5,319)", "CIND (n = 4,423)", "Dementia (n = 886)"]
main["table1"] = t1

# Table 2: observed transitions (counts and row %)
counts = {"Normal": [2740, 1227, 123, 314], "CIND": [1673, 1265, 155, 300],
          "Dementia": [113, 123, 65, 80]}
t2 = [["2018 state", "N", "W6: Normal, n (%)", "W6: CIND, n (%)",
       "W6: Dementia, n (%)", "W6: Death, n (%)"]]
for k, v in counts.items():
    n = sum(v)
    row = [k, str(n)] + [f"{x} ({100*x/n:.1f}%)" for x in v]
    t2.append(row)
main["table2"] = t2

# Table 3: 5-year transition probabilities (point estimates)
t3 = [["2018 state", "Normal", "CIND", "Dementia", "Death"],
      ["Normal", "54.4", "29.5", "4.0", "12.0"],
      ["CIND", "47.2", "30.9", "5.5", "16.3"],
      ["Dementia", "23.4", "20.4", "9.0", "47.2"],
      ["Death", "0", "0", "0", "100"]]
main["table3"] = t3

# Table 4: full adjusted RRRs
covlab = {"(Intercept)": "(Intercept)", "agez": "Age, per SD", "female1": "Female",
          "edu41": "Education: primary (ref illiterate)", "edu42": "Education: middle school (ref illiterate)",
          "edu43": "Education: high school+ (ref illiterate)", "married1": "Married/cohabiting",
          "drink1": "Past-year drinking", "htn1": "Hypertension", "dm1": "Diabetes",
          "heart1": "Heart disease", "stroke181": "Prevalent stroke (2018)",
          "stroke_inc1": "Incident stroke (2018\u2013W6)", "cesd101": "CES-D-10 \u2265 10"}
t4 = [["Baseline state", "W6 outcome", "Covariate", "RRR (95% CI)", "P"]]
with open(os.path.join(OUT, "multinom_rrr.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rrr, lo, up = float(r["RRR"]), float(r["L"]), float(r["U"])
        if up > 1e6:
            est = "not estimable (no events)"
        else:
            est = f"{rrr:.2f} ({lo:.2f}\u2013{up:.2f})"
        pv = float(r["p"])
        ps = "<0.001" if pv < 0.001 else f"{pv:.3f}"
        t4.append([r["baseline"], r["outcome"], covlab.get(r["covariate"], r["covariate"]), est, ps])
main["table4"] = t4

main["figures"] = [
    {"path": os.path.join(SUB, "figures", "fig0_flowchart.png"),
     "legend": ("Figure 1 (STROBE flow diagram). Derivation of the analysis samples. "
                "The continuous-time multi-state model was fitted on the analysis panel "
                "(n = 9,679); adjusted multinomial models used the complete-case sample "
                "(n = 8,178); multiple-imputation sensitivity used the full panel."),
     "w": 480, "h": 400},
    {"path": os.path.join(SUB, "figures", "fig2_transition_diagram.png"),
     "legend": ("Figure 2. Annual transition intensities (per person-year) between cognitive "
                "states and death, continuous-time Markov model, CHARLS 2018\u20132021/23 "
                "(full analysis panel, n = 9,679)."),
     "w": 520, "h": 349},
    {"path": os.path.join(SUB, "figures", "fig3_forest_stroke.png"),
     "legend": ("Figure 3. Adjusted relative risk ratios (RRRs) for prevalent (2018) and incident "
                "(2018\u2013W6) stroke on each cognitive-state transition, from baseline-state-"
                "stratified multinomial models (complete-case sample, n = 8,178). Transitions with "
                "no events are not shown (not estimable)."),
     "w": 560, "h": 409},
    {"path": os.path.join(SUB, "figures", "fig4_5yr_probabilities.png"),
     "legend": ("Figure 4. Five-year transition probabilities from the time-homogeneous Markov "
                "model (left bar of each pair) vs directly observed 2018\u2192W6 proportions "
                "(right bar, lighter shading), by baseline state. Modelled probabilities extrapolate to a "
                "full 5-year horizon; observed proportions cover a shorter window (W6 interviews "
                "at 3.3\u20135.6 years)."),
     "w": 600, "h": 272},
]
with open(os.path.join(SUB, "content_main.json"), "w", encoding="utf-8") as f:
    json.dump(main, f, ensure_ascii=False, indent=1)

# ---------- supplementary ----------
supp = {"title": "Supplementary Material",
        "subtitle": main["title"]}

# S1: IQCODE cutoff sensitivity (stroke RRRs)
s1 = [["IQCODE dementia cut-off", "Baseline state", "W6 outcome",
       "Prevalent stroke RRR (95% CI)", "Incident stroke RRR (95% CI)"]]
sens = {("348","Normal","CIND"): ("0.86 (0.62\u20131.18)", "1.94 (1.36\u20132.76)"),
        ("348","Normal","Dementia"): ("1.67 (0.88\u20133.15)", "2.71 (1.25\u20135.87)"),
        ("348","Normal","Death"): ("1.55 (1.01\u20132.37)", "not estimable (no events)"),
        ("348","CIND","Normal"): ("1.13 (0.81\u20131.58)", "0.83 (0.55\u20131.25)"),
        ("348","CIND","Dementia"): ("2.47 (1.36\u20134.48)", "0.40 (0.09\u20131.66)"),
        ("348","CIND","Death"): ("1.61 (0.97\u20132.66)", "not estimable (no events)"),
        ("39","Normal","CIND"): ("1.04 (0.75\u20131.43)", "2.27 (1.54\u20133.34)"),
        ("39","Normal","Dementia"): ("2.47 (1.11\u20135.52)", "2.86 (0.84\u20139.71)"),
        ("39","Normal","Death"): ("1.62 (1.00\u20132.64)", "not estimable (no events)"),
        ("39","CIND","Normal"): ("1.07 (0.81\u20131.40)", "0.77 (0.54\u20131.10)"),
        ("39","CIND","Dementia"): ("1.90 (1.06\u20133.42)", "0.73 (0.26\u20132.04)"),
        ("39","CIND","Death"): ("1.51 (0.99\u20132.28)", "not estimable (no events)")}
for (cut, b, o), (pv, iv) in sens.items():
    s1.append(["3.48" if cut == "348" else "3.9", b, o, pv, iv])

# S2: attrition
s2 = read_csv(os.path.join(OUT, "tableS2_attrition.csv"))

# S3: strict CIND
s3a = [["2018 state", "N", "W6: Normal, n (%)", "W6: CIND, n (%)", "W6: Dementia, n (%)", "W6: Death, n (%)"]]
scounts = {"Normal": [4880, 787, 146, 442], "CIND": [868, 419, 83, 172], "Dementia": [139, 64, 98, 80]}
for k, v in scounts.items():
    n = sum(v)
    s3a.append([k, str(n)] + [f"{x} ({100*x/n:.1f}%)" for x in v])
s3b = [["Baseline state", "W6 outcome", "Prevalent stroke RRR (95% CI)", "Incident stroke RRR (95% CI)"],
       ["Normal", "CIND", "0.94 (0.66\u20131.33)", "2.32 (1.65\u20133.27)"],
       ["Normal", "Dementia", "2.04 (1.19\u20133.48)", "1.54 (0.66\u20133.62)"],
       ["Normal", "Death", "1.60 (1.11\u20132.31)", "not estimable (no events)"],
       ["CIND", "Normal", "0.90 (0.55\u20131.47)", "0.59 (0.34\u20131.02)"],
       ["CIND", "Dementia", "1.80 (0.81\u20133.98)", "0.16 (0.02\u20131.24)"],
       ["CIND", "Death", "1.32 (0.69\u20132.53)", "not estimable (no events)"]]
s3c = [["Transition", "Intensity per year (95% CI)"],
       ["Normal \u2192 CIND", "0.096 (0.087\u20130.106)"],
       ["Normal \u2192 Dementia", "0.008 (0.006\u20130.013)"],
       ["Normal \u2192 Death", "0.018 (0.016\u20130.021)"],
       ["CIND \u2192 Normal", "0.384 (0.355\u20130.416)"],
       ["CIND \u2192 Dementia", "0.066 (0.051\u20130.086)"],
       ["CIND \u2192 Death", "0.054 (0.045\u20130.066)"],
       ["Dementia \u2192 CIND", "0.248 (0.217\u20130.284)"],
       ["Dementia \u2192 Death", "0.213 (0.188\u20130.242)"]]
s3d = [["2018 state", "Normal", "CIND", "Dementia", "Death"],
       ["Normal", "70.3", "14.5", "2.9", "12.3"],
       ["CIND", "55.7", "19.0", "4.8", "20.4"],
       ["Dementia", "23.8", "15.0", "12.5", "48.7"]]

# S4: MI vs complete-case stroke RRRs
s4 = [["Baseline state", "W6 outcome", "Exposure", "Complete-case RRR (95% CI)", "MI-pooled RRR (95% CI)"]]
cc_rows = {("Normal","CIND","stroke181"): "0.88 (0.64\u20131.21)",
           ("Normal","CIND","stroke_inc1"): "1.66 (1.14\u20132.41)",
           ("Normal","Dementia","stroke181"): "2.02 (1.07\u20133.84)",
           ("Normal","Dementia","stroke_inc1"): "6.47 (3.59\u201311.67)",
           ("Normal","Death","stroke181"): "1.47 (0.93\u20132.32)",
           ("CIND","Normal","stroke181"): "1.30 (0.95\u20131.78)",
           ("CIND","Normal","stroke_inc1"): "0.87 (0.59\u20131.29)",
           ("CIND","Dementia","stroke181"): "2.43 (1.40\u20134.23)",
           ("CIND","Dementia","stroke_inc1"): "0.82 (0.32\u20132.11)",
           ("CIND","Death","stroke181"): "1.95 (1.23\u20133.09)",
           ("Dementia","Normal","stroke181"): "0.68 (0.27\u20131.73)",
           ("Dementia","Normal","stroke_inc1"): "0.31 (0.09\u20131.03)",
           ("Dementia","CIND","stroke181"): "0.86 (0.35\u20132.09)",
           ("Dementia","CIND","stroke_inc1"): "0.61 (0.22\u20131.69)",
           ("Dementia","Death","stroke181"): "1.07 (0.42\u20132.77)"}
mi_rows = {("Normal","CIND","stroke181"): "0.82 (0.60\u20131.12)",
           ("Normal","CIND","stroke_inc1"): "1.41 (0.98\u20132.02)",
           ("Normal","Dementia","stroke181"): "1.90 (1.03\u20133.51)",
           ("Normal","Dementia","stroke_inc1"): "5.54 (3.18\u20139.67)",
           ("Normal","Death","stroke181"): "1.44 (0.93\u20132.22)",
           ("CIND","Normal","stroke181"): "1.31 (0.97\u20131.76)",
           ("CIND","Normal","stroke_inc1"): "0.84 (0.58\u20131.21)",
           ("CIND","Dementia","stroke181"): "2.20 (1.35\u20133.57)",
           ("CIND","Dementia","stroke_inc1"): "0.72 (0.32\u20131.61)",
           ("CIND","Death","stroke181"): "2.09 (1.40\u20133.13)",
           ("Dementia","Normal","stroke181"): "0.47 (0.24\u20130.92)",
           ("Dementia","Normal","stroke_inc1"): "0.23 (0.08\u20130.67)",
           ("Dementia","CIND","stroke181"): "0.50 (0.27\u20130.93)",
           ("Dementia","CIND","stroke_inc1"): "0.45 (0.20\u20131.01)",
           ("Dementia","Death","stroke181"): "0.98 (0.58\u20131.66)"}
for k, cc in cc_rows.items():
    b, o, cov = k
    s4.append([b, o, "Prevalent stroke (2018)" if cov == "stroke181" else "Incident stroke (2018\u2013W6)",
               cc, mi_rows[k]])

supp["sections"] = [
    {"heading": "Supplementary Table S1. Sensitivity to the IQCODE dementia cut-off: adjusted stroke RRRs under cut-offs 3.48 and 3.9 (main analysis: 3.6)",
     "table": s1},
    {"heading": "Supplementary Table S2. Baseline characteristics of participants retained vs lost to follow-up",
     "table": s2},
    {"heading": "Supplementary Table S3a. Strict-CIND-definition sensitivity: observed 2018\u2192W6 transitions (CIND requires \u2265 1 impaired domain AND IQCODE 3.19\u20133.6; CIND prevalence 21.5%)",
     "table": s3a},
    {"heading": "Supplementary Table S3b. Strict-CIND-definition sensitivity: adjusted stroke RRRs",
     "table": s3b},
    {"heading": "Supplementary Table S3c. Strict-CIND-definition sensitivity: annual transition intensities (null msm, n = 9,679)",
     "table": s3c},
    {"heading": "Supplementary Table S3d. Strict-CIND-definition sensitivity: model-based 5-year transition probabilities (%)",
     "table": s3d},
    {"heading": "Supplementary Table S4. Multiple-imputation (m = 20) sensitivity: pooled stroke RRRs vs complete-case estimates",
     "table": s4},
]
supp["figure"] = {"path": os.path.join(SUB, "figures", "figS1_gof.png"),
                  "legend": ("Supplementary Figure S1. Goodness of fit: observed (points) vs "
                             "model-expected (lines) prevalence of the three transient states, "
                             "continuous-time Markov null model (n = 9,679). Death is excluded "
                             "from the comparison because death times were interval-midpoint "
                             "imputed, making the modelled death-time distribution uninformative "
                             "for fit assessment."),
                  "w": 520, "h": 358}
with open(os.path.join(SUB, "content_supp.json"), "w", encoding="utf-8") as f:
    json.dump(supp, f, ensure_ascii=False, indent=1)
print("content JSON written")
