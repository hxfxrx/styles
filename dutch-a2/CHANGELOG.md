# Changelog

Releases of the Dutch A2 project. After each release, sync per MONITOR.md §4.

## v5 — 2026-06-11

- Local app parked at user request; claude.ai Project is the single learning path. Docs
  rewritten accordingly (no code deleted — everything stays in `app/` for a possible
  un-parking later).
- Sync: nothing to re-upload; docs-only.

## v4 — 2026-06-11

- Local app: API keys are no longer stored in files. The app prompts for the Claude key and
  (optionally) the ElevenLabs key at every startup; keys live in memory only. All key-file
  docs removed.
- Sync: `git pull` + restart `tutor.py`. Local `dutch.txt` / `elevenlabs.txt` files can be
  deleted — they are no longer read.

## v3 — 2026-06-11

- Local app: ElevenLabs voice integration (MONITOR.md §6, Phases 1+2). TTS playback with
  disk cache, dictation + read-aloud exercise types, spoken answers via Scribe STT, voice
  conversation with auto-speak, listening/speaking in the mastery dashboard. Enabled by an
  `elevenlabs.txt` key file; app stays text-only without it.
- Sync: `git pull` + restart `tutor.py`. No claude.ai Project changes.

## v2 — 2026-06-11

- Claude.ai tutor instructions reworked: save/resume across chats (`klaar`/`start`), never
  reuses printed module exercises, new modes `woorden`, `schrijven`, `toets`, `uitleg`.
- Sync: re-paste the instruction block; no knowledge files changed.

## v1 — 2026-06-11

- Initial course (modules 1–6, grammar reference, core vocabulary, resources), local tutor
  app (Sonnet 4.6 default, `dutch.txt` key file), first claude.ai Project instructions.
