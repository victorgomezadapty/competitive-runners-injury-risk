"""Acquire methods from the official university repository, without running source code."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin
import requests

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.extend(v for k, v in attrs if k == 'href' and v and '.pdf' in v)

root = Path(__file__).resolve().parents[1] / 'docs/sources'
root.mkdir(parents=True, exist_ok=True)
url = 'https://research.rug.nl/en/publications/injury-prediction-in-competitive-runners-with-machine-learning/'
r = requests.get(url, timeout=60)
r.raise_for_status()
(root / 'publication_portal.html').write_text(r.text, encoding='utf-8')
parser = Links()
parser.feed(r.text)
print(parser.links, flush=True)
pdf = urljoin(url, parser.links[0])
# Official Pure repository endpoint for the same university document.
pdf = pdf.replace('https://research.rug.nl/files/', 'https://pure.rug.nl/ws/portalfiles/portal/')
r = requests.get(pdf, timeout=90)
r.raise_for_status()
if not r.content.startswith(b'%PDF'):
    raise ValueError('Response is not a PDF')
(root / 'original_study.pdf').write_bytes(r.content)
(root / 'paper_url.txt').write_text(pdf, encoding='utf-8')
print(len(r.content), flush=True)
