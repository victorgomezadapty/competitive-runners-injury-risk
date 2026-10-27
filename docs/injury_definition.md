# Injury definition and target-construction gate

Status: **understood sufficiently for descriptive analysis and fixed Phase 2 research baselines**. The user authorized continuation on 2026-10-25. The original target and horizon remain unchanged; current results are in reports/phase_02_summary.md.

## Source-defined endpoint

The endpoint is a training-log flag indicating inability to complete the scheduled session because of injury, including an interrupted or skipped session. It is not a verified clinical diagnosis or tissue-specific onset date.

The creators required three injury-free weeks before an injury event. Healthy comparison events required full fitness for three weeks both before and after their event day. Missing/anomalous events were removed; further injury flags within three weeks of an index injury were excluded as the same injury. Thus retained flags approximate selected incident episodes, not every injured day or every injury in the original log. Absence of consecutive released labels is partly imposed by design.

## Time alignment

For event day E, inputs end at E-1. Day Approach provides E-7 through E-1; no suffix = E-7, `.1` = E-6, ..., `.6` = E-1. Week Approach: no suffix = E-7..E-1, `.1` = E-14..E-8, `.2` = E-21..E-15. This follows the corrected Dataverse README v2 (2024); the locally consulted 2021 PDF has the old daily ordering.

The current task is descriptive comparison before selected injury-labeled versus healthy events. A later prediction experiment would use information through t=E-1 to classify the label at E=t+1, conditional on the released selection process. This is not yet a prospective daily injury probability.

## Unresolved and unavailable

No diagnosis, anatomical site, mechanism, severity, duration, clinician confirmation, complete raw flags, or exact calendar origin. Source preprocessing cannot be rerun from these files. Three- or seven-day outcome horizons cannot be constructed by assuming omitted dates are healthy.

## Evidence

- [Original study, Methods/Design and Feature Construction, pp. 1523-1524](https://doi.org/10.1123/ijspp.2020-0518)
- [Original university PDF](https://pure.rug.nl/ws/portalfiles/portal/183763727/_15550273_International_Journal_of_Sports_Physiology_and_Performance_Injury_Prediction_in_Competitive_Runners_With_Machine_Learning.pdf)
- [Corrected source README](https://dataverse.nl/api/access/datafile/422690?format=original)
- [2024 erratum record](https://pubmed.ncbi.nlm.nih.gov/38897576/)

The future-conditioned selection of healthy controls is an upstream design limitation. Removing future variables from our feature functions does not undo it.
