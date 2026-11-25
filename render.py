#!/usr/bin/env python3
"""Draw entry.png for news-image-20261124: 'THE TUESDAY WORLD'.

A one-day world-news broadsheet front page, 1024x1024, drawn entirely in
code with PIL and system fonts. No network, no randomness, no timestamps:
running this script twice produces byte-identical output.

Layout: masthead, 3 hero panels, dotted world map with 7 numbered pins,
7 colour-coded region bands (35 stories total, every story with a tiny
drawn icon), bottom ticker, date-check box, footer.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
CREAM = (247, 243, 232)
PANEL = (255, 253, 245)
INK = (20, 20, 20)
GREY = (107, 114, 128)
LIGHT = (214, 206, 188)
RED = (220, 38, 38)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def serif_b(size):
    return ImageFont.truetype(os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf"), size)


def sans_b(size):
    return ImageFont.truetype(os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"), size)


def sans(size):
    return ImageFont.truetype(os.path.join(FONT_DIR, "DejaVuSans.ttf"), size)


def text_w(draw, text, font):
    return draw.textlength(text, font=font)


def fit_font(draw, text, start_size, max_width, loader, min_size=9):
    """Largest font size (from loader) that fits max_width."""
    size = start_size
    while size > min_size:
        f = loader(size)
        if text_w(draw, text, f) <= max_width:
            return f
        size -= 1
    return loader(min_size)


def wrap(draw, text, font, max_width):
    """Greedy word wrap into lines that fit max_width."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if text_w(draw, trial, font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def centre(draw, cx, y, text, font, fill=INK):
    w = text_w(draw, text, font)
    draw.text((cx - w / 2, y), text, font=font, fill=fill)
    return w


# ---------------------------------------------------------------- map data
# Simplified continent outlines as (lon, lat) polygons. Dots are plotted on
# a grid inside these polygons; precision is stylised, not cartographic.
NORTH_AMERICA = [
    (-168, 66), (-158, 58), (-152, 60), (-140, 60), (-130, 54), (-125, 49),
    (-124, 42), (-120, 34), (-114, 30), (-105, 22), (-97, 26), (-90, 21),
    (-86, 15), (-83, 9), (-79, 9), (-77, 7), (-80, 9), (-84, 13), (-88, 17),
    (-92, 15), (-96, 19), (-97, 26), (-93, 30), (-89, 30), (-84, 30),
    (-81, 25), (-80, 32), (-76, 35), (-74, 40), (-70, 42), (-68, 45),
    (-65, 44), (-60, 47), (-55, 47), (-60, 52), (-64, 58), (-68, 58),
    (-72, 62), (-78, 62), (-85, 66), (-92, 66), (-95, 69), (-110, 68),
    (-125, 70), (-140, 70), (-155, 71), (-165, 68), (-168, 66),
]
GREENLAND = [
    (-58, 64), (-52, 60), (-43, 60), (-40, 64), (-32, 68), (-25, 70),
    (-20, 74), (-30, 76), (-45, 76), (-58, 74), (-60, 70), (-58, 64),
]
SOUTH_AMERICA = [
    (-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
    (-70, -23), (-70, -30), (-73, -37), (-73, -44), (-70, -52), (-66, -55),
    (-68, -50), (-65, -45), (-62, -40), (-57, -35), (-52, -32), (-48, -27),
    (-41, -22), (-39, -17), (-35, -9), (-35, -6), (-40, -3), (-44, -2),
    (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12), (-76, 10),
    (-79, 9),
]
AFRICA = [
    (-17, 15), (-17, 21), (-15, 27), (-10, 31), (-5, 35), (0, 36), (10, 37),
    (11, 34), (20, 32), (30, 31), (32, 31), (34, 28), (35, 23), (37, 18),
    (39, 15), (43, 12), (48, 11), (51, 12), (46, 6), (41, 3), (40, -2),
    (40, -8), (38, -15), (36, -22), (33, -26), (28, -33), (20, -35),
    (17, -32), (15, -27), (12, -18), (13, -12), (12, -6), (9, -1), (9, 4),
    (4, 6), (-8, 5), (-13, 8), (-17, 12), (-17, 15),
]
EURASIA = [
    (-10, 36), (-9, 43), (-2, 48), (-4, 50), (0, 51), (3, 53), (8, 57),
    (10, 59), (5, 60), (5, 62), (10, 64), (18, 69), (25, 71), (32, 70),
    (40, 68), (50, 69), (60, 69), (70, 72), (80, 73), (90, 75), (100, 76),
    (110, 74), (120, 73), (130, 72), (140, 72), (150, 70), (160, 69),
    (170, 67), (178, 65), (178, 62), (170, 60), (162, 56), (158, 52),
    (150, 59), (142, 55), (140, 50), (135, 44), (130, 42), (127, 40),
    (122, 38), (120, 32), (115, 28), (110, 20), (108, 12), (105, 9),
    (103, 7), (100, 8), (98, 12), (95, 16), (92, 21), (89, 22), (86, 20),
    (82, 17), (80, 13), (77, 8), (75, 15), (72, 20), (68, 22), (66, 25),
    (62, 25), (58, 26), (55, 27), (52, 28), (50, 29), (48, 30), (50, 26),
    (54, 24), (57, 22), (59, 22), (56, 20), (52, 18), (48, 15), (44, 13),
    (42, 15), (39, 20), (38, 24), (36, 29), (34, 31), (30, 36), (27, 37),
    (23, 36), (19, 40), (15, 44), (12, 45), (8, 44), (3, 43), (-2, 37),
    (-6, 36), (-10, 36),
]
BRITAIN = [
    (-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-1, 51),
    (-5, 50),
]
JAPAN = [
    (130, 31), (132, 33), (135, 34), (137, 35), (139, 36), (140, 38),
    (141, 41), (143, 42), (145, 44), (142, 44), (140, 40), (138, 37),
    (136, 35), (133, 34), (131, 32), (130, 31),
]
BORNEO = [
    (109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (113, -3), (110, -1),
    (109, 1),
]
SUMATRA = [
    (95, 5), (98, 3), (100, 0), (103, -3), (105, -5), (104, -6), (101, -3),
    (98, 1), (95, 5),
]
NEW_GUINEA = [
    (131, -1), (136, -2), (141, -3), (146, -6), (150, -8), (147, -9),
    (143, -8), (138, -7), (134, -4), (131, -1),
]
AUSTRALIA = [
    (113, -22), (114, -30), (115, -34), (118, -35), (124, -33), (129, -32),
    (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
    (153, -32), (153, -27), (150, -22), (146, -19), (142, -15), (142, -11),
    (137, -12), (135, -15), (132, -12), (130, -13), (126, -14), (122, -17),
    (118, -20), (113, -22),
]
CONTINENTS = [
    NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA, BRITAIN,
    JAPAN, BORNEO, SUMATRA, NEW_GUINEA, AUSTRALIA,
]


def point_in_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xinters = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xinters:
                inside = not inside
        j = i
    return inside


def lonlat_to_xy(lon, lat, x0, x1, y0, y1):
    x = x0 + (lon + 170.0) / 360.0 * (x1 - x0)
    y = y0 + (80.0 - lat) / 140.0 * (y1 - y0)
    return x, y


# ------------------------------------------------------------------- icons
# Tiny 14x14 glyphs, one per story line. Each draws centred on (cx, cy).
def icon_ship(d, cx, cy, c):
    d.polygon([(cx - 6, cy - 1), (cx + 6, cy - 1), (cx + 4, cy + 4),
               (cx - 4, cy + 4)], fill=c)
    d.rectangle([cx - 2, cy - 6, cx + 2, cy - 1], fill=c)
    d.polygon([(cx + 2, cy - 6), (cx + 6, cy - 2), (cx + 2, cy - 2)], fill=c)
    d.line([(cx - 7, cy + 6), (cx + 7, cy + 6)], fill=c, width=1)


def icon_gavel(d, cx, cy, c):
    d.line([(cx - 5, cy + 5), (cx + 3, cy - 3)], fill=c, width=2)
    d.rectangle([cx + 1, cy - 7, cx + 7, cy - 3], fill=c)
    d.line([(cx - 6, cy + 7), (cx + 6, cy + 7)], fill=c, width=2)


def icon_flame(d, cx, cy, c):
    d.polygon([(cx, cy - 7), (cx + 4, cy - 1), (cx + 5, cy + 3),
               (cx + 2, cy + 6), (cx - 2, cy + 6), (cx - 5, cy + 3),
               (cx - 4, cy - 1)], fill=c)


def icon_car(d, cx, cy, c):
    d.rectangle([cx - 6, cy - 1, cx + 6, cy + 3], fill=c)
    d.rectangle([cx - 4, cy - 4, cx + 3, cy - 1], fill=c)
    d.ellipse([cx - 5, cy + 3, cx - 2, cy + 6], fill=c)
    d.ellipse([cx + 2, cy + 3, cx + 5, cy + 6], fill=c)


def icon_plane(d, cx, cy, c):
    d.polygon([(cx - 7, cy), (cx + 7, cy - 2), (cx + 7, cy + 1),
               (cx - 7, cy + 2)], fill=c)
    d.polygon([(cx - 1, cy - 5), (cx + 1, cy - 5), (cx + 2, cy + 1),
               (cx - 2, cy + 1)], fill=c)
    d.polygon([(cx - 5, cy + 2), (cx - 3, cy + 2), (cx - 2, cy + 6),
               (cx - 6, cy + 6)], fill=c)


def icon_scale(d, cx, cy, c):
    d.line([(cx, cy - 6), (cx, cy + 6)], fill=c, width=2)
    d.line([(cx - 6, cy - 4), (cx + 6, cy - 4)], fill=c, width=2)
    d.polygon([(cx - 7, cy - 4), (cx - 3, cy - 4), (cx - 5, cy + 1)], fill=c)
    d.polygon([(cx + 3, cy - 4), (cx + 7, cy - 4), (cx + 5, cy + 1)], fill=c)
    d.line([(cx - 6, cy + 6), (cx + 6, cy + 6)], fill=c, width=2)


def icon_chip(d, cx, cy, c):
    d.rectangle([cx - 4, cy - 4, cx + 4, cy + 4], fill=c)
    d.rectangle([cx - 2, cy - 2, cx + 2, cy + 2], fill=CREAM)
    for dx in (-4, 0, 4):
        d.line([(cx + dx, cy - 7), (cx + dx, cy - 4)], fill=c, width=1)
        d.line([(cx + dx, cy + 4), (cx + dx, cy + 7)], fill=c, width=1)


def icon_flag(d, cx, cy, c):
    d.line([(cx - 4, cy - 7), (cx - 4, cy + 7)], fill=c, width=2)
    d.polygon([(cx - 4, cy - 7), (cx + 6, cy - 4), (cx - 4, cy - 1)], fill=c)


def icon_blast(d, cx, cy, c):
    for dx, dy in ((-6, -6), (0, -7), (6, -6), (-7, 0), (7, 0),
                   (-6, 6), (0, 7), (6, 6)):
        d.line([(cx, cy), (cx + dx, cy + dy)], fill=c, width=2)
    d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=c)


def icon_tower(d, cx, cy, c):
    d.rectangle([cx - 4, cy - 2, cx + 4, cy + 7], fill=c)
    d.line([(cx, cy - 7), (cx, cy - 2)], fill=c, width=2)
    d.rectangle([cx - 2, cy + 1, cx + 2, cy + 4], fill=CREAM)


def icon_dome(d, cx, cy, c):
    d.polygon([(cx - 7, cy - 2), (cx, cy - 7), (cx + 7, cy - 2)], fill=c)
    for dx in (-5, 0, 5):
        d.rectangle([cx + dx - 1, cy - 2, cx + dx + 1, cy + 5], fill=c)
    d.line([(cx - 7, cy + 6), (cx + 7, cy + 6)], fill=c, width=2)


def icon_mine(d, cx, cy, c):
    for dx, dy in ((-5, -5), (0, -7), (5, -5), (-7, 0), (7, 0),
                   (-5, 5), (0, 7), (5, 5)):
        d.line([(cx, cy), (cx + dx, cy + dy)], fill=c, width=1)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=c)


def icon_med(d, cx, cy, c):
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=c, width=2)
    d.rectangle([cx - 1, cy - 4, cx + 1, cy + 4], fill=c)
    d.rectangle([cx - 4, cy - 1, cx + 4, cy + 1], fill=c)


def icon_ballot(d, cx, cy, c):
    d.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], outline=c, width=2)
    d.line([(cx - 3, cy), (cx - 1, cy + 3), (cx + 4, cy - 3)], fill=c, width=2)


def icon_globe(d, cx, cy, c):
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=c, width=2)
    d.ellipse([cx - 2, cy - 6, cx + 2, cy + 6], outline=c, width=1)
    d.line([(cx - 6, cy), (cx + 6, cy)], fill=c, width=1)


def icon_coin(d, cx, cy, c):
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], outline=c, width=2)
    d.line([(cx, cy - 5), (cx, cy + 5)], fill=c, width=2)
    d.line([(cx - 3, cy - 3), (cx + 3, cy - 3)], fill=c, width=1)
    d.line([(cx - 3, cy + 3), (cx + 3, cy + 3)], fill=c, width=1)


ICONS = {
    "ship": icon_ship, "gavel": icon_gavel, "flame": icon_flame,
    "car": icon_car, "plane": icon_plane, "scale": icon_scale,
    "chip": icon_chip, "flag": icon_flag, "blast": icon_blast,
    "tower": icon_tower, "dome": icon_dome, "mine": icon_mine,
    "med": icon_med, "ballot": icon_ballot, "globe": icon_globe,
    "coin": icon_coin,
}


# ------------------------------------------------------- hero illustrations
def hero_scales(d, x0, y0, w, h, accent):
    cx, top = x0 + w // 2, y0 + 8
    d.line([(cx, top + 6), (cx, top + 78)], fill=INK, width=5)
    d.line([(cx - 52, top + 18), (cx + 52, top + 18)], fill=INK, width=5)
    d.ellipse([cx - 4, top, cx + 4, top + 8], fill=accent)
    for sgn in (-1, 1):
        px = cx + sgn * 52
        d.line([(px, top + 18), (px, top + 44)], fill=INK, width=2)
        d.line([(px - 14, top + 44), (px, top + 18)], fill=INK, width=2)
        d.line([(px + 14, top + 44), (px, top + 18)], fill=INK, width=2)
        d.arc([px - 16, top + 38, px + 16, top + 62], 0, 180, fill=accent, width=4)
    d.line([(cx - 34, top + 86), (cx + 34, top + 86)], fill=INK, width=5)
    d.line([(cx - 26, top + 94), (cx + 26, top + 94)], fill=INK, width=4)
    # small gavel at the side
    d.line([(x0 + w - 52, top + 66), (x0 + w - 22, top + 44)], fill=accent, width=4)
    d.rectangle([x0 + w - 30, top + 34, x0 + w - 12, top + 48], fill=accent)


def hero_courthouse(d, x0, y0, w, h, accent):
    cx, top = x0 + w // 2, y0 + 10
    d.polygon([(cx - 62, top + 30), (cx, top), (cx + 62, top + 30)], fill=accent)
    d.rectangle([cx - 62, top + 30, cx + 62, top + 38], fill=INK)
    for dx in (-44, 0, 44):
        d.rectangle([cx + dx - 7, top + 38, cx + dx + 7, top + 78], fill=INK)
    d.rectangle([cx - 70, top + 78, cx + 70, top + 86], fill=INK)
    d.rectangle([cx - 78, top + 86, cx + 78, top + 94], fill=INK)
    # small chip emblem on the pediment
    d.rectangle([cx - 9, top + 12, cx + 9, top + 28], fill=PANEL)
    d.rectangle([cx - 4, top + 17, cx + 4, top + 23], fill=accent)


def hero_tanker(d, x0, y0, w, h, accent):
    cx, top = x0 + w // 2, y0 + 22
    # spiked mines
    for mx, my in ((x0 + 34, top + 66), (x0 + w - 34, top + 70)):
        for dx, dy in ((-9, -9), (0, -12), (9, -9), (-12, 0), (12, 0),
                       (-9, 9), (0, 12), (9, 9)):
            d.line([(mx, my), (mx + dx, my + dy)], fill=INK, width=2)
        d.ellipse([mx - 8, my - 8, mx + 8, my + 8], fill=INK)
    # hull
    d.polygon([(cx - 78, top + 34), (cx + 78, top + 34), (cx + 58, top + 62),
               (cx - 58, top + 62)], fill=accent)
    d.rectangle([cx - 52, top + 6, cx + 10, top + 34], fill=INK)
    d.rectangle([cx + 18, top + 14, cx + 34, top + 34], fill=INK)
    d.rectangle([cx + 42, top + 2, cx + 52, top + 34], fill=INK)
    d.line([(cx - 52, top + 48), (cx + 52, top + 48)], fill=PANEL, width=3)
    # waves
    for wy in (top + 74, top + 86):
        for k in range(5):
            wx = x0 + 18 + k * 62
            d.arc([wx, wy, wx + 44, wy + 16], 180, 360, fill=INK, width=3)


# ------------------------------------------------------------------ content
BANDS = [
    ("1", "EUROPE", (29, 78, 216), [
        ("ship", "Ukraine hits Russian ships off Finland and Libya"),
        ("globe", "NATO vows defence against threats in space"),
        ("flag", "Zelensky urges Ukraine-Russia-US-Europe talks soon"),
        ("blast", "Zaporizhzhia attack kills 2, wounds 40 incl. children"),
        ("gavel", "Sarkozy corruption case ordered to trial"),
    ]),
    ("2", "MIDDLE EAST", (180, 83, 9), [
        ("flag", "Houthis 60 km from Aden and ready to attack"),
        ("tower", "Saudi PIF tower in Riyadh hit in drone attack, 11 hurt"),
        ("blast", "Saudi strikes on Yemen buses, trucks: 25 dead or missing"),
        ("flag", "Israel kills Hamas internal security chief in Gaza"),
        ("med", "Gaza meningitis epidemic alert after case surge"),
    ]),
    ("3", "ASIA-PACIFIC", (13, 148, 136), [
        ("flame", "Hanoi restaurant blast kills at least six"),
        ("plane", "Malaysia to send thousands of migrants to Myanmar"),
        ("flag", "Hasina plans return to Bangladesh on Dec 16"),
        ("ballot", "Indonesia names two candidates for vice president"),
        ("coin", "Japan to pay full 2027 ICC contribution this year"),
    ]),
    ("4", "AFRICA", (220, 38, 38), [
        ("flag", "Libya's Haftar visits Turkey for the first time"),
        ("plane", "DR Congo searches for missing plane after rebel claim"),
        ("ballot", "Senegal regains AFCON title after court appeal"),
        ("med", "Ituri fighting traps DR Congo Ebola responders"),
    ]),
    ("5", "AMERICAS", (124, 58, 237), [
        ("flag", "Armed men hold 25 hostages at Cartagena supermarket"),
        ("car", "Car bomb outside Colombian offices injures 23"),
        ("plane", "US drone helps capture El Chapo Isidro in Mexico"),
        ("flag", "Bukele names three Salvadorans killed in Haiti"),
        ("tower", "Trump pardons turkeys Freedom and Feathers"),
    ]),
    ("6", "MARKETS & TECH", (5, 150, 105), [
        ("coin", "Iraq orders federal control of Kurdish oilfields"),
        ("chip", "US blacklists Megaspeed over Nvidia scandal"),
        ("gavel", "China sentences official to death for spying"),
        ("plane", "Pentagon rebukes Canada over F-35 and spending"),
    ]),
    ("7", "DEFENCE & SANCTIONS", (71, 85, 105), [
        ("plane", "Turkish Air Force helicopter crash kills five"),
        ("gavel", "UK sanctions Houthis and four senior officials"),
        ("plane", "South Korea shelters Ulleungdo after Russian jets"),
    ]),
]

HEROES = [
    ("ICJ: MYANMAR GUILTY", "OF GENOCIDE",
     "First time UN court finds a state responsible; 9-6 ruling on Rohingya",
     hero_scales, (29, 78, 216)),
    ("HUAWEI GUILTY OF", "TRADE-SECRETS THEFT",
     "US jury convicts on 10 of 12 counts; acquits on racketeering",
     hero_courthouse, (180, 83, 9)),
    ("FOUR TANKERS HIT", "MINES IN HORMUZ",
     "IRGC claims ship attack; strait closure threat grows",
     hero_tanker, (220, 38, 38)),
]

# (lon, lat) of each numbered pin, in band order.
PINS = [
    (-0.1, 51.5),    # 1 Europe — London
    (46.7, 24.7),    # 2 Middle East — Riyadh
    (103.8, 1.35),   # 3 Asia-Pacific — Singapore
    (3.4, 6.5),      # 4 Africa — Lagos
    (-46.6, -23.5),  # 5 Americas — Sao Paulo
    (139.7, 35.7),   # 6 Markets & Tech — Tokyo
    (-77.0, 38.9),   # 7 Defence & Sanctions — Washington DC
]

TICKER = ("Latvia sees war tipping point next year - Norway talks stability "
          "with Kyiv - Germany first on Delta system - Fort Hood shooter "
          "seeks stay")

DATE_CHECK = [
    "DATE CHECK - LEFT OUT (OTHER DAYS): Huang reinstated as Nvidia CEO Mon 23 Nov - Sparta II hit Sat 22 Nov (confirmed Tue)",
    "Riemann proof first reported Sat 22 Nov - Peru quake Fri 21 Nov",
]


# ------------------------------------------------------------------ drawing
def draw_masthead(d):
    centre(d, W // 2, 6, "THE TUESDAY WORLD", serif_b(50))
    centre(d, W // 2, 58, "TUESDAY 24 NOVEMBER 2026", serif_b(56))
    centre(d, W // 2, 120, "THE WORLD IN ONE DAY - 35 STORIES, 7 REGIONS",
           sans_b(17))
    d.line([(8, 142), (W - 8, 142)], fill=INK, width=2)


def draw_heroes(d):
    y0, h = 156, 250
    for i, (l1, l2, caption, art, accent) in enumerate(HEROES):
        x0 = 8 + i * 343
        d.rectangle([x0, y0, x0 + 322, y0 + h], outline=INK, width=2,
                    fill=PANEL)
        d.rectangle([x0, y0, x0 + 322, y0 + 5], fill=accent)
        art(d, x0, y0 + 8, 322, 120, accent)
        f1 = fit_font(d, l1, 24, 296, serif_b, min_size=18)
        f2 = fit_font(d, l2, 24, 296, serif_b, min_size=18)
        centre(d, x0 + 161, y0 + 136, l1, f1)
        centre(d, x0 + 161, y0 + 164, l2, f2)
        lines = wrap(d, caption, sans(14), 296)
        ly = y0 + 196
        for line in lines[:2]:
            centre(d, x0 + 161, ly, line, sans(14))
            ly += 18


def draw_map(d):
    x0, x1, y0, y1 = 8, W - 8, 416, 496
    d.rectangle([x0, y0, x1, y1], outline=LIGHT, width=1)
    step = 5
    for gx in range(x0 + 3, x1, step):
        for gy in range(y0 + 3, y1, step):
            lon = -170.0 + (gx - x0) / (x1 - x0) * 360.0
            lat = 80.0 - (gy - y0) / (y1 - y0) * 140.0
            if any(point_in_poly(lon, lat, poly) for poly in CONTINENTS):
                d.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=GREY)
    for i, (lon, lat) in enumerate(PINS):
        px, py = lonlat_to_xy(lon, lat, x0, x1, y0, y1)
        colour = BANDS[i][2]
        d.line([(px, py + 10), (px, 504)], fill=colour, width=2)
        d.ellipse([px - 10, py - 10, px + 10, py + 10], fill=colour,
                  outline=INK, width=1)
        num = str(i + 1)
        nw = text_w(d, num, sans_b(12))
        d.text((px - nw / 2, py - 8), num, font=sans_b(12), fill=(255, 255, 255))


def draw_bands(d):
    y = 508
    for num, name, colour, stories in BANDS:
        n = len(stories)
        rows = (n + 1) // 2
        band_h = 18 + rows * 17
        # header: number chip + name
        d.rectangle([16, y, 33, y + 17], fill=colour)
        nw = text_w(d, num, sans_b(12))
        d.text((24 - nw / 2, y + 2), num, font=sans_b(12), fill=(255, 255, 255))
        d.text((42, y + 1), name, font=sans_b(15), fill=INK)
        # stories in two columns, left column first
        left = stories[:(n + 1) // 2]
        right = stories[(n + 1) // 2:]
        for col, col_stories in enumerate((left, right)):
            col_x = 16 if col == 0 else 516
            for r, (glyph, headline) in enumerate(col_stories):
                ry = y + 18 + r * 17
                ICONS[glyph](d, col_x + 7, ry + 8, colour)
                d.text((col_x + 22, ry + 1), headline, font=sans(14), fill=INK)
        y += band_h
    return y


def draw_bottom(d):
    # ticker
    label = "ALSO TODAY - "
    rest = TICKER
    font = fit_font(d, label + rest, 14, W - 32, sans, min_size=11)
    bold = sans_b(font.size)
    d.text((16, 946), label, font=bold, fill=INK)
    lw = text_w(d, label, bold)
    d.text((16 + lw, 946), rest, font=font, fill=INK)
    # date-check box
    d.rectangle([8, 964, W - 8, 990], outline=RED, width=2)
    d.text((16, 966), DATE_CHECK[0], font=sans(11), fill=RED)
    d.text((16, 977), DATE_CHECK[1], font=sans(11), fill=RED)
    # footer
    centre(d, W // 2, 994,
           "Every story above happened or was first reported on Tuesday 24 November 2026.",
           sans(12))


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    img = Image.new("RGB", (W, H), CREAM)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_heroes(d)
    draw_map(d)
    draw_bands(d)
    draw_bottom(d)
    img.save(out, "PNG", optimize=True)
    size = os.path.getsize(out)
    print(f"{out}: {img.size[0]}x{img.size[1]} {size} bytes "
          f"({'OK' if size <= 1048576 else 'OVER 1 MiB'})")


if __name__ == "__main__":
    main()
