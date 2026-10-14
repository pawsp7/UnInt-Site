#!/usr/bin/env python3
"""Render the 6 ft × 3 ft Unnatural Intelligence banner.

Outputs a print PDF (72 in × 36 in at 150 DPI), 100 DPI and 150 DPI PNGs,
and a 1920×960 preview. The HTML layout PNG (banner_6x3ft_html_layout.png)
is captured from index.html + assets/jellyfish.svg with capture_html_layout.sh.
The print PDF embeds that 150 DPI layout when present.
Requires: pip install pillow numpy reportlab svglib pymupdf
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pymupdf
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

ROOT = Path(__file__).resolve().parent
FONTS = ROOT.parents[2] / "charter" / "fonts"
JELLY = ROOT / "assets" / "jellyfish.svg"
PREVIEW = ROOT / "Banner_6x3ft-preview.png"
PRINT_PNG = ROOT / "Banner_6x3ft-print.png"
PRINT_150 = ROOT / "Banner_6x3ft-150dpi.png"
HTML_PNG = ROOT / "banner_6x3ft_html_layout.png"
PDF = ROOT / "Banner_6x3ft.pdf"

W_IN, H_IN = 72.0, 36.0
DPI = 100
W, H = int(W_IN * DPI), int(H_IN * DPI)

# Sized to read as a faint graph-paper texture from across an expo aisle
# (~10–15 ft). Lines follow the jellyfish lime → pink wash.
GRID_STEP_IN = 0.72
GRID_LINE_IN = 0.10
GRID_HALO_IN = 0.045
GRID_MIX = 0.13
LIME = np.array([0xBA, 0xF8, 0x37], dtype=np.float32)
PINK = np.array([0xFA, 0x4A, 0x9E], dtype=np.float32)


def set_dpi(dpi: int) -> None:
    global DPI, W, H
    DPI = dpi
    W, H = int(W_IN * DPI), int(H_IN * DPI)


def inch_px(v: float) -> float:
    return v * DPI


def background() -> Image.Image:
    h, w = H, W
    yy, xx = np.ogrid[:h, :w]
    x = xx / (w - 1)

    c1 = np.array([0x1A, 0x08, 0x12], dtype=np.float32)
    c2 = np.array([0x0A, 0x04, 0x08], dtype=np.float32)
    c3 = np.array([0x03, 0x02, 0x05], dtype=np.float32)
    t = np.clip(x / 0.42, 0, 1)
    left = c1 * (1 - t[..., None]) + c2 * t[..., None]
    t2 = np.clip((x - 0.42) / 0.58, 0, 1)
    right = c2 * (1 - t2[..., None]) + c3 * t2[..., None]
    img = np.where(x[..., None] <= 0.42, left, right)

    def radial(cx, cy, rx, ry, color, strength):
        d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        a = np.clip(1.0 - d, 0, 1)
        a = (a ** 1.15) * strength
        return color, a

    layers = [
        radial(0, h * 0.50, w * 0.48, h * 0.90, np.array([89, 19, 55], np.float32), 0.92),
        radial(w * 0.18, h * 1.02, w * 0.42, h * 0.70, PINK, 0.16),
        radial(w * 0.88, h * 0.08, w * 0.36, h * 0.60, LIME, 0.07),
    ]
    for color, a in layers:
        img = img * (1 - a[..., None]) + color * a[..., None]

    step = inch_px(GRID_STEP_IN)
    line_w = inch_px(GRID_LINE_IN)
    halo = max(inch_px(GRID_HALO_IN), 1.0)

    def line_cov(f: np.ndarray) -> np.ndarray:
        core = np.clip(line_w - f, 0, 1)
        after = np.clip(1.0 - (f - line_w) / halo, 0, 1) * 0.34
        before = np.clip(1.0 - (step - f) / halo, 0, 1) * 0.34
        return np.maximum.reduce([core, after, before])

    fy = np.mod(yy.astype(np.float32), step)
    fx = np.mod(xx.astype(np.float32), step)
    grid = np.maximum(line_cov(fy), line_cov(fx))

    def falloff(cx, cy, rx, ry, p=0.85):
        d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
        return np.clip(1.0 - d, 0, 1) ** p

    lime_f = np.maximum(
        falloff(w * 0.26, h * 0.30, w * 0.48, h * 0.62),
        falloff(w * 0.86, h * 0.10, w * 0.38, h * 0.48) * 0.65,
    )
    pink_f = np.maximum(
        falloff(w * 0.20, h * 0.78, w * 0.46, h * 0.70),
        falloff(w * 0.64, h * 0.62, w * 0.58, h * 0.74),
    )
    wsum = lime_f + pink_f + 1e-6
    grid_color = (lime_f / wsum)[..., None] * LIME + (pink_f / wsum)[..., None] * PINK
    ga = grid * np.maximum(lime_f, pink_f) * GRID_MIX
    img = img * (1 - ga[..., None]) + grid_color * ga[..., None]

    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def rasterize_svg(path: Path, height_px: int) -> Image.Image:
    """Render the vector mascot at the requested pixel height."""
    drawing = svg2rlg(str(path))
    tmp = path.with_name("_jelly_render.pdf")
    renderPDF.drawToFile(drawing, str(tmp))
    try:
        doc = pymupdf.open(str(tmp))
        page = doc[0]
        zoom = height_px / page.rect.height
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=True)
        return Image.frombytes("RGBA", (pix.width, pix.height), pix.samples)
    finally:
        tmp.unlink(missing_ok=True)


def load_font(name: str, size_in: float) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / name), size=max(1, int(round(inch_px(size_in)))))


def text_width(font: ImageFont.FreeTypeFont, text: str, tracking_em: float) -> float:
    extra = tracking_em * font.size
    total = 0.0
    for i, ch in enumerate(text):
        total += font.getlength(ch)
        if i < len(text) - 1:
            total += extra
    return total


def draw_tracked(draw: ImageDraw.ImageDraw, xy, text, font, fill, tracking_em: float) -> None:
    x, y = xy
    extra = tracking_em * font.size
    for i, ch in enumerate(text):
        draw.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + extra


def compose() -> Image.Image:
    bg = background().convert("RGBA")
    jelly_h = inch_px(26.2)
    jelly = rasterize_svg(JELLY, int(round(jelly_h)))
    glow = jelly.copy().filter(ImageFilter.GaussianBlur(radius=inch_px(0.18)))
    glow_px = np.array(glow)
    glow_px[..., 3] = (glow_px[..., 3].astype(np.float32) * 0.35).astype(np.uint8)
    glow = Image.fromarray(glow_px, "RGBA")

    display = load_font("InterDisplay-Bold.ttf", 6.15)
    tag_font = load_font("Inter-Medium.ttf", 1.08)
    url_font = load_font("JetBrainsMono-Regular.ttf", 0.34)

    line1, line2 = "UNNATURAL", "INTELLIGENCE"
    tag = "GENERATED BY AI · PERFECTED BY HUMANS"
    url = "UNNATURALINTELLIGENCE.CLUB · SAIT STUDENT CLUB"

    scale_x = 0.84
    tracking_word = -0.055
    tracking_tag = 0.34
    lh = 0.86
    line_h = display.size * lh
    tag_gap = inch_px(1.35)

    w1 = text_width(display, line1, tracking_word) * scale_x
    w2 = text_width(display, line2, tracking_word) * scale_x
    wtag = text_width(tag_font, tag, tracking_tag) * scale_x
    type_w = max(w1, w2, wtag)
    type_h = line_h * 2 + tag_gap + tag_font.size

    gap = inch_px(1.35)
    lockup_w = jelly.width + gap + type_w
    lockup_h = max(jelly.height, type_h)
    origin_x = (W - lockup_w) / 2
    origin_y = (H - lockup_h) / 2

    jelly_x = int(round(origin_x))
    jelly_y = int(round(origin_y + (lockup_h - jelly.height) / 2))
    bg.alpha_composite(glow, (jelly_x, jelly_y))
    bg.alpha_composite(jelly, (jelly_x, jelly_y))

    type_x = origin_x + jelly.width + gap
    type_y = origin_y + (lockup_h - type_h) / 2
    paper = (249, 249, 250, 255)
    cyan = (126, 200, 255, 255)
    pink = (250, 74, 158, 255)

    def draw_scaled_line(text, font, y, fill, tracking, dx, dy, fill_tag=False):
        layer = Image.new("RGBA", (int(type_w / scale_x) + 80, int(font.size * 1.4) + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        ox, oy = 40, 12
        draw_tracked(d, (ox - dx / scale_x, oy + dy), text, font, cyan if not fill_tag else (92, 225, 255, 204), tracking)
        draw_tracked(d, (ox + dx / scale_x, oy - dy), text, font, pink if not fill_tag else (255, 90, 176, 204), tracking)
        draw_tracked(d, (ox, oy), text, font, fill, tracking)
        scaled_w = int(round(layer.width * scale_x))
        scaled = layer.resize((scaled_w, layer.height), Image.Resampling.LANCZOS)
        bg.alpha_composite(scaled, (int(round(type_x - 40 * scale_x)), int(round(y - 12))))

    draw_scaled_line(line1, display, type_y, paper, tracking_word, inch_px(0.075), inch_px(0.02))
    draw_scaled_line(line2, display, type_y + line_h, paper, tracking_word, inch_px(0.075), inch_px(0.02))
    tag_fill = (249, 249, 250, 209)
    draw_scaled_line(
        tag,
        tag_font,
        type_y + line_h * 2 + tag_gap,
        tag_fill,
        tracking_tag,
        inch_px(0.045),
        inch_px(0.012),
        fill_tag=True,
    )

    url_layer = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    ud = ImageDraw.Draw(url_layer)
    uw = text_width(url_font, url, 0.22)
    ux = (W - uw) / 2
    uy = H - inch_px(1.05) - url_font.size
    draw_tracked(ud, (ux, uy), url, url_font, (249, 249, 250, 148), 0.22)
    bg.alpha_composite(url_layer)
    return bg.convert("RGB")


def write_pdf(print_png: Path) -> None:
    """Write a 72 in × 36 in print PDF with the raster at native pixel size."""
    doc = pymupdf.open()
    page = doc.new_page(width=W_IN * 72, height=H_IN * 72)
    page.insert_image(page.rect, filename=str(print_png), keep_proportion=True)
    doc.set_metadata(
        {
            "title": "Unnatural Intelligence — 6 ft × 3 ft banner",
            "author": "Unnatural Intelligence",
        }
    )
    doc.save(str(PDF), deflate=True, garbage=4)
    doc.close()


def main() -> None:
    set_dpi(100)
    art100 = compose()
    art100.save(PRINT_PNG, optimize=True, dpi=(100, 100))
    preview = art100.resize((1920, 960), Image.Resampling.LANCZOS)
    preview.save(PREVIEW, optimize=True, dpi=(72, 72))

    set_dpi(150)
    art150 = compose()
    art150.save(PRINT_150, optimize=True, dpi=(150, 150))
    pdf_src = HTML_PNG if HTML_PNG.exists() else PRINT_150
    write_pdf(pdf_src)
    print(f"Wrote {PREVIEW.name}, {PRINT_PNG.name}, {PRINT_150.name}, {PDF.name} from {pdf_src.name}")


if __name__ == "__main__":
    main()
