#!/usr/bin/env python3
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, re
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parent.parent / 'audit/20260910/release/public'
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.ids=set(); self.h1=0; self.canonical=[]; self.scripts=[]
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.add(a['id'])
        if tag=='h1': self.h1+=1
        if tag=='link' and a.get('rel')=='canonical': self.canonical.append(a.get('href'))
        if tag=='script' and 'src' in a: self.scripts.append(a['src'])
        if tag in ('a','link','img','script'): self.links.append(a.get('href',a.get('src','')))
pages={}; errors=[]; schema_count=0
for file in ROOT.rglob('*.html'):
    page=Page(); source=file.read_text(); page.feed(source); pages[file]=page
    for data in re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',source,re.S):
        try: json.loads(data); schema_count+=1
        except ValueError: errors.append(f'{file.name}: invalid JSON-LD')
for file,page in pages.items():
    label=str(file.relative_to(ROOT))
    if page.h1 != 1: errors.append(f'{label}: H1={page.h1}')
    if file.name!='404.html' and len(page.canonical)!=1: errors.append(f'{label}: canonical count')
    if page.scripts.count('/js/analytics.js')!=1: errors.append(f'{label}: measurement loader count')
    if any('googletagmanager' in x or 'clarity.ms' in x for x in page.scripts): errors.append(f'{label}: duplicate direct tag')
    for link in page.links:
        u=urlsplit(link)
        if (u.netloc and u.netloc!='www.piste-ai.com') or u.scheme not in ('','http','https'): continue
        path=unquote(u.path)
        target=(ROOT/path.lstrip('/') if path.startswith('/') else file.parent/path).resolve() if path else file
        if target.is_dir(): target=target/'index.html'
        if not target.exists() and not target.suffix: target=target.with_suffix('.html')
        if not target.exists(): errors.append(f'{label}: missing {link}')
        elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids: errors.append(f'{label}: broken anchor {link}')
ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
locations=[x.text for x in ET.parse(ROOT/'sitemap.xml').findall('s:url/s:loc',ns)]
canonical={p.canonical[0] for f,p in pages.items() if f.name!='404.html' and len(p.canonical)==1}
if set(locations)!=canonical or len(locations)!=len(canonical): errors.append('sitemap/canonical mismatch')
result={'pages':len(pages),'sitemap_urls':len(locations),'json_ld_blocks':schema_count,'errors':errors}
(ROOT.parent/'validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
