"""Research evaluation figures, restricted to selected event-row probabilities."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import precision_recall_curve

LABELS={'known_temporal':'Known athletes / future period',
        'unseen_athlete':'Unseen athletes / all periods',
        'unseen_athlete_temporal':'Unseen athletes / future period'}
COLORS=['#8397a5','#518cae','#df8b26','#246a5f']


def comparison_plot(metrics,intervals,path):
    models=['no_skill_calibration','logistic_volume_sigmoid','logistic_load_response_raw','logistic_load_response_sigmoid']
    labels=['Calibration\nfrequency','Volume\ncalibrated','Load+response\nuncalibrated','Load+response\ncalibrated']
    fig,axs=plt.subplots(2,3,figsize=(15,8),layout='constrained')
    fig.suptitle('Held-out baseline evaluation | selected source events',fontsize=15)
    for j,(protocol,title) in enumerate(LABELS.items()):
        subset=metrics[metrics.protocol.eq(protocol)].set_index('model').loc[models]
        for i,metric in enumerate(['average_precision','brier']):
            ax=axs[i,j]
            ax.bar(np.arange(4),subset[metric],color=COLORS,width=.7)
            ax.set_xticks(range(4),labels,fontsize=8)
            ax.set_ylabel('Average precision (higher better)' if i==0 else 'Brier loss (lower better)')
            ax.spines[['top','right']].set_visible(False)
            ax.grid(axis='y',alpha=.15)
            if i==0:
                ax.set_title(title,fontsize=11)
                ax.axhline(subset.prevalence.iloc[0],color='#a63f43',linestyle='--',linewidth=1,label='Test label fraction')
                ci=intervals[(intervals.protocol.eq(protocol))&intervals.metric.eq(metric)].iloc[0]
                value=subset.loc[models[-1],metric]
                ax.errorbar(3,value,yerr=[[max(0,value-ci.ci95_low)],[max(0,ci.ci95_high-value)]],fmt='none',color='black',capsize=4)
                ax.legend(fontsize=8)
    fig.savefig(path,dpi=160); plt.close(fig)


def calibration_plot(bins,path):
    fig,axs=plt.subplots(1,3,figsize=(14,4.8),layout='constrained')
    fig.suptitle('Calibration among held-out selected events | source-sample probabilities',fontsize=14)
    for ax,(protocol,title) in zip(axs,LABELS.items()):
        subset=bins[bins.protocol.eq(protocol)]
        ceiling=.04
        for model,label,color in [('logistic_load_response_raw','Uncalibrated','#df8b26'),
                                  ('logistic_load_response_sigmoid','Sigmoid calibrated','#246a5f')]:
            b=subset[subset.model.eq(model)]
            ax.plot(b.mean_probability,b.observed_fraction,'o-',color=color,label=label,markersize=5)
            ceiling=max(ceiling,float(b[['mean_probability','observed_fraction']].max().max())*1.12)
        ax.plot([0,ceiling],[0,ceiling],'--',color='#6d747b',linewidth=1)
        ax.set_xlim(0,ceiling); ax.set_ylim(0,ceiling)
        ax.set_title(title,fontsize=10)
        ax.set_xlabel('Mean predicted probability')
        ax.set_ylabel('Observed label fraction')
        ax.spines[['top','right']].set_visible(False); ax.grid(alpha=.15)
        ax.legend(fontsize=8)
    fig.savefig(path,dpi=160); plt.close(fig)


def review_volume_plot(alerts,path):
    fig,axs=plt.subplots(1,3,figsize=(13,4.5),layout='constrained')
    fig.suptitle('Review burden: frozen calibration-score budgets, evaluated on held-out rows',fontsize=13)
    for ax,(protocol,title) in zip(axs,LABELS.items()):
        rows=alerts[(alerts.protocol.eq(protocol))&alerts.model.eq('logistic_load_response_sigmoid')]
        ax.plot(rows.alerts_per_100_selected_rows,rows.recall,'o-',color='#246a5f')
        for r in rows.itertuples():
            ax.annotate(f'{r.requested_budget:.0%}',(r.alerts_per_100_selected_rows,r.recall),
                        xytext=(5,5),textcoords='offset points',fontsize=8)
        ax.set_title(title,fontsize=10)
        ax.set_xlabel('Alerts per 100 selected event rows')
        ax.set_ylabel('Recall of retained injury labels')
        ax.set_ylim(0,1); ax.set_xlim(left=0)
        ax.grid(alpha=.15); ax.spines[['top','right']].set_visible(False)
    fig.savefig(path,dpi=160); plt.close(fig)
