"""Invariants that would invalidate longitudinal risk evaluation if broken."""
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import average_precision_score
from src.data.timelines import day_column
from src.features.athlete_baselines import prior_distance_baselines
from src.features.rolling import weekly_windows
from src.validation.temporal import temporal_partitions
from src.validation.athlete_split import athlete_partitions
from src.validation.leakage import audit_split,check_feature_list
from src.models.baseline import TrainingQuantileClipper,logistic_pipeline
from src.models.calibration import calibrate_frozen
from src.analysis.prediction_metrics import score_budget_threshold,_weighted_ap


def history(events):
    rows=[]
    for e in events:
        r={'Athlete ID':1,'Date':e,'injury':e%2}
        for s in range(7):
            r[day_column('total km',s)]=e-7+s+10
        rows.append(r)
    return pd.DataFrame(rows)


def test_personal_baseline_respects_source_ascertainment_and_future_invariance():
    raw=history(range(101))
    result=prior_distance_baselines(raw)
    assert result.loc[100,'prior_expected_distance_7d']==7*67
    assert result.loc[100,'prior_observed_days_56d']==41
    assert result.loc[100,'latest_source_ascertainment_day']<100
    future=pd.concat([raw,history([200])],ignore_index=True)
    future.injury=1-future.injury
    pd.testing.assert_series_equal(result.loc[100],prior_distance_baselines(future).loc[100])
    assert np.isnan(result.loc[10,'prior_expected_distance_7d'])


def test_temporal_information_spans_and_label_blind_cutoffs():
    d=pd.DataFrame({'Date':range(1000),'Athlete ID':1,'injury':np.arange(1000)%2})
    tr,ca,te=temporal_partitions(d)
    audit_split(d,tr,ca,te,lookback=63,temporal=True)
    assert d.loc[tr,'Date'].max()+21<d.loc[ca,'Date'].min()-63
    assert d.loc[ca,'Date'].max()+21<d.loc[te,'Date'].min()-63
    inverted=d.copy(); inverted.injury=1-inverted.injury
    for left,right in zip((tr,ca,te),temporal_partitions(inverted)):
        assert np.array_equal(left,right)
    with pytest.raises(ValueError,match='Temporal information overlap'):
        audit_split(d,np.arange(0,200),np.arange(200,400),np.arange(400,600),7,temporal=True)


def test_outer_test_and_inner_calibration_are_athlete_disjoint():
    d=pd.DataFrame({'Date':np.tile(range(20),15),'Athlete ID':np.repeat(range(15),20),
                    'injury':np.tile([0,1],150)},index=np.arange(300)+100)
    seen=[]
    for fold,tr,ca,te in athlete_partitions(d):
        audit_split(d,tr,ca,te,7,grouped=True)
        seen.extend(te)
    assert sorted(seen)==sorted(d.index)


def test_clipping_does_not_learn_test_distribution():
    x=pd.DataFrame({'distance':[0.,1.,2.,3.,4.]})
    clip=TrainingQuantileClipper(lower=0,upper=1).fit(x)
    bounds=clip.bounds_.copy()
    assert clip.transform([[1000000.]])[0,0]==4
    assert np.array_equal(bounds,clip.bounds_)
    pipe=logistic_pipeline()
    with pytest.raises(ValueError,match='Forbidden predictors'):
        check_feature_list(['distance_7d','injury'])


def test_calibration_never_refits_base_estimator():
    rng=np.random.default_rng(123)
    x=pd.DataFrame({'load':rng.normal(size=300)})
    y=(x.load.to_numpy()+rng.normal(size=300)>.5).astype(int)
    base=logistic_pipeline().fit(x.iloc[:200],y[:200])
    coefficients=base.named_steps['model'].coef_.copy()
    bounds=base.named_steps['clip'].bounds_.copy()
    calibrated=calibrate_frozen(base,x.iloc[200:],y[200:])
    assert np.array_equal(coefficients,base.named_steps['model'].coef_)
    assert np.array_equal(bounds,base.named_steps['clip'].bounds_)
    assert np.isfinite(calibrated.predict_proba(x)).all()


def test_score_only_review_budget_handles_ties_conservatively():
    for p in [np.ones(100)*.01,np.array([.1,.1,.2,.3,.3,.3,.4,.4,.9,.9])]:
        for budget in [0,.05,.1,.2,1]:
            threshold=score_budget_threshold(p,budget)
            assert np.mean(p>=threshold)<=budget+1e-12


def test_cluster_weighted_ap_matches_reference_with_ties_and_zero_weights():
    y=np.array([0,1,1,0,0,1,0,1])
    p=np.array([.1,.1,.3,.3,.7,.7,.9,.9])
    weights=np.array([1,0,2,2,0,3,1,1])
    assert _weighted_ap(y,p,weights)==pytest.approx(average_precision_score(y,p,sample_weight=weights))


def test_weekly_features_use_original_blocks_without_unbounded_ratios():
    d={'Athlete ID':[1],'Date':[100],'injury':[0]}
    for base in ['total kms','total km Z3-4','total km Z5-T1-T2','nr. rest days','nr. strength trainings','total hours alternative training']:
        for i,v in enumerate([7,14,21]):
            d[base if i==0 else f'{base}.{i}']=[v]
    r=weekly_windows(pd.DataFrame(d))
    assert r.distance_14d.iloc[0]==21
    assert r.distance_21d.iloc[0]==42
    assert r.distance_change_7d.iloc[0]==-7
    assert not any('ratio' in col for col in r)
