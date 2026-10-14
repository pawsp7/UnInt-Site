#!/usr/bin/env python3
"""Write 300 DPI PNGs for every promo piece, and a PNG for every SVG asset.

Gallery previews next to the HTML stay at screen resolution. This script fills
``png/`` (print files) and writes a ``.png`` beside each SVG in ``assets/``.
"""
from __future__ import annotations

import io
import shutil
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image

ROOT = Path(__file__).resolve().parent
PNG = ROOT / "png"
ASSETS = ROOT / "assets"
DPI = 300

# Letter sheet geometry from cards.html (inches).
CUT = 0.18
CARD_H = (11 - CUT) / 2  # 5.41
SQ = 3.9
GAP = 0.22
GRID = SQ * 2 + GAP  # 8.02
SQ_X = (8.5 - GRID) / 2  # 0.24
SQ_Y = (11 - GRID) / 2  # 1.49


def along(length: int, inches: float, total: float) -> int:
    return round(inches / total * length)


def save(im: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "PNG", optimize=True, dpi=(DPI, DPI))
    print(f"{path.relative_to(ROOT)}  {im.size[0]}x{im.size[1]}  {path.stat().st_size}")


def page(pdf: Path, index: int) -> Image.Image:
    doc = pdfium.PdfDocument(str(pdf))
    im = doc[index].render(scale=DPI / 72).to_pil()
    if im.mode != "RGB":
        im = im.convert("RGB")
    w, h = im.size
    return im


def promo() -> None:
    posters = [
        ("Podcast Poster E01 I Hate It (11x17).pdf", "E01 I Hate It 11x17.png", 11, 17),
        ("Podcast Poster E02 So Useful (11x17).pdf", "E02 So Useful 11x17.png", 11, 17),
        ("Podcast Poster E03 Human Finish (11x17).pdf", "E03 Human Finish 11x17.png", 11, 17),
    ]
    for src, name, ew, eh in posters:
        im = page(ROOT / src, 0)
        expect = (round(ew * DPI), round(eh * DPI))
        if abs(im.size[0] - expect[0]) > 4 or abs(im.size[1] - expect[1]) > 4:
            raise SystemExit(f"{src} rendered {im.size}, expected about {expect}")
        save(im, PNG / "posters" / name)

    sheets = page(ROOT / "Podcast Cards Letter.pdf", 0)
    sheets2 = page(ROOT / "Podcast Cards Letter.pdf", 1)
    squares = page(ROOT / "Podcast Cards Letter.pdf", 2)
    expect = (round(8.5 * DPI), round(11 * DPI))
    for label, im in (("sheet1", sheets), ("sheet2", sheets2), ("squares", squares)):
        if abs(im.size[0] - expect[0]) > 4 or abs(im.size[1] - expect[1]) > 4:
            raise SystemExit(f"{label} rendered {im.size}, expected about {expect}")

    save(sheets, PNG / "sheets" / "Letter halves 1.png")
    save(sheets2, PNG / "sheets" / "Letter halves 2.png")
    save(squares, PNG / "sheets" / "Letter squares.png")

    y1 = along(sheets.height, CARD_H, 11)
    y2 = along(sheets.height, CARD_H + CUT, 11)
    bottom = sheets.height
    cards = [
        (sheets, 0, y1, "cards/E01 I Hate It promo 8.5x5.4.png"),
        (sheets, y2, bottom, "cards/E02 So Useful promo 8.5x5.4.png"),
        (sheets2, 0, y1, "cards/E03 Human Finish promo 8.5x5.4.png"),
        (sheets2, y2, bottom, "cards/Series promo 8.5x5.4.png"),
    ]
    for im, top, bottom, name in cards:
        save(im.crop((0, top, im.width, bottom)), PNG / name)

    x0 = along(squares.width, SQ_X, 8.5)
    y0 = along(squares.height, SQ_Y, 11)
    side_x = along(squares.width, SQ, 8.5)
    side_y = along(squares.height, SQ, 11)
    step_x = along(squares.width, SQ + GAP, 8.5)
    step_y = along(squares.height, SQ + GAP, 11)
    quads = [
        (0, 0, "cards/E01 I Hate It square 3.9in.png"),
        (1, 0, "cards/E02 So Useful square 3.9in.png"),
        (0, 1, "cards/E03 Human Finish square 3.9in.png"),
        (1, 1, "cards/Series square 3.9in.png"),
    ]
    for col, row, name in quads:
        left = x0 + col * step_x
        top = y0 + row * step_y
        save(squares.crop((left, top, left + side_x, top + side_y)), PNG / name)


def assets() -> None:
    import cairosvg

    widths = {
        "jellyfish-gradient.svg": 1600,
        "jellyfish-ink.svg": 1600,
        "jellyfish-pink.svg": 1600,
        "audio-bars.svg": 2400,
        "bubble.svg": 512,
        "mask.svg": 512,
        "prompt.svg": 512,
        "spark.svg": 512,
    }
    for name, width in widths.items():
        src = ASSETS / name
        raw = cairosvg.svg2png(url=str(src), output_width=width)
        im = Image.open(io.BytesIO(raw))
        dest = ASSETS / (src.stem + ".png")
        save(im, dest)
        mirror = PNG / "assets" / dest.name
        mirror.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dest, mirror)

    for name in ("sait-logo.png", "saitsa-clubs-logo.png"):
        src = ASSETS / name
        dest = PNG / "assets" / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"{dest.relative_to(ROOT)}  copied")


def main() -> None:
    promo()
    assets()


if __name__ == "__main__":
    main()
