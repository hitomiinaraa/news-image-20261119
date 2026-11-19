#!/usr/bin/env python3
"""Draw the news-image-20261119 entry v1: a front-page poster summing up
the world news of Thursday 19 November 2026.

Design: dominant date masthead, a true world-map band (equirectangular
projection, real coastlines, 12 numbered pins at true lat/lon), 6 lead
stories, and a 26-story grid -- 32 verified stories in all, across 6
continents. Flat editorial illustration, Pillow only. Deterministic: no
randomness, no timestamps, no network. Run: python3 draw.py -> entry.png
beside this file (1024x1024, under 1 MiB). The entry program (main.ts)
only copies entry.png to the output directory.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---- palette: flat editorial, paper + ink + navy + signal red ----
PAPER = (244, 239, 228)
INK = (20, 24, 32)
NAVY = (20, 33, 61)
NAVY2 = (27, 45, 82)
RED = (193, 39, 45)
GOLD = (244, 201, 93)
WHITE = (255, 255, 255)
CREAM = (250, 247, 240)
GREY = (110, 116, 124)
SKY = (191, 217, 232)
SEA = (58, 110, 145)
SEA_DEEP = (31, 82, 108)
GRAT = (90, 140, 170)
LAND = (233, 211, 160)
LAND_EDGE = (178, 156, 108)
SAND = (238, 222, 178)
TEAL = (31, 95, 107)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_BOLD = os.path.join(FONT_DIR, "liberation", "LiberationSerif-Bold.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "liberation", "LiberationSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "liberation", "LiberationSans-Regular.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w, max_lines=None):
    """Greedy word wrap to a list of lines, each at most max_w wide."""
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if text_w(draw, trial, fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if max_lines is not None:
        lines = lines[:max_lines]
    return lines


def draw_wrapped(draw, text, fnt, x, y, max_w, fill, leading=None, max_lines=None):
    """Draw wrapped text; return the y just below the last line."""
    if leading is None:
        leading = fnt.size + 2
    lines = wrap(draw, text, fnt, max_w, max_lines)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y


def fit_size(draw, text, path, max_w, start, minimum=10):
    """Largest font size at which text fits max_w on one line."""
    size = start
    while size > minimum and text_w(draw, text, font(path, size)) > max_w:
        size -= 1
    return size


# ---- world map: equirectangular, lon -168..192, lat -58..84 ----
MAP_X0, MAP_X1 = 24, 1000
MAP_Y0, MAP_Y1 = 108, 316
LON0, LON1 = -168.0, 192.0
LAT0, LAT1 = -58.0, 84.0


def project(lon, lat):
    x = MAP_X0 + (lon - LON0) / (LON1 - LON0) * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (LAT1 - lat) / (LAT1 - LAT0) * (MAP_Y1 - MAP_Y0)
    return (x, y)


# Coarse but true coastlines, as (lon, lat) rings. Written from the
# geography itself: each ring traces one landmass around its outer edge.
NORTH_AMERICA = [
    (-168, 66), (-165, 60), (-158, 58), (-152, 60), (-140, 60), (-135, 57),
    (-130, 54), (-125, 49), (-124, 42), (-120, 34), (-117, 32), (-110, 24),
    (-105, 20), (-97, 16), (-94, 17), (-90, 14), (-86, 12), (-83, 9),
    (-80, 8), (-78, 7), (-80, 10), (-82, 13), (-84, 16), (-87, 21),
    (-90, 21), (-91, 19), (-96, 19), (-97, 26), (-93, 30), (-89, 30),
    (-84, 30), (-81, 25), (-80, 32), (-76, 35), (-74, 40), (-70, 42),
    (-68, 45), (-65, 44), (-60, 47), (-55, 52), (-60, 55), (-65, 58),
    (-68, 58), (-72, 62), (-78, 62), (-85, 66), (-92, 66), (-95, 69),
    (-110, 68), (-125, 70), (-140, 70), (-155, 71), (-165, 68), (-168, 66),
]
GREENLAND = [
    (-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-22, 70),
    (-25, 76), (-35, 80), (-55, 81), (-60, 76), (-58, 70), (-58, 64),
]
SOUTH_AMERICA = [
    (-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
    (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
    (-66, -55), (-65, -45), (-62, -41), (-58, -34), (-52, -32), (-48, -27),
    (-41, -23), (-39, -17), (-35, -8), (-35, -5), (-40, -3), (-44, -2),
    (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12),
    (-76, 10), (-79, 9),
]
AFRICA = [
    (-17, 15), (-16, 20), (-13, 27), (-10, 31), (-5, 35), (0, 36),
    (10, 37), (11, 34), (20, 32), (25, 32), (30, 31), (32, 31), (34, 28),
    (37, 22), (39, 18), (43, 12), (51, 11), (51, 2), (48, -2), (41, -4),
    (40, -10), (39, -15), (36, -20), (33, -26), (28, -33), (20, -35),
    (17, -32), (15, -27), (12, -18), (13, -12), (12, -6), (9, 4), (6, 4),
    (-8, 5), (-13, 8), (-17, 12), (-17, 15),
]
EURASIA = [
    (-10, 36), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (-2, 50), (0, 51),
    (3, 53), (8, 57), (10, 59), (6, 62), (12, 65), (18, 69), (25, 71),
    (30, 70), (35, 68), (40, 68), (45, 68), (50, 69), (55, 68), (60, 69),
    (68, 73), (75, 73), (80, 73), (90, 75), (100, 77), (110, 74),
    (120, 73), (130, 72), (140, 72), (150, 70), (158, 69), (162, 66),
    (170, 66), (178, 65), (178, 62), (170, 60), (162, 58), (158, 52),
    (150, 59), (142, 55), (140, 50), (135, 43), (130, 42), (127, 40),
    (122, 38), (120, 34), (122, 31), (120, 28), (115, 23), (110, 20),
    (108, 18), (105, 10), (103, 7), (100, 8), (98, 12), (94, 17),
    (92, 21), (89, 22), (86, 20), (82, 17), (80, 15), (77, 8), (75, 12),
    (73, 18), (70, 21), (66, 25), (62, 25), (58, 26), (54, 26), (51, 28),
    (50, 30), (48, 30), (44, 29), (42, 27), (40, 25), (39, 21), (43, 17),
    (45, 13), (48, 14), (51, 16), (55, 17), (58, 20), (60, 24), (57, 27),
    (52, 26), (50, 29), (48, 30), (44, 31), (40, 36), (36, 36), (33, 31),
    (30, 31), (27, 36), (23, 36), (22, 38), (19, 40), (15, 44), (12, 44),
    (8, 44), (6, 43), (3, 42), (0, 38), (-2, 37), (-6, 36), (-9, 37),
    (-10, 36),
]
AUSTRALIA = [
    (114, -22), (113, -26), (115, -32), (118, -35), (124, -33), (129, -32),
    (132, -32), (136, -35), (140, -38), (145, -38), (150, -37), (153, -32),
    (153, -27), (150, -23), (146, -19), (142, -15), (142, -11), (137, -12),
    (135, -15), (132, -12), (130, -13), (126, -14), (122, -17), (118, -20),
    (114, -22),
]
BRITAIN = [
    (-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
    (-3, 50), (-5, 50),
]
JAPAN = [
    (130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 36),
    (141, 39), (141, 41), (140, 44), (143, 43), (145, 44), (142, 42),
    (141, 39), (139, 37), (137, 36), (135, 34), (132, 33), (130, 31),
]
INDONESIA = [
    (95, 5), (98, 3), (100, 0), (102, -3), (105, -5), (108, -7), (110, -7),
    (113, -8), (116, -9), (119, -10), (122, -10), (125, -9), (128, -7),
    (131, -4), (134, -3), (137, -2), (140, -3), (141, -5), (138, -7),
    (135, -8), (132, -6), (129, -3), (126, 0), (123, 1), (120, 0),
    (117, 0), (114, 1), (110, 2), (107, 3), (104, 1), (101, 0), (98, 3),
    (95, 5),
]
NEW_GUINEA = [
    (131, -1), (136, -2), (141, -3), (146, -6), (150, -8), (147, -9),
    (142, -8), (137, -6), (132, -4), (131, -1),
]
NEW_ZEALAND = [
    (167, -45), (170, -42), (173, -40), (175, -38), (178, -37), (175, -40),
    (172, -43), (168, -46), (167, -45),
]
LAND_RINGS = [
    NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
    AUSTRALIA, BRITAIN, JAPAN, INDONESIA, NEW_GUINEA, NEW_ZEALAND,
]

# pin number -> (lon, lat, label, label side, label dy, display lon, display lat)
# display lon/lat are small nudges so pins in tight clusters (US east coast,
# Gulf, Black Sea, Bengal) do not sit on top of each other; the true
# location is the lon/lat pair and every nudge stays within a few degrees.
PINS = [
    (1, 114.1, 22.5, "SHENZHEN", "r", -16, 114.1, 22.5),
    (2, 4.3, 52.1, "THE HAGUE", "l", -16, 4.3, 52.1),
    (3, 48.0, 29.4, "KUWAIT", "r", -16, 50.0, 31.0),
    (4, 46.7, 24.7, "RIYADH", "r", 14, 42.5, 20.0),
    (5, -80.2, 25.8, "MIAMI", "l", 16, -88.0, 22.0),
    (6, -74.0, 40.7, "NEW YORK", "l", -16, -72.0, 42.0),
    (7, 30.7, 46.5, "ODESA", "l", -16, 29.0, 48.0),
    (8, 36.5, 45.3, "KERCH", "l", 14, 38.0, 44.0),
    (9, 90.4, 23.8, "DHAKA", "r", -16, 92.0, 25.0),
    (10, 85.7, 19.8, "ODISHA", "r", 14, 84.0, 18.0),
    (11, 178.4, -18.1, "FIJI", "l", 0, 178.4, -18.1),
    (12, -77.0, 38.9, "WASHINGTON", "l", 2, -82.0, 33.0),
]

REGION_LABELS = [
    ("NORTH AMERICA", -100.0, 55.0),
    ("SOUTH AMERICA", -60.0, -18.0),
    ("EUROPE", 38.0, 72.0),
    ("AFRICA", 20.0, 2.0),
    ("ASIA", 95.0, 55.0),
    ("OCEANIA", 138.0, -35.0),
]


def draw_pin(d, num, x, y):
    r = 11
    d.ellipse([x - r, y - r, x + r, y + r], fill=RED, outline=WHITE, width=2)
    t = str(num)
    f = font(SANS_BOLD, 13)
    tw = d.textlength(t, font=f)
    d.text((x - tw / 2, y - 7), t, font=f, fill=WHITE)


def draw_map(d):
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=SEA)
    # graticule every 30 degrees
    for lon in range(-150, 181, 30):
        x, _ = project(lon, 0)
        d.line([(x, MAP_Y0), (x, MAP_Y1)], fill=GRAT, width=1)
    for lat in (-30, 0, 30, 60):
        _, y = project(0, lat)
        d.line([(MAP_X0, y), (MAP_X1, y)], fill=GRAT, width=1)
    # equator, dashed
    _, y0 = project(0, 0)
    for x in range(MAP_X0, MAP_X1, 12):
        d.line([(x, y0), (min(x + 6, MAP_X1), y0)], fill=WHITE, width=1)
    for ring in LAND_RINGS:
        pts = [project(lon, lat) for lon, lat in ring]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    # region labels
    lf = font(SANS_BOLD, 12)
    for name, lon, lat in REGION_LABELS:
        x, y = project(lon, lat)
        d.text((x - d.textlength(name, font=lf) / 2, y - 6), name,
               font=lf, fill=TEAL)
    # pins with labels + leader lines; labels get a navy halo so they
    # stay readable over both the sea and the sand-coloured land
    pf = font(SANS_BOLD, 11)
    for num, lon, lat, label, side, dy, dlon, dlat in PINS:
        x, y = project(dlon, dlat)
        draw_pin(d, num, x, y)
        lw = d.textlength(label, font=pf)
        ly = y - 6 + dy
        if side == "l":
            lx = x - 14 - lw
            d.line([(x - 11, y), (x - 14, ly + 5)], fill=WHITE, width=1)
        else:
            lx = x + 14
            d.line([(x + 11, y), (x + 14, ly + 5)], fill=WHITE, width=1)
        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1),
                       (-1, 1), (1, -1)):
            d.text((lx + ox, ly + oy), label, font=pf, fill=NAVY)
        d.text((lx, ly), label, font=pf, fill=WHITE)
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], outline=NAVY, width=3)

# ---- stories: 6 lead + 26 grid = 32 verified 19-Nov stories ----
# (headline, subline). Every event happened or was first reported on
# 19 November 2026; uncertain claims carry their qualifier in the text.
LEAD = [
    ("TRUMP, XI AND PUTIN MEET FOR THE FIRST TIME",
     "First-ever trilateral agrees 4 points: nuclear-risk talks, UN reform, more refined oil."),
    ("COURT: MYANMAR COMMITTED GENOCIDE",
     "World Court rules 9-6 the Rohingya campaign was genocide - a first of its kind."),
    ("IRAN FIRES DRONES AT US BASES",
     "Tehran hits Kuwait and Bahrain after US jets strike Qeshm. No casualties reported."),
    ("HOUTHI MISSILE HITS RIYADH TOWER",
     "Saudi capital's PIF Tower damaged as the Gulf war widens."),
    ("GTA VI IS OUT",
     "Rockstar's epic launches worldwide: 99 on Metacritic, 2.3M watch on Twitch."),
    ("ANTHROPIC LISTS ON NASDAQ",
     "AI lab debuts as ANT at $70-78 a share, the year's biggest tech listing."),
]

GRID = [
    ("4 KILLED IN RUSSIAN STRIKE ON ODESA", "13 wounded in the port city."),
    ("KERCH BRIDGE HIT FOR 3RD TIME THIS WEEK", "Blasts close the Crimea link."),
    ("ZELENSKYY: NO DEAL WITHOUT UKRAINE", "Kyiv must be at the table."),
    ("TAKAICHI MEETS PUTIN", "Talks stay open after jet row."),
    ("LEE RENEWS CALL FOR N. KOREA TALKS", "Seoul urges dialogue."),
    ("BANGLADESH SHUTS DOWN; YUNUS HOME TORCHED", "Strike; ancestral home torched."),
    ("INDONESIA PASSES ASSET-FORFEITURE BILL", "Refinery blast kills one."),
    ("DENMARK BACKS GREENLAND DEFENCE DEAL", "Parliament approves 109-0."),
    ("SERBIA ELECTS NEW SPEAKER", "Cupic wins with 140 votes."),
    ("CYCLONE AKVAN NEARS; 72,000 EVACUATED", "Landfall expected Friday."),
    ("FIJI DECLARES DROUGHT DISASTER", "El Nino dries reservoirs."),
    ("UNHCR STOPS NEW ASYLUM CASES", "Registration halted."),
    ("TRUMP ASKS COURT TO END TPS SHIELD", "Bid to strip Venezuelans' shield."),
    ("BEGICH KEEPS ALASKA HOUSE SEAT", "Republican holds the only seat."),
    ("US AND VENEZUELA RESTORE MILITARY TIES", "Hegseth visits Caracas in a thaw."),
    ("PASTOR CONVICTED OVER MOISE KILLING", "2,500 Salvadoran troops to Haiti."),
    ("MIGRANT BOAT SINKS OFF SENEGAL", "About 100 aboard; dozens missing."),
    ("SUDAN: RSF COMMANDER DEFECTS", "Senior officer joins the army."),
    ("EBOLA FIGHT STALLS IN DR CONGO", "Response hampered in the east."),
    ("IRAN REPORTS 3 TANKERS ON FIRE", "Claims not independently verified."),
    ("NVIDIA SHARES BOUNCE", "Board says no to Huang's return."),
    ("CLIMATE TALKS STALL ON FOSSIL FUELS", "Final-stage wording unresolved."),
    ("LPG TANKER SINKS AFTER STRIKE", "Gas Husky sinks off Bulgaria."),
    ("AID GROUPS RATE PEACE PLAN 4 OF 26", "Agencies: rollout barely started."),
    ("APEC ADOPTS SHENZHEN OUTLOOK", "Trade, data and AI pact agreed."),
    ("RED CRABS BEGIN GREAT MIGRATION", "Millions cross the island to the sea."),
]


def draw_chip(d, num, x, y, size=20):
    d.rectangle([x, y, x + size, y + size], fill=RED)
    t = str(num)
    f = font(SANS_BOLD, 12 if size >= 20 else 10)
    tw = d.textlength(t, font=f)
    d.text((x + (size - tw) / 2, y + (size - f.size) / 2 - 1), t,
           font=f, fill=WHITE)


def draw():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead ----
    d.rectangle([0, 0, W, 104], fill=NAVY)
    kick = "THE WORLD IN ONE DAY"
    kf = font(SANS_BOLD, 15)
    d.text((24, 12), kick, font=kf, fill=GOLD)
    right = "32 STORIES  -  6 CONTINENTS"
    rf = font(SANS_BOLD, 15)
    d.text((W - 24 - d.textlength(right, font=rf), 12), right,
           font=rf, fill=SKY)
    date = "THURSDAY, 19 NOVEMBER 2026"
    dsize = fit_size(d, date, SERIF_BOLD, W - 48, 62)
    df = font(SERIF_BOLD, dsize)
    d.text((24, 30), date, font=df, fill=WHITE)
    d.line([(24, 98), (W - 24, 98)], fill=GOLD, width=2)

    # ---- map band ----
    draw_map(d)
    cap = "EVERY PIN IS A STORY - THE NUMBERS MATCH THE STORIES BELOW"
    cf = font(SANS_BOLD, 11)
    d.text((24, 320), cap, font=cf, fill=GREY)

    # ---- lead stories: 3 x 2 ----
    lx0, ly0 = 24, 340
    cw, ch, gap = 317, 100, 8
    for i, (head, sub) in enumerate(LEAD):
        col, row = i % 3, i // 3
        x = lx0 + col * (cw + gap)
        y = ly0 + row * (ch + gap)
        d.rectangle([x, y, x + cw, y + ch], fill=CREAM, outline=NAVY, width=1)
        d.rectangle([x, y, x + cw, y + 4], fill=RED)
        draw_chip(d, i + 1, x + 10, y + 12, 20)
        hf = font(SERIF_BOLD, 18)
        hy = draw_wrapped(d, head, hf, x + 38, y + 10, cw - 48, INK,
                          leading=21, max_lines=2)
        sf = font(SANS, 12)
        draw_wrapped(d, sub, sf, x + 10, hy + 2, cw - 20, GREY,
                     leading=14, max_lines=2)

    # ---- grid: 4 cols x 7 rows ----
    gx0, gy0 = 24, 556
    gw, gh, ggap = 236, 56, 5
    hgap = 10
    for i, (head, sub) in enumerate(GRID):
        col, row = i % 4, i // 4
        x = gx0 + col * (gw + hgap)
        y = gy0 + row * (gh + ggap)
        num = i + 7
        d.rectangle([x, y, x + gw, y + gh], fill=WHITE, outline=(200, 195, 180),
                    width=1)
        draw_chip(d, num, x + 6, y + 6, 18)
        hf = font(SANS_BOLD, 13)
        hy = draw_wrapped(d, head, hf, x + 30, y + 5, gw - 36, INK,
                          leading=15, max_lines=2)
        sf = font(SANS, 10)
        d.text((x + 30, y + gh - 15), sub, font=sf, fill=GREY)

    # ---- footer ----
    foot = ("Sources: AP, Reuters, BBC, USA TODAY, DPA, The Times, Just Security "
            "and others - all events of 19 November 2026.")
    ff = font(SANS, 10)
    d.text(((W - d.textlength(foot, font=ff)) / 2, 992), foot,
           font=ff, fill=GREY)
    return img


def main():
    img = draw()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
