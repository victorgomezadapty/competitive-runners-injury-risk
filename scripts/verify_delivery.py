"""Offline delivery audit, preserving Milestone 1 and authorized Phase 2 boundaries."""
from pathlib import Path
import ast
import hashlib
import json
import re
import nbformat
import pandas as pd
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))


def main():
    phase2_path=ROOT/'reports/phase_02/run_manifest.json'
    phase2=json.loads(phase2_path.read_text()) if phase2_path.exists() else None
    final_path=ROOT/'reports/final_analysis/manifest.json'
    final=json.loads(final_path.read_text()) if final_path.exists() else None
    historical=ROOT/'reports/milestone_01_verification.json'
    current=ROOT/'reports/verification.json'
    if phase2 and not historical.exists() and current.exists():
        old=json.loads(current.read_text())
        if not old.get('prediction_models_trained'):
            historical.write_bytes(current.read_bytes())
    expected_docs = ['data_dictionary','injury_definition','cohort_definition','temporal_design',
                     'leakage_audit','methodology','clinical_interpretation','limitations',
                     'phase_02_proposal','references','complementary_dataset_review']
    for name in expected_docs:
        assert (ROOT/f'docs/{name}.md').is_file(), name
    manifest = json.loads((ROOT/'data/source_manifest.json').read_text())
    for entry in manifest['files']:
        assert hashlib.sha256((ROOT/'data/raw'/entry['filename']).read_bytes()).hexdigest() == entry['sha256']
    soccer = ROOT/'data/complementary/soccermon'
    soccer_manifest = json.loads((soccer/'source_manifest.json').read_text())
    assert hashlib.sha256((soccer/'raw/subjective.zip').read_bytes()).hexdigest() == soccer_manifest['sha256']
    wu = ROOT/'data/complementary/wu_2026'
    wu_manifest = json.loads((wu/'source_manifest.json').read_text())
    for entry in wu_manifest['files']:
        assert hashlib.sha256((wu/'raw'/entry['filename']).read_bytes()).hexdigest() == entry['sha256']
    notebook_results = []
    for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        code = [c for c in notebook.cells if c.cell_type == 'code']
        if int(path.name[:2]) <= (11 if final else (9 if phase2 else 4)):
            assert code and all(c.execution_count is not None for c in code), path.name
            assert not any(o.output_type == 'error' for c in code for o in c.outputs), path.name
        else:
            assert not code, f'Later phase has executable code: {path.name}'
        notebook_results.append({'notebook':path.name, 'executed_cells':sum(c.execution_count is not None for c in code),
                                 'error_outputs':sum(o.output_type=='error' for c in code for o in c.outputs)})
    assert len(notebook_results) == 11
    for path in (ROOT/'src/models').glob('*.py'):
        if phase2 and path.name in ['baseline.py','calibration.py']:
            continue
        tree = ast.parse(path.read_text(encoding='utf-8'))
        assert all(isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant) and isinstance(n.value.value,str) for n in tree.body), path.name
    missing_links = []
    for path in ROOT.rglob('*.md'):
        if any(x in path.relative_to(ROOT).parts for x in ['raw','interim','processed','sources','.git','release','node_modules','dist']):
            continue
        for target in re.findall(r'\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            if '://' not in target and not target.startswith('#') and not (path.parent/target.split('#')[0]).exists():
                missing_links.append([str(path.relative_to(ROOT)), target])
    assert not missing_links, missing_links
    dictionary = pd.read_csv(ROOT/'reports/tables/data_dictionary.csv')
    source_columns = sum(len(pd.read_csv(ROOT/'data/raw'/entry['filename'], nrows=0).columns)
                         for entry in manifest['files'] if entry['filename'].endswith('.csv'))
    assert len(dictionary) == source_columns
    catalog = pd.read_csv(ROOT/'handoff/feature_catalog.csv')
    assert not catalog.feature_name.duplicated().any()
    assert len(list((ROOT/'reports/figures').glob('athlete_*_timeline.png'))) >= 5
    split_cases=0
    if phase2:
        assert phase2['status']=='completed'
        assert hashlib.sha256((ROOT/'config/phase_02_protocol.json').read_bytes()).hexdigest()==phase2['protocol_sha256']
        for name,checksum in phase2['source_code_sha256'].items():
            assert hashlib.sha256((ROOT/name.replace('\\','/')).read_bytes()).hexdigest()==checksum, f'Numerical-run source changed: {name}'
        from src.validation.leakage import audit_split
        raw=pd.read_csv(ROOT/'data/raw/day_approach_maskedID_timeseries.csv',usecols=['Athlete ID','Date','injury'])
        assignments=pd.read_csv(ROOT/'data/processed/phase_02/row_partitions.csv')
        for (protocol,fold),g in assignments.groupby(['protocol','fold']):
            indices=[g.loc[g.partition.eq(p),'row_id'].to_numpy() for p in ['train','calibration','test']]
            audit_split(raw,*indices,lookback=63 if protocol=='known_temporal' else 7,
                        grouped=protocol!='known_temporal',temporal=protocol!='unseen_athlete')
            split_cases+=1
        output_manifest=json.loads((ROOT/'reports/phase_02/output_manifest.json').read_text())
        for name,checksum in output_manifest['files'].items():
            assert hashlib.sha256((ROOT/name.replace('\\','/')).read_bytes()).hexdigest()==checksum, name
    result = {'status':'passed', 'raw_checksums_verified':len(manifest['files']),
              'stage':'final_research' if final else ('phase_02' if phase2 else 'milestone_01'),'split_cases_reverified':split_cases,
              'complementary_checksums_verified':1+len(wu_manifest['files']),
              'dictionary_columns_documented':len(dictionary), 'feature_registry_entries':len(catalog),
              'notebooks':notebook_results, 'missing_local_links':missing_links,
              'models_implemented':bool(phase2), 'prediction_models_trained':bool(phase2),
              'clinical_deployment':False,
              'note':'Scientific-contract tests are run separately with python -m pytest -q.'}
    (ROOT/'reports/verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
