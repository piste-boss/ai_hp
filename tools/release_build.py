#!/usr/bin/env python3
"""Create a deployable snapshot containing public assets only, then normalize it."""
from pathlib import Path
import shutil
import re
import json
import hashlib
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from urllib.parse import urlsplit
import measurement_build
from complete_page_metadata import complete

PROJECT = Path(__file__).resolve().parent.parent
SOURCE = PROJECT / 'site'
DEST = PROJECT / 'audit/20260910/release/public'
PUBLIC_DIRS = ('blog', 'images', 'css', 'js', 'media')
PUBLIC_FILES = ('favicon.png', 'robots.txt', 'sitemap.xml', 'feed.xml', 'llms.txt', '_headers', '_redirects', 'efd6c518082f782431bff4f0bb33c572.txt')  # 最後は IndexNow キー

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    inputs = list(SOURCE.glob('*.html')) + [SOURCE / f for f in PUBLIC_FILES if (SOURCE / f).exists()]
    for folder in PUBLIC_DIRS:
        inputs += [p for p in (SOURCE / folder).rglob('*') if p.is_file() and not any(x.startswith('.') for x in p.relative_to(SOURCE).parts)]
    manifest = {}
    for path in inputs:
        data = path.read_bytes()
        target = DEST / path.relative_to(SOURCE)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        manifest[str(path.relative_to(SOURCE))] = hashlib.sha256(data).hexdigest()
    # Only remove stale files in this generated directory.
    for path in DEST.rglob('*'):
        if path.is_file() and str(path.relative_to(DEST)) not in manifest:
            path.unlink()
    for path in DEST.rglob('*.html'):
        s = path.read_text()
        if path.parent.name == 'blog' and not path.name.startswith('category-'):
            s = re.sub(r'(?:70|110|120)社以上のAI導入(?:コンサルティング)?実績', 'AI導入の支援経験', s)
            s = re.sub(r'(?:70|110|120)社以上の導入実績', 'AI導入の支援経験', s)
        if path.name == 'ai-accounting-automation.html':
            s = re.sub(r'("dateModified"\s*:\s*")[^"]+', r'\g<1>2026-09-10T09:00:00+09:00', s)
        if path.name in ('index.html', 'training.html', 'aichi.html'):
            s = s.replace('経費助成75%（中小企業／人材育成支援コース）', '経費助成75%が適用される場合（コース・対象要件の確認が必要）')
            s = s.replace('賃金助成（1,000円/h）を併用すると、自己負担はさらに軽減されます。', '賃金助成の対象となる場合もあります。適用条件・金額は最新の制度をご確認ください。')
        s = re.sub(r'(href=["\'](?:https://www\.piste-ai\.com)?(?:\.\./|\./|/)?(?:index\.html)?#)(service|about|consulting)(["\'])',
            lambda m: m[1] + {'service':'services', 'about':'profile', 'consulting':'services'}[m[2]] + m[3], s)
        s = s.replace('href="#s6"', 'href="#cta"') if path.name == 'ai-accounting-automation.html' else s
        # Match Netlify's public URLs and Google's existing extensionless index.
        s = re.sub(r'https://www\.piste-ai\.com/([^\s"<>]*?)\.html(?=[#?"<\s]|$)',
            lambda m: 'https://www.piste-ai.com/' + (m[1][:-5] if m[1].endswith('index') else m[1]), s)
        def local_link(m):
            value = m[2]
            if urlsplit(value).scheme or value.startswith('//'): return m[0]
            value = re.sub(r'(^|/)index\.html(?=[#?]|$)', lambda n: n[1] or './', value)
            value = re.sub(r'\.html(?=[#?]|$)', '', value)
            if not value: value = './'
            return m[1] + value + m[3]
        s = re.sub(r'(href=["\'])([^"\']+)(["\'])', local_link, s)
        if path.parent.name == 'blog' and path.name != 'index.html' and not path.name.startswith('category-') and '/css/blog-accessibility.css' not in s:
            s = s.replace('</head>', '<link rel="stylesheet" href="/css/blog-accessibility.css">\n</head>')
        if path.parent.name == 'blog':
            def prioritize_image(match):
                tag = match[0]
                if f'/images/blog-{path.stem}.webp' not in tag: return tag
                tag = re.sub(r'\sloading="[^"]*"', '', tag)
                tag = re.sub(r'\sfetchpriority="[^"]*"', '', tag)
                return tag[:-1] + ' loading="eager" fetchpriority="high">'
            s = re.sub(r'<img\b[^>]*>', prioritize_image, s)
        path.write_text(complete(s, path, DEST))
        measurement_build.normalize(path)
    redirects = []
    for path in sorted(DEST.rglob('*.html')):
        if path.name == '404.html': continue
        relative = '/' + str(path.relative_to(DEST))
        target = relative[:-10] if relative.endswith('index.html') else relative[:-5]
        redirects.append(f'{relative} {target or "/"} 301!')
    (DEST / '_redirects').write_text('\n'.join(redirects) + '\n')
    for name in ('feed.xml', 'llms.txt'):
        path = DEST / name
        if path.exists():
            s = re.sub(r'https://www\.piste-ai\.com/([^\s"<>)]*?)\.html(?=[#?"<\s)]|$)',
                lambda m: 'https://www.piste-ai.com/' + (m[1][:-5] if m[1].endswith('index') else m[1]), path.read_text())
            path.write_text(s)
    # Keep asset changes visible immediately across successive deployments.
    headers = DEST / '_headers'
    h = headers.read_text() if headers.exists() else ''
    h = h.replace('/css/*\n  Cache-Control: public, max-age=604800', '/css/*\n  Cache-Control: public, max-age=0, must-revalidate')
    h = h.replace('/js/*\n  Cache-Control: public, max-age=604800', '/js/*\n  Cache-Control: public, max-age=0, must-revalidate')
    headers.write_text(h)
    # Preserve existing lastmod values; never invent article publication dates.
    ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    previous = ET.parse(DEST / 'sitemap.xml')
    dates = {u.findtext('s:loc', namespaces=ns): u.findtext('s:lastmod', namespaces=ns) for u in previous.findall('s:url', ns)}
    dates.update({re.sub(r'\.html$', '', key): value for key, value in list(dates.items())})
    ET.register_namespace('', ns['s'])
    xml = ET.Element('{'+ns['s']+'}urlset')
    for path in sorted(DEST.rglob('*.html')):
        if path.name == '404.html': continue
        s = path.read_text()
        canonical = re.search(r'<link(?=[^>]*\brel="canonical")(?=[^>]*\bhref="([^"]+)")[^>]*>', s)
        if not canonical: raise ValueError(f'Missing canonical: {path}')
        url = canonical[1]
        item = ET.SubElement(xml, 'url')
        ET.SubElement(item, 'loc').text = url
        if dates.get(url): ET.SubElement(item, 'lastmod').text = dates[url]
    ET.ElementTree(xml).write(DEST / 'sitemap.xml', encoding='utf-8', xml_declaration=True)
    (DEST.parent / 'input-manifest.json').write_text(json.dumps(manifest, indent=2))
    changed = [str(p.relative_to(SOURCE)) for p in inputs if hashlib.sha256(p.read_bytes()).hexdigest() != manifest[str(p.relative_to(SOURCE))]]
    if changed: raise RuntimeError('Inputs changed during build; rerun: ' + ', '.join(changed))
    print(f'Release snapshot: {DEST}\nPublic pages: {len(list(DEST.rglob("*.html")))}; input files: {len(inputs)}')

if __name__ == '__main__': main()
