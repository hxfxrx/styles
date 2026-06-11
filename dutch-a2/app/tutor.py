#!/usr/bin/env python3
"""Interactive Dutch A2 tutor — local web app backed by the Claude API.

Run:  pip install anthropic
      export ANTHROPIC_API_KEY=sk-ant-...
      python3 tutor.py
Then open http://localhost:8765
"""
import json
import os
import sys
import threading
from glob import glob
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    import anthropic
except ImportError:
    sys.exit("The 'anthropic' package is missing. Install it with:  pip install anthropic")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
COURSE_DIR = os.path.dirname(APP_DIR)
PROGRESS_FILE = os.path.join(APP_DIR, "progress.json")
MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
PORT = int(os.environ.get("PORT", "8765"))

TOPICS = [
    "pronunciation", "present_tense", "articles_de_het", "negation", "questions",
    "numbers_time", "word_order", "separable_verbs", "plurals", "possessives",
    "adjectives", "demonstratives", "prepositions", "modal_verbs", "imperative",
    "object_pronouns", "perfectum", "imperfectum", "future", "conjunctions",
    "comparatives", "er", "vocabulary",
]

EXERCISE_SCHEMA = {
    "type": "object",
    "properties": {
        "exercise_type": {
            "type": "string",
            "enum": ["multiple_choice", "fill_blank", "translate_to_dutch",
                     "reorder", "free_response"],
        },
        "topic": {"type": "string", "enum": TOPICS},
        "difficulty": {"type": "string", "enum": ["easy", "normal", "hard"]},
        "instructions": {"type": "string",
                         "description": "One short line telling the learner what to do, in English."},
        "question": {"type": "string",
                     "description": "The exercise itself. For fill_blank use ___ for the gap."},
        "options": {"type": "array", "items": {"type": "string"},
                    "description": "Answer choices for multiple_choice, or the shuffled words "
                                   "for reorder. Empty array for other types."},
    },
    "required": ["exercise_type", "topic", "difficulty", "instructions", "question", "options"],
    "additionalProperties": False,
}

GRADE_SCHEMA = {
    "type": "object",
    "properties": {
        "correct": {"type": "boolean"},
        "score": {"type": "integer",
                  "description": "0-100. Full credit 100; minor spelling slip 70-90; "
                                 "right idea wrong grammar 40-60; wrong 0-30."},
        "correct_answer": {"type": "string",
                           "description": "A model answer in Dutch."},
        "feedback": {"type": "string",
                     "description": "Two or three encouraging sentences in English explaining "
                                    "what was right or wrong and the rule involved."},
    },
    "required": ["correct", "score", "correct_answer", "feedback"],
    "additionalProperties": False,
}

CHAT_SCHEMA = {
    "type": "object",
    "properties": {
        "reply": {"type": "string",
                  "description": "Your conversational reply in simple Dutch, 1-3 short sentences, "
                                 "ending with a question to keep the conversation going."},
        "correction": {"type": "string",
                       "description": "If the learner's last message had a mistake: the corrected "
                                      "Dutch plus a one-line English explanation. Empty string if "
                                      "their message was fine."},
        "translation": {"type": "string",
                        "description": "English translation of your reply."},
    },
    "required": ["reply", "correction", "translation"],
    "additionalProperties": False,
}

def resolve_api_key():
    """Use ANTHROPIC_API_KEY if set; otherwise read dutch.txt next to this script."""
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        try:
            with open(os.path.join(APP_DIR, "dutch.txt"), encoding="utf-8") as f:
                key = f.read().strip()
        except FileNotFoundError:
            pass
    return key


API_KEY = resolve_api_key()
client = anthropic.Anthropic(api_key=API_KEY or None)
_lock = threading.Lock()


def load_modules():
    modules = {}
    for path in sorted(glob(os.path.join(COURSE_DIR, "module-*.md"))):
        num = int(os.path.basename(path).split("-")[1])
        with open(path, encoding="utf-8") as f:
            modules[num] = f.read()
    return modules


MODULES = load_modules()


def load_progress():
    try:
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"topics": {}, "history": []}


def save_progress(progress):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)


def record_result(topic, score):
    with _lock:
        p = load_progress()
        t = p["topics"].setdefault(topic, {"attempts": 0, "correct": 0, "ema": 0.5})
        t["attempts"] += 1
        if score >= 70:
            t["correct"] += 1
        t["ema"] = round(0.7 * t["ema"] + 0.3 * (score / 100), 3)
        p["history"].append({"topic": topic, "score": score})
        p["history"] = p["history"][-200:]
        save_progress(p)
        return p


def learner_summary():
    """A compact description of the learner's strengths/weaknesses for the prompt."""
    p = load_progress()
    if not p["topics"]:
        return ("This learner is just starting; no performance data yet. "
                "Use 'normal' difficulty and vary topics."), "normal"
    parts = []
    for topic, t in sorted(p["topics"].items(), key=lambda kv: kv[1]["ema"]):
        parts.append(f"{topic}: {t['ema']:.2f} mastery over {t['attempts']} attempts")
    recent = [h["score"] for h in p["history"][-10:]]
    avg = sum(recent) / len(recent)
    difficulty = "hard" if avg > 85 else "easy" if avg < 60 else "normal"
    summary = (
        "Per-topic mastery (0=struggling, 1=mastered), weakest first:\n- "
        + "\n- ".join(parts)
        + f"\nAverage score over the last {len(recent)} exercises: {avg:.0f}/100."
    )
    return summary, difficulty


def system_for_module(module):
    """Stable system prompt per module (cacheable prefix); learner stats go in the user turn."""
    return [{
        "type": "text",
        "text": (
            "You are a Dutch language tutor for an English-speaking learner working toward "
            "CEFR A2. You generate exercises and grade answers strictly based on the course "
            "module below. Only use vocabulary and grammar introduced in this module or "
            "earlier ones (modules are cumulative: module 1 = absolute basics, module 6 = "
            "full A2). Exercises must be self-contained and unambiguous.\n\n"
            "=== COURSE MODULE ===\n" + MODULES[module]
        ),
        "cache_control": {"type": "ephemeral"},
    }]


def call_claude(system, user_text, schema, effort):
    resp = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=system,
        messages=[{"role": "user", "content": user_text}],
        output_config={"format": {"type": "json_schema", "schema": schema},
                       "effort": effort},
    )
    if resp.stop_reason == "refusal":
        raise RuntimeError("The model declined this request; please try again.")
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)


def make_exercise(module, avoid):
    summary, difficulty = learner_summary()
    user = (
        f"{summary}\n\n"
        f"Create ONE new exercise at '{difficulty}' difficulty.\n"
        "Pick the topic with a strong bias toward the learner's weakest topics that this "
        "module covers; occasionally mix in a stronger topic to keep variety.\n"
        + (f"Do not repeat these recent questions: {avoid}\n" if avoid else "")
        + "Vary the exercise type. For 'reorder', put the words of the target sentence "
          "shuffled into options. Do not include the answer anywhere in the exercise."
    )
    return call_claude(system_for_module(module), user, EXERCISE_SCHEMA, "low")


def grade_answer(module, exercise, answer):
    user = (
        "Grade this learner's answer.\n\n"
        f"Exercise: {json.dumps(exercise, ensure_ascii=False)}\n"
        f"Learner's answer: {json.dumps(answer, ensure_ascii=False)}\n\n"
        "Be fair at A2 level: ignore capitalization and accept minor punctuation "
        "differences; for free responses accept any correct, level-appropriate answer."
    )
    result = call_claude(system_for_module(module), user, GRADE_SCHEMA, "medium")
    progress = record_result(exercise.get("topic", "vocabulary"),
                             max(0, min(100, int(result["score"]))))
    result["progress"] = progress
    return result


CHAT_SYSTEM = [{
    "type": "text",
    "text": (
        "You are a friendly Dutch conversation partner for an A1-A2 learner. Speak only "
        "simple Dutch using high-frequency words and short main clauses (occasional "
        "'omdat/als' subclauses are fine at A2). Stay on everyday topics: introductions, "
        "family, food, weather, daily routine, weekend plans, travel. Gently correct "
        "mistakes. Steer the conversation toward the learner's weak topics when natural."
    ),
    "cache_control": {"type": "ephemeral"},
}]


def chat_turn(messages):
    summary, _ = learner_summary()
    convo = [{"role": m["role"], "content": m["content"]} for m in messages[-20:]]
    while convo and convo[0]["role"] != "user":  # history must start with a user turn
        convo.pop(0)
    if not convo:
        raise ValueError("empty conversation")
    convo[-1]["content"] = (
        f"<learner_profile>\n{summary}\n</learner_profile>\n\n" + convo[-1]["content"]
    )
    resp = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=CHAT_SYSTEM,
        messages=convo,
        output_config={"format": {"type": "json_schema", "schema": CHAT_SCHEMA},
                       "effort": "medium"},
    )
    if resp.stop_reason == "refusal":
        raise RuntimeError("The model declined this request; please try again.")
    text = next(b.text for b in resp.content if b.type == "text")
    return json.loads(text)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, payload, content_type="application/json"):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            with open(os.path.join(APP_DIR, "index.html"), "rb") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif self.path == "/api/progress":
            self._send(200, load_progress())
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
            if self.path == "/api/exercise":
                module = int(body.get("module", 1))
                if module not in MODULES:
                    raise ValueError(f"unknown module {module}")
                self._send(200, make_exercise(module, body.get("avoid", [])))
            elif self.path == "/api/grade":
                self._send(200, grade_answer(int(body.get("module", 1)),
                                             body["exercise"], body["answer"]))
            elif self.path == "/api/chat":
                self._send(200, chat_turn(body["messages"]))
            else:
                self._send(404, {"error": "not found"})
        except anthropic.AuthenticationError:
            self._send(502, {"error": "Invalid or missing ANTHROPIC_API_KEY."})
        except anthropic.APIError as e:
            self._send(502, {"error": f"Claude API error: {e.message}"})
        except Exception as e:  # surface anything else to the UI instead of a blank failure
            self._send(500, {"error": str(e)})


def main():
    if not API_KEY:
        sys.exit(
            "No API key found. Easiest fix: create a file named dutch.txt in this folder\n"
            f"  ({APP_DIR})\n"
            "containing only your key (sk-ant-...). Get a key at https://platform.claude.com/\n"
            "Alternatively, set the ANTHROPIC_API_KEY environment variable."
        )
    if not MODULES:
        sys.exit(f"No module-*.md files found in {COURSE_DIR} — run from inside dutch-a2/app/.")
    print(f"Dutch A2 tutor running on http://localhost:{PORT}  (model: {MODEL})")
    print("Press Ctrl+C to stop.")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
