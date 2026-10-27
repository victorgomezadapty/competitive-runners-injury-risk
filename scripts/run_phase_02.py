"""Fixed Phase 2 experiments: audit -> windows -> split -> baseline -> calibration.

No trees, hyperparameter search, dataset pooling, or clinical deployment.
"""
from pathlib import Path
import sys
import json
import hashlib
import importlib.metadata
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.data.load_data import load_data
from src.features.daily import summarize_pre_event
from src.features.rolling import weekly_windows
from src.features.athlete_baselines import prior_distance_baselines
from src.validation.temporal import temporal_partitions,calendar_cutoffs
from src.validation.athlete_split import athlete_partitions
from src.validation.leakage import audit_split,check_feature_list
from src.models.baseline import logistic_pipeline
from src.models.calibration import calibrate_frozen
from src.analysis.prediction_metrics import (probability_metrics,score_budget_threshold,
                                           alert_metrics,reliability_bins,cluster_bootstrap_comparison)

REPORT=ROOT/'reports/phase_02'
TABLES=REPORT/'tables'
PROCESSED=ROOT/'data/processed/phase_02'


def save(df,name):
    df.to_csv(TABLES/name,index=False)


def main():
    for p in [REPORT,TABLES,REPORT/'figures',PROCESSED]:
        p.mkdir(parents=True,exist_ok=True)
    protocol_path=ROOT/'config/phase_02_protocol.json'
    protocol_bytes=protocol_path.read_bytes()
    cfg=json.loads(protocol_bytes)
    assert cfg['temporal_calendar_fractions']==[.6,.8]
    print('Loading checksummed originals; building within-row features.',flush=True)
    raw=load_data('day').reset_index(drop=True)
    week=load_data('week')
    features=summarize_pre_event(raw,7)
    three=summarize_pre_event(raw,3)
    for c in three:
        if c.endswith('_3d'):
            features[c]=three[c]
    print('Auditing conservative past-only personal histories (21-day selection delay).',flush=True)
    personal=prior_distance_baselines(raw,history_days=cfg['personal_history_days'],
                 minimum_days=cfg['personal_minimum_observed_days'],
                 selection_delay=cfg['personal_source_ascertainment_delay'])
    features=features.join(personal)
    assert (personal.latest_source_ascertainment_day.dropna()<raw.loc[personal.latest_source_ascertainment_day.notna(),'Date']).all()
    features.to_csv(PROCESSED/'daily_features.csv',index=False)
    weekly=weekly_windows(week)
    weekly.to_csv(PROCESSED/'weekly_windows.csv',index=False)
    weekly.drop(columns=['Athlete ID','Date','injury','feature_start_day','feature_end_day']).describe().T.to_csv(TABLES/'weekly_window_distributions.csv')
    coverage=features.groupby('Athlete ID').agg(rows=('Date','size'),
                 baseline_available_rows=('prior_expected_distance_7d','count'),
                 median_known_prior_days=('prior_observed_days_56d','median'))
    coverage['coverage_fraction']=coverage.baseline_available_rows/coverage.rows
    save(coverage.reset_index(),'personal_history_feasibility.csv')
    # Audit all-zero success histories descriptively; never a whole-athlete predictor flag.
    success=pd.read_csv(ROOT/'reports/tables/subjective_scale_usage_by_athlete.csv')
    save(success[success.variable.eq('perceived trainingSuccess')],'training_success_quality.csv')

    cases=[]
    train,cal,test=temporal_partitions(features,lookback=cfg['known_athlete_input_lookback'],
                                     selection_lookahead=cfg['healthy_selection_lookahead'])
    cases.append(('known_temporal',0,train,cal,test,cfg['known_athlete_input_lookback'],False,True))
    for fold,tr,ca,te in athlete_partitions(features,cfg['outer_athlete_folds'],cfg['seed'],cfg['calibration_athlete_fraction']):
        cases.append(('unseen_athlete',fold,tr,ca,te,7,True,False))
        groups=[set(features.loc[idx,'Athlete ID']) for idx in [tr,ca,te]]
        t,c,e=temporal_partitions(features,lookback=7,selection_lookahead=21,
                 train_groups=groups[0],calibration_groups=groups[1],test_groups=groups[2],known_only=False)
        cases.append(('unseen_athlete_temporal',fold,t,c,e,7,True,True))
    split_rows=[]; assignments=[]
    for protocol,fold,tr,ca,te,lookback,grouped,temporal in cases:
        audited=audit_split(features,tr,ca,te,lookback,grouped,temporal,cfg['healthy_selection_lookahead'])
        split_rows.extend([{**x,'protocol':protocol,'fold':fold} for x in audited])
        for name,ids in [('train',tr),('calibration',ca),('test',te)]:
            assignments.extend([{'protocol':protocol,'fold':fold,'partition':name,'row_id':int(i)} for i in ids])
    save(pd.DataFrame(split_rows),'split_audit.csv')
    pd.DataFrame(assignments).to_csv(PROCESSED/'row_partitions.csv',index=False)
    print('All split contracts passed; fitting fixed logistic baselines.',flush=True)
    objective=cfg['volume_features']; full=objective+cfg['response_features']
    configs=[('logistic_volume',objective,True),('logistic_load_response',full,True),
             ('logistic_success_sensitivity',full+['mean_training_success_7d'],True),
             ('logistic_uncapped_sensitivity',full,False)]
    fold_metrics=[]; predictions=[]; thresholds=[]; alert_rows=[]; coefficients=[]; clipping=[]
    for protocol,fold,tr,ca,te,lookback,grouped,temporal in cases:
        train,cal,test=features.loc[tr],features.loc[ca],features.loc[te]
        print(f'{protocol} fold {fold}: train={len(train)} cal={len(cal)} test={len(test)}',flush=True)
        y=train.injury.to_numpy(); yc=cal.injury.to_numpy(); yt=test.injury.to_numpy()
        reference=float(yc.mean())

        def record(model_name,p_test,p_cal):
            fold_metrics.append({'protocol':protocol,'fold':fold,'model':model_name,**probability_metrics(yt,p_test)})
            frame=test[['Athlete ID','Date','injury']].copy()
            frame['row_id']=test.index
            frame['protocol']=protocol; frame['fold']=fold; frame['model']=model_name
            frame['probability']=p_test; frame['baseline_probability']=reference
            predictions.append(frame)
            for budget in cfg['review_budgets']:
                threshold=score_budget_threshold(p_cal,budget)
                achieved=float(np.mean(np.asarray(p_cal)>=threshold))
                assert achieved<=budget+1e-12
                thresholds.append({'protocol':protocol,'fold':fold,'model':model_name,'requested_budget':budget,
                                   'threshold':threshold,'calibration_alert_fraction':achieved})
                alert_rows.append({'protocol':protocol,'fold':fold,'model':model_name,'requested_budget':budget,
                                   **alert_metrics(yt,p_test,threshold)})

        record('no_skill_train',np.full(len(test),y.mean()),np.full(len(cal),y.mean()))
        record('no_skill_calibration',np.full(len(test),reference),np.full(len(cal),reference))
        active=list(configs)
        if protocol=='known_temporal':
            cols=[c for c in full if c!='distance_7d']+['prior_expected_distance_7d','distance_deviation_7d']
            active.append(('logistic_personal_baseline_sensitivity',cols,True))
        for model_name,cols,clipped in active:
            check_feature_list(cols)
            estimator=logistic_pipeline(clipped=clipped,C=cfg['logistic_C'],quantiles=cfg['quantile_clipping'],
                                        max_iter=cfg['logistic_max_iter'])
            estimator.fit(train[cols],y)
            record(model_name+'_raw',estimator.predict_proba(test[cols])[:,1],estimator.predict_proba(cal[cols])[:,1])
            calibrated=calibrate_frozen(estimator,cal[cols],yc)
            record(model_name+'_sigmoid',calibrated.predict_proba(test[cols])[:,1],calibrated.predict_proba(cal[cols])[:,1])
            transformed=estimator[:-1].get_feature_names_out(cols)
            coefficients.extend([{'protocol':protocol,'fold':fold,'model':model_name,'feature':str(c),'coefficient':float(v)}
                                 for c,v in zip(transformed,estimator.named_steps['model'].coef_[0])])
            if clipped:
                clipping.extend([{'protocol':protocol,'fold':fold,'model':model_name,'feature':c,'train_low':lo,'train_high':hi}
                                 for c,(lo,hi) in zip(cols,estimator.named_steps['clip'].bounds_)])
    pred=pd.concat(predictions,ignore_index=True)
    for protocol,g in pred.groupby('protocol'):
        for model,part in g.groupby('model'):
            if part.row_id.duplicated().any():
                raise ValueError(f'Duplicate held-out predictions: {protocol}/{model}')
    pred.to_csv(PROCESSED/'held_out_predictions.csv',index=False)
    pooled=[]; calibration_rows=[]
    for (protocol,model),g in pred.groupby(['protocol','model']):
        pooled.append({'protocol':protocol,'model':model,'athletes':g['Athlete ID'].nunique(),
                       **probability_metrics(g.injury,g.probability)})
        bins=reliability_bins(g.injury.to_numpy(),g.probability.to_numpy())
        bins['protocol']=protocol; bins['model']=model
        calibration_rows.append(bins)
    save(pd.DataFrame(fold_metrics),'fold_metrics.csv')
    save(pd.DataFrame(pooled),'pooled_metrics.csv')
    save(pd.concat(calibration_rows,ignore_index=True),'reliability_bins.csv')
    save(pd.DataFrame(thresholds),'calibration_thresholds.csv')
    save(pd.DataFrame(alert_rows),'held_out_alert_metrics.csv')
    save(pd.DataFrame(coefficients),'logistic_coefficients.csv')
    save(pd.DataFrame(clipping),'training_clip_bounds.csv')
    intervals=[]
    for protocol,g in pred[pred.model.eq(cfg['primary_model'])].groupby('protocol'):
        print('Athlete-cluster uncertainty:',protocol,flush=True)
        ci=cluster_bootstrap_comparison(g,cfg['bootstrap_resamples'],cfg['seed'])
        ci['protocol']=protocol; intervals.append(ci)
    save(pd.concat(intervals,ignore_index=True),'primary_cluster_bootstrap.csv')
    late_start=calendar_cutoffs(features)[1]
    later=features[features.Date.ge(late_start)]
    known_test=pred[(pred.protocol=='known_temporal')&pred.model.eq('no_skill_train')]
    result={'stage':'phase_02','status':'completed','authorization_date':'2026-10-25',
            'protocol_sha256':hashlib.sha256(protocol_bytes).hexdigest(),'protocol':cfg,
            'source_manifest_sha256':hashlib.sha256((ROOT/'data/source_manifest.json').read_bytes()).hexdigest(),
            'calendar_cutoffs':list(calendar_cutoffs(features)),
            'baseline_available_rows':int(features.prior_expected_distance_7d.notna().sum()),
            'total_rows':len(features),'known_temporal_test_rows':len(known_test),
            'late_rows_excluded_as_new_athletes':len(later)-len(known_test),
            'base_estimators_fitted':len(set((x['protocol'],x['fold'],x['model']) for x in coefficients)),
            'calibration_estimators_fitted':len(set((x['protocol'],x['fold'],x['model']) for x in coefficients)),
            'prediction_models_trained':True,'models_serialized':False,'deployment_status':'research only',
            'environment':{k:importlib.metadata.version(k) for k in ['scikit-learn','pandas','numpy','scipy']},
            'source_code_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in list((ROOT/'src').rglob('*.py'))+[Path(__file__).resolve()]}}
    (REPORT/'run_manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('Phase 2 computations complete. No clinical threshold or deployment produced.',flush=True)


if __name__=='__main__':
    main()
