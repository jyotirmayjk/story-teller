# Whimsical Explorer 2 Web

Browser client for the existing Whimsical Explorer 2 product model, built with React, TypeScript, and Vite. It preserves the mobile flow with onboarding for Welcome, Voice Style, Category Selection, and Default Mode, then the main Home, Discoveries, and Activity surfaces.

## What it connects to

- REST:
  - `POST /api/v1/auth/login`
  - `GET/PATCH /api/v1/app/settings/`
  - `GET/POST/PATCH /api/v1/app/session/*`
  - `GET /api/v1/app/discoveries/`
  - `GET /api/v1/app/activity/` when available
  - `POST /api/v1/app/live/image/recognize`
- WebSocket:
  - `WS /api/v1/app/live/ws?token=<bearer_token>`

The client targets the `whimsicalexplorer2_sarvam_streaming_backend.zip` contract. It uses Sarvam through the backend for STT, `sarvam-30b` for LLM, and Sarvam for TTS. OpenAI is only used by the backend for image recognition.

## Setup

1. Copy `.env.example` to `.env`.
2. Install dependencies:

```bash
npm install
```

3. Start the app:

```bash
npm run dev
```

4. Open [http://localhost:5173](http://localhost:5173).

## Notes

- Auth token and saved settings are persisted in `localStorage`.
- Runtime session state is separate from saved settings.
- Push-to-talk currently captures browser mic audio as 16 kHz PCM because the target streaming backend expects `pcm_s16le`.
- The Activity screen gracefully falls back to an empty state if the backend does not expose `/app/activity/`.

## File map

```text
web/
  src/
    app/
    api/
    components/
    hooks/
    screens/
    store/
    styles/
    types/
```

## Manual verification

See [MANUAL_TEST_PLAN.md](/Users/jk/Code/sarvamai/kids-pokedex-sarvam/web/MANUAL_TEST_PLAN.md).
