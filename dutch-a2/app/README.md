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

## Setup (one time)

1. Install the SDK:

   ```bash
   pip install anthropic
   ```

2. Get an API key at <https://platform.claude.com/> → Settings → API keys → Create key.

3. Create a file named **`dutch.txt`** in this folder (`dutch-a2/app/`) containing only your
   key, e.g.:

   ```
   sk-ant-api03-xxxxxxxxxxxxxxxx
   ```

   That's it — the app reads it automatically. (The file is gitignored, so it can't be
   accidentally committed.) If you prefer environment variables, setting
   `ANTHROPIC_API_KEY` works too and takes precedence.

## Run

```bash
cd dutch-a2/app
python3 tutor.py
```

Then open **http://localhost:8765** in your browser. Stop the server with `Ctrl+C`.

## How it works

- `tutor.py` is a tiny local web server. When you ask for an exercise, it sends the relevant
  course module plus a summary of your per-topic performance to the Claude API
  (`claude-sonnet-4-6` by default) and asks for a structured exercise; grading works the same
  way. The module text is prompt-cached, so repeated exercises are fast and cheap.
- Your progress lives in `dutch-a2/app/progress.json` on your machine — delete it to start
  fresh. Nothing is stored anywhere else; the only network traffic is to the Claude API.
- Set `CLAUDE_MODEL=claude-opus-4-8` (smarter, pricier) or `PORT=9000` via environment
  variables if you want to change the defaults.

## Cost

Each exercise or chat turn is one or two API calls of a few thousand (mostly cached) input
tokens and a short output — typically well under a cent per exercise on Sonnet 4.6.
A daily 20-exercise session costs a few cents.
