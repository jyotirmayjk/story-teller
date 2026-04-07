import type { PropsWithChildren } from 'react';

export function OnboardingFrame({
  title,
  subtitle,
  children,
}: PropsWithChildren<{ title: string; subtitle: string }>) {
  return (
    <section className="onboarding-shell">
      <div className="panel panel--hero">
        <p className="eyebrow">Whimsical Explorer 2</p>
        <h1 className="headline">{title}</h1>
        <p className="subhead">{subtitle}</p>
      </div>
      <div className="panel panel--form">{children}</div>
    </section>
  );
}
