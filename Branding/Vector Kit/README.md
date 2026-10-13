# Vector kit

Self-contained SVGs for Unnatural Intelligence. Palette matches the 6×3 ft banner and Halt & Restart posters.

| Token | Hex |
| --- | --- |
| Paper | `#F9F9FA` |
| Olive | `#95B747` |
| Ink | `#030205` |
| Pink | `#FA4A9E` |
| Wine | `#591337` |
| Lime | `#BAF837` |
| Cyan (glitch) | `#7EC8FF` |

## Folders

- `marks/` — official jellyfish (filled outline) in each colour, plus a simplified mini mark for 16–64px
- `lockups/` — wordmark, jellyfish + type, and fifteen Unnatural Games marks (shear, spine, stripe, seal, slice, steps, cross, monogram, fan, ticket, crest, swim, overlap, quad, badge)
- `icons/` — 64px tools (token, prompt, halt, restart, workflow…) boxed and plain
- `stickers/` — speech-bubble quotes, icon die-cuts, tickets, jellyfish vinyl, a 3.5×1.55 in laptop wordmark, and 3 in circles
- `badges/` — member / exec / event chips
- `avatars/` — 512px social icons
- `social/` — Instagram, story, and banner templates
- `fact-bars/` — when / where / type / who strips. `strip.svg` sits on ink. `strip-clear.svg`, `scaffold.svg`, and the single bars have no background
- `frames/` — dashed ticket frame, plus transparent 11×17 tabloid borders
- `patterns/` — ink-backed tiles, transparent grid overlays, 11×17 alignment grids, wash, glitch bars
- `palette/` — swatches, `colors.json`, and `tokens.css`
- `png/` — sample raster of every SVG (same relative paths)

Open [`preview.html`](preview.html) to browse everything. Plain (unboxed) icon variants live next to the boxed files as `*-plain.svg` and are omitted from the catalog. PNG samples live under `png/` (for example `png/marks/jellyfish-gradient.png`).

## Regenerate

```bash
pip install fonttools cairosvg
python3 "Branding/Vector Kit/generate.py"
```

Fonts are Inter / Inter Display / JetBrains Mono (SIL OFL) from `charter/fonts/`. Wordmarks are outlined, so files do not need the fonts installed.

The official jellyfish path is loaded from `Branding/Jellyfish Mascot Gradient.svg`.
