interface ResponsePanelProps {
  text: string;
  placeholder: string;
  detectedObject?: string;
}

export function ResponsePanel({ text, placeholder, detectedObject }: ResponsePanelProps) {
  const hasText = Boolean(text);

  return (
    <section
      className={[
        'flex flex-col justify-center rounded-[1.75rem] border border-paper-line bg-[linear-gradient(180deg,rgba(255,249,241,0.98),rgba(244,231,209,0.96))] shadow-panel sm:rounded-[2.25rem] sm:p-10',
        hasText
          ? 'min-h-[14.5rem] flex-1 p-6 sm:min-h-[19rem]'
          : 'min-h-[6.5rem] p-5 sm:min-h-[10rem] sm:flex-1',
      ].join(' ')}
    >
      {detectedObject ? (
        <p className="mb-4 text-xs font-bold uppercase tracking-[0.28em] text-accent">
          Detected object
          <span className="ml-3 rounded-full bg-accent/10 px-3 py-1 text-sm tracking-[0.02em] text-accent">
            {detectedObject}
          </span>
        </p>
      ) : null}
      <p
        className={[
          'font-serif leading-[1.02]',
          hasText
            ? 'text-[2.15rem] text-ink sm:text-5xl'
            : 'text-base italic text-ink-soft sm:text-xl',
        ].join(' ')}
      >
        {hasText ? text : placeholder}
      </p>
    </section>
  );
}
