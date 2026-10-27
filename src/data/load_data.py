"""Read original files without changing names or inventing calendar dates."""
from pathlib import Path
import hashlib
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
FILES = {k: f"{k}_approach_maskedID_timeseries.csv" for k in ("day", "week")}


def load_data(approach="day", root=ROOT):
    if approach not in FILES:
        raise ValueError("approach must be day or week")
    root = Path(root)
    path = root / 'data/raw' / FILES[approach]
    manifest = json.loads((root/'data/source_manifest.json').read_text(encoding='utf-8'))
    source = next(f for f in manifest['files'] if f['filename'] == FILES[approach])
    if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
        raise ValueError(f'Raw file changed from the audited release: {path.name}')
    return pd.read_csv(path)
