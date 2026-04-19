import { wsBaseUrl } from './client';
import type { DiscoveryRecord, SessionRecord } from './types';
import type { AllowedCategory, Mode, VoiceStyle } from '../types/live';

export type LiveClientMessage =
  | {
      type: 'session.update';
      data: {
        active_mode?: Mode;
        voice_style?: VoiceStyle;
        current_object_name?: string | null;
        current_object_category?: AllowedCategory | null;
      };
    }
  | {
      type: 'audio.chunk';
      data: {
        audio: string;
        sample_rate: number;
        encoding: 'pcm_s16le';
      };
    }
  | { type: 'audio.flush' }
  | { type: 'ping' };

export type LiveServerMessage =
  | { type: 'session.started'; data: SessionRecord }
  | { type: 'session.updated'; data: SessionRecord }
  | { type: 'transcript.partial'; data: { text: string; language_code?: string | null } }
  | { type: 'transcript.final'; data: { text: string; language_code?: string | null } }
  | { type: 'llm.delta'; data: { text: string } }
  | { type: 'llm.completed'; data: { text: string } }
  | { type: 'tts.chunk'; data: { audio: string; codec?: string; kind?: string } }
  | { type: 'tts.completed'; data: { codec?: string } }
  | { type: 'discovery.created'; data: DiscoveryRecord }
  | { type: 'pong'; data: Record<string, never> }
  | { type: 'error'; data: { message: string } };

export class LiveSocketClient {
  private socket: WebSocket | null = null;
  private readonly token: string;
  private readonly onMessage: (message: LiveServerMessage) => void;
  private readonly onStateChange: (state: 'connecting' | 'connected' | 'disconnected' | 'error') => void;

  constructor(args: {
    token: string;
    onMessage: (message: LiveServerMessage) => void;
    onStateChange: (state: 'connecting' | 'connected' | 'disconnected' | 'error') => void;
  }) {
    this.token = args.token;
    this.onMessage = args.onMessage;
    this.onStateChange = args.onStateChange;
  }

  connect() {
    if (this.socket && this.socket.readyState <= WebSocket.OPEN) {
      return;
    }

    this.onStateChange('connecting');
    const socket = new WebSocket(`${wsBaseUrl}/app/live/ws?token=${encodeURIComponent(this.token)}`);
    this.socket = socket;

    socket.addEventListener('open', () => {
      this.onStateChange('connected');
    });

    socket.addEventListener('message', (event) => {
      try {
        const parsed = JSON.parse(event.data) as LiveServerMessage;
        this.onMessage(parsed);
      } catch {
        this.onStateChange('error');
      }
    });

    socket.addEventListener('close', () => {
      this.onStateChange('disconnected');
    });

    socket.addEventListener('error', () => {
      this.onStateChange('error');
    });
  }

  send(message: LiveClientMessage) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      return false;
    }
    this.socket.send(JSON.stringify(message));
    return true;
  }

  disconnect() {
    this.socket?.close();
    this.socket = null;
  }
}
