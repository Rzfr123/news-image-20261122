#!/usr/bin/env python3
"""Render the news-image-20261122 entry.

A newspaper front page summing up Sunday 22 November 2026: 35 dated
stories on one 1024x1024 page. Masthead -> giant date -> ticker ->
numbers strip -> region bar -> 3 lead panels -> 10 feature panels ->
world map with numbered pins -> 22 more one-line briefs -> DATE CHECK
box (listing the earlier news deliberately left out) -> sources footer.

Everything is drawn programmatically with Pillow on cream paper: flat
vector illustrations, original drawings, no photographs. All headlines
and facts are our own wording about the consensus Sunday 22 November
stories from the top-leaderboard study in run-notes.md (COP31 close to
a deal, Russia's 400-drone barrage, Iran striking US bases in Bahrain,
the Sparta II ship fire, 'El Chapo Isidro' caught, Bolsonaro in
intensive care, ...). Output: entry.png, 1024x1024, deterministic.
"""
import math

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
PAPER = (247, 242, 230)
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
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

REGIONS = {
    "EUROPE": (31, 80, 140),
    "MIDDLE EAST": (200, 110, 20),
    "AMERICAS": (20, 120, 120),
    "ASIA-PACIFIC": (46, 125, 60),
    "AFRICA": (150, 110, 30),
    "WORLD": (90, 90, 90),
}
REGION_ORDER = ["EUROPE", "MIDDLE EAST", "AMERICAS", "ASIA-PACIFIC",
                "AFRICA", "WORLD"]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, s, f, max_w):
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(d, x, y, s, f, max_w, fill=INK, leading=3):
    lines = wrap(d, s, f, max_w)
    lh = f.size + leading
    for i, line in enumerate(lines):
        d.text((x, y + i * lh), line, font=f, fill=fill)
    return y + len(lines) * lh


def text_c(d, cx, y, s, f, fill=INK):
    w = d.textlength(s, font=f)
    d.text((cx - w / 2, y), s, font=f, fill=fill)


# ---------------------------------------------------------------- stories
# n, region, location, beat, headline, summary, source
LEADS = [
    (1, "EUROPE", "ANTALYA, T\u00dcRKIYE", "CLIMATE",
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

# n, region, location, beat, headline, summary, source, icon
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
     "\u2018El Chapo Isidro\u2019 caught; violence follows",
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

# n, region, location, one-line brief, source
BRIEFS = [
    (14, "AMERICAS", "US", "FBI looks into apparent hack of its crime database.", "BBC"),
    (15, "AMERICAS", "US", "Teen gamer and his mother help FBI rescue a girl.", "BBC"),
    (16, "AMERICAS", "US", "Midterm loss corners Vance as 2028 field widens.", "ST"),
    (17, "MIDDLE EAST", "Saudi Arabia", "Air defences down a missile.", "Investing.com"),
    (18, "MIDDLE EAST", "Lebanon", "Aoun demands Israeli withdrawal.", "Al Jazeera"),
    (19, "MIDDLE EAST", "Iran", "President warns of a \u2018silent economic war\u2019.", "Al Jazeera"),
    (20, "MIDDLE EAST", "Hormuz", "Lewis Pugh swims strait as tanker is struck.", "BBC"),
    (21, "EUROPE", "Moldova", "Reports a Russian airspace breach.", "Kyiv Ind."),
    (22, "EUROPE", "Belgium", "Air traffic to halt in 23 Nov national strike.", "ST"),
    (23, "EUROPE", "Germany", "IG Metall widens car and shipyard strikes.", "Reuters"),
    (24, "EUROPE", "Portugal", "Thousands march in Lisbon on living costs.", "Reuters"),
    (25, "EUROPE", "Denmark", "Expels Russian attach\u00e9 over rapper plot.", "Guardian"),
    (26, "ASIA-PACIFIC", "Bangladesh", "30 Awami League homes set on fire.", "TOI"),
    (27, "ASIA-PACIFIC", "Australia", "Fred Nile, ex-NSW MP, dies aged 92.", "ABC"),
    (28, "ASIA-PACIFIC", "Australia", "Bystanders pull driver from burning car.", "ABC"),
    (29, "ASIA-PACIFIC", "Melbourne", "70 years since the 1956 Olympics opened.", "ABC"),
    (30, "WORLD", "Trade", "EU and Indonesia sign deal after 10 years.", "DW"),
    (31, "WORLD", "Rugby", "England beat New Zealand 37-12.", "Reuters"),
    (32, "WORLD", "Rugby", "France beat Argentina to reach the final.", "Reuters"),
    (33, "WORLD", "Football", "Arsenal 2-1 Newcastle; Leeds 4-1 Chelsea.", "BBC"),
    (34, "WORLD", "Tennis", "Zverev v Alcaraz in today\u2019s ATP Finals final.", "TOI"),
    (35, "WORLD", "Football", "Liverpool host Manchester United today.", "Al Jazeera"),
]

ALL_STORIES = LEADS + [(n, r, l, b, h, s, src) for (n, r, l, b, h, s, src, _i) in FEATURES] + \
    [(n, r, l, "", txt, src) for (n, r, l, txt, src) in BRIEFS]
assert len(ALL_STORIES) == 35, len(ALL_STORIES)
REGION_COUNTS = {r: sum(1 for s in ALL_STORIES if s[1] == r) for r in REGION_ORDER}
assert sum(REGION_COUNTS.values()) == 35
assert REGION_COUNTS == {"EUROPE": 9, "MIDDLE EAST": 8, "AMERICAS": 6,
                         "ASIA-PACIFIC": 5, "AFRICA": 1, "WORLD": 6}, REGION_COUNTS

NUMBERS = [
    ("~200", "NATIONS AT COP31", "nearly 200 countries"),
    ("03:00", "GMT OBJECTION DEADLINE", "to object to the deal"),
    ("400+", "DRONES FIRED AT UKRAINE", "overnight barrage"),
    ("110", "MISSILES IN THE SAME NIGHT", "one of the war's largest"),
    ("7+", "PEOPLE KILLED IN KYIV", "at least seven dead"),
    ("2", "US BASES TARGETED", "in Bahrain by Iran"),
]

# lon/lat of the numbered pins on the map
PINS = {1: (30.7, 36.9), 2: (30.5, 50.4), 3: (50.6, 26.2),
        4: (24.0, 59.5), 5: (33.4, 47.9), 6: (6.3, 4.8),
        7: (35.2, 31.8), 8: (34.5, 31.5), 9: (-107.4, 24.8),
        10: (51.4, 35.7), 11: (-77.0, 38.9), 12: (-47.9, -15.8),
        13: (149.1, -35.3)}
# Manual pixel nudges so clustered pins (Kyiv/Antalya/Kryvyi Rih/Finland,
# Bahrain/Tehran, Jerusalem/Gaza) do not overlap on the squat map.
PIN_NUDGE = {4: (-30, -8), 2: (-24, 4), 5: (20, -10), 1: (-2, 22),
             7: (-28, 6), 8: (26, 14), 10: (-6, -16), 3: (18, -6)}


# ---------------------------------------------------------------- icons
def starburst(d, cx, cy, r, fill):
    pts = []
    for i in range(16):
        ang = math.pi * i / 8
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def draw_icon(d, kind, x, y, w, h, col):
    """Tiny flat pictogram inside box (x, y, w, h)."""
    cx, cy = x + w / 2, y + h / 2
    if kind == "ship":
        d.rectangle([x + 4, cy - 2, x + w - 4, cy + 5], fill=col)
        d.rectangle([x + 12, cy - 10, x + 22, cy - 2], fill=col)
        d.polygon([(cx + 2, cy - 10), (cx + 8, cy - 16), (cx + 12, cy - 10)],
                  fill=(230, 110, 20))
        d.line([x + 2, cy + 8, x + w - 2, cy + 8], fill=BLUE, width=2)
    elif kind == "burst":
        starburst(d, cx, cy, 11, (230, 140, 20))
        starburst(d, cx, cy, 6, (178, 34, 28))
    elif kind == "boat":
        d.polygon([(x + 6, cy - 2), (x + w - 6, cy - 2), (x + w - 12, cy + 6),
                   (x + 12, cy + 6)], fill=col)
        d.line([x + 2, cy + 9, x + w - 2, cy + 9], fill=BLUE, width=2)
        d.arc([x + 8, cy + 6, x + 20, cy + 14], 0, 180, fill=BLUE, width=2)
    elif kind == "talks":
        d.ellipse([x + 2, y + 2, x + 20, y + 14], fill=col)
        d.polygon([(x + 8, y + 13), (x + 6, y + 19), (x + 13, y + 13)],
                  fill=col)
        d.ellipse([x + 22, y + 6, x + 40, y + 18], fill=(200, 110, 20))
        d.polygon([(x + 34, y + 17), (x + 36, y + 20), (x + 29, y + 17)],
                  fill=(200, 110, 20))
    elif kind == "truck":
        d.rectangle([x + 2, y + 4, x + 24, y + 14], fill=col)
        d.rectangle([x + 25, y + 7, x + 36, y + 14], fill=col)
        d.ellipse([x + 7, y + 14, x + 13, y + 20], fill=INK)
        d.ellipse([x + 27, y + 14, x + 33, y + 20], fill=INK)
        d.text((x + 8, y + 6), "+", font=font(SANS_B, 8), fill=WHITE)
    elif kind == "badge":
        starburst(d, cx, cy, 10, GOLD)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=NAVY)
        d.text((cx - 2, cy - 6), "*", font=font(SANS_B, 9), fill=WHITE)
    elif kind == "bolt":
        d.polygon([(cx + 3, y + 1), (cx - 7, cy + 4), (cx - 1, cy + 4),
                   (cx - 4, y + h - 1), (cx + 7, cy - 2), (cx + 1, cy - 2)],
                  fill=(230, 170, 20))
    elif kind == "chart":
        d.line([x + 4, y + h - 3, x + w - 4, y + h - 3], fill=INK, width=2)
        d.line([x + 4, y + h - 3, x + 4, y + 3], fill=INK, width=2)
        for i, bh in enumerate((6, 10, 14)):
            d.rectangle([x + 9 + i * 9, y + h - 4 - bh, x + 15 + i * 9,
                         y + h - 4], fill=col)
    elif kind == "pulse":
        d.line([(x + 2, cy), (x + 10, cy), (x + 14, cy - 8), (x + 18, cy + 8),
                (x + 22, cy - 4), (x + 26, cy), (x + w - 2, cy)],
               fill=RED, width=2)
    elif kind == "sub":
        d.ellipse([x + 4, cy - 6, x + w - 4, cy + 6], fill=col)
        d.rectangle([cx - 4, cy - 11, cx + 4, cy - 4], fill=col)
        d.line([x + 2, cy + 9, x + w - 2, cy + 9], fill=BLUE, width=2)


def draw_lead_art(d, kind, x, y, w, h):
    """Flat vector illustration for a lead panel."""
    if kind == 1:  # COP31: globe + overtime clock
        d.rectangle([x, y, x + w, y + h], fill=(205, 228, 210))
        d.ellipse([x + 14, y + 8, x + 86, y + h - 8], fill=(70, 130, 190),
                  outline=NAVY, width=2)
        d.ellipse([x + 26, y + 16, x + 46, y + 34], fill=(90, 170, 90))
        d.ellipse([x + 52, y + 40, x + 76, y + 56], fill=(90, 170, 90))
        d.ellipse([x + 30, y + 46, x + 44, y + 58], fill=(90, 170, 90))
        d.arc([x + 50, y + 8, x + 86, y + h - 8], 300, 60, fill=WHITE,
              width=2)
        # clock: talks run overtime
        cx, cy, r = x + w - 52, y + h / 2, 24
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE,
                  outline=INK, width=2)
        d.line([cx, cy, cx, cy - 15], fill=INK, width=2)
        d.line([cx, cy, cx + 12, cy + 6], fill=INK, width=2)
        d.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=RED)
        d.text((cx - 26, cy + r + 2), "OVERTIME", font=font(SANS_B, 8),
               fill=RED)
    elif kind == 2:  # Kyiv barrage: night sky, drones, bursts, skyline
        d.rectangle([x, y, x + w, y + h], fill=(16, 28, 52))
        for sx, sy in [(x + 30, y + 8), (x + 90, y + 16), (x + 160, y + 6),
                       (x + 220, y + 14), (x + 260, y + 8), (x + 300, y + 18)]:
            d.ellipse([sx, sy, sx + 2, sy + 2], fill=WHITE)
        # drones with trails
        for mx, my in [(x + 70, y + 12), (x + 165, y + 20), (x + 255, y + 10)]:
            d.line([mx - 26, my + 16, mx, my], fill=(255, 220, 120), width=2)
            d.line([mx - 8, my - 3, mx + 8, my + 3], fill=WHITE, width=2)
            d.line([mx - 8, my + 3, mx + 8, my - 3], fill=WHITE, width=2)
        # explosions over the skyline
        for mx, my in [(x + 110, y + 34), (x + 210, y + 30)]:
            starburst(d, mx, my, 10, (255, 180, 40))
            starburst(d, mx, my, 5, (255, 255, 255))
        for bx, bh in [(x + 8, 16), (x + 40, 24), (x + 80, 14), (x + 120, 26),
                       (x + 160, 18), (x + 200, 24), (x + 240, 14),
                       (x + 280, 22)]:
            d.rectangle([bx, y + h - bh, bx + 34, y + h], fill=(8, 14, 28))
            d.rectangle([bx + 8, y + h - bh - 6, bx + 14, y + h - bh],
                        fill=(8, 14, 28))
    else:  # Bahrain: sea, burning industrial site, tanker
        d.rectangle([x, y, x + w, y + h], fill=(240, 200, 150))
        # sea
        d.rectangle([x, y + h - 16, x + w, y + h], fill=(40, 90, 140))
        # tanker
        d.rectangle([x + 14, y + h - 30, x + 110, y + h - 16], fill=INK)
        d.rectangle([x + 84, y + h - 42, x + 100, y + h - 30], fill=INK)
        d.rectangle([x + 20, y + h - 36, x + 30, y + h - 30], fill=INK)
        # industrial site: towers + flames + smoke
        for bx, bh in [(x + 150, 30), (x + 180, 38), (x + 210, 26),
                       (x + 240, 34)]:
            d.rectangle([bx, y + h - 16 - bh, bx + 22, y + h - 16],
                        fill=(90, 80, 70))
        for fx, fy in [(x + 158, y + h - 50), (x + 216, y + h - 44),
                       (x + 248, y + h - 52)]:
            d.polygon([(fx, fy), (fx + 6, fy - 12), (fx + 12, fy)],
                      fill=(230, 110, 20))
            d.polygon([(fx + 3, fy), (fx + 6, fy - 7), (fx + 9, fy)],
                      fill=(255, 200, 40))
        for sx, sy, sr in [(x + 170, y + 8, 7), (x + 195, y + 4, 9),
                           (x + 225, y + 10, 6)]:
            d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                      fill=(120, 115, 110))


# ---------------------------------------------------------------- map
def project(lon, lat, mx, my, mw, mh):
    x = mx + (lon + 170) / 360.0 * mw
    y = my + (75 - lat) / 130.0 * mh
    return x, y


CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-65, 60), (-55, 47), (-70, 42), (-75, 35), (-80, 26),
     (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40),
     (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    [(-55, 60), (-45, 60), (-40, 65), (-30, 68), (-20, 70), (-30, 74),
     (-50, 76), (-60, 74), (-58, 64)],
    [(-80, 9), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-44, -3),
     (-35, -8), (-40, -20), (-48, -28), (-58, -35), (-65, -41),
     (-70, -50), (-73, -53), (-70, -40), (-72, -25), (-77, -12),
     (-81, -5), (-80, 2)],
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
     (25, 65), (20, 70), (15, 70), (10, 64), (5, 58), (-2, 55),
     (-5, 50), (-10, 43), (-10, 37)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-1, 51)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (51, 11), (48, 2), (40, -10), (35, -18),
     (32, -26), (26, -34), (19, -35), (15, -27), (12, -18), (9, -1),
     (9, 4), (-8, 5), (-15, 12)],
    [(28, 62), (35, 68), (50, 70), (70, 72), (90, 75), (110, 76),
     (130, 72), (150, 70), (170, 66), (178, 65), (170, 60), (162, 55),
     (158, 50), (150, 45), (142, 42), (140, 38), (135, 35), (130, 33),
     (127, 35), (122, 38), (120, 32), (115, 28), (110, 20), (108, 12),
     (105, 8), (100, 6), (97, 10), (92, 15), (88, 22), (85, 20),
     (80, 15), (77, 8), (74, 20), (70, 23), (66, 25), (62, 25),
     (58, 26), (55, 26), (52, 28), (50, 30), (48, 30), (44, 29),
     (40, 31), (36, 36), (32, 36), (28, 38), (26, 40), (24, 45),
     (22, 50), (24, 55), (26, 60)],
    [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (143, 44),
     (141, 45), (139, 40), (136, 36), (132, 33)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
     (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
     (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20)],
]


# ---------------------------------------------------------------- render
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead strip
    d.rectangle([0, 0, W, 24], fill=NAVY)
    d.text((10, 4), "THE WORLD IN ONE DAY", font=font(SANS_B, 15),
           fill=WHITE)
    right = "35 STORIES \u00b7 6 REGIONS \u00b7 EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    w = d.textlength(right, font=font(SANS_B, 10))
    d.text((W - 10 - w, 6), right, font=font(SANS_B, 10), fill=WHITE)

    # Giant date
    text_c(d, W // 2, 28, "Sunday 22 November 2026",
           font(SERIF_B, 34), fill=NAVY)
    d.line([10, 64, W - 10, 64], fill=RED, width=2)

    # Ticker
    text_c(d, W // 2, 68,
           "COP31 deal close  \u00b7  Russia's 400-drone barrage  "
           "\u00b7  Iran hits US bases in Bahrain",
           font(SANS_B, 11), fill=RED)

    # Numbers strip
    y0, y1 = 86, 128
    bw = (W - 20 - 5 * 6) / 6
    for i, (num, cap, sub) in enumerate(NUMBERS):
        x = 10 + i * (bw + 6)
        d.rectangle([x, y0, x + bw, y1], fill=WHITE, outline=GREY, width=1)
        text_c(d, x + bw / 2, y0 + 2, num, font(SERIF_B, 19), fill=NAVY)
        text_c(d, x + bw / 2, y0 + 24, cap, font(SANS_B, 8), fill=INK)
        if sub:
            text_c(d, x + bw / 2, y0 + 34, sub, font(SANS, 7),
                   fill=GREY)

    # Region bar
    y0, y1 = 132, 148
    d.text((10, y0 + 3), "STORIES BY REGION:",
           font=font(SANS_B, 10), fill=INK)
    total_w = W - 10 - 170
    x = 180
    for r in REGION_ORDER:
        n = REGION_COUNTS[r]
        seg = total_w * n / 35.0
        d.rectangle([x, y0, x + seg - 1, y1], fill=REGIONS[r])
        label = f"{r} {n}"
        lw = d.textlength(label, font=font(SANS_B, 7))
        if seg > lw + 4:
            d.text((x + (seg - lw) / 2, y0 + 5), label,
                   font=font(SANS_B, 7), fill=WHITE)
        else:
            # Segment too narrow for its label: leader line down to a
            # label below the bar, in the segment colour.
            cx = x + seg / 2
            d.line([cx, y1, cx, y1 + 3], fill=REGIONS[r], width=1)
            d.text((cx - lw / 2, y1 + 3), label,
                   font=font(SANS_B, 7), fill=REGIONS[r])
        x += seg

    # Lead panels
    ly0, ly1 = 160, 316
    lw = (W - 20 - 2 * 8) / 3
    for i, (n, region, loc, beat, head, summ, src) in enumerate(LEADS):
        x = 10 + i * (lw + 8)
        col = REGIONS[region]
        d.rectangle([x, ly0, x + lw, ly1], fill=WHITE, outline=GREY, width=1)
        d.rectangle([x, ly0, x + lw, ly0 + 18], fill=col)
        d.text((x + 6, ly0 + 3),
               f"{n} \u00b7 {loc} \u2014 {beat}",
               font=font(SANS_B, 9), fill=WHITE)
        draw_lead_art(d, n, x + 1, ly0 + 19, lw - 2, 56)
        hy = para(d, x + 8, ly0 + 82, head, font(SERIF_B, 15), lw - 16,
                  fill=NAVY, leading=1)
        para(d, x + 8, hy + 3, summ, font(SANS, 10), lw - 16, leading=2)
        d.text((x + 8, ly1 - 14), f"Source: {src}",
               font=font(SANS, 8), fill=GREY)

    # Feature panels: 5 x 2
    fy0 = 322
    fh, fw, gap = 86, (W - 20 - 4 * 6) / 5, 6
    for i, (n, region, loc, beat, head, summ, src, icon) in enumerate(FEATURES):
        col_i, row_i = i % 5, i // 5
        x = 10 + col_i * (fw + gap)
        y = fy0 + row_i * (fh + gap)
        col = REGIONS[region]
        d.rectangle([x, y, x + fw, y + fh], fill=WHITE, outline=GREY,
                    width=1)
        d.rectangle([x, y, x + fw, y + 15], fill=col)
        d.text((x + 5, y + 2), f"{n} \u00b7 {loc} \u2014 {beat}",
               font=font(SANS_B, 8), fill=WHITE)
        draw_icon(d, icon, x + 5, y + 17, 42, 20, col)
        d.text((x + 50, y + 19), beat, font=font(SANS_B, 8), fill=GREY)
        hy = para(d, x + 5, y + 39, head, font(SERIF_B, 11), fw - 10,
                  fill=NAVY, leading=0)
        para(d, x + 5, hy + 1, summ, font(SANS, 8), fw - 10, leading=1)
        d.text((x + 5, y + fh - 11), f"Source: {src}",
               font=font(SANS, 7), fill=GREY)

    # World map
    my0, my1 = 506, 610
    d.text((10, my0), "WHERE IT HAPPENED",
           font=font(SANS_B, 12), fill=NAVY)
    map_note = "Schematic map \u2014 pins match stories 1\u201313"
    d.text((W - 10 - d.textlength(map_note, font=font(SANS, 9)), my0 + 1),
           map_note, font=font(SANS, 9), fill=GREY)
    mx, my, mw, mh = 10, my0 + 18, W - 20, my1 - my0 - 18
    d.rectangle([mx, my, mx + mw, my + mh], fill=SKY, outline=GREY, width=1)
    for poly in CONTINENTS:
        pts = [project(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=(150, 130, 95))
    for n, (lon, lat) in sorted(PINS.items()):
        px, py = project(lon, lat, mx, my, mw, mh)
        dx, dy = PIN_NUDGE.get(n, (0, 0))
        if (dx, dy) != (0, 0):
            d.line([px, py, px + dx, py + dy], fill=RED, width=1)
            px, py = px + dx, py + dy
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED,
                  outline=WHITE, width=1)
        tw = d.textlength(str(n), font=font(SANS_B, 9))
        d.text((px - tw / 2, py - 7), str(n), font=font(SANS_B, 9),
               fill=WHITE)

    # ALSO ON list
    ay0 = 616
    d.text((10, ay0), "ALSO ON SUNDAY 22 NOVEMBER 2026 \u2014 22 MORE STORIES",
           font=font(SANS_B, 12), fill=NAVY)
    d.line([10, ay0 + 17, W - 10, ay0 + 17], fill=RED, width=2)
    f_txt = font(SANS, 10)
    col_w = (W - 20 - 16) / 2
    for i, (n, region, loc, txt, src) in enumerate(BRIEFS):
        col_i, row_i = i // 11, i % 11
        x = 10 + col_i * (col_w + 16)
        y = ay0 + 22 + row_i * 18
        col = REGIONS[region]
        d.rectangle([x, y + 1, x + 4, y + 13], fill=col)
        line = f"{n}. {loc}: {txt} ({src})"
        # One line each: shrink the font, then shorten, until it fits.
        f = f_txt
        while d.textlength(line, font=f) > col_w - 10 and f.size > 8:
            f = font(SANS, f.size - 1)
        while d.textlength(line, font=f) > col_w - 10:
            line = line[: -5].rstrip() + "\u2026"
        d.text((x + 8, y), line, font=f, fill=INK)

    # DATE CHECK box
    dy0, dy1 = 842, 960
    d.rectangle([10, dy0, W - 10, dy1], fill=(255, 240, 238),
                outline=RED, width=2)
    d.text((20, dy0 + 5), "DATE CHECK", font=font(SANS_B, 12), fill=RED)
    check = ("Every story on this page happened, or was first reported, on "
             "Sunday 22 November 2026 \u2014 wires read up to 05:00 UTC. "
             "LEFT OUT because it was other days' news: the Peru earthquake "
             "(20 Nov local); Russian missiles landing in Poland (19 Nov); "
             "the Kerch Bridge strikes (earlier this week); the Shenzhen "
             "summit (19 Nov); the Anthropic IPO debut (Thu 19 Nov); the "
             "GTA VI launch (Thu 19 Nov); Wall Street's correction "
             "(Fri 20 Nov).")
    para(d, 20, dy0 + 23, check, font(SANS, 10), W - 40, leading=2)

    # Sources footer
    fy = 966
    text_c(d, W // 2, fy,
           "Sources: Reuters, BBC, Al Jazeera, DW, The Straits Times, "
           "Sky News, CNA, ABC Australia, Times of India, The Guardian, "
           "Kyiv Independent.",
           font(SANS, 9), fill=GREY)
    text_c(d, W // 2, fy + 13,
           "Every story names its outlet. Pictures and map: original, "
           "drawn in code.",
           font(SANS, 8), fill=GREY)

    img.save("entry.png", optimize=True)
    print("saved entry.png", img.size)


if __name__ == "__main__":
    render()
