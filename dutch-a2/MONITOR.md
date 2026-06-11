# Project Monitor — how this branch manages the Dutch A2 project

This branch (`claude/dutch-a2-study-module-8b2xew`) is the **operations hub** for the Dutch
A2 learning project. The learning itself happens elsewhere (the Claude.ai Project, the local
app, paper study); *this* is where feedback lands, where the course evolves, and where new
capabilities get evaluated and integrated.

## 1. The loop

```
 you study (claude.ai Project / local app / paper)
        │
        ▼
 you notice something: an error, a friction, a wish, a new capability
        │
        ▼
 you open a Claude Code session on this branch and either
   a) add an entry to FEEDBACK.md (or just describe it in chat), or
   b) say one of the ritual commands below
        │
        ▼
 Claude Code triages → updates course files / app / instructions → commits → pushes
        │
        ▼
 you sync the changes back into where you study (see §4)
```

### Ritual commands (say these in a Claude Code session on this branch)

| You say | What happens |
|---|---|
| "process feedback" | Work through every open item in FEEDBACK.md: fix, implement, or explain why not; mark items done with what changed |
| "capability check" | Go through the watchlist (§3), search for what's newly possible, report findings, propose integrations |
| "course review" | Re-read the modules against my logged weak topics and feedback; tighten explanations, add exercises where I struggle |
| "release" | Bundle pending changes, bump the instruction version (§5), and produce the exact re-sync steps for the claude.ai Project |

## 2. Feedback intake

`FEEDBACK.md` is the inbox. Lowest-friction options, in order:

1. **Just say it in a session** — "module 4's directions vocabulary is too thin", "the toets
   command gives feedback too early". Claude logs it to FEEDBACK.md and acts on it.
2. **Edit FEEDBACK.md yourself** (on GitHub's web editor or locally) and start a session with
   "process feedback".
3. **Paste a save block** (`klaar` output from the claude.ai tutor) into FEEDBACK.md — these
   are treated as performance data: persistently weak topics trigger course improvements
   (more exercises, clearer explanations in that module).

Every processed item gets moved to the "Processed" section with a one-line resolution and the
commit that addressed it, so the file stays a readable history.

## 3. Capability watchlist

Checked on every "capability check". For each: what to look for, and what it would unlock.

| # | Capability | What to watch | Unlocks |
|---|---|---|---|
| W1 | **Claude.ai voice mode** on web/desktop (currently mobile-only dictation) | claude.ai release notes | Speaking practice in `gesprek` without leaving the Project |
| W2 | **Custom connectors / MCP in claude.ai Projects** | Whether a Project chat can call external tools on the user's plan | The claude.ai tutor could call ElevenLabs directly → voice inside Option 1, closing the gap with the local app |
| W3 | **ElevenLabs STT (Scribe) word-level confidence for Dutch** | ElevenLabs docs/changelog | True pronunciation *grading* (per-word scores), not just transcription |
| W4 | **ElevenLabs Conversational AI agents** | Latency + Dutch quality + bring-your-own-LLM | Real-time spoken conversation partner (Phase 3, §6) |
| W5 | **Claude API native audio input/output** | Claude API release notes | Single-vendor voice loop; would simplify the whole Phase 2 architecture |
| W6 | **Anki/spaced-repetition export formats** | stable | Auto-generate `.apkg` decks from the vocab lists + your miss-history |
| W7 | **Cheaper/faster Claude models** | model releases | Lower per-exercise cost in the local app |

Findings are logged in FEEDBACK.md under "Capability log" with a date, so the next check
doesn't repeat work.

## 4. Sync procedure (repo → where you study)

The repo is the **source of truth**; the claude.ai Project is a *deployment* of it.

After changes here:

- **Course content changed** (module files, vocab, grammar reference): in the claude.ai
  Project, delete the old file(s) from knowledge and upload the new ones. Only the changed
  files — the release notes will name them.
- **Tutor behavior changed** (`claude-ai-tutor.md` instruction block): re-paste the whole
  block into the Project's instructions. The version header (§5) tells you whether yours is
  stale.
- **Local app changed**: `git pull`, restart `tutor.py`.

A "release" command output always ends with a checklist of exactly which of these three
apply.

## 5. Versioning

The instruction block in `claude-ai-tutor.md` carries a version line (`INSTRUCTIONS v2 —
2026-06-11`). Any behavioral change bumps it. The claude.ai tutor states its version when
you type `start`, so a mismatch is immediately visible. `CHANGELOG.md` records every release
in two or three lines each.

## 6. Voice plan — ElevenLabs integration

**Goal:** add the two missing skills — *listening* and *speaking* — to a course that
currently trains reading and writing well. CEFR A2 requires all four.

**Where it lives:** the **local app** (Option 2), because claude.ai Projects can't call
external APIs today (watchlist W2 would change that). The claude.ai tutor keeps its
text-based modes; the local app becomes the voice trainer. They share the same course files
and the same topic-mastery model.

**Key handling:** same pattern as the Claude key — the ElevenLabs API key goes in a
gitignored `elevenlabs.txt` next to `tutor.py` (already in `.gitignore`). The app works
fully without it; voice features simply don't appear until the file exists.

### Phase 1 — Listening (TTS): smallest step, biggest gap closed

1. **"🔊 Luister" button** on every exercise, model answer, and chat reply: a new
   `/api/tts` endpoint sends the Dutch text to ElevenLabs (`eleven_multilingual_v2` or
   the cheaper `eleven_flash_v2_5`, both support Dutch) and streams the MP3 back to the
   browser. Audio is cached on disk by text-hash so repeated phrases (vocab words!) cost
   credits once.
2. **New exercise type: `dictee` (dictation).** The tutor generates a level-appropriate
   Dutch sentence; the UI plays it *without showing the text*; you type what you heard;
   Claude grades word-by-word. This is the single most effective listening drill at A2.
3. **Vocab audio:** the `woorden` flashcards play each Dutch word — fixes the
   ui/eu/g-pronunciation problem of learning from text alone.

*Effort: one session. Cost: a few hundred ElevenLabs characters per exercise — your
existing ElevenLabs credits go far at A2 sentence lengths.*

### Phase 2 — Speaking (STT + grading)

1. **Spoken answers:** a 🎤 button records via the browser (MediaRecorder), the server sends
   audio to ElevenLabs **Scribe** STT (Dutch supported), and the transcript is graded by
   Claude as usual — plus a comparison of the transcript against the expected sentence to
   flag the words the recognizer couldn't make out (a strong proxy for pronunciation
   problems: if Scribe heard "hond" when you said "hond", you're intelligible).
2. **Voice gesprek:** full loop — you speak, Scribe transcribes, Claude replies, TTS speaks
   the reply. Turn-based (press to talk), not real-time, which is actually *good* at A2:
   you get thinking time.
3. **Read-aloud drills:** the app shows a module dialogue line, you read it aloud, and the
   transcript-vs-target diff highlights which words to work on.
4. **Scoring model:** speaking results feed the same per-topic mastery store
   (`progress.json`) under new topics `listening` and `speaking`, so the dashboard and the
   adaptive targeting cover all four skills.

*Effort: one to two sessions. Depends on Phase 1.*

### Phase 3 — Real-time conversation (evaluate, don't assume)

ElevenLabs Conversational AI agents could host a streaming voice conversation with a Dutch
tutor persona (optionally backed by Claude as the LLM). Whether this beats the Phase 2
turn-based loop depends on latency, Dutch voice quality, and cost — this is watchlist item
W4, to be evaluated after Phase 2 is in daily use. Alternative trigger: W5 (Claude native
audio) would make Phase 3 a pure-Anthropic build.

### Holistic picture once Phases 1–2 land

| Skill | Where it's trained | Graded by |
|---|---|---|
| Reading | Modules, claude.ai drills | Claude |
| Writing | `schrijven` mode, drills | Claude |
| Listening | `dictee` + audio everywhere (local app) | Claude (your transcript vs. target) |
| Speaking | Spoken answers, voice gesprek, read-aloud (local app) | Scribe transcript + Claude |
| Vocabulary | `woorden` with audio, both options | Claude + miss-history |

A balanced week then looks like: claude.ai drills on commute (text, subscription credits),
two local-app voice sessions (listening + speaking, ElevenLabs + API credits), one
`schrijven` and one `toets` — all feeding one mastery picture.

## 7. Decision rubric for anything new

When a new idea or capability surfaces, it goes where it fits:

1. **Prompt- or content-only?** → claude.ai Project (edit course files / instruction block
   here, then sync). Zero infrastructure.
2. **Needs code or an external API?** → local app. It's the extensibility surface.
3. **Heavy/standalone** (e.g. a mobile app, an Anki pipeline, a real-time voice agent) →
   separate tool in this repo (`dutch-a2/<tool>/`), same key-file conventions.
4. **Not worth it yet** → watchlist entry with a trigger condition, so it's re-checked
   instead of forgotten.
