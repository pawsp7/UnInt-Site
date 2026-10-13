# Exec nameplates (75 × 25 mm)

Laser / rotary engraving templates for the human execs. **Daniil is not in this set.**

Each plate is **75 mm × 25 mm** with a 2 mm corner radius:

- jellyfish mascot on the left (official filled path)
- first name in Inter Display
- club title in JetBrains Mono
- hairline rule between name and title

## Files

Engrave films (black = engrave, red hairline = optional cut):

- `hailey.svg` — Hailey, President
- `pierre.svg` — Pierre, Vice President
- `alexander.svg` — Alexander, Treasurer
- `deema.svg` — Deema, Community Manager
- `logan.svg` — Logan, Community Manager
- `sheet-engrave.svg` — all five stacked with 8 mm gaps

Colour proofs (ink plate, lime–pink jellyfish) live in `proof/`. Open `preview.html` to compare both at actual size.

## Send to a shop or laser

1. Use the root `*.svg` files, not the proofs.
2. Artwork is already outlined — no fonts required.
3. Set **black fill** to engrave. Ignore or delete the **red** rounded rectangle if the blanks are already cut.
4. Import at 100%. The SVG `width` / `height` are millimetres.

Regenerate:

```bash
pip install fonttools
python3 "Branding/Design Templates/Name-Tags/engrave/generate.py"
```
