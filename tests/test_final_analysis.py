import numpy as np
import pandas as pd
import pytest
from scripts.run_final_analysis import athlete_weights,matched_features


def test_weighting_equalizes_total_influence_without_class_labels():
    ids=pd.Series([1,1,1,2,2,3])
    weights=athlete_weights(ids)
    totals=pd.Series(weights).groupby(ids).sum()
    assert np.allclose(totals,totals.iloc[0])
    assert np.isclose(weights.mean(),1)


def test_matching_rejects_target_disagreement():
    from src.data.load_data import load_data
    day=load_data('day').iloc[:20].copy()
    week=load_data('week').copy()
    matched=matched_features(day,week)
    assert not matched.duplicated(['Athlete ID','Date']).any()
    first=matched.iloc[0]
    mask=week['Athlete ID'].eq(first['Athlete ID']) & week.Date.eq(first.Date)
    week.loc[mask,'injury']=1-week.loc[mask,'injury']
    with pytest.raises(ValueError,match='targets disagree'): matched_features(day,week)
