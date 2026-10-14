# AI Agents — tabloid posters

Twelve 11×17 varieties for the Oct 1 Lunch & Learn. v1–v3 sit in the Halt & Restart family. v4–v6 use more of the vector kit. v7–v9 try tighter layouts. v10–v12 are billboard cousins of v9 with a few new kit icons.

Open [`index.html`](index.html) for PDF previews (PNG rasters of the printable sheets) plus HTML sources.

| File | Variety | Notes |
| --- | --- | --- |
| [`v1-ink.html`](v1-ink.html) | Dark ink grid | Halt & Restart v1 |
| [`v2-paper.html`](v2-paper.html) | Paper sheet + ink rail | Halt & Restart v2 |
| [`v3-arcade.html`](v3-arcade.html) | Arcade ticket + dashed frame | Halt & Restart v3 |
| [`v4-toolkit.html`](v4-toolkit.html) | Cyan toolkit dump | Chatbot vs agent + eight-tool grid |
| [`v5-lime.html`](v5-lime.html) | Lime header board | What / How / Use columns + icon agenda |
| [`v6-nodes.html`](v6-nodes.html) | Node map | Perceive → decide → act + halt / restart |
| [`v7-split.html`](v7-split.html) | Split lime rail | Facts on lime · lesson cards · live-lab agenda |
| [`v8-bands.html`](v8-bands.html) | Color bands | Full-bleed What / How / Use stripes · fact pills |
| [`v9-billboard.html`](v9-billboard.html) | Billboard | Giant outline title (What? How?) · hugging cards · pyramid schedule tiles |
| [`v10-monument.html`](v10-monument.html) | Monument | Even larger stacked title · full-color What / How / Use |
| [`v11-listings.html`](v11-listings.html) | Listings | Cinema-style runtime · studying / resume / project |
| [`v12-versus.html`](v12-versus.html) | Versus | Chatbots answer / Agents act split · new kit icons |

## Event copy on every sheet

- **Title:** AI Agents: What? How? & Learning to Use Them
- **When:** Thu Oct 1 · 6:00–8:00 PM
- **Where:** MB202 · Stan Grad Centre (SECC booking)
- **Type:** Student Club / Lunch & Learn / educational workshop
- **Purpose:** Demystify AI agents for a non-technical audience. No prior experience. Leave having used one.
- **Contact:** unnaturalintelligencesait@gmail.com + Discord QR

## Saitsa poster checklist

From [saitsa.com/Poster-Submission](https://saitsa.com/poster-submission/) and the Clubs Handbook:

| Requirement | On these sheets |
| --- | --- |
| Tabloid **11×17** | Yes (`@page { size: 11in 17in }`) |
| Date and time | Thu Oct 1 · 6:00–8:00 PM |
| Location | MB202 · Stan Grad Centre · SAIT campus |
| Type of event | Student Club / Lunch & Learn |
| Purpose of event | Demystify AI agents; no prior experience; leave having used one |
| Contact (email, phone, or QR) | Email + Discord QR |
| **Unaltered Saitsa Clubs logo** | White card, original PNG |
| SAIT logo | White card, official wordmark (same file as Halt & Restart) |
| No offensive / discriminatory content | Yes |
| No alcohol promotion | On campus · no alcohol |
| Submit as **Student Club** before posting | saitsa.com/Poster-Submission |
| Boards only; one poster per board | Posting rule, not a design field |

Student-club posters are required to carry the Saitsa Clubs logo unaltered. These sheets also include the official SAIT wordmark on a white card, matching Halt & Restart.

## Print

Open an HTML file in Chrome and Print → Save as PDF, paper size Tabloid / 11×17, margins none, background graphics on. Or:

```bash
./Events/AI-Agents/capture_posters.sh
```

Pass HTML filenames to print a subset (`./Events/AI-Agents/capture_posters.sh v4-toolkit.html v5-lime.html v6-nodes.html`).

Fonts are Inter / Inter Display / JetBrains Mono from `charter/fonts/`. Jellyfish, Saitsa Clubs logo, SAIT logo, and kit icons live in `assets/`.
