#!/usr/bin/env python3
"""Filled 2026–27 event proposal: 24-hour AI Game Jam (Godot × paid Ziva)."""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib.colors import white
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
EVENTS = HERE.parent
REPO = EVENTS.parent
CHARTER = REPO / "charter"
QUOTES = HERE / "quotes"
sys.path.insert(0, str(EVENTS))
sys.path.insert(0, str(CHARTER))

import generate_charter_revamp as kit
import generate_proposal as tmpl
from revamp_kit import export as export_kit

OUTPUT = HERE / "event-proposal-24-hour-AI-game-jam.pdf"

POSTER = 10.00
MISC = 5.00


def money(value: float) -> str:
    return f"${value:,.2f}"


def text_block(c, text, y, *, font="Inter", size=9.2, lead=12.2, color=None):
    color = color or kit.INK
    c.setFillColor(color)
    c.setFont(font, size)
    for line in kit.wrap(text, font, size, kit.CONTENT_W):
        c.drawString(kit.MARGIN_X, y, line)
        y -= lead
    return y


def labeled_copy(c, label, body, y, height):
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


def budget_table(c, y, rows, total_note="Do not spend before grant approval. Split 50/50."):
    item_w = 118
    cost_w = 72
    detail_w = kit.CONTENT_W - item_w - cost_w
    table_rows = []
    total = 0.0
    for item, details, cost, kind in rows:
        total += cost
        table_rows.append(([item, details, money(cost)], kind))
    table_rows.append((["TOTAL", total_note, money(total)], "total"))
    return tmpl.draw_table(
        c,
        y,
        ["Item", "Details", "Estimated cost"],
        [item_w, detail_w, cost_w],
        table_rows,
        aligns=["left", "left", "right"],
        min_row_h=22,
    )


def draw_quote(c, filename, y, *, max_h=None, caption=""):
    path = QUOTES / filename
    img = ImageReader(str(path))
    iw, ih = img.getSize()
    w = kit.CONTENT_W
    h = w * ih / iw
    if max_h and h > max_h:
        h = max_h
        w = h * iw / ih
    x = kit.MARGIN_X + (kit.CONTENT_W - w) / 2
    c.setStrokeColor(kit.RULE)
    c.setLineWidth(0.4)
    c.rect(x, y - h, w, h, fill=0, stroke=1)
    c.drawImage(img, x, y - h, width=w, height=h, mask="auto")
    y = y - h - 10
    if caption:
        c.setFillColor(kit.SLATE)
        c.setFont("Inter", 7.2)
        for line in kit.wrap(caption, "Inter", 7.2, kit.CONTENT_W):
            c.drawString(kit.MARGIN_X, y, line)
            y -= 9.2
    return y - 8


def page_cover(c):
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
    c.drawCentredString(
        kit.CX,
        kit.PAGE_H / 2 - 94,
        "Godot 4  ·  paid Ziva Basic  ·  24 hours  ·  doors Sat 9:00",
    )
    kit.draw_img(c, "tagline.png", kit.CX, kit.PAGE_H / 2 - 140, w=220, center=True)
    kit.badge_row(c, ["workshop", "live-lab", "halt-restart", "clubs-expo"], 148, h=15, gap=8)
    c.setFillColor(kit.SLATE)
    c.setFont("Inter", 8)
    c.drawCentredString(kit.CX, 124, "Saitsa Clubs Portal  ·  portal.hellorubric.com")
    tmpl.signature_line(c, y=88)


def page_overview(c):
    kit.chrome(c, 2, icon="ticket", badges=["workshop", "live-lab"])
    y = kit.draw_title(c, "24-Hour AI Game Jam Overview", kit.CONTENT_TOP, size=18) - 2
    y = labeled_copy(
        c,
        "Description",
        "Overnight Saturday–Sunday jam co-hosted with the Game Development Club. Doors Saturday 9:00. "
        "Theme, teams, Godot 4, and Ziva Basic before 10:30. Official build is 24 hours "
        "(Sat 10:30 – Sun 10:30). Teams of 2–5 ship a playable Godot prototype. Food is five drops "
        "from the attached Curated Catering campus menu only — no Event Palette items. "
        "Not a sleepover: leave-and-return allowed; a named exec is on site all night. No alcohol.",
        y,
        height=118,
    )
    y = labeled_copy(
        c,
        "Time and Date",
        "Saturday 14 November – Sunday 15 November 2026. Doors Sat 9:00 AM. Official jam "
        "Sat 10:30 AM – Sun 10:30 AM. Judging then teardown to ~1:00 PM Sunday. "
        "Pending SECC, Campus Security, and the 5 October grant intake.",
        y,
        height=56,
    )
    y = labeled_copy(
        c,
        "Proposed Location",
        "Indoor computer-friendly classroom or lab with projector, power, and Wi-Fi "
        "(Stan Grad / Heritage Hall). Weekend and after-hours booking by SECC only. "
        "Overflow if RSVPs exceed ~40.",
        y,
        height=48,
    )
    y = labeled_copy(
        c,
        "Expected Attendance",
        "30 recommended (fully fed, Philippines dinner) / 50 ceiling (pizza dinner). "
        "Engine: Godot 4 (free). AI: Ziva Basic at CAD $28/attendee. Cursor is BYO only. "
        "PEO: VP, Unnatural Intelligence (Pierre Tchio). Game Dev Club is logistics lead "
        "and overnight deputy. Equal budget split.",
        y,
        height=64,
    )
    tmpl.signature_line(c)


def page_agenda(c):
    kit.chrome(c, 3, icon="workflow", badges=["workshop", "live-lab"])
    y = kit.draw_title(c, "Agenda — Saturday 9:00 to Sunday afternoon", kit.CONTENT_TOP, size=16)
    y = text_block(
        c,
        "24 hours of game dev is fixed. Official clock Sat 10:30 – Sun 10:30. Quiet hours 01:00–06:00.",
        y,
        size=8.6,
        lead=11.2,
        color=kit.SLATE,
    )
    y -= 6
    rows = [
        (["Sat 09:00–09:15", "Doors, attendance, power map, both-club sign-ups"], "body"),
        (["Sat 09:15–10:00", "Welcome, rules, secret theme, teams (2–5)"], "body"),
        (["Sat 09:30", "Continental Lite kickoff ($10) — coffee included"], "body"),
        (["Sat 10:00–10:30", "Setup lab: Godot 4 + Ziva Basic redeem"], "body"),
        (["Sat 10:30", "Official start. 24-hour clock begins."], "builtin"),
        (["Sat 12:30", "Lunch boxes drop ($16). Eat at desks."], "body"),
        (["Sat 18:30", "Philippines dinner ($29) · pizza ($6) if 50-person ceiling"], "body"),
        (["Sun 00:00", "Energy bars & bites ($6) midnight drop"], "body"),
        (["Sun 01:00–06:00", "Quiet hours. Leave-and-return. Two-person exec minimum"], "body"),
        (["Sun 08:00", "Signature Breakfast Lite ($12)"], "body"),
        (["Sun 10:30", "Submissions freeze. Godot export + 60-second playable"], "builtin"),
        (["Sun 10:30–13:00", "Judging, results, send-home, exec teardown"], "body"),
    ]
    tmpl.draw_table(
        c,
        y,
        ["Clock", "Segment"],
        [120, kit.CONTENT_W - 120],
        rows,
        min_row_h=24,
    )
    tmpl.signature_line(c)


def page_objectives(c):
    kit.chrome(c, 4, icon="spark", badges=["workshop"])
    y = kit.draw_title(c, "Objectives & labour split", kit.CONTENT_TOP, size=18) - 2
    prompts = [
        "Ship a playable Godot game in 24 hours — every team leaves with a running scene.",
        "Use paid Ziva Basic as a Godot teammate, not as the designer — human finish.",
        "Cross-club recruitment — both clubs sign people up; beginners pair with shippers.",
        "Foundations: untapped (AI in Godot overnight), workflow (a real jam), human finish.",
    ]
    box_h = 48
    for i, prompt in enumerate(prompts, start=1):
        bottom = y - box_h
        c.setFillColor(white)
        c.setStrokeColor(kit.RULE)
        c.setLineWidth(0.8)
        c.roundRect(kit.MARGIN_X, bottom, kit.CONTENT_W, box_h, 8, fill=1, stroke=1)
        c.setFillColor(kit.LIME if i % 2 else kit.PINK)
        c.circle(kit.MARGIN_X + 18, y - 18, 8, fill=1, stroke=0)
        c.setFillColor(kit.INK)
        c.setFont("JetBrains-Bold", 9)
        c.drawCentredString(kit.MARGIN_X + 18, y - 21, str(i))
        c.setFont("Inter", 9)
        ty = y - 18
        for line in kit.wrap(prompt, "Inter", 9, kit.CONTENT_W - 50):
            c.drawString(kit.MARGIN_X + 34, ty, line)
            ty -= 11.4
        y = bottom - 6

    y -= 2
    c.setFillColor(kit.INK)
    c.setFont("Inter-Bold", 11)
    c.drawCentredString(kit.CX, y, "Who does what")
    y -= 12
    tmpl.draw_table(
        c,
        y,
        ["Unnatural Intelligence", "Game Development Club"],
        [kit.CONTENT_W / 2, kit.CONTENT_W / 2],
        [
            (["Files proposal + grant; 50% of cost", "Coordinates logistics via SECC; 50% of cost"], "body"),
            (["Ziva Basic redeem + setup lab", "Godot install, template, export"], "body"),
            (["First draft of judging rubric", "Reviews rubric; co-judges"], "body"),
            (["Named exec on overnight roster", "Named exec on overnight roster"], "body"),
            (["Theme together (secret until Sat 9:15)", "Theme together"], "builtin"),
        ],
        min_row_h=24,
    )
    tmpl.signature_line(c)


def page_menu(c):
    kit.chrome(c, 5, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Campus menu only — attached cards", kit.CONTENT_TOP, size=16)
    y = text_block(
        c,
        "Food quotes are the attached Curated Catering cards, not the Hotel Arts Event Palette. "
        "Order via SECC. SAITevents@hotelarts.ca · 403-210-5774. "
        "Fees card: +18% service + 5% GST (× 1.239). 20% / 50% deposits after grant approval. "
        "Additional staff $30/hr not budgeted. No statutory-holiday surcharge on 14–15 Nov 2026.",
        y,
        size=8.4,
        lead=11,
        color=kit.SLATE,
    )
    y -= 6
    y = tmpl.draw_table(
        c,
        y,
        ["Menu card", "Base", "Loaded", "This jam"],
        [168, 58, 70, kit.CONTENT_W - 296],
        [
            (["Continental Lite", "$10.00", "$12.39", "Sat 9:30 kickoff"], "body"),
            (["Lunch boxes", "$16.00", "$19.82", "Sat 12:30 lunch"], "builtin"),
            (["Taste of the Philippines", "$29.00", "$35.93", "Sat dinner (30 rec.)"], "builtin"),
            (["Taste of Morocco", "$30.00", "$37.17", "Dinner swap (~+$37 / 30)"], "body"),
            (["Pizza, 2 slices", "$6.00", "$7.43", "Sat dinner (50 ceiling)"], "body"),
            (["Energy bars & bites", "$6.00", "$7.43", "Sun 00:00 midnight"], "body"),
            (["Signature Breakfast Lite", "$12.00", "$14.87", "Sun 8:00 breakfast"], "body"),
            (["Sides & add-ons", "$1–$6", "—", "Not used"], "body"),
        ],
        aligns=["left", "right", "right", "left"],
        min_row_h=21,
    )
    y -= 10
    c.setFillColor(kit.INK)
    c.setFont("Inter-Bold", 11)
    c.drawString(kit.MARGIN_X, y, "Paid Ziva Basic — Cursor is not a grant line")
    y -= 12
    y = text_block(
        c,
        "Hobby ($3 usage) will not last 24 hours. Basic is $20 USD/mo = CAD $28.00 "
        "(BoC USD/CAD 1.4002 on 18 Sep 2026) with $20 weekly / $60 monthly usage. "
        "30 × $28 = $840. 50 × $28 = $1,400. Cancel after the jam. "
        "Stay under the weekly cap with Ziva’s free model plus any attendee’s own Claude Code / Codex. "
        "Cursor Pro is the same $20 USD — do not buy 30–50 seats.",
        y,
        size=8.4,
        lead=11,
        color=kit.SLATE,
    )
    y -= 4
    col = kit.CONTENT_W / 3
    tmpl.draw_table(
        c,
        y,
        ["Headcount", "Ziva Basic @ $28", "Five food drops loaded"],
        [col, col, col],
        [
            (["30", "$840", "$2,714 (Philippines dinner)"], "builtin"),
            (["50", "$1,400", "$3,098 (pizza dinner)"], "body"),
        ],
        aligns=["left", "right", "right"],
        min_row_h=24,
    )
    tmpl.signature_line(c)


def page_budget_30(c):
    kit.chrome(c, 6, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Budget A — $4,100 for 30 people", kit.CONTENT_TOP, size=16)
    y = text_block(
        c,
        "Recommended. Five campus-menu drops including Philippines dinner, Ziva Basic for 30, "
        "overnight security placeholder. Split $2,050 / $2,050.",
        y,
        size=8.8,
        lead=11.6,
        color=kit.SLATE,
    )
    y -= 4
    y = budget_table(
        c,
        y,
        [
            ("Posters", "Tabloid 11×17, unaltered Saitsa Clubs logo", POSTER, "builtin"),
            ("Misc", "Tape, markers, unexpected small costs", MISC, "builtin"),
            ("Continental Lite (30)", "Sat kickoff @ $10 pp + 18% + GST", 372, "body"),
            ("Lunch boxes (30)", "Sat lunch @ $16 pp loaded", 595, "body"),
            ("Philippines (30)", "Sat dinner @ $29 pp loaded", 1078, "body"),
            ("Energy bars (30)", "Midnight @ $6 pp loaded", 223, "body"),
            ("Signature Breakfast (30)", "Sun @ $12 pp loaded", 446, "body"),
            ("Ziva Basic (30)", "CAD $28 / attendee, one month then cancel", 840, "body"),
            ("After-hours security", "Placeholder until Security quote", 350, "body"),
            ("Name tags", "Printed club templates", 30, "body"),
            ("Power strips", "Overnight laptop load", 50, "body"),
            ("First aid + buffer", "Overnight kit + dietary / minimums", 101, "body"),
        ],
        total_note="UI $2,050 + Game Dev $2,050. Do not spend before approval.",
    )
    tmpl.signature_line(c)


def page_budget_50(c):
    kit.chrome(c, 7, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Budget B — $5,000 for 50 people", kit.CONTENT_TOP, size=16)
    y = text_block(
        c,
        "Ceiling. Same five drops but pizza dinner ($6) instead of Philippines ($29) — "
        "the $29 buffet at 50 people is $1,797 loaded and does not fit with Ziva Basic. "
        "Split $2,500 / $2,500. Do not go above 50.",
        y,
        size=8.6,
        lead=11.2,
        color=kit.SLATE,
    )
    y -= 4
    y = budget_table(
        c,
        y,
        [
            ("Posters", "Tabloid 11×17, unaltered Saitsa Clubs logo", POSTER, "builtin"),
            ("Misc", "Tape, markers, unexpected small costs", MISC, "builtin"),
            ("Continental Lite (50)", "Sat kickoff @ $10 pp loaded", 620, "body"),
            ("Lunch boxes (50)", "Sat lunch @ $16 pp loaded", 991, "body"),
            ("Pizza (50)", "Sat dinner @ $6 pp loaded (2 slices)", 372, "body"),
            ("Energy bars (50)", "Midnight @ $6 pp loaded", 372, "body"),
            ("Signature Breakfast (50)", "Sun @ $12 pp loaded", 743, "body"),
            ("Ziva Basic (50)", "CAD $28 / attendee, one month then cancel", 1400, "body"),
            ("After-hours security", "Placeholder until Security quote", 250, "body"),
            ("Name tags", "Printed club templates", 50, "body"),
            ("Power strips", "Higher laptop load", 60, "body"),
            ("First aid + buffer", "Overnight kit + dietary / minimums", 127, "body"),
        ],
        total_note="UI $2,500 + Game Dev $2,500. Do not spend before approval.",
    )
    tmpl.signature_line(c)


def page_quotes_food_1(c):
    kit.chrome(c, 8, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Quoted menu — breakfast & lunch", kit.CONTENT_TOP, size=16)
    y = text_block(
        c,
        "Attached Curated Catering cards. Base prices; add 18% + GST (× 1.239).",
        y,
        size=8.4,
        lead=11,
        color=kit.SLATE,
    )
    y -= 4
    y = draw_quote(
        c,
        "buffet-breakfast.png",
        y,
        max_h=210,
        caption="Continental Lite $10 (Sat kickoff) · Signature Breakfast Lite $12 (Sun 8:00). Min 15. Coffee included.",
    )
    y = draw_quote(
        c,
        "lunch-boxes.png",
        y,
        max_h=220,
        caption="Lunch boxes $16. Min 5. 21–50 guests = 2 protein choices. Sat 12:30.",
    )
    tmpl.signature_line(c)


def page_quotes_food_2(c):
    kit.chrome(c, 9, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Quoted menu — dinner & midnight", kit.CONTENT_TOP, size=16)
    y -= 2
    y = draw_quote(
        c,
        "taste-philippines-morocco.png",
        y,
        max_h=128,
        caption="Philippines $29 (30-person dinner) · Morocco $30 (swap). Min 15 guests.",
    )
    y = draw_quote(
        c,
        "pizza.png",
        y,
        max_h=118,
        caption="Pizza $6 / 2 slices. 50-person ceiling dinner. Max four flavours.",
    )
    y = draw_quote(
        c,
        "energy-bars.png",
        y,
        max_h=88,
        caption="Energy bars & bites $6 / 3 pieces. Midnight drop. Min 5 guests.",
    )
    y = draw_quote(
        c,
        "sides-addons.png",
        y,
        max_h=72,
        caption="Sides & add-ons — not used in these budgets.",
    )
    tmpl.signature_line(c)


def page_quotes_fees_ai(c):
    kit.chrome(c, 10, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Quoted fees, Ziva, FX", kit.CONTENT_TOP, size=16)
    y -= 2
    y = draw_quote(
        c,
        "deposit-fees.png",
        y,
        max_h=188,
        caption="18% service + 5% GST on all food. 20% / 50% deposits after grant approval. Staff $30/hr not budgeted.",
    )
    y = draw_quote(
        c,
        "ziva-usage-limits.png",
        y,
        max_h=168,
        caption="Ziva Basic $20 USD / $60 usage — the paid SKU for every attendee. Hobby $3 is too small for 24 hours.",
    )
    y = draw_quote(
        c,
        "boc-usd-cad.png",
        y,
        max_h=96,
        caption="BoC FXUSDCAD 18 Sep 2026 = 1.4002 → USD $20 = CAD $28.00.",
    )
    tmpl.signature_line(c)


def page_logistics(c):
    kit.chrome(c, 11, icon="halt", badges=["workshop", "live-lab"])
    y = kit.draw_title(c, "Logistics, Risk & Compliance", kit.CONTENT_TOP, size=16) - 2
    for text in [
        "Room booking coordinated exclusively by the SECC. Game Dev logistics lead files through them.",
        "Risk: medium. Indoor, no alcohol, no sport — after-hours, fatigue, food, laptops. Written exec roster; PEO or deputy always on site.",
        "After-hours with SECC and Campus Security. Occupants staying after facility hours listed. Booked work session, not an unsanctioned sleepover. Quiet hours 01:00–06:00.",
        "Food only through Curated Catering via SECC, using the attached campus menu cards. Dietary needs on RSVP. Drops 9:30, 12:30, 18:30, 00:00, 08:00.",
        "A/V returned after Sunday teardown (~13:00). Attendance list signed. Posters tabloid 11×17, Saitsa Clubs logo unaltered, $10 built-in.",
        "Disclose the 50/50 sister-club contribution. No spend before approval. Unused grant (including unspent security) is reclaimed.",
        "Ziva Basic is one month of event access, then cancelled — not a member gift. Do not buy Cursor for the room.",
    ]:
        y = kit.bullet_item(c, text, kit.MARGIN_X, y, level=0)

    y -= 6
    c.setFillColor(kit.INK)
    c.setFont("InterDisplay-Bold", 16)
    c.drawCentredString(kit.CX, y, "Promotion Plan")
    y -= 16
    for text in [
        "Posters on Saitsa General Poster Boards (approved submission first).",
        "Both clubs’ Discord, Instagram, Teams, and Rubric RSVP. Cap 50; waitlist after that.",
        "Clubs Fall Expo / Showcase (13–14 October 2026) if the jam is after it.",
        "Pitch: Godot + Ziva Basic, 24 hours, doors Saturday 9:00, meals included, beginners welcome.",
    ]:
        y = kit.bullet_item(c, text, kit.MARGIN_X, y, level=0)

    kit.draw_img(
        c,
        "saitsa-clubs.png",
        kit.PAGE_W - kit.MARGIN_X - 46,
        118,
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
        page_menu,
        page_budget_30,
        page_budget_50,
        page_quotes_food_1,
        page_quotes_food_2,
        page_quotes_fees_ai,
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
