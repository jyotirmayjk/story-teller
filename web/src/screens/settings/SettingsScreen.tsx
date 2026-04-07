import { useEffect, useMemo, useState } from 'react';
import { favoriteDiscovery, getDiscoveries } from '../../api/endpoints';
import { EmptyState } from '../../components/common/EmptyState';
import { useAuth } from '../../hooks/useAuth';
import { useSettings } from '../../hooks/useSettings';
import { useLiveStore } from '../../store/liveStore';
import type { DiscoveryRecord } from '../../api/types';
import type { Mode } from '../../types/live';

const groupedModes: { key: Mode; title: string; emptyCopy: string; accentBar: string }[] = [
  {
    key: 'conversation',
    title: 'Conversation',
    emptyCopy: 'Conversation turns will appear here once the child starts talking.',
    accentBar: 'border-l-accent',
  },
  {
    key: 'story_teller',
    title: 'Story Teller',
    emptyCopy: 'Story Teller transcripts will appear here after completed story turns.',
    accentBar: 'border-l-ink',
  },
];

export function SettingsScreen() {
  const { ensureLogin } = useAuth();
  const discoveries = useLiveStore((state) => state.discoveries);
  const setDiscoveries = useLiveStore((state) => state.setDiscoveries);
  const { voiceStyle, defaultMode, saveSettings } = useSettings();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savingField, setSavingField] = useState<'voice' | 'mode' | null>(null);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const token = await ensureLogin();
        const items = await getDiscoveries(token);
        if (active) {
          setDiscoveries(items);
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : 'Unable to load transcript history');
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    })();

    return () => {
      active = false;
    };
  }, [ensureLogin, setDiscoveries]);

  const groupedDiscoveries = useMemo(
    () =>
      groupedModes.map((group) => ({
        ...group,
        items: discoveries.filter((item) => item.mode === group.key),
      })),
    [discoveries],
  );

  if (loading) {
    return (
      <div className="rounded-[2rem] border border-paper-line bg-white/70 p-8 shadow-card">
        <p className="text-sm font-semibold uppercase tracking-[0.22em] text-ink-muted">Loading settings...</p>
      </div>
    );
  }

  if (error) {
    return <EmptyState title="Could not load settings" description={error} />;
  }

  return (
    <div className="flex flex-col bg-paper">
      <header className="mb-10 pt-5 sm:mb-12 sm:pt-8">
        <span className="text-xs font-bold uppercase tracking-[0.28em] text-accent">Settings</span>
        <h1 className="mt-3 font-serif text-5xl leading-none text-ink sm:text-7xl">Parent Dashboard</h1>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-ink-soft sm:text-lg">
          Review transcripts and manage the voice experience without bringing technical controls into the child-facing screens.
        </p>
      </header>

      <div className="mb-14 grid gap-6">
        <PreferenceCard
          title="Assistant voice"
          label="Voice style"
          tone="green"
          helperText={
            savingField === 'voice' ? 'Saving…' : 'Choose the voice the child hears across both modes.'
          }
          options={[
            {
              label: 'Friendly Cartoon',
              selected: voiceStyle === 'friendly_cartoon',
              onClick: async () => {
                setSavingField('voice');
                try {
                  await saveSettings({ voiceStyle: 'friendly_cartoon' });
                } finally {
                  setSavingField(null);
                }
              },
            },
            {
              label: 'Story Narrator',
              selected: voiceStyle === 'story_narrator',
              onClick: async () => {
                setSavingField('voice');
                try {
                  await saveSettings({ voiceStyle: 'story_narrator' });
                } finally {
                  setSavingField(null);
                }
              },
            },
          ]}
        />

        <PreferenceCard
          title="Default screen"
          label="Default mode"
          tone="amber"
          helperText={
            savingField === 'mode'
              ? 'Saving…'
              : 'This defines which child-facing screen opens first for a new session.'
          }
          options={[
            {
              label: 'Conversation',
              selected: defaultMode === 'conversation',
              onClick: async () => {
                setSavingField('mode');
                try {
                  await saveSettings({ defaultMode: 'conversation' });
                } finally {
                  setSavingField(null);
                }
              },
            },
            {
              label: 'Story Teller',
              selected: defaultMode === 'story_teller',
              onClick: async () => {
                setSavingField('mode');
                try {
                  await saveSettings({ defaultMode: 'story_teller' });
                } finally {
                  setSavingField(null);
                }
              },
            },
          ]}
        />
      </div>

      <section>
        <div className="mb-8 flex items-end justify-between gap-4">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-ink-muted">Transcript history</p>
            <h2 className="mt-2 font-serif text-4xl text-ink sm:text-5xl">Saved voice moments</h2>
          </div>
        </div>

        <div className="space-y-10">
          {groupedDiscoveries.map((group) => (
            <section key={group.key}>
              <div className="mb-5 flex items-center gap-3">
                <div className="h-2 w-2 rounded-full bg-ink-soft/60" />
                <h3 className="text-xs font-bold uppercase tracking-[0.28em] text-ink-muted">{group.title}</h3>
              </div>

              {group.items.length ? (
                <div className="space-y-6">
                  {group.items.map((item) => (
                    <TranscriptCard
                      key={item.id}
                      item={item}
                      accentBar={group.accentBar}
                      onFavorite={async () => {
                        const token = await ensureLogin();
                        const updated = await favoriteDiscovery(token, item.id);
                        setDiscoveries(
                          discoveries.map((existing) => (existing.id === updated.id ? updated : existing)),
                        );
                      }}
                    />
                  ))}
                </div>
              ) : (
                <div className="rounded-[2rem] border border-paper-line bg-white/60 p-6 text-ink-soft shadow-card">
                  {group.emptyCopy}
                </div>
              )}
            </section>
          ))}
        </div>
      </section>
    </div>
  );
}

function PreferenceCard({
  title,
  label,
  helperText,
  options,
  tone,
}: {
  title: string;
  label: string;
  helperText: string;
  tone: 'green' | 'amber';
  options: { label: string; selected: boolean; onClick: () => Promise<void> }[];
}) {
  const toneClassName =
    tone === 'green'
      ? 'bg-emerald-100 text-emerald-800'
      : 'bg-orange-100 text-orange-700';

  return (
    <div className="rounded-[2rem] border border-paper-line bg-white/60 p-7 shadow-card sm:p-8">
      <div className="mb-6 flex items-center gap-4">
        <div className={`flex h-12 w-12 items-center justify-center rounded-full text-lg ${toneClassName}`}>
          {tone === 'green' ? '•' : '◦'}
        </div>
        <div>
          <h3 className="font-serif text-3xl text-ink">{title}</h3>
          <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-ink-muted">{label}</p>
        </div>
      </div>
      <div className="space-y-3">
        {options.map((option) => (
          <button
            key={option.label}
            type="button"
            onClick={() => void option.onClick()}
            className={[
              'flex w-full items-center justify-between rounded-[1.5rem] px-5 py-5 text-left transition',
              option.selected
                ? 'border border-accent/20 bg-white text-ink shadow-sm'
                : 'bg-stone-100/55 text-ink opacity-75 hover:opacity-100',
            ].join(' ')}
          >
            <span className="text-base font-semibold">{option.label}</span>
            <span
              className={[
                'flex h-6 w-6 items-center justify-center rounded-full',
                option.selected ? 'bg-accent text-[10px] text-white' : 'border-2 border-stone-300',
              ].join(' ')}
            >
              {option.selected ? '✓' : ''}
            </span>
          </button>
        ))}
      </div>
      <p className="mt-4 text-sm leading-relaxed text-ink-soft">{helperText}</p>
    </div>
  );
}

function TranscriptCard({
  item,
  accentBar,
  onFavorite,
}: {
  item: DiscoveryRecord;
  accentBar: string;
  onFavorite: () => Promise<void>;
}) {
  return (
    <article className={`rounded-[2rem] border border-paper-line border-l-[10px] bg-white p-7 shadow-card ${accentBar}`}>
      <div className="mb-6 flex items-start justify-between gap-4">
        <div>
          <h3 className="font-serif text-3xl text-ink">{item.object_name || item.detected_object_name || 'Saved turn'}</h3>
          <p className="mt-1 text-[10px] font-bold uppercase tracking-[0.28em] text-ink-muted">
            {formatTimestamp(item.created_at)}
          </p>
        </div>
        <button
          type="button"
          onClick={() => void onFavorite()}
          className="rounded-full px-3 py-2 text-sm font-semibold text-accent transition hover:bg-accent/10"
        >
          {item.is_favorite ? '♥' : '♡'}
        </button>
      </div>
      <div className="space-y-6">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-ink-muted">Child transcript</p>
          <p className="mt-2 font-serif text-xl italic leading-relaxed text-ink">
            “{item.transcript || 'No transcript saved.'}”
          </p>
        </div>
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-accent/70">Assistant reply</p>
          <p className="mt-2 font-serif text-xl leading-relaxed text-ink">
            “{item.reply_text || item.summary}”
          </p>
        </div>
      </div>
    </article>
  );
}

function formatTimestamp(timestamp: string) {
  const date = new Date(timestamp);
  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return new Intl.DateTimeFormat('en-IN', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
    .format(date)
    .replace(',', ' •');
}
