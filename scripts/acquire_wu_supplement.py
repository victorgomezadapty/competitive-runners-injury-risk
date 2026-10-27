"""Acquire the three original small Wu 2026 supplementary files, never run code."""
from pathlib import Path
import json
import hashlib
import requests

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'data/complementary/wu_2026'


def main():
    FOLDER.mkdir(parents=True,exist_ok=True)
    path = FOLDER/'metadata.json'
    if not path.exists():
        r = requests.get('https://api.figshare.com/v2/articles/31368781',timeout=30)
        r.raise_for_status()
        path.write_text(json.dumps(r.json(),indent=2),encoding='utf-8')
    metadata = json.loads(path.read_text(encoding='utf-8'))
    files = metadata['files']
    if sum(f['size'] for f in files) > 20_000_000:
        raise ValueError('Supplement inventory unexpectedly large')
    raw = FOLDER/'raw'
    raw.mkdir(exist_ok=True)
    manifest = []
    for info in files:
        name = info['name']
        if Path(name).name != name:
            raise ValueError('Unsafe source filename')
        target = raw/name
        expected = info['computed_md5']
        if not target.exists() or hashlib.md5(target.read_bytes()).hexdigest() != expected:
            r = requests.get(info['download_url'],timeout=90)
            r.raise_for_status()
            if hashlib.md5(r.content).hexdigest() != expected:
                raise ValueError(f'Publisher checksum mismatch: {name}')
            target.write_bytes(r.content)
        manifest.append({'filename':name,'bytes':target.stat().st_size,'publisher_md5':expected,
                         'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'url':info['download_url']})
        print(name,target.stat().st_size,flush=True)
    output = {'dataset_id':'wu_2026_supplement','doi':'10.17028/rd.lboro.31368781',
              'article_doi':'10.1038/s41746-026-02413-y','license':metadata['license'],
              'files':manifest,'scope':'Separate runner cohort; processed supplement; not pooled with Lovdal'}
    (FOLDER/'source_manifest.json').write_text(json.dumps(output,indent=2),encoding='utf-8')


if __name__=='__main__':
    main()
