"""Folge 4: Warum landen Katzen immer auf den Füßen?  (9:16)

Rendern:   python3 videos/04_katze.py            (ElevenLabs, Stimme Brian)
Vorschau:  python3 videos/04_katze.py --stills
"""
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from PIL import Image  # noqa: E402

from ev.engine import (S, Pen, Video, canvas, caption, cli, ease_in_out, ease_out,  # noqa: E402
                       ease_out_back, glow, lerp, mix, place, prog, text_sprite)

BG = ((0, "#080b26"), (0.55, "#1a1747"), (1, "#2c1d5e"))
CAT = "#FF9F43"
CAT_REAR = "#FFD08F"
CAT_DARK = "#d9762a"
PINK = "#ff8fa3"
VIOLET = "#9b8cff"
MINT = "#5fe0c0"
GROUND = "#141030"
INK = "#1a0f2e"

rng = random.Random(4)
STARS = [(rng.uniform(0, 1080), rng.uniform(0, 1900), rng.uniform(1.5, 4), rng.uniform(0, 6.3))
         for _ in range(90)]


def stars(p, t, a=1.0):
    for x, y, r, ph in STARS:
        k = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(t * 2.2 + ph))
        p.circle(x, y, r, mix("#1a1747", "#ffffff", k * a))


def night(t):
    cv = canvas(BG)
    stars(Pen(cv), t)
    return cv


def pill(cv, text, cx, cy, color, alpha=1.0, scale=1.0, size=42, fg=INK):
    spr = text_sprite(text, size, weight="bold", stroke=0, color=fg, max_w=900)
    w, h = spr.width / S + 52, spr.height / S + 24
    img = Image.new("RGBA", (int(w * S) + 4, int(h * S) + 4), (0, 0, 0, 0))
    Pen(img).rrect((0, 0, w, h), h / 2, color)
    place(img, spr, w / 2, h / 2)
    place(cv, img, cx, cy, scale, alpha)


def ground(p, y=1560):
    p.poly([(0, y), (1080, y), (1080, 1920), (0, 1920)], GROUND)
    p.line([(0, y), (1080, y)], "#3a2f6e", 6, caps=False)


# ------------------------------------------------------------ Die Katze
def ellipse_pts(cx, cy, rx, ry, n=36):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n))
            for i in range(n)]


def cat(p, cx, cy, s=1.0, front=0.0, rear=0.0, ftuck=0.0, rtuck=0.0, bend=0.0, rot=0.0,
        legs=1.0, col_f=CAT, col_r=CAT, hs=1.0, drop=0.0):
    """Katze in Seitenansicht aus zwei Hälften.

    front/rear: Drehung der vorderen/hinteren Hälfte um die Wirbelsäule in Grad
    (0 = Füße unten, 180 = Füße oben). In der Seitenansicht sieht eine Drehung
    um die Längsachse wie ein senkrechtes Stauchen aus (cos).
    ftuck/rtuck: 0 = Beine ausgestreckt, 1 = angezogen.  bend: Knick in der Mitte.
    """
    cf, cr = math.cos(math.radians(front)), math.cos(math.radians(rear))
    b, r = math.radians(bend), math.radians(rot)

    def T(x, y, half, body=False):
        c = cf if half == "f" else cr
        if body:
            c = max(abs(c), 0.62)
        y = y * c + drop
        a = -b if half == "f" else b
        x1, y1 = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        x2, y2 = x1 * math.cos(r) - y1 * math.sin(r), x1 * math.sin(r) + y1 * math.cos(r)
        return cx + x2 * s, cy + y2 * s

    def leg(x, half, tuck, col):
        hip = T(x, 22, half)
        ln = 105 * legs
        end = (x + 40 * tuck, lerp(22 + ln, 58, tuck))
        knee = (x + 34 * tuck, lerp(22 + ln * 0.55, 62, tuck))
        pts = [hip, T(*knee, half), T(*end, half)]
        p.line(pts, col, 26 * s)
        p.circle(*pts[-1], 16 * s, col)

    rcol = mix(col_r, "#000000", 0.18)
    fcol = mix(col_f, "#000000", 0.18)
    # hintere (ferne) Beine etwas dunkler
    leg(-100, "r", rtuck, rcol)
    leg(75, "f", ftuck, fcol)
    # Schwanz
    tail = []
    for i in range(16):
        u = i / 15
        x = lerp(-120, -235, u)
        y = -5 - 120 * u * u + 18 * math.sin(u * 3)
        tail.append(T(x, y, "r"))
    p.line(tail, col_r, 20 * s)
    # Körper
    p.poly([T(x, y, "r", True) for x, y in ellipse_pts(-55, 0, 92, 50)], col_r)
    p.poly([T(x, y, "f", True) for x, y in ellipse_pts(55, -4, 92, 48)], col_f)
    leg(-55, "r", rtuck, col_r)
    leg(110, "f", ftuck, col_f)
    # Kopf
    hx, hy = 175, -48
    for ex in ((-40, -28, -52, -92, -18, -60), (2, -60, 28, -98, 42, -40)):
        p.poly([T(hx + ex[0] * hs, hy + ex[1] * hs, "f"), T(hx + ex[2] * hs, hy + ex[3] * hs, "f"),
                T(hx + ex[4] * hs, hy + ex[5] * hs, "f")], col_f)
    p.circle(*T(hx, hy, "f"), 52 * s * hs, col_f)
    p.circle(*T(hx + 44 * hs, hy + 12 * hs, "f"), 26 * s * hs, col_f)  # Schnauze
    ex_, ey_ = T(hx + 18 * hs, hy - 8 * hs, "f")
    p.circle(ex_, ey_, 9 * s * hs, INK)
    p.circle(ex_ + 3 * s, ey_ - 3 * s, 3 * s * hs, "#ffffff")
    p.circle(*T(hx + 66 * hs, hy + 6 * hs, "f"), 7 * s * hs, PINK)


def twist(u):
    """Zustand der Drehung beim Fallen, u in [0, 1] -> Parameter für cat()."""
    bend = 22 * ease_out(prog(u, 0.0, 0.12)) * (1 - ease_in_out(prog(u, 0.78, 0.95)))
    k1 = ease_in_out(prog(u, 0.12, 0.45))
    k2 = ease_in_out(prog(u, 0.48, 0.8))
    front = lerp(180, 0, k1)
    rear = lerp(180, 205, k1) + 155 * k2
    ftuck = ease_out(prog(u, 0.05, 0.15)) * (1 - ease_out(prog(u, 0.45, 0.55)))
    rtuck = ease_out(prog(u, 0.45, 0.55)) * (1 - ease_out(prog(u, 0.8, 0.92)))
    return dict(front=front, rear=rear, ftuck=ftuck, rtuck=rtuck, bend=bend)


def qmark(cv, x, y, scale=1.0, alpha=1.0):
    place(cv, text_sprite("?", 170, color="#ffffff"), x, y, scale, alpha)


# ------------------------------------------------------------ 1 Einstieg
def s1_einstieg(t):
    cv = night(t)
    p = Pen(cv)
    ground(p)
    if t < 3.4:
        u = prog(t, 0.3, 2.5)
        y = lerp(720, 1440, ease_in_out(u) * 0.3 + u * u * 0.7)
        land = prog(t, 2.5, 2.9)
        sq = math.sin(land * math.pi) * 0.35
        cat(p, 540, y + 40 * sq, 0.95, legs=1 - sq, **twist(u))
        if land > 0:
            pill(cv, "Füße unten!", 540, 1680, MINT, scale=ease_out_back(prog(t, 2.6, 2.95)))
    else:
        k = ease_out_back(prog(t, 3.4, 3.8))
        y = 1080 + 14 * math.sin(t * 2.5)
        for i in range(3):
            rr = 230 + 40 * i + 20 * math.sin(t * 2 + i)
            p.circle(540, y, rr, None, mix("#2c1d5e", "#ffffff", 0.18), 3)
        cat(p, 540, y, 0.95 * k, front=180, rear=180)
        qmark(cv, 860, y - 230, k)
        pill(cv, "Nichts zum Abstoßen", 540, 1440, VIOLET, scale=ease_out_back(prog(t, 3.8, 4.15)))
    caption(cv, t, 0.1, 3.4, "Katzen landen fast immer auf den *Füßen*", 500, size=88)
    caption(cv, t, 3.4, 9, "Dabei gibt es in der Luft *nichts zum Abstoßen*", 500, size=84)
    return cv


# ------------------------------------------------------------ 2 Zeitlupen-Fotos
SEPIA = "#e2c08f"


def s2_fotos(t):
    cv = canvas(BG)
    p = Pen(cv)
    stars(p, t, 0.5)
    slide = 1 - ease_out(prog(t, 0.2, 1.1))
    ox = 900 * slide
    y0, y1 = 900, 1290
    p.d.rectangle([(20 + ox) * S, y0 * S, (1060 + ox) * S, y1 * S], fill=(30, 22, 16, 255))
    for i in range(17):
        x = 40 + ox + i * 61
        p.rrect((x, y0 + 14, x + 30, y0 + 40), 6, "#5a4636")
        p.rrect((x, y1 - 40, x + 30, y1 - 14), 6, "#5a4636")
    for i in range(4):
        x = 40 + ox + i * 252
        p.rrect((x + 8, y0 + 58, x + 244, y1 - 58), 10, "#4a3a2c")
        u = i / 3
        kk = prog(t, 0.6 + i * 0.35, 0.9 + i * 0.35)
        if kk > 0:
            st = twist(u * 0.82)
            cat(p, x + 126, y0 + 195, 0.38, col_f=mix("#4a3a2c", SEPIA, kk),
                col_r=mix("#4a3a2c", SEPIA, kk), **st)
    if t > 2.4:
        place(cv, text_sprite("*1894*", 130, hl=SEPIA), 540, 1450, ease_out_back(prog(t, 2.4, 2.8)))
        pill(cv, "erste Zeitlupen-Fotos", 540, 1600, SEPIA, scale=ease_out_back(prog(t, 2.8, 3.15)))
    caption(cv, t, 0.2, 9, "Physiker haben lange *gerätselt*", 500, size=92)
    return cv


# ------------------------------------------------------------ 3 Gleichgewicht
def s3_ohr(t):
    cv = night(t)
    p = Pen(cv)
    cx, cy, s = 540, 1060, 1.5
    cat(p, cx, cy, s, front=180, rear=180)
    # Ohr liegt (kopfüber) unten
    ex, ey = cx + 152 * s, cy + 100 * s
    if t > 0.8:
        pulse = 0.6 + 0.4 * math.sin(t * 6)
        place(cv, glow(110, MINT, pulse), ex, ey)
        pill(cv, "Gleichgewichts-Organ", 760, 1360, MINT, scale=ease_out_back(prog(t, 1.0, 1.35)))
    # Kompass "oben"
    gx, gy, gr = 540, 1620, 95
    k = ease_out_back(prog(t, 1.4, 1.8))
    if k > 0:
        p.circle(gx, gy, gr * k, "#231d55", "#ffffff88", 4)
        tt = max(0.0, t - 1.6)
        ang = -90 + 120 * math.exp(-tt * 1.3) * math.cos(tt * 7)
        a = math.radians(ang)
        p.arrow(gx - math.cos(a) * 50 * k, gy - math.sin(a) * 50 * k,
                gx + math.cos(a) * 75 * k, gy + math.sin(a) * 75 * k, MINT, 14, 36)
        place(cv, text_sprite("oben", 40, weight="bold", stroke=0), gx + 170, gy - 50, k)
    caption(cv, t, 0.2, 9, "Zuerst: *Wo ist oben?*", 500, size=96)
    caption(cv, t, 2.0, 9, "Das spürt sie im *Ohr*", 720, size=76)
    return cv


# ------------------------------------------------------------ Drehpfeil
def spin(p, x, y, r, frac, color, width=12):
    if frac <= 0.02:
        return
    a0 = -math.pi / 2
    pts = [(x + r * math.cos(a0 + 2 * math.pi * frac * i / 30),
            y + r * math.sin(a0 + 2 * math.pi * frac * i / 30)) for i in range(31)]
    p.line(pts[:-2], color, width)
    (x0, y0), (x1, y1) = pts[-3], pts[-1]
    ang = math.atan2(y1 - y0, x1 - x0)
    h = width * 2.6
    p.poly([(x1 + math.cos(ang) * h * 0.6, y1 + math.sin(ang) * h * 0.6),
            (x1 + math.cos(ang + 2.2) * h, y1 + math.sin(ang + 2.2) * h),
            (x1 + math.cos(ang - 2.2) * h, y1 + math.sin(ang - 2.2) * h)], color)


# ------------------------------------------------------------ 4 Der Trick
def s4_trick(t):
    cv = night(t)
    p = Pen(cv)
    bend = 20 * ease_out(prog(t, 0.6, 1.6))
    ftuck = ease_out(prog(t, 4.4, 5.2))
    k = ease_in_out(prog(t, 7.9, 9.8))
    front, rear = lerp(180, 0, k), lerp(180, 205, k)
    cx, cy, s = 540, 1080, 1.45
    cat(p, cx, cy, s, front=front, rear=rear, ftuck=ftuck, bend=bend, col_r=CAT_REAR)
    if 1.8 < t < 4.2:
        a = prog(4.2 - t, 0, 0.2)
        pill(cv, "vorne", 760, 1420, CAT, a, ease_out_back(prog(t, 1.8, 2.15)))
        pill(cv, "hinten", 330, 1420, CAT_REAR, a, ease_out_back(prog(t, 2.0, 2.35)))
    if 4.4 < t < 7.6:
        a = prog(7.6 - t, 0, 0.2)
        pill(cv, "Beine ran", 760, 1420, CAT, a, ease_out_back(prog(t, 4.6, 4.95)))
        pill(cv, "Beine raus", 330, 1420, CAT_REAR, a, ease_out_back(prog(t, 5.4, 5.75)))
    if t > 7.6:
        spin(p, 760, 1450, 80, k * 0.9, CAT, 14)
        spin(p, 330, 1450, 80, k * 0.12, CAT_REAR, 14)
        pill(cv, "schnell", 760, 1600, CAT, scale=ease_out_back(prog(t, 8.2, 8.55)))
        pill(cv, "kaum", 330, 1600, CAT_REAR, scale=ease_out_back(prog(t, 8.6, 8.95)))
    caption(cv, t, 0.2, 4.2, "Der Trick: *zwei Hälften*", 500, size=96)
    caption(cv, t, 4.2, 7.6, "Vorne Beine *ran*, hinten Beine *raus*", 500, size=86)
    caption(cv, t, 7.6, 13, "Vorne dreht *schnell* – hinten *kaum*", 500, size=88)
    return cv


# ------------------------------------------------------------ 5 Hinten dreht nach
def s5_nach(t):
    cv = night(t)
    p = Pen(cv)
    sw = ease_out(prog(t, 0.3, 1.1))
    k = ease_in_out(prog(t, 1.4, 3.6))
    rear = lerp(205, 360, k)
    straight = ease_in_out(prog(t, 4.0, 4.6))
    wiggle = 26 * math.sin((t - 4.6) * 4) * prog(t, 4.6, 5.0) if t > 4.6 else 0
    bend = lerp(20, 0, straight) + wiggle
    rtuck = sw * (1 - ease_out(prog(t, 3.6, 4.2)))
    cx, cy, s = 540, 1080, 1.45
    cat(p, cx, cy, s, front=0, rear=rear, ftuck=1 - sw, rtuck=rtuck, bend=bend, col_r=CAT_REAR)
    if t < 4.4:
        spin(p, 330, 1450, 80, k * 0.9, CAT_REAR, 14)
        pill(cv, "hinten dreht nach", 540, 1640, CAT_REAR, prog(4.4 - t, 0, 0.2),
             ease_out_back(prog(t, 1.6, 1.95)))
    else:
        g = prog(t, 4.7, 5.1)
        for i in range(12):
            u = i / 11
            x = lerp(-130, 140, u)
            hf = "f" if x > 0 else "r"
            a = math.radians(-bend if hf == "f" else bend)
            yy = -32
            px, py = x * math.cos(a) - yy * math.sin(a), x * math.sin(a) + yy * math.cos(a)
            place(cv, glow(26, "#ffffff", g * 0.9), cx + px * s, cy + py * s)
            p.circle(cx + px * s, cy + py * s, 7 * g, "#ffffff")
        pill(cv, "super biegsamer Rücken", 540, 1500, MINT, scale=ease_out_back(prog(t, 5.0, 5.35)))
    caption(cv, t, 0.2, 4.6, "Dann *hinten*: Beine ran – und nachdrehen", 500, size=84)
    caption(cv, t, 4.6, 10, "Das klappt dank *biegsamem Rücken*", 500, size=88)
    return cv


# ------------------------------------------------------------ 6 Eine Sekunde + Landung
def s6_landung(t):
    cv = night(t)
    p = Pen(cv)
    if t < 3.4:
        a = prog(3.4 - t, 0, 0.25)
        k = ease_out_back(prog(t, 0.2, 0.6))
        gx, gy, r = 540, 1080, 230 * k
        if k > 0:
            p.circle(gx, gy, r, "#231d55", "#ffffff", 10)
            p.rrect((gx - 34, gy - r - 60, gx + 34, gy - r - 8), 12, "#ffffff")
            for i in range(12):
                aa = 2 * math.pi * i / 12
                p.line([(gx + math.cos(aa) * r * 0.82, gy + math.sin(aa) * r * 0.82),
                        (gx + math.cos(aa) * r * 0.92, gy + math.sin(aa) * r * 0.92)],
                       "#ffffff88", 6)
            sweep = ease_in_out(prog(t, 0.6, 1.8)) * 0.85
            pts = [(gx, gy)] + [(gx + math.sin(2 * math.pi * sweep * i / 40) * r * 0.78,
                                 gy - math.cos(2 * math.pi * sweep * i / 40) * r * 0.78)
                                for i in range(41)]
            if sweep > 0.01:
                p.poly(pts, MINT + "aa")
            hand = 2 * math.pi * sweep
            p.line([(gx, gy), (gx + math.sin(hand) * r * 0.8, gy - math.cos(hand) * r * 0.8)],
                   "#ffffff", 10)
            p.circle(gx, gy, 16, "#ffffff")
        if t > 1.9:
            place(cv, text_sprite("*unter 1 Sekunde*", 90, hl=MINT), 540, 1460,
                  ease_out_back(prog(t, 1.9, 2.25)), a)
    else:
        ground(p)
        u = prog(t, 3.5, 4.3)
        y = lerp(900, 1440, u * u)
        land = prog(t, 4.3, 5.1)
        sq = math.sin(min(1, land * 1.6) * math.pi) * 0.45 * (1 - land * 0.5) if land > 0 else 0
        cat(p, 540, y + 50 * sq, 0.95, legs=1 - sq)
        if land > 0:
            for i in range(3):
                rr = 40 + 160 * prog(land, i * 0.15, 1)
                aa = 1 - prog(land, i * 0.15, 1)
                if aa > 0:
                    p.ellipse((540 - rr * 1.6, 1560 - rr * 0.25, 540 + rr * 1.6, 1560 + rr * 0.25),
                              mix("#141030", MINT, aa * 0.6))
            pill(cv, "Beine federn ab", 540, 1700, MINT, scale=ease_out_back(prog(t, 4.6, 4.95)))
    caption(cv, t, 0.2, 3.4, "Das alles in *unter einer Sekunde*", 500, size=88)
    caption(cv, t, 3.4, 10, "Bei der Landung *federn* die Beine ab", 500, size=88)
    return cv


# ------------------------------------------------------------ 7 Kätzchen + Warnung
def s7_warnung(t):
    cv = night(t)
    p = Pen(cv)
    if t < 3.8:
        ground(p)
        k = ease_out_back(prog(t, 0.2, 0.6))
        if k > 0:
            cat(p, 520, 1560 - 120 * 0.75 * k, 0.75 * k, hs=1.3, col_f="#ffc27a", col_r="#ffc27a")
        pill(cv, "ab ca. 7 Wochen", 540, 1700, "#ffc27a", scale=ease_out_back(prog(t, 0.8, 1.15)))
    else:
        k = ease_out_back(prog(t, 3.9, 4.3))
        wob = math.sin((t - 3.9) * 10) * 6 * (1 - prog(t, 3.9, 5.0))
        cx, cy = 540, 1130
        pts = [(cx, cy - 260 * k), (cx + 270 * k, cy + 200 * k), (cx - 270 * k, cy + 200 * k)]
        rad = math.radians(wob)
        pts = [(cx + (x - cx) * math.cos(rad) - (y - cy) * math.sin(rad),
                cy + (x - cx) * math.sin(rad) + (y - cy) * math.cos(rad)) for x, y in pts]
        p.poly(pts, "#FFD23F")
        p.line(pts + [pts[0]], "#FFD23F", 40)
        place(cv, text_sprite("!", 300, color=INK, stroke=0), cx, cy + 40, k)
        pill(cv, "Nicht nachmachen!", 540, 1480, "#ffffff", scale=ease_out_back(prog(t, 4.4, 4.75)),
             size=50)
    caption(cv, t, 0.2, 3.8, "Kätzchen lernen das mit etwa *7 Wochen*", 500, size=86)
    caption(cv, t, 3.8, 11, "Verletzen können sie sich *trotzdem*!", 500, size=88)
    return cv


# ------------------------------------------------------------ 8 Ende
def s8_ende(t):
    cv = night(t)
    p = Pen(cv)
    place(cv, glow(260, "#fff4c9", 0.5), 820, 380)
    p.circle(820, 380, 120, "#fff4c9")
    p.circle(780, 350, 22, "#e9dfb4")
    p.circle(860, 420, 14, "#e9dfb4")
    p.poly([(0, 1540), (380, 1480), (760, 1540), (1080, 1500), (1080, 1920), (0, 1920)], GROUND)
    cat(p, 420, 1380, 0.75)
    caption(cv, t, 0.1, 9, "Hättest du's *gewusst*?", 760, size=110)
    caption(cv, t, 1.6, 9, "Folge für mehr *Warum eigentlich?*", 1010, size=66)
    return cv


VIDEO = Video([
    (7.0, s1_einstieg, [(0.1, "Wenn eine Katze fällt, landet sie fast immer auf den Füßen."),
                        (3.4, "Dabei kann sie sich in der Luft nirgends abstoßen.")]),
    (6.0, s2_fotos, [(0.2, "Physiker haben darüber lange gerätselt – sogar mit Zeitlupen-Fotos schon vor über hundert Jahren.")]),
    (5.0, s3_ohr, [(0.2, "Zuerst merkt die Katze, wo oben ist – mit dem Gleichgewichtsorgan im Ohr.")]),
    (12.0, s4_trick, [(0.2, "Dann kommt der Trick: Sie knickt in der Mitte ein, als hätte sie zwei Hälften."),
                      (4.2, "Die Vorderbeine zieht sie an, die Hinterbeine streckt sie aus."),
                      (7.6, "So dreht sich die vordere Hälfte schnell – die hintere kaum.")]),
    (8.5, s5_nach, [(0.2, "Dann umgekehrt: Hinterbeine ran, und die hintere Hälfte dreht nach."),
                    (4.6, "Möglich macht das ein super biegsamer Rücken.")]),
    (7.0, s6_landung, [(0.2, "Das Ganze dauert weniger als eine Sekunde."),
                       (3.4, "Bei der Landung federn die Beine den Aufprall ab.")]),
    (8.5, s7_warnung, [(0.2, "Kätzchen lernen das übrigens erst mit etwa sieben Wochen."),
                       (3.8, "Aber: Verletzen können sich Katzen trotzdem – also bitte nie ausprobieren!")]),
    (4.2, s8_ende, [(0.2, "Hättest du es gewusst?"),
                    (1.7, "Folge für mehr: Warum eigentlich?")]),
])

if __name__ == "__main__":
    cli(VIDEO, __file__, cover_t=1.4)
