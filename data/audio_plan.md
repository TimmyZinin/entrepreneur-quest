# Audio plan

## BGM (1 loop, ~75 sec)
**Target mood:** melancholic editorial piano, muted strings, warm, slow ~70bpm, loopable
**Primary source:** Suno AI (prompt below)
**Fallback:** Pixabay CC0 `https://pixabay.com/music/search/genre/cinematic/mood/melancholic/`

### Suno prompt
```
melancholic editorial piano, muted strings layer, soft sub bass, warm analog tape texture, 70 bpm, 4/4, introspective but hopeful, slow build, ends on unresolved note for loop, 75 seconds, no vocals, no drums
```

### Requirements
- Format: MP3 or WebM/Opus
- Bitrate: 128-192 kbps
- Normalized to -16 LUFS (ffmpeg `loudnorm=-16:11:-1.5`)
- Output: `audio/bgm.mp3`

## 5 SFX (all CC0 Freesound or similar)

| Name | Purpose | Target sound | Source hint |
|---|---|---|---|
| click | Button press | Soft UI click, tiny reverb | Freesound CC0 "soft click ui" |
| up | Resource increased | Rising chime, short, warm | Freesound CC0 "positive chime" |
| down | Resource decreased | Low thud, soft | Freesound CC0 "thud warm" |
| turn | Scene transition | Page turn or whoosh | Freesound CC0 "page turn" |
| success | Ending reveal | Soft stinger, triumphant but restrained | Freesound CC0 "stinger soft" |

### SFX processing
- ffmpeg `loudnorm=-18:9:-2` for all SFX
- Format: MP3 44.1kHz 128kbps
- Length: 0.2-0.8 sec each
- Output: `audio/{click|up|down|turn|success}.mp3`

## Audio engine (no Web Audio API)
- `<audio>` HTML elements preloaded in index.html
- `audio.play()` triggered on user gestures (start button + choice clicks)
- `audio.volume` for ducking (music → 0.3 during endings, → 0.8 otherwise)
- Mute toggle persisted in sessionStorage key `eq:mute`
- `playsinline` + `preload="auto"` attributes for iOS compat

## Licensing record
- BGM: Suno AI — Tim owns (commercial license via paid tier, or Pixabay CC0 attribution if fallback)
- SFX: All Freesound Creative Commons 0 (CC0) — no attribution required
- Full attribution list → `Audio-Design.md` Wiki page in S7
