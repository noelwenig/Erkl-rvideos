"""Deutsche Sprachausgabe mit Piper (offline, Open Source).

Stimme laden:  bash tools/get_voice.sh   (legt sie unter voices/ ab)
"""
import hashlib
import os
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.environ.get("EV_TTS", "piper")          # "piper" oder "elevenlabs"
VOICE = os.environ.get("EV_VOICE", "thorsten")
# ElevenLabs: Stimmen-ID (Standard: Brian). Schlüssel kommt über den Netzwerk-Proxy.
EL_VOICE = os.environ.get("EV_EL_VOICE", "nPczCjzI2devNBz1zQrb")
EL_MODEL = os.environ.get("EV_EL_MODEL", "eleven_v4")
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


def _elevenlabs(text, prev, nxt, path):
    import json
    import subprocess
    import urllib.request
    body = {"text": text, "model_id": EL_MODEL, "language_code": "de"}
    if prev:
        body["previous_text"] = prev
    if nxt:
        body["next_text"] = nxt
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{EL_VOICE}?output_format=mp3_44100_128",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "xi-api-key": os.environ.get("ELEVENLABS_API_KEY", "proxy-injected")})
    with urllib.request.urlopen(req, timeout=120) as r:
        mp3 = r.read()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "pipe:0", "-ac", "1", "-ar", "44100",
                    "-af", "silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                           "silenceremove=start_periods=1:start_threshold=-50dB,areverse",
                    path], input=mp3, check=True)


def say(text, prev=None, nxt=None):
    """Text -> (samples int16, samplerate). Ergebnis wird gecacht."""
    os.makedirs(CACHE, exist_ok=True)
    if BACKEND == "elevenlabs":
        key = hashlib.sha1(f"el|{EL_VOICE}|{EL_MODEL}|{prev}|{text}|{nxt}".encode()).hexdigest()[:16]
        path = os.path.join(CACHE, key + ".wav")
        if not os.path.exists(path):
            _elevenlabs(text, prev, nxt, path)
        with wave.open(path) as w:
            return np.frombuffer(w.readframes(w.getnframes()), np.int16), w.getframerate()
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


def clips_for(cues):
    """Alle Sätze erzeugen (mit Kontext davor/danach) -> [(samples, sr), ...]."""
    texts = [t for _, t in cues]
    return [say(t, texts[i - 1] if i else None, texts[i + 1] if i + 1 < len(texts) else None)
            if BACKEND == "elevenlabs" else say(t) for i, t in enumerate(texts)]


def voice_track(cues, duration, out):
    """cues: [(startzeit_s, text), ...] -> WAV mit allen Sätzen an ihrer Position."""
    clips = [(t, d, sr, txt) for (t, txt), (d, sr) in zip(cues, clips_for(cues))]
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
