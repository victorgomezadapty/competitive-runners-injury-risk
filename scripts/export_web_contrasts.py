"""Add saved within-athlete pre-event contrasts to web/data.json.

Reads only committed Milestone 1 tables (reports/tables). No model is refitted
and no value is recomputed beyond counting the sign of each saved paired
athlete difference.
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "reports" / "tables"
WEB = ROOT / "web" / "data.json"


def main():
    data = json.loads(WEB.read_text(encoding="utf-8"))
    signs = defaultdict(lambda: {"higher": 0, "lower": 0, "equal": 0})
    for window in (3, 7):
        with open(TABLES / f"within_athlete_paired_{window}d.csv", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                value = float(row["difference"])
                key = "higher" if value > 0 else "lower" if value < 0 else "equal"
                signs[row["feature"]][key] += 1
    contrasts = []
    with open(TABLES / "within_athlete_contrasts.csv", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            contrasts.append({
                "feature": row["feature"],
                "window_days": int(row["window_days"]),
                "paired_athletes": int(row["paired_athletes"]),
                "healthy_mean": round(float(row["healthy_athlete_mean"]), 4),
                "injury_mean": round(float(row["injury_athlete_mean"]), 4),
                "difference": round(float(row["injury_minus_healthy"]), 4),
                "ci95_low": round(float(row["ci95_low"]), 4),
                "ci95_high": round(float(row["ci95_high"]), 4),
                "standardized": round(float(row["paired_standardized_difference"]), 4),
                **signs[row["feature"]],
            })
    data["contrasts"] = contrasts
    rows = {}
    with open(TABLES / "pre_event_7d_distributions_by_label.csv", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["variable"] == "distance_7d":
                rows[row["representation"][-1]] = {k: round(float(row[k]), 2) for k in ("n", "q25", "median", "q75", "p99")}
    data["distance_7d_rows"] = {"healthy": rows["0"], "injury": rows["1"]}
    WEB.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Exported {len(contrasts)} paired contrasts to {WEB.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
