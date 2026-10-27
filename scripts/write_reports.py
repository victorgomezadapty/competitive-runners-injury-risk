"""Write Milestone 1 interpretation from computed tables (no fitted risk model)."""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def write(path, text):
    if (ROOT/'reports/phase_02/run_manifest.json').exists() and path in ['README.md','handoff/findings.md','docs/phase_02_proposal.md','docs/clinical_interpretation.md']:
        return  # Historical report regeneration must not reset current project status.
    if (ROOT/'reports/phase_02/run_manifest.json').exists() and path=='reports/milestone_01_summary.md':
        text='> Historical Milestone 1 record. The user authorized continuation; current results are in [Phase 2](phase_02_summary.md).\n\n'+text
    (ROOT/path).write_text(text.strip()+'\n', encoding='utf-8')


def markdown_table(df, columns=None, digits=3):
    df = df if columns is None else df[columns]
    def value(x):
        if isinstance(x, float):
            return f'{x:.{digits}f}' if pd.notna(x) else 'Unavailable'
        return str(x)
    return '| '+' | '.join(df.columns)+' |\n|'+'|'.join(['---']*len(df.columns))+'|\n'+''.join('| '+' | '.join(value(v) for v in row)+' |\n' for row in df.itertuples(index=False, name=None))


def main():
    a = json.loads((ROOT/'reports/tables/audit_summary.json').read_text())
    d,w,h = a['day'],a['week'],a['history']
    athlete = pd.read_csv(ROOT/'reports/tables/day_athlete_summary.csv')
    contrasts = pd.read_csv(ROOT/'reports/tables/within_athlete_contrasts.csv')
    daily_dist = pd.read_csv(ROOT/'reports/tables/unique_training_day_distributions.csv')
    manifest = json.loads((ROOT/'data/source_manifest.json').read_text())
    companion = json.loads((ROOT/'data/complementary/soccermon/profile_summary.json').read_text()) if (ROOT/'data/complementary/soccermon/profile_summary.json').exists() else None
    write('data/README.md', f'''# Original-source acquisition

Use [DataverseNL DOI 10.34894/UWU9PV](https://doi.org/10.34894/UWU9PV), not a Kaggle mirror. Retrieved for this milestone on 2026-10-25. The acquired dataset version is **{manifest['version']}**, published {manifest['release_time']}. Data license: **CC0-1.0** as recorded in original metadata. Dataset creators: Sofie Lövdal, Ruud J.R. den Hartigh, George Azzopardi.

From the repository root:

```powershell
python -m pip install -r requirements.txt
python scripts/download_data.py
python scripts/run_milestone_01.py
python scripts/build_project_artifacts.py
python scripts/write_reports.py
python -m pytest -q
python scripts/execute_notebooks.py
```

`download_data.py` discovers filenames/IDs in the original API, requests `format=original`, verifies the publisher SHA-1, and records SHA-256 and file sizes in `source_manifest.json`. It never executes the source notebook. Network access is needed only for acquisition. For a later release, preserve a copy of the manifest and metadata before updating; a changed version/checksum requires renewed audit. Exact statistical counts are computed from files, not hard-coded.

| Original file | File ID | Bytes | Purpose |
|---|---|---|---|
'''+''.join(f"| `{x['filename']}` | {x['file_id']} | {x['bytes']} | {'Reference code, read only' if x['filename'].endswith('.ipynb') else 'Source data/documentation'} |\n" for x in manifest['files'])+'''
The full exact checksums and URLs are in [source_manifest.json](source_manifest.json). Raw files, interim reconstruction, processed descriptive windows, and the copyright-restricted original-paper PDF are excluded from Git. Reports/tables/figures are retained for review. Optional `python scripts/fetch_paper.py` acquires the university paper; it needs pypdf only for optional local text inspection, not for the analysis pipeline.

The `raw/` directory also contains the saved Dataverse metadata response. `interim/` contains retrospective reconstructed training days with source-event provenance; `processed/` contains within-row 3- and 7-day descriptive summaries. Neither contains predictions. Do not combine the representations as independent samples: they heavily overlap and select somewhat different events.
''')
    write('docs/cohort_definition.md', f'''# Cohort definition

The released Day and Week files each contain **{d['athletes']} unique masked athletes**, computed with `nunique()` on `Athlete ID`. There is no sex/age lookup or event-specialty column. IDs must not be mapped to sex or matched to another dataset.

The study's Subjects section describes 77 initial runners (27 women/50 men). Its Design section explains that filtering leaves 74 (27 women/47 men), matching our directly audited released count. Thus this is an initial-versus-retained cohort discrepancy, not evidence of three missing files. The university portal abstract still reports 77; PubMed and the PDF abstract report 74. The reported retained sex distribution is source-level metadata, not independently verifiable by athlete from these CSVs.

The population is one high-level Dutch middle/long-distance team, approximately 800 m through marathon, mostly national and some international competitors. Source collection is approximately 2012-2019. This is not a recreational-running cohort or external validation across clubs. A stable coach and common recording system may generate team-specific habits.

Selected event rows per athlete: min {athlete.observations.min()}, median {athlete.observations.median():.1f}, IQR {athlete.observations.quantile(.25):.1f}-{athlete.observations.quantile(.75):.1f}, max {athlete.observations.max()}. Selected event span (inclusive first-to-last retained day): median {athlete.selected_event_span_days.median():.0f} days, range {athlete.selected_event_span_days.min()}-{athlete.selected_event_span_days.max()}. This is **not continuous observed follow-up**. Entry, dropout, time injured, missing logs and source exclusions cannot be fully separated.

There are {d['total_unselected_days_within_athlete_spans']:,} athlete-days without a selected event inside retained Day spans. They cannot be assigned healthy labels or rest. See [athlete summary](../reports/tables/day_athlete_summary.csv), [event gaps](../reports/tables/day_observation_gaps.csv), and [reconstructed history](../reports/tables/reconstructed_history_by_athlete.csv) for all athletes.

Sources: [study](https://doi.org/10.1123/ijspp.2020-0518), [university record](https://research.rug.nl/en/publications/injury-prediction-in-competitive-runners-with-machine-learning/), [Dataverse](https://doi.org/10.34894/UWU9PV).
''')
    write('docs/temporal_design.md', '''# Temporal design

E = selected event day; t = E-1 = end of information available before the target. The existing target is the flag at E, not a seven-day outcome. The study phrases its question as the next training session; the released Date refers to an event day. We retain the explicit event-day endpoint and do not assume every day has a scheduled session.

Day Approach: seven consecutive daily feature blocks E-7..E-1 within each row. Corrected suffix order is 0..6 from oldest to newest. Week Approach: three weekly blocks, newest week 0, then 1 and 2. Weekly windows advance with each event day, not only at calendar-week boundaries.

## Two different longitudinal objects

1. **Event table**: selected injury/healthy days with embedded earlier history. Suitable for conditional retrospective classification after review.
2. **Retrospective exposure reconstruction**: de-duplicated athlete-training days recovered from embedded histories. Used for timelines and distributions only. A day can be recovered from a future source event row; its inclusion must not be treated as prospective availability.

No raw continuous training log is provided. Retained-date gaps can arise from injury filtering, missing/anomalous data removal, absent logging or attendance, and other selection. These cannot be disentangled. The relative Date origin is not released as a calendar date. Negative reconstructed indices are legitimate earlier history, not fabricated pre-2012 dates.

## Phase 2 validation design proposal, not executed

- A: Known-athlete future estimation. Use explicit global relative-day cutoffs; report athletes with sufficient history on each side. Retain temporal order and a separate calibration period. Do not use a random row split.
- B: Unseen-athlete estimation. Outer athlete-disjoint groups; all outcomes from a held-out athlete remain outside fitting/tuning/calibration. Personal adaptation, if later considered, must use only prior unlabeled information and be evaluated as a separate protocol.
- C: Athlete-disjoint plus time-constrained validation if enough events remain. Do not infer recruitment order from numeric masked IDs.

For temporal boundaries, purge training events whose exposure histories overlap test exposure histories. At least a 7-day or 21-day input-span embargo, according to the representation, is required under a strict non-overlap design; account for longer future outcome horizons separately. Non-overlapping test histories are a useful sensitivity analysis, not an automatic replacement for the intended deployment estimand.

No new horizon is created from absent event days. A complete incident-injury registry would be needed for reliable 3/7-day outcomes, lead-time evaluation, false alerts per true athlete-month, or prospective operational calibration. Label-selected controls already use future fitness; fold-level safeguards do not repair that upstream selection.
''')
    write('docs/methodology.md', '''# Methodology: Milestone 1 only

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
''')
    write('docs/clinical_interpretation.md', '''# Clinical interpretation

This milestone describes injury-associated training histories in a selected release. It does not produce individual risk scores or advice about safe training. Training load is not injury; high load can reflect capacity and training goals. Associations do not establish causal or preventive effects.

Distinguish population-level differences, changes relative to an athlete's own history, and individual biological response. The present paired analysis addresses simple within-athlete contrasts but does not establish a personal risk model. Perceived recovery, exertion and success are incomplete subjective proxies with individual scale-use habits.

More exposure and fewer rest days appear before retained flags in descriptive comparisons. Recovery ratings are also higher in the computed comparisons; the expected low-recovery narrative is not supported here. This should prompt examination of scale use, selection, exposure, timing, and confounding, not a claim that recovery causes injury. Fifteen athletes record training success as zero throughout their recovered active-day histories; those zeros cannot be assumed biologically meaningful or automatically imputed without source clarification.

Any future probability will initially be conditional on this selected source sample. Risk estimate is not diagnosis; prediction is not prevention. A future decision-support display must state uncertainty and staff review workload, avoid deterministic language, and never claim that a hypothetical training change reduces injury risk by a causal amount.
''')
    limitations = '''# Limitations

- One competitive Dutch team with shared coaching and recording conventions; no recreational-running or broad clinical external validity.
- Injury is a selected training-log flag, not a tissue-specific medically verified diagnosis. Severity, anatomical site, mechanism, clinical onset and days lost are unavailable.
- Healthy events were selected using future full fitness. Near-injury periods and subsequent flags were excluded; the observed fraction is not cohort incidence or prospective baseline risk.
- Source logs were prefiltered for missing/anomalous data; no blank CSV cells does not establish complete data. Omitted days and excluded athletes/events cannot be reconstructed reliably.
- Relative dates only. Individual spans are lower-bound retained spans, not continuously observed follow-up; exact calendar dates and genuine person-time denominators are unavailable.
- Repeated, overlapping windows within athletes; shared team context may also correlate athletes. Cluster bootstrap uncertainty is exploratory and assumes athletes can be resampled.
- Reconstruction can use later event windows to expose past history. It is descriptive only, not a leak-free real-time data stream.
- Subjective scales lack detailed anchors and instrument provenance. -0.01 means rest-day unavailability; constant recorded zeros may reflect recording habits. Weekly all-rest rating summaries use zero, unlike sentinel-masked daily summaries.
- Extremes include large sprint distance/cross-training hours and weekly ratios exceeding 200 million. Original values are retained; source clarification and sensitivity analysis are required.
- Day/Week retain different event samples; agreement on matched labels does not make them interchangeable. Weekly rounding/aggregation and all-rest handling differ.
- No HRV, sleep, tissue capacity, symptoms, injury site/history registry, environmental stress, nutrition, sex-by-ID or running duration. Complementary cohorts cannot supply these missing values for the original runners.
- The 3/7-day contrasts and intervals are exploratory, unadjusted, and not independent tests of injury causation. No finding establishes that changing training would prevent an injury.
- No prediction performance, calibration, threshold utility or clinical deployment claim is available at Milestone 1.
'''
    write('docs/limitations.md', limitations)
    write('handoff/limitations.md', limitations)
    write('docs/phase_02_proposal.md', '''# Phase 2 proposal - review required before execution

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
''')
    write('handoff/future_integration.md', '''# Future integration architecture

Project line: **Sports Rehabilitation & Human Performance**. This repository is the longitudinal exposure component of a broader Physiotherapy Data Science portfolio.

Keep `running-injury-clinic` independent: it describes movement/biomechanics in different people and under another protocol. This repository describes histories before selected injury flags. Do not join participants or training days across cohorts.

Create source-specific adapters around common domain concepts: cohort ID, source athlete ID, relative/calendar time basis, measurement time, availability time, domain, original variable, units, quality/sentinel flags, target definition and ascertainment. Namespace IDs by source. Keep source-specific data dictionaries and outcome registries; missing modalities remain missing for that cohort.

The future Longitudinal Athlete State Engine can reuse prior-only baseline logic, window definitions, validation contracts, uncertainty displays and risk communication. A complementary sleep/HRV/wellness cohort can test those measurement modules independently; it cannot retrospectively add HRV or sleep to the Dutch runners or validate an injury endpoint it never measured.

The companion source review and acquisition are part of this milestone, not postponed row-level integration. See `docs/complementary_dataset_review.md`. No software architecture connection establishes biological equivalence or transportability.
''')
    # Computed evidence tables in the main report.
    core = pd.DataFrame([{'Representation': label, 'Athletes': x['athletes'], 'Rows': x['rows'],
                         'Injury labels': x['injury_rows'], 'Label prevalence (%)':100*x['injury_prevalence'],
                         'Athletes with labels':x['athletes_with_injury']} for label,x in [('Day',d),('Week',w)]])
    c7 = contrasts[contrasts.window_days.eq(7)].copy()
    short = c7[['feature','paired_athletes','injury_minus_healthy','ci95_low','ci95_high','paired_standardized_difference']]
    summary = f'''# Milestone 1 - Longitudinal Dataset & Injury Event Understanding

**Longitudinal Training Load & Injury Risk in Competitive Runners**  
Sports Rehabilitation & Human Performance | Physiotherapy Data Science portfolio  
Review date: 2026-10-25 | Original Dataverse release {manifest['version']} | **Milestone 1 complete; STOP before modeling**

## Findings at a glance

{markdown_table(core)}
Counts are calculated from downloaded files; no cohort/event size is hard-coded. Injury prevalence is **the fraction of retained event rows labeled injury**, not an annual injury rate or a prospective daily probability.

## What does one row represent?

A selected event day for a masked athlete with a binary injury/healthy label and an embedded earlier training history. It is not a raw unfiltered athlete-day. Day contains 70 exposure/response fields (10 x 7) plus athlete ID, target and Date. Week contains 66 weekly fields (22 x 3), three weekly ratios, athlete ID, target and Date. Day and Week are overlapping representations of different selected event sets, not independent cohorts.

## What constitutes an injury event?

A retained training-log flag for interruption or skipping of a scheduled session because of injury. Creators required three preceding injury-free weeks; further flags within three weeks were excluded as the same episode. Healthy comparisons required full fitness for three weeks before **and after** E. Missing/anomalous events were excluded. See [target definition](../docs/injury_definition.md) and the source study's Methods, pp. 1523-1524. A flag is not a verified anatomical diagnosis, severity category or exact biological onset date.

## How rare are injuries?

Day: {d['injury_rows']} of {d['rows']:,} ({100*d['injury_prevalence']:.4f}%). Week: {w['injury_rows']} of {w['rows']:,} ({100*w['injury_prevalence']:.4f}%). All-negative accuracy would be {100*(1-d['injury_prevalence']):.2f}% in Day, illustrating why accuracy is unsuitable. This arithmetic is not a trained model. Future average-precision no-skill reference is the evaluation-set label fraction, subject to the same sampling caveat.

{d['athletes_with_injury']} Day athletes and {w['athletes_with_injury']} Week athletes have a retained flag. In Day, labels per athlete range {athlete.injury_labels.min()}-{athlete.injury_labels.max()}, median {athlete.injury_labels.median():.0f}; full counts are in [day_athlete_summary.csv](tables/day_athlete_summary.csv).

There are {int(d['injury_interval_days']['count'])} computable within-athlete intervals between retained Day injury labels: median {d['injury_interval_days']['50%']:.0f} days, IQR {d['injury_interval_days']['25%']:.0f}-{d['injury_interval_days']['75%']:.2f}, range {d['injury_interval_days']['min']:.0f}-{d['injury_interval_days']['max']:.0f}. Week median is {w['injury_interval_days']['50%']:.1f}. **No consecutive injury labels exist** in either file; minimum interval is 22 days, consistent with creator filtering. Do not interpret this as absence of prolonged injuries or early recurrence in the original logs.

## How much longitudinal history exists per athlete?

- Selected Day event rows: median {athlete.observations.median():.1f}, IQR {athlete.observations.quantile(.25):.1f}-{athlete.observations.quantile(.75):.1f}, range {athlete.observations.min()}-{athlete.observations.max()}.
- Inclusive selected-event spans: median {athlete.selected_event_span_days.median():.0f} days; range {athlete.selected_event_span_days.min()}-{athlete.selected_event_span_days.max()}. These are retained spans, not continuous follow-up or days at risk.
- Event Date ranges **{d['first_relative_day']} to {d['last_relative_day']} relative days** in both representations. Exact earliest/latest calendar dates are unavailable. Source collection is approximately 2012-2019; no day/month is invented.
- {d['total_unselected_days_within_athlete_spans']:,} days inside athlete Day event spans have no selected row. Their cause cannot be identified. [Gap table](tables/day_observation_gaps.csv) preserves all intervals. Missing event rows are not rest or healthy days.
- Day history expands to {h['window_cells_rows']:,} overlapping athlete-history rows but only **{h['unique_athlete_training_days']:,} unique athlete-training days**, indices {h['earliest_training_relative_day']} to {h['latest_training_relative_day']}. Overlap conflicts: {h['conflicting_athlete_days']}. Reconstruction does not recover the complete log and is descriptive only.

All athlete-specific spans, observation counts, gaps, label counts, scale usage and reconstructed-history coverage are exported, rather than only population aggregates. Sex is unavailable by ID. Source retained cohort metadata reports 27 women/47 men. The 77 initially described in Subjects becomes 74 after filtering in Design; see [cohort definition](../docs/cohort_definition.md).

## What training information exists before injury?

Daily completed sessions, running km, Z3-4 km, Z5/T1/T2 km, sprint km, logged strength, cross-training hours, perceived exertion, recovery and training success over seven days. Weekly summaries add rest counts, maxima, tough/interval session counts and three weeks of aggregate history. Training duration, explicit easy-zone km, sleep and HRV are not released. Intensity-zone definitions and every exact column appear in the [data dictionary](../docs/data_dictionary.md).

### Distributions on unique reconstructed training days

{markdown_table(daily_dist, ['variable','n','missing','mean','median','q25','q75','p99','max'])}
Subjective missing counts here are deliberately masked rest sentinels, not blank source cells. There are {h['rest_days_reconstructed']:,} zero-session days ({100*h['rest_days_reconstructed']/h['unique_athlete_training_days']:.2f}% of reconstructed days). A zero-running day can still contain strength/cross training; rest is defined from zero sessions. The selected-window rest distribution is exported separately.

![Training distributions](figures/training_distributions.png)

## Missing data, coding and quality

Both released files contain zero blank/nonfinite cells and zero duplicate athlete/event keys. This follows creator filtering and does not prove complete raw surveillance. Day windows contain {h['sentinel_cells_in_event_windows']:,} subjective -0.01 cells: all occur on zero-session days, with no ordinary ratings on those rest days. They are excluded from rating means, while exposure days remain. All-rest seven-day windows: {h['all_rest_7d_event_windows']:,}, including {h['injury_rows_after_all_rest_7d']} injury-labeled rows. Their subjective averages are undefined in our daily summaries; weekly source summaries use zero, so direct rating comparisons need care.

Fifteen athletes have all-zero recorded training-success ratings across reconstructed active histories. We preserve zeros, flag the pattern and do not silently call zero missing or success. Scale anchors/transformations are insufficiently documented for a clinical score interpretation. Per-variable and per-athlete missingness plus scale-use tables are in `reports/tables/`.

{h['rows_for_source_review']} reconstructed training days meet transparent review triggers (large distance/sprint/cross-training values, strength >1, or intensity exceeding total). These triggers are screening rules, not proof of error. Original values remain. Weekly ratios reach over 200 million; zero-denominator cases and consistency errors are documented in [released_ratio_audit.csv](tables/released_ratio_audit.csv). No predictive use is authorized.

## What do pre-event patterns show?

The following are equal-athlete-weight **within-athlete** differences between each athlete's mean injury and mean healthy windows. They are different from raw population mean differences. CIs resample paired athlete contrasts 2,000 times; effect size is mean paired difference/SD of those differences. Objective features include {int(c7.paired_athletes.max())} paired athletes; subjective features include {int(c7.paired_athletes.min())} after undefined means are excluded. No time-varying confounding adjustment or multiplicity correction is applied.

{markdown_table(short)}
More volume, more Z3-4/Z5-T1-T2 distance, more sessions and fewer rest days precede retained injury labels in this comparison. **Perceived recovery is also higher**, as are exertion and success; lower-recovery assumptions are not supported by these summaries. Recording habits, source selection, temporal trends and training exposure may contribute. Strength and cross-training contrasts remain uncertain. Sprint results are particularly sensitive to extreme values. None establishes that a load or recovery change causes or prevents injury, or that intensity adds information independently of total volume.

3-day comparisons, raw per-label distributions, athlete-level paired values and separate Week-0 results are exported. The trajectory plot below weights athletes equally within each label, but label groups differ in athlete membership, so its curves are descriptive and not the paired estimator above.

![Pre-event profiles](figures/pre_event_profiles.png)

## Athlete timelines

Five athletes were selected deterministically from injured athletes across retained-observation-count quantiles: {', '.join(map(str,a['example_athletes']))}. Each figure shows running distance, intensity, perceived response, rest/other training and retained events with relative-day spacing. Gaps are blank. Training reconstructed from later windows is used only to visualize retrospective history; never as proof of prospective availability.

'''
    for athlete_id in a['example_athletes']:
        summary += f'![Athlete {athlete_id} timeline](figures/athlete_{athlete_id:02d}_timeline.png)\n\n'
    summary += f'''## Which variables might leak future information?

Future-conditioned healthy selection is the main upstream problem. Full-athlete healthy-label means/SD, future normalization, days until next event/injury, reconstructed history available only through later source windows, outcome-derived missingness and cross-fold athlete overlap are additional risks. `Athlete ID`, `Date`, `injury` and reconstruction provenance are not exposure predictors. See [feature-by-feature leakage audit](../docs/leakage_audit.md).

The original replication code was read but never executed. It holds out athletes, but its test-athlete healthy normalization uses full held-out athlete records and outcome labels. Training and calibration draws are taken from the same original observation pool and can overlap. The test threshold is passed from validation; using test labels to compute evaluation metrics is not itself leakage. Historical reported AUCs are not a leakage-free deployment benchmark. A recent temporal benchmark is listed in [references](../docs/references.md), but its stated daily suffix order conflicts with the corrected source README; the source correction governs our implementation.

## Athlete-level and temporal dependencies

Athlete-days are nested within {d['athletes']} athletes; they are not {d['rows']:,} independent people. There are {d['consecutive_selected_event_pairs']:,} adjacent retained Day event pairs whose seven-day histories share six exposure days. Repeated labels, personal rating habits, unequal history length and team context affect uncertainty. Random row splitting is not an unseen-athlete evaluation; a pure chronological split does not alone prevent overlap of input histories. Descriptive clustering, later athlete-disjoint folds and temporal purging address different aspects.

## What can this dataset legitimately predict?

After review, it can support carefully bounded retrospective estimation/classification of a **selected injury-labeled event day from preceding training windows**, and compare known-athlete temporal versus unseen-athlete generalization under explicitly specified protocols. This milestone demonstrates data availability and associations only; no predictive ability is claimed.

## What can it NOT tell us?

It cannot establish deterministic injury, medically verified diagnosis, injury mechanism, true cohort incidence, fully observed time at risk, treatment effects, safe load thresholds, injury prevention, complete recovery trajectories or transportability to recreational runners. Prospective real-world probability calibration and operational alert rates require representative ongoing surveillance. A complementary cohort cannot supply missing HRV/sleep or biomechanics for these same individuals.

## Day or Week as primary representation?

**Day Approach is primary** for daily trajectories, subjective-response audit and sequence-preserving descriptive work. It is not chosen because of the original AUC. Week remains a separate secondary representation for direct 14/21-day exposure and week-to-week comparisons. Do not reconstruct unobserved long histories by silently stitching selected rows.

Cross-file audit: {a['cross_representation']['matched_keys']:,} matched athlete/event keys, {a['cross_representation']['day_only']} Day-only and {a['cross_representation']['week_only']} Week-only; no label disagreements on matched keys. Seven-day objective sums reconcile exactly on common keys except small cross-training rounding differences. Weekly subjective averages are rounded and all-rest cases differ in missing-value handling. The two files must not be stacked.

## Candidate windows and Phase 2

Implemented descriptively: 3/7-day exposure, rest and subjective summaries with observed-rating counts. Proposed: 14/21-day weekly totals, week-to-week differences and prior-only personal deviations. Defer 28-day features until complete as-of history is established. Register a few physiological hypotheses; avoid arbitrary interactions or ACWR as a clinical truth. See [feature registry](../handoff/feature_catalog.csv) and [Phase 2 proposal](../docs/phase_02_proposal.md).

Complementary-data acquisition/review was opened in parallel at the user's request; see [source review](../docs/complementary_dataset_review.md) and [integration contract](../handoff/future_integration.md). Cohorts, IDs and outcomes remain separate.

Two complementary sources are now acquired and profiled: **SoccerMon** provides a working source-specific wellness/session adapter for {companion['wellness_participants_observed'] if companion else 'file-verified'} elite soccer athletes; **Wu 2026** provides multidisciplinary processed runner workbooks, but no explicit participant/time keys. Their acquisition, file-level profiles, dataset catalog and domain mapping are prepared now. Wu is quarantined for longitudinal/grouped modeling, and SoccerMon has its own reporting and availability limitations. See [complementary data profile](../docs/complementary_data_profile.md). Neither source fills missing measurements in the Dutch runners.

## Deliverable checklist

| Requested deliverables | Review location |
|---|---|
| 1 Repository structure; 2 acquisition; 3 exact files | README, data/README, source manifest |
| 4 dictionary | docs/data_dictionary.md and column-complete CSV |
| 5 athletes; 6 rows; 7 date range | Computed audit and findings table above |
| 8 observations/athlete; 9 follow-up | day/week_athlete_summary.csv; retained-span caveat above |
| 10 labels; 11 prevalence; 12 injured athletes; 13 labels/athlete | audit_summary.json and athlete tables |
| 14 intervals; 15 consecutive labels | day/week_injury_intervals.csv; minimum 22 days |
| 16 missingness | per-variable/per-athlete tables; sentinel and scale-use audits |
| 17 volume; 18 intensity; 19 rest; 20 recovery; 21 exertion; 22 success | Distribution tables and figure above |
| 23 five timelines | Five figures above; notebook 02 |
| 24 pre-event comparison | 3/7-day and Week-0 contrasts, CI/effect sizes, profiles |
| 25 target; 26 leakage | injury_definition.md; leakage_audit.md |
| 27 athlete dependencies; 28 temporal dependencies | This report, methodology and temporal_design.md |
| 29 candidate windows; 30 Phase 2 | Feature registry and phase_02_proposal.md |

**STOP: no injury-prediction model, calibration, thresholds or risk dashboard has been fitted. Milestone 1 must be reviewed before advanced analysis.**
'''
    write('reports/milestone_01_summary.md', summary)
    write('handoff/findings.md', f'''# Findings handoff - Milestone 1

- Day: {d['athletes']} athletes, {d['rows']:,} retained events, {d['injury_rows']} injury labels ({100*d['injury_prevalence']:.4f}%), {d['athletes_with_injury']} athletes with a label.
- Week: {w['rows']:,} events, {w['injury_rows']} labels ({100*w['injury_prevalence']:.4f}%), {w['athletes_with_injury']} athletes with a label.
- Source filtering explains the 77 initial versus 74 retained athletes. There is no sex-by-ID column.
- Correct daily order: unsuffixed E-7 to `.6` E-1. Do not copy reversed lag maps from old PDFs or recent secondary analyses.
- Selected controls use future fitness. Risk/alert interpretations are conditional on source selection.
- Date 0-2673 is relative, not exact 2012-2019 calendar dates. Median selected span {athlete.selected_event_span_days.median():.0f} days; median {athlete.observations.median():.1f} rows per athlete.
- {h['unique_athlete_training_days']:,} unique training days reconstructed; zero overlap conflicts. Retrospective reconstruction is not prospective availability.
- No blank cells; {h['sentinel_cells_in_event_windows']:,} rest-sentinel cells in overlapping subjective histories. Fifteen athletes have all-zero training-success histories; quality review required.
- Paired 7-day contrasts: more volume/intensity/sessions and fewer rest days before flags; recovery ratings are also higher. Association, not causation or proof of safe/unsafe load.
- No consecutive retained injuries; median interval 77 days, minimum 22, partly by design.
- Day primary; Week secondary for 14/21-day summaries. No models fitted. Review report and Phase 2 proposal before proceeding.

Full evidence: [milestone report](../reports/milestone_01_summary.md). Complementary source: [review](../docs/complementary_dataset_review.md).

Two complementary source tracks are acquired, checksummed and profiled. See [file-level assessment](../docs/complementary_data_profile.md), [dataset catalog](dataset_catalog.csv) and [domain mapping](domain_mapping.csv). SoccerMon has a separate working wellness/session adapter; Wu runner workbooks lack explicit participant/time keys and remain quarantined. No row linkage or outcome pooling.
''')
    write('README.md', f'''# Longitudinal Training Load & Injury Risk in Competitive Runners

*Leakage-aware study of daily training, recovery and injury-labeled events in competitive distance runners.*

**Project line:** Sports Rehabilitation & Human Performance  
Part of a broader Physiotherapy Data Science and Human Performance portfolio.  
**Status:** Milestone 1 delivered for review. **No injury-prediction model trained.**

The project asks what happened in an athlete's training history before a retained injury flag, while separating within-athlete changes, between-athlete differences and sample-selection effects. Its progression is training history -> longitudinal features -> injury-associated signals -> calibrated prediction -> decision-support exploration, with explicit review gates.

Start with the [Milestone 1 report](reports/milestone_01_summary.md), [target definition](docs/injury_definition.md), [data dictionary](docs/data_dictionary.md), [leakage audit](docs/leakage_audit.md) and [Phase 2 proposal](docs/phase_02_proposal.md).

## Directly audited release

| Representation | Athletes | Selected rows | Injury labels | Label fraction |
|---|---|---|---|---|
| Day | {d['athletes']} | {d['rows']:,} | {d['injury_rows']} | {100*d['injury_prevalence']:.4f}% |
| Week | {w['athletes']} | {w['rows']:,} | {w['injury_rows']} | {100*w['injury_prevalence']:.4f}% |

Data: Lövdal, den Hartigh & Azzopardi, [Replication Data DOI 10.34894/UWU9PV](https://doi.org/10.34894/UWU9PV), original Dataverse release {manifest['version']}. Original study: [IJSPP 2021](https://doi.org/10.1123/ijspp.2020-0518). See [references](docs/references.md).

**Critical finding:** this is a filtered event-window sample. Healthy controls require future full fitness, labels near injuries were removed, and Date is a relative index. Its label fraction is not a prospective daily injury incidence. Correct daily lag order is unsuffixed E-7 through `.6` E-1, as clarified in the source's 2024 README.

## Reproduce

```powershell
python -m pip install -r requirements.txt
python scripts/download_data.py
python scripts/run_milestone_01.py
python scripts/build_project_artifacts.py
python scripts/write_reports.py
python -m pytest -q
python scripts/execute_notebooks.py
```

Run from this repository root. Python {a['environment']['python']} was used; exact versions and audit facts are captured. Acquisition requires network; subsequent analysis runs locally. [Acquisition details, exact files and checksums](data/README.md). Downloaded data are CC0; the research article is separately copyrighted and excluded from Git. Do not execute the upstream replication notebook as part of this project.

## Repository map

```text
data/          original-source manifest; raw/interim/processed data kept local
notebooks/     01-04 descriptive views; 05-11 explicitly deferred plans
src/data/      loading, validation, corrected lag mapping and timelines
src/features/  reproducible within-row 3/7-day descriptive summaries
src/analysis/  retained event intervals; paired athlete-level contrasts
src/visualization/  athlete timelines and pre-event plots
src/models/    reserved modules only; no fitting implementation
src/validation/ reserved Phase 2 modules; no splits run yet
scripts/       acquisition, analysis, documentation, notebook execution
tests/         scientific contracts for lags, provenance and sentinel handling
docs/          cohort, target, design, methodology, interpretation and limitations
reports/       milestone summary, figures and computed tables
handoff/       feature registry, findings, limitations, integration architecture
```

The parallel [complementary-dataset review](docs/complementary_dataset_review.md) prepares additional modalities/cohorts now. Participant identities and outcomes remain source-specific. The independent `running-injury-clinic` project concerns movement/biomechanics in different people; integration is conceptual and architectural, never a row-by-row join.

**Complementary sources acquired now:** [file-level assessment](docs/complementary_data_profile.md). SoccerMon supplies a separate wellness/session adapter; Wu 2026 supplies multidisciplinary runner reference workbooks without explicit athlete/time keys. [Dataset catalog](handoff/dataset_catalog.csv) and [domain mapping](handoff/domain_mapping.csv) record compatibility and restrictions. No cross-cohort pooling or prediction has been performed.

Training load != injury. High load != harmful load. Association != causation. Risk estimate != diagnosis. Prediction != prevention. No individual clinical advice or validated clinical threshold is produced.
''')
    print('Interpretation, acquisition guide, main report and handoff written.')


if __name__ == '__main__':
    main()
