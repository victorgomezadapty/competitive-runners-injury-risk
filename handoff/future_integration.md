# Future integration architecture

Project line: **Sports Rehabilitation & Human Performance**. This repository is the longitudinal exposure component of a broader Physiotherapy Data Science portfolio.

Keep `running-injury-clinic` independent: it describes movement/biomechanics in different people and under another protocol. This repository describes histories before selected injury flags. Do not join participants or training days across cohorts.

Create source-specific adapters around common domain concepts: cohort ID, source athlete ID, relative/calendar time basis, measurement time, availability time, domain, original variable, units, quality/sentinel flags, target definition and ascertainment. Namespace IDs by source. Keep source-specific data dictionaries and outcome registries; missing modalities remain missing for that cohort.

The future Longitudinal Athlete State Engine can reuse prior-only baseline logic, window definitions, validation contracts, uncertainty displays and risk communication. A complementary sleep/HRV/wellness cohort can test those measurement modules independently; it cannot retrospectively add HRV or sleep to the Dutch runners or validate an injury endpoint it never measured.

The companion source review and acquisition are part of this milestone, not postponed row-level integration. See `docs/complementary_dataset_review.md`. No software architecture connection establishes biological equivalence or transportability.
