"""Folge 3: Warum ist das Meer salzig, aber Flüsse nicht?  (9:16)

Rendern:   python3 videos/03_meer.py            (ElevenLabs, Stimme Brian)
Vorschau:  python3 videos/03_meer.py --stills
"""
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image  # noqa: E402

from ev.engine import (S, Pen, Video, canvas, caption, cli, ease_in_out, ease_out,  # noqa: E402
                       ease_out_back, glow, layer, lerp, place, prog, text_sprite)

BG = ((0, "#041a30"), (0.6, "#0a3a5c"), (1, "#0c4a6e"))
SEA = "#1e88c7"
SEA_DEEP = "#0d5f94"
RIVER = "#5fc4ff"
LAND = "#2f6b3f"
LAND_DARK = "#24543a"
ROCK = "#6b5a4e"
ROCK_DARK = "#54463c"
SALT = "#ffffff"
ORANGE = "#FF9F43"
TEAL = "#4ECDC4"

rng = random.Random(11)


def pill(cv, text, cx, cy, color, alpha=1.0, scale=1.0, size=42, fg="#06243c"):
    spr = text_sprite(text, size, weight="bold", stroke=0, color=fg, max_w=900)
    w, h = spr.width / S + 52, spr.height / S + 24
    img = Image.new("RGBA", (int(w * S) + 4, int(h * S) + 4), (0, 0, 0, 0))
    Pen(img).rrect((0, 0, w, h), h / 2, color)
    place(img, spr, w / 2, h / 2)
    place(cv, img, cx, cy, scale, alpha)


def crystal(p, x, y, r=11, color=SALT):
    p.poly([(x, y - r), (x + r * 0.8, y), (x, y + r), (x - r * 0.8, y)], color)


# ------------------------------------------------------------ Landschaft
def bezier(p0, p1, p2, p3, n=80):
    out = []
    for i in range(n + 1):
        u = i / n
        a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        out.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return out


RIVER_PTS = bezier((110, 800), (420, 880), (280, 1160), (640, 1320))
SEA_Y = 1300
SEA_SALT = [(rng.uniform(60, 1020), rng.uniform(1360, 1640)) for _ in range(160)]


def sea(p, t, y0=SEA_Y):
    pts = [(x, y0 + 12 * math.sin(x / 90 + t * 2)) for x in range(0, 1101, 20)]
    p.poly(pts + [(1080, 1920), (0, 1920)], SEA)
    pts2 = [(x, y0 + 60 + 10 * math.sin(x / 70 - t * 1.6)) for x in range(0, 1101, 20)]
    p.poly(pts2 + [(1080, 1920), (0, 1920)], SEA_DEEP)


def landscape(cv, t, river_reveal=1.0):
    p = Pen(cv)
    p.poly([(0, 820), (180, 760), (420, 800), (640, 930), (780, 1150), (820, SEA_Y + 20),
            (0, SEA_Y + 20)], LAND)
    p.poly([(0, 1000), (200, 980), (420, 1100), (560, SEA_Y + 20), (0, SEA_Y + 20)], LAND_DARK)
    n = max(2, int(len(RIVER_PTS) * river_reveal))
    if river_reveal > 0:
        p.line(RIVER_PTS[:n], RIVER, 26)
    sea(p, t)
    return p


def along(u):
    """Punkt auf dem Fluss, u in [0, 1]."""
    i = min(len(RIVER_PTS) - 2, int(u * (len(RIVER_PTS) - 1)))
    f = u * (len(RIVER_PTS) - 1) - i
    (x0, y0), (x1, y1) = RIVER_PTS[i], RIVER_PTS[i + 1]
    return lerp(x0, x1, f), lerp(y0, y1, f)


def salt_shaker(p, x, y, s=1.0):
    p.rrect((x - 40 * s, y - 50 * s, x + 40 * s, y + 70 * s), 18 * s, "#ffffff")
    p.rrect((x - 36 * s, y - 85 * s, x + 36 * s, y - 45 * s), 14 * s, "#b9c7d6")
    for dx in (-14, 0, 14):
        p.circle(x + dx * s, y - 68 * s, 4 * s, "#5b6b7c")


# ------------------------------------------------------------ 1 Einstieg
def s1_einstieg(t):
    cv = canvas(BG)
    p = landscape(cv, t, ease_out(prog(t, 0.2, 1.6)))
    if t > 1.0:
        pill(cv, "Süßwasser", 250, 1060, RIVER, scale=ease_out_back(prog(t, 1.0, 1.35)))
    if t > 2.5:
        k = ease_out_back(prog(t, 2.5, 2.9))
        salt_shaker(p, 830, 1100 - 30 * math.sin(t * 3) * k, k)
        pill(cv, "Salzig?!", 820, 1460, "#ffffff", scale=k)
    caption(cv, t, 0.1, 2.3, "Jeder Fluss fließt ins *Meer*", 500, size=92)
    caption(cv, t, 2.3, 9, "Warum ist dann nur das Meer *salzig*?", 500, size=88)
    return cv


# ------------------------------------------------------------ 2 Regen
ROCK_POLY = [(150, 1480), (230, 1270), (380, 1180), (560, 1160), (730, 1210), (880, 1300),
             (950, 1480)]
DROPS = [(rng.uniform(190, 900), rng.uniform(0, 1)) for _ in range(46)]
CRYSTALS = [(rng.uniform(260, 840), rng.uniform(1230, 1400)) for _ in range(16)]


def cloud(p, cx, cy, s=1.0, col="#9fb2c4"):
    for dx, dy, r in ((-110, 20, 70), (-30, -25, 95), (70, -5, 85), (150, 25, 60), (20, 35, 75)):
        p.circle(cx + dx * s, cy + dy * s, r * s, col)


def s2_regen(t):
    cv = canvas(BG)
    p = Pen(cv)
    for x, ph in DROPS:
        y = 860 + ((t * 950 + ph * 420) % 420)
        p.line([(x, y), (x - 6, y + 34)], "#8fd3ff", 6)
    cloud(p, 540, 800)
    p.poly(ROCK_POLY, ROCK)
    p.poly([(560, 1160), (730, 1210), (880, 1300), (950, 1480), (620, 1480)], ROCK_DARK)
    for i, (x, y) in enumerate(CRYSTALS):
        t0 = 2.2 + i * 0.18
        k = ease_out_back(prog(t, t0, t0 + 0.3))
        if k <= 0:
            continue
        drift = max(0, t - t0 - 0.4) * 22
        if t > 5.6:
            place(cv, glow(40, "#ffffff", 0.6), x, y + drift)
        crystal(p, x, y + drift, 11 * k)
    if t > 5.7:
        pill(cv, "Salz", 760, 1560, "#ffffff", scale=ease_out_back(prog(t, 5.7, 6.0)), size=50)
    caption(cv, t, 0.2, 1.8, "Alles beginnt mit *Regen*", 500, size=92)
    caption(cv, t, 1.8, 5.6, "Regen löst *Mineralien* aus dem Gestein", 500, size=86)
    caption(cv, t, 5.6, 9, "Darunter: *Salz*!", 500, size=100)
    return cv


# ------------------------------------------------------------ 3 Fluss
PARTICLES = [(0.3 + i * 0.32, SEA_SALT[i]) for i in range(30)]


def river_salt(p, t, start=0.0, every=0.32, count=30, travel=2.2, base=0):
    """Salzkörnchen wandern den Fluss hinunter und bleiben im Meer liegen."""
    for i in range(count):
        t0 = start + i * every
        if t < t0:
            continue
        u = (t - t0) / travel
        if u < 1:
            x, y = along(u)
            p.circle(x, y, 7, SALT)
        else:
            sx, sy = SEA_SALT[(base + i) % len(SEA_SALT)]
            k = prog(t, t0 + travel, t0 + travel + 0.6)
            mx, my = RIVER_PTS[-1]
            p.circle(lerp(mx, sx, ease_out(k)), lerp(my, sy, ease_out(k)), 7, SALT)


def s3_fluss(t):
    cv = canvas(BG)
    p = landscape(cv, t)
    river_salt(p, t, 0.3)
    if t > 2.6:
        pill(cv, "Fluss: kaum Salz", 300, 1080, RIVER, scale=ease_out_back(prog(t, 2.6, 2.95)))
    if t > 5.9:
        pill(cv, "Meer: Salz sammelt sich", 640, 1720, "#ffffff",
             scale=ease_out_back(prog(t, 5.9, 6.25)))
    caption(cv, t, 0.2, 2.4, "Flüsse spülen das Salz ins *Meer*", 500, size=88)
    caption(cv, t, 2.4, 5.6, "Im Fluss: *viel zu wenig* zum Schmecken", 500, size=84)
    caption(cv, t, 5.6, 11, "Neuer Regen spült nach – im Fluss *sammelt sich nichts*", 500, size=80)
    return cv


# ------------------------------------------------------------ 4 Verdunstung
VAPOR = [(rng.uniform(560, 1000), rng.uniform(0, 1)) for _ in range(26)]


def s4_verdunstung(t):
    cv = canvas(BG)
    place(cv, glow(260, "#FFE08A", 0.8), 900, 720)
    Pen(cv).circle(900, 720, 80, "#FFE08A")
    p = landscape(cv, t)
    # Salz im Meer: wird immer mehr
    n = min(len(SEA_SALT), 30 + int(t * 12))
    for x, y in SEA_SALT[:n]:
        p.circle(x, y, 7, SALT)
    # Wasserdampf steigt auf (ohne Salz)
    va = prog(t, 1.6, 2.2)
    if va > 0:
        for x, ph in VAPOR:
            k = (t * 0.45 + ph) % 1.0
            y = lerp(SEA_Y - 10, 820, k)
            xx = lerp(x, 420 + (x - 560) * 0.4, k)
            p.circle(xx, y, 9 * (1 - 0.4 * k), "#bfe6ff")
        pill(cv, "nur Wasser", 820, 1060, "#bfe6ff", scale=ease_out_back(prog(t, 2.0, 2.35)))
    # Wolke + Regen zurück aufs Land
    ck = ease_out(prog(t, 2.6, 3.6))
    if ck > 0:
        cloud(p, 380, 780, 0.6 + 0.4 * ck, "#c9d6e2")
    if t > 5.0:
        for x, ph in DROPS[:20]:
            xx = 160 + (x - 190) * 0.45
            y = 860 + ((t * 900 + ph * 260) % 260)
            p.line([(xx, y), (xx - 5, y + 28)], "#8fd3ff", 5)
        river_salt(p, t, 5.3, every=0.3, count=14, travel=1.8, base=60)
    caption(cv, t, 0.2, 1.6, "Im Meer passiert der *Trick*:", 500, size=92)
    caption(cv, t, 1.6, 5.0, "Wasser verdunstet – das *Salz bleibt*", 500, size=88)
    caption(cv, t, 5.0, 12, "Regen holt *neues Salz* – immer wieder", 500, size=86)
    return cv


# ------------------------------------------------------------ 5 Millionen Jahre
BUBBLES = [(rng.uniform(-40, 40), rng.uniform(0, 1), rng.uniform(5, 12)) for _ in range(20)]


def fmt(n):
    return f"{n:,}".replace(",", ".")


def s5_jahre(t):
    cv = canvas(((0, "#062a44"), (0.55, "#0a3a5c"), (1, "#04121f")))
    p = Pen(cv)
    k = ease_in_out(prog(t, 0.3, 2.6))
    years = int(10 ** lerp(2, math.log10(500_000_000), k)) if k > 0 else 0
    if years > 1000:  # runde Zahlen, kein 499.999.999
        mag = 10 ** (len(str(years)) - 2)
        years = round(years / mag) * mag
    place(cv, text_sprite(f"*{fmt(years)}*", 120, hl="#ffffff"), 540, 860)
    place(cv, text_sprite("Jahre", 60, weight="bold", stroke=0, color="#9fd0ff"), 540, 980)
    # Meeresboden mit Vulkan
    p.poly([(0, 1500), (300, 1470), (420, 1330), (480, 1300), (600, 1300), (660, 1330),
            (780, 1470), (1080, 1500), (1080, 1920), (0, 1920)], "#2b2430")
    v = prog(t, 3.0, 3.4)
    if v > 0:
        place(cv, glow(150, ORANGE, 0.9 * v), 540, 1300)
        p.ellipse((490, 1288, 590, 1312), "#ff7b3d")
        for dx, ph, r in BUBBLES:
            kk = (t * 0.5 + ph) % 1.0
            p.circle(540 + dx + 25 * math.sin(kk * 9 + ph * 6), lerp(1280, 1060, kk), r * v,
                     None, "#bfe6ff", 3)
        pill(cv, "Mineralien", 820, 1180, ORANGE, scale=ease_out_back(prog(t, 3.3, 3.65)))
    caption(cv, t, 0.2, 3.0, "Seit *Hunderten Millionen* Jahren", 500, size=90)
    caption(cv, t, 3.0, 9, "Plus Mineralien aus *Unterwasser-Vulkanen*", 500, size=84)
    return cv


# ------------------------------------------------------------ 6 Wow
def spoon(p, x, y, s=1.0):
    p.line([(x + 60 * s, y), (x + 190 * s, y - 40 * s)], "#c7ced6", 16 * s)
    p.ellipse((x - 70 * s, y - 38 * s, x + 70 * s, y + 38 * s), "#c7ced6")
    p.ellipse((x - 55 * s, y - 40 * s, x + 55 * s, y + 6 * s), SALT)


def s6_wow(t):
    cv = canvas(BG)
    p = Pen(cv)
    a = 1 - prog(t, 5.0, 5.4)
    if a > 0:
        k = ease_out_back(prog(t, 0.3, 0.7))
        # Flasche
        lay, lp = layer()
        bx, by = 330, 1180
        lp.rrect((bx - 95, by - 190, bx + 95, by + 210), 40, "#ffffff22", "#ffffffcc", 5)
        lp.rrect((bx - 40, by - 250, bx + 40, by - 190), 14, "#ffffffcc")
        lp.rrect((bx - 88, by - 100, bx + 88, by + 203), 34, SEA)
        if a < 1:
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
        if k > 0:
            cv.alpha_composite(lay)
        place(cv, text_sprite("1 Liter", 46, weight="bold", stroke=0), bx, by + 70, alpha=a * k)
        for i in range(2):
            kk = ease_out_back(prog(t, 1.6 + i * 0.4, 2.0 + i * 0.4))
            if kk > 0 and a > 0.5:
                spoon(p, 700, 1060 + i * 190, kk)
        if t > 3.0:
            place(cv, text_sprite("*35 g* Salz", 96, hl=ORANGE), 760, 1480,
                  ease_out_back(prog(t, 3.0, 3.35)), a)
    else:
        # Salzschicht auf dem Kontinent
        g = ease_in_out(prog(t, 5.8, 8.2))
        ground = 1480
        p.d.rectangle([0, ground * S, 1080 * S, 1920 * S], fill=(43, 36, 48, 255))
        bx0, bx1, bh = 700, 830, 300
        p.d.rectangle([bx0 * S, (ground - bh) * S, bx1 * S, ground * S], fill=(60, 72, 90, 255))
        for r in range(9):
            for c in range(3):
                p.d.rectangle([(bx0 + 18 + c * 38) * S, (ground - bh + 18 + r * 31) * S,
                               (bx0 + 40 + c * 38) * S, (ground - bh + 36 + r * 31) * S],
                              fill=(255, 214, 120, 255))
        place(cv, text_sprite("Hochhaus, 100 m", 38, weight="bold", stroke=0, color="#cfd8e3"),
              765, ground - bh - 40, alpha=1 - g)
        h = 430 * g
        if h > 1:
            lay, lp = layer()
            lp.d.rectangle([40 * S, (ground - h) * S, 1040 * S, ground * S], fill=(245, 248, 252, 195))
            cv.alpha_composite(lay)
            for x, y in SEA_SALT[:50]:
                yy = ground - (y - 1360) / 280 * h
                crystal(p, x, yy, 7, "#dfe8f2")
        if g > 0.9:
            place(cv, text_sprite("*über 100 m* Salz", 70, hl=ORANGE), 540, ground - h - 70,
                  ease_out_back(prog(t, 8.0, 8.4)))
    caption(cv, t, 0.2, 5.2, "In *1 Liter* Meerwasser: rund *35 g* Salz", 500, size=84)
    caption(cv, t, 5.2, 13, "Alles Salz auf die Kontinente: *über 100 m* hoch!", 500, size=84)
    return cv


# ------------------------------------------------------------ 7 Ende
def s7_ende(t):
    cv = canvas(BG)
    caption(cv, t, 0.1, 9, "Hättest du's *gewusst*?", 760, size=110)
    caption(cv, t, 1.6, 9, "Folge für mehr *Warum eigentlich?*", 1010, size=66)
    return cv


VIDEO = Video([
    (6.5, s1_einstieg, [(0.1, "Jeder Fluss der Welt fließt ins Meer."),
                        (2.3, "Flusswasser ist nicht salzig – warum ist es dann das Meer?")]),
    (7.5, s2_regen, [(0.2, "Alles beginnt mit Regen."),
                     (1.8, "Regenwasser ist ganz leicht sauer – und löst winzige Mengen Mineralien aus dem Gestein."),
                     (5.6, "Darunter: Salz.")]),
    (9.0, s3_fluss, [(0.2, "Flüsse spülen dieses Salz ins Meer."),
                     (2.4, "Aber es ist so wenig, dass du es im Flusswasser nicht schmeckst."),
                     (5.6, "Und weil ständig neuer Regen nachfließt, sammelt sich dort nichts an.")]),
    (10.0, s4_verdunstung, [(0.2, "Im Meer passiert dann der Trick:"),
                            (1.6, "Die Sonne lässt Wasser verdunsten – aber das Salz bleibt zurück."),
                            (5.0, "Das Wasser regnet wieder ab, holt neues Salz – und alles beginnt von vorn.")]),
    (6.5, s5_jahre, [(0.2, "Und das seit Hunderten Millionen Jahren."),
                     (3.0, "Dazu kommen noch Mineralien aus Vulkanen am Meeresboden.")]),
    (11.0, s6_wow, [(0.2, "Heute stecken in jedem Liter Meerwasser rund 35 Gramm Salz – etwa zwei Esslöffel."),
                    (5.2, "Würde man alles Salz aus den Ozeanen auf die Kontinente verteilen, läge es über hundert Meter hoch.")]),
    (4.2, s7_ende, [(0.2, "Hättest du es gewusst?"),
                    (1.7, "Folge für mehr: Warum eigentlich?")]),
])

if __name__ == "__main__":
    cli(VIDEO, __file__, cover_t=3.5)
