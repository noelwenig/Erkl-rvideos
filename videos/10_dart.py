"""Folge 10: Warum sind die Zahlen auf der Dartscheibe so durcheinander?  (9:16, Kurzformat ~38 s)

Rendern:   python3 videos/10_dart.py            (ElevenLabs, Stimme Brian, 12 % schneller)
Vorschau:  python3 videos/10_dart.py --stills
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image, ImageDraw  # noqa: E402

from ev import tts  # noqa: E402
from ev.engine import (S, Pen, Video, canvas, caption, cli, ease_in_out, ease_out,  # noqa: E402
                       ease_out_back, glow, layer, lerp, mix, place, prog, rgba, text_sprite)

tts.TEMPO = 1.12

PUB = ((0, "#24160f"), (0.55, "#3a2418"), (1, "#1c110b"))
SEPIA_BG = ((0, "#3b2a1a"), (0.6, "#5a4128"), (1, "#2e2014"))
BLACK = "#1b1b1b"
CREAM = "#f3e6c8"
RED = "#d6332e"
GREEN = "#1f8f4e"
GOLD = "#FFD23F"
INK = "#1a0f08"

ORDER = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5]
SORTED = [20] + list(range(1, 20))
# Maße in mm (offizielle Scheibe)
R_BOARD, R_DO, R_DI, R_TO, R_TI, R_OB, R_B = 225, 170, 162, 107, 99, 15.9, 6.35
R_NUM = 197
BX, BY, BR = 540, 1160, 380   # Standard-Position der Scheibe


def pill(cv, text, cx, cy, color, alpha=1.0, scale=1.0, size=42, fg=INK):
    spr = text_sprite(text, size, weight="bold", stroke=0, color=fg, max_w=900)
    w, h = spr.width / S + 52, spr.height / S + 24
    img = Image.new("RGBA", (int(w * S) + 4, int(h * S) + 4), (0, 0, 0, 0))
    Pen(img).rrect((0, 0, w, h), h / 2, color)
    place(img, spr, w / 2, h / 2)
    place(cv, img, cx, cy, scale, alpha)


def cam(cv, t, z0=1.0, zoom_dur=0.7, shake_at=None, shake_dur=0.6, amp=14):
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


def pub(t, stops=PUB):
    cv = canvas(stops)
    p = Pen(cv)
    for i in range(9):
        x = 60 + i * 130
        p.line([(x, 0), (x, 1920)], mix(stops[1][1], "#000000", 0.25), 4, caps=False)
    place(cv, glow(620, "#ffcf8a", 0.22), BX, BY)
    return cv


# ------------------------------------------------------------ Dartscheibe
def seg_angle(pos):
    """Mittelwinkel (PIL-Grad, im Uhrzeigersinn ab 3 Uhr) der Position pos (0 = oben)."""
    return -90 + 18 * pos


def polar(cx, cy, R, pos, r_mm, off=0.0):
    a = math.radians(seg_angle(pos) + off)
    k = R / R_BOARD
    return cx + math.cos(a) * r_mm * k, cy + math.sin(a) * r_mm * k


def board(cv, cx, cy, R, num_angles=None, sepia=0.0, highlight=None):
    """num_angles: {zahl: winkel_in_positionen} für animierte Zahlen; highlight: {position: farbe}."""
    d = ImageDraw.Draw(cv)
    k = R / R_BOARD * S

    def col(c):
        return rgba(mix(c, "#b08a5a", sepia * 0.85)) if sepia else rgba(c)

    def circ(r, c):
        d.ellipse([cx * S - r * k, cy * S - r * k, cx * S + r * k, cy * S + r * k], fill=col(c))

    circ(R_BOARD, "#111111")
    for pos in range(20):
        a0, a1 = seg_angle(pos) - 9, seg_angle(pos) + 9
        single = BLACK if pos % 2 == 0 else CREAM
        ring = RED if pos % 2 == 0 else GREEN
        for r, c in ((R_DO, ring), (R_DI, single), (R_TO, ring), (R_TI, single)):
            d.pieslice([cx * S - r * k, cy * S - r * k, cx * S + r * k, cy * S + r * k], a0, a1, fill=col(c))
    circ(R_OB, GREEN)
    circ(R_B, RED)
    # Drahtring
    for r in (R_DO, R_DI, R_TO, R_TI):
        d.ellipse([cx * S - r * k, cy * S - r * k, cx * S + r * k, cy * S + r * k],
                  outline=col("#c9c9c9"), width=max(1, int(1.2 * S)))
    if highlight:
        lay = Image.new("RGBA", cv.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay)
        for pos, c in highlight.items():
            a0, a1 = seg_angle(pos) - 9, seg_angle(pos) + 9
            ld.pieslice([cx * S - R_DO * k, cy * S - R_DO * k, cx * S + R_DO * k, cy * S + R_DO * k],
                        a0, a1, fill=rgba(c))
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * 0.6)))
        cv.alpha_composite(lay)
    # Zahlen (beim starken Zoom ausblenden)
    if R > 700:
        return
    for i, n in enumerate(ORDER):
        posf = num_angles[n] if num_angles else i
        a = math.radians(-90 + 18 * posf)
        x = cx + math.cos(a) * R_NUM * R / R_BOARD
        y = cy + math.sin(a) * R_NUM * R / R_BOARD
        place(cv, text_sprite(str(n), max(10, int(R * 0.1)), color=mix("#ffffff", "#e8d2a8", sepia),
                              stroke=0, weight="bold"), x, y)


def shuffle_angles(u):
    """u=0: echte Reihenfolge, u=1: sortiert wie eine Uhr."""
    out = {}
    for n in ORDER:
        a0, a1 = ORDER.index(n), SORTED.index(n)
        dlt = (a1 - a0 + 10) % 20 - 10
        out[n] = a0 + dlt * u
    return out


def dart(p, x, y, s=1.0, col="#e8c547"):
    """Steckender Dartpfeil (Spitze bei x, y), schräg nach rechts oben."""
    dx, dy = 0.55, -0.83
    pts = lambda L: (x + dx * L * s, y + dy * L * s)  # noqa: E731
    p.line([(x, y), pts(26)], "#d9d9d9", 5 * s)
    p.line([pts(26), pts(95)], "#8a8f99", 16 * s)
    p.line([pts(95), pts(150)], "#5a5f6a", 7 * s)
    fx, fy = pts(150)
    nx, ny = -dy, dx
    p.poly([pts(120), (fx + nx * 34 * s, fy + ny * 34 * s), pts(165)], col)
    p.poly([pts(120), (fx - nx * 34 * s, fy - ny * 34 * s), pts(165)], mix(col, "#000000", 0.25))


def flying_dart(p, tx, ty, u, s=1.0):
    """Pfeil fliegt von rechts unten zum Ziel (u 0..1)."""
    if u <= 0:
        return
    sx, sy = tx + 700, ty + 900
    k = ease_in_out(u)
    dart(p, lerp(sx, tx, k), lerp(sy, ty, k) - 140 * math.sin(k * math.pi), s * lerp(1.6, 1.0, k))


def score(cv, text, x, y, col, t, t0):
    k = ease_out_back(prog(t, t0, t0 + 0.3))
    if k > 0:
        place(cv, text_sprite(text, 84, color=col), x, y - 60 * prog(t, t0, t0 + 1.2), k,
              1 - prog(t, t0 + 1.4, t0 + 1.8))


# ------------------------------------------------------------ 1 Einstieg (Hook)
HIT1 = (1, 135, 3)      # Position 1 (=Zahl 1), Radius mm, Winkelversatz


def s1_einstieg(t):
    cv = pub(t)
    hit = 0.7
    hl = {1: "#ff2a2a"} if t > hit and (t * 4) % 1 < 0.6 else None
    board(cv, BX, BY, BR, highlight=hl)
    p = Pen(cv)
    tx, ty = polar(BX, BY, BR, *HIT1)
    if t < hit:
        flying_dart(p, tx, ty, prog(t, 0.0, hit))
    else:
        dart(p, tx, ty)
    if t > 1.5:
        place(cv, text_sprite("?", 220, color="#ffffff"), 880, 760, ease_out_back(prog(t, 1.5, 1.9)))
    cv = cam(cv, t, z0=1.12, shake_at=hit, shake_dur=0.5)
    caption(cv, t, -1, 9, "Die *20* direkt neben der *1*?!", 470, size=100)
    return cv


# ------------------------------------------------------------ 2 Sortieren
def s2_sortiert(t):
    cv = pub(t)
    u = ease_in_out(prog(t, 0.5, 2.6))
    board(cv, BX, BY, BR, num_angles=shuffle_angles(u))
    if t > 2.6:
        pill(cv, "der Reihe nach – wie eine Uhr", 540, 1680, "#ffffff", scale=ease_out_back(prog(t, 2.6, 2.95)),
             size=44)
    caption(cv, t, 0.2, 9, "Was, wenn sie *sortiert* wären?", 470, size=96)
    return cv


# ------------------------------------------------------------ 3 Leichtes Spiel
EASY = [(19, 120, 4, 18, 1.2), (0, 60, -5, 20, 2.0), (18, 150, -2, 19, 2.8)]


def s3_leicht(t):
    cv = pub(t)
    hl = {18: GREEN, 19: GREEN, 0: GREEN} if t > 0.4 else None
    board(cv, BX, BY, BR, num_angles=shuffle_angles(1.0), highlight=hl)
    p = Pen(cv)
    for pos, r, off, n, t0 in EASY:
        tx, ty = polar(BX, BY, BR, pos, r, off)
        if t < t0:
            flying_dart(p, tx, ty, prog(t, t0 - 0.45, t0), 0.8)
        else:
            dart(p, tx, ty, 0.8)
    for i, (pos, r, off, n, t0) in enumerate(EASY):
        score(cv, f"+{n}", 300 + i * 240, 700, GOLD, t, t0)
    if t > 3.3:
        pill(cv, "zu einfach!", 540, 1680, GREEN, scale=ease_out_back(prog(t, 3.3, 3.65)), fg="#ffffff", size=50)
    caption(cv, t, 0.2, 9, "Dann einfach auf *18–19–20* zielen", 470, size=92)
    return cv


# ------------------------------------------------------------ 4 Gemischt
def s4_gemischt(t):
    cv = pub(t)
    u = 1 - ease_in_out(prog(t, 0.4, 2.4))
    hl = None
    if t > 3.4:
        hl = {0: GOLD, 19: RED, 1: RED}
    board(cv, BX, BY, BR, num_angles=shuffle_angles(u), highlight=hl)
    if t < 3.4:
        if t > 2.4:
            pill(cv, "groß neben klein", 540, 1680, "#ffffff", scale=ease_out_back(prog(t, 2.4, 2.75)), size=48)
    else:
        k = ease_out_back(prog(t, 3.5, 3.85))
        x5, y5 = polar(BX, BY, BR, 19, 270)
        x1, y1 = polar(BX, BY, BR, 1, 270)
        pill(cv, "5", x5 - 40, y5 - 20, RED, scale=k, size=56, fg="#ffffff")
        pill(cv, "1", x1 + 40, y1 - 20, RED, scale=k, size=56, fg="#ffffff")
    caption(cv, t, 0.2, 3.4, "Darum: groß *neben* klein", 470, size=100)
    caption(cv, t, 3.4, 9, "Die *20* zwischen *5* und *1*", 470, size=100)
    return cv


# ------------------------------------------------------------ 5 Bestraft
def s5_bestraft(t):
    cv = pub(t)
    board(cv, BX, BY, BR)
    p = Pen(cv)
    miss = polar(BX, BY, BR, 1, 128, -4)
    good = polar(BX, BY, BR, 0, 128, 0)
    for (tx, ty), t0 in ((miss, 0.7), (good, 2.4)):
        if t < t0:
            flying_dart(p, tx, ty, prog(t, t0 - 0.45, t0), 0.85)
        else:
            dart(p, tx, ty, 0.85)
    score(cv, "+1", miss[0] + 150, miss[1] - 20, "#ff5a4a", t, 0.7)
    score(cv, "+20", good[0] - 170, good[1] - 20, GOLD, t, 2.4)
    if t > 0.9 and t < 2.4:
        pill(cv, "knapp daneben", 540, 1680, "#ff5a4a", scale=ease_out_back(prog(t, 0.9, 1.25)), fg="#ffffff",
             size=48)
    if t > 2.6:
        pill(cv, "genau getroffen", 540, 1680, GOLD, scale=ease_out_back(prog(t, 2.6, 2.95)), size=48)
    cv = cam(cv, t, shake_at=0.7, shake_dur=0.4, amp=8)
    caption(cv, t, 0.2, 9, "Daneben = *bestraft*", 470, size=104)
    return cv


# ------------------------------------------------------------ 6 Erfinder
def s6_erfinder(t):
    cv = pub(t, SEPIA_BG)
    p = Pen(cv)
    p.rrect((BX - 450, BY - 450, BX + 450, BY + 450), 30, "#4a3420", "#8a6a42", 14)
    board(cv, BX, BY, 360, sepia=1.0)
    k = ease_out_back(prog(t, 0.6, 0.95))
    pill(cv, "um 1900?", 540, 1700, "#e8d2a8", scale=k, size=52)
    if t > 1.4:
        place(cv, text_sprite("?", 180, color="#e8d2a8"), 900, 760, ease_out_back(prog(t, 1.4, 1.8)))
    caption(cv, t, 0.2, 9, "Erfinder: *unbekannt*", 470, size=104)
    return cv


# ------------------------------------------------------------ 7 Triple 20
def s7_triple(t):
    cv = pub(t)
    z = ease_in_out(prog(t, 0.2, 1.4))
    R = lerp(BR, 1700, z)
    target = (R_TO + R_TI) / 2 / R_BOARD * R       # Abstand Mitte -> Triple-Ring (px)
    cy = lerp(BY, 1150 + target, z)
    board(cv, BX, cy, R)
    p = Pen(cv)
    if z > 0.95:
        k = ease_out(prog(t, 1.5, 1.9))
        y0 = cy - R_TO / R_BOARD * R
        y1 = cy - R_TI / R_BOARD * R
        x = BX + 260
        p.line([(x, y0), (x, y0 + (y1 - y0) * k)], GOLD, 8)
        p.line([(x - 20, y0), (x + 20, y0)], GOLD, 6)
        if k > 0.95:
            p.line([(x - 20, y1), (x + 20, y1)], GOLD, 6)
        place(cv, text_sprite("*8 mm*", 70, hl=GOLD), x + 130, (y0 + y1) / 2, k)
        for i, t0 in enumerate((2.6, 3.0, 3.4)):
            tx = BX - 50 + i * 50
            ty = (y0 + y1) / 2 + 4
            if t < t0:
                flying_dart(p, tx, ty, prog(t, t0 - 0.35, t0), 1.2)
            else:
                dart(p, tx, ty, 1.2)
        if t > 3.6:
            place(cv, glow(260, GOLD, 0.6), 540, 1550)
            place(cv, text_sprite("*180!*", 190, hl=GOLD), 540, 1550, ease_out_back(prog(t, 3.6, 4.0)))
    caption(cv, t, 0.2, 9, "Profis zielen auf die *dreifache 20*", 470, size=92)
    return cv


# ------------------------------------------------------------ 8 Ende (Loop)
def s8_ende(t):
    cv = pub(t)
    board(cv, BX, BY, BR)
    caption(cv, t, 0.1, 9, "Hättest du's *gewusst*?", 430, size=100)
    caption(cv, t, 1.4, 9, "Folge für mehr *Warum eigentlich?*", 660, size=62)
    return cv


VIDEO = Video([
    (3.5, s1_einstieg, [(0.0, "Auf der Dartscheibe liegt die 20 direkt neben der 1. Zufall? Nein – Absicht.")]),
    (3.8, s2_sortiert, [(0.2, "Stell dir vor, die Zahlen wären der Reihe nach sortiert – wie auf einer Uhr.")]),
    (4.5, s3_leicht, [(0.2, "Dann zielst du einfach auf die Ecke mit 18, 19 und 20 – und triffst fast immer viel.")]),
    (6.5, s4_gemischt, [(0.2, "Darum ist die Scheibe gemischt: Neben fast jeder großen Zahl liegt eine kleine."),
                        (3.4, "Die 20 hat links die 5 und rechts die 1.")]),
    (5.0, s5_bestraft, [(0.2, "Wer knapp daneben wirft, wird bestraft. Nur wer genau trifft, holt die großen Punkte.")]),
    (4.5, s6_erfinder, [(0.2, "Wer sich das ausgedacht hat, weiß man nicht sicher – die Anordnung ist über 100 Jahre alt.")]),
    (5.0, s7_triple, [(0.2, "Und die Profis zielen auf die dreifache 20: ein Feld, nur acht Millimeter breit.")]),
    (3.0, s8_ende, [(0.2, "Hättest du es gewusst?"),
                    (1.5, "Folge für mehr: Warum eigentlich?")]),
])

if __name__ == "__main__":
    cli(VIDEO, __file__, cover_t=1.2)
