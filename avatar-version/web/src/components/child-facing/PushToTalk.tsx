import { useEffect, useState } from 'react';
import type { PointerEvent as ReactPointerEvent } from 'react';
import type { RuntimeStatus } from '../../types/live';

type VoiceState = 'idle' | 'listening' | 'processing' | 'speaking';

interface PushToTalkProps {
  state: VoiceState;
  status: RuntimeStatus;
  error?: string;
  disabled?: boolean;
  onPress: () => void;
  onRelease: () => void;
  onCancel: () => void;
  onResetAudio: () => void;
}

const stateStyles: Record<VoiceState, string> = {
  idle: 'bg-[radial-gradient(circle_at_30%_20%,#f3cdbf,#C0573E_66%,#96412d_100%)] text-white',
  listening:
    'scale-[1.03] bg-[radial-gradient(circle_at_30%_20%,#fff1e8,#cf6d48_66%,#9b462a_100%)] text-white ring-8 ring-accent/15',
  processing:
    'bg-[radial-gradient(circle_at_30%_20%,#ffefc6,#dc9542_68%,#a96528_100%)] text-ink',
  speaking:
    'bg-[radial-gradient(circle_at_30%_20%,#e7f1df,#64856a_68%,#445c4b_100%)] text-white',
};

const stateLabels: Record<VoiceState, string> = {
  idle: 'Tap to Talk',
  listening: 'Listening...',
  processing: 'Thinking...',
  speaking: 'Speaking...',
};

export function PushToTalk({
  state,
  status,
  error,
  disabled = false,
  onPress,
  onRelease,
  onCancel,
  onResetAudio,
}: PushToTalkProps) {
  const [activePointerId, setActivePointerId] = useState<number | null>(null);

  useEffect(() => {
    if (activePointerId === null) {
      return;
    }

    const finish = (event: PointerEvent) => {
      if (event.pointerId !== activePointerId) {
        return;
      }
      setActivePointerId(null);
      onRelease();
    };

    const cancel = (event: PointerEvent) => {
      if (event.pointerId !== activePointerId) {
        return;
      }
      setActivePointerId(null);
      onCancel();
    };

    window.addEventListener('pointerup', finish);
    window.addEventListener('pointercancel', cancel);

    return () => {
      window.removeEventListener('pointerup', finish);
      window.removeEventListener('pointercancel', cancel);
    };
  }, [activePointerId, onCancel, onRelease]);

  const handlePointerDown = (event: ReactPointerEvent<HTMLButtonElement>) => {
    if (disabled || activePointerId !== null) {
      return;
    }
    event.preventDefault();
    setActivePointerId(event.pointerId);
    onPress();
  };

  return (
    <section className="flex flex-col items-center gap-4 pt-4">
      <button
        type="button"
        onPointerDown={handlePointerDown}
        onPointerLeave={(event) => {
          if (activePointerId !== null && event.buttons === 0 && event.pointerType !== 'touch') {
            setActivePointerId(null);
            onCancel();
          }
        }}
        disabled={disabled}
        aria-label={stateLabels[state]}
        style={{ touchAction: 'none' }}
        className={[
          'flex aspect-square w-[min(48vw,12rem)] items-center justify-center rounded-full p-3 shadow-button transition duration-300 ease-out sm:w-[min(72vw,18rem)] sm:p-4',
          'disabled:cursor-not-allowed disabled:opacity-80',
          stateStyles[state],
        ].join(' ')}
      >
        <span className="flex h-full w-full items-center justify-center rounded-full border border-white/15 bg-white/10 px-6 text-center font-serif text-xl italic sm:px-8 sm:text-[2rem]">
          {stateLabels[state]}
        </span>
      </button>

      {error ? <p className="text-sm font-medium text-warn">{error}</p> : null}

      <div className="flex flex-wrap items-center justify-center gap-3">
        <span className="rounded-full border border-paper-line bg-white/70 px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-ink-soft">
          {status}
        </span>
        <button
          type="button"
          onClick={onResetAudio}
          className="rounded-full px-4 py-2 text-sm font-semibold text-ink-soft transition hover:bg-white/55 hover:text-ink"
        >
          Reset audio
        </button>
      </div>
    </section>
  );
}
