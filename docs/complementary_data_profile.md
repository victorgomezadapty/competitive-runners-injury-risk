# Acquired complementary data: file-level understanding

## Decision

Retain the original Dutch runner Day file as the primary longitudinal injury-event dataset. Two separate sources have now been acquired, checksummed and profiled. They share a source catalog and domain vocabulary, while participant keys, times, units, outcomes and analysis eligibility remain separate.

| Source | Files directly inspected | Cohort verification | Current use |
|---|---|---|---|
| SoccerMon subjective | 18 CSV + 1 JSON in one original ZIP | 50 distinct athlete columns; 50 athletes with observed wellness | Working source-preserving wellness/session adapter |
| Wu 2026 supplement | Two original Excel workbooks + supplementary PDF | 142 runners reported by publication; no public ID field to verify unique count | Quarantined processed reference; not a longitudinal or athlete-disjoint modeling source |

## SoccerMon: what was actually acquired

Original [Zenodo record](https://zenodo.org/records/10033832), DOI 10.5281/zenodo.10033832. Creators: Midoglu et al.; two elite women's soccer teams. License verified from the repository API: **CC BY 4.0**. Attribution: [SoccerMon data descriptor](https://doi.org/10.1038/s41597-024-03386-x). The original ZIP's MD5 matches `a3e86aeca611f77c9331a535eae00bf7`; SHA-256 and all archive members are recorded in [manifest](../data/complementary/soccermon/source_manifest.json). No GPS archive was acquired.

Directly computed:

- 50 observed wellness athletes; header team split 27 Team A / 23 Team B.
- 17,008 athlete-dates with at least one wellness value; 118,959 observed scalar measurements. These are different denominators.
- Observed wellness range 2020-01-09 through 2021-12-31. Wide files have a padded 731-day calendar grid; padded rows and blank cells are not observations or rest days.
- Seven original variable names: `fatigue`, `mood`, `readiness`, `sleep_duration`, `sleep_quality`, `soreness`, `stress`.
- 16,265 session reports from 50 athletes, 2020-01-09 through 2021-12-31, with original fields `srpe`, `rpe`, `duration`, `date`. Source `srpe` equals `rpe * duration` in every acquired report.
- 151 rows belong to groups with identical athlete/date/RPE/duration/sRPE. They may be duplicate submissions or genuinely repeated sessions. Without stable session IDs, none are deleted.
- 162 injury reports among 15 athletes, 2020-01-14 through 2021-11-03. This is a report count, not an incident-injury count. The `type` field contains JSON body-region and minor/major pain descriptions; no medically adjudicated diagnosis is inferred.

The primary descriptor's published report totals differ from the acquired archive (including training and injury totals). Both are recorded in the [source review](complementary_dataset_review.md); do not silently substitute published totals for file-derived counts.

### Measurement and timing boundaries

Source-specific scales must remain intact. The primary descriptor Figure 1 identifies training duration in minutes and RPE 1-10. Figure 2 identifies sleep hours, sleep quality 1-5, readiness 1-10 and fatigue 1-5; higher `fatigue` means **fresher**, not more tired. Stress coding has an internal paper discrepancy (prose/observed 1-5 versus Table 1's 1-10). Preserve values and flag this instead of imposing a universal 0-1 wellness score. Do not transfer anchors from PMData.

Reports can be retrospective/offline-synchronized. A calendar date is not proof of the time a measurement became available. The adapter explicitly records unknown availability time; it does not generate predictors or injury labels.

The archive's `atl`, `ctl28`, `ctl42`, `acwr`, `monotony`, `strain`, `weekly_load` and `daily_load` are already prepared source summaries. Their complete calendar grids include zeros; zero cannot automatically establish a truly observed rest day. They are profiled and quarantined until calculation timing, padding and denominator conventions are understood. ACWR is not treated as a validated causal or clinical rule.

### Ready now

`src/data/complementary.py` reads the original ZIP, validates SHA-256, preserves source values, namespaces participant keys as `soccermon::...`, and returns observed wellness and source session records. It keeps missing calendar cells missing and keeps repeated reports flagged. Generated long tables remain in `data/complementary/soccermon/processed/`, separately from the Dutch runner tables. No cross-cohort join or target harmonization is performed.

## Wu 2026: acquired processed runner data

Source study: [Multidisciplinary prediction of running-related injuries using machine learning](https://doi.org/10.1038/s41746-026-02413-y). Original [supplement DOI 10.17028/rd.lboro.31368781](https://doi.org/10.17028/rd.lboro.31368781). **CC BY 4.0** verified in Figshare metadata. All three original files are downloaded and MD5/SHA-256 checked. [Manifest](../data/complementary/wu_2026/source_manifest.json).

| Workbook | Data rows | Columns | Positive `RRI` rows | Missing cells |
|---|---|---|---|---|
| `41746_2026_2413_MOESM2_ESM.xlsx` | 6181 | 40 | 564 | 0 |
| `41746_2026_2413_MOESM3_ESM.xlsx` | 6181 | 258 | 564 | 0 |

Both workbooks contain the same 6,181 supplied rows and 40 common columns agree exactly in supplied row order. `RRI` is binary with 564 positives (9.1247% of supplied rows). This is a **different weekly questionnaire-change target**, not the Dutch selected event-day flag. Do not compare these label fractions as injury incidence.

No explicit participant ID or date/week-order field exists in either workbook. `Athlete_Score` is a performance-related variable, not an athlete identifier. Thus the published 142-athlete count cannot be independently verified from released identifiers. **Do not fingerprint genetics/biometrics to reconstruct identities**, equate unique rows with people, or infer chronology from spreadsheet row order. Athlete-independent validation, individual baselines and legitimate temporal histories cannot currently be reconstructed from these workbooks.

The workbooks contain normalized/processed measurements across demographics, strength, biomechanics, nutrition, body composition, history and genetics. Original clinical units, imputation/scaling fit scope and measurement availability must be audited. `tracking_period_injury` and `past_month_injury` need explicit as-of definitions before any predictive use; their names alone do not prove or rule out future leakage. The 255-page supplement provides questionnaires and feature descriptions; no new injury model or feature selection was run.

All exact headers, extrema, missing counts and eligibility decisions are exported in [workbook_columns.csv](../data/complementary/wu_2026/workbook_columns.csv), with a [file profile](../data/complementary/wu_2026/file_profile.csv). We have acquired and assessed this source now, but it remains a reference cohort until longitudinal keys and preprocessing provenance can be obtained through an authorized access route. No authors were contacted.

## Reproduce the complementary track

```powershell
python scripts/acquire_soccermon_subjective.py
python scripts/profile_complementary.py
python scripts/acquire_wu_supplement.py
python scripts/profile_wu_supplement.py
python scripts/write_complementary_report.py
```

For workbook inspection in this run, the bundled Python/pandas/openpyxl runtime was used; exact versions are captured in Wu `profile_summary.json`. Workbooks were read only, never edited or recalculated. Install the pinned requirements for a fresh local environment. Original bytes, metadata, source dictionaries and source-specific profiles remain separate. Acquisition is network-only; subsequent profiling is offline.

## Integration already prepared

[Dataset catalog](../handoff/dataset_catalog.csv) records source role, time basis, verified athlete counts, endpoint and license. [Domain mapping](../handoff/domain_mapping.csv) explicitly distinguishes compatible concepts from interchangeable measurements. The current adapter is descriptive, with unknown report availability time exposed. Future interfaces can reuse these boundaries without inventing missing modalities for Dutch runners or merging unrelated participants.

No source has been pooled, no prediction model trained, and no clinical threshold or risk estimate generated. Milestone 1 review remains the next gate.
