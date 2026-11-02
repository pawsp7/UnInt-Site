# UnInt-Site

Public site for Unnatural Intelligence: https://unnaturalintelligence.club/

```bash
node scripts/build-site.mjs
node scripts/preview-site.mjs
```

## Updating /events/

The Events page layout lives in `site/content/events.html` and `site/js/events.js`. Do not edit those to add a night.

The club repo keeps **the** display poster in `Events/<EventName>/poster/` (prefer `poster.png`). Extra sheets next to that folder are ignored. Mirror the same file onto this site:

1. Create `site/assets/events/<id>/` (kebab-case id, for example `halt-restart` or `ai-project-showcase`).
2. Copy that poster into `site/assets/events/<id>/poster/`. Prefer `poster.png`. The build and the page only read posters from that folder.
3. Recap photos go in `recap/` (Halt & Restart photos still sit next to the event folder).
4. Copy an object in `site/assets/events/events.json`. Set `id`, `match` (title fragments), and `poster.alt`. The build fills `src` / width / height from the `poster/` folder. Optional: `ticket`, `place`, `datetime` if the public card should use those instead of Rubric.
5. Run `node scripts/build-site.mjs`. No HTML or JS edits.

Game Jam posters still live in the club repo (`Events/Game-Jam/AI-Assisted-Game-Jam`). Drop a chosen sheet into `poster/` here when it should show.

## Updating /resources/

Workshop slide decks live in `site/resources/<id>/` and are served at `/resources/<id>/`. Leave out the deck's `fonts/` folder: the build copies the Inter and JetBrains Mono files from `charter/fonts/` into it. Add the id to the deck list in `scripts/build-site.mjs`, put a 1600×900 title-slide picture in `site/resources/previews/<id>.jpg`, and add a card to `site/content/resources.html`.
