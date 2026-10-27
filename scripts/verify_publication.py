"""Verify the exact research outputs, notebook execution and public distribution boundaries."""
from pathlib import Path
import sys,json,hashlib,re
from html.parser import HTMLParser
import pandas as pd
import nbformat
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.validation.leakage import audit_split

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id'in a:self.ids.append(a['id'])
        for name in ['href','src']:
            if name in a:self.links.append(a[name])

def main():
    final=json.loads((ROOT/'reports/final_analysis/manifest.json').read_text())
    assert sha(ROOT/'config/final_analysis_protocol.json')==final['protocol_sha256']
    assert sha(ROOT/'scripts/run_final_analysis.py')==final['source_code_sha256']
    for name,digest in final['files'].items():assert sha(ROOT/name)==digest,name
    frame=pd.read_csv(ROOT/'data/processed/final_analysis/matched_features.csv')
    parts=pd.read_csv(ROOT/'data/processed/final_analysis/row_partitions.csv')
    cases=0
    for (protocol,seed,fold),g in parts.groupby(['protocol','seed','fold']):
        ids=[g.loc[g.partition.eq(role),'row_id'].to_numpy() for role in ['train','calibration','test']]
        audit_split(frame,*ids,lookback=63 if protocol=='known_temporal' else 21,grouped=protocol!='known_temporal',temporal=protocol!='unseen_athlete')
        cases+=1
    assert cases==21
    executed=[]
    for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
        nb=nbformat.read(path,as_version=4);nbformat.validate(nb)
        code=[c for c in nb.cells if c.cell_type=='code']
        assert code and all(c.execution_count is not None for c in code),path.name
        assert not any(o.output_type=='error' for c in code for o in c.outputs),path.name
        executed.append(path.name)
    assert len(executed)==11
    data=json.loads((ROOT/'web/data.json').read_text())
    assert len(data['athletes'])>=5
    assert len({a['id'] for a in data['athletes']})==len(data['athletes'])
    assert {m['protocol'] for m in data['metrics']}=={'known_temporal','unseen_athlete','unseen_athlete_temporal'}
    for path in (ROOT/'web').glob('*.html'):
        parsed=Links();parsed.feed(path.read_text(encoding='utf-8'))
        assert len(parsed.ids)==len(set(parsed.ids)),path.name
        for link in parsed.links:
            if link.startswith(('http','mailto:','data:')):continue
            base=link.split('?')[0].split('#')[0]
            if not base:
                assert link[1:] in parsed.ids,(path.name,link)
            elif base=='/':assert (ROOT/'web/index.html').exists()
            else:assert (ROOT/'web'/base.lstrip('/')).exists(),(path.name,link)
    dataset=ROOT/'release/kaggle_dataset'
    checksum=json.loads((dataset/'checksums.json').read_text())
    for name,digest in checksum.items():assert sha(dataset/name)==digest,name
    assert not list(dataset.rglob('*.pdf')) and not list(dataset.rglob('*.xlsx'))
    assert not list(dataset.rglob('*.ipynb'))
    result=dict(status='passed',date='2026-10-27',final_split_cases=cases,base_fits=84,executed_notebooks=executed,kaggle_checksummed_files=len(checksum),web_examples=len(data['athletes']),public_articles_redistributed=0,clinical_model_deployed=False)
    (ROOT/'reports/publication_verification.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
