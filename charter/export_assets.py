#!/usr/bin/env python3
"""Render brand PNGs from the same drawing code as the PDF charter."""

from __future__ import annotations

import io
from pathlib import Path

import pymupdf
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from generate_charter import (
    CX,
    PAGE_H,
    PAGE_W,
    draw_header_waves,
    draw_mascot,
    draw_wordmark,
    register_fonts,
)

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
SCALE = 3.0


def _page_image() -> Image.Image:
    register_fonts()
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    draw_header_waves(c)
    draw_mascot(c, CX, PAGE_H / 2, size=48)
    draw_wordmark(c, CX, PAGE_H / 2 - 120, size=72)
    c.save()
    doc = pymupdf.open(stream=buf.getvalue(), filetype="pdf")
    pix = doc[0].get_pixmap(matrix=pymupdf.Matrix(SCALE, SCALE), alpha=False)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def export() -> Path:
    ASSETS.mkdir(exist_ok=True)
    img = _page_image()
    w, h = img.size
    img.crop((0, 0, w, int(78 * SCALE))).save(ASSETS / "header.png")

    mascot_box = int(92 * SCALE)
    mascot_py = int((PAGE_H - PAGE_H / 2) * SCALE)
    img.crop(
        (
            w // 2 - mascot_box // 2,
            mascot_py - mascot_box // 2,
            w // 2 + mascot_box // 2,
            mascot_py + mascot_box // 2,
        )
    ).save(ASSETS / "mascot.png")

    word_top = int((PAGE_H - (PAGE_H / 2 - 120) - 80) * SCALE)
    word_bot = int((PAGE_H - (PAGE_H / 2 - 120) + 24) * SCALE)
    img.crop((int(w * 0.22), word_top, int(w * 0.78), word_bot)).save(ASSETS / "wordmark.png")
    print(f"Wrote {ASSETS}/header.png, mascot.png, wordmark.png")
    return ASSETS


if __name__ == "__main__":
    export()
