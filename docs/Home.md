# Entrepreneur Quest

**Live:** https://timzinin.com/eq/
**Repo:** https://github.com/TimmyZinin/entrepreneur-quest
**Lead proxy:** https://github.com/TimmyZinin/lead-proxy (private)

Интерактивная история "Год Марины" — браузерный лид-магнит для AI-трансформации консалтинга Тима Зинина.

## Архитектура воронки

```mermaid
graph TD
  Visitor[Посетитель соц-сети] -->|UTM link| Game[Entrepreneur Quest — 7 сцен]
  Game --> Archetype{Archetype}
  Archetype -->|Exit| ShareExit[Share poster 'Exit Marina']
  Archetype -->|Growth| ShareGrowth[Share poster 'Growth Marina']
  Archetype -->|Burnout| ShareBurn[Share poster 'Burnout Marina']
  Archetype -->|Phoenix| SharePhoenix[Share poster 'Phoenix Marina']
  Archetype --> CTA[CTA 'Получи план трансформации']
  CTA --> Form[2-step lead form]
  Form -->|FastAPI proxy| Bot[@timzinin_quest_lead_bot]
  Bot --> Tim[Тим → ручной ответ]
  Tim --> Call[$200 консультация]
  Call --> Retainer[$3K/мес интеграция]
  ShareExit --> NewVisitor[Новый посетитель]
  NewVisitor --> Game
```

## Sprint outcomes

| Sprint | Status | Score |
|---|---|---|
| S0 Retrospective Audit | ✅ | 10/10 round 5 |
| S2 Docs & scenes & FastAPI proxy | ✅ | 10/10 round 3 |
| S3 Art & HTML & Audio & Gameplay | ✅ | 10/10 round 2 |
| S6 Deploy & Verify | ✅ | in progress |
| S7 Launch Kit | ⏳ | Day 2 |

## Metrics targets

- Completion rate ≥70%
- Completion→Lead ≥8%
- Share CTR ≥15%
- Session duration 3-5 min

## Page index

- [GDD](GDD.md) — core loop and 3-act structure
- [Scenes Script](Scenes-Script.md) — full text of 10 scenes + 4 endings
- [Economy Balance](Economy-Balance.md) — deltas table and simulation results
- [Tech Architecture](Tech-Architecture.md) — client-only state machine + lead flow
- [Deployment](Deployment.md) — GitHub Pages monorepo + FastAPI proxy on Contabo
- [Changelog](Changelog.md) — prepend-only log
