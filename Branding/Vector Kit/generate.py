#!/usr/bin/env python3
"""Generate the Unnatural Intelligence vector brand kit.

Reads the official jellyfish path from Branding/Jellyfish Mascot Gradient.svg
and writes self-contained SVGs under this folder. Run from anywhere:

    python3 "Branding/Vector Kit/generate.py"
"""

from __future__ import annotations

import html
import io
import json
import math
import re
import shutil
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
OFFICIAL_SRC = REPO / "Branding" / "Jellyfish Mascot Gradient.svg"
FONTS = REPO / "charter" / "fonts"
PNG_ROOT = ROOT / "png"

PAPER = "#F9F9FA"
OLIVE = "#95B747"
INK = "#030205"
PINK = "#FA4A9E"
WINE = "#591337"
LIME = "#BAF837"
CYAN = "#7EC8FF"

JELLY_VB_W = 1177.209
JELLY_VB_H = 1289.550

GRADIENT_DEFS = f"""
  <linearGradient id="uni-jelly" x1="10%" y1="4%" x2="90%" y2="92%" gradientUnits="objectBoundingBox">
    <stop offset="0%" stop-color="{LIME}"/>
    <stop offset="42%" stop-color="{LIME}"/>
    <stop offset="58%" stop-color="{PINK}"/>
    <stop offset="100%" stop-color="{PINK}"/>
  </linearGradient>
""".strip()

MANIFEST: list[dict] = []


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

    def shape(self, text: str, size: float, *, tracking: float = 0, scale_x: float = 1.0):
        """Return (combined svg path d, width, height) with baseline at y=0, y-down."""
        s = size / self.upem
        x = 0.0
        chunks: list[str] = []
        for ch in text:
            if ch == " ":
                space = self.gs[self.cmap.get(ord(" "), "space")]
                x += space.width * s * scale_x + tracking
                continue
            name = self.cmap.get(ord(ch))
            if name is None:
                x += size * 0.45 * scale_x
                continue
            g = self.gs[name]
            pen = SVGPathPen(self.gs)
            tpen = TransformPen(pen, (s * scale_x, 0, 0, -s, x, 0))
            g.draw(tpen)
            d = round_path(pen.getCommands())
            if d:
                chunks.append(d)
            x += g.width * s * scale_x + tracking
        return " ".join(chunks), x, size

    def ink_bounds(
        self, text: str, size: float, *, tracking: float = 0, scale_x: float = 1.0
    ) -> tuple[float, float, float, float, float]:
        """Return (min_x, min_y, max_x, max_y, advance) with baseline at y=0, y-down."""
        s = size / self.upem
        x = 0.0
        minx = miny = 1e9
        maxx = maxy = -1e9
        for ch in text:
            if ch == " ":
                space = self.gs[self.cmap.get(ord(" "), "space")]
                x += space.width * s * scale_x + tracking
                continue
            name = self.cmap.get(ord(ch))
            if name is None:
                x += size * 0.45 * scale_x
                continue
            g = self.gs[name]
            pen = BoundsPen(self.gs)
            tpen = TransformPen(pen, (s * scale_x, 0, 0, -s, x, 0))
            g.draw(tpen)
            if pen.bounds:
                a, b, c, d = pen.bounds
                minx, miny = min(minx, a), min(miny, b)
                maxx, maxy = max(maxx, c), max(maxy, d)
            x += g.width * s * scale_x + tracking
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
INTER_BOLD = Font(FONTS / "Inter-Bold.ttf")
INTER_SEMI = Font(FONTS / "Inter-SemiBold.ttf")
INTER_MED = Font(FONTS / "Inter-Medium.ttf")
INTER_REG = Font(FONTS / "Inter-Regular.ttf")
JB_BOLD = Font(FONTS / "JetBrainsMono-Bold.ttf")
JB_REG = Font(FONTS / "JetBrainsMono-Regular.ttf")


def svg(viewbox: str, inner: str, *, w: str | None = None, h: str | None = None, label: str = "") -> str:
    size = ""
    if w:
        size += f' width="{w}"'
    if h:
        size += f' height="{h}"'
    aria = f' role="img" aria-label="{html.escape(label)}"' if label else ""
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}"{size}{aria} fill="none">\n'
        f"{inner.rstrip()}\n"
        f"</svg>\n"
    )


def write(rel: str, content: str, *, group: str, title: str, note: str = "") -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    MANIFEST.append({"file": rel, "group": group, "title": title, "note": note})


def jelly_path(fill: str, extra: str = "") -> str:
    return f'  <path fill="{fill}" fill-rule="evenodd"{extra} d="{D}"/>'


def jelly_mark(fill: str, *, bg: str | None = None, defs: str = "", pad: float = 48) -> str:
    vb = f"{-pad} {-pad} {JELLY_VB_W + pad * 2} {JELLY_VB_H + pad * 2}"
    parts = ["  <defs>", f"    {GRADIENT_DEFS}"]
    if defs:
        parts.append(defs)
    parts.append("  </defs>")
    if bg:
        parts.append(
            f'  <rect x="{-pad}" y="{-pad}" width="{JELLY_VB_W + pad * 2}" '
            f'height="{JELLY_VB_H + pad * 2}" fill="{bg}"/>'
        )
    parts.append(jelly_path(fill))
    return svg(vb, "\n".join(parts), label="Unnatural Intelligence jellyfish")


def glow_filter(fid: str = "glow") -> str:
    return f"""
    <filter id="{fid}" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur in="SourceGraphic" stdDeviation="18" result="b"/>
      <feColorMatrix in="b" type="matrix" values="
        1 0 0 0 0
        0 1 0 0 0
        0 0 1 0 0
        0 0 0 0.55 0" result="g"/>
      <feMerge>
        <feMergeNode in="g"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    """.strip()


def wash_bg(w: float, h: float) -> str:
    return f"""
  <defs>
    {GRADIENT_DEFS}
    <radialGradient id="wine-wash" cx="8%" cy="50%" r="70%">
      <stop offset="0%" stop-color="{WINE}"/>
      <stop offset="70%" stop-color="{INK}"/>
    </radialGradient>
    <pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse">
      <path d="M36 0H0V36" fill="none" stroke="{LIME}" stroke-width="1.1" opacity="0.18"/>
    </pattern>
    <pattern id="grid-pink" width="36" height="36" patternUnits="userSpaceOnUse">
      <path d="M36 0H0V36" fill="none" stroke="{PINK}" stroke-width="1.1" opacity="0.16"/>
    </pattern>
    <linearGradient id="grid-fade" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#fff"/>
      <stop offset="55%" stop-color="#fff" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <mask id="grid-mask">
      <rect width="{w}" height="{h}" fill="url(#grid-fade)"/>
    </mask>
  </defs>
  <rect width="{w}" height="{h}" fill="{INK}"/>
  <rect width="{w}" height="{h}" fill="url(#wine-wash)"/>
  <rect width="{w}" height="{h}" fill="url(#grid)" mask="url(#grid-mask)"/>
  <rect width="{w}" height="{h}" fill="url(#grid-pink)" opacity="0.55"/>
    """.strip()


def jelly_at(x: float, y: float, height: float, fill: str, extra: str = "") -> str:
    s = height / JELLY_VB_H
    return (
        f'  <g transform="translate({x:.2f} {y:.2f}) scale({s:.5f})" {extra}>\n'
        f"{jelly_path(fill)}\n"
        f"  </g>"
    )


def jelly_centered(cx: float, cy: float, height: float, fill: str, extra: str = "") -> str:
    """Place the official jellyfish so its viewBox is centered on (cx, cy)."""
    width = height * (JELLY_VB_W / JELLY_VB_H)
    return jelly_at(cx - width / 2, cy - height / 2, height, fill, extra=extra)


# ---------------------------------------------------------------------------
# Simplified jellyfish (small-size mark). Stroke construction matching the
# official mascot: dome, five oral loops, eight tentacles.
# ---------------------------------------------------------------------------

MINI_DOME = "M38 98 C38 42 68 26 100 26 C132 26 162 42 162 98"
MINI_ORAL = (
    "M38 98 Q48 124 58 100 Q70 128 84 98 Q100 126 116 98 "
    "Q130 128 142 100 Q152 124 162 98"
)
MINI_TENTACLES = [
    ("M48 120 C28 140 24 164 38 182 C46 194 38 204 28 210", 9),
    ("M64 132 C48 158 46 184 58 202 C64 212 52 222 44 226", 8),
    ("M80 146 C74 172 72 192 78 208", 7),
    ("M94 148 C88 188 84 218 92 230 C96 236 86 238 80 236", 11),
    ("M106 148 C112 188 116 218 108 230 C104 236 114 238 120 236", 11),
    ("M120 146 C126 172 128 192 122 208", 7),
    ("M136 132 C152 158 154 184 142 202 C136 212 148 222 156 226", 8),
    ("M152 120 C172 140 176 164 162 182 C154 194 162 204 172 210", 9),
]


def mini_jellyfish(color: str, *, width: float = 11) -> str:
    parts = [
        f'  <g fill="none" stroke="{color}" stroke-linecap="round" stroke-linejoin="round">',
        f'    <path stroke-width="{width}" d="{MINI_DOME}"/>',
        f'    <path stroke-width="{width}" d="{MINI_ORAL}"/>',
    ]
    for d, w in MINI_TENTACLES:
        parts.append(f'    <path stroke-width="{w}" d="{d}"/>')
    parts.append("  </g>")
    return "\n".join(parts)


def path_text(d: str, fill: str, extra: str = "") -> str:
    return f'  <path fill="{fill}"{extra} d="{d}"/>'


def fact_column_widths(canvas: float = 1100, pad: float = 42, gap: float = 10) -> list[float]:
    """Column widths for the when / where / type / who strip. 100 units = 1 in."""
    weights = (1.05, 1.2, 1.35, 1.15)
    avail = canvas - pad * 2 - gap * (len(weights) - 1)
    total = sum(weights)
    return [weight / total * avail for weight in weights]


def spark_mark(cx: float, cy: float, radius: float) -> str:
    scale = radius / 20
    cols = (LIME, PINK, OLIVE, CYAN, LIME, PINK, OLIVE, CYAN)
    parts = []
    for i, col in enumerate(cols):
        parts.append(
            f'  <g transform="translate({cx:.1f} {cy:.1f}) rotate({i * 45}) scale({scale:.4f})">'
            f'<path d="M0 -20 L6.5 -4 L0 0 L-6.5 -4 Z" fill="{col}"/></g>'
        )
    return "\n".join(parts)


def icon_at(inner: str, cx: float, cy: float, scale: float, origin: float = 32.0) -> str:
    """Place a 64px kit icon so its (origin, origin) lands on (cx, cy)."""
    return (
        f'  <g transform="translate({cx:.2f} {cy:.2f}) scale({scale:.4f}) '
        f'translate({-origin:.2f} {-origin:.2f})">\n'
        f"{inner.rstrip()}\n"
        f"  </g>"
    )


def restart_mark(cx: float, cy: float, r: float, color: str, stroke: float) -> str:
    """Clockwise refresh arrow. Filled head sits in the top-right gap."""
    a0 = math.radians(32)
    a1 = math.radians(322)
    x0 = cx + r * math.cos(a0)
    y0 = cy + r * math.sin(a0)
    x1 = cx + r * math.cos(a1)
    y1 = cy + r * math.sin(a1)
    tx, ty = -math.sin(a1), math.cos(a1)
    px, py = -ty, tx
    head_len = stroke * 2.6
    head_w = stroke * 1.55
    # Pull the arc end back so it meets the triangle base.
    bx = x1
    by = y1
    arc = (
        f'  <path d="M{x0:.2f} {y0:.2f} A {r:.2f} {r:.2f} 0 1 1 {bx:.2f} {by:.2f}" '
        f'fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round"/>'
    )
    tip_x = x1 + tx * head_len * 0.55
    tip_y = y1 + ty * head_len * 0.55
    b1x = bx + px * head_w
    b1y = by + py * head_w
    b2x = bx - px * head_w
    b2y = by - py * head_w
    head = (
        f'  <polygon points="{tip_x:.2f},{tip_y:.2f} {b1x:.2f},{b1y:.2f} {b2x:.2f},{b2y:.2f}" '
        f'fill="{color}"/>'
    )
    return f"{arc}\n{head}"


def centered_line(
    font: Font,
    text: str,
    size: float,
    y: float,
    fill: str,
    canvas_w: float,
    *,
    tracking: float = 0,
    scale_x: float = 1.0,
) -> str:
    d, tw, _ = font.shape(text, size, tracking=tracking, scale_x=scale_x)
    return f'  <g transform="translate({(canvas_w - tw) / 2:.1f} {y:.1f})">{path_text(d, fill)}</g>'


def text_at_ink_center(
    font: Font,
    text: str,
    size: float,
    cx: float,
    cy: float,
    fill: str,
    *,
    tracking: float = 0,
    scale_x: float = 1.0,
) -> str:
    """Place outlined text so its ink box is centered on (cx, cy)."""
    d, _, _ = font.shape(text, size, tracking=tracking, scale_x=scale_x)
    minx, miny, maxx, maxy, _ = font.ink_bounds(text, size, tracking=tracking, scale_x=scale_x)
    tx = cx - (minx + maxx) / 2
    ty = cy - (miny + maxy) / 2
    return f'  <g transform="translate({tx:.2f} {ty:.2f})">{path_text(d, fill)}</g>'


# ---------------------------------------------------------------------------
# Marks
# ---------------------------------------------------------------------------

def build_marks() -> None:
    write(
        "marks/jellyfish-gradient.svg",
        jelly_mark("url(#uni-jelly)"),
        group="Marks",
        title="Jellyfish — lime→pink gradient",
        note="Official mascot path with the club gradient.",
    )
    for name, color, title in [
        ("jellyfish-paper", PAPER, "paper"),
        ("jellyfish-ink", INK, "ink"),
        ("jellyfish-lime", LIME, "lime"),
        ("jellyfish-pink", PINK, "pink"),
        ("jellyfish-olive", OLIVE, "olive"),
        ("jellyfish-wine", WINE, "wine"),
        ("jellyfish-cyan", CYAN, "cyan"),
    ]:
        write(
            f"marks/{name}.svg",
            jelly_mark(color),
            group="Marks",
            title=f"Jellyfish — {title}",
        )
    write(
        "marks/jellyfish-currentColor.svg",
        jelly_mark("currentColor"),
        group="Marks",
        title="Jellyfish — currentColor",
        note="Inherits CSS color. Use in sites and slides.",
    )

    glow = svg(
        f"-80 -80 {JELLY_VB_W + 160} {JELLY_VB_H + 160}",
        f"  <defs>\n    {GRADIENT_DEFS}\n    {glow_filter()}\n  </defs>\n"
        f'  <g filter="url(#glow)">\n{jelly_path("url(#uni-jelly)")}\n  </g>',
        label="Unnatural Intelligence jellyfish with glow",
    )
    write("marks/jellyfish-glow.svg", glow, group="Marks", title="Jellyfish — gradient + glow")

    for name, bg, fill, title in [
        ("jellyfish-on-ink", INK, "url(#uni-jelly)", "gradient on ink"),
        ("jellyfish-on-ink-paper", INK, PAPER, "paper on ink"),
        ("jellyfish-on-lime", LIME, INK, "ink on lime"),
        ("jellyfish-on-pink", PINK, PAPER, "paper on pink"),
        ("jellyfish-on-wine", WINE, LIME, "lime on wine"),
        ("jellyfish-on-paper", PAPER, INK, "ink on paper"),
    ]:
        write(
            f"marks/{name}.svg",
            jelly_mark(fill, bg=bg, pad=80),
            group="Marks",
            title=f"Jellyfish — {title}",
        )

    write(
        "marks/jellyfish-mini.svg",
        svg(
            "0 0 200 248",
            mini_jellyfish("currentColor"),
            label="Unnatural Intelligence jellyfish (simplified)",
        ),
        group="Marks",
        title="Jellyfish mini — currentColor",
        note="Simplified construction for 16–64px (favicon, nav, buttons).",
    )
    write(
        "marks/jellyfish-mini-gradient.svg",
        svg(
            "0 0 200 248",
            f"  <defs>\n    {GRADIENT_DEFS}\n  </defs>\n" + mini_jellyfish("url(#uni-jelly)"),
            label="Unnatural Intelligence jellyfish (simplified, gradient)",
        ),
        group="Marks",
        title="Jellyfish mini — gradient",
    )
    # 32px favicon: lime mini on ink
    s = 26 / 248
    fx = (32 - 200 * s) / 2
    fy = (32 - 248 * s) / 2
    write(
        "marks/favicon.svg",
        svg(
            "0 0 32 32",
            f'  <rect width="32" height="32" rx="7" fill="{INK}"/>\n'
            f'  <g transform="translate({fx:.2f} {fy:.2f}) scale({s:.5f})">\n'
            + mini_jellyfish(LIME)
            + "\n  </g>",
            label="Unnatural Intelligence favicon",
        ),
        group="Marks",
        title="Favicon — lime mini on ink",
        note="32×32. Drop in as favicon.svg.",
    )


# ---------------------------------------------------------------------------
# Lockups + wordmarks
# ---------------------------------------------------------------------------

def glitch_word(d: str, fill: str, dx: float = 3.2, dy: float = 1.1) -> str:
    return (
        f'  <g opacity="0.85" transform="translate({-dx},{dy})">{path_text(d, CYAN)}</g>\n'
        f'  <g opacity="0.85" transform="translate({dx},{-dy})">{path_text(d, PINK)}</g>\n'
        f"{path_text(d, fill)}"
    )


def build_lockups() -> None:
    tracking = -3.4
    scale_x = 0.84
    size = 72
    d1, w1, _ = DISPLAY.shape("UNNATURAL", size, tracking=tracking, scale_x=scale_x)
    d2, w2, _ = DISPLAY.shape("INTELLIGENCE", size, tracking=tracking, scale_x=scale_x)
    tag_d, tag_w, _ = INTER_MED.shape(
        "GENERATED BY AI  ·  PERFECTED BY HUMANS",
        11,
        tracking=2.6,
        scale_x=1.0,
    )
    line_w = max(w1, w2)
    jelly_h = 248
    jelly_w = jelly_h * (JELLY_VB_W / JELLY_VB_H)
    gap = 36
    left = 28
    type_x = left + jelly_w + gap
    type_y = 78
    W = type_x + line_w + 36
    H = 300

    def lockup(
        bg: str | None,
        fill: str,
        tag_fill: str,
        glitch: bool,
        wine: bool = False,
        jelly_fill: str = "url(#uni-jelly)",
    ) -> str:
        parts = ["  <defs>", f"    {GRADIENT_DEFS}", "  </defs>"]
        if bg:
            parts.append(f'  <rect width="{W:.1f}" height="{H}" fill="{bg}"/>')
        if wine and bg:
            parts.insert(
                2,
                f'  <radialGradient id="lw"><stop offset="0%" stop-color="{WINE}"/><stop offset="100%" stop-color="{INK}"/></radialGradient>',
            )
            parts.append(f'  <rect width="{W:.1f}" height="{H}" fill="url(#lw)"/>')
        parts.append(jelly_at(left, 26, jelly_h, jelly_fill))
        parts.append(f'  <g transform="translate({type_x:.1f} {type_y})">')
        if glitch:
            parts.append(glitch_word(d1, fill))
        else:
            parts.append(path_text(d1, fill))
        parts.append("  </g>")
        parts.append(f'  <g transform="translate({type_x:.1f} {type_y + 78})">')
        if glitch:
            parts.append(glitch_word(d2, fill, dx=3.6, dy=1.2))
        else:
            parts.append(path_text(d2, fill))
        parts.append("  </g>")
        parts.append(f'  <g transform="translate({type_x:.1f} {type_y + 132})">')
        parts.append(path_text(tag_d, tag_fill))
        parts.append("  </g>")
        return svg(f"0 0 {W:.1f} {H}", "\n".join(parts), label="Unnatural Intelligence lockup")

    write(
        "lockups/horizontal-dark.svg",
        lockup(INK, PAPER, "rgba(249,249,250,0.78)", True, wine=True),
        group="Lockups",
        title="Horizontal lockup — dark / glitch",
    )
    write(
        "lockups/horizontal-ink.svg",
        lockup(INK, PAPER, "rgba(249,249,250,0.78)", False),
        group="Lockups",
        title="Horizontal lockup — dark, clean",
    )
    write(
        "lockups/horizontal-light.svg",
        lockup(PAPER, INK, "#5A5A5A", False),
        group="Lockups",
        title="Horizontal lockup — light",
    )
    write(
        "lockups/horizontal-lime.svg",
        lockup(LIME, INK, INK, False, jelly_fill=INK),
        group="Lockups",
        title="Horizontal lockup — lime",
    )
    write(
        "lockups/horizontal-wine.svg",
        lockup(WINE, LIME, "rgba(186,248,55,0.72)", False, jelly_fill=LIME),
        group="Lockups",
        title="Horizontal lockup — wine",
    )

    # Stacked
    s_size = 56
    sd1, sw1, _ = DISPLAY.shape("UNNATURAL", s_size, tracking=-2.6, scale_x=0.84)
    sd2, sw2, _ = DISPLAY.shape("INTELLIGENCE", s_size, tracking=-2.6, scale_x=0.84)
    stag, stw, _ = INTER_MED.shape("GENERATED BY AI  ·  PERFECTED BY HUMANS", 9, tracking=2.0)
    jh = 168
    jw = jh * (JELLY_VB_W / JELLY_VB_H)
    SW = max(sw1, sw2, jw) + 48
    SH = 340
    jx = (SW - jw) / 2
    tx = (SW - max(sw1, sw2)) / 2

    def stacked(bg: str, fill: str, tag: str, glitch: bool) -> str:
        parts = [
            "  <defs>",
            f"    {GRADIENT_DEFS}",
            "  </defs>",
            f'  <rect width="{SW:.1f}" height="{SH}" fill="{bg}"/>',
            jelly_at(jx, 12, jh, "url(#uni-jelly)"),
            f'  <g transform="translate({tx:.1f} 196)">',
        ]
        parts.append(glitch_word(sd1, fill) if glitch else path_text(sd1, fill))
        parts.append("  </g>")
        parts.append(f'  <g transform="translate({tx:.1f} 258)">')
        parts.append(glitch_word(sd2, fill) if glitch else path_text(sd2, fill))
        parts.append("  </g>")
        parts.append(f'  <g transform="translate({(SW - stw) / 2:.1f} 300)">')
        parts.append(path_text(stag, tag))
        parts.append("  </g>")
        return svg(f"0 0 {SW:.1f} {SH}", "\n".join(parts), label="Unnatural Intelligence stacked lockup")

    write("lockups/stacked-dark.svg", stacked(INK, PAPER, "rgba(249,249,250,0.78)", True), group="Lockups", title="Stacked lockup — dark / glitch")
    write("lockups/stacked-light.svg", stacked(PAPER, INK, "#5A5A5A", False), group="Lockups", title="Stacked lockup — light")

    # Wordmark only
    wm_w = max(w1, w2) + 24
    wm_h = 180
    wm = [
        "  <defs/>",
        f'  <g transform="translate(12 70)">{glitch_word(d1, PAPER)}</g>',
        f'  <g transform="translate(12 148)">{glitch_word(d2, PAPER)}</g>',
    ]
    write(
        "lockups/wordmark-glitch.svg",
        svg(f"0 0 {wm_w:.1f} {wm_h}", "\n".join(wm), label="Unnatural Intelligence wordmark"),
        group="Lockups",
        title="Wordmark — glitch (transparent)",
    )
    wm_ink = [
        f'  <g transform="translate(12 70)">{path_text(d1, INK)}</g>',
        f'  <g transform="translate(12 148)">{path_text(d2, INK)}</g>',
    ]
    write(
        "lockups/wordmark-ink.svg",
        svg(f"0 0 {wm_w:.1f} {wm_h}", "\n".join(wm_ink), label="Unnatural Intelligence wordmark"),
        group="Lockups",
        title="Wordmark — ink",
    )

    url_d, url_w, _ = JB_BOLD.shape("UNNATURALINTELLIGENCE.CLUB", 14, tracking=1.8)
    sait_d, sait_w, _ = JB_REG.shape("SAIT STUDENT CLUB", 11, tracking=2.4)
    bar_w = max(url_w, sait_w) + 8
    url_svg = [
        f'  <rect x="0" y="18" width="28" height="4" rx="2" fill="{LIME}"/>',
        f'  <rect x="30" y="18" width="18" height="4" rx="2" fill="{PINK}"/>',
        f'  <g transform="translate(58 28)">{path_text(url_d, PAPER)}</g>',
        f'  <g transform="translate(58 48)">{path_text(sait_d, OLIVE)}</g>',
    ]
    write(
        "lockups/url.svg",
        svg(f"0 0 {58 + bar_w:.1f} 64", "\n".join(url_svg), label="unnaturalintelligence.club"),
        group="Lockups",
        title="URL lockup",
    )

    # Circle monogram
    mono = [
        "  <defs>",
        f"    {GRADIENT_DEFS}",
        "  </defs>",
        f'  <circle cx="128" cy="128" r="128" fill="{INK}"/>',
        f'  <circle cx="128" cy="128" r="122" fill="none" stroke="{LIME}" stroke-width="3" opacity="0.35"/>',
        jelly_centered(128, 128, 210, "url(#uni-jelly)"),
    ]
    write(
        "lockups/monogram-circle.svg",
        svg("0 0 256 256", "\n".join(mono), label="Unnatural Intelligence monogram"),
        group="Lockups",
        title="Circle monogram",
    )
    rounded = [
        "  <defs>",
        f"    {GRADIENT_DEFS}",
        "  </defs>",
        f'  <rect width="256" height="256" rx="56" fill="{INK}"/>',
        jelly_centered(128, 128, 210, "url(#uni-jelly)"),
    ]
    write(
        "lockups/monogram-rounded.svg",
        svg("0 0 256 256", "\n".join(rounded), label="Unnatural Intelligence app icon"),
        group="Lockups",
        title="Rounded-square monogram / app icon",
    )


# ---------------------------------------------------------------------------
# Icons
# ---------------------------------------------------------------------------

def icon_svg(inner: str, label: str) -> str:
    return svg(
        "0 0 64 64",
        f'  <rect width="64" height="64" rx="14" fill="{INK}"/>\n{inner}',
        label=label,
    )


def icon_plain(inner: str, label: str) -> str:
    return svg("0 0 64 64", inner, label=label)


def build_icons() -> None:
    icons = []

    token = f"""
  <circle cx="32" cy="32" r="18" fill="none" stroke="{LIME}" stroke-width="3"/>
  <rect x="24" y="24" width="16" height="16" rx="3" fill="none" stroke="{PINK}" stroke-width="2.5"/>
  <circle cx="32" cy="32" r="3" fill="{LIME}"/>
"""
    icons.append(("token", token, "Token"))

    spark = ""
    cols = (LIME, PINK, OLIVE, CYAN, LIME, PINK, OLIVE, CYAN)
    for i, col in enumerate(cols):
        ang = i * 45
        spark += (
            f'  <g transform="translate(32 32) rotate({ang})">'
            f'<path d="M0 -20 L6.5 -4 L0 0 L-6.5 -4 Z" fill="{col}"/></g>\n'
        )
    icons.append(("spark", spark, "Spark"))

    prompt = f"""
  <path d="M18 20 L28 32 L18 44" fill="none" stroke="{LIME}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="34" y="38" width="14" height="4" rx="1.5" fill="{PINK}"/>
"""
    icons.append(("prompt", prompt, "Prompt"))

    halt = f"""
  <rect x="20" y="16" width="8" height="32" rx="2" fill="{LIME}"/>
  <rect x="36" y="16" width="8" height="32" rx="2" fill="{LIME}"/>
"""
    icons.append(("halt", halt, "Halt"))

    restart = "\n" + restart_mark(32, 32, 14, PINK, 3.5) + "\n"
    icons.append(("restart", restart, "Restart"))

    workflow = f"""
  <circle cx="14" cy="32" r="6" fill="{OLIVE}"/>
  <circle cx="32" cy="32" r="6" fill="{LIME}"/>
  <circle cx="50" cy="32" r="6" fill="{PINK}"/>
  <path d="M20 32h6M38 32h6" stroke="{PAPER}" stroke-width="2.5" stroke-linecap="round"/>
"""
    icons.append(("workflow", workflow, "Workflow"))

    neural = f"""
  <circle cx="32" cy="14" r="5" fill="{LIME}"/>
  <circle cx="14" cy="32" r="5" fill="{OLIVE}"/>
  <circle cx="50" cy="32" r="5" fill="{PINK}"/>
  <circle cx="24" cy="50" r="5" fill="{CYAN}"/>
  <circle cx="40" cy="50" r="5" fill="{PAPER}"/>
  <path d="M32 19 L14 27 M32 19 L50 27 M14 37 L24 45 M50 37 L40 45 M27 50h10" stroke="{PAPER}" stroke-width="1.6" opacity="0.7"/>
"""
    icons.append(("neural", neural, "Neural"))

    tentacle = f"""
  <defs>
    <linearGradient id="tgrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{LIME}"/>
      <stop offset="100%" stop-color="{PINK}"/>
    </linearGradient>
  </defs>
  <path d="M16 18 C30 24 20 38 32 44 C44 50 40 56 50 58" fill="none" stroke="url(#tgrad)" stroke-width="7" stroke-linecap="round"/>
  <path d="M22 14 C26 28 34 30 36 46" fill="none" stroke="url(#tgrad)" stroke-width="4" stroke-linecap="round" opacity="0.7"/>
"""
    icons.append(("tentacle", tentacle, "Tentacle"))

    glitch = f"""
  <rect x="12" y="20" width="40" height="8" fill="{CYAN}" transform="translate(-2 1)"/>
  <rect x="12" y="20" width="40" height="8" fill="{PINK}" transform="translate(2 -1)"/>
  <rect x="12" y="20" width="40" height="8" fill="{PAPER}"/>
  <rect x="16" y="34" width="28" height="6" fill="{CYAN}" transform="translate(2 1)"/>
  <rect x="16" y="34" width="28" height="6" fill="{PINK}" transform="translate(-2 -1)"/>
  <rect x="16" y="34" width="28" height="6" fill="{LIME}"/>
"""
    icons.append(("glitch", glitch, "Glitch"))

    bubble = f"""
  <rect x="10" y="12" width="44" height="30" rx="12" fill="{LIME}" stroke="{PINK}" stroke-width="3"/>
  <path d="M22 42 L18 54 L30 42" fill="{LIME}" stroke="{PINK}" stroke-width="3" stroke-linejoin="round"/>
"""
    icons.append(("bubble", bubble, "Speech bubble"))

    meter = f"""
  <rect x="10" y="28" width="44" height="10" rx="5" fill="#1a0812" stroke="{OLIVE}" stroke-width="2"/>
  <rect x="12" y="30" width="16" height="6" rx="3" fill="{LIME}"/>
  <path d="M18 18h2v6h-2zM32 16h2v8h-2zM46 18h2v6h-2z" fill="{PINK}" opacity="0.8"/>
"""
    icons.append(("meter", meter, "Lean tokens"))

    commit = f"""
  <circle cx="32" cy="32" r="8" fill="none" stroke="{LIME}" stroke-width="3"/>
  <path d="M32 12v12M32 40v12" stroke="{PINK}" stroke-width="3" stroke-linecap="round"/>
"""
    icons.append(("commit", commit, "Commit"))

    mask = f"""
  <path d="M16 40 C16 20 48 20 48 40 C48 50 40 54 32 54 C24 54 16 50 16 40Z" fill="{INK}" stroke="{PAPER}" stroke-width="2"/>
  <path d="M32 22 V54" stroke="{PAPER}" stroke-width="1.5" opacity="0.5"/>
  <circle cx="24" cy="36" r="3" fill="{LIME}"/>
  <circle cx="40" cy="36" r="3" fill="{PINK}"/>
"""
    icons.append(("mask", mask, "Human finish"))

    node = f"""
  <rect x="18" y="18" width="28" height="28" rx="6" fill="none" stroke="{LIME}" stroke-width="2.5"/>
  <circle cx="32" cy="32" r="5" fill="{PINK}"/>
  <circle cx="18" cy="18" r="3.5" fill="{OLIVE}"/>
  <circle cx="46" cy="18" r="3.5" fill="{CYAN}"/>
  <circle cx="46" cy="46" r="3.5" fill="{PAPER}"/>
  <circle cx="18" cy="46" r="3.5" fill="{LIME}"/>
"""
    icons.append(("node", node, "Node"))

    ticket = f"""
  <path d="M10 22 h44 a6 6 0 0 1 0 20 H10 a6 6 0 0 1 0 -20Z" fill="{LIME}"/>
  <path d="M24 22 v20" stroke="{INK}" stroke-width="2" stroke-dasharray="2 3"/>
  <circle cx="17" cy="32" r="3" fill="{INK}"/>
"""
    icons.append(("ticket", ticket, "Ticket"))

    for slug, inner, title in icons:
        write(
            f"icons/{slug}.svg",
            icon_svg(inner, f"{title} icon"),
            group="Icons",
            title=title,
        )
        write(
            f"icons/{slug}-plain.svg",
            icon_plain(inner, f"{title} icon"),
            group="Icons",
            title=f"{title} (plain)",
        )

    # Sprite of boxed icons
    cells = [(slug, inner, title) for slug, inner, title in icons]
    cols = 5
    rows = math.ceil(len(cells) / cols)
    sw, sh = cols * 80 + 16, rows * 80 + 16
    sprite = [f'  <rect width="{sw}" height="{sh}" fill="{INK}"/>']
    for i, (slug, inner, title) in enumerate(cells):
        c, r = i % cols, i // cols
        x, y = 16 + c * 80, 16 + r * 80
        sprite.append(f'  <g id="icon-{slug}" transform="translate({x} {y})">')
        sprite.append(inner)
        sprite.append("  </g>")
    write(
        "icons/sprite.svg",
        svg(f"0 0 {sw} {sh}", "\n".join(sprite), label="Unnatural Intelligence icon sprite"),
        group="Icons",
        title="Icon sprite",
        note="All boxed icons on one sheet.",
    )


# ---------------------------------------------------------------------------
# Stickers
# ---------------------------------------------------------------------------

# Same tail proportions as stickers/speech-bubble.svg (r=72: base 54, tip 70 down / 26 left).
BUBBLE_TAIL_BASE = 54 / 72
BUBBLE_TAIL_H = 70 / 72
BUBBLE_TAIL_DX = 26 / 72


def pill_bubble(x: float, y: float, w: float, h: float, tail: bool = True) -> str:
    """Lime pill with a pink stroke. With a tail, one path like the large die-cut."""
    r = h / 2
    attrs = f'fill="{LIME}" stroke="{PINK}" stroke-width="5"'
    if not tail:
        return f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" {attrs}/>'
    base = min(w - 2 * r, BUBBLE_TAIL_BASE * r)
    bot = y + h
    al = x + r
    ar = al + base
    tip_x = al - BUBBLE_TAIL_DX * r
    tip_y = bot + BUBBLE_TAIL_H * r
    d = (
        f"M{al:.2f} {bot:.2f} L{tip_x:.2f} {tip_y:.2f} L{ar:.2f} {bot:.2f} "
        f"H{x + w - r:.2f} "
        f"A{r:.2f} {r:.2f} 0 0 0 {x + w:.2f} {y + r:.2f} "
        f"A{r:.2f} {r:.2f} 0 0 0 {x + w - r:.2f} {y:.2f} "
        f"H{x + r:.2f} "
        f"A{r:.2f} {r:.2f} 0 0 0 {x:.2f} {y + r:.2f} "
        f"A{r:.2f} {r:.2f} 0 0 0 {al:.2f} {bot:.2f} Z"
    )
    return (
        f'  <path {attrs} stroke-linejoin="round" stroke-linecap="round" d="{d}"/>'
    )


def sticker_card(w: float, h: float, inner: str, grid: bool = True) -> str:
    parts = [
        "  <defs>",
        f"    {GRADIENT_DEFS}",
        f'    <pattern id="sg" width="28" height="28" patternUnits="userSpaceOnUse">',
        f'      <path d="M28 0H0V28" fill="none" stroke="{OLIVE}" stroke-width="1" opacity="0.28"/>',
        "    </pattern>",
        "  </defs>",
        f'  <rect width="{w}" height="{h}" rx="18" fill="{INK}"/>',
    ]
    if grid:
        parts.append(f'  <rect width="{w}" height="{h}" rx="18" fill="url(#sg)"/>')
        parts.append(
            jelly_at(w * 0.42, h * 0.02, h * 1.08, OLIVE, extra='opacity="0.18"')
        )
    parts.append(inner)
    return svg(f"0 0 {w} {h}", "\n".join(parts))


def build_stickers() -> None:
    # specify or it will improvise — recreation of the existing raster sticker
    W, H = 512, 560
    msg = "specify or it will improvise"
    d, tw, _ = JB_BOLD.shape(msg, 16)
    bw, bh = round(tw + 40, 2), 40
    bx = round((W - bw) / 2, 2)
    by = 28
    jh = 380
    jw = jh * (JELLY_VB_W / JELLY_VB_H)
    jx = (W - jw) / 2
    inner = "\n".join(
        [
            "  <defs>",
            f"    {GRADIENT_DEFS}",
            '    <pattern id="sg" width="28" height="28" patternUnits="userSpaceOnUse">',
            f'      <path d="M28 0H0V28" fill="none" stroke="{OLIVE}" stroke-width="1" opacity="0.28"/>',
            "    </pattern>",
            f'    <clipPath id="card"><rect width="{W}" height="{H}" rx="18"/></clipPath>',
            "  </defs>",
            f'  <g clip-path="url(#card)">',
            f'    <rect width="{W}" height="{H}" fill="{INK}"/>',
            f'    <rect width="{W}" height="{H}" fill="url(#sg)"/>',
            jelly_at(W * 0.30, H * -0.06, H * 1.18, OLIVE, extra='opacity="0.22"'),
            jelly_at(jx, 96, jh, PAPER),
            "  </g>",
            pill_bubble(bx, by, bw, bh),
            text_at_ink_center(JB_BOLD, msg, 16, bx + bw / 2, by + bh / 2, INK),
        ]
    )
    write(
        "stickers/specify-or-it-will-improvise.svg",
        svg(f"0 0 {W} {H}", inner, label="specify or it will improvise"),
        group="Stickers",
        title="specify or it will improvise",
        note="Vector remake of the existing raster sticker.",
    )

    def quote_sticker(filename: str, text: str, title: str, size: float = 18) -> None:
        _, tw, _ = INTER_BOLD.shape(text, size, tracking=-0.4)
        w = max(tw + 72, 280)
        bx, by, bw, bh = 16.0, 28.0, w - 32, 64.0
        h = math.ceil(by + bh + BUBBLE_TAIL_H * (bh / 2) + 16)
        inner = "\n".join(
            [
                pill_bubble(bx, by, bw, bh, tail=True),
                text_at_ink_center(INTER_BOLD, text, size, bx + bw / 2, by + bh / 2, INK, tracking=-0.4),
            ]
        )
        write(
            f"stickers/{filename}.svg",
            sticker_card(w, h, inner, grid=False),
            group="Stickers",
            title=title,
        )

    quote_sticker("i-hate-it-but-its-useful", "i hate it but its so useful", "i hate it but its so useful", 16)
    quote_sticker("stay-ahead", "stay ahead of the curve", "stay ahead of the curve", 16)
    quote_sticker("lean-tokens", "lean tokens, human finish", "lean tokens, human finish", 15)
    quote_sticker("untapped", "untapped  ·  integrated  ·  human", "untapped · integrated · human", 13)

    d1, w1, _ = INTER_SEMI.shape("GENERATED BY AI", 14, tracking=3.2)
    d2, w2, _ = INTER_SEMI.shape("PERFECTED BY HUMANS", 14, tracking=3.2)
    w = max(w1, w2) + 80
    inner = "\n".join(
        [
            f'  <rect x="12" y="12" width="{w-24:.1f}" height="96" rx="12" fill="{INK}" stroke="{LIME}" stroke-width="3"/>',
            f'  <g transform="translate({(w - w1) / 2:.1f} 48)">{path_text(d1, LIME)}</g>',
            f'  <g transform="translate({(w - w2) / 2:.1f} 78)">{path_text(d2, PINK)}</g>',
        ]
    )
    write(
        "stickers/generated-by-ai.svg",
        svg(f"0 0 {w:.1f} 120", inner, label="Generated by AI · Perfected by humans"),
        group="Stickers",
        title="Generated by AI · Perfected by humans",
    )

    def ink_sheet(w: float, h: float, rx: float, pid: str) -> list[str]:
        return [
            "  <defs>",
            f"    {GRADIENT_DEFS}",
            f'    <pattern id="{pid}" width="28" height="28" patternUnits="userSpaceOnUse">',
            f'      <path d="M28 0H0V28" fill="none" stroke="{OLIVE}" stroke-width="1" opacity="0.28"/>',
            "    </pattern>",
            f'    <clipPath id="{pid}-clip"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>',
            "  </defs>",
            f'  <g clip-path="url(#{pid}-clip)">',
            f'    <rect width="{w}" height="{h}" fill="{INK}"/>',
            f'    <rect width="{w}" height="{h}" fill="url(#{pid})"/>',
        ]

    # Circle: TAKE A TOKEN (clubs-expo language + token icon)
    token_icon = f"""
  <circle cx="32" cy="32" r="18" fill="none" stroke="{LIME}" stroke-width="3"/>
  <rect x="24" y="24" width="16" height="16" rx="3" fill="none" stroke="{PINK}" stroke-width="2.5"/>
  <circle cx="32" cy="32" r="3" fill="{LIME}"/>
"""
    S = 400
    take = ink_sheet(S, S, S / 2, "tok")
    take += [
        "  </g>",
        icon_at(token_icon, 200, 176, 4.1),
        centered_line(JB_BOLD, "TAKE A TOKEN", 18, 304, PAPER, S, tracking=2.4),
    ]
    write(
        "stickers/take-a-token.svg",
        svg(f"0 0 {S} {S}", "\n".join(take), label="Take a token"),
        group="Stickers",
        title="Take a token",
        note="Circular vinyl. Token icon from the kit.",
    )

    # if it drifts, halt — same family as specify
    W, H = 512, 560
    msg = "if it drifts, halt"
    d, tw, _ = JB_BOLD.shape(msg, 18)
    bw, bh = round(tw + 40, 2), 42
    bx = round((W - bw) / 2, 2)
    by = 28
    jh = 380
    jw = jh * (JELLY_VB_W / JELLY_VB_H)
    jx = (W - jw) / 2
    inner = "\n".join(
        [
            "  <defs>",
            f"    {GRADIENT_DEFS}",
            '    <pattern id="driftg" width="28" height="28" patternUnits="userSpaceOnUse">',
            f'      <path d="M28 0H0V28" fill="none" stroke="{OLIVE}" stroke-width="1" opacity="0.28"/>',
            "    </pattern>",
            f'    <clipPath id="drift"><rect width="{W}" height="{H}" rx="18"/></clipPath>',
            "  </defs>",
            '  <g clip-path="url(#drift)">',
            f'    <rect width="{W}" height="{H}" fill="{INK}"/>',
            f'    <rect width="{W}" height="{H}" fill="url(#driftg)"/>',
            jelly_at(W * 0.30, H * -0.06, H * 1.18, OLIVE, extra='opacity="0.22"'),
            jelly_at(jx, 96, jh, PAPER),
            "  </g>",
            pill_bubble(bx, by, bw, bh),
            text_at_ink_center(JB_BOLD, msg, 18, bx + bw / 2, by + bh / 2, INK),
        ]
    )
    write(
        "stickers/if-it-drifts-halt.svg",
        svg(f"0 0 {W} {H}", inner, label="if it drifts, halt"),
        group="Stickers",
        title="if it drifts, halt",
        note="Halt & Restart line. Same construction as specify.",
    )

    # HALT die-cut — lime ticket with pause bars
    hw, hh = 300, 340
    halt_sticker = [
        f'  <rect width="{hw}" height="{hh}" rx="28" fill="{LIME}"/>',
        f'  <rect x="86" y="48" width="42" height="168" rx="8" fill="{INK}"/>',
        f'  <rect x="172" y="48" width="42" height="168" rx="8" fill="{INK}"/>',
        centered_line(DISPLAY, "HALT", 42, 272, INK, hw, tracking=-1.4, scale_x=0.88),
    ]
    write(
        "stickers/halt.svg",
        svg(f"0 0 {hw} {hh}", "\n".join(halt_sticker), label="Halt sticker"),
        group="Stickers",
        title="Halt",
        note="Die-cut lime. Pause icon from the kit.",
    )

    # RESTART die-cut
    rw, rh = 300, 340
    restart_sticker = [
        f'  <rect width="{rw}" height="{rh}" rx="28" fill="{INK}"/>',
        f'  <rect x="6" y="6" width="{rw - 12}" height="{rh - 12}" rx="22" fill="none" stroke="{PINK}" stroke-width="8"/>',
        restart_mark(150, 148, 72, PINK, 14),
        centered_line(DISPLAY, "RESTART", 28, 278, PAPER, rw, tracking=-0.8, scale_x=0.88),
    ]
    write(
        "stickers/restart.svg",
        svg(f"0 0 {rw} {rh}", "\n".join(restart_sticker), label="Restart sticker"),
        group="Stickers",
        title="Restart",
        note="Die-cut. Restart icon from the kit.",
    )

    # Prompt / specify
    pw, ph = 340, 340
    prompt_sticker = ink_sheet(pw, ph, 28, "prm")
    prompt_sticker += [
        "  </g>",
        f'  <path d="M78 92 L148 170 L78 248" fill="none" stroke="{LIME}" stroke-width="22" stroke-linecap="round" stroke-linejoin="round"/>',
        f'  <rect x="178" y="196" width="92" height="28" rx="8" fill="{PINK}"/>',
        centered_line(JB_BOLD, "specify.", 22, 300, PAPER, pw, tracking=1.6),
    ]
    write(
        "stickers/prompt.svg",
        svg(f"0 0 {pw} {ph}", "\n".join(prompt_sticker), label="specify. prompt sticker"),
        group="Stickers",
        title="specify.",
        note="Prompt chevron from the kit.",
    )

    # Spark / untapped
    spark_sticker = [
        "  <defs>",
        f"    {GRADIENT_DEFS}",
        '    <pattern id="spk" width="28" height="28" patternUnits="userSpaceOnUse">',
        f'      <path d="M28 0H0V28" fill="none" stroke="{LIME}" stroke-width="1" opacity="0.2"/>',
        "    </pattern>",
        '    <clipPath id="spk-clip"><circle cx="200" cy="200" r="200"/></clipPath>',
        "  </defs>",
        '  <g clip-path="url(#spk-clip)">',
        f'    <rect width="400" height="400" fill="{INK}"/>',
        '    <rect width="400" height="400" fill="url(#spk)"/>',
        "  </g>",
        spark_mark(200, 168, 92),
        centered_line(DISPLAY, "UNTAPPED", 22, 322, LIME, 400, tracking=-0.6, scale_x=0.88),
    ]
    write(
        "stickers/spark-untapped.svg",
        svg("0 0 400 400", "\n".join(spark_sticker), label="Untapped spark"),
        group="Stickers",
        title="Untapped",
        note="Circular vinyl. Spark icon from the kit.",
    )

    # Human finish — mask
    mw, mh = 340, 380
    mask_sticker = ink_sheet(mw, mh, 28, "msk")
    mask_sticker += [
        f'    <rect width="{mw}" height="{mh}" fill="{WINE}" opacity="0.45"/>',
        "  </g>",
        f'  <path d="M70 210 C70 92 270 92 270 210 C270 268 222 292 170 292 C118 292 70 268 70 210Z" fill="{INK}" stroke="{PAPER}" stroke-width="6"/>',
        f'  <path d="M170 104 V292" stroke="{PAPER}" stroke-width="3" opacity="0.45"/>',
        f'  <circle cx="126" cy="196" r="16" fill="{LIME}"/>',
        f'  <circle cx="214" cy="196" r="16" fill="{PINK}"/>',
        centered_line(INTER_BOLD, "human finish", 20, 338, PAPER, mw, tracking=-0.3),
    ]
    write(
        "stickers/human-finish.svg",
        svg(f"0 0 {mw} {mh}", "\n".join(mask_sticker), label="human finish"),
        group="Stickers",
        title="human finish",
        note="Mask icon from the kit.",
    )

    # Lean tokens meter
    lw, lh = 440, 200
    meter_sticker = ink_sheet(lw, lh, 24, "mtr")
    meter_sticker += [
        "  </g>",
        f'  <rect x="40" y="48" width="360" height="52" rx="26" fill="#1a0812" stroke="{OLIVE}" stroke-width="5"/>',
        f'  <rect x="52" y="58" width="148" height="32" rx="16" fill="{LIME}"/>',
        f'  <rect x="92" y="28" width="10" height="22" rx="2" fill="{PINK}"/>',
        f'  <rect x="215" y="20" width="10" height="30" rx="2" fill="{PINK}"/>',
        f'  <rect x="338" y="28" width="10" height="22" rx="2" fill="{PINK}"/>',
        centered_line(JB_BOLD, "LEAN TOKENS", 20, 156, LIME, lw, tracking=3.2),
        centered_line(INTER_MED, "human finish", 14, 178, "rgba(249,249,250,0.7)", lw, tracking=1.2),
    ]
    write(
        "stickers/lean-meter.svg",
        svg(f"0 0 {lw} {lh}", "\n".join(meter_sticker), label="Lean tokens meter"),
        group="Stickers",
        title="Lean tokens meter",
        note="Meter icon from the kit.",
    )

    # Live prompting lab ticket
    tw, th = 500, 168
    b, bw, _ = DISPLAY.shape("HALT", 28, tracking=-1.2, scale_x=0.88)
    amp, ampw, _ = DISPLAY.shape("&", 28, tracking=0, scale_x=0.88)
    c, cw, _ = DISPLAY.shape("RESTART", 28, tracking=-1.2, scale_x=0.88)
    row_w = bw + 8 + ampw + 8 + cw
    row_x = (360 - row_w) / 2
    td, ttw, _ = JB_BOLD.shape("TICKET", 16, tracking=2.0)
    lab_d, lab_w, _ = JB_BOLD.shape("LIVE PROMPTING LAB", 12, tracking=1.8)
    lab = [
        "  <defs>",
        '    <mask id="ticket-hole">',
        f'      <rect width="{tw}" height="{th}" rx="16" fill="#fff"/>',
        '      <circle cx="372" cy="0" r="14" fill="#000"/>',
        f'      <circle cx="372" cy="{th}" r="14" fill="#000"/>',
        "    </mask>",
        "  </defs>",
        '  <g mask="url(#ticket-hole)">',
        f'    <rect width="{tw}" height="{th}" rx="16" fill="{LIME}"/>',
        f'    <rect x="14" y="14" width="{tw - 28}" height="{th - 28}" fill="none" stroke="{INK}" stroke-width="3" stroke-dasharray="8 7" opacity="0.55"/>',
        f'    <path d="M372 18 v{th - 36}" stroke="{INK}" stroke-width="3" stroke-dasharray="5 6"/>',
        f'    <g transform="translate({(360 - lab_w) / 2:.1f} 52)">{path_text(lab_d, INK)}</g>',
        f'    <g transform="translate({row_x:.1f} 118)">{path_text(b, INK)}</g>',
        f'    <g transform="translate({row_x + bw + 8:.1f} 118)">{path_text(amp, PINK)}</g>',
        f'    <g transform="translate({row_x + bw + 8 + ampw + 8:.1f} 118)">{path_text(c, INK)}</g>',
        f'    <g transform="translate({372 + (128 - ttw) / 2:.1f} 102)">{path_text(td, INK)}</g>',
        "  </g>",
    ]
    write(
        "stickers/live-prompting-lab.svg",
        svg(f"0 0 {tw} {th}", "\n".join(lab), label="Live prompting lab ticket"),
        group="Stickers",
        title="Live prompting lab",
        note="Dashed ticket. Halt & Restart event.",
    )

    # That's the push — commit icon
    cw_, ch = 340, 380
    commit_sticker = ink_sheet(cw_, ch, 28, "cmt")
    commit_sticker += [
        "  </g>",
        f'  <circle cx="170" cy="150" r="44" fill="none" stroke="{LIME}" stroke-width="12"/>',
        f'  <path d="M170 48 v58M170 194 v58" stroke="{PINK}" stroke-width="12" stroke-linecap="round"/>',
        centered_line(JB_BOLD, "THAT'S THE PUSH", 16, 300, PAPER, cw_, tracking=1.8),
        centered_line(INTER_MED, "take a sticker. you just shipped.", 12, 328, "rgba(249,249,250,0.65)", cw_, tracking=0.4),
    ]
    write(
        "stickers/thats-the-push.svg",
        svg(f"0 0 {cw_} {ch}", "\n".join(commit_sticker), label="that's the push"),
        group="Stickers",
        title="that's the push",
        note="Commit icon. Git-walk line from Clubs Expo.",
    )

    # Fold it into Tuesday — workflow
    ww, wh = 440, 220
    flow = ink_sheet(ww, wh, 24, "wf")
    flow += [
        "  </g>",
        f'  <circle cx="96" cy="88" r="28" fill="{OLIVE}"/>',
        f'  <circle cx="220" cy="88" r="28" fill="{LIME}"/>',
        f'  <circle cx="344" cy="88" r="28" fill="{PINK}"/>',
        f'  <path d="M124 88h68M248 88h68" stroke="{PAPER}" stroke-width="8" stroke-linecap="round"/>',
        centered_line(INTER_BOLD, "fold it into Tuesday", 18, 168, PAPER, ww, tracking=-0.3),
        centered_line(JB_REG, "WORKFLOW", 11, 192, OLIVE, ww, tracking=3.0),
    ]
    write(
        "stickers/fold-into-tuesday.svg",
        svg(f"0 0 {ww} {wh}", "\n".join(flow), label="fold it into Tuesday"),
        group="Stickers",
        title="fold it into Tuesday",
        note="Workflow nodes from the kit.",
    )

    # Glitch UNNATURAL chip
    g1, gw1, _ = DISPLAY.shape("UNNATURAL", 36, tracking=-1.8, scale_x=0.84)
    left = 78
    gw, gh = left + gw1 + 32, 120
    glitch_sticker = [
        f'  <rect width="{gw:.1f}" height="{gh}" rx="16" fill="{INK}"/>',
        f'  <rect x="18" y="28" width="48" height="12" fill="{CYAN}" transform="translate(-3 2)"/>',
        f'  <rect x="18" y="28" width="48" height="12" fill="{PINK}" transform="translate(3 -2)"/>',
        f'  <rect x="18" y="28" width="48" height="12" fill="{PAPER}"/>',
        f'  <rect x="22" y="48" width="36" height="8" fill="{CYAN}" transform="translate(2 1)"/>',
        f'  <rect x="22" y="48" width="36" height="8" fill="{PINK}" transform="translate(-2 -1)"/>',
        f'  <rect x="22" y="48" width="36" height="8" fill="{LIME}"/>',
        f'  <g transform="translate({left} 78)">{glitch_word(g1, PAPER, dx=2.4, dy=0.9)}</g>',
    ]
    write(
        "stickers/glitch-unnatural.svg",
        svg(f"0 0 {gw:.1f} {gh}", "\n".join(glitch_sticker), label="UNNATURAL glitch"),
        group="Stickers",
        title="UNNATURAL glitch",
        note="Glitch bars + wordmark.",
    )

    g2, gw2, _ = DISPLAY.shape("INTELLIGENCE", 32, tracking=-1.8, scale_x=0.84)
    left2 = 78
    iw, ih = left2 + gw2 + 32, 120
    intel_sticker = [
        f'  <rect width="{iw:.1f}" height="{ih}" rx="16" fill="{INK}"/>',
        f'  <rect x="18" y="28" width="48" height="12" fill="{CYAN}" transform="translate(-3 2)"/>',
        f'  <rect x="18" y="28" width="48" height="12" fill="{PINK}" transform="translate(3 -2)"/>',
        f'  <rect x="18" y="28" width="48" height="12" fill="{PAPER}"/>',
        f'  <rect x="22" y="48" width="36" height="8" fill="{CYAN}" transform="translate(2 1)"/>',
        f'  <rect x="22" y="48" width="36" height="8" fill="{PINK}" transform="translate(-2 -1)"/>',
        f'  <rect x="22" y="48" width="36" height="8" fill="{LIME}"/>',
        f'  <g transform="translate({left2} 78)">{glitch_word(g2, PAPER, dx=2.4, dy=0.9)}</g>',
    ]
    write(
        "stickers/glitch-intelligence.svg",
        svg(f"0 0 {iw:.1f} {ih}", "\n".join(intel_sticker), label="INTELLIGENCE glitch"),
        group="Stickers",
        title="INTELLIGENCE glitch",
        note="Glitch bars + wordmark. Pair with UNNATURAL.",
    )

    # Laptop wordmark — stacked glitch, physical size for vinyl / home print.
    # 3.5 × 1.55 in sits on a 13–16" lid without reading as a bumper sticker.
    wm_size = 56
    wm_track = -2.4
    wm_sx = 0.84
    wd1, ww1, _ = DISPLAY.shape("UNNATURAL", wm_size, tracking=wm_track, scale_x=wm_sx)
    wd2, ww2, _ = DISPLAY.shape("INTELLIGENCE", wm_size, tracking=wm_track, scale_x=wm_sx)
    wm_dx = round(3.2 * wm_size / 72, 2)
    wm_dy = round(1.1 * wm_size / 72, 2)
    PX_IN = 96.0
    WM_IN_W, WM_IN_H = 3.5, 1.55
    WM_W, WM_H = WM_IN_W * PX_IN, WM_IN_H * PX_IN
    wm_rx = 14
    wm_type = max(ww1, ww2)
    wm_tx = (WM_W - wm_type) / 2
    wm_cap = wm_size * 1490 / 2048
    wm_delta = wm_size * (78 / 72)
    wm_block = wm_delta + wm_cap
    wm_y1 = (WM_H - wm_block) / 2 + wm_cap
    wm_y2 = wm_y1 + wm_delta
    wordmark_art = "\n".join(
        [
            f'  <rect width="{WM_W:.2f}" height="{WM_H:.2f}" rx="{wm_rx}" fill="{INK}"/>',
            f'  <g transform="translate({wm_tx:.2f} {wm_y1:.2f})">'
            f"{glitch_word(wd1, PAPER, dx=wm_dx, dy=wm_dy)}</g>",
            f'  <g transform="translate({wm_tx:.2f} {wm_y2:.2f})">'
            f"{glitch_word(wd2, PAPER, dx=wm_dx, dy=wm_dy)}</g>",
        ]
    )
    write(
        "stickers/wordmark-laptop.svg",
        svg(
            f"0 0 {WM_W:.2f} {WM_H:.2f}",
            wordmark_art,
            w=f"{WM_IN_W}in",
            h=f"{WM_IN_H}in",
            label="Unnatural Intelligence laptop sticker",
        ),
        group="Stickers",
        title="Wordmark laptop sticker",
        note="3.5 × 1.55 in vinyl. Print the SVG at 100% or the 300 DPI PNG.",
    )

    # Clear die-cut — same stacked glitch, no ink plate.
    clear_pad = round(max(10.0, wm_dx + 8), 2)
    clear_w = wm_type + 2 * clear_pad
    clear_h = wm_block + 2 * clear_pad + 2 * wm_dy
    clear_y1 = clear_pad + wm_cap + wm_dy
    clear_y2 = clear_y1 + wm_delta
    clear_in_w = round(clear_w / PX_IN, 3)
    clear_in_h = round(clear_h / PX_IN, 3)
    write(
        "stickers/wordmark-laptop-clear.svg",
        svg(
            f"0 0 {clear_w:.2f} {clear_h:.2f}",
            "\n".join(
                [
                    f'  <g transform="translate({clear_pad:.2f} {clear_y1:.2f})">'
                    f"{glitch_word(wd1, PAPER, dx=wm_dx, dy=wm_dy)}</g>",
                    f'  <g transform="translate({clear_pad:.2f} {clear_y2:.2f})">'
                    f"{glitch_word(wd2, PAPER, dx=wm_dx, dy=wm_dy)}</g>",
                ]
            ),
            w=f"{clear_in_w}in",
            h=f"{clear_in_h}in",
            label="Unnatural Intelligence clear die-cut wordmark",
        ),
        group="Stickers",
        title="Wordmark laptop — clear die-cut",
        note=f"{clear_in_w} × {clear_in_h} in. Transparent. Cut to the letterforms.",
    )

    # US Letter sheet — sticker at actual size with crop marks
    letter_w, letter_h = 8.5 * PX_IN, 11 * PX_IN
    lx = (letter_w - WM_W) / 2
    ly = 2.4 * PX_IN
    mark = 14
    gap = 6

    def crop_marks(x: float, y: float, w: float, h: float) -> list[str]:
        c = OLIVE
        sw = 0.75
        return [
            f'  <path d="M{x - gap - mark:.1f} {y:.1f}h{mark}" stroke="{c}" stroke-width="{sw}"/>',
            f'  <path d="M{x:.1f} {y - gap - mark:.1f}v{mark}" stroke="{c}" stroke-width="{sw}"/>',
            f'  <path d="M{x + w + gap:.1f} {y:.1f}h{mark}" stroke="{c}" stroke-width="{sw}"/>',
            f'  <path d="M{x + w:.1f} {y - gap - mark:.1f}v{mark}" stroke="{c}" stroke-width="{sw}"/>',
            f'  <path d="M{x - gap - mark:.1f} {y + h:.1f}h{mark}" stroke="{c}" stroke-width="{sw}"/>',
            f'  <path d="M{x:.1f} {y + h + gap:.1f}v{mark}" stroke="{c}" stroke-width="{sw}"/>',
            f'  <path d="M{x + w + gap:.1f} {y + h:.1f}h{mark}" stroke="{c}" stroke-width="{sw}"/>',
            f'  <path d="M{x + w:.1f} {y + h + gap:.1f}v{mark}" stroke="{c}" stroke-width="{sw}"/>',
        ]

    sheet_note, note_w, _ = JB_REG.shape("3.5 × 1.55 IN  ·  LAPTOP STICKER  ·  PRINT AT 100%", 11, tracking=1.6)
    cut_note, cut_w, _ = JB_REG.shape("CUT THE ROUNDED RECT  ·  VINYL ON INK", 10, tracking=1.8)
    letter_inner = "\n".join(
        [
            f'  <rect width="{letter_w:.1f}" height="{letter_h:.1f}" fill="{PAPER}"/>',
            *crop_marks(lx, ly, WM_W, WM_H),
            f'  <g transform="translate({lx:.2f} {ly:.2f})">',
            wordmark_art,
            "  </g>",
            f'  <g transform="translate({(letter_w - note_w) / 2:.1f} {ly + WM_H + 36:.1f})">{path_text(sheet_note, INK)}</g>',
            f'  <g transform="translate({(letter_w - cut_w) / 2:.1f} {ly + WM_H + 54:.1f})">{path_text(cut_note, OLIVE)}</g>',
        ]
    )
    write(
        "stickers/wordmark-laptop-letter.svg",
        svg(
            f"0 0 {letter_w:.1f} {letter_h:.1f}",
            letter_inner,
            w="8.5in",
            h="11in",
            label="Laptop wordmark sticker print sheet",
        ),
        group="Stickers",
        title="Wordmark laptop — letter print sheet",
        note="US Letter. Sticker at actual size. Print at 100%, no fit-to-page.",
    )

    # Circular 3 in vinyls — same family as the wine-grid jellyfish avatar.
    CS = 400
    CS_IN = 3.0
    cx = cy = CS / 2

    def circle_shell(pid: str, fill: str, grid: str | None) -> list[str]:
        parts = [
            "  <defs>",
            f"    {GRADIENT_DEFS}",
            f'    <clipPath id="{pid}-c"><circle cx="{cx}" cy="{cy}" r="{CS / 2}"/></clipPath>',
        ]
        if grid:
            parts += [
                f'    <pattern id="{pid}-g" width="28" height="28" patternUnits="userSpaceOnUse">',
                f'      <path d="M28 0H0V28" fill="none" stroke="{grid}" stroke-width="1" opacity="0.32"/>',
                "    </pattern>",
            ]
        parts += [
            "  </defs>",
            f'  <g clip-path="url(#{pid}-c)">',
            f'    <rect width="{CS}" height="{CS}" fill="{fill}"/>',
        ]
        if grid:
            parts.append(f'    <rect width="{CS}" height="{CS}" fill="url(#{pid}-g)"/>')
        return parts

    def write_circle(filename: str, inner: list[str], title: str, note: str) -> None:
        write(
            f"stickers/{filename}.svg",
            svg(
                f"0 0 {CS} {CS}",
                "\n".join(inner),
                w=f"{CS_IN}in",
                h=f"{CS_IN}in",
                label=title,
            ),
            group="Stickers",
            title=title,
            note=note,
        )

    nd1, nw1, _ = DISPLAY.shape("UNNATURAL", 48, tracking=-2.2, scale_x=0.84)
    nd2, nw2, _ = DISPLAY.shape("INTELLIGENCE", 48, tracking=-2.2, scale_x=0.84)
    n_dx, n_dy = 2.1, 0.75
    n_type = max(nw1, nw2)
    n_tx = (CS - n_type) / 2
    n_cap = 48 * 1490 / 2048
    n_delta = 48 * (78 / 72)
    n_block = n_delta + n_cap
    n_y1 = (CS - n_block) / 2 + n_cap
    n_y2 = n_y1 + n_delta

    # 1. Wine + olive grid + gradient jelly (the reference circle)
    wine_jelly = circle_shell("cwj", WINE, OLIVE)
    wine_jelly += [
        jelly_centered(cx, cy, 348, "url(#uni-jelly)"),
        "  </g>",
    ]
    write_circle(
        "circle-wine-jelly",
        wine_jelly,
        "Circle — wine jellyfish",
        "3 in. Wine field, olive grid, gradient mascot.",
    )

    # 2. Double ring frame (lime + pink)
    rings = circle_shell("cfr", INK, OLIVE)
    rings += [
        f'    <rect width="{CS}" height="{CS}" fill="{WINE}" opacity="0.45"/>',
        jelly_centered(cx, cy, 292, "url(#uni-jelly)"),
        "  </g>",
        f'  <circle cx="{cx}" cy="{cy}" r="186" fill="none" stroke="{LIME}" stroke-width="7"/>',
        f'  <circle cx="{cx}" cy="{cy}" r="172" fill="none" stroke="{PINK}" stroke-width="3"/>',
    ]
    write_circle(
        "circle-frame-rings",
        rings,
        "Circle — double ring",
        "3 in. Double ring around the mascot.",
    )

    # 3. Dashed ticket frame
    dashed = circle_shell("cds", WINE, OLIVE)
    dashed += [
        jelly_centered(cx, cy, 300, "url(#uni-jelly)"),
        "  </g>",
        f'  <circle cx="{cx}" cy="{cy}" r="184" fill="none" stroke="{LIME}" '
        f'stroke-width="5" stroke-dasharray="12 9"/>',
    ]
    write_circle(
        "circle-frame-dashed",
        dashed,
        "Circle — dashed ticket frame",
        "3 in. Halt & Restart ticket ring.",
    )

    # 4. Paper rim (kiss-cut style frame)
    paper_rim = circle_shell("cpr", WINE, OLIVE)
    paper_rim += [
        jelly_centered(cx, cy, 312, "url(#uni-jelly)"),
        "  </g>",
        f'  <circle cx="{cx}" cy="{cy}" r="193" fill="none" stroke="{PAPER}" stroke-width="14"/>',
    ]
    write_circle(
        "circle-frame-paper",
        paper_rim,
        "Circle — paper rim",
        "3 in. White bumper around the wine field.",
    )

    # 5. Lime field, ink jelly, pink frame
    lime_circ = circle_shell("cli", LIME, None)
    lime_circ += [
        jelly_centered(cx, cy, 300, INK),
        "  </g>",
        f'  <circle cx="{cx}" cy="{cy}" r="186" fill="none" stroke="{PINK}" stroke-width="8"/>',
    ]
    write_circle(
        "circle-lime",
        lime_circ,
        "Circle — lime field",
        "3 in. Ink mascot on lime.",
    )

    # 6. Club name on wine
    name_circ = circle_shell("cnm", WINE, OLIVE)
    name_circ += [
        f'    <rect x="{n_tx + (n_type - 50) / 2:.1f}" y="{n_y1 - n_cap - 18:.1f}" width="28" height="5" rx="2.5" fill="{LIME}"/>',
        f'    <rect x="{n_tx + (n_type - 50) / 2 + 32:.1f}" y="{n_y1 - n_cap - 18:.1f}" width="18" height="5" rx="2.5" fill="{PINK}"/>',
        "  </g>",
        f'  <g transform="translate({n_tx:.2f} {n_y1:.2f})">{glitch_word(nd1, PAPER, dx=n_dx, dy=n_dy)}</g>',
        f'  <g transform="translate({n_tx:.2f} {n_y2:.2f})">{glitch_word(nd2, PAPER, dx=n_dx, dy=n_dy)}</g>',
    ]
    write_circle(
        "circle-name",
        name_circ,
        "Circle — club name",
        "3 in. Stacked glitch wordmark.",
    )

    # 7. Club name with double ring frame
    name_frame = circle_shell("cnf", INK, None)
    name_frame += [
        "  </g>",
        f'  <circle cx="{cx}" cy="{cy}" r="186" fill="none" stroke="{LIME}" stroke-width="7"/>',
        f'  <circle cx="{cx}" cy="{cy}" r="172" fill="none" stroke="{PINK}" stroke-width="3"/>',
        f'  <g transform="translate({n_tx:.2f} {n_y1:.2f})">{glitch_word(nd1, PAPER, dx=n_dx, dy=n_dy)}</g>',
        f'  <g transform="translate({n_tx:.2f} {n_y2:.2f})">{glitch_word(nd2, PAPER, dx=n_dx, dy=n_dy)}</g>',
    ]
    write_circle(
        "circle-name-frame",
        name_frame,
        "Circle — name in frame",
        "3 in. Wordmark inside lime & pink rings.",
    )

    # 2 in — ink field, gradient mascot, lime + pink frame
    def write_2in(filename: str, inner: list[str], title: str, note: str) -> None:
        write(
            f"stickers/{filename}.svg",
            svg(
                f"0 0 {CS} {CS}",
                "\n".join(inner),
                w="2in",
                h="2in",
                label=title,
            ),
            group="Stickers",
            title=title,
            note=note,
        )

    rings_2in = [
        f'  <circle cx="{cx}" cy="{cy}" r="187" fill="none" stroke="{LIME}" stroke-width="11"/>',
        f'  <circle cx="{cx}" cy="{cy}" r="172" fill="none" stroke="{PINK}" stroke-width="5.5"/>',
    ]

    two_in = circle_shell("c2i", INK, None)
    two_in += [
        jelly_centered(cx, cy, 288, "url(#uni-jelly)"),
        "  </g>",
        *rings_2in,
    ]
    write_2in(
        "circle-2in-ink-frame",
        two_in,
        "Circle — 2 in ink frame",
        "2 in vinyl. Black field, gradient mascot, lime and pink rings.",
    )

    # Olive grid on ink
    two_olive = circle_shell("c2o", INK, OLIVE)
    two_olive += [
        jelly_centered(cx, cy, 288, "url(#uni-jelly)"),
        "  </g>",
        *rings_2in,
    ]
    write_2in(
        "circle-2in-grid-olive",
        two_olive,
        "Circle — 2 in olive grid",
        "2 in. Black field, olive grid, lime and pink rings.",
    )

    # Lime grid on ink
    two_limeg = circle_shell("c2l", INK, LIME)
    two_limeg += [
        jelly_centered(cx, cy, 288, "url(#uni-jelly)"),
        "  </g>",
        *rings_2in,
    ]
    write_2in(
        "circle-2in-grid-lime",
        two_limeg,
        "Circle — 2 in lime grid",
        "2 in. Black field, lime grid, lime and pink rings.",
    )

    # Wine field + olive grid
    two_wine = circle_shell("c2w", WINE, OLIVE)
    two_wine += [
        jelly_centered(cx, cy, 288, "url(#uni-jelly)"),
        "  </g>",
        *rings_2in,
    ]
    write_2in(
        "circle-2in-grid-wine",
        two_wine,
        "Circle — 2 in wine grid",
        "2 in. Wine field, olive grid, lime and pink rings.",
    )

    # Same 2 in ink vinyl with thinner lime + pink rings, closer to the die-cut.
    rings_2in_thin = [
        f'  <circle cx="{cx}" cy="{cy}" r="194" fill="none" stroke="{LIME}" stroke-width="5"/>',
        f'  <circle cx="{cx}" cy="{cy}" r="186" fill="none" stroke="{PINK}" stroke-width="2.5"/>',
    ]
    two_thin = circle_shell("c2t", INK, None)
    two_thin += [
        jelly_centered(cx, cy, 288, "url(#uni-jelly)"),
        "  </g>",
        *rings_2in_thin,
    ]
    write_2in(
        "circle-2in-thin-frame",
        two_thin,
        "Circle — 2 in thin frame",
        "2 in. Black field, gradient mascot, thinner lime and pink rings.",
    )

    # Mid-weight rings between the thick and thin frames, with olive grid.
    rings_2in_mid = [
        f'  <circle cx="{cx}" cy="{cy}" r="191" fill="none" stroke="{LIME}" stroke-width="8"/>',
        f'  <circle cx="{cx}" cy="{cy}" r="179" fill="none" stroke="{PINK}" stroke-width="4"/>',
    ]
    two_mid = circle_shell("c2m", INK, OLIVE)
    two_mid += [
        jelly_centered(cx, cy, 288, "url(#uni-jelly)"),
        "  </g>",
        *rings_2in_mid,
    ]
    write_2in(
        "circle-2in-mid-grid",
        two_mid,
        "Circle — 2 in mid grid",
        "2 in. Black field, olive grid, mid-weight lime and pink rings.",
    )

    two_mid_lime = circle_shell("c2ml", INK, LIME)
    two_mid_lime += [
        jelly_centered(cx, cy, 288, "url(#uni-jelly)"),
        "  </g>",
        *rings_2in_mid,
    ]
    write_2in(
        "circle-2in-mid-grid-lime",
        two_mid_lime,
        "Circle — 2 in mid lime grid",
        "2 in. Black field, lime grid, mid-weight lime and pink rings.",
    )

    two_mid_wine = circle_shell("c2mw", WINE, OLIVE)
    two_mid_wine += [
        jelly_centered(cx, cy, 288, "url(#uni-jelly)"),
        "  </g>",
        *rings_2in_mid,
    ]
    write_2in(
        "circle-2in-mid-grid-wine",
        two_mid_wine,
        "Circle — 2 in mid wine grid",
        "2 in. Wine field, olive grid, mid-weight lime and pink rings.",
    )

    # 2 in club name — stacked glitch sized to clear the pink inner ring.
    n2_size = 56
    n2_track = -2.4
    n2_sx = 0.84
    n2d1, n2w1, _ = DISPLAY.shape("UNNATURAL", n2_size, tracking=n2_track, scale_x=n2_sx)
    n2d2, n2w2, _ = DISPLAY.shape("INTELLIGENCE", n2_size, tracking=n2_track, scale_x=n2_sx)
    n2_dx = round(2.1 * n2_size / 48, 2)
    n2_dy = round(0.75 * n2_size / 48, 2)
    n2_type = max(n2w1, n2w2)
    n2_tx = (CS - n2_type) / 2
    n2_cap = n2_size * 1490 / 2048
    n2_delta = n2_size * (78 / 72)
    n2_block = n2_delta + n2_cap
    n2_y1 = (CS - n2_block) / 2 + n2_cap
    n2_y2 = n2_y1 + n2_delta
    n2_tick_y = n2_y1 - n2_cap - 18
    n2_tick_x = n2_tx + (n2_type - 58) / 2
    name_type = [
        *rings_2in_mid,
        f'  <rect x="{n2_tick_x:.1f}" y="{n2_tick_y:.1f}" width="32" height="5" rx="2.5" fill="{LIME}"/>',
        f'  <rect x="{n2_tick_x + 36:.1f}" y="{n2_tick_y:.1f}" width="22" height="5" rx="2.5" fill="{PINK}"/>',
        f'  <g transform="translate({n2_tx:.2f} {n2_y1:.2f})">{glitch_word(n2d1, PAPER, dx=n2_dx, dy=n2_dy)}</g>',
        f'  <g transform="translate({n2_tx:.2f} {n2_y2:.2f})">{glitch_word(n2d2, PAPER, dx=n2_dx, dy=n2_dy)}</g>',
    ]
    two_name = circle_shell("c2n", INK, None)
    two_name += [
        jelly_centered(cx, cy, 288, "url(#uni-jelly)", extra='opacity="0.4"'),
        "  </g>",
        *name_type,
    ]
    write_2in(
        "circle-2in-name",
        two_name,
        "Circle — 2 in club name",
        "2 in. Ghost jellyfish behind stacked glitch UNNATURAL / INTELLIGENCE.",
    )

    two_name_plain = circle_shell("c2np", INK, None)
    two_name_plain += [
        "  </g>",
        *name_type,
    ]
    write_2in(
        "circle-2in-name-type",
        two_name_plain,
        "Circle — 2 in club name type",
        "2 in. Stacked glitch UNNATURAL / INTELLIGENCE, no jellyfish.",
    )

    # Pink outer, lime inner — mid-weight, swapped from the lime-outer set.
    rings_2in_pink = [
        f'  <circle cx="{cx}" cy="{cy}" r="191" fill="none" stroke="{PINK}" stroke-width="8"/>',
        f'  <circle cx="{cx}" cy="{cy}" r="179" fill="none" stroke="{LIME}" stroke-width="4"/>',
    ]

    def write_jelly_rings(
        filename: str,
        pid: str,
        fill: str,
        grid: str | None,
        rings: list[str],
        title: str,
        note: str,
    ) -> None:
        parts = circle_shell(pid, fill, grid)
        parts += [
            jelly_centered(cx, cy, 288, "url(#uni-jelly)"),
            "  </g>",
            *rings,
        ]
        write_2in(filename, parts, title, note)

    write_jelly_rings(
        "circle-2in-pink-frame",
        "c2pf",
        INK,
        None,
        rings_2in_pink,
        "Circle — 2 in pink frame",
        "2 in. Black field, gradient mascot, pink outer and lime inner rings.",
    )
    write_jelly_rings(
        "circle-2in-pink-grid-olive",
        "c2po",
        INK,
        OLIVE,
        rings_2in_pink,
        "Circle — 2 in pink olive grid",
        "2 in. Black field, olive grid, pink outer and lime inner rings.",
    )
    write_jelly_rings(
        "circle-2in-pink-grid-wine",
        "c2pw",
        WINE,
        OLIVE,
        rings_2in_pink,
        "Circle — 2 in pink wine grid",
        "2 in. Wine field, olive grid, pink outer and lime inner rings.",
    )

    two_pink_name = circle_shell("c2pn", INK, None)
    two_pink_name += [
        "  </g>",
        *rings_2in_pink,
        f'  <rect x="{n2_tick_x:.1f}" y="{n2_tick_y:.1f}" width="32" height="5" rx="2.5" fill="{LIME}"/>',
        f'  <rect x="{n2_tick_x + 36:.1f}" y="{n2_tick_y:.1f}" width="22" height="5" rx="2.5" fill="{PINK}"/>',
        f'  <g transform="translate({n2_tx:.2f} {n2_y1:.2f})">{glitch_word(n2d1, PAPER, dx=n2_dx, dy=n2_dy)}</g>',
        f'  <g transform="translate({n2_tx:.2f} {n2_y2:.2f})">{glitch_word(n2d2, PAPER, dx=n2_dx, dy=n2_dy)}</g>',
    ]
    write_2in(
        "circle-2in-pink-name",
        two_pink_name,
        "Circle — 2 in pink name",
        "2 in. Stacked club name, pink outer and lime inner rings.",
    )

    neural_icon = f"""
  <circle cx="32" cy="14" r="5" fill="{LIME}"/>
  <circle cx="14" cy="32" r="5" fill="{OLIVE}"/>
  <circle cx="50" cy="32" r="5" fill="{PINK}"/>
  <circle cx="24" cy="50" r="5" fill="{CYAN}"/>
  <circle cx="40" cy="50" r="5" fill="{PAPER}"/>
  <path d="M32 19 L14 27 M32 19 L50 27 M14 37 L24 45 M50 37 L40 45 M27 50h10" stroke="{PAPER}" stroke-width="1.6" opacity="0.7"/>
"""
    nw, nh = 340, 400
    neural_sticker = ink_sheet(nw, nh, 28, "nrn")
    neural_sticker += [
        "  </g>",
        icon_at(neural_icon, 170, 168, 4.6),
        centered_line(JB_BOLD, "GENERATED BY AI", 16, 332, LIME, nw, tracking=2.2),
        centered_line(INTER_MED, "perfected by humans", 13, 360, "rgba(249,249,250,0.65)", nw, tracking=0.6),
    ]
    write(
        "stickers/neural.svg",
        svg(f"0 0 {nw} {nh}", "\n".join(neural_sticker), label="Generated by AI neural"),
        group="Stickers",
        title="Generated by AI",
        note="Neural icon from the kit.",
    )

    tentacle_icon = f"""
  <defs>
    <linearGradient id="st-tgrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{LIME}"/>
      <stop offset="100%" stop-color="{PINK}"/>
    </linearGradient>
  </defs>
  <path d="M16 18 C30 24 20 38 32 44 C44 50 40 56 50 58" fill="none" stroke="url(#st-tgrad)" stroke-width="7" stroke-linecap="round"/>
  <path d="M22 14 C26 28 34 30 36 46" fill="none" stroke="url(#st-tgrad)" stroke-width="4" stroke-linecap="round" opacity="0.7"/>
"""
    tent = ink_sheet(400, 400, 200, "tnc")
    tent += [
        "  </g>",
        icon_at(tentacle_icon, 200, 148, 4.2),
        centered_line(DISPLAY, "UNNATURAL", 22, 348, PAPER, 400, tracking=-0.8, scale_x=0.88),
    ]
    write(
        "stickers/tentacle.svg",
        svg("0 0 400 400", "\n".join(tent), label="Unnatural tentacle"),
        group="Stickers",
        title="Tentacle",
        note="Circular vinyl. Tentacle icon from the kit.",
    )

    node_icon = f"""
  <rect x="18" y="18" width="28" height="28" rx="6" fill="none" stroke="{LIME}" stroke-width="2.5"/>
  <circle cx="32" cy="32" r="5" fill="{PINK}"/>
  <circle cx="18" cy="18" r="3.5" fill="{OLIVE}"/>
  <circle cx="46" cy="18" r="3.5" fill="{CYAN}"/>
  <circle cx="46" cy="46" r="3.5" fill="{PAPER}"/>
  <circle cx="18" cy="46" r="3.5" fill="{LIME}"/>
"""
    ndw, ndh = 340, 380
    node_sticker = ink_sheet(ndw, ndh, 28, "nde")
    node_sticker += [
        "  </g>",
        icon_at(node_icon, 170, 160, 4.5),
        centered_line(INTER_BOLD, "integrated", 22, 318, PAPER, ndw, tracking=-0.3),
        centered_line(JB_REG, "NODE", 11, 346, OLIVE, ndw, tracking=3.0),
    ]
    write(
        "stickers/integrated.svg",
        svg(f"0 0 {ndw} {ndh}", "\n".join(node_sticker), label="integrated node"),
        group="Stickers",
        title="integrated",
        note="Node icon from the kit.",
    )

    # Die-cut speech bubble — the bubble is the vinyl shape
    b1_size = 20
    b1_track = -0.35
    line1, line2 = "specify or it", "will improvise"
    sbw, sbh = 400, 318
    # Rounded body of the path (excluding the tail), nudged down so the pair
    # sits in the visual middle of the whole lime shape.
    body_cx, body_cy = sbw / 2, 138.0
    line_gap = 28.0
    _, b1_miny, _, b1_maxy, _ = INTER_BOLD.ink_bounds(line1, b1_size, tracking=b1_track)
    _, b2_miny, _, b2_maxy, _ = INTER_BOLD.ink_bounds(line2, b1_size, tracking=b1_track)
    block_cy = ((b1_miny + b1_maxy) / 2 + (b2_miny + b2_maxy) / 2 + line_gap) / 2
    y1 = body_cy - block_cy
    y2 = y1 + line_gap
    bubble = [
        f'  <path fill="{LIME}" stroke="{PINK}" stroke-width="8" stroke-linejoin="round" '
        f'stroke-linecap="round" d="M94 232 L68 302 L148 232 H306 A72 72 0 0 0 378 160 '
        f'V90 A72 72 0 0 0 306 18 H94 A72 72 0 0 0 22 90 V160 A72 72 0 0 0 94 232 Z"/>',
        text_at_ink_center(INTER_BOLD, line1, b1_size, body_cx, y1 + (b1_miny + b1_maxy) / 2, INK, tracking=b1_track),
        text_at_ink_center(INTER_BOLD, line2, b1_size, body_cx, y2 + (b2_miny + b2_maxy) / 2, INK, tracking=b1_track),
    ]
    write(
        "stickers/speech-bubble.svg",
        svg(f"0 0 {sbw} {sbh}", "\n".join(bubble), label="specify or it will improvise bubble"),
        group="Stickers",
        title="Speech bubble",
        note="Die-cut bubble. Same line as the jellyfish vinyl.",
    )

    # Clubs Expo ticket — kit ticket icon as the die-cut
    expo_d, expo_w, _ = JB_BOLD.shape("CLUBS EXPO", 18, tracking=2.4)
    ticket_sticker = [
        f'  <path d="M16 28 h388 a28 28 0 0 1 0 104 H16 a28 28 0 0 1 0 -104Z" fill="{LIME}"/>',
        f'  <path d="M118 28 v104" stroke="{INK}" stroke-width="4" stroke-dasharray="6 7"/>',
        f'  <circle cx="66" cy="80" r="14" fill="{INK}"/>',
        f'  <g transform="translate({118 + (286 - expo_w) / 2:.1f} 90)">{path_text(expo_d, INK)}</g>',
    ]
    write(
        "stickers/clubs-expo-ticket.svg",
        svg("0 0 432 160", "\n".join(ticket_sticker), label="Clubs Expo ticket"),
        group="Stickers",
        title="Clubs Expo ticket",
        note="Ticket icon from the kit.",
    )

    url_d, url_w, _ = JB_BOLD.shape("UNNATURALINTELLIGENCE.CLUB", 15, tracking=1.6)
    sait_d, sait_w, _ = JB_REG.shape("SAIT STUDENT CLUB", 12, tracking=2.2)
    url_bar = max(url_w, sait_w)
    url_w_canvas = 86 + url_bar + 28
    url_sticker = [
        f'  <rect width="{url_w_canvas:.1f}" height="96" rx="16" fill="{INK}"/>',
        f'  <rect x="22" y="38" width="28" height="5" rx="2.5" fill="{LIME}"/>',
        f'  <rect x="54" y="38" width="18" height="5" rx="2.5" fill="{PINK}"/>',
        f'  <g transform="translate(86 46)">{path_text(url_d, PAPER)}</g>',
        f'  <g transform="translate(86 70)">{path_text(sait_d, OLIVE)}</g>',
    ]
    write(
        "stickers/club-url.svg",
        svg(f"0 0 {url_w_canvas:.1f} 96", "\n".join(url_sticker), label="unnaturalintelligence.club"),
        group="Stickers",
        title="Club URL",
        note="URL lockup as a strip sticker.",
    )

    # HALT / RESTART pair
    pair_w, pair_h = 560, 300
    pair = [
        "  <defs>",
        f'    <clipPath id="hrp"><rect width="{pair_w}" height="{pair_h}" rx="28"/></clipPath>',
        "  </defs>",
        '  <g clip-path="url(#hrp)">',
        f'    <rect width="280" height="{pair_h}" fill="{LIME}"/>',
        f'    <rect x="280" width="280" height="{pair_h}" fill="{INK}"/>',
        "  </g>",
        f'  <rect x="8" y="8" width="{pair_w - 16}" height="{pair_h - 16}" rx="22" fill="none" stroke="{PINK}" stroke-width="5"/>',
        f'  <path d="M280 22 v{pair_h - 44}" stroke="{PINK}" stroke-width="3" stroke-dasharray="7 8"/>',
        f'  <rect x="86" y="48" width="36" height="148" rx="8" fill="{INK}"/>',
        f'  <rect x="158" y="48" width="36" height="148" rx="8" fill="{INK}"/>',
        centered_line(DISPLAY, "HALT", 28, 248, INK, 280, tracking=-1.2, scale_x=0.88),
        restart_mark(420, 132, 62, PINK, 12),
        f'  <g transform="translate(280 0)">',
        centered_line(DISPLAY, "RESTART", 22, 248, PAPER, 280, tracking=-0.8, scale_x=0.88),
        "  </g>",
    ]
    write(
        "stickers/halt-and-restart.svg",
        svg(f"0 0 {pair_w} {pair_h}", "\n".join(pair), label="Halt and Restart pair"),
        group="Stickers",
        title="Halt & Restart",
        note="Paired die-cut. Pause and restart icons.",
    )

    # Die-cut outline jellyfish (white with no background)
    write(
        "stickers/jellyfish-diecut-paper.svg",
        svg(
            f"-40 -40 {JELLY_VB_W + 80} {JELLY_VB_H + 80}",
            f"  <defs>\n    {GRADIENT_DEFS}\n  </defs>\n" + jelly_path(PAPER),
            label="Jellyfish die-cut",
        ),
        group="Stickers",
        title="Die-cut jellyfish — paper",
        note="Transparent background. Print on vinyl.",
    )
    write(
        "stickers/jellyfish-diecut-gradient.svg",
        svg(
            f"-40 -40 {JELLY_VB_W + 80} {JELLY_VB_H + 80}",
            f"  <defs>\n    {GRADIENT_DEFS}\n  </defs>\n" + jelly_path("url(#uni-jelly)"),
            label="Jellyfish die-cut gradient",
        ),
        group="Stickers",
        title="Die-cut jellyfish — gradient",
    )


# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------

def badge(label_text: str, accent: str, filename: str, title: str) -> None:
    d, tw, _ = JB_BOLD.shape(label_text.upper(), 13, tracking=2.8)
    w = max(tw + 56, 160)
    h = 48
    inner = [
        f'  <rect width="{w:.1f}" height="{h}" rx="8" fill="{INK}" stroke="{accent}" stroke-width="2.5"/>',
        f'  <rect x="10" y="14" width="8" height="20" rx="2" fill="{accent}"/>',
        f'  <g transform="translate(28 31)">{path_text(d, PAPER)}</g>',
    ]
    write(
        f"badges/{filename}.svg",
        svg(f"0 0 {w:.1f} {h}", "\n".join(inner), label=label_text),
        group="Badges",
        title=title,
    )


def build_badges() -> None:
    badge("member", LIME, "member", "Member")
    badge("exec", PINK, "exec", "Exec")
    badge("workshop", OLIVE, "workshop", "Workshop")
    badge("live lab", CYAN, "live-lab", "Live lab")
    badge("clubs expo", LIME, "clubs-expo", "Clubs expo")
    badge("halt & restart", PINK, "halt-restart", "Halt & Restart")

    # Ticket badge matching Halt & Restart v3
    a, aw, _ = JB_BOLD.shape("LIVE PROMPTING LAB", 10, tracking=1.6)
    b, bw, _ = DISPLAY.shape("HALT", 28, tracking=-1.2, scale_x=0.88)
    amp, ampw, _ = DISPLAY.shape("&", 28, tracking=0, scale_x=0.88)
    c, cw, _ = DISPLAY.shape("RESTART", 28, tracking=-1.2, scale_x=0.88)
    td, tw, _ = JB_BOLD.shape("TICKET", 9, tracking=1.4)
    left = 18
    gap = 8
    halt_x = left
    amp_x = halt_x + bw + gap
    restart_x = amp_x + ampw + gap
    box_w, box_h = 64, 60
    w = max(420, restart_x + cw + 20 + box_w + 16, left + aw + 16)
    box_x = w - 14 - box_w
    inner = [
        f'  <rect width="{w:.1f}" height="88" rx="10" fill="{LIME}"/>',
        f'  <g transform="translate({left} 22)">{path_text(a, INK)}</g>',
        f'  <g transform="translate({halt_x:.1f} 68)">{path_text(b, INK)}</g>',
        f'  <g transform="translate({amp_x:.1f} 68)">{path_text(amp, PINK)}</g>',
        f'  <g transform="translate({restart_x:.1f} 68)">{path_text(c, INK)}</g>',
        f'  <rect x="{box_x:.1f}" y="14" width="{box_w}" height="{box_h}" fill="{INK}"/>',
        f'  <g transform="translate({box_x + (box_w - tw) / 2:.1f} 50)">{path_text(td, LIME)}</g>',
    ]
    write(
        "badges/halt-restart-ticket.svg",
        svg(f"0 0 {w:.1f} 88", "\n".join(inner), label="Halt & Restart ticket"),
        group="Badges",
        title="Halt & Restart ticket strip",
    )


# ---------------------------------------------------------------------------
# Patterns + frames
# ---------------------------------------------------------------------------

def build_patterns() -> None:
    def grid_sheet(stroke: str, opacity: str) -> str:
        return (
            "  <defs>\n"
            '    <pattern id="g" width="72" height="72" patternUnits="userSpaceOnUse">\n'
            f'      <path d="M72 0H0V72" fill="none" stroke="{stroke}" stroke-width="1.25" opacity="{opacity}"/>\n'
            "    </pattern>\n"
            "  </defs>\n"
            f'  <rect width="288" height="288" fill="{INK}"/>\n'
            '  <rect width="288" height="288" fill="url(#g)"/>'
        )

    write(
        "patterns/olive-grid-tile.svg",
        svg("0 0 288 288", grid_sheet(OLIVE, "0.45"), label="Olive grid tile"),
        group="Patterns",
        title="Olive grid tile",
        note="Repeat as a pattern. 72×72 cell.",
    )
    write(
        "patterns/lime-grid-tile.svg",
        svg("0 0 288 288", grid_sheet(LIME, "0.28"), label="Lime grid tile"),
        group="Patterns",
        title="Lime grid tile",
    )
    write(
        "patterns/pink-grid-tile.svg",
        svg("0 0 288 288", grid_sheet(PINK, "0.28"), label="Pink grid tile"),
        group="Patterns",
        title="Pink grid tile",
    )

    def grid_overlay(stroke: str, opacity: str, cell: int = 72) -> str:
        """Tileable grid with no background fill, so it composites as an overlay."""
        size = cell * 4
        return (
            "  <defs>\n"
            f'    <pattern id="g" width="{cell}" height="{cell}" patternUnits="userSpaceOnUse">\n'
            f'      <path d="M{cell} 0H0V{cell}" fill="none" stroke="{stroke}" stroke-width="1.35" opacity="{opacity}"/>\n'
            "    </pattern>\n"
            "  </defs>\n"
            f'  <rect width="{size}" height="{size}" fill="url(#g)"/>\n'
            f'  <path d="M{size} 0V{size}H0" fill="none" stroke="{stroke}" stroke-width="1.35" opacity="{opacity}"/>'
        )

    overlay_note = "Transparent. No background ink. Tile 288×288, cell 72. Repeat over a poster."
    for slug, color, opacity, title in (
        ("lime", LIME, "0.8", "Lime grid overlay"),
        ("pink", PINK, "0.8", "Pink grid overlay"),
        ("cyan", CYAN, "0.85", "Cyan grid overlay"),
        ("olive", OLIVE, "0.85", "Olive grid overlay"),
        ("paper", PAPER, "0.55", "Paper grid overlay"),
    ):
        write(
            f"patterns/grid-overlay-{slug}.svg",
            svg("0 0 288 288", grid_overlay(color, opacity), label=title),
            group="Patterns",
            title=title,
            note=overlay_note,
        )

    def tabloid_grid(stroke: str, minor: str, major: str) -> str:
        lines = []
        for i in range(0, 1101, 50):
            major_line = i % 100 == 0
            op = major if major_line else minor
            sw = "1.15" if major_line else "0.6"
            lines.append(
                f'  <line x1="{i}" y1="0" x2="{i}" y2="1700" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"/>'
            )
        for i in range(0, 1701, 50):
            major_line = i % 100 == 0
            op = major if major_line else minor
            sw = "1.15" if major_line else "0.6"
            lines.append(
                f'  <line x1="0" y1="{i}" x2="1100" y2="{i}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"/>'
            )
        lines.append(
            f'  <rect x="50" y="50" width="1000" height="1600" fill="none" stroke="{stroke}" '
            f'stroke-width="1.35" stroke-dasharray="8 6" opacity="{major}"/>'
        )
        return "\n".join(lines)

    grid_note = "11×17. Transparent. Half-inch grid, heavier inch lines, dashed 0.5 in safe margin."
    write(
        "patterns/grid-overlay-tabloid.svg",
        svg(
            "0 0 1100 1700",
            tabloid_grid(LIME, "0.38", "0.72"),
            w="11in",
            h="17in",
            label="Tabloid lime grid overlay",
        ),
        group="Patterns",
        title="Tabloid grid overlay — lime",
        note=grid_note,
    )
    write(
        "patterns/grid-overlay-tabloid-paper.svg",
        svg(
            "0 0 1100 1700",
            tabloid_grid(PAPER, "0.28", "0.55"),
            w="11in",
            h="17in",
            label="Tabloid paper grid overlay",
        ),
        group="Patterns",
        title="Tabloid grid overlay — paper",
        note=grid_note + " Use over lime, pink, or photography.",
    )

    # Wide wash with dual grid, like the 6×3 banner
    w, h = 1200, 400
    write(
        "patterns/banner-wash.svg",
        svg(f"0 0 {w} {h}", wash_bg(w, h), label="Banner wash background"),
        group="Patterns",
        title="Banner wash (wine + dual grid)",
        note="Drop behind lockups and posters.",
    )

    bars = []
    for i, col in enumerate((CYAN, PINK, PAPER, LIME, PINK, CYAN)):
        y = 8 + i * 10
        ox = (-6, 6, 0, 4, -5, 3)[i]
        bars.append(f'  <rect x="{12 + ox}" y="{y}" width="{88 - abs(ox)}" height="6" fill="{col}"/>')
    write(
        "patterns/glitch-bars.svg",
        svg("0 0 112 80", "\n".join(bars), label="Glitch bars"),
        group="Patterns",
        title="Glitch bars",
    )

    scans = [f'  <rect width="200" height="200" fill="{INK}"/>']
    for i in range(0, 200, 4):
        scans.append(f'  <rect y="{i}" width="200" height="1.2" fill="{PAPER}" opacity="0.06"/>')
    write("patterns/scanlines-tile.svg", svg("0 0 200 200", "\n".join(scans)), group="Patterns", title="Scanlines tile")

    write(
        "patterns/gradient-bar.svg",
        svg(
            "0 0 240 16",
            f'  <defs><linearGradient id="gb" x1="0" x2="1"><stop offset="0%" stop-color="{LIME}"/><stop offset="100%" stop-color="{PINK}"/></linearGradient></defs>\n'
            f'  <rect width="148" height="8" rx="4" fill="{LIME}"/>\n'
            f'  <rect x="156" width="84" height="8" rx="4" fill="{PINK}"/>',
            label="Lime–pink accent bar",
        ),
        group="Patterns",
        title="Accent bar (Halt & Restart eyebrow)",
    )

    # Tentacle flourish
    flourish = f"""
  <defs>
    <linearGradient id="fl" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{LIME}"/>
      <stop offset="100%" stop-color="{PINK}"/>
    </linearGradient>
  </defs>
  <path d="M8 20 C 40 8, 40 48, 72 36 C 104 24, 104 64, 136 52 C 168 40, 176 72, 200 64"
        fill="none" stroke="url(#fl)" stroke-width="10" stroke-linecap="round"/>
  <path d="M20 36 C 48 28, 56 68, 92 58 C 128 48, 132 88, 168 78"
        fill="none" stroke="url(#fl)" stroke-width="5" stroke-linecap="round" opacity="0.7"/>
"""
    write(
        "patterns/tentacle-flourish.svg",
        svg("0 0 208 96", flourish, label="Tentacle flourish"),
        group="Patterns",
        title="Tentacle flourish",
    )

    # Dashed ticket frame (filled sample, kept for the old proportion)
    write(
        "frames/dashed-ticket.svg",
        svg(
            "0 0 400 560",
            f'  <rect width="400" height="560" fill="{INK}"/>\n'
            f'  <rect x="16" y="16" width="368" height="528" fill="none" stroke="{LIME}" stroke-width="3" stroke-dasharray="10 8" opacity="0.55"/>',
            label="Dashed ticket frame",
        ),
        group="Frames",
        title="Dashed ticket frame (11×17 proportion)",
    )

    def tabloid_frame(inner: str, filename: str, title: str, label: str, note: str) -> None:
        write(
            f"frames/{filename}.svg",
            svg("0 0 1100 1700", inner, w="11in", h="17in", label=label),
            group="Frames",
            title=title,
            note=note,
        )

    frame_note = "11×17 trim. Transparent interior. Strokes sit inside the sheet so a no-bleed print keeps the frame."
    tabloid_frame(
        f'  <rect x="14" y="14" width="1072" height="1672" fill="none" stroke="{LIME}" stroke-width="3.5" stroke-dasharray="18 12"/>',
        "tabloid-dashed-lime",
        "Tabloid border — dashed lime",
        "Tabloid dashed lime border",
        frame_note + " Inset 0.14 in, matching the arcade-ticket poster.",
    )
    tabloid_frame(
        f'  <rect x="12" y="12" width="1076" height="1676" fill="none" stroke="{LIME}" stroke-width="4"/>\n'
        f'  <rect x="26" y="26" width="1048" height="1648" fill="none" stroke="{PINK}" stroke-width="2.5"/>',
        "tabloid-double",
        "Tabloid border — double lime and pink",
        "Tabloid double border",
        frame_note,
    )
    ticks = []
    leg = 46
    for x, y, dx, dy, color in (
        (18, 18, 1, 1, LIME),
        (1082, 18, -1, 1, PINK),
        (1082, 1682, -1, -1, CYAN),
        (18, 1682, 1, -1, OLIVE),
    ):
        ticks.append(
            f'  <path d="M{x + dx * leg} {y} H{x} V{y + dy * leg}" fill="none" stroke="{color}" '
            f'stroke-width="5" stroke-linecap="square" stroke-linejoin="miter"/>'
        )
    tabloid_frame(
        "\n".join(ticks),
        "tabloid-corner-ticks",
        "Tabloid border — corner ticks",
        "Tabloid corner ticks",
        frame_note + " Lime, pink, cyan, olive. 0.46 in legs, inset 0.18 in.",
    )
    tabloid_frame(
        f'  <path d="M18 18H1082" fill="none" stroke="{LIME}" stroke-width="8" stroke-linecap="butt"/>\n'
        f'  <path d="M1082 18V1682" fill="none" stroke="{PINK}" stroke-width="8" stroke-linecap="butt"/>\n'
        f'  <path d="M1082 1682H18" fill="none" stroke="{CYAN}" stroke-width="8" stroke-linecap="butt"/>\n'
        f'  <path d="M18 1682V18" fill="none" stroke="{OLIVE}" stroke-width="8" stroke-linecap="butt"/>\n'
        f'  <rect x="36" y="36" width="1028" height="1628" fill="none" stroke="{PAPER}" stroke-width="1.5" opacity="0.85"/>',
        "tabloid-segmented",
        "Tabloid border — four fact colours",
        "Tabloid segmented border",
        frame_note + " Top lime, right pink, bottom cyan, left olive.",
    )
    tabloid_frame(
        f'  <rect x="18" y="18" width="1064" height="1664" fill="none" stroke="{PAPER}" stroke-width="1.75"/>',
        "tabloid-paper-hairline",
        "Tabloid border — paper hairline",
        "Tabloid paper hairline",
        frame_note,
    )
    # Column geometry matches fact-bars/strip.svg (100 units = 1 in).
    rule_cols = []
    rule_x = 42.0
    for width, color in zip(fact_column_widths(), (LIME, PINK, CYAN, OLIVE)):
        rule_cols.append(
            f'  <rect x="{rule_x:.2f}" y="22" width="{width:.2f}" height="8" fill="{color}"/>'
        )
        rule_cols.append(
            f'  <rect x="{rule_x:.2f}" y="1670" width="{width:.2f}" height="8" fill="{color}"/>'
        )
        rule_x += width + 10
    rule_cols.append(
        f'  <path d="M28 40V1660" fill="none" stroke="{PAPER}" stroke-width="1.5" opacity="0.8"/>'
    )
    rule_cols.append(
        f'  <path d="M1072 40V1660" fill="none" stroke="{PAPER}" stroke-width="1.5" opacity="0.8"/>'
    )
    tabloid_frame(
        "\n".join(rule_cols),
        "tabloid-fact-rules",
        "Tabloid border — fact-bar rules",
        "Tabloid fact-bar rules",
        frame_note + " Top and bottom rules use the same columns as the fact-bar strip.",
    )


# ---------------------------------------------------------------------------
# Fact bars (when / where / type / who)
# ---------------------------------------------------------------------------

def build_fact_bars() -> None:
    """Outlined templates of the poster fact strip. 100 units = 1 inch."""
    facts = (
        ("when", "WHEN", "MONDAYS", "6:00 – 8:00 PM", LIME),
        ("where", "WHERE", "ROOM TBA", "SAIT campus", PINK),
        ("type", "TYPE", "STUDENT CLUB", "Social game night · live AI demo", CYAN),
        ("who", "WHO", "FREE", "Every program · beginners welcome", OLIVE),
    )
    label_size = 9.5
    label_track = 0.16 * label_size
    value_size = 28
    value_track = -0.035 * value_size
    sub_size = 12.5
    pad = 42.0
    gap = 10.0
    rule_h = 5.5
    widths = fact_column_widths(pad=pad, gap=gap)

    _, label_top_ink, _, _, _ = JB_BOLD.ink_bounds("WHERE", label_size, tracking=label_track)
    _, value_top_ink, _, value_bot_ink, _ = DISPLAY.ink_bounds("MONDAYS", value_size, tracking=value_track)
    sub_top_ink = 0.0
    sub_bot_ink = 0.0
    for _, _, _, sub, _ in facts:
        _, miny, _, maxy, _ = INTER_MED.ink_bounds(sub, sub_size)
        sub_top_ink = min(sub_top_ink, miny)
        sub_bot_ink = max(sub_bot_ink, maxy)

    label_base = rule_h + 10.0 - label_top_ink
    value_base = label_base + 11.0 - value_top_ink
    sub_base = value_base + value_bot_ink + 8.0 - sub_top_ink
    height = round(sub_base + sub_bot_ink + 16.0, 2)

    def column_parts(x: float, width: float, label: str, value: str, sub: str, color: str, *, values: bool) -> list[str]:
        parts = [
            f'  <rect x="{x:.2f}" y="0" width="{width:.2f}" height="{rule_h}" fill="{color}"/>',
        ]
        ld, _, _ = JB_BOLD.shape(label, label_size, tracking=label_track)
        lmin, _, lmax, _, _ = JB_BOLD.ink_bounds(label, label_size, tracking=label_track)
        if x + lmax > x + width + 0.5 or lmin < -1:
            raise SystemExit(f"Fact label {label!r} does not fit its column")
        parts.append(f'  <g transform="translate({x:.2f} {label_base:.2f})">{path_text(ld, PINK)}</g>')
        if not values:
            return parts
        vd, _, _ = DISPLAY.shape(value, value_size, tracking=value_track)
        vmin, _, vmax, _, _ = DISPLAY.ink_bounds(value, value_size, tracking=value_track)
        sd, _, _ = INTER_MED.shape(sub, sub_size)
        smin, _, smax, _, _ = INTER_MED.ink_bounds(sub, sub_size)
        if max(vmax, smax) > width - 4 or min(vmin, smin) < -1:
            raise SystemExit(
                f"Fact copy {value!r} / {sub!r} overflows a {width:.1f} unit column "
                f"(value {vmax:.1f}, sub {smax:.1f})"
            )
        parts.append(f'  <g transform="translate({x:.2f} {value_base:.2f})">{path_text(vd, PAPER)}</g>')
        parts.append(
            f'  <g transform="translate({x:.2f} {sub_base:.2f})">'
            f'{path_text(sd, PAPER, extra=" opacity=\"0.72\"")}</g>'
        )
        return parts

    def strip_body(*, background: bool, values: bool) -> str:
        parts: list[str] = []
        if background:
            parts.append(f'  <rect width="1100" height="{height:.2f}" fill="{INK}"/>')
        x = pad
        for (slug, label, value, sub, color), width in zip(facts, widths):
            parts.extend(column_parts(x, width, label, value, sub, color, values=values))
            x += width + gap
        return "\n".join(parts)

    h_in = f"{height / 100:.3f}in"
    view = f"0 0 1100 {height:.2f}"
    write(
        "fact-bars/strip.svg",
        svg(view, strip_body(background=True, values=True), w="11in", h=h_in, label="Fact bar strip"),
        group="Fact bars",
        title="Fact bar strip",
        note="When lime, where pink, type cyan, who olive. 11 in wide, on ink. Matches the Presents poster.",
    )
    write(
        "fact-bars/strip-clear.svg",
        svg(view, strip_body(background=False, values=True), w="11in", h=h_in, label="Fact bar strip, transparent"),
        group="Fact bars",
        title="Fact bar strip — transparent",
        note="Same strip with no background, for overlaying a poster.",
    )
    scaffold_h = round(label_base + 14.0, 2)
    write(
        "fact-bars/scaffold.svg",
        svg(
            f"0 0 1100 {scaffold_h:.2f}",
            strip_body(background=False, values=False),
            w="11in",
            h=f"{scaffold_h / 100:.3f}in",
            label="Fact bar scaffold",
        ),
        group="Fact bars",
        title="Fact bar scaffold",
        note="Rules and labels only. Transparent. Set your own value and subline in the HTML template.",
    )
    for (slug, label, value, sub, color), width in zip(facts, widths):
        body = "\n".join(column_parts(0, width, label, value, sub, color, values=True))
        write(
            f"fact-bars/{slug}.svg",
            svg(
                f"0 0 {width:.2f} {height:.2f}",
                body,
                w=f"{width / 100:.3f}in",
                h=h_in,
                label=f"{label.title()} fact bar",
            ),
            group="Fact bars",
            title=f"{label.title()} bar",
            note="Transparent single column. Gap the four bars 0.10 in apart.",
        )


# ---------------------------------------------------------------------------
# Avatars + social
# ---------------------------------------------------------------------------

def build_avatars() -> None:
    def avatar(filename: str, bg_inner: str, jelly_fill: str, title: str, rounded: float | None = 0, circle: bool = False) -> None:
        clip = ""
        shape = f'  <rect width="512" height="512" fill="{INK}"/>'
        if circle:
            clip = '  <clipPath id="c"><circle cx="256" cy="256" r="256"/></clipPath>\n'
            shape = '  <g clip-path="url(#c)">'
        elif rounded:
            clip = f'  <clipPath id="c"><rect width="512" height="512" rx="{rounded}"/></clipPath>\n'
            shape = '  <g clip-path="url(#c)">'
        body = [
            "  <defs>",
            f"    {GRADIENT_DEFS}",
            '    <pattern id="ag" width="28" height="28" patternUnits="userSpaceOnUse">',
            f'      <path d="M28 0H0V28" fill="none" stroke="{LIME}" stroke-width="1" opacity="0.22"/>',
            "    </pattern>",
            clip,
            "  </defs>",
        ]
        if circle or rounded:
            body.append(shape)
            body.append(bg_inner)
            body.append(jelly_centered(256, 256, 456, jelly_fill))
            body.append("  </g>")
        else:
            body.append(bg_inner)
            body.append(jelly_centered(256, 256, 456, jelly_fill))
        write(
            f"avatars/{filename}.svg",
            svg("0 0 512 512", "\n".join(body), label="Unnatural Intelligence avatar"),
            group="Avatars",
            title=title,
        )

    grid_bg = (
        f'  <rect width="512" height="512" fill="{INK}"/>\n'
        f'  <rect width="512" height="512" fill="{WINE}" opacity="0.5"/>\n'
        f'  <rect width="512" height="512" fill="url(#ag)"/>'
    )

    avatar("ink-gradient", grid_bg, "url(#uni-jelly)", "Avatar — ink + gradient")
    avatar("ink-paper", f'  <rect width="512" height="512" fill="{INK}"/>', PAPER, "Avatar — ink + paper")
    avatar("lime", f'  <rect width="512" height="512" fill="{LIME}"/>', INK, "Avatar — lime")
    avatar("pink", f'  <rect width="512" height="512" fill="{PINK}"/>', PAPER, "Avatar — pink")
    avatar("wine", f'  <rect width="512" height="512" fill="{WINE}"/>', LIME, "Avatar — wine")
    avatar("paper", f'  <rect width="512" height="512" fill="{PAPER}"/>', INK, "Avatar — paper")
    avatar("circle-gradient", grid_bg, "url(#uni-jelly)", "Avatar — circle", circle=True)
    avatar("rounded-gradient", grid_bg, "url(#uni-jelly)", "Avatar — rounded (Discord / Slack)", rounded=96)

    tag, tw, _ = INTER_MED.shape("GENERATED BY AI  ·  PERFECTED BY HUMANS", 18, tracking=4.0)

    # Instagram — smaller jellyfish so type sits in the clear column on the right
    W, H = 1080, 1080
    d1, w1, _ = DISPLAY.shape("UNNATURAL", 78, tracking=-4.0, scale_x=0.84)
    d2, w2, _ = DISPLAY.shape("INTELLIGENCE", 78, tracking=-4.0, scale_x=0.84)
    ig_jelly_h = 500
    ig_jelly_w = ig_jelly_h * (JELLY_VB_W / JELLY_VB_H)
    ig_type_x = 48 + ig_jelly_w + 72
    ig_tag, _, _ = INTER_MED.shape("GENERATED BY AI  ·  PERFECTED BY HUMANS", 15, tracking=2.0)
    ig = [
        wash_bg(W, H),
        jelly_at(48, 220, ig_jelly_h, "url(#uni-jelly)"),
        f'  <g transform="translate({ig_type_x:.1f} 430)">{glitch_word(d1, PAPER, dx=4, dy=1.5)}</g>',
        f'  <g transform="translate({ig_type_x:.1f} 518)">{glitch_word(d2, PAPER, dx=4, dy=1.5)}</g>',
        f'  <g transform="translate({ig_type_x:.1f} 590)">{path_text(ig_tag, "rgba(249,249,250,0.8)")}</g>',
    ]
    write(
        "social/instagram-1080.svg",
        svg(f"0 0 {W} {H}", "\n".join(ig), label="Instagram post"),
        group="Social",
        title="Instagram post 1080×1080",
    )

    # Story — jellyfish in the upper half, wordmark below the tentacles
    SW, SH = 1080, 1920
    sd1, _, _ = DISPLAY.shape("UNNATURAL", 92, tracking=-4.8, scale_x=0.84)
    sd2, _, _ = DISPLAY.shape("INTELLIGENCE", 92, tracking=-4.8, scale_x=0.84)
    story_jelly_h = 820
    story = [
        wash_bg(SW, SH),
        jelly_at((SW - story_jelly_h * (JELLY_VB_W / JELLY_VB_H)) / 2, 220, story_jelly_h, "url(#uni-jelly)"),
        f'  <g transform="translate(90 1240)">{glitch_word(sd1, PAPER, dx=5, dy=2)}</g>',
        f'  <g transform="translate(90 1350)">{glitch_word(sd2, PAPER, dx=5, dy=2)}</g>',
        f'  <g transform="translate(90 1440)">{path_text(tag, "rgba(249,249,250,0.8)")}</g>',
    ]
    write(
        "social/story-1080x1920.svg",
        svg(f"0 0 {SW} {SH}", "\n".join(story), label="Instagram / TikTok story"),
        group="Social",
        title="Story 1080×1920",
    )

    # Banner
    BW, BH = 1500, 500
    b1, _, _ = DISPLAY.shape("UNNATURAL", 70, tracking=-3.6, scale_x=0.84)
    b2, _, _ = DISPLAY.shape("INTELLIGENCE", 70, tracking=-3.6, scale_x=0.84)
    banner = [
        wash_bg(BW, BH),
        jelly_at(48, 40, 420, "url(#uni-jelly)"),
        f'  <g transform="translate(520 200)">{glitch_word(b1, PAPER)}</g>',
        f'  <g transform="translate(520 278)">{glitch_word(b2, PAPER)}</g>',
        f'  <g transform="translate(520 340)">{path_text(tag, "rgba(249,249,250,0.8)")}</g>',
    ]
    write(
        "social/banner-1500x500.svg",
        svg(f"0 0 {BW} {BH}", "\n".join(banner), label="Social banner"),
        group="Social",
        title="Banner 1500×500",
    )

    OW, OH = 1200, 630
    o1, _, _ = DISPLAY.shape("UNNATURAL", 64, tracking=-3.2, scale_x=0.84)
    o2, _, _ = DISPLAY.shape("INTELLIGENCE", 64, tracking=-3.2, scale_x=0.84)
    og_jelly_h = 440
    og_jelly_w = og_jelly_h * (JELLY_VB_W / JELLY_VB_H)
    og_type_x = 36 + og_jelly_w + 64
    og = [
        wash_bg(OW, OH),
        jelly_at(36, 95, og_jelly_h, "url(#uni-jelly)"),
        f'  <g transform="translate({og_type_x:.1f} 250)">{glitch_word(o1, PAPER)}</g>',
        f'  <g transform="translate({og_type_x:.1f} 328)">{glitch_word(o2, PAPER)}</g>',
        f'  <g transform="translate({og_type_x:.1f} 390)">{path_text(tag, "rgba(249,249,250,0.8)")}</g>',
    ]
    write(
        "social/og-1200x630.svg",
        svg(f"0 0 {OW} {OH}", "\n".join(og), label="Open Graph share image"),
        group="Social",
        title="Open Graph 1200×630",
    )


# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------

def build_palette() -> None:
    swatches = [
        ("PAPER", PAPER, INK),
        ("OLIVE", OLIVE, INK),
        ("INK", INK, PAPER),
        ("PINK", PINK, PAPER),
        ("WINE", WINE, PAPER),
        ("LIME", LIME, INK),
        ("CYAN", CYAN, INK),
    ]
    w = 140 * len(swatches)
    parts = [f'  <rect width="{w}" height="240" fill="{PAPER}"/>']
    for i, (name, col, fg) in enumerate(swatches):
        x = i * 140
        nd, nw, _ = JB_BOLD.shape(name, 12, tracking=1.2)
        hd, hw, _ = JB_BOLD.shape(col.upper(), 11, tracking=0.6)
        parts.append(f'  <rect x="{x}" width="140" height="240" fill="{col}"/>')
        parts.append(f'  <g transform="translate({x + 12} 200) rotate(-90)">{path_text(nd, fg)}</g>')
        parts.append(f'  <g transform="translate({x + 36} 210) rotate(-90)">{path_text(hd, fg)}</g>')
    write(
        "palette/swatches.svg",
        svg(f"0 0 {w} 240", "\n".join(parts), label="Unnatural Intelligence palette"),
        group="Palette",
        title="Colour swatches",
    )
    (ROOT / "palette" / "colors.json").write_text(
        json.dumps(
            {
                "paper": PAPER,
                "olive": OLIVE,
                "ink": INK,
                "pink": PINK,
                "wine": WINE,
                "lime": LIME,
                "cyan": CYAN,
                "gradient": {"from": LIME, "to": PINK},
                "fonts": {"display": "Inter Display", "sans": "Inter", "mono": "JetBrains Mono"},
            },
            indent=2,
        )
        + "\n"
    )
    MANIFEST.append({"file": "palette/colors.json", "group": "Palette", "title": "Colour tokens (JSON)", "note": ""})
    (ROOT / "palette" / "tokens.css").write_text(
        f""":root {{
  --uni-paper: {PAPER};
  --uni-olive: {OLIVE};
  --uni-ink: {INK};
  --uni-pink: {PINK};
  --uni-wine: {WINE};
  --uni-lime: {LIME};
  --uni-cyan: {CYAN};
}}
"""
    )
    MANIFEST.append({"file": "palette/tokens.css", "group": "Palette", "title": "Colour tokens (CSS)", "note": ""})


# ---------------------------------------------------------------------------
# Preview + README
# ---------------------------------------------------------------------------

def build_preview() -> None:
    groups: dict[str, list[dict]] = {}
    for item in MANIFEST:
        groups.setdefault(item["group"], []).append(item)

    cards = []
    for group, items in groups.items():
        cards.append(f'<h2>{html.escape(group)}</h2><div class="grid">')
        for it in items:
            if it["file"].endswith((".json", ".css", ".html", ".md")):
                continue
            if it["file"].endswith("-plain.svg"):
                continue
            light = any(
                s in it["file"]
                for s in (
                    "light",
                    "on-paper",
                    "on-lime",
                    "on-pink",
                    "wordmark-ink",
                    "jellyfish-ink.svg",
                    "jellyfish-wine",
                    "jellyfish-currentColor",
                    "jellyfish-mini.svg",
                    "horizontal-lime",
                    "halt-restart-ticket",
                    "swatches",
                    "generated-by-ai",
                    "stickers/halt.svg",
                    "live-prompting-lab",
                    "speech-bubble",
                    "clubs-expo-ticket",
                    "circle-lime",
                    "avatars/lime",
                    "avatars/paper",
                    "avatars/pink",
                    "favicon",
                )
            )
            wide = any(
                s in it["file"]
                for s in (
                    "banner",
                    "instagram",
                    "story",
                    "og-1200",
                    "dashed-ticket",
                    "live-prompting-lab",
                    "lean-meter",
                    "fold-into-tuesday",
                    "glitch-unnatural",
                    "glitch-intelligence",
                    "club-url",
                    "clubs-expo-ticket",
                    "halt-and-restart",
                    "speech-bubble",
                    "wordmark-laptop",
                    "fact-bars/strip",
                    "fact-bars/scaffold",
                    "games-lean",
                    "games-spine",
                    "games-stripe",
                    "games-slice",
                    "games-steps",
                    "games-cross",
                    "games-fan",
                    "games-ticket",
                    "games-swim",
                    "games-overlap",
                    "games-quad",
                )
            )
            tone = "light" if light else "dark"
            span = " wide" if wide else ""
            note = f'<p class="note">{html.escape(it["note"])}</p>' if it["note"] else ""
            cards.append(
                f'<figure class="{tone}{span}">'
                f'<div class="frame"><img src="{html.escape(it["file"])}" alt="{html.escape(it["title"])}"></div>'
                f'<figcaption><strong>{html.escape(it["title"])}</strong>'
                f'<code>{html.escape(it["file"])}</code>{note}</figcaption></figure>'
            )
        cards.append("</div>")

    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vector kit — Unnatural Intelligence</title>
<style>
  @font-face {{ font-family: "Inter"; src: url("../../charter/fonts/Inter-Regular.ttf") format("truetype"); font-weight: 400; }}
  @font-face {{ font-family: "Inter"; src: url("../../charter/fonts/Inter-SemiBold.ttf") format("truetype"); font-weight: 600; }}
  @font-face {{ font-family: "Inter Display"; src: url("../../charter/fonts/InterDisplay-Bold.ttf") format("truetype"); font-weight: 700; }}
  @font-face {{ font-family: "JetBrains Mono"; src: url("../../charter/fonts/JetBrainsMono-Regular.ttf") format("truetype"); font-weight: 400; }}
  :root {{
    --paper: {PAPER}; --olive: {OLIVE}; --ink: {INK}; --pink: {PINK};
    --wine: {WINE}; --lime: {LIME}; --cyan: {CYAN};
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; background: #14040c; color: var(--paper); font-family: Inter, sans-serif; }}
  header {{
    padding: 48px 32px 24px; max-width: 1200px; margin: 0 auto;
  }}
  h1 {{
    font-family: "Inter Display", Inter, sans-serif; font-size: 42px; letter-spacing: -0.05em;
    text-transform: uppercase; margin: 0 0 8px; line-height: 0.9;
  }}
  .sub {{ font-family: "JetBrains Mono", monospace; font-size: 13px; letter-spacing: 0.18em; text-transform: uppercase; color: var(--lime); }}
  p.lede {{ max-width: 62ch; color: rgba(249,249,250,.72); line-height: 1.5; }}
  h2 {{
    font-family: "JetBrains Mono", monospace; font-size: 12px; letter-spacing: 0.2em;
    text-transform: uppercase; color: var(--pink); margin: 48px 0 16px; max-width: 1200px;
    margin-left: auto; margin-right: auto; padding: 0 32px;
  }}
  .grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 18px; max-width: 1200px; margin: 0 auto 24px; padding: 0 32px;
  }}
  figure {{ margin: 0; border: 1px solid rgba(186,248,55,.18); background: rgba(3,2,5,.55); }}
  .frame {{
    aspect-ratio: 1; display: grid; place-items: center; padding: 18px;
    background-image:
      linear-gradient(rgba(149,183,71,.18) 1px, transparent 1px),
      linear-gradient(90deg, rgba(149,183,71,.18) 1px, transparent 1px);
    background-size: 18px 18px;
  }}
  figure.light .frame {{ background-color: var(--paper); }}
  figure.dark .frame {{ background-color: var(--ink); }}
  figure.wide {{ grid-column: span 2; }}
  figure.wide .frame {{ aspect-ratio: 16 / 6; }}
  img {{ max-width: 100%; max-height: 180px; display: block; }}
  figure.wide img {{ max-height: 160px; width: auto; }}
  figcaption {{ padding: 10px 12px 14px; border-top: 1px solid rgba(186,248,55,.12); }}
  figcaption strong {{ display: block; font-size: 13px; }}
  figcaption code {{
    display: block; margin-top: 4px; font-family: "JetBrains Mono", monospace;
    font-size: 10px; color: var(--olive); word-break: break-all;
  }}
  .note {{ margin: 6px 0 0; font-size: 12px; color: rgba(249,249,250,.55); }}
  footer {{
    max-width: 1200px; margin: 48px auto; padding: 0 32px 64px;
    font-family: "JetBrains Mono", monospace; font-size: 11px; color: rgba(249,249,250,.45);
    letter-spacing: 0.08em;
  }}
</style>
</head>
<body>
<header>
  <div class="sub">Unnatural Intelligence · Vector kit</div>
  <h1>Graphical<br>assets</h1>
  <p class="lede">Self-contained SVGs in the club palette. Lime #BAF837 to pink #FA4A9E on ink #030205, with olive grid, wine wash, and a cyan glitch twin. Generated from the official jellyfish path plus a simplified mini mark for small sizes.</p>
</header>
{''.join(cards)}
<footer>UNNATURALINTELLIGENCE.CLUB — SAIT STUDENT CLUB · regenerate with python3 generate.py</footer>
</body>
</html>
"""
    (ROOT / "preview.html").write_text(doc)
    MANIFEST.append({"file": "preview.html", "group": "Meta", "title": "Catalog preview", "note": ""})


def build_readme() -> None:
    (ROOT / "README.md").write_text(
        """# Vector kit

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
"""
    )


def inch_raster(rel: str, svg_text: str) -> tuple[int, int] | None:
    """SVGs with width/height in inches print at 300 DPI (letter sheets at 150)."""
    wm = re.search(r'\bwidth="([\d.]+)in"', svg_text)
    hm = re.search(r'\bheight="([\d.]+)in"', svg_text)
    if not (wm and hm):
        return None
    name = Path(rel).name
    # Letter and tabloid sheets are catalog previews. The SVG is the print file.
    dpi = 150 if ("letter" in name or "tabloid" in name) else 300
    return max(1, round(float(wm.group(1)) * dpi)), max(1, round(float(hm.group(1)) * dpi))


def viewbox_size(svg_text: str) -> tuple[float, float]:
    m = re.search(r'viewBox="([^"]+)"', svg_text)
    if not m:
        raise ValueError("SVG missing viewBox")
    parts = m.group(1).split()
    return float(parts[2]), float(parts[3])


def sample_wh(rel: str, vb_w: float, vb_h: float) -> tuple[int, int]:
    """Preview-sized raster. Social templates stay native; marks cap at 512px."""
    folder = rel.split("/", 1)[0]
    name = Path(rel).name
    longest = max(vb_w, vb_h, 1.0)
    if folder == "social":
        scale = 1.0
    elif folder == "avatars":
        return 512, 512
    elif name == "favicon.svg":
        return 128, 128
    elif folder == "icons":
        scale = 2.0 if "sprite" in name else 128 / longest
    elif folder == "badges":
        scale = 3.0
    elif folder == "marks":
        scale = 512 / longest
    elif folder == "lockups":
        scale = min(2.0, 1000 / vb_w)
    elif folder == "stickers":
        scale = min(2.0, 640 / longest)
    elif folder == "frames":
        scale = 1.5
    elif folder == "patterns":
        scale = 1.0 if vb_w >= 400 else 2.0
    elif folder == "fact-bars":
        scale = 1.0 if vb_w >= 600 else 2.0
    elif folder == "palette":
        scale = 1.0
    else:
        scale = min(2.0, 512 / longest)
    return max(1, round(vb_w * scale)), max(1, round(vb_h * scale))


def rasterize_pngs() -> int:
    """Write a PNG sample for every SVG under this kit."""
    import cairosvg
    from PIL import Image

    if PNG_ROOT.exists():
        shutil.rmtree(PNG_ROOT)

    count = 0
    for svg_path in sorted(ROOT.rglob("*.svg")):
        if PNG_ROOT in svg_path.parents:
            continue
        rel = svg_path.relative_to(ROOT).as_posix()
        text = svg_path.read_text()
        vb_w, vb_h = viewbox_size(text)
        inch = inch_raster(rel, text)
        width, _height = inch if inch else sample_wh(rel, vb_w, vb_h)
        dest = PNG_ROOT / Path(rel).with_suffix(".png")
        dest.parent.mkdir(parents=True, exist_ok=True)
        raw = cairosvg.svg2png(url=str(svg_path), output_width=width)
        im = Image.open(io.BytesIO(raw))
        im.save(dest, "PNG", optimize=True)
        count += 1
    return count


def build_games_logos() -> None:
    """Unnatural Games marks. Same palette and type, not the club wordmark.

    The club mark is two horizontal lines with a cyan/pink offset. The marks
    use shear, a vertical spine, a clipped stripe, a circular seal, a slice,
    a rising rank, a crossed pair, a monogram plate, a card fan, a ticket stub,
    and five jellyfish constructions (crest, swim, overlap, quad, badge).
    """

    def ink_of(font: Font, text: str, size: float, *, tracking: float = 0, scale_x: float = 1.0):
        d, _, _ = font.shape(text, size, tracking=tracking, scale_x=scale_x)
        return (d, *font.ink_bounds(text, size, tracking=tracking, scale_x=scale_x))

    def arc_line(
        font: Font,
        text: str,
        cx: float,
        cy: float,
        radius: float,
        size: float,
        fill: str,
        *,
        tracking: float = 0,
        smile: bool = False,
    ) -> str:
        glyphs = []
        total = 0.0
        for ch in text:
            d, w, _ = font.shape(ch, size, tracking=tracking)
            glyphs.append((d, w))
            total += w
        angle = -total / (2 * radius)
        parts = []
        for d, w in glyphs:
            mid = angle + w / (2 * radius)
            if smile:
                x = cx + radius * math.sin(mid)
                y = cy + radius * math.cos(mid)
                deg = -math.degrees(mid)
            else:
                x = cx + radius * math.sin(mid)
                y = cy - radius * math.cos(mid)
                deg = math.degrees(mid)
            parts.append(
                f'  <g transform="translate({x:.2f} {y:.2f}) rotate({deg:.2f}) translate({-w / 2:.2f} 0)">'
                f"{path_text(d, fill)}</g>"
            )
            angle += w / radius
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # 1. Lean — shared shear, extended GAMES on a lime slab
    # ------------------------------------------------------------------
    g_size, g_track, g_sx = 112, -1.6, 1.06
    gd, gx0, gy0, gx1, gy1, _ = ink_of(DISPLAY, "GAMES", g_size, tracking=g_track, scale_x=g_sx)
    ud, ux0, uy0, ux1, uy1, _ = ink_of(JB_BOLD, "UNNATURAL", 22, tracking=4.4)
    shear = -16
    bar_pad_x, bar_top, bar_bot = 28, 18, 16
    # Local space: GAMES baseline at y=0. Bar wraps the word. Eyebrow sits above the bar.
    bar_x0 = gx0 - bar_pad_x
    bar_x1 = gx1 + bar_pad_x
    bar_y0 = gy0 - bar_top
    bar_y1 = gy1 + bar_bot
    eye_y = bar_y0 - 16
    eye_x = bar_x0 + 6
    t = math.tan(math.radians(shear))
    pts = []
    for x in (bar_x0, bar_x1, eye_x + ux0, eye_x + ux1):
        for y in (bar_y0, bar_y1, eye_y + uy0, eye_y + uy1):
            pts.append((x + y * t, y))
    minx = min(p[0] for p in pts) - 36
    miny = min(p[1] for p in pts) - 28
    maxx = max(p[0] for p in pts) + 48
    maxy = max(p[1] for p in pts) + 36
    lean_w, lean_h = maxx - minx, maxy - miny
    lean = [
        f'  <rect width="{lean_w:.1f}" height="{lean_h:.1f}" fill="{INK}"/>',
        f'  <g transform="translate({-minx:.2f} {-miny:.2f}) skewX({shear})">',
        f'    <rect x="{bar_x0:.2f}" y="{bar_y0:.2f}" width="{bar_x1 - bar_x0:.2f}" height="{bar_y1 - bar_y0:.2f}" fill="{LIME}"/>',
        f'    <rect x="{bar_x0:.2f}" y="{bar_y1 + 8:.2f}" width="{(bar_x1 - bar_x0) * 0.42:.2f}" height="7" fill="{PINK}"/>',
        f'    <g transform="translate({eye_x:.2f} {eye_y:.2f})">{path_text(ud, PAPER)}</g>',
        f"    {path_text(gd, INK)}",
        "  </g>",
    ]
    write(
        "lockups/games-lean.svg",
        svg(f"0 0 {lean_w:.1f} {lean_h:.1f}", "\n".join(lean), label="Unnatural Games — lean"),
        group="Games logos",
        title="Games — lean",
        note="Shared −16° shear. Extended GAMES on a lime slab. Not the club glitch wordmark.",
    )

    # ------------------------------------------------------------------
    # 2. Spine — UNNATURAL on the vertical, GAMES on a tipped rule
    # ------------------------------------------------------------------
    sd, sx0, sy0, sx1, sy1, sadv = ink_of(DISPLAY, "UNNATURAL", 34, tracking=3.2)
    gd, gx0, gy0, gx1, gy1, _ = ink_of(DISPLAY, "GAMES", 108, tracking=-1.4, scale_x=1.0)
    # rotate(-90) sends the word upward and the caps to the left.
    cap = -sy0
    spine_origin_x = 32 + cap
    spine_origin_y = 40 + sadv
    games_x = spine_origin_x + 36
    games_y = spine_origin_y - 36
    sw = games_x + gx1 + 48
    sh = spine_origin_y + 44
    spine = [
        f'  <rect width="{sw:.1f}" height="{sh:.1f}" fill="{INK}"/>',
        f'  <g transform="translate({spine_origin_x:.2f} {spine_origin_y:.2f}) rotate(-90)">{path_text(sd, LIME)}</g>',
        f'  <g transform="translate({games_x:.1f} {games_y:.1f})">{path_text(gd, PAPER)}</g>',
        f'  <g transform="translate({games_x + 6:.1f} {games_y + 18:.1f}) rotate(-8)">',
        f'    <rect width="{gx1 * 0.78:.1f}" height="8" fill="{PINK}"/>',
        "  </g>",
    ]
    write(
        "lockups/games-spine.svg",
        svg(f"0 0 {sw:.1f} {sh}", "\n".join(spine), label="Unnatural Games — spine"),
        group="Games logos",
        title="Games — spine",
        note="UNNATURAL reads up the left edge. GAMES is horizontal on an −8° rule.",
    )

    # ------------------------------------------------------------------
    # 3. Stripe — diagonal bands clipped to the letterforms
    # ------------------------------------------------------------------
    gd, gx0, gy0, gx1, gy1, _ = ink_of(DISPLAY, "GAMES", 124, tracking=-2.0, scale_x=0.98)
    ud, ux0, uy0, ux1, uy1, _ = ink_of(DISPLAY, "UNNATURAL", 26, tracking=5.5)
    games_x, games_y = 46, 196
    word_cx = games_x + (gx0 + gx1) / 2
    word_cy = games_y + (gy0 + gy1) / 2
    eye_x, eye_y = 58, 78
    stripe_w, stripe_h = games_x + gx1 + 64, 250
    stripe = [
        f'  <rect width="{stripe_w:.1f}" height="{stripe_h}" fill="{INK}"/>',
        "  <defs>",
        f'    <clipPath id="games-letters"><path transform="translate({games_x} {games_y})" d="{gd}"/></clipPath>',
        "  </defs>",
        f'  <g transform="translate({eye_x} {eye_y}) rotate(-13)">{path_text(ud, LIME)}</g>',
        f'  <g transform="translate({games_x} {games_y})">{path_text(gd, PAPER)}</g>',
        '  <g clip-path="url(#games-letters)">',
        f'    <g transform="translate({word_cx:.2f} {word_cy:.2f}) rotate(-27) translate({-word_cx:.2f} {-word_cy:.2f})">',
        f'      <rect x="-80" y="{word_cy - 20:.1f}" width="{stripe_w + 160:.1f}" height="26" fill="{PINK}"/>',
        f'      <rect x="-80" y="{word_cy + 16:.1f}" width="{stripe_w + 160:.1f}" height="9" fill="{LIME}"/>',
        "    </g>",
        "  </g>",
    ]
    write(
        "lockups/games-stripe.svg",
        svg(f"0 0 {stripe_w:.1f} {stripe_h}", "\n".join(stripe), label="Unnatural Games — stripe"),
        group="Games logos",
        title="Games — stripe",
        note="UNNATURAL at −13°. Pink and lime bands at −27°, clipped inside GAMES.",
    )

    # ------------------------------------------------------------------
    # 4. Seal — arched type around a rotated board
    # ------------------------------------------------------------------
    seal = 420
    cx = cy = seal / 2
    cells = 34
    board = cells * 2
    seal_parts = [
        f'  <rect width="{seal}" height="{seal}" fill="{INK}"/>',
        f'  <circle cx="{cx}" cy="{cy}" r="196" fill="none" stroke="{LIME}" stroke-width="3"/>',
        f'  <circle cx="{cx}" cy="{cy}" r="184" fill="none" stroke="{PINK}" stroke-width="1.25" opacity="0.85"/>',
        arc_line(DISPLAY, "UNNATURAL", cx, cy, 150, 28, PAPER, tracking=2.4),
        arc_line(DISPLAY, "GAMES", cx, cy, 146, 40, LIME, tracking=6.5, smile=True),
        f'  <g transform="translate({cx} {cy}) rotate(45)">',
    ]
    for row in range(2):
        for col in range(2):
            fill = PAPER if (row + col) % 2 == 0 else WINE
            seal_parts.append(
                f'    <rect x="{col * cells - board / 2}" y="{row * cells - board / 2}" width="{cells}" height="{cells}" fill="{fill}"/>'
            )
    seal_parts.append("  </g>")
    write(
        "lockups/games-seal.svg",
        svg(f"0 0 {seal} {seal}", "\n".join(seal_parts), label="Unnatural Games — seal"),
        group="Games logos",
        title="Games — seal",
        note="Type on two arcs. A 2×2 board turned 45° in the middle.",
    )

    # ------------------------------------------------------------------
    # 5. Slice — cap of GAMES shifted, whole mark tipped
    # ------------------------------------------------------------------
    gd, gx0, gy0, gx1, gy1, _ = ink_of(DISPLAY, "GAMES", 116, tracking=-1.8, scale_x=1.02)
    ud, ux0, uy0, ux1, uy1, _ = ink_of(JB_BOLD, "UNNATURAL", 20, tracking=5.2)
    cut = gy0 * 0.58  # y-down; gy0 is the cap top (negative)
    shift = 18
    eye_x, eye_y = 8, gy0 - 28
    local = [
        f'  <g transform="translate({eye_x} {eye_y:.2f})">{path_text(ud, OLIVE)}</g>',
        "  <defs>",
        f'    <clipPath id="slice-top"><rect x="-30" y="-400" width="2000" height="{400 + cut:.2f}"/></clipPath>',
        f'    <clipPath id="slice-bot"><rect x="-30" y="{cut:.2f}" width="2000" height="800"/></clipPath>',
        "  </defs>",
        f'  <g clip-path="url(#slice-top)" transform="translate({shift} -7)">{path_text(gd, LIME)}</g>',
        f'  <g clip-path="url(#slice-bot)">{path_text(gd, PAPER)}</g>',
        f'  <rect x="-16" y="{cut - 1.6:.2f}" width="{gx1 + shift + 36:.1f}" height="3.2" fill="{PINK}"/>',
    ]
    # Tip the whole group −9° and fit a viewBox to every rotated corner.
    tip = -9
    boxes = [
        (eye_x + ux0, eye_y + uy0, eye_x + ux1, eye_y + uy1),
        (shift + gx0, -7 + gy0, shift + gx1, -7 + min(cut, gy1)),
        (gx0, cut, gx1, max(gy1, 2)),
        (-16, cut - 1.6, gx1 + shift + 20, cut + 1.6),
    ]
    tr = math.radians(tip)
    cos_t, sin_t = math.cos(tr), math.sin(tr)
    rot = []
    for x0, y0, x1, y1 in boxes:
        for x in (x0, x1):
            for y in (y0, y1):
                rot.append((x * cos_t - y * sin_t, x * sin_t + y * cos_t))
    pad = 36
    rx0, ry0 = min(p[0] for p in rot) - pad, min(p[1] for p in rot) - pad
    rx1, ry1 = max(p[0] for p in rot) + pad, max(p[1] for p in rot) + pad
    slice_w, slice_h = rx1 - rx0, ry1 - ry0
    sliced = [
        f'  <rect width="{slice_w:.1f}" height="{slice_h:.1f}" fill="{INK}"/>',
        f'  <g transform="translate({-rx0:.2f} {-ry0:.2f}) rotate({tip})">',
        *["  " + line for line in local],
        "  </g>",
    ]
    write(
        "lockups/games-slice.svg",
        svg(f"0 0 {slice_w:.1f} {slice_h:.1f}", "\n".join(sliced), label="Unnatural Games — slice"),
        group="Games logos",
        title="Games — slice",
        note="The cap of GAMES steps up and turns lime. The whole mark sits at −9°.",
    )

    def rotated_corners(tx: float, ty: float, deg: float, x0: float, y0: float, x1: float, y1: float):
        rad = math.radians(deg)
        c, s = math.cos(rad), math.sin(rad)
        pts = []
        for lx, ly in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
            pts.append((tx + lx * c - ly * s, ty + lx * s + ly * c))
        return pts

    def fit_ink(corners, pad: float = 36) -> tuple[float, float, float, float]:
        minx = min(p[0] for p in corners) - pad
        miny = min(p[1] for p in corners) - pad
        maxx = max(p[0] for p in corners) + pad
        maxy = max(p[1] for p in corners) + pad
        return minx, miny, maxx - minx, maxy - miny

    # ------------------------------------------------------------------
    # 6. Steps — each letter climbs onto its own colour
    # ------------------------------------------------------------------
    step_colors = (LIME, PINK, CYAN, OLIVE, PAPER)
    step_glyphs = []
    for ch in "GAMES":
        step_glyphs.append(ink_of(DISPLAY, ch, 86, tracking=0))
    step_eye = ink_of(JB_BOLD, "UNNATURAL", 18, tracking=4.2)
    cell_w = max(g[3] - g[1] for g in step_glyphs) + 36
    cell_h = max(-g[2] for g in step_glyphs) + 44
    rise = 22
    overlap = 10
    stair = []
    corners = []
    for i, (d, x0, y0, x1, y1, _adv) in enumerate(step_glyphs):
        x = i * (cell_w - overlap)
        y = (4 - i) * rise
        fill = PAPER if step_colors[i] == PINK else INK
        text_x = x + (cell_w - (x1 - x0)) / 2 - x0
        text_y = y + cell_h - 16
        stair.append(
            f'  <rect x="{x:.2f}" y="{y:.2f}" width="{cell_w:.2f}" height="{cell_h:.2f}" fill="{step_colors[i]}"/>'
        )
        stair.append(f'  <g transform="translate({text_x:.2f} {text_y:.2f})">{path_text(d, fill)}</g>')
        corners.append((x, y))
        corners.append((x + cell_w, y + cell_h))
    eye_d, ex0, ey0, ex1, ey1, _ = step_eye
    eye_x, eye_y = 0, -34
    stair.append(f'  <g transform="translate({eye_x - ex0:.2f} {eye_y:.2f})">{path_text(eye_d, PAPER)}</g>')
    corners.extend(((eye_x, eye_y + ey0), (eye_x + (ex1 - ex0), eye_y + ey1)))
    sx0, sy0, sw, sh = fit_ink(corners, 32)
    steps = [
        f'  <rect width="{sw:.1f}" height="{sh:.1f}" fill="{INK}"/>',
        f'  <g transform="translate({-sx0:.2f} {-sy0:.2f})">',
        *stair,
        "  </g>",
    ]
    write(
        "lockups/games-steps.svg",
        svg(f"0 0 {sw:.1f} {sh:.1f}", "\n".join(steps), label="Unnatural Games — steps"),
        group="Games logos",
        title="Games — steps",
        note="GAMES climbs one letter at a time. Lime, pink, cyan, olive, paper.",
    )

    # ------------------------------------------------------------------
    # 7. Cross — the two words on opposing diagonals around an X
    # ------------------------------------------------------------------
    cross_u = ink_of(DISPLAY, "UNNATURAL", 42, tracking=2.2)
    cross_g = ink_of(DISPLAY, "GAMES", 92, tracking=-1.2)
    ud, ux0, uy0, ux1, uy1, _ = cross_u
    gd, gx0, gy0, gx1, gy1, _ = cross_g
    # Upper word climbs toward the middle. Lower word leaves it on the other diagonal.
    u_tx, u_ty, u_deg = 20, 150, -16
    g_tx, g_ty, g_deg = 360, 268, 14
    cross_pts = []
    cross_pts += rotated_corners(u_tx, u_ty, u_deg, ux0, uy0, ux1, uy1)
    cross_pts += rotated_corners(g_tx, g_ty, g_deg, gx0, gy0, gx1, gy1)
    cross_pts += rotated_corners(330, 196, 42, -64, -6, 64, 6)
    cross_pts += rotated_corners(330, 196, -48, -64, -6, 64, 6)
    cx0, cy0, cw, ch = fit_ink(cross_pts, 40)
    cross = [
        f'  <rect width="{cw:.1f}" height="{ch:.1f}" fill="{INK}"/>',
        f'  <g transform="translate({-cx0:.2f} {-cy0:.2f})">',
        f'    <g transform="translate(330 196) rotate(42)"><rect x="-64" y="-6" width="128" height="12" fill="{PINK}"/></g>',
        f'    <g transform="translate(330 196) rotate(-48)"><rect x="-64" y="-6" width="128" height="12" fill="{LIME}"/></g>',
        f'    <g transform="translate({u_tx} {u_ty}) rotate({u_deg})">{path_text(ud, LIME)}</g>',
        f'    <g transform="translate({g_tx} {g_ty}) rotate({g_deg})">{path_text(gd, PAPER)}</g>',
        "  </g>",
    ]
    write(
        "lockups/games-cross.svg",
        svg(f"0 0 {cw:.1f} {ch:.1f}", "\n".join(cross), label="Unnatural Games — cross"),
        group="Games logos",
        title="Games — cross",
        note="UNNATURAL at −16°, GAMES at +14°, with a pink and lime X between them.",
    )

    # ------------------------------------------------------------------
    # 8. Mark — UG monogram on a tipped plate
    # ------------------------------------------------------------------
    mu = ink_of(DISPLAY, "U", 168)
    mg = ink_of(DISPLAY, "G", 168)
    cap = ink_of(JB_BOLD, "UNNATURAL GAMES", 15, tracking=2.6)
    ud, ux0, uy0, ux1, uy1, _ = mu
    gd, gx0, gy0, gx1, gy1, _ = mg
    cd, cx0, cy0, cx1, cy1, _ = cap
    plate = 300
    # Overlap G into the right side of U.
    u_w = ux1 - ux0
    pair_w = u_w * 0.62 + (gx1 - gx0)
    pair_h = max(-uy0, -gy0)
    mark_w, mark_h = 440, 470
    mcx, mcy = 220, 210
    mark = [
        f'  <rect width="{mark_w}" height="{mark_h}" fill="{INK}"/>',
        f'  <g transform="translate({mcx} {mcy}) rotate(-10)">',
        f'    <rect x="{-plate / 2}" y="{-plate / 2}" width="{plate}" height="{plate}" fill="{WINE}"/>',
        f'    <rect x="{-plate / 2 + 14}" y="{-plate / 2 + 14}" width="{plate - 28}" height="{plate - 28}" fill="none" stroke="{LIME}" stroke-width="3"/>',
        "  </g>",
        f'  <g transform="translate({mcx - pair_w / 2:.2f} {mcy + pair_h * 0.42:.2f})">',
        f'    <g transform="translate({-ux0:.2f} 0)">{path_text(ud, LIME)}</g>',
        f'    <g transform="translate({u_w * 0.62 - gx0:.2f} 0)">{path_text(gd, PAPER)}</g>',
        "  </g>",
        f'  <g transform="translate({mcx - (cx1 - cx0) / 2:.2f} {mark_h - 42:.2f})">{path_text(cd, PAPER)}</g>',
    ]
    write(
        "lockups/games-mark.svg",
        svg(f"0 0 {mark_w} {mark_h}", "\n".join(mark), label="Unnatural Games — monogram"),
        group="Games logos",
        title="Games — monogram",
        note="UG on a wine plate tipped −10°. The name sits under the badge.",
    )

    # ------------------------------------------------------------------
    # 9. Fan — three copies of GAMES opening like a hand of cards
    # ------------------------------------------------------------------
    fan_word = ink_of(DISPLAY, "GAMES", 104, tracking=-1.4)
    fan_eye = ink_of(JB_BOLD, "UNNATURAL", 20, tracking=4.8)
    gd, gx0, gy0, gx1, gy1, _ = fan_word
    ed, ex0, ey0, ex1, ey1, _ = fan_eye
    fan_origin = (36, 210)
    fan_angles = ((-18, OLIVE), (-9, PINK), (0, PAPER))
    fan_pts = []
    fan_body = []
    for deg, color in fan_angles:
        fan_pts += rotated_corners(fan_origin[0], fan_origin[1], deg, gx0, gy0, gx1, gy1)
        fan_body.append(
            f'  <g transform="translate({fan_origin[0]} {fan_origin[1]}) rotate({deg})">{path_text(gd, color)}</g>'
        )
    eye_at = (fan_origin[0], fan_origin[1] + gy0 - 28)
    fan_pts += [(eye_at[0] + ex0, eye_at[1] + ey0), (eye_at[0] + ex1, eye_at[1] + ey1)]
    fx0, fy0, fw, fh = fit_ink(fan_pts, 40)
    fan = [
        f'  <rect width="{fw:.1f}" height="{fh:.1f}" fill="{INK}"/>',
        f'  <g transform="translate({-fx0:.2f} {-fy0:.2f})">',
        *fan_body,
        f'  <g transform="translate({eye_at[0] - ex0:.2f} {eye_at[1]:.2f})">{path_text(ed, LIME)}</g>',
        "  </g>",
    ]
    write(
        "lockups/games-fan.svg",
        svg(f"0 0 {fw:.1f} {fh:.1f}", "\n".join(fan), label="Unnatural Games — fan"),
        group="Games logos",
        title="Games — fan",
        note="Three copies of GAMES open from the left: olive −18°, pink −9°, paper flat.",
    )

    # ------------------------------------------------------------------
    # 10. Ticket — pink stub, perforation, GAMES on the ink half
    # ------------------------------------------------------------------
    stub_word = ink_of(DISPLAY, "UG", 54, tracking=-1)
    ticket_word = ink_of(DISPLAY, "GAMES", 92, tracking=-1.0)
    ticket_eye = ink_of(JB_BOLD, "UNNATURAL", 16, tracking=3.6)
    sd, sx0, sy0, sx1, sy1, _ = stub_word
    gd, gx0, gy0, gx1, gy1, _ = ticket_word
    ed, ex0, ey0, ex1, ey1, _ = ticket_eye
    th = 230
    stub = 188
    games_x = stub + 44 - gx0
    games_y = th / 2 - (gy0 + gy1) / 2
    eye_x = games_x
    eye_y = games_y + gy0 - 18
    tw = games_x + gx1 + 44
    # Center UG in the stub. rotate(0), ink on pink.
    ug_x = (stub - (sx1 - sx0)) / 2 - sx0
    ug_y = th / 2 - (sy0 + sy1) / 2
    dots = []
    for y in range(18, th - 8, 22):
        dots.append(f'  <circle cx="{stub}" cy="{y}" r="5.5" fill="{INK}"/>')
    ticket = [
        f'  <rect width="{tw}" height="{th}" fill="{INK}"/>',
        f'  <rect width="{stub}" height="{th}" fill="{PINK}"/>',
        f'  <g transform="translate({ug_x:.2f} {ug_y:.2f})">{path_text(sd, INK)}</g>',
        *dots,
        f'  <g transform="translate({eye_x:.2f} {eye_y:.2f})">{path_text(ed, LIME)}</g>',
        f'  <g transform="translate({games_x:.2f} {games_y:.2f})">{path_text(gd, PAPER)}</g>',
        f'  <rect x="{stub + 36}" y="{th - 28}" width="92" height="8" fill="{CYAN}"/>',
    ]
    write(
        "lockups/games-ticket.svg",
        svg(f"0 0 {tw} {th}", "\n".join(ticket), label="Unnatural Games — ticket"),
        group="Games logos",
        title="Games — ticket",
        note="Pink stub with UG, a punched perforation, then GAMES on ink.",
    )

    # Jellyfish constructions. These use the official mascot and still are not
    # the club lockup (no second line of INTELLIGENCE, no cyan/pink type ghost).
    def jelly_wh(height: float) -> tuple[float, float]:
        return height * (JELLY_VB_W / JELLY_VB_H), height

    def jelly_corners(cx: float, cy: float, height: float, deg: float = 0.0, y0f: float = 0.0, y1f: float = 1.0):
        w, h = jelly_wh(height)
        top = -h / 2 + h * y0f
        bot = -h / 2 + h * y1f
        return rotated_corners(cx, cy, deg, -w / 2, top, w / 2, bot)

    def jelly_svg(cx: float, cy: float, height: float, fill: str, deg: float = 0.0) -> str:
        w, _h = jelly_wh(height)
        scale = height / JELLY_VB_H
        return (
            f'  <g transform="translate({cx:.2f} {cy:.2f}) rotate({deg:g}) '
            f'translate({-w / 2:.2f} {-height / 2:.2f}) scale({scale:.5f})">\n'
            f"{jelly_path(fill)}\n"
            f"  </g>"
        )

    def ink_shift(block, x_ink: float, baseline: float) -> tuple[float, float]:
        _d, x0, _y0, _x1, _y1, _adv = block
        return x_ink - x0, baseline

    # ------------------------------------------------------------------
    # 11. Crest — jellyfish over a divider, then the name
    # ------------------------------------------------------------------
    crest_eye = ink_of(JB_BOLD, "UNNATURAL", 20, tracking=5.6)
    crest_word = ink_of(DISPLAY, "GAMES", 108, tracking=-1.2)
    ed, ex0, ey0, ex1, ey1, _ = crest_eye
    gd, gx0, gy0, gx1, gy1, _ = crest_word
    jh = 248
    jw, _ = jelly_wh(jh)
    content_w = max(jw, ex1 - ex0, gx1 - gx0)
    cx = content_w / 2
    jelly_cy = jh / 2
    dash_y = jh + 18
    dash_h = 7
    dash_w = 52
    dash_gap = 12
    eye_top = dash_y + dash_h + 22
    eye_base = eye_top - ey0
    eye_x, _ = ink_shift(crest_eye, cx - (ex1 - ex0) / 2, eye_base)
    games_top = eye_base + ey1 + 22
    games_base = games_top - gy0
    games_x, _ = ink_shift(crest_word, cx - (gx1 - gx0) / 2, games_base)
    crest_pts = jelly_corners(cx, jelly_cy, jh)
    crest_pts += [
        (cx - dash_gap / 2 - dash_w, dash_y),
        (cx + dash_gap / 2 + dash_w, dash_y + dash_h),
        (eye_x + ex0, eye_base + ey0),
        (eye_x + ex1, eye_base + ey1),
        (games_x + gx0, games_base + gy0),
        (games_x + gx1, games_base + gy1),
    ]
    crx, cry, crw, crh = fit_ink(crest_pts, 40)
    crest = [
        f'  <rect width="{crw:.1f}" height="{crh:.1f}" fill="{INK}"/>',
        "  <defs>",
        f"    {GRADIENT_DEFS}",
        "  </defs>",
        f'  <g transform="translate({-crx:.2f} {-cry:.2f})">',
        jelly_svg(cx, jelly_cy, jh, "url(#uni-jelly)"),
        f'  <rect x="{cx - dash_gap / 2 - dash_w:.2f}" y="{dash_y:.2f}" width="{dash_w}" height="{dash_h}" fill="{LIME}"/>',
        f'  <rect x="{cx + dash_gap / 2:.2f}" y="{dash_y:.2f}" width="{dash_w}" height="{dash_h}" fill="{PINK}"/>',
        f'  <g transform="translate({eye_x:.2f} {eye_base:.2f})">{path_text(ed, LIME)}</g>',
        f'  <g transform="translate({games_x:.2f} {games_base:.2f})">{path_text(gd, PAPER)}</g>',
        "  </g>",
    ]
    write(
        "lockups/games-crest.svg",
        svg(f"0 0 {crw:.1f} {crh:.1f}", "\n".join(crest), label="Unnatural Games — crest"),
        group="Games logos",
        title="Games — crest",
        note="Gradient jellyfish over a lime and pink divider, then UNNATURAL and GAMES.",
    )

    # ------------------------------------------------------------------
    # 12. Swim — jellyfish tipped, GAMES clear of the bell
    # ------------------------------------------------------------------
    swim_word = ink_of(DISPLAY, "GAMES", 124, tracking=-1.4)
    swim_eye = ink_of(JB_BOLD, "UNNATURAL", 24, tracking=3.0)
    gd, gx0, gy0, gx1, gy1, _ = swim_word
    ed, ex0, ey0, ex1, ey1, _ = swim_eye
    sjh = 292
    sdeg = -16
    # Center the word on the jellyfish and sit it just clear of that band,
    # so the bell and the tentacles both belong to the mark.
    # Sit the word a little below center so it fills the open ink beside the tentacles.
    games_base = -(gy0 + gy1) / 2 + 34
    word_top = games_base + gy0
    word_bot = games_base + gy1

    def yfrac(y: float) -> float:
        return min(1.0, max(0.0, (y + sjh / 2) / sjh))

    band = jelly_corners(0, 0, sjh, sdeg, yfrac(word_top), yfrac(word_bot))
    games_left = max(p[0] for p in band) + 24
    games_x, _ = ink_shift(swim_word, games_left, games_base)
    eye_base = games_base + gy0 - 18 - ey1
    eye_x, _ = ink_shift(swim_eye, games_left, eye_base)
    bar_x = games_left
    bar_y = games_base + gy1 + 12
    bar_w = min(156, gx1 - gx0)
    swim_pts = jelly_corners(0, 0, sjh, sdeg)
    swim_pts += [
        (games_x + gx0, games_base + gy0),
        (games_x + gx1, games_base + gy1),
        (eye_x + ex0, eye_base + ey0),
        (eye_x + ex1, eye_base + ey1),
        (bar_x, bar_y),
        (bar_x + bar_w, bar_y + 8),
    ]
    swx, swy, sww, swh = fit_ink(swim_pts, 36)
    swim = [
        f'  <rect width="{sww:.1f}" height="{swh:.1f}" fill="{INK}"/>',
        "  <defs>",
        f"    {GRADIENT_DEFS}",
        "  </defs>",
        f'  <g transform="translate({-swx:.2f} {-swy:.2f})">',
        jelly_svg(0, 0, sjh, "url(#uni-jelly)", sdeg),
        f'  <g transform="translate({eye_x:.2f} {eye_base:.2f})">{path_text(ed, LIME)}</g>',
        f'  <g transform="translate({games_x:.2f} {games_base:.2f})">{path_text(gd, PAPER)}</g>',
        f'  <rect x="{bar_x:.2f}" y="{bar_y:.2f}" width="{bar_w:.1f}" height="8" fill="{PINK}"/>',
        "  </g>",
    ]
    write(
        "lockups/games-swim.svg",
        svg(f"0 0 {sww:.1f} {swh:.1f}", "\n".join(swim), label="Unnatural Games — swim"),
        group="Games logos",
        title="Games — swim",
        note="Jellyfish tipped −16°, swimming beside GAMES. A pink bar grounds the word.",
    )

    # ------------------------------------------------------------------
    # 13. Overlap — jellyfish perched on the S
    # ------------------------------------------------------------------
    ov_word = ink_of(DISPLAY, "GAMES", 118, tracking=-1.4)
    ov_eye = ink_of(JB_BOLD, "UNNATURAL", 20, tracking=4.2)
    game_only = ink_of(DISPLAY, "GAME", 118, tracking=-1.4)
    s_only = ink_of(DISPLAY, "S", 118)
    gd, gx0, gy0, gx1, gy1, _ = ov_word
    ed, ex0, ey0, ex1, ey1, _ = ov_eye
    _, _, _, _, _, game_adv = game_only
    _, sx0, _, sx1, _, _ = s_only
    games_base = 0.0
    games_x = -gx0
    s_right = games_x + game_adv + sx1
    jh = 176
    jw, _ = jelly_wh(jh)
    into = 36
    jelly_bottom = games_base + gy0 + into
    jelly_cy = jelly_bottom - jh / 2
    jelly_cx = s_right + jw * 0.18
    bell_cy = jelly_cy - jh * 0.14
    games_left = games_x + gx0
    eye_base = bell_cy - (ey0 + ey1) / 2
    eye_x, _ = ink_shift(ov_eye, games_left, eye_base)
    bar_w = 132
    bar_x = games_left
    bar_y = games_base + gy1 + 10
    ov_pts = jelly_corners(jelly_cx, jelly_cy, jh)
    ov_pts += [
        (games_x + gx0, games_base + gy0),
        (games_x + gx1, games_base + gy1),
        (eye_x + ex0, eye_base + ey0),
        (eye_x + ex1, eye_base + ey1),
        (bar_x, bar_y),
        (bar_x + bar_w, bar_y + 8),
    ]
    ox, oy, ow, oh = fit_ink(ov_pts, 36)
    overlap = [
        f'  <rect width="{ow:.1f}" height="{oh:.1f}" fill="{INK}"/>',
        "  <defs>",
        f"    {GRADIENT_DEFS}",
        "  </defs>",
        f'  <g transform="translate({-ox:.2f} {-oy:.2f})">',
        f'  <g transform="translate({eye_x:.2f} {eye_base:.2f})">{path_text(ed, LIME)}</g>',
        f'  <g transform="translate({games_x:.2f} {games_base:.2f})">{path_text(gd, PAPER)}</g>',
        f'  <rect x="{bar_x:.2f}" y="{bar_y:.2f}" width="{bar_w}" height="8" fill="{CYAN}"/>',
        jelly_svg(jelly_cx, jelly_cy, jh, "url(#uni-jelly)"),
        "  </g>",
    ]
    write(
        "lockups/games-overlap.svg",
        svg(f"0 0 {ow:.1f} {oh:.1f}", "\n".join(overlap), label="Unnatural Games — overlap"),
        group="Games logos",
        title="Games — overlap",
        note="Gradient jellyfish perched on the S. Tentacles cross the cap; the word stays readable.",
    )

    # ------------------------------------------------------------------
    # 14. Quad — the poster row of four jellyfish, then GAMES
    # ------------------------------------------------------------------
    quad_eye = ink_of(JB_BOLD, "UNNATURAL", 18, tracking=6.4)
    quad_word = ink_of(DISPLAY, "GAMES", 104, tracking=-1.0)
    ed, ex0, ey0, ex1, ey1, _ = quad_eye
    gd, gx0, gy0, gx1, gy1, _ = quad_word
    qh = 132
    qw, _ = jelly_wh(qh)
    qgap = 14
    colours = (LIME, PINK, CYAN, PAPER)
    row_w = 4 * qw + 3 * qgap
    content_w = max(row_w, ex1 - ex0, gx1 - gx0)
    cx = content_w / 2
    eye_base = -ey0
    eye_x, _ = ink_shift(quad_eye, cx - (ex1 - ex0) / 2, eye_base)
    jelly_top = eye_base + ey1 + 18
    jelly_cy = jelly_top + qh / 2
    row_x = cx - row_w / 2
    games_top = jelly_top + qh + 20
    games_base = games_top - gy0
    games_x, _ = ink_shift(quad_word, cx - (gx1 - gx0) / 2, games_base)
    quad_pts = [
        (eye_x + ex0, eye_base + ey0),
        (eye_x + ex1, eye_base + ey1),
        (games_x + gx0, games_base + gy0),
        (games_x + gx1, games_base + gy1),
        (row_x, jelly_top),
        (row_x + row_w, jelly_top + qh),
    ]
    qx, qy, qbw, qbh = fit_ink(quad_pts, 36)
    quads = [
        f'  <rect width="{qbw:.1f}" height="{qbh:.1f}" fill="{INK}"/>',
        f'  <g transform="translate({-qx:.2f} {-qy:.2f})">',
        f'  <g transform="translate({eye_x:.2f} {eye_base:.2f})">{path_text(ed, LIME)}</g>',
    ]
    for i, colour in enumerate(colours):
        jcx = row_x + qw / 2 + i * (qw + qgap)
        quads.append(jelly_svg(jcx, jelly_cy, qh, colour))
    quads.append(f'  <g transform="translate({games_x:.2f} {games_base:.2f})">{path_text(gd, PAPER)}</g>')
    quads.append("  </g>")
    write(
        "lockups/games-quad.svg",
        svg(f"0 0 {qbw:.1f} {qbh:.1f}", "\n".join(quads), label="Unnatural Games — quad"),
        group="Games logos",
        title="Games — quad",
        note="Four jellyfish in lime, pink, cyan, and paper, with GAMES centered underneath.",
    )

    # ------------------------------------------------------------------
    # 15. Badge — rounded wine plate, jellyfish, name inside
    # ------------------------------------------------------------------
    badge_eye = ink_of(JB_BOLD, "UNNATURAL", 18, tracking=3.4)
    badge_word = ink_of(DISPLAY, "GAMES", 80, tracking=-0.8)
    ed, ex0, ey0, ex1, ey1, _ = badge_eye
    gd, gx0, gy0, gx1, gy1, _ = badge_word
    jh = 210
    jw, _ = jelly_wh(jh)
    side = 48
    bw = max(jw, gx1 - gx0, ex1 - ex0) + side * 2
    top = 30
    jelly_cy = top + jh / 2
    eye_top = top + jh + 8
    eye_base = eye_top - ey0
    games_top = eye_base + ey1 + 12
    games_base = games_top - gy0
    bar_w = 88
    bar_y = games_base + gy1 + 16
    bh = bar_y + 8 + 32
    cx = bw / 2
    eye_x, _ = ink_shift(badge_eye, cx - (ex1 - ex0) / 2, eye_base)
    games_x, _ = ink_shift(badge_word, cx - (gx1 - gx0) / 2, games_base)
    rx = 34
    inset = 14
    badge = [
        f'  <rect width="{bw:.1f}" height="{bh:.1f}" fill="{INK}"/>',
        "  <defs>",
        f"    {GRADIENT_DEFS}",
        "  </defs>",
        f'  <rect width="{bw:.1f}" height="{bh:.1f}" rx="{rx}" fill="{WINE}"/>',
        (
            f'  <rect x="{inset}" y="{inset}" width="{bw - inset * 2:.1f}" height="{bh - inset * 2:.1f}" '
            f'rx="{rx - 10}" fill="none" stroke="{LIME}" stroke-width="3"/>'
        ),
        jelly_svg(cx, jelly_cy, jh, "url(#uni-jelly)"),
        f'  <g transform="translate({eye_x:.2f} {eye_base:.2f})">{path_text(ed, LIME)}</g>',
        f'  <g transform="translate({games_x:.2f} {games_base:.2f})">{path_text(gd, PAPER)}</g>',
        f'  <rect x="{(bw - bar_w) / 2:.2f}" y="{bar_y:.2f}" width="{bar_w}" height="8" fill="{PINK}"/>',
    ]
    write(
        "lockups/games-badge.svg",
        svg(f"0 0 {bw:.1f} {bh:.1f}", "\n".join(badge), label="Unnatural Games — badge"),
        group="Games logos",
        title="Games — badge",
        note="Rounded wine plate with a lime keyline. Gradient jellyfish, then the name.",
    )


def main() -> None:
    build_marks()
    build_lockups()
    build_games_logos()
    build_icons()
    build_stickers()
    build_badges()
    build_patterns()
    build_fact_bars()
    build_avatars()
    build_palette()
    build_preview()
    build_readme()
    n_png = rasterize_pngs()
    print(f"Wrote {len(MANIFEST)} files and {n_png} PNG samples under {ROOT}")


if __name__ == "__main__":
    main()
