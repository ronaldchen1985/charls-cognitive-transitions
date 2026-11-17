# Cognitive state transitions and stroke in CHARLS 2018–2023

Analysis code for the manuscript:

> *Transitions between normal cognition, cognitive impairment no dementia, dementia, and death in Chinese older adults: a multi-state analysis of the CHARLS 2018–2023 cohort with a focus on stroke*

## Data

This repository contains **code only**. No CHARLS data are included or redistributed,
in accordance with the CHARLS data-use agreement. CHARLS data (wave 4, 2018; 2020 exit
module; wave 6, 2021–2023) are available to registered researchers from the CHARLS
project team at Peking University: https://charls.pku.edu.cn

All analysis datasets can be regenerated from the public CHARLS files using the
scripts below.

## Pipeline (run order)

| Step | Script | Purpose |
|------|--------|---------|
| 1 | `build_dataset.py` | Build the analysis panel and covariate file from raw CHARLS waves; cognitive-state classification (normal / CIND / dementia) per the pre-specified algorithm |
| 2 | `refit_null_full.R` | Continuous-time Markov multi-state null model (R `msm`), full panel (n = 9,679): intensities, sojourn times, transition probabilities |
| 3 | `analysis_multinom.R` | Baseline-state-stratified multinomial logistic models (complete case, n = 8,178): adjusted RRRs for all covariates |
| 4 | `sens_cutoffs.py`, `sens_multinom.R` | Sensitivity: IQCODE dementia cut-offs 3.48 / 3.9 |
| 5 | `sens_strictCIND.py`, `sens_strictCIND.R` | Sensitivity: strict CIND definition (≥ 1 impaired domain AND IQCODE 3.19–3.6) |
| 6 | `mi_impute.R`, `mi_pool.R` | Sensitivity: multiple imputation of missing covariates (m = 20) with Rubin's-rule pooling |
| 7 | `msm_misclass.R` | Attempted misclassification msm (documented as non-identifiable with a two-wave panel) |
| 8 | `gof_export.R`, `gof_plot.R` | Goodness-of-fit data export and check |
| 9 | `table1_figures.py`, `figures_final.py` | Tables and publication figures (PNG/PDF/SVG/TIFF) |
| 10 | `gen_content.py` | Content assembly for the submission documents |

## Pre-specification

`SAP.md` (statistical analysis plan) and `SAP_amendments.md` (dated amendments) are
included for transparency.

## Environment

- Python 3 (pandas, numpy, matplotlib)
- R 4.6.2 (`msm`, `nnet`, `mice`)

## License

MIT (code). No data are licensed or redistributed here.
