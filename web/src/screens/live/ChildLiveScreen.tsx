import { useEffect } from 'react';
import { ConversationDisplay } from '../../components/child-facing/ConversationDisplay';
import { PushToTalk } from '../../components/child-facing/PushToTalk';
import { ResponsePanel } from '../../components/child-facing/ResponsePanel';
import { EmptyState } from '../../components/common/EmptyState';
import { useBootstrap } from '../../hooks/useBootstrap';
import { useLiveSocket } from '../../hooks/useLiveSocket';
import { usePushToTalk } from '../../hooks/usePushToTalk';
import { useSession } from '../../hooks/useSession';
import { useLiveStore } from '../../store/liveStore';
import type { Mode } from '../../types/live';

const copyByMode: Record<Mode, { eyebrow: string; title: string; subtitle: string; placeholder: string }> = {
  conversation: {
    eyebrow: 'Conversation',
    title: 'I am listening.',
    subtitle: 'Tell me about your day, and I will ask one calm question back.',
    placeholder: 'A calm follow-up question will appear here after the child speaks.',
  },
  story_teller: {
    eyebrow: 'Story Teller',
    title: 'Once upon a time.',
    subtitle: 'Ask about a toy or object, and I will describe it first and then tell a story.',
    placeholder: 'Ask about any child-safe object and the story will appear here.',
  },
};

export function ChildLiveScreen({ mode }: { mode: Mode }) {
  const { bootstrapped, error } = useBootstrap();
  const liveSocket = useLiveSocket(bootstrapped);
  const session = useSession();
  const live = useLiveStore();
  const resetTurn = useLiveStore((state) => state.resetTurn);

  const pushToTalk = usePushToTalk({
    onBegin: () => {
      resetTurn();
    },
    onChunk: (audio, sampleRate) => {
      const ok =
        liveSocket?.send({
          type: 'audio.chunk',
          data: {
            audio,
            sample_rate: sampleRate,
            encoding: 'pcm_s16le',
          },
        }) ?? false;
      live.trackAudioChunkSent(audio.length, ok);
    },
    onStop: () => {
      const ok = liveSocket?.send({ type: 'audio.flush' }) ?? false;
      live.trackAudioFlushSent(ok);
    },
  });

  useEffect(() => {
    if (!bootstrapped || !liveSocket) {
      return;
    }

    session.updateRuntime({ activeMode: mode });
    void session.patchSession({ activeMode: mode });
    liveSocket.send({
      type: 'session.update',
      data: {
        active_mode: mode,
        voice_style: session.voiceStyle,
      },
    });
  }, [bootstrapped, liveSocket, mode, session]);

  if (error) {
    return (
      <EmptyState
        title="Bootstrap failed"
        description={error}
        actionLabel="Reload"
        onAction={() => window.location.reload()}
      />
    );
  }

  const screenCopy = copyByMode[mode];
  const pttState = getPushToTalkState(session.status, pushToTalk.recording);
  const detectedObject = mode === 'story_teller' ? session.currentObjectName : '';
  const previousTurn =
    mode === 'conversation' && live.recentTurns.length > 0
      ? live.recentTurns[live.recentTurns.length - 1]
      : undefined;

  return (
    <div className="flex min-h-full flex-1 flex-col bg-paper">
      <header className="mb-6 pt-2 sm:mb-12 sm:pt-8">
        <span className="text-xs font-bold uppercase tracking-[0.28em] text-accent">{screenCopy.eyebrow}</span>
        <h1 className="mt-2 font-serif text-[2.8rem] leading-none text-ink sm:mt-3 sm:text-7xl">{screenCopy.title}</h1>
        <p className="mt-3 max-w-sm text-sm leading-relaxed text-ink-soft sm:mt-4 sm:text-lg">{screenCopy.subtitle}</p>
      </header>

      <section className="flex flex-1 flex-col gap-4 sm:gap-8">
        <ConversationDisplay
          transcript={live.transcriptPartial || live.transcriptFinal}
          assistantReply={live.assistantText}
          previousTurn={previousTurn}
        />

        <ResponsePanel
          text={live.assistantText}
          detectedObject={detectedObject || undefined}
          placeholder={screenCopy.placeholder}
        />
      </section>

      <div className="mt-auto pt-4 sm:pt-10">
        <PushToTalk
          state={pttState}
          status={session.status}
          error={pushToTalk.error ?? undefined}
          disabled={!bootstrapped || session.status === 'speaking'}
          onPress={() => void pushToTalk.begin()}
          onRelease={() => void pushToTalk.end()}
          onCancel={() => {
            if (pushToTalk.recording) {
              void pushToTalk.end();
            }
          }}
          onResetAudio={() => window.location.reload()}
        />
      </div>
    </div>
  );
}

export function ConversationScreen() {
  return <ChildLiveScreen mode="conversation" />;
}

export function StoryTellerScreen() {
  return <ChildLiveScreen mode="story_teller" />;
}

function getPushToTalkState(status: string, recording: boolean) {
  if (recording || status === 'listening') {
    return 'listening';
  }
  if (status === 'processing') {
    return 'processing';
  }
  if (status === 'speaking') {
    return 'speaking';
  }
  return 'idle';
}
