# Erklärvideos – „Warum eigentlich?“

Kurze TikTok-Erklärvideos (9:16, 1080×1920, 30 fps), komplett per Code gerendert
mit Python (Pillow + NumPy) und ffmpeg. Die deutsche Sprecherstimme kommt von
[Piper](https://github.com/rhasspy/piper) (offline, Open Source).

Einmalig: `bash tools/get_voice.sh` (installiert piper-tts und lädt die Stimmen nach `voices/`).
Andere Stimme: `EV_VOICE=kerstin`, Sprechtempo: `EV_SPEED=0.92` (kleiner = schneller).

## Videos
| # | Thema | Video | Skript |
|---|---|---|---|
| 1 | Warum ist der Himmel blau? | `output/01_himmel_blau.mp4` | `videos/01_himmel_blau.md` |

## Rendern
```bash
python3 videos/01_himmel_blau.py            # fertiges MP4 + Cover nach output/
python3 videos/01_himmel_blau.py --stills   # schnelle Vorschaubilder
```

## Neues Video anlegen
`videos/01_himmel_blau.py` kopieren, Szenen-Funktionen anpassen und in `VIDEO = Video([...])`
mit ihrer Dauer und den Sprechertexten `[(sekunde_in_szene, "Text"), ...]` eintragen.
Beim Rendern wird angezeigt, ob ein Satz zu lang ist und den nächsten überlappt. Die Engine (`ev/engine.py`) liefert Verläufe, animierte
Untertitel (`*Wort*` wird gelb hervorgehoben), Formen, Glow und das Rendern.
