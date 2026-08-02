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
- `/methods/ai-assurance-method-v0-1/` — Norynthe AI Assurance Method v0.1
- `/downloads/the-norynthe-papers-volume-i-citation-revision-1.pdf` — current citation-verified Volume I PDF
- `/downloads/the-norynthe-papers-volume-i.pdf` — compatibility URL containing the corrected Citation Revision 1 PDF
- `/downloads/norynthe-ai-assurance-method-v0-1.pdf` — stable canonical PDF method URL

User-facing PDF actions route through the Pulse worker so a download is
confirmed before the canonical PDF is returned:

- `https://norynthe-pulse-tracker.alanmotley.workers.dev/download/papers-volume-i-citation-revision-1?site=papers`
- `https://norynthe-pulse-tracker.alanmotley.workers.dev/download/ai-assurance-method-v0-1?site=papers`

For Volume I, keep `citation_pdf_url` and structured-data `contentUrl` pointed
at the current citation-revision PDF. Keep `data-download-canonical` pointed at
that same revision-specific PDF, and use the revision-specific Pulse route for
visible download `href` values. The original `/download/papers-volume-i` route
and stable PDF URL now deliver the corrected revision as compatibility aliases;
the uncorrected PDF has been withdrawn from public distribution. The AI Assurance
Method retains its stable method PDF in citation metadata, structured data, and
`data-download-canonical`. Both publication generators preserve this separation
during rebuilds.
- `/papers-social-card.png` — 1200 × 630 social preview

## Updating the AI Assurance Method

The HTML reader and PDF are generated from the structured source file:

```sh
python3 tools/build_ai_assurance_method.py
```

After regeneration, verify the method page, PDF, citation, metadata, and sitemap together. A revised method version should keep the prior version available or explicitly preserve its revision relationship.

## Updating Volume I

The online reader is generated from the canonical First Editorial Edition DOCX in the parent workspace:

```sh
python3 -m pip install -r tools/requirements.txt
python3 tools/build_reader.py
```

After regeneration, verify the online reader, PDF URL, citation, edition language, metadata, and table of contents together. Published editions should never be silently overwritten; a revised edition must retain its own explicit editorial identity and revision record. Volume I Citation Revision 1 was issued in August 2026 after a source-by-source audit of all 22 intellectual-lineage notes.

## Adding future publications

1. Create a stable publication directory and download filename.
2. Add complete publication metadata and structured data.
3. Add the publication to the homepage ledger.
4. Add its canonical URL to `sitemap.xml`.
5. Preserve the prior edition and document the revision relationship.

## Volume II prepublication state

The homepage announces Volume II for August 25, 2026 while Volume I remains
Publication Record 001 and the current published volume. Until the release-day
switch, Volume II has no public reader, PDF action, citation record, sitemap
entry, or published-book structured data.

On publication day:

1. Confirm the final HTML reader and canonical PDF both return successfully.
2. Replace scheduled language with the final edition and exact extent.
3. Activate the reader and tracked PDF actions.
4. Make Volume II the current volume and add its institutional citation.
5. Add its Book metadata, canonical URL, PDF encoding, and sitemap entry.
6. Update the navigation, footer, and social preview for Volume II.
7. Verify every production link before requesting indexing.
