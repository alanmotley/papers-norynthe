#!/usr/bin/env python3
"""Build the Norynthe AI Assurance Method HTML and PDF artifacts."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "ai-assurance-method-v0-1.json"
HTML_OUTPUT = ROOT / "methods" / "ai-assurance-method-v0-1" / "index.html"
PDF_OUTPUT = ROOT / "downloads" / "norynthe-ai-assurance-method-v0-1.pdf"


def escape(value: str) -> str:
  return html.escape(value, quote=True)


def text_to_id(value: str) -> str:
  value = re.sub(r"^\d+\.\s*", "", value.lower())
  value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
  return value or "section"


def load_data() -> dict[str, Any]:
  return json.loads(SOURCE.read_text(encoding="utf-8"))


def render_block(block: dict[str, Any]) -> str:
  block_type = block["type"]

  if block_type == "p":
    return f"<p>{escape(block['text'])}</p>"

  if block_type == "h3":
    return f"<h3>{escape(block['text'])}</h3>"

  if block_type == "ul":
    items = "\n".join(f"<li>{escape(item)}</li>" for item in block["items"])
    return f"<ul>\n{items}\n</ul>"

  if block_type == "definition":
    return (
      '<div class="method-definition">'
      f"<strong>{escape(block['term'])}</strong>"
      f"<p>{escape(block['text'])}</p>"
      "</div>"
    )

  raise ValueError(f"Unsupported block type: {block_type}")


def render_sections(data: dict[str, Any]) -> str:
  rendered = []
  for section in data["sections"]:
    blocks = "\n".join(render_block(block) for block in section["blocks"])
    rendered.append(
      f'<section class="method-section" id="{escape(section["id"])}">\n'
      f'<h2 class="chapter-heading">{escape(section["title"])}</h2>\n'
      f"{blocks}\n"
      "</section>"
    )
  return "\n".join(rendered)


def render_toc(data: dict[str, Any]) -> str:
  return "\n".join(
    f'<li class="toc-chapter"><a href="#{escape(section["id"])}">{escape(section["title"])}</a></li>'
    for section in data["sections"]
  )


def render_json_ld(data: dict[str, Any]) -> str:
  meta = data["metadata"]
  graph = {
    "@context": "https://schema.org",
    "@graph": [
      {
        "@type": "Organization",
        "@id": "https://norynthe.com/#organization",
        "name": "Norynthe",
        "url": "https://norynthe.com/"
      },
      {
        "@type": "ScholarlyArticle",
        "@id": f"{meta['canonicalUrl']}#method",
        "url": meta["canonicalUrl"],
        "name": meta["title"],
        "alternativeHeadline": meta["subtitle"],
        "description": data["abstract"][0],
        "version": meta["version"],
        "datePublished": meta["datePublished"],
        "author": { "@id": "https://norynthe.com/#organization" },
        "publisher": { "@id": "https://norynthe.com/#organization" },
        "isPartOf": { "@id": "https://papers.norynthe.com/#series" },
        "inLanguage": "en",
        "encoding": {
          "@type": "MediaObject",
          "contentUrl": meta["pdfUrl"],
          "encodingFormat": "application/pdf"
        }
      },
      {
        "@type": "BreadcrumbList",
        "@id": f"{meta['canonicalUrl']}#breadcrumb",
        "itemListElement": [
          {
            "@type": "ListItem",
            "position": 1,
            "name": "The Norynthe Papers",
            "item": "https://papers.norynthe.com/"
          },
          {
            "@type": "ListItem",
            "position": 2,
            "name": meta["title"],
            "item": meta["canonicalUrl"]
          }
        ]
      },
      {
        "@type": "WebPage",
        "@id": f"{meta['canonicalUrl']}#webpage",
        "url": meta["canonicalUrl"],
        "name": meta["title"],
        "mainEntity": { "@id": f"{meta['canonicalUrl']}#method" },
        "breadcrumb": { "@id": f"{meta['canonicalUrl']}#breadcrumb" },
        "isPartOf": { "@id": "https://papers.norynthe.com/#website" },
        "inLanguage": "en"
      }
    ]
  }
  return json.dumps(graph, indent=2)


def build_html(data: dict[str, Any]) -> str:
  meta = data["metadata"]
  toc = render_toc(data)
  sections = render_sections(data)
  principles = "\n".join(f"<li>{escape(item)}</li>" for item in data["principles"])
  abstract = "\n".join(f"<p>{escape(item)}</p>" for item in data["abstract"])
  json_ld = render_json_ld(data)

  return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(meta["title"])} | The Norynthe Papers</title>
  <meta name="description" content="{escape(meta["subtitle"])}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#0f1115">
  <meta name="author" content="{escape(meta["author"])}">
  <meta name="citation_title" content="{escape(meta["title"])}">
  <meta name="citation_author" content="{escape(meta["author"])}">
  <meta name="citation_publication_date" content="{escape(meta["datePublished"])}">
  <meta name="citation_publisher" content="{escape(meta["publisher"])}">
  <meta name="citation_pdf_url" content="{escape(meta["pdfUrl"])}">
  <link rel="canonical" href="{escape(meta["canonicalUrl"])}">

  <meta property="og:type" content="article">
  <meta property="og:site_name" content="The Norynthe Papers">
  <meta property="og:title" content="{escape(meta["title"])}">
  <meta property="og:description" content="{escape(meta["subtitle"])}">
  <meta property="og:url" content="{escape(meta["canonicalUrl"])}">
  <meta property="og:image" content="https://papers.norynthe.com/papers-social-card.png">
  <meta property="og:image:alt" content="The Norynthe Papers - AI Assurance Method">
  <meta property="article:published_time" content="{escape(meta["datePublished"])}">
  <meta property="article:author" content="{escape(meta["author"])}">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{escape(meta["title"])}">
  <meta name="twitter:description" content="{escape(meta["subtitle"])}">
  <meta name="twitter:image" content="https://papers.norynthe.com/papers-social-card.png">

  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="apple-touch-icon" href="/norynthe-icon-180.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="stylesheet" href="/papers.css?v=20260730a">

  <script type="application/ld+json">
  {json_ld}
  </script>
</head>
<body
  class="reader-body"
  data-analytics-site="Papers"
  data-analytics-page="{escape(meta["title"])}"
  data-analytics-content-type="methodology_paper"
>
  <a class="skip-link" href="#method-text">Skip to method</a>
  <header class="reader-header">
    <div class="site-shell reader-header-inner">
      <a class="reader-back" href="/">The Norynthe Papers</a>
      <a
        class="reader-download"
        href="{escape(meta["downloadPath"])}"
        download
        aria-label="Download {escape(meta["title"])} as a PDF"
        data-analytics-role="paper_download"
        data-analytics-material="{escape(meta["title"])}"
        data-publication-title="{escape(meta["title"])}"
        data-download-canonical="{escape(meta["canonicalDownloadPath"])}"
      >Download PDF</a>
    </div>
  </header>

  <main>
    <section class="reader-masthead" aria-labelledby="method-title">
      <div class="site-shell reader-masthead-grid">
        <div>
          <p class="reader-kicker">{escape(meta["series"])} · {escape(meta["seriesCode"])}</p>
          <h1 id="method-title">{escape(meta["title"])}</h1>
          <p class="reader-deck">{escape(meta["subtitle"])}</p>
        </div>
        <div class="reader-meta" aria-label="Publication metadata">
          <span>{escape(meta["status"])}</span>
          <span>Version {escape(meta["version"])}</span>
          <span>{escape(meta["publisher"])} · {escape(meta["displayDate"])}</span>
        </div>
      </div>
    </section>

    <details class="mobile-toc">
      <summary>Contents</summary>
      <ol>
        <li class="toc-book"><a href="#abstract">Abstract</a></li>
        <li class="toc-book"><a href="#principles">Operating principles</a></li>
        {toc}
        <li class="toc-book"><a href="#citation">Citation</a></li>
      </ol>
    </details>

    <div class="reader-layout">
      <nav class="reader-toc" aria-label="Method contents">
        <span class="reader-toc-title">Contents</span>
        <ol>
          <li class="toc-book"><a href="#abstract">Abstract</a></li>
          <li class="toc-book"><a href="#principles">Operating principles</a></li>
          {toc}
          <li class="toc-book"><a href="#citation">Citation</a></li>
        </ol>
      </nav>

      <article class="reader-article method-article" id="method-text">
        <section class="method-section" id="abstract">
          <h2 class="front-heading">Abstract</h2>
          {abstract}
        </section>

        <section class="method-section method-principles" id="principles">
          <h2 class="book-heading">Operating principles</h2>
          <ul>
            {principles}
          </ul>
        </section>

        {sections}

        <section class="method-section method-citation" id="citation">
          <h2 class="book-heading">Citation</h2>
          <p id="method-citation-text">{escape(meta["citation"])}</p>
          <button class="copy-button" type="button" data-copy-target="method-citation-text" aria-describedby="method-copy-status">Copy citation</button>
          <span class="copy-status" id="method-copy-status" role="status" aria-live="polite"></span>
        </section>

        <p class="reader-endnote">End of {escape(meta["title"])} · {escape(meta["displayDate"])}</p>
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
        <a href="/volume-i/">Volume I</a>
        <a
          href="{escape(meta["downloadPath"])}"
          download
          aria-label="Download {escape(meta["title"])} as a PDF"
          data-analytics-role="paper_download"
          data-analytics-material="{escape(meta["title"])}"
          data-publication-title="{escape(meta["title"])}"
          data-download-canonical="{escape(meta["canonicalDownloadPath"])}"
        >PDF</a>
        <a href="https://norynthe.com/">Norynthe Home</a>
      </div>
      <p class="copyright">Copyright © 2026 Norynthe.</p>
    </div>
  </footer>

  <script src="/site.js" defer></script>
  <script src="https://norynthe.com/norynthe-analytics.js" defer></script>
  <script src="https://norynthe.com/norynthe-pulse-tracker.js" defer data-pulse-site="papers"></script>
</body>
</html>
"""


class Rule(Flowable):
  def __init__(self, color=colors.HexColor("#86a9c9"), width=1):
    super().__init__()
    self.color = color
    self.width = width

  def draw(self):
    self.canv.setStrokeColor(self.color)
    self.canv.setLineWidth(self.width)
    self.canv.line(0, 0, self.width_available, 0)

  def wrap(self, availWidth, availHeight):
    self.width_available = availWidth
    return availWidth, 0.08 * inch


def pdf_safe(text: str) -> str:
  replacements = {
    "\u2018": "'",
    "\u2019": "'",
    "\u201c": '"',
    "\u201d": '"',
    "\u2013": "-",
    "\u2014": "-",
    "\u00a0": " ",
  }
  for old, new in replacements.items():
    text = text.replace(old, new)
  return escape(text)


def pdf_styles():
  base = getSampleStyleSheet()
  return {
    "title": ParagraphStyle(
      "NoryntheTitle",
      parent=base["Title"],
      fontName="Helvetica-Bold",
      fontSize=31,
      leading=34,
      textColor=colors.HexColor("#0f1115"),
      alignment=TA_LEFT,
      spaceAfter=16,
    ),
    "subtitle": ParagraphStyle(
      "NoryntheSubtitle",
      parent=base["BodyText"],
      fontName="Times-Roman",
      fontSize=14.5,
      leading=20,
      textColor=colors.HexColor("#4c5865"),
      spaceAfter=18,
    ),
    "meta": ParagraphStyle(
      "NoryntheMeta",
      parent=base["BodyText"],
      fontName="Helvetica-Bold",
      fontSize=8,
      leading=12,
      textColor=colors.HexColor("#253f63"),
      uppercase=True,
      spaceAfter=7,
    ),
    "h1": ParagraphStyle(
      "NoryntheH1",
      parent=base["Heading1"],
      fontName="Helvetica-Bold",
      fontSize=18,
      leading=22,
      textColor=colors.HexColor("#0f1115"),
      spaceBefore=20,
      spaceAfter=9,
    ),
    "h2": ParagraphStyle(
      "NoryntheH2",
      parent=base["Heading2"],
      fontName="Helvetica-Bold",
      fontSize=12,
      leading=15,
      textColor=colors.HexColor("#253f63"),
      spaceBefore=14,
      spaceAfter=6,
    ),
    "body": ParagraphStyle(
      "NoryntheBody",
      parent=base["BodyText"],
      fontName="Times-Roman",
      fontSize=10.6,
      leading=15.8,
      textColor=colors.HexColor("#1d252d"),
      spaceAfter=8,
    ),
    "definition": ParagraphStyle(
      "NoryntheDefinition",
      parent=base["BodyText"],
      fontName="Times-Roman",
      fontSize=10.8,
      leading=16,
      leftIndent=12,
      borderColor=colors.HexColor("#86a9c9"),
      borderWidth=1,
      borderPadding=8,
      textColor=colors.HexColor("#1d252d"),
      spaceBefore=4,
      spaceAfter=12,
    ),
    "bullet": ParagraphStyle(
      "NoryntheBullet",
      parent=base["BodyText"],
      fontName="Times-Roman",
      fontSize=10.4,
      leading=15.2,
      textColor=colors.HexColor("#1d252d"),
      leftIndent=6,
    ),
    "citation": ParagraphStyle(
      "NoryntheCitation",
      parent=base["BodyText"],
      fontName="Times-Italic",
      fontSize=9.7,
      leading=14,
      textColor=colors.HexColor("#4c5865"),
      spaceBefore=10,
    ),
    "footer": ParagraphStyle(
      "NoryntheFooter",
      parent=base["BodyText"],
      fontName="Helvetica",
      fontSize=7.5,
      leading=10,
      textColor=colors.HexColor("#6f7a85"),
      alignment=TA_CENTER,
    )
  }


def add_paragraph(story: list[Any], text: str, style: ParagraphStyle):
  story.append(Paragraph(pdf_safe(text), style))


def add_bullets(story: list[Any], items: list[str], style: ParagraphStyle):
  story.append(
    ListFlowable(
      [ListItem(Paragraph(pdf_safe(item), style), leftIndent=10) for item in items],
      bulletType="bullet",
      start="circle",
      bulletFontName="Helvetica",
      bulletFontSize=6,
      bulletColor=colors.HexColor("#253f63"),
      leftIndent=18,
      spaceAfter=8,
    )
  )


def build_pdf(data: dict[str, Any]) -> None:
  meta = data["metadata"]
  styles = pdf_styles()
  PDF_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

  doc = SimpleDocTemplate(
    str(PDF_OUTPUT),
    pagesize=LETTER,
    rightMargin=0.72 * inch,
    leftMargin=0.72 * inch,
    topMargin=0.72 * inch,
    bottomMargin=0.7 * inch,
    title=meta["title"],
    author=meta["author"],
    subject=meta["subtitle"],
  )

  story: list[Any] = []
  add_paragraph(story, f"{meta['series']} - {meta['seriesCode']}", styles["meta"])
  story.append(Paragraph(pdf_safe(meta["title"]), styles["title"]))
  story.append(Paragraph(pdf_safe(meta["subtitle"]), styles["subtitle"]))
  story.append(Rule())
  add_paragraph(story, f"{meta['status']} - Version {meta['version']} - {meta['publisher']} - {meta['displayDate']}", styles["meta"])
  story.append(Spacer(1, 0.18 * inch))

  story.append(Paragraph("Abstract", styles["h1"]))
  for paragraph in data["abstract"]:
    add_paragraph(story, paragraph, styles["body"])

  story.append(Paragraph("Operating principles", styles["h1"]))
  add_bullets(story, data["principles"], styles["bullet"])

  for section in data["sections"]:
    story.append(Paragraph(pdf_safe(section["title"]), styles["h1"]))
    for block in section["blocks"]:
      block_type = block["type"]
      if block_type == "p":
        add_paragraph(story, block["text"], styles["body"])
      elif block_type == "h3":
        story.append(Paragraph(pdf_safe(block["text"]), styles["h2"]))
      elif block_type == "ul":
        add_bullets(story, block["items"], styles["bullet"])
      elif block_type == "definition":
        story.append(Paragraph(f"<b>{pdf_safe(block['term'])}</b><br/>{pdf_safe(block['text'])}", styles["definition"]))
      else:
        raise ValueError(f"Unsupported PDF block: {block_type}")

  story.append(Paragraph("Citation", styles["h1"]))
  story.append(Paragraph(pdf_safe(meta["citation"]), styles["citation"]))

  def footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d4dae0"))
    canvas.setLineWidth(0.4)
    canvas.line(document.leftMargin, 0.52 * inch, LETTER[0] - document.rightMargin, 0.52 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#6f7a85"))
    canvas.drawCentredString(
      LETTER[0] / 2,
      0.34 * inch,
      f"Norynthe AI Assurance Method v0.1 - The Norynthe Papers - Page {document.page}"
    )
    canvas.restoreState()

  doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
  data = load_data()
  HTML_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
  HTML_OUTPUT.write_text(build_html(data), encoding="utf-8")
  build_pdf(data)
  print(f"Wrote {HTML_OUTPUT}")
  print(f"Wrote {PDF_OUTPUT}")


if __name__ == "__main__":
  main()
