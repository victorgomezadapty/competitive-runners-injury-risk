"""Acquire only the small original SoccerMon subjective archive, never GPS files."""
from pathlib import Path
import hashlib
import json
import requests
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'data/complementary/soccermon'
URL = 'https://zenodo.org/records/10033832/files/subjective.zip?download=1'
EXPECTED_MD5 = 'a3e86aeca611f77c9331a535eae00bf7'


def main():
    raw = FOLDER/'raw'
    raw.mkdir(parents=True, exist_ok=True)
    path = raw/'subjective.zip'
    if not path.exists() or hashlib.md5(path.read_bytes()).hexdigest() != EXPECTED_MD5:
        r = requests.get(URL, timeout=60, stream=True)
        r.raise_for_status()
        content = bytearray()
        for chunk in r.iter_content(65536):
            content.extend(chunk)
            if len(content) > 2_000_000:
                raise ValueError('Archive unexpectedly large; do not fetch GPS files')
        if hashlib.md5(content).hexdigest() != EXPECTED_MD5:
            raise ValueError('SoccerMon publisher checksum mismatch')
        path.write_bytes(content)
    metadata = {}
    try:
        r = requests.get('https://zenodo.org/api/records/10033832', timeout=25)
        r.raise_for_status()
        metadata = r.json()
        (raw/'zenodo_metadata.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
    except requests.RequestException as exc:
        metadata = {'metadata_access_error':str(exc)}
    with zipfile.ZipFile(path) as archive:
        inventory = [{'member':i.filename,'uncompressed_bytes':i.file_size,'compressed_bytes':i.compress_size}
                     for i in archive.infolist() if not i.is_dir()]
        for member in inventory[:15]:
            print(member, flush=True)
    manifest = {'dataset_id':'soccermon_subjective','doi':'10.5281/zenodo.10033832',
                'source_record':'https://zenodo.org/records/10033832','download_url':URL,
                'filename':'subjective.zip','bytes':path.stat().st_size,
                'publisher_md5':EXPECTED_MD5,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'license_metadata':metadata.get('metadata',{}).get('license'),
                'inventory':inventory,'scope':'Separate elite women soccer cohort; subjective archive only; no join to runner identities'}
    (FOLDER/'source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Archive members:',len(inventory),'License:',manifest['license_metadata'], flush=True)


if __name__ == '__main__':
    main()
