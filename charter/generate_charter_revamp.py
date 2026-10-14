#!/usr/bin/env python3
"""Generate the 2026–27 Unnatural Intelligence Club Charter PDF.

A copy of the original charter, rebuilt on the vector kit: lime–pink
squiggle in the header, jellyfish mascot in the footer, icons and
badges on the pages. Copy is rewritten from the club mission and the
Saitsa Clubs Handbook 2026/27.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

import revamp_copy as copy
from revamp_kit import ASSETS, export as export_kit

ROOT = Path(__file__).resolve().parent
FONTS = ROOT / "fonts"
OUTPUT = ROOT / "Unnatural_Intelligence_Club_Charter_2026-27.pdf"

PAPER = HexColor("#F9F9FA")
OLIVE = HexColor("#95B747")
INK = HexColor("#030205")
PINK = HexColor("#FA4A9E")
WINE = HexColor("#591337")
LIME = HexColor("#BAF837")
CYAN = HexColor("#7EC8FF")
SLATE = HexColor("#5A5A5A")
RULE = HexColor("#D7D7DA")

PAGE_W, PAGE_H = A4
CX = PAGE_W / 2
MARGIN_X = 54
CONTENT_W = PAGE_W - 2 * MARGIN_X
HEADER_H = 58
FOOTER_H = 52
CHROME_BAND_Y = PAGE_H - 80
CONTENT_TOP = PAGE_H - 122
ICON_GUTTER = 30


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Inter", str(FONTS / "Inter-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("Inter-Italic", str(FONTS / "Inter-Italic.ttf")))
    pdfmetrics.registerFont(TTFont("Inter-Medium", str(FONTS / "Inter-Medium.ttf")))
    pdfmetrics.registerFont(TTFont("Inter-SemiBold", str(FONTS / "Inter-SemiBold.ttf")))
    pdfmetrics.registerFont(TTFont("Inter-Bold", str(FONTS / "Inter-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("InterDisplay-Bold", str(FONTS / "InterDisplay-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("InterDisplay", str(FONTS / "InterDisplay-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("JetBrains", str(FONTS / "JetBrainsMono-Regular.ttf")))
    pdfmetrics.registerFont(TTFont("JetBrains-Bold", str(FONTS / "JetBrainsMono-Bold.ttf")))


def mix(a: Color, b: Color, t: float) -> Color:
    return Color(
        a.red + (b.red - a.red) * t,
        a.green + (b.green - a.green) * t,
        a.blue + (b.blue - a.blue) * t,
    )


def png(name: str) -> Path:
    return ASSETS / name


def img_size(
    name: str, *, w: float | None = None, h: float | None = None
) -> tuple[float, float]:
    img = ImageReader(str(png(name)))
    iw, ih = img.getSize()
    if w is None and h is None:
        w = iw * 0.24
        h = ih * 0.24
    elif w is None:
        w = h * iw / ih
    elif h is None:
        h = w * ih / iw
    return w, h


def draw_img(
    c: canvas.Canvas,
    name: str,
    x: float,
    y: float,
    *,
    w: float | None = None,
    h: float | None = None,
    center: bool = False,
    vcenter: bool = False,
) -> tuple[float, float]:
    w, h = img_size(name, w=w, h=h)
    dx = x - w / 2 if center else x
    dy = y - h / 2 if (center or vcenter) else y
    c.drawImage(
        ImageReader(str(png(name))),
        dx,
        dy,
        width=w,
        height=h,
        mask="auto",
        preserveAspectRatio=True,
        anchor="c",
    )
    return w, h


def badge_row(
    c: canvas.Canvas,
    slugs: list[str],
    y: float,
    *,
    h: float = 14,
    gap: float = 6,
    x0: float | None = None,
) -> float:
    sizes = [img_size(f"badge-{slug}.png", h=h) for slug in slugs]
    total = sum(bw for bw, _ in sizes) + gap * max(len(slugs) - 1, 0)
    x = CX - total / 2 if x0 is None else x0
    for slug, (bw, _) in zip(slugs, sizes):
        draw_img(c, f"badge-{slug}.png", x, y, h=h, vcenter=True)
        x += bw + gap
    return total


def paper(c: canvas.Canvas) -> None:
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)


def draw_header(c: canvas.Canvas) -> None:
    draw_img(c, "header.png", 14, PAGE_H - 56, w=PAGE_W - 28)
    draw_img(c, "icon-spark-plain.png", CX, PAGE_H - 28, h=20, center=True)


def draw_footer(c: canvas.Canvas, page: int) -> None:
    draw_img(c, "jellyfish-mini.png", CX, 34, h=32, center=True)
    c.setFillColor(WINE)
    c.setFont("JetBrains-Bold", 8)
    c.drawCentredString(CX, 8, f"{page:02d}")
    c.setFillColor(mix(SLATE, INK, 0.2))
    c.setFont("JetBrains", 6.5)
    c.drawString(MARGIN_X, 10, copy.URL)
    c.drawRightString(PAGE_W - MARGIN_X, 10, copy.YEAR)


def chrome(
    c: canvas.Canvas,
    page: int,
    *,
    icon: str | None = None,
    badges: list[str] | None = None,
) -> None:
    paper(c)
    draw_header(c)
    draw_footer(c, page)
    stamp_h = 22
    if icon:
        draw_img(
            c,
            f"icon-{icon}.png",
            PAGE_W - MARGIN_X - stamp_h / 2,
            CHROME_BAND_Y,
            h=stamp_h,
            center=True,
        )
    if badges:
        badge_row(c, badges, CHROME_BAND_Y, h=12, gap=6, x0=MARGIN_X)


def wrap(text: str, font: str, size: float, max_width: float) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if pdfmetrics.stringWidth(test, font, size) <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines or [""]


def draw_title(c: canvas.Canvas, text: str, y: float, size: float = 24) -> float:
    c.setFillColor(INK)
    c.setFont("InterDisplay-Bold", size)
    for line in text.split("\n"):
        c.drawCentredString(CX, y, line)
        y -= size + 4
    return y


def hrule(c: canvas.Canvas, y: float) -> None:
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(MARGIN_X, y, PAGE_W - MARGIN_X, y)


def bullet_item(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    level: int = 0,
    bold: bool = False,
    width: float | None = None,
) -> float:
    marks = [("filled", 2.8), ("open", 2.4), ("square", 2.0), ("dot", 1.5)]
    style, r = marks[min(level, 3)]
    indent = x + level * 16
    max_w = (width or (PAGE_W - MARGIN_X - indent - 8)) - 12
    font = "Inter-Bold" if bold else "Inter"
    size = 10.1 if level == 0 else 9.5
    leading = 13.8 if level == 0 else 12.8
    lines = wrap(text, font, size, max_w)
    cy = y + 2.2
    c.setFillColor(PINK if level == 0 else INK)
    c.setStrokeColor(INK)
    if style == "filled":
        c.setFillColor(LIME if bold else PINK)
        c.circle(indent, cy, r, fill=1, stroke=0)
        c.setFillColor(INK)
    elif style == "open":
        c.setLineWidth(0.9)
        c.circle(indent, cy, r, fill=0, stroke=1)
    elif style == "square":
        c.setFillColor(OLIVE)
        c.rect(indent - r, cy - r, r * 2, r * 2, fill=1, stroke=0)
        c.setFillColor(INK)
    else:
        c.circle(indent, cy, r, fill=1, stroke=0)
    c.setFont(font, size)
    tx = indent + 10
    for i, line in enumerate(lines):
        c.drawString(tx, y - i * leading, line)
    return y - (len(lines) - 1) * leading - (15.5 if level == 0 else 13.2)


def section_block(
    c: canvas.Canvas,
    heading: str,
    body: str,
    y: float,
    *,
    icon: str | None = None,
) -> float:
    text_x = MARGIN_X + ICON_GUTTER if icon else MARGIN_X
    text_w = CONTENT_W - (ICON_GUTTER if icon else 0)
    if icon:
        draw_img(
            c,
            f"icon-{icon}-plain.png",
            MARGIN_X + 9,
            y + 4,
            h=16,
            center=True,
        )
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 12)
    heading_lines = wrap(heading, "Inter-Bold", 12, text_w)
    for line in heading_lines:
        c.drawString(text_x, y, line)
        y -= 15
    c.setFont("Inter", 10.5)
    for line in wrap(body, "Inter", 10.5, text_w):
        c.drawString(text_x, y, line)
        y -= 14.2
    y -= 6
    hrule(c, y + 4)
    return y - 14


def foundation_cards(c: canvas.Canvas, y_top: float) -> float:
    gap = 14
    card_w = (CONTENT_W - 2 * gap) / 3
    pad_x = 16
    pad_top = 22
    icon_h = 28
    icon_title_gap = 18
    title_size = 9.5
    title_lead = 13
    title_lines_slot = 2
    body_size = 8.3
    body_lead = 11.6
    title_body_gap = 12
    pad_bottom = 16
    text_w = card_w - 2 * pad_x

    measured: list[tuple[str, list[str], list[str], float]] = []
    max_h = 0.0
    for icon, title, body in copy.FOUNDATIONS:
        t_lines = wrap(title, "Inter-Bold", title_size, text_w)
        b_lines = wrap(body, "Inter", body_size, text_w)
        block = (
            pad_top
            + icon_h
            + icon_title_gap
            + title_lines_slot * title_lead
            + title_body_gap
            + len(b_lines) * body_lead
            + pad_bottom
        )
        measured.append((icon, t_lines, b_lines, block))
        max_h = max(max_h, block)

    card_h = max(max_h, 196)
    for i, (icon, t_lines, b_lines, _) in enumerate(measured):
        x = MARGIN_X + i * (card_w + gap)
        c.setFillColor(white)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.8)
        c.roundRect(x, y_top - card_h, card_w, card_h, 10, fill=1, stroke=1)
        ix = x + card_w / 2
        iy = y_top - pad_top - icon_h / 2
        draw_img(c, f"icon-{icon}.png", ix, iy, h=icon_h, center=True)
        ty = y_top - pad_top - icon_h - icon_title_gap - title_size
        unused_title = (title_lines_slot - len(t_lines)) * title_lead
        ty -= unused_title / 2
        c.setFillColor(INK)
        c.setFont("Inter-Bold", title_size)
        for line in t_lines:
            c.drawCentredString(ix, ty, line)
            ty -= title_lead
        title_block_bottom = (
            y_top - pad_top - icon_h - icon_title_gap - title_lines_slot * title_lead
        )
        by = title_block_bottom - title_body_gap - body_size
        c.setFont("Inter", body_size)
        c.setFillColor(SLATE)
        for line in b_lines:
            c.drawCentredString(ix, by, line)
            by -= body_lead
    return y_top - card_h


def role_block(c: canvas.Canvas, title: str, purpose: str, items, y: float) -> float:
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 12)
    for line in wrap(title, "Inter-Bold", 12, CONTENT_W):
        c.drawString(MARGIN_X, y, line)
        y -= 15
    c.setFont("Inter-Bold", 10)
    c.drawString(MARGIN_X, y, "Core Purpose:")
    c.setFont("Inter", 10)
    leftover = CONTENT_W - 78
    purpose_lines = wrap(purpose, "Inter", 10, leftover)
    c.drawString(MARGIN_X + 78, y, purpose_lines[0])
    y -= 14
    for extra in purpose_lines[1:]:
        c.drawString(MARGIN_X + 78, y, extra)
        y -= 13
    c.setFont("Inter-Bold", 10)
    c.setFillColor(INK)
    c.drawString(MARGIN_X, y, "Responsibilities:")
    y -= 15
    for text, level in items:
        y = bullet_item(c, text, MARGIN_X, y, level=level)
    return y


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


def page_cover(c: canvas.Canvas) -> None:
    chrome(c, 1)
    draw_img(c, "jellyfish.png", CX, PAGE_H / 2 + 168, h=148, center=True)
    draw_img(c, "wordmark.png", CX, PAGE_H / 2 + 42, w=236, center=True)
    c.setFillColor(INK)
    c.setFont("InterDisplay-Bold", 28)
    c.drawCentredString(CX, PAGE_H / 2 - 48, "Club Charter")
    c.setFont("JetBrains-Bold", 11)
    c.setFillColor(WINE)
    c.drawCentredString(CX, PAGE_H / 2 - 72, copy.YEAR)
    c.setFillColor(SLATE)
    c.setFont("Inter-Italic", 11)
    c.drawCentredString(CX, PAGE_H / 2 - 96, copy.PILLARS)
    draw_img(c, "tagline.png", CX, PAGE_H / 2 - 148, w=220, center=True)
    badge_row(c, ["member", "exec", "live-lab", "workshop"], 88, h=15, gap=8)


def page_toc(c: canvas.Canvas) -> None:
    chrome(c, 2, icon="commit")
    y = draw_title(c, "Contents", CONTENT_TOP, size=24) - 8
    for title, num, bold, level in copy.TOC:
        font = "Inter-Bold" if bold else "Inter"
        size = 11 if bold else 10
        x = MARGIN_X + level * 18
        c.setFont(font, size)
        c.setFillColor(INK)
        c.drawString(x, y, title)
        dots_x = x + pdfmetrics.stringWidth(title, font, size) + 8
        num_w = pdfmetrics.stringWidth(num, "JetBrains", size)
        c.setStrokeColor(RULE)
        c.setDash(1, 3)
        c.setLineWidth(0.6)
        c.line(dots_x, y + 3, PAGE_W - MARGIN_X - num_w - 8, y + 3)
        c.setDash()
        c.setFillColor(WINE)
        c.setFont("JetBrains", size)
        c.drawRightString(PAGE_W - MARGIN_X, y, num)
        y -= 18 if bold else 15.5


def page_mission(c: canvas.Canvas) -> None:
    chrome(c, 3, icon="spark", badges=["member"])
    y = draw_title(c, "Mission Statement", CONTENT_TOP, size=24) - 8
    c.setFillColor(INK)
    c.setFont("Inter", 11)
    for line in wrap(copy.MISSION_LEAD, "Inter", 11, CONTENT_W - 8):
        c.drawCentredString(CX, y, line)
        y -= 16
    y -= 12
    c.setFillColor(WINE)
    c.setFont("Inter-Italic", 13)
    for line in wrap(f"“{copy.MISSION_QUOTE}”", "Inter-Italic", 13, CONTENT_W - 24):
        c.drawCentredString(CX, y, line)
        y -= 18
    y -= 10
    c.setFillColor(INK)
    c.setFont("Inter", 11)
    for line in wrap(copy.MISSION_FEELINGS, "Inter", 11, CONTENT_W - 8):
        c.drawCentredString(CX, y, line)
        y -= 16
    y -= 18
    cards_bottom = foundation_cards(c, y)
    _quote_w, quote_h = img_size("quote-useful.png", w=200)
    footer_top = FOOTER_H + 10
    room = cards_bottom - footer_top
    quote_y = footer_top + room / 2
    min_y = cards_bottom - 22 - quote_h / 2
    if quote_y > min_y:
        quote_y = min_y
    draw_img(c, "quote-useful.png", CX, quote_y, w=200, center=True)


def page_basis(c: canvas.Canvas) -> None:
    chrome(c, 4, icon="tentacle")
    y = draw_title(c, "The Basis", CONTENT_TOP, size=24) - 6
    icons = ["bubble", "spark", "workflow", "mask", "ticket"]
    for (heading, body), icon in zip(copy.BASIS, icons):
        y = section_block(c, heading, body, y, icon=icon)


def page_goals_a(c: canvas.Canvas) -> None:
    chrome(c, 5, icon="spark")
    y = draw_title(c, "Goals", CONTENT_TOP, size=24) - 4
    icons = ["bubble", "spark", "workflow", "meter", "neural"]
    for (heading, body), icon in zip(copy.GOALS_A, icons):
        y = section_block(c, heading, body, y, icon=icon)


def page_goals_b(c: canvas.Canvas) -> None:
    chrome(c, 6, icon="node")
    y = CONTENT_TOP
    icons = ["ticket", "commit", "halt", "mask", "glitch"]
    for (heading, body), icon in zip(copy.GOALS_B, icons):
        y = section_block(c, heading, body, y, icon=icon)


def page_operate(c: canvas.Canvas) -> None:
    chrome(c, 7, icon="ticket", badges=["member", "exec"])
    y = draw_title(c, "How We Operate", CONTENT_TOP, size=22) - 2
    c.setFillColor(SLATE)
    c.setFont("Inter-Italic", 9)
    c.drawCentredString(CX, y, "From the Saitsa Clubs Handbook 2026/27")
    y -= 18
    icons = ["commit", "ticket", "node", "prompt", "token"]
    for (heading, body), icon in zip(copy.OPERATE, icons):
        y = section_block(c, heading, body, y, icon=icon)
    note_w = CONTENT_W - 108
    c.setFillColor(SLATE)
    c.setFont("Inter-Italic", 8.6)
    for line in wrap(copy.SIGNING_NOTE, "Inter-Italic", 8.6, note_w):
        c.drawString(MARGIN_X, y, line)
        y -= 12
    draw_img(c, "saitsa-clubs.png", PAGE_W - MARGIN_X - 46, 80, w=90, center=True)


def page_exec_divider(c: canvas.Canvas) -> None:
    chrome(c, 8, icon="node", badges=["exec"])
    draw_img(c, "jellyfish.png", CX, PAGE_H / 2 + 100, h=170, center=True)
    c.setFillColor(INK)
    c.setFont("InterDisplay-Bold", 28)
    c.drawCentredString(CX, PAGE_H / 2 - 24, "Executive Roles &")
    c.drawCentredString(CX, PAGE_H / 2 - 58, "Responsibilities")
    c.setFillColor(WINE)
    c.setFont("JetBrains", 9)
    c.drawCentredString(CX, PAGE_H / 2 - 84, "President  ·  VP Operations  ·  VP Finance")


def page_directors(c: canvas.Canvas) -> None:
    chrome(c, 9, icon="node", badges=["exec"])
    y = CONTENT_TOP
    c.setFillColor(INK)
    c.setFont("InterDisplay-Bold", 20)
    c.drawString(MARGIN_X, y, "Directors")
    y -= 24
    y = role_block(c, *copy.PRESIDENT, y)
    y -= 8
    y = role_block(c, *copy.VP_OPS, y)


def page_finance(c: canvas.Canvas) -> None:
    chrome(c, 10, icon="token", badges=["exec"])
    y = CONTENT_TOP
    c.setFillColor(INK)
    c.setFont("InterDisplay-Bold", 20)
    c.drawString(MARGIN_X, y, "Directors")
    y -= 26
    y = role_block(c, *copy.VP_FINANCE, y)
    y -= 10
    c.setFillColor(SLATE)
    c.setFont("Inter-Italic", 9)
    note = (
        "Saitsa requires every club to keep three key executives filled: "
        "President, Vice-President Operations, and Vice-President Finance. "
        "These are the club’s signing authorities. Only current SAIT students "
        "who have paid their Saitsa fee may hold executive positions. "
        "Executives cannot be paid; the club operates on a non-profit basis."
    )
    for line in wrap(note, "Inter-Italic", 9, CONTENT_W):
        c.drawString(MARGIN_X, y, line)
        y -= 12.5


def page_marketing(c: canvas.Canvas) -> None:
    chrome(c, 11, icon="glitch", badges=["exec"])
    y = CONTENT_TOP
    c.setFillColor(INK)
    c.setFont("InterDisplay-Bold", 20)
    c.drawString(MARGIN_X, y, "Marketing")
    y -= 22
    y = role_block(c, *copy.SOCIAL, y)
    y -= 6
    y = role_block(c, *copy.DESIGNER, y)


def page_events_roles(c: canvas.Canvas) -> None:
    chrome(c, 12, icon="ticket", badges=["exec", "workshop"])
    y = CONTENT_TOP
    c.setFillColor(INK)
    c.setFont("InterDisplay-Bold", 20)
    c.drawString(MARGIN_X, y, "Events")
    y -= 22
    y = role_block(c, *copy.EVENTS_COORD, y)
    y -= 6
    y = role_block(c, *copy.OUTREACH, y)


def page_events_divider(c: canvas.Canvas) -> None:
    chrome(c, 13, icon="halt", badges=["halt-restart", "live-lab", "workshop", "clubs-expo"])
    draw_img(c, "icon-halt.png", CX - 56, PAGE_H / 2 + 52, h=44, center=True)
    draw_img(c, "icon-restart.png", CX + 56, PAGE_H / 2 + 52, h=44, center=True)
    c.setFillColor(INK)
    c.setFont("InterDisplay-Bold", 32)
    c.drawCentredString(CX, PAGE_H / 2 - 16, "Event Concepts")
    c.setFillColor(SLATE)
    c.setFont("Inter-Italic", 11)
    c.drawCentredString(CX, PAGE_H / 2 - 46, "Live labs  ·  Workshops  ·  Mixers  ·  Showcases")


def page_events_a(c: canvas.Canvas) -> None:
    chrome(c, 14, icon="spark", badges=["workshop", "live-lab"])
    y = CONTENT_TOP
    y = bullet_item(
        c,
        "Untapped Potential — find what default chat never gets asked.",
        MARGIN_X,
        y,
        bold=True,
    )
    for text, level in copy.UNTAPPED_ITEMS:
        y = bullet_item(c, text, MARGIN_X, y, level=level)
    y -= 8
    y = bullet_item(
        c,
        "Workflow Integration — from demo to a Tuesday you would actually keep.",
        MARGIN_X,
        y,
        bold=True,
    )
    for text, level in copy.WORKFLOW_ITEMS:
        y = bullet_item(c, text, MARGIN_X, y, level=level)


def page_events_b(c: canvas.Canvas) -> None:
    chrome(c, 15, icon="mask", badges=["halt-restart", "clubs-expo"])
    y = CONTENT_TOP
    y = bullet_item(
        c,
        "Token Craft & Human Touch — less spend, more of you in the result.",
        MARGIN_X,
        y,
        bold=True,
    )
    for text, level in copy.TOKEN_ITEMS:
        y = bullet_item(c, text, MARGIN_X, y, level=level)
    y -= 8
    y = bullet_item(c, "Mixer events", MARGIN_X, y, bold=True)
    for text, level in copy.MIXER_ITEMS:
        y = bullet_item(c, text, MARGIN_X, y, level=level)


def page_calendar(c: canvas.Canvas) -> None:
    chrome(c, 16, icon="ticket", badges=["clubs-expo", "halt-restart"])
    y = draw_title(c, "This Year on Campus", CONTENT_TOP, size=22) - 4
    c.setFillColor(SLATE)
    c.setFont("Inter", 10)
    c.drawCentredString(CX, y, "Club year 2026–27  ·  Saitsa fiscal year ends 30 June")
    y -= 22
    row_h = 28
    for date, event in copy.CALENDAR:
        c.setFillColor(white)
        c.setStrokeColor(RULE)
        c.roundRect(MARGIN_X, y - 8, CONTENT_W, row_h - 4, 4, fill=1, stroke=1)
        c.setFillColor(WINE)
        c.setFont("JetBrains-Bold", 8.5)
        c.drawString(MARGIN_X + 10, y + 2, date)
        c.setFillColor(INK)
        c.setFont("Inter", 10)
        c.drawString(MARGIN_X + 168, y + 2, event)
        y -= row_h
    y -= 10
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 12)
    c.drawString(MARGIN_X, y, "How we register")
    y -= 16
    for note in copy.REGISTER:
        y = bullet_item(c, note, MARGIN_X, y, level=0)
        y -= 2


def page_style_visual(c: canvas.Canvas) -> None:
    chrome(c, 17, icon="spark")
    y = draw_title(c, "Unnatural Intelligence Style Guide", CONTENT_TOP, size=18)
    y -= 4
    col_w = CONTENT_W / 2
    band_h = 136
    band_mid = y - band_h / 2
    draw_img(
        c,
        "lockup-stacked.png",
        MARGIN_X + col_w / 2,
        band_mid,
        h=band_h,
        center=True,
    )
    draw_img(
        c,
        "jellyfish.png",
        MARGIN_X + col_w + col_w / 2,
        band_mid,
        h=92,
        center=True,
    )
    y -= band_h + 28
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 11)
    c.drawCentredString(CX, y, "Palette")
    y -= 10
    draw_img(c, "swatches.png", MARGIN_X, y - 78, w=CONTENT_W)
    y -= 100
    c.setFont("Inter-Bold", 11)
    c.drawCentredString(CX, y, "Icons — stamps for pages and events")
    y -= 12
    sprite_w, sprite_h = img_size("icon-sprite.png", h=108)
    draw_img(c, "icon-sprite.png", CX, y - sprite_h / 2, h=108, center=True)
    y -= sprite_h + 22
    c.setFont("Inter-Bold", 11)
    c.drawCentredString(CX, y, "Badges")
    y -= 18
    badge_row(
        c,
        ["member", "exec", "workshop", "live-lab", "halt-restart", "clubs-expo"],
        y,
        h=16,
        gap=8,
    )
    c.setFillColor(LIME)
    c.roundRect(MARGIN_X, 58, CONTENT_W, 26, 4, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 9)
    c.drawCentredString(CX, 67, "Primary: Inter  ·  Display titles  ·  JetBrains Mono for labels")


def page_style_codes(c: canvas.Canvas) -> None:
    chrome(c, 18, icon="glitch")
    y = draw_title(c, "Copy-paste codes", CONTENT_TOP, size=20)
    c.setFillColor(SLATE)
    c.setFont("Inter-Italic", 11)
    c.drawCentredString(CX, y, "Google-friendly fonts: Inter  |  Inter Display  |  JetBrains Mono")
    y -= 36
    box_w, box_h = 118, 52
    gap_x, gap_y = 16, 28
    cols = 4
    colors = {
        "#F9F9FA": PAPER,
        "#95B747": OLIVE,
        "#030205": INK,
        "#FA4A9E": PINK,
        "#591337": WINE,
        "#BAF837": LIME,
        "#7EC8FF": CYAN,
    }
    last_bottom = y
    n_swatches = len(copy.SWATCHES)
    for i, (hex_code, name) in enumerate(copy.SWATCHES):
        col_i, row = i % cols, i // cols
        row_start_i = row * cols
        items_in_row = min(cols, n_swatches - row_start_i)
        row_width = items_in_row * box_w + (items_in_row - 1) * gap_x
        row_start = CX - row_width / 2
        x = row_start + col_i * (box_w + gap_x)
        yy = y - box_h - row * (box_h + gap_y)
        last_bottom = yy
        col = colors[hex_code]
        c.setFillColor(col)
        if hex_code == "#F9F9FA":
            c.setStrokeColor(RULE)
            c.roundRect(x, yy, box_w, box_h, 6, fill=1, stroke=1)
        else:
            c.roundRect(x, yy, box_w, box_h, 6, fill=1, stroke=0)
        label = white if hex_code in ("#030205", "#591337", "#FA4A9E") else INK
        c.setFillColor(label)
        c.setFont("JetBrains-Bold", 9)
        c.drawCentredString(x + box_w / 2, yy + 24, hex_code)
        c.setFont("Inter", 8)
        c.drawCentredString(x + box_w / 2, yy + 10, name)
    y = last_bottom - 28
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 12)
    c.drawString(MARGIN_X, y, "How to use it")
    y -= 16
    for note in copy.STYLE_NOTES:
        y = bullet_item(c, note, MARGIN_X, y, level=0)
        y -= 2
    draw_img(c, "flourish.png", CX, 62, w=180, center=True)


def build() -> Path:
    export_kit()
    register_fonts()
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("Unnatural Intelligence Club Charter 2026–27")
    c.setAuthor("Unnatural Intelligence")
    c.setSubject(copy.MISSION_QUOTE)

    pages = [
        page_cover,
        page_toc,
        page_mission,
        page_basis,
        page_goals_a,
        page_goals_b,
        page_operate,
        page_exec_divider,
        page_directors,
        page_finance,
        page_marketing,
        page_events_roles,
        page_events_divider,
        page_events_a,
        page_events_b,
        page_calendar,
        page_style_visual,
        page_style_codes,
    ]
    for i, fn in enumerate(pages):
        fn(c)
        if i != len(pages) - 1:
            c.showPage()
    c.save()
    return OUTPUT


if __name__ == "__main__":
    path = build()
    print(f"Wrote {path}")
