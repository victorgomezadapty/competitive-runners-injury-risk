"""Reproduce all Milestone 1 tables/figures from verified original CSVs. No ML."""
from pathlib import Path
import sys
import json
import platform
import importlib.metadata
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data.load_data import load_data
from src.data.validation import validate_event_table
from src.data.timelines import (DAY_VARIABLES, SUBJECTIVE, to_history_long,
                                reconstruct_training_days, athlete_summary, observation_gaps, day_column)
from src.features.daily import summarize_pre_event
from src.analysis.injury_events import injury_intervals
from src.analysis.statistics import describe_columns, within_athlete_contrasts
from src.visualization.timelines import plot_athlete, plot_event_profiles
import matplotlib.pyplot as plt


def write_csv(df, name):
    df.to_csv(ROOT / 'reports/tables' / name, index=False)


def main():
    if 'Status: **understood' not in (ROOT / 'docs/injury_definition.md').read_text(encoding='utf-8'):
        raise RuntimeError('Target-definition gate not satisfied')
    for folder in ['reports/tables', 'reports/figures', 'data/interim', 'data/processed']:
        (ROOT/folder).mkdir(parents=True, exist_ok=True)
    day, week = load_data('day'), load_data('week')
    audit = {k: validate_event_table(d, k) for k, d in [('day', day), ('week', week)]}
    interval_tables = []
    for approach, df in [('day', day), ('week', week)]:
        stats = athlete_summary(df)
        write_csv(stats, f'{approach}_athlete_summary.csv')
        write_csv(observation_gaps(df), f'{approach}_observation_gaps.csv')
        intervals = injury_intervals(df)
        write_csv(intervals, f'{approach}_injury_intervals.csv')
        diffs = intervals.days_since_previous_retained_injury.dropna()
        audit[approach].update({
            'consecutive_injury_pairs': int(diffs.eq(1).sum()),
            'injury_interval_days': diffs.describe().to_dict(),
            'observations_per_athlete': stats.observations.describe().to_dict(),
            'selected_event_span_days': stats.selected_event_span_days.describe().to_dict(),
            'total_unselected_days_within_athlete_spans': int(stats.days_without_selected_event_inside_span.sum()),
            'consecutive_selected_event_pairs': int(df.sort_values(['Athlete ID', 'Date']).groupby('Athlete ID').Date.diff().eq(1).sum())})
        missing = df.isna().sum().rename('blank_cells').to_frame()
        missing['nonfinite_cells'] = (~np.isfinite(df)).sum()
        missing['minus_001_cells'] = df.eq(-.01).sum()
        missing['zero_cells'] = df.eq(0).sum()
        write_csv(missing.rename_axis('variable').reset_index(), f'{approach}_missingness_by_variable.csv')
        athlete_missing = df.isna().groupby(df['Athlete ID']).sum().sum(axis=1).rename('blank_cells').to_frame()
        athlete_missing['minus_001_cells'] = df.eq(-.01).groupby(df['Athlete ID']).sum().sum(axis=1)
        write_csv(athlete_missing.reset_index(), f'{approach}_missingness_by_athlete.csv')
        write_csv(describe_columns(df, df.columns, approach), f'{approach}_released_column_distributions.csv')
    merged = day[['Athlete ID', 'Date', 'injury']].merge(week[['Athlete ID', 'Date', 'injury']],
                     on=['Athlete ID', 'Date'], suffixes=('_day', '_week'), how='outer', indicator=True)
    write_csv(merged[merged['_merge'].ne('both')], 'representation_unmatched_events.csv')
    audit['cross_representation'] = {'matched_keys': int(merged['_merge'].eq('both').sum()),
            'day_only': int(merged['_merge'].eq('left_only').sum()),
            'week_only': int(merged['_merge'].eq('right_only').sum()),
            'label_disagreements': int((merged.injury_day != merged.injury_week)[merged['_merge'].eq('both')].sum())}
    history = to_history_long(day)
    training, conflicts = reconstruct_training_days(history)
    training.to_csv(ROOT/'data/interim/reconstructed_training_days.csv', index=False)
    write_csv(conflicts, 'overlapping_history_conflicts.csv')
    audit['history'] = {'window_cells_rows': len(history), 'unique_athlete_training_days': len(training),
                        'conflicting_athlete_days': len(conflicts),
                        'earliest_training_relative_day': int(training.training_day.min()),
                        'latest_training_relative_day': int(training.training_day.max()),
                        'rest_days_reconstructed': int(training['nr. sessions'].eq(0).sum()),
                        'sentinel_cells_in_event_windows': int(history[SUBJECTIVE].eq(-.01).sum().sum())}
    sentinel_checks = []
    for variable in SUBJECTIVE:
        sentinel = history[variable].eq(-.01)
        rest = history['nr. sessions'].eq(0)
        sentinel_checks.append({'variable': variable, 'sentinel_cells': int(sentinel.sum()),
                                'sentinel_on_training_day': int((sentinel & ~rest).sum()),
                                'rating_present_on_rest_day': int((~sentinel & rest).sum()),
                                'zero_training_day_ratings': int((history[variable].eq(0) & ~rest).sum())})
    write_csv(pd.DataFrame(sentinel_checks), 'subjective_sentinel_audit.csv')
    clean_training = training.copy()
    clean_training[SUBJECTIVE] = clean_training[SUBJECTIVE].replace(-.01, np.nan)
    write_csv(describe_columns(clean_training, DAY_VARIABLES, 'reconstructed_unique_days_retrospective'), 'unique_training_day_distributions.csv')
    subjective_usage = []
    for athlete, g in clean_training.groupby('Athlete ID'):
        for variable in SUBJECTIVE:
            ratings = g[variable].dropna()
            subjective_usage.append({'Athlete ID': athlete, 'variable': variable, 'recorded_ratings': len(ratings),
                'unavailable_rest_ratings': int(g[variable].isna().sum()), 'zero_ratings': int(ratings.eq(0).sum()),
                'distinct_ratings': int(ratings.nunique()), 'mean': ratings.mean(), 'sd': ratings.std()})
    write_csv(pd.DataFrame(subjective_usage), 'subjective_scale_usage_by_athlete.csv')
    training_stats = training.groupby('Athlete ID').agg(reconstructed_training_days=('training_day', 'size'),
                              first_training_day=('training_day', 'min'), last_training_day=('training_day', 'max'),
                              rest_days=('nr. sessions', lambda x: x.eq(0).sum()))
    training_stats['training_span_days'] = training_stats.last_training_day-training_stats.first_training_day+1
    training_stats['unreconstructed_days_inside_span'] = training_stats.training_span_days-training_stats.reconstructed_training_days
    write_csv(training_stats.reset_index(), 'reconstructed_history_by_athlete.csv')
    summaries = []
    for window in (3, 7):
        features = summarize_pre_event(day, window)
        features.to_csv(ROOT/f'data/processed/day_pre_event_{window}d_descriptive.csv', index=False)
        variables = [c for c in features if c.endswith(f'_{window}d') and not c.startswith('observed_')]
        contrast, paired = within_athlete_contrasts(features, variables)
        contrast['window_days'] = window
        summaries.append(contrast)
        write_csv(paired, f'within_athlete_paired_{window}d.csv')
        desc = pd.concat([describe_columns(g, variables, f'{window}d_label_{label}') for label, g in features.groupby('injury')])
        write_csv(desc, f'pre_event_{window}d_distributions_by_label.csv')
    write_csv(pd.concat(summaries, ignore_index=True), 'within_athlete_contrasts.csv')
    # Independent weekly summaries, never copied onto daily-only records.
    variables = ['total kms', 'total km Z3-4', 'total km Z5-T1-T2', 'nr. rest days', 'avg exertion',
                 'avg recovery', 'avg training success', 'nr. strength trainings', 'total hours alternative training']
    contrasts, paired = within_athlete_contrasts(week, variables)
    write_csv(contrasts, 'week0_within_athlete_contrasts.csv')
    write_csv(paired, 'week0_paired_athletes.csv')
    # Reconcile known common aggregate definitions on shared event keys.
    f7 = summarize_pre_event(day, 7)
    audit['history']['all_rest_7d_event_windows'] = int(f7.rest_days_7d.eq(7).sum())
    audit['history']['injury_rows_after_all_rest_7d'] = int(f7.loc[f7.rest_days_7d.eq(7), 'injury'].sum())
    rest_distribution = f7.groupby(['injury','rest_days_7d']).size().rename('event_rows').reset_index()
    write_csv(rest_distribution, 'rest_days_7d_distribution.csv')
    both = f7.merge(week, on=['Athlete ID', 'Date'], suffixes=('_derived', '_week'))
    both['combined_intensity_7d'] = both.z3_4_distance_7d+both.z5_t1_t2_distance_7d+both.sprint_distance_7d
    reconcile = []
    for derived, released in [('distance_7d', 'total kms'), ('sessions_7d', 'nr. sessions'),
                               ('rest_days_7d', 'nr. rest days'), ('z3_4_distance_7d', 'total km Z3-4'),
                               ('z5_t1_t2_distance_7d', 'total km Z5-T1-T2'),
                               ('strength_sessions_7d', 'nr. strength trainings'), ('cross_training_hours_7d', 'total hours alternative training'),
                               ('mean_exertion_7d', 'avg exertion'), ('mean_recovery_7d', 'avg recovery'),
                               ('mean_training_success_7d', 'avg training success'),
                               ('combined_intensity_7d', 'total km Z3-Z4-Z5-T1-T2')]:
        delta = (both[derived]-both[released]).abs()
        reconcile.append({'daily_summary': derived, 'weekly_column': released, 'matched_rows': len(both),
                           'comparable_nonmissing_rows': int(delta.notna().sum()),
                           'within_0011': int(delta.le(.011).sum()), 'max_absolute_difference': delta.max(),
                           'median_absolute_difference': delta.median()})
    write_csv(pd.DataFrame(reconcile), 'daily_weekly_aggregate_reconciliation.csv')
    ratio_checks = []
    for col, numerator, denominator in [('rel total kms week 0_1', 'total kms', 'total kms.1'),
                                       ('rel total kms week 0_2', 'total kms', 'total kms.2'),
                                       ('rel total kms week 1_2', 'total kms.1', 'total kms.2')]:
        positive = week[denominator].gt(0)
        err = (week.loc[positive, col] - week.loc[positive, numerator]/week.loc[positive, denominator]).abs()
        ratio_checks.append({'variable': col, 'zero_denominator_rows': int((~positive).sum()),
                             'positive_denominator_max_error': err.max(), 'max_released_ratio': week[col].max(),
                             'ratios_over_10': int(week[col].gt(10).sum())})
    write_csv(pd.DataFrame(ratio_checks), 'released_ratio_audit.csv')
    anomaly_rows = training.loc[(training['total km'].gt(50)) | (training['km sprinting'].gt(5)) |
               training['hours alternative'].gt(8) | training['strength training'].gt(1) |
               training[['km Z3-4','km Z5-T1-T2','km sprinting']].sum(axis=1).gt(training['total km']+.011)]
    write_csv(anomaly_rows, 'training_values_for_source_review.csv')
    audit['history']['rows_for_source_review'] = len(anomaly_rows)
    athlete_stats = athlete_summary(day).sort_values(['observations', 'Athlete ID'])
    eligible = athlete_stats[athlete_stats.injury_labels.gt(0)]
    positions = np.linspace(0, len(eligible)-1, 5).round().astype(int)
    selected = eligible.iloc[positions]['Athlete ID'].astype(int).tolist()
    for athlete in selected:
        plot_athlete(training, day, athlete, ROOT/f'reports/figures/athlete_{athlete:02d}_timeline.png')
    plot_event_profiles(history, ROOT/'reports/figures/pre_event_profiles.png')
    fig, axs = plt.subplots(3, 4, figsize=(14, 10), layout='constrained')
    fig.suptitle('Released training exposure | reconstructed unique days (retrospective)', fontsize=15)
    for ax, variable in zip(axs.flat, DAY_VARIABLES):
        values = clean_training[variable].dropna()
        ax.hist(values, bins=35, color='#21618c', alpha=.85)
        ax.set_title(variable, fontsize=10)
        ax.set_ylabel('Observed days')
        ax.spines[['top','right']].set_visible(False)
    axs.flat[10].hist(f7.rest_days_7d, bins=np.arange(-.5,8), color='#2c8a75')
    axs.flat[10].set_title('Rest days per selected 7-day window')
    axs.flat[10].set_xlabel('Days (not independent windows)')
    axs.flat[11].axis('off')
    axs.flat[11].text(.05,.9, 'No gap filling.\nSentinel -0.01 excluded from ratings.\nExtremes retained for review.\nCounts describe selected history,\nnot the full original training log.', va='top', fontsize=11, linespacing=1.7)
    fig.savefig(ROOT/'reports/figures/training_distributions.png', dpi=160)
    plt.close(fig)
    audit['example_athletes'] = selected
    audit['environment'] = {'python': platform.python_version(), 'packages': {p: importlib.metadata.version(p) for p in ['pandas','numpy','matplotlib','scipy','requests','nbformat','nbclient','ipykernel','pytest']}}
    (ROOT/'reports/tables/audit_summary.json').write_text(json.dumps(audit, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps({k: {x:y for x,y in v.items() if x in ['rows','athletes','injury_rows','athletes_with_injury','injury_prevalence']} for k,v in audit.items() if k in ['day','week']}, indent=2))
    print('Reconstruction:', audit['history'])
    print('Example athletes:', selected)


if __name__ == '__main__':
    main()
