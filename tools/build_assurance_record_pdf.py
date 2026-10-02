#!/usr/bin/env python3
"""Create the M-002 PDF companion from its structured source."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_ai_assurance_method import Rule, add_bullets, add_paragraph, pdf_safe, pdf_styles, Paragraph, SimpleDocTemplate, LETTER, inch, colors

DATA = json.loads((ROOT / "data/assurance-record-v0-1.json").read_text())
OUT = ROOT / "downloads/norynthe-assurance-record.pdf"
meta = DATA["metadata"]
styles = pdf_styles()
story = []
add_paragraph(story, f"{meta['series']} - {meta['seriesCode']}", styles["meta"])
story.append(Paragraph(pdf_safe(meta["title"]), styles["title"]))
story.append(Paragraph(pdf_safe(meta["subtitle"]), styles["subtitle"]))
story.append(Rule())
add_paragraph(story, f"{meta['status']} - Version {meta['version']} - {meta['publisher']} - {meta['displayDate']}", styles["meta"])
story.append(Paragraph("Abstract", styles["h1"]))
for paragraph in DATA["abstract"]: add_paragraph(story, paragraph, styles["body"])
story.append(Paragraph("Operating principles", styles["h1"]))
add_bullets(story, DATA["principles"], styles["bullet"])
for section in DATA["sections"]:
    story.append(Paragraph(pdf_safe(section["title"]), styles["h1"]))
    for block in section["blocks"]:
        if block["type"] == "p": add_paragraph(story, block["text"], styles["body"])
        elif block["type"] == "h3": story.append(Paragraph(pdf_safe(block["text"]), styles["h2"]))
        elif block["type"] == "ul": add_bullets(story, block["items"], styles["bullet"])
        elif block["type"] == "definition": story.append(Paragraph(f"<b>{pdf_safe(block['term'])}</b><br/>{pdf_safe(block['text'])}", styles["definition"]))
story.append(Paragraph("Citation", styles["h1"]))
story.append(Paragraph(pdf_safe(meta["citation"]), styles["citation"]))

def footer(canvas, document):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#d4dae0")); canvas.setLineWidth(0.4)
    canvas.line(document.leftMargin, 0.52 * inch, LETTER[0] - document.rightMargin, 0.52 * inch)
    canvas.setFont("Helvetica", 7.5); canvas.setFillColor(colors.HexColor("#6f7a85"))
    canvas.drawCentredString(LETTER[0] / 2, 0.34 * inch, f"The Norynthe Assurance Record - The Norynthe Papers - Page {document.page}")
    canvas.restoreState()

OUT.parent.mkdir(parents=True, exist_ok=True)
doc = SimpleDocTemplate(str(OUT), pagesize=LETTER, rightMargin=0.72*inch, leftMargin=0.72*inch, topMargin=0.72*inch, bottomMargin=0.7*inch, title=meta["title"], author=meta["author"], subject=meta["subtitle"])
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(f"Wrote {OUT}")
