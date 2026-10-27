"""Download original Dataverse bytes and verify publisher checksums (no mirror)."""
from pathlib import Path
import hashlib
import json
import requests

ROOT = Path(__file__).resolve().parents[1]
API = "https://dataverse.nl/api"
DOI = "doi:10.34894/UWU9PV"


def main():
    raw = ROOT / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    response = requests.get(f"{API}/datasets/:persistentId/", params={"persistentId": DOI}, timeout=90)
    response.raise_for_status()
    metadata = response.json()
    version = metadata["data"]["latestVersion"]
    version_name = f"{version['versionNumber']}.{version['versionMinorNumber']}"
    manifest_path = ROOT / "data/source_manifest.json"
    frozen = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else None
    if frozen and frozen['version'] != version_name:
        raise ValueError(f"Source changed from frozen version {frozen['version']} to {version_name}; review before updating")
    frozen_files = {f['filename']: f for f in frozen['files']} if frozen else {}
    if frozen and set(frozen_files) != {f['dataFile']['filename'] for f in version['files']}:
        raise ValueError('Source file inventory changed; review before updating')
    (raw / "dataverse_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    manifest = []
    for entry in version["files"]:
        info = entry["dataFile"]
        name = info["filename"]
        if Path(name).name != name:
            raise ValueError("Unsafe upstream filename")
        path = raw / name
        checksum = info.get("checksum", {})
        if name in frozen_files and checksum != frozen_files[name]['publisher_checksum']:
            raise ValueError(f'Publisher checksum differs from frozen release: {name}')
        algorithm = checksum.get("type", "MD5").lower().replace("-", "")
        expected = checksum.get("value")
        if not path.exists() or (expected and hashlib.new(algorithm, path.read_bytes()).hexdigest() != expected):
            download = requests.get(f"{API}/access/datafile/{info['id']}", params={"format": "original"}, timeout=180)
            download.raise_for_status()
            content = download.content
            if expected and hashlib.new(algorithm, content).hexdigest() != expected:
                raise ValueError(f"Publisher checksum mismatch: {name}")
            path.write_bytes(content)
        content = path.read_bytes()
        if name in frozen_files and hashlib.sha256(content).hexdigest() != frozen_files[name]['sha256']:
            raise ValueError(f'Content differs from frozen SHA-256: {name}')
        manifest.append({"filename": name, "file_id": info["id"], "bytes": len(content),
                         "sha256": hashlib.sha256(content).hexdigest(), "publisher_checksum": checksum,
                         "url": f"{API}/access/datafile/{info['id']}?format=original"})
        print(name, len(content), flush=True)
    output = {"doi": DOI, "version": version_name,
              "release_time": version["releaseTime"], "license": version.get("license"), "files": manifest}
    (ROOT / "data/source_manifest.json").write_text(json.dumps(output, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
