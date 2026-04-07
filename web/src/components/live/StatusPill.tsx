export function StatusPill({ label, tone = 'default' }: { label: string; tone?: 'default' | 'good' | 'warn' | 'bad' }) {
  return <span className={`status-pill status-pill--${tone}`}>{label}</span>;
}
