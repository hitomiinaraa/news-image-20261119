#!/usr/bin/env python3
"""Draw the news-image-20261119 entry v3: a picture newspaper summing up
the world news of Thursday 19 November 2026.

DIAGNOSIS (from viewing 7 of the top 10 entries' images live: #1
hazel-harbor-63, #2 izayoi-20, #4 lomfi, #8 kbara, #9 aryanpatelx,
#10 ipot, #12 hazel-kestrel-79): every top entry is a PICTURE paper --
3 large drawn hero scenes + 8-10 smaller drawn scenes, a big-number
strip, a region-count strip, per-story source attributions, and a DATE
CHECK box naming the near-miss stories it deliberately left out. Our
v2 was text-only cells plus a reference map (dev 0.9796, #954), and
#4 lomfi ranks #4 with only 19 stories -- density is not the driver,
pictures are. v3 therefore rebuilds the page as a picture paper: 3
hero illustrations + 8 mid illustrations, number strip, region strip,
sources on every story, and a DATE CHECK box. Story list: 33 verified
19-Nov stories (3 heroes + 8 mids + 22 briefs). The map is redrawn
fresh and simplified for the small box; coastlines are coarse but true.

Flat editorial illustration, Pillow only. Deterministic: no
randomness, no timestamps, no network. Run: python3 draw.py ->
entry.png beside this file (1024x1024, under 1 MiB). The entry
program (main.ts) only copies entry.png to the output directory.
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
TEAL = (31, 95, 107)
GREEN_DK = (24, 77, 54)
GREEN = (46, 125, 50)
ORANGE = (214, 110, 44)
PURPLE = (88, 60, 122)
SKIN = (232, 190, 150)
SKIN2 = (205, 155, 115)
SKIN3 = (170, 120, 85)
SUIT = (35, 42, 58)
BROWN = (122, 84, 52)
OLIVE = (107, 122, 44)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_BOLD = os.path.join(FONT_DIR, "liberation", "LiberationSerif-Bold.ttf")
SERIF_ITALIC = os.path.join(FONT_DIR, "liberation", "LiberationSerif-Italic.ttf")
SANS_BOLD = os.path.join(FONT_DIR, "liberation", "LiberationSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "liberation", "LiberationSans-Regular.ttf")


def font(path, size):
    return ImageFont.truetype(path, size)


def font_or(path, fallback, size):
    return ImageFont.truetype(path if os.path.exists(path) else fallback, size)


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


def draw_wrapped(draw, text, fnt, x, y, max_w, fill, leading=None,
                 max_lines=None):
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


def star(d, cx, cy, r_out, r_in, fill):
    """Five-point star as a polygon."""
    import math
    pts = []
    for i in range(10):
        r = r_out if i % 2 == 0 else r_in
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=fill)


# ---- world map: equirectangular, lon -168..192, lat -58..84 ----
# Simplified coastlines traced fresh for the small map box: coarse
# but recognisable landmasses.
MAP_X0, MAP_X1 = 24, 296
MAP_Y0, MAP_Y1 = 604, 792
LON0, LON1 = -168.0, 192.0
LAT0, LAT1 = -58.0, 84.0


def project(lon, lat):
    x = MAP_X0 + (lon - LON0) / (LON1 - LON0) * (MAP_X1 - MAP_X0)
    y = MAP_Y0 + (LAT1 - lat) / (LAT1 - LAT0) * (MAP_Y1 - MAP_Y0)
    return (x, y)


NORTH_AMERICA = [
    (-168, 66), (-158, 58), (-140, 60), (-130, 54), (-124, 42),
    (-117, 32), (-105, 20), (-94, 17), (-86, 12), (-80, 8),
    (-83, 9), (-87, 21), (-96, 19), (-97, 26), (-89, 30),
    (-81, 25), (-76, 35), (-70, 42), (-65, 44), (-60, 47),
    (-55, 52), (-65, 58), (-78, 62), (-92, 66), (-110, 68),
    (-125, 70), (-155, 71), (-168, 66),
]
GREENLAND = [
    (-58, 64), (-43, 60), (-32, 68), (-22, 70), (-35, 80),
    (-55, 81), (-60, 76), (-58, 70), (-58, 64),
]
SOUTH_AMERICA = [
    (-79, 9), (-80, -3), (-77, -12), (-70, -23), (-72, -37),
    (-70, -54), (-65, -45), (-58, -34), (-48, -27), (-39, -17),
    (-35, -8), (-44, -2), (-53, 4), (-62, 9), (-72, 12), (-79, 9),
]
AFRICA = [
    (-17, 15), (-10, 31), (0, 36), (11, 34), (25, 32),
    (32, 31), (37, 22), (43, 12), (51, 11), (48, -2),
    (40, -10), (36, -20), (28, -33), (20, -35), (15, -27),
    (12, -18), (9, 4), (-8, 5), (-17, 12), (-17, 15),
]
EURASIA = [
    (-10, 36), (-9, 43), (-2, 44), (-4, 48), (0, 51),
    (8, 57), (6, 62), (18, 69), (30, 70), (45, 68),
    (60, 69), (75, 73), (100, 77), (130, 72), (158, 69),
    (178, 65), (162, 58), (142, 55), (130, 42), (122, 38),
    (115, 23), (105, 10), (100, 8), (94, 17), (89, 22),
    (80, 15), (77, 8), (73, 18), (66, 25), (58, 26),
    (51, 28), (48, 30), (44, 29), (42, 27), (39, 21),
    (45, 13), (51, 16), (58, 20), (57, 27), (50, 29),
    (40, 36), (36, 36), (30, 31), (27, 36), (23, 36),
    (19, 40), (12, 44), (6, 43), (0, 38), (-6, 36), (-10, 36),
]
AUSTRALIA = [
    (114, -22), (115, -32), (124, -33), (136, -35), (145, -38),
    (153, -32), (150, -23), (142, -15), (137, -12), (130, -13),
    (122, -17), (114, -22),
]
BRITAIN = [
    (-5, 50), (-3, 53), (-5, 56), (-3, 58), (0, 53), (1, 51), (-3, 50),
]
JAPAN = [
    (130, 31), (134, 34), (138, 35), (141, 39), (140, 44),
    (143, 43), (141, 39), (137, 36), (132, 33), (130, 31),
]
INDONESIA = [
    (95, 5), (100, 0), (105, -5), (110, -7), (116, -9),
    (122, -10), (128, -7), (134, -3), (141, -5), (135, -8),
    (129, -3), (123, 1), (117, 0), (110, 2), (104, 1), (98, 3), (95, 5),
]
NEW_GUINEA = [
    (131, -1), (136, -2), (141, -3), (146, -6), (150, -8),
    (142, -8), (132, -4), (131, -1),
]
NEW_ZEALAND = [
    (167, -45), (170, -42), (173, -40), (175, -38), (178, -37),
    (172, -43), (168, -46), (167, -45),
]
LAND_RINGS = [
    NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
    AUSTRALIA, BRITAIN, JAPAN, INDONESIA, NEW_GUINEA, NEW_ZEALAND,
]

# pin number -> (lon, lat, label, side, dy, display lon, display lat)
# Story 4 (GTA VI, worldwide) has no single place, so it has no pin;
# the caption says so. Display lon/lat nudge pins in tight clusters
# (Kerch/Antalya/Riyadh sit within a few degrees of each other); the
# true location is the lon/lat pair and every nudge stays within ~8
# degrees, the same convention as v2.
PINS = [
    (1, 114.1, 22.5, "SHENZHEN", "r", -8, 114.1, 22.5),
    (2, 4.3, 52.1, "THE HAGUE", "l", -8, 4.3, 52.1),
    (3, 30.7, 36.9, "ANTALYA", "r", 10, 34.0, 32.0),
    (5, -74.0, 40.7, "NEW YORK", "l", -8, -72.0, 42.0),
    (6, 36.5, 45.3, "KERCH", "l", 8, 28.0, 52.0),
    (7, 46.7, 24.7, "RIYADH", "r", 10, 48.0, 20.0),
    (8, 85.7, 19.8, "ODISHA", "r", -8, 87.0, 21.0),
    (9, 127.0, 37.5, "SEOUL", "r", -8, 127.0, 37.5),
    (10, -74.1, 4.6, "BOGOTA", "r", 10, -74.1, 4.6),
    (11, 149.1, -35.3, "CANBERRA", "l", 10, 149.1, -35.3),
]


def draw_pin(d, num, x, y):
    r = 8
    d.ellipse([x - r, y - r, x + r, y + r], fill=RED, outline=WHITE, width=2)
    t = str(num)
    f = font(SANS_BOLD, 10)
    tw = d.textlength(t, font=f)
    d.text((x - tw / 2, y - 5), t, font=f, fill=WHITE)


def draw_map(d):
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], fill=SEA)
    for lon in range(-150, 181, 30):
        x, _ = project(lon, 0)
        d.line([(x, MAP_Y0), (x, MAP_Y1)], fill=GRAT, width=1)
    for lat in (-30, 0, 30, 60):
        _, y = project(0, lat)
        d.line([(MAP_X0, y), (MAP_X1, y)], fill=GRAT, width=1)
    _, y0 = project(0, 0)
    for x in range(MAP_X0, MAP_X1, 10):
        d.line([(x, y0), (min(x + 5, MAP_X1), y0)], fill=WHITE, width=1)
    for ring in LAND_RINGS:
        pts = [project(lon, lat) for lon, lat in ring]
        d.polygon(pts, fill=LAND, outline=LAND_EDGE)
    # Pins carry numbers only -- the numbered list beside the map gives
    # every place. Text labels on a 272px map collide in the Black Sea /
    # Gulf / Bengal clusters (v3 first render), and the top entries do
    # the same: numbered pins on the map, places in the list.
    for num, lon, lat, label, side, dy, dlon, dlat in PINS:
        x, y = project(dlon, dlat)
        draw_pin(d, num, x, y)
    d.rectangle([MAP_X0, MAP_Y0, MAP_X1, MAP_Y1], outline=NAVY, width=2)

# ---- drawn illustrations: flat vector scenes, all drawn in code ----
# Each scene function takes (draw, x0, y0, w, h) and draws inside that box.

def flag_us(d, x, y, w, h):
    for i in range(7):
        d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                    fill=RED if i % 2 == 0 else WHITE)
    cw, ch = w * 0.4, h * 4 / 7
    d.rectangle([x, y, x + cw, y + ch], fill=NAVY2)
    for r in range(3):
        for c in range(4):
            d.ellipse([x + 3 + c * cw / 4.5, y + 2 + r * ch / 3.5,
                       x + 5 + c * cw / 4.5, y + 4 + r * ch / 3.5],
                      fill=WHITE)


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=RED)
    star(d, x + w * 0.2, y + h * 0.3, h * 0.18, h * 0.07, GOLD)
    for sx, sy in ((0.48, 0.18), (0.58, 0.32), (0.55, 0.5), (0.4, 0.5)):
        star(d, x + w * sx, y + h * sy, h * 0.07, h * 0.03, GOLD)


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=WHITE)
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 87, 184))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=RED)


def figure(d, cx, base_y, skin, suit=SUIT, scale=1.0):
    """Seated figure: head + shoulders, seen from the front."""
    hr = 11 * scale
    d.ellipse([cx - hr, base_y - 52 * scale, cx + hr, base_y - 30 * scale],
              fill=skin)
    d.polygon([(cx - 20 * scale, base_y), (cx - 13 * scale, base_y - 34 * scale),
               (cx + 13 * scale, base_y - 34 * scale), (cx + 20 * scale, base_y)],
              fill=suit)
    d.polygon([(cx - 3 * scale, base_y - 32 * scale), (cx + 3 * scale, base_y - 32 * scale),
               (cx, base_y - 14 * scale)], fill=RED)


def nameplate(d, cx, y, text):
    f = font(SANS_BOLD, 9)
    tw = d.textlength(text, font=f)
    d.rectangle([cx - tw / 2 - 6, y, cx + tw / 2 + 6, y + 14], fill=WHITE,
                outline=NAVY, width=1)
    d.text((cx - tw / 2, y + 2), text, font=f, fill=INK)


def scene_summit(d, x0, y0, w, h):
    """Three leaders at one table: flags behind, nameplates in front."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=NAVY2)
    d.rectangle([x0, y0, x0 + w, y0 + 8], fill=GOLD)
    fw, fh = 52, 30
    flag_us(d, x0 + 22, y0 + 16, fw, fh)
    flag_cn(d, x0 + w / 2 - fw / 2, y0 + 16, fw, fh)
    flag_ru(d, x0 + w - 22 - fw, y0 + 16, fw, fh)
    ty = y0 + h - 26
    d.ellipse([x0 + 14, ty - 6, x0 + w - 14, ty + 22], fill=BROWN)
    d.rectangle([x0 + 14, ty + 6, x0 + w - 14, y0 + h], fill=(96, 64, 40))
    figure(d, x0 + 52, ty + 2, SKIN)
    figure(d, x0 + w / 2, ty + 2, SKIN2)
    figure(d, x0 + w - 52, ty + 2, SKIN3)
    nameplate(d, x0 + 52, y0 + h - 15, "TRUMP")
    nameplate(d, x0 + w / 2, y0 + h - 15, "XI")
    nameplate(d, x0 + w - 52, y0 + h - 15, "PUTIN")


def scene_court(d, x0, y0, w, h):
    """World Court building + scales of justice + 9-6 badge."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=SKY)
    bx, by, bw, bh = x0 + 12, y0 + 26, 150, 62
    d.polygon([(bx, by), (bx + bw / 2, by - 18), (bx + bw, by)], fill=(196, 172, 138))
    d.rectangle([bx, by, bx + bw, by + bh], fill=(232, 222, 200))
    for i in range(4):
        cx = bx + 18 + i * 38
        d.rectangle([cx, by + 8, cx + 10, by + bh - 10], fill=WHITE,
                    outline=(160, 150, 130), width=1)
    d.rectangle([bx - 4, by + bh - 10, bx + bw + 4, by + bh - 4], fill=(196, 172, 138))
    d.rectangle([bx - 8, by + bh - 4, bx + bw + 8, by + bh + 2], fill=(170, 146, 112))
    # scales, right side
    sx, sy = x0 + w - 62, y0 + 30
    d.line([(sx, sy - 6), (sx, sy + 44)], fill=INK, width=3)
    d.line([(sx - 26, sy), (sx + 26, sy)], fill=INK, width=3)
    for dx in (-26, 26):
        d.line([(sx + dx, sy), (sx + dx, sy + 16)], fill=INK, width=2)
        d.polygon([(sx + dx - 12, sy + 16), (sx + dx + 12, sy + 16),
                   (sx + dx, sy + 30)], fill=GOLD, outline=INK)
    d.ellipse([sx - 5, sy - 11, sx + 5, sy - 1], fill=GOLD, outline=INK)
    bf = font(SANS_BOLD, 20)
    bw2, bh2 = 52, 30
    d.rectangle([x0 + w - bw2 - 8, y0 + h - bh2 - 6, x0 + w - 8, y0 + h - 6],
                fill=RED)
    t = "9-6"
    d.text((x0 + w - bw2 - 8 + (bw2 - d.textlength(t, font=bf)) / 2,
            y0 + h - bh2 - 2), t, font=bf, fill=WHITE)


def scene_cop31(d, x0, y0, w, h):
    """Globe + thermometer + the draft deal with FOSSIL FUELS struck out."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=TEAL)
    gx, gy, gr = x0 + 48, y0 + 52, 34
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(64, 164, 200),
              outline=WHITE, width=2)
    d.ellipse([gx - 22, gy - 18, gx + 2, gy + 2], fill=GREEN)
    d.ellipse([gx + 4, gy + 6, gx + 24, gy + 24], fill=GREEN)
    d.ellipse([gx - 6, gy - 28, gx + 14, gy - 12], fill=GREEN)
    d.arc([gx - gr, gy - gr, gx + gr, gy + gr], 200, 340, fill=WHITE, width=1)
    # thermometer
    tx = x0 + 108
    d.rectangle([tx, y0 + 14, tx + 12, y0 + h - 22], fill=WHITE)
    d.ellipse([tx - 5, y0 + h - 30, tx + 17, y0 + h - 8], fill=RED)
    d.rectangle([tx + 3, y0 + 30, tx + 9, y0 + h - 20], fill=RED)
    # draft paper, right
    px, py, pw, ph = x0 + 138, y0 + 12, 164, 82
    d.rectangle([px, py, px + pw, py + ph], fill=WHITE, outline=NAVY, width=2)
    tf = font(SANS_BOLD, 10)
    d.text((px + 8, py + 6), "DRAFT DEAL - 19 NOV", font=tf, fill=GREY)
    ff = font(SANS_BOLD, 17)
    d.text((px + 8, py + 26), "FOSSIL FUELS", font=ff, fill=INK)
    d.line([(px + 6, py + 36), (px + 8 + d.textlength("FOSSIL FUELS", font=ff),
             py + 36)], fill=RED, width=3)
    sf = font(SANS_BOLD, 11)
    d.text((px + 8, py + 48), "$120BN ADAPTATION AID", font=sf, fill=INK)
    d.line([(px + 6, py + 56), (px + 8 + d.textlength("$120BN ADAPTATION AID", font=sf),
             py + 56)], fill=RED, width=2)
    d.text((px + 8, py + 64), "CUT", font=font(SANS_BOLD, 13), fill=RED)
    d.rectangle([px + 6, py + 62, px + 44, py + 80], outline=RED, width=2)


def scene_gta(d, x0, y0, w, h):
    """Vice City sunset skyline + game controller."""
    for i, c in enumerate([(88, 60, 122), (140, 70, 130), (214, 110, 90),
                           (244, 160, 80)]):
        d.rectangle([x0, y0 + i * h / 4, x0 + w, y0 + (i + 1) * h / 4], fill=c)
    d.ellipse([x0 + w - 40, y0 + 3, x0 + w - 12, y0 + 3 + (h - 6)], fill=GOLD)
    base = y0 + h
    for bx, bw, frac in ((0, 26, 0.55), (30, 18, 0.85), (52, 30, 0.65),
                         (86, 16, 0.95), (106, 34, 0.75), (144, 20, 0.95),
                         (168, 28, 0.6), (200, 18, 0.85), (222, 14, 0.65)):
        bh = int(frac * (h - 2))
        d.rectangle([x0 + bx, base - bh, x0 + bx + bw, base], fill=(40, 28, 58))
    cx, cy = x0 + w / 2, y0 + h - 12
    d.ellipse([cx - 34, cy - 12, cx + 34, cy + 12], fill=(30, 30, 40))
    d.rectangle([cx - 34, cy - 6, cx + 34, cy + 6], fill=(30, 30, 40))
    d.line([(cx - 24, cy), (cx - 12, cy)], fill=WHITE, width=3)
    d.line([(cx - 18, cy - 6), (cx - 18, cy + 6)], fill=WHITE, width=3)
    for dx, dy, c in ((14, -5, (255, 220, 0)), (22, 2, RED), (14, 6, GREEN),
                      (6, 0, (0, 140, 220))):
        d.ellipse([cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3], fill=c)
    vf = font(SERIF_BOLD, 22)
    d.text((x0 + 8, y0 + 4), "VI", font=vf, fill=WHITE)


def scene_nasdaq(d, x0, y0, w, h):
    """Rising candlestick chart on dark green, $83 tag."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=GREEN_DK)
    # Candles as fractions of the strip height so nothing bleeds past
    # the box (the first version's wicks crossed into the headline).
    span = h - 8
    candles = [(8, 0.75, 0.35), (34, 0.65, 0.45), (60, 0.55, 0.30),
               (86, 0.70, 0.50), (112, 0.40, 0.40), (138, 0.50, 0.55),
               (164, 0.30, 0.45), (190, 0.20, 0.50)]
    prev = None
    for bx, top_f, bh_f in candles:
        top = y0 + top_f * span
        bh = bh_f * span
        cx = x0 + bx + 8
        d.line([(cx, top - 3), (cx, top + bh + 3)], fill=WHITE, width=1)
        d.rectangle([x0 + bx, top, x0 + bx + 16, top + bh],
                    fill=(120, 200, 120))
        mid = (cx, top + bh / 2)
        if prev:
            d.line([prev, mid], fill=GOLD, width=2)
        prev = mid
    tf = font(SANS_BOLD, 18)
    d.text((x0 + w - 52, y0 + 6), "$83", font=tf, fill=GOLD)


def scene_kerch(d, x0, y0, w, h):
    """Bridge over water, blast starburst on the deck."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=SKY)
    d.rectangle([x0, y0 + h - 6, x0 + w, y0 + h], fill=SEA)
    for tx in (x0 + 40, x0 + w - 52):
        d.rectangle([tx, y0 + 4, tx + 12, y0 + h - 6], fill=NAVY)
    d.rectangle([x0, y0 + h - 12, x0 + w, y0 + h - 8], fill=INK)
    d.line([(x0 + 46, y0 + 6), (x0 + w / 2, y0 + h - 10)], fill=GREY, width=1)
    d.line([(x0 + w - 46, y0 + 6), (x0 + w / 2, y0 + h - 10)], fill=GREY,
           width=1)
    star(d, x0 + w / 2, y0 + h - 16, 7, 3, GOLD)
    star(d, x0 + w / 2, y0 + h - 16, 4, 2, RED)


def scene_riyadh(d, x0, y0, w, h):
    """Night skyline, missile streak, burst over the tower."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(16, 24, 44))
    base = y0 + h - 2
    for bx, bw, frac in ((0, 30, 0.55), (34, 22, 0.8), (60, 26, 0.65),
                         (90, 30, 0.95), (124, 22, 0.75), (150, 30, 0.55),
                         (184, 22, 0.85), (210, 22, 0.6)):
        bh = int(frac * (h - 4))
        d.rectangle([x0 + bx, base - bh, x0 + bx + bw, base], fill=(40, 52, 84))
        for wy in range(base - bh + 3, base - 3, 6):
            d.rectangle([x0 + bx + 4, wy, x0 + bx + 8, wy + 2], fill=GOLD)
    d.line([(x0 + 14, y0 + 4), (x0 + 140, y0 + 10)], fill=WHITE, width=2)
    star(d, x0 + 140, y0 + 10, 8, 3, ORANGE)
    star(d, x0 + 140, y0 + 10, 4, 2, GOLD)


def scene_cyclone(d, x0, y0, w, h):
    """Spiral storm over a coastline + RED ALERT tag."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(198, 226, 238))
    cx, cy = x0 + int(w * 0.36), y0 + h / 2 + 2
    rmax = h / 2 - 3
    for f, a0, a1 in ((0.3, 0, 300), (0.55, 40, 340), (0.8, 80, 380),
                     (1.0, 120, 420)):
        r = rmax * f
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=SEA_DEEP, width=3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)
    d.polygon([(x0 + w - 60, y0 + h), (x0 + w, y0 + h - 14), (x0 + w, y0 + h)],
              fill=LAND)
    tf = font(SANS_BOLD, 10)
    d.rectangle([x0 + 6, y0 + 5, x0 + 76, y0 + 19], fill=RED)
    d.text((x0 + 10, y0 + 7), "RED ALERT", font=tf, fill=WHITE)


def scene_suneung(d, x0, y0, w, h):
    """Exam desk: paper, pencil, clock."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(232, 222, 200))
    d.rectangle([x0 + 8, y0 + 5, x0 + w - 58, y0 + h - 6], fill=WHITE,
                outline=GREY, width=1)
    for ly in (y0 + 11, y0 + 16, y0 + 21):
        d.line([(x0 + 14, ly), (x0 + w - 64, ly)], fill=(180, 180, 170), width=1)
    d.line([(x0 + w - 48, y0 + 8), (x0 + w - 32, y0 + h - 12)], fill=GOLD,
           width=5)
    d.polygon([(x0 + w - 32, y0 + h - 12), (x0 + w - 26, y0 + h - 6),
               (x0 + w - 36, y0 + h - 6)], fill=(240, 200, 160))
    cx, cy, cr = x0 + w - 26, y0 + 14, 10
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=WHITE, outline=INK,
              width=2)
    d.line([(cx, cy), (cx, cy - 6)], fill=INK, width=2)
    d.line([(cx, cy), (cx + 4, cy + 2)], fill=INK, width=2)


def scene_colombia(d, x0, y0, w, h):
    """Marching crowd + PARO NACIONAL placard."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=(250, 240, 210))
    base = y0 + h - 4
    skins = [SKIN, SKIN2, SKIN3, SKIN, SKIN2]
    suits = [RED, NAVY2, TEAL, OLIVE, PURPLE]
    for i in range(5):
        cx = x0 + 26 + i * 42
        d.ellipse([cx - 8, base - 24, cx + 8, base - 8], fill=skins[i])
        d.polygon([(cx - 15, base), (cx - 10, base - 12), (cx + 10, base - 12),
                   (cx + 15, base)], fill=suits[i])
    d.rectangle([x0 + w - 92, y0 + 6, x0 + w - 10, y0 + 24], fill=WHITE,
                outline=INK, width=1)
    d.line([(x0 + w - 88, y0 + 24), (x0 + w - 88, y0 + 34)], fill=INK, width=2)
    d.line([(x0 + w - 14, y0 + 24), (x0 + w - 14, y0 + 34)], fill=INK, width=2)
    pf = font(SANS_BOLD, 9)
    t = "PARO NACIONAL"
    d.text((x0 + w - 51 - d.textlength(t, font=pf) / 2, y0 + 10), t, font=pf,
           fill=RED)


def scene_jobless(d, x0, y0, w, h):
    """Rising red bars + 4.9%."""
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=WHITE)
    base = y0 + h - 4
    for i, frac in enumerate((0.30, 0.42, 0.55, 0.70, 0.85)):
        bh = int(frac * (h - 8))
        bx = x0 + 14 + i * 26
        d.rectangle([bx, base - bh, bx + 18, base], fill=RED)
    d.line([(x0 + 10, base - 6), (x0 + w - 22, y0 + 5)], fill=INK, width=2)
    d.polygon([(x0 + w - 22, y0 + 5), (x0 + w - 32, y0 + 7),
               (x0 + w - 26, y0 + 15)], fill=INK)
    tf = font(SANS_BOLD, 15)
    d.text((x0 + w - 58, y0 + 3), "4.9%", font=tf, fill=RED)

# ---- stories: 3 heroes + 8 mids + 22 briefs = 33 verified 19-Nov stories ----
# (headline, subline, kicker, scene). Every event happened or was first
# reported on 19 November 2026; uncertain claims carry their qualifier.
# New in v3 (verified live in-session, primary sources): COP31 draft
# (Reuters, Antalya 19 Nov), Han term overturned in part (Yonhap/AP,
# 19 Nov), Australia 4.9% (Reuters, 19 Nov), Colombia strike (CUT/
# Fecode, 19 Nov), Suneung 551,864 (Education Ministry, 19 Nov),
# Gaza raid concluded (Reuters, 19 Nov), Florida schools shut 2nd day
# (AP, 19 Nov), Jepchirchir ban (AIU, 19 Nov). Carried over from v2
# (already verified): trilateral, ICJ 9-6, APEC, PIF Tower, GTA VI,
# Anthropic $83/$111.50, Odesa, Kerch, and the 22 briefs.
HEROES = [
    ("TRUMP, XI AND PUTIN HOLD FIRST THREE-WAY SUMMIT",
     "Leaders meet for ~90 minutes; a 'Declaration on Peace' on nuclear risk and UN reform.",
     "SHENZHEN - SUMMIT - Reuters", scene_summit),
    ("WORLD COURT: MYANMAR COMMITTED GENOCIDE",
     "Judges rule 9-6 the Rohingya campaign was genocide; reparations ordered.",
     "THE HAGUE - JUSTICE - Reuters", scene_court),
    ("COP31 DRAFT DROPS FOSSIL FUELS AND $120BN AID GOAL",
     "Slimmed-down text cuts the $120bn adaptation target; talks end Friday.",
     "ANTALYA - CLIMATE - Reuters", scene_cop31),
]

MIDS = [
    ("GTA VI IS OUT AFTER 13 YEARS",
     "Midnight launch: 99 Metacritic, 2.3M on Twitch. - BBC",
     "WORLDWIDE - GAMES - BBC", scene_gta),
    ("ANTHROPIC STARTS TRADING ON NASDAQ AS ANT",
     "Record $81.3bn sale at $83; opened $111.50. - AP",
     "NEW YORK - MARKETS - AP", scene_nasdaq),
    ("KERCH BRIDGE HIT FOR 3RD TIME THIS WEEK",
     "Blasts close the Crimea link. - Euronews",
     "CRIMEA - WAR - Euronews", scene_kerch),
    ("HOUTHI MISSILE HITS RIYADH TOWER",
     "PIF Tower damaged; debris falls. - Reuters",
     "RIYADH - WAR - Reuters", scene_riyadh),
    ("CYCLONE AKVAN NEARS INDIA'S EAST COAST",
     "72,000 evacuated; landfall Friday. - IMD",
     "ODISHA - STORM - IMD", scene_cyclone),
    ("HALF A MILLION SIT KOREA'S SUNEUNG EXAM",
     "551,864 sit; 22 caught with phones. - Yonhap",
     "SEOUL - EDUCATION - Yonhap", scene_suneung),
    ("COLOMBIA'S UNIONS HOLD NATIONAL STRIKE",
     "Marches in five cities vs rescue bill. - AFP",
     "BOGOTA - LABOUR - AFP", scene_colombia),
    ("AUSTRALIA'S JOBLESS RATE HITS 4.9%",
     "Highest since 2021; 43,500 jobs lost. - ABC",
     "CANBERRA - ECONOMY - ABC", scene_jobless),
]

# (place, headline, source) -- one line each in the numbered list.
BRIEFS = [
    ("ODESA", "4 killed in Russian strike.", "Euronews"),
    ("KYIV", "Zelenskyy: no deal without Ukraine.", "AP"),
    ("TOKYO", "Takaichi meets Putin.", "AP"),
    ("SEOUL", "Lee renews call for N. Korea talks.", "Yonhap"),
    ("DHAKA", "Bangladesh shuts down; Yunus home torched.", "AP"),
    ("JAKARTA", "Indonesia passes asset-forfeiture bill.", "Kompas"),
    ("COPENHAGEN", "Denmark backs Greenland defence deal, 109-0.", "AP"),
    ("SUVA", "Fiji declares drought disaster.", "RNZ"),
    ("ANCHORAGE", "Begich keeps Alaska House seat.", "AP"),
    ("CARACAS", "US and Venezuela restore military ties.", "AP"),
    ("PORT-AU-PRINCE", "Pastor convicted over Moise killing.", "AP"),
    ("DAKAR", "Migrant boat sinks off Senegal; ~100 aboard.", "AP"),
    ("KHARTOUM", "Sudan: RSF commander defects.", "AP"),
    ("KINSHASA", "Ebola fight stalls in DR Congo.", "AP"),
    ("HORMUZ", "Iran reports 3 tankers on fire (unverified).", "Press TV"),
    ("GAZA", "Aid groups rate peace plan 4 of 26.", "AP"),
    ("ZURICH", "Infantino faces first FIFA challenge.", "Reuters"),
    ("SHENZHEN", "APEC adopts Shenzhen Outlook.", "Reuters"),
    ("GAZA", "Israel concludes tank raid past Yellow Line.", "Reuters"),
    ("HOLLYWOOD", "Florida floods shut schools a 2nd day.", "AP"),
    ("SEOUL", "Top court overturns ex-PM Han's term in part.", "AP"),
    ("NAIROBI", "Marathon champion banned 3 years for doping.", "AIU"),
]

# (big figure, one-line label)
NUMBERS = [
    ("3", "presidents at one table"),
    ("9-6", "World Court vote"),
    ("$120bn", "aid goal cut at COP31"),
    ("$81.3bn", "Anthropic's record IPO"),
    ("551,864", "sit Korea's Suneung exam"),
    ("109-0", "Danish vote on Arctic pact"),
]

# (region, count, colour) -- counts match the 33 stories above.
REGIONS = [
    ("ASIA", 9, RED),
    ("EUROPE", 7, NAVY2),
    ("MIDDLE EAST", 4, TEAL),
    ("AFRICA", 4, OLIVE),
    ("AMERICAS", 6, PURPLE),
    ("OCEANIA", 2, ORANGE),
    ("GLOBAL", 1, GREY),
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
    d.rectangle([0, 0, W, 108], fill=NAVY)
    kf = font(SANS_BOLD, 13)
    d.text((24, 8), "THE WORLD IN ONE DAY", font=kf, fill=GOLD)
    right = "33 STORIES  -  6 CONTINENTS"
    rf = font(SANS_BOLD, 13)
    d.text((W - 24 - d.textlength(right, font=rf), 8), right,
           font=rf, fill=SKY)
    date = "THURSDAY, 19 NOVEMBER 2026"
    dsize = fit_size(d, date, SERIF_BOLD, W - 48, 52)
    df = font(SERIF_BOLD, dsize)
    d.text((24, 26), date, font=df, fill=WHITE)
    deck = ("Trump, Xi and Putin share one table - World Court finds genocide "
            "- COP31 draft drops fossil fuels")
    dk = font_or(SERIF_ITALIC, SERIF_BOLD, 13)
    d.text((24, 84), deck, font=dk, fill=(255, 220, 180))
    d.line([(24, 102), (W - 24, 102)], fill=GOLD, width=2)

    # ---- big-number strip ----
    nx0, ny0 = 24, 112
    cw = (W - 48) / 6
    nf = font(SERIF_BOLD, 24)
    lf = font(SANS, 10)
    for i, (num, label) in enumerate(NUMBERS):
        x = nx0 + i * cw
        d.text((x, ny0), num, font=nf, fill=RED)
        d.text((x, ny0 + 28), label, font=lf, fill=GREY)
        if i:
            d.line([(x - 8, ny0 + 2), (x - 8, ny0 + 38)], fill=(210, 205, 190),
                   width=1)

    # ---- region-count strip ----
    ry = 158
    segs = []
    rf2 = font(SANS_BOLD, 11)
    total_w = 0
    parts = []
    for name, count, colour in REGIONS:
        parts.append((name, count, colour))
        total_w += d.textlength(name + " " + str(count), font=rf2) + 20
    total_w -= 20
    x = (W - total_w) / 2
    for j, (name, count, colour) in enumerate(parts):
        d.text((x, ry), name, font=rf2, fill=colour)
        x += d.textlength(name, font=rf2)
        d.text((x, ry), " " + str(count), font=rf2, fill=INK)
        x += d.textlength(" " + str(count), font=rf2)
        if j < len(parts) - 1:
            d.text((x, ry), "  -  ", font=rf2, fill=GREY)
            x += 20

    # ---- hero stories: 3 cards with drawn scenes ----
    hx0, hy0 = 24, 176
    hw, hh, hgap = 317, 208, 8
    for i, (head, sub, kick, scene) in enumerate(HEROES):
        x = hx0 + i * (hw + hgap)
        y = hy0
        d.rectangle([x, y, x + hw, y + hh], fill=CREAM, outline=NAVY, width=1)
        d.rectangle([x, y, x + hw, y + 4], fill=RED)
        scene(d, x + 1, y + 5, hw - 2, 104)
        kf2 = font(SANS_BOLD, 10)
        d.text((x + 10, y + 114), kick, font=kf2, fill=GREY)
        hf = font(SERIF_BOLD, 17)
        hy = draw_wrapped(d, head, hf, x + 10, y + 130, hw - 20, INK,
                          leading=20, max_lines=2)
        sf = font(SANS, 11)
        draw_wrapped(d, sub, sf, x + 10, y + 172, hw - 20, GREY,
                     leading=13, max_lines=2)

    # ---- mid stories: 4 x 2 cards with small drawn scenes ----
    mx0, my0 = 24, 392
    mw, mh = 236, 88
    mgapx, mgapy = 10, 8
    for i, (head, sub, kick, scene) in enumerate(MIDS):
        col, row = i % 4, i // 4
        x = mx0 + col * (mw + mgapx)
        y = my0 + row * (mh + mgapy)
        num = i + 4
        d.rectangle([x, y, x + mw, y + mh], fill=WHITE,
                    outline=(200, 195, 180), width=1)
        scene(d, x + 1, y + 1, mw - 2, 32)
        # Number chip sits beside the headline, never on the picture:
        # on the 32px scene strip it covered the artwork (v3 first
        # render: it ate the RED ALERT tag and the chart bars).
        draw_chip(d, num, x + 6, y + 38, 16)
        hf = font(SANS_BOLD, 12)
        hy = draw_wrapped(d, head, hf, x + 28, y + 36, mw - 36, INK,
                          leading=14, max_lines=2)
        sf = font(SANS, 9)
        draw_wrapped(d, sub, sf, x + 8, max(hy + 2, y + 64), mw - 16, GREY,
                     leading=11, max_lines=2)

    # ---- map + numbered briefs ----
    ly = 584
    hf2 = font(SANS_BOLD, 11)
    d.text((24, ly), "WHERE IT HAPPENED", font=hf2, fill=RED)
    d.text((308, ly), "ALSO ON THURSDAY 19 NOVEMBER 2026", font=hf2, fill=INK)
    rf3 = font(SANS, 9)
    tail = "place - what happened - source"
    d.text((W - 24 - d.textlength(tail, font=rf3), ly), tail, font=rf3,
           fill=GREY)
    draw_map(d)
    cf = font(SANS, 9)
    d.text((24, 796), "Pins 1-3, 5-11; story 4 (GTA VI) is worldwide.",
           font=cf, fill=GREY)
    # briefs: 2 columns x 11 rows
    bx0, by0 = 308, 604
    bcol_w, brow_h = 346, 31
    bf = font(SANS_BOLD, 10)
    rf4 = font(SANS, 10)
    for i, (place, head, src) in enumerate(BRIEFS):
        col, row = i % 2, i // 2
        x = bx0 + col * bcol_w
        y = by0 + row * brow_h
        num = i + 12
        draw_chip(d, num, x, y + 2, 16)
        tx = x + 22
        ty = y + 4
        d.text((tx, ty), place + " - ", font=bf, fill=RED)
        px = tx + d.textlength(place + " - ", font=bf)
        rest = head + " - " + src
        d.text((px, ty), rest, font=rf4, fill=INK)

    # ---- DATE CHECK box ----
    d.rectangle([24, 952, W - 24, 988], fill=WHITE, outline=RED, width=2)
    tf = font(SANS, 10)
    df2 = font(SANS_BOLD, 10)
    d.text((32, 958), "DATE CHECK", font=df2, fill=RED)
    lx = 32 + d.textlength("DATE CHECK  ", font=df2)
    line1 = ("- Every story here happened, or was first reported, on Thursday "
             "19 November 2026.")
    d.text((lx, 958), line1, font=tf, fill=INK)
    line2 = ("LEFT OUT AS OTHER DAYS' NEWS - 18 NOV: EU 45bn Ukraine loan - "
             "Iran fires on Kuwait and Bahrain - Nvidia results - Van Gogh "
             "sale - Jeffries named speaker. 17 NOV: US strike on Qeshm.")
    d.text((32, 972), line2, font=tf, fill=INK)

    # ---- footer ----
    foot = ("Sources: Reuters, AP, AFP, BBC, Al Jazeera, UN News, Yonhap, "
            "ABC, IMD, Nature - Original drawings, drawn in code. Claims "
            "are attributed, not stated as fact.")
    ff = font(SANS, 9)
    d.text(((W - d.textlength(foot, font=ff)) / 2, 996), foot,
           font=ff, fill=GREY)
    return img


def main():
    img = draw()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG", optimize=True)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()
