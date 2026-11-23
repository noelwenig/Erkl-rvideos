"""Folge 2: Warum fühlt sich die Zeit schneller an, je älter wir werden?  (9:16)

Rendern:   python3 videos/02_zeit.py            (ElevenLabs, Stimme Brian)
Vorschau:  python3 videos/02_zeit.py --stills
"""
import math
import os
import random
import sys
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image  # noqa: E402

from ev.engine import (S, Pen, Video, canvas, caption, cli, ease_in_out, ease_out, layer,  # noqa: E402
                       ease_out_back, lerp, mix, place, prog, text_sprite)

BG = ((0, "#1a0b2e"), (1, "#3d1a4f"))
BG_GREY = ((0, "#1c1a24"), (1, "#34303f"))
ORANGE = "#FF9F43"
PINK = "#FF6B9A"
TEAL = "#4ECDC4"
GOLD = "#FFD23F"
VIOLET = "#A66CFF"
GREY = "#7a7489"
COLORS = [ORANGE, PINK, TEAL, GOLD, VIOLET, "#5CE65C"]


def pill(cv, text, cx, cy, color, alpha=1.0, scale=1.0, size=44):
    spr = text_sprite(text, size, weight="bold", stroke=0, color="#1a0b2e", max_w=900)
    w, h = spr.width / S + 56, spr.height / S + 26
    img = Image.new("RGBA", (int(w * S) + 4, int(h * S) + 4), (0, 0, 0, 0))
    Pen(img).rrect((0, 0, w, h), h / 2, color)
    place(img, spr, w / 2, h / 2)
    place(cv, img, cx, cy, scale, alpha)


# ------------------------------------------------------------ 1 Einstieg
MONTHS = ["JULI", "AUGUST", "SEPTEMBER", "OKTOBER", "NOVEMBER", "DEZEMBER"]
FLIPS = [2.0, 3.9, 4.2, 4.45, 4.65]  # Zeitpunkte, an denen ein Blatt abfliegt


@lru_cache(None)
def calendar_page(i):
    w, h = 460, 480
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    p = Pen(img)
    p.rrect((0, 0, w, h), 36, "#ffffff")
    p.rrect((0, 0, w, 120), 36, ORANGE if i < 5 else "#E84A5F")
    p.d.rectangle([0, 80 * S, w * S, 120 * S], fill=(232, 74, 95, 255) if i == 5 else (255, 159, 67, 255))
    place(img, text_sprite(MONTHS[i], 54, stroke=0), w / 2, 62)
    for r in range(5):
        for c in range(7):
            n = r * 7 + c + 1
            if n > 31:
                continue
            x, y = 45 + c * 62, 160 + r * 62
            hl = (i == 5 and n == 24)
            p.rrect((x - 22, y - 22, x + 22, y + 22), 10, "#E84A5F" if hl else "#ece6f5")
            if hl:
                place(img, text_sprite("24", 26, stroke=0), x, y)
    return img


def s1_einstieg(t):
    cv = canvas(BG)
    idx = sum(1 for f in FLIPS if t >= f)  # so viele Blätter sind schon abgerissen
    cx, cy = 540, 1170
    place(cv, calendar_page(idx), cx, cy)
    # fliegendes Blatt
    if idx > 0:
        f0 = FLIPS[idx - 1]
        dur = 0.6 if f0 < 3 else 0.35
        k = prog(t, f0, f0 + dur)
        if k < 1:
            spr = calendar_page(idx - 1).rotate(-55 * ease_out(k), expand=True,
                                                resample=Image.BILINEAR)
            place(cv, spr, cx + 520 * ease_in_out(k), cy - 700 * ease_in_out(k), 1 - 0.3 * k, 1 - k)
    caption(cv, t, 0.1, 3.6, "Erinnerst du dich an die *endlosen* Sommerferien?", 520)
    caption(cv, t, 3.6, 9, "Und heute? *Zack* – schon wieder Weihnachten!", 520)
    return cv


# ------------------------------------------------------------ 2 Die Rechnung
def s2_rechnung(t):
    cv = canvas(BG)
    p = Pen(cv)
    k = ease_in_out(prog(t, 3.9, 5.6))
    age = int(round(lerp(5, 50, k)))
    x0, x1, y = 90, 990, 1110
    seg = (x1 - x0) / age
    reveal = ease_out(prog(t, 0.3, 1.1))
    for i in range(age):
        a = x0 + i * seg
        if a > lerp(x0, x1, reveal):
            break
        last = i == age - 1
        p.rrect((a + 1.5, y - 45, a + seg - 1.5, y + 45), min(10, seg / 3),
                ORANGE if last else "#5a3d73")
    if reveal > 0.95:
        place(cv, text_sprite(f"{age} Jahre Leben", 52, weight="bold", stroke=0), 540, 990)
        place(cv, text_sprite("= 1 Jahr", 40, weight="bold", stroke=0, color=ORANGE),
              x1 - seg / 2 - 60 if age > 10 else x1 - seg / 2, 1205)
        pop = 1 + 0.15 * math.exp(-8 * max(0, t - 3.9)) * (t > 3.9)
        place(cv, text_sprite(f"*1/{age}*", 170, hl=ORANGE), 540, 1400, pop)
    caption(cv, t, 0.2, 3.9, "Mit *5 Jahren* ist ein Jahr *1/5* deines Lebens", 520)
    caption(cv, t, 3.9, 9, "Mit *50* nur noch *1/50*", 520, size=96)
    return cv


# ------------------------------------------------------------ 3 Neues
NEW = [("Erster Schultag", ORANGE), ("Das Meer", TEAL), ("Fahrradfahren", PINK),
       ("Schnee", "#9fd8ff"), ("Zoo", GOLD), ("Zelten", VIOLET)]
rng = random.Random(3)
SLOTS = [(rng.uniform(190, 890), rng.uniform(1370, 1500)) for _ in range(40)]


def memory_box(cv, label="Gedächtnis"):
    lay, p = layer()
    p.rrect((130, 1320, 950, 1550), 40, "#ffffff14", "#ffffff80", 4)
    cv.alpha_composite(lay)
    place(cv, text_sprite(label, 42, weight="bold", stroke=0, color="#d9c9ee"), 540, 1280)


def s3_neues(t):
    cv = canvas(BG)
    memory_box(cv)
    p = Pen(cv)
    for i, (word, col) in enumerate(NEW):
        t0 = 0.9 + i * 0.55
        k = prog(t, t0, t0 + 1.0)
        if k <= 0:
            continue
        sx, sy = (260 if i % 2 == 0 else 820), 820 + (i // 2) * 120
        tx, ty = SLOTS[i]
        if k < 0.45:
            pill(cv, word, sx, sy, col, scale=ease_out_back(k / 0.45))
        else:
            m = ease_in_out((k - 0.45) / 0.55)
            if m < 1:
                pill(cv, word, lerp(sx, tx, m), lerp(sy, ty, m), col, scale=lerp(1, 0.25, m),
                     alpha=1 - 0.5 * m)
            else:
                p.circle(tx, ty, 20, col)
    # Leuchten der gespeicherten Erinnerungen
    if t > 4.2:
        g = 0.5 + 0.5 * math.sin((t - 4.2) * 6)
        for i, (_, col) in enumerate(NEW):
            if t > 0.9 + i * 0.55 + 1.0:
                p.circle(*SLOTS[i], 26 + 6 * g, None, col, 3)
    caption(cv, t, 0.2, 4.2, "Als Kind ist fast *alles neu*", 500, size=88)
    caption(cv, t, 4.2, 9, "Neues speichert dein Gehirn *besonders gründlich*", 500, size=80)
    return cv


# ------------------------------------------------------------ 4 Routine
ROUTINE = ["Arbeit", "Einkaufen", "Serie", "Schlafen"]


def s4_routine(t):
    cv = canvas(BG_GREY)
    memory_box(cv)
    m = ease_in_out(prog(t, 4.0, 5.2))
    p = Pen(cv)
    for i in range(20):
        r, c = divmod(i, 4)
        t0 = 0.4 + i * 0.13
        if t < t0:
            continue
        a = ease_out_back(prog(t, t0, t0 + 0.3))
        x, y = 175 + c * 243, 700 + r * 105
        tx, ty = 540, 1435
        x, y = lerp(x, tx, m), lerp(y, ty, m)
        if m < 1:
            img_w = 220 * a * (1 - 0.5 * m)
            p.rrect((x - img_w / 2, y - 40 * a, x + img_w / 2, y + 40 * a), 18,
                    mix("#5d576b", "#4a4557", m))
            place(cv, text_sprite(ROUTINE[i % 4], 34, weight="bold", stroke=0, color="#cfc9dc"),
                  x, y, a * (1 - 0.5 * m), 1 - m)
    if m >= 1:
        p.circle(540, 1435, 22, GREY)
    caption(cv, t, 0.2, 4.0, "Als Erwachsener: *Routine*", 500, size=92)
    caption(cv, t, 4.0, 9, "Routine hinterlässt *kaum Erinnerungen*", 500, size=84)
    return cv


# ------------------------------------------------------------ 5 Rückblick
DOTS_KID = [(rng.uniform(0.02, 0.98), rng.choice(COLORS)) for _ in range(28)]
DOTS_NOW = [0.15, 0.4, 0.62, 0.85]


def timeline(cv, y, length, label, dots, x0=100, reveal=1.0):
    p = Pen(cv)
    x1 = x0 + length * reveal
    p.line([(x0, y), (x1, y)], "#7d6a96", 8)
    place(cv, text_sprite(label, 44, weight="bold", stroke=0, color="#d9c9ee"), x0 + 110, y - 75)
    for pos, col in dots:
        if pos <= reveal:
            p.circle(x0 + pos * length, y, 17, col)


def s5_rueckblick(t):
    cv = canvas(BG)
    r = ease_out(prog(t, 0.4, 1.6))
    timeline(cv, 950, 880, "Kindheit", DOTS_KID, reveal=r)
    shrink = lerp(880, 330, ease_in_out(prog(t, 4.3, 5.6)))
    timeline(cv, 1330, shrink, "Heute", [(d, GREY) for d in DOTS_NOW],
             reveal=ease_out(prog(t, 1.4, 2.6)))
    if t > 4.6:
        place(cv, text_sprite("fühlt sich *kurz* an", 46, weight="bold", stroke=0, hl=ORANGE),
              100 + shrink + 220, 1330, alpha=prog(t, 4.6, 5.0))
    caption(cv, t, 0.2, 4.3, "Dein Gehirn misst Zeit an deinen *Erinnerungen*", 520, size=84)
    caption(cv, t, 4.3, 9, "Wenig Erinnerungen = *kurzes Jahr*", 520, size=88)
    return cv


# ------------------------------------------------------------ 6 Der Tipp
TIPS = [("Neues ausprobieren", ORANGE), ("Reisen", TEAL), ("Etwas lernen", PINK),
        ("Anderer Heimweg", GOLD)]
DOTS_TIP = [(rng.uniform(0.03, 0.97), rng.choice(COLORS)) for _ in range(22)]


def s6_tipp(t):
    cv = canvas(BG)
    grow = ease_in_out(prog(t, 7.0, 8.4))
    length = lerp(330, 880, grow)
    fill = prog(t, 3.2, 7.2)
    dots = [(d, GREY) for d in DOTS_NOW] + [
        (pos, col) for i, (pos, col) in enumerate(DOTS_TIP) if i / len(DOTS_TIP) < fill]
    timeline(cv, 1330, length, "Dein Jahr", dots)
    for i, (word, col) in enumerate(TIPS):
        t0 = 2.8 + i * 0.9
        k = prog(t, t0, t0 + 0.35)
        if k > 0:
            pill(cv, word, 290 if i % 2 == 0 else 790, 820 + (i // 2) * 125, col,
                 scale=ease_out_back(k))
    caption(cv, t, 0.2, 2.6, "Die gute Nachricht: Du kannst das *ändern*!", 520, size=88)
    caption(cv, t, 2.6, 7.0, "Mach öfter *etwas Neues*", 520, size=92)
    caption(cv, t, 7.0, 11, "Mehr Neues = *längeres Jahr*", 520, size=92)
    return cv


# ------------------------------------------------------------ 7 Ende
def s7_ende(t):
    cv = canvas(BG)
    caption(cv, t, 0.1, 9, "Hättest du's *gewusst*?", 760, size=110)
    caption(cv, t, 1.6, 9, "Folge für mehr *Warum eigentlich?*", 1010, size=66)
    return cv


VIDEO = Video([
    (7.0, s1_einstieg, [(0.1, "Erinnerst du dich, wie endlos die Sommerferien als Kind waren?"),
                        (3.6, "Und heute?"),
                        (4.4, "Zack – schon wieder Weihnachten.")]),
    (7.5, s2_rechnung, [(0.2, "Mit fünf Jahren ist ein Jahr ein Fünftel deines ganzen Lebens."),
                        (3.9, "Mit fünfzig nur noch ein Fünfzigstel.")]),
    (7.0, s3_neues, [(0.2, "Als Kind ist fast alles neu: der erste Schultag, das erste Mal am Meer."),
                     (4.2, "Und Neues speichert dein Gehirn besonders gründlich.")]),
    (6.5, s4_routine, [(0.2, "Als Erwachsener wiederholt sich vieles: Arbeit, Einkaufen, Serie, schlafen."),
                       (4.0, "Und Routine hinterlässt kaum Erinnerungen.")]),
    (7.0, s5_rueckblick, [(0.2, "Wenn du zurückblickst, misst dein Gehirn die Zeit an deinen Erinnerungen."),
                          (4.3, "Wenige Erinnerungen – und das Jahr fühlt sich kurz an.")]),
    (9.5, s6_tipp, [(0.2, "Die gute Nachricht: Du kannst das ändern."),
                    (2.6, "Probier Neues aus, reise, lerne etwas – oder nimm einfach mal einen anderen Weg nach Hause."),
                    (7.0, "Mehr Neues, mehr Erinnerungen – und dein Jahr fühlt sich wieder länger an.")]),
    (4.2, s7_ende, [(0.2, "Hättest du es gewusst?"),
                    (1.7, "Folge für mehr: Warum eigentlich?")]),
])

if __name__ == "__main__":
    cli(VIDEO, __file__, cover_t=1.5)
