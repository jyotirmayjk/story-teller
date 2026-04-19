import { useCallback } from 'react';
import { getSettings, updateSettings } from '../api/endpoints';
import { useAuth } from './useAuth';
import { useSettingsStore } from '../store/settingsStore';
import type { AllowedCategory, Mode, VoiceStyle } from '../types/live';

export function useSettings() {
  const { ensureLogin } = useAuth();
  const voiceStyle = useSettingsStore((state) => state.voiceStyle);
  const defaultMode = useSettingsStore((state) => state.defaultMode);
  const allowedCategories = useSettingsStore((state) => state.allowedCategories);
  const onboardingComplete = useSettingsStore((state) => state.onboardingComplete);
  const setSettings = useSettingsStore((state) => state.setSettings);
  const markOnboardingComplete = useSettingsStore((state) => state.markOnboardingComplete);

  const refreshSettings = useCallback(async () => {
    const token = await ensureLogin();
    const settings = await getSettings(token);
    setSettings({
      voiceStyle: settings.voice_style,
      defaultMode: settings.default_mode,
      allowedCategories: settings.allowed_categories,
    });
    return settings;
  }, [ensureLogin, setSettings]);

  const saveSettings = useCallback(async (payload: {
    voiceStyle?: VoiceStyle;
    defaultMode?: Mode;
    allowedCategories?: AllowedCategory[];
  }) => {
    const token = await ensureLogin();
    const updated = await updateSettings(token, {
      voice_style: payload.voiceStyle,
      default_mode: payload.defaultMode,
      allowed_categories: payload.allowedCategories,
    });
    setSettings({
      voiceStyle: updated.voice_style,
      defaultMode: updated.default_mode,
      allowedCategories: updated.allowed_categories,
    });
    return updated;
  }, [ensureLogin, setSettings]);

  return {
    voiceStyle,
    defaultMode,
    allowedCategories,
    onboardingComplete,
    markOnboardingComplete,
    refreshSettings,
    saveSettings,
  };
}
