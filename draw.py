#!/usr/bin/env python3
"""news-image-20261119 v4 — picture-paper front page, drawn entirely in code.

40 stories, 3 drawn heroes + 12 drawn mids, number strip, region chips,
day-by-hours timeline, REPORTED/CLAIM/FORECAST tags, numbered-pin map,
DATE CHECK box. Output: entry.png (1024x1024, <=1 MiB), deterministic.
"""
import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 229)
INK = (26, 26, 26)
NAVY = (20, 38, 74)
RED = (178, 34, 34)
GOLD = (201, 162, 39)
SEA = (214, 229, 233)
LAND = (233, 216, 164)
LAND_LINE = (176, 152, 96)

FD = "/usr/share/fonts/truetype/dejavu"


def F(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)


SERIF_B = lambda s: F("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: F("DejaVuSerif.ttf", s)
SANS_B = lambda s: F("DejaVuSans-Bold.ttf", s)
SANS = lambda s: F("DejaVuSans.ttf", s)


def wrap(draw, text, font, max_w):
    """Greedy word wrap to max pixel width; returns list of lines."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def rrect(d, box, radius, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def tag(d, x, y, label, color):
    """Status chip: REPORTED (green) / CLAIM (amber) / FORECAST (blue)."""
    f = SANS_B(9)
    w = int(d.textlength(label, font=f)) + 10
    rrect(d, [x, y, x + w, y + 14], 3, fill=color)
    d.text((x + 5, y + 2), label, font=f, fill=(255, 255, 255))
    return w


GREEN = (46, 125, 50)
AMBER = (178, 106, 0)
BLUE = (21, 101, 192)

TAG_COLORS = {"REPORTED": GREEN, "CLAIM": AMBER, "FORECAST": BLUE}


def chip(d, x, y, label, color, font):
    w = int(d.textlength(label, font=font)) + 14
    rrect(d, [x, y, x + w, y + 20], 4, fill=color)
    d.text((x + 7, y + 4), label, font=font, fill=(255, 255, 255))
    return w


# ---------------------------------------------------------------- map data
# Rough lon/lat polygons (schematic; positions approximate).
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 68), (-100, 69),
     (-90, 69), (-85, 66), (-80, 73), (-70, 62), (-60, 55), (-55, 47),
     (-60, 45), (-68, 44), (-75, 39), (-76, 35), (-81, 31), (-84, 30),
     (-89, 29), (-91, 19), (-95, 16), (-100, 16), (-105, 20), (-110, 23),
     (-114, 29), (-120, 34), (-124, 42), (-124, 49), (-130, 55), (-140, 60),
     (-155, 58), (-165, 60)],
    # Greenland
    [(-55, 60), (-45, 60), (-40, 64), (-32, 68), (-22, 70), (-25, 76),
     (-40, 80), (-55, 78), (-60, 72)],
    # South America
    [(-80, 9), (-77, 8), (-72, 12), (-64, 10), (-57, 6), (-51, 4), (-50, 0),
     (-44, -3), (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-54, -34),
     (-62, -39), (-66, -45), (-70, -52), (-73, -50), (-72, -38), (-71, -30),
     (-75, -20), (-79, -12), (-81, -4), (-80, 3)],
    # Africa
    [(-17, 15), (-16, 20), (-10, 29), (-6, 35), (0, 36), (10, 37), (20, 32),
     (30, 31), (34, 28), (39, 21), (43, 12), (51, 11), (48, 2), (41, -4),
     (40, -12), (36, -18), (33, -26), (28, -33), (20, -35), (16, -28),
     (13, -20), (12, -12), (9, -1), (9, 4), (-8, 5), (-13, 8), (-17, 12)],
    # Europe
    [(-10, 36), (-9, 38), (-9, 43), (-4, 48), (-1, 49), (2, 51), (5, 53),
     (8, 57), (10, 59), (14, 58), (18, 56), (21, 55), (24, 58), (28, 61),
     (30, 66), (35, 68), (42, 68), (44, 64), (40, 58), (38, 52), (33, 47),
     (30, 46), (28, 44), (24, 40), (23, 36), (21, 38), (19, 42), (16, 44),
     (12, 44), (8, 44), (3, 42), (-1, 38), (-6, 36)],
    # Asia
    [(30, 36), (35, 36), (40, 40), (44, 42), (48, 46), (52, 50), (56, 53),
     (60, 56), (65, 60), (68, 66), (72, 71), (78, 74), (85, 76), (95, 77),
     (105, 77), (115, 73), (125, 72), (135, 72), (145, 72), (155, 69),
     (162, 66), (170, 66), (178, 65), (172, 62), (163, 60), (158, 53),
     (152, 58), (145, 59), (142, 52), (140, 44), (136, 43), (131, 38),
     (127, 35), (124, 39), (121, 34), (118, 30), (114, 23), (109, 19),
     (105, 10), (101, 8), (99, 10), (97, 15), (92, 21), (88, 22), (85, 19),
     (80, 13), (77, 8), (74, 15), (72, 20), (68, 23), (63, 25), (58, 26),
     (54, 27), (50, 29), (48, 30), (44, 29), (40, 31), (36, 36)],
    # Australia
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33), (129, -32),
     (133, -32), (136, -35), (140, -38), (145, -38), (150, -37), (153, -32),
     (153, -27), (150, -23), (146, -19), (142, -15), (142, -11), (137, -12),
     (135, -15), (132, -12), (129, -14), (126, -14), (122, -17), (118, -20)],
    # Indonesia (thin chain)
    [(95, 5), (98, 3), (101, 0), (104, -3), (107, -6), (111, -7), (115, -8),
     (119, -9), (122, -10), (126, -8), (130, -4), (134, -4), (138, -6),
     (141, -8), (138, -7), (132, -2), (126, 0), (120, 0), (114, -2),
     (108, -6), (102, -2), (97, 4)],
    # Japan (thin chain)
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 37),
     (141, 39), (142, 41), (144, 44), (142, 43), (140, 40), (138, 37),
     (135, 34), (132, 32)],
    # UK
    [(-5, 50), (-4, 52), (-5, 54), (-4, 56), (-2, 58), (0, 57), (1, 54),
     (0, 52), (-2, 51)],
    # New Zealand
    [(167, -45), (169, -43), (172, -41), (175, -39), (177, -38), (176, -40),
     (173, -42), (170, -44)],
]


def project(lon, lat, x0, y0, w, h):
    """Equirectangular: lon -170..190 -> x, lat 75..-55 -> y."""
    x = x0 + (lon + 170) / 360.0 * w
    y = y0 + (75 - lat) / 130.0 * h
    return (x, y)


def draw_map(d, box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    rrect(d, box, 3, fill=SEA)
    for lon in range(-150, 181, 30):
        x = x0 + (lon + 170) / 360.0 * w
        d.line([(x, y0), (x, y1)], fill=(255, 255, 255), width=1)
    for lat in range(60, -46, -30):
        y = y0 + (75 - lat) / 130.0 * h
        d.line([(x0, y), (x1, y)], fill=(255, 255, 255), width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat, x0, y0, w, h) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)


def pin(d, box, lon, lat, num):
    x0, y0, x1, y1 = box
    x, y = project(lon, lat, x0, y0, x1 - x0, y1 - y0)
    d.ellipse([x - 7, y - 7, x + 7, y + 7], fill=RED, outline=(255, 255, 255), width=1)
    f = SANS_B(9)
    tw = d.textlength(str(num), font=f)
    d.text((x - tw / 2, y - 5), str(num), font=f, fill=(255, 255, 255))


def dot(d, box, lon, lat):
    x0, y0, x1, y1 = box
    x, y = project(lon, lat, x0, y0, x1 - x0, y1 - y0)
    d.ellipse([x - 2.5, y - 2.5, x + 2.5, y + 2.5], fill=(110, 110, 110))


# ---------------------------------------------------------------- scenes
def flag_us(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    for i in range(7):
        yy = y + i * h / 13 * 2
        d.rectangle([x, yy, x + w, yy + h / 13], fill=(178, 34, 34))
    d.rectangle([x, y, x + w * 0.42, y + h * 7 / 13], fill=(20, 38, 74))


def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    cx, cy = x + w * 0.22, y + h * 0.28
    for dx, dy, r in [(0, 0, 5), (12, -4, 2), (14, 2, 2), (10, 8, 2), (3, 8, 2)]:
        d.ellipse([cx + dx - r, cy + dy - r, cx + dx + r, cy + dy + r],
                  fill=(255, 222, 0))


def flag_ru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(255, 255, 255))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(0, 57, 166))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(213, 0, 0))


def person(d, cx, head_y, skin, hair, suit, tie):
    """Cartoon seated figure: head + hair + suit + tie."""
    d.ellipse([cx - 13, head_y, cx + 13, head_y + 26], fill=skin)
    d.pieslice([cx - 13, head_y - 2, cx + 13, head_y + 12], 180, 360, fill=hair)
    d.ellipse([cx - 5, head_y + 10, cx - 1, head_y + 14], fill=INK)
    d.ellipse([cx + 1, head_y + 10, cx + 5, head_y + 14], fill=INK)
    d.arc([cx - 5, head_y + 15, cx + 5, head_y + 22], 20, 160, fill=INK, width=1)
    d.polygon([(cx - 20, head_y + 30), (cx + 20, head_y + 30),
               (cx + 24, head_y + 62), (cx - 24, head_y + 62)], fill=suit)
    d.polygon([(cx - 4, head_y + 30), (cx + 4, head_y + 30),
               (cx + 6, head_y + 58), (cx - 6, head_y + 58)], fill=tie)


def scene_summit(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(20, 38, 74))
    # skyline hint
    for bx, bh in [(0, 26), (28, 38), (60, 22), (250, 30), (282, 20)]:
        d.rectangle([x0 + bx, y0 + 62 - bh, x0 + bx + 24, y0 + 62],
                    fill=(28, 52, 96))
    # flags on poles
    poles = [(x0 + 52, flag_us), (x0 + 152, flag_cn), (x0 + 252, flag_ru)]
    for px, fn in poles:
        d.line([(px, y0 + 8), (px, y0 + 62)], fill=(220, 220, 220), width=2)
        fn(d, px + 2, y0 + 10, 34, 22)
    # table
    d.ellipse([x0 + 20, y0 + 92, x1 - 20, y0 + 122], fill=(122, 82, 44))
    d.rectangle([x0 + 20, y0 + 106, x1 - 20, y0 + 122], fill=(96, 62, 32))
    # three leaders with faces
    person(d, x0 + 62, y0 + 52, (232, 190, 150), (240, 220, 160), (30, 30, 30), RED)
    person(d, x0 + 165, y0 + 52, (232, 190, 150), (20, 20, 20), (30, 30, 30), NAVY)
    person(d, x0 + 268, y0 + 52, (232, 190, 150), (200, 200, 200), (30, 30, 30), GOLD)
    f = SANS_B(10)
    for cx, name in [(x0 + 62, "TRUMP"), (x0 + 165, "XI"), (x0 + 268, "PUTIN")]:
        w = d.textlength(name, font=f) + 10
        d.rectangle([cx - w / 2, y0 + 110, cx + w / 2, y0 + 124],
                    fill=(255, 255, 255), outline=INK, width=1)
        d.text((cx - d.textlength(name, font=f) / 2, y0 + 113), name,
               font=f, fill=INK)


def scene_icj(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(178, 216, 230))
    # court building
    d.rectangle([x0 + 30, y0 + 62, x0 + 170, y0 + 132], fill=(240, 234, 220),
                outline=(120, 110, 90), width=2)
    d.polygon([(x0 + 22, y0 + 62), (x0 + 100, y0 + 34), (x0 + 178, y0 + 62)],
              fill=(200, 180, 140), outline=(120, 110, 90))
    for cx in range(x0 + 44, x0 + 168, 26):
        d.rectangle([cx, y0 + 72, cx + 10, y0 + 124], fill=(255, 255, 255),
                    outline=(120, 110, 90), width=1)
    # scales
    sx = x0 + 248
    d.line([(sx, y0 + 40), (sx, y0 + 120)], fill=(90, 70, 30), width=3)
    d.line([(sx - 34, y0 + 52), (sx + 34, y0 + 52)], fill=(90, 70, 30), width=3)
    d.ellipse([sx - 5, y0 + 34, sx + 5, y0 + 44], fill=(212, 175, 55))
    for sgn in (-1, 1):
        d.line([(sx + sgn * 34, y0 + 52), (sx + sgn * 20, y0 + 78)],
               fill=(90, 70, 30), width=1)
        d.line([(sx + sgn * 34, y0 + 52), (sx + sgn * 48, y0 + 78)],
               fill=(90, 70, 30), width=1)
        d.pieslice([sx + sgn * 34 - 14, y0 + 76, sx + sgn * 34 + 14, y0 + 92],
                   0, 180, fill=(212, 175, 55))
    # 9-6 badge
    f = SANS_B(20)
    d.rectangle([x0 + 236, y0 + 100, x0 + 296, y0 + 132], fill=RED)
    d.text((x0 + 244, y0 + 106), "9–6", font=f, fill=(255, 255, 255))
    # banner
    bf = SANS_B(10)
    msg = "FIRST STATE EVER FOUND GUILTY"
    w = d.textlength(msg, font=bf) + 12
    d.rectangle([x0 + 8, y0 + 6, x0 + 8 + w, y0 + 22], fill=RED)
    d.text((x0 + 14, y0 + 8), msg, font=bf, fill=(255, 255, 255))


def scene_gta(d, box):
    x0, y0, x1, y1 = box
    # sunset bands
    bands = [(70, 24, 120), (120, 60, 140), (200, 80, 130), (240, 120, 90),
             (250, 160, 60)]
    bh = (y1 - y0) / len(bands)
    for i, c in enumerate(bands):
        d.rectangle([x0, y0 + i * bh, x1, y0 + (i + 1) * bh], fill=c)
    # sun (left, so the VI sits clear of it)
    d.ellipse([x0 + 30, y0 + 16, x0 + 90, y0 + 76], fill=(255, 214, 90))
    # skyline
    for bx, bw, bhgt in [(0, 34, 52), (40, 26, 70), (70, 30, 44), (230, 28, 62),
                         (262, 34, 48), (296, 22, 66)]:
        d.rectangle([x0 + bx, y1 - 58 - bhgt, x0 + bx + bw, y1 - 58],
                    fill=(40, 16, 60))
        for wy in range(y1 - 58 - bhgt + 6, y1 - 62, 12):
            d.rectangle([x0 + bx + 5, wy, x0 + bx + 10, wy + 5],
                        fill=(255, 214, 90))
    # palms
    for px in (x0 + 108, x0 + 216):
        d.line([(px, y1 - 58), (px, y1 - 96)], fill=(30, 60, 30), width=3)
        for ang in (-50, -20, 10, 40):
            import math
            ex = px + int(22 * math.cos(math.radians(ang - 90)))
            ey = y1 - 96 + int(16 * math.sin(math.radians(ang - 90)))
            d.line([(px, y1 - 96), (ex, ey)], fill=(30, 90, 40), width=2)
    # road
    d.polygon([(x0, y1), (x1, y1), (x1, y1 - 58), (x0, y1 - 58)], fill=(30, 30, 40))
    d.line([(x0, y1 - 29), (x1, y1 - 29)], fill=(255, 214, 90), width=2)
    # neon VI
    f = SERIF_B(44)
    d.text((x0 + 132, y0 + 58), "VI", font=f, fill=(255, 255, 255),
           stroke_width=2, stroke_fill=(255, 0, 180))
    bf = SANS_B(11)
    msg = "OUT TODAY · MIDNIGHT ROLLOUT"
    w = d.textlength(msg, font=bf) + 12
    d.rectangle([x0 + 92, y0 + 110, x0 + 92 + w, y0 + 126], fill=(255, 0, 180))
    d.text((x0 + 98, y0 + 113), msg, font=bf, fill=(255, 255, 255))


def scene_cop31(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(14, 90, 100))
    # globe (left, clear of the top-right tag)
    cx, cy, r = x0 + 24, y0 + 20, 15
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(80, 180, 200))
    d.ellipse([cx - 8, cy - 9, cx + 2, cy + 1], fill=(60, 160, 90))
    d.ellipse([cx + 2, cy + 3, cx + 11, cy + 11], fill=(60, 160, 90))
    # thermometer
    d.rectangle([x0 + 46, y0 + 6, x0 + 53, y0 + 30], fill=(255, 255, 255))
    d.rectangle([x0 + 48, y0 + 16, x0 + 51, y0 + 30], fill=RED)
    d.ellipse([x0 + 43, y0 + 26, x0 + 56, y0 + 39], fill=RED)
    # bottom band: struck-through FOSSIL FUELS + CUT stamp
    d.rectangle([x0 + 4, y0 + 38, x1 - 4, y0 + 54], fill=(255, 255, 255))
    d.text((x0 + 8, y0 + 41), "FOSSIL FUELS", font=SANS_B(9), fill=INK)
    d.line([(x0 + 8, y0 + 45), (x0 + 76, y0 + 45)], fill=RED, width=2)
    d.rectangle([x0 + 104, y0 + 39, x0 + 140, y0 + 51], fill=RED)
    d.text((x0 + 110, y0 + 41), "CUT", font=SANS_B(8), fill=(255, 255, 255))


def scene_ant(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(16, 60, 40))
    bars = [(0, 22, 30, 1), (14, 18, 34, 1), (28, 26, 30, 0), (42, 14, 40, 1),
            (56, 20, 36, 0), (70, 10, 44, 1), (84, 16, 40, 1)]
    for bx, by, bh, up in bars:
        c = (60, 200, 100) if up else (220, 70, 60)
        d.rectangle([x0 + 8 + bx, y0 + 8 + by, x0 + 18 + bx, y0 + 8 + by + bh],
                    fill=c)
    pts = [(x0 + 13 + bx, y0 + 8 + by) for bx, by, _, _ in bars]
    d.line(pts, fill=(255, 214, 90), width=2)
    f = SANS_B(20)
    d.text((x0 + 104, y0 + 22), "$83", font=f, fill=(255, 255, 255))
    d.text((x0 + 104, y0 + 44), "IPO", font=SANS_B(10), fill=(255, 214, 90))


def scene_kerch(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(140, 190, 220))
    d.rectangle([x0, y0 + 34, x1, y1], fill=(60, 110, 160))
    # bridge towers + deck
    for tx in (x0 + 34, x0 + 118):
        d.rectangle([tx, y0 + 8, tx + 6, y0 + 44], fill=(240, 240, 240))
    d.rectangle([x0 + 6, y0 + 40, x1 - 6, y0 + 48], fill=(240, 240, 240))
    for cx in range(x0 + 12, x1 - 10, 12):
        d.line([(cx, y0 + 40), (cx + 8, y0 + 16)], fill=(255, 255, 255), width=1)
    # starburst
    cx, cy = x0 + 82, y0 + 18
    for ang in range(0, 360, 30):
        import math
        ex = cx + int(14 * math.cos(math.radians(ang)))
        ey = cy + int(14 * math.sin(math.radians(ang)))
        d.line([(cx, cy), (ex, ey)], fill=(255, 140, 0), width=3)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 220, 0))


def scene_riyadh(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(16, 20, 48))
    for i in range(14):
        d.ellipse([x0 + 6 + (i * 23) % 150, y0 + 4 + (i * 7) % 14,
                   x0 + 8 + (i * 23) % 150, y0 + 6 + (i * 7) % 14],
                  fill=(255, 255, 255))
    for bx, bw, bh in [(0, 22, 30), (24, 18, 38), (46, 24, 26), (74, 16, 34),
                       (94, 20, 28), (118, 18, 32)]:
        d.rectangle([x0 + bx, y1 - bh, x0 + bx + bw, y1], fill=(40, 44, 80))
        for wy in range(y1 - bh + 5, y1 - 3, 9):
            d.rectangle([x0 + bx + 4, wy, x0 + bx + 9, wy + 4],
                        fill=(255, 214, 90))
    # missile trail
    d.arc([x0 + 60, y0 - 20, x0 + 170, y0 + 44], 200, 340, fill=(255, 255, 255),
          width=2)
    d.ellipse([x0 + 150, y0 + 6, x0 + 158, y0 + 14], fill=(255, 120, 40))


def scene_cyclone(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(190, 220, 235))
    cx, cy = x0 + 82, y0 + 30
    for r, a0 in [(26, 0), (19, 60), (12, 120), (6, 180)]:
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 240,
              fill=(255, 255, 255), width=4)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(20, 60, 120))
    bf = SANS_B(9)
    d.rectangle([x0 + 6, y0 + 6, x0 + 62, y0 + 20], fill=RED)
    d.text((x0 + 10, y0 + 8), "RED ALERT", font=bf, fill=(255, 255, 255))
    d.text((x0 + 102, y0 + 38), "72,000", font=SANS_B(11), fill=INK)
    d.text((x0 + 102, y0 + 50), "moved", font=SANS(9), fill=INK)


def scene_suneung(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(240, 235, 220))
    d.rectangle([x0 + 18, y0 + 8, x0 + 92, y0 + 54], fill=(255, 255, 255),
                outline=INK, width=1)
    for ly in range(y0 + 18, y0 + 50, 8):
        d.line([(x0 + 26, ly), (x0 + 84, ly)], fill=(150, 150, 150), width=1)
    # clock
    cx, cy = x0 + 126, y0 + 30
    d.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(255, 255, 255),
              outline=INK, width=2)
    d.line([(cx, cy), (cx, cy - 12)], fill=INK, width=2)
    d.line([(cx, cy), (cx + 9, cy + 4)], fill=INK, width=2)
    d.text((x0 + 108, y0 + 50), "08:40", font=SANS_B(9), fill=INK)


def scene_colombia(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(250, 240, 200))
    # banner stripes
    d.rectangle([x0 + 10, y0 + 4, x1 - 10, y0 + 10], fill=(255, 205, 0))
    d.rectangle([x0 + 10, y0 + 10, x1 - 10, y0 + 16], fill=(0, 56, 147))
    d.rectangle([x0 + 10, y0 + 16, x1 - 10, y0 + 22], fill=(206, 17, 38))
    d.text((x0 + 8, y0 + 25), "PARO NACIONAL", font=SANS_B(9), fill=RED)
    # crowd
    for i, cx in enumerate(range(x0 + 16, x1 - 10, 26)):
        skin = (232, 190, 150) if i % 2 == 0 else (200, 150, 110)
        d.ellipse([cx, y0 + 36, cx + 14, y0 + 50], fill=skin)
        d.rectangle([cx - 4, y0 + 50, cx + 18, y1 - 2],
                    fill=[(200, 60, 60), (60, 120, 200), (60, 160, 80)][i % 3])


def scene_jobless(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(235, 240, 245))
    bars = [16, 22, 28, 38]
    for i, bh in enumerate(bars):
        c = RED if i == 3 else (90, 120, 160)
        d.rectangle([x0 + 10 + i * 20, y1 - 8 - bh, x0 + 24 + i * 20, y1 - 8],
                    fill=c)
    d.text((x0 + 96, y0 + 20), "4.9%", font=SANS_B(20), fill=RED)
    d.text((x0 + 96, y0 + 42), "highest", font=SANS(9), fill=INK)


def scene_somalia(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(240, 235, 220))
    # Somalia flag
    d.rectangle([x0 + 10, y0 + 10, x0 + 66, y0 + 34], fill=(65, 137, 221))
    cx, cy = x0 + 38, y0 + 22
    d.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=(255, 255, 255))
    for ang in range(-90, 270, 72):
        import math
        ex = cx + int(9 * math.cos(math.radians(ang)))
        ey = cy + int(9 * math.sin(math.radians(ang)))
        ix = cx + int(4 * math.cos(math.radians(ang + 36)))
        iy = cy + int(4 * math.sin(math.radians(ang + 36)))
        d.polygon([(cx, cy - 9), (ex, ey), (ix, iy)], fill=(255, 255, 255))
    # UAE flag
    d.rectangle([x0 + 78, y0 + 10, x0 + 134, y0 + 34], fill=(255, 255, 255))
    d.rectangle([x0 + 78, y0 + 10, x0 + 96, y0 + 34], fill=RED)
    d.rectangle([x0 + 96, y0 + 10, x0 + 134, y0 + 18], fill=(0, 122, 61))
    d.rectangle([x0 + 96, y0 + 26, x0 + 134, y0 + 34], fill=(0, 0, 0))
    # 72 hrs badge
    d.rectangle([x0 + 8, y0 + 38, x0 + 94, y0 + 52], fill=RED)
    d.text((x0 + 12, y0 + 41), "72 HRS TO LEAVE", font=SANS_B(8),
           fill=(255, 255, 255))
    d.text((x0 + 98, y0 + 41), "envoy out", font=SANS(9), fill=INK)


def scene_greens(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(235, 240, 250))
    # tricolore
    d.rectangle([x0 + 12, y0 + 8, x0 + 32, y0 + 50], fill=(0, 85, 164))
    d.rectangle([x0 + 32, y0 + 8, x0 + 52, y0 + 50], fill=(255, 255, 255))
    d.rectangle([x0 + 52, y0 + 8, x0 + 72, y0 + 50], fill=(239, 65, 53))
    # Eiffel silhouette
    ex = x0 + 108
    d.polygon([(ex - 16, y0 + 52), (ex, y0 + 6), (ex + 16, y0 + 52)],
              fill=(60, 60, 70))
    d.rectangle([ex - 22, y0 + 48, ex + 22, y0 + 54], fill=(60, 60, 70))
    # green rosette
    d.ellipse([x0 + 124, y0 + 10, x0 + 150, y0 + 36], fill=(40, 140, 60))
    d.text((x0 + 132, y0 + 15), "✓", font=SANS_B(15), fill=(255, 255, 255))
    d.text((x0 + 80, y0 + 44), "GREENS BACK", font=SANS_B(8), fill=(40, 140, 60))


def scene_denmark(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(200, 220, 235))
    # mountains
    d.polygon([(x0, y1), (x0 + 40, y0 + 18), (x0 + 80, y1)], fill=(255, 255, 255),
              outline=(150, 150, 150))
    d.polygon([(x0 + 50, y1), (x0 + 100, y0 + 10), (x0 + 150, y1)],
              fill=(230, 230, 230), outline=(150, 150, 150))
    # Danish flag
    d.rectangle([x0 + 10, y0 + 6, x0 + 44, y0 + 26], fill=(200, 16, 46))
    d.rectangle([x0 + 20, y0 + 6, x0 + 26, y0 + 26], fill=(255, 255, 255))
    d.rectangle([x0 + 10, y0 + 13, x0 + 44, y0 + 19], fill=(255, 255, 255))
    # 109-0 badge (bottom-left, clear of the top-right tag)
    d.rectangle([x0 + 8, y0 + 32, x0 + 60, y0 + 50], fill=RED)
    d.text((x0 + 13, y0 + 36), "109–0", font=SANS_B(11), fill=(255, 255, 255))


def scene_gaza(d, box):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=(238, 220, 180))
    # dashed Yellow Line
    for xx in range(x0 + 6, x1 - 6, 14):
        d.line([(xx, y0 + 34), (xx + 8, y0 + 34)], fill=(200, 160, 0), width=3)
    d.text((x0 + 8, y0 + 6), "YELLOW LINE", font=SANS_B(9), fill=(140, 110, 40))
    # tank silhouette
    d.rectangle([x0 + 8, y0 + 38, x0 + 64, y0 + 52], fill=(90, 85, 70))
    d.rectangle([x0 + 22, y0 + 28, x0 + 44, y0 + 40], fill=(90, 85, 70))
    d.line([(x0 + 44, y0 + 32), (x0 + 74, y0 + 26)], fill=(90, 85, 70), width=4)
    d.ellipse([x0 + 14, y0 + 50, x0 + 26, y0 + 58], fill=(60, 58, 50))
    d.ellipse([x0 + 30, y0 + 50, x0 + 42, y0 + 58], fill=(60, 58, 50))
    d.ellipse([x0 + 46, y0 + 50, x0 + 58, y0 + 58], fill=(60, 58, 50))
    d.text((x0 + 84, y0 + 40), "RAID OVER", font=SANS_B(9), fill=INK)


# ---------------------------------------------------------------- cards
HEROES = [
    dict(num=1, scene=scene_summit, kicker="SHENZHEN · SUMMIT · Reuters",
         headline="TRUMP, XI AND PUTIN HOLD FIRST THREE-WAY SUMMIT",
         sub="Leaders meet for ~90 minutes; a \u2018Declaration on Peace\u2019 on nuclear risk and UN reform.",
         tag="REPORTED"),
    dict(num=2, scene=scene_icj, kicker="THE HAGUE · JUSTICE · Reuters",
         headline="WORLD COURT: MYANMAR COMMITTED GENOCIDE",
         sub="Judges rule 9\u20136 the Rohingya campaign was genocide; reparations ordered. First state ever found guilty.",
         tag="REPORTED"),
    dict(num=3, scene=scene_gta, kicker="WORLDWIDE · GAMES · BBC",
         headline="GTA VI IS OUT AFTER 13 YEARS",
         sub="Midnight launch, New Zealand first; 99 on Metacritic, 2.3M watching on Twitch.",
         tag="REPORTED"),
]

MIDS = [
    dict(num=4, scene=scene_cop31, kicker="ANTALYA · CLIMATE · Reuters",
         headline="COP31 DRAFT DROPS FOSSIL FUELS AND $120BN AID GOAL",
         sub="Slimmed-down text cuts the $120bn adaptation target; talks end Friday.",
         tag="REPORTED"),
    dict(num=5, scene=scene_ant, kicker="NEW YORK · MARKETS · AP",
         headline="ANTHROPIC STARTS TRADING ON NASDAQ AS ANT",
         sub="Record $81.3bn sale at $83; opened $111.50.",
         tag="REPORTED"),
    dict(num=6, scene=scene_kerch, kicker="CRIMEA · WAR · Euronews",
         headline="KERCH BRIDGE HIT FOR 3RD TIME THIS WEEK",
         sub="Blasts close the Crimea link.",
         tag="REPORTED"),
    dict(num=7, scene=scene_riyadh, kicker="RIYADH · WAR · Reuters",
         headline="HOUTHI MISSILE HITS RIYADH TOWER",
         sub="PIF Tower damaged; debris falls.",
         tag="REPORTED"),
    dict(num=8, scene=scene_cyclone, kicker="ODISHA · STORM · IMD",
         headline="CYCLONE AKVAN NEARS INDIA'S EAST COAST",
         sub="72,000 evacuated; landfall Friday.",
         tag="FORECAST"),
    dict(num=9, scene=scene_suneung, kicker="SEOUL · EDUCATION · Yonhap",
         headline="HALF A MILLION SIT KOREA'S SUNEUNG EXAM",
         sub="551,864 sit; 22 caught with phones.",
         tag="REPORTED"),
    dict(num=10, scene=scene_colombia, kicker="BOGOTÁ · LABOUR · AFP",
         headline="COLOMBIA'S UNIONS HOLD NATIONAL STRIKE",
         sub="Marches in five cities vs rescue bill.",
         tag="REPORTED"),
    dict(num=11, scene=scene_jobless, kicker="CANBERRA · ECONOMY · ABC",
         headline="AUSTRALIA'S JOBLESS RATE HITS 4.9%",
         sub="Highest since 2021; 43,500 jobs lost.",
         tag="REPORTED"),
    dict(num=12, scene=scene_somalia, kicker="MOGADISHU · DIPLOMACY · Reuters",
         headline="SOMALIA EXPELS UAE ENVOY",
         sub="Ambassador given 72 hours to leave; envoy recalled.",
         tag="REPORTED"),
    dict(num=13, scene=scene_greens, kicker="PARIS · POLITICS · Reuters",
         headline="GREENS OPEN DOOR TO BACKING MÉLENCHON",
         sub="Tondelier offers support; polls put him in runoff.",
         tag="REPORTED"),
    dict(num=14, scene=scene_denmark, kicker="GREENLAND · SECURITY · AP",
         headline="DENMARK BACKS ARCTIC PACT WITH US",
         sub="Parliament approves Greenland deal, 109\u20130.",
         tag="REPORTED"),
    dict(num=15, scene=scene_gaza, kicker="GAZA · WAR · Reuters",
         headline="ISRAEL CONCLUDES TANK RAID PAST YELLOW LINE",
         sub="Raid over; aid groups rate peace plan 4 of 26.",
         tag="REPORTED"),
]

BRIEFS = [
    (16, "ODESA", "4 killed in Russian strike.", "Euronews", "REPORTED", (30, 46)),
    (17, "KYIV", "Zelenskyy: no deal without Ukraine.", "AP", "REPORTED", (30, 50)),
    (18, "TOKYO", "Takaichi meets Putin.", "AP", "REPORTED", (139, 36)),
    (19, "SEOUL", "Lee renews call for N. Korea talks.", "Yonhap", "REPORTED", (127, 37)),
    (20, "DHAKA", "Bangladesh shuts down; Yunus home torched.", "AP", "REPORTED", (90, 24)),
    (21, "JAKARTA", "Indonesia passes asset-forfeiture bill.", "Kompas", "REPORTED", (107, -6)),
    (22, "SUVA", "Fiji declares drought disaster.", "RNZ", "REPORTED", (178, -18)),
    (23, "ANCHORAGE", "Begich keeps Alaska House seat.", "AP", "REPORTED", (-150, 61)),
    (24, "CARACAS", "US and Venezuela restore military ties.", "AP", "REPORTED", (-67, 10)),
    (25, "PORT-AU-PRINCE", "Pastor convicted over Moïse killing.", "AP", "REPORTED", (-72, 19)),
    (26, "DAKAR", "Migrant boat sinks off Senegal; ~100 aboard.", "AP", "REPORTED", (-17, 15)),
    (27, "KHARTOUM", "Sudan: RSF commander defects.", "AP", "REPORTED", (32, 15)),
    (28, "KINSHASA", "Ebola fight stalls in DR Congo.", "AP", "REPORTED", (15, -4)),
    (29, "HORMUZ", "Iran reports 3 tankers on fire (unverified).", "Press TV", "CLAIM", (56, 27)),
    (30, "ZURICH", "Infantino faces first FIFA challenge.", "Reuters", "REPORTED", (8, 47)),
    (31, "SHENZHEN", "APEC adopts Shenzhen Outlook.", "Reuters", "REPORTED", (114, 22)),
    (32, "HOLLYWOOD", "Florida floods shut schools a 2nd day.", "AP", "REPORTED", (-80, 26)),
    (33, "SEOUL", "Top court overturns ex-PM Han's term in part.", "AP", "REPORTED", (127, 37)),
    (34, "NAIROBI", "Marathon champion banned 3 years for doping.", "AIU", "REPORTED", (37, -1)),
    (35, "TANA RIVER", "Floods kill six, displace hundreds.", "Daily Nation", "REPORTED", (40, -1)),
    (36, "TONGA", "Drought emergency declared for 27 days.", "RNZ", "REPORTED", (-175, -21)),
    (37, "COOK ISLANDS", "Cyclone Xavier, Cat 4; 300+ in shelter.", "RNZ", "REPORTED", (-160, -21)),
    (38, "WASHINGTON", "Jobless claims 203,000; continuing +70,000.", "DOL", "REPORTED", (-77, 39)),
    (39, "SPACE", "Red giant seen swallowing a companion star.", "Nature", "REPORTED", (0, 0)),
]


def hero_card(d, box, hero):
    x0, y0, x1, y1 = (int(v) for v in box)
    d.rectangle((x0, y0, x1, y1), fill=(255, 255, 255), outline=(200, 190, 170), width=1)
    scene_box = (x0 + 4, y0 + 4, x1 - 4, y0 + 134)
    hero["scene"](d, scene_box)
    tag(d, x1 - 74, y0 + 8, hero["tag"], TAG_COLORS[hero["tag"]])
    d.text((x0 + 8, y0 + 138), hero["kicker"], font=SANS_B(9), fill=RED)
    lines = wrap(d, hero["headline"], SANS_B(15), x1 - x0 - 16)
    y = y0 + 152
    for ln in lines[:2]:
        d.text((x0 + 8, y), ln, font=SANS_B(15), fill=INK)
        y += 18
    lines = wrap(d, hero["sub"], SANS(11), x1 - x0 - 16)
    for ln in lines[:2]:
        d.text((x0 + 8, y), ln, font=SANS(11), fill=(60, 60, 60))
        y += 12


def mid_card(d, box, mid):
    x0, y0, x1, y1 = (int(v) for v in box)
    d.rectangle((x0, y0, x1, y1), fill=(255, 255, 255), outline=(200, 190, 170), width=1)
    scene_box = (x0 + 3, y0 + 3, x1 - 3, y0 + 55)
    mid["scene"](d, scene_box)
    tag(d, x1 - 66, y0 + 5, mid["tag"], TAG_COLORS[mid["tag"]])
    d.text((x0 + 5, y0 + 58), mid["kicker"], font=SANS_B(8), fill=RED)
    lines = wrap(d, mid["headline"], SANS_B(10), x1 - x0 - 10)
    y = y0 + 69
    for ln in lines[:2]:
        d.text((x0 + 5, y), ln, font=SANS_B(10), fill=INK)
        y += 12
    lines = wrap(d, mid["sub"], SANS(9), x1 - x0 - 10)
    for ln in lines[:2]:
        d.text((x0 + 5, y), ln, font=SANS(9), fill=(60, 60, 60))
        y += 10


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.rectangle([0, 0, W, 92], fill=NAVY)
    d.text((16, 10), "THE WORLD IN ONE DAY", font=SANS_B(13), fill=GOLD)
    d.text((W - 16 - d.textlength("39 STORIES · 7 REGIONS · ALL FROM THIS ONE DAY",
                                  font=SANS_B(11)), 12),
           "39 STORIES · 7 REGIONS · ALL FROM THIS ONE DAY", font=SANS_B(11),
           fill=(255, 255, 255))
    d.text((16, 30), "Thursday, 19 November 2026", font=SERIF_B(34),
           fill=(255, 255, 255))
    d.text((16, 68), "Trump, Xi and Putin share one table · World Court finds genocide · GTA VI ends a 13-year wait",
           font=SERIF(13), fill=(220, 210, 180))

    # ---- timeline strip
    d.text((16, 98), "THE DAY BY HOURS", font=SANS_B(10), fill=RED)
    tl = [("00:00", "GTA VI unlocks"),
          ("MORNING", "leaders sit down"),
          ("08:40", "Suneung begins"),
          ("10:00", "genocide verdict"),
          ("13:30", "jobless claims"),
          ("EVENING", "COP31 takes over")]
    x = 140
    for t, ev in tl:
        d.text((x, 98), t, font=SANS_B(9), fill=INK)
        x += d.textlength(t, font=SANS_B(9)) + 4
        d.text((x, 98), ev, font=SANS(9), fill=(60, 60, 60))
        x += d.textlength(ev, font=SANS(9)) + 12
    d.line([(0, 122), (W, 122)], fill=(200, 190, 170), width=1)

    # ---- region chips
    regions = [("ASIA 9", (178, 60, 40)), ("EUROPE 7", (40, 90, 160)),
               ("MIDDLE EAST 3", (150, 30, 30)), ("AFRICA 6", (40, 120, 60)),
               ("AMERICAS 7", (110, 60, 140)), ("OCEANIA 4", (20, 120, 120)),
               ("GLOBAL 3", (100, 100, 100))]
    x = 16
    for label, color in regions:
        x += chip(d, x, 130, label, color, SANS_B(11)) + 8
    d.text((x + 8, 134), "pins 1–15 on the map · grey dots = briefs 16–39",
           font=SANS(10), fill=(90, 90, 90))

    # ---- number strip (colored chips)
    nums = [("3", "LEADERS AT ONE TABLE"), ("9–6", "GENOCIDE VERDICT"),
            ("$120BN", "AID GOAL DROPPED"), ("$81.3BN", "ANT IPO"),
            ("551,864", "SIT SUNEUNG"), ("109–0", "GREENLAND VOTE")]
    cw = (W - 32) / 6
    for i, (n, lab) in enumerate(nums):
        cx = 16 + i * cw
        rrect(d, [cx, 158, cx + cw - 8, 190], 5, fill=NAVY)
        f = SERIF_B(22)
        tw = d.textlength(n, font=f)
        d.text((cx + (cw - 8 - tw) / 2, 162), n, font=f, fill=GOLD)
        lf = SANS_B(8)
        lw = d.textlength(lab, font=lf)
        d.text((cx + (cw - 8 - lw) / 2, 182), lab, font=lf,
               fill=(255, 255, 255))

    # ---- heroes
    hw = (W - 32 - 16) / 3
    for i, hero in enumerate(HEROES):
        hero_card(d, (16 + i * (hw + 8), 196, 16 + (i + 1) * hw + i * 8, 412), hero)

    # ---- mids, two rows of six
    mw = (W - 32 - 5 * 8) / 6
    for row in range(2):
        for col in range(6):
            mid = MIDS[row * 6 + col]
            x0 = 16 + col * (mw + 8)
            y0 = 420 + row * 120
            mid_card(d, (x0, y0, x0 + mw, y0 + 116), mid)

    # ---- map + briefs
    map_box = (8, 676, 300, 884)
    draw_map(d, map_box)
    d.text((8, 660), "WHERE IT HAPPENED", font=SANS_B(10), fill=RED)
    pins = [(1, 114, 22), (2, 7, 53), (4, 28, 38), (5, -74, 40), (6, 37, 47),
            (7, 48, 24), (8, 86, 20), (9, 127, 37), (10, -74, 4),
            (11, 149, -35), (12, 51, 2), (13, 0, 47), (14, -42, 72),
            (15, 34, 31)]
    for num, lon, lat in pins:
        pin(d, map_box, lon, lat, num)
    for num, place, text, src, tg, (lon, lat) in BRIEFS:
        if lon or lat:
            # skip dots that would sit on top of (or right beside) a numbered pin
            if any(abs(lon - plon) <= 4 and abs(lat - plat) <= 4
                   for _, plon, plat in pins):
                continue
            dot(d, map_box, lon, lat)

    d.text((312, 660), "THE REST OF THE DAY — 24 MORE STORIES · pin 3 = worldwide (GTA VI)",
           font=SANS_B(10), fill=RED)
    col_w = (W - 312 - 8 - 12) / 2
    for i, (num, place, text, src, tg, _) in enumerate(BRIEFS):
        col = i // 12
        row = i % 12
        bx = 312 + col * (col_w + 12)
        by = 676 + row * 17
        f = SANS_B(9)
        d.rectangle([bx, by, bx + 18, by + 13], fill=RED)
        d.text((bx + 9 - d.textlength(str(num), font=f) / 2, by + 1), str(num),
               font=f, fill=(255, 255, 255))
        line = f"{place} — {text} — {src}"
        maxw = col_w - 24 - (68 if tg != "REPORTED" else 0)
        while d.textlength(line, font=SANS(10)) > maxw and len(line) > 4:
            line = line[:-5] + "…"
        d.text((bx + 22, by + 1), line, font=SANS(10), fill=INK)
        if tg != "REPORTED":
            tag(d, bx + col_w - 62, by, tg, TAG_COLORS[tg])

    # ---- legend
    d.text((16, 886), "HOW SURE ARE WE?", font=SANS_B(10), fill=RED)
    lx = 140
    for label, color in [("REPORTED", GREEN), ("CLAIM", AMBER), ("FORECAST", BLUE)]:
        lx += tag(d, lx, 885, label, color) + 6
        desc = {"REPORTED": "confirmed by a named source",
                "CLAIM": "one side's account, unattributed",
                "FORECAST": "expected, not yet happened"}[label]
        d.text((lx, 887), desc, font=SANS(10), fill=(60, 60, 60))
        lx += d.textlength(desc, font=SANS(10)) + 16

    # ---- DATE CHECK
    rrect(d, [8, 906, W - 8, 984], 4, fill=(255, 248, 240),
          outline=RED, width=2)
    d.text((16, 912), "✓ DATE CHECK", font=SANS_B(12), fill=RED)
    d.text((16, 928),
           "Every story here happened, or was first reported, on Thursday 19 November 2026.",
           font=SANS_B(10), fill=INK)
    d.text((16, 944),
           "LEFT OUT AS OTHER DAYS' NEWS — 18 NOV: EU €45bn Ukraine loan · Iran fires on Kuwait and Bahrain ·",
           font=SANS(10), fill=(60, 60, 60))
    d.text((16, 958),
           "Nvidia results · Van Gogh sale · Jeffries named speaker · Derna drug bust · Darmanin on Mélenchon · Anthropic $83 pricing ·",
           font=SANS(10), fill=(60, 60, 60))
    d.text((16, 972),
           "Voyager 1 one light-day. 17 NOV: US strike on Qeshm.",
           font=SANS(10), fill=(60, 60, 60))

    # ---- footer
    d.text((16, 992),
           "Sources: Reuters, AP, AFP, BBC, Al Jazeera, UN News, Yonhap, ABC, IMD, RNZ, Daily Nation, DOL, Nature — Original drawings, drawn in code. Claims are attributed, not stated as fact.",
           font=SANS(8), fill=(90, 90, 90))

    img.save("entry.png", optimize=True)
    data = open("entry.png", "rb").read()
    print("bytes", len(data), "sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
