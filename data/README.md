# Original-source acquisition

Use [DataverseNL DOI 10.34894/UWU9PV](https://doi.org/10.34894/UWU9PV), not a Kaggle mirror. Retrieved for this milestone on 2026-10-25. The acquired dataset version is **2.0**, published 2024-06-05T13:13:16Z. Data license: **CC0-1.0** as recorded in original metadata. Dataset creators: Sofie Lövdal, Ruud J.R. den Hartigh, George Azzopardi.

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
| `day_approach_maskedID_timeseries.csv` | 47972 | 13547450 | Source data/documentation |
| `main.ipynb` | 47973 | 27126 | Reference code, read only |
| `README.txt` | 422690 | 5750 | Source data/documentation |
| `week_approach_maskedID_timeseries.csv` | 47971 | 15152612 | Source data/documentation |

The full exact checksums and URLs are in [source_manifest.json](source_manifest.json). Raw files, interim reconstruction, processed descriptive windows, and the copyright-restricted original-paper PDF are excluded from Git. Reports/tables/figures are retained for review. Optional `python scripts/fetch_paper.py` acquires the university paper; it needs pypdf only for optional local text inspection, not for the analysis pipeline.

The `raw/` directory also contains the saved Dataverse metadata response. `interim/` contains retrospective reconstructed training days with source-event provenance; `processed/` contains within-row 3- and 7-day descriptive summaries. Neither contains predictions. Do not combine the representations as independent samples: they heavily overlap and select somewhat different events.
