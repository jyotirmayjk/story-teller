import { create } from 'zustand';
import type { AllowedCategory, Mode, RuntimeStatus, VoiceStyle } from '../types/live';
import type { SessionRecord } from '../api/types';

interface SessionState {
  sessionId: number | null;
  activeMode: Mode;
  voiceStyle: VoiceStyle;
  currentObjectName: string;
  currentObjectCategory: AllowedCategory | null;
  status: RuntimeStatus;
  setSessionFromRecord: (session: SessionRecord) => void;
  updateRuntime: (payload: Partial<Pick<SessionState, 'activeMode' | 'voiceStyle' | 'currentObjectName' | 'currentObjectCategory' | 'status'>>) => void;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  activeMode: 'conversation',
  voiceStyle: 'friendly_cartoon',
  currentObjectName: '',
  currentObjectCategory: null,
  status: 'idle',
  setSessionFromRecord: (session) =>
    set({
      sessionId: session.id,
      activeMode: session.active_mode,
      voiceStyle: session.voice_style,
      currentObjectName: session.current_object_name ?? '',
      currentObjectCategory: session.current_object_category,
      status: normalizeStatus(session.status),
    }),
  updateRuntime: (payload) => set((state) => ({ ...state, ...payload })),
  clearSession: () =>
    set({
      sessionId: null,
      currentObjectName: '',
      currentObjectCategory: null,
      status: 'idle',
    }),
}));

function normalizeStatus(status: string): RuntimeStatus {
  if (
    status === 'connecting' ||
    status === 'active' ||
    status === 'listening' ||
    status === 'speaking' ||
    status === 'ended'
  ) {
    return status;
  }
  return 'active';
}
