"""Folge 12: Was wäre, wenn das Internet weltweit ausfällt?  (9:16, Kurzformat ~38 s)

Rendern:   python3 videos/12_internet.py            (ElevenLabs, Stimme Brian, 12 % schneller)
Vorschau:  python3 videos/12_internet.py --stills

Hook: Handy mit Apps ab Bild 1, nach 0,6 s „Keine Verbindung“ + Flackern + Wackeln,
die leuchtende Weltkarte im Hintergrund geht Linie für Linie aus.
(Keine echten App-Logos – nur neutrale Symbole.)
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

TECH = ((0, "#040b1c"), (0.55, "#0a1836"), (1, "#0e2148"))
SHOP = ((0, "#1b2340"), (0.6, "#2a3560"), (1, "#3a4675"))
CYAN = "#3ef0ff"
RED = "#ff4d5e"
GREEN = "#3ddc84"
GOLD = "#FFD23F"
INK = "#081022"

rng = random.Random(12)
CITIES = [(rng.uniform(40, 1040), rng.choice([rng.uniform(560, 800), rng.uniform(1650, 1880)])) for _ in range(34)]
LINKS = []
for i, (x, y) in enumerate(CITIES):
    near = sorted(range(len(CITIES)), key=lambda j: (CITIES[j][0] - x) ** 2 + (CITIES[j][1] - y) ** 2)[1:3]
    for j in near:
        if (j, i) not in LINKS:
            LINKS.append((i, j))
LINK_OFF = [rng.uniform(0.0, 1.0) for _ in LINKS]


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


def cam(cv, t, z0=1.0, zoom_dur=0.7, shake_at=None, shake_dur=0.6, amp=16):
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


def netmap(cv, t, off=0.0):
    """Leuchtendes Netz im Hintergrund; off 0..1 = Anteil ausgefallener Linien."""
    p = Pen(cv)
    for (i, j), o in zip(LINKS, LINK_OFF):
        (x0, y0), (x1, y1) = CITIES[i], CITIES[j]
        dead = o < off
        p.line([(x0, y0), (x1, y1)], "#16264a" if dead else mix("#0a1836", CYAN, 0.55), 3)
        if not dead:
            u = (t * 0.8 + o) % 1.0
            p.circle(lerp(x0, x1, u), lerp(y0, y1, u), 5, CYAN)
    for k, (x, y) in enumerate(CITIES):
        dead = all(LINK_OFF[n] < off for n, (i, j) in enumerate(LINKS) if k in (i, j))
        if not dead:
            place(cv, glow(22, CYAN, 0.7), x, y)
        p.circle(x, y, 7, "#2a3a60" if dead else "#ffffff")


# ------------------------------------------------------------ Handy
PX, PY, PW, PH = 540, 1210, 480, 900
ICON_COLS = ["#3ddc84", "#ff4d8d", "#4f9cf0", "#FFD23F", "#b388ff", "#ff8a3d", "#3ef0ff", "#ff5a4a",
             "#7ee081", "#ffa8d0", "#8fb8ff", "#ffcf6b"]
GLYPHS = ["chat", "play", "search", "note", "cam", "mail", "pin", "heart", "star", "cloud", "cart", "game"]


def glyph(p, kind, x, y, s=1.0):
    w = "#ffffff"
    if kind == "chat":
        p.circle(x, y - 4 * s, 22 * s, w)
        p.poly([(x - 14 * s, y + 10 * s), (x - 22 * s, y + 24 * s), (x - 2 * s, y + 16 * s)], w)
    elif kind == "play":
        p.poly([(x - 12 * s, y - 18 * s), (x + 18 * s, y), (x - 12 * s, y + 18 * s)], w)
    elif kind == "search":
        p.circle(x - 5 * s, y - 5 * s, 15 * s, None, w, 6 * s)
        p.line([(x + 6 * s, y + 6 * s), (x + 18 * s, y + 18 * s)], w, 7 * s)
    elif kind == "note":
        p.line([(x + 8 * s, y - 20 * s), (x + 8 * s, y + 10 * s)], w, 6 * s)
        p.circle(x, y + 12 * s, 10 * s, w)
    elif kind == "cam":
        p.rrect((x - 22 * s, y - 14 * s, x + 22 * s, y + 18 * s), 6 * s, w)
        p.circle(x, y + 2 * s, 9 * s, "#00000055")
    elif kind == "mail":
        p.rrect((x - 22 * s, y - 15 * s, x + 22 * s, y + 15 * s), 4 * s, w)
        p.line([(x - 20 * s, y - 12 * s), (x, y + 4 * s), (x + 20 * s, y - 12 * s)], "#00000055", 4 * s)
    elif kind == "pin":
        p.circle(x, y - 6 * s, 15 * s, w)
        p.poly([(x - 13 * s, y), (x + 13 * s, y), (x, y + 22 * s)], w)
    elif kind == "heart":
        p.circle(x - 9 * s, y - 5 * s, 11 * s, w)
        p.circle(x + 9 * s, y - 5 * s, 11 * s, w)
        p.poly([(x - 19 * s, y), (x + 19 * s, y), (x, y + 20 * s)], w)
    elif kind == "star":
        pts = [(x + (20 if k % 2 == 0 else 9) * s * math.cos(-math.pi / 2 + k * math.pi / 5),
                y + (20 if k % 2 == 0 else 9) * s * math.sin(-math.pi / 2 + k * math.pi / 5)) for k in range(10)]
        p.poly(pts, w)
    elif kind == "cloud":
        for dx, dy, r in ((-10, 4, 12), (6, -4, 15), (16, 6, 10)):
            p.circle(x + dx * s, y + dy * s, r * s, w)
    elif kind == "cart":
        p.rrect((x - 18 * s, y - 12 * s, x + 18 * s, y + 8 * s), 4 * s, w)
        p.circle(x - 10 * s, y + 16 * s, 5 * s, w)
        p.circle(x + 10 * s, y + 16 * s, 5 * s, w)
    elif kind == "game":
        p.rrect((x - 24 * s, y - 12 * s, x + 24 * s, y + 14 * s), 12 * s, w)


def icon_pos(i):
    c, r = i % 4, i // 4
    return PX - 165 + c * 110, PY - 300 + r * 130


def phone(cv, t, online=True, grey=0.0, fall=None, flicker=0.0, screen=None):
    """grey: Anteil grauer Apps; fall: {index: fortschritt}; screen: eigene Funktion für den Bildschirm."""
    p = Pen(cv)
    place(cv, glow(420, CYAN if online else RED, 0.18), PX, PY)
    p.rrect((PX - PW / 2 - 18, PY - PH / 2 - 18, PX + PW / 2 + 18, PY + PH / 2 + 18), 70, "#0b0f1a",
            "#3a4560", 5)
    bright = 1 - flicker
    p.rrect((PX - PW / 2, PY - PH / 2, PX + PW / 2, PY + PH / 2), 54,
            mix("#05070d", "#14244a", bright))
    if screen:
        screen(cv, p)
    else:
        for i, (col, g) in enumerate(zip(ICON_COLS, GLYPHS)):
            x, y = icon_pos(i)
            k = 0.0
            if fall and i in fall:
                k = fall[i]
            if k >= 1:
                continue
            gi = 1.0 if i < grey * len(ICON_COLS) else 0.0
            c = mix(mix(col, "#5a6075", gi), "#05070d", 1 - bright)
            dy = 900 * k * k
            ang = 50 * k * (1 if i % 2 else -1)
            spr = Image.new("RGBA", (110 * S, 110 * S), (0, 0, 0, 0))
            sp = Pen(spr)
            sp.rrect((10, 10, 100, 100), 24, c)
            glyph(sp, g, 55, 55, 1.0)
            if ang:
                spr = spr.rotate(ang, expand=True, resample=Image.BILINEAR)
            place(cv, spr, x, y + dy)
    # Statusleiste
    place(cv, text_sprite("07:30", 30, weight="bold", stroke=0), PX - PW / 2 + 70, PY - PH / 2 + 40)
    wx, wy = PX + PW / 2 - 60, PY - PH / 2 + 48
    col = "#ffffff" if online else "#5a6075"
    for k, r in enumerate((10, 20, 30)):
        p.d.arc([(wx - r) * S, (wy - r) * S, (wx + r) * S, (wy + r) * S], 225, 315, fill=col, width=int(5 * S))
    if not online:
        p.line([(wx - 16, wy - 34), (wx + 16, wy - 2)], RED, 6)
        p.line([(wx - 16, wy - 2), (wx + 16, wy - 34)], RED, 6)
    p.rrect((PX - 70, PY - PH / 2 + 6, PX + 70, PY - PH / 2 + 34), 14, "#0b0f1a")


def loader(p, x, y, t, r=42):
    a0 = t * 360 * 1.3
    p.d.arc([(x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S], a0, a0 + 270, fill=(255, 255, 255, 255),
            width=int(9 * S))


def no_conn(cv, t, k):
    if k <= 0.01:
        return
    p = Pen(cv)
    p.rrect((PX - 200, PY + 160, PX + 200, PY + 360), 30, "#1b2440")
    loader(p, PX, PY + 230, t)
    place(cv, text_sprite("Keine Verbindung", 34, weight="bold", stroke=0, color="#ff9aa5"), PX, PY + 315, k)


# ------------------------------------------------------------ 1 Einstieg (Hook)
def s1_einstieg(t):
    cv = canvas(TECH)
    cut = 0.6
    netmap(cv, t, off=ease_in_out(prog(t, cut, 2.8)))
    flick = 0.0
    if cut < t < cut + 0.5:
        flick = 0.7 if int(t * 24) % 2 == 0 else 0.0
    phone(cv, t, online=t < cut, flicker=flick)
    no_conn(cv, t, ease_out_back(prog(t, cut + 0.2, cut + 0.5)))
    cv = cam(cv, t, z0=1.12, shake_at=cut, shake_dur=0.6)
    caption(cv, t, -1, 9, "Das Internet ist *weg* – *weltweit*!", 470, size=96)
    return cv


# ------------------------------------------------------------ 2 Apps fallen
def s2_apps(t):
    cv = canvas(TECH)
    netmap(cv, t, off=1.0)
    grey = prog(t, 0.2, 1.4)
    fall = {i: prog(t, 1.6 + i * 0.12, 2.4 + i * 0.12) for i in range(12)}
    phone(cv, t, online=False, grey=grey, fall=fall)
    if t > 2.9:
        pill(cv, "…und das ist erst der Anfang", 540, 1750, RED, scale=ease_out_back(prog(t, 2.9, 3.25)),
             fg="#ffffff", size=44)
    caption(cv, t, 0.2, 9, "Kein Chat, kein Video, keine *Suche*", 470, size=92)
    return cv


# ------------------------------------------------------------ 3 Kasse
def person(p, x, y, s, col):
    p.circle(x, y - 150 * s, 42 * s, "#f6c9a8")
    p.rrect((x - 55 * s, y - 105 * s, x + 55 * s, y + 60 * s), 40 * s, col)
    p.line([(x - 25 * s, y + 60 * s), (x - 25 * s, y + 160 * s)], "#2a3050", 26 * s)
    p.line([(x + 25 * s, y + 60 * s), (x + 25 * s, y + 160 * s)], "#2a3050", 26 * s)


def s3_kasse(t):
    cv = canvas(SHOP)
    p = Pen(cv)
    p.poly([(0, 1640), (1080, 1640), (1080, 1920), (0, 1920)], "#202842")
    # Kartenterminal
    tx, ty = 300, 1000
    p.rrect((tx - 130, ty - 200, tx + 130, ty + 200), 34, "#2b2f3a")
    p.rrect((tx - 100, ty - 170, tx + 100, ty - 40), 14, "#ffe5e8" if t > 0.8 else "#9fe8ff")
    if t > 0.8:
        place(cv, text_sprite("FEHLER", 44, color=RED, stroke=0), tx, ty - 105, ease_out_back(prog(t, 0.8, 1.1)))
    for r in range(3):
        for c in range(3):
            p.rrect((tx - 85 + c * 62, ty - 10 + r * 55, tx - 35 + c * 62, ty + 32 + r * 55), 8, "#4a5060")
    kx = lerp(tx + 260, tx + 40, ease_in_out(prog(t, 0.1, 0.7)))
    p.rrect((kx - 80, ty - 300, kx + 80, ty - 200), 12, "#4f9cf0")
    p.rrect((kx - 60, ty - 280, kx - 20, ty - 250), 5, GOLD)
    # Geldautomat
    ax, ay = 790, 1050
    p.rrect((ax - 170, ay - 330, ax + 170, ay + 590), 20, "#3a4260")
    p.rrect((ax - 130, ay - 280, ax + 130, ay - 100), 14, "#0b0f1a")
    k = ease_out_back(prog(t, 1.6, 1.95))
    place(cv, text_sprite("Außer", 40, color=RED, stroke=0), ax, ay - 215, k)
    place(cv, text_sprite("Betrieb", 40, color=RED, stroke=0), ax, ay - 165, k)
    p.rrect((ax - 90, ay - 40, ax + 90, ay - 20), 6, "#0b0f1a")
    for i, col in enumerate(("#ff8a3d", "#b388ff", "#3ddc84")):
        k2 = ease_out(prog(t, 2.4 + i * 0.3, 2.8 + i * 0.3))
        if k2 > 0:
            person(p, 120 + i * 120, 1540 + 30 * (1 - k2), 0.75, col)
    caption(cv, t, 0.2, 9, "*Kartenzahlung* & *Geldautomat*: aus", 470, size=88)
    return cv


# ------------------------------------------------------------ 4 Telefon
def s4_telefon(t):
    cv = canvas(TECH)
    netmap(cv, t, off=1.0)

    def screen(cv2, p):
        ring = t < 1.6
        sh = 10 * math.sin(t * 50) if ring else 0
        cx, cy = PX + sh, PY - 60
        p.circle(cx, cy, 120, GREEN if ring else RED)
        hx, hy = cx, cy
        p.rrect((hx - 60, hy - 18, hx + 60, hy + 18), 18, "#ffffff")
        p.rrect((hx - 66, hy - 30, hx - 34, hy + 34), 12, "#ffffff")
        p.rrect((hx + 34, hy - 30, hx + 66, hy + 34), 12, "#ffffff")
        if ring:
            for i in range(3):
                r = 140 + ((t * 120 + i * 40) % 120)
                p.circle(cx, cy, r, None, mix("#14244a", GREEN, 1 - (r - 140) / 120), 5)
        else:
            k = ease_out_back(prog(t, 1.6, 1.95))
            place(cv2, text_sprite("Anruf", 50, color=RED, stroke=0), PX, PY + 160, k)
            place(cv2, text_sprite("fehlgeschlagen", 50, color=RED, stroke=0), PX, PY + 220, k)

    phone(cv, t, online=False, screen=screen)
    caption(cv, t, 0.2, 9, "Auch viele *Telefonate*: weg", 470, size=96)
    return cv


# ------------------------------------------------------------ 5 Regale leer
PRODUCTS = [(x, y, rng.choice(["#ff8a3d", "#3ddc84", "#4f9cf0", "#FFD23F", "#ff4d8d", "#b388ff", "#ffffff"]),
             rng.uniform(0, 1)) for y in (900, 1160, 1420) for x in range(150, 960, 72)]


def s5_regale(t):
    cv = canvas(SHOP)
    p = Pen(cv)
    for y in (900, 1160, 1420):
        p.rrect((100, y + 90, 980, y + 118), 6, "#8a6a42")
    p.rrect((90, 760, 120, 1560), 6, "#6a5032")
    p.rrect((960, 760, 990, 1560), 6, "#6a5032")
    gone = ease_in_out(prog(t, 0.6, 3.8))
    for x, y, col, d in PRODUCTS:
        if d < gone:
            continue
        p.rrect((x - 28, y - 70, x + 28, y + 88), 10, col)
        p.rrect((x - 20, y - 40, x + 20, y + 10), 6, "#ffffffaa")
    day = 1 + min(2, int(gone * 3))
    pill(cv, f"Tag {day}", 540, 1680, GOLD, size=56)
    caption(cv, t, 0.2, 9, "Nach wenigen Tagen: *Regale leer*", 470, size=92)
    return cv


# ------------------------------------------------------------ 6 GPS ohne Karte
def s6_gps(t):
    cv = canvas(TECH)
    p = Pen(cv)
    sx, sy = 860, 640
    p.rrect((sx - 40, sy - 30, sx + 40, sy + 30), 10, "#c9d2e3")
    p.rrect((sx - 140, sy - 18, sx - 50, sy + 18), 4, "#4f9cf0")
    p.rrect((sx + 50, sy - 18, sx + 140, sy + 18), 4, "#4f9cf0")
    for i in range(3):
        r = 60 + ((t * 160 + i * 60) % 180)
        p.d.arc([(sx - r) * S, (sy - r) * S, (sx + r) * S, (sy + r) * S], 100, 170,
                fill=(62, 240, 255, int(255 * (1 - (r - 60) / 180))), width=int(6 * S))

    def screen(cv2, p2):
        p2.rrect((PX - PW / 2 + 20, PY - PH / 2 + 80, PX + PW / 2 - 20, PY + PH / 2 - 30), 30, "#c9ccd4")
        for i in range(1, 8):
            y = PY - PH / 2 + 80 + i * 105
            p2.line([(PX - PW / 2 + 30, y), (PX + PW / 2 - 30, y)], "#b9bcc6", 2, caps=False)
        pulse = 1 + 0.25 * math.sin(t * 6)
        p2.circle(PX, PY, 50 * pulse, "#4f9cf055")
        p2.circle(PX, PY, 24, "#4f9cf0", "#ffffff", 6)
        if t > 1.6:
            place(cv2, text_sprite("?", 150, color="#6a6f80", stroke=0), PX + 120, PY - 200,
                  ease_out_back(prog(t, 1.6, 2.0)))

    phone(cv, t, online=False, screen=screen)
    pill(cv, "GPS ✓", 300, 760, GREEN, scale=ease_out_back(prog(t, 0.4, 0.75)), size=48)
    pill(cv, "Karte: weg", 540, 1740, RED, scale=ease_out_back(prog(t, 1.8, 2.15)), fg="#ffffff", size=48)
    caption(cv, t, 0.2, 9, "GPS geht – aber *keine Karte*", 470, size=96)
    return cv


# ------------------------------------------------------------ 7 Umweg
NODES = [(200, 900), (420, 760), (680, 820), (900, 950), (300, 1180), (560, 1100), (820, 1250),
         (220, 1480), (480, 1420), (740, 1560), (940, 1450)]
EDGES = [(0, 1), (1, 2), (2, 3), (0, 4), (1, 5), (2, 5), (3, 6), (4, 5), (5, 6), (4, 7), (5, 8), (7, 8),
         (8, 9), (6, 9), (9, 10), (6, 10), (3, 10)]
PATH_A = [0, 1, 2, 3, 10]
PATH_B = [0, 4, 5, 6, 10]
CUT = (1, 2)


def path_point(path, u):
    segs = len(path) - 1
    i = min(segs - 1, int(u * segs))
    f = u * segs - i
    (x0, y0), (x1, y1) = NODES[path[i]], NODES[path[i + 1]]
    return lerp(x0, x1, f), lerp(y0, y1, f)


def s7_umweg(t):
    cv = canvas(TECH)
    p = Pen(cv)
    cut = t > 2.2
    for a, b in EDGES:
        dead = cut and (a, b) == CUT
        p.line([NODES[a], NODES[b]], RED if dead else mix("#0a1836", CYAN, 0.6), 6)
    if cut:
        (x0, y0), (x1, y1) = NODES[CUT[0]], NODES[CUT[1]]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        k = ease_out_back(prog(t, 2.2, 2.5))
        p.line([(mx - 34 * k, my - 34 * k), (mx + 34 * k, my + 34 * k)], RED, 14)
        p.line([(mx - 34 * k, my + 34 * k), (mx + 34 * k, my - 34 * k)], RED, 14)
    for n, (x, y) in enumerate(NODES):
        place(cv, glow(36, CYAN, 0.6), x, y)
        p.circle(x, y, 18, "#ffffff" if n not in (0, 10) else GOLD)
    path = PATH_B if cut else PATH_A
    for k in range(6):
        u = (t * 0.45 + k / 6) % 1.0
        if cut and t < 3.0 and k % 2:
            continue
        x, y = path_point(path, u)
        place(cv, glow(26, CYAN, 0.9), x, y)
        p.circle(x, y, 10, CYAN)
    if t > 3.2:
        pill(cv, "Umweg gefunden", 540, 1720, GREEN, scale=ease_out_back(prog(t, 3.2, 3.55)), size=50)
    else:
        pill(cv, "kein zentrales Herz", 540, 1720, "#ffffff", scale=ease_out_back(prog(t, 0.6, 0.95)), size=46)
    caption(cv, t, 0.2, 9, "Zum Glück: fast *unmöglich*", 470, size=100)
    return cv


# ------------------------------------------------------------ 8 Ende (Loop)
def s8_ende(t):
    cv = canvas(TECH)
    netmap(cv, t, off=0.0)
    phone(cv, t, online=True)
    caption(cv, t, 0.1, 9, "Hättest du's *gewusst*?", 430, size=100)
    caption(cv, t, 1.4, 9, "Folge für mehr *Warum eigentlich?*", 640, size=62)
    return cv


VIDEO = Video([
    (3.2, s1_einstieg, [(0.0, "Du wachst auf – und das Internet ist weg. Weltweit.")]),
    (4.0, s2_apps, [(0.2, "Kein WhatsApp, kein TikTok, kein Google. Aber das ist erst der Anfang.")]),
    (4.8, s3_kasse, [(0.2, "An der Kasse geht kaum noch was: Kartenzahlung und Geldautomaten brauchen das Netz.")]),
    (3.2, s4_telefon, [(0.2, "Selbst viele Telefonate laufen heute übers Internet.")]),
    (4.6, s5_regale, [(0.2, "Supermärkte bestellen ihre Ware online – nach wenigen Tagen werden die Regale leer.")]),
    (4.6, s6_gps, [(0.2, "Dein Handy weiß per GPS noch, wo du bist – aber ohne Karten-App bringt dir das wenig.")]),
    (7.0, s7_umweg, [(0.2, "Zum Glück ist ein weltweiter Ausfall fast unmöglich: Das Internet hat kein zentrales Herz."),
                     (3.6, "Fällt eine Leitung aus, nehmen die Daten einfach einen Umweg.")]),
    (3.0, s8_ende, [(0.2, "Hättest du es gewusst?"),
                    (1.5, "Folge für mehr: Warum eigentlich?")]),
])

if __name__ == "__main__":
    cli(VIDEO, __file__, cover_t=1.2)
