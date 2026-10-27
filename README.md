# UnInt-Site

Public website for **Unnatural Intelligence**, SAIT’s AI club: [unnaturalintelligence.club](https://unnaturalintelligence.club/).

```bash
node scripts/build-site.mjs
node scripts/preview-site.mjs
```

The build writes `docs/`. Preview serves that folder at http://127.0.0.1:4173.

## Adding or updating an event

Club nights on the public site are data-driven. Do **not** edit `events.html`, `media.html`, or layout JS to add a night. Drop files in, update one JSON entry, rebuild.

Print originals live in the private working repo (`pawsp7/Unnatural-Intelligence`, under `Events/<EventName>/`). This site only stores **web-sized copies**.

### Folder convention

```
site/events/
  events.json                 # one object per event
  <id>/                       # kebab-case, same as the JSON id
    poster.png                # or .jpg / .webp — the lead poster
    recap/                    # optional room photos
      01-group.jpg
      02-hailey.jpg
    posters/                  # optional extra 11×17 variants
      paper.png
```

Recap files sort alphabetically with numeric prefixes (`01-`, `02-`, …). That order is the gallery order. Extra sheets in `posters/` also sort by filename.

### Manifest (`site/events/events.json`)

Add or edit one object in `events`:

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Folder name. Lowercase kebab-case. |
| `title` | yes | Display name. |
| `date` | if known | `YYYY-MM-DD`. Splits upcoming vs past. |
| `time`, `place`, `summary` | if known | Shown on the ticket. |
| `blurb` | no | Shorter ticket line; falls back to `summary`. |
| `kicker` | no | Stub label (`Live lab`, `Workshop`, `Jam`). |
| `chips` | no | Extra tags. `Past` is added automatically when `past` is true. |
| `past` | no | `true` once it has run. Recap photos also mark it past. |
| `listed` | no | Default `true`. `false` keeps it off Events (desk + public). |
| `media` | no | Default `true` if a poster or recap exists. Media page. |
| `featured` | no | `true` to show the poster on the home page. |
| `announce` | no | Upcoming nights need this (or a poster that isn’t `Proposed`) before they appear on Events without a Rubric listing. |
| `statusLabel` | no | Upcoming status chip (`Proposed`, `Confirmed`). |
| `poster` | if you have one | Filename in the event folder, usually `poster.png`. |
| `posterAlt` | yes if poster | Alt text for the lead poster. |
| `alts` | recap/sheets | Map of filename → alt text. Missing keys get a generic sentence. |
| `layout.wide` | no | Recap filenames that span the gallery row. Default: first landscape photo. |
| `layout.classes` | no | Extra CSS class on a recap file (`door` is the only special one today). |

### Exact steps (automated job)

1. Copy (do not move) the lead poster from the private repo into `site/events/<id>/poster.png`.
2. Copy recap photos into `site/events/<id>/recap/`, named `01-…`, `02-…` in gallery order.
3. Copy extra poster variants into `site/events/<id>/posters/` if they should appear on Media.
4. Add or update the matching object in `site/events/events.json`. Fill `date`, `time`, `place`, `summary`, and alt text when known. Set `past: true` after the night runs. Set `listed: true` when it should show on Events.
5. Run `node scripts/optimize-event-images.mjs` so anything larger than 1600px (photos) or 1400px (posters) is resized and compressed **in place**. Originals stay in the private repo.
6. Run `node scripts/build-site.mjs`. Confirm `/events/` shows the night and `/media/#<id>` opens its set.
7. Commit `site/events/events.json` plus the new/changed files under `site/events/<id>/`. No layout code.

Private-repo map that the job should look for:

| Private folder | Site `id` |
| --- | --- |
| `Events/Halt-Restart/` | `halt-restart` |
| `Events/AI-Agents-Workshop/` | `ai-agents` |
| `Events/Unnatural-Games/` (poster `FINAL-POSTER.png`, recap `IMG_2230`–`IMG_2237`) | `unnatural-games` |
| `Events/AI-Project-Showcase/` | `ai-project-showcase` |
| `Events/Game-Jam/AI-Assisted-Game-Jam/` (posters v1–v3) | `ai-assisted-game-jam` |

Do not commit secrets, tokens, or full-resolution originals.
