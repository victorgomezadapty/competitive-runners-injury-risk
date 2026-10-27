"""Conservative prior-only exposure ledger; source availability is not logging time."""
import numpy as np
import pandas as pd
from src.data.timelines import day_column


def prior_distance_baselines(raw, history_days=56, minimum_days=28, selection_delay=21):
    """For E, use unique days E-(history_days+7)..E-8, supplied by rows < E.

    Never use injury labels. No zero filling. The original future-conditioned
    release selection persists; this is an availability audit, not prospective
    certification. Only the known-athlete sensitivity experiment uses it.
    """
    if minimum_days < 1 or minimum_days > history_days:
        raise ValueError('Invalid minimum history')
    parts=[]
    for suffix in range(7):
        parts.append(pd.DataFrame({'athlete':raw['Athlete ID'],
            'training_day':raw.Date-(7-suffix),'source_event_day':raw.Date,
            'available_event_day':raw.Date+selection_delay,
            'distance':raw[day_column('total km',suffix)]}))
    ledger=pd.concat(parts,ignore_index=True)
    keys=['athlete','training_day']
    spread=ledger.groupby(keys).distance.agg(['min','max'])
    if (spread['max']-spread['min']).gt(1e-8).any():
        raise ValueError('Conflicting source distance histories')
    ledger=ledger.sort_values('available_event_day').drop_duplicates(keys)
    groups={k:g for k,g in ledger.groupby('athlete')}
    rows=[]
    for index,row in raw.iterrows():
        event=int(row.Date)
        g=groups[row['Athlete ID']]
        selected=g[g.training_day.between(event-history_days-7,event-8)&g.available_event_day.lt(event)]
        n=len(selected)
        baseline=7*selected.distance.mean() if n>=minimum_days else np.nan
        distance=sum(row[day_column('total km',s)] for s in range(7))
        rows.append({'row_id':index,'prior_expected_distance_7d':baseline,
                     'distance_deviation_7d':distance-baseline,
                     'prior_observed_days_56d':n,'prior_coverage_56d':n/history_days,
                     'latest_prior_training_day':selected.training_day.max(),
                     'latest_source_event_day':selected.source_event_day.max(),
                     'latest_source_ascertainment_day':selected.available_event_day.max()})
    return pd.DataFrame(rows).set_index('row_id').reindex(raw.index)
