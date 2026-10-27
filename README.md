# Longitudinal Training Load & Injury Risk in Competitive Runners

*Leakage-aware analysis of training, recovery and injury-labeled events in competitive runners.*

**Sports Rehabilitation & Human Performance · Physiotherapy Data Science**  
Analysis: **Víctor Andrés Gómez López**, research release 1.0.0, 2026-10-26.

Completed exploratory research case study and interactive presentation. Clinical validity and injury prevention are not established.

- [Interactive study](https://competitive-runners-injury-risk.vercel.app): animated presentation, five athlete histories, validation and review burden; ES/EN.
- [Discussion](docs/discussion.md), [documented narrative search](docs/literature_search.md), [BibTeX](docs/references.bib).
- [Kaggle dataset](https://www.kaggle.com/datasets/vctorandrsgmezlpez/competitive-runners-longitudinal-research) and [executable release-audit notebook](https://www.kaggle.com/code/vctorandrsgmezlpez/competitive-runners-longitudinal-audit).
- [Portfolio](https://victor-gomez-portfolio.vercel.app/projects/competitive-runners-injury-risk/).

## Source and audited population

Original measurements: **Sofie Lövdal, Ruud J. R. den Hartigh and George Azzopardi**, [Dataverse DOI 10.34894/UWU9PV](https://doi.org/10.34894/UWU9PV), v2.0, CC0. [Original study](https://doi.org/10.1123/ijspp.2020-0518), [erratum](https://doi.org/10.1123/ijspp.2024-0251). This project did not collect these measurements. [Rights inventory](DATA_LICENSE.md), [acquisition and checksums](data/README.md).

| Representation | Unique athletes | Selected rows | Injury labels | Label fraction |
|---|---:|---:|---:|---:|
| Day | 74 | 42,766 | 583 | 1.3632% |
| Week | 74 | 42,798 | 575 | 1.3435% |
| Matched extension | 74 | 42,680 | 575 | 1.3472% |

Counts are computed from files. The article distinguishes 77 initial and 74 retained athletes. One competitive Dutch middle/long-distance team does not establish recreational-running generalization.

**A row is a selected event preceded by training history.** Injury prevented completion of a scheduled session. Healthy controls required full fitness three weeks before **and after**; nearby injury events and missing/anomalous records were excluded. The label fraction is **not prospective incidence**. Date is relative (0–2673); calendar origin is unavailable. Unselected days are not healthy/rest days.

**Corrected lag order:** unsuffixed Day = E−7, `.6` = E−1. Week unsuffixed = E−7..E−1; `.1` = E−14..E−8. The 2024 README and overlap checks govern. Subjective −0.01 is a rest-day sentinel. [Target](docs/injury_definition.md), [dictionary](docs/data_dictionary.md), [cohort](docs/cohort_definition.md), [leakage audit](docs/leakage_audit.md).

## Findings and boundaries

[Milestone 1](reports/milestone_01_summary.md): cohort, observation spans, missingness, training domains, five timelines and paired athlete-level pre-event contrasts.

[Phase 2](reports/phase_02_summary.md) remains primary: fixed logistic models, independent calibration, training-only transformations, past-only personal-baseline feasibility and temporal/athlete validation.

| Evaluation | Test athletes | AP | ROC-AUC | Brier |
|---|---:|---:|---:|---:|
| Known / future | 23 | 0.0222 | 0.5839 | 0.01664 |
| Unseen / all periods | 74 | 0.0201 | 0.6330 | 0.01342 |
| Unseen / future | 32 | 0.0200 | 0.5456 | 0.01584 |

AP is non-interpolated average precision. Test label fractions differ (1.36–1.69%); compare frequency references, raw/calibrated results and uncertainty in the report. Calibration is not uniformly beneficial. In the combined unseen/future test, the 10% calibration review budget flags 14.2% of selected rows, captures 14.8% of retained labels and requires about 60 reviews per captured positive. These are **not alerts per true athlete-day**.

[Final completion](reports/final_project_summary.md): matched 14/21-day history, athlete-balanced fitting, fixed forest and three combined-validation partitions; all 84 base fits over 21 split cases retained. No best test result is promoted as a final predictor.

Training load ≠ injury. Association ≠ causation. Probability ≠ diagnosis. Prediction ≠ prevention. No browser model, clinical bands, treatment counterfactuals or model artifact is deployed. The website explores saved held-out results.

## Reproduce

Python 3.14 and Node 24 for the static site. Exact research versions are pinned. Run from repository root:

```bash
python -m pip install -r requirements.txt
python scripts/reproduce.py --notebooks
cd web
npm test
npm run build
```

Acquisition needs network; analysis runs locally. Add `--complementary` for the separate companion sources. Website builds consume committed exports and need no Python service/account. Upstream `main.ipynb` is read as text, never executed. Kaggle's authored notebook checks the release and displays saved results; the full training pipeline is in this repository.

Commands: `scripts/run_milestone_01.py`, `scripts/run_phase_02.py`, `scripts/write_phase_02_report.py`, `scripts/run_final_analysis.py`, `scripts/build_release.py`. [Publication instructions](docs/publication.md).

## Repository

```text
config/       recorded exploratory protocols
data/         manifests and independent-source catalogs; raw/derived data local
src/          reusable loading, windows, baselines, splits, metrics and plots
scripts/      acquisition, analysis, reporting and release packaging
notebooks/    01–11 authored result/exploration views
tests/        scientific contracts
reports/      descriptive, primary and sensitivity results; verification
docs/         target, methodology, limitations, discussion and search
handoff/      feature registry, dataset catalog and future architecture
web/          responsive static presentation, original SVGs and audited exports
.github/      research-contract and static-build CI
```

Some original architecture placeholders document optional methods; they are not claimed as implemented components. Imports, tests and manifests identify the working pipeline. Deep learning and advanced causal models are not required to support this analysis.

## Complementary sources and future research

[Complementary review](docs/complementary_dataset_review.md), [file profiles](docs/complementary_data_profile.md): SoccerMon adds a separate wellness/session adapter; Wu 2026 lacks explicit participant/time keys and remains excluded from longitudinal validation. Their original raw files are not redistributed in this Kaggle bundle. These sources and `running-injury-clinic` involve different people and outcomes; integration is conceptual/software-level, never row linkage.

Future clinical evaluation needs representative continuous logging, complete clinical ascertainment, available-at timestamps and external cohorts. [Limitations](docs/limitations.md) explain why exact incidence, event lead time and causal intervention effects cannot be recovered here.

## Cite and reuse

Cite [this analysis](CITATION.cff) and the original dataset separately. Own software/prose: [MIT](LICENSE). Original data and dedicated tabular exports: CC0. Articles, companion sources and fonts retain separate terms in [DATA_LICENSE.md](DATA_LICENSE.md). No third-party article or figure is republished.
