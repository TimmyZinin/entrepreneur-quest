#!/bin/bash
# Synthesize minimal ambient BGM loop (~75 sec) using ffmpeg.
# Layered sine pad in Cmaj7 — melancholic, loopable, warm.
set -euo pipefail

cd "$(dirname "$0")/.."
mkdir -p audio

DUR=75

# C3 (130.81), E3 (164.81), G3 (196.00), B3 (246.94) — Cmaj7
# Slow LFO modulation for breathing
ffmpeg -y \
  -f lavfi -i "sine=frequency=130.81:duration=${DUR}" \
  -f lavfi -i "sine=frequency=164.81:duration=${DUR}" \
  -f lavfi -i "sine=frequency=196.00:duration=${DUR}" \
  -f lavfi -i "sine=frequency=246.94:duration=${DUR}" \
  -filter_complex "
    [0]volume=0.18,tremolo=f=0.2:d=0.3[a];
    [1]volume=0.14,tremolo=f=0.25:d=0.35[b];
    [2]volume=0.12,tremolo=f=0.18:d=0.25[c];
    [3]volume=0.08,tremolo=f=0.22:d=0.4[d];
    [a][b][c][d]amix=inputs=4:duration=longest,
    lowpass=f=1800,
    aecho=0.6:0.4:800:0.3,
    afade=t=in:st=0:d=3,
    afade=t=out:st=72:d=3
  " \
  -ar 44100 -ac 2 -b:a 128k audio/bgm.mp3 2>&1 | tail -5

ls -la audio/bgm.mp3
echo "✓ BGM generated"
