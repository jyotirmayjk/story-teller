import type { AllowedCategory, ConnectionState, Mode, RuntimeStatus, VoiceStyle } from '../types/live';

export interface LoginRequest {
  name: string;
}

export interface LoginResponse {
  access_token: string;
}

export interface ChildSettings {
  voice_style: VoiceStyle;
  default_mode: Mode;
  allowed_categories: AllowedCategory[];
}

export interface PatchSettingsRequest {
  voice_style?: VoiceStyle;
  default_mode?: Mode;
  allowed_categories?: AllowedCategory[];
}

export interface SessionRecord {
  id: number;
  household_id: number;
  device_id: number | null;
  active_mode: Mode;
  voice_style: VoiceStyle;
  status: string;
  current_object_name: string | null;
  current_object_category: AllowedCategory | null;
  started_at: string | null;
  last_activity_at: string | null;
}

export interface StartSessionRequest {
  active_mode?: Mode;
  voice_style?: VoiceStyle;
  current_object_name?: string | null;
  current_object_category?: AllowedCategory | null;
}

export interface PatchSessionRequest extends StartSessionRequest {
  status?: string;
}

export interface EndSessionResponse {
  ok: boolean;
  session_id: number | null;
}

export interface DiscoveryRecord {
  id: string;
  title: string;
  object_name: string | null;
  object_category: AllowedCategory | null;
  mode: Mode;
  summary: string;
  transcript: string | null;
  reply_text: string | null;
  detected_object_name?: string | null;
  is_favorite: boolean;
  created_at: string;
}

export interface ReplayResponse {
  ok: boolean;
  discovery_id: string;
}

export interface ActivityRecord {
  id: string | number;
  event_type: string;
  metadata_json?: Record<string, unknown> | null;
  created_at: string;
}

export interface ImageRecognizeRequest {
  image_base64: string;
  mime_type: string;
}

export interface ImageRecognizeResponse {
  object_name: string | null;
  object_category: AllowedCategory | null;
  description: string | null;
}

export interface RuntimeSessionState {
  sessionId: number | null;
  activeMode: Mode;
  voiceStyle: VoiceStyle;
  currentObjectName: string;
  currentObjectCategory: AllowedCategory | null;
  status: RuntimeStatus;
  transcriptPartial: string;
  transcriptFinal: string;
  assistantText: string;
  connectionState: ConnectionState;
}
