"""Descriptive contrasts respecting athlete clustering; no prediction model."""
import numpy as np
import pandas as pd


def describe_columns(df, columns, representation):
    rows = []
    for col in columns:
        s = df[col]
        q = s.quantile([0, .01, .25, .5, .75, .99, 1])
        rows.append({'representation': representation, 'variable': col, 'n': int(s.notna().sum()),
                     'missing': int(s.isna().sum()), 'mean': s.mean(), 'sd': s.std(),
                     'min': q.iloc[0], 'p01': q.iloc[1], 'q25': q.iloc[2], 'median': q.iloc[3],
                     'q75': q.iloc[4], 'p99': q.iloc[5], 'max': q.iloc[6]})
    return pd.DataFrame(rows)


def within_athlete_contrasts(df, variables, n_boot=2000, seed=20261025):
    """Mean of athlete-specific (injury minus healthy) means, equal athlete weight.

    Bootstrap resamples entire paired athlete contrasts. CIs describe athlete-level
    uncertainty, not a causal effect, adjusted effect, or clinical threshold.
    """
    rng = np.random.default_rng(seed)
    rows, paired_rows = [], []
    for variable in variables:
        means = df.groupby(['Athlete ID', 'injury'])[variable].mean().unstack()
        means = means.reindex(columns=[0, 1]).dropna()
        diff = (means[1] - means[0]).to_numpy()
        if not len(diff):
            continue
        boot = diff[rng.integers(0, len(diff), size=(n_boot, len(diff)))].mean(axis=1)
        sd = diff.std(ddof=1)
        rows.append({'feature': variable, 'paired_athletes': len(diff),
                     'healthy_athlete_mean': means[0].mean(), 'injury_athlete_mean': means[1].mean(),
                     'injury_minus_healthy': diff.mean(), 'ci95_low': np.quantile(boot, .025),
                     'ci95_high': np.quantile(boot, .975),
                     'paired_standardized_difference': diff.mean()/sd if sd > 0 else np.nan})
        for athlete, values in means.iterrows():
            paired_rows.append({'Athlete ID': athlete, 'feature': variable, 'healthy_mean': values[0],
                                'injury_mean': values[1], 'difference': values[1]-values[0]})
    return pd.DataFrame(rows), pd.DataFrame(paired_rows)
