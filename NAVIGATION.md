# Repo map — Unnatural Intelligence

This repository is the working files for **Unnatural Intelligence**, a Saitsa student club at SAIT. It is not an application codebase. Most folders hold print-ready brand files, event posters, Saitsa paperwork, and receipts.

Club site: https://unnaturalintelligence.club/
Live schedule: https://cochon123.github.io/club-schedule/

If you only need one file, use [Start here](#start-here) or [I need…](#i-need). For a walk through every folder, skip to [Folder by folder](#folder-by-folder).

---

## Start here

| If you are… | Open |
| --- | --- |
| New to the club | [`README.md`](README.md) then [`Mission Statement.txt`](Mission%20Statement.txt) |
| Checking dates | [`SCHEDULE.md`](SCHEDULE.md) |
| Submitting the charter | [`charter/Unnatural_Intelligence_Club_Charter_2026-27.pdf`](charter/Unnatural_Intelligence_Club_Charter_2026-27.pdf) |
| Filing a Saitsa event proposal | [`Events/event-proposal-TEMPLATE.pdf`](Events/event-proposal-TEMPLATE.pdf) |
| Designing anything visual | [`Branding/Vector Kit/preview.html`](Branding/Vector%20Kit/preview.html) |
| Printing name tags | [`Branding/Design Templates/Name-Tags/index.html`](Branding/Design%20Templates/Name-Tags/index.html) |
| Logging a receipt | [`Finance/Ledger/`](Finance/Ledger/) |

Saitsa Clubs Handbook (campus rules, grants, posters): [`SAITSA Club Handbook 26-27.pdf`](SAITSA%20Club%20Handbook%2026-27.pdf)

---

## Map

```
Unnatural-Intelligence/
├── README.md                    Club overview, regen commands
├── NAVIGATION.md                This file
├── SCHEDULE.md                  Dates, rooms, notes
├── Mission Statement.txt        Source copy for charter / brand
├── SAITSA Club Handbook 26-27.pdf
├── discord pic.png              Discord server image
├── site/                        Public website source (Events, Media, Team, Connect, About, exec desk)
├── server/                      Exec-desk session and private link list
├── api/                         Vercel routes: login, logout, desk
├── vercel.json                  Builds the public site to docs/
│
├── Branding/                    Logos, kit, print templates
├── Events/                      Proposals, posters, booth plans
├── charter/                     Club constitution (print + generators)
├── Finance/                     Ledger, receipts, e-transfers
├── Exec Profiles/               Headshots
├── scripts/                     Static-site build for Clubs Expo
├── Obselete/                    Retired drafts (spelling as in repo)
└── .github/workflows/           GitHub Pages deploy
```

---

## I need…

| Task | Go to |
| --- | --- |
| Official jellyfish | [`Branding/Jellyfish Mascot Gradient.svg`](Branding/Jellyfish%20Mascot%20Gradient.svg) — source path used by the vector kit |
| Fun Jelly expressions | [`Branding/Jelly/preview.html`](Branding/Jelly/preview.html) — same body and proportions, new eye holes (happy, wink, hearts, and others). Transparent PNGs in [`Branding/Jelly/png/`](Branding/Jelly/png/) |
| Colour tokens | [`Branding/Vector Kit/palette/colors.json`](Branding/Vector%20Kit/palette/colors.json) and [`tokens.css`](Branding/Vector%20Kit/palette/tokens.css) |
| Wordmarks / lockups | [`Branding/Vector Kit/lockups/`](Branding/Vector%20Kit/lockups/) |
| Icons (token, halt, prompt, …) | [`Branding/Vector Kit/icons/`](Branding/Vector%20Kit/icons/) — boxed + `*-plain.svg` |
| Stickers / vinyl | [`Branding/Vector Kit/stickers/`](Branding/Vector%20Kit/stickers/) |
| Instagram / OG / story templates | [`Branding/Vector Kit/social/`](Branding/Vector%20Kit/social/) |
| Raster copies of the kit | [`Branding/Vector Kit/png/`](Branding/Vector%20Kit/png/) |
| 6×3 ft table banner | [`Branding/Design Templates/Banner_6x3ft/index.html`](Branding/Design%20Templates/Banner_6x3ft/index.html) · preview PNG at [`Branding/Banner_6x3ft-150dpi.png`](Branding/Banner_6x3ft-150dpi.png) |
| Banner stand PDF | [`Branding/Design Templates/Banner_Stand_Template_23.5x89.5_.pdf`](Branding/Design%20Templates/Banner_Stand_Template_23.5x89.5_.pdf) |
| Walk-up name tags | [`Branding/Design Templates/Name-Tags/`](Branding/Design%20Templates/Name-Tags/) — fill-in PDFs + `index.html` |
| Exec engraved plates | [`Branding/Design Templates/Name-Tags/engrave/`](Branding/Design%20Templates/Name-Tags/engrave/) |
| Dye-sub lanyards | [`Branding/Design Templates/Lanyards/`](Branding/Design%20Templates/Lanyards/) — send `print/` or `png/` to the shop |
| Halt & Restart posters | [`Events/Halt-Restart/`](Events/Halt-Restart/) — `halt-restart-v3.html` is the arcade ticket |
| Podcast posters | [`Events/Podcast/`](Events/Podcast/) — Season 1 of *I hate it but it’s so useful*, plus card sheets |
| AI Agents posters | [`Events/AI-Agents-Workshop/AI-Agents/`](Events/AI-Agents-Workshop/AI-Agents/) — open `index.html` |
| Unnatural Games posters | [`Events/Unnatural-Games/`](Events/Unnatural-Games/) — open `index.html`. Three 11×17 ideas. Edit `copy.js` before print |
| Clubs Expo booth | [`Events/Clubs-Expo/table-concepts.html`](Events/Clubs-Expo/table-concepts.html) |
| Game jam (Saturday) | [`Events/One-Day-AI-Game-Jam/`](Events/One-Day-AI-Game-Jam/) |
| Game jam (24-hour, Ziva) | [`Events/24-Hour-AI-Game-Jam/`](Events/24-Hour-AI-Game-Jam/) |
| Game jam (24-hour, older Layer draft) | [`Events/AI-Game-Jam/`](Events/AI-Game-Jam/) |
| Blank event proposal | [`Events/event-proposal-TEMPLATE.docx`](Events/event-proposal-TEMPLATE.docx) (Google Docs) or the PDF |
| 2026–27 charter (print) | [`charter/Unnatural_Intelligence_Club_Charter_2026-27.pdf`](charter/Unnatural_Intelligence_Club_Charter_2026-27.pdf) |
| Charter in Google Docs | Upload the `.docx` — see [`README.md`](README.md) |
| Charter in Google Slides | Upload the `.pptx` for page-accurate layout |
| Fonts (Inter, JetBrains Mono) | [`charter/fonts/`](charter/fonts/) — SIL OFL |
| Ledger (CSV / Excel) | [`Finance/Ledger/`](Finance/Ledger/) |
| Approved receipts | [`Finance/Submitted/Approved/`](Finance/Submitted/Approved/) |
| Saitsa Clubs logo (unaltered) | [`Branding/SaitsaStudentClubsPrimaryLogo.svg`](Branding/SaitsaStudentClubsPrimaryLogo.svg) |

---

## Folder by folder

### Root files

| File | What it is |
| --- | --- |
| [`README.md`](README.md) | Club pitch, charter/event/branding file tables, regenerate commands |
| [`SCHEDULE.md`](SCHEDULE.md) | Upcoming dates. Proposed items are marked `[proposed]` and point at the matching `Events/` folder |
| [`Mission Statement.txt`](Mission%20Statement.txt) | Raw mission copy. Charter generators and brand text pull from this voice |
| [`SAITSA Club Handbook 26-27.pdf`](SAITSA%20Club%20Handbook%2026-27.pdf) | Campus handbook — grants, posters, exec rules |
| [`discord pic.png`](discord%20pic.png) | Discord server picture |
| [`vercel.json`](vercel.json) | Tells Vercel to run `node scripts/build-site.mjs` and publish `docs/` |
| [`site/`](site/) | Public website: page copy, CSS, and the exec sign-in screen |
| `.gitignore` | Ignores `__pycache__/`, `.DS_Store`, and the generated `docs/` site |

---

### `Branding/` — visual identity

Start with **[`Branding/Vector Kit/preview.html`](Branding/Vector%20Kit/preview.html)** rather than browsing SVGs one by one.

#### Top-level brand files

| File | Use |
| --- | --- |
| `Jellyfish Mascot Gradient.svg` | Official mascot path (lime → pink). The kit generator loads this |
| `Jellyfish Mascot Gradient Transparent.png` / `Jellyfish Mascot.png` | Raster mascot |
| `SaitsaStudentClubsPrimaryLogo.svg` | Required, unaltered, on student-club posters |
| `saitoffficiallogo.jpg` | SAIT wordmark used on poster sheets |
| `Colour Palette.jpg` | Quick palette reference |
| `Banner_6x3ft-150dpi.png` | Raster of the 6×3 ft table banner |

#### `Branding/Vector Kit/`

Self-contained SVGs. Palette matches the banner and Halt & Restart posters.

| Folder | Contents |
| --- | --- |
| `marks/` | Jellyfish in each colour, mini marks, favicon |
| `lockups/` | Wordmark + jellyfish + type, plus fifteen Unnatural Games marks (`games-lean` through `games-badge`) |
| `icons/` | 64px tools: token, prompt, halt, restart, workflow, … Boxed and `*-plain` |
| `stickers/` | Quotes, die-cuts, tickets, 3 in circles, laptop wordmark |
| `badges/` | Member / exec / event chips |
| `avatars/` | 512px social icons |
| `social/` | Instagram 1080, story 1080×1920, OG 1200×630, banner 1500×500 |
| `fact-bars/` | When / where / type / who strips. `strip.svg` is on ink. Clear variants have no background |
| `frames/` | Dashed ticket frame, plus transparent 11×17 tabloid borders |
| `patterns/` | Ink-backed tiles, transparent grid overlays, 11×17 alignment grids, wash, glitch bars |
| `palette/` | `colors.json`, `tokens.css`, swatches |
| `png/` | Sample raster of every SVG, same relative paths |

Regenerate: `python3 "Branding/Vector Kit/generate.py"` (see kit README). Fonts come from `charter/fonts/`. Wordmarks are outlined so shops do not need the fonts installed.

#### `Branding/Design Templates/`

Print jobs, not the reusable kit.

| Path | What to open | Notes |
| --- | --- | --- |
| `Banner_6x3ft/` | `index.html` | HTML layout for the 6×3 ft table banner. `render_banner.py` / `capture_html_layout.sh` export it |
| `Name-Tags/` | `index.html` | First-name tags. Exec = lime. Human members = pink. Clankers = cyan. Print 4×3 lanyard inserts or 3.5×2 stickers |
| `Name-Tags/*-Fill-In*.pdf` | PDFs | Walk-up sheets: human A4, human ticket A4, clanker ticket A4, exec stickers |
| `Name-Tags/engrave/` | `preview.html` | 75×25 mm exec nameplates. Black-fill SVGs for laser; colour proofs in `proof/`. Daniil omitted |
| `Lanyards/` | `preview.html` | 45×2 cm dye-sub straps. Club templates have no names. Exec straps add first name + title. Send `print/` SVG/PDF or `png/` 300 DPI |
| `Banner_Stand_Template_23.5x89.5_.pdf` | PDF | Banner-stand template |

Lanyard print vs wear: `print/` is what the shop gets (outlined, actual size). `wear/` is the same art for on-screen mockups.

#### `Branding/Old/` and `Branding/Random Assets/`

Retired logos and one-off PNGs. Do not use these on new print. Prefer the Vector Kit.

---

### `Events/` — proposals, posters, booths

Each named subfolder is one event. Shared templates sit in the `Events/` root.

| Root file | Use |
| --- | --- |
| `event-proposal-TEMPLATE.pdf` / `.docx` | Blank Saitsa proposal in the 2026–27 kit. Every proposal already includes **$15 printing** (25 posters + 30 name tags) and **$5 misc** |
| `generate_proposal.py` / `generate_proposal_docx.py` | Rebuild those templates |
| `Outdated Event Proposal Template.pdf` | Old template — do not submit |
| `Poster Requirements.png` | Saitsa poster checklist screenshot |

**Convention:** posters are HTML sized for print (usually 11×17 tabloid). Open in Chrome → Print → Save as PDF, margins none, background graphics on. Several folders have a `capture_*.sh` script that does the same.

#### `Events/Halt-Restart/`

Live prompting lab (Fri 18 Sep 2026, Heritage Hall AA128).

| File | Variety |
| --- | --- |
| `halt-restart.html` | First pass |
| `halt-restart-v2.html` | Paper sheet + ink rail |
| `halt-restart-v3.html` | Arcade ticket (current portrait) |
| `halt-restart-v3-landscape.html` | 17×11 landscape of v3 |

`poster-boot.js` and `assets/` are shared with the print HTML.

#### `Events/AI-Agents-Workshop/`

Lunch & Learn (Thu 1 Oct 2026, MB202). Proposal markdown at the folder root. Twelve poster varieties live in **`AI-Agents/`** — open [`index.html`](Events/AI-Agents-Workshop/AI-Agents/index.html).

`v1`–`v3` match the Halt & Restart family. `v4`–`v12` use more of the vector kit (toolkit, lime board, nodes, billboard, listings, versus). Capture script: `Events/AI-Agents-Workshop/AI-Agents/capture_posters.sh`.

#### `Events/Unnatural-Games/`

Social game night (proposed Mondays 6:00–8:00 PM, room still with SECC). Three tabloid ideas in [`index.html`](Events/Unnatural-Games/index.html). Shared facts live in `copy.js`. `v1-presents.html` is the glitch-bar shell. `v2-scoreboard.html` is humans vs the model. `v3-ticket.html` is the arcade ticket. [`templates.html`](Events/Unnatural-Games/templates.html) is the editable fact-bar sheet, with transparent grid overlays and 11×17 borders. [`logos.html`](Events/Unnatural-Games/logos.html) is fifteen Games marks that are not the club wordmark, including five built around the jellyfish (crest, swim, overlap, quad, badge). Set the booked date and room before a Saitsa poster submission. Weekly repeat is not locked.
#### `Events/Podcast/`

Season 1 promo for the club podcast, *I hate it but it’s so useful*. Open [`index.html`](Events/Podcast/index.html).

| File | Variety |
| --- | --- |
| `ep01-hate.html` | 11×17 ticket · E01 *I hate it* |
| `ep02-useful.html` | 11×17 playlist · E02 *So useful* |
| `ep03-finish.html` | 11×17 meters · E03 *Human finish* |
| `cards.html` | Letter sheets: half-page promo cards and 3.9 in squares |
| `png/` | 300 DPI PNG of every poster, card, letter sheet, and asset |

These are listen-promos. No room or drop date is printed. Capture script: `Events/Podcast/capture.sh`.

#### `Events/Clubs-Expo/`

Fall Showcase booth (13–14 Oct 2026, Stan Grad Atrium).

| File | Use |
| --- | --- |
| `table-concepts.html` | Full booth page — recommended concept is **Candy git** |
| `candy-git.html` | Staff card for the candy-git table |
| `git-walk.html` | Printable 60-second paper git tutorial (staff card, tent signs, AI-slop cards) |
| `git-walk-seed/` | Optional laptop repo for the live demo |
| `assets/` | Booth images / inventory |

`scripts/build-clubs-expo-site.sh` is called by the site build and lands this folder at `docs/expo/` (`/expo/` on the club domain). It is the staff page for the booth, not the public homepage.

#### `Events/One-Day-AI-Game-Jam/`

Saturday jam with Game Development Club (Godot 4 + Ziva, doors 9:00, 8 hours). Markdown + quoted expense screenshots + branded PDF. Rebuild: `python3 Events/One-Day-AI-Game-Jam/generate_proposal.py`.

#### `Events/24-Hour-AI-Game-Jam/`

Overnight Saturday–Sunday jam (Godot 4 + **paid Ziva Basic**, doors Saturday 9:00, 24-hour build). Food from the attached Curated Catering campus menu cards only. PDF + editable PowerPoint (Google Slides). Rebuild: `python3 Events/24-Hour-AI-Game-Jam/generate_proposal.py` and `python3 Events/24-Hour-AI-Game-Jam/generate_pptx.py`.

#### `Events/AI-Game-Jam/`

Older overnight draft (Layer workspace + Hotel Arts Event Palette). Prefer [`Events/24-Hour-AI-Game-Jam/`](Events/24-Hour-AI-Game-Jam/) for the current grant packet.

#### `Events/AGJ/`

Older game-jam poster HTML (`v2.html`). Prefer the named Game Jam folders for current copy.

---

### `charter/` — club constitution

Current branded set uses the **2026–27** filename:

| File | Open with |
| --- | --- |
| `Unnatural_Intelligence_Club_Charter_2026-27.pdf` | Print / attach to grants |
| `Unnatural_Intelligence_Club_Charter_2026-27.docx` | Google Docs (structure, not pixel-perfect) |
| `Unnatural_Intelligence_Club_Charter_2026-27.pptx` | Google Slides (closest visual match) |

Files **without** `2026-27` in the name are the earlier teal/wave draft. Keep them; do not submit them as current.

| Script | Output |
| --- | --- |
| `generate_charter_revamp.py` | Current PDF |
| `generate_docx_revamp.py` | Current Word |
| `generate_pptx_revamp.py` | Current PowerPoint |
| `generate_charter.py` / `generate_docx.py` / `generate_pptx.py` | Earlier draft |
| `revamp_copy.py` | Body copy for the 2026–27 rewrite |
| `revamp_kit.py` / `export_assets.py` | Pull kit art into `assets/revamp/` |

`assets/` holds exported PNGs for the generators. `fonts/` is Inter + JetBrains Mono (SIL OFL) and is also referenced by posters and the vector kit.

```bash
pip install -r charter/requirements.txt
python3 charter/generate_charter_revamp.py
python3 charter/generate_docx_revamp.py
python3 charter/generate_pptx_revamp.py
```

---

### `Finance/` — money trail

| Path | What it is |
| --- | --- |
| `Ledger/` | Canonical list. CSV for git diffs, XLSX for Sheets. Companion Google Sheet is linked in the ledger README |
| `Submitted/Approved/` | Receipts already filed (banner, domain, Dollarama, stickers, expo storage) |
| `Submitted/Approved/Events/HaltRestart/` | Halt & Restart receipts (gift card, chopsticks, posters) |
| `eTransfers/` | Interac confirmations (e.g. Hailey Sept 14) |
| Root JPGs/PDFs (`PENDING TableCloth.pdf`, nametag receipts, …) | In-progress or not yet filed |

Ledger columns: date, description, category, vendor, amount CAD, purchaser, receipt path in this repo, status, notes, event.

Verify amounts against the original receipt image before audit or grant use.

---

### `Exec Profiles/`

Headshots (currently Hailey). Used when a design needs a photo rather than the vector avatars.

---

### `scripts/` and `.github/`

| File | Role |
| --- | --- |
| `scripts/build-site.mjs` | Builds the public site into `docs/`, then nests the Clubs Expo staff page at `docs/expo/` |
| `scripts/build-clubs-expo-site.sh` | Copies `Events/Clubs-Expo/` into a folder (used by the site build for `/expo/`) |
| `scripts/preview-site.mjs` | Serves `docs/` plus `/api/login`, `/api/logout`, `/api/desk`, and `/api/events` |
| `api/` | Vercel functions for the exec desk. Password is the `ADMIN_PASSWORD` environment variable |
| `server/desk-content.js` | Exec-only links (ledger, Rubric portal, internal dates). Not copied into the public HTML |
| `server/events-catalog.js` | Event copy. Upcoming nights stay hidden until checked. Past nights stay on the Events page |
| `server/data/event-visibility.json` | Which event ids are published. `{}` means none |
| `vercel.json` | Build command and `outputDirectory: docs` |

Generated `docs/` is gitignored. Preview with `node scripts/build-site.mjs` then `ADMIN_PASSWORD=… node scripts/preview-site.mjs`.

---

### `Obselete/`

Retired on purpose (folder name is misspelled in the repo). `index.html` is an old Rival AI Prompting Challenge poster. `LinkToGoogleDoc.txt` points at the original club Google Doc, which is also linked from the README. Do not treat these as current brand files.

---

## How files relate

```
Mission Statement.txt ──► charter/revamp_copy.py ──► 2026–27 charter PDF/DOCX/PPTX
                       ──► event proposal copy

Branding/Jellyfish Mascot Gradient.svg
        └──► Vector Kit/generate.py ──► marks, lockups, icons, stickers, …
                  └──► posters (Halt-Restart, AI-Agents) pull kit icons + fonts
                  └──► Name-Tags, Lanyards, Banner_6x3ft
                  └──► charter assets/revamp

Events/*-EN.md ──► generate_proposal.py ──► branded proposal PDF
```

Shared design tokens (from [`colors.json`](Branding/Vector%20Kit/palette/colors.json)):

| Token | Hex |
| --- | --- |
| Paper | `#F9F9FA` |
| Olive | `#95B747` |
| Ink | `#030205` |
| Pink | `#FA4A9E` |
| Wine | `#591337` |
| Lime | `#BAF837` |
| Cyan | `#7EC8FF` |

Fonts everywhere: **Inter Display** (titles), **Inter** (body), **JetBrains Mono** (labels). Files in `charter/fonts/`.

---

## Editing without getting lost

1. **Prefer HTML / SVG / markdown over exported PNG/PDF** when changing design. Regenerators overwrite the derived files.
2. **Open `preview.html` or `index.html` in a folder first.** Almost every design directory has one.
3. **Do not restyle the Saitsa Clubs logo.** Posters must use it unaltered.
4. **`Old/`, `Obselete/`, and filenames without `2026-27`** are archives.
5. **Python scripts** live next to the files they emit (`generate.py`, `generate_proposal.py`, `generate_*_revamp.py`).
6. **Print path:** HTML → Chrome print to PDF (tabloid, no margins, backgrounds on) or the folder’s `capture_*.sh`.
7. **Receipts** go in `Finance/` (or `Submitted/Approved/` once filed) and get a row in the ledger with a repo-relative path.
