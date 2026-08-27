# The Norynthe Papers

Production repository for [papers.norynthe.com](https://papers.norynthe.com/), the permanent publication archive of Norynthe.

## Architecture

The site follows the primary Norynthe website’s build-free GitHub Pages architecture:

- semantic, static HTML;
- a shared `papers.css` design layer for the archive and reader;
- minimal progressive enhancement in `site.js`;
- explicit canonical, Open Graph, Twitter, and JSON-LD metadata;
- root-level `CNAME`, `robots.txt`, `sitemap.xml`, and web manifest;
- canonical Norynthe icon assets;
- public analytics loaded from the primary Norynthe site.

No framework or build service is required for deployment.

## Publication structure

- `/` — publication archive homepage
- `/volume-i/` — semantic online edition of Volume I
- `/volume-ii/` — semantic online edition of Volume II
- `/methods/ai-assurance-method-v0-1/` — Norynthe AI Assurance Method v0.1
- `/downloads/the-norynthe-papers-volume-i.pdf` — stable canonical Volume I PDF
- `/downloads/the-norynthe-papers-volume-ii.pdf` — stable canonical Volume II PDF
- `/downloads/norynthe-ai-assurance-method-v0-1.pdf` — stable canonical PDF method URL

User-facing PDF actions route through the Pulse worker so a download is
confirmed before the canonical PDF is returned:

- `https://norynthe-pulse-tracker.alanmotley.workers.dev/download/papers-volume-i?site=papers`
- `https://norynthe-pulse-tracker.alanmotley.workers.dev/download/papers-volume-ii?site=papers`
- `https://norynthe-pulse-tracker.alanmotley.workers.dev/download/ai-assurance-method-v0-1?site=papers`

For Volumes I and II, keep `citation_pdf_url`, structured-data `contentUrl`, and
`data-download-canonical` pointed at each stable canonical PDF. Use the stable
Pulse routes for visible download `href` values. The AI Assurance Method retains
its stable method PDF in citation metadata, structured data, and
`data-download-canonical`. Both publication generators preserve this separation
during rebuilds.
- `/papers-social-card.png` — 1200 × 630 social preview

## Updating the AI Assurance Method

The HTML reader and PDF are generated from the structured source file:

```sh
python3 tools/build_ai_assurance_method.py
```

After regeneration, verify the method page, PDF, citation, metadata, and sitemap together.

## Updating Volume I

The online reader is generated from the canonical First Editorial Edition DOCX in the parent workspace:

```sh
python3 -m pip install -r tools/requirements.txt
python3 tools/build_reader.py
```

After regeneration, verify the online reader, PDF URL, citation, edition language, metadata, and table of contents together.

## Adding future publications

1. Create a stable publication directory and download filename.
2. Add complete publication metadata and structured data.
3. Add the publication to the homepage ledger.
4. Add its canonical URL to `sitemap.xml`.
5. Verify the publication metadata and public download paths together.

## Volume II publication state

Volume II was published on August 25, 2026. Its reader, canonical PDF,
institutional citation, sitemap record, structured data, social preview, and
Pulse-tracked PDF actions are active.
