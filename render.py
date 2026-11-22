#!/usr/bin/env python3
"""Draw the Sunday 22 November 2026 front page for news-image-20261122.

One 1024x1024 newspaper page holding 35 stories that all happened, or
were first reported, on Sunday 22 November 2026. Top to bottom: a navy
masthead, the date set large in serif, a red ticker, a strip of six
numbers, a colour-coded bar of stories per region, three lead panels
with flat vector art, ten feature panels with small pictograms, a
schematic world map with thirteen numbered pins, twenty-two one-line
briefs, a red DATE CHECK box naming the other days' news left out on
purpose, and a sources footer.

Everything is drawn in code with Pillow on cream paper. No photographs,
no outside images. The run is deterministic: the same script always
writes the same entry.png bytes.
"""

import math

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024

CREAM = (247, 242, 230)
INK = (24, 24, 24)
NAVY = (18, 38, 66)
RED = (178, 34, 28)
BLUE = (31, 80, 140)
GREY = (110, 108, 100)
WHITE = (255, 255, 255)
SKY = (188, 214, 232)
LAND = (224, 206, 168)
GOLD = (214, 158, 24)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

REGION_COLOURS = {
    "EUROPE": (31, 80, 140),
    "MIDDLE EAST": (200, 110, 20),
    "AMERICAS": (20, 120, 120),
    "ASIA-PACIFIC": (46, 125, 60),
    "AFRICA": (150, 110, 30),
    "WORLD": (90, 90, 90),
}
REGION_ORDER = ["EUROPE", "MIDDLE EAST", "AMERICAS", "ASIA-PACIFIC",
                "AFRICA", "WORLD"]

_FONT_CACHE = {}


def load_font(path, size):
    key = (path, size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(path, size)
    return _FONT_CACHE[key]


def wrap_lines(draw, text, fnt, max_width):
    """Greedy word wrap: pack as many words per line as fit."""
    lines = []
    current = ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_para(draw, x, y, text, fnt, max_width, fill=INK, leading=3):
    """Draw wrapped text; return the y just below the last line."""
    lines = wrap_lines(draw, text, fnt, max_width)
    step = fnt.size + leading
    for i, line in enumerate(lines):
        draw.text((x, y + i * step), line, font=fnt, fill=fill)
    return y + len(lines) * step


def draw_centred(draw, cx, y, text, fnt, fill=INK):
    width = draw.textlength(text, font=fnt)
    draw.text((cx - width / 2, y), text, font=fnt, fill=fill)


# ------------------------------------------------------------------ stories
# Each lead: number, region, dateline, beat, headline, summary, source.
LEADS = [
    (1, "EUROPE", "ANTALYA, TÜRKIYE", "CLIMATE",
     "COP31 close to a final deal after the fossil-fuel fight",
     "New package after the fossil-fuel fight; delegations have until "
     "03:00 GMT to object. No deal signed yet.",
     "Reuters / BBC"),
    (2, "EUROPE", "KYIV, UKRAINE", "WAR",
     "Russia fires 400 drones and 110 missiles at Ukraine",
     "One of the war's largest overnight attacks; at least seven killed "
     "in Kyiv.",
     "Al Jazeera"),
    (3, "MIDDLE EAST", "MANAMA, BAHRAIN", "IRAN WAR",
     "Iran strikes US bases in Bahrain as tankers burn",
     "An industrial site burns and no one is injured; tankers are hit "
     "in the Strait of Hormuz as the war widens.",
     "Al Jazeera / CNA"),
]

# Each feature: number, region, dateline, beat, headline, summary,
# source, pictogram kind.
FEATURES = [
    (4, "EUROPE", "GULF OF FINLAND", "WAR",
     "Russian cargo ship burns after drone strike",
     "Finland says Ukraine likely behind it; 16 crew evacuated.",
     "Reuters / BBC", "ship"),
    (5, "EUROPE", "KRYVYI RIH", "WAR",
     "Strike hits Zelenskyy's home city",
     "Two people are killed and 60 hurt in Kryvyi Rih.",
     "Al Jazeera", "burst"),
    (6, "AFRICA", "BAYELSA, NIGERIA", "DISASTER",
     "Boat carrying mourners capsizes",
     "Twenty-four people drown when a funeral boat overturns.",
     "DW / Sky News", "boat"),
    (7, "MIDDLE EAST", "JERUSALEM", "POLITICS",
     "Eisenkot invites Likud to talks",
     "The former general reaches across the aisle in Jerusalem.",
     "Straits Times", "talks"),
    (8, "MIDDLE EAST", "GAZA", "WAR",
     "Strike hits food aid vehicle",
     "Three Palestinians die when an aid vehicle is struck.",
     "Al Jazeera / Reuters", "truck"),
    (9, "AMERICAS", "SINALOA, MEXICO", "CRIME",
     "‘El Chapo Isidro’ caught; violence follows",
     "FBI top-ten fugitive held; 11 die in the violence.",
     "Sky News / BBC", "badge"),
    (10, "MIDDLE EAST", "TEHRAN, IRAN", "ENERGY",
     "Iran to ration electricity",
     "War damage hits the energy network, so power is rationed.",
     "Straits Times", "bolt"),
    (11, "AMERICAS", "WASHINGTON", "BUSINESS",
     "Nvidia faces US accounting probe",
     "An SEC inquiry is at an early stage, officials say.",
     "Straits Times", "chart"),
    (12, "AMERICAS", "BRASILIA, BRAZIL", "POLITICS",
     "Bolsonaro in intensive care",
     "The ex-president is stable and breathing on his own.",
     "Al Jazeera / Reuters", "pulse"),
    (13, "ASIA-PACIFIC", "CANBERRA", "DEFENCE",
     "Marles rejects US report on AUKUS subs",
     "Canberra pushes back on the report.",
     "ABC / Reuters", "sub"),
]

# Each brief: number, region, place, one-line story, source.
BRIEFS = [
    (14, "AMERICAS", "US", "FBI looks into apparent hack of its crime database.", "BBC"),
    (15, "AMERICAS", "US", "Teen gamer and his mother help FBI rescue a girl.", "BBC"),
    (16, "AMERICAS", "US", "Midterm loss corners Vance as 2028 field widens.", "ST"),
    (17, "MIDDLE EAST", "Saudi Arabia", "Air defences down a missile.", "Investing.com"),
    (18, "MIDDLE EAST", "Lebanon", "Aoun demands Israeli withdrawal.", "Al Jazeera"),
    (19, "MIDDLE EAST", "Iran", "President warns of a ‘silent economic war’.", "Al Jazeera"),
    (20, "MIDDLE EAST", "Hormuz", "Lewis Pugh swims strait as tanker is struck.", "BBC"),
    (21, "EUROPE", "Moldova", "Reports a Russian airspace breach.", "Kyiv Ind."),
    (22, "EUROPE", "Belgium", "Air traffic to halt in 23 Nov national strike.", "ST"),
    (23, "EUROPE", "Germany", "IG Metall widens car and shipyard strikes.", "Reuters"),
    (24, "EUROPE", "Portugal", "Thousands march in Lisbon on living costs.", "Reuters"),
    (25, "EUROPE", "Denmark", "Expels Russian attaché over rapper plot.", "Guardian"),
    (26, "ASIA-PACIFIC", "Bangladesh", "30 Awami League homes set on fire.", "TOI"),
    (27, "ASIA-PACIFIC", "Australia", "Fred Nile, ex-NSW MP, dies aged 92.", "ABC"),
    (28, "ASIA-PACIFIC", "Australia", "Bystanders pull driver from burning car.", "ABC"),
    (29, "ASIA-PACIFIC", "Melbourne", "70 years since the 1956 Olympics opened.", "ABC"),
    (30, "WORLD", "Trade", "EU and Indonesia sign deal after 10 years.", "DW"),
    (31, "WORLD", "Rugby", "England beat New Zealand 37-12.", "Reuters"),
    (32, "WORLD", "Rugby", "France beat Argentina to reach the final.", "Reuters"),
    (33, "WORLD", "Football", "Arsenal 2-1 Newcastle; Leeds 4-1 Chelsea.", "BBC"),
    (34, "WORLD", "Tennis", "Zverev v Alcaraz in today’s ATP Finals final.", "TOI"),
    (35, "WORLD", "Football", "Liverpool host Manchester United today.", "Al Jazeera"),
]

ALL_STORIES = LEADS + [
    (n, r, loc, beat, head, summ, src)
    for (n, r, loc, beat, head, summ, src, _icon) in FEATURES
] + [
    (n, r, loc, "", txt, src) for (n, r, loc, txt, src) in BRIEFS
]
assert len(ALL_STORIES) == 35, len(ALL_STORIES)
REGION_COUNTS = {r: sum(1 for s in ALL_STORIES if s[1] == r)
                 for r in REGION_ORDER}
assert sum(REGION_COUNTS.values()) == 35
assert REGION_COUNTS == {"EUROPE": 9, "MIDDLE EAST": 8, "AMERICAS": 6,
                         "ASIA-PACIFIC": 5, "AFRICA": 1, "WORLD": 6}, \
    REGION_COUNTS

# The six numbers in the strip: big figure, caption, small sub-caption.
NUMBERS = [
    ("~200", "NATIONS AT COP31", "nearly 200 countries"),
    ("03:00", "GMT OBJECTION DEADLINE", "to object to the deal"),
    ("400+", "DRONES FIRED AT UKRAINE", "overnight barrage"),
    ("110", "MISSILES IN THE SAME NIGHT", "one of the war's largest"),
    ("7+", "PEOPLE KILLED IN KYIV", "at least seven dead"),
    ("2", "US BASES TARGETED", "in Bahrain by Iran"),
]

# Map pins: story number -> (longitude, latitude).
PINS = {1: (30.7, 36.9), 2: (30.5, 50.4), 3: (50.6, 26.2),
        4: (24.0, 59.5), 5: (33.4, 47.9), 6: (6.3, 4.8),
        7: (35.2, 31.8), 8: (34.5, 31.5), 9: (-107.4, 24.8),
        10: (51.4, 35.7), 11: (-77.0, 38.9), 12: (-47.9, -15.8),
        13: (149.1, -35.3)}
# Hand-set pixel shifts so pins bunched in Europe and the Middle East
# (Kyiv/Antalya/Kryvyi Rih/Finland, Bahrain/Tehran, Jerusalem/Gaza)
# sit apart instead of on top of each other.
PIN_NUDGE = {4: (-30, -8), 2: (-24, 4), 5: (20, -10), 1: (-2, 22),
             7: (-28, 6), 8: (26, 14), 10: (-6, -16), 3: (18, -6)}


# ------------------------------------------------------------------- icons
def burst(draw, cx, cy, radius, colour):
    """Sixteen-point star: alternating long and short spikes."""
    points = []
    for i in range(16):
        angle = math.pi * i / 8
        reach = radius if i % 2 == 0 else radius * 0.45
        points.append((cx + reach * math.cos(angle),
                       cy + reach * math.sin(angle)))
    draw.polygon(points, fill=colour)


def paint_icon(draw, kind, x, y, w, h, colour):
    """Tiny flat pictogram inside the box (x, y, w, h)."""
    cx = x + w / 2
    cy = y + h / 2
    if kind == "ship":
        draw.rectangle([x + 4, cy - 2, x + w - 4, cy + 5], fill=colour)
        draw.rectangle([x + 12, cy - 10, x + 22, cy - 2], fill=colour)
        draw.polygon([(cx + 2, cy - 10), (cx + 8, cy - 16),
                      (cx + 12, cy - 10)], fill=(230, 110, 20))
        draw.line([x + 2, cy + 8, x + w - 2, cy + 8], fill=BLUE, width=2)
    elif kind == "burst":
        burst(draw, cx, cy, 11, (230, 140, 20))
        burst(draw, cx, cy, 6, (178, 34, 28))
    elif kind == "boat":
        draw.polygon([(x + 6, cy - 2), (x + w - 6, cy - 2),
                      (x + w - 12, cy + 6), (x + 12, cy + 6)], fill=colour)
        draw.line([x + 2, cy + 9, x + w - 2, cy + 9], fill=BLUE, width=2)
        draw.arc([x + 8, cy + 6, x + 20, cy + 14], 0, 180, fill=BLUE,
                 width=2)
    elif kind == "talks":
        draw.ellipse([x + 2, y + 2, x + 20, y + 14], fill=colour)
        draw.polygon([(x + 8, y + 13), (x + 6, y + 19), (x + 13, y + 13)],
                     fill=colour)
        draw.ellipse([x + 22, y + 6, x + 40, y + 18], fill=(200, 110, 20))
        draw.polygon([(x + 34, y + 17), (x + 36, y + 20), (x + 29, y + 17)],
                     fill=(200, 110, 20))
    elif kind == "truck":
        draw.rectangle([x + 2, y + 4, x + 24, y + 14], fill=colour)
        draw.rectangle([x + 25, y + 7, x + 36, y + 14], fill=colour)
        draw.ellipse([x + 7, y + 14, x + 13, y + 20], fill=INK)
        draw.ellipse([x + 27, y + 14, x + 33, y + 20], fill=INK)
        draw.text((x + 8, y + 6), "+", font=load_font(SANS_BOLD, 8),
                  fill=WHITE)
    elif kind == "badge":
        burst(draw, cx, cy, 10, GOLD)
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=NAVY)
        draw.text((cx - 2, cy - 6), "*", font=load_font(SANS_BOLD, 9),
                  fill=WHITE)
    elif kind == "bolt":
        draw.polygon([(cx + 3, y + 1), (cx - 7, cy + 4), (cx - 1, cy + 4),
                      (cx - 4, y + h - 1), (cx + 7, cy - 2),
                      (cx + 1, cy - 2)], fill=(230, 170, 20))
    elif kind == "chart":
        draw.line([x + 4, y + h - 3, x + w - 4, y + h - 3], fill=INK,
                  width=2)
        draw.line([x + 4, y + h - 3, x + 4, y + 3], fill=INK, width=2)
        for i, bh in enumerate((6, 10, 14)):
            draw.rectangle([x + 9 + i * 9, y + h - 4 - bh,
                            x + 15 + i * 9, y + h - 4], fill=colour)
    elif kind == "pulse":
        draw.line([(x + 2, cy), (x + 10, cy), (x + 14, cy - 8),
                   (x + 18, cy + 8), (x + 22, cy - 4), (x + 26, cy),
                   (x + w - 2, cy)], fill=RED, width=2)
    elif kind == "sub":
        draw.ellipse([x + 4, cy - 6, x + w - 4, cy + 6], fill=colour)
        draw.rectangle([cx - 4, cy - 11, cx + 4, cy - 4], fill=colour)
        draw.line([x + 2, cy + 9, x + w - 2, cy + 9], fill=BLUE, width=2)


def paint_lead_art(draw, which, x, y, w, h):
    """Flat vector illustration for one lead panel."""
    if which == 1:
        # COP31: a globe with an overtime clock beside it.
        draw.rectangle([x, y, x + w, y + h], fill=(205, 228, 210))
        draw.ellipse([x + 14, y + 8, x + 86, y + h - 8],
                     fill=(70, 130, 190), outline=NAVY, width=2)
        draw.ellipse([x + 26, y + 16, x + 46, y + 34], fill=(90, 170, 90))
        draw.ellipse([x + 52, y + 40, x + 76, y + 56], fill=(90, 170, 90))
        draw.ellipse([x + 30, y + 46, x + 44, y + 58], fill=(90, 170, 90))
        draw.arc([x + 50, y + 8, x + 86, y + h - 8], 300, 60, fill=WHITE,
                 width=2)
        cx, cy, r = x + w - 52, y + h / 2, 24
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE,
                     outline=INK, width=2)
        draw.line([cx, cy, cx, cy - 15], fill=INK, width=2)
        draw.line([cx, cy, cx + 12, cy + 6], fill=INK, width=2)
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
        draw.text((cx - 26, cy + r + 2), "OVERTIME",
                  font=load_font(SANS_BOLD, 8), fill=RED)
    elif which == 2:
        # Kyiv barrage: night sky, drone trails, bursts, skyline.
        draw.rectangle([x, y, x + w, y + h], fill=(16, 28, 52))
        for sx, sy in [(x + 30, y + 8), (x + 90, y + 16), (x + 160, y + 6),
                       (x + 220, y + 14), (x + 260, y + 8),
                       (x + 300, y + 18)]:
            draw.ellipse([sx, sy, sx + 2, sy + 2], fill=WHITE)
        for mx, my in [(x + 70, y + 12), (x + 165, y + 20),
                       (x + 255, y + 10)]:
            draw.line([mx - 26, my + 16, mx, my], fill=(255, 220, 120),
                      width=2)
            draw.line([mx - 8, my - 3, mx + 8, my + 3], fill=WHITE,
                      width=2)
            draw.line([mx - 8, my + 3, mx + 8, my - 3], fill=WHITE,
                      width=2)
        for mx, my in [(x + 110, y + 34), (x + 210, y + 30)]:
            burst(draw, mx, my, 10, (255, 180, 40))
            burst(draw, mx, my, 5, (255, 255, 255))
        for bx, bh in [(x + 8, 16), (x + 40, 24), (x + 80, 14),
                       (x + 120, 26), (x + 160, 18), (x + 200, 24),
                       (x + 240, 14), (x + 280, 22)]:
            draw.rectangle([bx, y + h - bh, bx + 34, y + h],
                           fill=(8, 14, 28))
            draw.rectangle([bx + 8, y + h - bh - 6, bx + 14, y + h - bh],
                           fill=(8, 14, 28))
    else:
        # Bahrain: sea, a tanker, and a burning industrial site.
        draw.rectangle([x, y, x + w, y + h], fill=(240, 200, 150))
        draw.rectangle([x, y + h - 16, x + w, y + h], fill=(40, 90, 140))
        draw.rectangle([x + 14, y + h - 30, x + 110, y + h - 16], fill=INK)
        draw.rectangle([x + 84, y + h - 42, x + 100, y + h - 30], fill=INK)
        draw.rectangle([x + 20, y + h - 36, x + 30, y + h - 30], fill=INK)
        for bx, bh in [(x + 150, 30), (x + 180, 38), (x + 210, 26),
                       (x + 240, 34)]:
            draw.rectangle([bx, y + h - 16 - bh, bx + 22, y + h - 16],
                           fill=(90, 80, 70))
        for fx, fy in [(x + 158, y + h - 50), (x + 216, y + h - 44),
                       (x + 248, y + h - 52)]:
            draw.polygon([(fx, fy), (fx + 6, fy - 12), (fx + 12, fy)],
                         fill=(230, 110, 20))
            draw.polygon([(fx + 3, fy), (fx + 6, fy - 7), (fx + 9, fy)],
                         fill=(255, 200, 40))
        for sx, sy, sr in [(x + 170, y + 8, 7), (x + 195, y + 4, 9),
                           (x + 225, y + 10, 6)]:
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                         fill=(120, 115, 110))


# --------------------------------------------------------------------- map
def project(lon, lat, mx, my, mw, mh):
    """Schematic equirectangular projection into the map box."""
    return mx + (lon + 170) / 360.0 * mw, my + (75 - lat) / 130.0 * mh


CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69),
     (-85, 66), (-80, 73), (-65, 60), (-55, 47), (-70, 42), (-75, 35),
     (-80, 26), (-90, 21), (-97, 16), (-105, 20), (-115, 28),
     (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    # Greenland
    [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-20, 70), (-30, 74),
     (-50, 76), (-60, 74), (-58, 64)],
    # South America
    [(-80, 9), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-58, -35), (-65, -41),
     (-70, -50), (-73, -53), (-70, -40), (-72, -25), (-77, -12),
     (-81, -5), (-80, 2)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
     (25, 65), (20, 70), (15, 70), (10, 64), (5, 58), (-2, 55),
     (-5, 50), (-10, 43), (-10, 37)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53),
     (-1, 51)],
    # Africa
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (51, 11), (48, 2), (40, -10), (35, -18),
     (32, -26), (26, -34), (19, -35), (15, -27), (12, -18), (9, -1),
     (9, 4), (-8, 5), (-15, 12)],
    # Asia
    [(28, 62), (35, 68), (50, 70), (70, 72), (90, 75), (110, 76),
     (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (162, 55),
     (158, 50), (150, 45), (142, 42), (140, 38), (135, 35), (130, 33),
     (127, 35), (122, 38), (120, 32), (115, 28), (110, 20), (108, 12),
     (105, 8), (100, 6), (97, 10), (92, 15), (88, 22), (85, 20),
     (80, 15), (77, 8), (74, 20), (70, 23), (66, 25), (62, 25),
     (58, 26), (55, 26), (52, 28), (50, 30), (48, 30), (44, 29),
     (40, 31), (36, 36), (32, 36), (28, 38), (26, 40), (24, 45),
     (22, 50), (24, 55), (26, 60)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (143, 44),
     (141, 45), (139, 40), (136, 36), (132, 33)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
     (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
     (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20)],
]


# ------------------------------------------------------------------ sections
def paint_header(draw):
    draw.rectangle([0, 0, PAGE, 24], fill=NAVY)
    draw.text((10, 4), "THE WORLD IN ONE DAY",
              font=load_font(SANS_BOLD, 15), fill=WHITE)
    right = "35 STORIES · 6 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    rw = draw.textlength(right, font=load_font(SANS_BOLD, 10))
    draw.text((PAGE - 10 - rw, 6), right, font=load_font(SANS_BOLD, 10),
              fill=WHITE)

    draw_centred(draw, PAGE // 2, 28, "Sunday 22 November 2026",
                 load_font(SERIF_BOLD, 34), fill=NAVY)
    draw.line([10, 64, PAGE - 10, 64], fill=RED, width=2)

    draw_centred(draw, PAGE // 2, 68,
                 "COP31 deal close  ·  Russia's 400-drone barrage  "
                 "·  Iran hits US bases in Bahrain",
                 load_font(SANS_BOLD, 11), fill=RED)


def paint_numbers(draw):
    top, bottom = 86, 128
    cell_w = (PAGE - 20 - 5 * 6) / 6
    for i, (num, cap, sub) in enumerate(NUMBERS):
        x = 10 + i * (cell_w + 6)
        draw.rectangle([x, top, x + cell_w, bottom], fill=WHITE,
                       outline=GREY, width=1)
        draw_centred(draw, x + cell_w / 2, top + 2, num,
                     load_font(SERIF_BOLD, 19), fill=NAVY)
        draw_centred(draw, x + cell_w / 2, top + 24, cap,
                     load_font(SANS_BOLD, 8), fill=INK)
        if sub:
            draw_centred(draw, x + cell_w / 2, top + 34, sub,
                         load_font(SANS, 7), fill=GREY)


def paint_region_bar(draw):
    top, bottom = 132, 148
    draw.text((10, top + 3), "STORIES BY REGION:",
              font=load_font(SANS_BOLD, 10), fill=INK)
    bar_w = PAGE - 10 - 170
    x = 180
    for region in REGION_ORDER:
        n = REGION_COUNTS[region]
        seg = bar_w * n / 35.0
        colour = REGION_COLOURS[region]
        draw.rectangle([x, top, x + seg - 1, bottom], fill=colour)
        label = f"{region} {n}"
        lw = draw.textlength(label, font=load_font(SANS_BOLD, 7))
        if seg > lw + 4:
            draw.text((x + (seg - lw) / 2, top + 5), label,
                      font=load_font(SANS_BOLD, 7), fill=WHITE)
        else:
            # Segment too narrow for its label: a short leader down to a
            # label below the bar, in the segment colour.
            mid = x + seg / 2
            draw.line([mid, bottom, mid, bottom + 3], fill=colour, width=1)
            draw.text((mid - lw / 2, bottom + 3), label,
                      font=load_font(SANS_BOLD, 7), fill=colour)
        x += seg


def paint_leads(draw):
    top, bottom = 160, 316
    panel_w = (PAGE - 20 - 2 * 8) / 3
    for i, (n, region, loc, beat, head, summ, src) in enumerate(LEADS):
        x = 10 + i * (panel_w + 8)
        colour = REGION_COLOURS[region]
        draw.rectangle([x, top, x + panel_w, bottom], fill=WHITE,
                       outline=GREY, width=1)
        draw.rectangle([x, top, x + panel_w, top + 18], fill=colour)
        draw.text((x + 6, top + 3), f"{n} · {loc} — {beat}",
                  font=load_font(SANS_BOLD, 9), fill=WHITE)
        paint_lead_art(draw, n, x + 1, top + 19, panel_w - 2, 56)
        hy = draw_para(draw, x + 8, top + 82, head,
                       load_font(SERIF_BOLD, 15), panel_w - 16, fill=NAVY,
                       leading=1)
        draw_para(draw, x + 8, hy + 3, summ, load_font(SANS, 10),
                  panel_w - 16, leading=2)
        draw.text((x + 8, bottom - 14), f"Source: {src}",
                  font=load_font(SANS, 8), fill=GREY)


def paint_features(draw):
    first_y = 322
    height, width, gap = 86, (PAGE - 20 - 4 * 6) / 5, 6
    for i, (n, region, loc, beat, head, summ, src, icon) in enumerate(FEATURES):
        col_i, row_i = i % 5, i // 5
        x = 10 + col_i * (width + gap)
        y = first_y + row_i * (height + gap)
        colour = REGION_COLOURS[region]
        draw.rectangle([x, y, x + width, y + height], fill=WHITE,
                       outline=GREY, width=1)
        draw.rectangle([x, y, x + width, y + 15], fill=colour)
        draw.text((x + 5, y + 2), f"{n} · {loc} — {beat}",
                  font=load_font(SANS_BOLD, 8), fill=WHITE)
        paint_icon(draw, icon, x + 5, y + 17, 42, 20, colour)
        draw.text((x + 50, y + 19), beat, font=load_font(SANS_BOLD, 8),
                  fill=GREY)
        hy = draw_para(draw, x + 5, y + 39, head,
                       load_font(SERIF_BOLD, 11), width - 10, fill=NAVY,
                       leading=0)
        draw_para(draw, x + 5, hy + 1, summ, load_font(SANS, 8),
                  width - 10, leading=1)
        draw.text((x + 5, y + height - 11), f"Source: {src}",
                  font=load_font(SANS, 7), fill=GREY)


def paint_map(draw):
    top, bottom = 506, 610
    draw.text((10, top), "WHERE IT HAPPENED",
              font=load_font(SANS_BOLD, 12), fill=NAVY)
    note = "Schematic map — pins match stories 1–13"
    draw.text((PAGE - 10 - draw.textlength(note, font=load_font(SANS, 9)),
               top + 1), note, font=load_font(SANS, 9), fill=GREY)
    mx, my, mw, mh = 10, top + 18, PAGE - 20, bottom - top - 18
    draw.rectangle([mx, my, mx + mw, my + mh], fill=SKY, outline=GREY,
                   width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        draw.polygon(pts, fill=LAND, outline=(150, 130, 95))
    for n, (lon, lat) in sorted(PINS.items()):
        px, py = project(lon, lat, mx, my, mw, mh)
        dx, dy = PIN_NUDGE.get(n, (0, 0))
        if (dx, dy) != (0, 0):
            draw.line([px, py, px + dx, py + dy], fill=RED, width=1)
            px, py = px + dx, py + dy
        draw.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                     outline=WHITE, width=1)
        tw = draw.textlength(str(n), font=load_font(SANS_BOLD, 9))
        draw.text((px - tw / 2, py - 7), str(n),
                  font=load_font(SANS_BOLD, 9), fill=WHITE)


def paint_briefs(draw):
    top = 616
    draw.text((10, top), "ALSO ON SUNDAY 22 NOVEMBER 2026 — 22 MORE STORIES",
              font=load_font(SANS_BOLD, 12), fill=NAVY)
    draw.line([10, top + 17, PAGE - 10, top + 17], fill=RED, width=2)
    base = load_font(SANS, 10)
    col_w = (PAGE - 20 - 16) / 2
    for i, (n, region, loc, txt, src) in enumerate(BRIEFS):
        col_i, row_i = i // 11, i % 11
        x = 10 + col_i * (col_w + 16)
        y = top + 22 + row_i * 18
        draw.rectangle([x, y + 1, x + 4, y + 13],
                       fill=REGION_COLOURS[region])
        line = f"{n}. {loc}: {txt} ({src})"
        # One line each: shrink the font, then shorten, until it fits.
        fnt = base
        while draw.textlength(line, font=fnt) > col_w - 10 and fnt.size > 8:
            fnt = load_font(SANS, fnt.size - 1)
        while draw.textlength(line, font=fnt) > col_w - 10:
            line = line[: -5].rstrip() + "…"
        draw.text((x + 8, y), line, font=fnt, fill=INK)


def paint_date_check(draw):
    top, bottom = 842, 960
    draw.rectangle([10, top, PAGE - 10, bottom], fill=(255, 240, 238),
                   outline=RED, width=2)
    draw.text((20, top + 5), "DATE CHECK", font=load_font(SANS_BOLD, 12),
              fill=RED)
    check = ("Every story on this page happened, or was first reported, on "
             "Sunday 22 November 2026 — wires read up to 05:00 UTC. "
             "LEFT OUT because it was other days' news: the Peru earthquake "
             "(20 Nov local); Russian missiles landing in Poland (19 Nov); "
             "the Kerch Bridge strikes (earlier this week); the Shenzhen "
             "summit (19 Nov); the Anthropic IPO debut (Thu 19 Nov); the "
             "GTA VI launch (Thu 19 Nov); Wall Street's correction "
             "(Fri 20 Nov).")
    draw_para(draw, 20, top + 23, check, load_font(SANS, 10), PAGE - 40,
              leading=2)


def paint_footer(draw):
    y = 966
    draw_centred(draw, PAGE // 2, y,
                 "Sources: Reuters, BBC, Al Jazeera, DW, The Straits Times, "
                 "Sky News, CNA, ABC Australia, Times of India, The Guardian, "
                 "Kyiv Independent.",
                 load_font(SANS, 9), fill=GREY)
    draw_centred(draw, PAGE // 2, y + 13,
                 "Every story names its outlet. Pictures and map: original, "
                 "drawn in code.",
                 load_font(SANS, 8), fill=GREY)


# -------------------------------------------------------------------- build
def build_page():
    img = Image.new("RGB", (PAGE, PAGE), CREAM)
    draw = ImageDraw.Draw(img)
    paint_header(draw)
    paint_numbers(draw)
    paint_region_bar(draw)
    paint_leads(draw)
    paint_features(draw)
    paint_map(draw)
    paint_briefs(draw)
    paint_date_check(draw)
    paint_footer(draw)
    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size)
    return img


if __name__ == "__main__":
    build_page()
