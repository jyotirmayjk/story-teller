import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../../components/common/Button';
import { OnboardingFrame } from '../../components/common/OnboardingFrame';
import { useSettings } from '../../hooks/useSettings';
import type { AllowedCategory } from '../../types/live';

const categories: { id: AllowedCategory; title: string }[] = [
  { id: 'animals', title: 'Animals' },
  { id: 'vehicles', title: 'Vehicles' },
  { id: 'toys', title: 'Toys' },
  { id: 'household_objects', title: 'Household Objects' },
];

export function CategorySelectionScreen() {
  const navigate = useNavigate();
  const { allowedCategories, saveSettings } = useSettings();
  const [selected, setSelected] = useState<AllowedCategory[]>(allowedCategories);
  const [saving, setSaving] = useState(false);

  const toggle = (category: AllowedCategory) => {
    setSelected((current) =>
      current.includes(category)
        ? current.filter((item) => item !== category)
        : [...current, category],
    );
  };

  return (
    <OnboardingFrame
      title="Set safe exploration categories."
      subtitle="These are persistent household settings, not just one-session choices."
    >
      <div className="option-grid">
        {categories.map((category) => (
          <button
            key={category.id}
            type="button"
            className={`choice-card ${selected.includes(category.id) ? 'choice-card--active choice-card--learn' : ''}`}
            onClick={() => toggle(category.id)}
          >
            <h3>{category.title}</h3>
          </button>
        ))}
      </div>
      <Button
        block
        disabled={!selected.length || saving}
        onClick={async () => {
          setSaving(true);
          await saveSettings({ allowedCategories: selected });
          navigate('/onboarding/default-mode');
        }}
      >
        {saving ? 'Saving...' : 'Continue'}
      </Button>
    </OnboardingFrame>
  );
}
