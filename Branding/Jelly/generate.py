#!/usr/bin/env python3
"""Fun expression versions of Jelly.

The body is the official mascot path (same proportions, lime→pink ribbon,
eyes as holes in the body). Only the two eye-hole subpaths change, plus a
few props that sit on or beside him.

    python3 "Branding/Jelly/generate.py"
"""

from __future__ import annotations

import html
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OFFICIAL = ROOT.parent / "Jellyfish Mascot Gradient.svg"

LIME = "#BAF837"
PINK = "#FA4A9E"
INK = "#030205"
PAPER = "#F9F9FA"
WINE = "#591337"
CYAN = "#7EC8FF"
OLIVE = "#95B747"

VB_W = 1177.209
VB_H = 1289.550

# Centres of the original eye holes (viewBox units).
LEFT = (434.9, 456.2)
RIGHT = (722.4, 456.0)

# Pupil subpaths in the official compound path (0 = silhouette).
EYE_INDEXES = (2, 3)


def official_parts() -> list[str]:
    src = OFFICIAL.read_text()
    m = re.search(r'<path[^>]*\sd="([^"]+)"', src)
    if not m:
        raise SystemExit(f"Could not read jellyfish path from {OFFICIAL}")
    parts = re.findall(r"M .*?Z", m.group(1))
    if len(parts) < 4:
        raise SystemExit(f"Expected compound path, got {len(parts)} subpaths")
    return parts


def n(v: float) -> str:
    s = f"{v:.2f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def pts_path(points: list[tuple[float, float]]) -> str:
    """Smooth closed curve through points (centripetal-ish cubic)."""
    if len(points) < 3:
        raise ValueError("need at least 3 points")
    m = len(points)
    d = [f"M {n(points[0][0])} {n(points[0][1])}"]
    for i in range(m):
        p0 = points[(i - 1) % m]
        p1 = points[i]
        p2 = points[(i + 1) % m]
        p3 = points[(i + 2) % m]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f"C {n(c1[0])} {n(c1[1])} {n(c2[0])} {n(c2[1])} {n(p2[0])} {n(p2[1])}")
    d.append("Z")
    return " ".join(d)


def ellipse(cx: float, cy: float, rx: float, ry: float) -> str:
    k = 0.5522847498
    return (
        f"M {n(cx + rx)} {n(cy)} "
        f"C {n(cx + rx)} {n(cy + k * ry)} {n(cx + k * rx)} {n(cy + ry)} {n(cx)} {n(cy + ry)} "
        f"C {n(cx - k * rx)} {n(cy + ry)} {n(cx - rx)} {n(cy + k * ry)} {n(cx - rx)} {n(cy)} "
        f"C {n(cx - rx)} {n(cy - k * ry)} {n(cx - k * rx)} {n(cy - ry)} {n(cx)} {n(cy - ry)} "
        f"C {n(cx + k * rx)} {n(cy - ry)} {n(cx + rx)} {n(cy - k * ry)} {n(cx + rx)} {n(cy)} Z"
    )


def smile(cx: float, cy: float, r: float = 52, thick: float = 18) -> str:
    """Happy squint: a thick arc, ends up, middle down. Same eye, smaller opening."""
    a0, a1 = 0.42, math.pi - 0.42
    steps = 16
    # Circle centre sits above the eye so the arc passes through it.
    cy_c = cy - r * 0.42
    outer: list[tuple[float, float]] = []
    inner: list[tuple[float, float]] = []
    for i in range(steps + 1):
        t = a0 + (a1 - a0) * i / steps
        outer.append((cx + math.cos(t) * r, cy_c + math.sin(t) * r))
        inner.append((cx + math.cos(t) * (r - thick), cy_c + math.sin(t) * (r - thick)))
    return pts_path(outer + inner[::-1])


def heart(cx: float, cy: float, w: float = 40, h: float = 46) -> str:
    """Heart hole, point down, cleft at the top so it still reads small."""
    raw = [
        (0.50, 0.98),
        (0.08, 0.52),
        (0.00, 0.30),
        (0.14, 0.06),
        (0.34, 0.08),
        (0.50, 0.30),
        (0.66, 0.08),
        (0.86, 0.06),
        (1.00, 0.30),
        (0.92, 0.52),
    ]
    pts = [(cx + (x - 0.5) * 2 * w, cy + (y - 0.50) * 2 * h) for x, y in raw]
    return _poly(pts)


def _poly(points: list[tuple[float, float]]) -> str:
    d = [f"M {n(points[0][0])} {n(points[0][1])}"]
    for x, y in points[1:]:
        d.append(f"L {n(x)} {n(y)}")
    d.append("Z")
    return " ".join(d)


def sparkle(cx: float, cy: float, r: float = 40, inner: float = 13) -> str:
    """Four-point star, same idea as the kit spark, cut out of the body."""
    pts = []
    for i in range(8):
        ang = -math.pi / 2 + i * math.pi / 4
        rad = r if i % 2 == 0 else inner
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    return _poly(pts)


def cross_eye(cx: float, cy: float, arm: float = 30, thick: float = 8) -> str:
    """One X-shaped hole. A plus rotated, so the middle stays open."""
    a, t = arm, thick
    raw = [
        (t, t), (t, a), (-t, a), (-t, t),
        (-a, t), (-a, -t), (-t, -t), (-t, -a),
        (t, -a), (t, -t), (a, -t), (a, t),
    ]
    ang = math.pi / 4
    ca, sa = math.cos(ang), math.sin(ang)
    pts = [(cx + x * ca - y * sa, cy + x * sa + y * ca) for x, y in raw]
    return _poly(pts)


def both(shape) -> str:
    return shape(*LEFT) + " " + shape(*RIGHT)


def shift(dx: float, dy: float, shape) -> str:
    return shape(LEFT[0] + dx, LEFT[1] + dy) + " " + shape(RIGHT[0] + dx, RIGHT[1] + dy)


def open_eye(cx: float, cy: float) -> str:
    """Close to the original eye-hole size."""
    return ellipse(cx, cy, 36, 46)


def party_hat() -> str:
    """Small hat on the bell peak. Stays inside the official viewBox."""
    tip = (588, 4)
    left = (552, 46)
    right = (626, 46)
    hat = (
        f"M {n(tip[0])} {n(tip[1])} "
        f"C {n(570)} {n(8)} {n(548)} {n(28)} {n(left[0])} {n(left[1])} "
        f"L {n(right[0])} {n(right[1])} "
        f"C {n(630)} {n(28)} {n(606)} {n(8)} {n(tip[0])} {n(tip[1])} Z"
    )
    brim = ellipse(589, 46, 46, 10)
    pom = ellipse(588, 6, 8, 8)
    band = ellipse(588, 30, 16, 5)
    return (
        f'  <path fill="{PINK}" d="{hat}"/>\n'
        f'  <path fill="{LIME}" d="{brim}"/>\n'
        f'  <path fill="{LIME}" d="{pom}"/>\n'
        f'  <path fill="{PAPER}" d="{band}"/>'
    )


def tongue() -> str:
    """Short tongue in the gap under the bell, between the front ribbons."""
    d = (
        "M 572 514 "
        "C 570 532 566 552 574 566 "
        "C 580 576 596 576 602 564 "
        "C 610 550 606 532 604 516 "
        "C 594 522 582 522 572 514 Z"
    )
    return f'  <path fill="{PINK}" d="{d}"/>'


def bow() -> str:
    """Bow just outside the upper-left ribbon, touching the bell."""
    cx, cy = 286, 136
    left = ellipse(cx - 22, cy, 20, 14)
    right = ellipse(cx + 22, cy, 20, 14)
    knot = ellipse(cx, cy, 8, 8)
    tail_l = f"M {n(cx - 8)} {n(cy + 4)} C {n(cx - 18)} {n(cy + 18)} {n(cx - 28)} {n(cy + 16)} {n(cx - 34)} {n(cy + 28)} C {n(cx - 22)} {n(cy + 22)} {n(cx - 16)} {n(cy + 26)} {n(cx - 6)} {n(cy + 12)} Z"
    tail_r = f"M {n(cx + 8)} {n(cy + 4)} C {n(cx + 16)} {n(cy + 20)} {n(cx + 28)} {n(cy + 14)} {n(cx + 36)} {n(cy + 26)} C {n(cx + 24)} {n(cy + 20)} {n(cx + 16)} {n(cy + 24)} {n(cx + 6)} {n(cy + 12)} Z"
    return (
        f'  <path fill="{PINK}" d="{left}"/>\n'
        f'  <path fill="{PINK}" d="{right}"/>\n'
        f'  <path fill="{LIME}" d="{tail_l}"/>\n'
        f'  <path fill="{LIME}" d="{tail_r}"/>\n'
        f'  <path fill="{PAPER}" d="{knot}"/>'
    )


def _band(points: list[tuple[float, float]], thick: float) -> str:
    """Thick open stroke following a polyline, as one filled outline."""
    # Tangents and outward normals. `points` run left → right over the head,
    # so a left-facing normal (negative cross of the tangent with +y-down) points up/out.
    normals = []
    for i, (x, y) in enumerate(points):
        if i == 0:
            tx, ty = points[1][0] - x, points[1][1] - y
        elif i == len(points) - 1:
            tx, ty = x - points[i - 1][0], y - points[i - 1][1]
        else:
            tx = points[i + 1][0] - points[i - 1][0]
            ty = points[i + 1][1] - points[i - 1][1]
        length = math.hypot(tx, ty) or 1
        tx, ty = tx / length, ty / length
        normals.append((-ty, tx))
    outer = [(x + nx * thick, y + ny * thick) for (x, y), (nx, ny) in zip(points, normals)]
    inner = [(x - nx * thick, y - ny * thick) for (x, y), (nx, ny) in zip(points, normals)]
    return _poly(outer + inner[::-1])


def headphones() -> str:
    """Thin band in the margin over the bell, cups on the outer ribbons."""
    spine = [
        (196, 248),
        (260, 168),
        (360, 96),
        (470, 48),
        (588, 22),
        (706, 48),
        (816, 96),
        (916, 168),
        (980, 248),
    ]
    band = _band(spine, 11)
    cup_l = ellipse(196, 252, 26, 34)
    cup_r = ellipse(980, 252, 26, 34)
    pad_l = ellipse(208, 252, 12, 18)
    pad_r = ellipse(968, 252, 12, 18)
    return (
        f'  <path fill="{CYAN}" d="{band}"/>\n'
        f'  <path fill="{CYAN}" d="{cup_l}"/>\n'
        f'  <path fill="{CYAN}" d="{cup_r}"/>\n'
        f'  <path fill="{LIME}" d="{pad_l}"/>\n'
        f'  <path fill="{PINK}" d="{pad_r}"/>'
    )


# name, title, note, eye path (replaces both pupils), extra svg after the body
EXPRESSIONS: list[tuple[str, str, str, str, str]] = [
    (
        "happy",
        "Happy",
        "Smile-shaped eyes, still cut out of the body.",
        both(lambda cx, cy: smile(cx, cy)),
        "",
    ),
    (
        "wink",
        "Wink",
        "One eye open, one squeezed into a smile. Bow on the bell.",
        open_eye(*LEFT) + " " + smile(RIGHT[0], RIGHT[1]),
        bow(),
    ),
    (
        "whoa",
        "Whoa",
        "Rounder eyes, same spot on the body.",
        both(lambda cx, cy: ellipse(cx, cy, 40, 42)),
        "",
    ),
    (
        "sleepy",
        "Sleepy",
        "Heavy lids. The holes sit low in the same eyes.",
        both(lambda cx, cy: ellipse(cx, cy + 14, 36, 12)),
        "",
    ),
    (
        "hearts",
        "Hearts",
        "Heart-shaped holes where the eyes are.",
        both(lambda cx, cy: heart(cx, cy, 40, 46)),
        "",
    ),
    (
        "sparkle",
        "Sparkle",
        "Four-point eyes, same spark as the kit icon.",
        both(lambda cx, cy: sparkle(cx, cy, 42, 14)),
        "",
    ),
    (
        "side-eye",
        "Side-eye",
        "Both eyes slid toward the left.",
        shift(-18, 4, lambda cx, cy: ellipse(cx, cy, 28, 42)),
        "",
    ),
    (
        "unamused",
        "Unamused",
        "Flat lids.",
        both(lambda cx, cy: ellipse(cx, cy, 38, 9)),
        "",
    ),
    (
        "glitch",
        "Glitch",
        "X eyes. The club error face.",
        both(lambda cx, cy: cross_eye(cx, cy, 32, 8)),
        "",
    ),
    (
        "party",
        "Party",
        "Happy eyes and a lime-and-pink hat on the bell.",
        both(lambda cx, cy: smile(cx, cy)),
        party_hat(),
    ),
    (
        "blep",
        "Blep",
        "Eyes up, tongue out under the bell.",
        shift(0, -16, lambda cx, cy: ellipse(cx, cy, 34, 42)),
        tongue(),
    ),
    (
        "tunes",
        "Tunes",
        "Headphones over the bell. Eyes half-closed.",
        both(lambda cx, cy: ellipse(cx, cy - 2, 34, 15)),
        headphones(),
    ),
]


def svg_doc(label: str, body_d: str, extra: str) -> str:
    extra_block = f"\n{extra}" if extra else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VB_W} {VB_H}" '
        f'role="img" aria-label="{html.escape(label)}" fill="none">\n'
        "  <defs>\n"
        '    <linearGradient id="uni-jelly" x1="10%" y1="4%" x2="90%" y2="92%" gradientUnits="objectBoundingBox">\n'
        f'      <stop offset="0%" stop-color="{LIME}"/>\n'
        f'      <stop offset="42%" stop-color="{LIME}"/>\n'
        f'      <stop offset="58%" stop-color="{PINK}"/>\n'
        f'      <stop offset="100%" stop-color="{PINK}"/>\n'
        "    </linearGradient>\n"
        "  </defs>\n"
        f'  <path fill="url(#uni-jelly)" fill-rule="evenodd" d="{body_d}"/>'
        f"{extra_block}\n"
        "</svg>\n"
    )


PNG_WIDTH = 1870  # same width as Jellyfish Mascot Gradient Transparent.png


def write_preview(items: list[tuple[str, str, str]]) -> None:
    cards = []
    for filename, title, note in items:
        png = "png/" + filename.replace(".svg", ".png")
        cards.append(
            "<figure class=\"dark\">"
            f'<div class="frame"><img src="{html.escape(filename)}" alt="{html.escape(title)}"></div>'
            f"<figcaption><strong>{html.escape(title)}</strong>"
            f"<code>{html.escape(filename)}</code>"
            f"<code>{html.escape(png)}</code>"
            f'<p class="note">{html.escape(note)}</p></figcaption></figure>'
        )
    original = (
        '<figure class="dark"><div class="frame">'
        '<img src="../Jellyfish%20Mascot%20Gradient.svg" alt="Jelly, official">'
        "</div><figcaption><strong>Jelly</strong>"
        "<code>Jellyfish Mascot Gradient.svg</code>"
        '<p class="note">Official mascot. Eyes are holes in the body.</p></figcaption></figure>'
    )
    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Jelly — fun versions</title>
<style>
  @font-face {{ font-family: "Inter"; src: url("../../charter/fonts/Inter-Regular.ttf") format("truetype"); font-weight: 400; }}
  @font-face {{ font-family: "Inter"; src: url("../../charter/fonts/Inter-SemiBold.ttf") format("truetype"); font-weight: 600; }}
  @font-face {{ font-family: "Inter Display"; src: url("../../charter/fonts/InterDisplay-Bold.ttf") format("truetype"); font-weight: 700; }}
  @font-face {{ font-family: "JetBrains Mono"; src: url("../../charter/fonts/JetBrainsMono-Regular.ttf") format("truetype"); font-weight: 400; }}
  :root {{
    --paper: #F9F9FA; --olive: #95B747; --ink: #030205; --pink: #FA4A9E;
    --wine: #591337; --lime: #BAF837; --cyan: #7EC8FF;
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; background: #14040c; color: var(--paper); font-family: Inter, sans-serif; }}
  header {{ padding: 48px 32px 8px; max-width: 1200px; margin: 0 auto; }}
  h1 {{
    font-family: "Inter Display", Inter, sans-serif; font-size: 42px; letter-spacing: -0.05em;
    text-transform: uppercase; margin: 0 0 8px; line-height: 0.9;
  }}
  .sub {{ font-family: "JetBrains Mono", monospace; font-size: 13px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--lime); }}
  p.lede {{ max-width: 66ch; color: rgba(249,249,250,.72); line-height: 1.5; }}
  .grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 18px; max-width: 1200px; margin: 0 auto 24px; padding: 0 32px;
  }}
  figure {{ margin: 0; border: 1px solid rgba(186,248,55,.18); background: rgba(3,2,5,.55); }}
  .frame {{
    aspect-ratio: 1; display: grid; place-items: center; padding: 18px; background: var(--ink);
  }}
  img {{ max-width: 100%; max-height: 240px; display: block; }}
  figcaption {{ padding: 10px 12px 14px; border-top: 1px solid rgba(186,248,55,.12); }}
  figcaption strong {{ display: block; font-size: 13px; }}
  figcaption code {{
    display: block; margin-top: 4px; font-family: "JetBrains Mono", monospace;
    font-size: 10px; color: var(--olive); word-break: break-all;
  }}
  .note {{ margin: 6px 0 0; font-size: 12px; color: rgba(249,249,250,.55); }}
  footer {{
    max-width: 1200px; margin: 32px auto; padding: 0 32px 64px;
    font-family: "JetBrains Mono", monospace; font-size: 11px; color: rgba(249,249,250,.45);
    letter-spacing: 0.08em;
  }}
</style>
</head>
<body>
<header>
  <div class="sub">Unnatural Intelligence · Jelly</div>
  <h1>Fun<br>versions</h1>
  <p class="lede">Same jellyfish, same proportions. The eyes stay holes in the body. Expressions swap those holes; a hat, bow, tongue, or headphones sit on top and do not reshape him. Transparent PNGs, same width as the official mascot raster, are in <code>png/</code>.</p>
</header>
<div class="grid">
{original}
{''.join(cards)}
</div>
<footer>UNNATURALINTELLIGENCE.CLUB — regenerate with python3 generate.py</footer>
</body>
</html>
"""
    (ROOT / "preview.html").write_text(html_doc)


def rasterize_pngs() -> int:
    """Transparent PNGs beside the SVGs, same width as the official mascot raster."""
    import cairosvg
    from PIL import Image
    import io

    out = ROOT / "png"
    out.mkdir(parents=True, exist_ok=True)
    count = 0
    for svg_path in sorted(ROOT.glob("jelly-*.svg")):
        raw = cairosvg.svg2png(url=str(svg_path), output_width=PNG_WIDTH)
        im = Image.open(io.BytesIO(raw))
        dest = out / f"{svg_path.stem}.png"
        im.save(dest, "PNG", optimize=True)
        count += 1
        print(f"wrote png/{dest.name} {im.size[0]}x{im.size[1]} {im.mode}")
    return count


def main() -> None:
    parts = official_parts()
    body = " ".join(p for i, p in enumerate(parts) if i not in EYE_INDEXES)
    written: list[tuple[str, str, str]] = []
    for slug, title, note, eyes, extra in EXPRESSIONS:
        filename = f"jelly-{slug}.svg"
        label = f"Jelly, {title.lower()}"
        doc = svg_doc(label, f"{body} {eyes}", extra)
        (ROOT / filename).write_text(doc)
        written.append((filename, title, note))
        print(f"wrote {filename}")
    write_preview(written)
    n_png = rasterize_pngs()
    print(f"wrote preview.html ({len(written)} versions, {n_png} pngs)")


if __name__ == "__main__":
    main()
