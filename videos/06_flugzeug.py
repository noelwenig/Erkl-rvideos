"""Folge 6: Warum fallen Flugzeuge nicht vom Himmel?  (9:16)

Rendern:   python3 videos/06_flugzeug.py            (ElevenLabs, Stimme Brian)
Vorschau:  python3 videos/06_flugzeug.py --stills
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

BG = ((0, "#1d5fc9"), (0.55, "#5aa6f5"), (1, "#bfe3ff"))
SUNSET = ((0, "#2b3f8f"), (0.5, "#d9708a"), (1, "#ffc27a"))
PLANE = "#ffffff"
PLANE_SHADE = "#dbe5f3"
WING = "#9fb3d1"
NAVY = "#1f3b73"
CORAL = "#ff6b4a"
GREEN = "#3ddc84"
AIR = "#ffffff"
GOLD = "#FFD23F"
INK = "#0f1d3d"

rng = random.Random(6)
CLOUDS = [(rng.uniform(0, 1400), rng.uniform(150, 1800), rng.uniform(0.6, 1.3), rng.uniform(40, 110))
          for _ in range(9)]


def cloud(p, x, y, s, col="#ffffff"):
    for dx, dy, r in ((-90, 15, 55), (-30, -20, 75), (50, -5, 65), (110, 20, 45), (10, 25, 60)):
        p.circle(x + dx * s, y + dy * s, r * s, col)


def sky(t, speed=1.0, stops=BG, col="#ffffff"):
    cv = canvas(stops)
    p = Pen(cv)
    for x0, y, s, v in CLOUDS:
        x = 1300 - ((t * v * speed + x0) % 1600)
        cloud(p, x, y, s * 0.8, mix(stops[1][1], col, 0.55))
    return cv


def pill(cv, text, cx, cy, color, alpha=1.0, scale=1.0, size=42, fg=INK):
    spr = text_sprite(text, size, weight="bold", stroke=0, color=fg, max_w=900)
    w, h = spr.width / S + 52, spr.height / S + 24
    img = Image.new("RGBA", (int(w * S) + 4, int(h * S) + 4), (0, 0, 0, 0))
    Pen(img).rrect((0, 0, w, h), h / 2, color)
    place(img, spr, w / 2, h / 2)
    place(cv, img, cx, cy, scale, alpha)


def faded(cv, alpha, draw):
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
    x0, y0 = (w - cw) // 2, int((h - ch) * 0.5)
    return cv.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.BILINEAR)


def big_arrow(p, x0, y0, x1, y1, col, width=34):
    p.arrow(x0, y0, x1, y1, col, width, width * 2.4)


# ------------------------------------------------------------ Flugzeug (Seitenansicht)
def plane(p, cx, cy, s=1.0, rot=0.0, engine=True, t=0.0):
    r = math.radians(rot)
    cr, sr = math.cos(r), math.sin(r)

    def T(x, y):
        return cx + (x * cr - y * sr) * s, cy + (x * sr + y * cr) * s

    def poly(pts, col):
        p.poly([T(x, y) for x, y in pts], col)

    poly([(-300, -30), (-345, -165), (-290, -165), (-205, -36)], PLANE_SHADE)          # Leitwerk
    poly([(-330, -2), (-250, -6), (-215, 4), (-320, 14)], WING)                         # Höhenruder
    body = [(-262, -38), (225, -38)]
    body += [(225 + 75 * math.sin(a), -38 + 40 * (1 - math.cos(a)) + 2)
             for a in [math.pi / 2 * i / 10 for i in range(1, 11)]]
    body += [(300 - 75 * (1 - math.cos(a)), 4 + 34 * math.sin(a))
             for a in [math.pi / 2 * i / 10 for i in range(1, 11)]]
    body += [(-230, 38), (-305, -22)]
    poly(body, PLANE)
    poly([(-230, 14), (240, 14), (262, 24), (-218, 24)], CORAL)                         # Streifen
    for i in range(15):
        x = -195 + i * 27
        p.circle(*T(x, -12), 6.5 * s, NAVY)
    poly([(244, -26), (282, -10), (250, -8)], NAVY)                                       # Cockpit
    poly([(70, 12), (-30, 18), (-185, 62), (-150, 70), (20, 34)], WING)                  # Flügel
    eng = [(30 + 60 * math.cos(a), 60 + 21 * math.sin(a)) for a in
           [2 * math.pi * i / 24 for i in range(24)]]
    poly(eng, "#c9d4e6")
    poly([(84 + 6 * math.cos(a), 60 + 19 * math.sin(a)) for a in
          [2 * math.pi * i / 16 for i in range(16)]], "#5b6b8a")
    if engine:
        for k in range(3):
            u = (t * 3 + k / 3) % 1.0
            x, y = T(-30 - 70 * u, 60)
            p.circle(x, y, (8 + 10 * u) * s, mix("#ffffff", "#bfe3ff", u))


def car_icon(p, x, y, s, col):
    p.rrect((x - 34 * s, y - 8 * s, x + 34 * s, y + 14 * s), 7 * s, col)
    p.rrect((x - 18 * s, y - 24 * s, x + 16 * s, y - 4 * s), 7 * s, col)
    p.circle(x - 19 * s, y + 15 * s, 8 * s, INK)
    p.circle(x + 19 * s, y + 15 * s, 8 * s, INK)


CAR_COLS = [CORAL, GOLD, GREEN, "#b388ff", "#ff8fc7", "#ffffff"]


# ------------------------------------------------------------ 1 Einstieg (Hook)
def s1_einstieg(t):
    cv = sky(t)
    p = Pen(cv)
    # Autoberg: 400 Autos (20 x 20), wächst ab dem ersten Bild
    n = int(lerp(160, 400, ease_out(prog(t, 0, 3.2))))
    for i in range(n):
        row, col = divmod(i, 20)
        x = 75 + col * 49 + (row % 2) * 20
        y = 1830 - row * 30
        car_icon(p, x, y, 0.62, CAR_COLS[(i * 7) % len(CAR_COLS)])
    place(cv, text_sprite(f"*{n}* Autos", 76, hl=GOLD), 540, 1830 - ((n - 1) // 20) * 30 - 80)
    bob = 12 * math.sin(t * 2)
    plane(p, 540, 850 + bob, 1.25, rot=-3, t=t)
    if t > 5.2:
        place(cv, text_sprite("?", 220, color="#ffffff"), 900, 700, ease_out_back(prog(t, 5.2, 5.6)))
    cv = punch(cv, t)
    caption(cv, t, -1, 5.2, "So schwer wie *400 Autos* – und es fliegt!", 470, size=86)
    caption(cv, t, 5.2, 9, "*Warum?*", 470, size=120)
    return cv


# ------------------------------------------------------------ Flügel-Profil
def airfoil_pts(cx, cy, chord, aoa, mirror=False, n=40, th=0.13):
    m, pp = 0.05, 0.4
    up, lo = [], []
    for i in range(n + 1):
        x = (1 - math.cos(math.pi * i / n)) / 2
        yt = 5 * th * (0.2969 * math.sqrt(x) - 0.126 * x - 0.3516 * x * x + 0.2843 * x ** 3
                       - 0.1015 * x ** 4)
        yc = m / pp ** 2 * (2 * pp * x - x * x) if x < pp else \
            m / (1 - pp) ** 2 * ((1 - 2 * pp) + 2 * pp * x - x * x)
        up.append((x, yc + yt))
        lo.append((x, yc - yt))
    a = math.radians(aoa)
    out = []
    for x, y in up + lo[::-1]:
        lx, ly = (x - 0.5) * chord, -y * chord
        if mirror:
            lx = -lx
        if mirror:
            rx, ry = lx * math.cos(a) + ly * math.sin(a), -lx * math.sin(a) + ly * math.cos(a)
        else:
            rx, ry = lx * math.cos(a) - ly * math.sin(a), lx * math.sin(a) + ly * math.cos(a)
        out.append((cx + rx, cy + ry))
    return out


WX, WY, CH, AOA = 540, 1080, 560, 8
UPPER = [-340, -250, -175, -110, -62]
LOWER = [72, 135, 205, 285]


def stream_y(x, h):
    """y-Abstand einer Stromlinie (h<0 oben, h>0 unten) an Stelle x (relativ zur Flügelmitte)."""
    near = math.exp(-(x / (CH * 0.55)) ** 2)
    down = 1 / (1 + math.exp(-x / (CH * 0.22)))
    up_before = math.exp(-((x + CH * 0.55) / (CH * 0.35)) ** 2)
    if h < 0:
        d = -75 * near * math.exp(-abs(h) / 230)
    else:
        d = 20 * near * math.exp(-abs(h) / 200)
    d += 120 * down * math.exp(-abs(h) / 380) - 30 * up_before * math.exp(-abs(h) / 300)
    return h + d


def streams(p, t, alpha=1.0, fast_top=True, particles=True, lines=True):
    lc = mix("#5aa6f5", AIR, 0.55 * alpha)
    for h in UPPER + LOWER:
        pts = [(WX + x, WY + stream_y(x, h)) for x in range(-560, 561, 20)]
        if lines:
            p.line(pts, lc, 4, caps=False)
        if particles:
            sp = (640 if (h < 0 and fast_top) else 400)
            for k in range(5):
                x = -560 + ((t * sp + k * 224 + (h * 7) % 224) % 1120)
                y = WY + stream_y(x, h)
                p.circle(WX + x, y, 9, mix("#5aa6f5", "#ffffff", alpha))


def wing(p, col=PLANE):
    p.poly(airfoil_pts(WX, WY, CH, AOA), col)


# ------------------------------------------------------------ 2 Flügel
def s2_fluegel(t):
    cv = sky(t)
    p = Pen(cv)
    if t < 2.3:
        a = prog(2.3 - t, 0, 0.3)
        z = 1.4 + 0.5 * ease_in_out(prog(t, 0.6, 2.3))

        def draw(lp):
            plane(lp, 600 + 120 * (z - 1.4), 1080, z, t=t)
        faded(cv, a, draw)
        if t > 0.5:
            pg = 0.5 + 0.5 * math.sin(t * 7)
            place(cv, glow(170, GOLD, 0.5 * pg * a), 600 - 70 * z + 120 * (z - 1.4), 1080 + 45 * z)
    else:
        k = ease_out_back(prog(t, 2.3, 2.7))
        aoa = AOA * ease_in_out(prog(t, 4.6, 5.6))
        p.poly(airfoil_pts(WX, WY, CH * k, aoa), PLANE)
        if t > 3.2:
            pill(cv, "gewölbt", 540, 880, GOLD, scale=ease_out_back(prog(t, 3.2, 3.55)))
        if t > 5.6:
            g = ease_out(prog(t, 5.6, 6.0))
            x0 = WX - CH / 2 - 40
            p.line([(x0, WY + 40), (WX + CH / 2 + 80, WY + 40)], "#ffffff", 5)
            a = math.radians(AOA)
            p.line([(x0 + 40, WY + 40 - 40 * math.tan(a) + 40),
                    (x0 + 40 + (CH + 60) * g, WY + 40 + (CH + 60) * g * math.tan(a) - 40 * math.tan(a))],
                   CORAL, 6)
            pill(cv, "leicht schräg", 540, 1340, CORAL, scale=ease_out_back(prog(t, 5.8, 6.15)), fg="#ffffff")
    caption(cv, t, 0.2, 2.4, "Das Geheimnis: der *Flügel*", 500, size=96)
    caption(cv, t, 2.4, 10, "Leicht *gewölbt* und etwas *schräg*", 500, size=90)
    return cv


# ------------------------------------------------------------ 3 Hand aus dem Fenster
WIND = [(rng.uniform(0, 1), rng.uniform(820, 1180), rng.uniform(80, 200)) for _ in range(18)]


def s3_hand(t):
    cv = sky(t, speed=3)
    p = Pen(cv)
    for ph, y, ln in WIND:
        x = 1180 - ((t * 1400 + ph * 1400) % 1400)
        p.line([(x, y), (x + ln, y)], "#ffffff", 5)
    tilt = 14 * ease_in_out(prog(t, 2.4, 3.4))
    lift = 110 * ease_in_out(prog(t, 3.8, 5.4))
    hx, hy = 770, 1190 - lift
    wx, wy = hx - 150, hy + 12
    # Auto
    p.rrect((-80, 1420, 1160, 2000), 120, CORAL)
    p.rrect((-60, 1300, 560, 1560), 60, "#d9553a")
    p.rrect((-30, 1330, 520, 1540), 40, "#9fd0ff")
    # Arm + Hand (Seitenansicht, Fingerspitzen zeigen in den Fahrtwind)
    p.line([(300, 1500), (wx, wy)], "#f2b48c", 70)
    p.poly(airfoil_pts(hx, hy, 320, tilt, mirror=True, th=0.26), "#f6c39e")
    p.circle(hx - 40, hy - 4, 34, "#f6c39e")
    if lift > 5:
        big_arrow(p, hx, hy - 80, hx, hy - 80 - 1.6 * lift, GREEN, 30)
    if t > 2.6:
        pill(cv, "leicht kippen", 790, 1680, GOLD, scale=ease_out_back(prog(t, 2.6, 2.95)), size=48)
    caption(cv, t, 0.2, 10, "Hand aus dem Fenster, leicht kippen: *hoch!*", 500, size=86)
    return cv


# ------------------------------------------------------------ 4 Luft nach unten
def s4_ablenken(t):
    cv = sky(t)
    p = Pen(cv)
    streams(p, t, alpha=prog(t, 0.1, 0.6))
    wing(p)
    if t > 1.4:
        g = ease_out(prog(t, 1.4, 2.0))
        for i, x in enumerate((850, 960)):
            big_arrow(p, x, 1180 + 30 * i, x + 20, 1180 + 30 * i + 150 * g, NAVY, 22)
        pill(cv, "Luft nach unten", 860, 1480, "#ffffff", scale=ease_out_back(prog(t, 1.6, 1.95)))
    if t > 3.0:
        g = ease_out_back(prog(t, 3.0, 3.5))
        big_arrow(p, 500, 960, 500, 960 - 230 * g, GREEN, 40)
        pill(cv, "Flügel nach oben", 500, 640, GREEN, scale=g)
    caption(cv, t, 0.2, 10, "Luft nach *unten* – Flügel nach *oben*", 470, size=88)
    return cv


# ------------------------------------------------------------ 5 Unterdruck + Auftrieb
MINUS = [(-200, -150), (-60, -175), (80, -160), (210, -130), (-130, -250), (40, -265)]
PLUS = [(-170, 120), (-30, 130), (110, 140), (240, 150)]


def chip(p, cv, x, y, sign, col, k):
    if k <= 0:
        return
    p.circle(x, y, 34 * k, col)
    place(cv, text_sprite(sign, 58, color="#ffffff", stroke=0, weight="black"), x, y - 4 * k, k)


def s5_auftrieb(t):
    cv = sky(t)
    p = Pen(cv)
    streams(p, t, alpha=1.0)
    wing(p)
    if 0.8 < t < 3.2:
        pill(cv, "oben schneller", 540, 740, "#ffffff", prog(3.2 - t, 0, 0.2),
             ease_out_back(prog(t, 0.8, 1.15)))
    for i, (dx, dy) in enumerate(MINUS):
        chip(p, cv, WX + dx, WY + dy, "–", NAVY, ease_out_back(prog(t, 3.4 + i * 0.12, 3.8 + i * 0.12)))
    if t > 4.3:
        pill(cv, "Unterdruck", 540, 690, NAVY, scale=ease_out_back(prog(t, 4.3, 4.65)), fg="#ffffff")
    for i, (dx, dy) in enumerate(PLUS):
        chip(p, cv, WX + dx, WY + dy, "+", CORAL, ease_out_back(prog(t, 7.4 + i * 0.12, 7.8 + i * 0.12)))
    if t > 8.4:
        g = ease_out_back(prog(t, 8.4, 9.0))
        place(cv, glow(200, GREEN, 0.5 * g), WX, WY - 120)
        big_arrow(p, WX, WY - 60, WX, WY - 60 - 330 * g, GREEN, 54)
        place(cv, text_sprite("*AUFTRIEB*", 92, hl=GREEN), WX, WY + 380, g)
    caption(cv, t, 0.2, 3.2, "Oben strömt die Luft *schneller*", 500, size=90)
    caption(cv, t, 3.2, 7.2, "Dort entsteht *Unterdruck* – er zieht nach oben", 500, size=84)
    caption(cv, t, 7.2, 13, "Unten drücken, oben ziehen = *Auftrieb*", 500, size=86)
    return cv


# ------------------------------------------------------------ 6 Geschwindigkeit
def gauge(p, cv, x, y, r, v, vmax=350):
    p.circle(x, y, r, "#13285c", "#ffffff", 8)
    for i in range(8):
        a = math.radians(150 + 240 * i / 7)
        p.line([(x + math.cos(a) * r * 0.78, y + math.sin(a) * r * 0.78),
                (x + math.cos(a) * r * 0.92, y + math.sin(a) * r * 0.92)], "#ffffff", 6)
    a = math.radians(150 + 240 * min(v, vmax) / vmax)
    p.line([(x, y), (x + math.cos(a) * r * 0.75, y + math.sin(a) * r * 0.75)], CORAL, 10)
    p.circle(x, y, 14, "#ffffff")
    place(cv, text_sprite(f"*{int(v)}*", 64, hl=GOLD), x, y + r * 0.45)
    place(cv, text_sprite("km/h", 30, weight="bold", stroke=0), x, y + r * 0.72)


def s6_tempo(t):
    cv = sky(t, speed=1 + 2 * prog(t, 0.5, 6))
    p = Pen(cv)
    v = 290 * ease_in_out(prog(t, 0.4, 6.4))
    # Startbahn
    p.poly([(0, 1560), (1080, 1560), (1080, 1920), (0, 1920)], "#5b6475")
    p.line([(0, 1560), (1080, 1560)], "#ffffff", 6, caps=False)
    off = (t * v * 4) % 220
    for i in range(7):
        x = 1100 - ((i * 220 + off) % 1320)
        p.rrect((x, 1730, x + 120, 1750), 6, "#ffffff")
    up = ease_in_out(prog(t, 6.6, 8.0))
    px, py = 470, 1470 - 380 * up
    rot = -10 * prog(t, 6.3, 6.8) + 2 * up
    plane(p, px, py, 0.95, rot=rot, t=t)
    # Auftriebspfeil wächst mit dem Tempo (∝ v²)
    L = 260 * (v / 290) ** 2
    if L > 12:
        big_arrow(p, px - 30, py - 70, px - 30, py - 70 - L, GREEN, 30)
    gauge(p, cv, 800, 920, 175, v)
    if up > 0.5:
        pill(cv, "abheben!", 470, py + 160, GOLD, scale=ease_out_back(prog(t, 7.4, 7.75)))
    caption(cv, t, 0.2, 3.0, "Je *schneller*, desto *stärker*", 500, size=92)
    caption(cv, t, 3.0, 10, "Zum Abheben: fast *300 km/h*", 500, size=92)
    return cv


# ------------------------------------------------------------ 7 Triebwerke + Gleiten
def s7_gleiten(t):
    if t < 5.2:
        cv = sky(t)
        p = Pen(cv)
        a = prog(5.2 - t, 0, 0.25)

        def draw(lp):
            plane(lp, 600, 1120, 1.45, t=t)
        faded(cv, a, draw)
        ex, ey = 600 + 30 * 1.45, 1120 + 60 * 1.45
        if t > 1.0:
            g = ease_out(prog(t, 1.0, 1.5))
            big_arrow(p, ex, ey - 120, ex, ey - 120 - 220 * g, "#ffffff", 30)
            if t > 1.7:
                k = ease_out_back(prog(t, 1.7, 2.0))
                cx, cy = ex, ey - 230
                p.line([(cx - 70 * k, cy - 70 * k), (cx + 70 * k, cy + 70 * k)], CORAL, 24)
                p.line([(cx - 70 * k, cy + 70 * k), (cx + 70 * k, cy - 70 * k)], CORAL, 24)
        if t > 2.8:
            g = ease_out_back(prog(t, 2.8, 3.3))
            big_arrow(p, 420, ey + 150, 420 + 320 * g, ey + 150, GREEN, 34)
            pill(cv, "nur nach vorne", 640, 1520, GREEN, scale=g)
        caption(cv, t, 0.2, 5.2, "Triebwerke schieben nur nach *vorne*", 500, size=88)
        return cv
    tt = t - 5.2
    cv = sky(t, stops=((0, "#16407f"), (0.6, "#3f86d6"), (1, "#9fd0ff")))
    p = Pen(cv)
    x0, y0, x1, y1 = 170, 760, 960, 1560
    p.poly([(0, y1), (1080, y1), (1080, 1920), (0, 1920)], "#2f6b3f")
    u = ease_in_out(prog(tt, 0.4, 5.6))
    # Gleitlinie (gestrichelt)
    for i in range(24):
        a, b = i / 24, (i + 0.55) / 24
        if a < u:
            b = min(b, u)
            p.line([(lerp(x0, x1, a), lerp(y0, y1, a)), (lerp(x0, x1, b), lerp(y0, y1, b))],
                   "#ffffff", 7)
    ang = math.degrees(math.atan2(y1 - y0, x1 - x0)) * 0.35
    plane(p, lerp(x0, x1, u), lerp(y0, y1, u) - 40, 0.42, rot=ang, engine=False)
    k = ease_out(prog(tt, 0.6, 1.2))
    if k > 0:
        p.line([(60, y0), (60, y0 + (y1 - y0) * k)], GOLD, 8)
        place(cv, text_sprite("10 km", 56, color=GOLD, stroke=6), 175, y0 + 520, alpha=k)
    k2 = ease_out(prog(tt, 2.0, 3.0))
    if k2 > 0:
        p.line([(x0, y1 + 70), (x0 + (x1 - x0) * k2, y1 + 70)], GOLD, 8)
        place(cv, text_sprite("*über 100 km*", 62, hl=GOLD), 560, y1 + 150, ease_out_back(k2))
    pill(cv, "Triebwerke aus", 760, 820, "#ffffff", scale=ease_out_back(prog(tt, 0.2, 0.55)))
    caption(cv, t, 5.2, 13, "Ohne Triebwerke: über *100 km* gleiten", 500, size=88)
    return cv


# ------------------------------------------------------------ 8 Ende
def s8_ende(t):
    cv = sky(t, stops=SUNSET, col="#ffd9b0")
    p = Pen(cv)
    place(cv, glow(320, "#fff1c9", 0.7), 760, 1500)
    p.circle(760, 1500, 120, "#ffe39a")
    plane(p, lerp(-200, 1300, t / 5), 1330 - 60 * t / 5, 0.5, rot=-4, t=t)
    caption(cv, t, 0.1, 9, "Hättest du's *gewusst*?", 760, size=110)
    caption(cv, t, 1.6, 9, "Folge für mehr *Warum eigentlich?*", 1010, size=66)
    return cv


VIDEO = Video([
    (7.0, s1_einstieg, [(0.0, "Du sitzt in einem Flugzeug, das so viel wiegt wie 400 Autos – und es fällt einfach nicht runter."),
                        (5.2, "Warum?")]),
    (7.5, s2_fluegel, [(0.2, "Das Geheimnis steckt im Flügel."),
                       (2.4, "Er ist leicht gewölbt und ein bisschen schräg nach oben gestellt.")]),
    (7.5, s3_hand, [(0.2, "Das kennst du: Halt als Beifahrer die Hand aus dem Fenster und kipp sie leicht – schon wird sie nach oben gedrückt.")]),
    (6.0, s4_ablenken, [(0.2, "Genau so lenkt der Flügel die Luft nach unten ab – und wird dabei selbst nach oben gedrückt.")]),
    (11.5, s5_auftrieb, [(0.2, "Gleichzeitig strömt die Luft über dem Flügel schneller."),
                         (3.2, "Dort entsteht Unterdruck, der den Flügel nach oben zieht."),
                         (7.2, "Unten drücken, oben ziehen – das nennt man Auftrieb.")]),
    (8.5, s6_tempo, [(0.2, "Und je schneller das Flugzeug, desto stärker."),
                     (3.0, "Darum braucht ein großer Jet zum Abheben fast 300 Kilometer pro Stunde.")]),
    (11.5, s7_gleiten, [(0.2, "Die Triebwerke heben das Flugzeug übrigens gar nicht hoch – sie schieben es nur nach vorne."),
                        (5.2, "Fallen sie aus, kann ein Jet aus zehn Kilometern Höhe noch über hundert Kilometer weit gleiten.")]),
    (4.2, s8_ende, [(0.2, "Hättest du es gewusst?"),
                    (1.7, "Folge für mehr: Warum eigentlich?")]),
])

if __name__ == "__main__":
    cli(VIDEO, __file__, cover_t=1.6)
