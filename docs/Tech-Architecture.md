# Tech Architecture

## Client-only stack

- **Language:** Vanilla JS + DOM + CSS (zero dependencies, ~25KB bundled)
- **Rendering:** `<div>` background-image per scene, CSS transforms for parallax, SVG noise grain overlay (data-URI)
- **Fonts:** Google Fonts — Instrument Serif Italic + Space Grotesk
- **Audio:** HTMLAudioElement only (not Web Audio API, better TG WebView compatibility)
- **State persistence:** sessionStorage (prefixed `eq:`)
- **Analytics:** Umami self-hosted

## State machine

```mermaid
graph TD
  Boot[boot loads scenes.json + dialogues.json] --> Start[start-screen]
  Start -->|click НАЧАТЬ| Game[game-screen scene i]
  Game -->|click choice A or B| Outcome[outcome-screen]
  Outcome -->|click Дальше| Check{more scenes?}
  Check -->|yes & no game over| Game
  Check -->|no or game over| Ending[ending-screen archetype]
  Ending -->|click CTA| CTAForm[cta-screen 2-step form]
  CTAForm -->|submit valid| Success[success-screen]
  Success -->|click Поделиться| Ending
```

## 3-act scene picker

```mermaid
graph LR
  Pool[10 scenes] --> Fixed[Fixed: s01, s06, s07]
  Pool --> Act1Non[Act 1 non-fixed: s02]
  Pool --> Act2Pool[Act 2 pool: s03, s04, s05, s08, s09, s10]
  Fixed --> Order
  Act1Non --> Order
  Act2Pool --> Shuffle[Shuffle] --> Take3[Take 3] --> Order
  Order[Order: s01 + s02 + 3 random + s06 + s07] --> Play[7 scenes]
```

`pickScenes` in both `tools/simulate.js` and `game.js` for consistency.

## Lead flow (security-critical)

```mermaid
sequenceDiagram
  participant Browser as Browser (timzinin.com)
  participant Proxy as FastAPI proxy<br/>(marshall.timzinin.com/quest-api)
  participant TG as Telegram Bot API
  participant Bot as @timzinin_quest_lead_bot
  Browser->>Browser: validateForm() trim + regex
  Browser->>Proxy: POST /lead<br/>{name, handle, pain, archetype,<br/>session_started_at, website: ""}
  Note over Browser,Proxy: Origin: timzinin.com (auto)
  Proxy->>Proxy: Origin check
  Proxy->>Proxy: CORS allowlist
  Proxy->>Proxy: slowapi rate limit 3/hour/IP
  Proxy->>Proxy: Honeypot check (website empty)
  Proxy->>Proxy: Session duration ≥30s
  Proxy->>Proxy: Pydantic validate
  Proxy->>TG: sendMessage chat_id=64242118<br/>Authorization: Bot {TOKEN from .env}
  TG->>Bot: Deliver to Tim's chat with bot
  Proxy-->>Browser: 200 {"ok":true}
  Browser->>Browser: setRateLimit() + setScreen(success)
```

**Security layers:**
1. Token **only** in `/opt/lead-proxy/.env` on Contabo VPS 30 — never in frontend
2. Origin header check (browser auto-sets)
3. CORS allowlist: `https://timzinin.com`, localhost dev
4. slowapi rate limit 3/hour/IP
5. Honeypot field (bots fill it, humans don't)
6. Session duration gate ≥30 seconds (bots submit instantly)
7. Pydantic validators: name regex, handle format, pain HTML strip, archetype enum
8. Client sessionStorage rate limit 1/session (defense in depth)

## Audio engine

```mermaid
flowchart LR
  Mute[Mute toggle<br/>sessionStorage eq:mute] --> Apply[applyMute]
  Start[Start button click] --> Play[audio.play BGM]
  Choice[Choice click] --> SFX[playSfx click/up/down/turn]
  Ending[Ending reach] --> Duck[duckBgm volume 0.15]
  Ending --> Success[playSfx success]
```

No `new AudioContext()` anywhere. All via HTML `<audio>` elements and `audio.play()/pause()/volume`.

## File layout

```
entrepreneur-quest/
├── index.html              # Entry, CSP meta, preload audio/fonts
├── game.js                 # State machine, rendering, shuffle, hooks
├── lead.js                 # Fetch to FastAPI, validation, rate limit
├── styles.css              # :root from archione, keyframes, mobile-first
├── data/
│   ├── scenes.json         # Source of truth — 10 scenes + 4 endings
│   └── dialogues.json      # UI copy, share presets, CTA, tooltip
├── img/
│   ├── hero.webp
│   └── scenes/s01..s07.webp (7 Gemini 2.5 Flash editorial)
├── og/
│   └── exit|growth|burnout|phoenix.webp (4 archetype posters)
├── audio/
│   ├── bgm.mp3             # 75s Cmaj7 ambient loop (ffmpeg synth)
│   └── click|up|down|turn|success.mp3 (5 SFX ffmpeg synth)
├── tools/
│   ├── simulate.js         # Balance simulator
│   ├── gen_art.py          # Gemini batch
│   ├── gen_bgm.sh          # ffmpeg BGM
│   ├── gen_sfx.sh          # ffmpeg SFX (deterministic seed)
│   └── style_bible.md      # Art direction anchor
└── docs/                   # 6 MUST documentation pages (this folder)
```

## QA hooks (develop-web-game skill compatibility)

```javascript
window.render_game_to_text = () => JSON.stringify({
  screen, scene_idx, total, current_scene, resources, archetype, gameOver, muted
});
window.advanceTime = () => {}; // event-driven, no frame stepping
```

QA override: `?ending=exit|growth|burnout|phoenix` jumps directly to ending screen for visual verification.
