import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button';
import { OnboardingFrame } from '../../components/common/OnboardingFrame';
import { useSettings } from '../../hooks/useSettings';
import type { VoiceStyle } from '../../types/live';

const voices: { id: VoiceStyle; title: string; description: string }[] = [
  {
    id: 'friendly_cartoon',
    title: 'Friendly Cartoon',
    description: 'Bright, energetic, and easy for short back-and-forths.',
  },
  {
    id: 'story_narrator',
    title: 'Story Narrator',
    description: 'Warm, calm, and tuned for cozy explanatory replies.',
  },
];

export function VoiceStyleScreen() {
  const navigate = useNavigate();
  const { voiceStyle, saveSettings } = useSettings();
  const [selected, setSelected] = useState<VoiceStyle>(voiceStyle);
  const [saving, setSaving] = useState(false);

  return (
    <OnboardingFrame
      title="Choose a voice style."
      subtitle="This becomes the saved personality default, while live runtime changes stay session-specific on Home."
    >
      <div className="option-grid">
        {voices.map((voice) => (
          <button
            key={voice.id}
            type="button"
            className={`choice-card ${selected === voice.id ? 'choice-card--active' : ''}`}
            onClick={() => setSelected(voice.id)}
          >
            <h3>{voice.title}</h3>
            <p>{voice.description}</p>
          </button>
        ))}
      </div>
      <Button
        block
        disabled={saving}
        onClick={async () => {
          setSaving(true);
          await saveSettings({ voiceStyle: selected });
          navigate('/onboarding/categories');
        }}
      >
        {saving ? 'Saving...' : 'Continue'}
      </Button>
    </OnboardingFrame>
  );
}
