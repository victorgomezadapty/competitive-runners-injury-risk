"""Profile the small companion source and prepare a source-preserving adapter output."""
from pathlib import Path
import sys
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.data.complementary import load_soccermon_tables, observed_wellness_long, load_soccermon_sessions


def main():
    folder = ROOT/'data/complementary/soccermon'
    tables = load_soccermon_tables()
    inventory, header_ids, observed_ids = [], set(), set()
    for name, frame in tables.items():
        row = {'file':name, 'rows':len(frame), 'columns':len(frame.columns),
               'blank_cells':int(frame.isna().sum().sum()), 'first_column':frame.columns[0]}
        participant_cols = [c for c in frame if c.startswith(('TeamA-','TeamB-'))]
        if participant_cols:
            header_ids.update(participant_cols)
            active = [c for c in participant_cols if frame[c].notna().any()]
            observed_ids.update(active)
            dates = pd.to_datetime(frame.iloc[:,0],format='%d.%m.%Y')
            values = frame[participant_cols]
            valid_dates = dates[values.notna().any(axis=1)]
            numeric = values.stack().dropna()
            row.update({'participant_columns':len(participant_cols), 'participants_with_values':len(active),
                        'nonmissing_values':int(values.notna().sum().sum()),
                        'zero_values':int(values.eq(0).sum().sum()), 'date_grid_start':str(dates.min().date()),
                        'date_grid_end':str(dates.max().date()),
                        'observed_start':str(valid_dates.min().date()) if len(valid_dates) else '',
                        'observed_end':str(valid_dates.max().date()) if len(valid_dates) else '',
                        'value_min':numeric.min() if len(numeric) else None,
                        'value_max':numeric.max() if len(numeric) else None})
        inventory.append(row)
    profile = pd.DataFrame(inventory)
    profile.to_csv(folder/'file_profile.csv',index=False)
    long = observed_wellness_long(tables)
    (folder/'processed').mkdir(exist_ok=True)
    long.to_csv(folder/'processed/observed_wellness_long.csv',index=False)
    athlete = long.groupby('participant_key').agg(observed_values=('source_value','size'),
                observed_dates=('source_date','nunique'),first_observed_date=('source_date','min'),
                last_observed_date=('source_date','max'))
    athlete.to_csv(folder/'wellness_by_athlete.csv')
    sessions = load_soccermon_sessions()
    sessions.to_csv(folder/'processed/source_session_reports.csv',index=False)
    injury = tables['subjective/injury/injury.csv']
    dates = pd.to_datetime(injury.timestamp,format='%d.%m.%Y')
    summary = {'dataset_id':'soccermon_subjective','archive_members':len(tables)+1,'csv_files':len(tables),'json_files':1,
               'unique_participant_columns':len(header_ids),'participants_with_any_nonmissing_value':len(observed_ids),
               'team_header_counts':{team:sum(x.startswith(team+'-') for x in header_ids) for team in ['TeamA','TeamB']},
               'wellness_participants_observed':int(long.participant_key.nunique()),
               'wellness_nonmissing_measurements':len(long),
               'wellness_unique_athlete_dates':len(long[['participant_key','source_date']].drop_duplicates()),
               'wellness_observed_start':str(long.source_date.min().date()),
               'wellness_observed_end':str(long.source_date.max().date()),
               'wellness_variables':sorted(long.source_variable.unique()),
               'injury_report_rows':len(injury),'athletes_with_injury_reports':int(injury.player_name.nunique()),
               'injury_report_first_date':str(dates.min().date()),'injury_report_last_date':str(dates.max().date()),
               'session_report_rows':len(sessions),'session_report_athletes':int(sessions.source_athlete_id.nunique()),
               'session_report_first_date':str(sessions.source_date.min().date()),
               'session_report_last_date':str(sessions.source_date.max().date()),
               'session_rows_in_identical_report_groups':int(sessions.potential_duplicate_report.sum()),
               'session_rpe_duration_product_mismatches':int((sessions.srpe-sessions.rpe*sessions.duration).abs().gt(1e-8).sum()),
               'session_source_fields':['srpe','rpe','duration','date'],
               'injury_note':'Reports, not adjudicated incident events; no inferred healthy days',
               'scope':'Source-specific adaptation only; no modeling or joining with Dutch runners'}
    (folder/'profile_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
