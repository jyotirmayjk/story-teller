import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button';
import { OnboardingFrame } from '../../components/common/OnboardingFrame';
import { useSettings } from '../../hooks/useSettings';
import { useSession } from '../../hooks/useSession';
import type { Mode } from '../../types/live';

const modes: { id: Mode; title: string; description: string }[] = [
  { id: 'conversation', title: 'Conversation', description: 'A calm companion that reflects one thing the child said and asks one grounded follow-up.' },
  { id: 'story_teller', title: 'Story Teller', description: 'Listens to the full question, identifies the object, and tells a short child-safe story.' },
];

export function DefaultModeScreen() {
  const navigate = useNavigate();
  const { defaultMode, saveSettings, markOnboardingComplete } = useSettings();
  const { bootstrapSession } = useSession();
  const [selected, setSelected] = useState<Mode>(defaultMode);
  const [saving, setSaving] = useState(false);

  return (
    <OnboardingFrame
      title="Choose the startup experience."
      subtitle="The child can still switch between Conversation and Story Teller later."
    >
      <div className="option-grid">
        {modes.map((mode) => (
          <button
            key={mode.id}
            type="button"
            className={`choice-card ${selected === mode.id ? 'choice-card--active choice-card--story' : ''}`}
            onClick={() => setSelected(mode.id)}
          >
            <h3>{mode.title}</h3>
            <p>{mode.description}</p>
          </button>
        ))}
      </div>
      <Button
        block
        disabled={saving}
        onClick={async () => {
          setSaving(true);
          const updated = await saveSettings({ defaultMode: selected });
          await bootstrapSession({
            defaultMode: updated.default_mode,
            voiceStyle: updated.voice_style,
          });
          markOnboardingComplete();
          navigate('/conversation');
        }}
      >
        {saving ? 'Finishing...' : 'Finish Setup'}
      </Button>
    </OnboardingFrame>
  );
}
