import type { PropsWithChildren } from 'react';
import { AppShell } from '../components/layout/AppShell';

export function AppLayout({ children }: PropsWithChildren) {
  return <AppShell>{children}</AppShell>;
}
