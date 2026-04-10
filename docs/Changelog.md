# Changelog

(prepend-only; most recent at top)

## Sprint timeline

```mermaid
graph LR
  S0[S0 Retro Audit<br/>10/10 r5] --> S2[S2 Docs + Proxy<br/>10/10 r3]
  S2 --> S3[S3 Art + Gameplay<br/>10/10 r2]
  S3 --> S6[S6 Deploy + Verify<br/>v1.0 Launch]
  S6 --> S7[S7 Launch Kit<br/>Day 2]
```

## 2026-04-11 — v1.0 Launch

### S6 — Deploy & Verify
- Deployed to `TimmyZinin/timmyzinin.github.io` monorepo subfolder `entrepreneur-quest/`
- `curl -sI https://timzinin.com/entrepreneur-quest/` → HTTP/2 200 ✓
- Jina Reader SPA render check passed (title, HUD, scene 1 visible)
- E2E on prod via Playwright: start → 7 scenes → ending (exit) → CTA → form → success
- Real lead submitted via prod → delivered to `@timzinin_quest_lead_bot` ✓
- 6 MUST docs written (Home, GDD, Scenes-Script, Economy-Balance, Tech-Architecture, Deployment, Changelog)

### S3 — Art, HTML, Audio, Gameplay ✓ 10/10 round 2
- 12 editorial 2D WebP via Gemini 2.5 Flash (7 scenes + 4 archetype OGs + hero)
- 1 BGM 75s Cmaj7 ambient loop + 5 SFX via ffmpeg synth
- Full game engine (game.js): state machine, 3-act scene picker, audio, HUD, share URLs
- FastAPI proxy lead flow (lead.js)
- Codex fixes: CSP strict, trim validation, prefers-reduced-motion, determinism, a11y

### S2 — Docs & FastAPI Proxy ✓ 10/10 round 3
- `scenes.json` — 10 scenes in strict 3-act structure, 4 archetype endings
- Balance simulator 1000 runs: 96.7% completion, all archetypes reachable
- `dialogues.json` — UI copy, share presets, CTA
- FastAPI lead-proxy deployed on Contabo (docker, multi-layered auth)
- Bot `@timzinin_quest_lead_bot` created via Telethon → BotFather
- E2E verified via curl POST

### S0 — Retrospective Audit ✓ 10/10 round 5
- Plan v2 → v2.3 after 5 rounds of Codex adversarial
- Key fixes: pixel override documented, FastAPI proxy, HMAC removed, HTMLAudioElement, balance sim, KPI metrics, CSP, SEC checklist
