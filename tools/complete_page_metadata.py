"""Complete metadata and intrinsic dimensions without rewriting page layout."""
from pathlib import Path
from html import escape, unescape
import re
from PIL import Image

def complete(source: str, page: Path, root: Path) -> str:
    def dimensions(match):
        tag=match[0]
        if re.search(r'\bwidth="\d+"',tag) and re.search(r'\bheight="\d+"',tag): return tag
        src=re.search(r'\bsrc="([^"]+)"',tag)
        if not src or '://' in src[1] or src[1].startswith('data:'): return tag
        image=(root/src[1].lstrip('/') if src[1].startswith('/') else page.parent/src[1]).resolve()
        if not image.is_file(): return tag
        with Image.open(image) as im: width,height=im.size
        tag=re.sub(r'\s(?:width|height)="[^"]*"','',tag)
        if 'logo.' in src[1]:
            if 'style="' in tag: tag=tag.replace('style="','style="width:auto;max-width:100%;',1)
            else: tag=tag[:-1]+' style="width:auto;max-width:100%">'
        return tag[:-1]+f' width="{width}" height="{height}">'
    source=re.sub(r'<img\b[^>]*>',dimensions,source)
    if page.name in ('privacy.html','terms.html','tokushoho.html'):
        title=re.search(r'<title>(.*?)</title>',source,re.S)
        desc=re.search(r'<meta\s+name="description"\s+content="([^"]*)"',source)
        canonical=re.search(r'<link\s+rel="canonical"\s+href="([^"]+)"',source)
        if title and desc and canonical:
            tags=[]
            values={'og:type':'website','og:title':unescape(title[1]),'og:description':unescape(desc[1]),'og:url':unescape(canonical[1]),'og:image':'https://www.piste-ai.com/images/ogp.jpg'}
            for key,value in values.items():
                if f'property="{key}"' not in source: tags.append(f'<meta property="{key}" content="{escape(value,quote=True)}">')
            if 'name="twitter:card"' not in source: tags.append('<meta name="twitter:card" content="summary_large_image">')
            source=source.replace('</head>','\n'.join(tags)+'\n</head>')
    return source
