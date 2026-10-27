# Methodology: complete research release

The numbered section below records Milestone 1 methods historically. Current predictive methods are specified in [Phase 2](../reports/phase_02_summary.md), the [final matched comparison](../reports/final_project_summary.md), and their frozen config files. All current results remain exploratory, selected-sample research. No clinical deployment.

# Historical Milestone 1 methods

1. Acquire and checksum original Dataverse release and inspect its corrected README, original study, and replication code as text. Establish the target definition before descriptive feature construction.
2. Validate integer keys, unique athlete/event pairs, binary labels, and finite values. Audit both representations independently and reconcile overlapping keys.
3. Decode corrected daily lag order, check exact overlap agreement, and reconstruct unique exposure days with source-window provenance. Never fill date gaps with zero.
4. Preserve all raw values. Mask -0.01 only in subjective rating summaries; preserve rest days, recorded zeros, and rating-availability counts. Flag suspicious extrema for review without deleting them.
5. Summarize cohort, event gaps, retained-injury intervals, variable distributions, per-athlete missingness/scale usage, daily-to-weekly consistency, and denominator-sensitive ratios.
6. Plot five deterministically selected injured athletes spanning the distribution of retained observation counts. Plot actual relative-day spacing; gaps remain blank. These illustrative cases are not a representative clinical sample.
7. Compare physiologically interpretable 3- and 7-day windows, calculated within each original event row. Compute raw label-stratified summaries and paired within-athlete contrasts. For each feature, average windows separately within each athlete/label; subtract healthy mean from injury mean; summarize these paired differences with equal athlete weight. Only athletes with both nonmissing categories contribute.
8. Use 2,000 bootstrap resamples of whole athlete-level paired contrasts, seed 20261025, for percentile 95% confidence intervals. Report the raw mean difference and paired standardized difference (mean/SD of athlete differences). No row-level independence assumption, p-value thresholding or causal inference is used. These exploratory intervals are not adjusted for multiple comparisons, time trends, shared coaching, or unmeasured confounding.

The within-athlete comparison removes simple between-athlete level differences, but it is not a person-centered mixed model, causal estimator, or an assessment of intensity independent of volume. Overlapping windows and creator-selected healthy periods limit interpretation. No mixed-effects model, GEE, machine learning, resampling of classes, calibration model, or risk threshold was fitted.

Runtime versions are captured in `reports/tables/audit_summary.json` and pinned in `requirements.txt`. Reusable logic is in `src/`; notebooks display the results and interpretation. Six primary and two complementary-source tests guard scientific invariants rather than evaluating predictive performance.
