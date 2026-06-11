# Feedback inbox

Drop anything here: course errors, friction, wishes, tutor misbehavior, `klaar` save blocks.
Each Claude Code session on this branch processes open items ("process feedback") and moves
them to **Processed** with a resolution. Format is free-form; a date helps.

## Open

_(nothing — add items below this line)_

## Save blocks (performance data)

_(paste `klaar` outputs here; persistently weak topics drive course improvements)_

## Capability log

- 2026-06-11 — Voice v3 live test from Claude Code blocked: the remote environment's
  network allowlist doesn't include api.elevenlabs.io (proxy 403 host_not_allowed).
  Code path verified with mocked responses instead. To enable live tests in future
  sessions, add api.elevenlabs.io to this environment's network policy at
  code.claude.com. User will live-test locally.

- 2026-06-11 — Watchlist created (see MONITOR.md §3). Baseline: claude.ai voice is
  mobile-dictation only; Projects cannot call external tools; ElevenLabs TTS + Scribe STT
  both support Dutch; no Claude native audio API.

## Processed

- 2026-06-11 — Voice Phases 1+2 built into the local app (TTS, dictation, read-aloud,
  spoken answers, voice gesprek). Pending: live test with a real ElevenLabs key. (v3)

- 2026-06-11 — Course created (modules 1–6, references, local app). Commits up to `c82bc22`.
- 2026-06-11 — Default model → Sonnet 4.6; API key via `dutch.txt` file. (`378460d`)
- 2026-06-11 — Claude.ai Project option added and fine-tuned: save/resume blocks, fresh
  exercises only, woorden/schrijven/toets/uitleg modes. (`5bf75f2`, `c82bc22`)
