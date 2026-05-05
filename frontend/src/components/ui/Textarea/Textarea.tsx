import type { TextareaHTMLAttributes } from 'react';
import './Textarea.css';

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string;
  error?: string;
}

export function Textarea({ id, label, error, className = '', ...props }: TextareaProps) {
  const textareaId = id ?? props.name;

  return (
    <label className={`textarea-field ${className}`.trim()} htmlFor={textareaId}>
      <span>{label}</span>
      <textarea id={textareaId} {...props} />
      {error ? <small className="textarea-field__error">{error}</small> : null}
    </label>
  );
}
