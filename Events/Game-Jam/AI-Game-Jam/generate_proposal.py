#!/usr/bin/env python3
"""Filled 2026–27 event proposal: 24-Hour AI Game Jam."""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib.colors import white
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
EVENTS = HERE.parent
REPO = EVENTS.parent
CHARTER = REPO / "charter"
sys.path.insert(0, str(EVENTS))
sys.path.insert(0, str(CHARTER))

import generate_charter_revamp as kit
import generate_proposal as tmpl
import revamp_copy as copy
from revamp_kit import export as export_kit

OUTPUT = HERE / "event-proposal-AI-game-jam.pdf"

POSTER = tmpl.POSTER_COST
MISC = tmpl.MISC_COST


def money(value: float) -> str:
    return f"${value:,.2f}"


def text_block(c: canvas.Canvas, text: str, y: float, *, font="Inter", size=9.4, lead=12.4, color=None) -> float:
    color = color or kit.INK
    c.setFillColor(color)
    c.setFont(font, size)
    for line in kit.wrap(text, font, size, kit.CONTENT_W):
        c.drawString(kit.MARGIN_X, y, line)
        y -= lead
    return y


def labeled_copy(c: canvas.Canvas, label: str, body: str, y: float, height: float) -> float:
    c.setFillColor(kit.INK)
    c.setFont("Inter-Bold", 11)
    c.drawString(kit.MARGIN_X, y, label)
    y -= 10
    bottom = y - height
    c.setFillColor(white)
    c.setStrokeColor(kit.RULE)
    c.setLineWidth(0.8)
    c.roundRect(kit.MARGIN_X, bottom, kit.CONTENT_W, height, 8, fill=1, stroke=1)
    c.setFillColor(kit.INK)
    c.setFont("Inter", 8.8)
    ty = y - 14
    for line in kit.wrap(body, "Inter", 8.8, kit.CONTENT_W - 24):
        if ty < bottom + 10:
            break
        c.drawString(kit.MARGIN_X + 12, ty, line)
        ty -= 11.6
    return bottom - 14


def budget_table(c: canvas.Canvas, y: float, rows: list[tuple[str, str, float, str]]) -> float:
    item_w = 108
    cost_w = 72
    detail_w = kit.CONTENT_W - item_w - cost_w
    table_rows: list[tuple[list[str], str]] = []
    total = 0.0
    for item, details, cost, kind in rows:
        total += cost
        table_rows.append(([item, details, money(cost)], kind))
    table_rows.append(
        (["TOTAL", "Do not spend before grant approval. Quotes via SECC / Curated Catering.", money(total)], "total")
    )
    return tmpl.draw_table(
        c,
        y,
        ["Item", "Details", "Estimated cost"],
        [item_w, detail_w, cost_w],
        table_rows,
        aligns=["left", "left", "right"],
        min_row_h=26,
    )


def page_cover(c: canvas.Canvas) -> None:
    kit.chrome(c, 1)
    kit.draw_img(c, "jellyfish.png", kit.CX, kit.PAGE_H / 2 + 176, h=132, center=True)
    kit.draw_img(c, "wordmark.png", kit.CX, kit.PAGE_H / 2 + 58, w=236, center=True)
    c.setFillColor(kit.INK)
    c.setFont("InterDisplay-Bold", 26)
    c.drawCentredString(kit.CX, kit.PAGE_H / 2 - 28, "Event Proposal")
    c.setFont("JetBrains-Bold", 11)
    c.setFillColor(kit.WINE)
    c.drawCentredString(kit.CX, kit.PAGE_H / 2 - 52, "24-Hour AI Game Jam  ·  Fall 2026")
    c.setFillColor(kit.SLATE)
    c.setFont("Inter-Italic", 11)
    c.drawCentredString(kit.CX, kit.PAGE_H / 2 - 74, "Unnatural Intelligence  ×  Game Development Club")
    c.setFont("Inter", 10)
    c.drawCentredString(kit.CX, kit.PAGE_H / 2 - 94, copy.PILLARS)
    kit.draw_img(c, "tagline.png", kit.CX, kit.PAGE_H / 2 - 140, w=220, center=True)
    kit.badge_row(c, ["workshop", "live-lab", "halt-restart", "clubs-expo"], 148, h=15, gap=8)
    c.setFillColor(kit.SLATE)
    c.setFont("Inter", 8)
    c.drawCentredString(kit.CX, 124, "Saitsa Clubs Portal  ·  portal.hellorubric.com")
    tmpl.signature_line(c, y=88)


def page_overview(c: canvas.Canvas) -> None:
    kit.chrome(c, 2, icon="ticket", badges=["workshop", "live-lab"])
    y = kit.draw_title(c, "24-Hour AI Game Jam Overview", kit.CONTENT_TOP, size=18) - 2
    y = labeled_copy(
        c,
        "Description",
        "A 24-hour on-campus game jam co-hosted by Unnatural Intelligence and the "
        "SAIT Game Development Club (Video Game Design Club). One secret theme at "
        "kickoff; teams of 2–5 ship a playable prototype. A shared Layer workspace "
        "gives 30–100 people game-dev AI (art, 3D, audio, assisted implementation) "
        "without buying a seat each. Game Dev Club covers engines and scope; UI "
        "covers the AI pipeline and the human finish. Not a sleepover: jammers may "
        "leave overnight. Anyone who stays is working in a booked room, listed with "
        "Campus Security, with a named organizer on site. No alcohol. Meals only "
        "through Curated Catering powered by Hotel Arts, via the SECC.",
        y,
        height=118,
    )
    y = labeled_copy(
        c,
        "Time and Date",
        "Saturday 14 November 2026, 10:00 AM  →  Sunday 15 November 2026, 10:00 AM. "
        "Pending SECC room confirmation and the 5 October 2026 grant intake "
        "(confirm 2026/27 disbursement dates with SECC).",
        y,
        height=52,
    )
    y = labeled_copy(
        c,
        "Proposed Location",
        "Indoor computer-friendly classroom or lab cluster with projector, power, "
        "and Wi-Fi (Stan Grad / Heritage Hall). Weekend booking by SECC only. "
        "Overflow room if RSVPs exceed ~40. After-hours access with Campus Security.",
        y,
        height=56,
    )
    y = labeled_copy(
        c,
        "Expected Attendance",
        "$500 / $1,000: 24 catered, ~30 RSVP.  $2,000 / $3,500: 30 catered, ~40 RSVP.  "
        "$5,000: 40 catered, AI workspace for 100. Open to all SAIT students; no "
        "prior game-dev or AI experience. PEO: VP, Unnatural Intelligence (Pierre Tchio), "
        "with a Game Development Club exec as overnight deputy.",
        y,
        height=62,
    )
    tmpl.signature_line(c)


def page_agenda(c: canvas.Canvas) -> None:
    kit.chrome(c, 3, icon="workflow", badges=["workshop", "live-lab"])
    y = kit.draw_title(c, "Agenda", kit.CONTENT_TOP, size=22) - 4
    c.setFillColor(kit.SLATE)
    c.setFont("Inter-Italic", 9)
    c.drawCentredString(kit.CX, y, "24 hours. Times may shift ±30 minutes with SECC access.")
    y -= 18
    rows = [
        (["45 min", "Doors, check-in, attendance, power map, member sign-ups (both clubs)"], "body"),
        (["30 min", "Welcome, rules, secret theme, team formation"], "body"),
        (["45 min", "AI + engine onboarding: Layer credits, Godot/Unity/web, human-finish rule"], "body"),
        (["10.5 h", "Build block 1 (Saturday). Mentors float. Snack/lunch drop (budget-dependent)"], "body"),
        (["45 min", "Mid-jam check-in: scope cuts, playtest buddy swap, credit check"], "body"),
        (["8 h", "Build block 2 + quiet hours 01:00–06:00. Midnight snack. Leave-and-return OK"], "body"),
        (["45 min", "Breakfast drop (budget-dependent) and final polish call"], "body"),
        (["90 min", "Submissions freeze, playtests, skill-based showcase (not a raffle)"], "body"),
        (["30 min", "Wrap, photos, teardown, room reset"], "body"),
    ]
    tmpl.draw_table(
        c,
        y,
        ["Duration", "Segment"],
        [88, kit.CONTENT_W - 88],
        rows,
        min_row_h=32,
    )
    tmpl.signature_line(c)


def page_objectives(c: canvas.Canvas) -> None:
    kit.chrome(c, 4, icon="spark", badges=["workshop"])
    y = kit.draw_title(c, "Objectives", kit.CONTENT_TOP, size=22) - 2
    c.setFillColor(kit.SLATE)
    c.setFont("Inter-Italic", 9.5)
    c.drawCentredString(kit.CX, y, "Tie at least one objective to a club foundation.")
    y -= 20
    prompts = [
        "Ship a playable prototype in 24 hours — every team leaves with a build or a recorded playthrough, even if the scope is tiny.",
        "Hands-on AI in production: a shared game-dev AI workspace for 30–100 people (not one seat each), with a team credit budget.",
        "Cross-club recruitment — Unnatural Intelligence and the Game Development Club both run sign-ups; beginners pair with people who have shipped.",
        "Foundations in public: untapped (AI for games), workflow (a real jam pipeline), human finish (the game still has to play). Feeds later events.",
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
        c.setFillColor(kit.INK)
        c.setFont("Inter", 10)
        ty = y - 26
        for line in kit.wrap(prompt, "Inter", 10, text_w):
            c.drawString(text_x, ty, line)
            ty -= 13.5
        y = bottom - 14
    tmpl.signature_line(c)


def page_rates(c: canvas.Canvas) -> None:
    kit.chrome(c, 5, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Requested Supplies and Budgeting", kit.CONTENT_TOP, size=16)
    y = text_block(
        c,
        "Built-in floor on every variant: $10 posters + $5 misc. Funding: Saitsa Clubs Grant "
        "(up to $5,000/term). Do not spend before approval. No alcohol, no gifts for members, "
        "swag capped at 50% of ordered cost. Attach quotes.",
        y,
        size=9.2,
        lead=12,
    )
    y -= 4
    c.setFillColor(kit.LIME)
    c.roundRect(kit.MARGIN_X, y - 36, kit.CONTENT_W, 40, 6, fill=1, stroke=0)
    c.setFillColor(kit.INK)
    c.setFont("Inter-Bold", 9)
    for i, line in enumerate(
        kit.wrap(
            "$2,000 is not enough for a true 24-hour catering program at SAIT rates. "
            "Recommended ask: $3,500 (30 fed). Term ceiling: $5,000 (40 fed, 100 on AI).",
            "Inter-Bold",
            9,
            kit.CONTENT_W - 20,
        )
    ):
        c.drawCentredString(kit.CX, y - 16 - i * 12, line)
    y -= 50

    c.setFillColor(kit.INK)
    c.setFont("Inter-Bold", 11)
    c.drawString(kit.MARGIN_X, y, "Catering — Curated Catering powered by Hotel Arts")
    y -= 14
    y = text_block(
        c,
        "Exclusive on-campus vendor. Order only via SECC. Everyday menu 72-hour lead; "
        "Express Drop Off 48 hours for groups ≤20. Quote: SAITevents@hotelarts.ca · 403-210-5774. "
        "Prices from the Hotel Arts Event Palette, × 18% service × 5% GST (× 1.239). Pending live quote.",
        y,
        size=8.7,
        lead=11.4,
        color=kit.SLATE,
    )
    y -= 6
    y = tmpl.draw_table(
        c,
        y,
        ["Menu item", "Base", "Loaded / person"],
        [kit.CONTENT_W - 160, 80, 80],
        [
            (["Coffee & tea", "$3.75", "$4.65"], "body"),
            (["Cookie Jar / Party Mix snack", "$12.00", "$14.87"], "body"),
            (["Energy Boost break", "$14.00", "$17.35"], "body"),
            (["Continental breakfast", "$22.00", "$27.26"], "body"),
            (["Working savoury meal (used as lunch)", "$24.00", "$29.74"], "body"),
            (["Wedding dinner (not used — too expensive)", "$45–$67", "$56–$83"], "body"),
        ],
        aligns=["left", "right", "right"],
        min_row_h=22,
    )
    y -= 12
    c.setFillColor(kit.INK)
    c.setFont("Inter-Bold", 11)
    c.drawString(kit.MARGIN_X, y, "Game-dev AI — Layer (unlimited members)")
    y -= 14
    y = text_block(
        c,
        "Per-seat tools fail at 30–100 people (Unity AI ~$10 USD/seat; Voxyl $29/seat; "
        "Meshy Studio $70 + $10/member). Layer: $0/seat, $10 USD for 300 Creative Units, "
        "then $60 / 1,000 CUs. Planning FX: USD 1.00 = CAD 1.38. ~70 CUs per jammer.",
        y,
        size=8.7,
        lead=11.4,
        color=kit.SLATE,
    )
    y -= 6
    col = kit.CONTENT_W / 4
    tmpl.draw_table(
        c,
        y,
        ["Headcount", "CU pool", "USD", "CAD"],
        [col, col, col, col],
        [
            (["30", "2,300", "$130", "$179"], "body"),
            (["50", "4,300", "$250", "$345"], "builtin"),
            (["100", "7,300", "$430", "$593"], "body"),
        ],
        aligns=["left", "right", "right", "right"],
        min_row_h=22,
    )
    tmpl.signature_line(c)


def page_budget_500_1000(c: canvas.Canvas) -> None:
    kit.chrome(c, 6, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Budget A — $500 snack lab", kit.CONTENT_TOP, size=16)
    y = text_block(
        c,
        "One Cookie Jar drop. Meals are BYO. Catering guarantee 24. RSVP cap ~30. Light Layer pool.",
        y,
        size=8.8,
        lead=11.5,
        color=kit.SLATE,
    )
    y -= 6
    y = budget_table(
        c,
        y,
        [
            ("Posters", "Tabloid 11×17, unaltered Saitsa Clubs logo", POSTER, "builtin"),
            ("Misc", "Tape, markers, unexpected small costs", MISC, "builtin"),
            ("Cookie Jar (24)", "Hotel Arts Cookie Jar @ $12 pp + 18% + GST", 357, "body"),
            ("Layer 1,300 CU", "Unlimited members. USD $70 × 1.38", 97, "body"),
            ("Name tags", "Printed club templates", 16, "body"),
            ("First aid / garbage", "Overnight supplies beyond misc", 15, "body"),
        ],
    )
    y -= 36
    y = kit.draw_title(c, "Budget B — $1,000 two snack services", y, size=15)
    y = text_block(
        c,
        "Kickoff Cookie Jar, midnight Party Mix, morning coffee. Still no sit-down meal. Guarantee 24.",
        y,
        size=8.8,
        lead=11.5,
        color=kit.SLATE,
    )
    y -= 6
    budget_table(
        c,
        y,
        [
            ("Posters", "Tabloid 11×17, unaltered Saitsa Clubs logo", POSTER, "builtin"),
            ("Misc", "Tape, markers, unexpected small costs", MISC, "builtin"),
            ("Cookie Jar (24)", "Kickoff @ $12 pp loaded", 357, "body"),
            ("Party Mix (24)", "Midnight @ $12 pp loaded", 357, "body"),
            ("Coffee & tea (24)", "Morning drop @ $3.75 pp loaded", 112, "body"),
            ("Layer 1,300 CU", "USD $70 × 1.38", 97, "body"),
            ("Name tags", "Printed club templates", 20, "body"),
            ("First aid + buffer", "Supplies $15 + dietary/minimums $27", 42, "body"),
        ],
    )
    tmpl.signature_line(c)


def page_budget_2000(c: canvas.Canvas) -> None:
    kit.chrome(c, 7, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Budget C — $2,000 breakfast jam", kit.CONTENT_TOP, size=18)
    y = text_block(
        c,
        "Snacks plus a real continental breakfast for 30. Midnight snack for 24. Moderate Layer pool. "
        "Still no Saturday lunch or dinner — $2,000 cannot buy a full 24-hour food program at "
        "Hotel Arts rates (a Working lunch for 30 is already ~$892 loaded).",
        y,
        size=9,
        lead=12,
        color=kit.SLATE,
    )
    y -= 8
    y = budget_table(
        c,
        y,
        [
            ("Posters", "Tabloid 11×17, unaltered Saitsa Clubs logo", POSTER, "builtin"),
            ("Misc", "Tape, markers, unexpected small costs", MISC, "builtin"),
            ("Cookie Jar (30)", "Kickoff @ $12 pp loaded", 446, "body"),
            ("Party Mix (24)", "Midnight @ $12 pp loaded", 357, "body"),
            ("Continental (30)", "Sunday breakfast @ $22 pp loaded", 818, "body"),
            ("Layer 2,300 CU", "~70 CU × 30. USD $130 × 1.38", 179, "body"),
            ("Name tags", "Printed club templates", 30, "body"),
            ("Power + first aid", "Strips, tape, basic kit", 40, "body"),
            ("After-hours security", "If assessed by SECC / Campus Security", 115, "body"),
        ],
    )
    y -= 14
    y = text_block(
        c,
        "Other costs held at $0 until quoted: room, A/V from SECC, Rosebud education arcade "
        "(register the jam; no seat fee), Godot/Unity Personal. Unused security money is reclaimed at close-out.",
        y,
        size=9,
        lead=12,
        color=kit.SLATE,
    )
    tmpl.signature_line(c)


def page_budget_3500(c: canvas.Canvas) -> None:
    kit.chrome(c, 8, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Budget D — $3,500 recommended", kit.CONTENT_TOP, size=18)
    y = text_block(
        c,
        "A real 24-hour jam: 30 people fed through lunch, snacks, midnight, breakfast, and coffee. "
        "Layer sized for ~50. Overnight security line. RSVP ~40; extras BYO food.",
        y,
        size=9,
        lead=12,
        color=kit.SLATE,
    )
    y -= 8
    budget_table(
        c,
        y,
        [
            ("Posters", "Tabloid 11×17, unaltered Saitsa Clubs logo", POSTER, "builtin"),
            ("Misc", "Tape, markers, unexpected small costs", MISC, "builtin"),
            ("Working meal (30)", "Savoury lunch drop @ $24 pp loaded", 892, "body"),
            ("Cookie Jar (30)", "Kickoff @ $12 pp loaded", 446, "body"),
            ("Party Mix (30)", "Midnight @ $12 pp loaded", 446, "body"),
            ("Continental (30)", "Sunday breakfast @ $22 pp loaded", 818, "body"),
            ("Coffee & tea (30)", "Extra drop @ $3.75 pp loaded", 139, "body"),
            ("Layer 4,300 CU", "Headroom for ~50. USD $250 × 1.38", 345, "body"),
            ("After-hours security", "Overnight coverage placeholder", 265, "body"),
            ("Name tags", "Printed club templates", 40, "body"),
            ("Power strips", "Classroom laptop load", 40, "body"),
            ("First aid + buffer", "Supplies $30 + dietary/minimums $24", 54, "body"),
        ],
    )
    tmpl.signature_line(c)


def page_budget_5000(c: canvas.Canvas) -> None:
    kit.chrome(c, 9, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Budget E — $5,000 term ceiling", kit.CONTENT_TOP, size=18)
    y = text_block(
        c,
        "40 people fed (lunch, late snack, midnight, breakfast, coffee). Layer sized for 100. "
        "People 41–100 may attend BYO if SECC allows the headcount; otherwise cap RSVP at 40. "
        "A 100-person fully catered 24-hour meal plan would need roughly $8,000–$15,000 in food alone.",
        y,
        size=9,
        lead=12,
        color=kit.SLATE,
    )
    y -= 8
    budget_table(
        c,
        y,
        [
            ("Posters", "Tabloid 11×17, unaltered Saitsa Clubs logo", POSTER, "builtin"),
            ("Misc", "Tape, markers, unexpected small costs", MISC, "builtin"),
            ("Working meal (40)", "Lunch drop @ $24 pp loaded", 1189, "body"),
            ("Energy Boost (40)", "Late-day snack @ $14 pp loaded", 694, "body"),
            ("Party Mix (40)", "Midnight @ $12 pp loaded", 595, "body"),
            ("Continental (40)", "Sunday breakfast @ $22 pp loaded", 1090, "body"),
            ("Coffee & tea (40)", "Extra drop @ $3.75 pp loaded", 186, "body"),
            ("Layer 7,300 CU", "~70 CU × 100. USD $430 × 1.38", 593, "body"),
            ("After-hours security", "Overnight coverage placeholder", 350, "body"),
            ("Name tags", "Printed club templates", 50, "body"),
            ("Power / ethernet", "Higher laptop load", 60, "body"),
            ("First aid + buffer", "Supplies $40 + dietary/price buffer $138", 178, "body"),
        ],
    )
    tmpl.signature_line(c)


def page_logistics(c: canvas.Canvas) -> None:
    kit.chrome(c, 10, icon="halt", badges=["workshop", "live-lab"])
    y = kit.draw_title(c, "Logistics, Risk & Compliance", kit.CONTENT_TOP, size=16) - 2
    for text in [
        "Room booking coordinated exclusively by the SECC — no direct booking by the club.",
        "Risk: medium. Indoor, no alcohol, no sport — but after-hours, fatigue, food, and laptop load.",
        "After-hours list to Campus Security (403-284-8530). Booked work session, not a sleepover. Quiet hours 01:00–06:00. Leave-and-return allowed.",
        "Food and beverages only through SAIT’s approved caterer (Curated Catering / Hotel Arts), arranged via the SECC. Dietary needs on RSVP.",
        "A/V picked up from SECC and returned after Sunday teardown.",
        "PEO plus a written shift roster so a named UI or Game Dev exec is on site every hour. Two-person overnight minimum.",
        "Attendance list for the event report. Posters: tabloid 11×17, Saitsa Clubs logo unaltered, saitsa.com/Poster-Submission, $10 built-in. Removed within 48 hours.",
        "If SECC calls this a social event, grant funds must already be in the club account before the event proposal. No spend before grant approval.",
    ]:
        y = kit.bullet_item(c, text, kit.MARGIN_X, y, level=0)

    y -= 8
    c.setFillColor(kit.INK)
    c.setFont("InterDisplay-Bold", 16)
    c.drawCentredString(kit.CX, y, "Promotion Plan")
    y -= 18
    for text in [
        "Posters on Saitsa General Poster Boards (approved submission first).",
        "Both clubs’ Discord, Instagram, Teams, and Rubric RSVP.",
        "Clubs Fall Expo / Showcase (13–14 October 2026) if the jam is after it.",
        "Word of mouth in IT, animation, media, and engineering classes; open to all SAIT students.",
    ]:
        y = kit.bullet_item(c, text, kit.MARGIN_X, y, level=0)

    kit.draw_img(
        c,
        "saitsa-clubs.png",
        kit.PAGE_W - kit.MARGIN_X - 46,
        128,
        w=90,
        center=True,
    )
    tmpl.signature_line(c)


def build() -> Path:
    if not (CHARTER / "assets" / "revamp" / "header.png").exists():
        export_kit()
    kit.register_fonts()
    c = canvas.Canvas(str(OUTPUT), pagesize=A4)
    c.setTitle("24-Hour AI Game Jam — Event Proposal")
    c.setAuthor("Unnatural Intelligence")
    c.setSubject("Saitsa student club event proposal — Fall 2026")

    pages = [
        page_cover,
        page_overview,
        page_agenda,
        page_objectives,
        page_rates,
        page_budget_500_1000,
        page_budget_2000,
        page_budget_3500,
        page_budget_5000,
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
