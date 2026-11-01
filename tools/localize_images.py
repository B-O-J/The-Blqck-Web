#!/usr/bin/env python3
"""Download every remote background photo used by the pages and relink the pages to local copies.

Run from the project root:   python3 tools/localize_images.py
Add --dry-run to just list what would be downloaded.
Needs only Python 3. If Pillow is installed (pip install pillow) it also makes
smaller 800px copies, and pages pick the right size automatically.
"""
import re, sys, glob, os, urllib.request
from urllib.parse import urlparse

DRY = '--dry-run' in sys.argv
OUT = 'Images/chapters'
IMG = re.compile(r'<img src="(https://[^"]+)"[^>]*?alt=""[^>]*>')

try: from PIL import Image
except ImportError: Image = None

def big(url):  # ask Unsplash for a 1600px version; leave other hosts as they are
    url = url.replace('&amp;', '&')
    return re.sub(r'w=\d+', 'w=1600', url) if 'unsplash' in url else url

os.makedirs(OUT, exist_ok=True)
for page in sorted(glob.glob('*.html')):
    html = open(page, encoding='utf-8').read()
    m = IMG.search(html)
    if not m: continue
    stem = re.sub(r'[^a-z0-9]+', '-', os.path.splitext(page)[0].lower()).strip('-')
    full, small = f'{OUT}/{stem}.jpg', f'{OUT}/{stem}-800.jpg'
    print(f'{page:28} <- {urlparse(m.group(1)).netloc}')
    if DRY: continue
    req = urllib.request.Request(big(m.group(1)), headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r, open(full, 'wb') as f: f.write(r.read())
    tag = f'<img src="{full}" alt="" fetchpriority="high" decoding="async">'
    if Image:
        im = Image.open(full).convert('RGB'); im.thumbnail((1600, 1600)); im.save(full, quality=72, optimize=True, progressive=True)
        im.thumbnail((800, 800)); im.save(small, quality=70, optimize=True, progressive=True)
        tag = f'<img src="{full}" srcset="{small} 800w, {full} 1600w" sizes="100vw" alt="" fetchpriority="high" decoding="async">'
    open(page, 'w', encoding='utf-8').write(html.replace(m.group(0), tag))
print('Dry run only.' if DRY else f'Done. Photos are in {OUT}/ and every page now points to them.')
