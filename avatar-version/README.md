# Story Teller

## Demo

Add your demo video link or thumbnail here.

Example:

```md
[![Watch the demo](./docs/demo-thumb.png)](https://your-demo-link)
```

The sections below are intended to sit directly under the demo once that link or thumbnail is added.

## Vision

Story Teller is a browser-first voice companion for young children built around a calm, simple interaction loop. Instead of presenting a dashboard full of controls, the app reduces the experience to a few child-readable surfaces: `Conversation` for grounded back-and-forth speaking practice, `Story Teller` for object-led storytelling, and `Settings` for parent-facing oversight. The goal is to make spoken interaction feel safe, focused, and inviting for a 2-4 year old without exposing technical complexity on the main screens.

At a higher level, this project is trying to turn voice AI into a gentle developmental tool rather than a noisy novelty. `Conversation` is designed to encourage 2-3 turn mini-conversations that help the child keep describing the same thing with a little more detail. `Story Teller` turns a child’s natural prompt into a short descriptive response and story without requiring structured input. The long-term vision is a trustworthy conversational companion that feels warm and responsive for the child while giving parents a clean record of what was said and how the system responded.

## Technical Architecture

The project is split into a React + TypeScript + Vite frontend in the `web/` directory and a FastAPI backend in the `backend/` directory. The frontend handles onboarding, mode routing, push-to-talk, live transcript display, and parent settings using React Router and Zustand. The backend owns auth, session state, websocket transport, streaming STT/TTS orchestration, LLM calls, transcript persistence, and a JSONL runtime trace for debugging. The live path is websocket-based end to end: browser mic audio is streamed to the backend, Sarvam STT produces transcripts, the LLM generates replies, Sarvam TTS returns audio, and the completed turn is sent back to the client and logged.

## Prompt Architecture

Prompting is behavior-specific rather than generic. `Story Teller` uses the full child transcript to infer the object, decide whether it is child-appropriate, describe it simply, and then tell a short story. `Conversation` uses recent turns from the active thread so the assistant can ask one grounded follow-up question and sustain a short 2-3 turn exchange. The prompt layer also includes recent-turn context, a lightweight topic anchor for short fragment replies, and fallback behavior so the assistant stays coherent even when STT returns brief or imperfect transcripts.

## What Is In This Repo

- `web/` — React + TypeScript + Vite frontend
- `backend/` — FastAPI backend for auth, session state, live websocket transport, STT/LLM/TTS orchestration, and transcript history
- `proposed-plan.md` — product plan for the current direction
- `ui-spec.md` — UI reference for the child-facing and parent-facing screens
- `instruction.md`, `changelog.md`, `future-roadmap.md` — working notes and project context

## Main Experience

### Conversation

The assistant listens to the child, reflects one concrete cue from what was said, and asks one calm follow-up question. The current implementation supports short multi-turn continuation so a child can stay on the same topic for 2-3 turns instead of restarting every time.

### Story Teller

The child speaks naturally, the full transcript goes to the LLM, and the assistant describes the object first and then tells a short story.

### Settings

Parent-facing controls for voice/default mode plus transcript history grouped by mode.

## How To Run

### 1. Backend setup

```bash
cd <project-directory>/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in the required values in `backend/.env`, especially:

- `SARVAM_API_KEY`
- any other voice/runtime settings you want to override

Then start the backend:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8010
```

### 2. Frontend setup

```bash
cd <project-directory>/web
npm install
cp .env.example .env.local
```

Set your frontend env to point at the backend:

```env
VITE_API_BASE_URL=http://127.0.0.1:8010/api/v1
VITE_WS_BASE_URL=ws://127.0.0.1:8010/api/v1
```

Then start the frontend:

```bash
npm run dev -- --host 127.0.0.1 --port 5173
```

### 3. Open the app

Use:

- frontend: [http://127.0.0.1:5173/](http://127.0.0.1:5173/)
- backend: [http://127.0.0.1:8010/](http://127.0.0.1:8010/)

## Notes

- Local machine-specific files such as `.env.local`, `.env`, virtualenvs, build artifacts, and runtime JSONL logs are intentionally not committed.
- Runtime turn traces are appended to:
  - `backend/runtime_logs/voice_turns.jsonl`
- The repository is intentionally trimmed to the standalone browser-first app and backend only.
