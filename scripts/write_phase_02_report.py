"""Render fixed experiment results and update current project status, not model choice."""
from pathlib import Path
import sys
import json
import hashlib
import nbformat as nbf
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.visualization.validation_plots import LABELS,comparison_plot,calibration_plot,review_volume_plot

REPORT=ROOT/'reports/phase_02'
TABLES=REPORT/'tables'


def table(frame,digits=4):
    def fmt(x):
        if isinstance(x,float):
            return f'{x:.{digits}f}' if np.isfinite(x) else 'Unavailable'
        return str(x)
    return '| '+' | '.join(frame.columns)+' |\n|'+'|'.join(['---']*len(frame.columns))+'|\n'+''.join('| '+' | '.join(fmt(x) for x in r)+' |\n' for r in frame.itertuples(index=False,name=None))


def main():
    run=json.loads((REPORT/'run_manifest.json').read_text())
    metrics=pd.read_csv(TABLES/'pooled_metrics.csv')
    folds=pd.read_csv(TABLES/'fold_metrics.csv')
    splits=pd.read_csv(TABLES/'split_audit.csv')
    ci=pd.read_csv(TABLES/'primary_cluster_bootstrap.csv')
    reliability=pd.read_csv(TABLES/'reliability_bins.csv')
    alerts=pd.read_csv(TABLES/'held_out_alert_metrics.csv')
    primary=metrics[metrics.model.eq('logistic_load_response_sigmoid')].copy()
    summaries=[]
    for r in primary.itertuples():
        f=folds[folds.protocol.eq(r.protocol)&folds.model.eq(r.model)]
        interval=ci[ci.protocol.eq(r.protocol)&ci.metric.eq('average_precision')].iloc[0]
        summaries.append({'Validation':LABELS[r.protocol],'Athletes':r.athletes,'Rows':r.rows,'Labels':r.positives,
                          'Label fraction':r.prevalence,'Pooled AP':r.average_precision,
                          'Mean fold AP':f.average_precision.mean(),'AP CI low':interval.ci95_low,
                          'AP CI high':interval.ci95_high,'ROC-AUC':r.roc_auc,'Brier':r.brier})
    summary=pd.DataFrame(summaries)
    summary.to_csv(TABLES/'primary_summary.csv',index=False)
    pooled_alerts=[]
    for (protocol,model,budget),g in alerts.groupby(['protocol','model','requested_budget']):
        m=metrics[(metrics.protocol.eq(protocol))&metrics.model.eq(model)].iloc[0]
        n=int(g.alerts.sum()); tp=int(g.true_positive_rows.sum()); fp=int(g.false_positive_rows.sum())
        pooled_alerts.append({'protocol':protocol,'model':model,'requested_budget':budget,'alerts':n,
              'alerts_per_100_selected_rows':100*n/m.rows,'true_positive_rows':tp,'false_positive_rows':fp,
              'precision':tp/n if n else 0,'recall':tp/m.positives,
              'alerts_per_captured_positive':n/tp if tp else np.nan})
    burden=pd.DataFrame(pooled_alerts)
    burden.to_csv(TABLES/'pooled_alerts.csv',index=False)
    comparison_plot(metrics,ci,REPORT/'figures/validation_comparison.png')
    calibration_plot(reliability,REPORT/'figures/calibration.png')
    review_volume_plot(burden,REPORT/'figures/review_volume.png')
    reference=metrics[metrics.model.eq('no_skill_calibration')][['protocol','average_precision','brier']].rename(columns={'average_precision':'No-skill pooled AP','brier':'No-skill Brier'})
    sensitivity=metrics[metrics.model.isin(['logistic_load_response_sigmoid','logistic_success_sensitivity_sigmoid',
                      'logistic_uncapped_sensitivity_sigmoid','logistic_personal_baseline_sensitivity_sigmoid'])]
    text=f'''# Phase 2 - Exposure windows, validation and first probability baselines

**Project:** Longitudinal Training Load & Injury Risk in Competitive Runners  
**Date:** 2026-10-25  
**Status:** research baselines completed following the user's request to continue. No clinical deployment, causal advice, tree/neural models or cross-cohort pooling.

## Improvements implemented

1. Reproducible 7/14/21-day exposure summaries and week-to-week distance differences from original complete weekly blocks. No unstable acute:chronic ratios were introduced. Day remains the primary modeling representation; weekly features are prepared and described, not yet used in the model comparison.
2. A prior-only personal exposure ledger with at least 28 observed days inside a 56-day baseline window ending before the current seven-day window. Each source event's fitness ascertainment is conservatively delayed 21 days, without inspecting its label. Missing days remain missing. This source-conditional availability audit supports only a known-athlete sensitivity experiment; it does not recover a continuous real-world training log.
3. A locally recorded specification before fitting: [protocol](../config/phase_02_protocol.json). Hyperparameters, feature groups, validation rules, clipping quantiles, calibration and score-review budgets were fixed. Milestone 1 already inspected the entire dataset, so this is exploratory reuse, not prospective preregistration or an untouched external test.
4. Three separate evaluations: known athletes in a later period; five outer athlete-disjoint folds; and athlete-disjoint plus temporal restrictions. Calibration observations are separate from fitting and testing. All grouped roles are athlete-disjoint. Calendar cutoffs were chosen from the time range without outcome optimization.
5. Temporal purging respects both feature lookback and the source's 21-day future-conditioned healthy selection. Known-athlete models use a common 63-day maximum input envelope so personal-history and ordinary baselines share the same split. Other protocols use seven days. These safeguards prevent cross-boundary information overlap but cannot undo the dataset's upstream selection.
6. Fixed regularized logistic models and two constant frequency baselines. Training-only clipping (0.5th/99.5th percentiles), median imputation, missing indicators and robust scaling. No resampling or class weighting. Primary features omit training success because 15 athletes have all-zero histories; its inclusion is an explicit sensitivity analysis.
7. Sigmoid calibration on disjoint calibration data with a frozen base estimator. No test labels choose preprocessing, hyperparameters, calibration or review thresholds. Review thresholds depend only on calibration scores and fixed review budgets; ties are retained or excluded as complete groups.

## Main held-out results

Primary model: ten exposure features plus seven-day exertion and recovery; training-only clipping and sigmoid calibration. AP means non-interpolated average precision, not trapezoidal PR area. Confidence intervals use 500 athlete-cluster resamples of the held-out predictions. They are conditional on fitted models, do not refit training, and do not account for dependence between athletes in a common team.

{table(summary)}

The three evaluations test different populations/periods and have different label fractions. Their scores are not a causal decomposition of athlete versus temporal effects. The combined design includes {int(primary[primary.protocol.eq('unseen_athlete_temporal')].athletes.iloc[0])} athletes with eligible later-period observations; this does not represent all athletes equally.

![Held-out comparison](phase_02/figures/validation_comparison.png)

### Fair frequency references

Two constant baselines are reported: fitting-period prevalence, and calibration-period prevalence (the latter has access to the same calibration labels as the calibrated model). The horizontal figure reference is the evaluation label fraction. Fold-specific constant probabilities can differ, so pooled out-of-fold AP need not equal pooled prevalence; mean fold AP is also shown. Neither is a prospective cohort incidence.

{table(reference)}

The model has limited ranking signal within this selected source sample. Small Brier values are expected when positives are rare; compare them with the constant baseline. Brier loss combines calibration and discrimination and does not establish calibration by itself. Bootstrap differences versus the calibration-frequency baseline appear in [paired uncertainty](phase_02/tables/primary_cluster_bootstrap.csv).

## Calibration is a comparison, not an automatic improvement

Uncalibrated and calibrated versions are both retained. Sigmoid calibration changes the probability scale and may improve or worsen held-out Brier, AP and ranking across different fold-specific models. It is not assumed beneficial. Sparse positive calibration cases and between-athlete differences remain important; inspect [partition event counts](phase_02/tables/split_audit.csv).

![Calibration](phase_02/figures/calibration.png)

These are source-sample calibration curves with quantile bins, not validated clinical risk curves. Bin counts and observed positives are exported. No independent-row confidence intervals are drawn on correlated records.

## Sensitivity analysis

{table(sensitivity[['protocol','model','average_precision','roc_auc','brier']])}

Treat differences as exploratory. The personal-history sensitivity is restricted to known athletes, replaces total distance with a prior expected level and current deviation, and allows earlier unlabeled exposures to update history during evaluation. It is not a cold-start model for new athletes. It is also not a mixed-effects estimate of within/between-person causal effects. Training success is retained unchanged in its sensitivity; zeros are not silently reclassified as missing. The uncapped comparison changes preprocessing only, not which rows are evaluated.

## Review burden in the selected sample

Budgets of 5%, 10% and 20% were applied to calibration scores. Actual test alert volume can shift. Alerts are counted **per 100 selected event rows**, not per 100 true athlete-days, and captured positive rows are retained labels rather than a complete clinical injury registry. Precision is reported as zero by convention when no alerts occur. No low/moderate/high clinical categories were invented.

{table(burden[burden.model.eq('logistic_load_response_sigmoid')].drop(columns='model'),digits=3)}

![Review volume](phase_02/figures/review_volume.png)

## Personal-history feasibility and exclusions

{run['baseline_available_rows']:,} of {run['total_rows']:,} original Day records have sufficient prior source-confirmed exposure for the specified personal baseline. Availability by athlete is exported, and missing personal values are handled only by fitting-period imputation in the sensitivity. The original retrospective visualization table is not used as a ready-made predictor stream. No future athlete averages or future injury counts enter predictors.

Known-athlete temporal evaluation retains {run['known_temporal_test_rows']:,} later-period rows and excludes {run['late_rows_excluded_as_new_athletes']:,} later rows belonging to athletes absent from the fitting period. Those athletes are evaluated by the separate unseen-athlete designs. Time purging also excludes boundary records from fitting/calibration. All row assignments and model predictions are retained locally under `data/processed/phase_02/`.

## What to improve next

- Add a matched-event comparison of original weekly 14/21-day load/change features versus daily windows using the same eligibility, folds and cutoff rules. Their prepared features currently have not entered the baseline comparison.
- Evaluate stability over prespecified alternative temporal cutoffs and athlete partitions. Also test athlete-balanced training weights so long histories do not dominate fitting. The present intervals capture held-out athlete heterogeneity, not full model-development uncertainty. Avoid selecting a favorable seed or reporting only one model's best split.
- Audit the cause of extreme sprint/cross-training values and constant subjective scales with source documentation; use transparent sensitivity handling until clarified. Personal-baseline coverage remains selective and needs better raw continuous surveillance.
- Consider repeated-measures associations that distinguish prior personal level and deviation; do not interpret logistic coefficients as causal effects. Tree models would be a later comparison only after these baselines, with identical validation.
- Representative prospective logging and complete clinical ascertainment remain necessary before calendar-day probabilities, injury-event lead time, false alerts per athlete-month or clinical review thresholds can be validated.
- Keep SoccerMon as a separate wellness/session source. Wu processed workbooks lack explicit athlete/time keys and remain quarantined. Neither fills missing modalities in the Dutch runners.

## Reproduce

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/run_phase_02.py
python scripts/write_phase_02_report.py
python scripts/execute_notebooks.py --start 5 --end 9
python scripts/verify_delivery.py
```

Original acquisition and Milestone 1 descriptive scripts remain documented in README. Numeric source files, the frozen protocol and original manifest are hashed in [run manifest](phase_02/run_manifest.json); no fitted model is serialized or deployed. Local predictions are retained for audit, not used to retrospectively choose a winner.

References: [group-aware cross-validation](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GroupKFold.html), [probability calibration and disjoint calibration data](https://scikit-learn.org/stable/modules/calibration.html), [AP definition](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.average_precision_score.html). Source sampling limitations and injury definition remain in [Milestone 1](milestone_01_summary.md).
'''
    (ROOT/'reports/phase_02_summary.md').write_text(text,encoding='utf-8')
    update_catalog()
    update_status(run)
    notebooks()
    files=list(TABLES.glob('*.csv'))+list((ROOT/'data/processed/phase_02').glob('*.csv'))
    files+=list((REPORT/'figures').glob('*.png'))
    checksums={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (REPORT/'output_manifest.json').write_text(json.dumps({'files':checksums},indent=2),encoding='utf-8')
    print('Phase 2 report, figures, current status, registry and notebooks written.')


def update_catalog():
    if (ROOT/'reports/final_analysis/manifest.json').exists():
        return
    path=ROOT/'handoff/feature_catalog.csv'
    frame=pd.read_csv(path).fillna('')
    for name in ['distance_14d','distance_21d','distance_change_7d']:
        frame.loc[frame.feature_name.eq(name),'limitations']='Implemented Phase 2 using original weekly blocks; not used in Day baseline models'
    rows=[]
    for days in [14,21]:
        for name,domain,units in [('z3_4_distance','Intensity','km'),('z5_t1_t2_distance','Intensity','km'),
                                  ('rest_days','Rest','days'),('strength_sessions','Strength','logged sessions'),
                                  ('cross_training_hours','Cross training','hours')]:
            rows.append([f'{name}_{days}d',domain,'Sum complete original weekly blocks in own event row',f'E-{days}..E-1',units,
                         f'{days//7} complete weekly blocks','End of E-1','Low within original row; existing source selection persists',
                         'Prior exposure; no causal or clinical threshold','Prepared Phase 2; not entered in Day model comparison'])
    rows.extend([
        ['prior_expected_distance_7d','Athlete Baseline','7 times mean unique prior-day distance; source event plus 21-day ascertainment must precede E',
         'E-63..E-8 with source ascertainment < E','km','28 observed unique prior days in 56-day window','End of E-1',
         'Prior-only ledger; no labels used; source selection and unknown logging times persist','Historical exposure level',
         'Known-athlete sensitivity only; missing dates not zero-filled; not a population biological baseline'],
        ['distance_deviation_7d','Relative Load','distance_7d minus prior_expected_distance_7d',
         'E-7..E-1 versus prior E-63..E-8','km','Current history plus available prior baseline','End of E-1',
         'Prior-only ledger and training-only preprocessing','Deviation from prior source-observed exposure',
         'Not causality; replaces total distance alongside expected baseline in known-athlete sensitivity'],
        ['prior_observed_days_56d','Availability','Count prior unique days meeting source ascertainment delay','E-63..E-8','days',
         'Past source windows only','End of E-1','Audit only; not a predictor','Coverage of retained prior history','Not complete time at risk'],
        ['prior_coverage_56d','Availability','prior_observed_days_56d divided by 56','E-63..E-8','fraction',
         'Past source windows only','End of E-1','Audit only; not a predictor','Source-history coverage','Not actual recording compliance']])
    frame=pd.concat([frame,pd.DataFrame(rows,columns=frame.columns)],ignore_index=True).drop_duplicates('feature_name',keep='last')
    frame.to_csv(path,index=False)
    audit=ROOT/'docs/leakage_audit.md'
    content=audit.read_text(encoding='utf-8')
    marker='\n## Phase 2 implementation extension\n'
    content=content.split(marker)[0]
    content=content.replace('No model has been fitted.','Milestone 1 historical audit; Phase 2 fixed baselines are now fitted, as documented in the extension below.')
    content+=marker+'\nUser continuation authorized Phase 2 on 2026-10-25. Original target/horizon and source boundaries remain fixed. All new features are in the current registry.\n\n'
    content+='| Feature | Window | Cutoff | Risk / decision |\n|---|---|---|---|\n'
    for row in rows:
        content+=f'| `{row[0]}` | {row[3]} | {row[6]} | {row[7]}; {row[9]} |\n'
    content+='\nOriginal weekly distance_14d, distance_21d and distance_change_7d candidates are now prepared. Temporal splits purge until earlier event +21 precedes later input start. Fit/calibration/test observations are disjoint; unseen-athlete roles are also athlete-disjoint. Clipping, imputation and scaling fit training rows only; sigmoid calibration uses a frozen base model and separate calibration rows. Review thresholds use only calibration scores under fixed budgets. Numeric provenance and split assignments are saved in reports/phase_02/run_manifest.json and data/processed/phase_02/. No complementary-cohort rows, test labels, IDs or raw Date are predictors.\n'
    audit.write_text(content,encoding='utf-8')


def update_status(run):
    if (ROOT/'reports/final_analysis/manifest.json').exists():
        return
    path=ROOT/'README.md'
    text=path.read_text(encoding='utf-8')
    start='**Status:** Milestone 1 delivered for review. **No injury-prediction model trained.**'
    text=text.replace(start,'**Status:** Phase 2 completed: fixed research baselines, strict validation and calibration. No clinical deployment.')
    text=text.replace('01-04 descriptive views; 05-11 explicitly deferred plans','01-04 descriptive views; 05-09 Phase 2 results; 10-11 deferred')
    text=text.replace('reserved modules only; no fitting implementation','fixed logistic baselines and independent sigmoid calibration')
    text=text.replace('reserved Phase 2 modules; no splits run yet','temporal purging, athlete-disjoint splits and leakage checks')
    text=text.replace('No cross-cohort pooling or prediction has been performed.',
                      'Complementary cohorts remain separate; no model was fitted to SoccerMon or Wu.')
    marker='\n## Current Phase 2 results\n'
    text=text.split(marker)[0]
    text+=marker+'\nSee [Phase 2 findings and next improvements](reports/phase_02_summary.md), [frozen protocol](config/phase_02_protocol.json) and [run provenance](reports/phase_02/run_manifest.json). Baselines are exploratory estimates within the selected source sample. No cross-cohort pooling, clinical thresholds or causal claims.\n\n```powershell\npython scripts/run_phase_02.py\npython scripts/write_phase_02_report.py\npython scripts/execute_notebooks.py --start 5 --end 9\npython scripts/verify_delivery.py\n```\n'
    path.write_text(text,encoding='utf-8')
    m1=ROOT/'reports/milestone_01_summary.md'
    old_m1=m1.read_text(encoding='utf-8')
    if not old_m1.startswith('> Historical Milestone 1 record.'):
        m1.write_text('> Historical Milestone 1 record. The user authorized continuation; current results are in [Phase 2](phase_02_summary.md).\n\n'+old_m1,encoding='utf-8')
    proposal=ROOT/'docs/phase_02_proposal.md'
    old=proposal.read_text(encoding='utf-8')
    if 'Execution update' not in old:
        old+='\n## Execution update\n\nThe user requested improvements and continuation on 2026-10-25, authorizing fixed Phase 2 baselines after Milestone 1 delivery. See reports/phase_02_summary.md and config/phase_02_protocol.json for what was implemented. Tree/neural models and clinical deployment remain deferred.\n'
        proposal.write_text(old,encoding='utf-8')
    handoff=ROOT/'handoff/findings.md'
    old=handoff.read_text(encoding='utf-8').split('\n## Phase 2 update\n')[0]
    old+='\n## Phase 2 update\n\nFixed logistic baselines and sigmoid calibration are now fitted following the user continuation. Three validation designs, training-only preprocessing, prior-history feasibility, bootstrap uncertainty and selected-row review burden are reported in [Phase 2](../reports/phase_02_summary.md). No clinical deployment, tree/neural modeling or cohort pooling.\n'
    handoff.write_text(old,encoding='utf-8')


def notebooks():
    setup="from pathlib import Path\nimport pandas as pd\nfrom IPython.display import display, Image\nROOT = Path.cwd() if (Path.cwd() / 'src').exists() else Path.cwd().parent\nT = ROOT / 'reports/phase_02/tables'\n"
    specs=[
        ('05_feature_windows','Exposure windows and personal-history feasibility',"display(pd.read_csv(T/'weekly_window_distributions.csv'))\ndisplay(pd.read_csv(T/'personal_history_feasibility.csv'))"),
        ('06_baseline_models','Fixed logistic baselines',"display(pd.read_csv(T/'primary_summary.csv'))\ndisplay(Image(filename=str(ROOT/'reports/phase_02/figures/validation_comparison.png')))"),
        ('07_athlete_independent_validation','Athlete-independent evaluation',"display(pd.read_csv(T/'split_audit.csv'))\ndisplay(pd.read_csv(T/'fold_metrics.csv').query(\"protocol == 'unseen_athlete'\"))"),
        ('08_temporal_models','Temporal validation of classical baselines',"display(pd.read_csv(T/'split_audit.csv').query(\"protocol != 'unseen_athlete'\"))\ndisplay(pd.read_csv(T/'primary_cluster_bootstrap.csv'))"),
        ('09_calibration','Independent calibration and selected-row review burden',"display(pd.read_csv(T/'pooled_alerts.csv').query(\"model == 'logistic_load_response_sigmoid'\"))\ndisplay(Image(filename=str(ROOT/'reports/phase_02/figures/calibration.png')))\ndisplay(Image(filename=str(ROOT/'reports/phase_02/figures/review_volume.png')))")]
    for name,title,code in specs:
        path=ROOT/f'notebooks/{name}.ipynb'
        if path.exists():
            existing=nbf.read(path,as_version=4)
            if existing.metadata.get('phase_02_result_view') and all(c.get('source')==s for c,s in zip(existing.cells,[f'# {title}\n\nPhase 2 fixed research baselines. These are selected-source event probabilities, not clinical daily risks. Model fitting is reproducible through scripts/run_phase_02.py. This notebook displays saved held-out results.\n',setup,code])):
                continue
        nb=nbf.v4.new_notebook(cells=[nbf.v4.new_markdown_cell(f'# {title}\n\nPhase 2 fixed research baselines. These are selected-source event probabilities, not clinical daily risks. Model fitting is reproducible through scripts/run_phase_02.py. This notebook displays saved held-out results.\n'),nbf.v4.new_code_cell(setup),nbf.v4.new_code_cell(code)])
        nb.metadata.kernelspec={'display_name':'Python 3','language':'python','name':'python3'}
        nb.metadata.phase_02_result_view=True
        nbf.write(nb,path)
    for name,title in [('10_risk_profiles','Risk-profile exploration'),('11_decision_support','Decision-support exploration')]:
        path=ROOT/f'notebooks/{name}.ipynb'
        nb=nbf.read(path,as_version=4)
        if not any(c.cell_type=='code' for c in nb.cells):
            nb.cells=[nbf.v4.new_markdown_cell(f'# {title}\n\nPlanned after the Phase 2 research baselines. See `reports/phase_02_summary.md` for current results and limitations. The available probabilities concern selected source events; clinical risk bands, prospective alert rates and prevention claims are not validated. No prototype or clinical threshold is implemented here.\n')]
            nbf.write(nb,path)


if __name__=='__main__':
    main()
