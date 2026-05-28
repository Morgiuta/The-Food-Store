import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type PropsWithChildren,
} from 'react';
import { X } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastMessage {
  id: number;
  message: string;
  type: ToastType;
}

interface ConfirmOptions {
  cancelLabel?: string;
  confirmLabel?: string;
  message: string;
  title?: string;
  type?: 'danger' | 'info';
}

interface ConfirmRequest extends Required<ConfirmOptions> {
  id: number;
  resolve: (value: boolean) => void;
}

interface ToastContextValue {
  confirm: (options: ConfirmOptions) => Promise<boolean>;
  error: (message: string) => void;
  info: (message: string) => void;
  notify: (type: ToastType, message: string) => void;
  success: (message: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

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

function ConfirmDialog({
  request,
  onCancel,
  onConfirm,
}: {
  request: ConfirmRequest;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  const isDanger = request.type === 'danger';

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center bg-charcoal/50 p-4 backdrop-blur-sm" role="dialog" aria-modal="true">
      <div className="w-full max-w-md rounded-xl bg-white shadow-2xl border border-gray-100 overflow-hidden">
        <div className="p-6 border-b border-gray-100">
          <span className={`text-xs font-black uppercase tracking-wide ${isDanger ? 'text-red-600' : 'text-blue-600'}`}>
            Confirmacion
          </span>
          <h3 className="mt-1 text-xl font-black text-charcoal">{request.title}</h3>
          <p className="mt-3 text-sm font-medium text-gray-600 leading-6">{request.message}</p>
        </div>
        <div className="flex justify-end gap-3 bg-gray-50 px-6 py-4">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-bold text-gray-600 hover:border-gray-300 hover:bg-gray-100"
          >
            {request.cancelLabel}
          </button>
          <button
            type="button"
            onClick={onConfirm}
            className={`rounded-lg px-4 py-2 text-sm font-black text-white ${
              isDanger ? 'bg-red-600 hover:bg-red-700' : 'bg-primary hover:bg-primary-dark'
            }`}
          >
            {request.confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

export function ToastProvider({ children }: PropsWithChildren) {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [confirmRequest, setConfirmRequest] = useState<ConfirmRequest | null>(null);

  const dismissToast = useCallback((id: number) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const notify = useCallback(
    (type: ToastType, message: string) => {
      const id = Date.now() + Math.floor(Math.random() * 1000);
      setToasts((current) => [...current.slice(-2), { id, message, type }]);
      window.setTimeout(() => dismissToast(id), 4200);
    },
    [dismissToast],
  );

  const confirm = useCallback((options: ConfirmOptions) => (
    new Promise<boolean>((resolve) => {
      setConfirmRequest({
        cancelLabel: options.cancelLabel ?? 'Cancelar',
        confirmLabel: options.confirmLabel ?? 'Confirmar',
        id: Date.now(),
        message: options.message,
        resolve,
        title: options.title ?? 'Confirmar accion',
        type: options.type ?? 'info',
      });
    })
  ), []);

  const closeConfirm = useCallback((value: boolean) => {
    setConfirmRequest((current) => {
      current?.resolve(value);
      return null;
    });
  }, []);

  const value = useMemo<ToastContextValue>(() => ({
    confirm,
    error: (message) => notify('error', message),
    info: (message) => notify('info', message),
    notify,
    success: (message) => notify('success', message),
  }), [confirm, notify]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <ToastViewport toasts={toasts} onDismiss={dismissToast} />
      {confirmRequest ? (
        <ConfirmDialog
          request={confirmRequest}
          onCancel={() => closeConfirm(false)}
          onConfirm={() => closeConfirm(true)}
        />
      ) : null}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast debe usarse dentro de ToastProvider');
  }
  return context;
}
