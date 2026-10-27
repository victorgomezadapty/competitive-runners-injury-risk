"""Matched-event history, weighting and fixed tree comparisons; no winner selection."""
from pathlib import Path
import sys, json, hashlib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.data.load_data import load_data
from src.features.daily import summarize_pre_event
from src.features.rolling import weekly_windows
from src.validation.temporal import temporal_partitions
from src.validation.athlete_split import athlete_partitions
from src.validation.leakage import audit_split,check_feature_list
from src.models.baseline import logistic_pipeline
from src.models.calibration import calibrate_frozen
from src.analysis.prediction_metrics import probability_metrics


def athlete_weights(ids):
    counts=ids.value_counts()
    weights=ids.map(1/counts).to_numpy()
    return weights/weights.mean()


def matched_features(day,week):
    features=summarize_pre_event(day,7)
    three=summarize_pre_event(day,3)
    for c in three:
        if c.endswith('_3d'): features[c]=three[c]
    weekly=weekly_windows(week).drop(columns=['feature_start_day','feature_end_day'])
    joined=features.merge(weekly,on=['Athlete ID','Date'],suffixes=('','_week'),validate='one_to_one')
    if not joined.injury.eq(joined.injury_week).all():
        raise ValueError('Matched targets disagree')
    return joined.drop(columns=[c for c in joined if c.endswith('_week')]).reset_index(drop=True)


def main():
    report=ROOT/'reports/final_analysis'; report.mkdir(exist_ok=True)
    local=ROOT/'data/processed/final_analysis'; local.mkdir(exist_ok=True)
    protocol=ROOT/'config/final_analysis_protocol.json'
    cfg=json.loads(protocol.read_text())
    initial=json.loads((ROOT/'config/phase_02_protocol.json').read_text())
    day=load_data('day'); week=load_data('week')
    frame=matched_features(day,week)
    basic=initial['volume_features']+initial['response_features']
    extended=basic+cfg['weekly_additions']
    check_feature_list(extended)
    cases=[]
    for seed in cfg['seeds']:
        if seed==cfg['seeds'][0]:
            tr,ca,te=temporal_partitions(frame,lookback=cfg['known_lookback'])
            cases.append(('known_temporal',seed,0,tr,ca,te,cfg['known_lookback'],False,True))
        for fold,tr,ca,te in athlete_partitions(frame,5,seed,.2):
            if seed==cfg['seeds'][0]:
                cases.append(('unseen_athlete',seed,fold,tr,ca,te,21,True,False))
            groups=[set(frame.loc[idx,'Athlete ID']) for idx in [tr,ca,te]]
            tr,ca,te=temporal_partitions(frame,lookback=21,train_groups=groups[0],calibration_groups=groups[1],test_groups=groups[2],known_only=False)
            cases.append(('unseen_athlete_temporal',seed,fold,tr,ca,te,21,True,True))
    audits=[]; assignments=[]; metrics=[]; predictions=[]; coefs=[]
    for name,seed,fold,tr,ca,te,lookback,grouped,temporal in cases:
        for item in audit_split(frame,tr,ca,te,lookback,grouped,temporal):
            audits.append(dict(protocol=name,seed=seed,fold=fold,**item))
        for role,ids in [('train',tr),('calibration',ca),('test',te)]:
            assignments.extend(dict(protocol=name,seed=seed,fold=fold,partition=role,row_id=int(i)) for i in ids)
        print(name,seed,fold,len(tr),len(ca),len(te),flush=True)
        train,cal,test=[frame.loc[i] for i in [tr,ca,te]]
        def record(model,p):
            metrics.append(dict(protocol=name,seed=seed,fold=fold,model=model,**probability_metrics(test.injury,p)))
            pred=test[['Athlete ID','Date','injury']].copy()
            pred['probability']=p; pred['row_id']=test.index; pred['protocol']=name
            pred['seed']=seed; pred['fold']=fold; pred['model']=model
            predictions.append(pred)
        record('no_skill_calibration',np.full(len(test),cal.injury.mean()))
        for model in cfg['models']:
            cols=basic if model=='day_logistic' else extended
            pipe=logistic_pipeline()
            if model.endswith('forest'):
                pipe.set_params(model=RandomForestClassifier(**cfg['forest'],random_state=seed,n_jobs=2))
            kwargs={}
            if model=='athlete_balanced_logistic': kwargs['model__sample_weight']=athlete_weights(train['Athlete ID'])
            pipe.fit(train[cols],train.injury,**kwargs)
            record(model+'_raw',pipe.predict_proba(test[cols])[:,1])
            calibrated=calibrate_frozen(pipe,cal[cols],cal.injury)
            record(model+'_sigmoid',calibrated.predict_proba(test[cols])[:,1])
            if not model.endswith('forest'):
                coefs.extend(dict(protocol=name,seed=seed,fold=fold,model=model,feature=str(c),coefficient=float(v)) for c,v in zip(pipe[:-1].get_feature_names_out(cols),pipe[-1].coef_[0]))
    pred=pd.concat(predictions,ignore_index=True)
    pooled=[]
    for (name,seed,model),g in pred.groupby(['protocol','seed','model']):
        if g.row_id.duplicated().any(): raise ValueError('Duplicated held-out event')
        pooled.append(dict(protocol=name,seed=int(seed),model=model,athletes=g['Athlete ID'].nunique(),**probability_metrics(g.injury,g.probability)))
    for filename,obj in [('split_audit',audits),('fold_metrics',metrics),('pooled_metrics',pooled),('coefficients',coefs)]:
        pd.DataFrame(obj).to_csv(report/f'{filename}.csv',index=False)
    pd.DataFrame(assignments).to_csv(local/'row_partitions.csv',index=False)
    pred.to_csv(local/'predictions.csv',index=False)
    frame.to_csv(local/'matched_features.csv',index=False)
    manifest=dict(status='completed',matched_rows=len(frame),day_rows=len(day),week_rows=len(week),athletes=frame['Athlete ID'].nunique(),labels=int(frame.injury.sum()),split_cases=len(cases),base_fits=len(cases)*4,protocol_sha256=hashlib.sha256(protocol.read_bytes()).hexdigest(),source_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),primary_remains='Phase 2 logistic_load_response_sigmoid',files={})
    for p in list(report.glob('*.csv'))+list(local.glob('*.csv')):
        manifest['files'][p.relative_to(ROOT).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    (report/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps({k:v for k,v in manifest.items() if k!='files'},indent=2))

if __name__=='__main__': main()
