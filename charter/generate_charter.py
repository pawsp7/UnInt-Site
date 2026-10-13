#!/usr/bin/env python3
"""Generate the Unnatural Intelligence Club Charter PDF.

Visual structure follows the UXIcorns Club Charter (A4, branded header,
section dividers, role pages, event concepts, style guide).
"""

from __future__ import annotations

import math
from pathlib import Path

from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
FONTS = ROOT / "fonts"
OUTPUT = ROOT / "Unnatural_Intelligence_Club_Charter.pdf"

# Brand — distinct from UXIcorns cyan/pink/yellow, still a student-club palette.
TEAL = HexColor("#1A7A84")
TEAL_DEEP = HexColor("#145F67")
MINT = HexColor("#8EE3D8")
VIOLET = HexColor("#7B61FF")
LAVENDER = HexColor("#C4B8FF")
CORAL = HexColor("#FF6B4A")
GOLD = HexColor("#F4C430")
CHARCOAL = HexColor("#3D3D3D")
SLATE = HexColor("#5A5A5A")
RULE = HexColor("#D9D9D9")
LIGHT = HexColor("#EAEAEA")
INK = HexColor("#1A1A1A")

PAGE_W, PAGE_H = A4
CX = PAGE_W / 2
MARGIN_X = 58
CONTENT_W = PAGE_W - 2 * MARGIN_X


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


def draw_spark(c: canvas.Canvas, x: float, y: float, size: float = 8) -> None:
    """Four-point spark used as the club mark (stand-in for the UXIcorns horn)."""
    colors = (CORAL, GOLD, VIOLET, MINT)
    c.saveState()
    c.translate(x, y)
    for i, col in enumerate(colors):
        c.saveState()
        c.rotate(i * 45)
        p = c.beginPath()
        p.moveTo(0, size)
        p.lineTo(size * 0.18, size * 0.18)
        p.lineTo(0, 0)
        p.lineTo(-size * 0.18, size * 0.18)
        p.close()
        c.setFillColor(col)
        c.drawPath(p, fill=1, stroke=0)
        c.restoreState()
    c.setFillColor(white)
    c.circle(0, 0, size * 0.16, fill=1, stroke=0)
    c.restoreState()


def draw_wordmark(c: canvas.Canvas, x: float, y: float, size: float = 26) -> None:
    font = "InterDisplay-Bold"
    c.setFillColor(TEAL)
    c.setFont(font, size)
    c.drawCentredString(x, y, "ui")
    # Spark replaces the tittle of the i (to the right of centre).
    u_w = pdfmetrics.stringWidth("u", font, size)
    i_w = pdfmetrics.stringWidth("i", font, size)
    spark_x = x + u_w / 2.0
    spark_y = y + size * 0.82
    c.setFillColor(white)
    c.circle(spark_x, y + size * 0.72, max(i_w * 0.28, 1.6), fill=1, stroke=0)
    draw_spark(c, spark_x, spark_y, size=size * 0.28)


def wave_path(c: canvas.Canvas, y: float, amp: float, phase: float, left: float, right: float):
    p = c.beginPath()
    first = True
    x = left
    while x <= right + 0.5:
        yy = y + math.sin((x * 0.042) + phase) * amp
        if first:
            p.moveTo(x, yy)
            first = False
        else:
            p.lineTo(x, yy)
        x += 2
    return p


def draw_header_waves(c: canvas.Canvas) -> None:
    """Three wavy bands flanking the wordmark — same device as UXIcorns."""
    gap = 34
    left_end = CX - gap
    right_start = CX + gap
    bands = (
        (MINT, 18.0, 0.0, 4.4),
        (VIOLET, 14.5, 0.9, 3.6),
        (CORAL, 11.0, 1.7, 3.2),
    )
    y_base = PAGE_H - 36
    c.setLineCap(1)
    c.setLineJoin(1)
    for col, amp, phase, weight in bands:
        c.setStrokeColor(col)
        c.setLineWidth(weight)
        c.drawPath(wave_path(c, y_base, amp, phase, 18, left_end))
        c.drawPath(wave_path(c, y_base, amp, phase + 0.4, right_start, PAGE_W - 18))
    draw_wordmark(c, CX, PAGE_H - 46, size=24)


def draw_mascot(c: canvas.Canvas, x: float, y: float, size: float = 16) -> None:
    c.saveState()
    c.setFillColor(TEAL)
    c.roundRect(x - size / 2, y - size / 2, size, size, size * 0.32, fill=1, stroke=0)
    # Eyes
    c.setFillColor(white)
    eye_w, eye_h = size * 0.16, size * 0.34
    c.roundRect(x - size * 0.28, y - size * 0.06, eye_w, eye_h, 1.4, fill=1, stroke=0)
    c.roundRect(x + size * 0.10, y - size * 0.06, eye_w, eye_h, 1.4, fill=1, stroke=0)
    draw_spark(c, x + size * 0.18, y + size * 0.62, size=size * 0.42)
    c.restoreState()


def draw_footer(c: canvas.Canvas, page: int) -> None:
    c.setFillColor(TEAL)
    c.setFont("Inter-Bold", 13)
    c.drawCentredString(CX, 38, str(page))
    draw_mascot(c, CX, 20, size=14)


def draw_header(c: canvas.Canvas, page: int) -> None:
    draw_header_waves(c)
    draw_footer(c, page)


def wrap(text: str, font: str, size: float, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
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


def draw_title(c: canvas.Canvas, text: str, y: float, size: float = 26) -> float:
    c.setFillColor(INK)
    c.setFont("Inter-Bold", size)
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
    """Draw a nested bullet. Returns the y position under the last line."""
    marks = [
        ("filled", 3.1),
        ("open", 2.6),
        ("square", 2.2),
        ("dot", 1.6),
    ]
    style, r = marks[min(level, 3)]
    indent = x + level * 16
    max_w = (width or (PAGE_W - MARGIN_X - indent - 8)) - 12
    font = "Inter-Bold" if bold else "Inter"
    size = 10.2 if level == 0 else 9.6
    leading = 14.2 if level == 0 else 13.2
    lines = wrap(text, font, size, max_w)
    cy = y + 2.4
    c.setFillColor(INK)
    c.setStrokeColor(INK)
    if style == "filled":
        c.circle(indent, cy, r, fill=1, stroke=0)
    elif style == "open":
        c.setLineWidth(0.9)
        c.circle(indent, cy, r, fill=0, stroke=1)
    elif style == "square":
        c.rect(indent - r, cy - r, r * 2, r * 2, fill=1, stroke=0)
    else:
        c.circle(indent, cy, r, fill=1, stroke=0)
    c.setFont(font, size)
    tx = indent + 10
    for i, line in enumerate(lines):
        c.drawString(tx, y - i * leading, line)
    return y - (len(lines) - 1) * leading - (16 if level == 0 else 13.5)


def section_block(c: canvas.Canvas, heading: str, body: str, y: float) -> float:
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 12.5)
    c.drawString(MARGIN_X, y, heading)
    y -= 18
    c.setFont("Inter", 11)
    for line in wrap(body, "Inter", 11, CONTENT_W):
        c.drawString(MARGIN_X, y, line)
        y -= 15
    y -= 8
    hrule(c, y + 6)
    return y - 16


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


def page_cover(c: canvas.Canvas) -> None:
    draw_header(c, 1)
    c.setFillColor(INK)
    c.setFont("InterDisplay-Bold", 36)
    c.drawCentredString(CX, PAGE_H / 2 + 48, "Unnatural Intelligence")
    c.setFont("Inter-Bold", 26)
    c.drawCentredString(CX, PAGE_H / 2 + 8, "Club Charter")
    c.setFont("Inter", 14)
    c.drawCentredString(CX, PAGE_H / 2 - 32, "August 2026")
    c.setFillColor(SLATE)
    c.setFont("Inter-Italic", 11)
    c.drawCentredString(CX, PAGE_H / 2 - 72, "Untapped  ·  Integrated  ·  Human")


def page_toc(c: canvas.Canvas) -> None:
    draw_header(c, 2)
    entries = [
        ("Unnatural Intelligence Club Charter", "1", True, 0),
        ("Mission Statement", "3", True, 0),
        ("The Basis", "4", True, 0),
        ("Goals", "5", True, 0),
        ("1. Pursue Untapped Potential", "5", False, 1),
        ("2. Integrate AI into Daily & Professional Workflows", "5", False, 1),
        ("3. Optimize Tokens, Keep the Human", "5", False, 1),
        ("4. Cross-Program Workflow Sharing", "5", False, 1),
        ("5. A Community of Practice, Not a Tool Fan Club", "5", False, 1),
        ("6. Lower Barriers to Participation", "6", False, 1),
        ("7. Leadership Development", "6", False, 1),
        ("8. Experiment Without Waste", "6", False, 1),
        ("9. Integrity, Voice, and Human Accountability", "6", False, 1),
        ("10. Strengthen Unnatural Intelligence’s Presence on Campus", "6", False, 1),
        ("Executive Roles & Responsibilities", "7", True, 0),
        ("Directors", "8", False, 1),
        ("President — Strategic Lead & Club Coordinator", "8", False, 2),
        ("Vice-President Operations — Operations & Visionary", "8", False, 2),
        ("Vice-President Finance — Budgeting & Funding", "9", False, 2),
        ("Marketing", "10", False, 1),
        ("Social Media Lead — Communication & Engagement", "10", False, 2),
        ("Graphic Designer — Visual Identity & Creative Production", "11", False, 2),
        ("Events", "12", False, 1),
        ("Events Coordinator — Planning & Execution", "12", False, 2),
        ("Outreach & Networking — External Communication", "12", False, 2),
        ("Event Concepts", "13", True, 0),
        ("Untapped Potential", "14", False, 1),
        ("Workflow Integration", "14", False, 1),
        ("Token Craft & Human Touch", "15", False, 1),
        ("Mixer events", "15", False, 1),
        ("Unnatural Intelligence Style Guide", "16", True, 0),
    ]
    y = PAGE_H - 92
    c.setFillColor(INK)
    for title, num, bold, level in entries:
        font = "Inter-Bold" if bold else "Inter"
        size = 10.4 if bold else 9.4
        x = MARGIN_X + level * 16
        c.setFont(font, size)
        c.setFillColor(INK)
        c.drawString(x, y, title)
        c.setFillColor(SLATE)
        c.setFont("Inter", size)
        c.drawRightString(PAGE_W - MARGIN_X, y, num)
        y -= 16.4 if bold else 14.6


def page_mission(c: canvas.Canvas) -> None:
    draw_header(c, 3)
    draw_title(c, "Mission Statement", PAGE_H / 2 + 88, size=24)
    quote = (
        "Pursue the untapped potential of AI. "
        "Explore integrating AI into our daily and professional workflows. "
        "Optimize token usage while still retaining that touch of humanity."
    )
    c.setFillColor(INK)
    c.setFont("Inter-Italic", 13.5)
    y = PAGE_H / 2 + 22
    for line in wrap(f"“{quote}”", "Inter-Italic", 13.5, CONTENT_W - 16):
        c.drawCentredString(CX, y, line)
        y -= 22
    y -= 18
    c.setFillColor(SLATE)
    c.setFont("Inter", 10)
    pillars = [
        "Untapped potential",
        "Daily & professional workflows",
        "Lean tokens, human finish",
    ]
    label = "  ·  ".join(pillars)
    c.drawCentredString(CX, y, label)


def page_basis(c: canvas.Canvas) -> None:
    draw_header(c, 4)
    y = draw_title(c, "The Basis", PAGE_H - 92, size=24) - 8
    blocks = [
        (
            "1. Pursue the untapped potential of AI",
            "Most students only meet the default chatbot. The interesting work is "
            "off to the side: multimodal shop-floor photos, syllabus-to-study-plan "
            "systems, custom assistants for one recurring task, uses nobody assigned "
            "in class. We go looking for those.",
        ),
        (
            "2. Integrate AI into daily and professional workflows",
            "A demo is not a habit. We treat AI as something you fold into Tuesday — "
            "class, practicum, job search, client email, shop estimates — then keep "
            "only the pieces that actually save time.",
        ),
        (
            "3. Optimize tokens, keep the human",
            "Wasteful prompts are sloppy thinking. We practice getting the same "
            "(or better) result with less context, then putting a human finish on "
            "whatever comes back so it still sounds like a person, not a template.",
        ),
        (
            "4. A polytechnic is the right place for this",
            "SAIT workflows are not generic. Construction, health, energy, business, "
            "media, and ICT each hide different unused potential. The club exists so "
            "those workflows can be compared in one room.",
        ),
        (
            "5. Built to exist as a Saitsa club",
            "Open membership, student-led, non-profit, three signing executives, "
            "registered through the Saitsa Clubs Portal. That structure is how we "
            "book rooms, apply for grants, and operate officially on campus.",
        ),
    ]
    for heading, body in blocks:
        y = section_block(c, heading, body, y)


def page_goals_a(c: canvas.Canvas) -> None:
    draw_header(c, 5)
    y = draw_title(c, "Goals", PAGE_H - 92, size=24) - 6
    blocks = [
        (
            "1. Pursue Untapped Potential",
            "Look past the default chatbot. Find uses, tools, and questions that "
            "students and workplaces have not worn out yet.",
        ),
        (
            "2. Integrate AI into Daily & Professional Workflows",
            "Move from one-off demos to habits: class, practicum, job search, "
            "and the work of each SAIT program.",
        ),
        (
            "3. Optimize Tokens, Keep the Human",
            "Spend fewer tokens for a better result, then edit until the work still "
            "sounds like a person — with judgment, taste, and a name on it.",
        ),
        (
            "4. Cross-Program Workflow Sharing",
            "A construction estimate, a lab write-up, and a client email are different "
            "jobs. Bring them into the same room so unused potential travels.",
        ),
        (
            "5. A Community of Practice, Not a Tool Fan Club",
            "Share the workflows people actually keep. Critique the ones that waste "
            "tokens or flatten a human voice.",
        ),
    ]
    for heading, body in blocks:
        y = section_block(c, heading, body, y)


def page_goals_b(c: canvas.Canvas) -> None:
    draw_header(c, 6)
    y = PAGE_H - 100
    blocks = [
        (
            "6. Lower Barriers to Participation",
            "Make joining easy. You do not need a computer-science background, a paid "
            "model, or a finished prompt library to walk in.",
        ),
        (
            "7. Leadership Development",
            "Run the club the way we want people to run AI: lean, documented, and "
            "human. Meetings, budgets, events, and conflict — under Saitsa’s framework.",
        ),
        (
            "8. Experiment Without Waste",
            "Try the weird idea. Kill the prompt that burns tokens for nothing. "
            "Curiosity is encouraged; sloppy generation is not the culture.",
        ),
        (
            "9. Integrity, Voice, and Human Accountability",
            "Keep academic honesty and a recognizable human voice. If you could not "
            "stand behind the output without the model, it is not finished.",
        ),
        (
            "10. Strengthen Unnatural Intelligence’s Presence on Campus",
            "Be the SAIT club known for unused potential, real workflows, and work "
            "that still sounds like a person.",
        ),
    ]
    for heading, body in blocks:
        y = section_block(c, heading, body, y)


def page_exec_divider(c: canvas.Canvas) -> None:
    draw_header(c, 7)
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 28)
    c.drawCentredString(CX, PAGE_H / 2 + 12, "Executive Roles &")
    c.drawCentredString(CX, PAGE_H / 2 - 24, "Responsibilities")


def page_directors(c: canvas.Canvas) -> None:
    draw_header(c, 8)
    y = PAGE_H - 88
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 22)
    c.drawString(MARGIN_X, y, "Directors")
    y -= 28

    c.setFont("Inter-Bold", 12)
    c.drawString(MARGIN_X, y, "President — Strategic Lead & Club Coordinator")
    y -= 16
    c.setFont("Inter-Bold", 10)
    c.drawString(MARGIN_X, y, "Core Purpose:")
    c.setFont("Inter", 10)
    c.drawString(MARGIN_X + 78, y, "Keep the club organized, aligned, and progressing forward.")
    y -= 16
    c.setFont("Inter-Bold", 10)
    c.drawString(MARGIN_X, y, "Responsibilities:")
    y -= 16
    for item in [
        ("Hold veto power for decisions affecting club direction or budget.", 0),
        ("Set semester direction, themes, and goals around the three foundations.", 0),
        ("Arrange and lead executive meetings.", 0),
        ("Prepare agendas.", 1),
        ("Follow up with other execs on tasks.", 0),
        ("Track deadlines.", 1),
        ("Book rooms and manage logistics.", 0),
        ("Monitor club email, Teams, Rubric, and official communication channels.", 0),
        ("Navigate communication between execs during conflict.", 0),
        ("Represent Unnatural Intelligence externally, including with Saitsa.", 0),
        ("Ensure the three Saitsa signing authorities remain filled.", 0),
    ]:
        y = bullet_item(c, item[0], MARGIN_X, y, level=item[1])

    y -= 6
    c.setFont("Inter-Bold", 12)
    c.setFillColor(INK)
    c.drawString(MARGIN_X, y, "Vice-President Operations — Operations & Visionary")
    y -= 16
    c.setFont("Inter-Bold", 10)
    c.drawString(MARGIN_X, y, "Core Purpose:")
    c.setFont("Inter", 10)
    purpose = "Aid overall direction and maintain operations in the absence of the president."
    c.drawString(MARGIN_X + 78, y, purpose)
    y -= 16
    c.setFont("Inter-Bold", 10)
    c.drawString(MARGIN_X, y, "Responsibilities:")
    y -= 16
    for item in [
        ("Serve as secondary decision-maker when the president is unavailable.", 0),
        ("Maintain direction of the club throughout the semester.", 0),
        ("Keep activity tied to the three foundations.", 1),
        ("Record meeting minutes.", 0),
        ("Assist the president with booking rooms and managing logistics.", 0),
        ("Maintain organization of documents.", 0),
        ("Event plans", 1),
        ("Budgets and grant paperwork", 1),
        ("Saitsa forms, Rubric submissions, and transition notes", 1),
        ("Help onboard new execs.", 0),
        ("Monitor club email, Teams, Rubric, and official communication channels.", 0),
        ("Navigate communication between execs during conflict.", 0),
        ("Represent Unnatural Intelligence externally.", 0),
    ]:
        y = bullet_item(c, item[0], MARGIN_X, y, level=item[1])


def page_finance(c: canvas.Canvas) -> None:
    draw_header(c, 9)
    y = PAGE_H - 88
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 22)
    c.drawString(MARGIN_X, y, "Directors")
    y -= 28
    c.setFont("Inter-Bold", 12)
    c.drawString(MARGIN_X, y, "Vice-President Finance — Budgeting & Funding")
    y -= 18
    c.setFont("Inter-Bold", 10.5)
    c.drawString(MARGIN_X, y, "Core Purpose:")
    c.setFont("Inter", 10.5)
    c.drawString(MARGIN_X + 82, y, "Manage club finances responsibly and transparently.")
    y -= 20
    c.setFont("Inter-Bold", 10.5)
    c.drawString(MARGIN_X, y, "Responsibilities:")
    y -= 18
    for item in [
        ("Prepare semester budget forecasts.", 0),
        ("Track overall expenses and maintain a ledger.", 0),
        ("Manage the Saitsa-issued club bank account.", 1),
        ("Keep receipts for the full club year for possible audit.", 1),
        ("Coordinate budgets with Events Coordinators.", 0),
        ("Take vision from an event and budget it out.", 1),
        ("Submit quotes and grant applications for events.", 1),
        ("Apply for new-club start-up reimbursement (up to $500) and term grants.", 0),
        ("Spend like we prompt: enough to do the work, nothing extra.", 0),
        ("Ensure purchases follow Saitsa and SAIT guidelines.", 0),
        ("Inform the SECC of any external monetary sponsorship.", 0),
        ("Reimburse members from the club account after approved spend.", 0),
    ]:
        y = bullet_item(c, item[0], MARGIN_X, y, level=item[1])

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
        y -= 13


def page_social(c: canvas.Canvas) -> None:
    draw_header(c, 10)
    y = PAGE_H - 88
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 22)
    c.drawString(MARGIN_X, y, "Marketing")
    y -= 26
    c.setFont("Inter-Bold", 12)
    c.drawString(MARGIN_X, y, "Social Media Lead (1–3 positions) — Communication & Engagement")
    y -= 16
    c.setFont("Inter-Bold", 10)
    c.drawString(MARGIN_X, y, "Core Purpose:")
    c.setFont("Inter", 10)
    c.drawString(MARGIN_X + 78, y, "Maintain active, engaging communication across platforms.")
    y -= 16
    c.setFont("Inter-Bold", 10)
    c.drawString(MARGIN_X, y, "Responsibilities:")
    y -= 16
    items = [
        ("Manage socials through regular, consistent posting and active replies.", 0, False),
        ("Instagram", 1, False),
        ("Discord", 1, False),
        ("Teams", 1, False),
        ("Rubric / Saitsa Clubs Portal", 1, False),
        ("LinkedIn", 1, False),
        ("Independently create:", 0, False),
        ("Captions", 1, False),
        ("Announcements", 1, False),
        ("Event recaps", 1, False),
        ("Instagram stories", 1, False),
        ("Engagement", 1, False),
        ("Posts", 2, False),
        ("Virtual events / activities", 2, False),
        ("And more…", 1, False),
        ("In collaboration with Graphic Designers create:", 0, False),
        ("General promotion", 1, False),
        ("In collaboration with Graphic Designers and Event Coordination create:", 0, False),
        ("Event promotion", 1, False),
        ("Track and optimize engagement metrics.", 0, False),
        ("Ensure consistent branding and a human club voice — no unedited AI captions.", 0, False),
        ("Publish lean-prompt tips, unused-use finds, and human-finish before/afters.", 0, False),
    ]
    for text, level, bold in items:
        y = bullet_item(c, text, MARGIN_X, y, level=level, bold=bold)


def page_designer(c: canvas.Canvas) -> None:
    draw_header(c, 11)
    y = PAGE_H - 88
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 22)
    c.drawString(MARGIN_X, y, "Marketing")
    y -= 26
    c.setFont("Inter-Bold", 12)
    title = "Graphic Designer (1–2 positions) — Visual Identity & Creative Production"
    for line in wrap(title, "Inter-Bold", 12, CONTENT_W):
        c.drawString(MARGIN_X, y, line)
        y -= 16
    y -= 2
    c.setFont("Inter-Bold", 10)
    c.drawString(MARGIN_X, y, "Core Purpose:")
    c.setFont("Inter", 10)
    c.drawString(MARGIN_X + 78, y, "Shape the club’s visual identity and produce design assets.")
    y -= 16
    c.setFont("Inter-Bold", 10)
    c.drawString(MARGIN_X, y, "Responsibilities:")
    y -= 16
    items = [
        ("Design graphics for social media and any general or event-specific promotional material.", 0),
        ("Create templates for recurring content.", 0),
        ("Social media posts", 1),
        ("Posters (tabloid 11×17 for Saitsa boards, with the Saitsa Clubs logo)", 1),
        ("Presentations", 1),
        ("And more…", 1),
        ("In collaboration with Social Media Leads create:", 0),
        ("General promotion", 1),
        ("In collaboration with Social Media Leads and Event Coordination create:", 0),
        ("Event promotion", 1),
        ("Ensure consistent and distinct branding.", 0),
        ("Expand upon branding", 1),
        ("Test and experiment with designs", 2),
        ("AI may sketch; a human always finishes what gets published.", 0),
        ("Do not use the official SAIT logo on club materials — student groups are not permitted to.", 0),
    ]
    for text, level in items:
        y = bullet_item(c, text, MARGIN_X, y, level=level)


def page_events_roles(c: canvas.Canvas) -> None:
    draw_header(c, 12)
    y = PAGE_H - 88
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 22)
    c.drawString(MARGIN_X, y, "Events")
    y -= 26
    c.setFont("Inter-Bold", 12)
    c.drawString(MARGIN_X, y, "Events Coordinator (2 positions) — Planning & Execution")
    y -= 15
    c.setFont("Inter-Bold", 10)
    c.drawString(MARGIN_X, y, "Core Purpose:")
    c.setFont("Inter", 10)
    c.drawString(MARGIN_X + 78, y, "Plan and deliver high-quality events.")
    y -= 15
    c.setFont("Inter-Bold", 10)
    c.drawString(MARGIN_X, y, "Responsibilities:")
    y -= 14
    for item in [
        ("Brainstorm and propose event ideas, including the:", 0),
        ("Agenda", 1),
        ("Which foundation it serves (untapped, workflow, or human/token)", 1),
        ("Necessary materials", 1),
        ("Setup coordination", 1),
        ("Coordinate with Finance on event budgets.", 0),
        ("Coordinate with Marketing for promotional materials.", 0),
        ("Collaborate with Outreach to secure speakers.", 0),
        ("Submit event proposals through the Saitsa Clubs Portal before promoting.", 0),
        ("Follow up with Marketing on event tasks.", 0),
        ("Manage event logistics and oversee execution.", 0),
        ("Collect and compile feedback for future improvements.", 0),
    ]:
        y = bullet_item(c, item[0], MARGIN_X, y, level=item[1])

    y -= 4
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 12)
    c.drawString(MARGIN_X, y, "Outreach & Networking — External Communication")
    y -= 15
    c.setFont("Inter-Bold", 10)
    c.drawString(MARGIN_X, y, "Core Purpose:")
    c.setFont("Inter", 10)
    c.drawString(MARGIN_X + 78, y, "Connect the club with speakers, partners, and opportunities.")
    y -= 15
    c.setFont("Inter-Bold", 10)
    c.drawString(MARGIN_X, y, "Responsibilities:")
    y -= 14
    for item in [
        ("Reach out to potential speakers, collaborators, or partnerships.", 0),
        ("Draft outreach messages", 1),
        ("Negotiate presentation details", 1),
        ("Maintain a contact list.", 0),
        ("Identify collaboration opportunities on campus and in Calgary industry.", 0),
        ("Find people whose real workflows still have unused AI potential.", 1),
        ("Coordinate with Events Coordinators to plan and arrange guests.", 0),
        ("In collaboration with Social Media Leads, manage LinkedIn connections.", 0),
        ("Represent Unnatural Intelligence externally.", 0),
        ("Help identify a faculty advisor (encouraged; required if registered as academic).", 0),
    ]:
        y = bullet_item(c, item[0], MARGIN_X, y, level=item[1])


def page_events_divider(c: canvas.Canvas) -> None:
    draw_header(c, 13)
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 28)
    c.drawCentredString(CX, PAGE_H / 2, "Event Concepts")


def page_events_a(c: canvas.Canvas) -> None:
    draw_header(c, 14)
    y = PAGE_H - 92
    y = bullet_item(
        c,
        "Untapped Potential — find what default chat never gets asked.",
        MARGIN_X,
        y,
        level=0,
        bold=True,
    )
    for text, level in [
        ("“What’s this button for?” nights: one tool, the features nobody opens.", 1),
        ("Multimodal labs: a shop-floor photo, a schematic, a messy syllabus, a voice note.", 1),
        ("Build a tiny assistant for one recurring student task — then delete it if it is not used.", 1),
        ("Cross-program “I didn’t know it could do that” demos.", 1),
        ("Estimating, spec-checking, and photo-to-takeoff for construction and energy", 2),
        ("Charting, patient-education drafts, and protocol lookup for health", 2),
        ("Campaign research, spreadsheet cleanup, and client-ready copy for business", 2),
        ("Accessibility, translation, and study systems as unused campus uses.", 1),
        ("Failed-experiment night: the prompt that looked clever and did nothing.", 1),
    ]:
        y = bullet_item(c, text, MARGIN_X, y, level=level)

    y -= 4
    y = bullet_item(
        c,
        "Workflow Integration — from demo to a Tuesday you would actually keep.",
        MARGIN_X,
        y,
        level=0,
        bold=True,
    )
    for text, level in [
        ("Bring Your Tuesday: rebuild a real day (class, shift, job hunt) with AI in the loop.", 1),
        ("Syllabus to system: one course, one stack, one week of use.", 1),
        ("Professional pack: meeting notes, email, portfolios, interview drills.", 1),
        ("Two-week Daily Driver challenge: keep only the workflow you still open on day 14.", 1),
        ("Workflow swap: pair with a student from another program and steal one habit.", 1),
        ("Open studio (Prompt Playgrounds) for unfinished, in-progress work.", 1),
        ("Student-led: host a session on the workflow you actually use, not a tool tour.", 1),
        ("End of semester Daily Driver showcase — the habit that survived, not the flashiest demo.", 1),
    ]:
        y = bullet_item(c, text, MARGIN_X, y, level=level)


def page_events_b(c: canvas.Canvas) -> None:
    draw_header(c, 15)
    y = PAGE_H - 92
    y = bullet_item(
        c,
        "Token Craft & Human Touch — less spend, more of you in the result.",
        MARGIN_X,
        y,
        level=0,
        bold=True,
    )
    for text, level in [
        ("Token Diet: same outcome, fewer tokens. Publish the before/after prompt.", 1),
        ("Human Finish Studio: take a generic draft and edit until it sounds like you.", 1),
        ("“Don’t send that” clinic: catch the telltale AI voice before it hits an inbox.", 1),
        ("Context packing: what belongs in the prompt, and what you should leave out.", 1),
        ("When not to generate — academic integrity as keeping the human accountable.", 1),
        ("Blind taste tests: human, machine, and human-finished side by side.", 1),
        ("Social drops: five-minute lean-prompt tips, unused-use finds, human-finish of the week.", 1),
        ("Monthly challenge: one task, a token budget, a required human pass.", 1),
    ]:
        y = bullet_item(c, text, MARGIN_X, y, level=level)

    y -= 6
    y = bullet_item(c, "Mixer events", MARGIN_X, y, level=0, bold=True)
    for text, level in [
        ("Game nights (phones down for a stretch — practice being the human in the room).", 1),
        ("Lean-token jams", 1),
        ("Unnatural-thons with a published brief and a token budget", 2),
        ("Short sprints that must ship a human-finished demo", 2),
        ("Workflow swap socials across programs", 1),
        ("Lunch & learns and industry nights with people who kept a workflow, not a slide deck", 1),
        ("Clubs Expo tables in fall and winter", 1),
    ]:
        y = bullet_item(c, text, MARGIN_X, y, level=level)

    y -= 12
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 12)
    c.drawString(MARGIN_X, y, "How we register")
    y -= 16
    notes = [
        "Any currently enrolled SAIT student can start or join. Before Stage 1 on the Saitsa Clubs Portal (Rubric), confirm three executives: President, Vice-President Operations, and Vice-President Finance.",
        "Register at portal.hellorubric.com, select Southern Alberta Institute of Technology, and submit for Saitsa approval. Contact saitsa.clubs@edu.sait.ca with questions.",
        "Membership stays open to all SAIT students. At least 75% of members must be current SAIT students. Community members may join at the executives’ discretion but cannot hold executive roles or vote.",
        "Seek a faculty advisor in the School for Advanced Digital Technology (or another school if a better fit). Advisors mentor; they do not run the club.",
    ]
    for note in notes:
        y = bullet_item(c, note, MARGIN_X, y, level=0)
        y -= 1


def page_style_visual(c: canvas.Canvas) -> None:
    draw_header(c, 16)
    draw_title(c, "Unnatural Intelligence Style Guide", PAGE_H - 92, size=20)

    # Large wordmark
    draw_wordmark(c, 130, PAGE_H - 200, size=72)

    # Color chips beside the mark
    chips = [
        (TEAL, MINT, VIOLET),
        (LAVENDER, CORAL, GOLD),
        (CHARCOAL, LIGHT, SLATE),
    ]
    x0, y0 = 250, PAGE_H - 168
    size = 42
    gap = 8
    for r, row in enumerate(chips):
        for col_i, col in enumerate(row):
            c.setFillColor(col)
            c.roundRect(x0 + col_i * (size + gap), y0 - r * (size + gap), size, size, 6, fill=1, stroke=0)

    # Mascot row
    my = PAGE_H - 340
    for i, dx in enumerate((-70, 0, 70)):
        draw_mascot(c, CX + dx, my, size=36)

    # Decorative waves
    y_base = PAGE_H - 410
    c.setLineCap(1)
    for col, amp, phase, weight in (
        (MINT, 16, 0.2, 10),
        (VIOLET, 12, 1.1, 8),
        (CORAL, 9, 2.0, 6),
    ):
        c.setStrokeColor(col)
        c.setLineWidth(weight)
        c.drawPath(wave_path(c, y_base, amp, phase, 40, PAGE_W - 40))

    # Font bars
    bar_y = 120
    c.setFillColor(LAVENDER)
    c.roundRect(MARGIN_X, bar_y + 28, CONTENT_W, 36, 4, fill=1, stroke=0)
    c.setFillColor(TEAL_DEEP)
    c.setFont("Inter-Bold", 11)
    c.drawString(MARGIN_X + 14, bar_y + 40, "Primary font: Inter  ·  Inter Display for titles")

    c.setFillColor(GOLD)
    c.roundRect(MARGIN_X, bar_y - 16, CONTENT_W, 36, 4, fill=1, stroke=0)
    c.setFillColor(TEAL_DEEP)
    c.setFont("JetBrains-Bold", 10)
    c.drawString(MARGIN_X + 14, bar_y - 4, "Secondary font: JetBrains Mono  ·  labels, codes, UI moments")


def page_style_codes(c: canvas.Canvas) -> None:
    draw_header(c, 17)
    y = PAGE_H - 110
    c.setFillColor(INK)
    c.setFont("Inter-Italic", 13)
    c.drawCentredString(CX, y, "Google Friendly Fonts:")
    y -= 22
    c.setFont("Inter", 13)
    c.drawCentredString(CX, y, "Inter  |  JetBrains Mono")

    swatches = [
        ("#1A7A84", TEAL),
        ("#8EE3D8", MINT),
        ("#5A5A5A", SLATE),
        ("#7B61FF", VIOLET),
        ("#C4B8FF", LAVENDER),
        ("#EAEAEA", LIGHT),
        ("#FF6B4A", CORAL),
        ("#F4C430", GOLD),
    ]
    y = PAGE_H - 190
    box_w, box_h = 130, 52
    gap_x, gap_y = 22, 70
    cols = 3
    start_x = CX - (3 * box_w + 2 * gap_x) / 2
    for i, (hex_code, col) in enumerate(swatches):
        col_i = i % cols
        row = i // cols
        x = start_x + col_i * (box_w + gap_x)
        yy = y - row * (box_h + gap_y)
        c.setFillColor(col)
        c.roundRect(x, yy, box_w, box_h, 6, fill=1, stroke=0)
        c.setFillColor(col if col != LIGHT else SLATE)
        c.setFont("JetBrains-Bold", 10)
        c.drawCentredString(x + box_w / 2, yy - 16, hex_code)

    # Copy-paste table
    table_top = 210
    c.setFillColor(INK)
    c.setFont("Inter-Bold", 11)
    c.drawString(MARGIN_X, table_top + 18, "Copy-Paste Codes")
    cell_w = CONTENT_W / 3
    cell_h = 28
    for i in range(9):
        col_i = i % 3
        row = i // 3
        x = MARGIN_X + col_i * cell_w
        yy = table_top - row * cell_h
        if i < len(swatches):
            hex_code, col = swatches[i]
            c.setFillColor(col)
            c.rect(x, yy - cell_h, cell_w, cell_h, fill=1, stroke=0)
            text_col = white if col in (TEAL, VIOLET, SLATE, CORAL) else INK
            c.setFillColor(text_col)
            c.setFont("JetBrains", 9)
            c.drawCentredString(x + cell_w / 2, yy - cell_h / 2 - 3, hex_code)
        else:
            c.setFillColor(white)
            c.rect(x, yy - cell_h, cell_w, cell_h, fill=1, stroke=0)
        c.setStrokeColor(mix(LIGHT, SLATE, 0.15))
        c.setLineWidth(0.5)
        c.rect(x, yy - cell_h, cell_w, cell_h, fill=0, stroke=1)


def build() -> Path:
    register_fonts()
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("Unnatural Intelligence Club Charter")
    c.setAuthor("Unnatural Intelligence")
    c.setSubject(
        "Pursue untapped potential. Integrate AI into daily and professional "
        "workflows. Optimize tokens, keep the human."
    )

    pages = [
        page_cover,
        page_toc,
        page_mission,
        page_basis,
        page_goals_a,
        page_goals_b,
        page_exec_divider,
        page_directors,
        page_finance,
        page_social,
        page_designer,
        page_events_roles,
        page_events_divider,
        page_events_a,
        page_events_b,
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
