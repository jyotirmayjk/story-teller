import { useCallback } from 'react';
import { endSession, getCurrentSession, startSession, updateCurrentSession } from '../api/endpoints';
import { useAuth } from './useAuth';
import { useSessionStore } from '../store/sessionStore';
import type { AllowedCategory, Mode, VoiceStyle } from '../types/live';

export function useSession() {
  const { ensureLogin } = useAuth();
  const sessionId = useSessionStore((state) => state.sessionId);
  const activeMode = useSessionStore((state) => state.activeMode);
  const voiceStyle = useSessionStore((state) => state.voiceStyle);
  const currentObjectName = useSessionStore((state) => state.currentObjectName);
  const currentObjectCategory = useSessionStore((state) => state.currentObjectCategory);
  const status = useSessionStore((state) => state.status);
  const setSessionFromRecord = useSessionStore((state) => state.setSessionFromRecord);
  const updateRuntime = useSessionStore((state) => state.updateRuntime);
  const clearSession = useSessionStore((state) => state.clearSession);

  const bootstrapSession = useCallback(async (fallback: { defaultMode: Mode; voiceStyle: VoiceStyle }) => {
    const token = await ensureLogin();
    try {
      const current = await getCurrentSession(token);
      setSessionFromRecord(current);
      return current;
    } catch {
      const started = await startSession(token, {
        active_mode: fallback.defaultMode,
        voice_style: fallback.voiceStyle,
      });
      setSessionFromRecord(started);
      return started;
    }
  }, [ensureLogin, setSessionFromRecord]);

  const patchSession = useCallback(async (payload: {
    activeMode?: Mode;
    voiceStyle?: VoiceStyle;
    currentObjectName?: string | null;
    currentObjectCategory?: AllowedCategory | null;
    status?: string;
  }) => {
    const token = await ensureLogin();
    const updated = await updateCurrentSession(token, {
      active_mode: payload.activeMode,
      voice_style: payload.voiceStyle,
      current_object_name: payload.currentObjectName,
      current_object_category: payload.currentObjectCategory,
      status: payload.status,
    });
    setSessionFromRecord(updated);
    return updated;
  }, [ensureLogin, setSessionFromRecord]);

  const stopSession = useCallback(async () => {
    const token = await ensureLogin();
    await endSession(token);
    clearSession();
  }, [clearSession, ensureLogin]);

  return {
    sessionId,
    activeMode,
    voiceStyle,
    currentObjectName,
    currentObjectCategory,
    status,
    updateRuntime,
    bootstrapSession,
    patchSession,
    stopSession,
  };
}
