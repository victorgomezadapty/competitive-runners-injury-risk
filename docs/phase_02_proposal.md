# Phase 2 initial proposal (historical; execution authorized)

## Priority: improve the longitudinal measurement design

1. Freeze target, source version, eligibility and corrected suffix map. Investigate extreme values, the 15 all-zero training-success histories, all-rest pre-event windows, and source preprocessing questions. Keep uncertain variables in sensitivity analyses rather than silently correcting them.
2. Retain Day Approach as primary for daily trajectory/subjective-response work. Use Week Approach separately for 14/21-day exposure and week-to-week differences. Compare representations on matched events as a sensitivity analysis; never stack them as independent records.
3. Start with the registered 3/7-day exposure, intensity, rest, and subjective summaries. Investigate previous-week versus current-week changes using original weekly blocks. Defer 28-day and personal-baseline features until past-only availability can be verified. Avoid unbounded ratios and arbitrary ACWR interpretations.
4. Separate between-person level from within-person deviation with historical, cutoff-aware baselines. Evaluate minimum-history and cold-start rules; never compute full-athlete healthy-label statistics. Describe this estimand before choosing a repeated-measures model.
5. Predefine temporal, athlete-independent and combined validation, including fold event counts, overlap purging, separate calibration and uncertainty at athlete level. Document the existing future-conditioned sampling limitation.

## Only after this design and Milestone 1 are reviewed

Establish no-skill prevalence and regularized logistic baselines before optional tree models. Use natural prevalence in evaluation; fit all transforms inside training folds. Report average precision/PR-AUC definition, precision, recall, Brier score, calibration and operational alert volume; ROC-AUC is secondary. Never use accuracy as the main metric. Calibration within selected cases is not prospective population calibration. Avoid SMOTE by default and avoid neural networks initially.

Threshold exploration, event recall/lead time, false alerts per athlete-month and prospective dashboard claims need complete event surveillance or an explicitly bounded source-sample estimand. Keep them deferred. No risk categories or causal counterfactual advice are authorized by this milestone.

The complementary-dataset work initiated during Milestone 1 should share domain schemas and validation contracts, not participant IDs or imputed missing modalities. See `docs/complementary_dataset_review.md`.

## Execution update

The user requested improvements and continuation on 2026-10-25, authorizing fixed Phase 2 baselines after Milestone 1 delivery. See reports/phase_02_summary.md and config/phase_02_protocol.json for what was implemented. Tree/neural models and clinical deployment remain deferred.
