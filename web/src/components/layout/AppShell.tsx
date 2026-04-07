import type { PropsWithChildren } from 'react';
import { BottomNav } from './BottomNav';

export function AppShell({ children }: PropsWithChildren) {
  return (
    <div className="min-h-dvh bg-paper text-ink">
      <main className="mx-auto flex min-h-dvh w-full max-w-5xl flex-col px-4 pb-6 pt-4 sm:px-6 sm:pb-10 sm:pt-8">
        {children}
      </main>
      <BottomNav />
    </div>
  );
}
