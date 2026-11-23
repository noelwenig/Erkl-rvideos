"""Deutsche Sprachausgabe mit Piper (offline, Open Source).

Stimme laden:  bash tools/get_voice.sh   (legt sie unter voices/ ab)
"""
import hashlib
import os
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE = os.environ.get("EV_VOICE", "thorsten")
SPEED = float(os.environ.get("EV_SPEED", "0.92"))  # <1 = schneller
CACHE = os.path.join(ROOT, "voices", "cache")

_voice = None


def _load():
    global _voice
    if _voice is None:
        from piper import PiperVoice
        path = os.path.join(ROOT, "voices", VOICE, f"de-{VOICE}-low.onnx")
        if not os.path.exists(path):
            raise SystemExit(f"Stimme fehlt: {path}\n-> bash tools/get_voice.sh")
        _voice = PiperVoice.load(path)
        orig = _voice.phonemize

        def phonemize(text):
            # espeak liefert 'ç' zerlegt (c + Cedille); das Modell kennt nur 'ç'.
            out = []
            for sent in orig(text):
                fixed = []
                for ph in sent:
                    if ph == "̧" and fixed and fixed[-1] == "c":
                        fixed[-1] = "ç"
                    else:
                        fixed.append(ph)
                out.append(fixed)
            return out

        _voice.phonemize = phonemize
    return _voice


def say(text):
    """Text -> (samples int16, samplerate). Ergebnis wird gecacht."""
    os.makedirs(CACHE, exist_ok=True)
    key = hashlib.sha1(f"{VOICE}|{SPEED}|{text}".encode()).hexdigest()[:16]
    path = os.path.join(CACHE, key + ".wav")
    if not os.path.exists(path):
        from piper import SynthesisConfig
        with wave.open(path, "wb") as w:
            _load().synthesize_wav(text, w, syn_config=SynthesisConfig(length_scale=SPEED))
    with wave.open(path) as w:
        sr = w.getframerate()
        data = np.frombuffer(w.readframes(w.getnframes()), np.int16)
    return data, sr


def voice_track(cues, duration, out):
    """cues: [(startzeit_s, text), ...] -> WAV mit allen Sätzen an ihrer Position."""
    clips = [(t, *say(txt), txt) for t, txt in cues]
    sr = clips[0][2]
    track = np.zeros(int(duration * sr) + sr, np.int32)
    report = []
    for i, (t, data, _, txt) in enumerate(clips):
        a = int(t * sr)
        track[a:a + len(data)] += data
        end = t + len(data) / sr
        nxt = clips[i + 1][0] if i + 1 < len(clips) else duration
        report.append((t, end, end > nxt + 0.01, txt))
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(np.clip(track[:int(duration * sr)], -32768, 32767).astype(np.int16).tobytes())
    return report
