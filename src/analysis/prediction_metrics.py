"""Rare-event evaluation, score-only review budgets, and athlete-cluster uncertainty."""
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss,log_loss


def probability_metrics(y,p):
    return {'rows':len(y),'positives':int(np.sum(y)),'prevalence':float(np.mean(y)),
            'average_precision':float(average_precision_score(y,p)),
            'roc_auc':float(roc_auc_score(y,p)),'brier':float(brier_score_loss(y,p)),
            'log_loss':float(log_loss(y,p,labels=[0,1])), 'mean_probability':float(np.mean(p))}


def score_budget_threshold(scores,budget):
    """Largest attainable alert count <= budget; ties are never split randomly."""
    if not 0<=budget<=1:
        raise ValueError('Budget must be a fraction')
    values,counts=np.unique(scores,return_counts=True)
    values,counts=values[::-1],counts[::-1]
    cumulative=np.cumsum(counts)
    feasible=np.flatnonzero(cumulative<=int(np.floor(len(scores)*budget)))
    return float(values[feasible[-1]]) if len(feasible) else float(np.nextafter(values[0],np.inf))


def alert_metrics(y,p,threshold):
    y=np.asarray(y,dtype=int)
    alert=np.asarray(p)>=threshold
    tp=int(np.sum(alert&(y==1))); fp=int(np.sum(alert&(y==0)))
    n=int(alert.sum()); positives=int(y.sum())
    precision=tp/n if n else 0.0
    recall=tp/positives if positives else np.nan
    return {'threshold':threshold,'alerts':n,'alerts_per_100_selected_rows':100*n/len(y),
            'true_positive_rows':tp,'false_positive_rows':fp,'precision':precision,'recall':recall,
            'f1':2*precision*recall/(precision+recall) if precision+recall else 0.0,
            'false_positive_rate':fp/int((y==0).sum()),
            'alerts_per_captured_positive':n/tp if tp else np.nan}


def reliability_bins(y,p,n_bins=8):
    d=pd.DataFrame({'y':y,'p':p})
    if d.p.nunique()<2:
        groups=[d]
    else:
        d['bin']=pd.qcut(d.p,q=min(n_bins,d.p.nunique()),duplicates='drop')
        groups=[g for _,g in d.groupby('bin',observed=True)]
    return pd.DataFrame([{'bin':i,'rows':len(g),'positive_rows':int(g.y.sum()),
                          'mean_probability':g.p.mean(),'observed_fraction':g.y.mean()}
                         for i,g in enumerate(groups)])


def _weighted_ap(y,score,weights):
    order=np.argsort(-np.asarray(score),kind='stable')
    y=np.asarray(y)[order]; score=np.asarray(score)[order]; weights=np.asarray(weights)[order]
    ends=np.r_[np.flatnonzero(score[1:]!=score[:-1]),len(score)-1]
    tp=np.cumsum(y*weights)[ends]; total=np.cumsum(weights)[ends]
    positives=np.sum(y*weights)
    if positives==0:
        return np.nan
    precision=np.divide(tp,total,out=np.zeros_like(tp,dtype=float),where=total>0)
    return float(np.sum(np.diff(np.r_[0,tp])/positives*precision))


def cluster_bootstrap_comparison(frame,n_boot=500,seed=20261025):
    """Paired conditional uncertainty for primary calibrated scores versus no-skill.

    Resamples athlete clusters; does not refit models or account for common-team
    dependence. Scores can be cross-fitted OOF, so fitting sets overlap across folds.
    """
    ids=np.unique(frame['Athlete ID'])
    positions=pd.Categorical(frame['Athlete ID'],categories=ids).codes
    y=frame.injury.to_numpy(); p=frame.probability.to_numpy(); b=frame.baseline_probability.to_numpy()
    rng=np.random.default_rng(seed)
    samples=[]
    for _ in range(n_boot):
        group_weights=np.bincount(rng.integers(0,len(ids),size=len(ids)),minlength=len(ids))
        weights=group_weights[positions]
        if not np.sum(weights*y):
            continue
        ap=_weighted_ap(y,p,weights); base_ap=_weighted_ap(y,b,weights)
        brier=np.average((p-y)**2,weights=weights)
        base_brier=np.average((b-y)**2,weights=weights)
        samples.append([ap,ap-base_ap,brier,brier-base_brier])
    samples=np.asarray(samples)
    rows=[]
    for i,name in enumerate(['average_precision','AP_minus_no_skill','brier','brier_minus_no_skill']):
        rows.append({'metric':name,'athletes':len(ids),'valid_resamples':len(samples),
                     'ci95_low':np.quantile(samples[:,i],.025),'ci95_high':np.quantile(samples[:,i],.975)})
    return pd.DataFrame(rows)
