import { apiClient, ApiError } from './client';
import type {
  ActivityRecord,
  ChildSettings,
  DiscoveryRecord,
  EndSessionResponse,
  LoginResponse,
  PatchSessionRequest,
  PatchSettingsRequest,
  ReplayResponse,
  SessionRecord,
  StartSessionRequest,
} from './types';

export const login = (name: string) =>
  apiClient.post<LoginResponse>('/auth/login', { name });

export const getSettings = (token: string) =>
  apiClient.get<ChildSettings>('/app/settings/', token);

export const updateSettings = (token: string, payload: PatchSettingsRequest) =>
  apiClient.patch<ChildSettings>('/app/settings/', payload, token);

export const getCurrentSession = (token: string) =>
  apiClient.get<SessionRecord>('/app/session/current', token);

export const startSession = (token: string, payload: StartSessionRequest = {}) =>
  apiClient.post<SessionRecord>('/app/session/start', payload, token);

export const updateCurrentSession = (token: string, payload: PatchSessionRequest) =>
  apiClient.patch<SessionRecord>('/app/session/current', payload, token);

export const endSession = (token: string) =>
  apiClient.post<EndSessionResponse>('/app/session/end', {}, token);

export const getDiscoveries = (token: string) =>
  apiClient.get<DiscoveryRecord[]>('/app/discoveries/', token);

export const favoriteDiscovery = (token: string, discoveryId: string) =>
  apiClient.post<DiscoveryRecord>(`/app/discoveries/${discoveryId}/favorite`, {}, token);

export const replayDiscovery = (token: string, discoveryId: string) =>
  apiClient.post<ReplayResponse>(`/app/discoveries/${discoveryId}/replay`, {}, token);

export const getActivity = async (token: string): Promise<ActivityRecord[]> => {
  try {
    return await apiClient.get<ActivityRecord[]>('/app/activity/', token);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return [];
    }
    throw error;
  }
};
