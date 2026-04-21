# Story Teller

## Demo

Add your video walkthrough link, embedded GitHub asset, or clickable thumbnail here.

Example:

https://github.com/user-attachments/assets/192c3ab3-5775-4544-958f-7c204839c61c
Story Mode in English

This project has the following features:

- Normal app: three-screen child-facing experience
- Conversation mode: 2-3 turn grounded exchange
- Story Teller mode: object-led story from speech
- Avatar version: duck overlay and Chrome extension flow
- Parent/settings view: transcript history and controls

The sections below are intended to sit directly under the demo once that link or thumbnail is added.

## Vision

Story Teller is a browser-first voice companion for young children built around a calm, simple interaction loop. Instead of presenting a dashboard full of controls, the app reduces the experience to a few child-readable surfaces: `Conversation` for grounded back-and-forth speaking practice, `Story Teller` for object-led storytelling, and `Settings` for parent-facing oversight. The goal is to make spoken interaction feel safe, focused, and inviting for a 2-4 year old without exposing technical complexity on the main screens.

At a higher level, this project is trying to turn voice AI into a gentle developmental tool rather than a noisy novelty. `Conversation` is designed to encourage 2-3 turn mini-conversations that help the child keep describing the same thing with a little more detail. `Story Teller` turns a child’s natural prompt into a short descriptive response and story without requiring structured input. The long-term vision is a trustworthy conversational companion that feels warm and responsive for the child while giving parents a clean record of what was said and how the system responded.

## Technical Architecture

The project is split into a React + TypeScript + Vite frontend in the `web/` directory and a FastAPI backend in the `backend/` directory. The frontend handles onboarding, mode routing, push-to-talk, live transcript display, and parent settings using React Router and Zustand. The backend owns auth, session state, websocket transport, streaming STT/TTS orchestration, LLM calls, transcript persistence, and a JSONL runtime trace for debugging. The live path is websocket-based end to end: browser mic audio is streamed to the backend, Sarvam STT produces transcripts, the LLM generates replies, Sarvam TTS returns audio, and the completed turn is sent back to the client and logged.

The voice intelligence stack is built around three Sarvam systems. `saaras:v3` handles speech-to-text in `transcribe` mode so the backend receives the child’s spoken words and detected language code. `sarvam-30b` is the LLM used for mode-specific behavior: grounded conversation, object inference, child-safe Story Teller responses, and language-sensitive replies. `bulbul:v3` handles text-to-speech and streams spoken audio back to the client. The backend keeps these stages separate so a turn can be inspected as STT input, LLM reply, and TTS output in `runtime_logs/voice_turns.jsonl`.

## Prompt Architecture

Prompting is behavior-specific rather than generic. `Story Teller` uses the full child transcript to infer the object, decide whether it is child-appropriate, describe it simply, and then tell a short story. `Conversation` uses recent turns from the active thread so the assistant can ask one grounded follow-up question and sustain a short 2-3 turn exchange. The prompt layer also includes recent-turn context, a lightweight topic anchor for short fragment replies, and fallback behavior so the assistant stays coherent even when STT returns brief or imperfect transcripts.

Prompting directly shapes the child’s experience, so the prompts are written to avoid sounding like a test, chatbot, or noisy entertainer. Conversation prompts ask the assistant to reflect one concrete cue from the child’s speech, stay on the same topic for a short mini-conversation, and use simple child-friendly language. The assistant should invite more speech without over-questioning, avoid loud praise every turn, and use natural caregiver-style phrasing in Marathi or Hindi rather than stiff literal translations. Story Teller prompts keep output short, safe, concrete, and easy to follow: first describe the object, then tell a tiny story. Language handling is also part of the UX: if STT detects English, the prompt and TTS should stay English; if Marathi or Hindi is detected, the assistant should respond naturally in that language.

## What Is In This Repo

- `web/` — React + TypeScript + Vite frontend
- `backend/` — FastAPI backend for auth, session state, live websocket transport, STT/LLM/TTS orchestration, and transcript history
- `avatar-version/` — isolated experimental copy with a duck avatar UI and Chrome extension prototype
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

## Avatar Version

`avatar-version/` is an isolated version of the project for experimenting with a child-facing animated duck avatar and a browser extension flow. It is intentionally separate from the normal app so avatar experiments do not destabilize the main three-screen experience.

The avatar version contains:

- a copied FastAPI backend configured for local port `8020`
- a copied React frontend configured for local port `5174`
- a canvas-based duck sprite renderer in the web UI
- a Chrome extension under `avatar-version/extension/`
- a floating duck overlay that can run on webpages
- a `Talk | Story` mode toggle for `conversation` and `story_teller`
- a `Reset audio` control for stopping playback or clearing stuck audio state

The extension bypasses onboarding and creates a temporary backend session as `Browser Avatar`. Clicking the duck records microphone audio, streams PCM16 audio to the backend websocket, shows detected transcript text in a hovering bubble, shows the assistant response in the same bubble, and plays TTS audio returned by the backend.

For avatar-version local development:

- backend: [http://127.0.0.1:8020/](http://127.0.0.1:8020/)
- frontend: [http://127.0.0.1:5174/](http://127.0.0.1:5174/)

## How To Run

The normal app and avatar-version run on different ports.

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

## How To Run Avatar Version

### 1. Avatar backend

```bash
cd <project-directory>/avatar-version/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8020
```

If you already maintain a shared Python environment for this repo, you can use that environment instead of creating a new `.venv`.

### 2. Avatar frontend

```bash
cd <project-directory>/avatar-version/web
npm install
cp .env.example .env.local
```

Set:

```env
VITE_API_BASE_URL=http://127.0.0.1:8020/api/v1
VITE_WS_BASE_URL=ws://127.0.0.1:8020/api/v1
```

Then run:

```bash
npm run dev -- --host 127.0.0.1 --port 5174
```

### 3. Avatar Chrome extension

1. Start the avatar backend on `8020`.
2. Open Chrome Extensions.
3. Enable Developer mode.
4. Choose Load unpacked.
5. Select `<project-directory>/avatar-version/extension`.
6. Open a normal webpage and click the floating duck.

## Notes

- Local machine-specific files such as `.env.local`, `.env`, virtualenvs, build artifacts, and runtime JSONL logs are intentionally not committed.
- Runtime turn traces are appended to:
  - `backend/runtime_logs/voice_turns.jsonl`
- Avatar-version runtime traces are appended to:
  - `avatar-version/backend/runtime_logs/voice_turns.jsonl`
- The repository is intentionally trimmed to the standalone browser-first app and backend only.
