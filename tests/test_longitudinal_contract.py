"""Guard scientific invariants: lag order, leakage boundaries, missingness and grouping."""
import numpy as np
import pandas as pd
import pytest
from src.data.timelines import DAY_VARIABLES, SUBJECTIVE, day_column, to_history_long, reconstruct_training_days
from src.data.validation import validate_event_table
from src.features.daily import summarize_pre_event


def synthetic():
    rows = []
    for event in (10, 11):
        row = {'Athlete ID': 1, 'Date': event, 'injury': int(event == 11)}
        for suffix in range(7):
            training_day = event-7+suffix
            for variable in DAY_VARIABLES:
                row[day_column(variable, suffix)] = training_day
        rows.append(row)
    return pd.DataFrame(rows)


def test_corrected_suffix_mapping_and_overlap_reconstruction():
    history = to_history_long(synthetic())
    assert history.training_day.lt(history.event_day).all()
    row = history[history.event_day.eq(10)].sort_values('training_day')
    assert row.training_day.tolist() == list(range(3, 10))
    assert row['total km'].tolist() == list(range(3, 10))
    training, conflicts = reconstruct_training_days(history)
    assert len(training) == 8
    assert conflicts.empty
    assert training['total km'].tolist() == list(range(3, 11))


def test_conflicting_overlap_is_not_silently_resolved():
    df = synthetic()
    df.loc[1, 'total km'] = 999
    training, conflicts = reconstruct_training_days(to_history_long(df))
    assert len(conflicts) == 1
    assert training.loc[training.conflicting_values, 'total km'].isna().all()


def test_features_do_not_change_when_future_rows_change():
    df = synthetic()
    expected = summarize_pre_event(df).iloc[0].copy()
    df.loc[1, [c for c in df if c not in ['Athlete ID','Date','injury']]] = 9999
    pd.testing.assert_series_equal(expected, summarize_pre_event(df).iloc[0])
    f3 = summarize_pre_event(df, 3)
    assert f3.iloc[0].distance_3d == 7+8+9
    assert f3.iloc[0].feature_end_day == 9


def test_rest_sentinel_is_not_a_rating_and_zero_km_is_not_rest():
    df = synthetic().iloc[:1].copy()
    for suffix in range(7):
        df[day_column('nr. sessions', suffix)] = 0 if suffix < 6 else 1
        df[day_column('total km', suffix)] = 0
        for variable in SUBJECTIVE:
            df[day_column(variable, suffix)] = -.01 if suffix < 6 else .5
    result = summarize_pre_event(df)
    assert result.rest_days_7d.iloc[0] == 6
    assert result.mean_recovery_7d.iloc[0] == .5
    assert result.observed_recovery_days_7d.iloc[0] == 1
    df['nr. sessions.6'] = 0
    df['perceived recovery.6'] = -.01
    assert np.isnan(summarize_pre_event(df).mean_recovery_7d.iloc[0])


def test_duplicate_athlete_event_rejected():
    df = pd.concat([synthetic(), synthetic().iloc[:1]])
    with pytest.raises(ValueError, match='Duplicate'):
        validate_event_table(df, 'day')


def test_original_files_respect_order_and_label_agreement():
    from src.data.load_data import load_data
    day, week = load_data('day'), load_data('week')
    validate_event_table(day, 'day')
    validate_event_table(week, 'week')
    ordered = day.sort_values(['Athlete ID','Date'])
    next_values = ordered.groupby('Athlete ID')['total km'].shift(-1)
    next_day = ordered.groupby('Athlete ID').Date.shift(-1)
    adjacent = next_day.eq(ordered.Date+1)
    assert np.allclose(ordered.loc[adjacent,'total km.1'], next_values[adjacent])
    shared = day.merge(week,on=['Athlete ID','Date'])
    assert shared.injury_x.eq(shared.injury_y).all()
