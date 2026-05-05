import type { InputHTMLAttributes } from 'react';
import './Input.css';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export function Input({ id, label, error, className = '', ...props }: InputProps) {
  const inputId = id ?? props.name;

  return (
    <label className={`input-field ${className}`.trim()} htmlFor={inputId}>
      <span>{label}</span>
      <input id={inputId} {...props} />
      {error ? <small className="input-field__error">{error}</small> : null}
    </label>
  );
}
