export type AllowedCategory =
  | 'animals'
  | 'vehicles'
  | 'toys'
  | 'household_objects';

export type VoiceStyle = 'friendly_cartoon' | 'story_narrator';
export type Mode = 'conversation' | 'story_teller';

export type RuntimeStatus =
  | 'idle'
  | 'connecting'
  | 'active'
  | 'listening'
  | 'processing'
  | 'speaking'
  | 'ended'
  | 'error';

export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error';
