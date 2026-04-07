# Story Teller

Story Teller is a child-facing voice app with a simple three-screen experience:

- `Conversation`
- `Story Teller`
- `Settings`

This standalone repo was split out from earlier exploratory work so it contains only the browser-first app and backend needed for the conversational companion experience.

## What is in this repo

- `web/` — React + TypeScript + Vite frontend
- `backend/` — FastAPI backend for auth, session state, live websocket transport, STT/LLM/TTS orchestration, and transcript history
- `proposed-plan.md` — product plan for the current direction
- `ui-spec.md` — UI reference for the child-facing and parent-facing screens
- `instruction.md`, `changelog.md`, `future-roadmap.md` — working notes and project context

## Experience

### Conversation
The assistant listens to the child, reflects one concrete cue from what was said, and asks one calm follow-up question.

### Story Teller
The child speaks naturally, the full transcript goes to the LLM, and the assistant describes the object first and then tells a short story.

### Settings
Parent-facing controls for voice/default mode plus transcript history grouped by mode.

## Local development

### Frontend

```bash
cd web
npm install
npm run dev
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8010
```

## Notes

- The frontend expects API and websocket base URLs via env when needed for local or remote testing.
- Local machine-specific files such as `.env.local`, `.env`, virtualenvs, and build artifacts are intentionally not committed.
