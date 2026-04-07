import type { ButtonHTMLAttributes, PropsWithChildren } from 'react';

type ButtonProps = PropsWithChildren<
  ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    block?: boolean;
  }
>;

export function Button({
  children,
  className = '',
  variant = 'primary',
  block = false,
  ...props
}: ButtonProps) {
  const variantClassName = {
    primary: 'bg-accent text-white hover:bg-accent-strong',
    secondary: 'border border-paper-line bg-white/80 text-ink hover:bg-white',
    ghost: 'bg-transparent text-ink-soft hover:bg-white/55 hover:text-ink',
    danger: 'bg-warn text-white hover:bg-[#8c4034]',
  }[variant];

  return (
    <button
      {...props}
      className={[
        'inline-flex items-center justify-center rounded-full px-4 py-2.5 text-sm font-semibold transition duration-200 ease-out',
        'disabled:cursor-not-allowed disabled:opacity-50',
        block ? 'w-full' : '',
        variantClassName,
        className,
      ].join(' ').trim()}
    >
      {children}
    </button>
  );
}
