"""Intervals between retained flags, not all biological injuries."""


def injury_intervals(df):
    events = df.loc[df.injury.eq(1), ['Athlete ID', 'Date']].sort_values(['Athlete ID', 'Date']).copy()
    events['previous_injury_day'] = events.groupby('Athlete ID').Date.shift()
    events['days_since_previous_retained_injury'] = events.Date - events.previous_injury_day
    return events
