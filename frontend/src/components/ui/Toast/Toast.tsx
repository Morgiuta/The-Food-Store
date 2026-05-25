import { X } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastMessage {
  id: number;
  message: string;
  type: ToastType;
}

interface ToastViewportProps {
  toasts: ToastMessage[];
  onDismiss: (id: number) => void;
}

const toastStyles: Record<ToastType, string> = {
  success: 'bg-green-100 text-green-800 border-green-200',
  error: 'bg-red-100 text-red-800 border-red-200',
  info: 'bg-blue-100 text-blue-800 border-blue-200',
};

export function ToastViewport({ onDismiss, toasts }: ToastViewportProps) {
  if (toasts.length === 0) {
    return null;
  }

  return (
    <div 
      className="fixed bottom-6 right-6 z-[100] flex flex-col gap-3" 
      aria-live="polite" 
      aria-atomic="true"
    >
      {toasts.map((toast) => (
        <div 
          className={`flex items-center justify-between gap-4 p-4 min-w-[300px] border rounded-lg shadow-lg ${toastStyles[toast.type]} animate-in slide-in-from-bottom-5 fade-in duration-300`} 
          key={toast.id}
        >
          <span className="font-medium text-sm">{toast.message}</span>
          <button 
            type="button" 
            aria-label="Cerrar notificacion" 
            onClick={() => onDismiss(toast.id)}
            className="opacity-70 hover:opacity-100 transition-opacity"
          >
            <X size={18} />
          </button>
        </div>
      ))}
    </div>
  );
}
