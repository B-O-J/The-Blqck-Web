#!/usr/bin/env python3
"""Download every remote background photo used by the pages and relink the pages to local copies.

Run from the project root:   python3 tools/localize_images.py
Add --dry-run to just list what would be downloaded.

For each page it tries the current photo first, then any replacements listed in REPLACEMENTS
below, and uses the first one that downloads. If a photo already exists as
Images/chapters/<page>.jpg (for example one you saved yourself) it is used as-is.
Needs only Python 3. With Pillow installed (pip install pillow) it also compresses the
photos and makes 800px copies for phones.
"""
import re, sys, glob, os, urllib.request
from urllib.parse import urlparse

DRY = '--dry-run' in sys.argv
OUT = 'Images/chapters'
IMG = re.compile(r'<img src="(https://[^"]+)"[^>]*?alt=""[^>]*>')

px = lambda i: f'https://images.pexels.com/photos/{i}/pexels-photo-{i}.jpeg?auto=compress&cs=tinysrgb&w=1600'
us = lambda i: f'https://unsplash.com/photos/{i}/download?force=true&w=1600'

# Free-licence replacements (Pexels licence / Unsplash licence), tried in order if the current photo is gone.
REPLACEMENTS = {
    'grief':   [us('URrQeK63qZI'), us('4UbeFRfl7qQ')],   # lone tree in fog, quiet and still
    'journey': [px(1668899), us('x3y9RsFYzF0'), us('YAuC7ai8cEU')],  # road vanishing into mist
    'live':    [px(2100002), px(1167358)],               # sunrays across an open field
}

try: from PIL import Image
except ImportError: Image = None

def big(url):  # ask Unsplash CDN links for a 1600px version; leave other links as they are
    url = url.replace('&amp;', '&')
    return re.sub(r'w=\d+', 'w=1600', url) if 'images.unsplash' in url else url

def fetch(url, dest):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
        if not r.headers.get('Content-Type', '').startswith('image/') or len(data) < 10_000:
            raise ValueError('not an image')
    open(dest, 'wb').write(data)

os.makedirs(OUT, exist_ok=True)
for page in sorted(glob.glob('*.html')):
    html = open(page, encoding='utf-8').read()
    m = IMG.search(html)
    if not m: continue
    stem = re.sub(r'[^a-z0-9]+', '-', os.path.splitext(page)[0].lower()).strip('-')
    full, small = f'{OUT}/{stem}.jpg', f'{OUT}/{stem}-800.jpg'
    print(f'{page:28} <- {urlparse(m.group(1)).netloc}')
    if DRY: continue
    if not os.path.exists(full):
        for url in [big(m.group(1))] + REPLACEMENTS.get(stem, []):
            try: fetch(url, full); print(f'  saved from {urlparse(url).netloc}'); break
            except Exception as e: print(f'  could not use {urlparse(url).netloc} ({e})')
        else:
            print(f'  FAILED. Save a photo as {full} and run again.'); continue
    tag = f'<img src="{full}" alt="" fetchpriority="high" decoding="async">'
    if Image:
        im = Image.open(full).convert('RGB'); im.thumbnail((1600, 1600)); im.save(full, quality=72, optimize=True, progressive=True)
        im.thumbnail((800, 800)); im.save(small, quality=70, optimize=True, progressive=True)
        tag = f'<img src="{full}" srcset="{small} 800w, {full} 1600w" sizes="100vw" alt="" fetchpriority="high" decoding="async">'
    open(page, 'w', encoding='utf-8').write(html.replace(m.group(0), tag))
print('Dry run only.' if DRY else f'Done. Photos are in {OUT}/ and every page now points to them.')
