#!/usr/bin/env python3
"""A4 slide deck matching the PDF charter page layout.

Open in Google Slides for the closest editable version of the designed
PDF / original UXicorns page format. Google Docs is a flowing word
processor and cannot keep full page-layout art.
"""

from __future__ import annotations

import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import nsmap, qn
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUTPUT = ROOT / "Unnatural_Intelligence_Club_Charter.pptx"

TEAL = RGBColor(0x1A, 0x7A, 0x84)
INK = RGBColor(0x1A, 0x1A, 0x1A)
SLATE = RGBColor(0x5A, 0x5A, 0x5A)
RULE = RGBColor(0xD9, 0xD9, 0xD9)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SWATCHES = [
    ("#1A7A84", RGBColor(0x1A, 0x7A, 0x84), True),
    ("#8EE3D8", RGBColor(0x8E, 0xE3, 0xD8), False),
    ("#5A5A5A", RGBColor(0x5A, 0x5A, 0x5A), True),
    ("#7B61FF", RGBColor(0x7B, 0x61, 0xFF), True),
    ("#C4B8FF", RGBColor(0xC4, 0xB8, 0xFF), False),
    ("#EAEAEA", RGBColor(0xEA, 0xEA, 0xEA), False),
    ("#FF6B4A", RGBColor(0xFF, 0x6B, 0x4A), True),
    ("#F4C430", RGBColor(0xF4, 0xC4, 0x30), False),
]


def _prs() -> Presentation:
    prs = Presentation()
    prs.slide_width = Inches(8.27)
    prs.slide_height = Inches(11.69)
    return prs


def blank(prs: Presentation):
    return prs.slides.add_slide(prs.slide_layouts[6])


def chrome(slide, prs, page: int) -> None:
    slide.shapes.add_picture(
        str(ASSETS / "header.png"),
        Inches(0.18),
        Inches(0.12),
        width=prs.slide_width - Inches(0.36),
    )
    box = slide.shapes.add_textbox(
        Inches(0), Inches(11.05), prs.slide_width, Inches(0.32)
    )
    tf = box.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = str(page)
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = TEAL
    run.font.name = "Inter"
    slide.shapes.add_picture(
        str(ASSETS / "mascot.png"),
        prs.slide_width / 2 - Inches(0.16),
        Inches(11.32),
        width=Inches(0.32),
    )


def tb(slide, l, t, w, h, text, *, size=12, bold=False, italic=False, color=INK, align=PP_ALIGN.LEFT, font="Inter", anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = None
    try:
        tf._txBody.bodyPr.set("anchor", {MSO_ANCHOR.MIDDLE: "ctr", MSO_ANCHOR.TOP: "t"}.get(anchor, "t"))
    except Exception:
        pass
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    run.font.name = font
    return tf


def bullets(slide, l, t, w, h, items, size=13):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    for i, (text, level) in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = text
        p.level = min(level, 2)
        p.font.size = Pt(size if level == 0 else size - 1)
        p.font.color.rgb = INK
        p.font.name = "Inter"
        p.space_after = Pt(4)
        p.font.bold = level == 0 and items[0][1] == 0 and i == 0 and False
    return tf


def section_list(slide, prs, title, blocks, page, start_y=1.35):
    chrome(slide, prs, page)
    tb(slide, Inches(0.55), Inches(1.15), Inches(7.2), Inches(0.45), title, size=24, bold=True, align=PP_ALIGN.CENTER)
    y = start_y
    for heading, body in blocks:
        tb(slide, Inches(0.7), Inches(y), Inches(6.9), Inches(0.32), heading, size=14, bold=True)
        tb(slide, Inches(0.7), Inches(y + 0.30), Inches(6.9), Inches(0.7), body, size=12, color=INK)
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0.7),
            Inches(y + 1.02),
            Inches(6.9),
            Pt(0.75),
        )
        line.fill.solid()
        line.fill.fore_color.rgb = RULE
        line.line.fill.background()
        y += 1.18


def build() -> Path:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    if not (ASSETS / "header.png").exists():
        from export_assets import export
        export()

    prs = _prs()
    M = Inches(0.7)
    W = Inches(6.9)
    page = 1

    # 1 cover
    s = blank(prs)
    chrome(s, prs, page)
    tb(s, Inches(0.4), Inches(4.4), Inches(7.5), Inches(0.7), "Unnatural Intelligence", size=32, bold=True, align=PP_ALIGN.CENTER)
    tb(s, Inches(0.4), Inches(5.15), Inches(7.5), Inches(0.5), "Club Charter", size=24, bold=True, align=PP_ALIGN.CENTER)
    tb(s, Inches(0.4), Inches(5.75), Inches(7.5), Inches(0.4), "August 2026", size=14, align=PP_ALIGN.CENTER)
    tb(s, Inches(0.4), Inches(6.25), Inches(7.5), Inches(0.35), "Untapped  ·  Integrated  ·  Human", size=12, italic=True, color=SLATE, align=PP_ALIGN.CENTER)
    page += 1

    # 2 contents
    s = blank(prs)
    chrome(s, prs, page)
    tb(s, M, Inches(1.2), W, Inches(0.4), "Contents", size=22, bold=True, align=PP_ALIGN.CENTER)
    toc = [
        "Mission Statement",
        "The Basis",
        "Goals",
        "Executive Roles & Responsibilities",
        "Event Concepts",
        "Style Guide",
    ]
    bullets(s, M, Inches(1.9), W, Inches(7), [(t, 0) for t in toc], size=16)
    page += 1

    # 3 mission
    s = blank(prs)
    chrome(s, prs, page)
    tb(s, M, Inches(3.6), W, Inches(0.5), "Mission Statement", size=24, bold=True, align=PP_ALIGN.CENTER)
    tb(
        s,
        Inches(0.85),
        Inches(4.3),
        Inches(6.55),
        Inches(2.2),
        "“Pursue the untapped potential of AI. Explore integrating AI into our daily and professional workflows. Optimize token usage while still retaining that touch of humanity.”",
        size=15,
        italic=True,
        align=PP_ALIGN.CENTER,
    )
    tb(s, M, Inches(6.7), W, Inches(0.4), "Untapped potential  ·  Daily & professional workflows  ·  Lean tokens, human finish", size=11, color=SLATE, align=PP_ALIGN.CENTER)
    page += 1

    # 4 basis
    s = blank(prs)
    section_list(
        s,
        prs,
        "The Basis",
        [
            ("1. Pursue the untapped potential of AI", "Most students only meet the default chatbot. The interesting work is off to the side. We go looking for those."),
            ("2. Integrate AI into daily and professional workflows", "A demo is not a habit. Fold AI into Tuesday, then keep only what actually saves time."),
            ("3. Optimize tokens, keep the human", "Wasteful prompts are sloppy thinking. Fewer tokens, then a human finish so it still sounds like a person."),
            ("4. A polytechnic is the right place for this", "Construction, health, energy, business, media, and ICT each hide different unused potential."),
            ("5. Built to exist as a Saitsa club", "Open membership, student-led, non-profit, three signing executives, registered through the Saitsa Clubs Portal."),
        ],
        page,
    )
    page += 1

    # 5-6 goals
    s = blank(prs)
    section_list(
        s,
        prs,
        "Goals",
        [
            ("1. Pursue Untapped Potential", "Look past the default chatbot. Find uses workplaces have not worn out yet."),
            ("2. Integrate AI into Daily & Professional Workflows", "Move from one-off demos to habits: class, practicum, job search, and each SAIT program."),
            ("3. Optimize Tokens, Keep the Human", "Spend fewer tokens, then edit until the work still sounds like a person."),
            ("4. Cross-Program Workflow Sharing", "Bring different jobs into the same room so unused potential travels."),
            ("5. A Community of Practice, Not a Tool Fan Club", "Share the workflows people actually keep. Critique the ones that flatten a human voice."),
        ],
        page,
    )
    page += 1
    s = blank(prs)
    section_list(
        s,
        prs,
        "Goals",
        [
            ("6. Lower Barriers to Participation", "You do not need a CS background, a paid model, or a prompt library to walk in."),
            ("7. Leadership Development", "Run the club lean, documented, and human — under Saitsa’s framework."),
            ("8. Experiment Without Waste", "Try the weird idea. Kill the prompt that burns tokens for nothing."),
            ("9. Integrity, Voice, and Human Accountability", "If you could not stand behind the output without the model, it is not finished."),
            ("10. Strengthen Unnatural Intelligence’s Presence on Campus", "Be known for unused potential, real workflows, and work that still sounds like a person."),
        ],
        page,
        start_y=1.5,
    )
    page += 1

    # 7 divider
    s = blank(prs)
    chrome(s, prs, page)
    tb(s, M, Inches(5.0), W, Inches(0.5), "Executive Roles &", size=28, bold=True, align=PP_ALIGN.CENTER)
    tb(s, M, Inches(5.5), W, Inches(0.5), "Responsibilities", size=28, bold=True, align=PP_ALIGN.CENTER)
    page += 1

    def role_slide(title, role_name, purpose, items, pg):
        sl = blank(prs)
        chrome(sl, prs, pg)
        tb(sl, M, Inches(1.15), W, Inches(0.35), title, size=22, bold=True)
        tb(sl, M, Inches(1.55), W, Inches(0.4), role_name, size=14, bold=True)
        tb(sl, M, Inches(1.95), W, Inches(0.4), f"Core Purpose: {purpose}", size=12)
        tb(sl, M, Inches(2.35), W, Inches(0.3), "Responsibilities:", size=12, bold=True)
        bullets(sl, M, Inches(2.65), W, Inches(7.8), items, size=12)
        return sl

    role_slide(
        "Directors",
        "President — Strategic Lead & Club Coordinator",
        "Keep the club organized, aligned, and progressing forward.",
        [
            ("Hold veto power for decisions affecting club direction or budget.", 0),
            ("Set semester direction around the three foundations.", 0),
            ("Arrange and lead executive meetings; prepare agendas.", 0),
            ("Follow up on tasks and track deadlines.", 0),
            ("Book rooms and manage logistics.", 0),
            ("Monitor club email, Teams, Rubric, and official channels.", 0),
            ("Navigate conflict; represent the club with Saitsa.", 0),
            ("Ensure the three Saitsa signing authorities remain filled.", 0),
        ],
        page,
    )
    page += 1

    # Combine VP ops onto next - PDF has both on one page. Keep one role per remaining to avoid crowding... PDF page 8 has both. I'll put VP ops + note that finance is next.
    s = blank(prs)
    chrome(s, prs, page)
    tb(s, M, Inches(1.15), W, Inches(0.35), "Directors", size=22, bold=True)
    tb(s, M, Inches(1.55), W, Inches(0.4), "Vice-President Operations — Operations & Visionary", size=14, bold=True)
    tb(s, M, Inches(1.95), W, Inches(0.4), "Core Purpose: Aid overall direction and maintain operations in the absence of the president.", size=12)
    tb(s, M, Inches(2.4), W, Inches(0.3), "Responsibilities:", size=12, bold=True)
    bullets(
        s,
        M,
        Inches(2.7),
        W,
        Inches(7.6),
        [
            ("Serve as secondary decision-maker when the president is unavailable.", 0),
            ("Keep activity tied to the three foundations.", 0),
            ("Record minutes; organize event plans, budgets, Saitsa forms.", 0),
            ("Help onboard new execs.", 0),
            ("Monitor channels; navigate conflict; represent the club externally.", 0),
        ],
        size=13,
    )
    page += 1

    s = blank(prs)
    chrome(s, prs, page)
    tb(s, M, Inches(1.15), W, Inches(0.35), "Directors", size=22, bold=True)
    tb(s, M, Inches(1.55), W, Inches(0.4), "Vice-President Finance — Budgeting & Funding", size=14, bold=True)
    tb(s, M, Inches(1.95), W, Inches(0.35), "Core Purpose: Manage club finances responsibly and transparently.", size=12)
    tb(s, M, Inches(2.35), W, Inches(0.3), "Responsibilities:", size=12, bold=True)
    bullets(
        s,
        M,
        Inches(2.65),
        W,
        Inches(6.5),
        [
            ("Prepare semester forecasts; keep a ledger and receipts.", 0),
            ("Manage the Saitsa-issued club bank account.", 0),
            ("Budget events; submit quotes and grants.", 0),
            ("Apply for start-up reimbursement (up to $500) and term grants.", 0),
            ("Spend like we prompt: enough to do the work, nothing extra.", 0),
            ("Follow Saitsa and SAIT purchase guidelines.", 0),
        ],
        size=13,
    )
    tb(
        s,
        M,
        Inches(8.6),
        W,
        Inches(1.6),
        "Saitsa requires three signing executives: President, VP Operations, and VP Finance. Only current SAIT students who have paid the Saitsa fee may hold executive positions. The club is non-profit.",
        size=11,
        italic=True,
        color=SLATE,
    )
    page += 1

    s = blank(prs)
    chrome(s, prs, page)
    tb(s, M, Inches(1.15), W, Inches(0.35), "Marketing", size=22, bold=True)
    tb(s, M, Inches(1.55), W, Inches(0.45), "Social Media Lead (1–3) — Communication & Engagement", size=14, bold=True)
    tb(s, M, Inches(2.0), W, Inches(0.35), "Core Purpose: Maintain active, engaging communication across platforms.", size=12)
    bullets(
        s,
        M,
        Inches(2.45),
        W,
        Inches(8),
        [
            ("Instagram, Discord, Teams, Rubric, LinkedIn", 0),
            ("Captions, announcements, recaps, stories — human voice, no unedited AI captions", 0),
            ("Publish lean-prompt tips, unused-use finds, and human-finish before/afters", 0),
        ],
        size=14,
    )
    page += 1

    s = blank(prs)
    chrome(s, prs, page)
    tb(s, M, Inches(1.15), W, Inches(0.35), "Marketing", size=22, bold=True)
    tb(s, M, Inches(1.55), W, Inches(0.5), "Graphic Designer (1–2) — Visual Identity & Creative Production", size=14, bold=True)
    tb(s, M, Inches(2.1), W, Inches(0.35), "Core Purpose: Shape the club’s visual identity and produce design assets.", size=12)
    bullets(
        s,
        M,
        Inches(2.55),
        W,
        Inches(8),
        [
            ("Social posts, tabloid posters with the Saitsa Clubs logo, presentations", 0),
            ("AI may sketch; a human always finishes what gets published", 0),
            ("Do not use the official SAIT logo on club materials", 0),
        ],
        size=14,
    )
    page += 1

    s = blank(prs)
    chrome(s, prs, page)
    tb(s, M, Inches(1.15), W, Inches(0.35), "Events", size=22, bold=True)
    tb(s, M, Inches(1.55), W, Inches(0.4), "Events Coordinator (2) — Planning & Execution", size=14, bold=True)
    bullets(
        s,
        M,
        Inches(2.05),
        W,
        Inches(3.6),
        [
            ("Propose ideas with agenda, materials, and which foundation it serves", 0),
            ("Coordinate finance, marketing, outreach; submit via Rubric before promoting", 0),
            ("Run the event; collect feedback", 0),
        ],
        size=13,
    )
    tb(s, M, Inches(5.7), W, Inches(0.4), "Outreach & Networking — External Communication", size=14, bold=True)
    bullets(
        s,
        M,
        Inches(6.15),
        W,
        Inches(4.2),
        [
            ("Speakers, partners, Calgary industry — people with unused AI potential in real workflows", 0),
            ("Help identify a faculty advisor (encouraged; required if academic)", 0),
        ],
        size=13,
    )
    page += 1

    s = blank(prs)
    chrome(s, prs, page)
    tb(s, M, Inches(5.2), W, Inches(0.5), "Event Concepts", size=28, bold=True, align=PP_ALIGN.CENTER)
    page += 1

    s = blank(prs)
    chrome(s, prs, page)
    tb(s, M, Inches(1.15), W, Inches(0.55), "Untapped Potential — find what default chat never gets asked.", size=16, bold=True)
    bullets(
        s,
        M,
        Inches(1.75),
        W,
        Inches(4.4),
        [
            ("“What’s this button for?” nights", 0),
            ("Multimodal labs: shop-floor photos, schematics, messy syllabi", 0),
            ("Tiny assistants you delete if unused", 0),
            ("Failed-experiment night", 0),
        ],
        size=14,
    )
    tb(s, M, Inches(6.2), W, Inches(0.5), "Workflow Integration — from demo to a Tuesday you would actually keep.", size=16, bold=True)
    bullets(
        s,
        M,
        Inches(6.75),
        W,
        Inches(3.8),
        [
            ("Bring Your Tuesday", 0),
            ("Daily Driver challenge (keep what you still open on day 14)", 0),
            ("Workflow swaps across programs", 0),
            ("End-of-semester Daily Driver showcase", 0),
        ],
        size=14,
    )
    page += 1

    s = blank(prs)
    chrome(s, prs, page)
    tb(s, M, Inches(1.15), W, Inches(0.55), "Token Craft & Human Touch — less spend, more of you in the result.", size=16, bold=True)
    bullets(
        s,
        M,
        Inches(1.75),
        W,
        Inches(4.6),
        [
            ("Token Diet: same outcome, fewer tokens", 0),
            ("Human Finish Studio", 0),
            ("“Don’t send that” clinic", 0),
            ("Blind taste tests: human / machine / human-finished", 0),
        ],
        size=14,
    )
    tb(s, M, Inches(6.4), W, Inches(0.4), "Mixer events", size=16, bold=True)
    bullets(
        s,
        M,
        Inches(6.85),
        W,
        Inches(3.6),
        [
            ("Game nights (phones down for a stretch)", 0),
            ("Unnatural-thons with a token budget", 0),
            ("Clubs Expo tables", 0),
        ],
        size=14,
    )
    page += 1

    s = blank(prs)
    chrome(s, prs, page)
    tb(s, M, Inches(1.2), W, Inches(0.4), "Unnatural Intelligence Style Guide", size=22, bold=True, align=PP_ALIGN.CENTER)
    s.shapes.add_picture(str(ASSETS / "wordmark.png"), Inches(2.7), Inches(1.8), width=Inches(2.8))
    tb(s, M, Inches(3.5), W, Inches(0.35), "Google-friendly fonts: Inter  |  JetBrains Mono", size=14, italic=True, align=PP_ALIGN.CENTER)
    # swatches 3x3
    left = Inches(1.15)
    top = Inches(4.1)
    box_w, box_h = Inches(1.85), Inches(0.85)
    gap = Inches(0.22)
    for i, (hex_code, rgb, light) in enumerate(SWATCHES):
        col, row = i % 3, i // 3
        shape = s.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE,
            left + col * (box_w + gap),
            top + row * (box_h + Inches(0.45)),
            box_w,
            box_h,
        )
        shape.fill.solid()
        shape.fill.fore_color.rgb = rgb
        shape.line.fill.background()
        tf = shape.text_frame
        tf.word_wrap = False
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        run = p.add_run()
        run.text = hex_code
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = WHITE if light else INK
        run.font.name = "JetBrains Mono"

    prs.save(str(OUTPUT))
    return OUTPUT


if __name__ == "__main__":
    path = build()
    print(f"Wrote {path}")
