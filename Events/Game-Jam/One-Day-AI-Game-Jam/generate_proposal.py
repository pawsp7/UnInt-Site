#!/usr/bin/env python3
"""Filled 2026–27 event proposal: one-day AI Game Jam (Godot × Ziva)."""

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

OUTPUT = HERE / "event-proposal-one-day-AI-game-jam.pdf"

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
    item_w = 108
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
        min_row_h=24,
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
    y = y - h - 12
    if caption:
        c.setFillColor(kit.SLATE)
        c.setFont("Inter", 7.2)
        for line in kit.wrap(caption, "Inter", 7.2, kit.CONTENT_W):
            c.drawString(kit.MARGIN_X, y, line)
            y -= 9.4
    return y - 10


def page_cover(c):
    kit.chrome(c, 1)
    kit.draw_img(c, "jellyfish.png", kit.CX, kit.PAGE_H / 2 + 176, h=132, center=True)
    kit.draw_img(c, "wordmark.png", kit.CX, kit.PAGE_H / 2 + 58, w=236, center=True)
    c.setFillColor(kit.INK)
    c.setFont("InterDisplay-Bold", 26)
    c.drawCentredString(kit.CX, kit.PAGE_H / 2 - 28, "Event Proposal")
    c.setFont("JetBrains-Bold", 11)
    c.setFillColor(kit.WINE)
    c.drawCentredString(kit.CX, kit.PAGE_H / 2 - 52, "One-Day AI Game Jam  ·  Fall 2026")
    c.setFillColor(kit.SLATE)
    c.setFont("Inter-Italic", 11)
    c.drawCentredString(kit.CX, kit.PAGE_H / 2 - 74, "Unnatural Intelligence  ×  Game Development Club")
    c.setFont("Inter", 10)
    c.drawCentredString(kit.CX, kit.PAGE_H / 2 - 94, "Godot 4  ·  Ziva  ·  8 hours  ·  doors 9:00  ·  30–50 people")
    kit.draw_img(c, "tagline.png", kit.CX, kit.PAGE_H / 2 - 140, w=220, center=True)
    kit.badge_row(c, ["workshop", "live-lab", "halt-restart", "clubs-expo"], 148, h=15, gap=8)
    c.setFillColor(kit.SLATE)
    c.setFont("Inter", 8)
    c.drawCentredString(kit.CX, 124, "Saitsa Clubs Portal  ·  portal.hellorubric.com")
    tmpl.signature_line(c, y=88)


def page_overview(c):
    kit.chrome(c, 2, icon="ticket", badges=["workshop", "live-lab"])
    y = kit.draw_title(c, "One-Day AI Game Jam Overview", kit.CONTENT_TOP, size=18) - 2
    y = labeled_copy(
        c,
        "Description",
        "A single Saturday jam co-hosted with the Game Development Club. Doors 9:00. "
        "Theme, teams, Godot 4, and Ziva Hobby before 10:30. Official build time is 8 hours "
        "(10:30–18:30). Teams of 2–5 ship a playable Godot prototype with Ziva inside the editor. "
        "Lunch through Curated Catering / Hotel Arts. Mentors float; judging after freeze. "
        "Same-day send-home by 8:00 PM. No alcohol, no overnight. Cap 30–50.",
        y,
        height=108,
    )
    y = labeled_copy(
        c,
        "Time and Date",
        "Saturday 14 November 2026, 9:00 AM – 8:00 PM. Official jam 10:30 AM – 6:30 PM. "
        "Results ~7:30 PM. Exec teardown to 8:00. Pending SECC and the 5 October grant intake.",
        y,
        height=48,
    )
    y = labeled_copy(
        c,
        "Proposed Location",
        "Indoor computer-friendly classroom or lab with projector, power, and Wi-Fi "
        "(Stan Grad / Heritage Hall). Weekend booking by SECC only. Overflow if RSVPs exceed ~40.",
        y,
        height=48,
    )
    y = labeled_copy(
        c,
        "Expected Attendance",
        "30 core / 50 ceiling. Open to all SAIT students. Engine: Godot 4 (free). "
        "AI: Ziva Hobby (free) inside Godot; optional Ziva Basic at CAD $28. Cursor is BYO / "
        "campus credits only — not purchased for every seat. PEO: VP, Unnatural Intelligence "
        "(Pierre Tchio). Game Dev Club is logistics lead. Equal budget split.",
        y,
        height=64,
    )
    tmpl.signature_line(c)


def page_agenda(c):
    kit.chrome(c, 3, icon="workflow", badges=["workshop", "live-lab"])
    y = kit.draw_title(c, "Agenda — one Saturday", kit.CONTENT_TOP, size=18) - 2
    c.setFillColor(kit.SLATE)
    c.setFont("Inter-Italic", 8.8)
    for line in kit.wrap(
        "Doors 9:00 (was 10:00). 8 hours of game dev is fixed. Teardown by 20:30.",
        "Inter-Italic",
        8.8,
        kit.CONTENT_W,
    ):
        c.drawCentredString(kit.CX, y, line)
        y -= 12
    y -= 6
    rows = [
        (["09:00–09:15", "Doors, attendance, power map, both-club sign-ups"], "body"),
        (["09:15–10:00", "Welcome, rules, secret theme, team formation (2–5)"], "body"),
        (["09:30", "Cookie Jar drop (coffee + pastry) during welcome"], "body"),
        (["10:00–10:30", "Setup lab: install Godot 4, enable Ziva Hobby"], "body"),
        (["10:30", "Official start. 8-hour clock begins."], "builtin"),
        (["10:30–18:30", "Build (8 h). Mentors float. Optional 45-min club tips at 12:00"], "body"),
        (["12:30–13:30", "Catered Working lunch drop. Eat at desks."], "body"),
        (["~15:00", "Optional mid-jam playtest (compressed from the notes’ 90 min review)"], "body"),
        (["18:30", "Submissions freeze. Godot export + 60-second playable build"], "builtin"),
        (["18:30–20:30", "Judging, results, send-home, exec teardown"], "body"),
    ]
    tmpl.draw_table(
        c,
        y,
        ["Clock", "Segment"],
        [100, kit.CONTENT_W - 100],
        rows,
        min_row_h=26,
    )
    tmpl.signature_line(c)


def page_objectives(c):
    kit.chrome(c, 4, icon="spark", badges=["workshop"])
    y = kit.draw_title(c, "Objectives & labour split", kit.CONTENT_TOP, size=18) - 2
    prompts = [
        "Ship a playable Godot game in 8 hours — every team leaves with a running scene.",
        "Use Ziva as a Godot teammate, not as the designer — Hobby default, human finish.",
        "Cross-club recruitment — both clubs sign people up; beginners pair with shippers.",
        "Foundations: untapped (AI in Godot), workflow (a real jam), human finish (it has to play).",
    ]
    box_h = 52
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
        c.setFont("Inter", 9.2)
        ty = y - 20
        for line in kit.wrap(prompt, "Inter", 9.2, kit.CONTENT_W - 50):
            c.drawString(kit.MARGIN_X + 34, ty, line)
            ty -= 12
        y = bottom - 8

    y -= 4
    c.setFillColor(kit.INK)
    c.setFont("Inter-Bold", 11)
    c.drawCentredString(kit.CX, y, "Who does what")
    y -= 14
    tmpl.draw_table(
        c,
        y,
        ["Unnatural Intelligence", "Game Development Club"],
        [kit.CONTENT_W / 2, kit.CONTENT_W / 2],
        [
            (["Files proposal + grant; 50% of cost", "Coordinates logistics via SECC; 50% of cost"], "body"),
            (["Ziva Hobby setup lab (optional Basic)", "Godot install, project template, export"], "body"),
            (["First draft of judging rubric", "Reviews rubric; co-judges"], "body"),
            (["2–5 guest speakers / judges", "2–5 guest speakers / judges"], "body"),
            (["Theme decided together (secret until 9:15)", "Theme decided together"], "builtin"),
        ],
        min_row_h=26,
    )
    tmpl.signature_line(c)


def page_menu_ai(c):
    kit.chrome(c, 5, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Catering menu & Godot AI", kit.CONTENT_TOP, size=16)
    y = text_block(
        c,
        "Built-in floor: $10 posters + $5 misc. Food only through Curated Catering powered by "
        "Hotel Arts, via SECC. Everyday menu 72-hour lead. Quote: SAITevents@hotelarts.ca · 403-210-5774. "
        "Prices from the Hotel Arts Event Palette × 18% service × 5% GST (× 1.239). "
        "Quoted pages: quotes/hotel-arts-working.png and quotes/hotel-arts-cookie-jar.png.",
        y,
        size=8.6,
        lead=11.2,
        color=kit.SLATE,
    )
    y -= 6
    y = tmpl.draw_table(
        c,
        y,
        ["Menu item", "Base", "Loaded / person", "This jam"],
        [200, 70, 88, kit.CONTENT_W - 358],
        [
            (["Cookie Jar (pastry + coffee)", "$12.00", "$14.87", "Kickoff ~9:30"], "body"),
            (["Working sandwich + fruit + coffee", "$24.00", "$29.74", "Saturday lunch"], "builtin"),
            (["Coffee & tea only", "$3.75", "$4.65", "Skip — Cookie Jar includes it"], "body"),
            (["Continental breakfast", "$22.00", "$27.26", "Not used (no Sunday)"], "body"),
        ],
        aligns=["left", "right", "right", "left"],
        min_row_h=22,
    )
    y -= 12
    c.setFillColor(kit.INK)
    c.setFont("Inter-Bold", 11)
    c.drawString(kit.MARGIN_X, y, "Ziva in Godot — Cursor is optional, not the grant line")
    y -= 14
    y = text_block(
        c,
        "Godot 4 is free and 2D-first. Ziva runs inside the editor (scene tree, errors, running game). "
        "Hobby is free: $3/mo premium usage + unlimited free model. Basic is $20 USD/mo = CAD $28.00 "
        "at Bank of Canada USD/CAD 1.4002 (18 Sep 2026). Cursor Pro is the same $20 USD, but it is a "
        "text editor — no live scene tree without MCP. Buying both is CAD $56/person. Recommendation: "
        "Ziva Hobby for everyone. Upgrade to Ziva Basic only if a 30-minute Hobby test fails. "
        "Cursor: BYO or campus credits (hi@cursor.com), never 30–50 paid seats.",
        y,
        size=8.6,
        lead=11.2,
        color=kit.SLATE,
    )
    y -= 6
    col = kit.CONTENT_W / 4
    tmpl.draw_table(
        c,
        y,
        ["Headcount", "Ziva Hobby", "Ziva Basic @ $28", "Working lunch"],
        [col, col, col, col],
        [
            (["30", "$0", "$840", "$892"], "builtin"),
            (["50", "$0", "$1,400", "$1,487"], "body"),
        ],
        aligns=["left", "right", "right", "right"],
        min_row_h=24,
    )
    tmpl.signature_line(c)


def page_budget_30(c):
    kit.chrome(c, 6, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Budget A — $1,500 for 30 people", kit.CONTENT_TOP, size=16)
    y = text_block(
        c,
        "Recommended. Lunch + kickoff Cookie Jar + Ziva Hobby (free) for 30. Split $750 / $750. "
        "Lunch-only alt (no Cookie Jar): $1,000 ($500 each). Paid-AI alt (Ziva Basic × 30): $2,300 "
        "($1,150 each) — same dollars the Cursor notes used, spent on Ziva instead.",
        y,
        size=9,
        lead=12,
        color=kit.SLATE,
    )
    y -= 6
    y = budget_table(
        c,
        y,
        [
            ("Posters", "Tabloid 11×17, unaltered Saitsa Clubs logo", POSTER, "builtin"),
            ("Misc", "Tape, markers, unexpected small costs", MISC, "builtin"),
            ("Working lunch (30)", "Hotel Arts Working @ $24 pp + 18% + GST", 892, "body"),
            ("Cookie Jar (30)", "Kickoff coffee + pastry @ $12 pp loaded", 446, "body"),
            ("Ziva Hobby (30)", "Free in-editor Godot agent", 0, "body"),
            ("Name tags", "Printed club templates", 30, "body"),
            ("Power strips", "Classroom laptop load", 40, "body"),
            ("Quote buffer", "Dietary / minimums", 77, "body"),
        ],
        total_note="UI $750 + Game Dev $750. Do not spend before approval.",
    )
    y -= 14
    y = text_block(
        c,
        "Do not add Cursor Pro × 30 ($840). If campus credits land, they are a bonus IDE. "
        "Test Ziva Hobby before the 5 October intake; bump to Basic only if Hobby cannot ship a tiny scene.",
        y,
        size=9,
        lead=12,
        color=kit.SLATE,
    )
    tmpl.signature_line(c)


def page_budget_50(c):
    kit.chrome(c, 7, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Budget B — $2,400 for 50 people", kit.CONTENT_TOP, size=16)
    y = text_block(
        c,
        "Ceiling on Ziva Hobby. Split $1,200 / $1,200. Lunch-only alt: $1,650 ($825 each). "
        "Paid-AI alt (Ziva Basic × 50): $3,800 ($1,900 each). Do not go above 50. No Cursor seats.",
        y,
        size=9,
        lead=12,
        color=kit.SLATE,
    )
    y -= 6
    y = budget_table(
        c,
        y,
        [
            ("Posters", "Tabloid 11×17, unaltered Saitsa Clubs logo", POSTER, "builtin"),
            ("Misc", "Tape, markers, unexpected small costs", MISC, "builtin"),
            ("Working lunch (50)", "@ $24 pp loaded", 1487, "body"),
            ("Cookie Jar (50)", "Kickoff @ $12 pp loaded", 743, "body"),
            ("Ziva Hobby (50)", "Free in-editor Godot agent", 0, "body"),
            ("Name tags", "Printed club templates", 50, "body"),
            ("Power strips", "Higher laptop load", 50, "body"),
            ("First aid + buffer", "Dietary / minimums", 55, "body"),
        ],
        total_note="UI $1,200 + Game Dev $1,200. Do not spend before approval.",
    )
    y -= 12
    c.setFillColor(kit.INK)
    c.setFont("Inter-Bold", 11)
    c.drawString(kit.MARGIN_X, y, "Judging rubric — UI draft, Game Dev to review")
    y -= 12
    tmpl.draw_table(
        c,
        y,
        ["Criterion (1–5)", "What a 5 looks like"],
        [130, kit.CONTENT_W - 130],
        [
            (["Playable", "A stranger runs it in 60 seconds without an exec at the keyboard"], "body"),
            (["Theme", "The secret theme is readable in play, not only in the title"], "body"),
            (["Godot craft", "Scenes/nodes/signals on purpose; not one 2,000-line script"], "body"),
            (["AI as tool", "Ziva helped; the team can show what they kept vs threw away"], "body"),
            (["Human finish", "Scope cut, juiced, playable loop — not a dumped agent transcript"], "builtin"),
        ],
        min_row_h=22,
    )
    tmpl.signature_line(c)


def page_quotes_ai(c):
    kit.chrome(c, 8, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Quoted prices — Ziva & Cursor", kit.CONTENT_TOP, size=16)
    y = text_block(
        c,
        "Direct captures, 20 Sep 2026. Full files: Events/One-Day-AI-Game-Jam/quotes/.",
        y,
        size=8.4,
        lead=11,
        color=kit.SLATE,
    )
    y -= 4
    y = draw_quote(
        c,
        "ziva-usage-limits.png",
        y,
        max_h=268,
        caption="ziva.sh/docs/usage-limit-best-practices — Hobby $3 usage (free plan); Basic $20 / $60.",
    )
    y = draw_quote(
        c,
        "cursor-pricing.png",
        y,
        max_h=158,
        caption="cursor.com/pricing — Pro USD $20/mo. Cited to show why we are not buying 30 seats.",
    )
    tmpl.signature_line(c)


def page_quotes_working(c):
    kit.chrome(c, 9, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Quoted prices — Working lunch", kit.CONTENT_TOP, size=16)
    y = text_block(
        c,
        "Hotel Arts Event Palette p.5 (same caterer as campus). Working $24 / person. "
        "Footer: prices do not include 18% service charge or 5% GST (× 1.239). Pending a live SECC quote.",
        y,
        size=8.4,
        lead=11,
        color=kit.SLATE,
    )
    y -= 4
    y = draw_quote(
        c,
        "hotel-arts-working.png",
        y,
        max_h=360,
        caption="docslib.org copy of Hotel Arts Event Palette — Working $24 / person (Saturday lunch planning figure).",
    )
    y = draw_quote(
        c,
        "boc-usd-cad.png",
        y,
        max_h=108,
        caption="Bank of Canada FXUSDCAD 18 Sep 2026 = 1.4002 → USD $20 = CAD $28.00.",
    )
    tmpl.signature_line(c)


def page_quotes_cookie(c):
    kit.chrome(c, 10, icon="token", badges=["exec"])
    y = kit.draw_title(c, "Quoted prices — Cookie Jar & caterer", kit.CONTENT_TOP, size=16)
    y = text_block(
        c,
        "Event Palette p.10 Cookie Jar $12 / person (kickoff ~9:30). Campus food must go through "
        "Curated Catering powered by Hotel Arts.",
        y,
        size=8.4,
        lead=11,
        color=kit.SLATE,
    )
    y -= 4
    y = draw_quote(
        c,
        "hotel-arts-cookie-jar.png",
        y,
        max_h=300,
        caption="Event Palette p.10 — Cookie Jar $12 / person; coffee $3.75 / person.",
    )
    y = draw_quote(
        c,
        "sait-catertrax.png",
        y,
        max_h=168,
        caption="saitcatering.catertrax.com — SAITevents@hotelarts.ca · 403-210-5774 · Mon–Fri 7:30 AM–3:30 PM.",
    )
    tmpl.signature_line(c)


def page_logistics(c):
    kit.chrome(c, 11, icon="halt", badges=["workshop", "live-lab"])
    y = kit.draw_title(c, "Logistics, Risk & Compliance", kit.CONTENT_TOP, size=16) - 2
    for text in [
        "Room booking coordinated exclusively by the SECC. Game Dev logistics lead files through them.",
        "Risk: low. Indoor Saturday, no alcohol, no overnight, no sport. PEO on site the whole time.",
        "Food and beverages only through SAIT’s approved caterer (Curated Catering / Hotel Arts) via SECC. Drops 9:30 and 12:30.",
        "A/V picked up from SECC and returned after teardown (~20:30).",
        "Attendance list for the event report. Posters: tabloid 11×17, Saitsa Clubs logo unaltered, $10 built-in. Down within 48 hours.",
        "Disclose the 50/50 sister-club contribution to the SECC. If this is classed as a social event, grant funds must already be in the account before the event proposal. No spend before approval.",
        "Ziva Hobby is free. If we buy Ziva Basic, it is one month of event access, then cancelled — not a member gift. Do not buy Cursor for the room.",
    ]:
        y = kit.bullet_item(c, text, kit.MARGIN_X, y, level=0)

    y -= 8
    c.setFillColor(kit.INK)
    c.setFont("InterDisplay-Bold", 16)
    c.drawCentredString(kit.CX, y, "Promotion Plan")
    y -= 18
    for text in [
        "Posters on Saitsa General Poster Boards (approved submission first).",
        "Both clubs’ Discord, Instagram, Teams, and Rubric RSVP. Cap 50; waitlist after that.",
        "Clubs Fall Expo / Showcase (13–14 October 2026) if the jam is after it.",
        "Pitch: Godot + Ziva, 8 hours, doors 9:00, lunch included, beginners welcome.",
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
    c.setTitle("One-Day AI Game Jam — Event Proposal")
    c.setAuthor("Unnatural Intelligence")
    c.setSubject("Saitsa student club event proposal — Fall 2026")

    pages = [
        page_cover,
        page_overview,
        page_agenda,
        page_objectives,
        page_menu_ai,
        page_budget_30,
        page_budget_50,
        page_quotes_ai,
        page_quotes_working,
        page_quotes_cookie,
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
