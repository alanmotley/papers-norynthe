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
- `/downloads/the-norynthe-papers-volume-i.pdf` — stable PDF publication URL
- `/papers-social-card.png` — 1200 × 630 social preview

## Updating Volume I

The online reader is generated from the canonical First Editorial Edition DOCX in the parent workspace:

```sh
python3 -m pip install -r tools/requirements.txt
python3 tools/build_reader.py
```

After regeneration, verify the online reader, PDF URL, citation, edition language, metadata, and table of contents together. Published editions should never be silently overwritten; a revised edition must retain its own explicit editorial identity and revision record.

## Adding future publications

1. Create a stable publication directory and download filename.
2. Add complete publication metadata and structured data.
3. Add the publication to the homepage ledger.
4. Add its canonical URL to `sitemap.xml`.
5. Preserve the prior edition and document the revision relationship.
