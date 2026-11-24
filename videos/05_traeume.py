"""Folge 5: Warum vergessen wir unsere Träume?  (9:16)

Rendern:   python3 videos/05_traeume.py            (ElevenLabs, Stimme Brian)
Vorschau:  python3 videos/05_traeume.py --stills

Neu ab dieser Folge – starker Einstieg ("Hook"):
- ab dem allerersten Bild Bewegung + großer Untertitel (kein leerer Start)
- kurzer Zoom-Effekt in den ersten 0,7 s
- Titelbild = Anfangsbild
"""
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image  # noqa: E402

from ev.engine import (S, Pen, Video, canvas, caption, cli, ease_in_out, ease_out,  # noqa: E402
                       ease_out_back, glow, layer, lerp, mix, place, prog, text_sprite)

BG = ((0, "#06142e"), (0.5, "#141a4d"), (1, "#2b1650"))
TURQ = "#4fe3d0"
LILAC = "#c39bff"
PINK = "#ff8fc7"
GOLD = "#FFD23F"
SKIN = "#f6c9a8"
HAIR = "#3b2468"
BRAIN = "#f2a7c9"
BRAIN_DARK = "#c97aa3"
BUBBLE = "#232a66"
BUBBLE_LINE = "#9fb4ff"
INK = "#140b2e"

rng = random.Random(5)
STARS = [(rng.uniform(0, 1080), rng.uniform(0, 1900), rng.uniform(1.5, 3.5), rng.uniform(0, 6.3))
         for _ in range(70)]


def night(t):
    cv = canvas(BG)
    p = Pen(cv)
    for x, y, r, ph in STARS:
        k = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 2 + ph))
        p.circle(x, y, r, mix("#141a4d", "#ffffff", k))
    return cv


def pill(cv, text, cx, cy, color, alpha=1.0, scale=1.0, size=42, fg=INK):
    spr = text_sprite(text, size, weight="bold", stroke=0, color=fg, max_w=900)
    w, h = spr.width / S + 52, spr.height / S + 24
    img = Image.new("RGBA", (int(w * S) + 4, int(h * S) + 4), (0, 0, 0, 0))
    Pen(img).rrect((0, 0, w, h), h / 2, color)
    place(img, spr, w / 2, h / 2)
    place(cv, img, cx, cy, scale, alpha)


def faded(cv, alpha, draw):
    """Etwas halbtransparent zeichnen: draw(pen) auf eigener Ebene."""
    if alpha <= 0.01:
        return
    lay, lp = layer()
    draw(lp)
    if alpha < 0.999:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * alpha)))
    cv.alpha_composite(lay)


def punch(cv, t, dur=0.7, z0=1.14):
    """Kurzer Zoom am Anfang (Hook)."""
    z = lerp(z0, 1.0, ease_out(prog(t, 0, dur)))
    if z <= 1.001:
        return cv
    w, h = cv.size
    cw, ch = int(w / z), int(h / z)
    x0, y0 = (w - cw) // 2, int((h - ch) * 0.55)
    return cv.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.BILINEAR)


# ------------------------------------------------------------ Traum-Symbole
def icon(p, kind, x, y, s=1.0):
    if kind == "star":
        pts = []
        for i in range(10):
            r = (46 if i % 2 == 0 else 20) * s
            a = -math.pi / 2 + i * math.pi / 5
            pts.append((x + r * math.cos(a), y + r * math.sin(a)))
        p.poly(pts, GOLD)
    elif kind == "moon":
        p.circle(x, y, 40 * s, "#fff1b8")
        p.circle(x + 20 * s, y - 12 * s, 34 * s, BUBBLE)
    elif kind == "fish":
        p.poly([(x - 30 * s, y), (x - 62 * s, y - 26 * s), (x - 62 * s, y + 26 * s)], TURQ)
        p.ellipse((x - 42 * s, y - 26 * s, x + 44 * s, y + 26 * s), TURQ)
        p.circle(x + 22 * s, y - 6 * s, 6 * s, INK)
    elif kind == "heart":
        p.circle(x - 19 * s, y - 10 * s, 23 * s, PINK)
        p.circle(x + 19 * s, y - 10 * s, 23 * s, PINK)
        p.poly([(x - 41 * s, y - 2 * s), (x + 41 * s, y - 2 * s), (x, y + 42 * s)], PINK)
    elif kind == "house":
        p.rrect((x - 32 * s, y - 8 * s, x + 32 * s, y + 40 * s), 4 * s, LILAC)
        p.poly([(x - 44 * s, y - 4 * s), (x, y - 44 * s), (x + 44 * s, y - 4 * s)], "#ff9f6b")
        p.rrect((x - 10 * s, y + 12 * s, x + 10 * s, y + 40 * s), 3 * s, INK)


def bubble(p, kind, x, y, r=78):
    p.circle(x, y, r, BUBBLE, BUBBLE_LINE, 5)
    icon(p, kind, x, y, r / 78)


KINDS = ["star", "fish", "moon", "heart", "house"]
DUST = [[(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(4, 9)) for _ in range(14)]
        for _ in range(5)]
BUB_POS = [(230, 1080, 80), (520, 940, 92), (820, 1060, 80), (330, 800, 70), (740, 800, 72)]


def dreams(cv, t, dissolve=0.0, appear=1.0, y_shift=0.0):
    """Schwebende Traumblasen; dissolve 0..1 = zerfallen zu Staub."""
    p = Pen(cv)
    for i, ((bx, by, r), kind) in enumerate(zip(BUB_POS, KINDS)):
        a = prog(appear, i * 0.12, i * 0.12 + 0.4)
        if a <= 0:
            continue
        x = bx + 14 * math.sin(t * 1.3 + i)
        y = by + y_shift + 18 * math.sin(t * 1.7 + i * 2)
        d = prog(dissolve, i * 0.08, i * 0.08 + 0.55)
        if d < 1:
            faded(cv, (1 - d) * a, lambda lp, x=x, y=y, r=r, kind=kind:
                  bubble(lp, kind, x, y, r * (0.7 + 0.3 * ease_out_back(a))))
        if d > 0:
            for dx, dy, rr in DUST[i]:
                k = ease_out(d)
                col = mix("#141a4d", BUBBLE_LINE, 1 - d)
                p.circle(x + dx * r * (1 + 2.2 * k), y + dy * r * (1 + 2.2 * k) - 120 * k,
                         rr * (1 - 0.6 * d), col)


def sleeper(p, t, x=440, y=1430, eyes_open=0.0):
    """Liegender Kopf auf Kissen mit Decke."""
    p.rrect((x - 230, y - 20, x + 90, y + 120), 60, "#b7a6ff")          # Kissen
    p.rrect((x + 40, y - 30, 1100, y + 170), 80, "#6c4fd6")             # Decke
    p.rrect((x + 40, y - 30, x + 140, y + 170), 50, "#8a72e8")
    p.circle(x - 40, y - 10, 120, SKIN)                                  # Kopf
    p.d.pieslice([(x - 170) * S, (y - 140) * S, (x + 90) * S, (y + 120) * S], 150, 330,
                 fill=(59, 36, 104, 255))                                # Haare
    p.circle(x - 40, y - 10, 104, SKIN)
    p.circle(x + 72, y + 6, 18, SKIN)                                    # Nase
    ex, ey = x + 20, y - 30
    if eyes_open > 0.5:
        p.circle(ex, ey, 13, "#ffffff")
        p.circle(ex + 3, ey, 7, INK)
    else:
        p.line([(ex - 22, ey), (ex - 8, ey + 8), (ex + 8, ey + 8), (ex + 22, ey)], INK, 6)
    p.line([(x + 30, y + 46), (x + 52, y + 50)], "#c98a74", 5)            # Mund


def zzz(cv, t, x, y, size=54, alpha=1.0):
    for i in range(3):
        k = (t * 0.5 + i / 3) % 1.0
        a = math.sin(k * math.pi) * alpha
        place(cv, text_sprite("Z", int(size * (0.7 + 0.5 * k)), color="#ffffff", stroke=0,
                              weight="black"), x + 60 * k, y - 150 * k, 1.0, a)


# ------------------------------------------------------------ 1 Einstieg (Hook)
def s1_einstieg(t):
    cv = night(t)
    p = Pen(cv)
    sleeper(p, t)
    zzz(cv, t, 560, 1270, alpha=1 - prog(t, 4.4, 4.8))
    dreams(cv, t, dissolve=prog(t, 2.0, 4.0), appear=1.0)
    if t > 1.0:
        pill(cv, "ca. 2 Stunden Träume", 540, 1700, LILAC, scale=ease_out_back(prog(t, 1.0, 1.35)),
             size=46)
    if t > 4.6:
        place(cv, text_sprite("?", 260, color="#ffffff"), 540, 900, ease_out_back(prog(t, 4.6, 5.0)))
    cv = punch(cv, t)
    caption(cv, t, -1, 4.6, "2 Stunden geträumt – *fast alles vergessen*", 500, size=84)
    caption(cv, t, 4.6, 9, "Warum *eigentlich*?", 500, size=100)
    return cv


# ------------------------------------------------------------ Gehirn
LOBES = [(-120, -40, 95), (-20, -90, 100), (90, -60, 95), (150, 30, 80), (-150, 50, 80),
         (-40, 40, 110), (60, 50, 100)]


def brain(p, cx, cy, s=1.0, col=BRAIN, dark=BRAIN_DARK, lit=None):
    p.line([(cx + 80 * s, cy + 120 * s), (cx + 60 * s, cy + 250 * s)], dark, 46 * s)
    p.circle(cx + 150 * s, cy + 125 * s, 62 * s, dark)
    for i, (dx, dy, r) in enumerate(LOBES):
        c = col if lit is None else mix("#3a2f6e", col, lit[i])
        p.circle(cx + dx * s, cy + dy * s, r * s, c)
    # Windungen
    for j, (dx, dy, ln) in enumerate(((-150, -40, 120), (-60, -100, 140), (50, -60, 130),
                                      (-120, 50, 120), (20, 20, 140), (100, 70, 90))):
        pts = [(cx + (dx + u * ln) * s, cy + (dy + 16 * math.sin(u * 9 + j)) * s)
               for u in [i / 14 for i in range(15)]]
        p.line(pts, dark if lit is None else mix("#2a2350", dark, min(lit)), 7 * s)


HIPPO = [(-60, 70), (-30, 92), (10, 98), (45, 84), (62, 58), (52, 36)]


def hippocampus(p, cx, cy, s, col):
    p.line([(cx + x * s, cy + y * s) for x, y in HIPPO], col, 26 * s)
    p.circle(cx + 52 * s, cy + 36 * s, 20 * s, col)


# ------------------------------------------------------------ 2 REM
def s2_rem(t):
    cv = night(t)
    p = Pen(cv)
    if t < 4.6:
        a = prog(4.6 - t, 0, 0.25)
        k = ease_out_back(prog(t, 0.2, 0.6))
        cx, cy = 540, 1100

        def eye(lp):
            w, h = 300 * k, 150 * k
            top = [(cx + w * math.cos(u), cy - h * math.sin(u)) for u in
                   [math.pi * i / 30 for i in range(31)]]
            bot = [(cx + w * math.cos(u), cy + h * 0.55 * math.sin(u)) for u in
                   [math.pi - math.pi * i / 30 for i in range(31)]]
            lp.poly(top + bot, SKIN)
            px = cx + 150 * k * math.sin(t * 9) * (0.6 + 0.4 * math.sin(t * 2.3))
            lp.ellipse((px - 80 * k, cy - 95 * k, px + 80 * k, cy + 40 * k), "#e9b493")
            lp.line([(cx - w, cy), (cx - w * 0.5, cy + 34 * k), (cx + w * 0.5, cy + 34 * k),
                     (cx + w, cy)], INK, 9)
            for i in range(7):
                u = -0.75 + i * 0.25
                bx, by = cx + w * 0.8 * u, cy + 30 * k * (1 - u * u) + 8
                lp.line([(bx, by), (bx + 10 * u, by + 36)], INK, 7)
        faded(cv, a, eye)
        if t > 1.6:
            pill(cv, "REM = schnelle Augen-Bewegung", 540, 1420, TURQ, a,
                 ease_out_back(prog(t, 1.6, 1.95)))
    else:
        k = ease_out_back(prog(t, 4.6, 5.0))
        glow_k = 0.5 + 0.5 * math.sin(t * 5)
        place(cv, glow(330, PINK, 0.35 + 0.25 * glow_k), 540, 1060)
        brain(p, 540, 1060, 1.25 * k)
        # Aktivitäts-Balken
        f = ease_out(prog(t, 5.2, 6.4)) * 0.9
        p.rrect((190, 1500, 890, 1560), 30, "#2a2f6e")
        if f > 0.02:
            p.rrect((190, 1500, 190 + 700 * f, 1560), 30, TURQ)
        place(cv, text_sprite("fast wie wach", 44, weight="bold", stroke=0), 540, 1620,
              alpha=prog(t, 6.0, 6.3))
    caption(cv, t, 0.2, 4.6, "Träume entstehen in der *REM-Phase*", 500, size=88)
    caption(cv, t, 4.6, 10, "Dein Gehirn: fast so *aktiv wie am Tag*", 500, size=86)
    return cv


# ------------------------------------------------------------ 3 Noradrenalin
PARTS = [(rng.uniform(0, 6.3), rng.uniform(250, 420), rng.uniform(0.3, 0.8)) for _ in range(40)]


def floppy(p, x, y, s=1.0):
    p.rrect((x - 90 * s, y - 90 * s, x + 90 * s, y + 90 * s), 14 * s, "#5b6bd6")
    p.rrect((x - 50 * s, y - 90 * s, x + 50 * s, y - 30 * s), 6 * s, "#d7defc")
    p.rrect((x - 60 * s, y + 10 * s, x + 60 * s, y + 90 * s), 8 * s, "#ffffff")


def s3_stoff(t):
    cv = night(t)
    p = Pen(cv)
    level = 1 - ease_in_out(prog(t, 1.0, 3.4)) * 0.93
    cx, cy = 540, 1000
    brain(p, cx, cy, 1.05)
    n = int(len(PARTS) * level)
    for ang, rad, sp in PARTS[:n]:
        a = ang + t * sp
        x, y = cx + math.cos(a) * rad, cy + math.sin(a) * rad * 0.8
        place(cv, glow(22, GOLD, 0.9), x, y)
        p.circle(x, y, 8, GOLD)
    # Füllstand
    p.rrect((150, 1430, 930, 1480), 25, "#2a2f6e")
    p.rrect((150, 1430, 150 + 780 * level, 1480), 25, GOLD)
    place(cv, text_sprite("Noradrenalin", 46, weight="bold", stroke=0, color=GOLD), 540, 1390)
    if t > 3.8:
        k = ease_out_back(prog(t, 3.8, 4.2))
        floppy(p, 540, 1650, 0.8 * k)
        if t > 4.4:
            g = ease_out(prog(t, 4.4, 4.7))
            p.line([(540 - 110 * g, 1650 - 110 * g), (540 + 110 * g, 1650 + 110 * g)], "#ff4d6d", 22)
    caption(cv, t, 0.2, 3.8, "Aber es fehlt *Noradrenalin*", 500, size=92)
    caption(cv, t, 3.8, 10, "Das braucht dein Gehirn zum *Speichern*", 500, size=86)
    return cv


# ------------------------------------------------------------ 4 Hippocampus
def s4_hippo(t):
    cv = night(t)
    p = Pen(cv)
    cx, cy, s = 540, 1030, 1.3
    if t < 4.8:
        lit = [0.55] * len(LOBES)
        brain(p, cx, cy, s, lit=lit)
        pulse = 0.6 + 0.4 * math.sin(t * 6)
        if t > 0.8:
            place(cv, glow(140, TURQ, pulse), cx, cy + 75 * s)
        hippocampus(p, cx, cy, s, TURQ)
        if t > 1.4:
            pill(cv, "Hippocampus = Speicher-Knopf", 540, 1500, TURQ,
                 prog(4.8 - t, 0, 0.2), ease_out_back(prog(t, 1.4, 1.75)))
    else:
        tt = t - 4.8
        lit = [ease_out(prog(tt, 0.3 + i * 0.25, 0.7 + i * 0.25)) * 0.45 + 0.55
               for i in range(len(LOBES))]
        place(cv, glow(260, "#ffe9a8", 0.25 * min(lit)), cx, cy)
        brain(p, cx, cy, s, lit=lit)
        hippocampus(p, cx, cy, s, "#4a4f8a")
        zzz(cv, t, cx + 40, cy + 30, size=50)
        pill(cv, "wacht als Letztes auf", 540, 1500, LILAC, scale=ease_out_back(prog(tt, 0.6, 0.95)))
    caption(cv, t, 0.2, 4.8, "Der *Hippocampus*: dein Speicher-Knopf", 500, size=86)
    caption(cv, t, 4.8, 11, "Er wacht vermutlich *als Letztes* auf", 500, size=86)
    return cv


# ------------------------------------------------------------ 5 Aufnahme aus
def s5_film(t):
    cv = night(t)
    p = Pen(cv)
    k = ease_out_back(prog(t, 0.1, 0.5))
    # Leinwand mit Traum
    p.rrect((120, 720, 960, 1220), 30, "#0e1236", "#ffffff", 6)
    for i, kind in enumerate(KINDS):
        x = 120 + ((t * 160 + i * 190) % 840)
        if 170 < x < 910:
            icon(p, kind, x, 970 + 60 * math.sin(t * 2 + i), 1.3)
    # Kamera
    cx, cy = 540, 1470
    p.rrect((cx - 200 * k, cy - 110 * k, cx + 160 * k, cy + 110 * k), 26, "#3a3f7a")
    p.poly([(cx + 160 * k, cy - 40 * k), (cx + 260 * k, cy - 100 * k),
            (cx + 260 * k, cy + 100 * k), (cx + 160 * k, cy + 40 * k)], "#3a3f7a")
    p.circle(cx - 110 * k, cy - 170 * k, 70 * k, "#3a3f7a")
    p.circle(cx + 30 * k, cy - 170 * k, 70 * k, "#3a3f7a")
    p.circle(cx - 130 * k, cy, 26 * k, "#6b6f8f")                         # REC aus
    place(cv, text_sprite("REC", 44, weight="bold", stroke=0, color="#8a8fb3"), cx - 30, cy, k)
    if t > 1.8:
        pill(cv, "Aufnahme: AUS", 540, 1680, "#ff6b8a", scale=ease_out_back(prog(t, 1.8, 2.15)),
             size=46)
    caption(cv, t, 0.2, 9, "Der Film läuft – die *Aufnahme ist aus*", 500, size=88)
    return cv


# ------------------------------------------------------------ 6 Mäuse
def mouse(p, x, y, s=1.0):
    p.line([(x - 140 * s, y + 30 * s), (x - 220 * s, y + 10 * s), (x - 260 * s, y - 40 * s)],
           "#d99aa8", 10 * s)
    p.ellipse((x - 160 * s, y - 70 * s, x + 90 * s, y + 70 * s), "#b9b4cf")
    p.circle(x + 70 * s, y - 70 * s, 50 * s, "#b9b4cf")
    p.circle(x + 70 * s, y - 70 * s, 30 * s, "#e8a8bd")
    p.circle(x + 120 * s, y + 0 * s, 58 * s, "#b9b4cf")
    p.circle(x + 176 * s, y + 8 * s, 11 * s, PINK)
    p.line([(x + 118 * s, y - 10 * s), (x + 142 * s, y - 6 * s)], INK, 5 * s)


def s6_maus(t):
    cv = night(t)
    p = Pen(cv)
    mouse(p, 520, 1450, 1.15)
    zzz(cv, t, 720, 1320, size=46)
    # Traumblasen werden wegradiert
    er = prog(t, 1.6, 4.6)
    ex = lerp(150, 950, ease_in_out(er))
    for i, kind in enumerate(KINDS[:4]):
        x, y = 210 + i * 220, 980 + 30 * math.sin(t * 1.5 + i)
        if x > ex:
            bubble(p, kind, x, y, 82)
        else:
            for dx, dy, rr in DUST[i][:8]:
                d = min(1.0, (ex - x) / 300)
                p.circle(x + dx * 90 * (1 + d), y + dy * 90 * (1 + d) - 80 * d, rr * (1 - 0.7 * d),
                         mix("#141a4d", BUBBLE_LINE, 1 - d))
    if 0 < er < 1:
        p.rrect((ex - 50, 960, ex + 50, 1100), 18, PINK)
        p.rrect((ex - 50, 1040, ex + 50, 1100), 18, "#5b6bd6")
    if t > 0.6:
        pill(cv, "Studie 2019", 540, 1700, LILAC, scale=ease_out_back(prog(t, 0.6, 0.95)))
    caption(cv, t, 0.2, 9, "Bei Mäusen: Nervenzellen, die beim *Vergessen* helfen", 500, size=82)
    return cv


# ------------------------------------------------------------ 7 Trick
def notebook(p, t, x, y, written):
    p.rrect((x - 260, y - 200, x + 260, y + 220), 24, "#fffaf0")
    p.rrect((x - 260, y - 200, x - 230, y + 220), 12, "#ff8fc7")
    for i in range(6):
        ly = y - 130 + i * 62
        p.line([(x - 200, ly + 26), (x + 220, ly + 26)], "#cfd6ee", 3, caps=False)
        w = prog(written, i / 6, (i + 1) / 6)
        if w > 0:
            pts = [(x - 190 + u * 380 * w * (0.7 + 0.3 * ((i * 7) % 3) / 2),
                    ly + 6 * math.sin(u * 40 + i)) for u in [j / 30 for j in range(31)]]
            p.line(pts, "#3b3f8f", 6)
    return written


def s7_trick(t):
    cv = night(t)
    p = Pen(cv)
    if t < 5.8:
        a = prog(5.8 - t, 0, 0.25)

        def scene(lp):
            sleeper(lp, t, y=1430)
            # Wecker
            ring = t < 1.2
            wx, wy = 930, 1300 + (8 * math.sin(t * 60) if ring else 0)
            lp.circle(wx, wy, 70, "#ff6b8a")
            lp.circle(wx, wy, 56, "#ffffff")
            lp.line([(wx, wy), (wx, wy - 36)], INK, 6)
            lp.line([(wx, wy), (wx + 26, wy)], INK, 6)
            lp.circle(wx - 50, wy - 64, 22, "#ff6b8a")
            lp.circle(wx + 50, wy - 64, 22, "#ff6b8a")
        faded(cv, a, scene)
        if a > 0.5:
            dreams(cv, t, appear=prog(t, 1.6, 4.6), y_shift=10)
        steps = ("1. still liegen", "2. Augen zu", "3. an den Traum denken")
        i = min(2, int((t - 1.2) / 1.3)) if t > 1.2 else -1
        if i >= 0:
            t0 = 1.2 + i * 1.3
            pill(cv, steps[i], 540, 1700, TURQ, a, ease_out_back(prog(t, t0, t0 + 0.35)), size=46)
    else:
        k = ease_out_back(prog(t, 5.9, 6.3))
        written = prog(t, 6.3, 9.0)
        cx, cy = 540, 1150
        if k > 0:
            notebook(p, t, cx, cy, written)
            px = cx - 190 + 380 * ((written * 6) % 1)
            py = cy - 130 + 62 * min(5, int(written * 6)) - 20
            p.line([(px, py), (px + 90, py - 140)], GOLD, 26)
            p.poly([(px - 8, py + 14), (px - 10, py - 8), (px + 12, py + 2)], INK)
        pill(cv, "sofort aufschreiben", 540, 1500, GOLD, scale=ease_out_back(prog(t, 6.4, 6.75)))
    caption(cv, t, 0.2, 5.8, "Ein Trick: *still liegen*, Augen zu, nachdenken", 500, size=84)
    caption(cv, t, 5.8, 11, "Dann *sofort* aufschreiben!", 500, size=92)
    return cv


# ------------------------------------------------------------ 8 Ende
def s8_ende(t):
    cv = night(t)
    dreams(cv, t, appear=1.0, y_shift=560)
    caption(cv, t, 0.1, 9, "Hättest du's *gewusst*?", 760, size=110)
    caption(cv, t, 1.6, 9, "Folge für mehr *Warum eigentlich?*", 1010, size=66)
    return cv


VIDEO = Video([
    (7.5, s1_einstieg, [(0.0, "Du hast heute Nacht rund zwei Stunden geträumt – und weißt davon fast nichts mehr."),
                        (4.6, "Warum ist das so?")]),
    (8.0, s2_rem, [(0.2, "Die meisten Träume entstehen in der REM-Phase – da zucken deine Augen hinter den Lidern hin und her."),
                   (4.6, "Dein Gehirn ist dann fast so aktiv wie am Tag.")]),
    (8.0, s3_stoff, [(0.2, "Aber ein wichtiger Botenstoff fehlt fast ganz: Noradrenalin."),
                     (3.8, "Und den braucht dein Gehirn, um Erlebnisse abzuspeichern.")]),
    (9.0, s4_hippo, [(0.2, "Dazu kommt der Hippocampus – sozusagen der Speicher-Knopf für neue Erinnerungen."),
                     (4.8, "Forscher vermuten: Er wacht morgens als Letztes auf.")]),
    (5.0, s5_film, [(0.2, "Der Film läuft also – aber die Aufnahme ist aus.")]),
    (6.5, s6_maus, [(0.2, "Bei Mäusen haben Forscher sogar Nervenzellen gefunden, die im Traumschlaf beim Vergessen helfen.")]),
    (9.5, s7_trick, [(0.2, "Ein Trick dagegen: Bleib nach dem Aufwachen kurz still liegen, Augen zu, und denk an deinen Traum."),
                     (5.8, "Dann schreib ihn sofort auf.")]),
    (4.2, s8_ende, [(0.2, "Hättest du es gewusst?"),
                    (1.7, "Folge für mehr: Warum eigentlich?")]),
])

if __name__ == "__main__":
    cli(VIDEO, __file__, cover_t=1.4)
