#!/usr/bin/env python3
"""75 × 25 mm exec nameplates for laser / rotary engraving.

Black fill = engrave. Optional red hairline = cut the plate outline.
Type is outlined (Inter Display + JetBrains Mono). Daniil is omitted.

    python3 "Branding/Design Templates/Name-Tags/engrave/generate.py"
"""

from __future__ import annotations

import html
import re
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[3]
OFFICIAL_SRC = REPO / "Branding" / "Jellyfish Mascot Gradient.svg"
FONTS = REPO / "charter" / "fonts"

PAPER = "#F9F9FA"
INK = "#030205"
LIME = "#BAF837"
PINK = "#FA4A9E"
CYAN = "#7EC8FF"

JELLY_VB_W = 1177.209
JELLY_VB_H = 1289.550

# Physical plate.
W = 75.0
H = 25.0
CORNER = 2.0
MARGIN = 1.75
JELLY_H = 18.0
JELLY_GAP = 2.25
CUT = "#FF0000"
ENGRAVE = "#000000"

EXECS = [
    {"name": "Hailey", "role": "President"},
    {"name": "Pierre", "role": "Vice President"},
    {"name": "Alexander", "role": "Treasurer"},
    {"name": "Deema", "role": "Community Manager"},
    {"name": "Logan", "role": "Community Manager"},
]


def official_d() -> str:
    src = OFFICIAL_SRC.read_text()
    m = re.search(r'<path[^>]*\sd="([^"]+)"', src)
    if not m:
        raise SystemExit(f"Could not read jellyfish path from {OFFICIAL_SRC}")
    return m.group(1)


D = official_d()


class Font:
    def __init__(self, path: Path):
        self.tt = TTFont(path)
        self.gs = self.tt.getGlyphSet()
        self.cmap = self.tt.getBestCmap()
        self.upem = self.tt["head"].unitsPerEm

    def shape(self, text: str, size: float, *, tracking: float = 0):
        s = size / self.upem
        x = 0.0
        chunks: list[str] = []
        for ch in text:
            if ch == " ":
                space = self.gs[self.cmap.get(ord(" "), "space")]
                x += space.width * s + tracking
                continue
            name = self.cmap.get(ord(ch))
            if name is None:
                x += size * 0.45
                continue
            g = self.gs[name]
            pen = SVGPathPen(self.gs)
            tpen = TransformPen(pen, (s, 0, 0, -s, x, 0))
            g.draw(tpen)
            d = round_path(pen.getCommands())
            if d:
                chunks.append(d)
            x += g.width * s + tracking
        return " ".join(chunks), x

    def ink_bounds(
        self, text: str, size: float, *, tracking: float = 0
    ) -> tuple[float, float, float, float, float]:
        s = size / self.upem
        x = 0.0
        minx = miny = 1e9
        maxx = maxy = -1e9
        for ch in text:
            if ch == " ":
                space = self.gs[self.cmap.get(ord(" "), "space")]
                x += space.width * s + tracking
                continue
            name = self.cmap.get(ord(ch))
            if name is None:
                x += size * 0.45
                continue
            g = self.gs[name]
            pen = BoundsPen(self.gs)
            tpen = TransformPen(pen, (s, 0, 0, -s, x, 0))
            g.draw(tpen)
            if pen.bounds:
                a, b, c, d = pen.bounds
                minx, miny = min(minx, a), min(miny, b)
                maxx, maxy = max(maxx, c), max(maxy, d)
            x += g.width * s + tracking
        if minx > maxx:
            return 0.0, -size * 0.72, x, 0.0, x
        return minx, miny, maxx, maxy, x


def round_path(d: str) -> str:
    def repl(m: re.Match) -> str:
        n = float(m.group(0))
        r = round(n, 2)
        if r == int(r):
            return str(int(r))
        return f"{r:.2f}".rstrip("0").rstrip(".")

    return re.sub(r"-?\d+\.?\d*(?:e-?\d+)?", repl, d, flags=re.I)


DISPLAY = Font(FONTS / "InterDisplay-Bold.ttf")
MONO = Font(FONTS / "JetBrainsMono-Bold.ttf")


def jelly_group(x: float, y: float, height: float, fill: str) -> str:
    s = height / JELLY_VB_H
    return (
        f'  <g transform="translate({x:.3f} {y:.3f}) scale({s:.6f})">\n'
        f'    <path fill="{fill}" fill-rule="evenodd" d="{D}"/>\n'
        f"  </g>"
    )


def fit_name(text: str, max_w: float, start: float = 8.15, floor: float = 5.6) -> float:
    size = start
    while size > floor:
        _a, _b, _c, _d, adv = DISPLAY.ink_bounds(text, size)
        if adv <= max_w:
            return round(size, 2)
        size -= 0.05
    return floor


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def layout(person: dict) -> dict:
    name = person["name"].upper()
    role = person["role"].upper()
    jelly_w = JELLY_H * (JELLY_VB_W / JELLY_VB_H)
    jelly_x = MARGIN
    jelly_y = (H - JELLY_H) / 2
    text_x = jelly_x + jelly_w + JELLY_GAP
    text_w = W - MARGIN - text_x

    name_size = fit_name(name, text_w)
    role_size = 2.52
    role_track = 0.14
    _n0, nmin, _n1, nmax, name_adv = DISPLAY.ink_bounds(name, name_size)
    while True:
        _r0, rmin, _r1, rmax, role_adv = MONO.ink_bounds(
            role, role_size, tracking=role_track
        )
        if role_adv <= text_w or role_size <= 1.9:
            break
        role_size -= 0.04
        role_track = max(0.04, role_track - 0.01)

    name_d, _ = DISPLAY.shape(name, name_size)
    role_d, _ = MONO.shape(role, role_size, tracking=role_track)

    rule_h = 0.28
    gap_name_rule = 1.18
    gap_rule_role = 1.22
    stack_top = nmin  # negative
    stack_h = (nmax - nmin) + gap_name_rule + rule_h + gap_rule_role + (rmax - rmin)
    origin_y = (H - stack_h) / 2 - stack_top
    name_y = origin_y
    rule_y = name_y + nmax + gap_name_rule
    role_y = rule_y + rule_h + gap_rule_role - rmin
    rule_w = max(name_adv, role_adv)

    return {
        "person": person,
        "name": name,
        "role": role,
        "jelly": (jelly_x, jelly_y, JELLY_H, jelly_w),
        "text_x": text_x,
        "name_d": name_d,
        "name_y": name_y,
        "name_size": name_size,
        "name_adv": name_adv,
        "role_d": role_d,
        "role_y": role_y,
        "role_size": role_size,
        "role_adv": role_adv,
        "rule_y": rule_y,
        "rule_h": rule_h,
        "rule_w": rule_w,
    }


def cut_outline() -> str:
    return (
        f'  <g id="cut" fill="none" stroke="{CUT}" stroke-width="0.1">\n'
        f'    <rect x="0.05" y="0.05" width="{W - 0.1}" height="{H - 0.1}" rx="{CORNER}"/>\n'
        f"  </g>"
    )


def artwork(lay: dict, *, jelly: str, name: str, role: str, rule: str) -> str:
    jx, jy, jh, _jw = lay["jelly"]
    tx = lay["text_x"]
    return "\n".join(
        [
            jelly_group(jx, jy, jh, jelly),
            f'  <g id="type" transform="translate({tx:.3f} 0)">',
            f'    <path fill="{name}" d="{lay["name_d"]}" transform="translate(0 {lay["name_y"]:.3f})"/>',
            f'    <rect x="0" y="{lay["rule_y"]:.3f}" width="{lay["rule_w"]:.3f}" height="{lay["rule_h"]:.3f}" fill="{rule}"/>',
            f'    <path fill="{role}" d="{lay["role_d"]}" transform="translate(0 {lay["role_y"]:.3f})"/>',
            "  </g>",
        ]
    )


def svg_doc(inner: str, *, label: str, extra_attr: str = "") -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<!-- Unnatural Intelligence exec nameplate. 75mm × 25mm.\n"
        "     Black fill = engrave. Red hairline = optional cut.\n"
        "     Regenerated by generate.py. Daniil is not in this set. -->\n"
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}" '
        f'width="{W:g}mm" height="{H:g}mm" role="img" '
        f'aria-label="{html.escape(label)}" fill="none"{extra_attr}>\n'
        f"{inner.rstrip()}\n"
        "</svg>\n"
    )


def engrave_svg(lay: dict) -> str:
    person = lay["person"]
    inner = (
        f'  <g id="engrave">\n{artwork(lay, jelly=ENGRAVE, name=ENGRAVE, role=ENGRAVE, rule=ENGRAVE)}\n  </g>\n'
        + cut_outline()
    )
    return svg_doc(inner, label=f"{person['name']} — {person['role']} · engrave")


def proof_svg(lay: dict) -> str:
    person = lay["person"]
    inner = "\n".join(
        [
            "  <defs>",
            '    <linearGradient id="uni-jelly" x1="10%" y1="4%" x2="90%" y2="92%" gradientUnits="objectBoundingBox">',
            f'      <stop offset="0%" stop-color="{LIME}"/>',
            f'      <stop offset="42%" stop-color="{LIME}"/>',
            f'      <stop offset="58%" stop-color="{PINK}"/>',
            f'      <stop offset="100%" stop-color="{PINK}"/>',
            "    </linearGradient>",
            "  </defs>",
            f'  <rect width="{W:g}" height="{H:g}" rx="{CORNER}" fill="{INK}"/>',
            artwork(lay, jelly="url(#uni-jelly)", name=PAPER, role=LIME, rule=LIME),
        ]
    )
    return svg_doc(inner, label=f"{person['name']} — {person['role']} · proof")


def sheet_svg(lays: list[dict], *, kind: str) -> str:
    gap = 8.0
    n = len(lays)
    sh = n * H + (n - 1) * gap
    blocks = [
        f'<!-- Sheet of {n} exec nameplates, {kind}, 75mm × 25mm each, {gap:g}mm gap. -->'
    ]
    for i, lay in enumerate(lays):
        y = i * (H + gap)
        if kind == "engrave":
            body = (
                f'    <g id="engrave-{slug(lay["person"]["name"])}">\n'
                f"{artwork(lay, jelly=ENGRAVE, name=ENGRAVE, role=ENGRAVE, rule=ENGRAVE)}\n"
                "    </g>\n"
                f'    <g fill="none" stroke="{CUT}" stroke-width="0.1">\n'
                f'      <rect x="0.05" y="0.05" width="{W - 0.1}" height="{H - 0.1}" rx="{CORNER}"/>\n'
                "    </g>"
            )
        else:
            gid = f"uni-jelly-{i}"
            body = "\n".join(
                [
                    "    <defs>",
                    f'      <linearGradient id="{gid}" x1="10%" y1="4%" x2="90%" y2="92%" gradientUnits="objectBoundingBox">',
                    f'        <stop offset="0%" stop-color="{LIME}"/>',
                    f'        <stop offset="42%" stop-color="{LIME}"/>',
                    f'        <stop offset="58%" stop-color="{PINK}"/>',
                    f'        <stop offset="100%" stop-color="{PINK}"/>',
                    "      </linearGradient>",
                    "    </defs>",
                    f'    <rect width="{W:g}" height="{H:g}" rx="{CORNER}" fill="{INK}"/>',
                    artwork(lay, jelly=f"url(#{gid})", name=PAPER, role=LIME, rule=LIME),
                ]
            )
        blocks.append(f'  <g transform="translate(0 {y:.3f})">\n{body}\n  </g>')
    inner = "\n".join(blocks)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {sh:g}" '
        f'width="{W:g}mm" height="{sh:g}mm" role="img" '
        f'aria-label="Unnatural Intelligence exec nameplates · {kind}" fill="none">\n'
        f"{inner}\n"
        "</svg>\n"
    )


def preview_html(lays: list[dict]) -> str:
    cards = []
    for lay in lays:
        p = lay["person"]
        s = slug(p["name"])
        cards.append(
            f"""    <article class="card">
      <header>
        <h2>{html.escape(p["name"])}</h2>
        <p>{html.escape(p["role"])}</p>
      </header>
      <div class="pair">
        <figure>
          <img src="proof/{s}.svg" width="75" height="25" alt="{html.escape(p["name"])} proof plate">
          <figcaption>Proof · ink plate</figcaption>
        </figure>
        <figure class="film">
          <img src="{s}.svg" width="75" height="25" alt="{html.escape(p["name"])} engrave film">
          <figcaption>Engrave · black = laser</figcaption>
        </figure>
      </div>
    </article>"""
        )
    roster = ", ".join(f"{p['name']} ({p['role']})" for p in EXECS)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Exec nameplates — Unnatural Intelligence</title>
<style>
  @font-face {{ font-family: "Inter"; src: url("../../../../charter/fonts/Inter-Regular.ttf") format("truetype"); font-weight: 400; }}
  @font-face {{ font-family: "Inter Display"; src: url("../../../../charter/fonts/InterDisplay-Bold.ttf") format("truetype"); font-weight: 700; }}
  @font-face {{ font-family: "JetBrains Mono"; src: url("../../../../charter/fonts/JetBrainsMono-Regular.ttf") format("truetype"); font-weight: 400; }}
  :root {{
    --paper: {PAPER}; --ink: {INK}; --lime: {LIME}; --pink: {PINK}; --cyan: {CYAN};
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; }}
  body {{
    background: #14040c; color: var(--paper);
    font-family: Inter, sans-serif; min-height: 100%;
  }}
  .rail {{
    max-width: 920px; margin: 28px auto 8px; padding: 0 24px;
    font-family: "JetBrains Mono", ui-monospace, monospace;
    font-size: 12px; line-height: 1.55; color: rgba(249,249,250,.72);
  }}
  h1 {{
    font-family: "Inter Display", Inter, sans-serif;
    font-size: 28px; letter-spacing: -0.04em; margin: 0 0 8px; color: var(--paper);
  }}
  .rail strong {{ color: var(--lime); }}
  .rail code {{ color: var(--pink); }}
  .gallery {{
    max-width: 920px; margin: 12px auto 48px; padding: 0 24px;
    display: grid; gap: 28px;
  }}
  .card header {{
    display: flex; align-items: baseline; gap: 12px; margin-bottom: 12px;
  }}
  .card h2 {{
    font-family: "Inter Display", Inter, sans-serif;
    font-size: 18px; margin: 0; letter-spacing: -0.03em;
  }}
  .card header p {{
    margin: 0; font-family: "JetBrains Mono", ui-monospace, monospace;
    font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--lime);
  }}
  .pair {{ display: flex; flex-wrap: wrap; gap: 22px; align-items: flex-start; }}
  figure {{ margin: 0; }}
  figure img {{
    display: block; width: 75mm; height: 25mm;
    filter: drop-shadow(0 18px 28px rgba(0,0,0,.5));
  }}
  .film {{
    padding: 8px; background: #efefef; border-radius: 10px;
  }}
  .film img {{ background: #fff; border-radius: 2mm; }}
  figcaption {{
    margin-top: 8px; font-family: "JetBrains Mono", ui-monospace, monospace;
    font-size: 10px; letter-spacing: 0.12em; text-transform: uppercase;
    color: rgba(249,249,250,.5);
  }}
  .sheet {{
    max-width: 920px; margin: 0 auto 64px; padding: 0 24px;
  }}
  .sheet img {{
    width: 75mm; height: auto;
    filter: drop-shadow(0 18px 28px rgba(0,0,0,.5));
  }}
  .sheet .film-sheet {{
    padding: 12px; background: #efefef; border-radius: 12px; width: fit-content;
  }}
  .sheet .film-sheet img {{ filter: none; background: #fff; }}
  @media print {{
    body {{ background: #fff; color: #000; }}
    .rail, figcaption, .sheet h2, .card header {{ color: #000; }}
    figure img {{ filter: none; }}
  }}
</style>
</head>
<body>
  <div class="rail">
    <h1>Exec nameplates</h1>
    <p><strong>75 × 25 mm</strong> engraving templates. Official jellyfish mascot, first name, club title. Daniil is omitted. Black fill = engrave. Red hairline = optional cut.</p>
    <p>Roster: {html.escape(roster)}. Rebuild with <code>python3 generate.py</code>. Import the per-person SVGs into LightBurn, xTool, or a trophy shop.</p>
  </div>
  <section class="gallery">
{chr(10).join(cards)}
  </section>
  <section class="sheet">
    <h2 class="rail" style="padding:0;margin:0 0 12px">Batch sheet · proof</h2>
    <img src="sheet-proof.svg" alt="All five exec nameplates, colour proof">
    <h2 class="rail" style="padding:0;margin:28px 0 12px">Batch sheet · engrave film</h2>
    <div class="film-sheet">
      <img src="sheet-engrave.svg" alt="All five exec nameplates, black engrave film">
    </div>
  </section>
</body>
</html>
"""


def readme() -> str:
    names = "\n".join(
        f"- `{slug(p['name'])}.svg` — {p['name']}, {p['role']}" for p in EXECS
    )
    return f"""# Exec nameplates (75 × 25 mm)

Laser / rotary engraving templates for the human execs. **Daniil is not in this set.**

Each plate is **75 mm × 25 mm** with a 2 mm corner radius:

- jellyfish mascot on the left (official filled path)
- first name in Inter Display
- club title in JetBrains Mono
- hairline rule between name and title

## Files

Engrave films (black = engrave, red hairline = optional cut):

{names}
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
"""


def main() -> None:
    if any(p["name"].lower() == "daniil" for p in EXECS):
        raise SystemExit("Daniil is excluded from the engraved exec set.")
    proof_dir = ROOT / "proof"
    proof_dir.mkdir(parents=True, exist_ok=True)
    lays = [layout(p) for p in EXECS]
    for lay in lays:
        s = slug(lay["person"]["name"])
        (ROOT / f"{s}.svg").write_text(engrave_svg(lay))
        (proof_dir / f"{s}.svg").write_text(proof_svg(lay))
        print(
            f"{lay['person']['name']:10} name {lay['name_size']:.2f}mm  "
            f"title {lay['role_size']:.2f}mm  adv {lay['name_adv']:.1f}/{lay['role_adv']:.1f}"
        )
    (ROOT / "sheet-engrave.svg").write_text(sheet_svg(lays, kind="engrave"))
    (ROOT / "sheet-proof.svg").write_text(sheet_svg(lays, kind="proof"))
    (ROOT / "preview.html").write_text(preview_html(lays))
    (ROOT / "README.md").write_text(readme())
    print(f"Wrote {len(lays)} plates + sheets under {ROOT}")


if __name__ == "__main__":
    main()
