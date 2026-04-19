# Manual Test Plan

## Setup

1. Start the Sarvam backend on `http://localhost:8000`.
2. Start the web client with `npm run dev`.
3. Open the app in a Chromium-based browser and allow camera and microphone access.

## Onboarding

1. Open `/onboarding/welcome`.
2. Click `Get Started`.
3. Verify login succeeds and the app advances to Voice Style.
4. Select `Friendly Cartoon`, continue, and verify settings persist.
5. Select multiple allowed categories, continue, and verify settings persist.
6. Select a default mode, finish setup, and verify you land on `/home`.
7. Refresh the page and verify onboarding does not repeat.

## Home Runtime

1. Verify session bootstrap loads current settings and starts or resumes a session.
2. Change mode using the mode segmented control and verify the runtime session updates.
3. Change voice style and verify the runtime session updates without overwriting saved settings unless intended.
4. Type an object name and choose a category. Verify the session updates after clicking `Update Session`.
5. Start webcam preview. Verify live camera video renders.
6. Capture a frame. Verify image recognition runs and fills object name/category when the backend returns them.
7. Hold `Push to Talk`, speak, then release.
8. Verify:
   - connection state is `connected`
   - transcript partial updates appear while audio is being processed
   - transcript final appears after release
   - assistant text streams in progressively
   - audio playback begins after TTS chunks complete
   - a new discovery is inserted into the recent rail and discoveries list

## Discoveries

1. Open `/discoveries`.
2. Verify discoveries returned from REST render as cards.
3. Toggle favorite on a discovery and verify the card updates.
4. Trigger a new live discovery from Home and verify it appears without a full page refresh.

## Activity

1. Open `/activity`.
2. If the backend exposes activity, verify items are listed newest-first.
3. If the backend returns 404 or no data, verify the empty state explains that activity is not available yet.

## Resilience

1. Stop the backend while the app is open and verify the Home screen shows a disconnected/error state.
2. Restart the backend and reconnect from the Home screen.
3. Deny microphone permission and verify an inline error appears near push-to-talk.
4. Deny camera permission and verify an inline error appears near webcam controls.
