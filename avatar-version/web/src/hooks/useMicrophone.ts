import { useCallback, useEffect, useRef, useState } from 'react';

const TARGET_SAMPLE_RATE = 16000;

function floatTo16BitPCM(float32Array: Float32Array) {
  const pcm = new Int16Array(float32Array.length);
  for (let i = 0; i < float32Array.length; i += 1) {
    const sample = Math.max(-1, Math.min(1, float32Array[i]));
    pcm[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
  }
  return new Uint8Array(pcm.buffer);
}

function downsampleBuffer(buffer: Float32Array, inputSampleRate: number) {
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
    result[offsetResult] = accum / count;
    offsetResult += 1;
    offsetBuffer = nextOffsetBuffer;
  }
  return result;
}

function bytesToBase64(bytes: Uint8Array) {
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

export function useMicrophone() {
  const [error, setError] = useState<string | null>(null);
  const [recording, setRecording] = useState(false);
  const streamRef = useRef<MediaStream | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);

  const start = useCallback(async (onChunk: (audio: string) => void) => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const audioContext = new AudioContext();
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);

      processor.onaudioprocess = (event) => {
        const input = event.inputBuffer.getChannelData(0);
        const downsampled = downsampleBuffer(input, audioContext.sampleRate);
        const pcm = floatTo16BitPCM(downsampled);
        onChunk(bytesToBase64(pcm));
      };

      source.connect(processor);
      processor.connect(audioContext.destination);

      streamRef.current = stream;
      audioContextRef.current = audioContext;
      processorRef.current = processor;
      sourceRef.current = source;
      setRecording(true);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to access microphone');
    }
  }, []);

  const stop = useCallback(async () => {
    processorRef.current?.disconnect();
    sourceRef.current?.disconnect();
    streamRef.current?.getTracks().forEach((track) => track.stop());
    await audioContextRef.current?.close();
    processorRef.current = null;
    sourceRef.current = null;
    streamRef.current = null;
    audioContextRef.current = null;
    setRecording(false);
  }, []);

  useEffect(() => {
    return () => {
      void stop();
    };
  }, [stop]);

  return {
    start,
    stop,
    recording,
    error,
    sampleRate: TARGET_SAMPLE_RATE,
  };
}
