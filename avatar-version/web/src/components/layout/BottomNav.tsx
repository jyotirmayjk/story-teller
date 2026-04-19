import { NavLink } from 'react-router-dom';

const tabs = [
  { to: '/conversation', label: 'Conversation' },
  { to: '/story-teller', label: 'Story Teller' },
  { to: '/settings', label: 'Settings' },
];

export function BottomNav() {
  return (
    <nav
      aria-label="Primary"
      className="sticky bottom-3 z-30 mx-auto mt-4 grid w-full max-w-xl grid-cols-3 gap-1.5 rounded-full border border-paper-line/80 bg-paper-card/95 p-1.5 shadow-panel backdrop-blur sm:bottom-4 sm:mt-6 sm:gap-2 sm:p-2"
    >
      {tabs.map((tab) => (
        <NavLink
          key={tab.to}
          to={tab.to}
          className={({ isActive }) =>
            [
              'rounded-full px-2 py-2.5 text-center text-[13px] font-semibold tracking-[0.01em] transition sm:px-3 sm:py-3 sm:text-sm',
              isActive
                ? 'bg-accent/12 text-accent'
                : 'text-ink-soft hover:bg-white/65 hover:text-ink',
            ].join(' ')
          }
        >
          {tab.label}
        </NavLink>
      ))}
    </nav>
  );
}
