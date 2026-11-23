"""Folge 1: Warum ist der Himmel blau?  (~55 s, 9:16)

Rendern:   python3 videos/01_himmel_blau.py
Vorschau:  python3 videos/01_himmel_blau.py --stills
CapCut:    python3 videos/01_himmel_blau.py --capcut   (Ton aus assets/, Zeiten aus *_capcut.json)
"""
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ev.engine import (YELLOW, Pen, Video, blend_canvas, canvas, caption, ease_in_out,  # noqa: E402
                       ease_out, glow, layer, lerp, mix, place, prog, text_sprite)

DARK = ((0, "#0a1430"), (1, "#1b3a7a"))
SKY = ((0, "#2f7fe0"), (1, "#a9d6ff"))
SKY_DEEP = ((0, "#1f5fbf"), (0.75, "#7fbfff"), (1, "#7fbfff"))
VIOLET_BG = ((0, "#140c30"), (1, "#2b2370"))
SUNSET = ((0, "#2a1b5e"), (0.45, "#d9486b"), (0.8, "#ffb347"), (1, "#ffb347"))

BLUE = "#6CC4FF"
RED = "#FF5A5A"
PURPLE = "#C08BFF"
RAINBOW = ["#FF4D4D", "#FF9A3C", "#FFE14D", "#5CE65C", "#4DA8FF", "#4D5BFF", "#A64DFF"]


def cloud(p, cx, cy, s=1.0):
    for dx, dy, r in ((-70, 10, 55), (0, -20, 75), (75, 5, 60), (0, 25, 60)):
        p.circle(cx + dx * s, cy + dy * s, r * s, "#ffffff")


def sun(cv, x, y, r, color="#FFF3B0", glow_r=None, glow_a=0.8):
    place(cv, glow(int(glow_r or r * 3.2), color, glow_a), x, y)
    Pen(cv).circle(x, y, r, color)


# ------------------------------------------------------------ 1 Hook (3.5 s)
def s1_hook(t):
    cv = canvas(SKY)
    sun(cv, 540, 1380, 120 + 6 * math.sin(t * 4), glow_r=430)
    p = Pen(cv)
    cloud(p, 180 + t * 25, 1650, 1.1)
    cloud(p, 900 - t * 18, 1130, 0.8)
    caption(cv, t, 0.05, 9, "Warum ist der Himmel *blau*?", 700, size=118)
    caption(cv, t, 1.7, 9, "…und nicht *lila*?", 960, size=84, hl=PURPLE)
    return cv


# ------------------------------------------------------------ 2 Weißes Licht (6.5 s)
def s2_prisma(t):
    cv = canvas(DARK)
    sun(cv, 110, 1150, 70, glow_r=230)
    p = Pen(cv)
    cy = 1150
    # weißer Strahl
    pb = ease_out(prog(t, 0.3, 1.2))
    if pb > 0:
        p.line([(180, cy), (lerp(180, 420, pb), cy)], "#ffffff", 16)
    # Regenbogen-Fächer
    pr = ease_out(prog(t, 1.3, 2.4))
    if pr > 0:
        xe = lerp(540, 1100, pr)
        for k, col in enumerate(RAINBOW):
            ya = lerp(cy - 8 + k * 2.3, 1000 + k * 46, pr)
            yb = lerp(cy - 6 + k * 2.3, 1000 + (k + 1) * 46, pr)
            p.poly([(535, cy - 8 + k * 2.3), (xe, ya), (xe, yb), (535, cy - 6 + k * 2.3)], col)
    # Prisma
    p.poly([(480, cy - 150), (350, cy + 75), (610, cy + 75)], "#24417e", "#ffffff", 6)
    caption(cv, t, 0.2, 2.7, "Sonnenlicht sieht *weiß* aus…", 520)
    caption(cv, t, 2.7, 9, "…ist aber ein Mix aus *allen Farben*!", 520)
    return cv


# ------------------------------------------------------------ 3 Wellen (7 s)
def wave(p, t, y, amp, wl, color, reveal, speed=160):
    if reveal <= 0:
        return
    x_end = lerp(90, 990, reveal)
    pts = []
    x = 90.0
    while x <= x_end:
        pts.append((x, y + amp * math.sin((x - t * speed) / wl * 2 * math.pi)))
        x += 5
    p.line(pts, color, 12)


def s3_wellen(t):
    cv = canvas(DARK)
    p = Pen(cv)
    wave(p, t, 1000, 70, 380, RED, ease_out(prog(t, 1.6, 2.6)))
    wave(p, t, 1350, 70, 120, BLUE, ease_out(prog(t, 3.0, 4.0)))
    caption(cv, t, 1.7, 9, "Rot: *lange* Welle", 860, size=58, hl=RED)
    caption(cv, t, 3.0, 9, "Blau: *kurze* Welle", 1210, size=58, hl=BLUE)
    caption(cv, t, 0.2, 4.7, "Jede Farbe ist eine *Welle*", 480)
    caption(cv, t, 4.7, 9, "Und genau das macht den *Unterschied*…", 480)
    return cv


# ------------------------------------------------------------ 4 Streuung (10 s)
rng = random.Random(7)
MOLS = []
while len(MOLS) < 42:
    m = (rng.uniform(70, 1010), rng.uniform(920, 1460), rng.uniform(9, 14))
    if all((m[0] - o[0]) ** 2 + (m[1] - o[1]) ** 2 > 85 ** 2 for o in MOLS):
        MOLS.append(m)

PHOTONS = []
for i in range(120):
    t0 = 0.8 + i * 0.075
    if i % 2 == 0:  # rot: fliegt geradeaus
        PHOTONS.append(dict(t0=t0, c=RED, y=rng.uniform(930, 1450), sx=None))
    else:           # blau: trifft ein Teilchen und wird gestreut
        mx, my, mr = rng.choice([m for m in MOLS if 200 < m[0] < 900])
        ang = rng.choice([rng.uniform(-2.9, -0.5), rng.uniform(0.5, 2.9)])
        PHOTONS.append(dict(t0=t0, c=BLUE, y=my, sx=mx - mr - 6,
                            dx=math.cos(ang), dy=math.sin(ang)))
SPEED = 560


def photon_pos(ph, tt):
    dt = tt - ph["t0"]
    x = -20 + dt * SPEED
    if ph["sx"] is None or x < ph["sx"]:
        return x, ph["y"], False
    rest = (x - ph["sx"])
    return ph["sx"] + ph["dx"] * rest, ph["y"] + ph["dy"] * rest, True


def s4_streuung(t):
    cv = canvas(DARK)
    p = Pen(cv)
    mol_a = ease_out(prog(t, 0.1, 0.8))
    for x, y, r in MOLS:
        p.circle(x, y, r * mol_a, "#9fb3d9")
    for ph in PHOTONS:
        if t < ph["t0"]:
            continue
        x, y, hit = photon_pos(ph, t)
        if x > 1200 or x < -200 or y < 600 or y > 2000:
            continue
        trail = [photon_pos(ph, max(ph["t0"], t - k * 0.03))[:2] for k in (4, 3, 2, 1, 0)]
        p.line(trail, mix(ph["c"], "#0a1430", 0.45), 7)
        p.circle(x, y, 10, ph["c"])
        if ph["sx"] is not None:
            t_hit = ph["t0"] + (ph["sx"] + 20) / SPEED
            k = prog(t, t_hit, t_hit + 0.35)
            if 0 < k < 1:
                p.circle(ph["sx"], ph["y"], 12 + 40 * k, None, mix(BLUE, "#1b3a7a", k), 4)
    # Legende
    la = prog(t, 2.8, 3.1)
    if la > 0:
        lg = Pen(cv)
        lg.circle(190, 790, 14, RED)
        lg.circle(600, 790, 14, BLUE)
        place(cv, text_sprite("fliegt durch", 42, weight="bold", stroke=6), 340, 790, alpha=la)
        place(cv, text_sprite("wird gestreut", 42, weight="bold", stroke=6), 765, 790, alpha=la)
    caption(cv, t, 0.2, 2.8, "Die Luft ist voller winziger *Teilchen*", 480)
    caption(cv, t, 2.8, 6.7, "*Blaues* Licht prallt daran ab und wird *verstreut*", 480, size=78)
    caption(cv, t, 6.7, 11, "Blau sogar fast *6-mal* stärker als Rot!", 480, size=80)
    return cv


# ------------------------------------------------------------ 5 Von überall (6 s)
def s5_ueberall(t):
    cv = canvas(SKY_DEEP)
    p = Pen(cv)
    cloud(p, 160 + t * 15, 1250, 0.7)
    # Boden
    p.poly([(0, 1580), (300, 1540), (650, 1570), (1080, 1530), (1080, 1920), (0, 1920)], "#1c3b2a")
    # Strichmännchen
    hx, hy = 540, 1400
    p.line([(hx, hy + 45), (hx, hy + 140)], NAVY_S, 12)
    p.line([(hx, hy + 140), (hx - 40, hy + 210)], NAVY_S, 12)
    p.line([(hx, hy + 140), (hx + 40, hy + 210)], NAVY_S, 12)
    p.line([(hx - 55, hy + 70), (hx, hy + 80), (hx + 55, hy + 70)], NAVY_S, 12)
    p.circle(hx, hy, 42, NAVY_S)
    p.circle(hx - 13, hy - 12, 6, "#ffffff")
    p.circle(hx + 13, hy - 12, 6, "#ffffff")
    # Pfeile aus allen Richtungen
    for k in range(13):
        ang = math.radians(195 + k * (150 / 12))
        start = 0.5 + ((k * 5) % 13) * 0.16
        g = ease_out(prog(t, start, start + 0.55))
        if g <= 0:
            continue
        x0, y0 = hx + math.cos(ang) * 640, hy + math.sin(ang) * 640
        x1, y1 = hx + math.cos(ang) * 135, hy + math.sin(ang) * 135
        p.arrow(x0, y0, lerp(x0, x1, g), lerp(y0, y1, g), "#e6f6ff", 9, 30)
    caption(cv, t, 0.2, 9, "So kommt *blaues* Licht von *überall* am Himmel zu dir", 460, size=78)
    return cv


NAVY_S = "#0b1a3a"


# ------------------------------------------------------------ 6 Warum nicht lila (8 s)
def card(cv, t, start, y, text):
    k = ease_out(prog(t, start, start + 0.45))
    if k <= 0:
        return
    off = lerp(-1000, 0, k)
    lay, lp = layer()
    lp.rrect((90 + off, y - 100, 990 + off, y + 100), 34, "#ffffff22", "#ffffff66", 3)
    cv.alpha_composite(lay)
    place(cv, text_sprite(text, 54, weight="bold", stroke=0, max_w=800, hl=PURPLE),
          540 + off, y)


def s6_lila(t):
    cv = canvas(VIOLET_BG)
    caption(cv, t, 0.1, 3.1, "Aber Moment: *Violett* wird sogar noch *stärker* gestreut!", 520,
            size=78, hl=PURPLE)
    caption(cv, t, 3.1, 11, "Warum ist der Himmel dann nicht *lila*?", 500, size=82, hl=PURPLE)
    card(cv, t, 5.0, 900, "1. Die Sonne strahlt *weniger Violett* ab")
    card(cv, t, 7.6, 1160, "2. Unsere Augen sehen *Blau* viel besser")
    return cv


# ------------------------------------------------------------ 7 Sonnenuntergang (8.5 s)
def s7_sunset(t):
    k = ease_in_out(prog(t, 0.3, 3.5))
    cv = blend_canvas(SKY, SUNSET, k)
    sy = lerp(1000, 1530, ease_in_out(prog(t, 0.3, 8.0)))
    col = mix("#FFF3B0", "#FF7A3D", k)
    sun(cv, 540, sy, 120, color=col, glow_r=460, glow_a=0.9)
    p = Pen(cv)
    p.poly([(0, 1540), (220, 1490), (480, 1535), (760, 1480), (1080, 1525),
            (1080, 1920), (0, 1920)], "#1a0f2e")
    caption(cv, t, 0.2, 2.0, "Und beim *Sonnenuntergang*?", 480, size=88)
    caption(cv, t, 2.0, 4.6, "Das Licht muss einen *viel längeren Weg* durch die Luft", 480, size=78)
    caption(cv, t, 4.6, 9, "Das Blau ist unterwegs weggestreut – *Rot & Orange* bleiben übrig",
            480, size=74)
    return cv


# ------------------------------------------------------------ 8 Outro (5 s)
def s8_outro(t):
    cv = canvas(DARK)
    caption(cv, t, 0.1, 9, "Hättest du's *gewusst*?", 760, size=110)
    caption(cv, t, 1.6, 9, "Folge für mehr *Warum eigentlich?*", 1010, size=66)
    caption(cv, t, 3.8, 9, "Nächstes Mal: Warum sind Sonnenuntergänge auf dem Mars *blau*?",
            1260, size=52, hl=BLUE, weight="bold")
    return cv


VIDEO = Video([
    (3.5, s1_hook, [(0.1, "Warum ist der Himmel blau?"),
                    (1.7, "Und nicht lila?")]),
    (6.5, s2_prisma, [(0.3, "Sonnenlicht sieht weiß aus."),
                      (2.7, "Aber in Wahrheit ist es ein Mix aus allen Farben.")]),
    (7.0, s3_wellen, [(0.2, "Jede Farbe ist eine Welle."),
                      (1.8, "Rot hat lange Wellen."),
                      (3.1, "Blau hat kurze."),
                      (4.8, "Und genau das macht den Unterschied.")]),
    (10.0, s4_streuung, [(0.3, "Die Luft ist voller winziger Teilchen."),
                         (2.9, "Blaues Licht prallt daran ab, und wird in alle Richtungen verstreut."),
                         (6.8, "Fast sechsmal stärker als rotes Licht!")]),
    (4.6, s5_ueberall, [(0.4, "Deshalb kommt blaues Licht von überall am Himmel zu dir.")]),
    (10.6, s6_lila, [(0.1, "Aber Moment! Violett wird sogar noch stärker gestreut."),
                     (3.2, "Warum ist der Himmel dann nicht lila?"),
                     (5.2, "Erstens: Die Sonne strahlt weniger Violett ab."),
                     (7.8, "Zweitens: Unsere Augen sehen Blau viel besser.")]),
    (8.8, s7_sunset, [(0.3, "Und beim Sonnenuntergang?"),
                      (2.1, "Das Licht muss einen viel längeren Weg durch die Luft."),
                      (4.7, "Das Blau ist unterwegs weggestreut. Rot und Orange bleiben übrig.")]),
    (7.6, s8_outro, [(0.2, "Hättest du es gewusst?"),
                     (1.7, "Folge für mehr: Warum eigentlich?"),
                     (3.9, "Nächstes Mal: Warum sind Sonnenuntergänge auf dem Mars blau?")]),
])

if __name__ == "__main__":
    name = os.path.splitext(os.path.basename(__file__))[0]
    if "--stills" in sys.argv:
        d = os.path.join(ROOT, "output", name + "_stills")
        os.makedirs(d, exist_ok=True)
        for ts in sys.argv[sys.argv.index("--stills") + 1:] or [3, 9, 15, 24, 31, 40, 48, 53]:
            VIDEO.still(float(ts), os.path.join(d, f"t{float(ts):05.1f}.png"))
        print("Stills in", d)
    elif "--capcut" in sys.argv:
        # eigene Sprachaufnahme (z. B. aus CapCut): Animationen werden daran angepasst
        import json
        cfg = json.load(open(os.path.join(ROOT, "videos", name + "_capcut.json")))
        VIDEO.fit_to_audio(cfg["starts"], cfg["audio_end"])
        VIDEO.render(os.path.join(ROOT, "output", name + "_capcut.mp4"),
                     audio=os.path.join(ROOT, cfg["audio"]))
    else:
        suffix = "_ohne_stimme" if os.environ.get("EV_NOVOICE") else ""
        out = os.path.join(ROOT, "output", name + suffix + ".mp4")
        VIDEO.render(out)
        VIDEO.still(2.8, os.path.join(ROOT, "output", name + "_cover.png"))
