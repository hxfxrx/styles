# Dutch A2 Tutor — interactive local app

A small app that runs on your own computer and turns the [course modules](../README.md) into
an interactive tutor powered by Claude. It:

- **Generates exercises** (multiple choice, fill-in-the-blank, translation, word order, free
  response) from the module you're studying — never repeating itself.
- **Grades your answers live** with a 0–100 score, an explanation of the rule involved, and a
  model answer.
- **Adapts to you**: it tracks your accuracy per grammar topic in a local `progress.json` and
  automatically targets your weakest topics and adjusts difficulty (easy/normal/hard) to your
  recent scores.
- **Chats with you** in simple Dutch ("Gesprek" tab), correcting your mistakes gently and
  translating its replies.
- Shows a **live score bar** (session average + streak) and a **mastery dashboard** per topic.

## Requirements

- Python 3.9+ (`python3 --version` to check)
- An Anthropic API key — create one at <https://platform.claude.com/> (the API is pay-as-you-go
  and separate from a Claude.ai subscription)
- Optional: an ElevenLabs API key (<https://elevenlabs.io/>) for the voice features

## Setup (one time)

```bash
pip install anthropic
```

## Run

```bash
cd dutch-a2/app
python3 tutor.py
```

**The app asks for your API keys every time it starts** — first the Claude key (required),
then the ElevenLabs key (press Enter to skip voice). Input is hidden while you paste it, the
keys live only in the app's memory for that run, and nothing is ever written to disk. When
the server line appears, open **http://localhost:8765** in your browser. Stop with `Ctrl+C`.

## Voice (optional, via ElevenLabs)

If you enter an ElevenLabs key at startup, the app also trains **listening and speaking**:

- 🔊 buttons everywhere: hear any question, model answer, or chat reply in Dutch.
- **Dictation exercises**: a sentence is played (never shown); you type what you hear.
- **Read-aloud exercises**: you read a sentence into the microphone; your speech is
  transcribed and compared word-by-word — mismatches point at pronunciation problems.
- 🎤 **spoken answers** on any exercise, and full voice conversation in the Gesprek tab
  (speak → transcribed → tutor replies out loud).
- Listening and speaking get their own bars in the progress dashboard.

Generated audio is cached in `tts-cache/` so repeated phrases don't re-spend credits. Voice
and TTS/STT models are overridable via `ELEVEN_VOICE`, `ELEVEN_TTS_MODEL`, `ELEVEN_STT_MODEL`
environment variables. The microphone requires the page to be on `localhost` (it is) and your
browser to grant mic permission on first use.

## How it works

- `tutor.py` is a tiny local web server. When you ask for an exercise, it sends the relevant
  course module plus a summary of your per-topic performance to the Claude API
  (`claude-sonnet-4-6` by default) and asks for a structured exercise; grading works the same
  way. The module text is prompt-cached, so repeated exercises are fast and cheap.
- Your progress lives in `dutch-a2/app/progress.json` on your machine — delete it to start
  fresh. Nothing is stored anywhere else; the only network traffic is to the Claude API and
  (if voice is on) ElevenLabs.
- Set `CLAUDE_MODEL=claude-opus-4-8` (smarter, pricier) or `PORT=9000` via environment
  variables if you want to change the defaults.

## Cost

Each exercise or chat turn is one or two API calls of a few thousand (mostly cached) input
tokens and a short output — typically well under a cent per exercise on Sonnet 4.6.
A daily 20-exercise session costs a few cents. Voice adds a few hundred ElevenLabs
characters per spoken sentence.
