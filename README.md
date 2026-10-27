# UnInt-Site

Public site for Unnatural Intelligence: https://unnaturalintelligence.club/

```bash
node scripts/build-site.mjs
node scripts/preview-site.mjs
```

## Updating /events/

The Events page layout lives in `site/content/events.html` and `site/js/events.js`. Do not edit those to add a night.

1. Create `site/assets/events/<id>/` (kebab-case id, for example `halt-restart`).
2. Put a web-sized poster in that folder (`poster.png`, or `ink.png` for Agents). Put recap photos in `recap/` (Halt & Restart photos sit next to the poster).
3. Copy an object in `site/assets/events/events.json`. Set `id`, `match` (title fragments), `poster` (src/width/height/alt), and `recap.pages` (the photos, in order). If the night should appear under “Already ran” even before the catalog marks it past, add a `fallback` ticket like AI Agents.
4. Run `node scripts/build-site.mjs`. No HTML or JS edits.

Private-repo recaps not in this tree (Unnatural Games `Recap/IMG_2230–2237` and `FINAL-POSTER.png`, AI Project Showcase posters, AI-Assisted Game Jam v1–v3) were not readable here. Drop those files into a new `<id>/` folder and add the JSON object when you have them.
