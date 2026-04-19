(() => {
  if (window.__storyCompanionDuckLoaded) {
    return;
  }
  window.__storyCompanionDuckLoaded = true;

  const API_BASE = 'http://127.0.0.1:8020/api/v1';
  const WS_BASE = 'ws://127.0.0.1:8020/api/v1';
  const TARGET_SAMPLE_RATE = 16000;
  const FRAME_SIZE = 256;
  const COLUMNS = 4;
  const FPS = 6;
  const SPRITE_SRC = chrome.runtime.getURL('assets/duck-avatar-sprite.png');

  const animationFrames = {
    idle: [0, 1, 2, 3],
    listening: [4, 5, 6, 7],
    processing: [8, 9, 10, 11],
    speaking: [12, 13, 14, 15],
  };

  const state = {
    token: null,
    socket: null,
    status: 'idle',
    isRecording: false,
    responseBuffer: '',
    stream: null,
    audioContext: null,
    source: null,
    processor: null,
    audioQueue: [],
    audioPlaying: false,
  };

  const root = document.createElement('div');
  root.id = 'story-companion-duck-root';
  root.innerHTML = `
    <div id="story-companion-duck-bubble">Tap the duck to talk</div>
    <button id="story-companion-duck-button" type="button" aria-label="Tap the duck to talk" data-state="idle">
      <canvas id="story-companion-duck-canvas" width="128" height="128"></canvas>
    </button>
  `;
  document.documentElement.appendChild(root);

  const bubble = root.querySelector('#story-companion-duck-bubble');
  const button = root.querySelector('#story-companion-duck-button');
  const canvas = root.querySelector('#story-companion-duck-canvas');
  const ctx = canvas.getContext('2d');
  const sprite = new Image();
  sprite.src = SPRITE_SRC;

  function setBubble(text) {
    bubble.textContent = text || 'Tap the duck to talk';
  }

  function setStatus(nextStatus) {
    state.status = nextStatus;
    button.dataset.state = nextStatus;
    button.setAttribute('aria-label', `Duck avatar ${nextStatus}`);
  }

  function bytesToBase64(bytes) {
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i += 1) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }

  function floatTo16BitPCM(float32Array) {
    const pcm = new Int16Array(float32Array.length);
    for (let i = 0; i < float32Array.length; i += 1) {
      const sample = Math.max(-1, Math.min(1, float32Array[i]));
      pcm[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
    }
    return new Uint8Array(pcm.buffer);
  }

  function downsampleBuffer(buffer, inputSampleRate) {
    if (inputSampleRate === TARGET_SAMPLE_RATE) {
      return buffer;
    }
    const sampleRateRatio = inputSampleRate / TARGET_SAMPLE_RATE;
    const newLength = Math.round(buffer.length / sampleRateRatio);
    const result = new Float32Array(newLength);
    let offsetResult = 0;
    let offsetBuffer = 0;

    while (offsetResult < result.length) {
      const nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
      let accum = 0;
      let count = 0;
      for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i += 1) {
        accum += buffer[i];
        count += 1;
      }
      result[offsetResult] = count > 0 ? accum / count : 0;
      offsetResult += 1;
      offsetBuffer = nextOffsetBuffer;
    }

    return result;
  }

  async function login() {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'Browser Avatar' }),
    });
    if (!response.ok) {
      throw new Error(`Login failed with ${response.status}`);
    }
    const payload = await response.json();
    state.token = payload.data?.access_token || payload.access_token;
    if (!state.token) {
      throw new Error('Login did not return a token');
    }
  }

  async function startSession() {
    const response = await fetch(`${API_BASE}/app/session/start`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${state.token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        active_mode: 'conversation',
        voice_style: 'friendly_cartoon',
      }),
    });
    if (!response.ok) {
      throw new Error(`Session start failed with ${response.status}`);
    }
  }

  function connectSocket() {
    return new Promise((resolve, reject) => {
      const socket = new WebSocket(`${WS_BASE}/app/live/ws?token=${encodeURIComponent(state.token)}`);
      state.socket = socket;

      socket.addEventListener('open', () => {
        socket.send(JSON.stringify({
          type: 'session.update',
          data: {
            active_mode: 'conversation',
            voice_style: 'friendly_cartoon',
          },
        }));
        resolve();
      });

      socket.addEventListener('message', (event) => {
        handleSocketMessage(event.data);
      });

      socket.addEventListener('close', () => {
        state.socket = null;
        if (!state.isRecording && state.status !== 'speaking') {
          setStatus('idle');
        }
      });

      socket.addEventListener('error', () => {
        reject(new Error('WebSocket connection failed'));
      });
    });
  }

  async function ensureBackendReady() {
    if (state.socket?.readyState === WebSocket.OPEN) {
      return;
    }
    setBubble('Connecting...');
    await login();
    await startSession();
    await connectSocket();
    setBubble('Tap the duck to talk');
  }

  function sendAudioChunk(audio) {
    if (state.socket?.readyState !== WebSocket.OPEN) {
      return;
    }
    state.socket.send(JSON.stringify({
      type: 'audio.chunk',
      data: {
        audio,
        sample_rate: TARGET_SAMPLE_RATE,
        encoding: 'pcm_s16le',
      },
    }));
  }

  async function startRecording() {
    if (state.isRecording || state.status === 'speaking' || state.status === 'processing') {
      return;
    }

    try {
      await ensureBackendReady();
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);

      processor.onaudioprocess = (event) => {
        const input = event.inputBuffer.getChannelData(0);
        const downsampled = downsampleBuffer(input, audioContext.sampleRate);
        const pcm = floatTo16BitPCM(downsampled);
        sendAudioChunk(bytesToBase64(pcm));
      };

      source.connect(processor);
      processor.connect(audioContext.destination);

      state.stream = stream;
      state.audioContext = audioContext;
      state.source = source;
      state.processor = processor;
      state.responseBuffer = '';
      state.isRecording = true;
      setStatus('listening');
      setBubble('Listening...');
    } catch (error) {
      setStatus('idle');
      setBubble(error instanceof Error ? error.message : 'Could not start recording');
    }
  }

  async function stopRecording() {
    if (!state.isRecording) {
      return;
    }

    state.processor?.disconnect();
    state.source?.disconnect();
    state.stream?.getTracks().forEach((track) => track.stop());
    await state.audioContext?.close();

    state.stream = null;
    state.audioContext = null;
    state.source = null;
    state.processor = null;
    state.isRecording = false;

    setStatus('processing');
    setBubble('Thinking...');
    state.socket?.send(JSON.stringify({ type: 'audio.flush' }));
  }

  function handleSocketMessage(rawMessage) {
    let message;
    try {
      message = JSON.parse(rawMessage);
    } catch {
      return;
    }

    const data = message.data || {};

    if (message.type === 'transcript.partial' && data.text) {
      setBubble(data.text);
      return;
    }

    if (message.type === 'transcript.final') {
      setBubble(data.text || 'I heard you.');
      state.responseBuffer = '';
      return;
    }

    if (message.type === 'llm.delta' && data.text) {
      state.responseBuffer += data.text;
      setBubble(state.responseBuffer);
      return;
    }

    if (message.type === 'llm.completed') {
      state.responseBuffer = data.text || state.responseBuffer;
      setBubble(state.responseBuffer);
      return;
    }

    if (message.type === 'tts.chunk' && data.audio) {
      setStatus('speaking');
      queueAudio(data.audio, data.codec || 'mp3');
      return;
    }

    if (message.type === 'tts.completed') {
      if (!state.audioPlaying) {
        setStatus('idle');
      }
      return;
    }

    if (message.type === 'error') {
      setStatus('idle');
      setBubble(data.message || 'Something went wrong.');
    }
  }

  function queueAudio(audioBase64, codec) {
    state.audioQueue.push({ audioBase64, codec });
    if (!state.audioPlaying) {
      void playNextAudio();
    }
  }

  async function playNextAudio() {
    const item = state.audioQueue.shift();
    if (!item) {
      state.audioPlaying = false;
      setStatus('idle');
      return;
    }

    state.audioPlaying = true;
    const audio = new Audio(`data:audio/${item.codec};base64,${item.audioBase64}`);
    audio.addEventListener('ended', () => {
      void playNextAudio();
    }, { once: true });
    audio.addEventListener('error', () => {
      void playNextAudio();
    }, { once: true });

    try {
      await audio.play();
    } catch {
      state.audioPlaying = false;
      setStatus('idle');
    }
  }

  button.addEventListener('click', () => {
    if (state.isRecording) {
      void stopRecording();
    } else {
      void startRecording();
    }
  });

  let animationIndex = 0;
  let lastFrameTime = 0;

  function drawAvatar(time) {
    if (sprite.complete && ctx) {
      const sequence = animationFrames[state.status] || animationFrames.idle;
      if (time - lastFrameTime > 1000 / FPS) {
        animationIndex = (animationIndex + 1) % sequence.length;
        lastFrameTime = time;
      }

      const frame = sequence[animationIndex];
      const sx = (frame % COLUMNS) * FRAME_SIZE;
      const sy = Math.floor(frame / COLUMNS) * FRAME_SIZE;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(sprite, sx, sy, FRAME_SIZE, FRAME_SIZE, 0, 0, canvas.width, canvas.height);
    }
    requestAnimationFrame(drawAvatar);
  }

  requestAnimationFrame(drawAvatar);
})();
