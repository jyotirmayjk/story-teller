import { useEffect, useRef } from 'react';
import { LiveSocketClient } from '../api/liveSocket';
import type { LiveServerMessage } from '../api/liveSocket';
import { useAuthStore } from '../store/authStore';
import { useLiveStore } from '../store/liveStore';
import { useSessionStore } from '../store/sessionStore';
import { useAudioPlayback } from './useAudioPlayback';

export function useLiveSocket(enabled = true) {
  const token = useAuthStore((state) => state.token);
  const setConnectionState = useLiveStore((state) => state.setConnectionState);
  const setTranscriptPartial = useLiveStore((state) => state.setTranscriptPartial);
  const setTranscriptFinal = useLiveStore((state) => state.setTranscriptFinal);
  const appendAssistantText = useLiveStore((state) => state.appendAssistantText);
  const setAssistantText = useLiveStore((state) => state.setAssistantText);
  const archiveCompletedTurn = useLiveStore((state) => state.archiveCompletedTurn);
  const prependDiscovery = useLiveStore((state) => state.prependDiscovery);
  const resetTurn = useLiveStore((state) => state.resetTurn);
  const setSessionFromRecord = useSessionStore((state) => state.setSessionFromRecord);
  const updateRuntime = useSessionStore((state) => state.updateRuntime);
  const { enqueueChunk, flush } = useAudioPlayback();
  const handlersRef = useRef({
    setConnectionState,
    setTranscriptPartial,
    setTranscriptFinal,
    appendAssistantText,
    setAssistantText,
    archiveCompletedTurn,
    prependDiscovery,
    setSessionFromRecord,
    updateRuntime,
    enqueueChunk,
    flush,
  });
  const socketRef = useRef<LiveSocketClient | null>(null);

  handlersRef.current = {
    setConnectionState,
    setTranscriptPartial,
    setTranscriptFinal,
    appendAssistantText,
    setAssistantText,
    archiveCompletedTurn,
    prependDiscovery,
    setSessionFromRecord,
    updateRuntime,
    enqueueChunk,
    flush,
  };

  useEffect(() => {
    if (!enabled || !token) {
      socketRef.current?.disconnect();
      socketRef.current = null;
      return;
    }

    const handleMessage = async (message: LiveServerMessage) => {
      const handlers = handlersRef.current;

      switch (message.type) {
        case 'session.started':
        case 'session.updated':
          handlers.setSessionFromRecord(message.data);
          break;
        case 'transcript.partial':
          handlers.updateRuntime({ status: 'listening' });
          handlers.setTranscriptPartial(message.data.text);
          break;
        case 'transcript.final':
          handlers.updateRuntime({ status: 'processing' });
          handlers.setTranscriptFinal(message.data.text);
          break;
        case 'llm.delta':
          handlers.updateRuntime({ status: 'processing' });
          handlers.appendAssistantText(message.data.text);
          break;
        case 'llm.completed':
          handlers.setAssistantText(message.data.text);
          handlers.updateRuntime({ status: 'speaking' });
          break;
        case 'tts.chunk':
          handlers.enqueueChunk(message.data.audio);
          break;
        case 'tts.completed':
          await handlers.flush(message.data.codec || 'mp3');
          handlers.archiveCompletedTurn();
          handlers.updateRuntime({ status: 'active' });
          break;
        case 'discovery.created':
          handlers.prependDiscovery(message.data);
          break;
        case 'error':
          handlers.updateRuntime({ status: 'error' });
          break;
        case 'pong':
          break;
      }
    };

    const socket = new LiveSocketClient({
      token,
      onStateChange: (state) => handlersRef.current.setConnectionState(state),
      onMessage: handleMessage,
    });
    socketRef.current = socket;
    socket.connect();
    resetTurn();

    return () => {
      socket.disconnect();
      if (socketRef.current === socket) {
        socketRef.current = null;
      }
    };
  }, [enabled, resetTurn, token]);

  return socketRef.current;
}
