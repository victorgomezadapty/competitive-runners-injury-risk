# Complementary longitudinal data review

Reviewed on 2026-10-25. Scope: source evaluation and a parallel data-understanding track only. No injury prediction models and no linkage of unrelated participants.

## Recommendation

Keep the Lovdal Dataverse day representation as the primary competitive-runner cohort. Add a separate, explicitly named recovery/wellness cohort at the data-source and software-interface level now. SoccerMon's small subjective archive is an immediately usable candidate for that track. It contains sleep, fatigue, soreness, stress, mood and readiness reports that are absent from the runner release. It is women's elite soccer data, so it cannot supply missing measurements for the Dutch runners or validate runner injury predictions.

The strongest population match identified is Wu et al. (2026), a prospective multidisciplinary endurance-runner study. Its article explicitly makes processed data available in supplementary materials. Its raw data are available by contact and include anonymity restrictions. The supplementary deposit inventory and CC BY 4.0 license were verified from its Figshare API metadata during the parallel track. All three supplementary files are now acquired and checksum-verified. Both workbooks contain 6,181 rows with 564 positive RRI labels, but neither exposes an explicit participant identifier or date/week-order key. The published 142-athlete count therefore remains unverified from released identifiers. This source is a multidisciplinary reference, unsuitable for individual timelines or athlete-disjoint validation in its current public form. See complementary_data_profile.md.

## Sources evaluated

| Source | Complementary information | Access and license evidence | Decision |
|---|---|---|---|
| Wu et al., *Multidisciplinary prediction of running-related injuries using machine learning* (2026), DOI 10.1038/s41746-026-02413-y | Competitive endurance runners; baseline/history, strength, biomechanics, body composition, nutrition and genetic variables; weekly training and injury surveillance | Article full-text XML retrieved from Europe PMC. Authors state processed data are in supplementary materials; raw data require contact. Supplementary deposit DOI 10.17028/rd.lboro.31368781 API metadata confirms CC BY 4.0, one PDF and two spreadsheets. | Best population match; inspect supplementary records before any inclusion. No assumption that normalized processed variables retain raw clinical units or true prospective availability. |
| SoccerMon, DOI 10.5281/zenodo.10033832; accompanying Scientific Data article DOI 10.1038/s41597-024-03386-x | Longitudinal session load, wellness/sleep, fatigue, readiness, soreness, stress, injury and illness reports; two elite women's soccer teams, 2020–2021 | Zenodo lists `subjective.zip`, about 705.8 kB, publisher MD5 `a3e86aeca611f77c9331a535eae00bf7`. Article and project identify CC BY 4.0. The much larger objective archives total roughly 99 GB on Zenodo and are unnecessary for this stage. | Acquire/profile subjective archive separately. Treat as a complementary athlete-monitoring methods cohort, not competitive-running outcome validation. |
| PMData, *PMData: A Sports Logging Dataset*, DOI 10.1145/3339825.3394926 | Fitbit sleep, resting heart rate, activity; subjective session RPE, wellness, readiness, injury/pain; five-month lifelogging | Official Simula site and OSF vx4bk. Full archive about 1.4 GB. Project page currently says CC BY 4.0, whereas original paper states CC BY-NC 4.0. Participant reporting also needs file-level verification: paper describes 16 persons while one demographic sentence sums to 15. | Alternative only; no full archive acquisition during this review. Resolve license/version and cohort counts before reuse. Does not establish a competitive-running cohort or an HRV series. |
| Generic/synthetic athlete overtraining or triathlete datasets | Often advertise HRV, sleep and injury together | Provenance, real-world collection and label construction may be weak or explicitly synthetic | Exclude as empirical injury evidence. Synthetic data may test software only if clearly labeled. |

## Wu runner cohort: what is confirmed

The authors report 142 analyzed runners and 6,181 participant-week samples after a prospective year of monitoring; 149 runners were initially recruited. The 6,181 rows are verified in both acquired workbooks; the 142-athlete count remains publication-reported because participant IDs are absent. Recruitment included competitive endurance runners aged 14–50 with at least three years' competitive running and at least four hours running per week. They were injury-free at initiation. This differs from the single Dutch team and its released selected event-day sample.

Weekly online questionnaires included running volume, other physical training and Oslo Sports Trauma Research Centre Overuse Injury Questionnaire information. Their operational outcome required an increase in questionnaire score for any body region compared with the previous week and the participant identifying the problem as running-related. A weekly change in a questionnaire-defined complaint is not identical to the Lovdal selected injury-labeled event day, nor necessarily a new clinically verified diagnosis. Their publication says samples without prior-week data were excluded. Raw injury chronology, recurrent-complaint handling and exact processed target fields need independent inspection.

Multidisciplinary measurements include strength, biomechanics, bone/body composition, nutrition and genetic markers, with some repeated laboratory assessments during follow-up. These would complement runner training histories conceptually, but they were measured in different people. The public processed data were normalized; some raw metrics must remain normalized for anonymity. Original baseline measurements, later visits and prospective tracking must remain distinguishable. A future adapter must ensure a laboratory value was actually available at the prediction cutoff.

The article's methodological description includes normalization, imputation and feature ranking using broad data pools, and row-stratified cross-validation. These choices must be audited before adopting its prepared features or comparing reported AUCs. Its published performance is a historical study result, not evidence of leakage-safe transportability or a target to optimize toward.

Confirmed data availability wording was extracted from the authors' full-text XML: processed data are shared in supplementary materials, while raw data are available upon contact and some metrics must remain normalized. No author was contacted. Code is linked by the article to `henrywu0709/TSNN-TSGNN-for-prognostic-modelling`; source code was not run. The XML is retained under `data/complementary/review_sources/wu2026.xml` for provenance. The parallel track saved the Figshare API response under `data/complementary/wu_2026/metadata.json`. It confirms CC BY 4.0 and the following inventory; byte sizes are independently checked against acquired files and publisher MD5, with local SHA-256 recorded:

| File | Publisher-reported bytes |
|---|---:|
| `MOESM1_ESM.pdf` | 1,659,745 |
| `MOESM2_ESM.xlsx` | 1,188,998 |
| `MOESM3_ESM.xlsx` | 8,187,498 |

The two workbooks have 40 and 258 columns; their 40 common columns agree exactly in supplied row order. Explicit participant/time keys are absent. Do not fingerprint genetic or biometric values to reconstruct identities, or assume row order is chronology. Original units and prospective preprocessing are not recoverable from the normalized table alone. tracking_period_injury and past_month_injury need as-of definitions before use. Full file and column profiles are retained.

## SoccerMon: parallel track and limits

The official article reports 50 players and 33,849 subjective reports: 16,261 training-load reports, 17,002 wellness reports, 306 injury reports, 32 illness reports and 248 game-performance reports. The parallel acquisition/profile completed during this milestone verified the downloaded `subjective.zip` publisher MD5 and local SHA-256 `338e9878fbed1f941cfc37b3f012cb356f97cc0f726e80a79aa5c8e67cc2a87c`. The archive contains 19 members: 18 CSV files plus `session.json`. Direct inspection found 50 participant identifiers (Team A 27, Team B 23), 17,008 athlete-date wellness observations with 118,959 recorded values across seven domains, covering 2020-01-09 to 2021-12-31. The downloaded injury file has 162 report rows for 15 participants. These observed counts differ from the article's report totals and must remain explicitly source-specific; their cause is not established. Do not silently substitute article counts for archive counts.

Report count must not be confused with participant-days or injury onsets. A participant may have several sessions, duplicate/subsequent submissions, multiple report types, and missing days. The injury file fields include participant, JSON-formatted location/severity content and timestamp. Session JSON includes `srpe`, `rpe`, `duration` and `date`.

Primary-source measurement audit: Figure 1 shows session duration in minutes and RPE 1–10; all 16,265 acquired session records satisfy `srpe = rpe × duration`. Figure 2 anchors readiness 1–10 from not ready to eager, fatigue 1–5 from tired to fresh, and sleep quality 1–5 from insomnia to excellent sleep. Thus high fatigue scores mean greater freshness in that instrument. Sleep duration is elicited in hours/minutes. Methods prose places other wellness ratings on 1–5, but Table 1 lists stress 1–10: retain this internal discrepancy until the export and questionnaire resolve it. The report date can be backdated; offline synchronization means event date does not prove availability time. Injury reports are subjective pain/location notifications, not diagnoses, and consecutive reports remain separate. See [the primary article](https://doi.org/10.1038/s41597-024-03386-x), Methods, Table 1 and Figures 1–3. Do not import PMData scale definitions merely because both use PMSys.

The subjective archive is sufficient to inspect session load and wellness availability without acquiring GPS records. Sleep duration/quality, fatigue, mood, readiness, muscle soreness and stress are useful complementary domains. Sleep measurements here are subjective; this is not a nocturnal-HRV dataset. Injury reports may represent symptoms, ongoing problems, severity or availability rather than fresh incident events. Establish the exact schema, reporting prompts, timestamp semantics, repeated reports and target interpretation before event counts or cross-source comparisons.

The data are a different sport, sex composition, coaching context and surveillance system. Soccer involves match exposure, contacts and accelerations that differ from distance running. This source can support a separate demonstration of how daily athlete state might be represented and how missingness/reporting timestamps are handled. It cannot establish that a soccer-associated signal transfers to runners or fill any Dutch runner's sleep, soreness or injury history.

## Architecture decisions made now

1. Source boundaries remain explicit: retain original bytes and source-specific manifests under `data/complementary/<source>/`, with download URLs, version, license, checksums and inspection status.
2. Namespace identifiers by source; an identical numeric athlete ID in two sources never means the same person. Preserve the original variable name, timestamp and units alongside any later common-domain mapping.
3. Use common domains (volume, intensity, recovery, rest, subjective state) to organize adapters, documentation and visual components. Domain alignment does not imply scale equivalence or permit pooled rows.
4. Each source keeps its own outcome contract: event definition, prediction cutoff, horizon, label availability, comparison selection and exclusions. No universal `injury=1` is assumed.
5. Calendar timestamps, relative-day indices, observation times and report-submission times are different fields. No matching on a calendar or relative date across cohorts creates shared measurements.
6. If a common state interface is implemented after review, use a long-form record such as `source_id, participant_id, observation_time, available_time, domain, original_variable, value, unit, missingness_reason`. The current hito requires documentation and profiling, not implementation of a predictive engine.
7. Keep all analysis within each cohort. A future cross-source evaluation must predefine compatible features and outcomes and explicitly assess transportability; it cannot be described as external validation merely because a second file exists.

## Immediate acceptance checklist

- SoccerMon subjective ZIP acquisition/checksum and basic profile are complete in the parallel track. Preserve its manifest and exact member inventory. Finish source-specific duration units, questionnaire anchors, timestamp semantics and target-definition audit before interpreting load or injury incidence.
- Wu files and CC BY 4.0 license are verified; file inspection confirms no explicit participant/time keys. Keep these processed records quarantined for longitudinal/grouped analysis. Do not request raw data or contact authors without user authorization.
- Any future usable release would need participant/time keys, original outcome semantics and preprocessing provenance. A normalized ML-ready table alone may not support the intended longitudinal audit.
- Do not train models or produce risk scores in either track during Milestone 1. Leave the proposed next work for review.

## Primary references

- [Wu et al., npj Digital Medicine article](https://www.nature.com/articles/s41746-026-02413-y)
- [Wu et al., Europe PMC full-text XML endpoint](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC12987969/fullTextXML)
- [Wu et al., university supplementary deposit DOI](https://doi.org/10.17028/rd.lboro.31368781)
- [University publication record identifying the supplementary deposit](https://publications.lboro.ac.uk/publications/all/collated/hussm.html)
- [SoccerMon Zenodo record](https://zenodo.org/records/10033832)
- [SoccerMon primary data descriptor](https://pmc.ncbi.nlm.nih.gov/articles/PMC11139986/)
- [SoccerMon official project page](https://datasets.simula.no/soccermon/)
- [PMData official project page](https://datasets.simula.no/pmdata/)
- [PMData original paper from Simula](https://web-backend.simula.no/sites/default/files/publications/files/3339825.3394926.pdf)
- [PMData OSF project](https://osf.io/vx4bk/)
