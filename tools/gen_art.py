#!/usr/bin/env python3
"""Batch generate 12 editorial 2D images for Entrepreneur Quest.

Cascade: OpenRouter Gemini 2.5 Flash Image → Pollinations.ai FLUX fallback.
Retries 2 per source. Images saved as .png, then converted to .webp via sips.
"""
import os
import sys
import time
import base64
import re
import urllib.parse
import requests
from pathlib import Path

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GEMINI_MODEL = "google/gemini-2.5-flash-image"
API_KEY = os.environ.get("OPENROUTER_API_KEY")

REPO = Path(__file__).resolve().parent.parent

NEGATIVE = (
    "no smiling people, no handshakes, no laptops on desks, no team meetings, "
    "no stock photo, no cozy lifestyle interior, no cartoon, no mascots, "
    "no neon signs, no sunset beach, no pastel, no flat corporate illustration"
)

ANCHOR = (
    "editorial 2D illustration, warm sunset palette (terracotta #C5380E and amber #E6A817 "
    "on off-white #F5F0EB), melancholic but hopeful mood, soft film grain, cinematic composition, "
    "NO people portraits — only environmental/POV/silhouette framing, "
    "Instagram editorial style, premium magazine aesthetic"
)

SCENES = {
    "hero": (
        "editorial 2D illustration of a woman sitting at a kitchen table from behind, "
        "looking at laptop screen in golden hour warm light, terracotta and amber sunset palette, "
        "melancholic but hopeful mood, soft film grain, cinematic wide shot, "
        "silhouette only, no face visible, premium magazine aesthetic",
        "img/hero.png",
    ),
    "s01": (
        "editorial 2D illustration, top-down view of kitchen table, cold coffee cup, "
        "open laptop with email inbox visible, hand resting on keyboard (partial), "
        "warm morning light through window, terracotta and amber palette, melancholic mood, "
        "film grain, wide shot, no people, cinematic composition",
        "img/scenes/s01.png",
    ),
    "s02": (
        "editorial 2D illustration, empty modern office interior, two chairs facing each other, "
        "one empty, soft afternoon light, muted tones with amber accents, "
        "melancholic aftermath mood, film grain, wide shot, no people in frame",
        "img/scenes/s02.png",
    ),
    "s03": (
        "editorial 2D illustration, close-up of computer monitor showing text document "
        "and browser tabs, keyboard in foreground blurred, warm desk lamp light, "
        "terracotta palette, cozy productive mood, film grain, over-the-shoulder POV, no face",
        "img/scenes/s03.png",
    ),
    "s04": (
        "editorial 2D illustration, empty modern meeting room at night, long table, "
        "slide deck on projector screen showing charts silhouettes, warm amber lights, "
        "melancholic late-night mood, film grain, wide shot, no people",
        "img/scenes/s04.png",
    ),
    "s05": (
        "editorial 2D illustration, smartphone screen close-up showing twitter thread, "
        "hands holding phone (partial, back of hands), warm ambient light, "
        "tense but composed mood, terracotta accents, film grain, POV shot, no face",
        "img/scenes/s05.png",
    ),
    "s06": (
        "editorial 2D illustration, laptop screen showing slack interface with long message, "
        "coffee mug next to keyboard, desk plant, warm afternoon window light, "
        "terracotta and amber palette, contemplative mood, film grain, flat angle, no people",
        "img/scenes/s06.png",
    ),
    "s07": (
        "editorial 2D illustration, empty stage at a conference venue seen from audience POV, "
        "spotlight on podium, amber stage lights, soft terracotta seats blurred in foreground, "
        "hopeful anticipation mood, film grain, low-angle wide shot, no people on stage",
        "img/scenes/s07.png",
    ),
    "exit": (
        "editorial poster graphic, bold geometric composition, silhouette of a woman standing "
        "on a hill at sunset wide shot, terracotta and amber sunset sky, triumphant serene mood, "
        "grain texture, asymmetric poster layout, premium magazine cover style",
        "og/exit.png",
    ),
    "growth": (
        "editorial poster graphic, bold geometric composition, vibrant studio interior with "
        "plants and light, terracotta and amber palette on cream background, uplifting mood, "
        "grain texture, asymmetric poster layout, premium magazine cover style",
        "og/growth.png",
    ),
    "burnout": (
        "editorial poster graphic, melancholic monochrome composition with single terracotta accent, "
        "empty desk with cold coffee and closed laptop, fading amber light, somber reflective mood, "
        "heavy grain texture, asymmetric poster layout, premium magazine cover style",
        "og/burnout.png",
    ),
    "phoenix": (
        "editorial poster graphic, bold geometric composition, phoenix-like abstract flame in terracotta "
        "rising from warm grey ashes on cream background, hopeful rebirth mood, "
        "grain texture, asymmetric poster layout, premium magazine cover style",
        "og/phoenix.png",
    ),
}


def gemini_generate(prompt: str) -> bytes | None:
    if not API_KEY:
        return None
    full = f"Generate a high-quality image: {prompt}\n\nAnchor: {ANCHOR}\n\nAvoid: {NEGATIVE}"
    try:
        resp = requests.post(
            OPENROUTER_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": GEMINI_MODEL, "messages": [{"role": "user", "content": full}]},
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()
        msg = data.get("choices", [{}])[0].get("message", {})
        images = msg.get("images", [])
        if images:
            url = images[0].get("image_url", {}).get("url", "")
            if "base64," in url:
                return base64.b64decode(url.split("base64,")[1])
        m = re.search(r"base64,([A-Za-z0-9+/=]{1000,})", str(data))
        if m:
            return base64.b64decode(m.group(1))
    except Exception as e:
        print(f"  gemini err: {e}", file=sys.stderr)
    return None


def pollinations_generate(prompt: str, width: int = 1600, height: int = 900) -> bytes | None:
    full = f"{prompt}. {ANCHOR}"
    encoded = urllib.parse.quote(full)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&model=flux&nologo=true&seed={abs(hash(prompt)) % 99999}"
    )
    try:
        resp = requests.get(url, timeout=180)
        if resp.status_code == 200:
            return resp.content
    except Exception as e:
        print(f"  pollinations err: {e}", file=sys.stderr)
    return None


def generate_one(name: str, prompt: str, out_rel: str) -> bool:
    out = REPO / out_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 10000:
        print(f"  [{name}] already exists, skipping")
        return True

    for attempt in range(2):
        print(f"  [{name}] gemini attempt {attempt + 1}...")
        data = gemini_generate(prompt)
        if data and len(data) > 10000:
            out.write_bytes(data)
            print(f"  [{name}] ✓ gemini ({len(data)} bytes)")
            return True
        time.sleep(2)

    print(f"  [{name}] gemini failed, trying pollinations...")
    width, height = (1200, 630) if out_rel.startswith("og/") else (1600, 900)
    for attempt in range(2):
        data = pollinations_generate(prompt, width, height)
        if data and len(data) > 10000:
            out.write_bytes(data)
            print(f"  [{name}] ✓ pollinations ({len(data)} bytes)")
            return True
        time.sleep(5)

    print(f"  [{name}] ✗ ALL SOURCES FAILED")
    return False


def main():
    if not API_KEY:
        print("WARN: OPENROUTER_API_KEY not set, using Pollinations only")
    print(f"Generating {len(SCENES)} images into {REPO}")
    results = {}
    for name, (prompt, rel) in SCENES.items():
        results[name] = generate_one(name, prompt, rel)

    ok = sum(results.values())
    total = len(results)
    print(f"\n=== Result: {ok}/{total} generated ===")
    failed = [n for n, v in results.items() if not v]
    if failed:
        print(f"FAILED: {failed}")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
