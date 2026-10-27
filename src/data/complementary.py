"""Separate SoccerMon source adapter. No cross-cohort athlete or outcome joins."""
from pathlib import Path
import hashlib
import json
import zipfile
import pandas as pd
from src.data.load_data import ROOT


def load_soccermon_tables(root=ROOT):
    folder = Path(root)/'data/complementary/soccermon'
    manifest = json.loads((folder/'source_manifest.json').read_text())
    archive_path = folder/'raw/subjective.zip'
    if hashlib.sha256(archive_path.read_bytes()).hexdigest() != manifest['sha256']:
        raise ValueError('SoccerMon source differs from acquired checksum')
    with zipfile.ZipFile(archive_path) as archive:
        return {name:pd.read_csv(archive.open(name)) for name in archive.namelist() if name.endswith('.csv')}


def observed_wellness_long(tables):
    """Preserve source values and scale names; do not impute padded calendar grids.

    Source dates are daily calendar labels. Time-of-day and prospective recording
    availability are unknown. This table is not prediction-ready.
    """
    parts = []
    for name, frame in tables.items():
        if '/wellness/' not in name:
            continue
        date_col = frame.columns[0]
        long = frame.melt(id_vars=[date_col], var_name='source_athlete_id', value_name='source_value')
        long = long.rename(columns={date_col:'source_date'}).dropna(subset=['source_value'])
        long['source_date'] = pd.to_datetime(long.source_date, format='%d.%m.%Y')
        long['dataset_id'] = 'soccermon_subjective'
        long['participant_key'] = 'soccermon::'+long.source_athlete_id
        long['source_variable'] = Path(name).stem
        long['source_file'] = name
        long['availability_rule'] = 'Calendar date only; recording time unknown'
        parts.append(long)
    result = pd.concat(parts, ignore_index=True)
    if result.duplicated(['participant_key','source_date','source_variable']).any():
        raise ValueError('Duplicate source wellness observation')
    return result.sort_values(['participant_key','source_date','source_variable'])


def load_soccermon_sessions(root=ROOT):
    folder = Path(root)/'data/complementary/soccermon'
    path = folder/'raw/subjective.zip'
    manifest = json.loads((folder/'source_manifest.json').read_text())
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest['sha256']:
        raise ValueError('SoccerMon source checksum changed')
    with zipfile.ZipFile(path) as archive:
        sessions = json.loads(archive.read('subjective/training-load/session.json'))
    rows = []
    for athlete, records in sessions.items():
        for index, record in enumerate(records):
            rows.append({**record,'source_athlete_id':athlete,'source_record_index':index})
    result = pd.DataFrame(rows)
    result['source_date'] = pd.to_datetime(result['date'],format='%d.%m.%Y')
    result['dataset_id'] = 'soccermon_subjective'
    result['participant_key'] = 'soccermon::'+result.source_athlete_id
    # Multiple identical reports can be genuine repeated sessions or duplicates.
    # Without stable source session IDs, flag them but never silently deduplicate.
    result['potential_duplicate_report'] = result.duplicated(['source_athlete_id','date','srpe','rpe','duration'],keep=False)
    return result.sort_values(['participant_key','source_date','source_record_index'])
