"""Executable contracts for indices, information intervals and feature allowlists."""
import numpy as np

FORBIDDEN={'injury','Athlete ID','Date','row_id','feature_start_day','feature_end_day',
           'latest_prior_training_day','latest_source_event_day','latest_source_ascertainment_day',
           'prior_observed_days_56d','prior_coverage_56d'}


def check_feature_list(columns):
    bad=FORBIDDEN.intersection(columns)
    if bad:
        raise ValueError(f'Forbidden predictors: {sorted(bad)}')
    if len(columns)!=len(set(columns)):
        raise ValueError('Duplicate features')


def audit_split(frame, train, calibration, test, lookback, grouped=False, temporal=False,
                selection_lookahead=21):
    parts={'train':np.asarray(train),'calibration':np.asarray(calibration),'test':np.asarray(test)}
    if any(not len(x) for x in parts.values()):
        raise ValueError('Empty split')
    for left,right in [('train','calibration'),('train','test'),('calibration','test')]:
        if set(parts[left])&set(parts[right]):
            raise ValueError('Observation overlap')
        if grouped and set(frame.loc[parts[left],'Athlete ID'])&set(frame.loc[parts[right],'Athlete ID']):
            raise ValueError('Athlete overlap')
        if temporal:
            left_end=frame.loc[parts[left],'Date'].max()+selection_lookahead
            right_start=frame.loc[parts[right],'Date'].min()-lookback
            if left_end>=right_start:
                raise ValueError('Temporal information overlap, including control selection')
    result=[]
    for name,idx in parts.items():
        d=frame.loc[idx]
        if d.injury.nunique()!=2:
            raise ValueError(f'{name} lacks a target class')
        result.append({'partition':name,'rows':len(d),'athletes':d['Athlete ID'].nunique(),
                       'positive_rows':int(d.injury.sum()),'prevalence':d.injury.mean(),
                       'first_day':int(d.Date.min()),'last_day':int(d.Date.max()),
                       'input_lookback_days':lookback,'selection_lookahead_days':selection_lookahead})
    return result
