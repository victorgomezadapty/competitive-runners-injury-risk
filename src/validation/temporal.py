"""Outcome-blind calendar partitions with information-span purging."""
import numpy as np


def calendar_cutoffs(df):
    start,end=int(df.Date.min()),int(df.Date.max())
    span=end-start+1
    return start+int(.60*span),start+int(.80*span)


def temporal_partitions(df,lookback=63,selection_lookahead=21,train_groups=None,
                        calibration_groups=None,test_groups=None,known_only=True):
    cal_start,test_start=calendar_cutoffs(df)
    # Left partitions must finish ascertainment before the next input window.
    train=df.index[df.Date.lt(cal_start-lookback-selection_lookahead)]
    cal=df.index[df.Date.ge(cal_start)&df.Date.lt(test_start-lookback-selection_lookahead)]
    test=df.index[df.Date.ge(test_start)]
    if train_groups is not None:
        train=train[df.loc[train,'Athlete ID'].isin(train_groups)]
        cal=cal[df.loc[cal,'Athlete ID'].isin(calibration_groups)]
        test=test[df.loc[test,'Athlete ID'].isin(test_groups)]
    if known_only:
        known=set(df.loc[train,'Athlete ID'])
        cal=cal[df.loc[cal,'Athlete ID'].isin(known)]
        test=test[df.loc[test,'Athlete ID'].isin(known)]
    return np.asarray(train),np.asarray(cal),np.asarray(test)
