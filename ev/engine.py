"""Kleine Render-Engine für TikTok-Erklärvideos (1080x1920, 30 fps).

Jede Szene ist eine Funktion f(t) -> RGBA-Bild (in S-facher Auflösung, für
Kantenglättung). Koordinaten werden immer im 1080x1920-Raum angegeben.
"""
import math
import os
import subprocess
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, S, FPS = 1080, 1920, 2, 30

FONTS = {
    "black": "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "bold": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "semi": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
}

YELLOW = "#FFD23F"
NAVY = "#0b1a3a"
WHITE = "#ffffff"


# ---------------------------------------------------------------- Helfer
def rgba(h, a=None):
    if isinstance(h, tuple):
        return h if len(h) == 4 else (*h, 255 if a is None else a)
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    alpha = int(h[6:8], 16) if len(h) == 8 else 255
    return (r, g, b, alpha if a is None else a)


def mix(c1, c2, x):
    a, b = rgba(c1), rgba(c2)
    return tuple(int(a[i] + (b[i] - a[i]) * x) for i in range(4))


def clamp01(x):
    return max(0.0, min(1.0, x))


def prog(t, a, b):
    return clamp01((t - a) / (b - a))


def lerp(a, b, x):
    return a + (b - a) * x


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    return 3 * x * x - 2 * x * x * x


def ease_out_back(x, k=1.70158):
    x -= 1
    return 1 + (k + 1) * x ** 3 + k * x ** 2


@lru_cache(None)
def font(size, weight="black"):
    return ImageFont.truetype(FONTS[weight], int(size * S))


# ---------------------------------------------------------------- Hintergrund
@lru_cache(None)
def gradient(stops):
    """stops: ((pos, '#hex'), ...) vertikaler Verlauf."""
    ys = np.linspace(0, 1, H * S)
    pos = [p for p, _ in stops]
    cols = [rgba(c) for _, c in stops]
    row = np.stack([np.interp(ys, pos, [c[i] for c in cols]) for i in range(3)], axis=1)
    arr = np.repeat(row[:, None, :], W * S, axis=1).astype(np.uint8)
    return Image.fromarray(arr, "RGB").convert("RGBA")


def canvas(stops):
    return gradient(stops).copy()


def blend_canvas(stops_a, stops_b, x):
    return Image.blend(gradient(stops_a), gradient(stops_b), clamp01(x))


@lru_cache(None)
def glow(radius, color, strength=1.0):
    n = int(radius * 2 * S)
    yy, xx = np.mgrid[0:n, 0:n]
    d = np.sqrt((xx - n / 2) ** 2 + (yy - n / 2) ** 2) / (radius * S)
    a = (np.clip(1 - d, 0, 1) ** 2) * 255 * strength
    c = rgba(color)
    arr = np.zeros((n, n, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = c[0], c[1], c[2]
    arr[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")


# ---------------------------------------------------------------- Text
def _words(text):
    """'Der Himmel ist *blau*?' -> Liste von Wörtern, jedes eine Liste (txt, hl)."""
    words, cur, hl = [], [], False
    buf = ""
    for ch in text:
        if ch == "*":
            if buf:
                cur.append((buf, hl))
                buf = ""
            hl = not hl
        elif ch == " ":
            if buf:
                cur.append((buf, hl))
                buf = ""
            if cur:
                words.append(cur)
                cur = []
        else:
            buf += ch
    if buf:
        cur.append((buf, hl))
    if cur:
        words.append(cur)
    return words


@lru_cache(maxsize=512)
def text_sprite(text, size, color=WHITE, hl=YELLOW, max_w=940, weight="black",
                stroke=8, stroke_color=NAVY, line_h=1.15):
    f = font(size, weight)
    space = f.getlength(" ") + stroke * S * 0.8
    maxw = max_w * S
    lines, cur, curw = [], [], 0.0
    for runs in _words(text):
        ww = sum(f.getlength(t) for t, _ in runs)
        if cur and curw + space + ww > maxw:
            lines.append((cur, curw))
            cur, curw = [], 0.0
        if cur:
            curw += space
        cur.append((runs, ww))
        curw += ww
    if cur:
        lines.append((cur, curw))

    sw = int(stroke * S)
    lh = int(size * S * line_h)
    asc, desc = f.getmetrics()
    width = int(max(lw for _, lw in lines) + 2 * sw + 4)
    height = int(lh * (len(lines) - 1) + asc + desc + 2 * sw + 4)
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for pass_ in (0, 1):
        if pass_ == 0 and sw == 0:
            continue
        for li, (ws, lw) in enumerate(lines):
            x = (width - lw) / 2
            y = sw + 2 + li * lh
            for runs, ww in ws:
                for t, h in runs:
                    if pass_ == 0:
                        d.text((x, y), t, font=f, fill=rgba(stroke_color),
                               stroke_width=sw, stroke_fill=rgba(stroke_color))
                    else:
                        d.text((x, y), t, font=f, fill=rgba(hl if h else color))
                    x += f.getlength(t)
                x += space
    return img


def place(cv, spr, cx, cy, scale=1.0, alpha=1.0):
    """Sprite mittig bei (cx, cy) einfügen (1080er-Koordinaten)."""
    if alpha <= 0.01 or scale <= 0.01:
        return
    if abs(scale - 1) > 1e-3:
        spr = spr.resize((max(1, int(spr.width * scale)), max(1, int(spr.height * scale))),
                         Image.BILINEAR)
    if alpha < 0.999:
        spr = spr.copy()
        spr.putalpha(spr.getchannel("A").point(lambda v: int(v * alpha)))
    x = int(cx * S - spr.width / 2)
    y = int(cy * S - spr.height / 2)
    sx, sy = max(0, -x), max(0, -y)
    ex, ey = min(spr.width, cv.width - x), min(spr.height, cv.height - y)
    if ex <= sx or ey <= sy:
        return
    if sx or sy or ex < spr.width or ey < spr.height:
        spr = spr.crop((sx, sy, ex, ey))
    cv.alpha_composite(spr, dest=(x + sx, y + sy))


def caption(cv, t, start, end, text, y, size=84, x=540, pop=True, **kw):
    """Animierte Untertitel-Zeile: Pop-in + Fade-out."""
    if t < start or t >= end:
        return
    l = t - start
    sc = lerp(0.7, 1.0, ease_out_back(prog(l, 0, 0.35))) if pop else 1.0
    a = prog(l, 0, 0.15) * prog(end - t, 0, 0.18)
    place(cv, text_sprite(text, size, **kw), x, y, sc, a)


# ---------------------------------------------------------------- Formen
class Pen:
    def __init__(self, img):
        self.d = ImageDraw.Draw(img)

    @staticmethod
    def _p(pts):
        return [(x * S, y * S) for x, y in pts]

    def circle(self, cx, cy, r, fill=None, outline=None, width=0):
        self.d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S],
                       fill=rgba(fill) if fill else None,
                       outline=rgba(outline) if outline else None, width=int(width * S))

    def ellipse(self, box, fill):
        self.d.ellipse([v * S for v in box], fill=rgba(fill))

    def line(self, pts, fill, width, caps=True):
        if len(pts) < 2:
            return
        self.d.line(self._p(pts), fill=rgba(fill), width=int(width * S), joint="curve")
        if caps:
            for x, y in (pts[0], pts[-1]):
                self.circle(x, y, width / 2, fill)

    def poly(self, pts, fill=None, outline=None, width=0):
        self.d.polygon(self._p(pts), fill=rgba(fill) if fill else None,
                       outline=rgba(outline) if outline else None, width=int(width * S))

    def rrect(self, box, r, fill=None, outline=None, width=0):
        self.d.rounded_rectangle([v * S for v in box], radius=int(r * S),
                                 fill=rgba(fill) if fill else None,
                                 outline=rgba(outline) if outline else None,
                                 width=int(width * S))

    def arrow(self, x0, y0, x1, y1, fill, width=10, head=28):
        ang = math.atan2(y1 - y0, x1 - x0)
        bx, by = x1 - math.cos(ang) * head * 0.8, y1 - math.sin(ang) * head * 0.8
        self.line([(x0, y0), (bx, by)], fill, width)
        l, r = ang + 2.6, ang - 2.6
        self.poly([(x1, y1), (x1 + math.cos(l) * head, y1 + math.sin(l) * head),
                   (x1 + math.cos(r) * head, y1 + math.sin(r) * head)], fill)


def layer():
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    return img, Pen(img)


# ---------------------------------------------------------------- Rendern
_VIDEO = None


def _render(i):
    return _VIDEO.frame_bytes(i)


class Video:
    def __init__(self, scenes, voice=True):
        # scenes: [(dauer, fn) oder (dauer, fn, [(zeit_in_szene, sprechertext), ...]), ...]
        self.scenes = [(sc[0], sc[1], sc[2] if len(sc) > 2 else []) for sc in scenes]
        self.duration = sum(d for d, _, _ in self.scenes)
        self.n = int(round(self.duration * FPS))
        self.voice = voice

    def cues(self):
        acc, out = 0.0, []
        for d, _, cs in self.scenes:
            out += [(acc + t, txt) for t, txt in cs]
            acc += d
        return out

    def image(self, t):
        acc = 0.0
        for k, (d, fn, _) in enumerate(self.scenes):
            if t < acc + d or k == len(self.scenes) - 1:
                return fn(min(t - acc, d - 1e-6)).reduce(S).convert("RGB")
            acc += d

    def frame_bytes(self, i):
        return self.image(i / FPS).tobytes()

    def still(self, t, path):
        self.image(t).save(path)

    def build_voice(self, wav):
        from ev.tts import voice_track
        rep = voice_track(self.cues(), self.duration, wav)
        bad = 0
        for a, e, overlap, txt in rep:
            flag = "  <-- ZU LANG, überlappt!" if overlap else ""
            bad += overlap
            print(f"  {a:5.2f}-{e:5.2f}s  {txt}{flag}")
        if bad:
            print(f"  WARNUNG: {bad} Satz/Sätze überlappen.")
        return rep

    def render(self, out, workers=None):
        global _VIDEO
        _VIDEO = self
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
        if self.voice and self.cues() and not os.environ.get("EV_NOVOICE"):
            wav = os.path.splitext(out)[0] + "_voice.wav"
            print("Sprachspur:")
            self.build_voice(wav)
            audio_in = ["-i", wav]
            afilter = ["-af", "highpass=f=70,loudnorm=I=-15:TP=-1.5:LRA=11,aresample=44100",
                       "-ac", "2"]
        else:
            audio_in = ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"]
            afilter = []
        cmd = ["ffmpeg", "-y", "-loglevel", "error",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               *audio_in,
               "-map", "0:v", "-map", "1:a", "-t", f"{self.duration:.3f}",
               "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
               *afilter, "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with Pool(workers or os.cpu_count()) as pool:
            for k, b in enumerate(pool.imap(_render, range(self.n), chunksize=6)):
                ff.stdin.write(b)
                if k % (FPS * 5) == 0:
                    print(f"  {k / FPS:5.1f}s / {self.duration:.1f}s", flush=True)
        ff.stdin.close()
        ff.wait()
        print("fertig:", out)
