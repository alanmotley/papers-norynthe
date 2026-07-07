#!/usr/bin/env python3
"""Build the semantic Volume I reader from the canonical publication DOCX."""

from __future__ import annotations

import html
import re
import unicodedata
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / (
    "The Norynthe Papers - Volume I - On Trust, Inference, and Intelligence "
    "- First Editorial Edition.docx"
)
OUTPUT = ROOT / "volume-i" / "index.html"
PDF_URL = "/downloads/the-norynthe-papers-volume-i.pdf"

URL_RE = re.compile(r"https?://[^\s<]+")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "section"


def linkify(value: str) -> str:
    output: list[str] = []
    cursor = 0
    for match in URL_RE.finditer(value):
        raw = match.group(0)
        trailing = ""
        while raw and raw[-1] in ".,;:)]:":
            trailing = raw[-1] + trailing
            raw = raw[:-1]
        output.append(html.escape(value[cursor : match.start()]))
        output.append(
            f'<a href="{html.escape(raw, quote=True)}">{html.escape(raw)}</a>'
        )
        output.append(html.escape(trailing))
        cursor = match.end()
    output.append(html.escape(value[cursor:]))
    return "".join(output)


def run_html(run_element, *, allow_linkify: bool = True) -> str:
    pieces: list[str] = []
    for node in run_element.iterchildren():
        if node.tag == qn("w:t"):
            pieces.append(node.text or "")
        elif node.tag == qn("w:tab"):
            pieces.append(" ")
        elif node.tag == qn("w:br"):
            pieces.append("\n")
    value = "".join(pieces)
    if not value:
        return ""

    rendered = linkify(value) if allow_linkify else html.escape(value)
    properties = run_element.find(qn("w:rPr"))
    if properties is not None:
        if properties.find(qn("w:i")) is not None:
            rendered = f"<em>{rendered}</em>"
        if properties.find(qn("w:b")) is not None:
            rendered = f"<strong>{rendered}</strong>"
        vertical = properties.find(qn("w:vertAlign"))
        if vertical is not None and vertical.get(qn("w:val")) == "superscript":
            rendered = f"<sup>{rendered}</sup>"
    return rendered.replace("\n", "<br>")


def paragraph_html(document: Document, paragraph) -> str:
    output: list[str] = []
    for child in paragraph._p.iterchildren():
        if child.tag == qn("w:r"):
            output.append(run_html(child))
        elif child.tag == qn("w:hyperlink"):
            relation_id = child.get(qn("r:id"))
            href = ""
            if relation_id and relation_id in document.part.rels:
                href = document.part.rels[relation_id].target_ref
            content = "".join(run_html(run, allow_linkify=False) for run in child.iterchildren() if run.tag == qn("w:r"))
            if href:
                output.append(f'<a href="{html.escape(href, quote=True)}">{content}</a>')
            else:
                output.append(content)
    return "".join(output) or linkify(paragraph.text)


def heading_id(text: str, seen: dict[str, int]) -> str:
    base = slugify(text)
    seen[base] = seen.get(base, 0) + 1
    return base if seen[base] == 1 else f"{base}-{seen[base]}"


def build_content(document: Document) -> tuple[str, str]:
    paragraphs = document.paragraphs
    selected = [paragraphs[8], paragraphs[9], *paragraphs[56:]]
    seen: dict[str, int] = {}
    toc: list[tuple[str, str, str]] = []
    content: list[str] = []
    list_type: str | None = None

    def close_list() -> None:
        nonlocal list_type
        if list_type:
            content.append(f"</{list_type}>")
            list_type = None

    for paragraph in selected:
        text = paragraph.text.strip()
        if not text:
            close_list()
            continue

        style = paragraph.style.name
        inline = paragraph_html(document, paragraph)

        if style in {"List Bullet", "List Number"}:
            required = "ul" if style == "List Bullet" else "ol"
            if list_type != required:
                close_list()
                content.append(f"<{required}>")
                list_type = required
            content.append(f"<li>{inline}</li>")
            continue

        close_list()

        if style == "Norynthe Front" or (style == "Heading 2" and text == "Epigraph"):
            identifier = heading_id(text, seen)
            content.append(f'<h2 class="front-heading" id="{identifier}">{inline}</h2>')
            toc.append(("front", identifier, text))
        elif style == "Norynthe Book":
            identifier = heading_id(text, seen)
            content.append(f'<h2 class="book-heading" id="{identifier}">{inline}</h2>')
            toc.append(("book", identifier, text))
        elif style == "Heading 1":
            identifier = heading_id(text, seen)
            content.append(f'<h2 class="chapter-heading" id="{identifier}">{inline}</h2>')
            toc.append(("chapter", identifier, text))
        elif style == "Heading 2":
            identifier = heading_id(text, seen)
            content.append(f'<h3 id="{identifier}">{inline}</h3>')
        elif style == "Heading 3":
            identifier = heading_id(text, seen)
            content.append(f'<h4 id="{identifier}">{inline}</h4>')
        elif style == "Norynthe Quote":
            quote_class = " cycle-quote" if "OBSERVATION" in text else ""
            content.append(f'<blockquote class="{quote_class.strip()}">{inline}</blockquote>')
        elif style == "Norynthe Article":
            content.append(f'<p class="article-text">{inline}</p>')
        elif style == "Norynthe Source":
            content.append(f'<p class="source-text">{inline}</p>')
        else:
            content.append(f"<p>{inline}</p>")

    close_list()

    toc_items = "\n".join(
        f'<li class="toc-{kind}"><a href="#{identifier}">{html.escape(label)}</a></li>'
        for kind, identifier, label in toc
    )
    return "\n".join(content), toc_items


def build_page(content: str, toc_items: str) -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Volume I — On Trust, Inference, and Intelligence | The Norynthe Papers</title>
  <meta name="description" content="Read Volume I of The Norynthe Papers: On Trust, Inference, and Intelligence, the founding treatise on trustworthy inference.">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#0f1115">
  <meta name="author" content="Alan Motley">
  <meta name="citation_title" content="The Norynthe Papers: Volume I — On Trust, Inference, and Intelligence">
  <meta name="citation_author" content="Alan Motley">
  <meta name="citation_publication_date" content="2026">
  <meta name="citation_publisher" content="Norynthe">
  <meta name="citation_pdf_url" content="https://papers.norynthe.com/downloads/the-norynthe-papers-volume-i.pdf">
  <link rel="canonical" href="https://papers.norynthe.com/volume-i/">

  <meta property="og:type" content="article">
  <meta property="og:site_name" content="The Norynthe Papers">
  <meta property="og:title" content="Volume I — On Trust, Inference, and Intelligence">
  <meta property="og:description" content="The founding treatise of Norynthe and the science of trustworthy inference.">
  <meta property="og:url" content="https://papers.norynthe.com/volume-i/">
  <meta property="og:image" content="https://papers.norynthe.com/papers-social-card.png">
  <meta property="og:image:alt" content="The Norynthe Papers — On Trust, Inference, and Intelligence">
  <meta property="article:published_time" content="2026">
  <meta property="article:author" content="Alan Motley">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Volume I — On Trust, Inference, and Intelligence">
  <meta name="twitter:description" content="The founding treatise of Norynthe and the science of trustworthy inference.">
  <meta name="twitter:image" content="https://papers.norynthe.com/papers-social-card.png">

  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="apple-touch-icon" href="/norynthe-icon-180.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="stylesheet" href="/papers.css">

  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@graph": [
      {{
        "@type": "Organization",
        "@id": "https://www.norynthe.com/#organization",
        "name": "Norynthe",
        "url": "https://www.norynthe.com/"
      }},
      {{
        "@type": "Book",
        "@id": "https://papers.norynthe.com/volume-i/#book",
        "url": "https://papers.norynthe.com/volume-i/",
        "name": "The Norynthe Papers, Volume I: On Trust, Inference, and Intelligence",
        "alternativeHeadline": "A Founding Treatise",
        "description": "The founding treatise of Norynthe and the science of trustworthy inference.",
        "bookEdition": "First Editorial Edition",
        "datePublished": "2026",
        "author": {{
          "@type": "Person",
          "@id": "https://www.alanmotley.com/#person",
          "name": "Alan Motley"
        }},
        "publisher": {{ "@id": "https://www.norynthe.com/#organization" }},
        "isPartOf": {{ "@id": "https://papers.norynthe.com/#series" }},
        "inLanguage": "en",
        "encoding": {{
          "@type": "MediaObject",
          "contentUrl": "https://papers.norynthe.com/downloads/the-norynthe-papers-volume-i.pdf",
          "encodingFormat": "application/pdf"
        }}
      }},
      {{
        "@type": "BreadcrumbList",
        "@id": "https://papers.norynthe.com/volume-i/#breadcrumb",
        "itemListElement": [
          {{
            "@type": "ListItem",
            "position": 1,
            "name": "The Norynthe Papers",
            "item": "https://papers.norynthe.com/"
          }},
          {{
            "@type": "ListItem",
            "position": 2,
            "name": "Volume I — On Trust, Inference, and Intelligence",
            "item": "https://papers.norynthe.com/volume-i/"
          }}
        ]
      }},
      {{
        "@type": "WebPage",
        "@id": "https://papers.norynthe.com/volume-i/#webpage",
        "url": "https://papers.norynthe.com/volume-i/",
        "name": "Volume I — On Trust, Inference, and Intelligence",
        "mainEntity": {{ "@id": "https://papers.norynthe.com/volume-i/#book" }},
        "breadcrumb": {{ "@id": "https://papers.norynthe.com/volume-i/#breadcrumb" }},
        "isPartOf": {{ "@id": "https://papers.norynthe.com/#website" }},
        "inLanguage": "en"
      }}
    ]
  }}
  </script>
</head>
<body class="reader-body" data-analytics-page="The Norynthe Papers — Volume I">
  <a class="skip-link" href="#volume-text">Skip to Volume I</a>
  <header class="reader-header">
    <div class="site-shell reader-header-inner">
      <a class="reader-back" href="/">The Norynthe Papers</a>
      <a class="reader-download" href="{PDF_URL}" download>Download PDF</a>
    </div>
  </header>

  <main>
    <section class="reader-masthead" aria-labelledby="volume-title">
      <div class="site-shell reader-masthead-grid">
        <div>
          <p class="reader-kicker">The Norynthe Papers · Volume I</p>
          <h1 id="volume-title">On Trust, Inference, and Intelligence</h1>
          <p class="reader-deck">A founding treatise on trustworthy inference as an object of science.</p>
        </div>
        <div class="reader-meta" aria-label="Publication metadata">
          <span>First Editorial Edition</span>
          <span>Alan Motley</span>
          <span>Norynthe · 2026</span>
        </div>
      </div>
    </section>

    <details class="mobile-toc">
      <summary>Contents</summary>
      <ol>
        {toc_items}
      </ol>
    </details>

    <div class="reader-layout">
      <nav class="reader-toc" aria-label="Volume I contents">
        <span class="reader-toc-title">Contents</span>
        <ol>
          {toc_items}
        </ol>
      </nav>

      <article class="reader-article" id="volume-text">
        {content}
        <p class="reader-endnote">End of the First Editorial Edition · 2026</p>
      </article>
    </div>
  </main>

  <footer class="site-footer">
    <div class="site-shell footer-grid">
      <div>
        <span class="footer-institution">Norynthe</span>
        <span class="footer-series">The Norynthe Papers</span>
      </div>
      <p>Trustworthy inference as an object of science.</p>
      <div class="footer-links">
        <a href="/">Papers</a>
        <a href="{PDF_URL}" download>PDF</a>
        <a href="https://www.norynthe.com/">Norynthe Home</a>
      </div>
      <p class="copyright">Copyright © 2026 Norynthe.</p>
    </div>
  </footer>

  <script src="https://www.norynthe.com/norynthe-analytics.js" defer></script>
</body>
</html>
'''


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing canonical DOCX: {SOURCE}")
    document = Document(SOURCE)
    content, toc_items = build_content(document)
    page = build_page(content, toc_items)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(page):,} characters)")


if __name__ == "__main__":
    main()
