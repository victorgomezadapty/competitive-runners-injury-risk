"""Small, interpretable within-row summaries; no future-row access."""
import numpy as np
import pandas as pd
from src.data.timelines import DAY_VARIABLES, SUBJECTIVE, day_column


def summarize_pre_event(df, days=7):
    if days not in (3, 7):
        raise ValueError("Milestone 1 implements only 3-day and 7-day summaries")
    out = df[['Athlete ID', 'Date', 'injury']].copy()
    mapping = {'nr. sessions': 'sessions', 'total km': 'distance', 'km Z3-4': 'z3_4_distance',
               'km Z5-T1-T2': 'z5_t1_t2_distance', 'km sprinting': 'sprint_distance',
               'strength training': 'strength_sessions', 'hours alternative': 'cross_training_hours'}
    for source, name in mapping.items():
        out[f'{name}_{days}d'] = df[[day_column(source, s) for s in range(7-days, 7)]].sum(axis=1)
    sessions = df[[day_column('nr. sessions', s) for s in range(7-days, 7)]].to_numpy()
    out[f'rest_days_{days}d'] = (sessions == 0).sum(axis=1)
    for source, name in zip(SUBJECTIVE, ['exertion', 'training_success', 'recovery']):
        values = df[[day_column(source, s) for s in range(7-days, 7)]].replace(-0.01, np.nan)
        out[f'mean_{name}_{days}d'] = values.mean(axis=1)
        out[f'observed_{name}_days_{days}d'] = values.notna().sum(axis=1)
    out['feature_end_day'] = df.Date - 1
    out['feature_start_day'] = df.Date - days
    return out
