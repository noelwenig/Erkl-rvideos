"""Folge 7: Warum ist es im Weltall dunkel, obwohl die Sonne scheint?  (9:16)

Rendern:   python3 videos/07_weltall.py            (ElevenLabs, Stimme Brian)
Vorschau:  python3 videos/07_weltall.py --stills

Hook: Rakete startet ab dem ersten Bild (Wackeln + Zoom), Höhenmesser rast hoch,
der Himmel wird in 3 Sekunden schwarz – das Rätsel ist zu sehen, bevor es erklärt wird.
"""
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image  # noqa: E402

from ev.engine import (S, Pen, Video, blend_canvas, canvas, caption, cli, ease_in_out,  # noqa: E402
                       ease_out, ease_out_back, glow, layer, lerp, mix, place, prog, text_sprite)

SKY = ((0, "#1d5fc9"), (0.55, "#4f9cf0"), (1, "#a9d8ff"))
SPACE = ((0, "#000000"), (0.6, "#05060f"), (1, "#0b0e22"))
ROOM = ((0, "#0b0d18"), (1, "#151a2c"))
SUNC = "#fff6d8"
GOLD = "#FFD23F"
LIGHT = "#ffe27a"
BLUE = "#4fa3ff"
RED = "#ff5a4a"
MOON = "#8d8f99"
MOON_DARK = "#6b6d78"
INK = "#0b0e22"

rng = random.Random(7)
STARS = [(rng.uniform(0, 1080), rng.uniform(0, 1920), rng.uniform(1.5, 3.8), rng.uniform(0, 6.3))
         for _ in range(110)]


def stars(p, t, a=1.0, bg="#05060f", ymax=1920):
    if a <= 0.02:
        return
    for x, y, r, ph in STARS:
        if y > ymax:
            continue
        k = (0.5 + 0.5 * (0.5 + 0.5 * math.sin(t * 2 + ph))) * a
        p.circle(x, y, r, mix(bg, "#ffffff", k))


def space(t, a=1.0):
    cv = canvas(SPACE)
    stars(Pen(cv), t, a)
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


def hook_cam(cv, t, zoom_dur=0.7, z0=1.14, shake_dur=2.6, amp=12):
    """Hook: kurzer Zoom + Wackeln am Anfang."""
    z = lerp(z0, 1.0, ease_out(prog(t, 0, zoom_dur)))
    a = amp * (1 - prog(t, 0, shake_dur)) * S
    if z <= 1.001 and a < 0.5:
        return cv
    z = max(z, 1.0 + 2 * a / cv.width + 0.002)
    w, h = cv.size
    cw, ch = int(w / z), int(h / z)
    dx, dy = a * math.sin(t * 53), a * math.cos(t * 41)
    x0 = int(min(max(0, (w - cw) / 2 + dx), w - cw))
    y0 = int(min(max(0, (h - ch) / 2 + dy), h - ch))
    return cv.crop((x0, y0, x0 + cw, y0 + ch)).resize((w, h), Image.BILINEAR)


def sun(cv, x, y, r=70, k=1.0):
    place(cv, glow(r * 4.5, "#fff3c0", 0.9 * k), x, y)
    place(cv, glow(r * 2.2, "#ffffff", 0.9 * k), x, y)
    Pen(cv).circle(x, y, r * k, SUNC)


def packet(p, x0, y0, x1, y1, u, col=LIGHT, ln=60, w=8):
    """Lichtpaket (kurzer Strich mit Schweif) auf der Strecke bei Anteil u."""
    if not 0 <= u <= 1:
        return
    L = math.hypot(x1 - x0, y1 - y0) or 1
    x, y = lerp(x0, x1, u), lerp(y0, y1, u)
    tx, ty = x - (x1 - x0) / L * ln, y - (y1 - y0) / L * ln
    p.line([(tx, ty), (x, y)], col, w)
    p.circle(x, y, w * 0.9, "#ffffff")


# ------------------------------------------------------------ Figuren
def rocket(p, x, y, s=1.0, t=0.0, flame=1.0):
    if flame > 0:
        fl = (1 + 0.18 * math.sin(t * 40) + 0.1 * math.sin(t * 73)) * flame
        p.poly([(x - 45 * s, y + 150 * s), (x + 45 * s, y + 150 * s), (x, y + (150 + 260 * fl) * s)],
               "#ff8a3d")
        p.poly([(x - 28 * s, y + 150 * s), (x + 28 * s, y + 150 * s), (x, y + (150 + 170 * fl) * s)],
               GOLD)
        p.poly([(x - 14 * s, y + 150 * s), (x + 14 * s, y + 150 * s), (x, y + (150 + 90 * fl) * s)],
               "#ffffff")
    p.poly([(x - 55 * s, y + 60 * s), (x - 110 * s, y + 160 * s), (x - 55 * s, y + 140 * s)], RED)
    p.poly([(x + 55 * s, y + 60 * s), (x + 110 * s, y + 160 * s), (x + 55 * s, y + 140 * s)], RED)
    p.rrect((x - 55 * s, y - 170 * s, x + 55 * s, y + 150 * s), 30 * s, "#f4f6fb")
    p.poly([(x - 55 * s, y - 150 * s), (x, y - 290 * s), (x + 55 * s, y - 150 * s)], RED)
    p.circle(x, y - 60 * s, 30 * s, "#9aa7c4")
    p.circle(x, y - 60 * s, 22 * s, BLUE)
    p.rrect((x - 55 * s, y + 40 * s, x + 55 * s, y + 60 * s), 4 * s, RED)


def astronaut(p, x, y, s=1.0, visor=GOLD):
    suit, shade = "#f2f4f8", "#c9cfdc"
    p.rrect((x - 95 * s, y - 40 * s, x - 40 * s, y + 110 * s), 18 * s, shade)       # Rucksack
    p.line([(x - 30 * s, y + 110 * s), (x - 45 * s, y + 230 * s)], suit, 46 * s)     # Beine
    p.line([(x + 30 * s, y + 110 * s), (x + 50 * s, y + 225 * s)], suit, 46 * s)
    p.line([(x - 50 * s, y + 20 * s), (x - 120 * s, y + 100 * s)], suit, 40 * s)     # Arme
    p.line([(x + 50 * s, y + 20 * s), (x + 120 * s, y - 30 * s)], suit, 40 * s)
    p.rrect((x - 62 * s, y - 50 * s, x + 62 * s, y + 130 * s), 40 * s, suit)
    p.rrect((x - 30 * s, y + 10 * s, x + 30 * s, y + 55 * s), 8 * s, "#7c8bb0")
    p.circle(x, y - 105 * s, 78 * s, suit)
    p.ellipse((x - 55 * s, y - 145 * s, x + 60 * s, y - 70 * s), visor)
    p.ellipse((x + 10 * s, y - 135 * s, x + 40 * s, y - 115 * s), "#ffffffaa")


def eye(p, x, y, s=1.0, lit=0.0):
    w, h = 130 * s, 70 * s
    top = [(x + w * math.cos(u), y - h * math.sin(u)) for u in [math.pi * i / 24 for i in range(25)]]
    bot = [(x + w * math.cos(u), y + h * math.sin(u)) for u in [math.pi - math.pi * i / 24 for i in range(25)]]
    p.poly(top + bot, mix("#5a5f73", "#ffffff", 0.3 + 0.7 * lit))
    p.circle(x, y, 48 * s, mix("#24305a", BLUE, 0.3 + 0.7 * lit))
    p.circle(x, y, 22 * s, INK)
    p.circle(x + 14 * s, y - 14 * s, 9 * s, "#ffffff")


# ------------------------------------------------------------ 1 Einstieg (Hook)
SMOKE = [(rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(40, 90)) for _ in range(16)]
CLOUDS1 = [(rng.uniform(80, 1000), rng.uniform(0, 1), rng.uniform(0.6, 1.2)) for _ in range(7)]


def s1_einstieg(t):
    d = ease_in_out(prog(t, 0.4, 3.6))
    cv = blend_canvas(SKY, SPACE, d)
    p = Pen(cv)
    stars(p, t, prog(d, 0.65, 1.0))
    # Erde: Boden fällt weg, dann taucht die Erdkrümmung auf
    g = ease_in_out(prog(t, 0, 1.2))
    if g < 1:
        p.poly([(0, 1640 + 500 * g), (1080, 1640 + 500 * g), (1080, 1920), (0, 1920)], "#3d8b4f")
    for cx, ph, sc in CLOUDS1:
        y = -200 + ((t * 1500 + ph * 2400) % 2400)
        if d < 0.8:
            col = mix("#ffffff", "#4f9cf0", 0.3 + 0.7 * d)
            for dx, dy, r in ((-60, 10, 45), (0, -15, 60), (60, 8, 48)):
                p.circle(cx + dx * sc, y + dy * sc, r * sc, col)
    e = ease_out(prog(t, 1.6, 3.6))
    if e > 0:
        R = 2600
        p.circle(540, 1920 + R - 260 * e, R, mix("#1e4fa8", "#2f6fd6", 0.5))
        p.circle(540, 1920 + R - 260 * e + 10, R - 18, "#1e4fa8")
        place(cv, glow(500, "#7fc4ff", 0.25 * e), 540, 1920 - 220 * e)
    sun(cv, 860, 800, 70)
    # Rauch am Start
    for dx, ph, r in SMOKE:
        u = (t * 0.9 + ph) % 1.0
        if t < 1.6:
            p.circle(540 + dx * 160 * (1 + u), 1550 + 300 * u + 200 * t, r * (1 + u),
                     mix("#e6eaf2", "#9aa7c4", u))
    rocket(p, 540, 1130 + 10 * math.sin(t * 30) * (1 - prog(t, 0, 2.5)), 1.0, t)
    km = 100 * ease_in_out(prog(t, 0.0, 3.6))
    pill(cv, f"Höhe: {km:.0f} km", 230, 760, "#ffffff", size=44)
    if t > 5.6:
        place(cv, text_sprite("?", 240, color="#ffffff"), 820, 1120, ease_out_back(prog(t, 5.6, 6.0)))
    cv = hook_cam(cv, t)
    caption(cv, t, -1, 5.6, "Der Himmel wird *schwarz* – obwohl die Sonne scheint!", 470, size=84)
    caption(cv, t, 5.6, 9, "Wie kann das *sein*?", 470, size=100)
    return cv


# ------------------------------------------------------------ 2 Licht ist unsichtbar
def s2_unsichtbar(t):
    cv = space(t, 0.4)
    p = Pen(cv)
    ex, ey = 760, 1450
    # Strahl 1: fliegt am Auge vorbei
    for k in range(3):
        u = prog(t, 0.3 + k * 0.5, 1.6 + k * 0.5)
        packet(p, -60, 960 + k * 40, 1140, 960 + k * 40, u, ln=120, w=10)
    hit = prog(t, 3.6, 4.0)
    if t > 2.8:
        u = prog(t, 2.8, 3.6)
        packet(p, 80, 900, ex, ey, u, ln=120, w=12)
    if hit > 0:
        place(cv, glow(220, LIGHT, 0.8 * hit * (0.7 + 0.3 * math.sin(t * 8))), ex, ey)
    eye(p, ex, ey, 1.2, hit)
    if t < 3.6:
        pill(cv, "Auge sieht: nichts", ex, ey + 170, "#8f96ad", scale=ease_out_back(prog(t, 1.0, 1.35)))
    else:
        pill(cv, "jetzt sichtbar!", ex, ey + 170, LIGHT, scale=ease_out_back(prog(t, 3.7, 4.05)))
    caption(cv, t, 0.2, 2.8, "Licht selbst ist *unsichtbar*", 500, size=96)
    caption(cv, t, 2.8, 9, "…bis es in dein *Auge* trifft", 500, size=96)
    return cv


# ------------------------------------------------------------ 3 Luft streut Licht
SUN3 = (170, 760)
PERSON = (560, 1640)
PARTS = [(rng.uniform(120, 1000), rng.uniform(860, 1460)) for _ in range(46)]
RAYS = []
for k in range(80):
    i = rng.randrange(len(PARTS))
    if k % 4 == 0:
        dx, dy = PERSON[0] - PARTS[i][0], PERSON[1] - 70 - PARTS[i][1]
        a = math.atan2(dy, dx)
    else:
        a = rng.uniform(0, 2 * math.pi)
    RAYS.append((i, a, 3.3 + k * 0.07))


def person(p, x, y, lit=0.0):
    p.line([(x - 20, y + 60), (x - 26, y + 150)], "#2d3a66", 26)
    p.line([(x + 20, y + 60), (x + 26, y + 150)], "#2d3a66", 26)
    p.rrect((x - 45, y - 40, x + 45, y + 80), 30, RED)
    p.circle(x, y - 85, 50, "#f6c9a8")
    p.circle(x + 18, y - 95, 7, INK)
    if lit > 0:
        p.circle(x + 18, y - 95, 7 + 6 * lit, mix(INK, LIGHT, lit))


def s3_luft(t):
    b = ease_in_out(prog(t, 3.8, 7.0))
    cv = blend_canvas(((0, "#0d1d45"), (1, "#20356e")), SKY, b)
    p = Pen(cv)
    p.poly([(0, 1780), (1080, 1780), (1080, 1920), (0, 1920)], "#3d8b4f")
    sun(cv, *SUN3, 70)
    for i, (x, y) in enumerate(PARTS):
        k = ease_out_back(prog(t, 0.4 + i * 0.03, 0.7 + i * 0.03))
        if k > 0:
            p.circle(x, y, 9 * k, mix("#9fc8ff", "#ffffff", 0.5))
    for i, a, t0 in RAYS:
        px, py = PARTS[i]
        u1 = prog(t, t0, t0 + 0.45)
        if u1 < 1:
            packet(p, SUN3[0], SUN3[1], px, py, u1, ln=50, w=6)
        else:
            u2 = prog(t, t0 + 0.45, t0 + 1.25)
            packet(p, px, py, px + math.cos(a) * 520, py + math.sin(a) * 520, u2, ln=50, w=6)
    lit = 0.6 + 0.4 * math.sin(t * 6) if t > 4.2 else 0
    person(p, *PERSON, lit)
    if 0.9 < t < 3.2:
        pill(cv, "winzige Luftteilchen", 600, 780, "#ffffff", prog(3.2 - t, 0, 0.2),
             ease_out_back(prog(t, 0.9, 1.25)))
    if t > 6.2:
        pill(cv, "der ganze Himmel leuchtet", 540, 760, "#ffffff", scale=ease_out_back(prog(t, 6.2, 6.55)))
    caption(cv, t, 0.2, 3.2, "Auf der Erde: Luft voller *Teilchen*", 500, size=90)
    caption(cv, t, 3.2, 12, "Sie werfen das Licht in *alle Richtungen*", 500, size=88)
    return cv


# ------------------------------------------------------------ 4 Weltall: keine Luft
SUN4 = (150, 1060)


def s4_weltall(t):
    cv = space(t, 0.5)
    p = Pen(cv)
    sun(cv, *SUN4, 80)
    fade = 1 - prog(t, 0.2, 1.2)
    if fade > 0:
        for x, y in PARTS:
            p.circle(x, y - 40, 9, mix("#05060f", "#9fc8ff", fade))
    ax, ay = 760, 1080 + 14 * math.sin(t * 1.5)
    for k in range(14):
        y = 760 + k * 50
        if abs(y - (ay - 40)) < 170:
            continue
        for j in range(3):
            u = ((t * 0.55 + j / 3 + k * 0.13) % 1.0)
            packet(p, SUN4[0], y, 1160, y, u, ln=90, w=7)
    glint = prog(t, 4.8, 5.4)
    visor = mix(GOLD, "#ffffff", glint * (0.6 + 0.4 * math.sin(t * 7)))
    if t > 4.6:
        u = prog(t, 4.6, 5.2)
        packet(p, SUN4[0], SUN4[1], ax, ay - 105, u, ln=110, w=10)
        if glint > 0:
            place(cv, glow(90, "#ffffff", 0.8 * glint), ax, ay - 105)
    astronaut(p, ax, ay, 1.0, visor)
    if 0.8 < t < 4.6:
        pill(cv, "keine Luft", 540, 1640, "#ffffff", prog(4.6 - t, 0, 0.2), ease_out_back(prog(t, 0.8, 1.15)))
    if t > 5.4:
        pill(cv, "nur die Sonne leuchtet", 540, 1640, LIGHT, scale=ease_out_back(prog(t, 5.4, 5.75)))
    caption(cv, t, 0.2, 4.6, "Im Weltall: *keine Luft* – Licht fliegt vorbei", 500, size=86)
    caption(cv, t, 4.6, 12, "Sonne grell – drumherum *schwarz*", 500, size=92)
    return cv


# ------------------------------------------------------------ 5 Taschenlampe
DUST = [(rng.uniform(0, 1), rng.uniform(-1, 1), rng.uniform(0, 6.3), rng.uniform(3, 7)) for _ in range(140)]


def s5_lampe(t):
    cv = canvas(ROOM)
    p = Pen(cv)
    p.poly([(880, 640), (1080, 560), (1080, 1820), (880, 1620)], "#1f2540")
    lx, ly = 210, 1150
    wx, wy, wh = 900, 1130, 170
    dust = ease_in_out(prog(t, 4.4, 5.6))
    beam_a = 0.06 + 0.5 * dust

    def beam(lp):
        lp.poly([(lx + 60, ly - 28), (wx, wy - wh), (wx, wy + wh), (lx + 60, ly + 28)], "#fff1b0")
    faded(cv, beam_a, beam)
    place(cv, glow(200, "#fff1b0", 0.9), wx + 10, wy)
    p.ellipse((wx - 20, wy - wh * 0.9, wx + 40, wy + wh * 0.9), "#fff6d0")
    # Staub
    if dust > 0:
        for u, v, ph, r in DUST:
            x = lerp(lx + 60, wx, u) + 20 * math.sin(t * 0.8 + ph)
            hh = lerp(28, wh, u)
            y = ly + v * hh * 1.25 + 25 * math.sin(t * 0.6 + ph * 2)
            inside = abs(y - ly) < hh
            col = mix("#151a2c", "#fff6d0" if inside else "#3a4160", dust)
            p.circle(x, y, r * (1.0 if inside else 0.7), col)
    # Taschenlampe
    p.rrect((lx - 150, ly - 32, lx + 20, ly + 32), 14, "#3c4560")
    p.poly([(lx + 10, ly - 32), (lx + 60, ly - 50), (lx + 60, ly + 50), (lx + 10, ly + 32)], "#59647f")
    p.rrect((lx - 90, ly - 40, lx - 50, ly - 30), 4, RED)
    if t < 4.2:
        pill(cv, "Strahl: kaum zu sehen", 540, 1520, "#8f96ad", prog(4.2 - t, 0, 0.2),
             ease_out_back(prog(t, 1.6, 1.95)))
    else:
        pill(cv, "mit Staub: leuchtet!", 540, 1520, LIGHT, scale=ease_out_back(prog(t, 5.0, 5.35)))
    caption(cv, t, 0.2, 4.2, "Taschenlampe im Dunkeln: Strahl *kaum zu sehen*", 500, size=84)
    caption(cv, t, 4.2, 12, "Mit *Staub* in der Luft: Er *leuchtet*!", 500, size=88)
    return cv


# ------------------------------------------------------------ Mond
CRATERS = [(rng.uniform(40, 1040), rng.uniform(1480, 1880), rng.uniform(20, 70)) for _ in range(16)]


def moonscape(cv, t, expo=0.0, horizon=1420):
    """Mondlandschaft; expo 0 = normale Belichtung, 1 = lang belichtet (Boden überstrahlt, Sterne da)."""
    p = Pen(cv)
    stars(p, t, expo, ymax=horizon)
    g = mix(MOON, "#ffffff", 0.85 * expo)
    gd = mix(MOON_DARK, "#f2f2f2", 0.85 * expo)
    pts = [(x, horizon + 25 * math.sin(x / 140) + 12 * math.sin(x / 37)) for x in range(0, 1101, 30)]
    p.poly(pts + [(1080, 1920), (0, 1920)], g)
    for x, y, r in CRATERS:
        if y - r * 0.35 > horizon + 40:
            p.ellipse((x - r, y - r * 0.35, x + r, y + r * 0.35), gd)
    # Fahne + Astronaut
    p.line([(250, horizon + 60), (250, horizon - 260)], "#dfe3ea", 8)
    p.rrect((256, horizon - 260, 420, horizon - 160), 6, mix("#3a6fd8", "#ffffff", 0.6 * expo))
    astronaut(p, 640, horizon - 160, 0.95, mix(GOLD, "#ffffff", 0.5 * expo))


def s6_mond(t):
    cv = canvas(SPACE)
    sun(cv, 180, 820, 60)
    moonscape(cv, t)
    if t > 1.2:
        pill(cv, "12 Uhr mittags", 760, 820, "#ffffff", scale=ease_out_back(prog(t, 1.2, 1.55)), size=46)
    caption(cv, t, 0.2, 9, "Auf dem *Mond*: mittags *schwarzer* Himmel", 500, size=88)
    return cv


# ------------------------------------------------------------ 7 Keine Sterne auf Fotos
def viewfinder(p, x0=70, y0=700, x1=1010, y1=1720, col="#ffffff"):
    L = 70
    for (x, y, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        p.line([(x + sx * L, y), (x, y), (x, y + sy * L)], col, 8)


def s7_fotos(t):
    cv = canvas(SPACE)
    sun(cv, 180, 820, 60)
    e = ease_in_out(prog(t, 3.8, 5.0)) * (1 - ease_in_out(prog(t, 6.6, 7.8)))
    moonscape(cv, t, expo=e)
    p = Pen(cv)
    viewfinder(p)
    if (t * 2) % 2 < 1.3:
        p.circle(860, 770, 14, RED)
    place(cv, text_sprite("REC", 34, weight="bold", stroke=0, color="#ffffff"), 925, 770)
    # Belichtungs-Regler
    k = ease_out_back(prog(t, 3.4, 3.8))
    if k > 0:
        y = 1000
        p.rrect((200, y - 10, 880, y + 10), 10, "#ffffff88")
        kx = lerp(260, 820, e)
        p.circle(kx, y, 30 * k, GOLD)
        place(cv, text_sprite("kurz", 36, weight="bold", stroke=0), 200, y - 55, k)
        place(cv, text_sprite("lang", 36, weight="bold", stroke=0), 880, y - 55, k)
        place(cv, text_sprite("Belichtung", 40, weight="bold", stroke=0, color=GOLD), 540, y - 60, k)
    if t < 3.4 and t > 1.0:
        place(cv, text_sprite("?", 200, color="#ffffff"), 820, 1060, ease_out_back(prog(t, 1.0, 1.4)))
    if e > 0.8:
        pill(cv, "Sterne da – Boden überstrahlt", 540, 1160, LIGHT)
    caption(cv, t, 0.2, 3.4, "Warum keine *Sterne* auf Mondfotos?", 500, size=90)
    caption(cv, t, 3.4, 12, "Kamera auf den hellen Boden eingestellt", 500, size=84)
    return cv


# ------------------------------------------------------------ 8 Ende
def s8_ende(t):
    cv = space(t, 0.8)
    p = Pen(cv)
    ex, ey = 700, 1620 - 280 * ease_out(prog(t, 0, 3.5))
    place(cv, glow(260, "#6fb3ff", 0.5), ex, ey)
    p.circle(ex, ey, 170, "#2f6fd6")
    for dx, dy, r in ((-60, -40, 60), (40, 30, 50), (-20, 80, 40), (90, -70, 35)):
        p.circle(ex + dx, ey + dy, r, "#3d9b5f")
    p.circle(ex - 80, ey - 90, 40, "#ffffff")
    p.circle(ex + 70, ey + 100, 34, "#ffffff")
    pts = [(x, 1560 + 25 * math.sin(x / 140) + 12 * math.sin(x / 37)) for x in range(0, 1101, 30)]
    p.poly(pts + [(1080, 1920), (0, 1920)], MOON)
    caption(cv, t, 0.1, 9, "Hättest du's *gewusst*?", 760, size=110)
    caption(cv, t, 1.6, 9, "Folge für mehr *Warum eigentlich?*", 1010, size=66)
    return cv


VIDEO = Video([
    (7.5, s1_einstieg, [(0.0, "Steig in eine Rakete. Nach wenigen Minuten wird der blaue Himmel pechschwarz – obwohl die Sonne voll scheint."),
                        (5.6, "Wie kann das sein?")]),
    (6.0, s2_unsichtbar, [(0.2, "Licht selbst kannst du nicht sehen – nur, wenn es in dein Auge trifft.")]),
    (9.5, s3_luft, [(0.2, "Auf der Erde ist die Luft voller winziger Teilchen."),
                    (3.2, "Sie werfen das Sonnenlicht in alle Richtungen – auch in deine Augen. Darum leuchtet der ganze Himmel.")]),
    (9.0, s4_weltall, [(0.2, "Im Weltall gibt es keine Luft. Das Licht fliegt einfach geradeaus an dir vorbei."),
                       (4.6, "Du siehst die Sonne grell strahlen – aber drumherum bleibt alles schwarz.")]),
    (9.0, s5_lampe, [(0.2, "Das kennst du: Eine Taschenlampe im dunklen Zimmer – den Strahl siehst du kaum."),
                     (4.2, "Erst mit Staub oder Nebel in der Luft leuchtet er plötzlich auf.")]),
    (5.5, s6_mond, [(0.2, "Deshalb ist auch auf dem Mond der Himmel mitten am Tag schwarz.")]),
    (9.5, s7_fotos, [(0.2, "Und warum sieht man auf Mondfotos keine Sterne?"),
                     (3.4, "Die Kamera war auf den hellen Boden eingestellt – dafür waren die Sterne zu schwach.")]),
    (4.2, s8_ende, [(0.2, "Hättest du es gewusst?"),
                    (1.7, "Folge für mehr: Warum eigentlich?")]),
])

if __name__ == "__main__":
    cli(VIDEO, __file__, cover_t=2.6)
