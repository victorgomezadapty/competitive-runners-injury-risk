"""Calendar exposure windows from complete blocks in a single original weekly row."""
import pandas as pd


def weekly_windows(df):
    out = df[['Athlete ID','Date','injury']].copy()
    for days in (7,14,21):
        blocks = days//7
        for source, name in [('total kms','distance'),('total km Z3-4','z3_4_distance'),
                             ('total km Z5-T1-T2','z5_t1_t2_distance'),('nr. rest days','rest_days'),
                             ('nr. strength trainings','strength_sessions'),
                             ('total hours alternative training','cross_training_hours')]:
            cols = [source if i==0 else f'{source}.{i}' for i in range(blocks)]
            out[f'{name}_{days}d'] = df[cols].sum(axis=1,min_count=blocks)
    out['distance_change_7d'] = df['total kms']-df['total kms.1']
    out['feature_start_day'] = df.Date-21
    out['feature_end_day'] = df.Date-1
    return out
