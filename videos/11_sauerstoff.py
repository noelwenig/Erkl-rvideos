"""Folge 11: Was wäre, wenn 5 Sekunden lang kein Sauerstoff auf der Erde wäre?  (9:16, Kurzformat ~40 s)

Rendern:   python3 videos/11_sauerstoff.py            (ElevenLabs, Stimme Brian, 12 % schneller)
Vorschau:  python3 videos/11_sauerstoff.py --stills

Hook: roter Countdown + Alarmlicht ab Bild 1, nach 0,5 s gehen alle Flammen mit „PLOPP“ aus (Wackeln).
Zwei Stufen: erst nur O₂ aus der Luft, dann jedes Sauerstoff-Atom (Glitch + Warnschild).
"""
import math
import os
import random
import sys
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

from ev import tts  # noqa: E402
from ev.engine import (H, S, W, Pen, Video, canvas, caption, cli, ease_in_out, ease_out,  # noqa: E402
                       ease_out_back, glow, layer, lerp, mix, place, prog, text_sprite)

tts.TEMPO = 1.12

NIGHT = ((0, "#0a0f24"), (0.55, "#141a3a"), (1, "#1d1630"))
ALARM = ((0, "#2a0608"), (0.55, "#4a0c10"), (1, "#22050a"))
DAY = ((0, "#5aa6f5"), (0.6, "#9fd0ff"), (1, "#dff0ff"))
SEA = ((0, "#6fb3ff"), (0.45, "#a9d6ff"), (1, "#dff0ff"))
RED = "#ff3b3b"
ORANGE = "#FF9F43"
GOLD = "#FFD23F"
SKIN = "#f6c9a8"
INK = "#120a1e"

rng = random.Random(11)


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


def cam(cv, t, z0=1.0, zoom_dur=0.7, shake_at=None, shake_dur=0.7, amp=18):
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


@lru_cache(None)
def vignette_img():
    yy, xx = np.mgrid[0:H * S:4, 0:W * S:4]
    d = np.sqrt(((xx / (W * S)) - 0.5) ** 2 * 1.6 + ((yy / (H * S)) - 0.5) ** 2)
    a = np.clip((d - 0.38) / 0.3, 0, 1) ** 1.6 * 255
    arr = np.zeros(a.shape + (4,), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = 255, 30, 30
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr, "RGBA").resize((W * S, H * S), Image.BILINEAR)


def vignette(cv, strength):
    if strength <= 0.02:
        return
    v = vignette_img()
    if strength < 0.999:
        v = v.copy()
        v.putalpha(v.getchannel("A").point(lambda x: int(x * strength)))
    cv.alpha_composite(v)


def glitch(cv, t, amount):
    """Horizontale Bildstreifen verschieben (Störung)."""
    if amount <= 0.02:
        return cv
    out = cv.copy()
    r = random.Random(int(t * 30))
    for _ in range(int(10 * amount) + 2):
        y = r.randint(0, H * S - 60)
        h = r.randint(10, 90) * S // 2
        dx = int(r.uniform(-60, 60) * amount * S)
        band = cv.crop((0, y, W * S, min(H * S, y + h)))
        out.paste(band, (dx, y))
    return out


# ------------------------------------------------------------ Kerzen / Flammen
CANDLES = [(250, 1560, 1.0), (540, 1520, 1.25), (830, 1560, 1.0)]
SMOKE = [(rng.uniform(-1, 1), rng.uniform(0, 1)) for _ in range(10)]


def candle(p, cv, x, y, s, t, lit=True, off_t=0.0):
    p.rrect((x - 45 * s, y - 160 * s, x + 45 * s, y + 120 * s), 14 * s, "#f3ead8")
    p.rrect((x - 45 * s, y - 160 * s, x + 45 * s, y - 130 * s), 14 * s, "#ffffff")
    p.line([(x, y - 160 * s), (x, y - 190 * s)], "#2a2a2a", 5 * s)
    if lit:
        f = 1 + 0.08 * math.sin(t * 23 + x)
        place(cv, glow(140 * s, "#ffb347", 0.55), x, y - 230 * s)
        p.ellipse((x - 24 * s, y - 290 * s * f, x + 24 * s, y - 185 * s), ORANGE)
        p.ellipse((x - 12 * s, y - 250 * s * f, x + 12 * s, y - 190 * s), "#fff1a8")
    else:
        for dx, ph in SMOKE:
            u = ((t - off_t) * 0.6 + ph) % 1.0
            p.circle(x + dx * 30 * s + 25 * math.sin(u * 8 + ph * 5) * s, y - 200 * s - 360 * u * s,
                     (8 + 16 * u) * s, mix("#3a3550", "#8a8aa0", 1 - u))


def beacon(cv, x, y, t):
    p = Pen(cv)
    a = t * 6
    for k in (0, math.pi):
        aa = a + k
        pts = [(x, y), (x + 900 * math.cos(aa - 0.18), y + 900 * math.sin(aa - 0.18)),
               (x + 900 * math.cos(aa + 0.18), y + 900 * math.sin(aa + 0.18))]
        faded(cv, 0.16, lambda lp, pts=pts: lp.poly(pts, RED))
    place(cv, glow(110, RED, 0.9), x, y)
    p.rrect((x - 40, y - 30, x + 40, y + 40), 16, "#ff4d4d")
    p.rrect((x - 55, y + 30, x + 55, y + 55), 8, "#555a6a")


def countdown(cv, t, x=540, y=930, start=5, step=1.0):
    n = max(1, start - int(t / step))
    ph = (t / step) % 1.0
    k = 1.0 + 0.25 * max(0, 1 - ph * 5)
    place(cv, glow(230, RED, 0.45), x, y)
    place(cv, text_sprite(str(n), 300, color=RED, stroke=10, stroke_color="#ffffff"), x, y, k)


# ------------------------------------------------------------ 1 Einstieg (Hook)
def s1_einstieg(t):
    cv = canvas(NIGHT)
    off = 0.5
    beacon(cv, 120, 760, t)
    beacon(cv, 960, 760, t + 0.5)
    p = Pen(cv)
    p.poly([(0, 1690), (1080, 1690), (1080, 1920), (0, 1920)], "#2a2236")
    for x, y, s in CANDLES:
        candle(p, cv, x, y, s, t, lit=t < off, off_t=off)
    countdown(cv, t, step=1.1)
    if t > off:
        k = ease_out_back(prog(t, off, off + 0.25))
        place(cv, text_sprite("PLOPP!", 110, color="#ffffff"), 540, 1180, k, 1 - prog(t, off + 1.0, off + 1.4))
    vignette(cv, 0.4 + 0.25 * math.sin(t * 7))
    cv = cam(cv, t, z0=1.12, shake_at=off, shake_dur=0.7)
    caption(cv, t, -1, 9, "*5 Sekunden* ohne Sauerstoff!", 470, size=100)
    return cv


# ------------------------------------------------------------ 2 Ohren knallen
def s2_ohren(t):
    cv = canvas(DAY)
    p = Pen(cv)
    p.poly([(0, 1500), (220, 1050), (420, 1300), (640, 900), (880, 1250), (1080, 1000), (1080, 1920), (0, 1920)],
           "#7c8fb0")
    p.poly([(560, 1010), (640, 900), (720, 1010)], "#ffffff")
    # Kopf im Profil
    hx, hy = 400, 1300
    p.circle(hx, hy, 210, SKIN)
    p.d.pieslice([(hx - 230) * S, (hy - 230) * S, (hx + 230) * S, (hy + 230) * S], 180, 320,
                 fill=(70, 45, 35, 255))
    p.circle(hx, hy + 10, 200, SKIN)
    p.ellipse((hx - 40, hy - 50, hx + 40, hy + 70), "#e9a988")
    p.ellipse((hx - 18, hy - 20, hx + 18, hy + 40), "#c98a74")
    p.circle(hx + 150, hy - 60, 14, INK)
    k = prog(t, 0.4, 1.4)
    if k > 0:
        for i in range(3):
            r = 60 + 160 * prog(k, i * 0.2, 1)
            a = 1 - prog(k, i * 0.2, 1)
            if a > 0:
                p.circle(hx, hy + 10, r, None, mix("#9fd0ff", "#ffffff", a), int(8 * a) + 1)
        place(cv, text_sprite("PLOPP!", 90, color="#ffffff"), hx - 60, hy - 300, ease_out_back(prog(t, 0.4, 0.7)))
    # Höhenmesser
    m = 2000 * ease_out(prog(t, 1.2, 2.6))
    x0, y0, y1 = 860, 1650, 900
    p.rrect((x0 - 30, y1, x0 + 30, y0), 30, "#1d2a4a")
    if m > 60:
        p.rrect((x0 - 22, y0 - (y0 - y1) * m / 2000, x0 + 22, y0 - 8), 22, GOLD)
    place(cv, text_sprite(f"*{int(m):,} m*".replace(",", "."), 64, hl=GOLD), x0 - 20, y1 - 60)
    pill(cv, "Luftdruck –21 %", 540, 1760, "#ffffff", scale=ease_out_back(prog(t, 2.6, 2.95)), size=46)
    caption(cv, t, 0.2, 9, "Deine *Ohren* knallen!", 470, size=104)
    return cv


# ------------------------------------------------------------ 3 Flammen / Motoren aus
def car(p, x, y, s, col):
    p.rrect((x - 120 * s, y - 30 * s, x + 120 * s, y + 45 * s), 22 * s, col)
    p.rrect((x - 70 * s, y - 80 * s, x + 70 * s, y - 20 * s), 22 * s, col)
    p.rrect((x - 55 * s, y - 70 * s, x + 55 * s, y - 30 * s), 12 * s, "#cfe8ff")
    p.circle(x - 65 * s, y + 48 * s, 30 * s, INK)
    p.circle(x + 65 * s, y + 48 * s, 30 * s, INK)


CARS = [(1150, "#4f9cf0", 0.0), (1150, "#ff6b4a", 0.9), (1150, GOLD, 1.8)]


def s3_motoren(t):
    cv = canvas(((0, "#2a3355"), (0.6, "#3a4570"), (1, "#4a5585")))
    p = Pen(cv)
    p.poly([(0, 1420), (1080, 1420), (1080, 1920), (0, 1920)], "#2b2f3a")
    for i in range(6):
        x = 60 + i * 200
        p.rrect((x, 1590, x + 100, 1606), 6, "#d9d9d9")
    stop = 1.0
    for i, (x0, col, d) in enumerate(CARS):
        tt = min(t, stop)
        x = x0 - 300 * (tt + d) - 30 * (1 - math.exp(-max(0, t - stop) * 14))
        y = 1520 + (i % 2) * 120 - 60
        jerk = 6 * math.sin(max(0, t - stop) * 30) * math.exp(-max(0, t - stop) * 6) if t > stop else 0
        car(p, x, y + jerk, 1.0, col)
        if t < stop:
            for k in range(3):
                u = (t * 2 + k / 3) % 1.0
                p.circle(x + 140 + 80 * u, y + 30 - 20 * u, 14 + 20 * u, mix("#3a4570", "#b9c0d6", 1 - u))
        elif t > stop + 0.3 + i * 0.25:
            pill(cv, "Motor aus", x, y - 140, "#ffffff", scale=ease_out_back(prog(t, stop + 0.3 + i * 0.25,
                                                                                 stop + 0.6 + i * 0.25)), size=36)
    # Laterne mit Flamme
    p.line([(160, 1420), (160, 900)], "#1d2238", 16)
    p.rrect((110, 820, 210, 920), 14, "#1d2238")
    if t < stop:
        place(cv, glow(120, "#ffb347", 0.7), 160, 870)
        p.ellipse((145, 835, 175, 900), ORANGE)
    caption(cv, t, 0.2, 9, "Jede *Flamme* aus, jeder *Motor* aus", 470, size=88)
    return cv


# ------------------------------------------------------------ 4 Luft anhalten
def s4_luft(t):
    cv = canvas(DAY)
    p = Pen(cv)
    hx, hy = 380, 1220
    puff = 1 + 0.06 * math.sin(t * 5)
    p.rrect((hx - 150, hy + 170, hx + 150, hy + 600), 80, "#4f9cf0")
    p.circle(hx, hy, 190, SKIN)
    p.circle(hx - 120, hy + 50, 85 * puff, "#ffb59a")
    p.circle(hx + 120, hy + 50, 85 * puff, "#ffb59a")
    p.circle(hx, hy + 20, 150, SKIN)
    for dx in (-60, 60):
        p.line([(hx + dx - 30, hy - 40), (hx + dx + 30, hy - 40)], INK, 9)
    p.ellipse((hx - 26, hy + 75, hx + 26, hy + 105), "#c98a74")
    # Blut-Tank
    tx, ty = 800, 1250
    p.rrect((tx - 110, ty - 260, tx + 110, ty + 260), 50, "#ffffff", "#c9d6e6", 8)
    lvl = 0.85 * ease_out(prog(t, 0.6, 1.6))
    p.rrect((tx - 96, ty + 246 - 492 * lvl, tx + 96, ty + 246), 40, "#e0303a")
    place(cv, text_sprite("O₂", 70, color="#ffffff"), tx, ty + 60)
    pill(cv, "Vorrat: einige Minuten", tx - 40, ty + 340, "#ffffff", scale=ease_out_back(prog(t, 1.6, 1.95)))
    if t > 2.4:
        k = ease_out_back(prog(t, 2.4, 2.8))
        p.circle(hx + 170, hy - 200, 70 * k, "#3ddc84")
        p.line([(hx + 135, hy - 200), (hx + 160, hy - 170), (hx + 210, hy - 230)], "#ffffff", 14 * k)
    caption(cv, t, 0.2, 9, "Du? *Luft anhalten* – das reicht!", 470, size=96)
    return cv


# ------------------------------------------------------------ 5 Stufe 2
ATOM_PARTS = [(rng.uniform(0, 2 * math.pi), rng.uniform(200, 700), rng.uniform(6, 16)) for _ in range(40)]


def s5_stufe2(t):
    cv = canvas(ALARM)
    p = Pen(cv)
    k = ease_out_back(prog(t, 0.1, 0.45))
    cx, cy = 540, 860
    pts = [(cx, cy - 170 * k), (cx + 190 * k, cy + 140 * k), (cx - 190 * k, cy + 140 * k)]
    p.poly(pts, GOLD)
    p.line(pts + [pts[0]], GOLD, 30)
    place(cv, text_sprite("!", 200, color=INK, stroke=0), cx, cy + 30, k)
    place(cv, text_sprite("STUFE 2", 90, color=RED, stroke=8, stroke_color="#ffffff"), cx, cy + 260, k)
    ax, ay = 540, 1450
    burst = prog(t, 1.6, 2.6)
    if burst < 0.05:
        for i in range(3):
            a = t * 3 + i * 2.1
            p.circle(ax + 200 * math.cos(a + i), ay + 70 * math.sin(a * 1.3 + i), 16, "#9fd0ff")
        p.circle(ax, ay, 110, RED)
        place(cv, text_sprite("O", 130, color="#ffffff", stroke=0), ax, ay - 8)
    else:
        for ang, dist, r in ATOM_PARTS:
            d = dist * ease_out(burst)
            p.circle(ax + math.cos(ang) * d, ay + math.sin(ang) * d, r * (1 - 0.7 * burst), mix(RED, "#2a0608", burst))
    vignette(cv, 0.8)
    cv = glitch(cv, t, 1.0 - prog(t, 0, 0.8) + 0.6 * (1 if 1.6 < t < 1.9 else 0))
    caption(cv, t, 0.2, 9, "Und wenn *jedes* Sauerstoff-Atom verschwindet?", 470, size=86)
    return cv


# ------------------------------------------------------------ 6 Meere werden zu Gas
GAS = [(rng.uniform(0, 1080), rng.uniform(0, 1), rng.uniform(8, 22)) for _ in range(70)]


def s6_meere(t):
    cv = canvas(SEA)
    p = Pen(cv)
    lvl = lerp(1000, 1650, ease_in_out(prog(t, 1.0, 5.0)))
    pts = [(x, lvl + 18 * math.sin(x / 60 + t * 3)) for x in range(0, 1101, 30)]
    p.poly(pts + [(1080, 1920), (0, 1920)], "#2a74c4")
    p.poly([(x, y + 40) for x, y in pts] + [(1080, 1920), (0, 1920)], "#1f5fa8")
    p.poly([(0, 1800), (1080, 1800), (1080, 1920), (0, 1920)], "#c9b36b")
    g = prog(t, 0.8, 1.4)
    for x, ph, r in GAS:
        u = (ph + t * 0.45) % 1.0
        y = lvl - 30 - 900 * u
        p.circle(x + 20 * math.sin(u * 9 + ph * 7), y, r * (0.6 + 0.6 * u),
                 mix("#a9d6ff", "#ffffff", 0.5 + 0.5 * u) if g > 0 else "#a9d6ff")
    if t > 1.6:
        place(cv, text_sprite("*H₂O → H₂*", 110, hl="#ffffff"), 540, 780, ease_out_back(prog(t, 1.6, 2.0)))
    if t > 3.0:
        pill(cv, "Meere werden zu Gas", 540, 900, "#ffffff", scale=ease_out_back(prog(t, 3.0, 3.35)), size=48)
    caption(cv, t, 0.2, 9, "Ohne Sauerstoff: Meere werden zu *Gas*", 470, size=88)
    return cv


# ------------------------------------------------------------ 7 Beton zerbröselt
BLOCKS = [(x, y) for y in range(800, 1640, 70) for x in range(330, 750, 70)]
ROCKS = [(rng.uniform(40, 300), rng.uniform(1500, 1700), rng.uniform(30, 70)) for _ in range(6)] + \
        [(rng.uniform(780, 1040), rng.uniform(1500, 1700), rng.uniform(30, 70)) for _ in range(6)]
DELAY = [rng.uniform(0, 1) for _ in range(len(BLOCKS))]


def s7_beton(t):
    cv = canvas(((0, "#6f7a91"), (0.6, "#9aa3b6"), (1, "#c9cfdb")))
    p = Pen(cv)
    p.poly([(0, 1700), (1080, 1700), (1080, 1920), (0, 1920)], "#5b5f6a")
    c = prog(t, 0.8, 4.0)
    # Stahlträger bleiben stehen
    for x in (330, 540, 750):
        p.line([(x, 800), (x, 1700)], "#4a5160", 14)
    for y in range(800, 1701, 210):
        p.line([(330, y), (750, y)], "#4a5160", 10)
    for (x, y), d in zip(BLOCKS, DELAY):
        u = prog(c, d * 0.6, d * 0.6 + 0.4)
        if u >= 1:
            continue
        fall = 600 * u * u
        s = 1 - u
        p.rrect((x + 4, y + 4 + fall, x + 4 + 62 * s, y + 4 + 62 * s + fall), 6, mix("#b9bec8", "#9aa3b6", u))
        if u > 0:
            for k in range(3):
                p.circle(x + 30 + 40 * math.sin(d * 20 + k) * u, y + 30 + fall + 50 * k * u, 6 * (1 - u), "#d6d9e0")
    for x, y, r in ROCKS:
        s = 1 - prog(c, 0.3, 0.9)
        if s > 0:
            p.circle(x, y, r * s, "#7a7266")
        for k in range(5):
            u = prog(c, 0.3, 1.0)
            p.circle(x + (k - 2) * 20 * u * 3, y + 40 * u, 7 * (1 - u * 0.5) * (u > 0), "#a59c8e")
    if c > 0.6:
        pill(cv, "nur Stahl bleibt stehen", 540, 760, "#ffffff", scale=ease_out_back(prog(t, 3.0, 3.35)), size=46)
    caption(cv, t, 0.2, 9, "*Beton* und *Steine* zerbröseln", 470, size=96)
    return cv


# ------------------------------------------------------------ 8 Dein Körper
def body_poly(cx, top):
    return [(cx - 90, top + 220), (cx - 200, top + 300), (cx - 230, top + 620), (cx - 180, top + 630),
            (cx - 150, top + 400), (cx - 130, top + 700), (cx - 140, top + 1080), (cx - 50, top + 1080),
            (cx - 20, top + 760), (cx + 20, top + 760), (cx + 50, top + 1080), (cx + 140, top + 1080),
            (cx + 130, top + 700), (cx + 150, top + 400), (cx + 180, top + 630), (cx + 230, top + 620),
            (cx + 200, top + 300), (cx + 90, top + 220)]


def s8_koerper(t):
    cv = canvas(NIGHT)
    cx, top = 400, 640
    lay, lp = layer()
    lp.circle(cx, top + 110, 105, "#ffffff")
    lp.poly(body_poly(cx, top), "#ffffff")
    a = np.array(lay.getchannel("A"))
    fill = 0.65 * ease_in_out(prog(t, 0.6, 2.6))
    ybound = int((top + 1080 - 1080 * fill) * S)
    rgb = np.zeros(a.shape + (4,), np.uint8)
    rgb[..., 0], rgb[..., 1], rgb[..., 2] = 60, 70, 110
    rgb[ybound:, :, 0], rgb[ybound:, :, 1], rgb[ybound:, :, 2] = 230, 50, 60
    rgb[..., 3] = a
    cv.alpha_composite(Image.fromarray(rgb, "RGBA"))
    if fill > 0.05:
        Pen(cv).line([(cx - 260, ybound / S), (cx + 260, ybound / S)], "#ffffff", 4, caps=False)
    if t > 2.6:
        place(cv, glow(200, RED, 0.5), 840, 1250)
        place(cv, text_sprite("*≈ 65 %*", 110, hl=RED), 850, 1250, ease_out_back(prog(t, 2.6, 3.0)))
        pill(cv, "Sauerstoff", 850, 1370, RED, scale=ease_out_back(prog(t, 2.9, 3.25)), fg="#ffffff", size=46)
    caption(cv, t, 0.2, 9, "Dein Körper: fast *⅔ Sauerstoff*", 470, size=96)
    return cv


# ------------------------------------------------------------ 9 Ende (Loop)
def s9_ende(t):
    cv = canvas(NIGHT)
    beacon(cv, 120, 760, t)
    beacon(cv, 960, 760, t + 0.5)
    p = Pen(cv)
    p.poly([(0, 1690), (1080, 1690), (1080, 1920), (0, 1920)], "#2a2236")
    for x, y, s in CANDLES:
        candle(p, cv, x, y, s, t, lit=True)
    countdown(cv, 0.05, y=1000)
    vignette(cv, 0.4 + 0.25 * math.sin(t * 7))
    caption(cv, t, 0.1, 9, "Hättest du's *gewusst*?", 430, size=100)
    caption(cv, t, 1.4, 9, "Folge für mehr *Warum eigentlich?*", 660, size=62)
    return cv


VIDEO = Video([
    (3.2, s1_einstieg, [(0.0, "Fünf Sekunden lang kein Sauerstoff auf der Erde. Das passiert:")]),
    (5.0, s2_ohren, [(0.2, "Zuerst knallen deine Ohren – der Luftdruck fällt, als wärst du plötzlich auf 2.000 Metern Höhe.")]),
    (4.5, s3_motoren, [(0.2, "Jede Flamme geht aus. Autos bleiben stehen – ihre Motoren brauchen Sauerstoff.")]),
    (5.0, s4_luft, [(0.2, "Und du? Halt einfach die Luft an. Dein Blut hat Sauerstoff für ein paar Minuten gespeichert.")]),
    (3.5, s5_stufe2, [(0.2, "Aber was, wenn jedes einzelne Sauerstoff-Atom verschwindet?")]),
    (5.5, s6_meere, [(0.2, "Dann wird es gruselig: Wasser besteht aus Wasserstoff und Sauerstoff – ohne Sauerstoff würden die Meere zu Gas.")]),
    (4.5, s7_beton, [(0.2, "Beton und Steine zerbröseln, denn auch sie stecken voller Sauerstoff.")]),
    (4.5, s8_koerper, [(0.2, "Und dein Körper? Der besteht zu fast zwei Dritteln aus Sauerstoff.")]),
    (3.0, s9_ende, [(0.2, "Hättest du es gewusst?"),
                    (1.5, "Folge für mehr: Warum eigentlich?")]),
])

if __name__ == "__main__":
    cli(VIDEO, __file__, cover_t=1.0)
