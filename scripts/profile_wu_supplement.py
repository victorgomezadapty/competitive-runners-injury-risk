"""Read-only workbook audit. Never infer participant identity from biometrics/genetics."""
from pathlib import Path
import hashlib
import json
import platform
import importlib.metadata
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT/'data/complementary/wu_2026'
    manifest = json.loads((folder/'source_manifest.json').read_text())
    tables, profiles, columns = {}, [], []
    id_names = {'athlete id','athlete_id','participant id','participant_id','id','runner_id','subject id','subject_id'}
    time_names = {'date','timestamp','week_index','week_number','week','time','visit_date'}
    for source in manifest['files']:
        path = folder/'raw'/source['filename']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256']
        if path.suffix != '.xlsx':
            continue
        book = pd.ExcelFile(path,engine='openpyxl')
        for sheet in book.sheet_names:
            frame = pd.read_excel(book,sheet_name=sheet)
            tables[path.name] = frame
            profile = {'file':path.name,'sheet':sheet,'rows':len(frame),'columns':len(frame.columns),
                       'missing_cells':int(frame.isna().sum().sum()),
                       'exact_duplicate_rows':int(frame.duplicated().sum()),
                       'explicit_id_columns':[str(c) for c in frame if str(c).lower() in id_names],
                       'explicit_time_columns':[str(c) for c in frame if str(c).lower() in time_names],
                       'RRI_positive_rows':int(frame.RRI.sum()),'RRI_prevalence':float(frame.RRI.mean())}
            profiles.append(profile)
            for col in frame:
                values = frame[col]
                columns.append({'file':path.name,'sheet':sheet,'original_column':str(col),
                                'dtype':str(values.dtype),'nonmissing':int(values.notna().sum()),
                                'distinct_values':int(values.nunique()),'observed_min':values.min(),
                                'observed_max':values.max(),'unit_status':'Processed/normalized; original units not recoverable here',
                                'use_decision':'Outcome only' if col=='RRI' else 'Quarantined; identity, availability and preprocessing audit required'})
    names = sorted(tables)
    small, large = tables[names[0]], tables[names[1]]
    common = small.columns.intersection(large.columns)
    identical = bool(small[common].equals(large[common]))
    pd.DataFrame(profiles).to_csv(folder/'file_profile.csv',index=False)
    pd.DataFrame(columns).to_csv(folder/'workbook_columns.csv',index=False)
    result = {'dataset_id':'wu_2026_supplement','workbooks':profiles,
              'shared_columns':len(common),'shared_columns_identical_in_supplied_row_order':identical,
              'publication_reported_athletes':142,'unique_athletes_file_verified':None,
              'athlete_count_limitation':'No explicit participant identifiers released; do not infer identities from repeated biometrics or genetic signatures',
              'time_limitation':'No explicit date or week-order key; spreadsheet row order is not verified chronology',
              'modeling_decision':'No modeling, pooling, grouped validation or temporal reconstruction from these workbooks',
              'potential_leakage_review':['tracking_period_injury','past_month_injury','upstream normalization/imputation/feature selection'],
              'read_environment':{'python':platform.python_version(),
                                  'pandas':importlib.metadata.version('pandas'),'openpyxl':importlib.metadata.version('openpyxl')}}
    (folder/'profile_summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
