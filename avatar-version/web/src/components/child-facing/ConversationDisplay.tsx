interface ConversationDisplayProps {
  transcript: string;
  assistantReply: string;
  previousTurn?: {
    transcript: string;
    assistantReply: string;
  };
}

export function ConversationDisplay({ transcript, assistantReply, previousTurn }: ConversationDisplayProps) {
  return (
    <section className="rounded-[1.75rem] border border-paper-line bg-white/55 p-5 shadow-card backdrop-blur-sm sm:rounded-[2rem] sm:p-6">
      <div className="space-y-4 sm:space-y-5">
        {previousTurn ? (
          <div className="rounded-[1.25rem] bg-paper/70 p-4">
            <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-ink-muted">Previous turn</p>
            <p className="mt-2 font-serif text-sm italic leading-relaxed text-ink-soft sm:text-lg">
              {previousTurn.transcript}
            </p>
            <p className="mt-2 font-serif text-sm leading-relaxed text-ink-soft sm:text-lg">
              {previousTurn.assistantReply}
            </p>
          </div>
        ) : null}
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-ink-muted">What I heard</p>
          <p className="mt-2 font-serif text-lg leading-relaxed text-ink sm:text-2xl">
            {transcript || 'Press and hold the talk button when the child is ready.'}
          </p>
        </div>
        <div className="border-t border-paper-line pt-4 sm:pt-5">
          <p className="text-[10px] font-bold uppercase tracking-[0.28em] text-ink-muted">Last reply</p>
          <p className="mt-2 font-serif text-base italic leading-relaxed text-ink-soft sm:text-xl">
            {assistantReply || 'The next reply will appear here exactly as it is spoken.'}
          </p>
        </div>
      </div>
    </section>
  );
}
