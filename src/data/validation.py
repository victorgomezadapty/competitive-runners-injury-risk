"""Structural checks. Expected cohort/event counts are computed, never hard-coded."""
import numpy as np


def validate_event_table(df, approach):
    for name in ("Athlete ID", "Date", "injury"):
        if name not in df or df[name].isna().any():
            raise ValueError(f"Missing key/target: {name}")
        if not np.equal(df[name], np.floor(df[name])).all():
            raise ValueError(f"Noninteger key/target: {name}")
    if df.duplicated(["Athlete ID", "Date"]).any():
        raise ValueError("Duplicate athlete-event key")
    if not set(df.injury.unique()).issubset({0, 1}):
        raise ValueError("Target is not binary")
    if not np.isfinite(df.to_numpy(dtype=float)).all():
        raise ValueError("Missing or infinite released values")
    return {"representation": approach, "rows": len(df), "columns": len(df.columns),
            "athletes": int(df['Athlete ID'].nunique()), "injury_rows": int(df.injury.sum()),
            "injury_prevalence": float(df.injury.mean()),
            "athletes_with_injury": int(df.loc[df.injury.eq(1), 'Athlete ID'].nunique()),
            "first_relative_day": int(df.Date.min()), "last_relative_day": int(df.Date.max()),
            "blank_cells": int(df.isna().sum().sum()), "duplicate_keys": 0}
