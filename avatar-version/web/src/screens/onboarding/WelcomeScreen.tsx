import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { Button } from '../../components/common/Button';
import { OnboardingFrame } from '../../components/common/OnboardingFrame';
import { useAuth } from '../../hooks/useAuth';

export function WelcomeScreen() {
  const navigate = useNavigate();
  const { ensureLogin, householdName, setHouseholdName } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  return (
    <OnboardingFrame
      title="Meet your gentle, browser-based explorer."
      subtitle="Keep the mobile product model, but bring camera, microphone, and live speech streaming into a desktop-friendly flow."
    >
      <label className="field">
        <span>Household name</span>
        <input
          value={householdName}
          onChange={(event) => setHouseholdName(event.target.value)}
          placeholder="Web Explorer Family"
        />
      </label>
      <Button
        block
        disabled={busy}
        onClick={async () => {
          setBusy(true);
          setError(null);
          try {
            await ensureLogin();
            navigate('/onboarding/voice-style');
          } catch (err) {
            setError(err instanceof Error ? err.message : 'Unable to start onboarding');
          } finally {
            setBusy(false);
          }
        }}
      >
        {busy ? 'Starting...' : 'Get Started'}
      </Button>
      {error ? <p className="inline-error">{error}</p> : null}
    </OnboardingFrame>
  );
}
