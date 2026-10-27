# Limitations

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
- Prediction metrics are now available for exploratory Phase 2 and final sensitivity analyses. Calibration remains conditional on the selected sample; clinical utility, prospective incidence and prevention are not established. Alternative partitions expose uncertainty beyond conditional bootstrap intervals.
