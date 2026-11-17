# Statistical Analysis Plan (SAP)

## Multi-state transitions of cognitive status among Chinese older adults: normal cognition → cognitive impairment no dementia (CIND) → dementia → death, 2018–2023 (CHARLS Waves 4–6)

**Project**: DementiaTransition_W6
**Date**: 2026-11-17
**Version**: 1.0 (pre-specified before model fitting)
**Data**: CHARLS Wave 4 (2018) and Wave 6 (2021–2023, first public release), plus Wave 5 (2020) Exit Module for death ascertainment.

---

## 1. Background and rationale

Dementia develops along a continuum. Most CHARLS cognition studies use continuous scores or single-threshold impairment; only two published works applied an algorithmic dementia classification to CHARLS (Gen Psychiatry 2023, cross-sectional prevalence in 2018; BMC Neurol 2026, incidence at 2018 from earlier waves). No study has modelled the full multi-state structure — including **reversion from CIND to normal cognition** — using the newly released Wave 6 (2021–2023) data, the first CHARLS wave after 2018 with both self-report cognition and informant (IQCODE) assessment. Stroke is a key modifiable vascular risk factor; its effect on each specific transition (onset of impairment, progression to dementia, recovery, death) has not been quantified in a Chinese national cohort.

## 2. Objectives

**Primary**: Estimate transition intensities among four states — normal cognition (1), CIND (2), dementia (3), death (4) — in Chinese adults ≥ 60 years between 2018 and W6 (2021–2023).

**Secondary**:
1. Quantify the association of stroke (prevalent at 2018; incident during follow-up) with each transition intensity.
2. Quantify recovery: probability and predictors of CIND → normal reversion.
3. Other risk factors: age, sex, education, residence, smoking, drinking, hypertension, diabetes, heart disease, depressive symptoms.

## 3. Study population

- Baseline: CHARLS 2018 (Wave 4) respondents aged ≥ 60 years at the 2018 interview.
- Follow-up: W6 = pooled 2021/2022/2023 releases (single wave executed 2021–2023), deduplicated by ID; death ascertainment from 2020 Exit Module and 2023 Sample_Infor (died flag).
- Inclusion: alive at 2018 interview, completed 2018 interview; classifiable cognitive state at 2018 (self-test and/or informant IQCODE) OR died before W6 with death date known.
- Exclusion: missing both cognitive data sources at 2018 and alive at W6 with no W6 data (loss to follow-up retained for descriptive reporting; main msm analysis uses observed panel states).

## 4. Cognitive status classification (algorithm)

Two data sources per wave: (a) self-administered cognitive battery; (b) informant questionnaire (IQCODE, 26 items, mean score).

### 4.1 Cognitive domains (self-test)

Five domains; each domain score = sum/average of constituent item scores; domain z-scores computed **within education strata** (illiterate / primary / middle school / high school or above) and **within wave**:

| Domain | 2018 items | W6 items |
|---|---|---|
| Orientation | dc001/002/003/005/006_w4 (year, season, day, month, week) | dc001–dc005 |
| Episodic memory | 10-word immediate (dc028–030_w4_s1..s10) + delayed (dc047_w4_s1..s10) + 3-word delayed recall (dc015) | xscorewr + xscoredr + dc023_s1..s3 |
| Executive function | serial 7s correctness (dc014_w4_1..5) + number series (dc029_w3 block) | serial 7s (dc017–dc021) + xnscorrectnum |
| Language | MMSE naming/repetition/reading/3-stage command/writing (dc016–dc023_w4 subset) + animal naming (dc032–dc039_w4, 2018 only) | MMSE naming (dc024/025), repetition (dc026), reading (dc027), 3-stage command (dc028–030), writing (dc031) |
| Visuospatial | copying overlapping pentagons (dc024_w4) | copying drawing (dc032) |

**Pre-specified deviation**: animal naming (verbal fluency) was removed from the W6 battery; the language domain is therefore constructed from MMSE language items common to both waves. A sensitivity check compares the 2018 language domain with and without animal naming.

Domain impairment: domain z < −1.5 SD below the education-stratum mean (Gen Psychiatry 2023 convention). Single-item domains (visuospatial) are coded impaired if the item is failed.

### 4.2 State definitions

- **Dementia (state 3)**: ≥ 2 domains impaired AND IQCODE ≥ 3.6.
- **Proxy-only rule**: participants with no usable self-test but a valid IQCODE are classified as dementia if IQCODE ≥ 3.6 AND ≥ 1 ADL impairment; otherwise CIND if IQCODE ≥ 3.19, else normal.
- **CIND (state 2)**: not dementia, and (≥ 1 domain impaired OR 3.19 ≤ IQCODE < 3.6).
- **Normal (state 1)**: all remaining classifiable participants.
- **Death (state 4)**: absorbing; death date from 2020 Exit Module (exb001_1/2/3) when available; otherwise died flag from 2023 Sample_Infor with date interval-censored between 2018 interview and the W6 survey reference date.

IQCODE requires ≥ 13 of 26 items non-missing; score = mean of answered items.

### 4.3 ADL impairment

6 basic ADL items (dressing, bathing, eating, getting in/out of bed, toileting, continence): 2018 db010–db015; W6 db001/db003/db005/db007/db009/db011. Item impaired if response ≥ 2 (has difficulty). ADL impaired = any item impaired.

## 5. Covariates (2018 baseline unless noted)

- Age at 2018 interview (from ba002_1 birth year and Sample_Infor iyear/imonth), sex (xrgender), education (4 strata), residence (urban/rural), marital status (be001), smoking (da059 ever), drinking (da067 past-year frequency ≥ monthly), hypertension / diabetes / heart disease (da007_2_ / da007_5_ / da007_7_), depressive symptoms (CES-D-10 ≥ 10; 2018 dc009–dc018).
- **Stroke**: prevalent stroke at 2018 (da007_8_ = 1); **incident stroke**: no stroke in 2018 and stroke reported at W6 (da011_8_ = 1) or informant-reported stroke at W6 (dd012 = 1). Incident stroke enters models as a time-fixed covariate (limitation acknowledged).

## 6. Statistical analysis

### 6.1 Main model

Continuous-time Markov multi-state model for panel data (`msm` R package). States 1–4; permitted transitions: 1↔2, 2↔3, 1→3, 1→4, 2→4, 3→4. Observation times: actual interview dates (2018: iyear/imonth, day=15 if unknown; W6: iyear/imonth). Deaths with exact dates are treated as exact death times; deaths known only by died flag use the midpoint between last known alive date and W6 reference date (sensitivity: interval-censoring approach if feasible).

Misclassification is **not** modelled in the primary analysis (the algorithm already blends two sources); a sensitivity model adds a misclassification matrix.

### 6.2 Outputs

- Transition intensity matrix (Q) with 95% CIs.
- Hazard ratios for each covariate on each permitted transition.
- Sojourn times per transient state.
- 5-year transition probabilities from each 2018 state; state occupancy probabilities over time.
- Recovery: estimated intensity and 5-year probability of CIND → normal.

### 6.3 Sensitivity analyses

1. IQCODE cutoffs: dementia 3.48 / 3.9; CIND lower bound 3.19 / 3.44.
2. Dementia definition additionally requiring ADL impairment (BMC Neurol 2026 convention).
3. Alternative outcome: informant-reported doctor diagnosis of dementia/Alzheimer's or memory-related disease (dd014/dd015).
4. Death timing: exact dates only vs midpoint imputation.
5. Misclassification-adjusted msm.

### 6.4 Missing data

Item-level: domain score computed if ≥ 60% of items present (word recall ≥ 8/10 words scored). IQCODE ≥ 13/26. Participants unclassifiable at both waves are excluded; baseline characteristics compared between included/excluded. Complete-case covariate analysis (missing covariates < 5% expected; otherwise multiple imputation with mice).

### 6.5 Software

Python 3 (pandas) for data construction; R 4.6.2 with `msm`, `survival`, `ggplot2` for analysis. Two-sided α = 0.05.

## 7. Reporting

STROBE checklist; flow diagram of sample selection; table of baseline characteristics by 2018 state; transition diagram with annualized intensities; forest plot of HRs for stroke on each transition.
