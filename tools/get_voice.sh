#!/usr/bin/env bash
# Lädt die deutschen Piper-Stimmen (Thorsten = männlich, Kerstin = weiblich) nach voices/
# und installiert piper-tts.
set -e
cd "$(dirname "$0")/.."
pip install -q piper-tts
mkdir -p voices
for n in thorsten kerstin; do
  if [ ! -f "voices/$n/de-$n-low.onnx" ]; then
    curl -sL -o "voices/$n.tgz" "https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-de-$n-low.tar.gz"
    mkdir -p "voices/$n" && tar xzf "voices/$n.tgz" -C "voices/$n" && rm "voices/$n.tgz"
  fi
done
echo "Stimmen bereit in voices/"
