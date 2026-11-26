"""Folge 8: Was wäre, wenn die Erde aufhört, sich zu drehen?  (9:16, Kurzformat ~35 s)

Rendern:   python3 videos/08_erde_stopp.py            (ElevenLabs, Stimme Brian, 12 % schneller)
Vorschau:  python3 videos/08_erde_stopp.py --stills

Kurzformat-Test: erster Satz < 3 s, alle 3–5 s neues Bild, schnellere Stimme,
letztes Bild = erstes Bild (Loop).
"""
import math
import os
import random
import sys
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image, ImageDraw  # noqa: E402

from ev import tts  # noqa: E402
from ev.engine import (S, Pen, Video, blend_canvas, canvas, caption, cli, ease_in_out,  # noqa: E402
                       ease_out, ease_out_back, glow, lerp, mix, place, prog, rgba, text_sprite)

tts.TEMPO = 1.12

SPACE = ((0, "#050a1f"), (0.55, "#0b1640"), (1, "#14225a"))
DAY = ((0, "#3d86e0"), (0.6, "#7fbaf2"), (1, "#cfe8ff"))
STORM = ((0, "#2a2f3d"), (0.6, "#474e60"), (1, "#5d6578"))
OCEAN = "#1f6fd1"
LAND = "#3fa65a"
SAND = "#c9b36b"
GOLD = "#FFD23F"
ORANGE = "#FF9F43"
RED = "#ff4d4d"
INK = "#0b1230"

rng = random.Random(8)
STARS = [(rng.uniform(0, 1080), rng.uniform(0, 1920), rng.uniform(1.5, 3.5), rng.uniform(0, 6.3))
         for _ in range(90)]


def space(t):
    cv = canvas(SPACE)
    p = Pen(cv)
    for x, y, r, ph in STARS:
        p.circle(x, y, r, mix("#0b1640", "#ffffff", 0.4 + 0.5 * (0.5 + 0.5 * math.sin(t * 2 + ph))))
    return cv


def pill(cv, text, cx, cy, color, alpha=1.0, scale=1.0, size=42, fg=INK):
    spr = text_sprite(text, size, weight="bold", stroke=0, color=fg, max_w=900)
    w, h = spr.width / S + 52, spr.height / S + 24
    img = Image.new("RGBA", (int(w * S) + 4, int(h * S) + 4), (0, 0, 0, 0))
    Pen(img).rrect((0, 0, w, h), h / 2, color)
    place(img, spr, w / 2, h / 2)
    place(cv, img, cx, cy, scale, alpha)


def cam(cv, t, z0=1.0, zoom_dur=0.7, shake_at=None, shake_dur=0.9, amp=16):
    """Zoom am Anfang + Wackeln (z. B. beim Stopp)."""
    z = lerp(z0, 1.0, ease_out(prog(t, 0, zoom_dur)))
    a = 0.0
    if shake_at is not None and shake_at <= t < shake_at + shake_dur:
        a = amp * (1 - prog(t, shake_at, shake_at + shake_dur)) * S
    if z <= 1.001 and a < 0.5:
        return cv
    z = max(z, 1.0 + 2 * a / cv.width + 0.002)
    w, h = cv.size
    cw, ch = int(w / z), int(h / z)
    dx, dy = a * math.sin(t * 61), a * math.cos(t * 47)
    x0 = int(min(max(0, (w - cw) / 2 + dx), w - cw))
    y0 = int(min(max(0, (h - ch) / 2 + dy), h - ch))
    return cv.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.BILINEAR)


# ------------------------------------------------------------ Globus
CONTINENTS = [
    [(35, -17), (37, 10), (31, 32), (12, 43), (-11, 40), (-35, 20), (-34, 18), (-17, 12), (5, 8),
     (5, -10), (15, -17)],                                                              # Afrika
    [(36, -9), (43, -9), (48, -5), (54, 8), (58, 10), (70, 25), (72, 60), (76, 100), (72, 140),
     (66, 180), (60, 165), (52, 140), (40, 128), (22, 120), (10, 105), (20, 93), (8, 77), (25, 62),
     (12, 45), (30, 33), (36, 28), (40, 20), (37, 15), (44, 8)],                         # Eurasien
    [(70, -160), (70, -95), (60, -65), (45, -60), (30, -81), (25, -80), (18, -95), (8, -80),
     (18, -105), (32, -117), (48, -125), (60, -145)],                                    # Nordamerika
    [(10, -75), (8, -60), (-5, -35), (-23, -42), (-35, -57), (-55, -68), (-40, -73), (-18, -71),
     (-5, -81)],                                                                         # Südamerika
    [(-12, 130), (-11, 142), (-25, 153), (-38, 146), (-35, 117), (-22, 114)],             # Australien
    [(60, -45), (70, -22), (82, -30), (78, -70), (68, -53)],                              # Grönland
]
GERMANY = (51, 10)
TILT = math.radians(18)


def _interp(poly, n=6):
    out = []
    for i in range(len(poly)):
        (a0, b0), (a1, b1) = poly[i], poly[(i + 1) % len(poly)]
        if b1 - b0 > 180:
            b1 -= 360
        elif b0 - b1 > 180:
            b1 += 360
        for k in range(n):
            u = k / n
            out.append((lerp(a0, a1, u), lerp(b0, b1, u)))
    return out


CONT_FINE = [_interp(c) for c in CONTINENTS]


def proj(lat, lon, rot, R):
    """Orthografische Projektion mit leicht gekippter Achse. -> (x, y, sichtbar)."""
    la, lo = math.radians(lat), math.radians(lon + rot)
    x, y, z = math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo)
    y2 = y * math.cos(TILT) - z * math.sin(TILT)
    z2 = y * math.sin(TILT) + z * math.cos(TILT)
    if z2 < 0:  # hinter dem Rand: auf den Rand schieben
        d = math.hypot(x, y2) or 1
        x, y2 = x / d, y2 / d
    return x * R, -y2 * R, z2 >= 0


def globe_sprite(R, rot, polar=0.0, pin=False, night=None):
    """Erde als Sprite. polar 0..1: Meere wandern zu den Polen. night: Winkel (Grad) der Nachtseite."""
    n = int(2 * R * S) + 8
    img = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = n / 2

    def P(pts):
        return [(c + x * S, c + y * S) for x, y in pts]

    d.ellipse([c - R * S, c - R * S, c + R * S, c + R * S], fill=rgba(OCEAN))
    if polar < 1:
        land = mix(LAND, SAND, polar * 0.6)
        for poly in CONT_FINE:
            pts = [proj(la, lo, rot, R) for la, lo in poly]
            if any(v for _, _, v in pts):
                d.polygon(P([(x, y) for x, y, _ in pts]), fill=land)
    if polar > 0:
        # Landgürtel um den Äquator, Meere an den Polen
        h = R * lerp(1.0, 0.5, ease_in_out(polar))
        band = []
        for i in range(73):
            a = 2 * math.pi * i / 72
            band.append((R * math.cos(a), max(-h, min(h, R * math.sin(a) + 10 * math.sin(a * 9 + rot / 30)))))
        lay = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        ImageDraw.Draw(lay).polygon(P(band), fill=rgba(SAND))
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * min(1, polar * 1.6))))
        img.alpha_composite(lay)
    if pin:
        x, y, vis = proj(*GERMANY, rot, R)
        if vis:
            d.ellipse([c + (x - 16) * S, c + (y - 16) * S, c + (x + 16) * S, c + (y + 16) * S],
                      fill=rgba(GOLD), outline=rgba(INK), width=int(4 * S))
    if night is not None:
        lay = Image.new("RGBA", (n, n), (0, 0, 0, 0))
        a = math.radians(night)
        pts = [(R * math.cos(a + math.pi / 2 + math.pi * i / 36), R * math.sin(a + math.pi / 2 + math.pi * i / 36))
               for i in range(37)]
        ImageDraw.Draw(lay).polygon(P(pts), fill=(5, 10, 35, 190))
        img.alpha_composite(lay)
    # Glanz / Atmosphärenrand
    d = ImageDraw.Draw(img)
    d.ellipse([c - R * S, c - R * S, c + R * S, c + R * S], outline=(160, 210, 255, 255), width=int(5 * S))
    return img


def globe(cv, cx, cy, R, rot, **kw):
    place(cv, glow(R * 1.35, "#5aa8ff", 0.35), cx, cy)
    place(cv, globe_sprite(R, rot, **kw), cx, cy)


def spin_rot(t, stop_at=None):
    """Drehwinkel: schnell drehen, bei stop_at abrupt anhalten."""
    if stop_at is None or t < stop_at:
        return -t * 140
    return -stop_at * 140 - 25 * (1 - math.exp(-(t - stop_at) * 12))


# ------------------------------------------------------------ 1 Einstieg (Hook)
GX, GY, GR = 540, 1160, 330


def stop_sign(cv, x, y, k):
    if k <= 0:
        return
    p = Pen(cv)
    r = 120 * k
    pts = [(x + r * math.cos(math.pi / 8 + i * math.pi / 4), y + r * math.sin(math.pi / 8 + i * math.pi / 4))
           for i in range(8)]
    p.poly(pts, RED)
    p.poly([(x + (r - 12 * k) * math.cos(math.pi / 8 + i * math.pi / 4),
             y + (r - 12 * k) * math.sin(math.pi / 8 + i * math.pi / 4)) for i in range(8)], None, "#ffffff", 6)
    place(cv, text_sprite("STOPP", 56, color="#ffffff", stroke=0), x, y, k)


def s1_einstieg(t):
    cv = space(t)
    stop = 1.5
    globe(cv, GX, GY, GR, spin_rot(t, stop))
    stop_sign(cv, 860, 850, ease_out_back(prog(t, stop + 0.05, stop + 0.4)))
    cv = cam(cv, t, z0=1.12, shake_at=stop, shake_dur=0.8, amp=18)
    caption(cv, t, -1, 9, "Was, wenn die Erde *stoppt*?", 470, size=100)
    return cv


# ------------------------------------------------------------ 2 Tempo
def gauge(cv, x, y, r, v, vmax=1200):
    p = Pen(cv)
    p.circle(x, y, r, "#13285c", "#ffffff", 8)
    for i in range(7):
        a = math.radians(150 + 240 * i / 6)
        p.line([(x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78),
                (x + math.cos(a) * r * 0.92, y + math.sin(a) * r * 0.92)], "#ffffff", 6)
    a = math.radians(150 + 240 * min(v, vmax) / vmax)
    p.line([(x, y), (x + math.cos(a) * r * 0.75, y + math.sin(a) * r * 0.75)], ORANGE, 10)
    p.circle(x, y, 14, "#ffffff")
    place(cv, text_sprite(f"*{int(v):,}*".replace(",", "."), 60, hl=GOLD), x, y + r * 0.45)
    place(cv, text_sprite("km/h", 30, weight="bold", stroke=0), x, y + r * 0.72)


def s2_tempo(t):
    cv = space(t)
    grot = -4 - t * 5   # Europa in der Mitte, langsam weiterdrehend
    globe(cv, 470, 1250, 380, grot, pin=True)
    v = 1050 * ease_out(prog(t, 0.4, 2.2))
    gauge(cv, 830, 820, 160, v)
    if t > 0.5:
        x, y, vis = proj(*GERMANY, grot, 380)
        pill(cv, "Deutschland", 470 + x - 40, 1250 + y - 80, GOLD, scale=ease_out_back(prog(t, 0.5, 0.85)))
    caption(cv, t, 0.2, 9, "Du rast mit: über *1.000 km/h*", 470, size=90)
    return cv


# ------------------------------------------------------------ 3 Alles fliegt weg
@lru_cache(None)
def obj_sprite(kind):
    w, h = 300, 300
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    p = Pen(img)
    if kind == "house":
        p.rrect((50, 120, 250, 280), 8, "#f2d6b3")
        p.poly([(35, 125), (150, 30), (265, 125)], "#d9553a")
        p.rrect((120, 200, 175, 280), 6, "#7a4b2a")
        p.rrect((70, 150, 110, 190), 4, "#9fd0ff")
        p.rrect((190, 150, 230, 190), 4, "#9fd0ff")
    elif kind == "car":
        p.rrect((30, 150, 270, 225), 22, "#4f9cf0")
        p.rrect((80, 100, 220, 160), 22, "#4f9cf0")
        p.rrect((95, 110, 205, 150), 12, "#cfe8ff")
        p.circle(85, 228, 30, INK)
        p.circle(215, 228, 30, INK)
    elif kind == "person":
        p.circle(150, 80, 34, "#f6c9a8")
        p.line([(150, 115), (150, 200)], ORANGE, 30)
        p.line([(150, 140), (100, 175)], ORANGE, 16)
        p.line([(150, 140), (200, 175)], ORANGE, 16)
        p.line([(150, 200), (120, 270)], INK, 18)
        p.line([(150, 200), (180, 270)], INK, 18)
    elif kind == "tree":
        p.rrect((135, 170, 165, 280), 8, "#7a4b2a")
        p.circle(150, 130, 75, "#3d9b5f")
    return img


STREET = [("house", 180, 1.0, 0.0), ("tree", 400, 0.8, 0.3), ("house", 620, 0.95, 0.1),
          ("car", 330, 0.7, 0.5), ("person", 520, 0.55, 0.65), ("person", 760, 0.55, 0.4),
          ("car", 880, 0.7, 0.2), ("tree", 980, 0.75, 0.6)]


def s3_wegfliegen(t):
    cv = canvas(DAY)
    p = Pen(cv)
    p.poly([(0, 1560), (1080, 1560), (1080, 1920), (0, 1920)], "#4f8a3d")
    p.rrect((-10, 1600, 1090, 1700), 0, "#5b6475")
    go = 0.9
    for kind, x, sc, delay in STREET:
        tt = max(0.0, t - go - delay * 0.6)
        dx = 900 * tt * tt + 380 * tt
        dy = -260 * tt + 120 * tt * tt * 0.2
        ang = -200 * tt * (1 if kind != "house" else 0.6)
        spr = obj_sprite(kind)
        if tt > 0:
            spr = spr.rotate(ang, expand=True, resample=Image.BILINEAR)
        base_y = 1600 - 150 * sc
        if kind in ("car", "person"):
            base_y = 1655 - 150 * sc
        place(cv, spr, x + dx, base_y + dy, sc)
    if t > go:
        for i in range(16):
            y = 820 + i * 55
            x = -300 + ((t * 2600 + i * 237) % 1700)
            p.line([(x, y), (x + 220, y)], "#ffffff", 6)
        pill(cv, "alles fliegt weiter →", 540, 1780, "#ffffff", scale=ease_out_back(prog(t, go + 0.3, go + 0.65)),
             size=46)
    caption(cv, t, 0.2, 9, "Alles fliegt *weiter*: Menschen, Autos, *Häuser*", 470, size=84)
    return cv


# ------------------------------------------------------------ 4 Sturm + Flutwelle
WIND = [(rng.uniform(0, 1), rng.uniform(700, 1700), rng.uniform(120, 320)) for _ in range(40)]


def s4_sturm(t):
    cv = canvas(STORM)
    p = Pen(cv)
    for ph, y, ln in WIND:
        x = -400 + ((t * 2400 + ph * 1800) % 1800)
        p.line([(x, y), (x + ln, y - 20)], "#c9d2e3", 5)
    # Skyline
    for i, (x, w, h) in enumerate(((60, 120, 260), (200, 100, 380), (320, 140, 300), (480, 110, 450),
                                   (610, 130, 330), (760, 120, 400), (900, 140, 280))):
        p.rrect((x, 1620 - h, x + w, 1700), 6, "#1d2333")
        for r in range(int(h / 60)):
            p.rrect((x + 20, 1620 - h + 25 + r * 60, x + w - 20, 1620 - h + 45 + r * 60), 3, "#ffd36b55")
    p.poly([(0, 1700), (1080, 1700), (1080, 1920), (0, 1920)], "#2b3242")
    # Flutwelle von links
    k = ease_in_out(prog(t, 1.4, 3.6))
    if k > 0:
        H = 1100 * k
        front = -200 + 900 * k
        pts = [(-50, 1920), (-50, 1920 - H * 0.8)]
        for i in range(31):
            u = i / 30
            x = lerp(-50, front, u)
            y = 1920 - H * (0.8 + 0.25 * math.sin(u * math.pi * 0.9)) + 18 * math.sin(u * 20 + t * 6)
            pts.append((x, y))
        pts += [(front + 120, 1920 - H * 0.55), (front + 60, 1920 - H * 0.35), (front + 160, 1920)]
        p.poly(pts, "#1f5fb8")
        p.poly([(x, y + 30) for x, y in pts[2:-3]] + [(front - 40, 1920 - H * 0.7)], "#2f7fdc")
        for i in range(12):
            x = front - 60 + 40 * math.sin(i * 1.7 + t * 5)
            y = 1920 - H * (0.95 - i * 0.03)
            p.circle(x + 60, y, 14 + 6 * math.sin(i + t * 4), "#e6f2ff")
    if t > 0.5:
        pill(cv, "Wind > 1.000 km/h", 760, 760, "#ffffff", scale=ease_out_back(prog(t, 0.5, 0.85)), size=46)
    caption(cv, t, 0.2, 9, "Stürme stärker als jeder *Hurrikan*", 470, size=90)
    return cv


# ------------------------------------------------------------ 5 Ein Tag = ein Jahr
MONTHS = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]


def s5_jahr(t):
    cv = space(t)
    p = Pen(cv)
    sx, sy = 540, 1150
    place(cv, glow(260, "#ffd27a", 0.8), sx, sy)
    p.circle(sx, sy, 95, "#ffd27a")
    rx, ry = 360, 250
    for i in range(72):
        a = 2 * math.pi * i / 72
        if i % 2 == 0:
            p.line([(sx + rx * math.cos(a), sy + ry * math.sin(a)),
                    (sx + rx * math.cos(a + 0.08), sy + ry * math.sin(a + 0.08))], "#5a6aa8", 4)
    u = ease_in_out(prog(t, 1.0, 5.6))
    th = math.pi + 2 * math.pi * u
    ex, ey = sx + rx * math.cos(th), sy + ry * math.sin(th)
    to_sun = math.degrees(math.atan2(sy - ey, sx - ex))
    globe(cv, ex, ey, 85, 30, night=to_sun, pin=False)
    # fester Punkt (Deutschland) – zeigt immer nach rechts, weil sich die Erde nicht dreht
    mx, my = ex + 62, ey - 10
    lit = math.cos(math.radians(to_sun)) > 0
    p.circle(mx, my, 13, GOLD if lit else "#5a6488")
    m = MONTHS[int((u * 12)) % 12] if u < 1 else "Jan"
    pill(cv, "hell" if lit else "dunkel", 540, 780,
         GOLD if lit else "#5a6488", scale=1.0, size=54, fg=INK if lit else "#ffffff")
    pill(cv, f"Monat: {m}", 540, 1560, "#ffffff", size=46)
    caption(cv, t, 0.2, 9, "1 Tag = *1 Jahr*: halb hell, halb dunkel", 470, size=88)
    return cv


# ------------------------------------------------------------ 6 Meere zu den Polen
def s6_meere(t):
    cv = space(t)
    m = ease_in_out(prog(t, 0.6, 3.2))
    globe(cv, GX, GY, GR, -40, polar=m)
    p = Pen(cv)
    if 0.6 < t < 3.4:
        a = math.sin(prog(t, 0.6, 3.4) * math.pi)
        for dx in (-150, 0, 150):
            p.arrow(GX + dx, GY - 60, GX + dx, GY - 220, mix("#0b1640", "#ffffff", a), 14, 34)
            p.arrow(GX + dx, GY + 60, GX + dx, GY + 220, mix("#0b1640", "#ffffff", a), 14, 34)
    if t > 2.6:
        pill(cv, "Riesen-Kontinent", GX, GY, SAND, scale=ease_out_back(prog(t, 2.6, 2.95)), size=50)
        pill(cv, "Meer am Nordpol", GX, GY - GR - 60, "#9fd0ff", scale=ease_out_back(prog(t, 3.0, 3.35)))
        pill(cv, "Meer am Südpol", GX, GY + GR + 60, "#9fd0ff", scale=ease_out_back(prog(t, 3.2, 3.55)))
    caption(cv, t, 0.2, 9, "Meere zu den *Polen* – ein *Riesen-Kontinent*", 470, size=86)
    return cv


# ------------------------------------------------------------ 7 Zum Glück
def s7_gluck(t):
    cv = space(t)
    globe(cv, GX, GY, GR, -t * 30)
    if t > 0.6:
        place(cv, text_sprite("*+0,002 Sek.*", 96, hl=GOLD), 540, 720, ease_out_back(prog(t, 0.6, 1.0)))
        pill(cv, "pro Jahrhundert", 540, 830, "#ffffff", scale=ease_out_back(prog(t, 1.0, 1.35)), size=46)
    caption(cv, t, 0.2, 9, "Zum Glück: nur *ganz langsam* langsamer", 470, size=88)
    return cv


# ------------------------------------------------------------ 8 Ende (Loop zum Anfang)
def s8_ende(t):
    cv = space(t)
    globe(cv, GX, GY, GR, -(t - 3.0) * 140)
    caption(cv, t, 0.1, 9, "Hättest du's *gewusst*?", 430, size=100)
    caption(cv, t, 1.4, 9, "Folge für mehr *Warum eigentlich?*", 660, size=62)
    return cv


VIDEO = Video([
    (3.5, s1_einstieg, [(0.0, "Was wäre, wenn die Erde plötzlich aufhört, sich zu drehen?")]),
    (4.0, s2_tempo, [(0.2, "Du rast nämlich gerade mit – in Deutschland mit über 1.000 km/h.")]),
    (5.0, s3_wegfliegen, [(0.2, "Stoppt die Erde, fliegt alles weiter, was nicht festgeschraubt ist: Menschen, Autos, sogar Häuser.")]),
    (4.0, s4_sturm, [(0.2, "Dazu Stürme, stärker als jeder Hurrikan – und riesige Flutwellen.")]),
    (6.0, s5_jahr, [(0.2, "Und danach? Ein Tag dauert ein ganzes Jahr: ein halbes Jahr hell, ein halbes Jahr dunkel.")]),
    (5.0, s6_meere, [(0.2, "Die Meere fließen zu den Polen. In der Mitte entsteht ein einziger Riesen-Kontinent.")]),
    (5.0, s7_gluck, [(0.2, "Zum Glück wird die Erde nur ganz langsam langsamer – um ein paar tausendstel Sekunden pro Jahrhundert.")]),
    (3.0, s8_ende, [(0.2, "Hättest du es gewusst?"),
                    (1.5, "Folge für mehr: Warum eigentlich?")]),
])

if __name__ == "__main__":
    cli(VIDEO, __file__, cover_t=1.0)
