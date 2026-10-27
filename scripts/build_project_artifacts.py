"""Build documentation, exact column dictionary, registry, and staged notebooks."""
from pathlib import Path
import json
import re
import sys
import csv
import nbformat as nbf
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.load_data import load_data
from src.data.timelines import DAY_VARIABLES, SUBJECTIVE


def write(path, text):
    p = ROOT/path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.strip()+'\n', encoding='utf-8')


DAILY = {
    'nr. sessions': ('Training frequency', 'Number of completed training sessions that day', 'sessions'),
    'total km': ('Volume', 'Distance covered running that day', 'km'),
    'km Z3-4': ('Intensity', 'Running distance in Z3-4: on or slightly above anaerobic threshold (corrected README)', 'km'),
    'km Z5-T1-T2': ('Intensity', 'Distance in Z5 near maximum heart rate or intensive track intervals; T1 longer and T2 shorter repetitions', 'km'),
    'km sprinting': ('Intensity', 'Distance covered sprinting; no numerical speed cut-point supplied', 'km'),
    'strength training': ('Strength', 'Logged strength training; README calls this an indicator, but values reach 2 and paper calls it session count', 'logged count; review >1'),
    'hours alternative': ('Cross training', 'Hours of alternative/cross training; type not released', 'hours'),
    'perceived exertion': ('Subjective', 'Self-estimated tiredness after main session; released 0-1 scale, not established Borg RPE', 'released rating 0-1'),
    'perceived trainingSuccess': ('Subjective', 'Self-estimated success of main session; released 0-1 scale', 'released rating 0-1'),
    'perceived recovery': ('Recovery', 'Self-estimated restedness before session; released 0-1 scale', 'released rating 0-1')}
WEEKLY = {
    'nr. sessions': ('Training frequency', 'Total completed training sessions in preceding week', 'sessions'),
    'nr. rest days': ('Rest', 'Number of days without a training session in preceding week', 'days'),
    'total kms': ('Volume', 'Total weekly running distance', 'km'),
    'max km one day': ('Volume', 'Maximum running distance on one day of week', 'km/day'),
    'total km Z3-Z4-Z5-T1-T2': ('Intensity', 'Total weekly distance in Z3 or faster; includes sprint exposure in observed weekly aggregation, see reconciliation note', 'km'),
    'nr. tough sessions (effort in Z5, T1 or T2)': ('Intensity', 'Number of tough sessions containing Z5/T1/T2 effort', 'sessions'),
    'nr. days with interval session': ('Intensity', 'Number of days containing Z3-or-faster interval training', 'days'),
    'total km Z3-4': ('Intensity', 'Weekly running distance in Z3-4', 'km'),
    'max km Z3-4 one day': ('Intensity', 'Maximum Z3-4 running distance in one day', 'km/day'),
    'total km Z5-T1-T2': ('Intensity', 'Weekly running distance in Z5/T1/T2', 'km'),
    'max km Z5-T1-T2 one day': ('Intensity', 'Maximum Z5/T1/T2 distance in one day', 'km/day'),
    'total hours alternative training': ('Cross training', 'Weekly hours of cross training', 'hours'),
    'nr. strength trainings': ('Strength', 'Number of logged strength trainings in week', 'sessions')}
for subject in ['exertion', 'training success', 'recovery']:
    for stat, definition in [('avg', 'Mean'), ('min', 'Minimum'), ('max', 'Maximum')]:
        WEEKLY[f'{stat} {subject}'] = ('Recovery' if subject == 'recovery' else 'Subjective', f'{definition} perceived {subject} across weekly trainings; source aggregation retained', 'released rating 0-1')


def dictionary():
    rows = []
    for approach in ['day', 'week']:
        df = load_data(approach)
        for col in df:
            m = re.search(r'\.(\d+)$', col)
            suffix = int(m.group(1)) if m else 0
            base = col[:m.start()] if m else col
            role, sentinel = 'historical exposure', ''
            if col in ['Athlete ID', 'Date', 'injury']:
                domain = 'Metadata' if col != 'injury' else 'Target'
                definition, units = {
                    'Athlete ID': ('Masked athlete identifier; numeric order is not a biological quantity', 'identifier'),
                    'Date': ('Event day relative to first record in dataset; calendar origin unavailable', 'relative days'),
                    'injury': ('Retained injury flag (1) versus selected healthy event (0); see injury_definition.md', 'binary')}[col]
                window, role = 'event day E', 'target' if col == 'injury' else 'grouping/index only'
            elif col.startswith('rel total kms'):
                domain, definition, units = 'Relative Load', 'Released weekly volume ratio; numerator and denominator specified in column name; zero-denominator handling not documented', 'ratio'
                window = 'E-21..E-1 subsets'
                role = 'quarantined until denominator rule reviewed'
            else:
                domain, definition, units = (DAILY if approach == 'day' else WEEKLY)[base]
                window = f'E-{7-suffix}' if approach == 'day' else f'E-{7*(suffix+1)}..E-{7*suffix+1}'
                if approach == 'day' and base in SUBJECTIVE:
                    sentinel = '-0.01 = unavailable on rest day; exclude from numeric rating means; retain day'
            rows.append({'representation': approach, 'original_column': col, 'base_name': base,
                         'domain': domain, 'definition': definition, 'window_relative_to_event': window,
                         'units': units, 'dtype': str(df[col].dtype), 'observed_min': df[col].min(),
                         'observed_max': df[col].max(), 'blank_cells': int(df[col].isna().sum()),
                         'sentinel_handling': sentinel, 'role': role})
    table = pd.DataFrame(rows)
    table.to_csv(ROOT/'reports/tables/data_dictionary.csv', index=False)
    text = '''# Data dictionary

Exact original names are preserved in raw data. This is a column-complete dictionary generated from both original files; its machine-readable version is [data_dictionary.csv](../reports/tables/data_dictionary.csv).

E denotes the selected event day. Corrected daily order: unsuffixed E-7 through `.6` E-1. Weekly order: unsuffixed E-7..E-1, `.1` E-14..E-8, `.2` E-21..E-15. The 2024 source README takes precedence over the uncorrected 2021 PDF and conflicting secondary papers.

Subjective values are released on a 0-1 numerical scale, with -0.01 as the daily rest sentinel. Original questionnaire anchors, transformations from another scale, and instrument validation are not supplied. Do not multiply by 10 and call this Borg RPE. Zero can be a valid value and is not automatically imputed. Training success has athlete-specific response patterns; examine the usage audit.

`strength training` is described as a presence indicator in the README, but the paper and observed values suggest counts; retain original values and flag values >1 rather than silently binarizing. The files contain no running duration column despite duration being recorded upstream. No explicit easy-zone distance, HRV, sleep, wellness, sex, age, diagnosis, or injury severity column is available. Do not invent these variables or link sex to IDs.

Observed extrema below are audit facts, not verified physiological limits. Weekly ratio values can be enormous near zero denominator. These are preserved but quarantined.

Definitions: [source README](https://dataverse.nl/api/access/datafile/422690?format=original), [study](https://doi.org/10.1123/ijspp.2020-0518). Units and numerical range are directly checked against the original files.

| Representation | Exact column | Window | Units | Definition | Observed range |
|---|---|---|---|---|---|
'''
    for row in rows:
        text += f"| {row['representation']} | `{row['original_column']}` | {row['window_relative_to_event']} | {row['units']} | {row['definition']} | {row['observed_min']:g} to {row['observed_max']:g} |\n"
    write('docs/data_dictionary.md', text)


def registry():
    if (ROOT/'reports/phase_02/run_manifest.json').exists():
        return  # Preserve the expanded Phase 2 registry and leakage audit.
    rows = []
    sums = [('distance', 'Volume', 'total km', 'km'), ('z3_4_distance', 'Intensity', 'km Z3-4', 'km'),
            ('z5_t1_t2_distance', 'Intensity', 'km Z5-T1-T2', 'km'), ('sprint_distance', 'Intensity', 'km sprinting', 'km'),
            ('sessions', 'Training frequency', 'nr. sessions', 'sessions'), ('strength_sessions', 'Strength', 'strength training', 'logged sessions'),
            ('cross_training_hours', 'Cross training', 'hours alternative', 'hours')]
    for window in [3, 7]:
        for name, domain, source, units in sums:
            rows.append([f'{name}_{window}d', domain, f'Sum of {source} in last {window} days', f'E-{window}..E-1', units,
                         f'{window} observed daily values in own event row', 'End of E-1',
                         'Low in own row; high if missing dates filled from future event windows',
                         'Recent exposure, not tissue damage', 'Selected windows; overlapping records; review extrema'])
        rows.append([f'rest_days_{window}d', 'Rest', 'Count days with nr. sessions == 0; zero running km alone is not rest',
                     f'E-{window}..E-1', 'days', f'{window} observed session counts', 'End of E-1', 'Low in own row',
                     'Training-free days', 'Not sleep or biological recovery; original session coding'])
        for source, name in zip(SUBJECTIVE, ['exertion', 'training_success', 'recovery']):
            rows.append([f'mean_{name}_{window}d', 'Recovery' if name == 'recovery' else 'Subjective',
                         f'Mean {source} excluding -0.01 sentinel', f'E-{window}..E-1', 'released 0-1 rating',
                         'At least 1 recorded rating; accompanying count mandatory', 'End of E-1', 'Low in own row',
                         'Perceived response', 'Not Borg scale; personal scale usage; absent on rest days'])
            rows.append([f'observed_{name}_days_{window}d', 'Availability', f'Count ratings other than -0.01 for {source}',
                         f'E-{window}..E-1', 'days', f'{window} recorded days including rest sentinel', 'End of E-1',
                         'Low temporal risk; recording-process proxy', 'Rating availability only', 'May encode rest and habits'])
    candidates = [
        ['distance_14d', 'Volume', 'Sum two weekly distance blocks', 'E-14..E-1', 'km', '2 complete original weekly blocks', 'End of E-1', 'Use original weekly own-row blocks', 'Longer recent exposure', 'Proposed only; Week sample differs'],
        ['distance_21d', 'Volume', 'Sum three weekly distance blocks', 'E-21..E-1', 'km', '3 complete original weekly blocks', 'End of E-1', 'Use original weekly own-row blocks', 'Three-week exposure', 'Proposed only; no daily composition beyond seven days'],
        ['distance_28d', 'Volume', '28-day running total', 'E-28..E-1', 'km', '28 prospectively observed days', 'End of E-1', 'HIGH if stitching future windows or treating gaps as zero', 'Longer exposure', 'Deferred; not guaranteed in release'],
        ['distance_change_7d', 'Trend', 'Week-0 minus week-1 distance', 'E-14..E-1', 'km', '2 complete weekly blocks', 'End of E-1', 'Low using original own-row blocks', 'Change in exposure', 'Proposed; context-dependent; no causal threshold'],
        ['relative_distance', 'Relative Load', 'Current week minus prior-only personal baseline; scale by prior SD with a minimum history rule', 'Current E-7..E-1 versus history ending E-8', 'SD or km', 'At least 28 prior truly available days; assess feasibility', 'End of E-1', 'HIGH with full-athlete/future normalization', 'Unusual relative to own history', 'Deferred pending as-of history audit; unstable low SD'],
        ['load_recovery_interaction', 'Interaction', 'Prespecified distance_7d times mean_recovery_7d after training-fold centering', 'E-7..E-1', 'product', 'Both parent variables', 'End of E-1', 'Fit centering on train only', 'Joint load/response hypothesis', 'Proposed only; statistical interaction is not treatment effect']]
    rows.append(['combined_intensity_7d', 'Quality audit', 'Sum Z3-4, Z5/T1/T2 and sprint km solely to reconcile source weekly aggregate',
                 'E-7..E-1', 'km', '7 observed daily blocks', 'End of E-1', 'Low within own row; audit only',
                 'Confirms source coding; no independent clinical interpretation', 'Not used as a model feature or separate outcome contrast'])
    rows.extend(candidates)
    columns = ['feature_name','domain','definition','window','units','minimum_required_data','prediction_time_available','leakage_risk','clinical_interpretation','limitations']
    pd.DataFrame(rows, columns=columns).to_csv(ROOT/'handoff/feature_catalog.csv', index=False)
    audit = '# Leakage audit\n\nNo model has been fitted. Every implemented descriptive summary and proposed candidate is registered below. Prediction cutoff t=E-1; outcome at E. `data/interim/reconstructed_training_days.csv` is retrospective visualization only.\n\n'
    audit += '| Feature | Observation window | Prediction date/cutoff | Potential leakage risk | Decision |\n|---|---|---|---|---|\n'
    for row in rows:
        decision = 'Descriptive only, implemented within own row' if row[0].endswith(('_3d','_7d')) and not row[0].startswith('distance_change') else 'Proposed, not implemented'
        audit += f'| `{row[0]}` | {row[3]} | E / end of E-1 | {row[7]} | {decision} |\n'
    audit += '''
## Dataset and workflow risks

| Variable/process | Risk | Decision |
|---|---|---|
| `injury` | Outcome leakage | Target and descriptive grouping only |
| `Date` | Time index and sample-selection proxy; not calendar date | Split/order/audit only initially |
| `Athlete ID` | Memorization, participant overlap | Grouping only for unseen-athlete validation |
| Healthy-control selection | Uses fitness 21 days after E | Cannot undo from release; conditional retrospective estimand |
| Gaps / days until next row / next injury | Future observation/outcome information | Never predictors; no zero filling |
| Reconstructed training days | Some past days are supplied only by future event windows | Visualization only; never a prospective source without an availability audit |
| Full-athlete healthy mean/SD | Uses future observations and labels to define personal baseline | Reject; prior-only baselines and fold-specific transforms |
| Original replication notebook | Computes test-athlete statistics conditional on healthy labels; training/calibration draws come from the same observation pool | Inspect as historical code only; never execute or copy preprocessing workflow |
| Weekly released ratios | Near-zero denominator instability; not future leakage by itself | Quarantine; transparent difference or explicit denominator policy later |
| Sentinel -0.01 | Encodes rest/recording habits, not negative biological response | Mask for numeric summaries, retain rest days and availability count |
| Adjacent windows | Shared exposures across temporal boundary | Purge train outcomes whose full input span overlaps test input span (7 or 21 days); calibrate separately |
| Scaling/imputation/PCA/selection/resampling | Test distribution influences fitted transforms | Fit training fold only; no resampling before split |
| Descriptive inspection of all records | Influences later hypothesis selection | Milestone 1 is exploratory; register Phase 2 before modeling and label data reuse |

Reconstruction provenance (`first_source_event_day`, `last_source_event_day`, `supporting_event_windows`) must not enter predictors. Overlap checks and weekly consistency checks support the corrected suffix mapping. Sex is not encoded by any known ID mapping; do not infer it.
'''
    write('docs/leakage_audit.md', audit)


def notebooks():
    setup = "from pathlib import Path\nimport sys\nROOT = Path.cwd() if (Path.cwd() / 'src').exists() else Path.cwd().parent\nsys.path.insert(0, str(ROOT))\nimport pandas as pd\nfrom IPython.display import display, Image\n"
    specs = [
        ('01_data_understanding', 'Data understanding', "from src.data.load_data import load_data\nfrom src.data.validation import validate_event_table\nday, week = load_data('day', ROOT), load_data('week', ROOT)\ndisplay(pd.DataFrame([validate_event_table(day, 'day'), validate_event_table(week, 'week')]))\ndisplay(pd.read_csv(ROOT / 'reports/tables/data_dictionary.csv').head(15))\ndisplay(pd.read_csv(ROOT / 'reports/tables/subjective_sentinel_audit.csv'))"),
        ('02_athlete_timeline', 'Athlete timelines', "import json\naudit = json.loads((ROOT / 'reports/tables/audit_summary.json').read_text())\ndisplay(pd.read_csv(ROOT / 'reports/tables/day_athlete_summary.csv'))\nfor athlete in audit['example_athletes']:\n    display(Image(filename=str(ROOT / f'reports/figures/athlete_{athlete:02d}_timeline.png')))"),
        ('03_injury_event_analysis', 'Retained injury events', "display(pd.read_csv(ROOT / 'reports/tables/day_injury_intervals.csv').describe())\ndisplay(pd.read_csv(ROOT / 'reports/tables/within_athlete_contrasts.csv'))\ndisplay(Image(filename=str(ROOT / 'reports/figures/pre_event_profiles.png')))"),
        ('04_training_load_eda', 'Training exposure and subjective response', "display(pd.read_csv(ROOT / 'reports/tables/unique_training_day_distributions.csv'))\ndisplay(pd.read_csv(ROOT / 'reports/tables/pre_event_7d_distributions_by_label.csv'))\ndisplay(pd.read_csv(ROOT / 'reports/tables/released_ratio_audit.csv'))")]
    planned = [('05_feature_windows','Candidate feature windows'), ('06_baseline_models','Baseline models'),
               ('07_athlete_independent_validation','Athlete-independent validation'), ('08_temporal_models','Temporal models'),
               ('09_calibration','Calibration'), ('10_risk_profiles','Risk profiles'), ('11_decision_support','Decision support')]
    for name, title, code in specs:
        if (ROOT/f'notebooks/{name}.ipynb').exists():
            continue
        nb = nbf.v4.new_notebook(cells=[nbf.v4.new_markdown_cell(f'# {title}\n\nMilestone 1 descriptive analysis. Run `python scripts/run_milestone_01.py` first. No injury prediction model is fitted. Calendar dates are unavailable; omitted event dates are not healthy days.'), nbf.v4.new_code_cell(setup), nbf.v4.new_code_cell(code)])
        nb.metadata.kernelspec = {'display_name':'Python 3', 'language':'python', 'name':'python3'}
        nbf.write(nb, ROOT/f'notebooks/{name}.ipynb')
    for name, title in planned:
        if (ROOT/f'notebooks/{name}.ipynb').exists():
            continue
        nb = nbf.v4.new_notebook(cells=[nbf.v4.new_markdown_cell(f'# {title}\n\n**Planned only. Blocked pending Milestone 1 review.** No models, calibration, risk thresholds, or clinical recommendations have been produced.\n\nSee `docs/phase_02_proposal.md`, `docs/temporal_design.md`, and `handoff/feature_catalog.csv`.')])
        nbf.write(nb, ROOT/f'notebooks/{name}.ipynb')


def structure():
    for folder in ['data/raw','data/interim','data/processed','notebooks','reports/figures','reports/tables','handoff','tests']:
        (ROOT/folder).mkdir(parents=True, exist_ok=True)
    modules = {
        'features': ['rolling','load_change','recovery','athlete_baselines'],
        'models': ['baseline','tree_models','temporal_models','calibration'],
        'validation': ['temporal','athlete_split','leakage'],
        'visualization': ['risk_plots','calibration_plots']}
    for package in ['data','features','models','validation','analysis','visualization']:
        write(f'src/{package}/__init__.py', f'"""{package.capitalize()} package."""')
    for package, names in modules.items():
        for name in names:
            p = ROOT/f'src/{package}/{name}.py'
            if not p.exists():
                write(str(p.relative_to(ROOT)), f'"""Reserved: {name.replace("_", " ")}.\n\nNot implemented. Requires Milestone 1 review before further work.\n"""')
    write('.gitignore', '''# Private/local downloaded copies and reproducible derived data
data/raw/*
!data/raw/.gitkeep
data/interim/*
!data/interim/.gitkeep
data/processed/*
!data/processed/.gitkeep
docs/sources/
data/complementary/*/raw/
data/complementary/*/processed/
data/complementary/review_sources/
data/complementary/wu_2026/supplement_methods.txt
__pycache__/
.pytest_cache/
.ipynb_checkpoints/
.venv/
.env
*.pyc
''')
    for folder in ['raw','interim','processed']:
        write(f'data/{folder}/.gitkeep','')
    audit = json.loads((ROOT/'reports/tables/audit_summary.json').read_text())
    pins = {**audit['environment']['packages'], 'openpyxl':'3.1.5','scikit-learn':'1.9.1'}
    write('requirements.txt', '\n'.join(f'{name}=={version}' for name, version in pins.items()))


if __name__ == '__main__':
    structure()
    dictionary()
    registry()
    notebooks()
    print('Structure, dictionary, registry, leakage audit, and 11 staged notebooks generated.')
