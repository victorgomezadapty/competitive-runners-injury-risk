"""Execute an explicit range of authored notebooks, never upstream replication code."""
import argparse
from pathlib import Path
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--start',type=int,default=1)
    parser.add_argument('--end',type=int,default=4)
    args=parser.parse_args()
    for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
        if not args.start<=int(path.name[:2])<=args.end:
            continue
        notebook = nbformat.read(path, as_version=4)
        if not any(c.cell_type=='code' for c in notebook.cells):
            continue
        client = NotebookClient(notebook, timeout=180, kernel_name='python3',
                                resources={'metadata': {'path': str(ROOT)}})
        client.execute()
        nbformat.write(notebook, path)
        print(f'Executed {path.name}', flush=True)


if __name__ == '__main__':
    main()
