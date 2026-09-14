#!/usr/bin/env python3
"""Apply the shared theme to current and newly generated public HTML pages."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent / 'site'
LINK = '<link rel="stylesheet" href="/css/piste-theme.css?v=20260914-1">'

def apply_theme(root=ROOT):
    count = 0
    for path in root.rglob('*.html'):
        s = path.read_text(encoding='utf-8')
        if '</head>' not in s or '<body' not in s:
            continue
        original = s
        s = re.sub(r'<link\b[^>]*href=[\"\']/css/piste-theme\.css[^\"\']*[\"\'][^>]*>\s*', '', s)
        s = s.replace('</head>', LINK + '\n</head>', 1)
        def body(m):
            tag = m[0]
            if re.search(r'\bclass=', tag):
                return re.sub(r'class=([\"\'])(.*?)\1', lambda c: 'class=' + c[1] + ' '.join(dict.fromkeys(c[2].split() + ['piste-theme'])) + c[1], tag, count=1)
            return tag[:-1] + ' class="piste-theme">'
        s = re.sub(r'<body\b[^>]*>', body, s, count=1)
        if s != original:
            path.write_text(s, encoding='utf-8')
            count += 1
    return count

if __name__ == '__main__':
    print(f'Theme applied: {apply_theme()} pages')
