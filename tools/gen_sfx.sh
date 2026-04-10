#!/bin/bash
# Synthesize 5 SFX using ffmpeg. Warm, soft, UI-friendly.
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p audio

# click: very short click at 1.2kHz
ffmpeg -y -f lavfi -i "sine=frequency=1200:duration=0.04" \
  -af "afade=t=out:st=0:d=0.04,volume=0.35" \
  -ar 44100 -ac 1 -b:a 128k audio/click.mp3 2>/dev/null

# up: two-tone ascending (G4 → C5 quick)
ffmpeg -y -f lavfi -i "sine=frequency=392:duration=0.1" \
  -f lavfi -i "sine=frequency=523:duration=0.1" \
  -filter_complex "[0]adelay=0|0,volume=0.4[a];[1]adelay=80|80,volume=0.4[b];[a][b]amix=inputs=2" \
  -ar 44100 -ac 1 -b:a 128k -t 0.25 audio/up.mp3 2>/dev/null

# down: two-tone descending (C4 → G3)
ffmpeg -y -f lavfi -i "sine=frequency=262:duration=0.12" \
  -f lavfi -i "sine=frequency=196:duration=0.12" \
  -filter_complex "[0]adelay=0|0,volume=0.35[a];[1]adelay=100|100,volume=0.35[b];[a][b]amix=inputs=2,afade=t=out:st=0.22:d=0.05" \
  -ar 44100 -ac 1 -b:a 128k -t 0.28 audio/down.mp3 2>/dev/null

# turn: deterministic pitched whoosh (sweep from 800Hz to 300Hz)
ffmpeg -y -f lavfi -i "anoisesrc=color=pink:duration=0.25:amplitude=0.18:seed=42" \
  -af "afade=t=in:st=0:d=0.05,afade=t=out:st=0.2:d=0.05,lowpass=f=3000" \
  -ar 44100 -ac 1 -b:a 128k audio/turn.mp3 2>/dev/null

# success: major triad chord quick (C-E-G)
ffmpeg -y -f lavfi -i "sine=frequency=523:duration=0.5" \
  -f lavfi -i "sine=frequency=659:duration=0.5" \
  -f lavfi -i "sine=frequency=784:duration=0.5" \
  -filter_complex "[0]volume=0.25[a];[1]volume=0.22[b];[2]volume=0.22[c];[a][b][c]amix=inputs=3,afade=t=out:st=0.35:d=0.15" \
  -ar 44100 -ac 1 -b:a 128k -t 0.5 audio/success.mp3 2>/dev/null

ls -la audio/*.mp3
echo "✓ SFX generated"
