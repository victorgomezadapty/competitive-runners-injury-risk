# Final analysis and project completion

Date: 2026-10-26. Research release 1.0.0. Phase 2 remains the primary analysis; the following comparisons were specified after reviewing its results and are exploratory.

## Matched-event comparison

Day and Week inner join: 42,680 rows, 74 masked athletes, 575 positive labels; zero target disagreement. The 86 Day-only and 118 Week-only rows are excluded only from this matched comparison. This is not the full Day target population. Features: original daily 3/7-day summaries plus six interpretable 14/21-day load, rest and change variables. Ratios remain excluded. All compared models share exactly the same rows and partitions within a protocol/seed/fold; no comparison across different samples is presented as a causal effect.

Three protocols at seed 20261025, plus two alternative athlete partitions for the combined unseen-athlete/future question: 21 split cases, 84 fixed base fits and independent sigmoid calibrators. Temporal purging uses a common 21-day history (63 for known athletes) and 21-day source ascertainment. Training-only clipping, imputation and scaling. Inverse training-history weights equalize each athlete's total loss contribution, not injury-class frequency; calibration and evaluation retain source-sample weights. The fixed random forest uses 200 trees, depth 6, leaf minimum 30 and max_features 0.7. No hyperparameter search, test-based winner or clinical model release.

## Unseen athletes and future period

| seed | model | rows | positives | average_precision | roc_auc | brier |
|---|---|---|---|---|---|---|
| 20261025 | athlete_balanced_logistic_sigmoid | 7596 | 122 | 0.02001 | 0.54245 | 0.01582 |
| 20261025 | day_logistic_sigmoid | 7596 | 122 | 0.02032 | 0.54889 | 0.01584 |
| 20261025 | day_week_forest_sigmoid | 7596 | 122 | 0.01886 | 0.50657 | 0.01599 |
| 20261025 | day_week_logistic_sigmoid | 7596 | 122 | 0.02271 | 0.56702 | 0.01582 |
| 20261026 | athlete_balanced_logistic_sigmoid | 7596 | 122 | 0.02295 | 0.57879 | 0.01587 |
| 20261026 | day_logistic_sigmoid | 7596 | 122 | 0.02477 | 0.59159 | 0.01581 |
| 20261026 | day_week_forest_sigmoid | 7596 | 122 | 0.01804 | 0.55464 | 0.01586 |
| 20261026 | day_week_logistic_sigmoid | 7596 | 122 | 0.02265 | 0.58769 | 0.01583 |
| 20261027 | athlete_balanced_logistic_sigmoid | 7596 | 122 | 0.02318 | 0.57289 | 0.01585 |
| 20261027 | day_logistic_sigmoid | 7596 | 122 | 0.02956 | 0.57406 | 0.01584 |
| 20261027 | day_week_forest_sigmoid | 7596 | 122 | 0.02230 | 0.55725 | 0.01587 |
| 20261027 | day_week_logistic_sigmoid | 7596 | 122 | 0.02906 | 0.56685 | 0.01585 |

Differences across partitions show development uncertainty that the Phase 2 conditional cluster bootstrap does not capture. All partitions, raw/calibrated results and coefficients are retained. A tree comparison is methodological context; it does not establish clinical utility. Logistic coefficients are conditional standardized associations affected by correlated windows; not causal treatment effects. No strongest numerical row is promoted as the final predictor.

## Completed research deliverables

- Original files, checksum validation, corrected daily lag order, dictionary and source-specific target definitions.
- Full athlete, observation, follow-up-span, missingness, intensity, rest and subjective-response descriptions; five individual timelines and repeated-measures-aware paired descriptive contrasts.
- Past-only personal-history feasibility, known/future and unseen-athlete validation, disjoint calibration, imbalance-aware metrics, conditional athlete-cluster uncertainty and review-burden analysis.
- Matched longer-history comparisons, athlete-balanced fitting, fixed tree sensitivity and partition stability.
- Eleven authored notebooks; final two explore saved risk profiles and review budgets, without training a model in the browser.
- Literature-backed discussion, transparent narrative search, source bibliography, license inventory, reproducible public code/data packaging and interactive website.

## Analyses that the source cannot support

Exact calendar dates, complete clinical incidence, injury diagnosis/severity/location and complete time at risk cannot be recovered. No valid event lead time or false alerts per athlete-month can be calculated from this future-filtered sample. Twenty-eight-day windows are not created by filling unobserved days. Sex-specific analysis is unavailable at masked-participant level. Additional cohorts are independent; their participants cannot supply missing modalities here. Causal rest/load interventions, validated prevention and external clinical utility require new prospective surveillance.

The project is complete as a reproducible exploratory research case study. Clinical deployment, patient-specific recommendations and a claim of injury prevention are not supported deliverables.

## Reproduction

`python scripts/reproduce.py --notebooks` rebuilds the main analysis. Add `--complementary` to acquire and profile the separate companion sources. `cd web` then `npm run build` builds the static site. Kaggle's companion notebook independently checks the public data and saved results; the full model-fitting pipeline lives in GitHub.
