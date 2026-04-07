import { Button } from './Button';

export function EmptyState({
  title,
  description,
  actionLabel,
  onAction,
}: {
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <div className="mx-auto flex min-h-[50vh] w-full max-w-xl flex-col items-center justify-center rounded-[2rem] border border-paper-line bg-white/70 p-8 text-center shadow-card">
      <h2 className="font-serif text-4xl text-ink">{title}</h2>
      <p className="mt-3 text-base leading-relaxed text-ink-soft">{description}</p>
      {actionLabel && onAction ? <Button onClick={onAction}>{actionLabel}</Button> : null}
    </div>
  );
}
