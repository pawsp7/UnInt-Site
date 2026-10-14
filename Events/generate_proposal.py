#!/usr/bin/env python3
"""Generate the branded Unnatural Intelligence event proposal template.

Same 2026–27 kit as the charter: lime–pink squiggle, jellyfish footer,
Inter / JetBrains Mono. Every proposal includes $15 printing
(25 posters + 30 name tags) and $5 misc.
"""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib.colors import white
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

EVENTS = Path(__file__).resolve().parent
REPO = EVENTS.parent
CHARTER = REPO / "charter"
sys.path.insert(0, str(CHARTER))

import generate_charter_revamp as kit
import revamp_copy as copy
from revamp_kit import export as export_kit

OUTPUT = EVENTS / "event-proposal-TEMPLATE.pdf"

POSTER_QTY = 25
POSTER_COST = 12.00
NAMETAG_QTY = 30
NAMETAG_COST = 3.00
PRINTING_COST = POSTER_COST + NAMETAG_COST
MISC_COST = 5.00
BUILT_IN_TOTAL = PRINTING_COST + MISC_COST
PRINTING_DETAILS = (
    f"{POSTER_QTY}× tabloid 11×17 posters (${POSTER_COST:.0f}) and "
    f"{NAMETAG_QTY} name tags (${NAMETAG_COST:.0f}). Unaltered Saitsa Clubs "
    "logo, saitsa.com/Poster-Submission"
)

LIME_WASH = kit.mix(kit.PAPER, kit.LIME, 0.28)
PINK_WASH = kit.mix(kit.PAPER, kit.PINK, 0.16)


def money(value: float) -> str:
    return f"${value:.2f}"


def signature_line(c: canvas.Canvas, y: float = 60) -> None:
    c.setFillColor(kit.INK)
    c.setFont("Inter-Bold", 7.5)
    c.drawCentredString(
        kit.CX,
        y,
        "Primary Event Organizer — [NAME AND EXECUTIVE ROLE]",
    )
    c.setFillColor(kit.SLATE)
    c.setFont("Inter", 7.5)
    c.drawCentredString(
        kit.CX,
        y - 12,
        "Signature: ____________________     Date: ______________",
    )


def labeled_box(
    c: canvas.Canvas,
    label: str,
    hint: str,
    y: float,
    height: float = 44,
) -> float:
    c.setFillColor(kit.INK)
    c.setFont("Inter-Bold", 12)
    c.drawString(kit.MARGIN_X, y, label)
    y -= 10
    bottom = y - height
    c.setFillColor(white)
    c.setStrokeColor(kit.RULE)
    c.setLineWidth(0.8)
    c.roundRect(kit.MARGIN_X, bottom, kit.CONTENT_W, height, 8, fill=1, stroke=1)
    if hint:
        c.setFillColor(kit.SLATE)
        c.setFont("Inter-Italic", 9.5)
        lines = kit.wrap(hint, "Inter-Italic", 9.5, kit.CONTENT_W - 24)
        ty = y - 16
        for line in lines:
            c.drawString(kit.MARGIN_X + 12, ty, line)
            ty -= 13
    return bottom - 18


def draw_table(
    c: canvas.Canvas,
    y: float,
    headers: list[str],
    widths: list[float],
    rows: list[tuple[list[str], str]],
    aligns: list[str] | None = None,
    min_row_h: float = 30,
) -> float:
    aligns = aligns or ["left"] * len(headers)
    x0 = kit.MARGIN_X
    pad_x = 8
    pad_y = 8
    size = 9.2
    lead = 12.2
    header_h = 22

    c.setFillColor(kit.INK)
    c.roundRect(x0, y - header_h, kit.CONTENT_W, header_h, 6, fill=1, stroke=0)
    # square off the bottom of the header so it joins the body
    c.rect(x0, y - header_h, kit.CONTENT_W, 8, fill=1, stroke=0)
    c.setFillColor(kit.PAPER)
    c.setFont("Inter-Bold", 8.5)
    x = x0
    for header, width, align in zip(headers, widths, aligns):
        tx = x + pad_x if align != "right" else x + width - pad_x
        if align == "right":
            c.drawRightString(tx, y - 14, header)
        else:
            c.drawString(tx, y - 14, header)
        x += width
    y -= header_h

    for cells, kind in rows:
        wrapped: list[list[str]] = []
        fonts = []
        for i, (text, width) in enumerate(zip(cells, widths)):
            bold = kind in {"builtin", "total"} and i == 0
            font = "Inter-Bold" if bold or kind == "total" else "Inter"
            fonts.append(font)
            wrapped.append(kit.wrap(text, font, size, width - 2 * pad_x) or [""])
        n_lines = max(len(lines) for lines in wrapped)
        row_h = max(min_row_h, pad_y * 2 + n_lines * lead)
        fill = {
            "builtin": LIME_WASH,
            "total": PINK_WASH,
            "blank": white,
            "body": white,
        }[kind]
        c.setFillColor(fill)
        c.setStrokeColor(kit.RULE)
        c.setLineWidth(0.5)
        c.rect(x0, y - row_h, kit.CONTENT_W, row_h, fill=1, stroke=1)
        x = x0
        for lines, width, align, font in zip(wrapped, widths, aligns, fonts):
            c.setFont(font, size)
            c.setFillColor(kit.WINE if kind == "total" else kit.INK)
            ty = y - pad_y - size
            for line in lines:
                if align == "right":
                    c.drawRightString(x + width - pad_x, ty, line)
                else:
                    c.drawString(x + pad_x, ty, line)
                ty -= lead
            x += width
        y -= row_h
    return y


def page_cover(c: canvas.Canvas) -> None:
    kit.chrome(c, 1)
    kit.draw_img(c, "jellyfish.png", kit.CX, kit.PAGE_H / 2 + 168, h=148, center=True)
    kit.draw_img(c, "wordmark.png", kit.CX, kit.PAGE_H / 2 + 42, w=236, center=True)
    c.setFillColor(kit.INK)
    c.setFont("InterDisplay-Bold", 28)
    c.drawCentredString(kit.CX, kit.PAGE_H / 2 - 48, "Event Proposal")
    c.setFont("JetBrains-Bold", 11)
    c.setFillColor(kit.WINE)
    c.drawCentredString(kit.CX, kit.PAGE_H / 2 - 72, "Template  ·  Fall 2026")
    c.setFillColor(kit.SLATE)
    c.setFont("Inter-Italic", 11)
    c.drawCentredString(kit.CX, kit.PAGE_H / 2 - 96, copy.PILLARS)
    kit.draw_img(c, "tagline.png", kit.CX, kit.PAGE_H / 2 - 148, w=220, center=True)
    kit.badge_row(
        c,
        ["workshop", "live-lab", "halt-restart", "clubs-expo"],
        138,
        h=15,
        gap=8,
    )
    c.setFillColor(kit.SLATE)
    c.setFont("Inter", 8)
    c.drawCentredString(
        kit.CX,
        116,
        "Saitsa Clubs Portal  ·  portal.hellorubric.com",
    )
    signature_line(c, y=82)


def page_overview(c: canvas.Canvas) -> None:
    kit.chrome(c, 2, icon="ticket", badges=["workshop", "live-lab"])
    y = kit.draw_title(c, "[EVENT NAME] Overview", kit.CONTENT_TOP, size=22) - 4
    y = labeled_box(
        c,
        "Description",
        "[Brief description of the event here]",
        y,
        height=110,
    )
    y = labeled_box(c, "Time and Date", "[DAY, DATE  ·  START–END]", y, height=48)
    y = labeled_box(
        c,
        "Proposed Location",
        "Preferred room? Indoor/Outdoor? Offsite? SECC books campus rooms.",
        y,
        height=56,
    )
    y = labeled_box(
        c,
        "Expected Attendance",
        "5–10?  20?  50?  100?  10000000????",
        y,
        height=48,
    )
    signature_line(c)


def page_agenda(c: canvas.Canvas) -> None:
    kit.chrome(c, 3, icon="workflow", badges=["workshop"])
    y = kit.draw_title(c, "Agenda", kit.CONTENT_TOP, size=22) - 6
    c.setFillColor(kit.SLATE)
    c.setFont("Inter-Italic", 9.5)
    note = (
        "Include the important segments. Estimate if you cannot give exact times."
    )
    c.drawCentredString(kit.CX, y, note)
    y -= 20
    dur_w = 110
    seg_w = kit.CONTENT_W - dur_w
    rows = [
        (
            [
                "[DURATION]",
                "[SEGMENT — e.g. welcome, club presentation, member sign-ups]",
            ],
            "blank",
        ),
        (["[DURATION]", "[SEGMENT — topic, format]"], "blank"),
        (["[DURATION]", "[SEGMENT — topic, format]"], "blank"),
        (["[DURATION]", "[SEGMENT — topic, format]"], "blank"),
        (
            ["[DURATION]", "[SEGMENT — e.g. Q&A and open discussion]"],
            "blank",
        ),
        (["[DURATION]", "[SEGMENT]"], "blank"),
    ]
    draw_table(
        c,
        y,
        ["Duration", "Segment"],
        [dur_w, seg_w],
        rows,
        min_row_h=36,
    )
    signature_line(c)


def page_objectives(c: canvas.Canvas) -> None:
    kit.chrome(c, 4, icon="spark", badges=["workshop"])
    y = kit.draw_title(c, "Objectives", kit.CONTENT_TOP, size=22) - 2
    c.setFillColor(kit.SLATE)
    c.setFont("Inter-Italic", 9.5)
    c.drawCentredString(
        kit.CX,
        y,
        "What this event is for. Tie at least one objective to a club foundation.",
    )
    y -= 22
    prompts = [
        "[OBJECTIVE 1 — e.g. what students will learn or experience]",
        "[OBJECTIVE 2 — e.g. hands-on practice for every attendee]",
        "[OBJECTIVE 3 — e.g. recruit new club members]",
        "[OBJECTIVE 4 — e.g. promote a foundation (untapped / workflow / human finish) and feed the pipeline of future events]",
    ]
    box_h = 78
    for i, prompt in enumerate(prompts, start=1):
        bottom = y - box_h
        c.setFillColor(white)
        c.setStrokeColor(kit.RULE)
        c.setLineWidth(0.8)
        c.roundRect(kit.MARGIN_X, bottom, kit.CONTENT_W, box_h, 10, fill=1, stroke=1)
        c.setFillColor(kit.LIME if i % 2 else kit.PINK)
        c.circle(kit.MARGIN_X + 22, y - 22, 10, fill=1, stroke=0)
        c.setFillColor(kit.INK)
        c.setFont("JetBrains-Bold", 10)
        c.drawCentredString(kit.MARGIN_X + 22, y - 25, str(i))
        text_x = kit.MARGIN_X + 42
        text_w = kit.CONTENT_W - 56
        c.setFillColor(kit.SLATE)
        c.setFont("Inter-Italic", 10)
        ty = y - 26
        for line in kit.wrap(prompt, "Inter-Italic", 10, text_w):
            c.drawString(text_x, ty, line)
            ty -= 14
        y = bottom - 14
    signature_line(c)


def page_budget(c: canvas.Canvas) -> None:
    kit.chrome(c, 5, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Requested Supplies and Budgeting", kit.CONTENT_TOP, size=18)
    y -= 2
    c.setFillColor(kit.INK)
    c.setFont("Inter", 10)
    intro = (
        "List every supply, including promotional materials. Built-in costs "
        f"of ${PRINTING_COST:.0f} printing ({POSTER_QTY} posters + {NAMETAG_QTY} name tags) "
        f"and ${MISC_COST:.0f} misc are already on the table — add anything "
        "else this event needs and update the total."
    )
    for line in kit.wrap(intro, "Inter", 10, kit.CONTENT_W):
        c.drawString(kit.MARGIN_X, y, line)
        y -= 14
    y -= 6
    c.setFillColor(kit.LIME)
    c.roundRect(kit.MARGIN_X, y - 22, kit.CONTENT_W, 28, 6, fill=1, stroke=0)
    c.setFillColor(kit.INK)
    c.setFont("Inter-Bold", 9.5)
    c.drawCentredString(kit.CX, y - 12, "Attach quotes for all purchases.")
    y -= 40

    item_w = 128
    cost_w = 80
    detail_w = kit.CONTENT_W - item_w - cost_w
    rows = [
        (
            [
                "Printing expenses",
                PRINTING_DETAILS,
                money(PRINTING_COST),
            ],
            "builtin",
        ),
        (
            [
                "Misc",
                "Tape, markers, unexpected small costs",
                money(MISC_COST),
            ],
            "builtin",
        ),
        (["[ITEM]", "[DETAILS]", "[COST]"], "blank"),
        (["[ITEM]", "[DETAILS]", "[COST]"], "blank"),
        (["[ITEM]", "[DETAILS]", "[COST]"], "blank"),
        (
            [
                "TOTAL",
                "Built-in floor. Add event-specific items above and update this total.",
                money(BUILT_IN_TOTAL),
            ],
            "total",
        ),
    ]
    y = draw_table(
        c,
        y,
        ["Item", "Details", "Estimated cost"],
        [item_w, detail_w, cost_w],
        rows,
        aligns=["left", "left", "right"],
        min_row_h=32,
    )
    y -= 16
    c.setFillColor(kit.SLATE)
    c.setFont("Inter-Italic", 9)
    notes = [
        f"Lime rows are built into every proposal (${PRINTING_COST:.0f} printing + ${MISC_COST:.0f} misc = ${BUILT_IN_TOTAL:.0f}). Do not delete them.",
        "Funding: Saitsa Clubs Grant or start-up reimbursement. Do not spend before approval.",
        "Eligible spend only — no alcohol, no gifts for members, swag capped where the handbook says.",
    ]
    for note in notes:
        y = kit.bullet_item(c, note, kit.MARGIN_X, y, level=0)
        y -= 2
    signature_line(c)


def page_logistics(c: canvas.Canvas) -> None:
    kit.chrome(c, 6, icon="halt", badges=["workshop", "live-lab"])
    y = kit.draw_title(c, "Logistics, Risk & Compliance", kit.CONTENT_TOP, size=20) - 4
    for text in [
        "Room booking coordinated exclusively by the SECC — no direct booking by the club.",
        "[RISK LEVEL — e.g. low-risk: on campus, indoor, no alcohol, no physical activity]",
        "If refreshments are served: food and beverages ordered through SAIT’s approved catering vendor only, arranged via the SECC.",
        "A/V equipment (if any) picked up from SECC and returned [WHEN — e.g. the same evening].",
        "Primary Event Organizer (PEO) will be present for the full duration of the event and will manage risk.",
        "Attendance list will be kept for the event report.",
        f"Printing expenses (${PRINTING_COST:.0f}): {POSTER_QTY} tabloid 11×17 posters (${POSTER_COST:.0f}) and {NAMETAG_QTY} name tags (${NAMETAG_COST:.0f}). Posters: Saitsa Clubs logo unaltered, submitted via saitsa.com/Poster-Submission before posting.",
        "Posters removed by the club within 48 hours after the event.",
    ]:
        y = kit.bullet_item(c, text, kit.MARGIN_X, y, level=0)

    y -= 10
    c.setFillColor(kit.INK)
    c.setFont("InterDisplay-Bold", 18)
    c.drawCentredString(kit.CX, y, "Promotion Plan")
    y -= 20
    for text in [
        "Posters on Saitsa General Poster Boards (approved submission first).",
        "Announcements in club channels and student groups.",
        "Promotion at [CLUBS EVENT — e.g. Clubs Fall Showcase] if the event is scheduled after it.",
        "Word of mouth in classes; open to all SAIT students to maximize reach.",
    ]:
        y = kit.bullet_item(c, text, kit.MARGIN_X, y, level=0)

    kit.draw_img(
        c,
        "saitsa-clubs.png",
        kit.PAGE_W - kit.MARGIN_X - 46,
        140,
        w=90,
        center=True,
    )
    signature_line(c)


def build() -> Path:
    if not (CHARTER / "assets" / "revamp" / "header.png").exists():
        export_kit()
    kit.register_fonts()
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("Unnatural Intelligence Event Proposal Template")
    c.setAuthor("Unnatural Intelligence")
    c.setSubject("Saitsa student club event proposal — Fall 2026")

    pages = [
        page_cover,
        page_overview,
        page_agenda,
        page_objectives,
        page_budget,
        page_logistics,
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
