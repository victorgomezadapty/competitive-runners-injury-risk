"""Generate the public static data, documentation, CC0 data bundle and audit notebook."""
from pathlib import Path
import sys,json,hashlib,shutil,zipfile,html,re
import pandas as pd
import numpy as np
import nbformat as nbf
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.data.load_data import load_data
from src.data.timelines import to_history_long,reconstruct_training_days
from src.features.daily import summarize_pre_event

def records(df): return json.loads(df.to_json(orient='records',double_precision=12))
def table(df):
    cols=list(df.columns)
    out=['| '+' | '.join(cols)+' |','|'+'|'.join(['---']*len(cols))+'|']
    for row in df.itertuples(index=False,name=None):
        out.append('| '+' | '.join(f'{v:.5f}' if isinstance(v,float) else str(v) for v in row)+' |')
    return '\n'.join(out)

def markdown(text):
    """Small safe renderer for authored Markdown, with no raw HTML execution."""
    def inline(s):
        s=html.escape(s)
        s=re.sub(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',r'<a href="\2">\1</a>',s)
        s=re.sub(r'\*\*([^*]+)\*\*',r'<strong>\1</strong>',s)
        s=re.sub(r'`([^`]+)`',r'<code>\1</code>',s)
        return s
    out=[]; paragraph=[]; listing=False; tabular=False; table_started=False
    def flush():
        if paragraph: out.append('<p>'+inline(' '.join(paragraph))+'</p>');paragraph.clear()
    for line in text.splitlines()+['']:
        if line.startswith('|'):
            flush()
            if not tabular:out.append('<div class="table-scroll"><table>');tabular=True;table_started=False
            if re.match(r'^\|[\s:|\-]+\|$',line):continue
            cells=[inline(s.strip()) for s in line.strip('|').split('|')]
            tag='td' if table_started else 'th'
            out.append('<tr>'+''.join(f'<{tag}>{s}</{tag}>' for s in cells)+'</tr>');table_started=True
            continue
        elif tabular:
            out.append('</table></div>');tabular=False
        if line.startswith('#'):
            flush()
            if listing:out.append('</ul>');listing=False
            m=re.match(r'^(#{1,6})\s+(.*)',line)
            if m:
                level=min(len(m[1])+1,6);out.append(f'<h{level}>{inline(m[2])}</h{level}>')
        elif line.startswith(('- ','* ')):
            flush()
            if not listing:out.append('<ul>');listing=True
            out.append('<li>'+inline(line[2:])+'</li>')
        elif not line.strip():
            flush()
            if listing:out.append('</ul>');listing=False
        else:paragraph.append(line)
    return '\n'.join(out)

def main():
    web=ROOT/'web';downloads=web/'downloads';downloads.mkdir(exist_ok=True)
    release=ROOT/'release';dataset=release/'kaggle_dataset';kernel=release/'kaggle_notebook'
    dataset.mkdir(parents=True,exist_ok=True);kernel.mkdir(exist_ok=True)
    audit=json.loads((ROOT/'reports/tables/audit_summary.json').read_text())
    raw=load_data('day'); daily=summarize_pre_event(raw)
    history,_=reconstruct_training_days(to_history_long(raw))
    predictions=pd.read_csv(ROOT/'data/processed/phase_02/held_out_predictions.csv')
    pred=predictions[predictions.protocol.eq('unseen_athlete') & predictions.model.eq('logistic_load_response_sigmoid')]
    metrics=pd.read_csv(ROOT/'reports/phase_02/tables/pooled_metrics.csv')
    alerts=pd.read_csv(ROOT/'reports/phase_02/tables/pooled_alerts.csv')
    alerts=alerts[alerts.model.eq('logistic_load_response_sigmoid')]
    final=pd.read_csv(ROOT/'reports/final_analysis/pooled_metrics.csv')
    examples=[]
    for athlete in audit['example_athletes']:
        events=raw[raw['Athlete ID'].eq(athlete)].sort_values('Date')
        item=dict(id=int(athlete),rows=len(events),injuries=int(events.injury.sum()))
        for label,key in [(1,'injury'),(0,'healthy')]:
            choices=events[events.injury.eq(label)]
            event=choices.iloc[len(choices)//2];day=int(event.Date);start=day-70;end=day+14
            h=history[history['Athlete ID'].eq(athlete)&history.training_day.between(start,end)]
            rows=[]
            for _,r in h.iterrows():
                row=dict(day=int(r.training_day),distance=float(r['total km']),intensity=float(r['km Z5-T1-T2']),rest=int(r['nr. sessions']==0))
                for source,name in [('perceived recovery','recovery'),('perceived exertion','exertion'),('perceived trainingSuccess','success')]:
                    row[name]=None if r[source]==-.01 or pd.isna(r[source]) else float(r[source])
                rows.append(row)
            p=pred[pred['Athlete ID'].eq(athlete)&pred.Date.eq(day)].iloc[0]
            features=daily[daily['Athlete ID'].eq(athlete)&daily.Date.eq(day)].iloc[0]
            item[key]=dict(event=day,start=start,end=end,days=rows,injuries=events.loc[events.injury.eq(1)&events.Date.between(start,end),'Date'].astype(int).tolist(),probability=float(p.probability),distance_7d=float(features.distance_7d),rest_days_7d=int(features.rest_days_7d))
        examples.append(item)
    data=dict(source='10.34894/UWU9PV v2.0 CC0',build_date='2026-10-26',athletes=examples,metrics=records(metrics),alerts=records(alerts),intervals=records(pd.read_csv(ROOT/'reports/phase_02/tables/primary_cluster_bootstrap.csv')),final=records(final))
    (web/'data.json').write_text(json.dumps(data,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    comparison=final[final.protocol.eq('unseen_athlete_temporal')&final.model.str.endswith('_sigmoid')][['seed','model','rows','positives','average_precision','roc_auc','brier']]
    report='''# Final analysis and project completion

Date: 2026-10-26. Research release 1.0.0. Phase 2 remains the primary analysis; the following comparisons were specified after reviewing its results and are exploratory.

## Matched-event comparison

Day and Week inner join: 42,680 rows, 74 masked athletes, 575 positive labels; zero target disagreement. The 86 Day-only and 118 Week-only rows are excluded only from this matched comparison. This is not the full Day target population. Features: original daily 3/7-day summaries plus six interpretable 14/21-day load, rest and change variables. Ratios remain excluded. All compared models share exactly the same rows and partitions within a protocol/seed/fold; no comparison across different samples is presented as a causal effect.

Three protocols at seed 20261025, plus two alternative athlete partitions for the combined unseen-athlete/future question: 21 split cases, 84 fixed base fits and independent sigmoid calibrators. Temporal purging uses a common 21-day history (63 for known athletes) and 21-day source ascertainment. Training-only clipping, imputation and scaling. Inverse training-history weights equalize each athlete's total loss contribution, not injury-class frequency; calibration and evaluation retain source-sample weights. The fixed random forest uses 200 trees, depth 6, leaf minimum 30 and max_features 0.7. No hyperparameter search, test-based winner or clinical model release.

## Unseen athletes and future period

'''+table(comparison)+'''

Differences across partitions show development uncertainty that the Phase 2 conditional cluster bootstrap does not capture. All partitions, raw/calibrated results and coefficients are retained. A tree comparison is methodological context; it does not establish clinical utility. Logistic coefficients are conditional standardized associations affected by correlated windows; not causal treatment effects. No strongest numerical row is promoted as the final predictor.

## Completed research deliverables

- Original files, checksum validation, corrected daily lag order, dictionary and source-specific target definitions.
- Full athlete, observation, follow-up-span, missingness, intensity, rest and subjective-response descriptions; five individual timelines and repeated-measures-aware paired descriptive contrasts.
- Past-only personal-history feasibility, known/future and unseen-athlete validation, disjoint calibration, imbalance-aware metrics, conditional athlete-cluster uncertainty and review-burden analysis.
- Matched longer-history comparisons, athlete-balanced fitting, fixed tree sensitivity and partition stability.
- Eleven authored notebooks; final two explore saved risk profiles and review budgets, without training a model in the browser.
- Literature-backed discussion, transparent narrative search, source bibliography, license inventory, reproducible public code/data packaging and interactive website.

## Analyses that the source cannot support

Exact calendar dates, complete clinical incidence, injury diagnosis/severity/location and complete time at risk cannot be recovered. No valid event lead time or false alerts per athlete-month can be calculated from this future-filtered sample. Twenty-eight-day windows are not created by filling unobserved days. Sex-specific analysis is unavailable at masked-participant level. Additional cohorts are independent; their participants cannot supply missing modalities here. Causal rest/load interventions, validated prevention and external clinical utility require new prospective surveillance.

The project is complete as a reproducible exploratory research case study. Clinical deployment, patient-specific recommendations and a claim of injury prevention are not supported deliverables.

## Reproduction

`python scripts/reproduce.py --notebooks` rebuilds the main analysis. Add `--complementary` to acquire and profile the separate companion sources. `cd web` then `npm run build` builds the static site. Kaggle's companion notebook independently checks the public data and saved results; the full model-fitting pipeline lives in GitHub.
'''
    (ROOT/'reports/final_project_summary.md').write_text(report,encoding='utf-8')
    # Complete the planned result notebooks as views of auditable saved outputs.
    views=[('10_risk_profiles.ipynb','Individual histories and held-out profiles',"profiles = pd.read_csv(ROOT/'data/processed/phase_02/held_out_predictions.csv')\nprofiles = profiles[profiles.model.eq('logistic_load_response_sigmoid') & profiles.protocol.eq('unseen_athlete')]\ndisplay(profiles.groupby('Athlete ID').agg(rows=('injury','size'), positive_labels=('injury','sum'), mean_score=('probability','mean')))"),('11_decision_support.ipynb','Review burden, not a clinical threshold',"review = pd.read_csv(ROOT/'reports/phase_02/tables/pooled_alerts.csv')\ndisplay(review[review.model.eq('logistic_load_response_sigmoid')])\ndisplay(pd.read_csv(ROOT/'reports/final_analysis/pooled_metrics.csv'))")]
    for filename,title,code in views:
        path=ROOT/'notebooks'/filename
        nb=nbf.v4.new_notebook(cells=[nbf.v4.new_markdown_cell('# '+title+'\n\nExploratory selected-sample research. No clinical bands, diagnosis, causal scenario or prospective event-level claims. Repeated rows are not independent people. See reports/final_project_summary.md and docs/discussion.md.'),nbf.v4.new_code_cell("from pathlib import Path\nimport pandas as pd\nROOT = Path.cwd()\nif ROOT.name == 'notebooks': ROOT = ROOT.parent"),nbf.v4.new_code_cell(code)],metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}})
        old=nbf.read(path,as_version=4)
        if [c.source for c in old.cells]!=[c.source for c in nb.cells]:nbf.write(nb,path)
    # Distribution is limited to CC0 originals and tabular exports; no PDFs or companion raw data.
    for name in ['day_approach_maskedID_timeseries.csv','week_approach_maskedID_timeseries.csv','README.txt']:
        shutil.copy2(ROOT/'data/raw'/name,dataset/name)
    shutil.copy2(ROOT/'data/source_manifest.json',dataset/'source_manifest.json')
    exports={'phase02_metrics.csv':ROOT/'reports/phase_02/tables/pooled_metrics.csv','phase02_alerts.csv':ROOT/'reports/phase_02/tables/pooled_alerts.csv','phase02_uncertainty.csv':ROOT/'reports/phase_02/tables/primary_cluster_bootstrap.csv','final_metrics.csv':ROOT/'reports/final_analysis/pooled_metrics.csv','athlete_summary.csv':ROOT/'reports/tables/day_athlete_summary.csv','data_dictionary.csv':ROOT/'reports/tables/data_dictionary.csv','feature_catalog.csv':ROOT/'handoff/feature_catalog.csv'}
    for name,path in exports.items():shutil.copy2(path,dataset/name)
    description='''Reproducibility bundle for Longitudinal Training Load & Injury Risk in Competitive Runners by Víctor Andrés Gómez López (2026).

ORIGINAL DATA: Sofie Lövdal, Ruud J. R. den Hartigh and George Azzopardi. Replication Data for: Injury Prediction In Competitive Runners With Machine Learning. Dataverse release 2.0. DOI https://doi.org/10.34894/UWU9PV. Original CSVs and corrected README are unmodified and CC0. Dataverse is the source of record. Original study DOI https://doi.org/10.1123/ijspp.2020-0518; erratum DOI https://doi.org/10.1123/ijspp.2024-0251. No article PDFs, third-party figures, or source authors' notebook are redistributed.

74 athletes; Day 42,766 selected rows / 583 positive labels. Week 42,798 / 575. Each Day row is a selected event with seven preceding daily histories, NOT an independent athlete or an arbitrary observed day. Unsuffixed fields are E-7; .6 is E-1, per corrected 2024 README. Date is relative, not calendar date. Subjective -0.01 indicates a rest-day sentinel. Injury prevented completing the scheduled session. Healthy controls required full fitness three weeks before AND AFTER, with nearby injury events excluded. Label frequency is not prospective incidence. Missing dates cannot be assigned healthy/rest labels. IDs remain masked.

Original exports: descriptive summaries, feature catalog and held-out evaluation metrics, dedicated CC0 by the project author. Matched Day/Week extension uses 42,680 common events and 575 labels; no future-conditioned clinical risk claim. Phase 2 remains primary. Independent calibration and temporal/athlete validation; modest ranking, sparse positives and substantial alert burden. No causal injury prevention or clinical diagnosis. SoccerMon and Wu complementary raw files are excluded; cohorts are never pooled.

Code, exact protocol, full training reproduction, literature discussion and license inventory: https://github.com/victorgomezadapty/competitive-runners-injury-risk . Interactive study: https://competitive-runners-injury-risk.vercel.app . Original project software/text MIT; the data license does not relicense referenced articles. checksums.json verifies included files. This bundle is an attributed mirror and derived research release, not newly collected measurements or clinical advice.'''
    (dataset/'README.md').write_text(description,encoding='utf-8')
    (dataset/'dataset-metadata.json').write_text(json.dumps(dict(title='Competitive Runners: Longitudinal Research & Audit',id='vctorandrsgmezlpez/competitive-runners-longitudinal-research',licenses=[{'name':'CC0-1.0'}],description=description,keywords=['running','sports','health','time-series','research']),ensure_ascii=False,indent=2),encoding='utf-8')
    checksums={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in dataset.iterdir() if p.is_file() and p.name not in ['checksums.json','dataset-metadata.json']}
    (dataset/'checksums.json').write_text(json.dumps(checksums,indent=2))
    cells=[nbf.v4.new_markdown_cell('# Competitive Runners: Longitudinal Dataset Audit\n\nVíctor Andrés Gómez López (2026). This notebook **executes a release audit**, not the full training pipeline. Full code, frozen protocols and discussion: [GitHub](https://github.com/victorgomezadapty/competitive-runners-injury-risk). Original data: Lövdal, den Hartigh & Azzopardi, [Dataverse 10.34894/UWU9PV](https://doi.org/10.34894/UWU9PV), v2.0, CC0. Source authors collected the measurements. No article is redistributed.\n\nThis is a filtered event-window sample, not continuous prospective surveillance. Injury labels are not complete clinical diagnoses; healthy selection uses future fitness. No causal injury-prevention claims. Notebook wrapper: Apache 2.0; data retain CC0, original project code/prose MIT.'),nbf.v4.new_code_cell("from pathlib import Path\nimport hashlib, json\nimport pandas as pd\nimport numpy as np\nimport matplotlib.pyplot as plt\ncandidates = list(Path('/kaggle/input').rglob('day_approach_maskedID_timeseries.csv')) if Path('/kaggle/input').exists() else list(Path('release/kaggle_dataset').glob('day_approach_maskedID_timeseries.csv'))\nassert len(candidates)==1, candidates\nDATA=candidates[0].parent\nfor name, expected in json.loads((DATA/'checksums.json').read_text()).items():\n    assert hashlib.sha256((DATA/name).read_bytes()).hexdigest()==expected, name\nprint('All bundled file checksums verified')\nday=pd.read_csv(DATA/'day_approach_maskedID_timeseries.csv')\nweek=pd.read_csv(DATA/'week_approach_maskedID_timeseries.csv')\ndisplay(pd.DataFrame([dict(representation=name, rows=len(df), athletes=df['Athlete ID'].nunique(), labels=int(df.injury.sum()), label_fraction=df.injury.mean(), first_relative_day=df.Date.min(), last_relative_day=df.Date.max()) for name,df in [('Day',day),('Week',week)]]))"),nbf.v4.new_markdown_cell('## Check the corrected daily lag order\n\nUnsuffixed = E−7, `.6` = E−1. Check overlapping event windows within an athlete. Rest-day subjective −0.01 is non-applicable; never low recovery. Relative dates cannot be converted to calendar dates.'),nbf.v4.new_code_cell("parts=[]\nfor suffix in range(7):\n    col='total km' if suffix==0 else f'total km.{suffix}'\n    parts.append(pd.DataFrame({'athlete':day['Athlete ID'],'training_day':day.Date-(7-suffix),'distance':day[col]}))\nhistory=pd.concat(parts).groupby(['athlete','training_day']).distance.agg(['min','max','first']).reset_index()\nassert np.allclose(history['min'],history['max'])\nfig,axes=plt.subplots(5,1,figsize=(12,12),layout='constrained')\nfor ax,athlete in zip(axes,[55,13,67,38,32]):\n    h=history[history.athlete.eq(athlete)]\n    ax.scatter(h.training_day,h['first'],s=3,color='#24645a')\n    for event in day.loc[day['Athlete ID'].eq(athlete)&day.injury.eq(1),'Date']: ax.axvline(event,color='#bc4b28',alpha=.25)\n    ax.set(title=f'Masked athlete {athlete}: retrospective recoverable history',ylabel='km')\naxes[-1].set_xlabel('Relative training day; gaps are not rest or healthy labels')\nplt.show()\ndisplay(pd.read_csv(DATA/'athlete_summary.csv').head(10))"),nbf.v4.new_markdown_cell('## Inspect saved held-out results\n\nAP is non-interpolated average precision. Training, calibration and test are separate. Model-fitting occurs in the GitHub pipeline. These exported tables are verified here, not recomputed by refitting. The denominators are selected rows, not true athlete-days. Brier alone does not establish calibration.'),nbf.v4.new_code_cell("metrics=pd.read_csv(DATA/'phase02_metrics.csv')\nprimary=metrics[metrics.model.eq('logistic_load_response_sigmoid')]\ndisplay(primary)\nuncertainty=pd.read_csv(DATA/'phase02_uncertainty.csv')\ndisplay(uncertainty)\nalerts=pd.read_csv(DATA/'phase02_alerts.csv')\ndisplay(alerts[alerts.model.eq('logistic_load_response_sigmoid')&alerts.requested_budget.eq(.1)])\ndisplay(pd.read_csv(DATA/'final_metrics.csv'))\nprint('Primary results remain Phase 2; no test-based winner selection.')"),nbf.v4.new_markdown_cell('## Interpretation, limitations and discussion\n\nThere is modest source-sample ranking signal, with sparse labels and substantial review burden. More history or a nonlinear model does not establish prospective utility. Known-athlete and unseen-athlete protocols answer different questions. No lead time, false alerts per athlete-month, clinical thresholds, rest intervention effect or real-world incidence is identifiable here.\n\nThe discussion and documented narrative literature search are in the repository. Key primary sources: [original study](https://doi.org/10.1123/ijspp.2020-0518), [erratum](https://doi.org/10.1123/ijspp.2024-0251), [ACWR critique](https://doi.org/10.1123/ijspp.2019-0864), [calibration](https://doi.org/10.1186/s12916-019-1466-7). Different cohorts remain separate; no participants are linked to complementary sources.')]
    notebook=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'}})
    nbf.write(notebook,kernel/'audit.ipynb')
    (kernel/'kernel-metadata.json').write_text(json.dumps(dict(id='vctorandrsgmezlpez/competitive-runners-longitudinal-audit',title='Competitive Runners: Longitudinal Audit',code_file='audit.ipynb',language='python',kernel_type='notebook',is_private=False,enable_gpu=False,enable_internet=False,dataset_sources=['vctorandrsgmezlpez/competitive-runners-longitudinal-research'],competition_sources=[],kernel_sources=[],keywords=['sports','running','research']),indent=2))
    # Public evidence page: original prose, links to primary sources, no copied article text.
    discussion=ROOT/'docs/discussion.md';search=ROOT/'docs/literature_search.md'
    if not discussion.exists() or not search.exists():raise FileNotFoundError('Literature discussion/search must be completed before publication')
    header='''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Competitive Runners · Evidencia y discusión</title><meta name="description" content="Discusión científica, búsqueda bibliográfica documentada, reproducibilidad y derechos de los datos de corredores competitivos."><link rel="stylesheet" href="/styles.css"><link rel="icon" href="/favicon.svg"><script type="module" src="/app.js"></script></head><body><a class="skip" href="#main">Saltar al contenido / Skip to content</a><header class="nav"><a class="brand" href="/">CR / Competitive Runners</a><nav aria-label="Principal"><a href="/" data-es="Volver al estudio" data-en="Back to study">Volver al estudio</a><a href="#discussion" data-es="Discusión" data-en="Discussion">Discusión</a><a href="#search" data-es="Búsqueda" data-en="Search">Búsqueda</a><a href="#rights" data-es="Derechos" data-en="Rights">Derechos</a></nav><button id="lang">EN</button></header><main id="main" class="wrap evidence chapter"><p class="eyebrow">EVIDENCE / OPEN RESEARCH</p><h1 data-es="Lo que los datos permiten afirmar." data-en="What the data allow us to say.">Lo que los datos permiten afirmar.</h1><p data-es="Discusión completa en español, con resumen en inglés y fuentes primarias enlazadas. Búsqueda narrativa: no revisión sistemática." data-en="Full discussion in Spanish, with an English summary and linked primary sources. Narrative search, not a systematic review.">Discusión completa en español, con resumen en inglés y fuentes primarias enlazadas. Búsqueda narrativa: no revisión sistemática.</p><blockquote lang="en"><strong>English summary.</strong> This exploratory reanalysis audits selected training-event windows in 74 competitive runners. Strict athlete and temporal validation leaves modest ranking signal; calibration is not uniformly better. Future-conditioned healthy selection prevents estimating prospective daily incidence. Longer windows, weighting and a fixed forest remain sensitivity analyses. Prediction does not establish prevention or causal treatment effects.</blockquote><div class="contents"><a href="/downloads/results.zip">Download results ↗</a><a href="https://github.com/victorgomezadapty/competitive-runners-injury-risk">Full code ↗</a><a href="/downloads/references.bib">BibTeX ↗</a></div>'''
    evidence=header+'<article id="discussion" lang="es">'+markdown(discussion.read_text(encoding='utf-8'))+'</article><section id="search" lang="es">'+markdown(search.read_text(encoding='utf-8'))+'</section><section id="rights">'+markdown((ROOT/'DATA_LICENSE.md').read_text(encoding='utf-8'))+'</section></main><footer class="wrap"><p>Víctor Andrés Gómez López · 2026</p><a href="/">Competitive Runners ↗</a><a href="https://doi.org/10.34894/UWU9PV">Original Dataverse ↗</a></footer></body></html>'
    (web/'evidence.html').write_text(evidence,encoding='utf-8')
    shutil.copy2(ROOT/'docs/references.bib',downloads/'references.bib')
    public_files=[*list((ROOT/'reports/tables').glob('*.csv')),*list((ROOT/'reports/phase_02/tables').glob('*.csv')),*list((ROOT/'reports/final_analysis').glob('*.csv')),*list((ROOT/'docs').glob('*.md')),*list((ROOT/'config').glob('*.json')),*list((ROOT/'reports/figures').glob('*.png')),*list((ROOT/'reports/phase_02/figures').glob('*.png')),*list((ROOT/'handoff').glob('*.csv')),ROOT/'reports/final_project_summary.md',ROOT/'reports/phase_02_summary.md',ROOT/'reports/milestone_01_summary.md',ROOT/'data/README.md',ROOT/'data/source_manifest.json',ROOT/'DATA_LICENSE.md',ROOT/'LICENSE',ROOT/'CITATION.cff',ROOT/'docs/references.bib']
    with zipfile.ZipFile(downloads/'results.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in public_files:z.write(p,p.relative_to(ROOT).as_posix())
    print('Generated website data, evidence, final report, notebooks and attributed Kaggle bundle.')

if __name__=='__main__':main()
