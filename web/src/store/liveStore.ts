import { create } from 'zustand';
import type { DiscoveryRecord } from '../api/types';
import type { ConnectionState } from '../types/live';

interface RecentTurn {
  transcript: string;
  assistantReply: string;
}

const GENERIC_FALLBACK_REPLY = 'Hello. I am here with you.';

interface LiveState {
  connectionState: ConnectionState;
  transcriptPartial: string;
  transcriptFinal: string;
  assistantText: string;
  recentTurns: RecentTurn[];
  discoveries: DiscoveryRecord[];
  sentAudioChunks: number;
  sentAudioFlushes: number;
  lastAudioChunkBytes: number;
  lastSendOk: boolean | null;
  setConnectionState: (state: ConnectionState) => void;
  setTranscriptPartial: (text: string) => void;
  setTranscriptFinal: (text: string) => void;
  appendAssistantText: (text: string) => void;
  setAssistantText: (text: string) => void;
  archiveCompletedTurn: () => void;
  setDiscoveries: (items: DiscoveryRecord[]) => void;
  prependDiscovery: (item: DiscoveryRecord) => void;
  trackAudioChunkSent: (bytes: number, ok: boolean) => void;
  trackAudioFlushSent: (ok: boolean) => void;
  resetTurn: () => void;
}

export const useLiveStore = create<LiveState>((set) => ({
  connectionState: 'disconnected',
  transcriptPartial: '',
  transcriptFinal: '',
  assistantText: '',
  recentTurns: [],
  discoveries: [],
  sentAudioChunks: 0,
  sentAudioFlushes: 0,
  lastAudioChunkBytes: 0,
  lastSendOk: null,
  setConnectionState: (connectionState) => set({ connectionState }),
  setTranscriptPartial: (transcriptPartial) => set({ transcriptPartial }),
  setTranscriptFinal: (transcriptFinal) => set({ transcriptFinal, transcriptPartial: '' }),
  appendAssistantText: (text) =>
    set((state) => ({ assistantText: `${state.assistantText}${text}` })),
  setAssistantText: (assistantText) => set({ assistantText }),
  archiveCompletedTurn: () =>
    set((state) => {
      const transcript = state.transcriptFinal.trim();
      const assistantReply = state.assistantText.trim();
      if (!transcript || !assistantReply) {
        return state;
      }
      if (assistantReply === GENERIC_FALLBACK_REPLY) {
        return state;
      }

      return {
        recentTurns: [
          ...state.recentTurns,
          {
            transcript,
            assistantReply,
          },
        ].slice(-3),
      };
    }),
  setDiscoveries: (discoveries) => set({ discoveries }),
  prependDiscovery: (item) =>
    set((state) => ({
      discoveries: [item, ...state.discoveries.filter((existing) => existing.id !== item.id)],
    })),
  trackAudioChunkSent: (bytes, ok) =>
    set((state) => ({
      sentAudioChunks: state.sentAudioChunks + 1,
      lastAudioChunkBytes: bytes,
      lastSendOk: ok,
    })),
  trackAudioFlushSent: (ok) =>
    set((state) => ({
      sentAudioFlushes: state.sentAudioFlushes + 1,
      lastSendOk: ok,
    })),
  resetTurn: () =>
    set({
      transcriptPartial: '',
      transcriptFinal: '',
      assistantText: '',
      sentAudioChunks: 0,
      sentAudioFlushes: 0,
      lastAudioChunkBytes: 0,
      lastSendOk: null,
    }),
}));
