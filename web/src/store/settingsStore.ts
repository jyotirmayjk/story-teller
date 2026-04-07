import { create } from 'zustand';
import { createJSONStorage, persist } from 'zustand/middleware';
import type { AllowedCategory, Mode, VoiceStyle } from '../types/live';

interface SettingsState {
  voiceStyle: VoiceStyle;
  defaultMode: Mode;
  allowedCategories: AllowedCategory[];
  onboardingComplete: boolean;
  setSettings: (payload: Partial<Pick<SettingsState, 'voiceStyle' | 'defaultMode' | 'allowedCategories'>>) => void;
  markOnboardingComplete: () => void;
}

export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      voiceStyle: 'friendly_cartoon',
      defaultMode: 'conversation',
      allowedCategories: ['animals', 'vehicles', 'toys'],
      onboardingComplete: false,
      setSettings: (payload) => set((state) => ({ ...state, ...payload })),
      markOnboardingComplete: () => set({ onboardingComplete: true }),
    }),
    {
      name: 'whimsicalexplorer-settings',
      storage: createJSONStorage(() => localStorage),
    },
  ),
);
