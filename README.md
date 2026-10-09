# Seiko Alpinist Archive

An independent, non-commercial interactive museum and field guide to the Seiko Alpinist, 1959 to today. Not affiliated with Seiko.

## Run locally

```bash
python3 -m http.server 8791
```

Then open http://localhost:8791.

## Rebuild after editing data

```bash
python3 tools/build.py
```

The build reads the research and curation files and regenerates `index.html`, `watches/*.html` (one page per reference), `assets/js/data.js` and `data/models.json`.

| File | Contents |
|---|---|
| `research/vintage.json`, `sarb.json`, `prospex.json` | Model specs with sources, uncertain fields and disputes |
| `research/context.json` | Japanese mountains and context facts, fact-checked |
| `research/images.json` | Photo manifest: licence, author, source URL. Commons files are stored locally; official Seiko images are hotlinked with credit |
| `research/curation.json` | Editorial layer: series groupings, colour themes, landscape picks, family tree, evolution stages, display copy |

Unverified values stay `null` and render as *Unknown*. To change which landscape a watch page uses, edit `landscape_by_ref` in `curation.json`.
