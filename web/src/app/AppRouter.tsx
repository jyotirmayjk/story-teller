import type { ReactElement } from 'react';
import { Navigate, Route, Routes } from 'react-router-dom';
import { AppLayout } from './AppLayout';
import { WelcomeScreen } from '../screens/onboarding/WelcomeScreen';
import { VoiceStyleScreen } from '../screens/onboarding/VoiceStyleScreen';
import { CategorySelectionScreen } from '../screens/onboarding/CategorySelectionScreen';
import { DefaultModeScreen } from '../screens/onboarding/DefaultModeScreen';
import { ConversationScreen, StoryTellerScreen } from '../screens/live/ChildLiveScreen';
import { SettingsScreen } from '../screens/settings/SettingsScreen';
import { useSettingsStore } from '../store/settingsStore';

function ProtectedApp({ children }: { children: ReactElement }) {
  const onboardingComplete = useSettingsStore((state) => state.onboardingComplete);
  if (!onboardingComplete) {
    return <Navigate to="/onboarding/welcome" replace />;
  }
  return <AppLayout>{children}</AppLayout>;
}

export function AppRouter() {
  const onboardingComplete = useSettingsStore((state) => state.onboardingComplete);

  return (
    <Routes>
      <Route
        path="/"
        element={<Navigate to={onboardingComplete ? '/conversation' : '/onboarding/welcome'} replace />}
      />
      <Route path="/onboarding/welcome" element={<WelcomeScreen />} />
      <Route path="/onboarding/voice-style" element={<VoiceStyleScreen />} />
      <Route path="/onboarding/categories" element={<CategorySelectionScreen />} />
      <Route path="/onboarding/default-mode" element={<DefaultModeScreen />} />
      <Route
        path="/conversation"
        element={
          <ProtectedApp>
            <ConversationScreen />
          </ProtectedApp>
        }
      />
      <Route
        path="/story-teller"
        element={
          <ProtectedApp>
            <StoryTellerScreen />
          </ProtectedApp>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedApp>
            <SettingsScreen />
          </ProtectedApp>
        }
      />
    </Routes>
  );
}
