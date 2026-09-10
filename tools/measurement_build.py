#!/usr/bin/env python3
"""Run after SEO generation and before deployment; keep one production-only loader."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent / 'site'
def normalize(page):
    source = page.read_text()
    def script(match):
        block = match.group()
        if 'application/ld+json' in block:
            return block
        if any(key in block for key in ('googletagmanager.com/gtag/js', "gtag('config'", 'clarity.ms/tag/', "'line_friend_add'", '/js/analytics.js')):
            return ''
        return block
    source = re.sub(r'<script\b[^>]*>[\s\S]*?</script>', script, source, flags=re.I)
    source = source.replace('</head>', '  <script defer src="/js/analytics.js"></script>\n</head>')
    if 'class="contact-form' in source and 'name="website"' not in source:
        source = source.replace('<form class="contact-form fade-in" id="contactForm">', '<form class="contact-form fade-in" id="contactForm">\n<div hidden aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off"></label></div>')
    page.write_text(source)

if __name__ == '__main__':
    pages = list(ROOT.rglob('*.html'))
    for page in pages:
        if '.netlify' not in page.parts:
            normalize(page)
    print(f'Measurement loader normalized: {len(pages)} pages')
