#!/usr/bin/env python3
"""Build the HTML-only M-002 reader using the actual M-001 reader shell.

No PDF is claimed or linked until a companion PDF exists. This build uses only
the Python standard library and preserves the shared reader CSS and scripts.
"""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/assurance-record-v0-1.json'
TEMPLATE = ROOT / 'methods/ai-assurance-method-v0-1/index.html'
OUTPUT = ROOT / 'methods/assurance-record-v0-1/index.html'


def inline(text):
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html.escape(text))


def block(item):
    kind = item['type']
    if kind in ('p', 'h3'):
        return f'<{kind}>{inline(item["text"])}</{kind}>'
    if kind == 'ul':
        return '<ul>\n' + '\n'.join(f'<li>{inline(s)}</li>' for s in item['items']) + '\n</ul>'
    if kind == 'definition':
        return ('<div class="method-definition"><strong>' + inline(item['term'])
                + '</strong><p>' + inline(item['text']) + '</p></div>')
    raise ValueError(f'Unsupported block: {kind}')


def replace(pattern, replacement, text, count=1):
    result, found = re.subn(pattern, lambda _: replacement, text, flags=re.S)
    if found != count:
        raise ValueError(f'M-001 template changed: expected {count} matches for {pattern}, got {found}')
    return result


def build_html(data):
    meta = data['metadata']
    page = TEMPLATE.read_text()
    graph = json.loads(re.search(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', page, re.S)[1])
    old_url = 'https://papers.norynthe.com/methods/ai-assurance-method-v0-1/'
    old_title = 'Norynthe AI Assurance Method v0.1'
    # Replace only the shell metadata before inserting M-002's own content.
    page = page.replace(old_url, meta['canonicalUrl']).replace(old_title, html.escape(meta['title']))
    page = page.replace('A preliminary institutional method for evidence-bound evaluation of AI systems.', html.escape(meta['subtitle']))
    page = page.replace('Series M-001', meta['seriesCode']).replace('Published method', meta['status'])
    page = page.replace('July 30, 2026', meta['displayDate']).replace('2026-07-30', meta['datePublished'])
    page = page.replace('The Norynthe Papers - AI Assurance Method', 'The Norynthe Papers')
    page = page.replace('Skip to method', 'Skip to framework').replace('Method contents', 'Framework contents')
    page = replace(r'\s*<meta name="citation_pdf_url"[^>]+>', '', page)
    # A month is the source's full date precision; do not invent an issue day.
    page = replace(r'\s*<meta property="article:published_time"[^>]+>', '', page)
    page = replace(r'<a\s+class="reader-download".*?</a>',
                   '<a class="reader-download" href="/methods/ai-assurance-method-v0-1/">Method v0.1</a>', page)
    page = replace(r'<a\s+href="[^"]+"\s+download.*?>PDF</a>',
                   '<a href="/methods/ai-assurance-method-v0-1/">Method v0.1</a>', page)
    graph = json.loads(json.dumps(graph).replace(old_url, meta['canonicalUrl']).replace(old_title, meta['title']))
    article = next(x for x in graph['@graph'] if x['@type'] == 'ScholarlyArticle')
    article.update(alternativeHeadline=meta['subtitle'], description=re.sub(r'\*\*', '', data['abstract'][0]),
                   datePublished=meta['datePublished'], version=meta['version'])
    article.pop('encoding')
    article['citation'] = old_url
    page = replace(r'<script type="application/ld\+json">.*?</script>',
                   '<script type="application/ld+json">\n' + json.dumps(graph, indent=2) + '\n  </script>', page)
    toc_items = [('abstract', 'Abstract', 'toc-book'), ('principles', 'Operating principles', 'toc-book')]
    toc_items += [(s['id'], s['title'], 'toc-chapter') for s in data['sections']]
    toc_items += [('citation', 'Citation', 'toc-book')]
    toc = '<ol>\n' + '\n'.join(f'<li class="{c}"><a href="#{i}">{html.escape(t)}</a></li>' for i, t, c in toc_items) + '\n</ol>'
    page = replace(r'(?<=<summary>Contents</summary>)\s*<ol>.*?</ol>', '\n' + toc, page)
    page = replace(r'(?<=<span class="reader-toc-title">Contents</span>)\s*<ol>.*?</ol>', '\n' + toc, page)
    content = ['<section class="method-section" id="abstract"><h2 class="front-heading">Abstract</h2>']
    content += [block({'type': 'p', 'text': s}) for s in data['abstract']]
    content += ['</section>', '<section class="method-section method-principles" id="principles"><h2 class="book-heading">Operating principles</h2>', block({'type': 'ul', 'items': data['principles']}), '</section>']
    for section in data['sections']:
        content += [f'<section class="method-section" id="{section["id"]}"><h2 class="chapter-heading">{html.escape(section["title"])}</h2>']
        content += [block(b) for b in section['blocks']]
        content += ['</section>']
    content += ['<section class="method-section method-citation" id="citation"><h2 class="book-heading">Citation</h2>',
                f'<p id="method-citation-text">{html.escape(meta["citation"])}</p>',
                '<button class="copy-button" type="button" data-copy-target="method-citation-text" aria-describedby="method-copy-status">Copy citation</button>',
                '<span class="copy-status" id="method-copy-status" role="status" aria-live="polite"></span></section>',
                f'<p class="reader-endnote">End of {html.escape(meta["title"])} · {meta["displayDate"]}</p>']
    return replace(r'(<article class="reader-article method-article" id="method-text">).*?</article>',
                   '<article class="reader-article method-article" id="method-text">\n' + '\n'.join(content) + '\n</article>', page)


if __name__ == '__main__':
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_html(json.loads(SOURCE.read_text())), encoding='utf-8')
    print(f'Built {OUTPUT.relative_to(ROOT)}')
