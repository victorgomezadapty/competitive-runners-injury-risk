"""Corrected day suffixes and retrospective reconstruction with provenance.

The reconstruction is for visualization only. It must NOT be used as an as-of
predictor table: a future selected event can expose a past training day.
"""
import numpy as np
import pandas as pd

DAY_VARIABLES = ["nr. sessions", "total km", "km Z3-4", "km Z5-T1-T2", "km sprinting",
                 "strength training", "hours alternative", "perceived exertion",
                 "perceived trainingSuccess", "perceived recovery"]
SUBJECTIVE = DAY_VARIABLES[-3:]


def day_column(variable, suffix):
    if suffix not in range(7):
        raise ValueError("Daily suffix must be 0..6")
    return variable if suffix == 0 else f"{variable}.{suffix}"


def to_history_long(df):
    parts = []
    for suffix in range(7):
        part = df[["Athlete ID", "Date", "injury"]].copy()
        part = part.rename(columns={"Date": "event_day", "injury": "event_label"})
        part["days_before_event"] = 7 - suffix
        part["training_day"] = part.event_day - (7 - suffix)
        for variable in DAY_VARIABLES:
            part[variable] = df[day_column(variable, suffix)].to_numpy()
        parts.append(part)
    return pd.concat(parts, ignore_index=True).sort_values(["Athlete ID", "event_day", "training_day"])


def reconstruct_training_days(history):
    grouped = history.groupby(["Athlete ID", "training_day"], sort=True)
    spread = grouped[DAY_VARIABLES].max() - grouped[DAY_VARIABLES].min()
    conflicts = spread.gt(1e-8).any(axis=1)
    result = grouped[DAY_VARIABLES].first()
    result["supporting_event_windows"] = grouped.size()
    result["first_source_event_day"] = grouped.event_day.min()
    result["last_source_event_day"] = grouped.event_day.max()
    result["conflicting_values"] = conflicts
    # Do not silently pick one version where overlapping windows disagree.
    result.loc[conflicts, DAY_VARIABLES] = np.nan
    return result.reset_index(), spread.loc[conflicts].reset_index()


def athlete_summary(df):
    ordered = df.sort_values(["Athlete ID", "Date"])
    result = ordered.groupby("Athlete ID").agg(
        observations=("Date", "size"), first_event_day=("Date", "min"),
        last_event_day=("Date", "max"), injury_labels=("injury", "sum"))
    result["selected_event_span_days"] = result.last_event_day - result.first_event_day + 1
    result["days_without_selected_event_inside_span"] = result.selected_event_span_days - result.observations
    result["selected_event_coverage"] = result.observations / result.selected_event_span_days
    result["injury_label_prevalence"] = result.injury_labels / result.observations
    gap = ordered.groupby("Athlete ID").Date.diff()
    result["largest_event_gap_days"] = gap.groupby(ordered['Athlete ID']).max()
    result["contiguous_event_runs"] = (gap.ne(1)).groupby(ordered['Athlete ID']).sum()
    result["blank_cells"] = df.isna().groupby(df['Athlete ID']).sum().sum(axis=1)
    return result.reset_index()


def observation_gaps(df):
    ordered = df.sort_values(["Athlete ID", "Date"]).copy()
    ordered["previous_event_day"] = ordered.groupby('Athlete ID').Date.shift()
    ordered["gap_days"] = ordered.Date - ordered.previous_event_day
    return ordered.loc[ordered.gap_days.gt(1), ['Athlete ID', 'previous_event_day', 'Date', 'gap_days']]
