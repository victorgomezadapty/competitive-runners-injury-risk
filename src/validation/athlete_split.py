"""Outer athlete-disjoint folds with an independent inner calibration cohort."""
import numpy as np
from sklearn.model_selection import GroupKFold,GroupShuffleSplit


def athlete_partitions(df,n_splits=5,seed=20261025,calibration_fraction=.20):
    outer=GroupKFold(n_splits=n_splits,shuffle=True,random_state=seed)
    for fold,(development,test) in enumerate(outer.split(df,groups=df['Athlete ID'])):
        dev=df.iloc[development]
        inner=GroupShuffleSplit(n_splits=1,test_size=calibration_fraction,random_state=seed+fold+1)
        train_local,cal_local=next(inner.split(dev,groups=dev['Athlete ID']))
        labels=df.index.to_numpy()
        yield fold,labels[development[train_local]],labels[development[cal_local]],labels[test]
