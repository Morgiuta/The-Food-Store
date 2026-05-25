import type { InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export function Input({ id, label, error, className = '', ...props }: InputProps) {
  const inputId = id ?? props.name;

  return (
    <div className={`flex flex-col gap-1.5 ${className}`.trim()}>
      <label className="text-sm font-bold text-charcoal" htmlFor={inputId}>
        {label}
      </label>
      <input 
        id={inputId} 
        className={`w-full p-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all ${
          error ? 'border-red-500 bg-red-50/50' : 'border-gray-300'
        }`}
        {...props} 
      />
      {error ? <small className="text-red-500 text-xs font-medium">{error}</small> : null}
    </div>
  );
}
