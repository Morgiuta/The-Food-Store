import type { ButtonHTMLAttributes, PropsWithChildren } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary: 'bg-primary text-white hover:bg-primary-dark shadow-sm border border-transparent',
  secondary: 'bg-white text-charcoal border border-gray-300 hover:bg-gray-50',
  danger: 'bg-red-50 text-red-600 hover:bg-red-100 hover:text-red-700 border border-transparent',
  ghost: 'bg-transparent text-gray-600 hover:bg-gray-100 border border-transparent',
};

export function Button({
  children,
  className = '',
  type = 'button',
  variant = 'primary',
  ...props
}: PropsWithChildren<ButtonProps>) {
  return (
    <button 
      className={`px-4 py-2 font-bold text-sm rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${variantClasses[variant]} ${className}`.trim()} 
      type={type} 
      {...props}
    >
      {children}
    </button>
  );
}
