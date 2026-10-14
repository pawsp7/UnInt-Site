#!/usr/bin/env python3
"""Rasterize Vector Kit SVGs used by the 2026–27 charter."""

from __future__ import annotations

from pathlib import Path

import cairosvg

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
KIT = REPO / "Branding" / "Vector Kit"
ASSETS = ROOT / "assets" / "revamp"

HEADER_SVG = """<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 840 80" fill="none">
  <defs>
    <linearGradient id="fl" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#BAF837"/>
      <stop offset="48%" stop-color="#95B747"/>
      <stop offset="100%" stop-color="#FA4A9E"/>
    </linearGradient>
  </defs>
  <!-- Left flourish; right side is a true mirror around x=420 so the spark sits in an even gap. -->
  <path d="M16 34 C 72 8, 118 60, 170 30 C 222 4, 268 58, 318 36"
        fill="none" stroke="url(#fl)" stroke-width="12" stroke-linecap="round"/>
  <path d="M38 50 C 88 22, 140 66, 192 46 C 244 24, 290 68, 334 50"
        fill="none" stroke="url(#fl)" stroke-width="5.5" stroke-linecap="round" opacity="0.75"/>
  <path d="M522 36 C 572 58, 618 4, 670 30 C 722 60, 768 8, 824 34"
        fill="none" stroke="url(#fl)" stroke-width="12" stroke-linecap="round"/>
  <path d="M506 50 C 550 68, 596 24, 648 46 C 700 66, 752 22, 802 50"
        fill="none" stroke="url(#fl)" stroke-width="5.5" stroke-linecap="round" opacity="0.75"/>
</svg>
"""

RASTERS: list[tuple[str, Path | None, str, int]] = [
    # name, source (None = generated), dest filename, height_px
    ("header", None, "header.png", 220),
    ("jellyfish", KIT / "marks/jellyfish-gradient.svg", "jellyfish.png", 900),
    ("jellyfish_mini", KIT / "marks/jellyfish-mini-gradient.svg", "jellyfish-mini.png", 280),
    ("lockup", KIT / "lockups/stacked-light.svg", "lockup-stacked.png", 720),
    ("wordmark", KIT / "lockups/wordmark-ink.svg", "wordmark.png", 220),
    ("swatches", KIT / "palette/swatches.svg", "swatches.png", 280),
    ("sprite", KIT / "icons/sprite.svg", "icon-sprite.png", 420),
    ("quote", KIT / "stickers/i-hate-it-but-its-useful.svg", "quote-useful.png", 220),
    ("tagline", KIT / "stickers/generated-by-ai.svg", "tagline.png", 200),
    ("saitsa", REPO / "Branding/SaitsaStudentClubsPrimaryLogo.svg", "saitsa-clubs.png", 140),
    ("flourish", KIT / "patterns/tentacle-flourish.svg", "flourish.png", 200),
]

ICONS = [
    "spark",
    "token",
    "prompt",
    "halt",
    "restart",
    "workflow",
    "mask",
    "tentacle",
    "glitch",
    "bubble",
    "meter",
    "commit",
    "neural",
    "node",
    "ticket",
]

BADGES = [
    "member",
    "exec",
    "workshop",
    "live-lab",
    "halt-restart",
    "clubs-expo",
]


def raster_svg(src: Path, dest: Path, height_px: int) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    cairosvg.svg2png(
        url=str(src),
        write_to=str(dest),
        output_height=height_px,
        background_color="transparent",
    )
    return dest


def export() -> Path:
    ASSETS.mkdir(parents=True, exist_ok=True)
    header_svg = ASSETS / "header-squiggle.svg"
    header_svg.write_text(HEADER_SVG)

    for name, src, dest_name, height in RASTERS:
        dest = ASSETS / dest_name
        path = header_svg if src is None else src
        raster_svg(path, dest, height)

    for slug in ICONS:
        boxed = KIT / "icons" / f"{slug}.svg"
        plain = KIT / "icons" / f"{slug}-plain.svg"
        if boxed.exists():
            raster_svg(boxed, ASSETS / f"icon-{slug}.png", 160)
        if plain.exists():
            raster_svg(plain, ASSETS / f"icon-{slug}-plain.png", 140)

    for slug in BADGES:
        src = KIT / "badges" / f"{slug}.svg"
        raster_svg(src, ASSETS / f"badge-{slug}.png", 96)

    print(f"Wrote {ASSETS}")
    return ASSETS


if __name__ == "__main__":
    export()
