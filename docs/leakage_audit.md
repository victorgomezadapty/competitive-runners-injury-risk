# Leakage audit

Milestone 1 historical audit; Phase 2 fixed baselines are now fitted, as documented in the extension below. Every implemented descriptive summary and proposed candidate is registered below. Prediction cutoff t=E-1; outcome at E. `data/interim/reconstructed_training_days.csv` is retrospective visualization only.

| Feature | Observation window | Prediction date/cutoff | Potential leakage risk | Decision |
|---|---|---|---|---|
| `distance_3d` | E-3..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `z3_4_distance_3d` | E-3..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `z5_t1_t2_distance_3d` | E-3..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `sprint_distance_3d` | E-3..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `sessions_3d` | E-3..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `strength_sessions_3d` | E-3..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `cross_training_hours_3d` | E-3..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `rest_days_3d` | E-3..E-1 | E / end of E-1 | Low in own row | Descriptive only, implemented within own row |
| `mean_exertion_3d` | E-3..E-1 | E / end of E-1 | Low in own row | Descriptive only, implemented within own row |
| `observed_exertion_days_3d` | E-3..E-1 | E / end of E-1 | Low temporal risk; recording-process proxy | Descriptive only, implemented within own row |
| `mean_training_success_3d` | E-3..E-1 | E / end of E-1 | Low in own row | Descriptive only, implemented within own row |
| `observed_training_success_days_3d` | E-3..E-1 | E / end of E-1 | Low temporal risk; recording-process proxy | Descriptive only, implemented within own row |
| `mean_recovery_3d` | E-3..E-1 | E / end of E-1 | Low in own row | Descriptive only, implemented within own row |
| `observed_recovery_days_3d` | E-3..E-1 | E / end of E-1 | Low temporal risk; recording-process proxy | Descriptive only, implemented within own row |
| `distance_7d` | E-7..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `z3_4_distance_7d` | E-7..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `z5_t1_t2_distance_7d` | E-7..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `sprint_distance_7d` | E-7..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `sessions_7d` | E-7..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `strength_sessions_7d` | E-7..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `cross_training_hours_7d` | E-7..E-1 | E / end of E-1 | Low in own row; high if missing dates filled from future event windows | Descriptive only, implemented within own row |
| `rest_days_7d` | E-7..E-1 | E / end of E-1 | Low in own row | Descriptive only, implemented within own row |
| `mean_exertion_7d` | E-7..E-1 | E / end of E-1 | Low in own row | Descriptive only, implemented within own row |
| `observed_exertion_days_7d` | E-7..E-1 | E / end of E-1 | Low temporal risk; recording-process proxy | Descriptive only, implemented within own row |
| `mean_training_success_7d` | E-7..E-1 | E / end of E-1 | Low in own row | Descriptive only, implemented within own row |
| `observed_training_success_days_7d` | E-7..E-1 | E / end of E-1 | Low temporal risk; recording-process proxy | Descriptive only, implemented within own row |
| `mean_recovery_7d` | E-7..E-1 | E / end of E-1 | Low in own row | Descriptive only, implemented within own row |
| `observed_recovery_days_7d` | E-7..E-1 | E / end of E-1 | Low temporal risk; recording-process proxy | Descriptive only, implemented within own row |
| `combined_intensity_7d` | E-7..E-1 | E / end of E-1 | Low within own row; audit only | Descriptive only, implemented within own row |
| `distance_14d` | E-14..E-1 | E / end of E-1 | Use original weekly own-row blocks | Proposed, not implemented |
| `distance_21d` | E-21..E-1 | E / end of E-1 | Use original weekly own-row blocks | Proposed, not implemented |
| `distance_28d` | E-28..E-1 | E / end of E-1 | HIGH if stitching future windows or treating gaps as zero | Proposed, not implemented |
| `distance_change_7d` | E-14..E-1 | E / end of E-1 | Low using original own-row blocks | Proposed, not implemented |
| `relative_distance` | Current E-7..E-1 versus history ending E-8 | E / end of E-1 | HIGH with full-athlete/future normalization | Proposed, not implemented |
| `load_recovery_interaction` | E-7..E-1 | E / end of E-1 | Fit centering on train only | Proposed, not implemented |

## Dataset and workflow risks

| Variable/process | Risk | Decision |
|---|---|---|
| `injury` | Outcome leakage | Target and descriptive grouping only |
| `Date` | Time index and sample-selection proxy; not calendar date | Split/order/audit only initially |
| `Athlete ID` | Memorization, participant overlap | Grouping only for unseen-athlete validation |
| Healthy-control selection | Uses fitness 21 days after E | Cannot undo from release; conditional retrospective estimand |
| Gaps / days until next row / next injury | Future observation/outcome information | Never predictors; no zero filling |
| Reconstructed training days | Some past days are supplied only by future event windows | Visualization only; never a prospective source without an availability audit |
| Full-athlete healthy mean/SD | Uses future observations and labels to define personal baseline | Reject; prior-only baselines and fold-specific transforms |
| Original replication notebook | Computes test-athlete statistics conditional on healthy labels; training/calibration draws come from the same observation pool | Inspect as historical code only; never execute or copy preprocessing workflow |
| Weekly released ratios | Near-zero denominator instability; not future leakage by itself | Quarantine; transparent difference or explicit denominator policy later |
| Sentinel -0.01 | Encodes rest/recording habits, not negative biological response | Mask for numeric summaries, retain rest days and availability count |
| Adjacent windows | Shared exposures across temporal boundary | Purge train outcomes whose full input span overlaps test input span (7 or 21 days); calibrate separately |
| Scaling/imputation/PCA/selection/resampling | Test distribution influences fitted transforms | Fit training fold only; no resampling before split |
| Descriptive inspection of all records | Influences later hypothesis selection | Milestone 1 is exploratory; register Phase 2 before modeling and label data reuse |

Reconstruction provenance (`first_source_event_day`, `last_source_event_day`, `supporting_event_windows`) must not enter predictors. Overlap checks and weekly consistency checks support the corrected suffix mapping. Sex is not encoded by any known ID mapping; do not infer it.

## Phase 2 implementation extension

User continuation authorized Phase 2 on 2026-10-25. Original target/horizon and source boundaries remain fixed. All new features are in the current registry.

| Feature | Window | Cutoff | Risk / decision |
|---|---|---|---|
| `z3_4_distance_14d` | E-14..E-1 | End of E-1 | Low within original row; existing source selection persists; Prepared Phase 2; not entered in Day model comparison |
| `z5_t1_t2_distance_14d` | E-14..E-1 | End of E-1 | Low within original row; existing source selection persists; Prepared Phase 2; not entered in Day model comparison |
| `rest_days_14d` | E-14..E-1 | End of E-1 | Low within original row; existing source selection persists; Prepared Phase 2; not entered in Day model comparison |
| `strength_sessions_14d` | E-14..E-1 | End of E-1 | Low within original row; existing source selection persists; Prepared Phase 2; not entered in Day model comparison |
| `cross_training_hours_14d` | E-14..E-1 | End of E-1 | Low within original row; existing source selection persists; Prepared Phase 2; not entered in Day model comparison |
| `z3_4_distance_21d` | E-21..E-1 | End of E-1 | Low within original row; existing source selection persists; Prepared Phase 2; not entered in Day model comparison |
| `z5_t1_t2_distance_21d` | E-21..E-1 | End of E-1 | Low within original row; existing source selection persists; Prepared Phase 2; not entered in Day model comparison |
| `rest_days_21d` | E-21..E-1 | End of E-1 | Low within original row; existing source selection persists; Prepared Phase 2; not entered in Day model comparison |
| `strength_sessions_21d` | E-21..E-1 | End of E-1 | Low within original row; existing source selection persists; Prepared Phase 2; not entered in Day model comparison |
| `cross_training_hours_21d` | E-21..E-1 | End of E-1 | Low within original row; existing source selection persists; Prepared Phase 2; not entered in Day model comparison |
| `prior_expected_distance_7d` | E-63..E-8 with source ascertainment < E | End of E-1 | Prior-only ledger; no labels used; source selection and unknown logging times persist; Known-athlete sensitivity only; missing dates not zero-filled; not a population biological baseline |
| `distance_deviation_7d` | E-7..E-1 versus prior E-63..E-8 | End of E-1 | Prior-only ledger and training-only preprocessing; Not causality; replaces total distance alongside expected baseline in known-athlete sensitivity |
| `prior_observed_days_56d` | E-63..E-8 | End of E-1 | Audit only; not a predictor; Not complete time at risk |
| `prior_coverage_56d` | E-63..E-8 | End of E-1 | Audit only; not a predictor; Not actual recording compliance |

Original weekly distance_14d, distance_21d and distance_change_7d candidates are now prepared. Temporal splits purge until earlier event +21 precedes later input start. Fit/calibration/test observations are disjoint; unseen-athlete roles are also athlete-disjoint. Clipping, imputation and scaling fit training rows only; sigmoid calibration uses a frozen base model and separate calibration rows. Review thresholds use only calibration scores under fixed budgets. Numeric provenance and split assignments are saved in reports/phase_02/run_manifest.json and data/processed/phase_02/. No complementary-cohort rows, test labels, IDs or raw Date are predictors.
