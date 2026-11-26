"""Folge 9: Warum frieren Fische im Winter nicht ein?  (9:16, Kurzformat ~35 s)

Rendern:   python3 videos/09_fische.py            (ElevenLabs, Stimme Brian, 12 % schneller)
Vorschau:  python3 videos/09_fische.py --stills
"""
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image  # noqa: E402

from ev import tts  # noqa: E402
from ev.engine import (S, Pen, Video, canvas, caption, cli, ease_in_out, ease_out,  # noqa: E402
                       ease_out_back, glow, layer, lerp, mix, place, prog, text_sprite)

tts.TEMPO = 1.12

WINTER = ((0, "#9fb8d6"), (0.5, "#c9dbee"), (1, "#e8f1fa"))
UNDER = ((0, "#3d8fd6"), (0.45, "#1f5fa8"), (1, "#0b2a5c"))
POLAR = ((0, "#1a4f8a"), (0.5, "#0e2f63"), (1, "#061a3d"))
ICE = "#e6f4ff"
ICE_EDGE = "#b8dcf5"
WATER = "#2a74c4"
WATER_COLD = "#9fd6ff"
GROUND = "#5b4a3a"
FISH = "#FF8A3D"
GOLD = "#FFD23F"
RED = "#ff5a4a"
INK = "#0b1f3d"

rng = random.Random(9)
SNOW = [(rng.uniform(0, 1080), rng.uniform(0, 1), rng.uniform(4, 10), rng.uniform(0, 6.3)) for _ in range(70)]
BUBBLES = [(rng.uniform(100, 980), rng.uniform(0, 1), rng.uniform(5, 12)) for _ in range(26)]


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


def cam(cv, t, z0=1.0, zoom_dur=0.7, shake_at=None, shake_dur=0.8, amp=16):
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


def snow(p, t, col="#ffffff", speed=160, drift=1.0, ymax=1920):
    for x, ph, r, w in SNOW:
        y = (ph * 1920 + t * speed) % 1920
        if y > ymax:
            continue
        p.circle(x + 30 * math.sin(t * 1.3 + w) * drift, y, r, col)


def fish(p, x, y, s=1.0, col=FISH, t=0.0, flip=False, fins=True):
    d = -1 if flip else 1
    wag = math.sin(t * 8) * 14 * s
    p.poly([(x - d * 70 * s, y), (x - d * 125 * s, y - 42 * s + wag), (x - d * 125 * s, y + 42 * s + wag)],
           mix(col, "#000000", 0.12))
    p.ellipse((x - 95 * s, y - 45 * s, x + 95 * s, y + 45 * s), col)
    if fins:
        p.poly([(x - d * 10 * s, y - 40 * s), (x + d * 30 * s, y - 70 * s), (x + d * 45 * s, y - 38 * s)],
               mix(col, "#000000", 0.12))
    p.circle(x + d * 55 * s, y - 10 * s, 11 * s, "#ffffff")
    p.circle(x + d * 58 * s, y - 10 * s, 6 * s, INK)
    p.line([(x + d * 20 * s, y - 30 * s), (x + d * 10 * s, y + 30 * s)], mix(col, "#ffffff", 0.35), 6 * s)


def ice_top(cv, t, dy=0.0):
    """Eisfläche von oben (für Anfang und Ende)."""
    p = Pen(cv)
    p.rrect((-20, -20 - dy, 1100, 1940 - dy), 0, "#d6ecfb")
    for i, (x0, y0, x1, y1) in enumerate(((120, 700, 420, 980), (420, 980, 380, 1300), (420, 980, 760, 1120),
                                          (760, 1120, 980, 1060), (760, 1120, 820, 1520), (300, 1500, 600, 1700))):
        p.line([(x0, y0 - dy), (x1, y1 - dy)], "#a9cbe6", 5)
    for x, y, r in ((200, 1250, 120), (850, 800, 150), (560, 1500, 90)):
        p.ellipse((x - r, y - r * 0.45 - dy, x + r, y + r * 0.45 - dy), "#f4faff")
    # dunkler Fisch-Schatten unter dem Eis
    sx = 540 + 160 * math.sin(t * 1.4)
    p.ellipse((sx - 80, 1180 - 26 - dy, sx + 80, 1180 + 26 - dy), "#bcd3e6")
    snow(p, t, "#ffffff", 220)


def underwater(cv, t):
    def rays(lp):
        for i in range(5):
            x = 150 + i * 200 + 40 * math.sin(t + i)
            lp.poly([(x - 30, 0), (x + 30, 0), (x + 160, 1920), (x + 60, 1920)], "#ffffff")
    faded(cv, 0.07, rays)
    p = Pen(cv)
    p.poly([(0, 0), (1080, 0), (1080, 640), (0, 640)], ICE)
    p.poly([(0, 640)] + [(x, 640 + 18 * math.sin(x / 70)) for x in range(0, 1101, 40)] + [(1080, 600)], ICE_EDGE)
    for x, ph, r in BUBBLES:
        y = 1900 - ((ph * 1260 + t * 120) % 1260)
        p.circle(x + 10 * math.sin(t * 3 + ph * 9), y, r, None, "#cfe8ff", 3)


# ------------------------------------------------------------ 1 Einstieg (Hook)
def s1_einstieg(t):
    cv = canvas(UNDER)
    underwater(cv, t)
    p = Pen(cv)
    fish(p, 540 + 200 * math.sin(t * 0.9), 1180, 1.6, t=t, flip=math.cos(t * 0.9) < 0)
    fish(p, 260 + 60 * math.sin(t * 1.3), 1520, 0.8, col="#ffb347", t=t + 1)
    dive = ease_in_out(prog(t, 1.1, 1.9))
    if dive < 1:
        lay = Image.new("RGBA", cv.size, (0, 0, 0, 0))
        ice_top(lay, t, dy=1920 * dive)
        cv.alpha_composite(lay)
    cv = cam(cv, t, z0=1.12, shake_at=1.0, shake_dur=0.7, amp=16)
    caption(cv, t, -1, 9, "Warum frieren Fische *nicht ein*?", 470, size=96)
    return cv


# ------------------------------------------------------------ 2 Waage
def drop(p, x, y, s, col):
    p.circle(x, y + 20 * s, 48 * s, col)
    p.poly([(x - 40 * s, y - 2 * s), (x, y - 80 * s), (x + 40 * s, y - 2 * s)], col)


def s2_waage(t):
    cv = canvas(WINTER)
    p = Pen(cv)
    ang = math.radians(-12 * ease_out_back(prog(t, 0.8, 1.6)))
    cx, cy, L = 540, 1080, 330
    p.poly([(cx - 30, cy + 10), (cx + 30, cy + 10), (cx + 80, 1500), (cx - 80, 1500)], "#5b6b8a")
    p.rrect((cx - 200, 1500, cx + 200, 1540), 12, "#5b6b8a")
    lx, ly = cx - L * math.cos(ang), cy - L * math.sin(ang)
    rx, ry = cx + L * math.cos(ang), cy + L * math.sin(ang)
    p.line([(lx, ly), (rx, ry)], "#3c4560", 18)
    p.circle(cx, cy, 22, GOLD)
    for x, y, col, lab in ((lx, ly, WATER, "4 °C"), (rx, ry, WATER_COLD, "0 °C")):
        p.line([(x, y), (x, y + 150)], "#3c4560", 6)
        p.rrect((x - 120, y + 150, x + 120, y + 170), 10, "#3c4560")
        drop(p, x, y + 60, 0.95, col)
        place(cv, text_sprite(lab, 46, weight="bold", stroke=0, color=INK), x, y + 230)
    if t > 1.4:
        pill(cv, "am schwersten", lx, ly + 330, GOLD, scale=ease_out_back(prog(t, 1.4, 1.75)), size=46)
    caption(cv, t, 0.2, 9, "Wasser ist bei *4 °C* am schwersten", 470, size=90)
    return cv


# ------------------------------------------------------------ See im Querschnitt
SURF = 760
BASIN = [(110, SURF), (230, 1420), (540, 1600), (850, 1420), (970, SURF)]


def basin_x(y):
    """linker/rechter Rand des Sees in Höhe y."""
    u = (y - SURF) / (1420 - SURF)
    return lerp(110, 230, max(0, min(1, u))), lerp(970, 850, max(0, min(1, u)))


def lake(cv, t, col=WATER, ice=0.0, sky=WINTER, storm=False):
    p = Pen(cv)
    p.poly([(0, SURF), (110, SURF), (230, 1420), (540, 1600), (850, 1420), (970, SURF), (1080, SURF),
            (1080, 1920), (0, 1920)], GROUND)
    p.poly([(0, SURF - 10), (110, SURF - 10), (110, SURF + 4), (0, SURF + 4)], "#f4faff")
    p.poly([(970, SURF - 10), (1080, SURF - 10), (1080, SURF + 4), (970, SURF + 4)], "#f4faff")
    p.poly(BASIN, col)
    if ice > 0:
        th = 70 * ice
        l0, r0 = basin_x(SURF)
        l1, r1 = basin_x(SURF + th)
        p.poly([(l0, SURF - 8), (r0, SURF - 8), (r1, SURF + th), (l1, SURF + th)], ICE)
        p.line([(l1, SURF + th), (r1, SURF + th)], ICE_EDGE, 6)


def temp_tag(cv, text, x, y, col, k=1.0):
    pill(cv, text, x, y, col, scale=k, size=44, fg=INK)


def s3_sinken(t):
    cv = canvas(WINTER)
    lake(cv, t)
    p = Pen(cv)
    for i in range(12):
        t0 = 0.3 + i * 0.28
        u = prog(t, t0, t0 + 1.6)
        if u <= 0:
            continue
        x = 260 + (i * 97) % 560
        y = lerp(SURF + 30, 1380 - (abs(x - 540) * 0.4), ease_in_out(u))
        p.circle(x, y, 26, mix(WATER_COLD, WATER, u * 0.7))
        if u < 1:
            p.arrow(x, y + 36, x, y + 90, "#ffffff", 7, 20)
    snow(p, t, "#ffffff", 200, ymax=SURF - 20)
    temp_tag(cv, "oben kälter", 780, 680, WATER_COLD, ease_out_back(prog(t, 0.4, 0.75)))
    caption(cv, t, 0.2, 9, "Kaltes Wasser *sinkt nach unten*", 470, size=92)
    return cv


def s4_zufrieren(t):
    cv = canvas(WINTER)
    ice = ease_in_out(prog(t, 1.6, 3.6))
    lake(cv, t, col=mix(WATER, "#2f7fd0", 0.5), ice=ice)
    p = Pen(cv)
    snow(p, t, "#ffffff", 200, ymax=SURF - 20)
    for i, (x, y) in enumerate(((380, 1000), (680, 1050), (540, 1300))):
        k = ease_out_back(prog(t, 0.3 + i * 0.2, 0.65 + i * 0.2))
        if k > 0:
            place(cv, text_sprite("4 °C", 54, color="#ffffff"), x, y, k)
    if ice > 0.3:
        pill(cv, "Eis", 540, SURF - 70, ICE, scale=ease_out_back(prog(t, 2.2, 2.55)), size=48)
    caption(cv, t, 0.2, 9, "Alles *4 °C* – dann friert es *oben* zu", 470, size=88)
    return cv


# ------------------------------------------------------------ 5 Eis schwimmt
def s5_glas(t):
    cv = canvas(WINTER)
    p = Pen(cv)
    gx, gy, gw, gh = 540, 1250, 300, 520
    wl = gy - gh / 2 + 140
    p.rrect((gx - gw / 2 - 12, gy - gh / 2, gx + gw / 2 + 12, gy + gh / 2 + 12), 30, "#ffffff")
    p.rrect((gx - gw / 2, gy - gh / 2 - 10, gx + gw / 2, gy + gh / 2), 24, "#eef6fd")
    p.rrect((gx - gw / 2, wl, gx + gw / 2, gy + gh / 2), 24, "#6fb3ef")
    p.rrect((gx - gw / 2, wl, gx + gw / 2, wl + 30), 6, "#6fb3ef")
    u = prog(t, 0.3, 1.0)
    bob = 18 * math.exp(-max(0, t - 1.0) * 2.5) * math.sin((t - 1.0) * 10) if t > 1.0 else 0
    iy = lerp(gy - gh / 2 - 300, wl + 40, ease_in_out(u) if u < 1 else 1) + bob
    rot = 15 * (1 - u)
    s = 110
    pts = [(-s / 2, -s / 2), (s / 2, -s / 2), (s / 2, s / 2), (-s / 2, s / 2)]
    a = math.radians(rot)
    p.poly([(gx + x * math.cos(a) - y * math.sin(a), iy + x * math.sin(a) + y * math.cos(a)) for x, y in pts],
           "#f4fbff", ICE_EDGE, 6)
    if t > 1.4:
        pill(cv, "Eis schwimmt oben", gx, gy + gh / 2 + 110, ICE, scale=ease_out_back(prog(t, 1.4, 1.75)), size=46)
        pill(cv, "ca. 9 % leichter", gx + 290, wl - 120, GOLD, scale=ease_out_back(prog(t, 1.9, 2.25)))
    caption(cv, t, 0.2, 9, "Eis ist *leichter* – es schwimmt wie ein *Deckel*", 470, size=86)
    return cv


# ------------------------------------------------------------ 6 Deckel hält warm
def s6_deckel(t):
    cv = canvas(((0, "#6f86a6"), (0.5, "#9fb3cc"), (1, "#c9d6e6")))
    lake(cv, t, col=WATER, ice=1.0)
    p = Pen(cv)
    for x, ph, r, w in SNOW:
        y = (ph * 700 + t * 300) % 700
        p.line([(x + 200 * (y / 700) - 100, y + 40), (x + 200 * (y / 700) - 60, y + 50)], "#ffffff", 5)
    fish(p, 540 + 120 * math.sin(t * 0.7), 1300, 0.9, t=t, flip=math.cos(t * 0.7) < 0)
    temp_tag(cv, "–15 °C", 820, 660, "#ffffff", ease_out_back(prog(t, 0.4, 0.75)))
    temp_tag(cv, "4 °C am Grund", 540, 1490, GOLD, ease_out_back(prog(t, 1.8, 2.15)))
    caption(cv, t, 0.2, 9, "Der Deckel hält die *Kälte draußen*", 470, size=92)
    return cv


# ------------------------------------------------------------ 7 Winterruhe
def s7_ruhe(t):
    cv = canvas(UNDER)
    underwater(cv, t)
    p = Pen(cv)
    p.poly([(0, 1580)] + [(x, 1580 + 20 * math.sin(x / 90)) for x in range(0, 1101, 40)] + [(1080, 1920), (0, 1920)],
           "#3b3326")
    for i, (x, s) in enumerate(((330, 1.0), (700, 0.85))):
        fish(p, x, 1500 - 10 * i + 4 * math.sin(t * 0.8 + i), s, t=t * 0.15, flip=i == 1)
    # Herzschlag wird langsamer
    k = prog(t, 0.5, 4.0)
    rate = lerp(5, 1.2, k)
    pts = []
    for i in range(121):
        x = 140 + i * 6.7
        ph = (x / 120 - t * rate * 0.6) % 1.0
        y = 960 - (90 * math.exp(-((ph - 0.5) / 0.04) ** 2) * (1 - 0.5 * k))
        pts.append((x, y))
    p.rrect((110, 860, 970, 1060), 30, "#0b2a5c")
    p.line(pts, "#ff6b8a", 8)
    place(cv, text_sprite("Puls", 40, weight="bold", stroke=0, color="#ff9fb3"), 210, 900)
    for i in range(3):
        kk = (t * 0.5 + i / 3) % 1.0
        place(cv, text_sprite("Z", int(50 + 30 * kk), color="#ffffff", stroke=0), 420 + 70 * kk, 1380 - 160 * kk,
              alpha=math.sin(kk * math.pi))
    pill(cv, "Energiesparmodus", 540, 1700, GOLD, scale=ease_out_back(prog(t, 1.2, 1.55)), size=46)
    caption(cv, t, 0.2, 9, "Fische fahren den Körper *runter*", 470, size=92)
    return cv


# ------------------------------------------------------------ 8 Antarktis
def s8_antarktis(t):
    cv = canvas(POLAR)
    p = Pen(cv)
    p.poly([(0, 0), (1080, 0), (1080, 620), (0, 620)], "#dff1ff")
    for x, w, h in ((80, 260, 260), (520, 340, 380), (880, 220, 200)):
        p.poly([(x, 620), (x + w * 0.2, 620 + h), (x + w * 0.7, 620 + h * 0.8), (x + w, 620)], "#bfe2fb")
    for x, ph, r in BUBBLES:
        y = 1900 - ((ph * 1200 + t * 90) % 1200)
        p.circle(x, y, r * 0.8, None, "#7fb8e6", 3)
    fx, fy = 540 + 80 * math.sin(t * 0.8), 1220
    place(cv, glow(320, "#9fe8ff", 0.25), fx, fy)
    fish(p, fx, fy, 2.0, col="#dbeef7", t=t, fins=True)
    for i in range(18):
        a = i * 2.4 + t * 1.5
        x = fx + 120 * math.cos(a) * (0.4 + 0.6 * ((i * 37) % 10) / 10)
        y = fy + 50 * math.sin(a * 1.3) * 0.8
        place(cv, glow(18, "#5fe0ff", 0.9), x, y)
        p.circle(x, y, 6, "#5fe0ff")
    temp_tag(cv, "–1,9 °C", 820, 760, "#ffffff", ease_out_back(prog(t, 0.4, 0.75)))
    pill(cv, "Frostschutz im Blut", 540, 1520, "#5fe0ff", scale=ease_out_back(prog(t, 1.4, 1.75)), size=48)
    caption(cv, t, 0.2, 9, "*Antarktis*: Frostschutz im Blut!", 470, size=92)
    return cv


# ------------------------------------------------------------ 9 Ende (Loop)
def s9_ende(t):
    cv = canvas(UNDER)
    lay = Image.new("RGBA", cv.size, (0, 0, 0, 0))
    ice_top(lay, t + 1.0)
    cv.alpha_composite(lay)
    caption(cv, t, 0.1, 9, "Hättest du's *gewusst*?", 430, size=100)
    caption(cv, t, 1.4, 9, "Folge für mehr *Warum eigentlich?*", 660, size=62)
    return cv


VIDEO = Video([
    (3.0, s1_einstieg, [(0.0, "Der See ist zugefroren. Warum frieren die Fische nicht ein?")]),
    (3.5, s2_waage, [(0.2, "Das Geheimnis: Wasser ist bei vier Grad am schwersten.")]),
    (4.0, s3_sinken, [(0.2, "Im Herbst kühlt es oben ab, wird schwer und sinkt nach unten.")]),
    (4.5, s4_zufrieren, [(0.2, "Erst wenn der ganze See vier Grad hat, friert die Oberfläche zu.")]),
    (4.5, s5_glas, [(0.2, "Und Eis ist leichter als Wasser – es schwimmt oben wie ein Deckel.")]),
    (4.5, s6_deckel, [(0.2, "Der Deckel hält die Kälte draußen. Am Grund bleibt es bei etwa vier Grad.")]),
    (5.0, s7_ruhe, [(0.2, "Die Fische fahren ihren Körper runter, bewegen sich kaum und brauchen fast kein Futter.")]),
    (4.5, s8_antarktis, [(0.2, "Und in der Antarktis haben manche Fische sogar Frostschutzmittel im Blut.")]),
    (3.0, s9_ende, [(0.2, "Hättest du es gewusst?"),
                    (1.5, "Folge für mehr: Warum eigentlich?")]),
])

if __name__ == "__main__":
    cli(VIDEO, __file__, cover_t=2.2)
