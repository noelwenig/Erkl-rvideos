# Erklärvideos „Warum eigentlich?“ – Arbeitsweise

TikTok-Erklärvideos (9:16, 1080×1920, ca. 55–60 s), komplett per Code gerendert.
Sprache mit dem Nutzer: Deutsch, einfach und ohne Fachjargon.

## Ablauf für ein neues Video
1. Themenvorschläge machen (Format „Warum …?“, starker Einstieg, gut animierbar).
2. **Skript zuerst zum Absegnen zeigen** (Sprechertext + Bildidee pro Szene, ca. 850–950 Zeichen).
   Erst nach OK das Video bauen – jede Textänderung kostet bei ElevenLabs den ganzen Text neu.
3. Neue Datei `videos/NN_thema.py` nach Vorbild von `videos/03_meer.py` / `02_zeit.py`:
   - `VIDEO = Video([(dauer, szene_fn, [(sekunde_in_szene, "Satz"), ...]), ...])`
   - Untertitel-Zeiten in der Szene = Zeiten der Sätze (die Engine verzerrt die Zeit passend zur Stimme).
   - `*Wort*` in Untertiteln = gelb hervorgehoben; geschütztes Leerzeichen (` `) gegen Umbruch, z. B. „100 m“.
   - Eigene Farbwelt pro Folge, gleiche Schrift/Untertitel; Ende immer „Hättest du's gewusst? / Folge für mehr Warum eigentlich?“.
   - **Kein Ausblick auf das nächste Thema** (Wunsch des Nutzers).
   - **Starker Einstieg (Hook)** nach Vorbild `videos/05_traeume.py`: erster Satz spricht den Zuschauer direkt
     mit einer Überraschung an („Du hast heute Nacht …“), ab dem ersten Bild Bewegung + Untertitel
     (`caption(..., -1, ...)`), kurzer Zoom `punch()`, Titelbild ≈ Anfangsbild.
     Noch stärker (`videos/07_weltall.py`): Zuschauer in die Szene holen („Steig in eine Rakete.“),
     Wackeln `hook_cam()`, und das Rätsel in den ersten 3 s *zeigen*, bevor die Frage kommt.
     Gut ankommen (Nutzer-Favorit Folge 6): Staun-Zahl am Anfang + Alltagsbeispiel in der Mitte.
   - **Kein „Am Ende verrate ich dir …“-Satz** (Wunsch des Nutzers).
4. Vorschau prüfen: `python3 videos/NN_thema.py --stills` (Bilder ansehen, Fehler beheben).
5. Rendern: `python3 videos/NN_thema.py` → ElevenLabs-Stimme „Brian“, ganzer Text in einem Durchgang.
6. `videos/NN_thema.md` (Sprechertext, Fakten/Quellen, TikTok-Beschreibung) anlegen, README-Tabelle ergänzen,
   committen, pushen, Video mit SendUserFile schicken.

## Technik
- Engine: `ev/engine.py` (Zeichnen, Untertitel, Rendern, `cli()`), Stimme: `ev/tts.py`.
- ElevenLabs-Schlüssel wird von der Cloud-Umgebung „erkl-rvideos“ automatisch eingespeist (nie im Chat erfragen).
  Kostenloses Paket: 10.000 Zeichen/Monat, nicht kommerziell.
- Offline-Alternative: `--piper` (braucht `bash tools/get_voice.sh`).
- Fakten sorgfältig prüfen, Unsicheres vorsichtig formulieren („Forscher vermuten …“).
