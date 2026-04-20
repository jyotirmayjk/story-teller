# Avatar Chrome Extension Plan

## Goal

Build a lightweight Chrome extension inside `avatar-version` that shows only the duck avatar overlay on webpages. Clicking the avatar records the microphone, sends audio to the avatar-version backend, and displays transcript and assistant response text in a hovering bubble.

## Scope

The extension should not use the React app shell, onboarding, settings screen, bottom navigation, or route system.

The first version should:

- inject the duck avatar into normal webpages
- use the sprite sheet as an animated canvas avatar
- click avatar once to start recording
- click avatar again to stop recording and flush audio
- send audio to the existing backend websocket as `pcm_s16le`
- show detected STT transcript in a hovering text bubble
- show the assistant response in the same text bubble
- play returned TTS audio
- default to `conversation` mode

## Runtime Ports

For avatar-version local development:

- frontend app: `5174`
- backend: `8020`
- extension backend API: `http://127.0.0.1:8020/api/v1`
- extension backend websocket: `ws://127.0.0.1:8020/api/v1`

## Architecture

```text
Chrome content script
  -> inject floating avatar canvas + text bubble
  -> login to backend with default household name
  -> start session in conversation mode
  -> connect live websocket
  -> capture mic as PCM16 16kHz
  -> send audio.chunk messages
  -> send audio.flush on second click
  -> render transcript.final in text bubble
  -> render llm.completed in text bubble
  -> play tts.chunk audio
```

## Audio Format Strategy

Do not use `MediaRecorder` for the MVP because browser `MediaRecorder` usually emits `webm/opus`, while the backend already expects:

```json
{
  "type": "audio.chunk",
  "data": {
    "audio": "<base64 pcm16>",
    "sample_rate": 16000,
    "encoding": "pcm_s16le"
  }
}
```

The extension will reuse the existing web app strategy:

- `getUserMedia({ audio: true })`
- `AudioContext`
- `ScriptProcessorNode`
- downsample to `16000`
- convert `Float32Array` samples to signed 16-bit little-endian PCM
- base64 encode bytes
- send websocket chunks

This keeps the backend and Sarvam STT flow unchanged.

For TTS playback, the extension should mirror the React web app:

- collect each `tts.chunk` as decoded bytes
- wait for `tts.completed`
- create one `Blob` with the final codec
- play the object URL with `new Audio(url)`

This avoids trying to play partial MP3 chunks as standalone audio files.

## Onboarding Strategy

The extension should bypass onboarding entirely.

On startup it should:

1. `POST /auth/login` with a default household name like `Browser Avatar`.
2. Store the returned temp token in memory.
3. `POST /app/session/start` with:
   - `active_mode: "conversation"`
   - `voice_style: "friendly_cartoon"`
4. Connect to:
   - `/app/live/ws?token=<token>`
5. Send a `session.update` websocket event for conversation mode.

## Extension Files

```text
extension/
  manifest.json
  src/
    content.js
    avatar.css
  assets/
    duck-avatar-sprite.png
```

## Sprite Mapping

The sprite sheet is `1024 x 1024` with a `4 x 4` grid.

Frame size:

```text
256 x 256
```

State mapping:

```text
idle:       frames 0-3
listening:  frames 4-7
processing: frames 8-11
speaking:   frames 12-15
```

## Text Bubble Behavior

The floating text bubble should show:

- initial: `Tap the duck to talk`
- recording: `Listening...`
- after transcript final: detected transcript
- while LLM response arrives: response text
- during speaking: final assistant response
- on error: short error message

## Reset Audio Control

Add a small secondary `Reset audio` button near the mode toggle.

It should:

- stop any currently playing TTS audio
- clear queued TTS chunks
- stop any active microphone stream
- close the active `AudioContext`
- clear the in-progress assistant response buffer
- return the avatar to `idle`

It should not:

- delete the backend session
- clear the selected mode
- hide the duck
- reload the page

## Mode Toggle Plan

The extension should support both assistant modes without adding onboarding or the full React app UI.

### UI

Add a compact segmented control near the duck:

- `Talk`
- `Story`

The control should stay visually secondary to the duck. The duck remains the primary interaction target for recording audio.

### Behavior

- `Talk` maps to backend mode `conversation`.
- `Story` maps to backend mode `story_teller`.
- The selected mode should persist with `chrome.storage.local`.
- The initial default remains `conversation`.
- Changing mode while idle should immediately send a websocket `session.update` event if the socket is already connected.
- Changing mode while recording should be ignored until the current recording finishes, to avoid sending one utterance to two modes.
- The text bubble should update by mode:
  - `conversation`: `Tap the duck to talk`
  - `story_teller`: `Tap the duck and ask for a story`

### Backend Integration

Use the same backend routes and websocket transport:

- `POST /auth/login`
- `POST /app/session/start`
- `GET /app/live/ws?token=<token>`
- websocket `session.update`

When starting a session, use the current extension mode:

```json
{
  "active_mode": "conversation",
  "voice_style": "friendly_cartoon"
}
```

or:

```json
{
  "active_mode": "story_teller",
  "voice_style": "friendly_cartoon"
}
```

No onboarding screen is needed because the extension still creates a temporary local backend session as `Browser Avatar`.

## Known Risks

- Some pages may restrict extension behavior, but content scripts are more reliable than bookmarklets.
- Content-script microphone capture may fail on some pages. If that happens, move the same audio logic into an offscreen document in a future version.
- Localhost backend access requires the avatar-version backend to be running on `8020`.

## Definition Of Done

- Extension loads as an unpacked Chrome extension.
- Duck avatar appears on normal webpages.
- Click starts recording.
- Second click stops recording.
- Text bubble shows transcript and assistant reply.
- TTS audio plays.
- Sprite changes state for idle, listening, processing, and speaking.
