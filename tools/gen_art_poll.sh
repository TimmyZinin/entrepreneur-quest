#!/bin/bash
# Generate missing images via Pollinations FLUX (no API key needed)
set -euo pipefail

cd "$(dirname "$0")/.."

ANCHOR="editorial 2D illustration, warm sunset palette, terracotta and amber on off-white, melancholic but hopeful mood, soft film grain, cinematic composition, NO people portraits, premium magazine aesthetic"

gen() {
  local name="$1" prompt="$2" out="$3" w="${4:-1600}" h="${5:-900}"
  if [ -f "$out" ] && [ "$(stat -f%z "$out")" -gt 10000 ]; then
    echo "  [$name] exists"
    return
  fi
  mkdir -p "$(dirname "$out")"
  local full="$prompt. $ANCHOR"
  local encoded
  encoded=$(printf '%s' "$full" | python3 -c 'import sys,urllib.parse;print(urllib.parse.quote(sys.stdin.read()))')
  local seed=$((RANDOM * RANDOM % 99999))
  local url="https://image.pollinations.ai/prompt/${encoded}?width=${w}&height=${h}&model=flux&nologo=true&seed=${seed}"
  echo "  [$name] downloading..."
  if curl -sfL -o "$out" --max-time 180 "$url"; then
    local sz
    sz=$(stat -f%z "$out" 2>/dev/null || echo 0)
    if [ "$sz" -gt 10000 ]; then
      echo "  [$name] ✓ $sz bytes"
      return 0
    fi
  fi
  echo "  [$name] ✗ FAILED"
  rm -f "$out"
  return 1
}

# Missing scenes
gen "s03" "editorial 2D, close-up computer monitor showing text and tabs, keyboard in foreground blurred, warm desk lamp light, terracotta palette, over-the-shoulder POV, no face" "img/scenes/s03.png"
gen "s05" "editorial 2D, smartphone screen showing twitter thread, hands holding phone partial back of hands, warm ambient light, tense mood, terracotta accents, POV shot, no face" "img/scenes/s05.png"
gen "s07" "editorial 2D, empty stage at conference venue seen from audience POV, spotlight on podium, amber stage lights, terracotta seats blurred foreground, hopeful anticipation, low-angle wide shot, no people" "img/scenes/s07.png"

# 4 archetype OGs
gen "og-exit" "editorial poster graphic, bold geometric, silhouette of woman on hill at sunset wide shot, terracotta and amber sky, triumphant serene, asymmetric poster layout, magazine cover style" "og/exit.png" 1200 630
gen "og-growth" "editorial poster graphic, bold geometric, vibrant studio interior with plants and light, terracotta amber palette on cream, uplifting, asymmetric poster layout, magazine cover style" "og/growth.png" 1200 630
gen "og-burnout" "editorial poster graphic, melancholic monochrome with single terracotta accent, empty desk cold coffee closed laptop, fading amber light, somber reflective, heavy grain, asymmetric poster, magazine cover" "og/burnout.png" 1200 630
gen "og-phoenix" "editorial poster graphic, bold geometric, phoenix-like abstract flame in terracotta rising from warm grey ashes on cream, hopeful rebirth, asymmetric poster, magazine cover" "og/phoenix.png" 1200 630

echo "Done"
