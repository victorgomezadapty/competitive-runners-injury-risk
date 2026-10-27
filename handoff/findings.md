# Findings handoff - Milestone 1

- Day: 74 athletes, 42,766 retained events, 583 injury labels (1.3632%), 63 athletes with a label.
- Week: 42,798 events, 575 labels (1.3435%), 61 athletes with a label.
- Source filtering explains the 77 initial versus 74 retained athletes. There is no sex-by-ID column.
- Correct daily order: unsuffixed E-7 to `.6` E-1. Do not copy reversed lag maps from old PDFs or recent secondary analyses.
- Selected controls use future fitness. Risk/alert interpretations are conditional on source selection.
- Date 0-2673 is relative, not exact 2012-2019 calendar dates. Median selected span 801 days; median 426.5 rows per athlete.
- 49,162 unique training days reconstructed; zero overlap conflicts. Retrospective reconstruction is not prospective availability.
- No blank cells; 241,047 rest-sentinel cells in overlapping subjective histories. Fifteen athletes have all-zero training-success histories; quality review required.
- Paired 7-day contrasts: more volume/intensity/sessions and fewer rest days before flags; recovery ratings are also higher. Association, not causation or proof of safe/unsafe load.
- No consecutive retained injuries; median interval 77 days, minimum 22, partly by design.
- Day primary; Week secondary for 14/21-day summaries. No models fitted. Review report and Phase 2 proposal before proceeding.

Full evidence: [milestone report](../reports/milestone_01_summary.md). Complementary source: [review](../docs/complementary_dataset_review.md).

Two complementary source tracks are acquired, checksummed and profiled. See [file-level assessment](../docs/complementary_data_profile.md), [dataset catalog](dataset_catalog.csv) and [domain mapping](domain_mapping.csv). SoccerMon has a separate working wellness/session adapter; Wu runner workbooks lack explicit participant/time keys and remain quarantined. No row linkage or outcome pooling.

## Phase 2 update

Fixed logistic baselines and sigmoid calibration are now fitted following the user continuation. Three validation designs, training-only preprocessing, prior-history feasibility, bootstrap uncertainty and selected-row review burden are reported in [Phase 2](../reports/phase_02_summary.md). No clinical deployment, tree/neural modeling or cohort pooling.
