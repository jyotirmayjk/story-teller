import { useCallback, useRef } from 'react';

function decodeBase64(base64: string) {
  const raw = atob(base64);
  const bytes = new Uint8Array(raw.length);
  for (let index = 0; index < raw.length; index += 1) {
    bytes[index] = raw.charCodeAt(index);
  }
  return bytes;
}

export function useAudioPlayback() {
  const chunksRef = useRef<Uint8Array[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const currentUrlRef = useRef<string | null>(null);

  const enqueueChunk = useCallback((base64: string) => {
    chunksRef.current.push(decodeBase64(base64));
  }, []);

  const flush = useCallback(async (codec = 'mp3') => {
    if (!chunksRef.current.length) {
      return;
    }
    const parts = chunksRef.current.map((chunk) => {
      const copy = new Uint8Array(chunk.byteLength);
      copy.set(chunk);
      return copy;
    });
    const blob = new Blob(parts, { type: `audio/${codec}` });
    const url = URL.createObjectURL(blob);
    if (audioRef.current) {
      audioRef.current.pause();
    }
    if (currentUrlRef.current) {
      URL.revokeObjectURL(currentUrlRef.current);
    }
    const audio = new Audio(url);
    audioRef.current = audio;
    currentUrlRef.current = url;
    chunksRef.current = [];
    await new Promise<void>((resolve, reject) => {
      const cleanup = () => {
        audio.removeEventListener('ended', handleEnded);
        audio.removeEventListener('error', handleError);
      };

      const handleEnded = () => {
        cleanup();
        resolve();
      };

      const handleError = () => {
        cleanup();
        reject(new Error('Audio playback failed'));
      };

      audio.addEventListener('ended', handleEnded, { once: true });
      audio.addEventListener('error', handleError, { once: true });

      void audio.play().catch((error) => {
        cleanup();
        reject(error instanceof Error ? error : new Error('Audio playback failed'));
      });
    });
  }, []);

  return {
    enqueueChunk,
    flush,
  };
}
